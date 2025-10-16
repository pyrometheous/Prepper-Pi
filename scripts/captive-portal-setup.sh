#!/bin/bash
# Captive Portal Setup Script for Prepper Pi
# This script configures the captive portal and internet passthrough with proper DNS and firewall rules

echo "=== Configuring Captive Portal with Internet Passthrough ==="

# 1. Create captive portal Python script with detection URL handling
sudo tee /usr/local/bin/captive-portal.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver

PORT = 80
REDIRECT_URL = "http://10.20.30.1:3000"

# Detection URLs used by various operating systems
PORTAL_CHECK_PATHS = [
    '/hotspot-detect.html',      # iOS
    '/generate_204',             # Android
    '/connecttest.txt',          # Windows
    '/success.txt',              # Chrome/Chromium
    '/ncsi.txt',                 # Windows Network Connectivity Status Indicator
]

class CaptivePortalHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # For portal detection URLs, return 200 OK with redirect HTML
        if self.path in PORTAL_CHECK_PATHS:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            redirect_html = f'''<!DOCTYPE html>
<html><head>
<meta http-equiv="refresh" content="0;url={REDIRECT_URL}">
</head><body>Redirecting...</body></html>'''
            self.wfile.write(redirect_html.encode())
        else:
            # For all other requests, use 302 redirect
            self.send_response(302)
            self.send_header('Location', REDIRECT_URL)
            self.end_headers()
        
    def do_HEAD(self):
        if self.path in PORTAL_CHECK_PATHS:
            self.send_response(200)
        else:
            self.send_response(302)
            self.send_header('Location', REDIRECT_URL)
        self.end_headers()
        
    def do_POST(self):
        self.do_GET()
        
    def log_message(self, format, *args):
        return  # Suppress logging

# Allow port reuse
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), CaptivePortalHandler) as httpd:
    print(f"Captive portal running on port {PORT}, redirecting to {REDIRECT_URL}")
    httpd.serve_forever()
EOF

sudo chmod +x /usr/local/bin/captive-portal.py

# 2. Create systemd service
sudo tee /etc/systemd/system/captive-portal.service << 'EOF'
[Unit]
Description=Captive Portal HTTP Redirect
After=network.target dnsmasq.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/local/bin/captive-portal.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 3. Configure dnsmasq for proper DNS forwarding and captive portal detection
sudo tee /etc/dnsmasq.d/090_raspap.conf << 'EOF'
# RaspAP WiFi AP configuration
interface=wlan1
dhcp-range=10.20.30.100,10.20.30.199,255.255.255.0,24h
dhcp-option=option:router,10.20.30.1
dhcp-option=option:dns-server,10.20.30.1

# Upstream DNS servers for internet access
server=8.8.8.8
server=8.8.4.4

# Captive portal detection domains - redirect to our portal
address=/captive.apple.com/10.20.30.1
address=/connectivitycheck.gstatic.com/10.20.30.1
address=/www.msftconnecttest.com/10.20.30.1
address=/detectportal.firefox.com/10.20.30.1
EOF

# 4. Configure firewall rules for internet passthrough
echo "Configuring firewall rules..."

# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf

# Add NAT rule for internet access (wlan0 is upstream, wlan1 is AP)
sudo iptables -t nat -C POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || \
    sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

# Add FORWARD chain rules to allow traffic between interfaces
sudo iptables -C FORWARD -i wlan1 -o wlan0 -j ACCEPT 2>/dev/null || \
    sudo iptables -I FORWARD 1 -i wlan1 -o wlan0 -j ACCEPT

sudo iptables -C FORWARD -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
    sudo iptables -I FORWARD 2 -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT

# 5. Install and save iptables rules
echo "Installing iptables-persistent..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y iptables-persistent
sudo netfilter-persistent save

# 6. Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable captive-portal
sudo systemctl restart dnsmasq
sudo systemctl start captive-portal

echo "=== Captive Portal Configuration Complete ==="
echo "- Portal redirects HTTP traffic to http://10.20.30.1:3000"
echo "- Internet passthrough enabled via wlan0"
echo "- Captive portal detection configured for iOS, Android, Windows"
