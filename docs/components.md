# Prepper-Pi Components List

> **Project Status:** This components list reflects the planned hardware for the complete Prepper-Pi system. Currently, only Phase 1 (Compute & Core) components are owned. See [../README.md](../README.md) for development phases and current status.

## Complete Bill of Materials

### Compute & Core
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 1 | Raspberry Pi Foundation | Raspberry Pi 5 (8GB) | Main board |
| 1 | Raspberry Pi Foundation | 27W USB-C Power Supply | If not powering from 12→5V buck |
| 1 | Raspberry Pi Foundation | Pi 5 Active Cooler | Heatsink + fan |
| 1 | Raspberry Pi Foundation | M.2 HAT+ (Compact) | NVMe carrier for Pi 5 |
| 1 | TeamGroup / WD / Crucial (example) | NVMe SSD 512GB (PCIe 3.0, 2280) | Storage |
| 1 | ALFA Network | AWUS036ACM | Long-Range Dual-Band AC1200 USB WiFi Adapter w/External Antenna |

### TV (75Ω path)
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 1 | Antennas Direct | ClearStream 2MAX | VHF-Hi/UHF OTA antenna |
| 1 | Channel Master | CM-7777HD | Mast preamp + power inserter; FM-trap/LTE filtering |
| 1 | Proxicast / PolyPhaser | 75Ω F-F Coax Lightning Arrestor | Protects OTA run; at entry |
| 1 | Channel Master | CM-3414 (Ultra Mini 4) | 4-port distribution amp |
| 1 | Hauppauge | WinTV-dualHD (USB Dual ATSC 1.0) | Two independent TV tuners in one |

#### ATSC 3.0 (NextGen TV) notes
- Market availability varies; some markets simulcast both ATSC 1.0 and 3.0.
- Common codecs: HEVC (video) and AC‑4 (audio). Ensure your OS/software provides legal decoders; this project does not ship codec licenses.
- Some ATSC 3.0 services may be encrypted; reception of encrypted content is limited by tuner and software capabilities. This project does not circumvent content protection.
- Software support is evolving. Tvheadend may require external tools or patches for 3.0 workflows.
- Example 3.0‑capable devices (non‑exhaustive; verify driver/OS support):
	- HDHomeRun CONNECT 4K (network tuner)
	- Hauppauge WinTV‑quadHD ATSC 3.0 (where available) or newer Hauppauge 3.0 products
	- PCIe/USB ATSC 3.0 tuners from regional vendors (Linux driver support varies)


### Radio (SDR)
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 2 | RTL-SDR Blog | RTL-SDR V4 (dongle-only) | Two simultaneous radio stations |
| 1 | Nooelec (example) | Flamingo+ Broadcast FM Notch | FM band-stop for NOAA leg |
| 2 | Nooelec / Pasternack (example) | F-female → SMA-male pigtail/adapter | Adapt 75Ω RG-6 to SDR SMA |

### LoRa
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 2 | Waveshare | SX1262 915 MHz LoRa HAT (for Pi) | Pi-attached LoRa radios - dual mesh requirement |
| 1-2 | ALFA Network | ARS-915P (SMA) | 915 MHz omni antenna(s) - qty 2 for dual antenna setup |
| 2 | L-com / Times Microwave | LMR-240 SMA patch (~3 ft) | Short RF jumper(s) inside case |
| 2 | LILYGO | T-Beam (ESP32 + SX1262) | Handheld companion nodes (BLE + GPS variants available) |
| 1 | Various | SMA A/B manual RF switch (DC-pass) | Optional - for single antenna dual radio setup |
| 1 | Various | uhubctl-compatible powered USB 3.0 hub | Optional - for USB LoRa radio power control |

### Cables / Bulkheads
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 1 | Belden / CommScope (example) | RG-6 Quad-Shield Coax (cut to length) | OTA coax runs |
| 1 | Various | Ground Block (F-type, 75Ω) | Bond to case/ground |
| 1 | MC4 / Amphenol (example) | MC4 PV Leads/Bulkheads | Panel → controller |

