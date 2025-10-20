#!/bin/bash
#
# Simple Internet Passthrough Setup (No Captive Portal)
# Configures NAT and forwarding for internet access through AP
# Devices connect normally without any captive portal interference
#

set -e

echo "=== Internet Passthrough Setup (No Captive Portal) ==="

# Detect interfaces dynamically
UPSTREAM_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
AP_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v "$UPSTREAM_INTERFACE" | head -n1)

if [ -z "$AP_INTERFACE" ]; then
    echo "ERROR: Could not detect AP interface"
    echo "Available interfaces:"
    ip link show
    exit 1
fi

echo "Detected interfaces:"
echo "  AP Interface: $AP_INTERFACE"
echo "  Upstream Interface: $UPSTREAM_INTERFACE"
echo ""

# Disable any existing captive portal service
if systemctl is-active --quiet captive-portal 2>/dev/null; then
    echo "Disabling captive portal service..."
    sudo systemctl stop captive-portal || true
    sudo systemctl disable captive-portal || true
fi

# Remove captive portal files
if [ -f /usr/local/bin/captive-portal.py ]; then
    echo "Removing captive portal script..."
    sudo rm -f /usr/local/bin/captive-portal.py
fi

if [ -f /etc/systemd/system/captive-portal.service ]; then
    echo "Removing captive portal service..."
    sudo rm -f /etc/systemd/system/captive-portal.service
    sudo systemctl daemon-reload
fi

# Configure dnsmasq for simple DNS forwarding (no hijacking)
echo "Configuring dnsmasq..."
sudo tee /etc/dnsmasq.d/090_raspap.conf > /dev/null << EOF
interface=$AP_INTERFACE
domain-needed
bogus-priv
dhcp-range=10.20.30.100,10.20.30.199,255.255.255.0,24h

# DNS forwarding - use upstream DNS servers
server=8.8.8.8
server=8.8.4.4

# DHCP options
dhcp-option=option:router,10.20.30.1
dhcp-option=option:dns-server,10.20.30.1
EOF

# Enable IP forwarding
echo "Enabling IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf > /dev/null

# Configure iptables for NAT
echo "Configuring firewall rules..."

# Clear any existing rules
sudo iptables -t nat -F
sudo iptables -F FORWARD

# Enable NAT (masquerading) on upstream interface
sudo iptables -t nat -A POSTROUTING -o $UPSTREAM_INTERFACE -j MASQUERADE

# Allow forwarding from AP to upstream
sudo iptables -A FORWARD -i $AP_INTERFACE -o $UPSTREAM_INTERFACE -j ACCEPT
sudo iptables -A FORWARD -i $UPSTREAM_INTERFACE -o $AP_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT

# Save iptables rules
sudo netfilter-persistent save

# Restart dnsmasq
echo "Restarting dnsmasq..."
sudo systemctl restart dnsmasq

echo ""
echo "=== Internet Passthrough Setup Complete ==="
echo ""
echo "Configuration:"
echo "  - No captive portal popup"
echo "  - Devices connect normally like any WiFi network"
echo "  - Internet access through $UPSTREAM_INTERFACE"
echo "  - DNS: 8.8.8.8, 8.8.4.4"
echo "  - DHCP range: 10.20.30.100-199"
echo ""
echo "Users can access Homepage at: http://10.20.30.1:3000"
echo ""
