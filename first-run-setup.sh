#!/bin/bash
echo "[*] Starting initial setup..."
echo "[*] Installing packages from packages.txt..."
sudo apt update && sudo xargs -a packages.txt apt install -y

echo "[*] Configuring macvlan for OpenWRT..."
docker network inspect maclan >/dev/null 2>&1 || docker network create -d macvlan \
  --subnet=10.20.30.0/24 --gateway=10.20.30.1 \
  -o parent=wlan0 maclan

echo "[*] Starting Docker stack..."
docker-compose up -d
echo "[*] Setup complete."
