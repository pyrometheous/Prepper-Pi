#!/bin/bash
echo "[*] Starting initial setup..."

# Install Docker & Docker Compose
echo "[*] Installing Docker..."
sudo apt update && sudo apt install -y docker.io docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER

# Create OpenWRT config directory
mkdir -p openwrt/config

# Copy default OpenWRT config files
cp -r openwrt/default_config/* openwrt/config/

# Start Docker stack
echo "[*] Starting Docker stack..."
docker-compose up -d

echo "[*] Setup complete. You may need to reboot or log out/in for docker group changes to take effect."
