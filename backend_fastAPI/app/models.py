from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import relationship
from .database import DB_Base

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
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

    playlists = relationship('PlaylistModel', secondary=PlaylistSongsTable, back_populates='songs')

class PlaylistModel(DB_Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

    songs = relationship('SongModel', secondary=PlaylistSongsTable, back_populates='playlists')
