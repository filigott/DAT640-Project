from fastapi import FastAPI
from .routers import  client_only_routes, playlist_routes, song_routes, websocket_routes, seed_routes

from .database import engine, DB_Base

# Create database tables
DB_Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routers
app.include_router(client_only_routes.router)
app.include_router(playlist_routes.router)
app.include_router(song_routes.router)
app.include_router(websocket_routes.router)
app.include_router(seed_routes.router)