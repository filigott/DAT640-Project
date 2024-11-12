from enum import Enum, auto
from typing import Dict, Optional, List

# Enum for different user goals
class UserGoalType(Enum):
    create_playlist = 0
    ask_album_details = auto()
    receive_recommendations = auto()

# Enum for possible actions that a user can take
class UserAction(Enum):
    add_song_to_playlist = 0
    get_list_of_songs_in_playlist = auto()

    add_song_to_playlist_by_artist = auto()
    ask_about_song = auto()
    ask_about_album = auto()
    ask_about_artist = auto()

    request_song_recommendations = auto()
    accept_recommendations = auto()
    reject_recommendations = auto()
    exit_conversation = auto()

# Goal class for storing the user's goal information
class UserGoal:
    def __init__(self, goal_type: UserGoalType, goal_text: str, max_turns: Optional[int] = None, max_songs: Optional[int] = None):
        """
        Initializes the goal object with a description.
        
        :param goal_type: The type of goal (e.g., "create_playlist", "ask_album_details").
        :param goal_text: A textual description of the goal (e.g., "Create a playlist of liked songs").
        :param max_turns: Optional maximum number of conversation turns.
        :param max_songs: Optional maximum number of songs for the playlist.
        """
        self.goal_type = goal_type
        self.goal_text = goal_text
        self.max_turns = max_turns
        self.max_songs = max_songs


# Default actions for each goal type
def default_actions_for_goal(goal_type: UserGoalType) -> List[UserAction]:
    if goal_type == UserGoalType.create_playlist:
        return [
            UserAction.add_song_to_playlist,
            UserAction.get_list_of_songs_in_playlist,
            UserAction.add_song_to_playlist_by_artist,
            ]
    elif goal_type == UserGoalType.receive_recommendations:
        return [
            UserAction.request_song_recommendations, 
            UserAction.accept_recommendations, 
            UserAction.reject_recommendations
            ]
    elif goal_type == UserGoalType.ask_album_details:
        return [UserAction.ask_about_album]
    else:
        return [UserAction.exit_conversation]
    

def default_action_weights(goal_type: UserGoalType) -> Dict[UserAction, int]:
    """
    Returns a dictionary of action weights based on the goal type.
    These weights represent the likelihood of each action being selected.
    """
    if goal_type == UserGoalType.create_playlist:
        return {
            UserAction.add_song_to_playlist: 50,  # 50% chance to add song to playlist
            UserAction.get_list_of_songs_in_playlist: 20,  # 20% chance to get the song list
            UserAction.add_song_to_playlist_by_artist: 20,  # 20% chance to add song by artist
            UserAction.exit_conversation: 10,  # 10% chance to exit the conversation
        }
    elif goal_type == UserGoalType.receive_recommendations:
        return {
            UserAction.request_song_recommendations: 40,  # 40% chance to request song recommendations
            UserAction.accept_recommendations: 30,  # 30% chance to accept recommendations
            UserAction.reject_recommendations: 30,  # 30% chance to reject recommendations
            UserAction.exit_conversation: 10,  # 10% chance to exit the conversation
        }
    elif goal_type == UserGoalType.ask_album_details:
        return {
            UserAction.ask_about_album: 80,  # 80% chance to ask about an album
            UserAction.exit_conversation: 20,  # 20% chance to exit the conversation
        }
    else:
        return {
            UserAction.exit_conversation: 100,  # 100% chance to exit if no valid goal
        }