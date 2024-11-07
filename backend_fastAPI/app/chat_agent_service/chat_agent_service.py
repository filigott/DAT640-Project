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
            song_model = r.add_song_to_playlist(self.db, 1, id)
            return song_model.to_dto()
        return None

    async def add_song_to_playlist_async(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        print(song_description)
        id = r.get_song_by_song_description(self.db, song_description)
        if id:
            song_model = r.add_song_to_playlist(self.db, 1, id)
            await ws_push_playlist_update()
            return song_model.to_dto()
        return None

    def remove_song_from_playlist(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        id = r.get_song_by_song_description(self.db, song_description) 
        if id:
            song_model = r.remove_song_from_playlist(self.db, 1, id)
            return song_model.to_dto()
        return None
    
    async def remove_song_from_playlist_async(self, song_description: Dict[str, Any]) -> Optional[SongSchema]:
        id = r.get_song_by_song_description(self.db, song_description) 
        if id:
            song_model = r.remove_song_from_playlist(self.db, 1, id)
            await ws_push_playlist_update()
            return song_model.to_dto()
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


    ## TODO
    def get_album_of_song(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        return 

    def get_albums_of_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        for entity_val in entity_values:
            artist_name = entity_val["value"]
            song_models = r.get_songs_by_artist(self.db, artist_name)
            unique_albums = set(song.album for song in (song_model.to_dto() for song_model in song_models))
            if unique_albums:
                return {"message": f"The albums by {artist_name} are: {', '.join(unique_albums)}",
                        "albums": list(unique_albums)}
        return None  # Indicate that no artist or albums were found
    

    async def rasa_remove_song_from_playlist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        song_data = {}
        for entity_data in entity_values:
            if entity_data['entity'] == "song":
                value = entity_data['value']
                song_data["title"] = value
            if entity_data['entity'] == "artist":
                value = entity_data['value']
                song_data["artist"] = value

        if song_data.get("title"):
            result = await self.remove_song_from_playlist_async(song_data)
            return {"message": f"Song '{result.title}' by '{result.artist}' was removed from playlist.",
                        "song": result}
        
        return None
        

    def find_song_matches(
        self, 
        title: str, 
        artist: Optional[str] = None, 
        album: Optional[str] = None, 
        year: Optional[int] = None
    ) -> List[SongSchema]:
        """Finds matching songs based on title and other optional fields like artist, album, and year."""

        # Step 1: Attempt an exact match first
        exact_match = r.find_exact_song_match(self.db, title, artist, album, year)
        
        if exact_match:
            # Return a single exact match as a list with one item
            return [SongModel.to_dto(exact_match)]

        # Step 2: If no exact match, try flexible matching with find_song_matches
        matched_songs_models = r.find_fuzzy_song_matches(self.db, title, artist, album, year)
        
        # If matches are found, convert the list of SongModel instances to DTOs
        if matched_songs_models:
            return SongModel.list_to_dto(matched_songs_models)

        # Return an empty list if no matches are found
        return []