from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..repository import get_song_id_by_name
from ..schemas import SongSchema
from .playlist_routes import add_song as add_song_to_playlist
from .playlist_routes import remove_song as remove_song_from_playlist

router = APIRouter()

# Bot add a song to a specific playlist
@router.post("/bot/add_song", response_model=SongSchema)
async def add_song(request: Request, db: Session = Depends(get_db)):
    song_description = await request.json()
    id = get_song_id_by_name(db, song_description)
    if not id:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song = await add_song_to_playlist(1, id, db)

    return song


# Bot remove a song from a specific playlist
@router.post("/bot/remove_song", response_model=SongSchema)
async def remove_song(request: Request, db: Session = Depends(get_db)):
    song_description = await request.json()
    id = get_song_id_by_name(db, song_description)
    if not id:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song = await remove_song_from_playlist(1, id, db)

    return song