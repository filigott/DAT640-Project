"""Simplest possible agent that parrots back everything the user says."""

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.agent import Agent
from dialoguekit.participant.participant import DialogueParticipant
from dialoguekit.nlu.models.diet_classifier_rasa import IntentClassifierRasa
import requests
import time
import random
import re

fast_api_endpoint = "http://localhost:8000"
hardcoded_commands = ["/add", "/remove", "/view", "/clear"]
rasa_url = "http://localhost:5005/model/parse"


intents = {
    "ask_song_release_date": f"{fast_api_endpoint}/bot/song_release_date",
    "ask_songs_of_artist": f"{fast_api_endpoint}/bot/songs_of_artist",
    "ask_artist_of_song": f"{fast_api_endpoint}/bot/artist_of_song",
    "ask_album_release_date": f"{fast_api_endpoint}/bot/album_release_date",
    "ask_album_of_song": f"{fast_api_endpoint}/bot/album_of_song",
    "ask_albums_of_artist": f"{fast_api_endpoint}/bot/albums_of_artist"
}



entities = {
    "ask_song_release_date": "song",
    "ask_songs_of_artist": "artist",
    "ask_artist_of_song": "song",
    "ask_album_release_date": "album",
    "ask_album_of_song": "song",
    "ask_albums_of_artist": "artist"
}

def test(song_description):
    return {
        "ask_song_release_date": f"When was the song {song_description.get('title')} released?",
        "ask_songs_of_artist": f"What songs does {song_description.get('artist')} have?",
        "ask_album_of_song": f"Which album is the song {song_description.get('title')} from?",
    }

def get_random_question(song_description):
    questions = test(song_description)
    print(list(questions.values()))
    random_question = random.choice(list(questions.values()))
    return random_question


