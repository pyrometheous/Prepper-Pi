#!/bin/bash

echo "[*] Starting initial setup..."

# Install required packages
if [ -f packages.txt ]; then
  echo "[*] Installing packages from packages.txt..."
  sudo apt update && sudo xargs -a packages.txt apt install -y
fi

# Start Docker services
echo "[*] Starting Docker stack..."
docker-compose up -d

echo "[*] Setup complete."
