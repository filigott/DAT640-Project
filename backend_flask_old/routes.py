from flask import Blueprint, render_template, redirect, url_for, request
from models import Playlist, Song
from db import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    playlist = Playlist.query.first()
    all_songs = Song.query.all()

    # Filter out songs that are already in the playlist
    songs_not_in_playlist = [song for song in all_songs if song not in playlist.songs]
    
    return render_template('index.html', playlist=playlist, songs=songs_not_in_playlist)

@main.route('/add_song', methods=['POST'])
def add_song():
    song_id = request.form.get('song_id')
    playlist = Playlist.query.first()  # Get the first playlist
    song = Song.query.get(song_id)  # Find the song by ID
    
    if song and playlist:
        playlist.songs.append(song)  # Add the song to the playlist
        db.session.commit()
    
    # return redirect(url_for('main.index'))

@main.route('/remove_song/<int:song_id>', methods=['POST'])
def remove_song(song_id):
    playlist = Playlist.query.first()  # Get the first playlist
    
    if playlist:
        song = Song.query.get(song_id)  # Find the song by ID
        if song in playlist.songs:
            playlist.songs.remove(song)  # Remove the song from the playlist
            db.session.commit()
    
    # return redirect(url_for('main.index'))
