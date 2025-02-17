import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import PlaylistComponent from "./components/Playlist";
import SongListComponent from "./components/Songlist";
import { Playlist, Song } from "./types";
import './App.css'; 
import CustomChatWidget from "./components/CustomChatWidget/CustomChatWidget";

// Debounce function to avoid multiple API calls on quick inputs
const debounce = (func: Function, delay: number) => {
  let timer: ReturnType<typeof setTimeout>;
  return function (...args: any[]) {
    clearTimeout(timer);
    timer = setTimeout(() => func(...args), delay);
  };
};

const App: React.FC = () => {
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const playlistId = 1; // Static playlist ID for now
  const [searchTerm, setSearchTerm] = useState("");
  const [searchSongs, setSearchSongs] = useState<Song[]>([]);
  const playlistWS = useRef<WebSocket | null>(null);

  const establishPlaylistConnection = useCallback(() => {
    if (playlistWS.current) {
      playlistWS.current.close(); // Close existing connection if any
    }
    playlistWS.current = new WebSocket("ws://localhost:8000/ws/playlist");

    playlistWS.current.onopen = () => {
      console.log("Connected to playlist WebSocket");
    };

    playlistWS.current.onmessage = (event) => {
      const message = event.data;
      console.log("Received from server:", message);
      const updatedPlaylistId = JSON.parse(message).updated_playlist_id;

      if (updatedPlaylistId === playlistId) {
        console.log("Updating playlist...");
        fetchPlaylist();
      }
    };

    playlistWS.current.onclose = () => {
      console.log("Disconnected from playlist WebSocket");
    };
  }, [playlistId]);

  useEffect(() => {
    fetchPlaylist();
    establishPlaylistConnection();

    return () => {
      playlistWS.current?.close();
    };
  }, [establishPlaylistConnection]);

  const reconnectAll = useCallback(() => {
    establishPlaylistConnection();
  }, [establishPlaylistConnection]);

  // Memoize the debounced search function
  const debouncedSearchForSongs = useCallback(
    debounce(async (searchField: string) => {
      try {
        const response = await axios.get<Song[]>(`/api/playlist/${playlistId}/songs_not_in`, {
          params: { search: searchField },
        });
        setSearchSongs(response.data);
      } catch (error) {
        console.error("Error searching for songs:", error);
      }
    }, 300), [playlistId]
  );

  useEffect(() => {
    if (searchTerm.length >= 3) {  // Fetch only if search term is at least 3 characters
      debouncedSearchForSongs(searchTerm);
    } else {
      setSearchSongs([]);  // Clear if search term is less than 3 characters
    }
  }, [searchTerm, debouncedSearchForSongs]);

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
      console.log("Added song: ", song);
      fetchPlaylist();
    } catch (error) {
      console.error("Error adding song:", error);
    }
  };

  const handleRemoveSong = async (songId: number) => {
    try {
      const song = await axios.post(`/api/client/playlist/${playlistId}/remove_song/${songId}`);
      console.log("Removed song: ", song);
      fetchPlaylist();
    } catch (error) {
      console.error("Error removing song:", error);
    }
  };

  return (
    <div className="App">
      <CustomChatWidget reconnectAll={reconnectAll} />
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
