<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# 🥧 Prepper Pi

> **⚠️ DISCLAIMER:** Personal project, early development. No warranties or support. Use at your own risk.

## Table of Contents

- [📄 License & Commercial Use](#-license-trademarks--commercial-use)
- [✨ Core Features](#-core-features)
- [🛠️ Hardware Assembly](#️-hardware-assembly)
- [📚 Documentation](#-documentation)
- [🔧 Software Setup](#-software-setup)
- [📥 Public Domain Content Downloaders](#-public-domain-content-downloaders)
  - [🎵 Music Downloads](pd_downloader/music/README.md)
  - [📽️ Movie Downloads](pd_downloader/movies/README.md)
  - [📚 Gutenberg Books](pd_downloader/ebooks/GUTENBERG_README.md)
  - [📖 Standard Ebooks](pd_downloader/ebooks/STANDARD_EBOOKS_README.md)
- [🔒 Security Hardening](#-security-hardening-do-this-before-field-use)
- [⚙️ Service Access & Configuration](#️-service-access--configuration)
- [🧠 Local LLM on Raspberry Pi](#-local-llm-on-raspberry-pi-pifriendly-options)
- [🌐 Network Architecture](#-network-architecture)
- [📋 Hardware Requirements](#-hardware-requirements)
- [🛣️ Development Roadmap](#️-development-roadmap)
- [✅ Testing & Validation](#-testing--validation)
- [🙏 Acknowledgments](#-acknowledgments)

---

## License, Trademarks & Commercial Use

**Project code:** **Prepper Pi Noncommercial License (PP-NC-1.0)** (see `LICENSE`).  
**Docs & media:** **CC BY-NC 4.0** (see `LICENSE-DOCS`).  
**Third-party software:** Licensed under their own FOSS licenses. See `licenses/THIRD_PARTY_NOTICES.md`.  
**GPL/LGPL source:** I publish the Corresponding Source **in the matching GitHub Release** for any image/binary I ship. See `licenses/SOURCE-OFFER.md`.

**DIY/personal use:** Free for personal, educational, and internal DIY builds.  
**Commercial sales:** Selling preconfigured hardware or services that ship/market the Prepper‑Pi stack requires a separate commercial license with revenue share. See `docs/legal/COMMERCIAL-LICENSE.md`.

**Commercial hardware sales (preconfigured devices):** Allowed **only** under a separate commercial license with revenue share. See `docs/legal/COMMERCIAL-LICENSE.md` and contact **pyrometheous**.

**Trademarks:** "Prepper Pi" name/logo are not covered by the software licenses. See `docs/legal/TRADEMARKS.md`. Do **not** market third-party marks (e.g., Meshtastic, OpenWrt, Raspberry Pi, Jellyfin) as product branding without their owners' permissions.

For transparency about brand/trademark outreach, see `docs/legal/permissions-log.md`.

**No copyrighted media included:** Devices ship **without** copyrighted content. Users are responsible for lawful use of media and RF features.

**Codecs/patents note:** FFmpeg and certain codecs (e.g., H.264/AVC, HEVC, AAC, AC-4) may be patent-encumbered in some regions. ATSC 3.0 deployments commonly use HEVC video and AC-4 audio. This project does not grant patent licenses. Where required, ship legal codecs from your OS vendor and let end-users enable optional encoders themselves.

**Regulatory note:** The FCC’s NextGen TV (ATSC 3.0) transition is voluntary and preserves consumer reception while requiring local simulcasting obligations for broadcasters, subject to waivers. Consumer use of ATSC 3.0 receivers where available is permitted. See FCC guidance (DOC‑415053A1): https://docs.fcc.gov/public/attachments/DOC-415053A1.pdf. This project is receive‑only; do not retransmit or bypass content protection.

> **Note:** If a matching GitHub Release isn't published yet for a given image/binary, use the repository source at the tagged commit. Once a formal Release is cut, the corresponding source will be attached to that Release.

### 🔐 Security

Please report vulnerabilities privately via GitHub Security Advisories (GitHub → Security → Report a vulnerability). If that is unavailable, open a minimal Issue with the `security` label and I’ll follow up privately. See `SECURITY.md`.

Note: This is a hobby project with no guaranteed turnaround for issues or security reports. I’ll review items as time permits.

---

**A comprehensive off-grid communication and media platform with solar power, dual LoRa mesh protocols, TV/radio reception, and WiFi hotspot capabilities.**

## ✨ Core Features

> **📋 Note:** The following features represent the planned capabilities of Prepper Pi. Phase 1 (WiFi infrastructure with RaspAP) is working and validated on Raspberry Pi 5. Remaining phases require additional hardware.

### 📺 Concurrent Operations
- Two OTA TV channels (ATSC 1.0 or ATSC 3.0/NextGen TV, market/tuner dependent) via dual tuner
- Two radio stations (FM + NOAA) via dual RTL-SDR
- Dual LoRa meshes (Meshtastic + MeshCore)
- WiFi hotspot with service dashboard
- Jellyfin media streaming
- Kavita ebook server (OPDS feeds for KOReader/Kindle)
- Samba file sharing
- Local LLM (offline Q&A) with Pi‑friendly models (via Ollama/llama.cpp; optional Open WebUI)
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
sudo apt update && sudo apt install -y git
```

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git \
  && cd Prepper-Pi && sudo bash scripts/first-run-setup.sh
```

**On Raspberry Pi:** `cp compose/docker-compose.pi.yml docker-compose.override.yml` before `docker compose up -d`.
Alternatively use explicit files:
`docker compose -f docker-compose.yml -f compose/docker-compose.pi.yml up -d`.

**WiFi Configuration:**
- Uses native RaspAP with hostapd for WiFi AP functionality
- Configure WiFi settings via RaspAP web interface at `http://10.20.30.1:8080`
- Default SSID: "Prepper Pi", default password: `ChangeMeNow!` ⚠️ **Change immediately**
- Supports dual WiFi setup: wlan0 (upstream/internet), wlan1 (AP for clients)

###  Quick Access via QR Code

Once connected to the **Prepper Pi** WiFi network, scan this QR code to access the homepage dashboard:

<div align="center">
  <img src="qr_code/homepage.svg" alt="Prepper Pi Homepage QR Code" width="300"/>
  <br/>
  <em>Scan to access: http://10.20.30.1:3000</em>
</div>

The QR code provides instant access to the Homepage dashboard where you can navigate to all services (Jellyfin, Nextcloud, Kavita, etc.).

### 🗑️ System Removal

```bash
git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && sudo bash scripts/cleanup.sh && cd .. && rm -rf Prepper-Pi
```

## Public Domain Content Downloaders

**Build your offline library with legal, verified public domain content:**

The Prepper Pi includes automated downloaders for populating your offline media library with legal public domain and Creative Commons Zero (CC0) content. All downloaders include license verification, disk space management, and integration with Jellyfin (movies/music) and Kavita (ebooks).

### 🎵 Music - Public Domain & CC0 Recordings
Download classical music, historical jazz, and pre-1930 recordings with automatic disk space checking and unlimited download support.

**Features:**
- ✅ Three-layer license verification (source, metadata, Musopen cross-check)
- ✅ Automatic disk space management (warns before large downloads)
- ✅ Smart defaults (no query required)
- ✅ Unlimited download mode for complete archives
- ✅ Duplicate detection and resume support
- ✅ Jellyfin/Navidrome ready with embedded metadata

**Quick Start:**
```powershell
cd pd_downloader/music
pip install -r requirements.txt
python pd_music_downloader.py --out ./music --max-items 100
```

**Documentation:** [Music Downloader README](pd_downloader/music/README.md)

---

### 📽️ Movies - Public Domain Films
Download verified public domain films from Internet Archive and Wikimedia Commons with provenance tracking.

**Features:**
- ✅ Curated manifest system prevents arbitrary downloads
- ✅ SHA256 checksums for integrity verification
- ✅ Provenance tracking for audit trails
- ✅ Restoration copyright warnings
- ✅ Trademark considerations documented

**Quick Start:**
```powershell
cd pd_downloader/movies
python public_domain_movies.py --manifest manifest.csv --out ./movies
```

**Documentation:** [Movies Downloader README](pd_downloader/movies/README.md)

---

### 📚 Books - Project Gutenberg Library
Download the entire Project Gutenberg library (70,000+ books) using self-hosted Gutendex with Docker.

**Features:**
- ✅ Self-hosted Docker solution (unlimited API access)
- ✅ Fully automated setup with `automated_gutendex_download.py`
- ✅ Kavita-ready metadata and folder organization
- ✅ Automatic PG branding removal for redistribution compliance
- ✅ Genre-based filtering and discovery mode

**Quick Start:**
```powershell
cd pd_downloader/ebooks
pip install -r requirements.txt
python automated_gutendex_download.py --mode popular --count 100
```

**Documentation:** [Gutenberg Downloader README](pd_downloader/ebooks/GUTENBERG_README.md)

---

### 📖 Books - Standard Ebooks Library
Download professionally edited, beautifully formatted public domain ebooks (requires Patrons Circle membership).

**Features:**
- ✅ All editions are CC0 (public domain)
- ✅ Modern typography and semantic markup
- ✅ 600+ professionally edited classics
- ✅ Kavita integration with collection metadata
- ✅ Series organization and OPDS support

**Quick Start:**
```powershell
cd pd_downloader/ebooks
pip install -r requirements.txt
python standard_ebooks_to_kavita.py --api-key YOUR_KEY --out ./StandardEbooks
```

**Documentation:** [Standard Ebooks README](pd_downloader/ebooks/STANDARD_EBOOKS_README.md)

---

**📦 Complete Downloader Suite Documentation:** [pd_downloader/README.md](pd_downloader/README.md)

**Storage Requirements:**
- **Music:** 5 MB avg/track (MP3), 20 MB/track (FLAC). Unlimited downloads: 1-8 TB
- **Movies:** 500 MB - 2 GB per film. Full archive: ~1 TB
- **Books (Gutenberg):** 70,000+ books: ~60 GB total
- **Books (Standard Ebooks):** 600+ books: ~2 GB total

**Legal Compliance:**
All downloaders implement multi-layer license verification and include interactive warnings about copyright. Users are responsible for verifying public domain status in their jurisdiction.

## 🔒 Security Hardening (do this before field use)
1. **Change all defaults** (RaspAP admin password from "secret", WiFi SSID/passphrase from "Prepper Pi"/"ChangeMeNow!", Pi user password).
2. **Configure RaspAP security**: Set strong WiFi password, change admin password, consider restricting management to wired access only.
3. **Enable HTTPS** on admin interfaces; restrict management to wired or trusted network.
4. **Rotate API keys/secrets** for any services you enable (Jellyfin, Portainer CE).
5. **Update & lock** package versions; rebuild images with `scripts/build-manifest.sh` to record digests.
6. **Back up** `/etc/prepper-pi/VERSION` and the full `MANIFEST.txt` with each release.

## ⚙️ Service Access & Configuration

### 🌐 Network Access
- **Pi Gateway/Router:** `10.20.30.1` (WiFi AP gateway)
- **RaspAP Admin:** `http://10.20.30.1:8080` - **Default credentials: `admin` / `secret`** ⚠️ **CHANGE IMMEDIATELY**
- **Wi‑Fi Network (default):** SSID "Prepper Pi", password `ChangeMeNow!` ⚠️ **Change via RaspAP web UI**
- **DHCP Range:** 10.20.30.100-199 for client devices
- **Homepage Dashboard:** `http://10.20.30.1:3000` (manual access - no automatic captive portal redirect)

### 📊 Service URLs
| Service | URL | Status | Notes |
|---------|-----|--------|-------|
| RaspAP Router | http://10.20.30.1:8080 | ✅ **Working** | WiFi & network management (admin/secret) |
| Homepage Dashboard | http://10.20.30.1:3000 | 🔄 **In Development** | Service dashboard (manual access) |
| Portainer | http://10.20.30.1:9000 | 🔄 **In Development** | Container management *(Community Edition)* |
| Jellyfin | http://10.20.30.1:8096 | 🔄 **In Development** | Media server (needs content) |
| Samba | \\\\10.20.30.1 | ✅ **Working** | File sharing |
| Tvheadend | http://10.20.30.1:9981 | 📋 **Planned** | TV backend (ATSC 1.0; ATSC 3.0 where supported; HEVC/AC‑4; encryption varies) |
| Meshtastic | http://10.20.30.1:2443 | 📋 **Planned** | LoRa mesh A (Phase 5) |
| MeshCore | http://10.20.30.1:2444 | 📋 **Planned** | LoRa mesh B (Phase 5) |

**Status Legend:**
- ✅ **Working** - Tested and verified on Raspberry Pi 5
- 🔄 **In Development** - Functional but undergoing improvements
- ⏸️ **On Hold** - Deprioritized; may not be pursued
- 📋 **Planned** - Service templates ready, hardware needed

## 🧠 Local LLM on Raspberry Pi (Pi‑friendly options)

> Goal: run small, useful, fully offline models on a Raspberry Pi 5 for emergency Q&A, checklists, and basic text tasks.

What works well on a Pi 5 (8 GB) today:
- Prefer 1–2B parameter models (quantized GGUF) for responsiveness.
- 3–4B can run with tight memory; keep context short and use 4‑bit quantization.
- 7B usually requires more RAM than is comfortably available for the OS + services.

Approaches
- Ollama (simple runner + registry)
  - Install on ARM64 Linux (Pi OS 64‑bit): https://ollama.com/download/linux
  - Pull tiny models first (examples):
    - Qwen2‑1.5B‑Instruct (good general small chat; Apache‑2.0)
    - Gemma 3 1B (very small; basic tasks)
  - Pair with a web UI: Open WebUI supports Ollama out‑of‑the‑box (Docker or pip). See docs: https://docs.openwebui.com/
- llama.cpp (lowest overhead, flexible server)
  - Runs GGUF models with a lightweight CLI and an OpenAI‑compatible HTTP server (`llama-server`).
  - Project: https://github.com/ggerganov/llama.cpp
  - Use 4‑bit (Q4_K_M) quantized models and modest context windows for speed.
- Whisper.cpp (optional speech‑to‑text)
  - For offline transcription of short voice notes or radio clips (tiny/base models tend to work best).
  - Project: https://github.com/ggml-org/whisper.cpp

Model pointers (GGUF)
- Qwen/Qwen2‑1.5B‑Instruct‑GGUF (Apache‑2.0): https://huggingface.co/Qwen/Qwen2-1.5B-Instruct-GGUF
- TheBloke/phi‑2‑GGUF (MSR research license – noncommercial): https://huggingface.co/TheBloke/phi-2-GGUF

Practical tips on a Pi 5
- Cooling matters: avoid thermal throttling with a fan or active cooler.
- Keep context short (e.g., 512–1024 tokens) to reduce RAM/CPU use.
- Prefer 4‑bit quantization (Q4_K_M) for a good quality/speed tradeoff.
- Check model licenses—many are noncommercial/research‑only; this project’s noncommercial code license does not change third‑party model terms.

Web UIs
- Open WebUI (works offline; integrates with Ollama; has RAG tools):
  - Project: https://github.com/open-webui/open-webui
  - “Bundled with Ollama” images and usage: https://docs.openwebui.com/

References
- Ollama quickstart, models, and CLI: https://github.com/ollama/ollama
- llama.cpp quickstart and server: https://github.com/ggerganov/llama.cpp
- Open WebUI installation and troubleshooting: https://docs.openwebui.com/
- Whisper.cpp quickstart and memory guidance: https://github.com/ggml-org/whisper.cpp

## 🌐 Network Architecture

### 📡 Network Topology
```
Internet Connection (ethernet/cellular - optional)
     |
     └── wlan0 (upstream WiFi - builtin)
          |
Raspberry Pi 5 (10.20.30.1 WiFi AP Gateway)
     |
     ├── wlan1 (AP - ALFA AWUS036ACM USB WiFi)
     │   └── RaspAP (hostapd + dnsmasq)
     │       └── WiFi Access Point "Prepper Pi"
     │           └── Client devices (10.20.30.100-199)
     │
     └── Docker Bridge (172.17.0.0/16)
         ├── Homepage (port 3000) ← Service dashboard
         ├── Jellyfin (port 8096)
         ├── Portainer (port 9000)
         └── Samba (port 445)
```

### 🔗 Service Access
*All services accessible via `10.20.30.1` gateway IP with specific ports. Homepage dashboard at http://10.20.30.1:3000 provides links to all services. Internet passthrough from wlan0 → wlan1 via NAT.*

## 📋 Hardware Requirements

> **📝 Complete Components List:** See [docs/components.md](docs/components.md) for detailed specifications, part numbers, and development phase status.

### 🖥️ Base Requirements (Currently Owned)
- **Raspberry Pi 5** (8GB) with adequate cooling solution
- **NVMe SSD** (1TB+) for media storage and OS performance
- **ALFA Network AWUS036ACM** - Long-range dual-band AC1200 USB WiFi adapter with external antenna
- **MicroSD Card** (32GB+) for initial boot and backup

### 📡 RF Communications (Future Hardware)
- **Dual RTL-SDR Dongles** for FM radio and NOAA weather reception
- **Dual TV Tuner** USB devices for OTA broadcast reception (ATSC 1.0 or ATSC 3.0‑capable, depending on your market and needs)
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
- ✅ **Tested & Working** - Deployed and verified on Raspberry Pi 5
- ⭐ **Code Complete** - Implementation finished, tested and working
- 🔄 **In Development** - Functional but actively being improved
- ⏸️ **On Hold** - Deprioritized; may not be pursued
- 📋 **Planned** - Not yet started
- ❌ **Blocked** - Waiting on hardware/dependencies

### Phase 1: Basic WiFi Infrastructure
- [✅] Raspberry Pi 5 setup with adequate cooling and NVMe storage
- [✅] **Docker Compose service stack** - *Tested and working on Pi 5 (8GB)*
- [✅] **WiFi hotspot configuration** - *Working with RaspAP native hostapd*
- [✅] **Hardware integration testing** - *Complete: validated on Pi 5 with dual WiFi*
- [🔄] **Homepage dashboard** - *Functional, undergoing UI/UX improvements*
- [⏸️] **Automatic captive portal redirect** - *On hold; may not be pursued (manual access works)*

**Current Status:** Phase 1 is functionally complete! WiFi AP works reliably with RaspAP, all Docker services are accessible, and internet passthrough is operational. Hardware validation complete on Raspberry Pi 5 with dual WiFi adapters (wlan0=upstream, wlan1=AP). Homepage provides clean dashboard for service access. Automatic captive portal redirect has been deprioritized in favor of manual access.

**Active Development:** Homepage UI/UX improvements ongoing in `feature/native-hostapd` branch.

### Phase 2: Emergency Resources & AI
- [📋] Offline emergency resource database (first aid, survival guides)
- [📋] Local LLM deployment for emergency consultation and guidance
- [📋] Emergency communication protocols and documentation
- [📋] Offline Wikipedia and essential reference materials
- [📋] Testing AI response quality and resource accessibility

### Phase 3: Media Server & Storage
- [📋] Jellyfin media server configuration and optimization
- [📋] Kavita ebook server for digital library management
- [⭐] **Media library organization on NVMe SSD storage** - *Public domain downloader suite complete (music, movies, ebooks)*
- [📋] File sharing with Samba for local network access
- [📋] Mobile-optimized interfaces for media streaming and reading
- [📋] Performance testing with multiple concurrent streams

### Phase 4: TV & Radio Reception (Acquire Hardware)
- [❌] Dual TV tuner USB devices for OTA broadcast reception
- [❌] Dual RTL-SDR dongles for FM radio and NOAA weather reception
- [❌] Antenna system design and RF signal optimization
- [❌] Tvheadend configuration and emergency broadcast monitoring (ATSC 1.0; experimental ATSC 3.0 as supported)

Note: ATSC 3.0 commonly uses HEVC video and AC‑4 audio. Some ATSC 3.0 broadcasts may be encrypted. Compatibility depends on tuner hardware, drivers, and software (e.g., Tvheadend). This project does not circumvent content protection.
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

### 🔬 Phase 1 Completed Validations
1. ✅ **WiFi AP Hardware Validation** - RaspAP working with native hostapd on Pi 5
2. ✅ **Service Connectivity Verification** - All Docker services accessible via gateway IP
3. ✅ **USB WiFi Device Compatibility** - ALFA AWUS036ACM confirmed working as AP (wlan1)
4. ✅ **Docker Service Stack Stability** - All services start reliably and remain accessible
5. ✅ **Dual WiFi Configuration** - wlan0 (builtin upstream) + wlan1 (USB AP) working
6. ✅ **Internet Passthrough** - NAT routing from wlan0 → wlan1 operational

### 📋 Future Testing Priorities
1. **Power Consumption Baseline** - Measure current usage before adding additional hardware
2. **Homepage UI/UX Refinement** - Continue improvements to service dashboard
3. **Long-term Stability** - Extended runtime testing for reliability
4. **Performance Optimization** - Tune for best experience on Pi 5 hardware

### 🧪 Validation Tests

**Current Client Experience:**
1. Connect to "Prepper Pi" SSID with password `ChangeMeNow!` (⚠️ change via RaspAP)
2. Get DHCP address from RaspAP (10.20.30.100-199 range)
3. Manually browse to http://10.20.30.1:3000 for Homepage dashboard
4. Access all services through the Homepage or direct URLs
5. Internet access works via wlan0→wlan1 passthrough

**Manual Verification Commands (on Pi):**
```bash
# Check WiFi AP status (native hostapd)
sudo systemctl status hostapd

# Check DHCP server
sudo systemctl status dnsmasq

# View connected clients
iw dev wlan1 station dump  # wlan1 is AP interface (ALFA USB adapter)

# Check interface configuration
ip addr show wlan1

# Verify internet routing
sudo iptables -t nat -L POSTROUTING -v

# Test services are accessible
curl -I http://10.20.30.1:3000  # Homepage
curl -I http://10.20.30.1:8080  # RaspAP
curl -I http://10.20.30.1:9000  # Portainer
```

**Validated Success Indicators (Phase 1 Complete):**
- ✅ WiFi SSID "Prepper Pi" is visible and connectable
- ✅ Clients can connect and get 10.20.30.x addresses from DHCP
- ✅ Homepage dashboard accessible at http://10.20.30.1:3000
- ✅ All Docker services accessible via 10.20.30.1
- ✅ Internet passthrough working (wlan0→wlan1 via NAT)
- ✅ Dual WiFi configuration stable (builtin + USB adapter)

## 🙏 Acknowledgments

**Networking & WiFi Management**

* **[RaspAP](https://raspap.com/)** – WiFi hotspot management for Raspberry Pi with web UI
* **[hostapd](https://w1.fi/hostapd/)** – WiFi access point daemon
* **[dnsmasq](https://thekelleys.org.uk/dnsmasq/doc.html)** – Lightweight DNS/DHCP server
* **[iptables](https://www.netfilter.org/)** – Linux firewall and NAT routing

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

**AI & Local LLMs**

* **[Ollama](https://github.com/ollama/ollama)** – Local model runner and registry; ARM64 Linux install: https://ollama.com/download/linux
* **[llama.cpp](https://github.com/ggerganov/llama.cpp)** – Lightweight GGUF inference and OpenAI‑compatible server
* **[Open WebUI](https://github.com/open-webui/open-webui)** — Self‑hosted AI UI; docs with “bundled with Ollama” option: https://docs.openwebui.com/
* **[whisper.cpp](https://github.com/ggml-org/whisper.cpp)** — Offline speech‑to‑text (tiny/base models fit best on Pi)
* Models (GGUF examples):
  - **Qwen/Qwen2‑1.5B‑Instruct‑GGUF** (Apache‑2.0): https://huggingface.co/Qwen/Qwen2-1.5B-Instruct-GGUF
  - **TheBloke/phi‑2‑GGUF** (Microsoft Research license): https://huggingface.co/TheBloke/phi-2-GGUF

---

**Comprehensive off-grid communication and media platform**