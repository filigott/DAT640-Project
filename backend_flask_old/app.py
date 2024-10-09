import os
from flask import Flask
from db import db
from routes import main as main_routes

ENABLE_DEBUG = True

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    db.init_app(app)

    app.register_blueprint(main_routes)  # Register routes

    return app

def init_db(app):
    with app.app_context():
        db.create_all()  # Create tables

        # Check if any songs exist to avoid duplicates
        if Song.query.count() == 0:
            from models import Song, Playlist  # Import here to avoid circular import

            songs = [
                Song(title="Shape of You", artist="Ed Sheeran", album="Divide", year=2017),
                Song(title="Blinding Lights", artist="The Weeknd", album="After Hours", year=2020),
                Song(title="Levitating", artist="Dua Lipa", album="Future Nostalgia", year=2020),
                Song(title="Bad Guy", artist="Billie Eilish", album="When We All Fall Asleep, Where Do We Go?", year=2019),
                Song(title="Watermelon Sugar", artist="Harry Styles", album="Fine Line", year=2019),
            ]

            # Add songs to the session
            db.session.bulk_save_objects(songs)
            db.session.commit()

            # Add a dummy playlist and associate songs with it
            playlist = Playlist(name="My Favorite Songs", description="A collection of my favorite tracks.")
            playlist.songs.extend(songs)  # Add all songs to the playlist
            
            db.session.add(playlist)
            db.session.commit()

if __name__ == "__main__":
    app = create_app()

    if not os.path.isfile("instance/db.sqlite"):
        init_db(app)
    
    app.run(debug=ENABLE_DEBUG, port=5001)
