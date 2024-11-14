import random
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

    def create_playlist_if_not_exist(self, user_id: int):
        print(f"Trying to create playlist for user {user_id}, if not exist.")
        r.create_playlist(self.db, user_id)

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


    async def add_song_to_playlist_async(self, song_description: Dict[str, Any], user_id: int) -> Optional[SongSchema]:
        print(song_description)
        id = r.get_song_by_song_description(self.db, song_description)
        if id:
            song_model = r.add_song_to_playlist(self.db, playlist_id=user_id, song_id=id)
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
        songs = r.get_recommendations_from_songs(self.db, 1)
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

        result = await self.add_multiple_songs_to_playlist_async(song_ids)
        return result


    async def add_from_recommendations_position(self, entity_values: List[Dict[str, str]], cache) -> Optional[Dict[str, Any]]:
        position = self._get_entity_value(entity_values, "position")
        number = self._get_entity_value(entity_values, "number")

        song_ids = []

        if position and number:
            pos_index = self.position_map.get(position)
            if pos_index is None:
                pos_index = int(position) - 1
            else:
                pos_index -= 1
            number = self.number_map.get(number, number)
            print(pos_index)
            print(number)

            # Wants to add last(position) two(number) songs
            if pos_index == -1:
                cache.reverse()
                song_ids = [song.id for song in cache[:number]]
            else:
                song_ids = [song.id for song in cache[pos_index:pos_index+number]]
        elif position and not number:
            pos_index = self.position_map.get(position)
            if pos_index is None:
                pos_index = int(position) - 1
            else:
                pos_index -= 1
            song_ids.append(cache[pos_index].id)

        result = await self.add_multiple_songs_to_playlist_async(song_ids)
        return result

    async def add_from_recommendations_except(self, entity_values, cache):
        artist = self._get_entity_value(entity_values, "artist")
        position = self._get_entity_value(entity_values, "position")
        number = self._get_entity_value(entity_values, "number")        
        song_ids = []

        # Add all except the songs by aritst
        if artist and not position and not number:
            song_ids = [song.id for song in cache if song.artist != artist]

        elif not artist and position and number:
            pass
        elif not artist and position and not number:
            pos_num = self.position_map.get(position)
            song_ids = [song.id for index, song in enumerate(cache) if index != pos_num - 1] 

        result = await self.add_multiple_songs_to_playlist_async(song_ids)
        return result            

    async def add_multiple_songs_to_playlist_async(self, ids) -> Dict[str, Any]:
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

        print("Exact match: ", exact_match)
        
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
    

    async def create_playlist_from_description(self, entities: list) -> Optional[Dict[str, Any]]:
        # Get inferred playlist length
        playlist_length = self.infer_playlist_length(entities)
        print("Inferred playlist length:", playlist_length)

        # Get mood and activity from the entities
        mood = self._get_entity_value(entities, "mood")
        activity = self._get_entity_value(entities, "activity")

        # Use service to get recommended songs based on description
        recommended_songs = await self.filter_songs_by_playlist_description(mood, activity, playlist_length)

        print("Number of recommended songs found for playlist: ", len(recommended_songs))

        if recommended_songs:
            self.clear_playlist()
            song_ids = [song.id for song in recommended_songs]
            await self.add_multiple_songs_to_playlist_async(song_ids)

            # Return the playlist with the recommended songs
            return {"message": f"Created a playlist with {len(recommended_songs)} songs based on your description.",
                    "songs": recommended_songs}
        
        return {"message": "Found no songs fitting the wanted playlist description."}
    

    async def filter_songs_by_playlist_description(self, mood: Optional[str], activity: Optional[str], playlist_length_minutes: int) -> List[dict]:
        # Query the database to get all songs
        songs = SongModel.list_to_dto(r.get_all_songs(self.db))

        print(songs[0])

        # Filter songs by mood and activity
        if mood:
            songs = [song for song in songs if self.match_mood(song, mood)]
        if activity:
            songs = [song for song in songs if self.match_activity(song, activity)]

        # Calculate the average song duration from the list of songs
        # Assuming each song has a 'duration' field in seconds (e.g., 180 seconds = 3 minutes)
        total_duration = sum(song.duration for song in songs)
        num_songs = len(songs)

        print("Num songs still here after mood and activity filtering: ", num_songs)
        
        if num_songs == 0:
            return []  # If no songs are found after filtering, return an empty list
        
        average_song_duration = total_duration / num_songs  # average song duration in seconds
        average_song_duration_minutes = average_song_duration / 60  # convert to minutes
        
        # Calculate how many songs fit in the requested playlist length
        num_songs_needed = int(playlist_length_minutes / average_song_duration_minutes)
        
        # If there are more songs than needed, select randomly
        if len(songs) > num_songs_needed:
            songs = r.get_recommendations_from_songs(self.db, 1, songs, num_songs_needed)

        return songs
    

    def match_mood(self, song: SongSchema, mood: str) -> bool:
        match mood:
            case "sad":
                return (song.valence or 0) < 0.3  # Stricter threshold for sadness
            case "energetic":
                return (song.energy or 0) > 0.75  # Higher energy required for energetic
            case "chill":
                return (song.valence or 0) > 0.55 and (song.energy or 0) < 0.3  # Higher valence and lower energy for chill
            case "upbeat":
                return (song.energy or 0) > 0.75 and (song.valence or 0) > 0.55  # Stricter upbeat condition
            case "romantic":
                return (song.valence or 0) > 0.7 and (song.energy or 0) < 0.6  # Romantic needs higher valence
            case "relaxing":
                return (song.energy or 0) < 0.3  # Lower energy required for relaxing
            case "calm":
                return (song.energy or 0) < 0.35 and (song.valence or 0) > 0.55  # Calm requires even lower energy and higher valence
            case "happy":
                return (song.valence or 0) > 0.65  # Stricter threshold for happy songs
            case "motivational":
                return (song.energy or 0) > 0.75 and (song.valence or 0) > 0.6  # Both higher energy and valence
            case "fun":
                return (song.danceability or 0) > 0.75  # Increased danceability for fun
            case "lively":
                return (song.energy or 0) > 0.65  # Stricter threshold for lively
            case "peaceful":
                return (song.valence or 0) > 0.7 and (song.energy or 0) < 0.3  # Peaceful needs high valence, low energy
            case "bright":
                return (song.energy or 0) > 0.7 and (song.valence or 0) > 0.65  # Stricter threshold for bright
            case "mellow":
                return (song.energy or 0) < 0.4  # Mellow requires lower energy
            case "uplifting":
                return (song.valence or 0) > 0.7 and (song.energy or 0) > 0.55  # Both high valence and energy for uplifting
            case "fast-paced":
                return (song.tempo or 0) > 120  # Stricter fast-paced tempo requirement
            case "slow":
                return (song.tempo or 0) < 85  # Stricter slow tempo
            case "pump-up":
                return (song.energy or 0) > 0.85  # Very high energy for pump-up
            case _:
                return False


    def match_activity(self, song: SongSchema, activity: str) -> bool:
        match activity:
            case "gym":
                return (song.energy or 0) > 0.8  # Requires higher energy for gym
            case "workout":
                return (song.energy or 0) > 0.8  # Higher energy required for workout
            case "study":
                return (song.instrumentalness or 0) > 0.6  # Stricter instrumentalness threshold for study
            case "party":
                return (song.danceability or 0) > 0.75  # Increased danceability for party
            case "road trip":
                return (song.energy or 0) > 0.65 and (song.danceability or 0) > 0.65  # Higher requirements for energy and danceability
            case "sleep":
                return (song.energy or 0) < 0.25  # Much lower energy required for sleep
            case "running":
                return (song.energy or 0) > 0.7 and (song.tempo or 0) > 120  # Higher energy and tempo for running
            case "meditation":
                return (song.energy or 0) < 0.3 and (song.instrumentalness or 0) > 0.7  # Requires both low energy and high instrumentalness
            case "relaxation":
                return (song.energy or 0) < 0.4 and (song.valence or 0) > 0.65  # More strict relaxing conditions
            case "evening":
                return (song.energy or 0) < 0.45  # Lower energy for evening
            case "night out":
                return (song.danceability or 0) > 0.75  # Stricter danceability for night out
            case "dinner date":
                return (song.valence or 0) > 0.65 and (song.energy or 0) < 0.5  # Requires higher valence and lower energy
            case "morning run":
                return (song.energy or 0) > 0.75 and (song.tempo or 0) > 120  # Stricter energy and tempo for morning run
            case "reading":
                return (song.instrumentalness or 0) > 0.7  # Higher instrumentalness for reading
            case "spa day":
                return (song.energy or 0) < 0.25 and (song.valence or 0) > 0.65  # Very low energy for spa day, high valence
            case "night in":
                return (song.energy or 0) < 0.45  # Low energy for night in
            case "dance party":
                return (song.danceability or 0) > 0.8  # Even higher danceability for dance party
            case _:
                return False



    def infer_playlist_length(self, entities: list) -> int:
        # Extract the duration, mood, and activity entities (if provided)
        duration = self._get_entity_value(entities, "duration")
        mood = self._get_entity_value(entities, "mood")
        activity = self._get_entity_value(entities, "activity")
        
        # Default playlist length if no duration or activity is provided
        playlist_length = 60  # Default length in minutes
        
        # Handle duration if specified
        if duration:
            if duration == "long":
                playlist_length = 75  # Default duration for long playlist
            elif duration == "short":
                playlist_length = 30  # Default duration for short playlist
        
        # Modify playlist length based on mood and activity if they're provided
        if mood:
            if mood in ["energetic", "upbeat", "high-energy", "pump-up"]:
                playlist_length += 15  # Energetic moods typically need longer playlists
            elif mood in ["chill", "mellow", "slow"]:
                playlist_length -= 15  # Chill/slow moods can be shorter
            elif mood in ["motivational", "uplifting"]:
                playlist_length += 10  # Motivational moods typically need mid-length playlists
            elif mood in ["romantic", "peaceful", "relaxing", "calm"]:
                playlist_length += 5  # Relaxing or romantic moods can be moderate length
            elif mood in ["fun", "lively", "bright"]:
                playlist_length += 10  # Fun or lively moods generally need a bit longer
        
        if activity:
            if activity in ["gym", "workout", "dance party"]:
                playlist_length += 10  # Ensure it's at least 50 minutes for workout-related activities
            elif activity in ["study", "study session", "reading", "mellow"]:
                playlist_length -= 10  # Shorter playlist for study or reading
            elif activity in ["party", "road trip", "night out", "dinner date", "morning run", "spa day"]:
                playlist_length += 15  # Longer playlists for road trips, parties, and active activities
            elif activity in ["sleep", "meditation", "relaxation", "evening", "night in"]:
                playlist_length += 20  # Longer playlists for sleep, meditation, and relaxation
        
        # Make sure the playlist length is within a reasonable range (e.g., 15 to 120 minutes)
        playlist_length = max(15, min(120, playlist_length))

        # Return the inferred playlist length
        return playlist_length


