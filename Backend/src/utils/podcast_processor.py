import ffmpeg
from together import Together
from cartesia import Cartesia
from pathlib import Path
from pypdf import PdfReader
from models.podcast import Script, PodcastInput, LineItem  # Added LineItem import
from config.settings import (
    TOGETHER_API_KEY, 
    CARTESIA_API_KEY, 
    SYSTEM_PROMPT_CONVERSE,
    HOST_VOICE_ID,
    GUEST_VOICE_ID,
    MODEL_ID
)
import subprocess
import os
import time
import asyncio
from utils.email_sender import send_podcast_email

class PodcastProcessor:
    def __init__(self):
        self.together_client = Together(api_key=TOGETHER_API_KEY)
        self.cartesia_client = Cartesia(api_key=CARTESIA_API_KEY)
        # Create output directory if it doesn't exist
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
        reader = PdfReader(file_path)
        total_text = []
        
        # Clamp page range between available pages
        start_page = max(0, 4)  # 5th page (0-indexed)
        end_page = min(25, len(reader.pages))

        for i in range(start_page, end_page):
            page_text = reader.pages[i].extract_text()
            if page_text:
                total_text.append(page_text)
            if sum(len(t) for t in total_text) >= 2000:
                break  # stop early if limit reached

        final_text = "\n\n".join(total_text)[:2000]  # hard cut at 2000 chars
        return final_text
    

    async def generate_podcast_script(self, input_text: str) -> Script:
        try:
            response = self.together_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_CONVERSE},
                    {"role": "user", "content": input_text},
                ],
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                response_format={"type": "json_object"}
            )
            
            # Get the raw response
            raw_response = response.choices[0].message.content
            print(f"Raw LLM response: {raw_response}")
            
            try:
                # Parse the raw JSON response
                import json
                json_response = json.loads(raw_response)
                
                # Extract dialogue from the response
                dialogue = []
                if isinstance(json_response, dict):
                    # Handle the current response format
                    if "script" in json_response:
                        dialogue = json_response["script"]
                    else:
                        # Try to extract any dialogue array
                        for key, value in json_response.items():
                            if isinstance(value, list) and value and isinstance(value[0], dict):
                                if all("speaker" in item and "text" in item for item in value):
                                    dialogue = value
                                    break
                
                # Convert to our Script format
                if dialogue:
                    # Map any non-Jane speaker to "Guest"
                    return Script(
                        scratchpad=json_response.get("podcastOutro", ""),
                        name_of_guest=next((item["speaker"] for item in dialogue 
                                          if item["speaker"] not in ["Jane", "Host"]), "Guest"),
                        script=[
                            LineItem(
                                # Map all non-Jane speakers to "Guest"
                                speaker="Host" if item["speaker"] in ["Jane", "Host"] else "Guest",
                                text=item["text"]
                            ) for item in dialogue
                        ]
                    )
                else:
                    raise ValueError("No valid dialogue found in response")
                    
            except Exception as validation_error:
                print(f"Validation error: {validation_error}")
                return Script(
                    scratchpad="Error processing input",
                    name_of_guest="AI Assistant",
                    script=[
                        LineItem(speaker="Host", 
                                text="I apologize, but we encountered an error processing the content."),
                        LineItem(speaker="Guest", 
                                text="The system needs adjustment. Please try again later.")
                    ]
                )
                
        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")   

    
    async def generate_podcast_audio(self, script: Script) -> str:
        try:
            # Create unique filenames using timestamp
            timestamp = int(time.time())
            output_pcm = os.path.join(self.output_dir, f"temp_podcast_{timestamp}.pcm")
            output_wav = os.path.join(self.output_dir, f"podcast_{timestamp}.wav")
            
            # print(f"Will save files to:")
            # print(f"PCM: {output_pcm}")
            # print(f"WAV: {output_wav}")

            # Validate script has content
            if not script.script or len(script.script) == 0:
                print("Error: Empty script received")
                # Create a default error message script
                script.script = [
                    LineItem(
                        speaker="Host", 
                        text="I apologize, but we couldn't generate the podcast content."
                    ),
                    LineItem(
                        speaker="Guest", 
                        text="Please try again with different input content."
                    )
                ]
                print("Created fallback script with error messages")

            # Debug print to verify script content
            print(f"Generating audio for {len(script.script)} lines of dialogue")
            
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }
            
            print(f"Output PCM path: {output_pcm}")
            print(f"Output WAV path: {output_wav}")
            
            try:
                ws = self.cartesia_client.tts.websocket()
                with open(output_pcm, "wb") as f:
                    total_bytes_written = 0
                    for i, line in enumerate(script.script):
                        print(f"Processing line {i+1}: {line.speaker} - {line.text[:30]}...")
                        voice_id = HOST_VOICE_ID if line.speaker != "Guest" else GUEST_VOICE_ID
                        print(f"Using voice_id: {voice_id}")

                        # Add delay between voice switches
                        if i > 0 and script.script[i-1].speaker != line.speaker:
                            await asyncio.sleep(0.5)  # 500ms delay when switching voices
                        
                        retries = 3
                        while retries > 0:
                            try:
                                audio_chunks = ws.send(
                                    model_id=MODEL_ID,
                                    transcript = "-" + line.text, # the "-"" is to add a pause between speakers
                                    voice={
                                        "id": voice_id,
                                        },
                                    stream=True,
                                    output_format=output_format
                                )
                                
                                chunk_count = 0
                                chunk_data = bytearray()
                                
                                # Set timeout for chunk processing
                                timeout = time.time() + 10  # 10 second timeout
                                
                                for chunk in audio_chunks:
                                    if time.time() > timeout:
                                        raise TimeoutError("Chunk processing timeout")
                                        
                                    if isinstance(chunk, bytes):
                                        chunk_data.extend(chunk)
                                        chunk_count += 1
                                    elif hasattr(chunk, 'audio') and chunk.audio:
                                        chunk_data.extend(chunk.audio)
                                        chunk_count += 1
                                
                                if chunk_count > 0:
                                    # Write all chunks at once
                                    bytes_written = f.write(chunk_data)
                                    total_bytes_written += bytes_written
                                    print(f"Successfully processed {chunk_count} chunks for line {i+1}")
                                    
                                    # Add variable pause based on punctuation
                                    if line.text.rstrip().endswith(('.', '!', '?')):
                                        f.write(b'\x00' * 8820)  # 0.2s pause after sentences
                                    else:
                                        f.write(b'\x00' * 4410)  # 0.1s pause otherwise
                                        
                                    break  # Success - exit retry loop
                                else:
                                    print(f"Warning: No audio chunks in try {3-retries+1}")
                                    retries -= 1
                                    if retries > 0:
                                        await asyncio.sleep(0.5)  # Wait before retry
                                        ws = self.cartesia_client.tts.websocket()  # New connection
                                        
                            except Exception as chunk_error:
                                print(f"Chunk error in try {3-retries+1}: {str(chunk_error)}")
                                retries -= 1
                                if retries > 0:
                                    await asyncio.sleep(0.5)
                                    ws = self.cartesia_client.tts.websocket()
                                else:
                                    raise chunk_error
                    
                    print(f"Total bytes written to PCM: {total_bytes_written}")
                    
                ws.close()
                
                # Verify PCM file exists and has content
                if os.path.exists(output_pcm) and os.path.getsize(output_pcm) > 0:
                    print(f"PCM file created successfully: {os.path.getsize(output_pcm)} bytes")
                    
                    # Convert to WAV using ffmpeg
                    try:
                        # Generate unique filename with timestamp
                        timestamp = int(time.time())
                        unique_wav = output_wav.replace('.wav', f'_{timestamp}.wav')
                        
                        # Convert PCM to WAV without overwrite flag
                        ffmpeg.input(
                            output_pcm,
                            format="f32le",   # Input format is 32-bit float PCM
                            acodec="pcm_f32le",  # Input audio codec
                            ac=1,             # 1 audio channel (mono)
                            ar=44100          # Sample rate of 44.1kHz
                        ).output(
                            unique_wav,
                            acodec="pcm_s16le"  # Convert to 16-bit PCM for better compatibility
                        ).run(
                            capture_stdout=True, 
                            capture_stderr=True
                        )
                        
                        print(f"WAV file created successfully at: {unique_wav}")
                        print(f"WAV file size: {os.path.getsize(unique_wav)} bytes")
                        
                        return unique_wav
                            
                    except ffmpeg.Error as ff_error:
                        print(f"FFmpeg error: {ff_error.stderr.decode()}")
                        raise Exception("FFmpeg conversion failed")
                else:
                    raise Exception(f"PCM file creation failed. Total bytes written: {total_bytes_written}")
                    
            except Exception as ws_error:
                raise Exception(f"Websocket processing failed: {str(ws_error)}")
                
        except Exception as e:
            if os.path.exists(output_pcm):
                os.remove(output_pcm)
            raise Exception(f"Audio generation failed: {str(e)}")

        try:
            timestamp = int(time.time())
            output_pcm = os.path.join(self.output_dir, f"anchor_{timestamp}.pcm")
            output_wav = os.path.join(self.output_dir, f"anchor_{timestamp}.wav")
            
            # Use a single voice for anchor
            voice_id = HOST_VOICE_ID

             # Validate script has content
            if not script.script or len(script.script) == 0:
                print("Error: Empty script received")
                # Create a default error message script
                script.script = [
                    LineItem(
                        speaker="Host", 
                        text="I apologize, but we couldn't generate the podcast content."
                    )
                ]
                print("Created fallback script with error messages")

            # Debug print to verify script content
            print(f"Generating audio for {len(script.script)} lines of dialogue")
            
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }
            
            print(f"Output PCM path: {output_pcm}")
            print(f"Output WAV path: {output_wav}")
            
            try:
                ws = self.cartesia_client.tts.websocket()
                with open(output_pcm, "wb") as f:
                    total_bytes_written = 0
                    for i, line in enumerate(script.script):
                        print(f"Processing line {i+1}: {line.speaker} - {line.text[:30]}...")
                        print(voice_id)
                        try:
                            # Updated websocket parameters to match Cartesia's API
                            audio_chunks = ws.send(
                                model_id=MODEL_ID,
                                transcript = "-" + line.text, # the "-"" is to add a pause between speakers
                                voice={
                                    "id": voice_id,
                                    },
                                stream=True,
                                output_format=output_format,
                            )
                            
                            chunk_count = 0
                            for chunk in audio_chunks:
                                if isinstance(chunk, bytes):
                                    bytes_written = f.write(chunk)
                                    total_bytes_written += bytes_written
                                    chunk_count += 1
                                elif hasattr(chunk, 'audio') and chunk.audio:
                                    bytes_written = f.write(chunk.audio)
                                    total_bytes_written += bytes_written
                                    chunk_count += 1
                            
                            if chunk_count > 0:
                                print(f"Successfully processed {chunk_count} chunks for line {i+1}")
                                # Add a small pause between lines
                                f.write(b'\x00' * 4410)  # 0.1 second pause at 44.1kHz
                            else:
                                print(f"Warning: No audio chunks processed for line {i+1}")
                                
                        except Exception as line_error:
                            print(f"Error processing line {i+1}: {str(line_error)}")
                            raise line_error

                    print(f"Total bytes written to PCM: {total_bytes_written}")
                    
                ws.close()
                
                # Verify PCM file exists and has content
                if os.path.exists(output_pcm) and os.path.getsize(output_pcm) > 0:
                    print(f"PCM file created successfully: {os.path.getsize(output_pcm)} bytes")
                    
                    # Convert to WAV using ffmpeg
                    try:
                        # Generate unique filename with timestamp
                        timestamp = int(time.time())
                        unique_wav = output_wav.replace('.wav', f'_{timestamp}.wav')
                        
                        # Convert PCM to WAV without overwrite flag
                        ffmpeg.input(
                            output_pcm,
                            format="f32le",   # Input format is 32-bit float PCM
                            acodec="pcm_f32le",  # Input audio codec
                            ac=1,             # 1 audio channel (mono)
                            ar=44100          # Sample rate of 44.1kHz
                        ).output(
                            unique_wav,
                            acodec="pcm_s16le"  # Convert to 16-bit PCM for better compatibility
                        ).run(
                            capture_stdout=True, 
                            capture_stderr=True
                        )
                        
                        print(f"WAV file created successfully at: {unique_wav}")
                        print(f"WAV file size: {os.path.getsize(unique_wav)} bytes")
                        
                        return unique_wav
                            
                    except ffmpeg.Error as ff_error:
                        print(f"FFmpeg error: {ff_error.stderr.decode()}")
                        raise Exception("FFmpeg conversion failed")
                else:
                    raise Exception(f"PCM file creation failed. Total bytes written: {total_bytes_written}")
                    
            except Exception as ws_error:
                raise Exception(f"Websocket processing failed: {str(ws_error)}")
                
        except Exception as e:
            if os.path.exists(output_pcm):
                os.remove(output_pcm)
            raise Exception(f"Audio generation failed: {str(e)}")

    async def process_and_email(self, input_text: str, recipient_email: str) -> dict:
        try:
            # Generate script
            script = await self.generate_podcast_script(input_text)
            
            # Generate audio
            audio_path = await self.generate_podcast_audio(script)
            
            # Send email
            email_sent = await send_podcast_email(
                recipient_email=recipient_email,
                audio_file_path=audio_path,
                transcript=script.dict(),
                is_anchor=False
            )
            
            return {
                "success": True,
                "audio_path": audio_path,
                "email_sent": email_sent,
                "transcript": script
            }
            
        except Exception as e:
            raise Exception(f"Processing failed: {str(e)}")