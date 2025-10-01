#!/bin/bash

# Prepper-Pi WiFi AP Verification Script
# Based on ChatGPT audit recommendations

echo "🔍 Prepper-Pi WiFi AP Verification"
echo "=================================="
echo ""

# Check if Docker Compose is running
echo "📋 Checking Docker Compose status..."
if ! docker compose ps | grep -q "openwrt"; then
    echo "❌ OpenWRT container not running. Please start with: docker compose up -d"
    exit 1
fi
echo "✅ OpenWRT container is running"
echo ""

# A) Does OpenWrt in the container see the radio and support AP?
echo "📡 Test A: OpenWRT Radio Detection & AP Capability"
echo "=================================================="

docker exec openwrt sh -c '
  echo "=== Available radios ==="
  iw dev 2>/dev/null || echo "No wireless devices found"
  echo ""
  
  echo "=== AP capability check ==="
  iw list 2>/dev/null | sed -n "/Supported interface modes:/,/Supported commands:/p" || echo "No wireless capability info available"
  echo ""
  
  echo "=== Current wireless configuration ==="
  uci show wireless 2>/dev/null | sed -n "1,160p" || echo "No wireless configuration found"
  echo ""
  
  echo "=== WiFi status ==="
  wifi status 2>/dev/null || echo "WiFi status unavailable"
  echo ""
  
  echo "=== DHCP/DNS logs (last 100 lines) ==="
  logread 2>/dev/null | tail -n 100 | grep -Ei "dnsmasq|DHCP" || echo "No DHCP logs found"
  echo ""
  
  echo "=== Kernel wireless drivers and radio logs ==="
  dmesg 2>/dev/null | egrep -i "cfg80211|mac80211|wlan|mt76|ath|brcm" | tail -n 20 || echo "No wireless driver logs found"
  echo ""
  
  echo "=== Network interfaces and bridge status ==="
  ip a 2>/dev/null || echo "ip command not available"
  echo "--- Bridge status ---"
  brctl show 2>/dev/null || bridge link 2>/dev/null || echo "No bridge information available"
'

echo ""
echo "📋 Test A Results:"
echo "Expected: wlan interface present, AP in supported modes, SSID up"
echo "If missing: Check USB WiFi device connection and host kernel drivers"
echo ""

# Additional network configuration check
echo "🔧 Test A2: Network Configuration Check"
echo "======================================="

docker exec openwrt sh -c '
  echo "=== LAN configuration ==="
  uci show network.lan 2>/dev/null || echo "No LAN config found"
  echo ""
  
  echo "=== Wireless summary ==="
  uci show wireless 2>/dev/null | egrep "ssid|encryption|key" || echo "No wireless config found"
'

echo ""

# B) Captive portal actually intercepts DNS/HTTP
echo "🌐 Test B: Captive Portal & DNS Interception"
echo "============================================="

docker exec openwrt sh -c '
  echo "=== OpenWRT logs (captive portal related) ==="
  logread 2>/dev/null | tail -n 50 | egrep -i "nodogsplash|opennds|dnsmasq|http|captive" || echo "No captive portal logs found"
  echo ""
  
  echo "=== DNS service status ==="
  netstat -lnup 2>/dev/null | grep :53 || echo "No DNS service listening on port 53"
  echo ""
  
  echo "=== HTTP service status ==="
  netstat -lntp 2>/dev/null | grep :80 || echo "No HTTP service listening on port 80"
  echo ""
  
  echo "=== uhttpd listening ==="
  netstat -lntp 2>/dev/null | grep ":80 " || echo "uhttpd not listening on :80"
  echo ""
  
  echo "=== test portal page ==="
  wget -qO- http://127.0.0.1/ | head -n 3 || echo "router / not reachable"
  echo ""
  
  echo "=== OpenNDS status ==="
  /etc/init.d/opennds status 2>/dev/null || echo "OpenNDS service not running"
  echo ""
  
  echo "=== OpenNDS process check ==="
  ps 2>/dev/null | grep -i opennds | grep -v grep || echo "No OpenNDS process found"
