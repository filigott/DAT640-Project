import random
from typing import Optional, List
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from rapidfuzz import process

from app.init_db import seed_db_demo
from app.utils import advanced_normalize_text
from ..models import PlaylistModel, SongModel

MAX_NUM_SONGS_SEARCH = 10
RAPIDFUZZ_SCORE_CUTOFF = 70

def create_playlist(db: Session, user_id: int):
    playlist: PlaylistModel = db.query(PlaylistModel).filter(PlaylistModel.id == user_id).first()

    if playlist:
        return
 
    playlist = PlaylistModel(title=f"User {user_id}'s favorite songs")
    db.add(playlist)
    db.commit()

def demo_seed_database(db: Session):
    seed_db_demo(db)

def get_all_playlists(db: Session) -> List[PlaylistModel]:
    """Retrieve all playlists from the database as raw models."""
    return db.query(PlaylistModel).all()

def get_all_songs(db: Session) -> List[SongModel]:
    """Retrieve all songs from the database as raw models."""
    return db.query(SongModel).all()

def get_playlist(db: Session, playlist_id: int) -> Optional[PlaylistModel]:
    """Retrieve a specific playlist by ID and return the raw model."""
    return db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()

def get_search_songs_not_in_playlist(db: Session, playlist_id: int, search_field: str = "") -> List[SongModel]:
    """Retrieve a maximum of 10 songs not in a specific playlist matching a search field."""
    
    # Create a query to fetch songs not in the specified playlist
    query = db.query(SongModel).filter(~SongModel.playlists.any(id=playlist_id))

    # If there's a search term, filter the query based on the search field
    if search_field:
        search = f"%{search_field.lower()}%"
        query = query.filter(
            (SongModel.title.ilike(search)) | 
            (SongModel.artist.ilike(search))
        )

    # Limit the query to 10 results
    return query.limit(MAX_NUM_SONGS_SEARCH).all()

