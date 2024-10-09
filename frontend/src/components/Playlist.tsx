// src/components/PlaylistComponent.tsx
import React from "react";
import { Playlist, Song } from "../types";
import axios from "axios";

interface PlaylistProps {
  playlist: Playlist;
  onSongRemoved: (songId: number) => void; // Callback for when a song is removed
}

const PlaylistComponent: React.FC<PlaylistProps> = ({ playlist, onSongRemoved }) => {
  const handleRemoveSong = async (songId: number) => {
    try {
      await axios.post(`/api/playlist/${playlist.id}/remove_song/${songId}`);
      onSongRemoved(songId); // Notify parent component to update state
    } catch (error) {
      console.error("Error removing song:", error);
    }
  };

  return (
    <div className="playlist">
      <h2>{playlist.name}</h2>
      <ul>
        {playlist.songs?.length ? (
          playlist.songs.map((song: Song) => (
            <li key={song.id}>
              {song.title} by {song.artist}
              <button onClick={() => handleRemoveSong(song.id)}>Delete</button>
            </li>
          ))
        ) : (
          <li>No songs in this playlist.</li>
        )}
      </ul>
    </div>
  );
};

export default PlaylistComponent;
