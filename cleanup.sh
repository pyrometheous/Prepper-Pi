#!/bin/bash
echo "[*] Stopping and removing Docker containers..."
docker-compose down || echo "[-] Could not run docker-compose down"

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt_config

echo "[*] Cleanup complete."
