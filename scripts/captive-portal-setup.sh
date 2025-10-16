#!/bin/bash
# Captive Portal Setup Script for Prepper Pi
# This script configures the captive portal and internet passthrough

echo "=== Configuring Captive Portal ==="

# 1. Create captive portal Python script
sudo tee /usr/local/bin/captive-portal.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver

PORT = 80
REDIRECT_URL = "http://10.20.30.1:3000"

class RedirectHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(302)
        self.send_header('Location', REDIRECT_URL)
        self.end_headers()
        
    def do_HEAD(self):
        self.do_GET()
        
    def do_POST(self):
        self.do_GET()
        
    def log_message(self, format, *args):
        return  # Suppress logging

# Allow port reuse
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), RedirectHandler) as httpd:
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

# 3. Add captive portal detection domains to dnsmasq
if ! grep -q "captive.apple.com" /etc/dnsmasq.d/090_raspap.conf; then
    sudo tee -a /etc/dnsmasq.d/090_raspap.conf << 'EOF'

# Captive portal detection
address=/captive.apple.com/10.20.30.1
address=/connectivitycheck.gstatic.com/10.20.30.1
address=/www.msftconnecttest.com/10.20.30.1
address=/detectportal.firefox.com/10.20.30.1
EOF
fi

# 4. Configure NAT for internet passthrough
sudo iptables -t nat -C POSTROUTING -o wlan0 -j MASQUERADE 2>/dev/null || \
    sudo iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

# 5. Install and save iptables rules
sudo apt-get install -y iptables-persistent
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
