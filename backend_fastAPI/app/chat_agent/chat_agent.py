from collections import deque
from typing import Deque, List, Union
import requests
from requests import Session

from .utils import *
from app.chat_agent_service import ChatAgentService

class ChatAgent:
    def __init__(self, db_session: Session):
        self.service = ChatAgentService(db_session)
        # Map intents to ChatAgentService functions
        self.intent_function_map = {
            Intents.ask_song_release_date: self.service.get_song_release_date,
            Intents.ask_songs_of_artist: self.service.get_songs_by_artist,
            Intents.ask_artist_of_song: self.service.get_artist_of_song,
            Intents.ask_album_release_date: self.service.get_album_release_date,
            Intents.ask_album_of_song: self.service.get_album_of_song,
            Intents.ask_albums_of_artist: self.service.get_albums_of_artist,
            Intents.add_song_to_playlist: self.service.rasa_add_song_to_playlist,
            Intents.remove_song_from_playlist: self.service.rasa_remove_song_from_playlist,
            # Intents.list_songs_in_playlist: self.view_playlist,
            # Intents.empty_playlist: self.clear_playlist_async
        }
        self.welcome_sent = False
        self.response_queue: Deque[str] = deque()  # Queue to store multiple responses
    
    def add_response(self, message: str, action: str = "message"):
        """Add a structured response to the response queue with a default action."""
        self.response_queue.append({"action": action, "message": message})

    def welcome(self):
        """Queue the agent's welcome message."""
        self.add_response("Hello, I'm your music bot. How can I help you?", action="welcome")

    def goodbye(self):
        """Queue the agent's goodbye message."""
        self.add_response("It was nice talking to you. Bye", action="exit")

    def parrot(self, message_split) -> str:
        """Sends a parrot message back"""
        self.add_response("Parroting: " + " ".join(message_split[1:]))

    async def seed(self) -> str:
        """Initates seeding of demo data playlist"""
        await self.service.seed_async()
        self.add_response("Demo seeding finished")

    async def process_message(self, message: str) -> Union[str, List[str]]:
        """Processes a user message and returns an appropriate response."""
        self.response_queue.clear()

        # Extracting the message from the incoming JSON data
        print("Message sent: ", message)
        message_split = message.split(" ")
        command = message_split[0] if message_split else ""

        print(f"Received command: {command}")

        # Handle hardcoded commands
        match command:
            case Commands.exit.value:
                self.goodbye()
            case Commands.hello.value:
                self.welcome()
            case Commands.parrot.value:
                self.parrot(message_split)
            case Commands.seed.value:
                await self.seed()
            case Commands.add.value:
                await self.add_song_async(message)
            case Commands.remove.value:
                await self.remove_song_async(message_split)
            case Commands.view.value:
                self.view_playlist()
            case Commands.clear.value:
                await self.clear_playlist_async()
            case _:
                # Send message to Rasa for intent handling if it's not a command
                print("Sending message over to Rasa...")
                await self.handle_rasa_response(message)


    async def handle_rasa_response(self, message: str):
        """Handles Rasa response, queues any resulting messages."""
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

        if confidence > 0.9 and entities:
            entity_type = entities[0].get("entity")
            if entity_type:
                await self.query_backend(intent, entities)
                return
        
        # Rasa intents that does not need entity: View playlist and clear playlist
        if confidence > 0.7 and not entities:
            if intent == Intents.list_songs_in_playlist:
                self.view_playlist()
                return
            if intent == Intents.empty_playlist:
                await self.clear_playlist_async()
                return

        self.add_response("I'm sorry, I didn't understand that.")


    # TODO: replace intent_function map with Intent switch case
    
    async def query_backend(self, intent: Intents, entities: list):
        """Queries backend service based on intent and entities, queues response."""
        service_function = self.intent_function_map.get(intent)
        if service_function:
            result = await service_function(entities)
            if result:
                message = result.get("message", "I found the information you requested.")
                self.add_response(message)
            else:
                self.add_response("I couldn't find the information you're looking for.")
        else:
            self.add_response("I'm not able to process your request at the moment.")


    async def add_song_async(self, message: str):
        """Handles adding a song and queues example questions."""
        artist, title = parse_add_song_input(message)
        if title:
            song_data = {"artist": artist, "title": title}
            result = await self.service.add_song_to_playlist_async(song_data)
            if result:
                self.add_response(f"Song '{result.title}' by '{result.artist}' added to playlist.")
                if (random.random() < RANDOM_QUESTION_CHANCE):
                    example_question = generate_example_questions(song_data)
                    self.add_response(f"Did you know you can ask me questions like: {example_question}")
            else:
                self.add_response("The song couldn't be added. Please try again.")
        else:
            self.add_response("Please provide the song details to add.")


    async def remove_song_async(self, message_split: List[str]):
        """Handles removing a song, queues appropriate response."""
        title = " ".join(message_split[1:])
        if title:
            song_data = {"title": title}
            result = await self.service.remove_song_from_playlist_async(song_data)
            if result:
                self.add_response(f"Song '{result.title}' by '{result.artist}' removed from playlist.")
            else:
                self.add_response("The song couldn't be removed. Please try again.")
        else:
            self.add_response("Please provide the song details to remove.")


    def view_playlist(self):
        """Queues playlist details, returning up to N songs."""
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
        """Clears the playlist and queues confirmation."""
        await self.service.clear_playlist_async()
        self.add_response("Playlist cleared.")
    