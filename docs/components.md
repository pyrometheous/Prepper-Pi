# Prepper-Pi Components List

> **Project Status:** This components list reflects the planned hardware for the complete Prepper-Pi system. Currently, only Phase 1 (Compute & Core) components are owned. See [../README.md](../README.md) for development phases and current status.

## Complete Bill of Materials

| Category | Qty | Make | Model/Part | Notes |
|----------|-----|------|------------|-------|
| **Compute & Core** | | | | |
| Compute & Core | 1 | Raspberry Pi Foundation | Raspberry Pi 5 (8GB) | Main board |
| Compute & Core | 1 | Raspberry Pi Foundation | 27W USB-C Power Supply | If not powering from 12→5V buck |
| Compute & Core | 1 | Raspberry Pi Foundation | Pi 5 Active Cooler | Heatsink + fan |
| Compute & Core | 1 | Raspberry Pi Foundation | M.2 HAT+ (Compact) | NVMe carrier for Pi 5 |
| Compute & Core | 1 | TeamGroup / WD / Crucial (example) | NVMe SSD 512GB (PCIe 3.0, 2280) | Storage |
| Compute & Core | 1 | ALFA Network | AWUS036ACM | Long-Range Dual-Band AC1200 USB WiFi Adapter w/External Antenna |
| **TV (75Ω path)** | | | | |
| TV (75Ω path) | 1 | Antennas Direct | ClearStream 2MAX | VHF-Hi/UHF OTA antenna |
| TV (75Ω path) | 1 | Channel Master | CM-7777HD | Mast preamp + power inserter; FM-trap/LTE filtering |
| TV (75Ω path) | 1 | Proxicast / PolyPhaser | 75Ω F-F Coax Lightning Arrestor | Protects OTA run; at entry |
| TV (75Ω path) | 1 | Channel Master | CM-3414 (Ultra Mini 4) | 4-port distribution amp |
| TV (75Ω path) | 1 | Hauppauge | WinTV-dualHD (USB Dual ATSC) | Two independent TV tuners in one |
| **Radio (SDR)** | | | | |
| Radio (SDR) | 2 | RTL-SDR Blog | RTL-SDR V4 (dongle-only) | Two simultaneous radio stations |
| Radio (SDR) | 1 | Nooelec (example) | Flamingo+ Broadcast FM Notch | FM band-stop for NOAA leg |
| Radio (SDR) | 2 | Nooelec / Pasternack (example) | F-female → SMA-male pigtail/adapter | Adapt 75Ω RG-6 to SDR SMA |
| **LoRa** | | | | |
| LoRa | 1-2 | Waveshare | SX1262 915 MHz LoRa HAT (for Pi) | Pi-attached LoRa radio(s) - qty 2 for dual mesh |
| LoRa | 1-2 | ALFA Network | ARS-915P (SMA) | 915 MHz omni antenna(s) |
| LoRa | 1-2 | L-com / Times Microwave | LMR-240 SMA patch (~3 ft) | Short RF jumper(s) inside case |
| LoRa | 2 | LILYGO | T-Beam (ESP32 + SX1262) | Handheld companion nodes (BLE + GPS variants available) |
| LoRa | 1 | Various | SMA A/B manual RF switch (DC-pass) | Optional - for single antenna dual radio setup |
| LoRa | 1 | Various | uhubctl-compatible powered USB 3.0 hub | Optional - for USB LoRa radio power control |
| **Cables / Bulkheads** | | | | |
| Cables / Bulkheads | 1 | Belden / CommScope (example) | RG-6 Quad-Shield Coax (cut to length) | OTA coax runs |
| Cables / Bulkheads | 1 | Various | Ground Block (F-type, 75Ω) | Bond to case/ground |
| Cables / Bulkheads | 1 | MC4 / Amphenol (example) | MC4 PV Leads/Bulkheads | Panel → controller |
| **Power / Solar / UPS** | | | | |
| Power / Solar / UPS | 1 | LiTime (example) | 12 V 50 Ah LiFePO₄ | Main battery (size per runtime) |
| Power / Solar / UPS | 1 | Victron Energy | SmartSolar MPPT 75/15 | Solar charge controller (12 V system) |
| Power / Solar / UPS | 1 | Renogy (example) | 100 W 12 V Monocrystalline Panel | Foldable or rigid |
| Power / Solar / UPS | 1 | Pololu (or equivalent) | D24V50F5 (5 V / 5 A Buck) | Pi power from 12 V |
| Power / Solar / UPS | 1 | Optional | 13.2 V DC Regulator | For CM-3414 if you want fixed 13.2 V |
| Power / Solar / UPS | 1 | Powerwerx (example) | Anderson Powerpole Kit (150-pc) | DC distribution/connectors |
| Power / Solar / UPS | 2 | InstallGear / Littelfuse (example) | Inline ATO/ATC Fuse Holders (10 AWG) | Branch protection |
| **Enclosure & Hardware** | | | | |
| Enclosure & Hardware | 1 | Custom | Custom 3D print | Weather-resistant enclosure, internal partition |
| Enclosure & Hardware | as needed | Various | Bulkhead feed-throughs (MC4 / F / SMA) & cable glands | Wall pass-throughs, strain relief |
| Enclosure & Hardware | as needed | Various | Ground Rod & Strap | Single-point bond for case/arrestor |
| Enclosure & Hardware | as needed | Various | 12 V case fans + grills | Vent the power bay |

