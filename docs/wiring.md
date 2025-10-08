# Prepper‑Pi Field Box

## ⚠️ DISCLAIMER
**I am not a licensed electrician.** This information reflects my understanding and personal experience, but I cannot guarantee that any design will work for your specific situation or be safe/compliant in your jurisdiction. **If you build this and something breaks, catches fire, or causes injury - that's on you.** Always consult qualified professionals and follow local electrical codes.

## 📋 PROJECT STATUS
**This is a future hardware design document.** Currently only Phase 1 (WiFi infrastructure) is currently deployed. Phases 4-6 (RF, LoRa, Solar/Power) are blocked pending hardware acquisition. See [../README.md](../README.md) for current project status and development phases.

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
│  🟠 LoRa branch (dual mesh - required)
│     🟠 Antenna A (915 MHz) ─▶ 🟠 bulkhead ▶ 🟠 short LMR to LoRa-A (Meshtastic)
│     🟠 Antenna B (915 MHz) ─▶ 🟠 bulkhead ▶ 🟠 short LMR to LoRa-B (MeshCore)
│       OR: Single antenna via A/B switch ─▶ 🟠 bulkhead ▶ 🟠 switch ▶ LoRa-A/B
│     🟠 Dual USB/HAT LoRa Radios ▶ 🟩 Pi 5 ▶ 💬 Mesh protocols (Web UI + MQTT optional)
│
│  🟩 Pi 5 roles: OpenWrt AP + Docker (Tvheadend, Icecast/Liquidsoap, Dual Mesh)
└───────────────────────────────────────────────────────────────────────────────────┘
```

## Enclosure & Thermal Management (Field Deployment)

For outdoor/zero-maintenance use, the project supports a sealed NEMA 4X/IP66 enclosure with an external heatsink and ePTFE pressure-equalization vent. The Pi’s heat is conducted through the enclosure wall to a fin stack outside; no dust filters or routine servicing are required. For cold/wet sites, a 10–20 W anti-condensation heater on a ~15 °C thermostat may be added.

See: [Weatherproof Enclosure Options](./enclosures.md).

### Concurrency
- 📺 **Two TV channels at once** (dual ATSC tuner).  
- 📻 **Two radio stations at once** (two RTL‑SDR dongles: FM + NOAA).  
- 💬 **Dual LoRa mesh protocols** (Meshtastic + MeshCore) with text/location sharing via Web UI on your local Wi‑Fi.

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
- **WiFi Adapter:** ALFA Network AWUS036ACM Long-Range Wide-Coverage Dual-Band AC1200 USB Wireless w/High-Sensitivity External Antenna

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

### LoRa (Phase 5 - Hardware to be Acquired)
- **Radios:** Dual setup required - 2× Waveshare SX1262 915 MHz LoRa HAT or USB LoRa modules
- **Antennas:** 1-2× ALFA Network ARS-915P (SMA) 915 MHz omni (qty depends on antenna strategy)
- **RF Jumpers:** 2× short LMR‑240 SMA patches (~3 ft) inside case for each radio
- **Companions:** 2× handheld LoRa nodes (LILYGO T‑Beam) for phone BLE pairing
- **Software:** Dual mesh protocols required - Meshtastic + MeshCore (Web UI + optional MQTT)

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
- **Dual LoRa Mesh**: Meshtastic + MeshCore services with Web UI (and MQTT if desired)  
- **OpenWrt** (router/AP) + captive landing page linking to Tvheadend, streams, and mesh protocols

---

## Safety & Compliance
- Observe regional **ISM band** limits (LoRa TX power/duty cycle).  
- Follow **NEC‑style** grounding practices; use proper weatherproofing and drip loops.  
- Verify **fuse sizes** match wire gauges and worst‑case load; place fuses close to the source.

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
> Replace `/path/...` with real host paths. Keep mesh protocol ports LAN‑only.

```yaml
version: "3.9"
services:
  meshtasticd:
    image: meshtastic/meshtasticd:latest
    container_name: meshtasticd
    restart: unless-stopped
    # USB LoRa A (change bus/device to match `ls -l /dev/serial/by-id`):
    devices:
      - /dev/bus/usb/001/006:/dev/bus/usb/001/006
    # For Waveshare SX1262 HAT instead, use:
    # devices:
    #   - /dev/spidev0.0:/dev/spidev0.0
    ports:
      - "127.0.0.1:4403:4403/tcp"   # Web UI (LAN only)
    networks:
      - meshtastic_net

  meshcore:
    image: meshcore/meshcore:latest
    container_name: meshcore
    restart: unless-stopped
    # USB LoRa B (change bus/device to match second LoRa radio):
    devices:
      - /dev/bus/usb/001/007:/dev/bus/usb/001/007
    ports:
      - "127.0.0.1:4404:4404/tcp"   # Web UI (LAN only)
    networks:
      - meshcore_net

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
  meshcore_net:
    driver: bridge
  tvheadend_net:
    driver: bridge
  icecast_net:
    driver: bridge
