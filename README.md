# 🥧 Prepper Pi

> **⚠️ DISCLAIMER: This is a personal project in early development. No support is provided, and functionality is not guaranteed. Use at your own risk.**

**A comprehensive off-grid communication and media platform with solar power, LoRa mesh, TV/radio reception, and WiFi hotspot capabilities.**

Prepper Pi is a complete field-deployable system combining solar power, over-the-air TV/radio reception, LoRa mesh networking, WiFi hotspot, and media services in a weatherproof enclosure - designed for emergency preparedness, off-grid living, and remote communication scenarios.

## ✨ Core Features

### 📺 Concurrent Operations
- **Two TV channels** streaming simultaneously via dual ATSC tuner
- **Two radio stations** (FM + NOAA) streaming via dual RTL-SDR setup
- **LoRa mesh messaging** with text and GPS location sharing
- **WiFi hotspot** serving multiple devices with WPA2 security and captive portal
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

*See [docs/wiring.md](docs/wiring.md) for detailed component layout and connection diagrams.*

## � Documentation

### 📖 Complete Documentation
- **[📝 Documentation Index](docs/README.md)** - Overview of all technical documentation
- **[🔧 Components & BOM](docs/components.md)** - Complete parts list with specifications and phases  
- **[⚡ Wiring & Assembly](docs/wiring.md)** - Electrical specifications, diagrams, and safety guidelines
- **[📡 WiFi Testing Protocol](docs/wifi-testing.md)** - Hardware validation guide for AP functionality

## �🖥️ Software Setup

### ⚡ Automated Installation

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash first-run-setup.sh
```

**On Raspberry Pi:** `cp docker-compose.pi.yml docker-compose.override.yml` before `docker compose up -d`.

### 🗑️ System Removal

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash cleanup.sh && cd .. && rm -rf Prepper-Pi
```

## ⚙️ Configuration Steps

### 🚦 Feature Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| **Phase 1: Core Infrastructure** | | |
| Docker Service Stack | ✅ **Implemented** | OpenWRT, Portainer, Homepage, Jellyfin, Samba |
| WiFi Access Point | ⚠️ **Experimental** | Bootstrap generates config on first boot, then applies WPA2 |
| Captive Portal | ⚠️ **Experimental** | OpenNDS configured, needs end-to-end testing |
| Landing Page | ✅ **Implemented** | Homepage dashboard with service links |
| **Phase 4: TV & Radio** | | |
| TV Reception (ATSC) | 📋 **Planned** | Tvheadend service template ready |
| FM Radio Streaming | 📋 **Planned** | RTL-SDR + Icecast template ready |
| NOAA Weather Radio | 📋 **Planned** | RTL-SDR + Icecast template ready |
| **Phase 5: LoRa Mesh** | | |
| Mesh Networking | 📋 **Planned** | Meshtastic service template ready |
| **Phase 6: Solar Power** | | |
| Solar Charging | 📋 **Planned** | Hardware design phase |
| Power Monitoring | 📋 **Planned** | Victron integration planned |

**Status Legend:**
- ✅ **Implemented** - Tested and working
- ⚠️ **Experimental** - Configured but needs hardware validation  
- 📋 **Planned** - Service templates ready, hardware needed

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
http://10.20.30.40:3000

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
RPi5 Ethernet ← host networking → OpenWRT Container
                      |                     |
               Docker Bridge         WiFi Access Point
              (172.20.0.0/16)        "Prepper Pi" SSID
                      |              (10.20.30.0/24)
               Container Services            |
              (Jellyfin, Portainer)   Client devices
                                    (10.20.30.100-199)
