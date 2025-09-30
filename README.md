# 🥧 Prepper Pi

**A comprehensive off-grid communication and media platform with solar power, LoRa m### 📺 Concurrent Operations
- **Two TV channels** streaming simultaneously via dual ATSC tuner
- **Two radio stations** (FM + NOAA) streaming via dual RTL-SDR setup
- **LoRa mesh messaging** with text and GPS location sharing
- **WiFi hotspot** serving multiple devices with captive portal
- **Media streaming** from local Jellyfin library
- **File sharing** via Samba network shares
- **Solar power monitoring** via Victron SmartSolar Bluetooth interface
- **Real-time emergency broadcasts** (NOAA weather alerts, EAS)

### 🔋 Power Management
- **Solar charging** with MPPT optimization and battery monitoring
- **12V LiFePO₄ storage** for extended off-grid operation
- **Regulated power rails** for stable RF and compute performance
- **Fused distribution** with overcurrent protection on all branches
- **Low-power modes** for extended runtime during poor solar conditions

## 🛠️ Hardware Assembly

### 📐 System Construction
1. **Enclosure Preparation**: Install metal partition between power and RF compartments
2. **Power System**: Mount battery, MPPT controller, and DC distribution panel
3. **RF Installation**: Install bulkhead connectors, distribution amp, and arrestors
4. **Compute Setup**: Mount Pi 5 with cooling, connect USB devices and network interfaces
5. **Antenna Mounting**: Install TV and LoRa antennas with proper grounding
6. **Integration Testing**: Verify all systems before field deployment

*See `wiring.md` for detailed component layout and connection diagrams.*

## 🚀 Software Setup

### 🛠 Automated Installation

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash first-run-setup.sh
```

### 🧹 System Removal

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash cleanup.sh && cd .. && rm -rf Prepper-Pi
```

## 📖 Configuration Stepsrrent Operationssh, TV/radio reception, and WiFi hotspot capabilities.**

Prepper Pi is a complete field-deployable system combining solar power, over-the-air TV/radio reception, LoRa mesh networking, WiFi hotspot, and media services in a weatherproof enclosure - designed for emergency preparedness, off-grid living, and remote communication scenarios.

## ✨ Core Features

### 🌐 Communications & Networking
- **WiFi Hotspot**: Dual-band (2.4/5GHz) access point with captive portal
- **LoRa Mesh**: Meshtastic-based long-range text and location sharing
- **Network Management**: OpenWRT router with firewall, DHCP, and routing
- **Internet Gateway**: Automatic failover between available connections

### 📺 Broadcast Reception & Media
- **Dual TV Tuning**: Simultaneous reception of two OTA ATSC channels via Tvheadend
- **Dual Radio Reception**: FM broadcast streams and NOAA weather radio via RTL-SDR
- **Media Streaming**: Jellyfin server for stored movies, TV shows, and music
- **Live Broadcasting**: Real-time TV and radio streaming to connected devices

### 📱 Web Services & Management
- **Landing Page**: Unified dashboard with all services and emergency resources
- **Container Management**: Portainer for Docker service administration
- **File Sharing**: Samba/CIFS network shares for device file access
- **System Monitoring**: Real-time power, RF, and system status

### ⚡ Power & Infrastructure
- **Solar UPS**: Complete 12V LiFePO₄ battery system with MPPT charge controller
- **Power Management**: Regulated supplies for all RF and compute components
- **Lightning Protection**: Grounding and arrestor systems for RF safety
- **Weatherproof Design**: Portable field-deployable enclosure

## 📋 Required Hardware Components

### 🧠 Compute Platform
- **Raspberry Pi 5** (8GB RAM) with official 27W USB-C PSU
- **Pi 5 Active Cooler** for thermal management under load
- **NVMe Storage** (512GB M.2 via Pi M.2 HAT+) for fast Docker volumes
- **Case & Mounting** hardware for secure installation

### � TV Reception System (75Ω Path)
- **OTA Antenna**: Antennas Direct ClearStream 2MAX (VHF-Hi/UHF) or equivalent
- **Mast Preamp**: Channel Master CM-7777HD with FM trap and LTE filtering
- **Power Inserter**: 12-15V DC injection for preamp power
- **Distribution Amp**: Channel Master CM-3414 (4-port, +8dB/port)
- **TV Tuner**: Hauppauge WinTV-dualHD (USB dual ATSC tuner)
- **Lightning Protection**: 75Ω F-F coax arrestor and ground block

### 📻 Radio Reception System (50Ω Path)
- **RTL-SDR Dongles**: 2x RTL-SDR Blog V4 for concurrent FM and NOAA reception
- **FM Notch Filter**: 88-108MHz band-stop filter for NOAA leg interference
- **RF Adapters**: F-female to SMA-male pigtails for SDR connections
- **Attenuators**: 3-10dB inline pads for overload protection as needed

