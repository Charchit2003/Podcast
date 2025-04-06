import ffmpeg
from together import Together
from cartesia import Cartesia
from pathlib import Path
from pypdf import PdfReader
from models.anchor import AnchorLine, AnchorScript
from config.settings import (
    TOGETHER_API_KEY, 
    CARTESIA_API_KEY, 
    SYSTEM_PROMPT_ANCHOR,
    HOST_VOICE_ID,
    MODEL_ID
)
import subprocess
import os
import time
import json
import asyncio

class AnchorProcessor:
    def __init__(self):
        self.together_client = Together(api_key=TOGETHER_API_KEY)
        self.cartesia_client = Cartesia(api_key=CARTESIA_API_KEY)
        self.output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_dir, exist_ok=True)

    async def download_audio(self, url: str) -> str:
        try:
            output_path = "temp_audio.mp3"
            subprocess.run(['ffmpeg', '-i', url, '-vn', '-acodec', 'libmp3lame', output_path])
            return output_path
        except Exception as e:
            raise Exception(f"Error downloading audio: {str(e)}")

    async def get_PDF_text(self, file_path: str) -> str:
        text = ''
        try:
            reader = PdfReader(file_path)
            text = "\n\n".join([page.extract_text() for page in reader.pages])
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    async def generate_script(self, input_text: str) -> AnchorScript:
        try:
            response = self.together_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_ANCHOR},
                    {"role": "user", "content": input_text},
                ],
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                response_format={"type": "json_object"}
            )
            
            raw_response = response.choices[0].message.content
            print(f"Raw LLM response: {raw_response}")
            
            try:
                json_response = json.loads(raw_response)
                
                if not isinstance(json_response, dict) or "script" not in json_response:
                    raise ValueError("Invalid response format")
                    
                return AnchorScript(
                    scriptNotes=json_response.get("scriptNotes", ""),
                    script=[
                        AnchorLine(
                            speaker="Anchor",
                            text=item["text"]
                        ) for item in json_response["script"]
                    ]
                )
                
            except json.JSONDecodeError as json_error:
                print(f"JSON parsing error: {str(json_error)}")
                return self._create_fallback_script()
            except Exception as validation_error:
                print(f"Validation error: {str(validation_error)}")
                return self._create_fallback_script()
                
        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")

    def _create_fallback_script(self) -> AnchorScript:
        """Create a fallback script when there's an error"""
        return AnchorScript(
            scriptNotes="Error occurred while processing the input",
            script=[
                AnchorLine(
                    speaker="Anchor",
                    text="We apologize, but we encountered technical difficulties. Please try again later."
                )
            ]
        )

    async def generate_audio(self, script: AnchorScript) -> str:
        try:
            timestamp = int(time.time())
            output_pcm = os.path.join(self.output_dir, f"anchor_{timestamp}.pcm")
            output_wav = os.path.join(self.output_dir, f"anchor_{timestamp}.wav")
            
            # Validate script
            if not script.script or len(script.script) == 0:
                print("Error: Empty script received")
                script.script = [
                    AnchorLine(
                        speaker="Anchor", 
                        text="I apologize, but we couldn't generate the content."
                    )
                ]

            print(f"Generating audio for {len(script.script)} lines")
            
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }

            try:
                with open(output_pcm, "wb") as f:
                    total_bytes_written = 0
                    
                    # Create a single websocket connection for all lines
                    ws = self.cartesia_client.tts.websocket()
                    
                    for i, line in enumerate(script.script):
                        print(f"Processing line {i+1}/{len(script.script)}")
                        
                        # Add natural pause before starting new line
                        if i > 0:
                            f.write(b'\x00' * 4410)  # 0.1s pause between lines
                        
                        retries = 3
                        success = False
                        
                        while retries > 0 and not success:
                            try:
                                # Clean text and add pause markers
                                clean_text = line.text.strip()
                                if not clean_text.endswith(('.', '!', '?')):
                                    clean_text += '.'  # Ensure proper sentence ending
                                
                                # Send with modified parameters
                                audio_chunks = ws.send(
                                    model_id=MODEL_ID,
                                    transcript=clean_text,
                                    voice={
                                        "id" : HOST_VOICE_ID,
                                        },  # Direct voice_id instead of voice object
                                    stream=True,
                                    output_format=output_format
                                )
                                
                                # Process chunks with timeout
                                chunk_data = bytearray()
                                chunk_count = 0
                                timeout = time.time() + 15  # 15 second timeout
                                
                                async for chunk in audio_chunks:
                                    if time.time() > timeout:
                                        raise TimeoutError("Chunk processing timeout")
                                    
                                    if hasattr(chunk, 'audio') and chunk.audio:
                                        chunk_data.extend(chunk.audio)
                                        chunk_count += 1
                                
                                if chunk_count > 0:
                                    # Write consolidated audio data
                                    bytes_written = f.write(chunk_data)
                                    total_bytes_written += bytes_written
                                    
                                    # Add dynamic pause based on punctuation
                                    if clean_text[-1] in '.!?':
                                        f.write(b'\x00' * 8820)  # 0.2s for sentence end
                                    else:
                                        f.write(b'\x00' * 4410)  # 0.1s for other breaks
                                    
                                    success = True
                                    print(f"Line {i+1}: Processed {chunk_count} chunks")
                                else:
                                    print(f"Warning: No audio data for line {i+1}, attempt {4-retries}")
                                    retries -= 1
                                    
                            except Exception as e:
                                print(f"Error on line {i+1}, attempt {4-retries}: {str(e)}")
                                retries -= 1
                                if retries > 0:
                                    await asyncio.sleep(1)  # Longer delay between retries
                                    ws = self.cartesia_client.tts.websocket()  # Fresh connection
                        
                        if not success:
                            raise Exception(f"Failed to process line {i+1} after all retries")
                    
                    ws.close()
                    print(f"Total audio bytes written: {total_bytes_written}")
                    
                    # Convert to WAV if PCM was successful
                    if total_bytes_written > 0:
                        unique_wav = output_wav.replace('.wav', f'_{timestamp}.wav')
                        
                        ffmpeg.input(
                            output_pcm,
                            format="f32le",
                            acodec="pcm_f32le",
                            ac=1,
                            ar=44100
                        ).output(
                            unique_wav,
                            acodec="pcm_s16le"
                        ).run(capture_stdout=True, capture_stderr=True)
                        
                        os.remove(output_pcm)  # Clean up PCM file
                        return unique_wav
                    else:
                        raise Exception("No audio data was generated")
                        
            except Exception as ws_error:
                if os.path.exists(output_pcm):
                    os.remove(output_pcm)
                raise Exception(f"Audio generation failed: {ws_error}")
                
        except Exception as e:
            if os.path.exists(output_pcm):
                os.remove(output_pcm)
            raise Exception(f"Audio processing failed: {e}")