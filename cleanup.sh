#!/bin/bash
echo "[*] Stopping and removing Docker containers..."
sudo docker compose down || true

echo "[*] Removing OpenWRT config directory..."
rm -rf ./openwrt

echo "[*] Cleanup complete."
