export interface Song {
  id: number;
  title: string;
  artist: string;
  album?: string;
  year?: number;
}

export interface Playlist {
  id: number;
  name: string;
  songs: Song[];
}