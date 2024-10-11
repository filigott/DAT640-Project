#!/bin/bash

# Navigate to FastAPI backend directory and start the server
echo "Starting FastAPI backend..."
cd backend_fastAPI
uvicorn app.main:app --reload &
FASTAPI_PID=$!
echo "FastAPI backend started with PID: $FASTAPI_PID"
cd ..

# # Navigate to Flask backend directory and start the server
# echo "Starting Flask server..."
# cd chatbot_agent
# python3 chat_bot.py &
# FLASK_PID=$!
# echo "Flask server started with PID: $FLASK_PID"
# cd ..

# Navigate to frontend directory and start Vite
echo "Starting Vite React frontend..."
cd frontend
npm run dev &
VITE_PID=$!
echo "Vite React frontend started with PID: $VITE_PID"
cd ..

# Function to stop all processes on script exit
cleanup() {
    echo "Stopping all running services..."
    
    echo "Stopping FastAPI (PID: $FASTAPI_PID)..."
    kill $FASTAPI_PID

    echo "Stopping Flask (PID: $FLASK_PID)..."
    kill $FLASK_PID

    echo "Stopping Vite React frontend (PID: $VITE_PID)..."
    kill $VITE_PID
    
    echo "All services stopped."
    exit 0
}

# Trap CTRL+C (SIGINT) and call cleanup
trap cleanup SIGINT

# Keep the script running to allow the servers to keep running
echo "All services are running. Press Ctrl + C to stop them."
wait
