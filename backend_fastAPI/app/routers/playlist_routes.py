from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..schemas import PlaylistSchema, SongSchema
from ..websocket import ws_push_playlist_update
from ..database import get_db
import app.repository as r

router = APIRouter()

# Get all playlists
@router.get("/playlists", response_model=List[PlaylistSchema])
def read_all_playlists(db: Session = Depends(get_db)):
    playlists = r.get_all_playlists(db)
    # Convert SQLAlchemy models to Pydantic schema
    return [PlaylistSchema.from_orm(playlist) for playlist in playlists]

# Get a specific playlist by its ID
@router.get("/playlist/{playlist_id}", response_model=PlaylistSchema)
def read_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = r.get_playlist(db, playlist_id)
    # Handle the case where the playlist is not found
    if not playlist:
        return {"message": "Playlist not found"}
    # Convert SQLAlchemy model to Pydantic schema
    return PlaylistSchema.from_orm(playlist)

# Get all songs not in a specific playlist matching a searchfield
@router.get("/playlist/{playlist_id}/songs_not_in", response_model=List[SongSchema])
def read_songs_not_in_playlist(playlist_id: int, search: str = "", db: Session = Depends(get_db)):
    """Retrieve a maximum of 10 songs not in a specific playlist, optionally filtering by search term."""
    songs = r.get_search_songs_not_in_playlist(db, playlist_id, search)
    return [SongSchema.from_orm(song) for song in songs]

# Add a song to a specific playlist
@router.post("/playlist/{playlist_id}/add_song/{song_id}")
async def add_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    # Add the song to the playlist
    song = await r.add_song_to_playlist_async(db, playlist_id, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found or already in the playlist")
    # Notify via WebSocket
    await ws_push_playlist_update(playlist_id)
    return SongSchema.from_orm(song)

# Remove a song from a specific playlist
@router.post("/playlist/{playlist_id}/remove_song/{song_id}")
async def remove_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    # Remove the song from the playlist
    song = await r.remove_song_from_playlist_async(db, playlist_id, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found in the playlist")
    # Notify via WebSocket
    await ws_push_playlist_update(playlist_id)
    return SongSchema.from_orm(song)

# Clear a playlist
@router.post("/playlist/{playlist_id}/clear")
async def clear_playlist_async(playlist_id: int, db: Session = Depends(get_db)):
    # Clear all songs from the playlist
    r.clear_playlist(db, playlist_id)
    playlist = r.get_playlist(db, playlist_id)
    # Notify via WebSocket
    await ws_push_playlist_update(playlist_id)
    return PlaylistSchema.from_orm(playlist)
