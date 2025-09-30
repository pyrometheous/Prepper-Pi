# Wireless Configuration Notes

This directory does NOT contain a wireless config file by design.

**Why no wireless config file?**
- OpenWRT needs actual hardware device paths (not placeholders like 'auto-detect')
- Radio paths are different on each Pi and depend on specific WiFi hardware
- Bootstrap script generates correct config with `wifi config` then applies our settings

**What happens on first boot:**
1. Bootstrap runs `wifi config` to detect actual radio hardware and paths
2. Script applies our SSID names and WPA2 settings via UCI commands
3. WiFi radios come up with correct device-specific configuration

**To see the generated config:**
```bash
docker exec -it openwrt uci show wireless
```

**To modify settings:**
Edit the UCI commands in `bootstrap.sh` rather than creating a static file.

This approach ensures compatibility across different WiFi adapters and Pi hardware.
