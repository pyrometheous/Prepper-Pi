#!/bin/bash
set -e

echo "[*] Starting initial setup..."

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "[*] Installing Docker..."
    sudo apt update
    sudo apt install -y docker.io docker-compose
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
fi

# Create Docker network and start Traefik
echo "[*] Starting Docker stack..."
docker-compose up -d

echo "[*] Setup complete."
