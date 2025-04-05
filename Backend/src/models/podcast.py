from pydantic import BaseModel
from typing import List, Literal, Optional

class LineItem(BaseModel):
    speaker: Literal["Host (Jane)", "Guest"]
    text: str

class Script(BaseModel):
    scratchpad: str
    name_of_guest: str
    script: List[LineItem]

class PodcastInput(BaseModel):
    url: str
    pdf_content: Optional[str] = None
    topic: Optional[str] = None
    language: Optional[str] = "english"

class PodcastOutput(BaseModel):
    audio_url: str
    transcript: Script
    summary: str