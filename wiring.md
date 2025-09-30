# Prepper‑Pi Field Box

## ⚠️ DISCLAIMER
**I am not a licensed electrician.** This information reflects my understanding and personal experience, but I cannot guarantee that any design will work for your specific situation or be safe/compliant in your jurisdiction. **If you build this and something breaks, catches fire, or causes injury - that's on you.** Always consult qualified professionals and follow local electrical codes.

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
│                           🔴▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶🔴                              │
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
│    🔵─▶ 📶 4‑Port 75 Ω Distribution Amp (CM‑3414)
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
2. **Impedance domains:** Keep 🔵 *75 Ω TV coax* separate from 🟠 *50 Ω RF*. Adapt to SMA right at the SDR inputs.  
3. **Power rails:** Feed the Pi from a **5 V/5 A buck** on the 12 V battery bus. Fuse every branch (🚧) close to the source.  
4. **Grounding:** Bond MPPT, battery negative, arrestor, case, and partition to a single **ground point**; tie to a **ground rod** when practical.  
5. **EMI hygiene:** Twist PV and battery leads, add ferrites near switchers, route RF coax away from the MPPT/buck.  
6. **Antenna placement:** Height & clear line‑of‑sight matter more than raw gain. Keep internal LoRa jumpers short.

---

## Components (Example Bill of Materials)
> Substitute brands are fine; these are pairings from my design, your milage may varry.

### Compute & Core
- Raspberry Pi 5 (8 GB) + Official 27 W USB‑C PSU (or your 5 V/5 A buck)  
- Pi 5 Active Cooler  
- NVMe storage (M.2 via Pi M.2 HAT+, e.g., 512 GB)

### RF — TV (75 Ω path)
- **Antenna:** Antennas Direct ClearStream 2MAX (VHF‑Hi/UHF) or similar compact OTA  
- **Mast Preamp:** Channel Master CM‑7777HD (FM trap switchable, LTE filtered) + **🔌 Power Inserter**  
- **Protection:** 75 Ω F‑F coax lightning arrestor + ground block at entry  
- **Distribution:** Channel Master CM‑3414 (4‑port, +~8 dB/port) or comparable distro amp  
- **Tuners:** Hauppauge WinTV‑dualHD (USB **dual** ATSC)  
- **Cables/Adapters:** RG‑6 quad‑shield; F‑female ⇄ SMA‑male pigtails for SDR legs

### RF — Radio & SDR (50 Ω legs off distro)
- **RTL‑SDR x2:** RTL‑SDR Blog V4 (dongle‑only)  
- **Filter for NOAA leg:** FM band‑stop/notch (88–108 MHz) inline ahead of RTL‑SDR #2  
- **(Optional)** inline attenuators (3–10 dB) if overload appears

### LoRa / Meshtastic
- **Radio on Pi:** SX1262‑based HAT **or** USB LoRa stick (US 915 MHz)  
- **Antenna:** 915 MHz omni on mast; short LMR‑240/400 jumpers inside the case  
- **Companions:** 1–2 handheld Meshtastic nodes (e.g., LILYGO T‑Beam) for phone BLE pairing
- **Software:** `meshtasticd` (+ Web UI, optional MQTT)

### Power / Solar / UPS
- **Battery:** 12 V LiFePO₄ (size to your runtime: 40–100 Ah typical)  
- **Charge Controller:** Victron SmartSolar **MPPT 75/15** (Bluetooth)  
- **Panel:** 100–150 W monocrystalline (MC4)  
- **DC‑DC:** 12→5 V/5 A buck regulator for Pi; 13.2 V regulator for distro amp (if needed)  
- **Distribution:** fused panel (Powerpole/XT60), inline fuses sized to wire & load, master disconnect  
- **Grounding/Lightning:** arrestors, bonding straps, ground rod (camp or base station)

### Enclosure & Hardware
- Weather‑resistant case (APACHE 2800 / Pelican 1200 class)  
- Bulkhead feed‑throughs: MC4 (PV), F‑female (TV), SMA/N (RF), gland nuts for DC/USB/Ethernet  
- Metal partition (🧱) between power and RF bays; ventilation as needed

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

## Fuse & Wire Gauge Table (12 V DC side)

> These values are conservative and assume short runs (≤1–2 m inside the box).  
> Size fuses to **protect the wire** (not the device). Place fuses **close to the source**.

| Branch / Load                               | Nominal V | Est. Max A | Suggested Wire | Fuse (ATO/ATC) | Notes |
|---|---:|---:|---|---:|---|
| **Battery → Master bus**                    | 12–14 V   | 20–30 A    | **AWG 10**     | **30 A**       | Main feed to DC dist. Keep as short as practical. |
| **PV panel (+) → MPPT PV+**                 | 18–22 V   | 6–8 A      | **AWG 14**     | **10 A** (inline MC4) | One fuse per series string. |
| **MPPT → Battery (+)**                      | 12–14 V   | ≤15 A      | **AWG 12**     | **20 A**       | Fuse at battery end. |
| **Bus → 12→5 V Buck (Pi 5)**                | 12–14 V   | 3–4 A      | **AWG 16**     | **5 A**        | Buck input fuse; keep 5 V leads short/thick. |
| **Bus → 13.2 V Reg (TV distro amp)**        | 12–14 V   | 0.6–1.0 A  | **AWG 18**     | **2 A**        | Some amps accept 12 V directly; if so, skip the reg. |
| **Bus → Preamp power inserter**             | 12–15 V   | 0.2–0.5 A  | **AWG 20**     | **1 A**        | Inserter feeds DC up the RG‑6 to the mast LNA. |
| **Bus → Case fans / aux**                   | 12 V      | 0.3–0.6 A  | **AWG 20**     | **1 A**        | Grouped on a small fan header board is fine. |
| **Ground bond (case/partition/arrestor)**   | —         | —          | **AWG 8 strap**| —              | Single-point bond; tie to ground rod when practical. |