class MusicAgent(Agent):
    def __init__(self, agent_id: str):
        """Parrot agent.

        This agent parrots back what the user utters.
        To end the conversation the user has to say `EXIT`.

        Args:
            agent_id: Agent id.
        """
        super().__init__(agent_id)

    def welcome(self) -> None:
        """Sends the agent's welcome message."""
        utterance = AnnotatedUtterance(
            "Hello, im your music bot. How can I help you?",
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def goodbye(self) -> None:
        """Sends the agent's goodbye message."""
        utterance = AnnotatedUtterance(
            "It was nice talking to you. Bye",
            intent=self.stop_intent,
            participant=DialogueParticipant.AGENT,
        )
        self._dialogue_connector.register_agent_utterance(utterance)

    def view(self, playlist_id: int) -> None:
        resp = requests.get(fast_api_endpoint + f"/playlist/{playlist_id}")

        playlist_json = resp.json()

        playlist_name = playlist_json.get("name", "Unnamed Playlist")
        songs = playlist_json.get("songs", [])


        # song_titles = ", ".join(song.get("title", "Unnamed Song") for song in songs)
        song_titles = ", ".join(f"{song.get('title', 'Unnamed Song')} ({song.get('artist', 'Unknown Artist')}, {song.get('year', 'Unknown Year')})" for song in songs)

        answer = f"Your playlist '{playlist_name}' includes the following songs: {song_titles}"
        utterance1 = AnnotatedUtterance(
            answer,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance1)
        # self._dialogue_connector.register_agent_utterance(utterance)

    def add(self, title="", artist="", album="", playlist_id = 1) -> None:
        song_description = {
            "artist": artist,
            "title": title,
            "album": album
        }
        resp = requests.post(fast_api_endpoint + "/bot/add_song", json={"data": song_description})
        print("resp: ", resp) 
        print("resp.json: ", resp.json())  
        if resp.status_code != 200:
            answer = "Song not found"
            utterance = AnnotatedUtterance(
                answer,
                participant=DialogueParticipant.AGENT,
            )
            self._dialogue_connector.register_agent_utterance(utterance)
            return

        song = resp.json()
        random_question = get_random_question(song_description={"title": song.get("title"), "artist": song.get("artist"), "album": song.get("album")})
        print(random_question)
        answer = f"Song added to playlist. Did you know you can ask me questions like this: '{random_question}'"       
        utterance = AnnotatedUtterance(
            answer,
            participant=DialogueParticipant.AGENT,
        )
    
        # question_utterance = AnnotatedUtterance(
        #     random_question,
        #     participant=DialogueParticipant.AGENT,
        # )
        self._dialogue_connector.register_agent_utterance(utterance)
        

    def remove(self, title="", artist="", album="", playlist_id = 1) -> None:
        song_description = {
            "artist": artist,
            "title": title,
            "album": album
        }
        resp = requests.post(fast_api_endpoint + "/bot/remove_song", json={"data": song_description})

        if resp.status_code != 200:
            answer = "Song not found"
            utterance = AnnotatedUtterance(
                answer,
                participant=DialogueParticipant.AGENT,
            )
            self._dialogue_connector.register_agent_utterance(utterance)
            return
       
        utterance = AnnotatedUtterance(
            "Song removed from playlist.",
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance)
    
    def clear(self, playlist_id = 1) -> None:
        resp = requests.post(fast_api_endpoint + f"/playlist/{playlist_id}/clear")
        
        if resp.status_code != 200:
            answer = "Could not clear playlist"
            utterance = AnnotatedUtterance(
                answer,
                participant=DialogueParticipant.AGENT,
            )
            self._dialogue_connector.register_agent_utterance(utterance)
            return
        utterance = AnnotatedUtterance(
            "Playlist cleared",
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance)

    def rasa(self, input) -> None:
        rasa_resp = requests.post(rasa_url, json={"text": input}).json()
        print(rasa_resp)
        intent = rasa_resp.get("intent").get("name")
        intent_confidence = rasa_resp.get("intent").get("confidence")
        entity = rasa_resp.get("entities")[0].get("entity")
        entity_confidence = rasa_resp.get("entities")[0].get("confidence_entity")
        entity_value = rasa_resp.get("entities")[0].get("value")
        entity_values = rasa_resp.get("entities")
        print("intent: ", intent)
        print("confidence: ", intent_confidence)
        print("entity: ", entity)
        print("entity confidence: ", entity_confidence)

        
        ## Ensure high confidence and right entity for the intent
        if intent_confidence > 0.9 and entity == entities.get(intent):
            endpoint = intents.get(intent)
            resp = requests.post(endpoint, json={"data": entity_values})

            if resp.status_code == 400:
                utterance = AnnotatedUtterance(
                    "Need more information",
                    participant=DialogueParticipant.AGENT,
                )
                self._dialogue_connector.register_agent_utterance(utterance)

                ## Handle more information here (?)
                return
            
            if resp.status_code == 404:
                utterance = AnnotatedUtterance(
                    "Could not find what you were looking for",
                    participant=DialogueParticipant.AGENT,
                )
                self._dialogue_connector.register_agent_utterance(utterance)
                return
            
            if resp.status_code == 200:
                answer = resp.json().get("message")
                utterance = AnnotatedUtterance(
                    answer,
                    participant=DialogueParticipant.AGENT,
                )
                self._dialogue_connector.register_agent_utterance(utterance)
        else:
            utterance = AnnotatedUtterance(
                "I'm sorry, I didn't understand that",
                participant=DialogueParticipant.AGENT,
            )
            self._dialogue_connector.register_agent_utterance(utterance)
            


    def receive_utterance(self, utterance: Utterance) -> None:
        """Gets called each time there is a new user utterance.

        If the received message is "EXIT" it will close the conversation.

        Args:
            utterance: User utterance.
        """
        utternace_text_split = utterance.text.split(" ")
        print(utternace_text_split)

        if utterance.text == "EXIT":
            self.goodbye()
            return
        
        # Hardcoded commands
        if utternace_text_split[0] == "/add":
            artist, song_title = parse_add_song_input(utterance.text)
            # Either [artist]: [title]" or "[title] by [artist]", else just "[title]"
            if artist and song_title:
                self.add(title = song_title, artist = artist)
            else:
                song_title = " ".join(utternace_text_split[1:])
                self.add(title = song_title)


        if utternace_text_split[0] == "/remove":
            song_title = " ".join(utternace_text_split[1:])
            self.remove(title = song_title)

        if utternace_text_split[0] == "/view":
            # playlist_id = utternace_text_split[1]
            playlist_id = 1
            self.view(playlist_id)
        
        if utternace_text_split[0] == "/clear":
            self.clear()


        # RASA for general questions
        if utternace_text_split[0] not in hardcoded_commands :
            self.rasa(utterance.text)
        


        # response = AnnotatedUtterance(
        #     "(Parroting) " + utterance.text,
        #     participant=DialogueParticipant.AGENT,
        # )
        # self._dialogue_connector.register_agent_utterance(response)

def parse_add_song_input(input_text):
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

    # Return the extracted artist and title
    return artist.strip(), title.strip()