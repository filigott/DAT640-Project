from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..repository import add_song_to_playlist, remove_song_from_playlist
from ..schemas import SongSchema

router = APIRouter()

# Clients add a song to a specific playlist directly
@router.post("/client/playlist/{playlist_id}/add_song/{song_id}", response_model=SongSchema)
async def add_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    song = await add_song_to_playlist(db, playlist_id, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found or already in the playlist")
    return SongSchema.from_orm(song)

# Clients remove a song from a specific playlist directly
@router.post("/client/playlist/{playlist_id}/remove_song/{song_id}", response_model=SongSchema)
async def remove_song(playlist_id: int, song_id: int, db: Session = Depends(get_db)):
    song = await remove_song_from_playlist(db, playlist_id, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found in the playlist")
    return SongSchema.from_orm(song)
