// Important! These interfaces should match the schema of the matching model

export interface Song {
  id: number;
  title: string;
  artist?: string;
  album?: string;
  year?: number;
}

export interface Playlist {
  id: number;
  title: string;
  songs: Song[];
}
