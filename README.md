<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# 🥧 Prepper Pi

> **⚠️ DISCLAIMER:** Personal project, early development. No warranties or support. Use at your own risk.

## 📄 License, Trademarks & Commercial Use

**Project code:** **Prepper Pi Noncommercial License (PP-NC-1.0)** (see `LICENSE`).  
**Docs & media:** **CC BY-NC 4.0** (see `LICENSE-DOCS`).  
**Third-party software:** Licensed under their own FOSS licenses. See `licenses/THIRD_PARTY_NOTICES.md`.  
**GPL/LGPL source:** We publish the Corresponding Source **in the matching GitHub Release** for any image/binary we ship. See `licenses/SOURCE-OFFER.md`.
**Project code license:** see `LICENSE` (PP-NC-1.0).  
**Documentation/media license:** see `LICENSE-DOCS` (CC BY-NC 4.0).

**Commercial hardware sales (preconfigured devices):** Allowed **only** under a separate commercial license with revenue share. See `COMMERCIAL-LICENSE.md` and contact **pyrometheous**.

**Trademarks:** "Prepper Pi" name/logo are not covered by the software licenses. See `TRADEMARKS.md`. Do **not** market third-party marks (e.g., Meshtastic, OpenWrt, Raspberry Pi, Jellyfin) as product branding without their owners' permissions.

**No copyrighted media included:** Devices ship **without** copyrighted content. Users are responsible for lawful use of media and RF features.

**Codecs/patents note:** FFmpeg and certain codecs (e.g., H.264/AVC, HEVC, AAC) may be patent-encumbered in some regions. This project does not grant patent licenses. Where required, ship legal codecs from your OS vendor and let end-users enable optional encoders themselves.

> **Note:** If a matching GitHub Release isn't published yet for a given image/binary, use the repository source at the tagged commit. Once a formal Release is cut, the corresponding source will be attached to that Release.

---

**A comprehensive off-grid communication and media platform with solar power, dual LoRa mesh protocols, TV/radio reception, and WiFi hotspot capabilities.**

## ✨ Core Features

> **📋 Note:** The following features represent the planned capabilities of Prepper Pi. Phase 1 (WiFi infrastructure) is configured but requires hardware testing. Later phases require additional hardware acquisition.

### 📺 Concurrent Operations
- Two ATSC TV channels via dual tuner
- Two radio stations (FM + NOAA) via dual RTL-SDR
- Dual LoRa meshes (Meshtastic + MeshCore)
- Captive-portal Wi-Fi hotspot
- Jellyfin media streaming
- Kavita ebook server
- Samba file sharing
- Solar monitoring (Victron SmartSolar)
- Real-time NOAA/EAS alerts

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

## 📚 Documentation

### 📖 Complete Documentation
- **[📝 Documentation Index](docs/README.md)** - Overview of all technical documentation
- **[🔧 Components & BOM](docs/components.md)** - Complete parts list with specifications and phases  
- **[⚡ Wiring & Assembly](docs/wiring.md)** - Electrical specifications, diagrams, and safety guidelines
- **[📡 WiFi Testing Protocol](docs/wifi-testing.md)** - Hardware validation guide for AP functionality

## 🔧 Software Setup

### ⚡ Automated Installation

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git \
  && cd Prepper-Pi && sudo bash first-run-setup.sh
```

**On Raspberry Pi:** `cp docker-compose.pi.yml docker-compose.override.yml` before `docker compose up -d`.

### 🗑️ System Removal

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash cleanup.sh && cd .. && rm -rf Prepper-Pi
```

## 🔒 Security Hardening (do this before field use)
1. **Change all defaults** (OpenWrt root password, Wi-Fi SSID/passphrase, disable passwordless logins).
2. **Enable HTTPS** on admin interfaces; restrict management to wired or trusted VLAN.
3. **Rotate API keys/secrets** for any services you enable (Jellyfin, Portainer CE).
4. **Update & lock** package versions; rebuild images with `scripts/build-manifest.sh` to record digests.
5. **Back up** `/etc/prepper-pi/VERSION` and the full `MANIFEST.txt` with each release.

