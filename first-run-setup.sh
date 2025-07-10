#!/bin/bash
echo "[*] Starting initial setup..."

# NVMe and Jellyfin setup - temporarily disabled
: '
echo "[*] Checking for PCIe config..."
CONFIG_LINE="dtparam=pciex1=true"
CONFIG_FILE="/boot/firmware/config.txt"
if ! grep -q "$CONFIG_LINE" "$CONFIG_FILE"; then
    echo "$CONFIG_LINE" | sudo tee -a "$CONFIG_FILE"
    echo "[*] PCIe enabled in config.txt (reboot required)."
else
    echo "[*] PCIe already enabled in config.txt."
fi

echo "[*] Mounting NVMe to /mnt/nvme..."
sudo mkdir -p /mnt/nvme
sudo mount /dev/nvme0n1p1 /mnt/nvme 2>/dev/null || echo "[!] NVMe not mounted (likely not connected yet)."
'

# Docker setup
echo "[*] Installing Docker..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose

# Pull and run containers
echo "[*] Starting Docker stack..."
sudo docker-compose up -d

echo "[*] Setup complete."
