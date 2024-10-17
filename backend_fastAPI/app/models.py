from sqlalchemy import Column, Integer, String, ForeignKey, Table
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

    playlists = relationship('PlaylistModel', secondary=PlaylistSongsTable, back_populates='songs')

class PlaylistModel(DB_Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

    songs = relationship('SongModel', secondary=PlaylistSongsTable, back_populates='playlists')


# # Many-to-Many Association Table for songs and playlists
# playlist_songs_table = Table(
#     'playlist_songs',
#     DB_Base.metadata,
#     Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
#     Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True)
# )

# song_genre_table = Table(
#     'song_genre',
#     DB_Base.metadata,
#     Column('song_id', Integer, ForeignKey('songs.id'), primary_key=True),
#     Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
# )

# class Artist_model(DB_Base):
#     __tablename__ = 'artists'
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)

#     albums = relationship('Album_model', back_populates='artist')
#     songs = relationship('Song_model', back_populates='artist', viewonly=True)

# class Album_model(DB_Base):
#     __tablename__ = 'albums'
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     release_year = Column(Integer)

#     artist_id = Column(Integer, ForeignKey('artists.id'))
#     artist = relationship('Artist_model', back_populates='albums')
#     songs = relationship('Song_model', back_populates='album')

# class Genre_model(DB_Base):
#     __tablename__ = 'genres'
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)

#     songs = relationship('Song_model', secondary=song_genre_table, back_populates='genres')

# class Song_model(DB_Base):
#     __tablename__ = 'songs'
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)

#     album_id = Column(Integer, ForeignKey('albums.id'))
#     album = relationship('Album_model', back_populates='songs')
#     artist_id = Column(Integer, ForeignKey('artists.id'))
#     artist = relationship('Artist_model', back_populates='songs')

#     genres = relationship('Genre_model', secondary=song_genre_table, back_populates='songs')

# class Playlist_model(DB_Base):
#     __tablename__ = 'playlists'
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)

#     songs = relationship('Song_model', secondary=playlist_songs_table, back_populates='playlists', viewonly=True)

