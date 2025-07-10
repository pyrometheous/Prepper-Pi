#!/bin/bash
echo "[*] Stopping and removing Docker containers..."
if docker compose down; then
    echo "[*] Docker containers removed."
else
    echo "[-] Could not run docker compose down"
fi

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt-config

echo "[*] Cleanup complete."