### 📡 LoRa Mesh Communication
- **LoRa Radio**: SX1262-based HAT or USB module (915MHz US ISM band)
- **LoRa Antenna**: 915MHz omnidirectional on mast with LMR-240/400 jumpers
- **Handheld Nodes**: 1-2 LILYGO T-Beam or equivalent for phone BLE pairing
- **Mesh Software**: meshtasticd with Web UI and optional MQTT integration

### ⚡ Solar Power System
- **Battery**: 12V LiFePO₄ (40-100Ah capacity based on runtime requirements)
- **Charge Controller**: Victron SmartSolar MPPT 75/15 with Bluetooth monitoring
- **Solar Panel**: 100-150W monocrystalline with MC4 connectors
- **Power Regulation**: 12→5V/5A buck converter for Pi, 13.2V regulator for RF amps
- **Distribution**: Fused DC panel with Powerpole/XT60 connectors and master disconnect

### 🏗️ Enclosure & Infrastructure
- **Weather Case**: APACHE 2800 / Pelican 1200 class weatherproof enclosure
- **Bulkhead Fittings**: MC4 (solar), F-female (TV), SMA/N (RF), gland nuts (data)
- **Metal Partition**: RF isolation between power and signal compartments
- **Grounding System**: Ground rod, bonding straps, and lightning arrestors
- **Cables**: RG-6 quad-shield coax, LMR-240/400 RF cables, proper gauge DC wiring

## 🌐 Network Architecture

```
Solar → MPPT → 12V LiFePO₄ → DC Distribution
                    ↓
        [Power Compartment | RF Compartment]
                    ↓
   Mast: TV Antenna + LoRa Antenna + Preamp
                    ↓
   RF Distribution → Dual TV Tuner + Dual RTL-SDR + LoRa Radio
                    ↓
            Raspberry Pi 5 (OpenWRT + Docker)
                    ↓
   WiFi Hotspot "Prepper Pi" → Connected Devices
   - Tvheadend (Live TV: http://10.20.30.1:9981)
   - Icecast (FM/NOAA: http://10.20.30.1:8000)
   - Meshtastic (Mesh: http://10.20.30.1:8080)
   - Jellyfin (Media: http://10.20.30.1:8096)
   - Landing Page (Portal: http://10.20.30.40)
```

**IP Address Scheme:**
- **OpenWRT Router**: `10.20.30.1`
- **Landing Page**: `10.20.30.40`
- **DHCP Range**: `10.20.30.100-250`
- **Host Bridge**: `10.20.30.254`

## 🚀 System Capabilities

### � Concurrent Operations
- **Two TV channels** streaming simultaneously via dual ATSC tuner
- **Two radio stations** (FM + NOAA) streaming via dual RTL-SDR setup
- **LoRa mesh messaging** with text and GPS location sharing
- **WiFi hotspot** serving multiple devices with captive portal
- **Media streaming** from local Jellyfin library
- **File sharing** via Samba network shares
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

## 📖 Configuration Steps

### 1. **Hardware Assembly**
```bash
# Follow wiring.md for complete component installation
# Install solar power system, RF components, and compute platform
# Verify all connections and grounding before power-up
```

### 2. **Software Installation**
```bash
# Update base system
sudo apt update && sudo apt upgrade -y

# Clone repository and run setup
git clone https://github.com/pyrometheous/Prepper-Pi.git
cd Prepper-Pi
sudo bash first-run-setup.sh
```

### 3. **RF System Configuration**
```bash
# Configure TV tuner and RTL-SDR devices
# Set up LoRa radio and Meshtastic mesh networking
# Optimize antenna positions and verify reception
```

### 4. **Access System Services**
- **Landing Page**: `http://prepper-pi.local:3000` or `http://10.20.30.40`
- **Live TV (Tvheadend)**: `http://10.20.30.1:9981`
- **Radio Streams (Icecast)**: `http://10.20.30.1:8000`
- **LoRa Mesh (Meshtastic)**: `http://10.20.30.1:8080`
- **Media Server (Jellyfin)**: `http://10.20.30.1:8096`
- **Router Admin (OpenWRT)**: `http://10.20.30.1`
- **Container Management (Portainer)**: `http://localhost:9000`

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

## 📁 Project Structure

```
Prepper-Pi/
├── docker-compose.yml      # Complete service stack (TV, Radio, LoRa, Media)
├── first-run-setup.sh      # Automated hardware and software setup
├── startup.sh             # Service startup with health checks
├── cleanup.sh             # Complete system removal
├── wiring.md              # Hardware assembly and component diagrams
├── openwrt/               # OpenWRT router configuration
│   └── config/            # Network, wireless, firewall, DHCP configs
├── homepage/              # Landing page dashboard configuration
├── media/                 # Media library for Jellyfin streaming
│   ├── movies/           # Movie collection
│   ├── tv-shows/         # TV series collection
│   ├── music/            # Music library
│   └── recordings/       # OTA TV recordings
└── shares/                # Network file shares
    ├── public/           # Public access files
    ├── documents/        # Document sharing
    └── emergency/        # Emergency resource files
```

