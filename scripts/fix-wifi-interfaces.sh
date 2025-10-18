#!/bin/bash
# Fix WiFi interface configuration on existing Prepper Pi installation
# This script corrects the AP interface from wlan0 to wlan1

set -e

echo "=== Fixing WiFi Interface Configuration ==="

# Detect WiFi interfaces
if ! ip link show wlan1 &> /dev/null; then
    echo "ERROR: wlan1 interface not found!"
    echo "Please ensure your secondary WiFi adapter (ALFA AWUS036ACM) is connected."
    exit 1
fi

echo "✓ Dual WiFi interfaces detected"
AP_INTERFACE="wlan1"
UPSTREAM_INTERFACE="wlan0"

echo "  - Upstream (Internet): $UPSTREAM_INTERFACE"
echo "  - Access Point: $AP_INTERFACE"

# 1. Update hostapd configuration
echo ""
echo "Updating hostapd configuration..."
sudo sed -i "s/^interface=.*/interface=$AP_INTERFACE/" /etc/hostapd/hostapd.conf
echo "✓ hostapd now using $AP_INTERFACE"

# 2. Update dhcpcd configuration
echo ""
echo "Updating dhcpcd configuration..."
sudo sed -i '/interface wlan[01]/,/nohook wpa_supplicant/d' /etc/dhcpcd.conf
sudo tee -a /etc/dhcpcd.conf << EOF

# Prepper Pi AP Interface Configuration
interface $AP_INTERFACE
    static ip_address=10.20.30.1/24
    nohook wpa_supplicant
EOF
echo "✓ dhcpcd configured for $AP_INTERFACE"

# 3. Update dnsmasq configuration
echo ""
echo "Updating dnsmasq configuration..."
sudo sed -i "s/^interface=.*/interface=$AP_INTERFACE/" /etc/dnsmasq.d/090_raspap.conf
echo "✓ dnsmasq now listening on $AP_INTERFACE"

# 4. Update firewall rules
echo ""
echo "Updating firewall rules..."

# Remove old rules (ignore errors if they don't exist)
sudo iptables -t nat -D POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || true
sudo iptables -D FORWARD -i wlan1 -o wlan0 -j ACCEPT 2>/dev/null || true
sudo iptables -D FORWARD -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || true

# Add correct rules
sudo iptables -t nat -A POSTROUTING -o $UPSTREAM_INTERFACE -j MASQUERADE
sudo iptables -I FORWARD 1 -i $AP_INTERFACE -o $UPSTREAM_INTERFACE -j ACCEPT
sudo iptables -I FORWARD 2 -i $UPSTREAM_INTERFACE -o $AP_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT

# Save iptables rules
sudo netfilter-persistent save
echo "✓ Firewall rules updated and saved"

# 5. Bring down wlan0 AP mode and configure it for client mode
echo ""
echo "Configuring $UPSTREAM_INTERFACE for client mode..."
sudo ip link set $UPSTREAM_INTERFACE down 2>/dev/null || true
sudo systemctl restart dhcpcd

# 6. Restart services
echo ""
echo "Restarting network services..."
sudo systemctl restart dnsmasq
sudo systemctl restart hostapd
sudo systemctl restart captive-portal 2>/dev/null || echo "Note: captive-portal not running"

# 7. Show status
echo ""
echo "=== Configuration Complete ==="
echo ""
echo "Interface Status:"
ip -br addr show wlan0
ip -br addr show wlan1
echo ""
echo "Service Status:"
sudo systemctl is-active hostapd && echo "✓ hostapd: running" || echo "✗ hostapd: not running"
sudo systemctl is-active dnsmasq && echo "✓ dnsmasq: running" || echo "✗ dnsmasq: not running"
sudo systemctl is-active captive-portal && echo "✓ captive-portal: running" || echo "✗ captive-portal: not running"
echo ""
echo "Next steps:"
echo "1. Connect $UPSTREAM_INTERFACE to your home WiFi via RaspAP web UI (http://10.20.30.1:8080)"
echo "   or use raspi-config / nmcli to configure WiFi client"
echo "2. Look for 'Prepper Pi' WiFi network - it should now be broadcasting on $AP_INTERFACE"
echo "3. Test internet passthrough by connecting and browsing the web"
echo ""
echo "If AP is still not visible, try: sudo reboot"