## ⚙️ Service Access & Configuration

### 🌐 Network Access
- **Default Gateway (example):** `10.20.30.1` (OpenWrt admin interface)
- **Initial Credentials (example):** username: `root`, password: *(set on first boot)*
- **Wi-Fi Network (example):** SSID "Prepper Pi", password `ChangeMeNow!`  ← update during setup
- **DHCP Range:** 10.20.30.100-199 for client devices

### 📊 Service URLs
| Service | URL | Status | Notes |
|---------|-----|--------|-------|
| Landing Page | http://10.20.30.1 | ⚠️ **Experimental** | Captive portal redirect |
| Jellyfin | http://10.20.30.1:8096 | ⚠️ **Experimental** | Media server |
| Portainer | http://10.20.30.1:9000 | ⚠️ **Experimental** | Container management *(Community Edition)* |
| Tvheadend | http://10.20.30.1:9981 | 📋 **Planned** | TV backend (Phase 4) |
| Meshtastic | http://10.20.30.1:2443 | 📋 **Planned** | LoRa mesh A (Phase 5) |
| MeshCore | http://10.20.30.1:2444 | 📋 **Planned** | LoRa mesh B (Phase 5) |
| Samba | \\\\10.20.30.1 | 📋 **Planned** | File sharing (Phase 3) |

**Status Legend:**
- ✅ **Implemented** - Tested and working
- ⚠️ **Experimental** - Configured but needs hardware validation  
- 📋 **Planned** - Service templates ready, hardware needed

## 🌐 Network Architecture

### 📡 Network Topology
```
Internet/Cellular Modem (optional)
     |
   Router (host network)
     |
RPi5 Ethernet ← host networking → OpenWrt Container
                      |                     |
               Docker Bridge         WiFi Access Point
              (172.20.0.0/16)        "Prepper Pi" SSID
                      |              (10.20.30.0/24)
               Container Services            |
              (Jellyfin, Portainer)   Client devices
                                    (10.20.30.100-199)
```

### 🔗 Service Access Table
*All services accessible via the unified 10.20.30.1 IP address with port-specific access as listed above. Captive portal redirects new connections to the landing page.*

## 📋 Hardware Requirements

> **📝 Complete Components List:** See [docs/components.md](docs/components.md) for detailed specifications, part numbers, and development phase status.

### 🖥️ Base Requirements (Currently Owned)
- **Raspberry Pi 5** (8GB) with adequate cooling solution
- **NVMe SSD** (1TB+) for media storage and OS performance
- **ALFA Network AWUS036ACM** - Long-range dual-band AC1200 USB WiFi adapter with external antenna
- **MicroSD Card** (32GB+) for initial boot and backup

### 📡 RF Communications (Future Hardware)
- **Dual RTL-SDR Dongles** for FM radio and NOAA weather reception
- **Dual TV Tuner** USB devices for OTA broadcast reception
- **Dual LoRa Radio Modules** for Meshtastic and MeshCore mesh networking
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

## 🛣️ Development Roadmap

**Status Legend:**
- ✅ **Tested & Working** - Deployed and verified in field conditions
- ⭐ **Code Complete** - Implementation finished, awaiting testing
- 🔄 **In Development** - Actively being coded/configured
- 📋 **Planned** - Not yet started
- ❌ **Blocked** - Waiting on hardware/dependencies

### Phase 1: Basic WiFi Infrastructure
- [✅] Raspberry Pi 5 setup with adequate cooling and NVMe storage
- [⭐] **Docker Compose service stack** - *Configuration complete, awaiting hardware testing*
- [⭐] **WiFi hotspot configuration** - *Complete with host networking, DNAT redirects, and captive portal*
- [⭐] **Landing page with captive portal** - *Service templates ready, needs hardware validation*
- [🔄] **Hardware integration testing** - *Ready for validation on actual Pi hardware*

