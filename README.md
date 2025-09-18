# 🥧 Prepper Pi

# IMPORTANT NOTE: THIS IS NOT PRODUCTION READY AND SHOULD NOT BE USED AND EXPECTED TO WORK PROPERLY



**An all-in-one Raspberry Pi-based offline-first server for emergency preparedness and off-grid scenarios.**

Prepper Pi transforms your Raspberry Pi into a complete offline-capable server with WiFi hotspot, media streaming, file sharing, and network management - perfect for camping, emergencies, or anywhere you need local services without internet.

## ✨ Features

### 🌐 Network & Connectivity
- **WiFi Hotspot**: Broadcasts open "Prepper Pi" network using OpenWRT in Docker
- **Captive Portal**: Landing page automatically opens when connecting
- **Network Management**: Full OpenWRT router functionality with firewall, DHCP, routing
- **Dual-band Support**: 2.4GHz and 5GHz networks (with compatible hardware)
- **Internet Fallback**: Smart switching between offline and online modes

### 📱 Web Services
- **Landing Page**: Beautiful dashboard with links to all services
- **Media Streaming**: Jellyfin server for movies, TV shows, music
- **File Sharing**: Samba/CIFS network shares for easy file access
- **Container Management**: Portainer for Docker administration
- **Reverse Proxy**: Traefik for clean URLs and SSL termination

### 🚀 Future Expansion Ready
- **RTL-SDR Radio**: Software-defined radio capabilities
- **TV Tuning**: USB ATSC/DVB-T tuner support
- **Offline Archives**: Wikipedia, maps, ebooks
- **Local LLM**: AI assistant running locally
- **IoT Integration**: Home automation and sensors

## 📋 Hardware Requirements

### 🧠 Minimum Setup
- **Raspberry Pi 4/5** (4GB+ RAM recommended)
- **microSD Card** (32GB+ for OS)
- **USB WiFi Adapter** (AP mode capable, e.g., ALFA AWUS036ACM)
- **Power Supply** (Official Raspberry Pi adapter recommended)

### 🚀 Recommended Setup
- **Raspberry Pi 5** (8GB RAM)
- **NVMe SSD + Hat** (for fast storage and Docker volumes)
- **ALFA AWUS036ACM** (Dual-band USB WiFi with excellent range)
- **Active Cooling** (for sustained performance)
- **External Storage** (USB HDD/SSD for media)

### 📡 Optional Expansion
- **RTL-SDR Dongle** (for radio reception)
- **USB TV Tuner** (for OTA broadcasts)
- **Battery Bank** (for portable operation)
- **Ethernet Adapter** (for additional network ports)

## 🚀 Quick Setup

### 🛠 One-Line Installation

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash first-run-setup.sh
```

### 🧹 One-Line Removal

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash cleanup.sh && cd .. && rm -rf Prepper-Pi
```

## 📖 Detailed Setup

### 1. **Prepare Your Raspberry Pi**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Clone repository
git clone https://github.com/pyrometheous/Prepper-Pi.git
cd Prepper-Pi
```

### 2. **Run Setup Script**
```bash
# Run the automated setup (requires sudo)
sudo bash first-run-setup.sh
```

### 3. **Configure WiFi Adapter** (if using external adapter)
```bash
# Setup external WiFi adapter for AP mode
sudo bash setup-wifi-adapter.sh
```

### 4. **Access Your Services**
- **Landing Page**: `http://prepper-pi.local:3000`
- **OpenWRT**: `http://10.20.30.1`
- **Portainer**: `http://localhost:9000`
- **Jellyfin**: `http://localhost:8096`

## 🌐 Network Architecture

```
Internet ──► [Raspberry Pi] ──► WiFi Hotspot "Prepper Pi"
              │                    │
              ├─ OpenWRT (10.20.30.1)
              ├─ Landing Page (10.20.30.40)
              ├─ Jellyfin Media Server
              ├─ File Shares (SMB/CIFS)
              └─ Container Management
```

**IP Address Scheme:**
- **OpenWRT Router**: `10.20.30.1`
- **Landing Page**: `10.20.30.40`
- **DHCP Range**: `10.20.30.100-250`
- **Host Bridge**: `10.20.30.254`

## 🔧 Management Commands

```bash
# Check system status
./status.sh

# Start/restart services
./startup.sh

# View service logs
./logs.sh [service-name]

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

## 📁 Directory Structure

```
Prepper-Pi/
├── docker-compose.yml      # Main service definitions
├── first-run-setup.sh      # Automated setup script
├── startup.sh             # Service startup script
├── cleanup.sh             # Complete removal script
├── openwrt/               # OpenWRT configuration
│   └── config/            # Network, wireless, firewall configs
├── homepage/              # Landing page configuration
├── media/                 # Media files for Jellyfin
│   ├── movies/
│   ├── tv-shows/
│   └── music/
└── shares/                # Public file shares
    ├── public/
    └── documents/
```

## 🔐 Security Considerations

- **Open WiFi**: Default setup uses open network for accessibility
- **Local Network**: Services only accessible on local network
- **Firewall**: OpenWRT provides routing and firewall protection
- **Container Isolation**: Each service runs in isolated Docker container

### 🔒 Hardening (Optional)
```bash
# Add WPA2 security to WiFi
# Edit: openwrt/config/wireless
option encryption 'psk2'
option key 'your-password-here'
```

## 🚨 Troubleshooting

### Common Issues

**OpenWRT won't start:**
```bash
# Check macvlan network
docker network ls | grep openwrt
./setup-macvlan.sh

# Check logs
./logs.sh openwrt
```

**WiFi hotspot not broadcasting:**
```bash
# Check USB WiFi adapter
lsusb | grep -i wireless
iwconfig

# Check OpenWRT wireless config
docker exec openwrt uci show wireless
```

**Services not accessible:**
```bash
# Check network bridge
ip addr show macvlan-host

# Restart network setup
sudo ./setup-host-bridge.sh
```

### Network Interface Issues
```bash
# Auto-detect interface
ip route | grep default

# Manually set interface in docker-compose.yml
# Change "parent: eth0" to your interface name
```

## 🛣️ Roadmap

### Phase 1 ✅ (Current)
- [x] Docker-based service architecture
- [x] OpenWRT router functionality
- [x] Basic WiFi hotspot
- [x] Media streaming (Jellyfin)
- [x] File sharing (Samba)
- [x] Web dashboard

### Phase 2 🚧 (In Progress)
- [ ] Captive portal integration
- [ ] RTL-SDR radio interface
- [ ] USB TV tuner support
- [ ] Offline Wikipedia/maps
- [ ] Enhanced WiFi management

### Phase 3 🔮 (Planned)
- [ ] Local LLM integration
- [ ] Mesh networking
- [ ] IoT device management
- [ ] Mobile app companion
- [ ] Automated failover

## 🙏 Acknowledgments

- **OpenWRT Project** - For the excellent router firmware
- **Paul MacKinnon** - For the original Docker macvlan guide
- **Jellyfin Team** - For the amazing media server
- **Portainer** - For container management UI
- **Raspberry Pi Foundation** - For the incredible hardware

---

**Personal project for emergency preparedness and off-grid scenarios**

*"Be prepared, stay connected, even when disconnected."*
