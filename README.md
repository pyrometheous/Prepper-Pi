# Prepper Pi Initial Setup

This archive sets up the core Docker stack and folder structure for your Raspberry Pi NVMe-based server.

## Instructions

1. Copy the contents of this archive to your Raspberry Pi (e.g., `/home/pi/setup`).
2. SSH into the Raspberry Pi and run:
   ```bash
   cd /home/pi/setup
   sudo ./first-run-setup.sh
   ```

This script installs Docker, mounts your NVMe drive, creates necessary folders, and deploys Jellyfin, Traefik, OpenWRT, and FileBrowser.

## Directory Structure

- `/mnt/nvme/configs/*`: Configuration for each app
- `/mnt/nvme/media/*`: Your media library
- `/mnt/nvme/transfer`: Use FileBrowser to move content from flash drives here
