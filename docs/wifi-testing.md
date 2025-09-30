# WiFi AP Configuration Testing Guide

> **Status:** This configuration requires hardware validation. Current setup is theoretical and needs testing on actual Raspberry Pi hardware.

## 🚨 Current Issue Analysis

Based on configuration audit, our OpenWRT-in-Docker WiFi AP setup has several potential issues that need resolution:

### **Identified Problems:**

1. **Network Mode**: Using `macvlan` instead of `host` networking may prevent proper AP operation
2. **Device Access**: Missing USB device mounts for WiFi adapters
3. **Firmware**: No firmware directory mount for wireless drivers
4. **Radio Detection**: Generic device paths won't match actual Pi hardware

## 🔧 Proposed Configuration Fixes

### **Option A: Enhanced Docker OpenWRT (Recommended First Test)**

Update `docker-compose.yml` OpenWRT service:

```yaml
openwrt:
  image: openwrt/rootfs:x86-64-23.05.2  # May need ARM64 version for Pi
  container_name: openwrt
  restart: unless-stopped
  network_mode: "host"  # Changed from macvlan
  privileged: true
  cap_add:
    - NET_ADMIN
    - SYS_ADMIN
  devices:
    - /dev/net/tun:/dev/net/tun
    - /dev/bus/usb:/dev/bus/usb  # USB WiFi adapter access
  volumes:
    - ./openwrt/config:/etc/config
    - ./openwrt/data:/root
    - /lib/firmware:/lib/firmware:ro  # Host firmware access
    - /sys/class/ieee80211:/sys/class/ieee80211:ro  # Radio detection
    - /run/udev:/run/udev:ro  # Device management
  command: ["/sbin/init"]
```

### **Option B: Host-based hostapd (Fallback)**

If container approach fails, use host-based WiFi AP:

```bash
# Install hostapd on Pi OS
sudo apt install hostapd dnsmasq

# Configure hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq

# Keep Docker services, remove OpenWRT WiFi
```

## 🧪 Hardware Testing Protocol

### **Prerequisites:**
- Raspberry Pi 5 with Pi OS
- USB WiFi adapter (recommend ALFA AWUS036ACM or similar)
- Docker and Docker Compose installed

### **Test Sequence:**

1. **Driver Verification:**
```bash
# Check WiFi hardware detection
lsusb | grep -i wireless
iw list | head -20
ls /lib/firmware/ | grep -E "(mt76|rtl|ath)"
```

2. **Container Radio Access:**
```bash
# Test device passthrough
docker compose up openwrt
docker exec openwrt iw dev
docker exec openwrt ls /sys/class/ieee80211/
```

3. **AP Mode Test:**
```bash
# Inside OpenWRT container
uci show wireless
wifi reload
sleep 5
iw dev
logread | grep -E "wlan|wireless"
```

4. **Client Connection Test:**
```bash
# From phone/laptop: connect to "Prepper Pi" SSID
# Check DHCP assignment in container
docker exec openwrt logread | grep DHCP
```

5. **Service Access Test:**
```bash
# Verify service reachability
curl http://10.20.30.40/  # Homepage
curl http://10.20.30.40:9000/  # Portainer
```

## 📋 Expected Results

### **Success Criteria:**
- [ ] WiFi radio visible in container (`iw dev` shows wlan interface)
- [ ] AP mode starts successfully (`wifi reload` creates AP)
- [ ] SSID visible to client devices
- [ ] Client can associate and receive DHCP from container
- [ ] HTTP traffic redirected to captive portal
- [ ] Services accessible from WiFi clients
- [ ] Configuration survives container restart

### **Failure Scenarios:**
- **No radio in container**: Device mount or firmware issue
- **AP won't start**: Driver or configuration problem  
- **No client association**: RF or authentication issue
- **No DHCP**: Networking mode or service configuration
- **No internet/services**: Routing or firewall configuration

## 🛠️ Troubleshooting Guide

### **Radio Not Detected:**
```bash
# Host side
lsusb  # Verify USB WiFi present
dmesg | tail -20  # Check driver messages
modprobe <driver>  # Load specific driver if needed

# Container side  
docker exec openwrt dmesg | tail -20
docker exec openwrt lsmod | grep mac80211
```

### **AP Mode Fails:**
```bash
# Check OpenWRT wireless config
docker exec openwrt uci show wireless
docker exec openwrt wifi status
docker exec openwrt logread | grep -E "wlan|hostapd"
```

### **No Client DHCP:**
```bash
# Check dnsmasq in container
docker exec openwrt ps | grep dnsmasq
docker exec openwrt netstat -ln | grep :67
docker exec openwrt cat /tmp/dhcp.leases
```

## 🔄 Configuration Updates

Once testing is complete, this document will be updated with:
- Working docker-compose.yml configuration
- Validated wireless device configuration  
- Confirmed networking mode and device mounts
- End-to-end test results and screenshots

## 📝 Test Results

**Status:** ⏳ **Hardware testing pending**

*This section will be populated with actual test results once hardware validation is performed.*

---

*Last updated: 2025-09-30*
