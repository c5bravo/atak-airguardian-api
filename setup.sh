#!/bin/bash
# setup.sh - Setup script for ATAK Air Guardian API

set -e

echo "ATAK Air Guardian API - Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed!!!!"
    echo "Run ./install_docker_ubuntu.sh first"
    exit 1
fi

echo "✅ Docker is installed"

# Check .env.docker
if [ ! -f ".env.docker" ]; then
    echo ".env.docker file not found!!!"
    echo "Please create .env.docker file with your configuration"
    exit 1
fi

echo ".env.docker file found"

echo ""
echo "======================================"
echo "  Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Review .env.docker configuration"
echo "  2. Start services: docker compose up -d --build"
echo "  3. View logs: docker compose logs -f"
echo "  4. Check status: docker compose ps"
echo ""
echo "Test the API: curl https://localhost:8002/radar/aircraft"
echo ""
