#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Virtual environment not activated"
    exit 1
fi

# Check if Docker container is running
if ! docker-compose ps | grep -q "Up"; then
    echo "Error: Docker container is not running"
    echo "Starting Docker container..."
    docker-compose up -d
fi

# Add the project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the application
echo "Starting FritterLedger..."
python src/main.py