from fastapi import FastAPI, HTTPException, BackgroundTasks, File, UploadFile, Form
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
from models.anchor import AnchorOutput
from utils.podcast_processor import PodcastProcessor
from utils.anchor_processor import AnchorProcessor
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


# Initialize processors
podcast_processor = PodcastProcessor()
anchor_processor = AnchorProcessor()

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
        input_text = await podcast_processor.get_PDF_text(str(temp_path))
        
        # print(input_text)

        # Generate script
        script = await podcast_processor.generate_podcast_script(input_text)
        print(script.script[0])

        # Generate audio
        audio_path = await podcast_processor.generate_podcast_audio(script)
        
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

@app.post("/api/process-anchor", response_model=AnchorOutput)
async def process_anchor(
    pdf_file: UploadFile = File(...),
    topic: Optional[str] = None,
    language: str = "english",
    background_tasks: BackgroundTasks = None
):
    try:
        temp_path = UPLOAD_DIR / pdf_file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)
        
        input_text = await anchor_processor.get_PDF_text(str(temp_path))
        script = await anchor_processor.generate_script(input_text)
        print(script.script[0])
        
        audio_path = await anchor_processor.generate_audio(script)
        
        background_tasks.add_task(os.remove, temp_path)
        
        return AnchorOutput(
            audio_url=audio_path,
            transcript=script,
            summary=script.scriptNotes
        )
    except Exception as e:
        if 'temp_path' in locals():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/process-and-email")
async def process_and_email_podcast(
    pdf_file: UploadFile = File(...),
    email: str = Form(...),
    is_anchor: bool = Form(False),
    topic: Optional[str] = None,
    language: str = "english"
):
    try:
        # Save uploaded file temporarily
        temp_path = UPLOAD_DIR / pdf_file.filename
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(pdf_file.file, buffer)
        
        # Process based on type
        processor = anchor_processor if is_anchor else podcast_processor
        
        # Get content from PDF
        input_text = await processor.get_PDF_text(str(temp_path))
        
        # Process and email
        result = await processor.process_and_email(input_text, email)
        
        # Clean up
        os.remove(temp_path)
        
        return {
            "success": True,
            "message": f"Content processed and emailed to {email}",
            "audio_url": result["audio_path"],
            "email_sent": result["email_sent"]
        }
        
    except Exception as e:
        if 'temp_path' in locals():
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)