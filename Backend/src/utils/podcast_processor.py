import ffmpeg
from together import Together
from cartesia import Cartesia
from pathlib import Path
from pypdf import PdfReader
from models.podcast import Script, PodcastInput
from config.settings import (
    TOGETHER_API_KEY, 
    CARTESIA_API_KEY, 
    SYSTEM_PROMPT,
    HOST_VOICE_ID,
    GUEST_VOICE_ID,
    MODEL_ID
)
import subprocess
import os

class PodcastProcessor:
    def __init__(self):
        self.together_client = Together(api_key=TOGETHER_API_KEY)
        self.cartesia_client = Cartesia(api_key=CARTESIA_API_KEY)

    async def download_audio(self, url: str) -> str:
        try:
            output_path = "temp_audio.mp3"
            subprocess.run(['ffmpeg', '-i', url, '-vn', '-acodec', 'libmp3lame', output_path])
            return output_path
        except Exception as e:
            raise Exception(f"Error downloading audio: {str(e)}")

    async def transcribe_audio(self, audio_path: str) -> str:
        try:
            # Add your transcription logic here
            # This is a placeholder - implement actual transcription
            return "Transcribed text"
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")

    async def generate_summary(self, text: str) -> Tuple[str, List[str], List[str]]:
        try:
            prompt = f"Summarize this podcast transcript:\n\n{text}"
            response = self.together_client.Complete.create(
                prompt=prompt,
                model="togethercomputer/llama-2-70b-chat",
                max_tokens=1000,
                temperature=0.7
            )
            
            summary = response['output']['choices'][0]['text']
            chapters = ["Chapter 1", "Chapter 2"]  # Placeholder
            highlights = ["Highlight 1", "Highlight 2"]  # Placeholder
            
            return summary, chapters, highlights
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")

    async def get_PDF_text(self, file_path: str) -> str:
        text = ''
        try:
            with Path(file_path).open("rb") as f:
                reader = PdfReader(f)
                text = "\n\n".join([page.extract_text() for page in reader.pages])
                if len(text) > 400000:
                    raise Exception("PDF too long - exceeds token limit")
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")

    async def generate_script(self, input_text: str) -> Script:
        try:
            response = self.together_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": input_text},
                ],
                model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
                response_format={"type": "json_object"}
            )
            return Script.model_validate_json(response.choices[0].message.content)
        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")

    async def generate_audio(self, script: Script) -> str:
        try:
            output_format = {
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            }
            
            ws = self.cartesia_client.tts.websocket()
            output_pcm = "temp_podcast.pcm"
            output_wav = "podcast.wav"
            
            with open(output_pcm, "wb") as f:
                for line in script.script:
                    voice_id = GUEST_VOICE_ID if line.speaker == "Guest" else HOST_VOICE_ID
                    for output in ws.send(
                        model_id=MODEL_ID,
                        transcript='-' + line.text,
                        voice={"id": voice_id},
                        stream=True,
                        output_format=output_format,
                    ):
                        f.write(output.audio)
            
            ws.close()
            
            # Convert to WAV
            ffmpeg.input(output_pcm, format="f32le").output(output_wav).run()
            os.remove(output_pcm)
            
            return output_wav
        except Exception as e:
            raise Exception(f"Audio generation failed: {str(e)}")