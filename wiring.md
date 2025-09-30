
# Prepper‑Pi Field Box
**TV / Radio / Wi‑Fi / LoRa + Solar‑UPS — Wiring & Components**  
*(README-ready, emoji-friendly, copy‑pasteable.)*

---

## Legend
🔴 DC power · 🔵 75 Ω TV coax (RG‑6) · 🟠 50 Ω RF (LMR‑240/400) · 🟩 USB/Ethernet/Data · ⚫ Ground/Bond  
🧱 metal partition · 📦 enclosure wall/bulkhead · 🚧 fuse · 🔌 power inserter · 🛡️ lightning arrestor

---

## System Diagram (Text/Emoji)

```
┌─────────────────────────────── Power Compartment ───────────────────────────────┐
│                                                                                │
│  ☀️  Solar Panel                                                                │
│    🔴──▶ 📦 MC4 bulkhead ─▶ 🔧 MPPT (Victron SmartSolar 75/15)                   │
│                              │                                                 │
│                              ▼                                                 │
│                         🔋 12 V LiFePO₄ (40–100 Ah)                             │
│                              │                                                 │
│   Preamp DC feed ──▶ 🔴 12–15 V ─▶ 🔌 Power Inserter (to OTA coax)              │
│                              │                                                 │
│   12 V loads bus ──▶ 🔴 DC Distribution (🚧 fuses on each branch)                │
│                              ├─▶ 🔧 12→5 V Buck (5 V/5 A) ─▶ 🟩 Pi 5 USB‑C        │
│                              └─▶ 🔴 13.2 V Reg ─▶ 📶 4‑Port Distribution Amp     │
│                                                                                │
│  ⚫ Ground Rod ─▶ ⚫ Bonding bar ─┬─▶ ⚫ MPPT & Battery −                         │
│                                  ├─▶ ⚫ Coax Ground Block/Arrestor              │
│                                  └─▶ ⚫ Enclosure & 🧱 Partition                  │
└───────────────────────────────🧱 metal partition🧱───────────────────────────────┘

┌──────────────────────────── RF & Compute Compartment ───────────────────────────┐
│                                                                                │
│  📡 OTA Antenna (VHF‑Hi/UHF)                                                   │
│    🔵─▶ 🎚️ Mast Preamp (CM‑7777HD; FM trap as needed; LTE filt)                 │
│    🔵─▶ 🛡️ Coax Arrestor + Ground Block (at entry)                              │
│    🔵─▶ 🔌 Power Inserter (from 12–15 V)                                        │
│    🔵─▶ 📶 4‑Port 75 Ω Distribution Amp (CM‑3414)                                │
│           │                 │                 │                 │              │
│           │                 │                 │                 └─▶ 🔵 Spare    │
│           │                 │                                                    
│           │                 └─▶ 🔵 ▶ F→SMA ▶ 🚫🎚️ FM‑Notch ▶ 📻 RTL‑SDR #2 ▶ NOAA  │
│           │                                                                      
│           └─▶ 🔵 ▶ F→SMA ▶ 📻 RTL‑SDR #1 ▶ FM stream (Icecast/Liquidsoap)        │
│                                                                                  │
│  📺 TV: 🔵 ▶ USB ATSC **Dual** Tuner (Hauppauge dualHD) ▶ 🟩 Pi 5 ▶ Tvheadend     │
│                                                                                  │
│  🟠 LoRa: 🟠 915 MHz Omni (mast) ─▶ 🟠 bulkhead ─▶ 🟠 short LMR ─▶                 │
│           🟠 USB/HAT LoRa Radio (SX1262 class) ▶ 🟩 Pi 5 ▶ 💬 meshtasticd         │
│                                                                                  │
│  🟩 Pi 5 roles: OpenWrt AP + Docker (Tvheadend, Icecast/Liquidsoap, Meshtastic)  │
└──────────────────────────────────────────────────────────────────────────────────┘
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
> Substitute brands are fine; these are proven pairings from our design.

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
