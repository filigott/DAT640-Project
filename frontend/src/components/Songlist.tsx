// src/components/SongListComponent.tsx
import React from "react";
import { Song } from "../types";
import axios from "axios";

interface SongListProps {
  playlistId: number; // Pass the playlist ID as a prop
  songsNotInPlaylist: Song[];
  onSongAdded: (songId: number) => void; // Callback for when a song is added
}

const SongListComponent: React.FC<SongListProps> = ({ playlistId, songsNotInPlaylist, onSongAdded }) => {
  const handleAddSong = async (songId: number) => {
    try {
      await axios.post(`/api/playlist/${playlistId}/add_song/${songId}`);
      onSongAdded(songId); // Notify parent to remove song from available list
    } catch (error) {
      console.error("Error adding song:", error);
    }
  };

  return (
    <div className="song-list">
      <h2>Songs Available to Add</h2>
      <ul>
        {songsNotInPlaylist.length > 0 ? (
          songsNotInPlaylist.map((song) => (
            <li key={song.id} className="song-item">
              <div className="song-details">
                <span className="song-title">{song.title}</span> by <span className="song-artist">{song.artist}</span>
                {song.album && <span className="song-album"> | Album: {song.album}</span>}
                {song.year && <span className="song-year"> | Year: {song.year}</span>}
              </div>
              <button className="add-song-btn" onClick={() => handleAddSong(song.id)}>Add</button>
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
