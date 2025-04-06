from pydantic import BaseModel
from typing import List, Literal, Optional

class AnchorLine(BaseModel):
    speaker: Literal["Anchor"]
    text: str

class AnchorScript(BaseModel):
    scriptNotes: str
    script: List[AnchorLine]

class AnchorOutput(BaseModel):
    audio_url: str
    transcript: AnchorScript
    summary: str