```

### 🔗 Service Access
| Service | Local Domain | IP Address | Port |
|---------|--------------|------------|------|
| Landing Page | prepper-pi.local | 10.20.30.40 | 3000 |
| OpenWRT Web UI | openwrt.local | 10.20.30.1 | 80 |
| Jellyfin Media Server | jellyfin.local | 10.20.30.40 | 8096 |
| Portainer Management | portainer.local | 10.20.30.40 | 9000 |
| Traefik Dashboard | - | 10.20.30.40 | 8080 |
| Tvheadend | - | 10.20.30.40 | 9981 |
| Samba/CIFS | - | \\10.20.30.40 | 445 |

*Note: Local domains work when connected to the Prepper Pi WiFi network. Traefik provides reverse proxy functionality for clean URLs.*

## 📋 Hardware Requirements

> **📝 Complete Components List:** See [docs/components.md](docs/components.md) for detailed specifications, part numbers, and development phase status.

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
- [🔄] **WiFi hotspot configuration** - *Docker setup exists but requires hardware testing*
- [⭐] Landing page with captive portal and service links
- [�] **Hardware integration testing** - *Network configuration needs validation on real Pi*

**Current Limitation:** WiFi AP functionality exists in configuration but has not been tested on actual Raspberry Pi hardware. Docker OpenWRT setup may require additional device mounts and host networking mode for reliable AP operation.

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
1. **WiFi AP Hardware Validation** - Test OpenWRT container AP mode on actual Pi 5 hardware
2. **Device Mount Configuration** - Verify USB WiFi device passthrough to container  
3. **Network Mode Testing** - Compare macvlan vs host networking for AP reliability
4. **Landing Page Functionality** - Test captive portal and service accessibility
5. **Docker Service Stack** - Verify OpenWRT, Portainer, and Homepage stability
6. **Power Consumption Baseline** - Measure current usage before adding hardware

**⚠️ Important:** WiFi AP functionality is configured but not yet hardware-tested. Real-world deployment requires validation on Raspberry Pi with USB WiFi adapter.

### 🧪 Smoke Test Validation

**You should be able to:**
1. Connect to "Prepper Pi" SSID with password `PrepperPi2024!`
2. Get DHCP address from OpenWRT container (10.20.30.x range)
3. Be redirected to landing page (http://10.20.30.40:3000) via captive portal
4. Access OpenWRT admin interface at http://10.20.30.1
5. Open Jellyfin media server at http://10.20.30.40:8096
6. Access Portainer management at http://10.20.30.40:9000
7. Future: Tvheadend TV backend at http://10.20.30.40:9981 (Phase 4)
8. Future: Meshtastic Web UI at http://10.20.30.40:2443 (Phase 5)

**Validation Script:** Run `./verify-ap.sh` to check AP configuration and device mapping.

**Manual Client Tests:**
```bash
# Test DNS resolution (should work from connected client)
nslookup example.com 10.20.30.1

# Test captive portal redirect (should return 302/303 redirect)
curl -I http://neverssl.com/ | head -n 5
```

**Success Indicators:**
- `iw list` shows AP in "Supported interface modes"
- `iw dev` lists wlan* interfaces; `wifi status` shows SSIDs
- `logread` shows dnsmasq DHCPACK lines when clients connect
- DNS queries to 10.20.30.1 return responses
- HTTP requests redirect to http://10.20.30.40:3000/ until portal accepted

## ⚠️ Configuration Status & Testing Needed

**Phase 1 WiFi AP Configuration:**
- ✅ **Fixed:** Docker OpenWRT now uses `host` networking mode for proper radio access
- ✅ **Fixed:** USB WiFi device passthrough configured with `/dev/bus/usb` mount
- ✅ **Fixed:** Firmware and driver access via `/lib/firmware` and `/sys/class/ieee80211` mounts  
- ✅ **Fixed:** OpenNDS captive portal configured to redirect to landing page
- ✅ **Fixed:** Default WiFi security upgraded to WPA2 (open mode available for emergencies)

**Hardware Testing Required:**
1. Validate USB WiFi adapter compatibility with Pi 5 and container access
2. Test OpenWRT wireless driver initialization and AP mode activation  
3. Verify captive portal redirect functionality end-to-end
4. Confirm DHCP assignment and client connectivity (10.20.30.0/24 range)
5. Test service accessibility through landing page

**If OpenWRT image fails on Pi:** Use `docker-compose.pi.yml` for ARM64-specific image.

**Run Verification:** Use `./verify-ap.sh` to validate configuration before field deployment.

These improvements address the audit findings. Phase 1 is now properly configured for hardware testing.

### ✅ Quick Setup Checklist

**Before Hardware Testing:**
- [ ] Raspberry Pi 5 with adequate cooling
- [ ] USB WiFi adapter compatible with hostapd/nl80211
- [ ] NVMe SSD mounted and accessible
- [ ] Docker and Docker Compose installed

**Configuration Validation:**
- [ ] `docker compose up -d` starts all services without errors
- [ ] `./verify-ap.sh` shows ARM64 OpenWRT image loads successfully
- [ ] `iw list` inside container shows WiFi device with AP mode support
- [ ] `iw dev` lists wlan* interfaces and `wifi status` shows SSIDs
- [ ] OpenNDS service starts and configures captive portal
- [ ] DHCP assigns addresses in 10.20.30.0/24 range

**Client Testing:**
- [ ] "Prepper Pi" SSID broadcasts and accepts WPA2 connections
- [ ] Captive portal redirects to http://10.20.30.40:3000/ landing page
- [ ] All services accessible through landing page links
- [ ] `nslookup example.com 10.20.30.1` returns DNS response
- [ ] `curl -I http://neverssl.com/` returns HTTP 302/303 redirect
- [ ] `logread` shows dnsmasq DHCPACK entries for connected clients

**Future Hardware Ready:**
- [ ] Tvheadend service template ready (uncomment when TV tuner added)
- [ ] RTL-SDR radio streaming templates ready (uncomment when dongles added)  
- [ ] Meshtastic service template ready (uncomment when LoRa hardware added)

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