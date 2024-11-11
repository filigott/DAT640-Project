from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from ..models import SongModel
from ..schemas import SongSchema
from app.websocket import ws_push_playlist_update
from app.chat_agent.chat_utils import IntentType
import app.repository as r


class ChatAgentService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.position_map = {
            "first": 1, "second": 2, "third": 3, "fourth": 4, 
            "fifth": 5, "sixth": 6, "seventh": 7, "eight": 8,
            "ninth": 9, "last": 0
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
    

    @staticmethod
    def _get_entity_value(entities: List[Dict[str, str]], entity_name: str) -> Optional[str]:
        return next((e['value'] for e in entities if e['entity'] == entity_name), None)
    

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
        song_name = self._get_entity_value(entity_values, IntentType.song.value)
        if song_name:
            song_models = r.get_songs_by_name(self.db, song_name)
            if song_models:
                song = song_models[0].to_dto()  # Assuming we use the first result if multiple are found
                return {"message": f"The song '{song.title}' by {song.artist} was released in {song.year}.", "song": song}
        return None 
    

    def get_songs_by_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        artist_name = self._get_entity_value(entity_values, IntentType.artist.value)
        if artist_name:
            song_models = r.get_songs_by_artist(self.db, artist_name)
            songs = [song_model.to_dto() for song_model in song_models]
            if songs:
                song_titles = ', '.join(song.title for song in songs)
                return {"message": f"The songs by {artist_name} are: {song_titles}.", "songs": songs}
        return None


    def get_artist_of_song(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        song_name = self._get_entity_value(entity_values, IntentType.song.value)
        if song_name:
            song_models = self.find_song_matches(title=song_name)
            if song_models:
                song = song_models[0].to_dto()  # Use the first matching song
                return {"message": f"The artist of the song '{song.title}' is {song.artist}.", "song": song}
        return None  # No match found


    def get_album_release_date(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        album_name = self._get_entity_value(entity_values, IntentType.album.value)
        if album_name:
            song_models = r.get_songs_by_album(self.db, album_name)
            if song_models:
                album_song = song_models[0].to_dto()  # Assume using the first song in the album to get the year
                return {"message": f"The album '{album_song.album}' was released in {album_song.year}.", "album": album_song.album}
        return None  # No album found


    def get_albums_of_song(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        song_name = self._get_entity_value(entity_values, IntentType.song.value)
        if song_name:
            song_models = self.find_song_matches(title=song_name)
            if song_models:
                unique_albums = set(song.album for song in song_models)
                if unique_albums:
                    return {
                        "message": f"The albums that feature the song {song_name} are: {', '.join(unique_albums)}",
                        "albums": list(unique_albums)
                    }
        return None  # No albums found for the given song


    def get_albums_of_artist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        artist_name = self._get_entity_value(entity_values, IntentType.artist.value)
        if artist_name:
            song_models = r.get_songs_by_artist(self.db, artist_name)
            unique_albums = set(song.album for song in (song_model.to_dto() for song_model in song_models))
            if unique_albums:
                return {"message": f"The albums by {artist_name} are: {', '.join(unique_albums)}",
                        "albums": list(unique_albums)}
        return None  # No artist or albums found
    

    async def rasa_remove_song_from_playlist(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        song_data = {
            "title": self._get_entity_value(entity_values, "song"),
            "artist": self._get_entity_value(entity_values, "artist")
        }
        if song_data.get("title"):
            result = await self.remove_song_from_playlist_async(song_data)
            return {"message": f"Song '{result.title}' by '{result.artist}' was removed from playlist.", "song": result}
        
        return None
    

    async def remove_from_playlist_position(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        position = self._get_entity_value(entity_values, "position")
        number = self._get_entity_value(entity_values, "number")

        playlist = r.get_playlist(self.db, 1)
        songs = SongModel.list_to_dto(playlist.songs)

        remove_ids = []

        if position and number:
            pos_index = self.position_map.get(position) - 1
            num = self.number_map.get(number)

            if pos_index == -1:
                songs.reverse()
                songs = songs[:num]
            else:
                songs = songs[pos_index:num]

            remove_ids = [song.id for song in songs]
            for id in remove_ids:
                r.remove_song_from_playlist(self.db, 1, id)

            await ws_push_playlist_update()
            return {"message": "Removed songs from your playlist:", "songs": songs}
        
        if position and not number:
            pos_index = self.position_map.get(position) - 1
            song_to_remove = songs[pos_index]
            r.remove_song_from_playlist(self.db, 1, song_to_remove.id)
            await ws_push_playlist_update()

            return {"message": f"Song {song_to_remove.title} by {song_to_remove.artist} removed from your playlist", "song": song_to_remove}

        return {"message": "Did not understand"}
    

    async def song_release_date_position(self, entity_values: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
        position = self._get_entity_value(entity_values, "position")

        playlist = r.get_playlist(self.db, 1)
        songs = playlist.songs

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
        artist = self._get_entity_value(entity_values, "artist")
        song_ids = []

        # If artist is specified, add songs by the artist
        if artist:
            song_ids = [song.id for song in cache if song.artist == artist]
        else:
            song_ids = [song.id for song in cache]  # Add all recommendations

        result = await self.add_multiple_songs_to_playlist(song_ids)
        return result


    async def add_from_recommendations_position(self, entity_values: List[Dict[str, str]], cache) -> Optional[Dict[str, Any]]:
        position = self._get_entity_value(entity_values, "position")
        number = self._get_entity_value(entity_values, "number")

        song_ids = []

        if position and number:
            pos_index = self.position_map.get(position) - 1
            number = self.number_map.get(number, number)

            # Wants to add last(position) two(number) songs
            if pos_index == -1:
                cache.reverse()
                song_ids = [song.id for song in cache[:number]]
            else:
                song_ids = [song.id for song in cache[pos_index:number]]
        elif position and not number:
            pos_num = self.position_map.get(position)
            song_ids.append(cache[pos_num - 1].id)

        result = await self.add_multiple_songs_to_playlist(song_ids)
        return result


    async def add_multiple_songs_to_playlist(self, ids) -> Dict[str, Any]:
        songs = []

        # Add each song by ID
        for id in ids:
            song = r.add_song_to_playlist(self.db, 1, id)
            if song:
                songs.append(song)

        # Push playlist update after all songs are added
        await ws_push_playlist_update()

        return {"message": "Added songs:", "songs": songs}


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
