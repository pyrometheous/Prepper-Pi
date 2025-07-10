#!/bin/bash
set -e

echo "[*] Starting initial setup..."

# Install Docker and Docker Compose if not installed
if ! command -v docker &> /dev/null; then
    echo "[*] Installing Docker..."
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
fi

echo "[*] Starting Docker stack..."
docker compose up -d

echo "[*] Setup complete."
