from db import db

# Association table for the many-to-many relationship between playlists and songs
playlist_song = db.Table(
    "playlist_song",
    db.Column("playlist_id", db.Integer, db.ForeignKey("playlists.id"), primary_key=True),
    db.Column("song_id", db.Integer, db.ForeignKey("songs.id"), primary_key=True)
)

class Song(db.Model):
    __tablename__ = "songs"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    artist = db.Column(db.String(100), nullable=False, index=True)
    album = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Song {self.title} by {self.artist}>"

class Playlist(db.Model):
    __tablename__ = "playlists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)

    # Many-to-many relationship
    songs = db.relationship(
        "Song",
        secondary=playlist_song,
        lazy="subquery",
        backref=db.backref("playlists", lazy=True)
    )

    def __repr__(self):
        return f"<Playlist {self.name}>"
