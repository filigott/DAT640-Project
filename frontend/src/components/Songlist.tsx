import React, { useState } from "react";
import { Song } from "../types";

interface SongListProps {
  playlistId: number; // Pass the playlist ID as a prop
  songsNotInPlaylist: Song[];
  onSongAdded: (songId: number) => void; // Callback for when a song is added
}

const numSongsToDisplay = 10;

const SongListComponent: React.FC<SongListProps> = ({ songsNotInPlaylist, onSongAdded }) => {
  const [searchTerm, setSearchTerm] = useState("");

  // Filter songs based on the search term
  const filteredSongs = songsNotInPlaylist.filter((song) =>
    song.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    song.artist && song.artist.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="song-list">
      <h2>Songs Available to Add</h2>
      
      {/* Search Box */}
      <input
        type="text"
        placeholder="Search by title or artist..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="search-box"
      />

      <ul>
        {filteredSongs.length > 0 ? (
          // Display only the first N songs
          filteredSongs.slice(0, numSongsToDisplay).map((song) => ( 
            <li key={song.id} className="song-item">
              <div className="song-details">
                <span className="song-title">{song.title}</span> by <span className="song-artist">{song.artist}</span>
                {song.album && <span className="song-album"> | Album: {song.album}</span>}
                {song.year && <span className="song-year"> | Year: {song.year}</span>}
              </div>
              <button className="add-song-btn" onClick={() => onSongAdded(song.id)}>Add</button>
            </li>
          ))
        ) : (
          <li>No songs available to add.</li>
        )}
      </ul>
    </div>
  );
};

export default SongListComponent;
