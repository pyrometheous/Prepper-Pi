#!/bin/bash
echo "[*] Starting initial setup..."

# Start Docker containers using modern compose syntax
echo "[*] Starting Docker stack..."
docker compose up -d

echo "[*] Setup complete."
