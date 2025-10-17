<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Quick Deploy Checklist

## Pre-Image Backup
```bash
# Save current configs from Pi
ssh admin@prepper-pi.local
ip addr show > ~/backup-network.txt
cat /etc/dnsmasq.d/090_raspap.conf > ~/backup-dnsmasq.conf
sudo iptables-save > ~/backup-iptables.txt
exit

# Copy to local machine
scp admin@prepper-pi.local:~/backup-*.txt ./docs/backup/
```

## Fresh Install
1. ⬜ Image Raspberry Pi OS (64-bit) with Pi Imager
   - Hostname: `prepper-pi`
   - User: `admin`
   - Enable SSH
   - Configure WiFi for upstream (wlan0)

2. ⬜ **IMPORTANT**: Boot WITHOUT USB WiFi adapter plugged in
   - Let Pi boot and connect to your WiFi network using built-in wlan0
   - Wait for Pi to show up on network (check router or use `ping prepper-pi.local`)
   - Verify SSH access: `ssh admin@prepper-pi.local`
   - **THEN** plug in USB WiFi adapter (ALFA AWUS036ACM)
   - Verify both interfaces: `ip link show` should show wlan0 and wlan1

3. ⬜ Update system packages
   ```bash
   ssh admin@prepper-pi.local
   sudo apt update && sudo apt upgrade -y
   ```

4. ⬜ Clone and setup (includes RaspAP + captive portal configuration)
   ```bash
   git clone https://github.com/pyrometheous/Prepper-Pi.git
   cd Prepper-Pi
   git checkout feature/native-hostapd
   
   # Option 1: Interactive SSH session (recommended)
   sudo bash scripts/first-run-setup.sh
   
   # Option 2: Via SSH from remote machine (requires -t flag)
   # ssh -t admin@<pi-ip> "cd Prepper-Pi && sudo bash scripts/first-run-setup.sh"
   ```
   
   **Note**: RaspAP installer requires a PTY. If running via SSH, use `-t` flag.
   
   This automatically configures:
   - RaspAP WiFi access point
   - Captive portal with internet passthrough
   - DNS forwarding (no wildcard hijacking)
   - Firewall rules for wlan1↔wlan0 traffic

4. ⬜ Start Docker services
   ```bash
   cp compose/docker-compose.pi.yml docker-compose.override.yml
   docker compose up -d
   ```

## Quick Tests
- ⬜ Ping internet from Pi: `ping -c 4 8.8.8.8`
- ⬜ See WiFi SSID "Prepper Pi" from phone/laptop
- ⬜ Connect to WiFi (password: ChangeMeNow!)
- ⬜ From connected device:
  - ⬜ Ping gateway: `ping 10.20.30.1`
  - ⬜ Ping internet: `ping 8.8.8.8`
  - ⬜ Browse to: http://10.20.30.1:3000 (Homepage)
  - ⬜ Browse to: http://10.20.30.1:8080 (RaspAP)
  - ⬜ Access any website (google.com)

## Expected Results
✅ Internet works through AP
✅ All services accessible
✅ No host validation errors
✅ DNS resolves properly

## If Problems
- Internet not working: Check `systemctl status captive-portal` and firewall rules
- DNS issues: `cat /etc/dnsmasq.d/090_raspap.conf` (should have server=8.8.8.8)
- Services not accessible: `docker compose ps` (all should be "Up")
- WiFi not broadcasting: `systemctl status hostapd`
- Captive portal not configured: Manually run `sudo bash scripts/captive-portal-setup.sh`
