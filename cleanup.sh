#!/bin/bash

echo "[*] Stopping and removing Docker containers..."

if command -v docker-compose &>/dev/null; then
    docker-compose down 2>/dev/null || echo "[-] Could not run docker-compose down"
elif docker compose version &>/dev/null; then
    docker compose down 2>/dev/null || echo "[-] Could not run docker compose down"
else
    echo "[-] Neither docker-compose nor docker compose found"
fi

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt-data

echo "[*] Cleanup complete."
