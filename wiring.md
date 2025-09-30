# Prepper‑Pi Field Box

## ⚠️ DISCLAIMER
**I am not a licensed electrician.** This information reflects my understanding and personal experience, but I cannot guarantee that any design will work for your specific situation or be safe/compliant in your jurisdiction. **If you build this and something breaks, catches fire, or causes injury - that's on you.** Always consult qualified professionals and follow local electrical codes.

## 📋 PROJECT STATUS
**This is a future hardware design document.** Currently only Phase 1 (WiFi infrastructure) hardware is owned and deployed. Phases 4-6 (RF, LoRa, Solar/Power) are blocked pending hardware acquisition. See [README.md](README.md) for current project status and development phases.

## Legend
🔴 DC power · 🔵 75 Ω TV coax (RG‑6) · 🟠 50 Ω RF (LMR‑240/400) · 🟩 USB/Ethernet/Data · ⚫ Ground/Bond  
🧱 metal partition · 📦 enclosure wall/bulkhead · 🚧 fuse · 🔌 power inserter · 🛡️ lightning arrestor  
☀️ solar panel · 🔋 battery · 🔧 regulator/converter · 📡 antenna · 🎚️ amplifier · 📶 distribution amp  
📻 radio/SDR · 📺 TV tuner · 💬 LoRa/mesh · 🚫 filter/notch · 📱 client device · 🎵 audio stream  
🌧️ weather data · 🔵 spare output

## ⚠️ SAFETY DISCLAIMER
**This guide is for educational purposes.** Building electrical systems involves risks including fire, shock, and injury. 
- **Consult local codes** - electrical work may require permits and professional installation
- **Use proper PPE** - safety glasses, insulated tools, etc.
- **Verify all connections** before applying power
- **When in doubt, consult a qualified electrician**
- The authors assume no responsibility for damage, injury, or regulatory violations

---

## System Diagram

```
┌─────────────────────────────── Power Compartment ────────────────────────────────┐
│
│   ☀️  Solar Panel
│     🔴──────▶ 📦 MC4 bulkhead ▶ 🔧 MPPT (75/15)
│                           🔴▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶🔴
│                                      │
│                                      ▼
│                                🔋 12 V LiFePO₄
│                                      │
│       (preamp feed) ──▶ 🔴 12–15 V ─▶ 🔌 Power Inserter (to OTA coax)
│                                      │
│           loads bus  ──▶ 🔴 Fused 12 V DC Distribution
│                                      ├─▶ 🔧 12→5 V Buck (5 V/5 A) ─▶🟩 Pi 5 USB-C
│                                      └─▶ 🔴 13.2 V Reg  ─▶ 📶 Distribution Amp
│
│  ⚫ Ground Rod ───▶ ⚫ Bonding bar  ──┬─▶ ⚫ MPPT/- batt
│                                      ├─▶ ⚫ Coax Ground Block/Arrestor
│                                      └─▶ ⚫ Enclosure/Partition
└───────────────────────────────────────────────────────────────────────────────────┘
 ──────────────────────────────🧱 metal partition🧱────────────────────────────────
┌──────────────────────────── RF & Compute Compartment ─────────────────────────────┐
│
│  📡 OTA Antenna (VHF‑Hi/UHF)
│    🔵─▶ 🎚️ Mast Preamp (CM‑7777HD; FM trap as needed; LTE filt)
│    🔵─▶ 🛡️ Coax Arrestor + Ground Block (at entry
│    🔵─▶ 🔌 Power Inserter (from 12–15 V)
│    🔵─▶ 📶 4‑Port 75 Ω Distribution Amp (CM‑3414)
│             │  │  │  │
│             │  │  │  └──▶ 🔵 Spare Out
│             │  │  │
│             │  │  └──▶ 🔵▶ SMA pigtail ▶ 🚫🎚️ FM-Notch
│             │  │                                     ▶ 📻 RTL-SDR #2
│             │  │                                     ▶ 🟩 Icecast
│             │  │                                     ▶ 🌧️ NOAA Wx
│             │  │
│             │  └──▶ 🔵▶ SMA pigtail ▶ 📻 RTL-SDR #1 ▶ 🟩 Icecast ▶ 🎵 FM
│             │
│             └──▶ 🔵▶ 📺 USB ATSC **Dual** Tuner ▶ 🟩 Pi 5 ▶ 🟩 Tvheadend ▶ 📱 Clients
│
│  🟠 LoRa branch
│     🟠 Antenna (915 MHz omni on mast) ─▶ 🟠 bulkhead ▶ 🟠 short LMR to
│     🟠 USB/HAT LoRa Radio ▶ 🟩 Pi 5 ▶ 💬 meshtasticd (Web UI + MQTT optional)
│
│  🟩 Pi 5 roles: OpenWrt AP + Docker (Tvheadend, Icecast/Liquidsoap, Meshtastic)
└───────────────────────────────────────────────────────────────────────────────────┘
```

