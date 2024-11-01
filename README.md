# Project Name

A brief description of your project.

## Requirements

- **Docker** and **Docker Compose**
- **Node.js** (for the frontend)
- **Python 3.x** (for the backend)

## Dataset

- Download dataset from: <https://www.kaggle.com/datasets/snapcrack/the-billboard-200-acoustic-data>
- Place unzipped sqlite database file into the data folder

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Start the services with Docker**:

   ```bash
   cd postgres
   docker compose pull && docker compose up -d
   ```

3. **Set up the backend**:

   - Navigate to the `backend_fastAPI` directory and install dependencies:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Set up the frontend**:

   - Navigate to the `frontend` directory and install dependencies:

   ```bash
   npm install
   ```

## Running the Application

To start the FastAPI backend and the Vite frontend, run the following commands in their respective folders:

```bash
# Start the chat bot agent server
python3 run_chat_bot.py

# Start the backend
uvicorn app.main:app --reload

# Start the Vite frontend
npm run dev

# Start rasa agent from rasa directory
rasa run --enable-api -m models/nlu-20241017-225924-brilliant-formant.tar.gz
```

## Access the Application

- **FastAPI**: `http://localhost:8000`
- **Vite React**: `http://localhost:8001`
- **PostgreSQL**: `localhost:5432` (use `postgres`/`postgres` for user/password)
- **Adminer**: `http://localhost:8080`
- **Rasa**: `http://localhost:5005`


## Stopping the Application

To stop the services:

```bash
docker-compose down
```

Alternatively, if you started the backend and frontend manually, you can stop them by pressing `Ctrl + C` in the terminal where they are running. This will gracefully terminate the FastAPI and Vite processes.
