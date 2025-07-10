#!/bin/bash
echo "[*] Starting initial setup..."

echo "[*] Starting Docker stack..."
if command -v docker compose &>/dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

echo "[*] Setup complete."