## Development Phases

### Phase 1: Currently Owned ✅
- Raspberry Pi 5 (8GB) and related compute components
- NVMe storage and cooling solutions  
- ALFA Network AWUS036ACM WiFi adapter for hotspot functionality

### Phase 4: TV & Radio Reception (Hardware to be Acquired) ❌
- Dual TV tuner and OTA antenna system
- Dual RTL-SDR setup for FM/NOAA reception

### Phase 5: LoRa Mesh Networking (Hardware to be Acquired) ❌
- Dual LoRa radio setup for Meshtastic and MeshCore capabilities
- Waveshare LoRa HAT(s) and companion nodes
- 915 MHz antenna system with switching capability

### Phase 6: Solar Power & Enclosure (Hardware to be Acquired) ❌
- Complete solar power system with battery
- Custom 3D printed weatherproof enclosure

---

For detailed technical specifications and wiring diagrams, see [wiring.md](wiring.md).

## Dual LoRa Mesh Radios (Meshtastic + MeshCore)

> **Goal:** Run **two independent 915 MHz LoRa radios** so Meshtastic and MeshCore can both be utilized, with **simple on/off toggling** and a clear antenna strategy.

### Radio Configuration Options

**Option A — Two Pi HATs (SX1262, 915 MHz):**
- Components: Waveshare SX1262 LoRa HAT ×2
- Pros: Compact design, direct GPIO interface
- Cons: Power control/toggling complexity, physical stacking clearance required

**Option B — Two USB LoRa nodes (ESP32 + SX1262/1276, 915 MHz):**
- Components: Meshtastic-capable ESP32 LoRa boards ×2 (one Meshtastic, one MeshCore firmware)
- Pros: Simple USB isolation, easy power toggle, flexible placement
- Cons: Slightly larger footprint than HATs

**Option C — Mixed Configuration:**
- Components: 1× HAT + 1× USB LoRa node
- Pros: Balances compactness with flexibility

### Power Management & Toggling

**Recommended for USB Options (B/C):**
- **uhubctl-compatible powered USB 3.0 hub** — per-port power switching from software
- **Inline USB on/off switches (×2)** — manual toggles per radio USB line

**For HAT Option (A):**
- **2-channel DC load switch/relay board** (5V GPIO-controlled) — cuts radio Vcc
- **Raspberry Pi PoE/ATX-style HAT** — advanced option for managed power domains

### Antenna Strategy

**Dual Antenna Setup (Recommended):**
- **Two separate 915 MHz antennas** with short LMR-240/LMR-200 pigtails
- Maintain at least 30–50 cm separation between antennas
- Simplest configuration, allows simultaneous operation

**Single Antenna with A/B Switch:**
- **SMA A/B coax switch (DC-pass on "A" side)** feeding single 915 MHz antenna
- Set A=Meshtastic or B=MeshCore; only one connected at a time
- Prevents TX collisions but requires manual/software switching

> ⚠️ **Important:** Avoid simple splitters/combiners for simultaneous TX — they can cause damage unless properly isolated and PTT-coordinated.

### Additional Dual LoRa Components

- **2× 915 MHz LoRa radios** (per chosen configuration above)
- **1× Powered USB 3.0 hub (uhubctl-compatible)** *or* **2× Inline USB on/off switches**
- **1× SMA A/B manual RF switch (DC-pass)** *or* **1× Second 915 MHz antenna**
- **2–4× SMA male–male coax jumpers** (0.3–0.5 m, 50 Ω)
- **2× 915 MHz rubber-duck or short omni antennas** *(for dual-antenna setup)*
- **Mounting hardware/spacers** for stacked HATs *(if Option A)*
- **Short USB-A/USB-C cables** for radio placement/strain relief *(if Option B/C)*

### Software & Labeling Notes

- Label radios and ports clearly: **LoRa-A (Meshtastic)**, **LoRa-B (MeshCore)**
- If using `uhubctl`, implement service scripts to toggle ports and prevent concurrent transmission when using single antenna via A/B switch
- Consider automated switching logic to prevent RF interference between mesh protocols

## Additional Components (Optional)

- **Powered USB 3.0 hub (5 V, ≥3 A PSU)** — optional for SDR/ATSC stability under load
- **SMA inline attenuators (2×, 6 dB typical)** — for front‑end overload control on SDR legs
- **ATO/ATC fuse assortment (1–30 A)** — mixed pack to match sizing table
- **Ferrite snap‑on cores (5–7 mm ID, 6–10 pcs)** — common‑mode chokes for USB/coax leads
- **12 V TVS diode (e.g., SMAJ58A or system‑appropriate)** — transient suppression on 12 V bus
- **Coax weatherproofing** — self‑fusing silicone tape or boots for exterior F‑connectors

*Last updated: 2025-10-07*
