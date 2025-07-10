#!/bin/bash

echo "[*] Stopping and removing Docker containers..."
docker-compose down || echo "[-] Docker compose down failed or was not installed."

echo "[*] Removing OpenWRT config directory..."
rm -rf openwrt/etc

echo "[*] Removing macvlan interface if exists..."
ip link delete macvlan0 2>/dev/null || echo "[-] macvlan0 not present."

echo "[*] Cleanup complete."
