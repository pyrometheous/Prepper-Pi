#!/bin/bash
# Enable PCIe (needed for NVMe)
if ! grep -q 'dtparam=pciex1=true' /boot/firmware/config.txt; then
  echo 'dtparam=pciex1=true' | sudo tee -a /boot/firmware/config.txt
fi

set -e

NVME_DEV="/dev/nvme0n1p1"
MOUNT_POINT="/mnt/nvme"
COMPOSE_FILE="$MOUNT_POINT/docker-compose.yml"

echo "[*] Starting initial setup..."

# Ensure PCIe is enabled for NVMe support
CONFIG_FILE="/boot/firmware/config.txt"
if ! grep -q "^dtparam=pciex1=on" "$CONFIG_FILE"; then
  echo "[*] Enabling PCIe for NVMe in config.txt..."
  echo "dtparam=pciex1=on" | sudo tee -a "$CONFIG_FILE"
else
  echo "[*] PCIe already enabled in config.txt."
fi


if ! grep -qs "$MOUNT_POINT " /proc/mounts; then
    echo "[*] Mounting NVMe to $MOUNT_POINT..."
    sudo mkdir -p $MOUNT_POINT
    sudo mount $NVME_DEV $MOUNT_POINT
else
    echo "[*] NVMe already mounted."
fi

echo "[*] Creating folder structure..."
mkdir -p $MOUNT_POINT/configs/{jellyfin,openwrt,traefik,filebrowser}
mkdir -p $MOUNT_POINT/media/{movies,shows,music}
mkdir -p $MOUNT_POINT/transfer

echo "[*] Installing Docker and Docker Compose..."
sudo apt update
sudo apt install -y docker.io docker-compose unzip

echo "[*] Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

echo "[*] Writing docker-compose.yml..."

cat <<EOF | tee $COMPOSE_FILE > /dev/null
version: "3.8"

services:
  traefik:
    image: traefik:v2.11
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - $MOUNT_POINT/configs/traefik:/etc/traefik
    restart: always

  openwrt:
    image: openwrtorg/rootfs:x86-64
    privileged: true
    network_mode: host
    volumes:
      - $MOUNT_POINT/configs/openwrt:/etc/config
    restart: always

  jellyfin:
    image: jellyfin/jellyfin
    ports:
      - "8096:8096"
    volumes:
      - $MOUNT_POINT/configs/jellyfin:/config
      - $MOUNT_POINT/media:/media
    restart: always

  filebrowser:
    image: filebrowser/filebrowser
    ports:
      - "8081:80"
    volumes:
      - $MOUNT_POINT/transfer:/srv
      - $MOUNT_POINT/configs/filebrowser:/config
    restart: always
EOF

echo "[*] Deploying Docker stack..."
cd $MOUNT_POINT
sudo docker-compose up -d

echo "[✔] Setup complete! Services are now running."
