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
| **LoRa / Meshtastic** | | | | |
| LoRa / Meshtastic | 1 | Waveshare | SX1262 915 MHz LoRa HAT (for Pi) | Pi-attached LoRa radio |
| LoRa / Meshtastic | 1 | ALFA Network | ARS-915P (SMA) | 915 MHz omni antenna |
| LoRa / Meshtastic | 1 | L-com / Times Microwave | LMR-240 SMA patch (~3 ft) | Short RF jumper inside case |
| LoRa / Meshtastic | 2 | LILYGO | T-Beam (ESP32 + SX1262) | Handheld companion nodes (BLE + GPS variants available) |
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

### Phase 4: TV & Radio Reception (Hardware to be Acquired) ❌
- Dual TV tuner and OTA antenna system
- Dual RTL-SDR setup for FM/NOAA reception

### Phase 5: LoRa Mesh Networking (Hardware to be Acquired) ❌
- Waveshare LoRa HAT and companion nodes
- 915 MHz antenna system

### Phase 6: Solar Power & Enclosure (Hardware to be Acquired) ❌
- Complete solar power system with battery
- Custom 3D printed weatherproof enclosure

---

For detailed technical specifications and wiring diagrams, see [wiring.md](wiring.md).

*Last updated: 2025-09-30*
