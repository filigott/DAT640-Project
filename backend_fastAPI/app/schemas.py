from pydantic import BaseModel
from typing import List, Optional

# Base model for songs and playlists
class SongSchemaBase(BaseModel):
    title: str
    artist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[int] = None

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


# # Base models for each entity
# class SongBase(BaseModel):
#     title: str

# class AlbumBase(BaseModel):
#     title: str
#     release_year: int

# class ArtistBase(BaseModel):
#     name: str

# class GenreBase(BaseModel):
#     name: str

# class PlaylistBase(BaseModel):
#     title: str

# # Derived models including additional fields and relationships
# class SongOut(SongBase):
#     id: int
#     album: Optional['AlbumOut'] = None
#     artist: Optional['ArtistOut'] = None
#     genres: List['GenreOut'] = []

#     class Config:
#         orm_mode = True

# class AlbumOut(AlbumBase):
#     id: int
#     artist: Optional['ArtistOut'] = None
#     songs: List[SongOut] = []

#     class Config:
#         orm_mode = True

# class ArtistOut(ArtistBase):
#     id: int
#     albums: List[AlbumOut] = []
#     songs: List[SongOut] = []

#     class Config:
#         orm_mode = True

# class GenreOut(GenreBase):
#     id: int
#     songs: List[SongOut] = []

#     class Config:
#         orm_mode = True

# class PlaylistOut(PlaylistBase):
#     id: int
#     songs: List[SongOut] = []

#     class Config:
#         orm_mode = True

