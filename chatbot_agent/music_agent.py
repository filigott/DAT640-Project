"""Simplest possible agent that parrots back everything the user says."""

from dialoguekit.core.annotated_utterance import AnnotatedUtterance
from dialoguekit.core.utterance import Utterance
from dialoguekit.participant.agent import Agent
from dialoguekit.participant.participant import DialogueParticipant
import requests

fast_api_endpoint = "http://localhost:8000"

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
            "Hello, I'm Parrot. What can I help u with?",
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
        resp = requests.post(fast_api_endpoint + "/bot/get_song_id", json={"data": song_description}).json()
        
        song_id = resp.get("song_id")
        print("song_id: ", song_id)

        resp = requests.post(fast_api_endpoint + f"/playlist/{playlist_id}/add_song/{song_id}").json()
        answer = resp.get("message")
        utterance = AnnotatedUtterance(
            answer,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance)

    def remove(self, title="", artist="", album="", playlist_id = 1) -> None:
        song_description = {
            "artist": artist,
            "title": title,
            "album": album
        }
        resp = requests.post(fast_api_endpoint + "/bot/get_song_id", json={"data": song_description}).json()

        song_id = resp.get("song_id")
        print("song_id: ", song_id)

        resp = requests.post(fast_api_endpoint + f"/playlist/{playlist_id}/remove_song/{song_id}").json()
        answer = resp.get("message")
        utterance = AnnotatedUtterance(
            answer,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance)
    
    def clear(self, playlist_id = 1) -> None:
        resp = requests.post(fast_api_endpoint + f"/playlist/{playlist_id}/clear").json()
        answer = resp.get("message")
        utterance = AnnotatedUtterance(
            answer,
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
        
        # Currently only by title of song
        if utternace_text_split[0] == "/add":
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

        # response = AnnotatedUtterance(
        #     "(Parroting) " + utterance.text,
        #     participant=DialogueParticipant.AGENT,
        # )
        # self._dialogue_connector.register_agent_utterance(response)
