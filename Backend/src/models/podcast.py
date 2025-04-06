from pydantic import BaseModel
from typing import List, Literal, Optional
from fastapi import UploadFile

class LineItem(BaseModel):
    speaker: Literal["Host", "Guest"]
    text: str

class Script(BaseModel):
    scratchpad: str
    name_of_guest: str
    script: List[LineItem]

class PodcastInput(BaseModel):
    pdf_content: Optional[str] = None
    topic: Optional[str] = None
    language: Optional[str] = "english"

    class Config:
        arbitrary_types_allowed = True

class PodcastOutput(BaseModel):
    audio_url: str
    transcript: Script
    summary: str
