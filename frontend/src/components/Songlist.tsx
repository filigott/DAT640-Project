import { Song } from "../types";

interface SongListProps {
  playlistId: number;
  searchSongs: Song[];
  onSongAdded: (songId: number) => void;
  searchTerm: string;
  setSearchTerm: (searchTerm: string) => void;
}

const SongListComponent: React.FC<SongListProps> = ({ searchSongs, onSongAdded, searchTerm, setSearchTerm }) => {
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
        {searchSongs && searchSongs.length > 0 ? (
          searchSongs.map((song) => (
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
          <li>No songs found matching the search criteria.</li>
        )}
      </ul>
    </div>
  );
};

export default SongListComponent;
