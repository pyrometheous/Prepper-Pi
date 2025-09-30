# 🥧 Prepper Pi

> **⚠️ DISCLAIMER: This is a personal project in early development. No support is provided, and functionality is not guaranteed. Use at your own risk.**

**A comprehensive off-grid communication and media platform with solar power, LoRa mesh, TV/radio reception, and WiFi hotspot capabilities.**

Prepper Pi is a complete field-deployable system combining solar power, over-the-air TV/radio reception, LoRa mesh networking, WiFi hotspot, and media services in a weatherproof enclosure - designed for emergency preparedness, off-grid living, and remote communication scenarios.

## ✨ Core Features

### 📺 Concurrent Operations
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

### 🏗️ System Construction
1. **Enclosure Preparation**: Install metal partition between power and RF compartments
2. **Power System**: Mount battery, MPPT controller, and DC distribution panel
3. **RF Installation**: Install bulkhead connectors, distribution amp, and arrestors
4. **Compute Setup**: Mount Pi 5 with cooling, connect USB devices and network interfaces
5. **Antenna Mounting**: Install TV and LoRa antennas with proper grounding
6. **Integration Testing**: Verify all systems before field deployment

*See [wiring.md](wiring.md) for detailed component layout and connection diagrams.*

## 🖥️ Software Setup

### ⚡ Automated Installation

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash first-run-setup.sh
```

### 🗑️ System Removal

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash cleanup.sh && cd .. && rm -rf Prepper-Pi
```

## ⚙️ Configuration Steps

### 1. 🌐 Network Configuration
```bash
# Access OpenWRT admin interface
http://10.20.30.1:8080

# Default credentials
Username: root
Password: (blank)
```

### 2. 📊 Services Dashboard
```bash
# Landing page with all service links
http://10.20.30.40

# Individual service access
Jellyfin: http://10.20.30.40:8096
Portainer: http://10.20.30.40:9000
Samba: \\10.20.30.40
```

### 3. 📺 TV Configuration
```bash
# Tvheadend web interface
http://10.20.30.40:9981

# Initial setup
1. Configure tuners and scan for channels
2. Set up recording profiles
3. Create user accounts for streaming access
```

### 4. 📻 Radio Configuration
```bash
# RTL-SDR configuration via SSH
ssh pi@10.20.30.40

# Test radio reception
rtl_fm -f 101.1M -M wbfm -s 200000 -r 48000 | aplay -r 48k -f S16_LE
```

## 🌐 Network Architecture

### 📡 Network Topology
```
Internet/Cellular Modem (optional)
     |
   Router (host network)
     |
RPi5 Ethernet ← macvlan bridge → Docker Services
                      |
               OpenWRT Container
              (10.20.30.1 gateway)
                      |
                WiFi Access Point
               "Prepper Pi" SSID
                      |
           Client devices (10.20.30.100-199)
```

### 🔗 Port Mappings
| Service | Internal Port | External Access |
|---------|---------------|-----------------|
| OpenWRT Web UI | 80 | 10.20.30.1:8080 |
| Landing Page | 80 | 10.20.30.40 |
| Jellyfin | 8096 | 10.20.30.40:8096 |
| Portainer | 9000 | 10.20.30.40:9000 |
| Tvheadend | 9981 | 10.20.30.40:9981 |
| Samba/CIFS | 445 | \\10.20.30.40 |

## 📋 Hardware Requirements

### 🖥️ Base Requirements (Currently Owned)
- **Raspberry Pi 5** (8GB) with adequate cooling solution
- **NVMe SSD** (1TB+) for media storage and OS performance
- **USB WiFi Adapter** for external antenna capability
- **MicroSD Card** (32GB+) for initial boot and backup

### 📡 RF Communications (Future Hardware)
- **Dual RTL-SDR Dongles** for FM radio and NOAA weather reception
- **Dual TV Tuner** USB devices for OTA broadcast reception
- **LoRa Radio Modules** for mesh networking capability
- **Antenna System** with proper impedance matching and grounding

### 🔋 Power Systems (Future Hardware)
- **100W Solar Panel** with MPPT charge controller
- **100Ah LiFePO₄ Battery** with integrated BMS protection
- **DC Distribution Panel** with fusing and monitoring
- **Power Monitoring** system with low-voltage disconnect

