<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Fresh Deploy Testing Guide

## Purpose
Validate that a fresh Raspberry Pi OS installation can be configured using the automated setup scripts to achieve the same working state as the current deployment.

## Pre-Imaging Backup Checklist

### 1. Current Configuration Snapshot
Before re-imaging, document the current working state:

```bash
# On the Pi - save current configurations
ssh admin@prepper-pi.local

# Network configuration
ip addr show > ~/backup-network-config.txt
ip route show >> ~/backup-network-config.txt
cat /etc/network/interfaces >> ~/backup-network-config.txt

# DNS configuration
cat /etc/dnsmasq.d/090_raspap.conf > ~/backup-dnsmasq.conf

# Firewall rules
sudo iptables -L -n -v > ~/backup-iptables-filter.txt
sudo iptables -t nat -L -n -v > ~/backup-iptables-nat.txt

# Service status
systemctl status hostapd > ~/backup-services.txt
systemctl status dnsmasq >> ~/backup-services.txt
systemctl status captive-portal >> ~/backup-services.txt

# Docker containers
docker ps -a > ~/backup-docker.txt
docker compose ps >> ~/backup-docker.txt

# WiFi configuration
iw dev wlan0 info > ~/backup-wifi.txt
iw dev wlan1 info >> ~/backup-wifi.txt

# Copy backups to local machine
exit
scp admin@prepper-pi.local:~/backup-*.txt ./docs/backup/
```

### 2. Hardware Information
Document what's currently connected:

- **Upstream WiFi**: wlan0 (192.168.50.99 on existing network)
- **AP WiFi**: wlan1 (ALFA AWUS036ACM - 10.20.30.1/24)
- **Network**: wlan0 provides internet, wlan1 provides AP
- **Storage**: NVMe SSD mounted where?
- **USB Devices**: List all USB devices connected

```bash
# On the Pi
lsusb > ~/backup-usb-devices.txt
lsblk > ~/backup-storage.txt
```

## Fresh Installation Steps

### 1. Image Raspberry Pi OS
- Use Raspberry Pi Imager
- OS: Raspberry Pi OS (64-bit, Debian Trixie)
- Configure:
  - Hostname: `prepper-pi`
  - Username: `admin`
  - Password: [your password]
  - WiFi: Configure wlan0 for upstream network
  - Enable SSH
  - Set locale/timezone

### 2. Initial Boot & Updates
```bash
ssh admin@prepper-pi.local

# Update system
sudo apt update && sudo apt upgrade -y

# Reboot if kernel updated
sudo reboot
```

### 3. Run Automated Setup
```bash
# Clone repository
sudo apt update && sudo apt install -y git
git clone https://github.com/pyrometheous/Prepper-Pi.git
cd Prepper-Pi

# Checkout the feature branch
git checkout feature/native-hostapd

# Run first-run setup
sudo bash scripts/first-run-setup.sh
```

### 4. Configure Docker Services
```bash
# Copy Pi-specific docker-compose override
cp compose/docker-compose.pi.yml docker-compose.override.yml

# Start services
docker compose up -d

# Check services are running
docker compose ps
```

### 5. Run Captive Portal Setup
```bash
# Run captive portal configuration
sudo bash scripts/captive-portal-setup.sh

# Verify services started
sudo systemctl status captive-portal
sudo systemctl status dnsmasq
sudo systemctl status hostapd
```

## Validation Tests

### 1. Network Connectivity Tests
```bash
# On the Pi
# Test internet connectivity
ping -c 4 8.8.8.8
ping -c 4 google.com

# Check interfaces
ip addr show wlan0  # Should have upstream IP (192.168.50.x)
ip addr show wlan1  # Should have 10.20.30.1

# Check routes
ip route show

# Check firewall rules
sudo iptables -L -n -v
sudo iptables -t nat -L -n -v
```

### 2. WiFi AP Tests
```bash
# Check WiFi is broadcasting
iw dev wlan1 info
sudo iw dev wlan1 station dump  # Shows connected clients
```

**From client device:**
- [ ] Can see "Prepper Pi" SSID
- [ ] Can connect with password "ChangeMeNow!"
- [ ] Receives IP in range 10.20.30.100-199
- [ ] Can ping 10.20.30.1 (gateway)

### 3. DNS Tests
```bash
# On the Pi
cat /etc/dnsmasq.d/090_raspap.conf
# Verify:
# - Has server=8.8.8.8 and server=8.8.4.4
# - Has captive portal detection domains
# - NO wildcard address=/#/10.20.30.1
```

**From client device:**
```bash
# Test DNS resolution
nslookup google.com 10.20.30.1  # Should resolve
nslookup captive.apple.com 10.20.30.1  # Should return 10.20.30.1
```

