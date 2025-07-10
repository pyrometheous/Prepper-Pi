#!/bin/bash

echo "[*] Stopping and removing Docker containers..."
if command -v docker &>/dev/null; then
    if docker ps -a --format '{{.Names}}' | grep -q 'traefik\|openwrt'; then
        docker compose down || echo "[-] Could not run docker compose down"
    else
        echo "[*] No matching containers to stop."
    fi
else
    echo "[-] Docker is not installed."
fi

echo "[*] Removing OpenWRT config directory..."
rm -rf ./openwrt

echo "[*] Cleanup complete."
