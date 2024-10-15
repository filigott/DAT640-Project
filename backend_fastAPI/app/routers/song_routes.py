from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List

from ..schemas import SongSchema
from ..database import get_db
from ..repository import get_song_id_by_name, get_all_songs

router = APIRouter()

# Get all songs in the database
@router.get("/songs", response_model=List[SongSchema])
def read_all_songs(db: Session = Depends(get_db)):
    songs = get_all_songs(db)
    print(songs[0:20])
    return [SongSchema.from_orm(song) for song in songs]


# Simulate playlist update and broadcast it to all connected clients
@router.post("/songs/get_song_id", response_model=SongSchema)
async def bot_get_song(request: Request, db: Session = Depends(get_db)):
    print(await request.json())
    id = get_song_id_by_name(db, await request.json())
    # Broadcast the updated playlist to all connected WebSocket clients
    
    return {"song_id": id}