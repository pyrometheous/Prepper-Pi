#!/bin/bash

echo "[*] Starting initial setup..."

echo "[*] Installing packages from packages.txt..."
sudo apt update
sudo xargs -a packages.txt apt install -y

echo "[*] Creating OpenWRT config directory..."
mkdir -p openwrt-config

echo "[*] Starting Docker stack..."
sudo docker-compose up -d

echo "[*] Setup complete."