from collections import deque
from typing import Deque, List, Optional, Union
import requests
from requests import Session

from .chat_utils import *
from app.chat_agent_service import ChatAgentService

class ChatAgent:
    def __init__(self, db_session: Session):
        self.service = ChatAgentService(db_session)
        # Map intents to ChatAgentService functions
        self.welcome_sent = False
        self.response_queue: Deque[str] = deque()  # Queue to store multiple responses
        # Stores state needed to handle multi-response conversations
        self.conversation_context = ConversationContext()
    
    def add_response(self, message: str, action: str = "message"):
        self.response_queue.append({"action": action, "message": message})

    def welcome(self):
        self.add_response("Hello, I'm your music bot. How can I help you?", action="welcome")

    def goodbye(self):
        self.add_response("It was nice talking to you. Bye", action="exit")

    def parrot(self, message_split) -> str:
        self.add_response("Parroting: " + " ".join(message_split[1:]))

    async def seed(self) -> str:
        await self.service.seed_async()
        self.add_response("Demo seeding finished")

    async def process_message(self, message: str) -> Union[str, List[str]]:
        self.response_queue.clear()

        # Extracting the message from the incoming JSON data
        print("Message sent: ", message)

        if self.conversation_context.add_song.state == AddSongState.song_added:
            self.conversation_context.add_song.state = AddSongState.default

        # Check the add song conversation state
        if self.conversation_context.add_song.state != AddSongState.default:
            await self.add_song_conversation_continue(message)
            return

        message_split = message.split(" ")
        possible_command = message_split[0] if message_split else ""

        print(f"Received command: {possible_command}")

        # Handle hardcoded commands
        match possible_command:
            case Commands.exit.value:
                self.goodbye()
            case Commands.greet.value:
                self.welcome()
            case Commands.learn.value:
                self.learn_about_system()
            case Commands.parrot.value:
                self.parrot(message_split)
            case Commands.seed.value:
                await self.seed()
            case Commands.add.value:
                title, artist = parse_add_song_input(message)
                await self.add_song_conversation_start(title, artist)
            case Commands.remove.value:
                await self.remove_song_async(message_split)
            case Commands.view.value:
                self.view_playlist()
            case Commands.clear.value:
                await self.clear_playlist_async()
            case Commands.recommend.value:
                await self.recommend_songs_based_on_playlist()
            case _:
                # Send message to Rasa for intent handling if it's not a command
                print("Sending message over to Rasa...")
                await self.handle_rasa_response(message)


    async def handle_rasa_response(self, message: str):
        print("---------------------------------------------------------")
        print(message)
        rasa_resp = requests.post(RASA_URL, json={"text": message}).json()
        intent_name = rasa_resp.get("intent", {}).get("name")
        confidence = rasa_resp.get("intent", {}).get("confidence")
        entities = rasa_resp.get("entities")

        print("Intent: ", intent_name)
        print("Intent confidence: ", confidence)
        print("Entities:", entities)

        intent = Intents.__members__.get(intent_name)
        print("Intent mapped from Rasa:", intent)
            
        if self.conversation_context.recommend_playlist.state == RecommendPlaylistState.in_progress:
            match intent:
                case Intents.add_all_recommended_songs:
                    await self.add_recommended_songs(entities)
                case Intents.add_position_recommended_songs:
                    await self.add_position_recommended_songs(entities)
                case Intents.add_all_except_recommended_songs:
                    await self.add_except_recommended_songs(entities)
                case Intents.add_none_recommended_songs:
                    self.add_response("Understood. Is there something else I can help you with?")
                case _:
                    self.add_response("Did not understand. Aborting recommendations.")
            self.conversation_context.recommend_playlist.state = RecommendPlaylistState.finished
        
        # Reset recommend playlist conversation context
        if  self.conversation_context.recommend_playlist.state == RecommendPlaylistState.finished:
            self.conversation_context.recommend_playlist.state = RecommendPlaylistState.default
            self.conversation_context.recommend_playlist.pending_songs = [] # Probably not needed
            return

        if confidence > 0.7:
            match intent:
                case Intents.list_songs_in_playlist:
                    self.view_playlist()
                case Intents.empty_playlist:
                    await self.clear_playlist_async()
                case Intents.remove_from_playlist_position:
                    await self.remove_from_playlist_position(entities)
                case Intents.song_release_date_position:
                    await self.song_release_date_position(entities)
                case Intents.recommend_songs_based_on_playlist:
                    await self.recommend_songs_based_on_playlist()
                case Intents.generate_playlist_based_on_description:
                    await self.generate_playlist_based_on_description(entities)
                case _:
                    await self.handle_more_intents(intent, entities)
            return

        self.add_response("I'm sorry, I didn't understand that. (too low confidence score)")


    async def handle_more_intents(self, intent: Intents, entities: list):
        song_details: SongDetails = extract_rasa_song_details(entities)

        # Use match-case to map intents to service functions
        match intent:
            case Intents.greet:
                self.welcome()
                return
            case Intents.learn_about_system:
                self.learn_about_system()
                return
            case Intents.ask_song_release_date:
                result = self.service.get_song_release_date(entities)
            case Intents.ask_songs_of_artist:
                result = self.service.get_songs_by_artist(entities)
            case Intents.ask_artist_of_song:
                result = self.service.get_artist_of_song(entities)
            case Intents.ask_album_release_date:
                result = self.service.get_album_release_date(entities)
            case Intents.ask_album_of_song:
                result = self.service.get_albums_of_song(entities)
            case Intents.ask_albums_of_artist:
                result = self.service.get_albums_of_artist(entities)
            case Intents.add_song_to_playlist:
                await self.add_song_conversation_start(song_details.title, song_details.artist, song_details.album)
                return
            case Intents.remove_song_from_playlist:
                result = await self.service.rasa_remove_song_from_playlist(entities)
            case _:
                self.add_response("I'm not able to handle your intent at the moment.")
                return

        if result:
            message = result.get("message", "I found the information you requested.")
            self.add_response(message)
        else:
            self.add_response("I couldn't find the information you're looking for.")


    async def add_song_conversation_start(self, title: str, artist: str = None, album: str = None) -> None:
        print("Add song conversation start")
        print(f"Title: {title}, Artist: {artist}, Album: {album}")

        if title:
            # Find matching songs based on current details
            song_matches: List[SongSchema] = self.service.find_song_matches(title, artist, None, None)

            print("Num song matches: ", len(song_matches))
            print(f"Song matches: ", song_matches)

            if len(song_matches) == 1:
                # If exactly one match, add the song directly
                await self.add_song_async(song_matches[0])
                self.conversation_context.add_song.state = AddSongState.song_added

            elif len(song_matches) > 1:
                # If multiple matches, ask for clarification
                self.conversation_context.add_song.state = AddSongState.waiting_for_clarification
                self.conversation_context.add_song.pending_songs = song_matches

                self.add_response(f"I found several songs matching '{title}'{f' by {artist}' if artist else ''}. \
                                  Could you clarify which one you mean by entering the index?")
                
                for i, song in enumerate(song_matches, start=1):
                    self.add_response(f"{i}. {song.title} by {song.artist} ({song.album}) - {song.year}")

            else:
                self._handle_no_song_matches(title, artist)

        else:
            self.add_response("I'm not able to process your request at the moment.")


    async def add_song_conversation_continue(self, message: str) -> None:
        print("Entering add song continue, state: ", self.conversation_context.add_song.state)
        if message.lower() == "exit":
            self.conversation_context.add_song.state = AddSongState.default
            self.add_response("Song addition cancelled.")
            return

        try:
            # User may enter a number or song title to clarify choice
            song_index = int(message.strip()) - 1
            if 0 <= song_index < len(self.conversation_context.add_song.pending_songs):
                selected_song = self.conversation_context.add_song.pending_songs[song_index]
                await self.add_song_async(selected_song)
                self.conversation_context.add_song.state = AddSongState.song_added
            else:
                self.add_response("Please select a valid song number from the list.")

        except ValueError:
            # Fallback in case user input is not a valid number
            self.add_response("Please select a song by entering the number next to the song title.")

        finally:
            if self.conversation_context.add_song.state == AddSongState.waiting_for_clarification:
                self.conversation_context.add_song.state = AddSongState.continue_clarification
            elif self.conversation_context.add_song.state != AddSongState.song_added:
                self.add_response("You can enter 'exit' to cancel.")

            if self.conversation_context.add_song.state == AddSongState.song_added:
                self.conversation_context.add_song.state = AddSongState.default

    async def add_song_async(self, song: SongSchema):
        song_data = {"id": song.id, "title": song.title, "artist": song.artist}
        print("song data sent to add song service:", song_data)
        song: SongSchema = await self.service.add_song_to_playlist_async(song_data)
        if song:
            self.add_response(f"Song '{song.title}' by '{song.artist}' has been added to your playlist.")
            self._maybe_send_random_question(song)
  
        else:
            self.add_response("The song couldn't be added. Please try again.")
    

    async def remove_song_async(self, message_split: List[str]):
        title = " ".join(message_split[1:])
        if title:
            song_data = {"title": title}
            song: SongSchema = await self.service.remove_song_from_playlist_async(song_data)
            if song:
                self.add_response(f"Song '{song.title}' by '{song.artist}' removed from playlist.")
            else:
                self.add_response("The song couldn't be removed. Please try again.")
        else:
            self.add_response("Please provide the song details to remove.")


    def view_playlist(self):
        playlist_data = self.service.view_playlist()
        
        if playlist_data and playlist_data.songs:
            self.add_response("Your playlist includes:")
            for song in playlist_data.songs[:MAX_NUM_SONGS]:
                self.add_response(f"{song.title} by {song.artist}")
            
            if len(playlist_data.songs) > 5:
                self.add_response("... and more songs are in your playlist.")
        else:
            self.add_response("I couldn't retrieve the playlist details.")

    async def clear_playlist_async(self):
        await self.service.clear_playlist_async()
        self.add_response("Playlist cleared.")
    

    async def remove_from_playlist_position(self, entities):
        result = await self.service.remove_from_playlist_position(entities)
        if result:
            message = result.get("message", "I found the information you requested.")
            self.add_response(message)
            songs: List[SongSchema] = result.get("songs")
            self.add_response("The playlist now contains the songs:")

            self._respond_with_song_details(songs)
        else:
            self.add_response("I couldn't find the information you're looking for.")


    async def song_release_date_position(self, entities):
        result = await self.service.song_release_date_position(entities)
        if result:
            message = result.get("message", "I found the information you requested.")
            self.add_response(message)
        else:
            self.add_response("I couldn't find the information you're looking for.")

    
    async def recommend_songs_based_on_playlist(self):
        result = await self.service.recommend_songs_based_on_playlist()
        if result:
            self.add_response(result.get("message"))
            songs: List[SongSchema] = result.get("songs")
            self.conversation_context.recommend_playlist.pending_songs = songs
            self.conversation_context.recommend_playlist.state = RecommendPlaylistState.in_progress
            self._respond_with_song_details(songs, show_index=True)


    async def add_recommended_songs(self, entities):
        result = await self.service.add_from_recommendations(entities, self.conversation_context.recommend_playlist.pending_songs)
        if result:
            self.add_response(result.get("message"))
            songs: List[SongSchema] = result.get("songs")
            self._respond_with_song_details(songs, show_index=True)

    
    async def add_position_recommended_songs(self, entities):
        result = await self.service.add_from_recommendations_position(entities, self.conversation_context.recommend_playlist.pending_songs)
        if result:
            self.add_response(result.get("message"))
            songs: List[SongSchema] = result.get("songs")
            self._respond_with_song_details(songs, show_index=True)
    
    async def add_except_recommended_songs(self, entities):
        result = await self.service.add_from_recommendations_except(entities, self.conversation_context.recommend_playlist.pending_songs)
        if result:
            self.add_response(result.get("message"))
            songs = result.get("songs")
            self._respond_with_song_details(songs, show_index=True)


    async def generate_playlist_based_on_description(self, entities) -> None:
        # Filter songs based on entities and inferred playlist length
        result = await self.service.create_playlist_from_description(entities)
        if result:
            self.add_response(result.get("message"))
            songs: List[SongSchema] = result.get("songs")
            self.add_response("The playlist now contains the songs:")

            self._respond_with_song_details(songs)


    def learn_about_system(self) -> None:
        self.add_response("You can try commands such as these")
        commands_list = "\n".join(cmd.value for cmd in Commands)
        self.add_response(commands_list)

        self.add_response("Or you can try to initiate one of these intents using natural language:")
        # Join intents with proper formatting
        intents_list = "\n".join(" ".join(intent.split("_")) for intent in Intents._member_names_)
        self.add_response(intents_list)
        
        self.add_response("For example: Add the song Thriller by Michael Jackson to my playlist")
    

    def _maybe_send_random_question(self, song_data: SongSchema) -> None:
        if (random.random() < RANDOM_QUESTION_CHANCE):
            example_question = generate_example_questions(song_data)
            self.add_response(f"Did you know you can ask me questions like: {example_question}")

    def _handle_no_song_matches(self, title: str, artist: Optional[str]) -> None:
        if not artist:
            self.add_response(f"I couldn't find a song matching '{title}'. Please double-check the details.")
        else:
            self.add_response(f"Sorry, I couldn't find any matches for '{title}' by {artist}. Please double-check the details.")

    def _respond_with_song_details(self, songs: List[SongSchema], show_index: bool = False):
        if songs:
            for i, song in enumerate(songs, start=1):
                # Construct the response text with or without the index
                song_text = (f"{i}: " if show_index else "") + f"{song.title} by {song.artist} ({song.album}) - {song.year}"
                self.add_response(song_text)
        else:
            self.add_response("No songs found.")