**Current Status:** All WiFi AP functionality is properly configured with host networking mode, firewall4/nftables DNAT redirects, and unified service URLs. The system uses router IP (10.20.30.1) for all services with proper port forwarding to host containers. Configuration is complete but requires hardware testing to validate Docker stack, WiFi AP functionality, and service accessibility.

### Phase 2: Emergency Resources & AI
- [📋] Offline emergency resource database (first aid, survival guides)
- [📋] Local LLM deployment for emergency consultation and guidance
- [📋] Emergency communication protocols and documentation
- [📋] Offline Wikipedia and essential reference materials
- [📋] Testing AI response quality and resource accessibility

### Phase 3: Media Server & Storage
- [📋] Jellyfin media server configuration and optimization
- [📋] Kavita ebook server for digital library management
- [📋] Media library organization on NVMe SSD storage
- [📋] File sharing with Samba for local network access
- [📋] Mobile-optimized interfaces for media streaming and reading
- [📋] Performance testing with multiple concurrent streams

### Phase 4: TV & Radio Reception (Acquire Hardware)
- [❌] Dual TV tuner USB devices for OTA broadcast reception
- [❌] Dual RTL-SDR dongles for FM radio and NOAA weather reception
- [❌] Antenna system design and RF signal optimization
- [❌] Tvheadend configuration and emergency broadcast monitoring
- [❌] Integration testing with existing Docker services

### Phase 5: LoRa Mesh Networking (Acquire Hardware)
- [❌] Dual LoRa radio modules required for Meshtastic and MeshCore integration
- [❌] Mesh network configuration and range testing for both protocols
- [❌] Emergency messaging and offline communication protocols
- [❌] Multi-node mesh deployment and routing optimization
- [❌] Cross-protocol mesh interoperability testing
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

## ✅ Testing & Validation

### 🔬 Phase 1 Testing Priorities
1. **WiFi AP Hardware Validation** - Test OpenWrt container AP mode on actual Pi 5 hardware
2. **Service Connectivity Verification** - Confirm DNAT redirects work for all services (3000/8096/9000)  
3. **Captive Portal End-to-End** - Validate complete portal flow from connection to service access
4. **USB WiFi Device Compatibility** - Test specific adapter models with container passthrough
5. **Docker Service Stack Stability** - Verify all services start reliably and remain accessible
6. **Power Consumption Baseline** - Measure current usage before adding additional hardware

### 🧪 Validation Tests

