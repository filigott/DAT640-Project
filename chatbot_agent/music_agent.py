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

    def add(self, song) -> None:
        resp = requests.post(fast_api_endpoint + "/add", json={"data": song}).json()
        answer = resp.get("message")
        utterance = AnnotatedUtterance(
            answer,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance)

    def remove(self, song) -> None:
        resp = requests.post(fast_api_endpoint + "/remove", json={"data": song}).json()
        answer = resp.get("message")
        utterance = AnnotatedUtterance(
            answer,
            participant=DialogueParticipant.AGENT,
        )

        self._dialogue_connector.register_agent_utterance(utterance)
    
    def clear(self) -> None:
        resp = requests.get(fast_api_endpoint + "/clear").json()
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
        
        if utternace_text_split[0] == "/add":
            song = utternace_text_split[1]
            self.add(song)

        if utternace_text_split[0] == "/remove":
            song = utternace_text_split[1]
            self.remove(song)
        
        if utterance.text == "/clear":
            self.clear()

        # response = AnnotatedUtterance(
        #     "(Parroting) " + utterance.text,
        #     participant=DialogueParticipant.AGENT,
        # )
        # self._dialogue_connector.register_agent_utterance(response)
