#!/bin/bash
#
# Enhanced Captive Portal Setup with iptables port forwarding
# This forces ALL HTTP traffic (port 80) to the captive portal
# More aggressive approach for modern devices
#

set -e

echo "=== Enhanced Captive Portal Setup ==="

# Detect interfaces
UPSTREAM_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
AP_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v "$UPSTREAM_INTERFACE" | head -n1)

if [ -z "$AP_INTERFACE" ]; then
    echo "ERROR: Could not detect AP interface"
    exit 1
fi

echo "AP Interface: $AP_INTERFACE"
echo "Upstream Interface: $UPSTREAM_INTERFACE"

# Create enhanced captive portal Python script with logging
cat > /usr/local/bin/captive-portal.py << 'PYEOF'
#!/usr/bin/env python3
import http.server
import socketserver
from urllib.parse import urlparse
import logging

PORT = 80
REDIRECT_URL = "http://10.20.30.1:3000"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Captive portal detection URLs
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
    def log_message(self, format, *args):
        # Custom logging
        logging.info("%s - %s" % (self.client_address[0], format % args))
    
    def do_GET(self):
        path = urlparse(self.path).path
        host = self.headers.get('Host', '')
        
        logging.info(f"Request from {self.client_address[0]}: {host}{path}")
        
        # For captive portal detection URLs, return HTML with redirect
        if any(check in path for check in PORTAL_CHECK_PATHS) or 'generate_204' in path or 'gen_204' in path:
            # Return HTTP 200 with HTML content to trigger portal
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={REDIRECT_URL}">
    <title>Prepper Pi Network</title>
</head>
<body>
    <h1>Welcome to Prepper Pi</h1>
    <p>Redirecting to homepage...</p>
    <script>window.location.href = "{REDIRECT_URL}";</script>
</body>
</html>'''
            self.wfile.write(html.encode())
            logging.info(f"  -> Sent portal detection response (200)")
        else:
            # For all other requests, redirect to homepage
            self.send_response(302)
            self.send_header('Location', REDIRECT_URL)
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            logging.info(f"  -> Sent redirect (302) to {REDIRECT_URL}")

    def do_HEAD(self):
        # Handle HEAD requests (some devices use these)
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def do_POST(self):
        # Handle POST requests
        self.do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CaptivePortalHandler) as httpd:
        logging.info(f"Captive portal server listening on port {PORT}")
        logging.info(f"Redirecting all traffic to {REDIRECT_URL}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            httpd.shutdown()
PYEOF

chmod +x /usr/local/bin/captive-portal.py

# Update dnsmasq configuration with more aggressive settings
echo "Configuring dnsmasq for captive portal..."

# Backup existing config
sudo cp /etc/dnsmasq.d/090_raspap.conf /etc/dnsmasq.d/090_raspap.conf.bak 2>/dev/null || true

# Create enhanced dnsmasq config
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

# Disable DNS rebind protection for captive portal domains
rebind-domain-ok=/apple.com/
rebind-domain-ok=/google.com/
rebind-domain-ok=/gstatic.com/
rebind-domain-ok=/msftconnecttest.com/
rebind-domain-ok=/firefox.com/

# Captive portal detection - hijack these domains
address=/captive.apple.com/10.20.30.1
address=/connectivitycheck.gstatic.com/10.20.30.1
address=/www.msftconnecttest.com/10.20.30.1
address=/detectportal.firefox.com/10.20.30.1
address=/clients3.google.com/10.20.30.1
address=/connecttest.txt/10.20.30.1

# Additional iOS domains
address=/apple.com/10.20.30.1
address=/www.apple.com/10.20.30.1
address=/gsp1.apple.com/10.20.30.1

# Additional Android domains  
address=/play.googleapis.com/10.20.30.1
address=/clients1.google.com/10.20.30.1
address=/clients4.google.com/10.20.30.1

# Additional Windows domains
address=/msftncsi.com/10.20.30.1
address=/www.msftncsi.com/10.20.30.1
EOF

# Configure iptables for transparent HTTP redirect
echo "Configuring firewall rules..."

# Clear any existing captive portal redirect rules
sudo iptables -t nat -D PREROUTING -i $AP_INTERFACE -p tcp --dport 80 -j REDIRECT --to-ports 80 2>/dev/null || true

# Add rule to redirect all HTTP traffic from AP interface to captive portal
sudo iptables -t nat -I PREROUTING -i $AP_INTERFACE -p tcp --dport 80 -j REDIRECT --to-ports 80

# Save iptables rules
sudo netfilter-persistent save

# Restart services
echo "Restarting services..."
sudo systemctl restart dnsmasq
sudo systemctl restart captive-portal

sleep 2

# Check status
echo ""
echo "=== Service Status ==="
sudo systemctl status captive-portal --no-pager | grep -E "(Active|Main PID)"
sudo systemctl status dnsmasq --no-pager | grep -E "(Active|loaded)"

echo ""
echo "=== Port 80 Listening ==="
sudo ss -tulpn | grep ':80 '

echo ""
echo "=== Enhanced Captive Portal Setup Complete ==="
echo ""
echo "Changes made:"
echo "  1. Added logging to captive portal script"
echo "  2. Added more DNS hijacking domains (apple.com, play.googleapis.com, etc.)"
echo "  3. Added iptables transparent HTTP redirect for all port 80 traffic"
echo "  4. Disabled DNS rebind protection for captive portal domains"
echo ""
echo "To monitor requests in real-time:"
echo "  sudo journalctl -u captive-portal -f"
echo ""
echo "To test from a connected device:"
echo "  curl -v http://captive.apple.com"
echo "  curl -v http://www.google.com"
echo ""
echo "Note: Modern devices using HTTPS or DNS-over-HTTPS may still not trigger"
echo "      the popup automatically. Users may need to open a browser manually."
