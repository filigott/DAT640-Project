// src/App.tsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import PlaylistComponent from "./components/Playlist";
import SongListComponent from "./components/Songlist";
import { Playlist, Song } from "./types";
import ChatWidget from "./components/ChatWidget";
import './App.css'; 


const App: React.FC = () => {
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [songsNotInPlaylist, setSongsNotInPlaylist] = useState<Song[]>([]);
  const playlistId = 1; // Static playlist ID for now

  useEffect(() => {
    fetchPlaylist();
    fetchSongsNotInPlaylist();

    // Establish WebSocket connection on mount
    const ws = new WebSocket("ws://localhost:8000/ws/playlist")

    ws.onmessage = (event) => {
      // Handle incoming messages (e.g., playlist updates)
      const message = event.data;
      console.log("Received from server:", message);

      // Parse the message if it's JSON (optional)
      const updatedPlaylistId = JSON.parse(message);

      console.log(updatedPlaylistId)

      // Update the playlist if a new song is added or removed
      if (updatedPlaylistId === playlistId) {
        fetchPlaylist();
        fetchSongsNotInPlaylist();
      }
    };

    return () => {
      ws.close(); // Clean up WebSocket connection on component unmount
    };
  }, []);

  const fetchPlaylist = async () => {
    try {
      const response = await axios.get<Playlist>(`/api/playlist/${playlistId}`);
      setPlaylist(response.data);
    } catch (error) {
      console.error("Error fetching playlist:", error);
    }
  };

  const fetchSongsNotInPlaylist = async () => {
    try {
      const response = await axios.get<Song[]>(`/api/playlist/${playlistId}/songs_not_in`);
      setSongsNotInPlaylist(response.data);
    } catch (error) {
      console.error("Error fetching songs not in playlist:", error);
    }
  };

  const handleAddSong = async (songId: number) => {
    try {
      await axios.post(`/api/playlist/${playlistId}/add_song/${songId}`);
      // After adding, we need to refresh both the playlist and songs not in playlist
      fetchPlaylist();
      fetchSongsNotInPlaylist();
    } catch (error) {
      console.error("Error adding song:", error);
    }
  };

  const handleRemoveSong = async (songId: number) => {
    try {
      await axios.post(`/api/playlist/${playlistId}/remove_song/${songId}`);
      // After removing, we need to refresh both the playlist and songs not in playlist
      fetchPlaylist();
      fetchSongsNotInPlaylist();
    } catch (error) {
      console.error("Error removing song:", error);
    }
  };

return (
    <div className="App">
      <ChatWidget />

      {playlist ? (
        <>
            <PlaylistComponent playlist={playlist} onSongRemoved={handleRemoveSong} />
          
            <SongListComponent
              songsNotInPlaylist={songsNotInPlaylist}
              playlistId={playlistId}
              onSongAdded={handleAddSong}
            />
        </>
      ) : (
        <p>Loading playlist...</p>
      )}
    </div>
  );
};

export default App;