## 🔐 Security & Safety

### 🛡️ Network Security
- **Isolated operation**: All services run on isolated local network
- **Container security**: Each service runs in separate Docker container
- **Firewall protection**: OpenWRT provides NAT and filtering
- **Optional WPA2**: Can be enabled for hotspot security when needed

### ⚡ RF & Power Safety
- **Lightning protection**: Coax arrestors and proper grounding
- **Overcurrent protection**: Fused distribution on all power circuits
- **ISM compliance**: LoRa transmission within legal limits
- **EMI mitigation**: Proper cable routing and ferrite cores

### 🔒 Access Control (Optional)
```bash
# Enable WPA2 security for WiFi hotspot
# Edit: openwrt/config/wireless
option encryption 'psk2'
option key 'your-secure-password'
```

## 🛠️ System Management

## �️ System Management

### 🔧 Control Commands
```bash
# System status and health checks
./status.sh

# Start/restart all services
./startup.sh

# View service logs (specify service name)
./logs.sh [tvheadend|icecast|meshtasticd|jellyfin|openwrt]

# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# Restart specific service
docker-compose restart [service-name]
```

### 📊 System Monitoring
```bash
# Check battery and solar status (if Victron connected)
victron-status.sh

# Monitor RF signal levels
rtl_power -f 88M:108M:1M    # FM band scan
rtl_power -f 162M:163M:1k   # NOAA weather frequencies

# Check LoRa mesh status
curl http://10.20.30.1:8080/api/v1/nodes
```

### 🔄 Maintenance Tasks
```bash
# Update container images
docker-compose pull && docker-compose up -d

# Backup configuration
tar -czf prepper-pi-backup.tar.gz openwrt/ homepage/ media/ shares/

# Clean up old recordings
find media/recordings -name "*.ts" -mtime +30 -delete
```

## �🚨 Troubleshooting

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

## 🛣️ System Development

**Status Legend:**
- 🟢 **Tested & Working** - Deployed and verified in field conditions
- 🟡 **Code Complete** - Implementation finished, awaiting testing
- 🟠 **In Development** - Actively being coded/configured
- ⚪ **Planned** - Not yet started
- 🔴 **Blocked** - Waiting on hardware/dependencies

### Phase 1 🟡 (Core Infrastructure - Code Complete, Needs Testing)
- [🟡] Solar power system with LiFePO₄ battery and MPPT charging
- [🟡] Dual TV tuner with OTA broadcast reception and Tvheadend
- [🟡] Dual RTL-SDR setup for FM and NOAA weather radio streams
- [🟡] LoRa mesh networking with Meshtastic integration
- [🟡] OpenWRT WiFi hotspot with captive portal landing page
- [🟡] Weatherproof enclosure with RF/power compartment isolation
- [🟡] Complete Docker service stack (TV, Radio, Media, Mesh)

### Phase 2 � (Enhanced Features - Mixed Development Status)
- [⚪] Advanced power management with low-power sleep modes
- [⚪] Automated TV recording scheduler with conflict resolution
- [⚪] Enhanced LoRa mesh routing and message relay capabilities
- [⚪] Offline emergency resource database (first aid, survival guides)
- [🟠] Mobile-optimized web interfaces for phone/tablet access
- [⚪] RF signal analysis and automatic antenna tuning

### Phase 3 ⚪ (Future Enhancements - Planning Stage)
- [⚪] Satellite communication integration (Starlink/Iridium backup)
- [⚪] AI-powered content recommendation and emergency alert processing
- [⚪] Multi-site mesh networking with automatic failover routing
- [⚪] Integration with amateur radio digital modes (FT8, VARA)
- [⚪] Environmental sensor network (weather, radiation, air quality)
- [⚪] Blockchain-based mesh messaging for censorship resistance

### 🔬 Testing Priorities
1. **Hardware Integration** - Verify all RF components work together without interference
2. **Power System** - Test solar charging, battery life, and load management
3. **LoRa Range Testing** - Establish actual mesh communication distances
4. **TV Reception** - Validate dual tuner performance with local broadcast signals
5. **Weather Deployment** - Field test weatherproof enclosure and grounding
6. **Load Testing** - Verify system stability under maximum concurrent usage

## 🙏 Acknowledgments

- **[OpenWRT Project](https://openwrt.org/)** - Router firmware and network management
- **[Tvheadend Team](https://tvheadend.org/)** - Professional TV backend software
- **[Meshtastic Project](https://meshtastic.org/)** - LoRa mesh networking protocol
- **[RTL-SDR Community](https://www.rtl-sdr.com/)** - Software-defined radio ecosystem
- **[Jellyfin Team](https://jellyfin.org/)** - Open-source media server platform
- **[Victron Energy](https://www.victronenergy.com/)** - Solar charge controller and monitoring
- **[Raspberry Pi Foundation](https://www.raspberrypi.org/)** - Single-board computer platform

---

**Comprehensive off-grid communication and media platform**

*"Stay informed, stay connected, stay prepared."*