### 🏠 Enclosure & Protection (Future Hardware)
- **Weatherproof Enclosure** (IP65 rated) with ventilation
- **Lightning Protection** with proper grounding system
- **RF Filters** and isolation for clean signal paths
- **Thermal Management** for extended operation in heat

## 🛣️ System Development

**Status Legend:**
- ✅ **Tested & Working** - Deployed and verified in field conditions
- ⭐ **Code Complete** - Implementation finished, awaiting testing
- 🔄 **In Development** - Actively being coded/configured
- 📋 **Planned** - Not yet started
- ❌ **Blocked** - Waiting on hardware/dependencies

### Phase 1: Basic WiFi Infrastructure
- [⭐] Raspberry Pi 5 setup with adequate cooling and NVMe storage
- [⭐] Docker Compose service stack (OpenWRT, Portainer, Homepage)
- [⭐] Basic WiFi hotspot using external USB WiFi adapter
- [⭐] Landing page with captive portal and service links
- [📋] Initial testing with indoor WiFi coverage and basic connectivity

### Phase 2: Emergency Resources & AI
- [📋] Offline emergency resource database (first aid, survival guides)
- [📋] Local LLM deployment for emergency consultation and guidance
- [📋] Emergency communication protocols and documentation
- [📋] Offline Wikipedia and essential reference materials
- [📋] Testing AI response quality and resource accessibility

### Phase 3: Media Server & Storage
- [📋] Jellyfin media server configuration and optimization
- [📋] Media library organization on NVMe SSD storage
- [📋] File sharing with Samba for local network access
- [📋] Mobile-optimized interfaces for media streaming
- [📋] Performance testing with multiple concurrent streams

### Phase 4: TV & Radio Reception (Acquire Hardware)
- [❌] Dual TV tuner USB devices for OTA broadcast reception
- [❌] Dual RTL-SDR dongles for FM radio and NOAA weather reception
- [❌] Antenna system design and RF signal optimization
- [❌] Tvheadend configuration and emergency broadcast monitoring
- [❌] Integration testing with existing Docker services

### Phase 5: LoRa Mesh Networking (Acquire Hardware)
- [❌] LoRa radio modules and Meshtastic device integration
- [❌] Mesh network configuration and range testing
- [❌] Emergency messaging and offline communication protocols
- [❌] Multi-node mesh deployment and routing optimization
- [❌] Integration with emergency resource database

### Phase 6: Solar Power & Enclosure Design
- [❌] Solar panel and charge controller selection and sizing
- [❌] LiFePO4 battery bank integration with power monitoring
- [❌] 3D printed enclosure design (with friend's assistance)
- [❌] Weatherproof housing with proper ventilation and RF access
- [❌] Power management and low-voltage disconnect systems

### Phase 7: Field Testing & Deployment
- [📋] Complete system integration and interference testing
- [📋] Weatherproof enclosure assembly and sealing
- [📋] Field deployment in target environment
- [📋] Long-term reliability testing and performance optimization
- [📋] Documentation of lessons learned and system improvements

### 🔬 Current Testing Priorities (Phase 1)
1. **WiFi Hotspot Performance** - Measure coverage area and connection stability
2. **Landing Page Functionality** - Test captive portal and service accessibility
3. **Docker Service Stack** - Verify OpenWRT, Portainer, and Homepage stability
4. **Raspberry Pi 5 Performance** - Monitor cooling and NVMe performance under load
5. **Network Configuration** - Validate OpenWRT routing and basic connectivity
6. **Power Consumption Baseline** - Measure current usage before adding hardware

## 🙏 Acknowledgments

- **[OpenWRT Project](https://openwrt.org/)** - Router firmware and network management
- **[Paul MacKinnon](https://github.com/paulmackinnon)** - For the original [Docker macvlan guide](https://paul-mackinnon.medium.com/openwrt-raspberry-pi-docker-vlan-project-9cb1db10684c)
- **[Tvheadend Team](https://tvheadend.org/)** - Professional TV backend software
- **[Meshtastic Project](https://meshtastic.org/)** - LoRa mesh networking protocol
- **[RTL-SDR Community](https://www.rtl-sdr.com/)** - Software-defined radio ecosystem
- **[Jellyfin Team](https://jellyfin.org/)** - Open-source media server platform
- **[Victron Energy](https://www.victronenergy.com/)** - Solar charge controller and monitoring
- **[Raspberry Pi Foundation](https://www.raspberrypi.org/)** - Single-board computer platform

---

**Comprehensive off-grid communication and media platform**