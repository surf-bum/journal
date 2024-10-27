from typing import Optional
from pydantic import BaseModel


class CreateNote(BaseModel):
    title: str

class Note(BaseModel):
    id: str
    title: str

class PatchNote(BaseModel):
    title: Optional[str]