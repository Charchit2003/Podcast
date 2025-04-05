from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
# from motor.motor_asyncio import AsyncIOMotorClient
import pypdf
import together
import cartesia
import ffmpeg
from models.podcast import PodcastInput, PodcastOutput
from utils.podcast_processor import PodcastProcessor
import os
from dotenv import load_dotenv

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
# MONGO_URI = "your_mongodb_uri_here"
# client = AsyncIOMotorClient(MONGO_URI)
# db = client.podcast_db

# User model
class User(BaseModel):
    username: str
    email: str
    password: str

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to the API"}


# Initialize podcast processor
processor = PodcastProcessor()

@app.post("/api/process-podcast", response_model=PodcastOutput)
async def process_podcast(podcast: PodcastInput, background_tasks: BackgroundTasks):
    try:
        # Get content from PDF if provided
        input_text = podcast.pdf_content
        if not input_text and podcast.url.endswith('.pdf'):
            input_text = await processor.get_PDF_text(podcast.url)

        # Generate script
        script = await processor.generate_script(input_text)
        
        # Generate audio
        audio_path = await processor.generate_audio(script)
        
        # Clean up in background
        background_tasks.add_task(os.remove, audio_path)
        
        return PodcastOutput(
            audio_url=audio_path,
            transcript=script,
            summary=script.scratchpad
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)