import React from "react";
import { Playlist, Song } from "../types";

interface PlaylistProps {
  playlist: Playlist;
  onSongRemoved: (songId: number) => void; // Callback for when a song is removed
}

const PlaylistComponent: React.FC<PlaylistProps> = ({ playlist, onSongRemoved }) => {
  return (
    <div className="playlist">
      <h2>{playlist.title}</h2>
      <ul>
        {playlist.songs?.length ? (
          playlist.songs.map((song: Song) => (
            <li key={song.id} className="song-item">
              <div className="song-details">
                <span className="song-title">{song.title}</span> by <span className="song-artist">{song.artist}</span>
                {song.album && <span className="song-album"> | Album: {song.album}</span>}
                {song.year && <span className="song-year"> | Year: {song.year}</span>}
              </div>
              <button className="remove-song-btn" onClick={() => onSongRemoved(song.id)}>Delete</button>
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
