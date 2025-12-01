#!/bin/bash

# Setup script for Pair Programming Application
# This script automates the setup process

set -e  # Exit on error

echo "=================================="
echo "Pair Programming App Setup"
echo "=================================="
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✓ Docker found"
    DOCKER_AVAILABLE=true
else
    echo "✗ Docker not found"
    DOCKER_AVAILABLE=false
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    echo "✓ Docker Compose found"
    DOCKER_COMPOSE_AVAILABLE=true
else
    echo "✗ Docker Compose not found"
    DOCKER_COMPOSE_AVAILABLE=false
fi

echo ""
echo "Choose setup method:"
echo "1) Docker (Recommended - requires Docker & Docker Compose)"
echo "2) Local (requires Python 3.11+ and PostgreSQL)"
read -p "Enter choice (1 or 2): " choice

if [ "$choice" == "1" ]; then
    if [ "$DOCKER_AVAILABLE" = false ] || [ "$DOCKER_COMPOSE_AVAILABLE" = false ]; then
        echo "Error: Docker and Docker Compose are required for this option"
        echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    echo ""
    echo "Starting services with Docker Compose..."
    docker-compose up -d
    
    echo ""
    echo "Waiting for services to be ready..."
    sleep 10
    
    echo ""
    echo "✓ Setup complete!"
    echo ""
    echo "Services:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo "  - PostgreSQL: localhost:5432"
    echo ""
    echo "To stop services: docker-compose down"
    echo "To view logs: docker-compose logs -f"
    
elif [ "$choice" == "2" ]; then
    echo ""
    echo "Setting up local environment..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "✓ Python found: $PYTHON_VERSION"
    else
        echo "✗ Python 3 not found"
        echo "Please install Python 3.11+ from: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Create virtual environment
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate || . venv/Scripts/activate
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    # Setup environment file
    if [ ! -f .env ]; then
        echo "Creating .env file..."
        cp .env.example .env
        echo "⚠ Please configure your .env file with database credentials"
    fi
    
    echo ""
    echo "✓ Backend setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Ensure PostgreSQL is running"
    echo "2. Configure backend/.env with your database credentials"
    echo "3. Run migrations: cd backend && alembic upgrade head"
    echo "4. Start server: uvicorn main:app --reload"
    echo ""
    echo "Then access:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    
else
    echo "Invalid choice"
    exit 1
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="