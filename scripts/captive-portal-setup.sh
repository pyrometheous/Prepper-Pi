#!/bin/bash
# Captive Portal Setup Script for Prepper Pi
# This script configures the captive portal and internet passthrough

echo "=== Configuring Captive Portal ==="

# Detect WiFi interfaces
if ip link show wlan1 &> /dev/null; then
    echo "Dual WiFi detected: wlan0 (upstream) and wlan1 (AP)"
    AP_INTERFACE="wlan1"
    UPSTREAM_INTERFACE="wlan0"
else
    echo "Single WiFi detected: using wlan0 for AP, eth0 for upstream"
    AP_INTERFACE="wlan0"
    UPSTREAM_INTERFACE="eth0"
fi

echo "AP Interface: $AP_INTERFACE"
echo "Upstream Interface: $UPSTREAM_INTERFACE"

# 1. Create captive portal Python script
sudo tee /usr/local/bin/captive-portal.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
from urllib.parse import urlparse

PORT = 80
REDIRECT_URL = "http://10.20.30.1:3000"

# Captive portal detection URLs that need special handling
PORTAL_CHECK_PATHS = [
    '/hotspot-detect.html',        # iOS
    '/library/test/success.html',  # iOS alternate
    '/generate_204',                # Android/Chrome
    '/gen_204',                     # Android alternate
    '/connecttest.txt',             # Windows
    '/redirect',                    # Windows alternate  
    '/success.txt',                 # Firefox
    '/canonical.html',              # Ubuntu
    '/connectivity-check.html',     # Various Linux
]

class CaptivePortalHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path

        # For captive portal detection URLs, return response that triggers portal
        if any(check in path for check in PORTAL_CHECK_PATHS) or 'generate_204' in path or 'gen_204' in path:
            # Return HTTP 200 with content (not 204) to trigger captive portal
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            # Return HTML that will trigger captive portal popup
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={REDIRECT_URL}">
    <title>Prepper Pi - Network Portal</title>
</head>
<body>
    <h1>Welcome to Prepper Pi</h1>
    <p>Redirecting to dashboard...</p>
    <p>If not redirected, <a href="{REDIRECT_URL}">click here</a></p>
</body>
</html>'''
            self.wfile.write(html.encode())
        else:
            # For all other URLs, send 302 redirect
            self.send_response(302)
            self.send_header('Location', REDIRECT_URL)
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()

    def do_HEAD(self):
        # For HEAD requests, return 200 to indicate captive portal
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        return  # Suppress logging

# Allow port reuse
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), CaptivePortalHandler) as httpd:
    print(f"Captive portal running on port {PORT}")
    print(f"Portal checks return success with redirect to {REDIRECT_URL}")
    print(f"All other HTTP requests redirect to {REDIRECT_URL}")
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

# 3. Configure dnsmasq for DNS and captive portal detection
echo "Configuring dnsmasq..."
sudo cp /etc/dnsmasq.d/090_raspap.conf /etc/dnsmasq.d/090_raspap.conf.bak 2>/dev/null || true

# Remove wildcard DNS hijacking and configure properly
# 3. Configure dnsmasq
echo "Configuring dnsmasq for DHCP and DNS..."
sudo tee /etc/dnsmasq.d/090_raspap.conf << EOF
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

# Captive portal detection - these trigger the captive portal popup
address=/captive.apple.com/10.20.30.1
address=/connectivitycheck.gstatic.com/10.20.30.1
address=/www.msftconnecttest.com/10.20.30.1
address=/detectportal.firefox.com/10.20.30.1
address=/clients3.google.com/10.20.30.1
address=/connecttest.txt/10.20.30.1
EOF

# 4. Configure NAT for internet passthrough
echo "Configuring firewall rules..."
sudo iptables -t nat -C POSTROUTING -o $UPSTREAM_INTERFACE -j MASQUERADE 2>/dev/null || 
    sudo iptables -t nat -A POSTROUTING -o $UPSTREAM_INTERFACE -j MASQUERADE

# 5. Add FORWARD rules to allow traffic from AP to upstream
sudo iptables -C FORWARD -i $AP_INTERFACE -o $UPSTREAM_INTERFACE -j ACCEPT 2>/dev/null || 
    sudo iptables -I FORWARD 1 -i $AP_INTERFACE -o $UPSTREAM_INTERFACE -j ACCEPT

sudo iptables -C FORWARD -i $UPSTREAM_INTERFACE -o $AP_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || 
    sudo iptables -I FORWARD 2 -i $UPSTREAM_INTERFACE -o $AP_INTERFACE -m state --state RELATED,ESTABLISHED -j ACCEPT

# 4. Configure NAT for internet passthrough
echo "Configuring firewall rules..."
sudo iptables -t nat -C POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || \
    sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

# 5. Add FORWARD rules to allow traffic from wlan1 to wlan0
sudo iptables -C FORWARD -i wlan1 -o wlan0 -j ACCEPT 2>/dev/null || \
    sudo iptables -I FORWARD 1 -i wlan1 -o wlan0 -j ACCEPT

sudo iptables -C FORWARD -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
    sudo iptables -I FORWARD 2 -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT

# 6. Install and save iptables rules
sudo apt-get install -y iptables-persistent
sudo netfilter-persistent save

# 7. Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable captive-portal
sudo systemctl restart dnsmasq
sudo systemctl restart captive-portal

echo "=== Captive Portal Configuration Complete ==="
echo ""
echo "✅ Configuration Summary:"
echo "- AP Interface: $AP_INTERFACE"
echo "- Upstream Interface: $UPSTREAM_INTERFACE"
echo "- Captive portal running on port 80"
echo "- HTTP redirects to http://10.20.30.1:3000"
echo "- Internet passthrough enabled ($AP_INTERFACE -> $UPSTREAM_INTERFACE)"
echo "- DNS properly configured with upstream servers (8.8.8.8, 8.8.4.4)"
echo "- Captive portal detection configured for iOS, Android, Windows"
echo ""
echo "🧪 Test by connecting to 'Prepper Pi' WiFi:"
echo "1. Device should show captive portal notification"
echo "2. Internet access should work"
echo "3. Browser opens to http://10.20.30.1:3000"
