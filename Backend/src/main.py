from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import shutil
import os
from pathlib import Path
# from motor.motor_asyncio import AsyncIOMotorClient
import pypdf
import together
import cartesia
import ffmpeg
from models.podcast import PodcastInput, PodcastOutput
from utils.podcast_processor import PodcastProcessor
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

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/process-podcast", response_model=PodcastOutput)
async def process_podcast(
    pdf_file: UploadFile = File(...),
    topic: Optional[str] = None,
    language: str = "english",
    background_tasks: BackgroundTasks = None
):
    try:
        # Save uploaded file temporarily
        temp_path = UPLOAD_DIR / pdf_file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)
        
        # Get content from PDF
        input_text = await processor.get_PDF_text(str(temp_path))
        
        # print(input_text)

        # Generate script
        script = await processor.generate_script(input_text)
        print(script.script[0])

        # Generate audio
        audio_path = await processor.generate_audio(script)
        
        # Only clean up the temporary PDF file
        background_tasks.add_task(os.remove, temp_path)
        
        return PodcastOutput(
            audio_url=audio_path,
            transcript=script,
            summary=script.scratchpad
        )
    except Exception as e:
        # Clean up on error
        if 'temp_path' in locals():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)