### Power / Solar / UPS
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 1 | LiTime (example) | 12 V 50 Ah LiFePO₄ | Main battery (size per runtime) |
| 1 | Victron Energy | SmartSolar MPPT 75/15 | Solar charge controller (12 V system) |
| 1 | Renogy (example) | 100 W 12 V Monocrystalline Panel | Foldable or rigid |
| 1 | Pololu (or equivalent) | D24V50F5 (5 V / 5 A Buck) | Pi power from 12 V |
| 1 | Optional | 13.2 V DC Regulator | For CM-3414 if you want fixed 13.2 V |
| 1 | Powerwerx (example) | Anderson Powerpole Kit (150-pc) | DC distribution/connectors |
| 2 | InstallGear / Littelfuse (example) | Inline ATO/ATC Fuse Holders (10 AWG) | Branch protection |

### Enclosure & Hardware
| Qty | Make | Model/Part | Notes |
|-----|------|------------|-------|
| 1 | Hammond / Bud / Polycase | Polycarbonate NEMA 4X / IP66 enclosure (≈ 300×200×150 mm, light color) | Sealed outdoor box; UV-stabilized |
| 1 | Generic / Fischer / Wakefield | External finned heatsink (≈ 200×150×25 mm), vertical fins | Through-wall thermal rejection (Option A) |
| 1 | 6061 plate | Aluminum transfer plate, 3–4 mm | Internal thermal bridge under sink footprint |
| 1 | FujiPoly / Gelid / Arctic | Thermal pad 1–2 mm, ≥6 W/m·K (or thin thermal epoxy) | Between wall↔plate and/or plate↔sink |
| 1–2 | Gore / equivalent | ePTFE pressure-equalization vent, M12 | Prevents baro-pumping; reduces condensation |
| 1 | Industrial PoE splitter | 802.3at PoE → 5 V/5 A (USB-C) | One-cable outdoor power for Pi + peripherals |
| 1 | Transtherm / Stego (opt.) | Mini anti-condensation heater 10–20 W, ~15 °C stat | Cold/wet climates; low duty cycle |
| as needed | L-com / Amphenol | IP68 cable glands (M16/M20), SMA/N bulkheads | Ethernet/DC entries, RF pass-throughs |
| as needed | PolyPhaser / Proxicast | Coax/PoE surge protectors | Protection at enclosure entry |
| 1 | Desiccant + RH card | Silica gel packs + humidity indicator | Door-side visual check |
| (opt.) | Custom | 3D-printed brackets/partition | Mounting inside sealed box (non-structural) |

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

> **Goal:** Run **two independent 915 MHz LoRa radios** for simultaneous Meshtastic and MeshCore capabilities, with **simple on/off toggling** and a clear antenna strategy.

> **Required:** This build assumes **dual LoRa radios are mandatory** for full mesh protocol support. Antenna configuration (1 or 2 antennas) is flexible based on implementation preference.

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

**USB Options (B/C):**
- **uhubctl-compatible powered USB 3.0 hub** — per-port power switching from software
- **Inline USB on/off switches (×2)** — manual toggles per radio USB line

**For HAT Option (A):**
- **2-channel DC load switch/relay board** (5V GPIO-controlled) — cuts radio Vcc
- **Raspberry Pi PoE/ATX-style HAT** — advanced option for managed power domains

### Antenna Strategy

**Dual Antenna Setup:**
- **Two separate 915 MHz antennas** with short LMR-240/LMR-200 pigtails
- Maintain at least 30–50 cm separation between antennas
- Simplest configuration, allows simultaneous operation

**Single Antenna with A/B Switch:**
- **SMA A/B coax switch (DC-pass on "A" side)** feeding single 915 MHz antenna
- Set A=Meshtastic or B=MeshCore; only one connected at a time
- Prevents TX collisions but requires manual/software switching

> ⚠️ **Important:** Avoid simple splitters/combiners for simultaneous TX — they can cause damage unless properly isolated and PTT-coordinated.

### Additional Dual LoRa Components

- **2× 915 MHz LoRa radios** (required - per chosen configuration above)
- **1× Powered USB 3.0 hub (uhubctl-compatible)** *or* **2× Inline USB on/off switches**
- **1× SMA A/B manual RF switch (DC-pass)** *or* **1× Second 915 MHz antenna**
- **2–4× SMA male–male coax jumpers** (0.3–0.5 m, 50 Ω)
- **1-2× 915 MHz rubber-duck or short omni antennas** *(qty depends on antenna strategy)*
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

*Last updated: 2025-10-09*
