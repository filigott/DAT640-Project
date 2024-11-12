from typing import Dict, List, Optional

from app.simulation.user_sim_utils import UserAction, UserGoal, UserGoalType, default_action_weights, default_actions_for_goal

# Defining different user profiles with varied preferences and goals
class UserProfile:
    def __init__(
        self,
        id: int,
        liked_artists: List[str],
        disliked_artists: List[str],
        liked_songs: List[str],
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
        return f"UserProfile(id={self.id}, goal={self.goal}, allowed_actions={self.allowed_actions})"

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
            UserAction.get_list_of_songs_in_playlist
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
            UserAction.get_list_of_songs_in_playlist
        ],
          action_weights={
            UserAction.add_song_to_playlist: 85,
            UserAction.get_list_of_songs_in_playlist: 10,
            UserAction.exit_conversation: 5,
        }
    ),
    # UserProfile(
    #     id=4,
    #     liked_artists=["The Beatles", "Queen", "Micheal Jackson"],
    #     disliked_artists=["Justin Bieber"],
    #     liked_songs=[
    #     {"title": "Come Together", "artist": "The Beatles"},
    #     {"title": "We Will Rock You", "artist": "Queen"},
    #     {"title": "Billie Jean", "artist": "Michael Jackson"}
    # ],
    #     disliked_songs=["Baby"],
    #     goal=UserGoal(
    #         goal_type=UserGoalType.create_playlist,
    #         goal_text="Create a playlist with up to 10 favorite songs from liked artists",
    #         max_songs=10
    #     ),
    #     # allowed_actions=[UserAction.add_song_to_playlist, UserAction.add_song_to_playlist_by_artist]
    #     allowed_actions=[
    #         UserAction.add_song_to_playlist
    #         ]
    # ),
    # UserProfile(
    #     id=2,
    #     liked_artists=["Adele", "Ed Sheeran"],
    #     disliked_artists=["Kanye West"],
    #     liked_songs=["Someone Like You", "Shape of You"],
    #     disliked_songs=["Stronger"],
    #     goal=UserGoal.ask_album_details
    # ),
    # UserProfile(
    #     id=3,
    #     liked_artists=["Billie Eilish", "Lorde"],
    #     disliked_artists=["Nickelback"],
    #     liked_songs=["Bad Guy", "Royals"],
    #     disliked_songs=["Photograph"],
    #     goal=UserGoal.receive_recommendations
    # ),
]