> **USB Loads:** Tuners/SDRs draw from the Pi’s 5 V rail; ensure your 5 V/5 A buck is high‑quality and the Pi’s USB supply setting is configured to allow high‑power devices.

---

## Docker Compose (template)

> This focuses on the services we know work broadly.  
> Icecast/rtl_fm are provided as an **optional pattern** (pick your preferred images).  
> Replace `/path/...` with real host paths. Keep Meshtastic ports LAN‑only.

```yaml
version: "3.9"
services:
  meshtasticd:
    image: meshtastic/meshtasticd:latest
    container_name: meshtasticd
    restart: unless-stopped
    # Choose ONE of the following device blocks:
    # USB LoRa (change bus/device to match `ls -l /dev/serial/by-id` or /dev/bus/usb):
    devices:
      - /dev/bus/usb/001/006:/dev/bus/usb/001/006
    # For an SPI HAT instead, use:
    # devices:
    #   - /dev/spidev0.0:/dev/spidev0.0
    ports:
      - "2443:2443"  # Meshtastic Web UI (HTTPS)
      - "4403:4403"  # TCP device API
    volumes:
      - /path/meshtastic/config.yaml:/etc/meshtasticd/config.yaml:ro

  mosquitto:
    image: eclipse-mosquitto:2
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"
    volumes:
      - /path/mosquitto:/mosquitto

  tvheadend:
    image: lscr.io/linuxserver/tvheadend:latest
    container_name: tvheadend
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Los_Angeles
    # If your kernel exposes /dev/dvb, this gives Tvheadend the tuner:
    devices:
      - /dev/dvb:/dev/dvb
    ports:
      - "9981:9981"  # web UI
      - "9982:9982"  # HTSP
    volumes:
      - /path/tvheadend/config:/config
      - /path/tvheadend/recordings:/recordings

  # --- Optional: Icecast + radio streams (choose images you prefer) ---
  # Example images you can try: 'infiniteproject/icecast', 'pdonorio/icecast2', etc.
  # icecast:
  #   image: YOUR_ICECAST_IMAGE_HERE
  #   container_name: icecast
  #   restart: unless-stopped
  #   ports:
  #     - "8000:8000"
  #   environment:
  #     - ICECAST_SOURCE_PASSWORD=sourcepass
  #     - ICECAST_ADMIN_PASSWORD=adminpass
  #     - ICECAST_RELAY_PASSWORD=relaypass
  #     - ICECAST_PASSWORD=listeners
  #   volumes:
  #     - /path/icecast:/config

  # FM stream (rtl_fm -> Icecast) pattern using a minimal SDR image or your own build.
  # rtl_fm_fm:
  #   image: ghcr.io/YOUR_SDR_IMAGE   # or build: ./containers/rtl-fm
  #   container_name: rtl_fm_fm
  #   restart: unless-stopped
  #   devices:
  #     - /dev/bus/usb:/dev/bus/usb
  #   depends_on: [icecast]
  #   command: >
  #     bash -lc "rtl_fm -M wbfm -f 99.5M -s 200k -l 0 -g 20 |
  #               sox -t raw -r 200k -e s -b 16 -c 1 - -t mp3 -C 128 - |
  #               curl -H 'Content-Type: audio/mpeg' -u source:sourcepass
  #               --data-binary @- http://icecast:8000/fm.mp3"

  # NOAA stream:
  # rtl_fm_noaa:
  #   image: ghcr.io/YOUR_SDR_IMAGE
  #   container_name: rtl_fm_noaa
  #   restart: unless-stopped
  #   devices:
  #     - /dev/bus/usb:/dev/bus/usb
  #   depends_on: [icecast]
  #   command: >
  #     bash -lc "rtl_fm -M fm -f 162.550M -s 24k -g 20 -l 0 |
  #               sox -t raw -r 24k -e s -b 16 -c 1 - -t mp3 -C 64 - |
  #               curl -H 'Content-Type: audio/mpeg' -u source:sourcepass
  #               --data-binary @- http://icecast:8000/noaa.mp3"
```

### Compose Notes
- Map **/dev/dvb** for the ATSC dual tuner; for RTL‑SDR, map **/dev/bus/usb** to the SDR containers.  
- Keep Meshtastic ports LAN‑only (do not expose to WAN). Add a DNS entry like `mesh.prepper-pi.local`.  
- For Icecast, choose a maintained image and secure the passwords; the command lines above show the **pattern** to publish FM/NOAA streams.

---

*Appendix updated:* 2025-09-30
