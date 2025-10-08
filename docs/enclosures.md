# Weatherproof Enclosure Options (Prepper-Pi)

> Goal: Zero-maintenance, deploy-anywhere (CONUS climates), safe in rain/spray/dust, with reliable cooling for a Raspberry Pi 5 + RF gear.

## TL;DR
Use a sealed NEMA 4X/IP66 polycarbonate enclosure with a through-wall thermal path to an external finned heatsink, plus an ePTFE pressure-equalization vent and (optionally) a mini anti-condensation heater. Power via PoE→5 V so only one outdoor cable is needed.

---

## Option A — Sealed + External Heatsink

What: Keep the box fully sealed. Move heat to the outside via a thermal bridge (internal aluminum plate and thermal pad/epoxy) bolted to an external finned heatsink.

Why: High ingress protection; no dust filters to service; suitable for hot/cold/humid zones.

Core BOM
- Enclosure: Polycarbonate NEMA 4X / IP66 (≈ 300×200×150 mm; light color).
- External heatsink: ≈ 200×150×25 mm, vertical fins.
- Thermal bridge: 3–4 mm internal aluminum transfer plate + 1–2 mm high-conductivity pad (≥6 W/m·K) or thin thermal epoxy at wall interface.
- Pi cooler: Low-profile heat-pipe/vapor-chamber on the Pi 5; mechanically coupled to the transfer plate (short heat path).
- Pressure-equalization vent: ePTFE screw-in vent (M12), mounted low on a side wall.
- (Optional) Anti-condensation heater: 10–20 W mini enclosure heater with ~15 °C thermostat; mount low.
- Power: PoE (802.3at) → 5 V/5 A industrial splitter (USB-C to Pi).
- Penetrations: IP68 cable glands (bottom face), RF bulkhead pass-throughs (SMA/N) with gaskets.
- Moisture indicators: Silica gel packs + humidity card (door-side).

Layout Notes
1. Mount external fins vertical, shaded if possible; standoff the box by 10–20 mm for airflow wash.
2. Put the ePTFE vent on a side wall near the bottom (splash-protected).
3. Keep RF coax runs short; cross PoE and RF at 90° if needed.
4. Bond enclosure ground and use an in-line PoE surge protector at entry.

---

## Option B — “Breathing” (Vented Membrane + Fans)

What: IP55–IP65 enclosure with hydrophobic ePTFE vent media panels and PWM fans (intake/exhaust) creating slight positive pressure.

Why: Can achieve lower internal temperatures in high-load/hot ambients.  
Trade-offs: Filters eventually need cleaning; not ideal for direct driving rain or fine dust over long unattended periods.

Use when: You accept annual service for filters and expect very hot, continuous load operation.

---

## Option C — Sealed + Mini Heat-Exchanger

What: A compact air-to-air cabinet heat-exchanger (two isolated paths) or pass-through heat pipes with an internal blower.

Why: Strong thermal performance while staying IP66.  
Trade-offs: Cost/complexity; sourcing the exchanger.

---

## Sizing & Thermal Targets

- Pi 5 + radios typical: 8–15 W sustained; plan for 20–25 W peak.
- Target CPU: <70 °C under worst-case ambient/sun.  
- If CPU >70 °C sustained on Option A, upsize the heatsink or add a quiet 40–60 mm internal fan to stir air over the plate.

---

## Drill/Cut Template (Option A)

1. Heatsink mount: 4–6× M4/M5 through-holes per your sink’s pattern on a side or rear wall (not the lid). No big cutout; just a flat-to-flat bolted interface with pad/epoxy.
2. Vent: 1× M12 threaded hole for the ePTFE vent on a side wall near the bottom.
3. Glands: Bottom face for Ethernet/PoE and DC as needed; ensure drip loops outside.
4. Bulkheads: SMA/N pass-throughs for antennas with rubber washers; weather-wrap externally.

Tip: Lightly grease door gasket; torque latches evenly.

---

## Condensation Control

- ePTFE vent prevents baro-pumping through gaskets.  
- Silica gel + humidity card for maintenance at a glance.  
- Mini heater (10–20 W) on a snap-disc (~15 °C) if night RH spikes or cold/wet sites are expected.

---

## Grounding & Protection

- Single-point bond: enclosure, arrestors, DC negative/ground bar.  
- PoE surge protector at entry; arrestors on RF/coax where applicable.  
- Portable field use: bonding helps but is not a substitute for a proper ground rod—disconnect antennas during storms when practical.

---

## Deployment Checklist

- [ ] Mount shaded or under a small hood; keep external fins vertical/clear.  
- [ ] Verify humidity card after first warm-up; swap desiccant if needed.  
- [ ] Confirm PoE link + 5 V load headroom (≥5 A typical).  
- [ ] Label RF bulkheads (“LoRa-A”, “LoRa-B”, “ATSC”, “SDR-FM/NOAA”).  
- [ ] Add internal temp/RH sensor and surface it in the dashboard.

---

## Where this connects in the repo

- Components: See updated Enclosure & Hardware items in components.md (this branch).  
- Wiring: See new Enclosure & Thermal Management note in wiring.md linking back here.

Document version: 2025-10-08