async def add_song_to_playlist_async(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Add a song to a specific playlist and return the added song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()
    
    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.commit()
        return song
    return None

def add_song_to_playlist(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Add a song to a specific playlist and return the added song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()

    print("Song model inside: ", song)

    print(playlist)
    print(playlist.songs)
    
    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.commit()
        return song
    return None

async def remove_song_from_playlist_async(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Remove a song from a specific playlist and return the removed song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()

    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
        return song
    return None

def remove_song_from_playlist(db: Session, playlist_id: int, song_id: int) -> Optional[SongModel]:
    """Remove a song from a specific playlist and return the removed song."""
    playlist = get_playlist(db, playlist_id)
    song = db.query(SongModel).filter(SongModel.id == song_id).first()

    if playlist and song and song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
        return song
    return None

def clear_playlist(db: Session, playlist_id: int):
    """Clear all songs from a specific playlist."""
    playlist = get_playlist(db, playlist_id)
    if playlist:
        playlist.songs = []
        db.commit()

def get_song_id(db: Session, song_description: dict) -> Optional[int]:
    """Get a song ID based on a description (title, artist, album, year)."""
    filters = []
    if 'title' in song_description:
        filters.append(SongModel.title.ilike(f"%{song_description['title']}%"))
    if 'artist' in song_description:
        filters.append(SongModel.artist.ilike(f"%{song_description['artist']}%"))
    if 'album' in song_description:
        filters.append(SongModel.album.ilike(f"%{song_description['album']}%"))
    if 'year' in song_description:
        filters.append(SongModel.year == song_description['year'])

    try:
        song: SongModel = db.query(SongModel).filter(or_(*filters)).first()
        return song.id if song else None
    except Exception as e:
        print(f"Error fetching song ID: {e}")
        return None

def get_song_by_song_description(db: Session, song_description: dict) -> Optional[int]:
    """Get a song ID based on the song title."""
     # If 'id' is already provided in the description, return it directly
    song_id = song_description.get("id")
    if song_id:
        return song_id
    
    song_name = song_description.get("title")
    artist_name = song_description.get("artist")
    ##album_name = song_description["data"].get("album")
    if not song_name:
        return None
    
    if song_name and artist_name:
        song = db.query(SongModel).filter(SongModel.title == song_name, SongModel.artist == artist_name).first()
        return song.id if song else None

    song: SongModel = db.query(SongModel).filter(SongModel.title == song_name).first()
    return song.id if song else None

def get_songs_by_name(db: Session, song_name: str) -> List[SongModel]:
    """Get a list of songs based on the song title."""
    if not song_name:
        return []
    songs = db.query(SongModel).filter(SongModel.title.ilike(f"%{song_name}%")).all()
    print(songs)
    return songs

def get_songs_by_artist(db: Session, artist_name: str) -> List[SongModel]:
    """Get a list of songs based on the artist name."""
    if not artist_name:
        return []
  
    songs = db.query(SongModel).filter(SongModel.artist.ilike(f"%{artist_name}%")).all()
    if songs:
        return songs
    else:
        all_artists = db.query(SongModel.artist).distinct().all()
        artist_names = [artist[0] for artist in all_artists] 

        best_match = process.extractOne(artist_name, artist_names, score_cutoff=RAPIDFUZZ_SCORE_CUTOFF)
        if best_match:
            songs = db.query(SongModel).filter(SongModel.artist == best_match[0]).all()
            return songs
        return songs

def get_songs_by_album(db: Session, album_name: str) -> List[SongModel]:
    """Get a list of songs based on the album name."""
    if not album_name:
        return []
    songs = db.query(SongModel).filter(SongModel.album.ilike(f"%{album_name}%")).all()
    return songs


def filter_and_rank_songs(
    playlist_songs: List[SongModel],
    songs_to_filter: List[SongModel],
    num_recommendations: int
) -> List[SongModel]:
    
    filtered_songs = songs_to_filter
    
    # Extract artists, albums, and titles from the playlist songs
    if playlist_songs:
        artists = {song.artist for song in playlist_songs}
        albums = {song.album for song in playlist_songs}
        titles = {song.title for song in playlist_songs}

        print("Inside filter and rank songs: ", artists, albums, titles)

        # Filter the songs based on relaxed matching (at least one condition met)
        filtered_songs = [
            song for song in songs_to_filter
            if (song.artist in artists or song.album in albums) and song.title not in titles
        ]

    print("Num filtered song in filter_and_rank_songs: ", len(filtered_songs))
    if not filtered_songs:
        return []

    # Rank the filtered songs by ID in descending order (higher IDs are better)
    top_songs = sorted(filtered_songs, key=lambda song: song.id, reverse=False)[:num_recommendations * 5]

    print(f"Num top songs after sorting and limiting: {len(top_songs)}")

    # Ensure the number of songs to sample is not greater than the available population
    sample_size = min(num_recommendations, len(top_songs))

    # Randomly sample from the top-ranked songs for variety
    final_selection = random.sample(top_songs, sample_size)

    return final_selection



def get_recommendations_from_songs(
    db: Session,
    playlist_id: int,
    songs: Optional[List[SongModel]] = None,
    num_recommendations: int = 10
) -> List[SongModel]:
    # Retrieve playlist songs from the database based on the given playlist_id
    playlist = get_playlist(db, playlist_id)
    playlist_songs = SongModel.list_to_dto(playlist.songs)

    # Determine the set of songs to filter: either provided as input or query all songs from DB
    if songs is None:
        songs_to_filter = db.query(SongModel).all()
    else:
        songs_to_filter = songs

    # Use the helper function to filter and rank the songs
    recommended_songs = filter_and_rank_songs(
        playlist_songs=playlist_songs,
        songs_to_filter=songs_to_filter,
        num_recommendations=num_recommendations
    )

    return recommended_songs


def find_fuzzy_song_matches(
    db: Session, 
    title: str, 
    artist: Optional[str] = None, 
    album: Optional[str] = None, 
    year: Optional[int] = None
) -> List[SongModel]:
    """Find songs that match the specified criteria with flexible matching, considering the song's id as its rank."""
    
    # Normalize the input title for fuzzy matching
    normalized_title = advanced_normalize_text(title)

    # Start the query with ilike to allow partial matches on the normalized title
    query = db.query(SongModel).filter(SongModel.normalized_title.ilike(f"%{normalized_title}%"))
    
    if artist:
        query = query.filter(SongModel.artist.ilike(f"%{artist}%"))
    if album:
        query = query.filter(SongModel.album.ilike(f"%{album}%"))
    if year:
        query = query.filter(SongModel.year == year)
    
    # Retrieve initial candidates using the ilike query (limiting to 50 for now)
    candidates: List[SongModel] = query.limit(50).all()

    print("Num fuzzy song matches candidates: ", len(candidates))
    
    # Normalize the titles of all candidates for better matching
    candidate_titles = [advanced_normalize_text(c.title) for c in candidates]
    
    # Perform fuzzy matching using the normalized title
    scored_candidates = process.extract(normalized_title, candidate_titles, score_cutoff=RAPIDFUZZ_SCORE_CUTOFF)
    
    # Map back to SongModel objects using the index of matches in scored_candidates
    matched_songs = [candidates[idx] for _, score, idx in scored_candidates]

    # Now, we rank the songs based on their original position (id is treated as the rank)
    ranked_songs = sorted(matched_songs, key=lambda song: song.id)
    
    return ranked_songs[:MAX_NUM_SONGS_SEARCH]


def find_exact_song_match(
    db: Session, 
    title: str, 
    artist: Optional[str] = None, 
    album: Optional[str] = None, 
    year: Optional[int] = None
) -> Optional[SongModel]:
    """Attempts to find a song with an exact match on title, artist, album, and year."""

    # Apply exact filters for title, artist, album, and year
    filters = [SongModel.title == title]
    if artist:
        filters.append(SongModel.artist == artist)
    if album:
        filters.append(SongModel.album == album)
    if year:
        filters.append(SongModel.year == year)

    # Query with all filters applied
    matched_songs = db.query(SongModel).filter(and_(*filters)).all()
    
    # Return the song if there is a unique match
    if len(matched_songs) == 1:
        return matched_songs[0]
    elif len(matched_songs) > 1 and artist:
        # Additional check for exact match with title and artist only
        best_match = matched_songs[0]
        for song in matched_songs[1:]:
            if best_match.title == song.title and best_match.artist == song.artist:
                return best_match

    # No unique exact match found
    return None