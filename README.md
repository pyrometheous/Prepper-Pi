# Prepper Pi

This project sets up a Raspberry Pi-based local server with Docker and custom Wi-Fi management, using OpenWRT and Jellyfin.

## 🚀 Quick Start

Copy and paste the following command into your Pi terminal after flashing Raspberry Pi OS:

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && bash first-run-setup.sh
```

This script:
- Enables PCIe for NVMe (reboot required)
- Mounts the NVMe drive to `/mnt/nvme`
- Installs Docker, Docker Compose
- Deploys the Docker stack (Traefik, Jellyfin, file browser, OpenWRT)
