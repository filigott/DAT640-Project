from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .routers import  client_only_routes, playlist_routes, song_routes, websocket_routes

from .init_db import reset_and_seed_db_demo
from .database import engine, DB_Base, get_db

# Create database tables
DB_Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register routers
app.include_router(client_only_routes.router)
app.include_router(playlist_routes.router)
app.include_router(song_routes.router)
app.include_router(websocket_routes.router)


# Endpoint to seed the database
@app.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    try:
        reset_and_seed_db_demo(db)  # Seed the database with demo data
        return {"message": "Database seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))