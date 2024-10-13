import json
from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from .websocket import WSConnectionManager

from .init_db import seed_db
from .database import engine, Base, get_db
from .crud import (
    add_song_to_playlist,
    bot_get_song_id,
    bot_get_song_id_by_name,
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

ws_manager = WSConnectionManager()

# Endpoint to seed the database
@app.get("/seed")
def seed_database(db: Session = Depends(get_db)):
    try:
        seed_db(db)  # Seed the database with demo data
        return {"message": "Database seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all playlists
@app.get("/playlists", response_model=List[Playlist])
def read_all_playlists(db: Session = Depends(get_db)):
    playlists = get_all_playlists(db)
    print(playlists)
    return playlists

# Get all songs in the database
@app.get("/songs", response_model=List[Song])
def read_all_songs(db: Session = Depends(get_db)):
    songs = get_all_songs(db)
    print(songs)
    return songs

# Get a specific playlist by its ID
@app.get("/playlist/{playlist_id}", response_model=Playlist)
def read_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return playlist

# Get all songs not in a specific playlist
@app.get("/playlist/{playlist_id}/songs_not_in", response_model=List[Song])
def read_songs_not_in_playlist(playlist_id: int, db: Session = Depends(get_db)):
    return get_songs_not_in_playlist(db, playlist_id)

# Add a song to a specific playlist
@app.post("/playlist/{playlist_id}/add_song/{song_id}")
async def add_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    await add_song_to_playlist(db, playlist_id, song_id)
    message = {"updated_playlist_id": playlist_id}
    await ws_manager.broadcast(json.dumps(message)) 
    return {"message": "Song added to the playlist"}

# Remove a song from a specific playlist
@app.post("/playlist/{playlist_id}/remove_song/{song_id}")
async def remove_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    await remove_song_from_playlist(db, playlist_id, song_id)
    message = {"updated_playlist_id": playlist_id}
    await ws_manager.broadcast(json.dumps(message))  
    return {"message": "Song removed from the playlist"}

# Clear a playlist
@app.post("/playlist/{playlist_id}/clear")
async def clear_playlist(playlist_id: int, db: Session = Depends(get_db)):
    playlist = get_playlist(db, playlist_id)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")
    playlist.songs = []
    db.commit()
    message = {"updated_playlist_id": playlist_id}
    await ws_manager.broadcast(json.dumps(message))  
    return {"message": "Playlist cleared"}

@app.websocket("/ws/playlist")
async def websocket_endpoint(websocket: WebSocket):
    print(websocket)
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages if necessary
            _ = await websocket.receive_text()  # Can be used if client sends data
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# Simulate playlist update and broadcast it to all connected clients
@app.get("/test/playlist/{playlist_id}/add_song/{song_id}")
async def test_add_song_ws(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    await add_song(db, playlist_id, song_id)
    # Broadcast the updated playlist to all connected WebSocket clients
    message = {"updated_playlist_id": playlist_id}
    await ws_manager.broadcast(json.dumps(message))  
    return {"message": "Song added and broadcasted"}




# Simulate playlist update and broadcast it to all connected clients
@app.post("/bot/get_song_id")
async def bot_get_song(request: Request, db: Session = Depends(get_db)):
    print(await request.json())
    id = bot_get_song_id_by_name(db, await request.json())
    # Broadcast the updated playlist to all connected WebSocket clients
    
    return {"song_id": id}