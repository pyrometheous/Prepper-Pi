#!/bin/bash
#
# Diagnose captive portal issues
#

echo "=== Captive Portal Diagnostics ==="
echo ""

# Check if service is running
echo "1. Service Status:"
sudo systemctl status captive-portal --no-pager | grep -E "(Active|Main PID)"
echo ""

# Check if port 80 is listening
echo "2. Port 80 Listening:"
sudo ss -tulpn | grep ':80 '
echo ""

# Check the Python script
echo "3. Captive Portal Script (first 30 lines):"
head -30 /usr/local/bin/captive-portal.py
echo ""

# Check DNS hijacking
echo "4. DNS Hijacking Configuration:"
grep "address=" /etc/dnsmasq.d/090_raspap.conf
echo ""

# Test DNS resolution from Pi itself
echo "5. DNS Resolution Test (from Pi):"
dig @10.20.30.1 captive.apple.com +short
echo ""

# Check iptables rules
echo "6. Firewall Rules (port 80):"
sudo iptables -L -n -v | grep -A 5 "dpt:80"
echo ""

# Try to curl the captive portal locally
echo "7. Local HTTP Test:"
curl -v http://10.20.30.1/ 2>&1 | head -20
echo ""

# Check for any errors in journal
echo "8. Recent Captive Portal Logs:"
sudo journalctl -u captive-portal -n 50 --no-pager | grep -v "Started\|Stopped\|Stopping"
echo ""

echo "=== Diagnostics Complete ==="
