# Prepper-Pi

An offline-capable Raspberry Pi-based media server and local Wi-Fi access point with Docker support.

## Features

- Wi-Fi access point using OpenWRT in Docker
- Traefik reverse proxy for subdomain routing
- Jellyfin media server
- File browser for transferring files from USB to NVMe
- All app configs and media stored on NVMe SSD

## SSH Setup

1. SSH into your Raspberry Pi:

```bash
ssh pi@<your-pi-ip>
```

(Default username/password is `pi`/`raspberry`, unless changed.)

2. Clone the repository:

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git
cd Prepper-Pi
```

3. Run the setup script:

```bash
chmod +x startup.sh
./startup.sh
```

This will:
- Set up necessary folders
- Deploy Docker services
