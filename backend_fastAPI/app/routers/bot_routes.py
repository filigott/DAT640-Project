from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..repository import get_song_id_by_name, get_songs_by_album, get_songs_by_name, get_songs_by_artist
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

# intents = {
#     "ask_song_release_date": f"{fast_api_endpoint}/bot/song_release_date",
#     "ask_songs_of_artist": f"{fast_api_endpoint}/bot/songs_of_artist",
#     "ask_artist_of_song": f"{fast_api_endpoint}/bot/artist_of_song",
#     "ask_album_release_date": f"{fast_api_endpoint}/bot/album_release_date",
#     "ask_album_of_song": f"{fast_api_endpoint}/bot/album_of_song",
#     "ask_albums_of_artist": f"{fast_api_endpoint}/bot/albums_of_artist"
# }

@router.post("/bot/song_release_date")
async def song_release_date(request: Request, db: Session = Depends(get_db)):
    song_data = await request.json()
    entity_values = song_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity in entity_values:
        entity = entity["value"] # song name
        print("entity: ", entity)
        songs = get_songs_by_name(db, entity)
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
        songs = get_songs_by_artist(db, entity)
        if len(songs) == 0:
            continue
        return {"message": f"The songs by {entity} are: {', '.join([song.title for song in songs])}", 
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
        songs = get_songs_by_name(db, entity)
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The artist of '{entity}' is {songs[0].artist}.", 
                    "songs": SongSchema.from_orm(songs[0])}
        if len(songs) > 1:
            return {"message": f"Multiple artists have released a song with name: '{entity}'",
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
        songs = get_songs_by_album(db, entity)
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The album '{entity}' was released in {songs[0].year}.", 
                    "songs": SongSchema.from_orm(songs[0])}
        if len(songs) > 1:
            ## Possible to return all songs in the album here if needed
            return {"message": f"The album '{entity}' was released in {songs[0].year}."}
        
    raise HTTPException(status_code=404, detail="Song not found")

@router.post("/bot/album_of_song")
async def album_of_song(request: Request, db: Session = Depends(get_db)):
    song_data = await request.json()
    entity_values = song_data["data"]
    # if rasa returns mulitple entities. Not given the first is correct
    for entity in entity_values:
        entity = entity["value"] # song name
        print("entity: ", entity)
        songs = get_songs_by_name(db, entity)
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The album of '{entity}' is '{songs[0].album}'.", 
                    "songs": SongSchema.from_orm(songs[0])}
        
        if len(songs) > 1:
            return {"message": f"Multiple albums contains the song with name: '{entity}'",
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
        songs = get_songs_by_artist(db, entity)
        unique_albums = set([song.album for song in songs])
        if len(songs) == 0:
            continue
        if len(songs) == 1:
            return {"message": f"The album by {entity} is: {songs[0].album}", 
                    "songs": SongSchema.from_orm(songs[0])}
        if len(songs) > 1:
            return {"message": f"The albums by {entity} are: {', '.join(unique_albums)}", 
                    "songs": [SongSchema.from_orm(song) for song in songs]}
    
    raise HTTPException(status_code=404, detail="Artist not found")
