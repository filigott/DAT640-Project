from typing import List, Optional
from pydantic import BaseModel

class SongBase(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    year: Optional[int] = None

class Song(SongBase):
    id: int

    class Config:
        orm_mode = True

class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None

class Playlist(PlaylistBase):
    id: int
    songs: List[Song] = []

    class Config:
        orm_mode = True
