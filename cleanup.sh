#!/bin/bash
set -e

echo "[*] Stopping and removing Docker containers..."

# Check if docker is accessible without sudo
if ! docker info > /dev/null 2>&1; then
    echo "[*] Docker requires sudo, using sudo for docker-compose..."
    alias docker-compose='sudo docker-compose'
fi

docker-compose down || sudo docker-compose down

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt

echo "[*] Cleanup complete."