**Expected Client Experience (example values; change yours in production):**
1. Connect to "Prepper Pi" SSID with password `ChangeMeNow!`
2. Get DHCP address from OpenWrt container (10.20.30.x range)
3. Be redirected to landing page (http://10.20.30.1) via captive portal
4. Access all services through the landing page

**Manual Verification Commands:**
```bash
# Test DNS resolution from connected client
nslookup example.com 10.20.30.1

# Test captive portal redirect (should return 302/303)
curl -I http://neverssl.com/ | head -n 5

# Run configuration verification script
./verify-ap.sh
```

**Success Indicators:**
- `iw list` shows AP mode support
- `iw dev` lists wireless interfaces
- `logread` shows DHCP assignments
- All services accessible via 10.20.30.1

## 🙏 Acknowledgments

**Networking & Router**

* **[OpenWrt Project](https://openwrt.org/)** – Router firmware and network management
* **[dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)** – Lightweight DNS/DHCP server
* **[firewall4 / nftables](https://openwrt.org/docs/guide-user/firewall/firewall_configuration)** – OpenWrt firewall (firewall4/nftables) and packet filtering stack
* **[LuCI](https://github.com/openwrt/luci)** – Web UI for OpenWrt configuration
* **[OpenNDS (GitHub)](https://github.com/openNDS/openNDS) — [OpenNDS](https://opennds.readthedocs.io/en/stable/)** – Captive portal powering splash and status pages
* **[uhttpd](https://openwrt.org/docs/guide-user/services/webserver/uhttpd)** – Embedded web server for portal and status pages

**Dashboards & Ops**

* **[Homepage](https://gethomepage.dev/)** – Lightweight dashboard for the service landing page
* **[Portainer](https://www.portainer.io/)** – Docker container management

**Media & Streaming**

* **[Icecast](https://icecast.org/) + [SoX](https://sourceforge.net/projects/sox/)** – Streaming server and audio toolchain for planned FM/NOAA feeds
* **[Jellyfin](https://jellyfin.org/)** – Open-source media server
* **[Kavita](https://www.kavitareader.com/)** – Self-hosted digital library for ebooks, manga, and comics
* **[LinuxServer.io](https://www.linuxserver.io/)** – High-quality container images for media services
* **[Standard Ebooks](https://standardebooks.org/)** – High-quality public domain literature collection for offline reading
* **[Tvheadend](https://tvheadend.org/)** – TV backend software

**Kindle & Kavita Integration**

* **[WinterBreak (Kindle jailbreak)](https://kindlemodding.org/jailbreaking/WinterBreak/)** – Current, community-maintained jailbreak guide for supported Kindles. Project repo: [KindleModding/WinterBreak](https://github.com/KindleModding/WinterBreak).
* **[Post‑JB: KOReader on Kindle](https://kindlemodding.org/jailbreaking/post-jailbreak/koreader.html)** – KOReader install steps (via KUAL/MRPI) after jailbreaking.
* **[NiLuJe's Jailbreak Hotfix/Bridge](https://www.mobileread.com/forums/showthread.php?t=349767)** – Persists the jailbreak across updates and cleans demo-mode leftovers.
* **[Kavita OPDS Guide](https://wiki.kavitareader.com/guides/features/opds/)** – Enable and copy your user‑specific OPDS URL/key for 3rd‑party readers.
* **[Kavita × KOReader notes](https://wiki.kavitareader.com/guides/3rdparty/koreader/)** – Tips for connecting KOReader to Kavita (nightly KOReader recommended per Kavita docs).
* **Community status threads:** MobileRead's [Kindle Developer's Corner](https://www.mobileread.com/forums/forumdisplay.php?f=150) — key threads:
  - [WinterBreak (intro)](https://www.mobileread.com/forums/showthread.php?t=365372)
  - [Post-update jailbreak recovery / bridge](https://www.mobileread.com/forums/showthread.php?t=349767)
  - [Rollback / factory-reset notes](https://www.mobileread.com/forums/showthread.php?t=361500)
  - [NiLuJe's snapshots & Hotfix](https://www.mobileread.com/forums/showthread.php?t=225030)

> **Quick Start:** Jailbreak (WinterBreak) → install Hotfix/Bridge → install KOReader → add your **Kavita OPDS** URL in KOReader (OPDS Catalog).

**Radio, Mesh & Offline Resources**

* **[Kiwix](https://www.kiwix.org/)** – Offline Wikipedia and documentation platform (Phase 2 resources)
* **[MeshCore](https://meshcore.co.uk/)** – Off-grid, LoRa-based mesh communications platform focused on secure, reliable text messaging
* **[Meshtastic](https://meshtastic.org/)** – LoRa mesh networking protocol
* **[OpenStreetMap](https://www.openstreetmap.org/)** – Community-driven mapping data for offline navigation
* **[RTL-SDR Community](https://www.rtl-sdr.com/)** – Software-defined radio ecosystem

**Hardware, Platform & Power**

* **[Docker](https://www.docker.com/)** – Container runtime platform
* **[Raspberry Pi Foundation](https://www.raspberrypi.org/)** – Single-board computer platform
* **[Raspberry Pi OS](https://www.raspberrypi.com/software/)** / **[Debian](https://www.debian.org/)** – Base OS and packaging ecosystem
* **[Victron Energy](https://www.victronenergy.com/)** – Solar charge controller and monitoring

**Community Contributions**

* **[Paul MacKinnon](https://github.com/paulmackinnon)** – Original [Docker macvlan guide](https://paul-mackinnon.medium.com/openwrt-raspberry-pi-docker-vlan-project-9cb1db10684c)

---

**Comprehensive off-grid communication and media platform**
