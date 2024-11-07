from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import SongModel
from ..schemas import SongSchema
from app.websocket import ws_push_playlist_update
import app.repository as r


class ChatAgentService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.position_map = {
            "first": 1,
            "second": 2,
            "third": 3,
            "fourth": 4, 
            "fifth": 5,
            "sixth": 6,
            "seventh": 7,
            "eight": 8,
            "ninth": 9,
            "last": 0
        }

        self.number_map = {
            "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
            "ten": 10,
        }

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

    async def get_song_release_date(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
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
    
    async def get_songs_by_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
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

    async def get_albums_of_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
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
    
    async def remove_from_playlist_position(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        position_data = {}
        for entity_data in entity_values:
            entity = entity_data['entity']
            value = entity_data['value']
            position_data[entity] = value
        
        position = position_data.get("position")
        number = position_data.get("number")
        

        playlist = r.get_playlist(self.db, 1)
        songs = [song for song in playlist.songs]
        
        remove_ids = []

        if position and number:
            pos_index = self.position_map.get(position) - 1
            num = self.number_map.get(number)
            if pos_index == -1:
                songs.reverse()
                songs = songs[0:num]
                remove_ids = [song.id for song in songs]
            else:
                songs = songs[pos_index:num]
                remove_ids = [song.id for song in songs]
            
            for id in remove_ids:
                r.remove_song_from_playlist(self.db, 1, id)
            await ws_push_playlist_update()
            return {"message": "Removed songs from your playlist:", "songs": songs}
        
        if position and not number:
            pos_index = self.position_map.get(position) -1
            r.remove_song_from_playlist(self.db, 1, songs[pos_index].id)
            await ws_push_playlist_update()
            return {"message": f"Song {songs[pos_index].title} by {songs[pos_index].artist} removed from your playlist", "song": songs[pos_index]}     

        return {"message": "Did not understand"}
    
    async def song_release_date_position(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        position_data = {}
        for entity_data in entity_values:
            entity = entity_data['entity']
            value = entity_data['value']
            position_data[entity] = value

        position = position_data.get("position")
        
        playlist = r.get_playlist(self.db, 1)
        songs = [song for song in playlist.songs]

        if position:
            pos_index = self.position_map.get(position) - 1
            song = songs[pos_index]
            return {"message": f"{song.title} by {song.artist} was released in {song.year}."} 

        return {"message": "Did not understand"}
    
    async def recommend_songs_based_on_playlist(self) -> Optional[Dict[str, Any]]:
        songs = r.get_recommendations_from_playlist(self.db)
        recommended_songs = [song.to_dto() for song in songs]
        return {"message": "Recommendations based on your playlist: ", "songs": recommended_songs}

    async def add_from_recommendations(self, entity_values: List[Dict[str, str]], cache) -> Optional[Dict[str, Any]]:
        song_data = {}
        for entity in entity_values:
            e = entity["entity"]
            v = entity["value"]
            song_data[e] = v

        song_ids = []
    
        ## User: Add all songs by XXXXX
        if song_data.get("artist"):
            for song in cache:
                if song.artist == song_data.get("artist"):
                    song_ids.append(song.id)

        ## Add all recommendations
        else:
            for song in cache:
                song_ids.append(song.id)            
    

        result = await self.add_multiple_songs_to_playlist(song_ids)
        return result

    async def add_from_recommendations_position(self, entity_values: List[Dict[str, str]], cache) -> Optional[Dict[str, Any]]:
        position_data = {}
        for entity in entity_values:
            e = entity["entity"]
            v = entity["value"]
            position_data[e] = v
        
        song_ids = []

        position = position_data.get("position")
        number = position_data.get("number")

        if position and number:
            pos_index = self.position_map.get(position) - 1
            number = self.number_map.get(number, number)
            # Wants to add last(position) two(number) songs
            if pos_index == -1:
                cache.reverse()
                songs = cache[0:number]
                song_ids = [song.id for song in songs]
            # Wants to add first(position) two(number) songs
            else: 
                songs = cache[pos_index:number]
                song_ids = [song.id for song in songs]
                print(song_ids)
        elif position and not number:
            # Wants to add the first or second or third song
            pos_num = self.position_map.get(position)
            song =  cache[pos_num-1]
            song_ids.append(song.id)
            print(song_ids)
        result = await self.add_multiple_songs_to_playlist(song_ids)
        return result

    async def add_multiple_songs_to_playlist(self, ids):
        for id in ids:
            r.add_song_to_playlist(self.db, 1, id)
        await ws_push_playlist_update()
        return {"message": "Added songs"}

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
