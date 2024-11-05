import os
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import SongModel
from ..schemas import SongSchema
from app.websocket import ws_push_playlist_update
import app.repository as r


class ChatAgentService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def clean(self, input: str) -> str:
        return re.sub(r'[^\x00-\x7F]+', '', input)

    def save_data_to_disk(self) -> None:
        file_data = {
            "all_songs.yml": (SongModel.title, 'song'),
            "all_artists.yml": (SongModel.artist, 'artist'),
            "all_albums.yml": (SongModel.album, 'album'),
        }

        for filename, (column, lookup_type) in file_data.items():
            distinct_values = self.db.query(column).distinct().all()
            with open(filename, "w", encoding="utf-8") as f:
                f.write('version: "3.1"\n')
                f.write('nlu:\n')
                f.write(f'- lookup: {lookup_type}\n')
                f.write('  examples: |\n')
                for value in distinct_values:
                    f.write(f"    - {value[0]}\n")

    async def seed_async(self) -> bool:
        r.seed_db_demo(self.db)
        await ws_push_playlist_update()
        return True

    def _get_songs_response(self, song_models: List[SongModel], entity_name: str) -> Optional[Dict[str, Any]]:
        songs = [song_model.to_dto() for song_model in song_models]
        if len(songs) == 1:
            return {"message": f"The {entity_name} '{songs[0].title}' is by {songs[0].artist}." if entity_name == "song"
                    else f"The {entity_name} '{songs[0].album}' was released in {songs[0].year}.",
                    "song": songs}
        elif len(songs) > 1:
            return {"error": "Multiple matches found", "songs": songs}
        return None  # No match found
    
    def add_song_to_playlist(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        id = r.get_song_by_song_description(self.db, song_description)
        if id:
            song = r.add_song_to_playlist(self.db, 1, id)
            return song
        return None

    async def add_song_to_playlist_async(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        print(song_description)
        id = r.get_song_by_song_description(self.db, song_description)
        if id:
            song = r.add_song_to_playlist(self.db, 1, id)
            await ws_push_playlist_update()
            return song
        return None

    def remove_song_from_playlist(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        id = r.get_song_by_song_description(self.db, song_description) 
        if id:
            song = r.remove_song_from_playlist(self.db, 1, id)
            return song
        return None
    
    async def remove_song_from_playlist_async(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        id = r.get_song_by_song_description(self.db, song_description) 
        if id:
            song = r.remove_song_from_playlist(self.db, 1, id)
            await ws_push_playlist_update()
            return song
        return None
    
    def view_playlist(self, playlist_id: int = 1):
        playlistModel = r.get_playlist(self.db, playlist_id)
        return playlistModel.to_dto() if playlistModel else None

    def clear_playlist(self, playlist_id: int = 1):
        r.clear_playlist(self.db, playlist_id)

    async def clear_playlist_async(self, playlist_id: int = 1):
        r.clear_playlist(self.db, playlist_id)
        await ws_push_playlist_update()

    def get_song_release_date(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        for entity in entity_values:
            entity_value = entity["value"]
            song_models = r.get_songs_by_name(self.db, entity_value)
            songs = [song_model.to_dto() for song_model in song_models]
            if len(songs) == 0:
                continue
            
            if len(songs) == 1:
                return {"message": f"'{songs[0].title}' by {songs[0].artist} was released in {songs[0].year}.", 
                        "song": songs[0]}
            
            if len(songs) > 1: 
                return {"message": "Need more information to identify the song.",
                        "songs": songs}

        return None  # Indicate that no match was found
    
    def get_songs_by_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        for entity_val in entity_values:
            artist_name = entity_val["value"]
            song_models = r.get_songs_by_artist(self.db, artist_name)
            songs = [song_model.to_dto() for song_model in song_models]
            if songs:
                return {"message": f"The songs by {songs[0].artist} are: {', '.join(song.title for song in songs)}",
                        "songs": songs}
        return None  # Indicate that no artist was found

    def get_artist_of_song(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        for entity in entity_values:
            song_name = entity["value"]
            song_models = r.get_songs_by_name(self.db, song_name)
            response = self._get_songs_response(song_models, "song")
            if response:
                return response
        return None  # Indicate that no match was found

    def get_album_release_date(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        for entity in entity_values:
            album_name = entity["value"]
            song_models = r.get_songs_by_album(self.db, album_name)
            response = self._get_songs_response(song_models, "album")
            if response:
                return response
        return None  # Indicate that no album was found

    def get_album_of_song(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        return self.get_artist_of_song(entity_values)  # Similar logic can be reused

    def get_albums_of_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        for entity_val in entity_values:
            artist_name = entity_val["value"]
            song_models = r.get_songs_by_artist(self.db, artist_name)
            unique_albums = set(song.album for song in (song_model.to_dto() for song_model in song_models))
            if unique_albums:
                return {"message": f"The albums by {artist_name} are: {', '.join(unique_albums)}",
                        "albums": list(unique_albums)}
        return None  # Indicate that no artist or albums were found


    ## TODO
    def rasa_add_song_to_playlist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        return
    

    ## TODO
    def rasa_remove_song_from_playlist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        return