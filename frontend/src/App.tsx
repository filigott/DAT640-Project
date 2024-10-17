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
  const playlistId = 1; // Static playlist ID for now
  const [searchTerm, setSearchTerm] = useState("");
  const [searchSongs, setSearchSongs] = useState<Song[]>([]);

  useEffect(() => {
    // Note. Dev mode calls this code twice startup.
    fetchPlaylist();
    
    // Establish WebSocket connection on mount
    const ws = new WebSocket("ws://localhost:8000/ws/playlist")

    ws.onmessage = (event) => {
      // Handle incoming messages (e.g., playlist updates)
      const message = event.data;
      console.log("Received from server:", message);

      // Parse the message if it's JSON (optional)
      const updatedPlaylistId = JSON.parse(message).updated_playlist_id;

      if (updatedPlaylistId === playlistId) {
        // Do something??
        console.log("Updating playlist...");
        fetchPlaylist();
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    if (searchTerm.length >= 3) {  // Fetch only if search term is at least 3 characters
      searchForSongs(searchTerm);
    } else {
      setSearchSongs([]);  // Clear if search term is less than 3 characters
    }
  }, [searchTerm]);

  const fetchPlaylist = async () => {
    try {
      const response = await axios.get<Playlist>(`/api/playlist/${playlistId}`);
      setPlaylist(response.data ?? []);
    } catch (error) {
      console.error("Error fetching playlist:", error);
    }
  };

  const handleAddSong = async (songId: number) => {
    try {
      const song = await axios.post(`/api/client/playlist/${playlistId}/add_song/${songId}`);
      console.log("Added song: ", song)
      fetchPlaylist()
    } catch (error) {
      console.error("Error adding song:", error);
    }
  };

  const handleRemoveSong = async (songId: number) => {
    try {
      const song = await axios.post(`/api/client/playlist/${playlistId}/remove_song/${songId}`);
      console.log("Removed song: ", song)
      fetchPlaylist()
    } catch (error) {
      console.error("Error removing song:", error);
    }
  };

  const searchForSongs = async (searchField: string) => {
    try {
      // Assuming the backend provides an endpoint to search for songs not in the playlist
      const response = await axios.get<Song[]>(`/api/playlist/${playlistId}/songs_not_in`, {
        params: { search: searchField }
      });
      setSearchSongs(response.data);
    } catch (error) {
      console.error("Error searching for songs: ", error);
    }
  };

return (
    <div className="App">
      <ChatWidget />

      {playlist ? (
        <>
            <PlaylistComponent playlist={playlist} onSongRemoved={handleRemoveSong} />
          
            <SongListComponent
              playlistId={playlistId}
              onSongAdded={handleAddSong}
              searchTerm={searchTerm}
              setSearchTerm={setSearchTerm}
              searchSongs={searchSongs}
            />
        </>
      ) : (
        <p>Loading playlist...</p>
      )}
    </div>
  );
};

export default App;
