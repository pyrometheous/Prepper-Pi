#!/bin/bash
set -e

echo "Creating directories..."
mkdir -p /mnt/nvme/config/jellyfin
mkdir -p /mnt/nvme/config/filebrowser
mkdir -p /mnt/nvme/media

echo "Bringing up Docker containers..."
docker compose up -d
