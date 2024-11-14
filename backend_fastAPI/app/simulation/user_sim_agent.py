import asyncio
import random
import time
from app.simulation.ws_sim_client import WebSocketClient
from app.chat_agent.chat_utils import Commands, Intents
from app.simulation.user_sim_utils import UserAction, UserGoalType
from app.simulation.user_sim_profiles import UserProfile

DEFAULT_MAX_TURNS = 20

class UserSimAgent:
    def __init__(self, profile: UserProfile, user_id: int, ws_url: str):
        self.profile = profile
        self.goal = profile.goal
        self.user_id = user_id
        self.ws_url = ws_url
        self.ws_client = WebSocketClient(user_id, ws_url)
        self.all_user_messages = []
        self.all_responses = []
        self.completed = False
        self.turn_count = 1
        self.num_songs_playlist = 0
        self.num_questions_asked = 0
        self.max_turns = profile.goal.max_turns or DEFAULT_MAX_TURNS
        self.valid_commands = Commands
        self.valid_intents = Intents
        # Define keywords and associated actions
        self.keywords_to_actions = {
            "has been added to your playlist": self._handle_song_added,
            # Add more keywords and handlers as needed
            "The songs by": self._handle_ask_songs_of_artist,
            "was released in": self._handle_ask_song_release_date
        }
        self.last_referenced_song = None
        self.last_references_artist = None


    async def simulate_conversation(self, sequantial: bool):
        """Simulate the user's conversation with the music recommender system."""
        await self.ws_client.connect()

        try:
        # Try to receive the hello message with a timeout
            await asyncio.wait_for(self.ws_client.receive_response(), timeout=3.0)  # Timeout for hello message
        except asyncio.TimeoutError:
            pass

        await self.ws_client.send_message(Commands.clear.value)
        await self.ws_client.receive_response()

        while not self.completed and self.turn_count < self.max_turns:

            if sequantial:
                await asyncio.sleep(2)
            else:
                await asyncio.sleep(random.uniform(3, 5))

            print(f"[Client {self.profile.id}] Current turn: {self.turn_count}")

            user_message = self.get_user_message()
            self.all_user_messages.append(user_message)
            await self.ws_client.send_message(user_message)

            if user_message == Commands.exit.value:
                await self.ws_client.disconnect()
                return

            responses = []  # To store all responses for the current message
            timeout_duration = 5  # Timeout duration in seconds

            try:
                # We will repeatedly attempt to receive responses until timeout or a break condition
                while True:
                    try:
                        # Use asyncio.wait_for to impose a timeout on the receive operation
                        response = await asyncio.wait_for(self.ws_client.receive_response(), timeout=timeout_duration)
                        responses.append(response)  # Add the response to our list
                    except asyncio.TimeoutError:
                        # Timeout occurred, break the loop
                        print(f"[Client {self.profile.id}] have received all responses.")
                        break

            except Exception as e:
                print(f"[Client {self.profile.id}] Error while waiting for responses: {e}")

            # Process all received responses
            for response in responses:
                self.process_response(response)

            self.turn_count += 1

        await self.ws_client.disconnect()


    def get_user_message(self) -> str:      
        action: UserAction = self.select_action()
        num_tries = 0
        max_tries = 10

        # Retry until we get a valid action or hit the maximum number of tries
        while action is None and num_tries < max_tries:
            num_tries += 1
            action = self.select_action()

        # If still no action, exit as a fallback
        if action is None:
            return Commands.exit.value

        # Reset retries for getting a non-null message
        num_tries = 0
        message = None
        
        # Try to get a non-null message based on the action
        while message is None and num_tries < max_tries:
            num_tries += 1
            
            match action:
                case UserAction.add_song_to_playlist:
                    message = self.add_liked_song_to_playlist()
                
                case UserAction.get_list_of_songs_in_playlist:
                    message = Commands.view.value
                
                case UserAction.ask_about_songs_of_artist:
                    message = self.ask_about_songs_of_artist()
                
                case UserAction.ask_about_song_release_date:
                    message = self.ask_about_song_release_date()
                
                case UserAction.exit_conversation:
                    message = Commands.exit.value
                
                case _:
                    message = Commands.exit.value

        # If still no valid message, return exit command as a fallback
        if message is None:
            return Commands.exit.value

        return message


    def select_action(self) -> UserAction:
        """Select the next action based on the user's profile and goal."""
        possible_actions = self.profile.allowed_actions

        if not possible_actions:
            return UserAction.exit_conversation  # Exit if no valid actions are left

        # Enforce conditions for playlist creation goal

        match self.goal.goal_type:
            case UserGoalType.create_playlist:
                if self.goal.max_songs and self.num_songs_playlist >= self.goal.max_songs:
                    if not self.completed:
                        self.completed = True
                        possible_actions = [UserAction.get_list_of_songs_in_playlist]
                    else:
                        possible_actions = [UserAction.exit_conversation]

            case UserGoalType.ask_questions:
                if self.goal.max_questions and self.num_questions_asked >= self.goal.max_questions:
                    if not self.completed:
                        self.completed = True
                        possible_actions = [UserAction.exit_conversation]
            case _:
                possible_actions = [UserAction.exit_conversation]

        print(f"[Client {self.profile.id}] Possible actions: ", [action.name for action in possible_actions])

        # Use the action weights from the profile
        action_weights = self.profile.get_action_weights()

        # Filter weights based on the available actions
        action_weights_for_selected_actions = [
            action_weights.get(action, 1) for action in possible_actions
        ]

        # Select an action based on weighted probabilities
        selected_action = random.choices(possible_actions, weights=action_weights_for_selected_actions, k=1)[0]
        print(f"[Client {self.profile.id}] Selected action: {selected_action}")

        return selected_action


    def process_response(self, response: str):
        """Process the response to determine if the goal has been met or the conversation should stop."""
        # Check response for each keyword and call the associated handler if found
        for keyword, action in self.keywords_to_actions.items():
            if keyword in response:
                print(f"[Client {self.profile.id}] Found keyword: {keyword} in response")
                action()  # Call the corresponding handler
                return  # Exit after the first matched action to avoid multiple triggers
            

    def add_liked_song_to_playlist(self):
        """Simulates adding a specific song to the playlist."""
        if self.profile.liked_songs:
            print(f"[Client {self.profile.id}] Has remaining {len(self.profile.liked_songs)} liked songs: ")
            song = random.choice(self.profile.liked_songs)
            title = song["title"]
            artist = song["artist"]
            self.last_referenced_song = song
            return f"{Commands.add.value} {title} by {artist}"
        return f"{Commands.exit.value}"
    

    def ask_about_song_release_date(self):
        if self.profile.liked_songs:
            print(f"[Client {self.profile.id}] Has remaining {len(self.profile.liked_songs)} liked songs: ")
            song = random.choice(self.profile.liked_songs)
            title = song["title"]
            self.last_referenced_song = song
            return f"What's the release date for {title}?"
        return None


    def ask_about_songs_of_artist(self):
        if self.profile.liked_artists:
            print(f"[Client {self.profile.id}] Has remaining {len(self.profile.liked_artists)} liked artists: ")
            artist = random.choice(self.profile.liked_artists)
            self.last_references_artist = artist
            return f"What has {artist} released?"
        return None
    

    # async def request_recommendations(self):
    #     """Simulates requesting recommendations."""
    #     return Commands.REQUEST_RECOMMENDATIONS

    # Define each handler function with the desired action
    def _handle_song_added(self):
        """Handles the song being added to the playlist and removes it from liked_songs."""
        if self.last_referenced_song:
            print(f"[Client {self.profile.id}] Song added to playlist: {self.last_referenced_song['title']} by {self.last_referenced_song['artist']}")
            # Remove the last added song from the liked_songs list
            self.profile.liked_songs = [song for song in self.profile.liked_songs if song["title"] != self.last_referenced_song["title"]]
            self.num_songs_playlist += 1
            self.last_referenced_song = None

    def _handle_ask_song_release_date(self):
        if self.last_referenced_song:
            self.profile.liked_songs = [song for song in self.profile.liked_songs if song["title"] != self.last_referenced_song["title"]]
            self.num_questions_asked += 1
            print(f"[Client {self.profile.id}] Number of questions asked: {self.num_questions_asked}")
            self.last_referenced_song = None

    def _handle_ask_songs_of_artist(self):
        if self.last_references_artist:
            self.profile.liked_artists = [artist for artist in self.profile.liked_artists if artist != self.last_references_artist]
            self.num_questions_asked += 1
            print(f"[Client {self.profile.id}] Number of questions asked: {self.num_questions_asked}")
            self.last_references_artist = None

    def get_summary(self):
            """Generate a summary of the simulation results."""
            return {
                "user_id": self.user_id,
                "goal": self.goal.goal_text,
                "actions_taken": self.turn_count,
                "songs_added_to_playlist": self.num_songs_playlist,
                "num_questions_asked": self.num_questions_asked,
                "completed": self.completed,
            }