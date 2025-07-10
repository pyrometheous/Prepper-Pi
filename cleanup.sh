#!/bin/bash
echo "[*] Stopping and removing Docker containers..."
docker-compose down

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt/config

echo "[*] Cleanup complete."