```

### Compose Notes
1. **Device paths:** Adjust `/dev/bus/usb/...` to match your system (`lsusb` or `/dev/serial/by-id/`). Use separate USB devices for dual LoRa setup.  
2. **Host volumes:** Replace `/path/...` with real directories for config and recordings.  
3. **Network security:** Bind sensitive services to `127.0.0.1` (LAN‑only) where shown.  
4. **RTL‑SDR:** Implementation pending hardware acquisition (Phase 4).
5. **Dual LoRa:** Configure separate USB ports/devices for Meshtastic and MeshCore radios.

---

## Clarifications & Notes

**Distribution Amp Input Voltage (CM‑3414):** Verify your unit's DC input spec. If it requires ~13–15 V, keep the dedicated regulator in the chain. If your model tolerates 12 V, you may feed it directly from the 12 V bus. Always keep the preamp **power inserter before** the distribution amp so DC reaches the mast preamp but not the amp outputs.

**USB Power Headroom:** Dual ATSC + 2× RTL‑SDR can exceed what the Pi can stably source under heat/load. If you encounter brownouts or tuner dropouts, insert a **powered USB 3.0 hub** for the capture devices.

**Inline Attenuators (SDR legs):** If you see ADC overload (clipping), insert **6 dB SMA attenuators** at the SDR inputs (after the 75 Ω→SMA adaptation).

**EMI/RFI Hygiene:** Add **ferrite snap‑on cores** to USB leads (SDRs/ATSC) and, where practical, to coax jumpers near the enclosure. Keep power pairs twisted and route RF away from DC switching paths.

**Bus Protection:** Add a **TVS diode** across the 12 V rails near the distribution block to clamp transients from switching or hot‑plug events.

**Weatherproofing:** At exterior bulkheads, apply **self‑fusing silicone tape** or use coax boots over F‑connectors and form **drip loops** before entry.

**Grounding (Field Use):** In portable scenarios without a permanent ground rod, enclosure bonding plus the gas discharge path of the arrestor helps but **is not a substitute for proper earthing**. Disconnect antennas during storms when practical.

---

## Dual LoRa Mesh Wiring (Meshtastic + MeshCore)

**Goal:** Run **two independent 915 MHz LoRa radios** for simultaneous **Meshtastic** and **MeshCore** operation, with easy toggling and clear RF isolation.

> **Required Configuration:** This build mandates **dual LoRa radios** for full mesh protocol support. Antenna configuration (1 or 2 antennas) remains flexible based on RF requirements and enclosure constraints.

### RF Topologies

**Option 1 — Two antennas (preferred for simplicity)**
- Antenna A → LoRa‑A (Meshtastic)
- Antenna B → LoRa‑B (MeshCore)
- Keep at least **30–50 cm** separation between antennas; more is better.
- Use **50 Ω** jumpers (LMR‑200/240, SMA male‑male, 0.3–0.5 m).

**Option 2 — Single antenna via SMA A/B switch (manual)**
```
[915 MHz Antenna]
        │
   [SMA A/B Switch]──A──> LoRa‑A (Meshtastic)
                     └──B─> LoRa‑B (MeshCore)
```
- Only **one radio** is connected to the antenna at a time → prevents TX collisions.
- Choose an A/B switch rated for UHF with **low insertion loss**; DC‑pass on at least one throw is handy if you ever insert an inline LNA (not required for baseline).

> ⚠️ **Warning:** Avoid simple splitters/combiners unless you have proper TX isolation and coordination—simultaneous TX can damage hardware.

### Physical/Power Layout

**USB Radios (ESP32+SX1262/1276):**
- Plug into a **powered USB 3.0 hub**; label the ports: **LoRa‑A** and **LoRa‑B**.
- Optionally use **inline USB on/off switches** for manual control.
- For software control, use a hub that works with **uhubctl** (per‑port power).

**Pi HAT Radios (SX1262):**
- Use **standoffs** for stacking/clearance; route short SMA pigtails to bulkhead.
- For on/off, add a **2‑channel DC load‑switch/relay** to cut radio Vcc (GPIO‑controlled).
- Label PCB headers/cables to prevent cross‑wiring between A and B.

### Grounding & EMC
- Maintain **single‑point ground** (enclosure, arrestor, DC‑ bus). Keep RF jumpers short.
- Add **ferrite snap‑ons** to USB leads near the SDR/LoRa radios to curb common‑mode noise.
- Keep RF (LoRa/ATSC/SDR) away from buck converters and high‑di/dt DC wiring.

### Software & Labels
- Assign clear identities:
  - **LoRa‑A** → Meshtastic
  - **LoRa‑B** → MeshCore
- If using a single antenna with A/B switch, add a simple **toggle script** to ensure only the intended radio is powered before flipping the switch.

### Example: uhubctl toggle scripts (per‑port power)
> Replace `BUS=1`, `PORT_A=2`, `PORT_B=3` with your actual hub bus/port numbers (`uhubctl` will list them).

```bash
#!/usr/bin/env bash
# lora-switch.sh
set -euo pipefail
BUS="${BUS:-1}"
PORT_A="${PORT_A:-2}"   # Meshtastic
PORT_B="${PORT_B:-3}"   # MeshCore

usage(){ echo "Usage: $0 {A|B|off}"; exit 1; }
[[ $# -eq 1 ]] || usage

case "$1" in
  A|a)
    uhubctl -l $BUS -p $PORT_B -a off || true   # ensure B is off
    uhubctl -l $BUS -p $PORT_A -a on
    echo "LoRa-A (Meshtastic) ON, LoRa-B OFF"
    ;;
  B|b)
    uhubctl -l $BUS -p $PORT_A -a off || true
    uhubctl -l $BUS -p $PORT_B -a on
    echo "LoRa-B (MeshCore) ON, LoRa-A OFF"
    ;;
  off)
    uhubctl -l $BUS -p $PORT_A -a off || true
    uhubctl -l $BUS -p $PORT_B -a off || true
    echo "Both LoRa radios OFF"
    ;;
  *)
    usage
    ;;
esac
```

> **Tip:** Pair this with systemd services or a tiny web button on your admin UI so you can switch roles without SSHing into the Pi.

*Last updated: 2025-10-07*