### Concurrency
- 📺 **Two TV channels at once** (dual ATSC tuner).  
- 📻 **Two radio stations at once** (two RTL‑SDR dongles: FM + NOAA).  
- 💬 LoRa mesh text/location via Meshtastic Web on your local Wi‑Fi.

---

## Detailed Wiring Notes
1. **Preamp power:** Place the 🔌 *power inserter before* the 📶 distribution amp so DC reaches the mast preamp.  
2. **Impedance domains:** Keep 🔵 *75 Ω TV coax* separate from 🟠 *50 Ω RF*. Adapt to SMA right at the SDR inputs.  
3. **Power rails:** Feed the Pi from a **5 V/5 A buck** on the 12 V battery bus. Fuse every branch (🚧) close to the source.  
4. **Grounding:** Bond MPPT, battery negative, arrestor, case, and partition to a single **ground point**; tie to a **ground rod** when practical.  
5. **EMI hygiene:** Twist PV and battery leads, add ferrites near switchers, route RF coax away from the MPPT/buck.  
6. **Antenna placement:** Height & clear line‑of‑sight matter more than raw gain. Keep internal LoRa jumpers short.

---

## Components (Example Bill of Materials)
> **IMPORTANT: This is a future hardware design.** Most components listed are not yet acquired (see README.md project phases). Specifications reflect planned hardware for Phases 4-6.

### Compute & Core (Phase 1 - Currently Owned)
- Raspberry Pi 5 (8 GB) + Official 27 W USB‑C PSU (or 5 V/5 A buck when solar is added)  
- Pi 5 Active Cooler  
- NVMe storage (M.2 via Pi M.2 HAT+, 512 GB) - *may upgrade to 1TB for media storage*

### RF — TV (75 Ω path) (Phase 4 - Hardware to be Acquired)
- **Antenna:** Antennas Direct ClearStream 2MAX (VHF‑Hi/UHF) or similar compact OTA  
- **Mast Preamp:** Channel Master CM‑7777HD (FM trap switchable, LTE filtered) + **🔌 Power Inserter**  
- **Protection:** 75 Ω F‑F coax lightning arrestor + ground block at entry  
- **Distribution:** Channel Master CM‑3414 (4‑port, +~8 dB/port) or comparable distro amp  
- **Tuners:** Hauppauge WinTV‑dualHD (USB **dual** ATSC)  
- **Cables/Adapters:** RG‑6 quad‑shield; F‑female ⇄ SMA‑male pigtails for SDR legs

### RF — Radio & SDR (50 Ω legs off distro) (Phase 4 - Hardware to be Acquired)
- **RTL‑SDR x2:** RTL‑SDR Blog V4 (dongle‑only)  
- **Filter for NOAA leg:** FM band‑stop/notch (88–108 MHz) inline ahead of RTL‑SDR #2  
- **(Optional)** inline attenuators (3–10 dB) if overload appears

### LoRa / Meshtastic (Phase 5 - Hardware to be Acquired)
- **Radio on Pi:** Waveshare SX1262 915 MHz LoRa HAT (for Pi)
- **Antenna:** ALFA Network ARS-915P (SMA) 915 MHz omni on mast; short LMR‑240 jumpers inside case  
- **Companions:** 1–2 handheld Meshtastic nodes (LILYGO T‑Beam) for phone BLE pairing
- **Software:** `meshtasticd` (+ Web UI, optional MQTT)

### Power / Solar / UPS (Phase 6 - Hardware to be Acquired)
- **Battery:** LiTime 12 V 50 Ah LiFePO₄ (may scale to 100Ah based on runtime requirements)  
- **Charge Controller:** Victron SmartSolar **MPPT 75/15** (Bluetooth)  
- **Panel:** Renogy 100 W 12 V monocrystalline (foldable or rigid)  
- **DC‑DC:** Pololu D24V50F5 (5 V/5 A buck) for Pi; optional 13.2 V regulator for distro amp  
- **Distribution:** Anderson Powerpole connectors, inline ATO/ATC fuse holders, master disconnect  
- **Grounding/Lightning:** arrestors, bonding straps, ground rod (camp or base station)