### 4. Internet Passthrough Tests
**From client device connected to "Prepper Pi":**
- [ ] Can ping 8.8.8.8
- [ ] Can ping google.com
- [ ] Can browse to https://google.com
- [ ] Can access external websites

### 5. Service Access Tests
**From client device connected to "Prepper Pi":**
- [ ] http://10.20.30.1:3000 - Homepage (no "Host validation failed")
- [ ] http://10.20.30.1:8080 - RaspAP (login: admin/secret)
- [ ] http://10.20.30.1:8096 - Jellyfin
- [ ] http://10.20.30.1:9000 - Portainer

### 6. Captive Portal Tests
**From client device:**
- [ ] Connect to "Prepper Pi" WiFi
- [ ] Browser automatically opens? (Known issue - may not work)
- [ ] Manually navigate to http://captive.apple.com
- [ ] Gets redirected to http://10.20.30.1:3000

### 7. Docker Container Health
```bash
# On the Pi
docker compose ps
docker logs homepage --tail 20
docker logs jellyfin --tail 20
docker logs portainer --tail 20

# Check for errors
docker compose logs | grep -i error
```

## Expected Results

### Working ✅
- Internet passthrough (clients can access internet)
- Homepage accessible at 10.20.30.1:3000 (no host validation errors)
- DNS forwards to upstream servers (8.8.8.8, 8.8.4.4)
- WiFi AP broadcasts "Prepper Pi" SSID
- Clients receive DHCP addresses (10.20.30.100-199)
- RaspAP admin interface accessible
- All Docker services running

### Known Issues ⚠️
- Captive portal may not auto-open browser on WiFi connection
  - Workaround: Manually navigate to http://captive.apple.com or http://10.20.30.1:3000

## Comparison Checklist

After fresh deploy, compare with backed up configurations:

```bash
# Compare network settings
diff docs/backup/backup-network-config.txt <(ip addr show; ip route show)

# Compare DNS config
diff docs/backup/backup-dnsmasq.conf /etc/dnsmasq.d/090_raspap.conf

# Compare firewall rules (general structure, IPs may differ)
diff docs/backup/backup-iptables-filter.txt <(sudo iptables -L -n -v)
diff docs/backup/backup-iptables-nat.txt <(sudo iptables -t nat -L -n -v)

# Compare service status
systemctl status hostapd dnsmasq captive-portal docker

# Compare Docker containers
docker compose ps
```

## Troubleshooting

### If Internet Passthrough Doesn't Work
1. Check IP forwarding: `sysctl net.ipv4.ip_forward` (should be 1)
2. Check NAT rule: `sudo iptables -t nat -L POSTROUTING -n -v`
3. Check FORWARD rules: `sudo iptables -L FORWARD -n -v`
4. Verify interfaces: `ip addr show wlan0 wlan1`

### If DNS Doesn't Work
1. Check dnsmasq config: `cat /etc/dnsmasq.d/090_raspap.conf`
2. Check dnsmasq is running: `systemctl status dnsmasq`
3. Test from Pi: `nslookup google.com 127.0.0.1`
4. Check for wildcard hijacking: `grep "address=/#/" /etc/dnsmasq.d/090_raspap.conf` (should be empty)

### If Homepage Shows Host Validation Error
1. Check environment variable: `docker inspect homepage | grep HOMEPAGE_ALLOWED_HOSTS`
2. Should show: `HOMEPAGE_ALLOWED_HOSTS=10.20.30.1:3000,localhost:3000,10.20.30.1,localhost`
3. If missing, edit docker-compose.yml and restart: `docker compose up -d homepage`

### If WiFi AP Doesn't Start
1. Check hostapd: `systemctl status hostapd`
2. Check interface: `iw dev wlan1 info`
3. Check RaspAP config: Check web UI at http://10.20.30.1:8080
4. View logs: `journalctl -u hostapd -n 50`

## Rollback Plan

If fresh deploy fails, you can restore from backup or revert to previous working Pi image.

**Option 1: Keep old SD card**
- Image to a new SD card for testing
- Keep old SD card as working backup

**Option 2: Clone current install**
```bash
# Before re-imaging, create a full backup image
# On local machine (not Pi)
ssh admin@prepper-pi.local "sudo dd if=/dev/mmcblk0 bs=4M status=progress" | dd of=prepper-pi-backup.img bs=4M
```

## Success Criteria

The fresh deploy is successful when:
- ✅ All validation tests pass
- ✅ Internet passthrough works
- ✅ All services accessible
- ✅ No errors in Docker logs
- ✅ Configuration matches working backup
- ✅ Performance is acceptable

## Post-Deploy Hardening

After confirming everything works:
1. Change default WiFi password from "ChangeMeNow!"
2. Change RaspAP admin password from "secret"
3. Change Pi user password
4. Enable HTTPS for web services
5. Update and lock package versions
