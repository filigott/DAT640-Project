from typing import List
import requests
import re

from requests import Session
from .defs import *
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
        }
        self.welcome_sent = False

    def welcome(self) -> str:
        """Sends the agent's welcome message."""
        return "Hello, im your music bot. How can I help you?"
           

    def goodbye(self) -> str:
        """Sends the agent's goodbye message."""
        return "It was nice talking to you. Bye"

    def parrot(self, message_split) -> str:
        """Sends a parrot message back"""
        return "Parroting: " + " ".join(message_split[1:])

    async def seed(self) -> str:
        """Initates seeding of demo data playlist"""
        await self.service.seed_async()
        return "Demo seeding finished"

    # TODO: Could be made to return an object/dict for making frontend create multiple text boxes
    async def process_message(self, message: str) -> str:
        """Processes a user message and returns an appropriate response."""
        # Extracting the message from the incoming JSON data
        print("Message sent: ", message)
        message_split = message.split(" ")
        command = message_split[0] if message_split else ""

        print(f"Received command: {command}")

        # Handle hardcoded commands
        match command:
            case Commands.exit.value:
                return "exit"
            case Commands.hello.value:
                return self.welcome()
            case Commands.parrot.value:
                return self.parrot(message_split)
            case Commands.seed.value:
                return await self.seed()
            case Commands.add.value:
                return await self.add_song_async(message)
            case Commands.remove.value:
                return await self.remove_song_async(message_split)
            case Commands.view.value:
                return self.view_playlist()
            case Commands.clear.value:
                return await self.clear_playlist_async()
            case _:
                print("Sending message over to rasa...")
                # Pass message to Rasa if it isn't a hardcoded command
                return self.handle_rasa_response(message)


    def handle_rasa_response(self, message: str) -> str:
        """Sends the message to Rasa for intent and entity extraction."""
        print(message)
        rasa_resp = requests.post(RASA_URL, json={"text": message}).json()
        print(rasa_resp)
        intent_name = rasa_resp.get("intent", {}).get("name")
        confidence = rasa_resp.get("intent", {}).get("confidence")
        entities = rasa_resp.get("entities")

        # Convert the intent name to the Intent Enum if it exists
        intent = Intents.__members__.get(intent_name)
        print("intent: ", intent)
        test =  Intents.ask_song_release_date
        print("TETETSTSTWTW")
        print(test)

        print(self.intent_function_map)

        # Ensure high confidence and valid entity
        if confidence > 0.9 and entities:
            # # expected_entity_type = self.intent_function_map.get(intent)
            # if expected_entity_type and expected_entity_type.value in [entity.get("entity") for entity in entities]:
            return self.query_backend(intent, entities)
            # else:
                # return "I couldn't understand your question. Could you provide more details?"
        else:
            return "I'm sorry, I didn't understand that."


    def query_backend(self, intent: Intents, entities: list) -> str:
        """Maps intent to the respective bot service function and calls it."""
        service_function = self.intent_function_map.get(intent)
        print(service_function)
        # service_function = self.service.get_song_release_date
        if service_function:
            result = service_function(entities)
            if result:
                if "message" in result:
                    return result["message"]
                return "I found the information you requested."
            return "I couldn't find the information you're looking for."
        return "I'm not able to process your request at the moment."


    async def add_song_async(self, message: str) -> str:
        """Handles adding a song to the playlist based on user input."""
        artist, title = self.parse_add_song_input(message)
        print(title)
        if title:
            song_data = {"artist": artist, "title": title}
            result = await self.service.add_song_to_playlist_async(song_data)
            if result:
                return f"Song '{result.title}' by '{result.artist}' added to playlist."
            return "The song couldn't be added. Please try again."
        return "Please provide the song details to add."


    async def remove_song_async(self, message_split: List[str]) -> str:
        """Handles removing a song from the playlist."""
        title = " ".join(message_split[1:])
        if title:
            song_data = {"title": title}
            result = await self.service.remove_song_from_playlist_async(song_data)
            if result:
                return f"Song '{result.title}' by '{result.artist}' removed from playlist."
            return "The song couldn't be removed. Please try again."
        return "Please provide the song details to remove."


    def view_playlist(self) -> str:
        """Retrieves and formats the current playlist details."""
        # Direct function call to fetch playlist data
        playlist_data = self.service.view_playlist()
        print(playlist_data)
        if playlist_data:
            song_titles = ", ".join(f"{song.title} by {song.artist}" for song in playlist_data.songs)
            return f"Your playlist includes: {song_titles}"
        return "I couldn't retrieve the playlist details."


    async def clear_playlist_async(self) -> str:
        """Clears the playlist of all songs."""
        await self.service.clear_playlist_async()
        return "Playlist cleared."


    def parse_add_song_input(self, input_text):
        # First, ensure the command starts with "/add"
        if not input_text.startswith("/add "):
            return None, None

        # Remove the "/add " prefix
        command_text = input_text[5:].strip()

        # Try to match both patterns
        # Pattern 1: "[artist]: [title]"
        match1 = re.match(r'^(.*):\s*(.*)$', command_text)
        # Pattern 2: "[title] by [artist]"
        match2 = re.match(r'^(.*)\s+by\s+(.*)$', command_text, re.IGNORECASE)

        if match1:
            artist, title = match1.groups()
        elif match2:
            title, artist = match2.groups()
        else:
            return None, None  # If no patterns matched

        # Return the extracted artist and title without any additional formatting
        return artist.strip(), title.strip()
