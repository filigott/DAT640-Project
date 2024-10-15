Generic single-database configuration.

Step 4: Create an Initial Migration
After configuring Alembic, generate the initial migration that matches your SQLAlchemy models:

bash
Copy code
alembic revision --autogenerate -m "Initial migration"
This will generate a new file under the alembic/versions folder. It will contain the SQL to create all your tables based on your models.

Step 5: Apply the Migration
To apply the migration to your database, run:

bash
Copy code
alembic upgrade head
This command will execute the SQL code generated in the migration file and apply the changes to your PostgreSQL database.

Step 6: Updating Models and Creating New Migrations
Whenever you make changes to your SQLAlchemy models, you need to generate new migrations.

Modify the models in models.py.
Run alembic revision --autogenerate -m "Added new fields"
Run alembic upgrade head to apply the new migration.
Example of Using Alembic with Song and Playlist
Adding a New Column (e.g., description to Playlist):
Modify your Playlist model in models.py:
python
Copy code
class Playlist(Base):
    __tablename__ = "playlists"
    playlist_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)  # New field
    songs = relationship("Song", secondary=playlist_song_association, back_populates="playlists")
Run the Alembic commands:
bash
Copy code
alembic revision --autogenerate -m "Added description to Playlist"
alembic upgrade head
Alembic will handle the migration by adding the description column to your playlists table.

Final Notes on Alembic:
Migrations and Auto-Generation: Alembic can generate migration scripts automatically using the --autogenerate flag, but ensure that your models and database schema are in sync.
Reverting Migrations: If you want to revert a migration, you can use alembic downgrade <version>. This is useful if you need to undo a schema change.
Handling Foreign Keys and Indexes: Alembic will also handle foreign key relationships and indexes defined in your SQLAlchemy models.