### Enclosure & Hardware (Phase 6 - Custom Design)
- **Custom 3D printed enclosure** (weather-resistant, designed with friend's assistance)  
- **Metal partition** (🧱) between power and RF bays with adequate ventilation
- **Bulkhead feed‑throughs:** MC4 (PV), F‑female (TV), SMA/N (RF), cable glands for DC/USB/Ethernet  
- **12V case fans** + grills for thermal management

---

## Optional Software Stack (Docker)
- **Tvheadend**: live TV backend (uses dual ATSC USB tuner)  
- **Icecast + rtl_fm/Liquidsoap**: FM & NOAA audio streams for phones on LAN  
- **Meshtasticd**: LoRa mesh service with Web UI (and MQTT if desired)  
- **OpenWrt** (router/AP) + captive landing page linking to Tvheadend, streams, and Meshtastic

---

## Safety & Compliance
- Observe regional **ISM band** limits (LoRa TX power/duty cycle).  
- Follow **NEC‑style** grounding practices; use proper weatherproofing and drip loops.  
- Verify **fuse sizes** match wire gauges and worst‑case load; place fuses close to the source.

---

*Last updated:* 2025-09-30


---

## Fuse & Wire Gauge Table (12 V DC side)

> **CRITICAL:** These values are conservative and assume short runs (≤2 m inside the box).  
> **Size fuses to protect the wire** (not the device). Place fuses **close to the source**.
> **These are future hardware specifications** - see project status above.

| Branch / Load                               | Nominal V | Est. Max A | Suggested Wire | Fuse (ATO/ATC) | Notes |
|---|---:|---:|---|---:|---|
| **Battery → Master bus**                    | 12–14 V   | 20–30 A    | **AWG 10**     | **30 A**       | Main feed to DC dist. Keep as short as practical. |
| **PV panel (+) → MPPT PV+**                 | 18–22 V   | 6–8 A      | **AWG 14**     | **10 A** (inline MC4) | One fuse per series string. |
| **MPPT → Battery (+)**                      | 12–14 V   | ≤15 A      | **AWG 12**     | **15 A**       | Fuse at battery end. Critical safety circuit. |
| **Bus → 12→5 V Buck (Pi 5)**                | 12–14 V   | 4–5 A      | **AWG 16**     | **5 A**        | Buck input fuse; use quality converter with OCP. |
| **Bus → 13.2 V Reg (TV distro amp)**        | 12–14 V   | 0.6–1.0 A  | **AWG 18**     | **2 A**        | Some amps accept 12 V directly; if so, skip the reg. |
| **Bus → Preamp power inserter**             | 12–15 V   | 0.2–0.5 A  | **AWG 20**     | **1 A**        | Inserter feeds DC up the RG‑6 to the mast LNA. |
| **Bus → Case fans / aux**                   | 12 V      | 0.3–0.6 A  | **AWG 20**     | **1 A**        | Grouped on a small fan header board is fine. |
| **Ground bond (case/partition/arrestor)**   | —         | —          | **AWG 8 strap**| —              | Single-point bond; tie to ground rod when practical. |

> **USB Loads:** Tuners/SDRs draw from the Pi's 5 V rail; ensure your 5 V/5 A buck is high‑quality and the Pi's USB supply setting is configured to allow high‑power devices.

---

## Docker Compose (template)

> **NOTE:** This is for future phases when hardware is acquired.  
> Currently only basic WiFi infrastructure (Phase 1) is deployed.  
> Replace `/path/...` with real host paths. Keep Meshtastic ports LAN‑only.

```yaml
version: "3.9"
services:
  meshtasticd:
    image: meshtastic/meshtasticd:latest
    container_name: meshtasticd
    restart: unless-stopped
    # USB LoRa (change bus/device to match `ls -l /dev/serial/by-id`):
    devices:
      - /dev/bus/usb/001/006:/dev/bus/usb/001/006
    # For Waveshare SX1262 HAT instead, use:
    # devices:
    #   - /dev/spidev0.0:/dev/spidev0.0
    ports:
      - "127.0.0.1:4403:4403/tcp"   # Web UI (LAN only)
    networks:
      - meshtastic_net

  tvheadend:
    image: linuxserver/tvheadend:latest
    container_name: tvheadend
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/New_York
    volumes:
      - /path/to/tvheadend/config:/config
      - /path/to/tvheadend/recordings:/recordings
    # USB ATSC tuner (Hauppauge dualHD):
    devices:
      - /dev/bus/usb/001/007:/dev/bus/usb/001/007
    ports:
      - "9981:9981"   # Web UI
      - "9982:9982"   # HTSP
    networks:
      - tvheadend_net

  # RTL-SDR services (for future implementation)
  icecast:
    image: moul/icecast
    container_name: icecast
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ICECAST_SOURCE_PASSWORD=hackme
      - ICECAST_ADMIN_PASSWORD=hackme
      - ICECAST_PASSWORD=hackme
    networks:
      - icecast_net

networks:
  meshtastic_net:
    driver: bridge
  tvheadend_net:
    driver: bridge
  icecast_net:
    driver: bridge
```

### Compose Notes
1. **Device paths:** Adjust `/dev/bus/usb/...` to match your system (`lsusb` or `/dev/serial/by-id/`).  
2. **Host volumes:** Replace `/path/...` with real directories for config and recordings.  
3. **Network security:** Bind sensitive services to `127.0.0.1` (LAN‑only) where shown.  
4. **RTL‑SDR:** Implementation pending hardware acquisition (Phase 4).

---

*Appendix updated:* 2025-09-30