'

echo ""
echo "📋 Test B Results:"
echo "Expected: DNS answers from OpenWrt (10.20.30.1), HTTP redirects to landing page"
echo ""
echo "🧪 Manual client tests (run from connected device):"
echo "   nslookup example.com 10.20.30.1"
echo "   curl -I http://neverssl.com/ | head -n 5"
echo "   Expected: HTTP 302/303 redirect to http://10.20.30.1/"
echo ""

# C) Future hardware device mapping checks
echo "📺 Test C: Future Hardware Device Mapping"
echo "========================================="

echo "=== TV Tuner devices (Phase 4) ==="
if ls /dev/dvb* >/dev/null 2>&1; then
    echo "✅ TV tuner devices found:"
    ls -l /dev/dvb*
    if docker compose ps | grep -q "tvheadend"; then
        docker exec -it tvheadend bash -c 'ls -l /dev/dvb 2>/dev/null || echo "DVB devices not mapped to container"'
    else
        echo "📋 Tvheadend service not enabled (expected for Phase 1)"
    fi
else
    echo "📋 No TV tuner devices found (expected for Phase 1)"
fi

echo ""
echo "=== RTL-SDR devices (Phase 4) ==="
if lsusb 2>/dev/null | grep -i rtl; then
    echo "✅ RTL-SDR devices found:"
    lsusb | grep -i rtl
    if docker compose ps | grep -q "icecast"; then
        echo "📋 Checking RTL-SDR access in radio containers..."
        for container in rtl_fm_fm rtl_fm_noaa; do
            if docker compose ps | grep -q "$container"; then
                docker exec -it "$container" bash -c 'lsusb 2>/dev/null | grep -i rtl || echo "RTL-SDR not accessible in container"'
            fi
        done
    else
        echo "📋 Radio streaming services not enabled (expected for Phase 1)"
    fi
else
    echo "📋 No RTL-SDR devices found (expected for Phase 1)"
fi

echo ""
echo "=== LoRa devices (Phase 5) ==="
if lsusb 2>/dev/null | grep -i "cp210x\|ch340\|ftdi"; then
    echo "✅ Potential LoRa/Serial devices found:"
    lsusb | grep -i "cp210x\|ch340\|ftdi"
    if docker compose ps | grep -q "meshtasticd"; then
        docker exec -it meshtasticd bash -c 'ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "Serial devices not mapped to container"'
    else
        echo "📋 Meshtastic service not enabled (expected for Phase 1)"
    fi
else
    echo "📋 No LoRa/Serial devices found (expected for Phase 1)"
fi

echo ""
echo "🎯 Verification Summary"
echo "======================"
echo ""
echo "Phase 1 (Current): WiFi AP Infrastructure"
echo "✅ Configured: OpenWRT container with host networking"
echo "✅ Configured: USB WiFi device passthrough"
echo "✅ Configured: Firmware and driver mounts"
echo "⚠️  Needs Testing: Actual WiFi AP functionality on Pi hardware"
echo "⚠️  Needs Testing: Captive portal redirect functionality"
echo ""
echo "Phase 4 (Future): TV & Radio Reception"
echo "📋 Ready: Tvheadend service template (commented out)"
echo "📋 Ready: RTL-SDR radio streaming templates (commented out)"
echo "📋 Pending: Hardware acquisition and testing"
echo ""
echo "Phase 5 (Future): LoRa Mesh Networking"
echo "📋 Ready: Meshtastic service template (commented out)"
echo "📋 Pending: Hardware acquisition and testing"
echo ""
echo "Next Steps:"
echo "1. Test on actual Raspberry Pi 5 with USB WiFi adapter"
echo "2. Validate SSID broadcast and client connectivity"
echo "3. Test captive portal redirect to landing page"
echo "4. Document working configuration parameters"
echo ""
echo "For detailed hardware requirements, see: docs/components.md"
echo "For testing protocol, see: docs/wifi-testing.md"
