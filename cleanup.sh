#!/bin/bash
echo "[*] Stopping and removing Docker containers..."
if command -v docker compose &>/dev/null; then
    docker compose down || echo "[-] Could not run docker compose down"
else
    docker-compose down || echo "[-] Could not run docker-compose down"
fi

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt

echo "[*] Cleanup complete."
