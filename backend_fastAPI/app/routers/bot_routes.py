from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..models import SongModel
from ..database import get_db
from ..schemas import SongSchema
from .playlist_routes import add_song as add_song_to_playlist
from .playlist_routes import remove_song as remove_song_from_playlist
import re
import app.repository as r

router = APIRouter()

# TODO: Not used. Logic moved to chat_agent_service

def clean(input):
    return re.sub(r'[^\x00-\x7F]+', '', input)

# Bot add a song to a specific playlist
@router.post("/bot/save_data_to_disk")
async def save_data_to_disk(request: Request, db: Session = Depends(get_db)):
    all_songs = db.query(SongModel.title).distinct().all()
    all_artists = db.query(SongModel.artist).distinct().all()
    all_albums = db.query(SongModel.album).distinct().all()
    print(len(all_songs), len(all_artists), len(all_albums))

    with open("all_songs.yml", "w", encoding="utf-8") as f:
        # Write the version and NLU headers
        f.write('version: "3.1"\n')
        f.write('nlu:\n')
        f.write('- lookup: song\n')
        f.write('  examples: |\n')
        
        # Write each song title with indentation
        for song in all_songs:
            f.write(f"    - {song.title}\n")
    
    with open("all_artists.yml", "w", encoding="utf-8") as f:
        f.write('version: "3.1"\n')
        f.write('nlu:\n')
        f.write('- lookup: artist\n')
        f.write('  examples: |\n')
        
        for artist in all_artists:
            f.write(f"    - {artist[0]}\n")
    
    with open("all_albums.yml", "w", encoding="utf-8") as f:
        f.write('version: "3.1"\n')
        f.write('nlu:\n')
        f.write('- lookup: album\n')
        f.write('  examples: |\n')
        
        for album in all_albums:
            f.write(f"    - {album[0]}\n")


@router.post("/bot/add_song", response_model=SongSchema)
async def add_song(request: Request, db: Session = Depends(get_db)):
    song_description = await request.json()
    id = r.get_song_by_song_description(db, song_description)
    if not id:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song = await add_song_to_playlist(1, id, db)

    return song


# Bot remove a song from a specific playlist
@router.post("/bot/remove_song", response_model=SongSchema)
async def remove_song(request: Request, db: Session = Depends(get_db)):
    song_description = await request.json()
    id = r.get_song_by_song_description(db, song_description)
    if not id:
        raise HTTPException(status_code=404, detail="Song not found")
    
    song = await remove_song_from_playlist(1, id, db)

    return song


@router.post("/bot/song_release_date")
async def song_release_date(request: Request, db: Session = Depends(get_db)):
    song_data = await request.json()
    entity_values = song_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity in entity_values:
        entity = entity["value"] # song name
        print("entity: ", entity)
        songs = r.get_songs_by_name(db, entity)
        if len(songs) == 0:
            continue
        
        if len(songs) == 1:
            return {"message": f"'{entity}' by {songs[0].artist} was released in {songs[0].year}.", 
                    "song": SongSchema.from_orm(songs[0])}
        
        if len(songs) > 1:
            raise HTTPException(status_code=400, detail="Need more information to identify the song")
        
    raise HTTPException(status_code=404, detail="Song not found")

@router.post("/bot/songs_of_artist")
async def songs_of_artist(request: Request, db: Session = Depends(get_db)):
    artist_data = await request.json()
    entity_values = artist_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity_val in entity_values: 
        entity = entity_val["value"] # artist name
        print("entity: ", entity)
        songs = r.get_songs_by_artist(db, entity)
        if len(songs) == 0:
            continue
        return {"message": f"The songs by {songs[0].artist} are: {', '.join([song.title for song in songs])}", 
                "songs": [SongSchema.from_orm(song) for song in songs]}
        
    raise HTTPException(status_code=404, detail="Artist not found")


@router.post("/bot/artist_of_song")
async def artist_of_song(request: Request, db: Session = Depends(get_db)):
    song_data = await request.json()
    entity_values = song_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity in entity_values:
        entity = entity["value"] # song name
        print("entity: ", entity)
        songs = r.get_songs_by_name(db, entity)
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The artist of '{songs[0].title}' is {songs[0].artist}.", 
                    "songs": SongSchema.from_orm(songs[0])}
        if len(songs) > 1:
            return {"message": f"Need more information to identify the song",
                    "second_message": f"{', '.join([song.artist for song in songs])}"}
        
    raise HTTPException(status_code=404, detail="Song not found")

## Prob not the best way to do this
## Assuming album name is unique
@router.post("/bot/album_release_date")
async def album_release_date(request: Request, db: Session = Depends(get_db)):
    album_data = await request.json()
    entity_values = album_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity in entity_values:
        entity = entity["value"] # album name
        print("entity: ", entity)
        songs = r.get_songs_by_album(db, entity)
        print(songs)
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The album '{songs[0].album}' was released in {songs[0].year}.", 
                    "songs": SongSchema.from_orm(songs[0])}
        if len(songs) > 1:
            ## Possible to return all songs in the album here if needed
            return {"message": "Need more information to identify the album"}
        
    raise HTTPException(status_code=404, detail="Song not found")

@router.post("/bot/album_of_song")
async def album_of_song(request: Request, db: Session = Depends(get_db)):
    song_data = await request.json()
    entity_values = song_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity in entity_values:
        entity = entity["value"] # song name
        print("entity: ", entity)
        songs: List[SongModel] = r.get_songs_by_name(db, entity)
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The album of '{songs[0].title}' is '{songs[0].album}'.", 
                    "songs": SongSchema.from_orm(songs[0])}
        
        if len(songs) > 1:
            return {"message": f"Need more information to indentify the song",
                    "second_message": f"{', '.join([song.album for song in songs])}"}
        
    raise HTTPException(status_code=404, detail="Song not found")

@router.post("/bot/albums_of_artist")
async def albums_of_artist(request: Request, db: Session = Depends(get_db)):
    artist_data = await request.json()
    entity_values = artist_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity_val in entity_values: 
        entity = entity_val["value"] # artist name
        print("entity: ", entity)
        songs = r.get_songs_by_artist(db, entity)
        unique_albums = set([song.album for song in songs])
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The album by {songs[0].artist} is: {songs[0].album}", 
                    "songs": SongSchema.from_orm(songs[0])}
        if len(songs) > 1:
            return {"message": f"The albums by {songs[0].artist} are: {', '.join(unique_albums)}", 
                    "songs": [SongSchema.from_orm(song) for song in songs]}
    
    raise HTTPException(status_code=404, detail="Artist not found")
