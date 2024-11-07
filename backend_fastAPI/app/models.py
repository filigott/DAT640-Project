from typing import List
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import relationship

from .schemas import PlaylistSchema, SongSchema
from .database import DB_Base

# Many-to-Many Association Table for songs and playlists
PlaylistSongsTable = Table(
    'playlist_songs',
    DB_Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True)
)

class SongModel(DB_Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, nullable=False)
    album = Column(String)
    year = Column(Integer)
    duration = Column(Integer)
    tempo = Column(Float)

    # New normalized title column
    normalized_title = Column(String, nullable=False)

    playlists = relationship('PlaylistModel', secondary=PlaylistSongsTable, back_populates='songs')

    def to_dto(self):
        """Map the SongModel instance to SongSchema for JSON serialization."""
        return SongSchema.from_orm(self)
    
    @classmethod
    def list_to_dto(cls, song_models) -> List[SongSchema]:
        """Map a list of SongModel instances to a list of SongSchema instances."""
        return [song.to_dto() for song in song_models]

class PlaylistModel(DB_Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

    songs = relationship('SongModel', secondary=PlaylistSongsTable, back_populates='playlists')

    def to_dto(self):
        """Map the PlaylistModel instance to PlaylistSchema for JSON serialization."""
        return PlaylistSchema.from_orm(self)
