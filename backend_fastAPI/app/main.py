from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.orm import Session

from .init_db import seed_db
from .database import engine, Base, get_db
from .crud import (
    add_song_to_playlist,
    remove_song_from_playlist,
    get_playlist,
    get_songs_not_in_playlist,
    get_all_playlists,
    get_all_songs,
)
from .schemas import Playlist, Song

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Endpoint to seed the database
@app.get("/seed")
def seed_database(db: Session = Depends(get_db)):
    try:
        seed_db(db)  # Seed the database with demo data
        return {"message": "Database seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get a specific playlist by its ID
@app.get("/playlist/{playlist_id}", response_model=Playlist)
def read_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist


# Get all playlists
@app.get("/playlists", response_model=List[Playlist])
def read_all_playlists(db: Session = Depends(get_db)):
    playlists = get_all_playlists(db)
    return playlists


# Get all songs in the database
@app.get("/songs", response_model=List[Song])
def read_all_songs(db: Session = Depends(get_db)):
    songs = get_all_songs(db)
    print(songs)
    return songs


# Get all songs not in a specific playlist
@app.get("/playlist/{playlist_id}/songs_not_in", response_model=List[Song])
def read_songs_not_in_playlist(playlist_id: int, db: Session = Depends(get_db)):
    return get_songs_not_in_playlist(db, playlist_id)


# Add a song to a specific playlist
@app.post("/playlist/{playlist_id}/add_song/{song_id}")
def add_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    add_song_to_playlist(db, playlist_id, song_id)
    return {"message": "Song added to the playlist"}


# Remove a song from a specific playlist
@app.post("/playlist/{playlist_id}/remove_song/{song_id}")
def remove_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    remove_song_from_playlist(db, playlist_id, song_id)
    return {"message": "Song removed from the playlist"}
