from pydantic import BaseModel
from typing import List, Optional

# Base model for songs and playlists
class SongSchemaBase(BaseModel):
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None
    duration: Optional[int] = None
    tempo: Optional[float] = None

class PlaylistSchemaBase(BaseModel):
    title: str

# Derived models including additional fields and relationships
class SongSchema(SongSchemaBase):
    id: int

    class Config:
        orm_mode = True

class PlaylistSchema(PlaylistSchemaBase):
    id: int
    songs: List[SongSchema] = []

    class Config:
        orm_mode = True