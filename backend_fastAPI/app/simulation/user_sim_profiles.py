from typing import Dict, List, Optional

from app.simulation.user_sim_utils import UserAction, UserGoal, UserGoalType, default_action_weights, default_actions_for_goal

# Defining different user profiles with varied preferences and goals
class UserProfile:
    def __init__(
        self,
        id: int,
        liked_artists: List[str],
        disliked_artists: List[str],
        liked_songs: Dict[str, str],
        disliked_songs: List[str],
        goal: UserGoal,
        allowed_actions: Optional[List[UserAction]] = None,
           action_weights: Optional[Dict[UserAction, int]] = None,
    ):
        self.id = id
        self.liked_artists = liked_artists
        self.disliked_artists = disliked_artists
        self.liked_songs = liked_songs
        self.disliked_songs = disliked_songs
        self.goal = goal
        self.allowed_actions = allowed_actions or default_actions_for_goal(goal.goal_type)
        self.action_weights = action_weights or default_action_weights()

    def __repr__(self):
        return (f"UserProfile(id={self.id}, "
                f"Goal: {self.goal.goal_text}, "
                f"Allowed Actions: {', '.join(action.name for action in self.allowed_actions)}")

    def available_actions(self) -> List[UserAction]:
        return self.allowed_actions
    
    def get_action_weights(self) -> Dict[UserAction, int]:
        """Get the action weights for this profile."""
        return self.action_weights


# Predefined user profiles
user_profiles = [
    UserProfile(
        id=2,
        liked_artists=["The Beatles", "Queen", "Micheal Jackson"],
        disliked_artists=["Justin Bieber"],
        liked_songs=[
        {"title": "Hey Jude", "artist": "The Beatles"},
        {"title": "Bohemian Rhapsody", "artist": "Queen"},
        {"title": "Thriller", "artist": "Michael Jackson"}
    ],
        disliked_songs=["Baby"],
        goal=UserGoal(
            goal_type=UserGoalType.create_playlist,
            goal_text="Create a playlist with liked songs",
            max_songs=3
        ),
        allowed_actions=[
            UserAction.add_song_to_playlist,
            UserAction.get_list_of_songs_in_playlist,
            UserAction.exit_conversation
        ],
        action_weights={
            UserAction.add_song_to_playlist: 75,
            UserAction.get_list_of_songs_in_playlist: 20,
            UserAction.exit_conversation: 5,
        }
        
    ),
    UserProfile(
        id=3,
        liked_artists=["The Beatles", "Queen", "Micheal Jackson"],
        disliked_artists=["Justin Bieber"],
        liked_songs=[
        {"title": "Come Together", "artist": "The Beatles"},
        {"title": "We Will Rock You", "artist": "Queen"},
        {"title": "Billie Jean", "artist": "Michael Jackson"},
        {"title": "Shape Of You", "artist": "Ed Sheeran"}
    ],
        disliked_songs=["Baby"],
        goal=UserGoal(
            goal_type=UserGoalType.create_playlist,
            goal_text="Create a playlist with liked songs",
            max_songs=4
        ),
        allowed_actions=[
            UserAction.add_song_to_playlist,
            UserAction.get_list_of_songs_in_playlist,
            UserAction.exit_conversation
        ],
          action_weights={
            UserAction.add_song_to_playlist: 85,
            UserAction.get_list_of_songs_in_playlist: 10,
            UserAction.exit_conversation: 5,
        }
    ),
    UserProfile(
        id=4,
        liked_artists=["Adele", "Ed Sheeran", "John Legend"],
        disliked_artists=["Kanye West", "Justin Bieber"],
        liked_songs=[
            {"title": "Someone Like You", "artist": "Adele"},
            {"title": "Shape of You", "artist": "Ed Sheeran"},
            {"title": "All of Me", "artist": "John Legend"}
        ],
        disliked_songs=["Baby"],
        goal=UserGoal(
            goal_type=UserGoalType.ask_questions,
            goal_text="Get to know about liked songs and songs of liked artists",
            max_questions=5
        ),
        allowed_actions=[
            # UserAction.add_song_to_playlist,
            # UserAction.get_list_of_songs_in_playlist,
            UserAction.ask_about_song_release_date,
            UserAction.ask_about_songs_of_artist,
            UserAction.exit_conversation
        ],
        action_weights={
            # UserAction.add_song_to_playlist: 20,
            # UserAction.get_list_of_songs_in_playlist: 10,
            UserAction.ask_about_song_release_date: 45,
            UserAction.ask_about_songs_of_artist: 45,
            UserAction.exit_conversation: 10
        }
    ),
    UserProfile(
        id=5,
        liked_artists=["Taylor Swift", "Ed Sheeran", "Ariana Grande"],
        disliked_artists=["Kanye West"],
        liked_songs=[
            {"title": "Love Story", "artist": "Taylor Swift"},
            {"title": "Perfect", "artist": "Ed Sheeran"},
            {"title": "No Tears Left to Cry", "artist": "Ariana Grande"}
        ],
        disliked_songs=["Baby"],
        goal=UserGoal(
            goal_type=UserGoalType.create_playlist,
            goal_text="Create a playlist. But also not.",
            max_songs=3
        ),
        allowed_actions=[
            UserAction.add_song_to_playlist,
            UserAction.get_list_of_songs_in_playlist,
            UserAction.exit_conversation
        ],
        action_weights={
            UserAction.add_song_to_playlist: 30,
            UserAction.get_list_of_songs_in_playlist: 20,
            UserAction.exit_conversation: 50,
        }
    )
]
