import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..init_db import seed_db_demo, seed_db_dataset_sqlite
from ..database import get_db

router = APIRouter()

# Endpoint to seed the database
@router.post("/seed/demo")
def seed_database_demo(db: Session = Depends(get_db)):
    try:
        seed_db_demo(db)  # Seed the database with demo data
        return {"message": "Database seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# Endpoint to seed the database
@router.post("/seed/dataset")
def seed_database_dataset(db: Session = Depends(get_db)):
    try:
         # Get the absolute path to the SQLite file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        db_file_path = os.path.join(base_dir, "data", "billboard-200.db")

        if not db_file_path:
            raise Exception("No dataset file")

        # Seed the database using the absolute path
        seed_db_dataset_sqlite(db, db_file_path)

        return {"message": "Database seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))