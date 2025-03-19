#!/bin/bash

# Stop and remove existing Docker containers
echo "Cleaning up Docker containers..."
docker-compose down -v

# Remove existing virtual environment
echo "Removing existing virtual environment..."
rm -rf venv

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    libyaml-dev \
    python3-yaml \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    python3-pil

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and core packages
echo "Upgrading pip and core packages..."
pip install --upgrade pip setuptools wheel

# Create a temporary requirements file without Pillow
echo "PyQt6==6.4.0
SQLAlchemy==1.4.41
psycopg2-binary==2.9.5
python-dateutil==2.8.2" > requirements.txt

# Install base requirements
echo "Installing base requirements..."
pip install -r requirements.txt

# Install Pillow separately
echo "Installing Pillow..."
pip install Pillow==9.3.0

# Create necessary directories
echo "Creating directories..."
mkdir -p exports

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Starting Docker..."
    sudo systemctl start docker
fi

# Start database container
echo "Starting database container..."
docker-compose up -d || {
    echo "Error starting Docker container"
    exit 1
}

echo "Setup complete! Run './run.sh' to start the application."