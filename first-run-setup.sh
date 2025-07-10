#!/bin/bash
set -e

echo "[*] Starting initial setup..."

echo "[*] Starting Docker stack..."
docker compose up -d

echo "[*] Setup complete."
