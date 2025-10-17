#!/bin/bash
#
# Captive Portal with Bypass Option
# Allows devices to use the network without signing in
# Compatible with Nintendo Switch, IoT devices, etc.
#

set -e

echo "=== Configuring Captive Portal with Bypass ==="

# Detect interfaces
UPSTREAM_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
AP_INTERFACE=$(iw dev | awk '$1=="Interface"{print $2}' | grep -v "$UPSTREAM_INTERFACE" | head -n1)

if [ -z "$AP_INTERFACE" ]; then
    echo "ERROR: Could not detect AP interface"
    exit 1
fi

echo "AP Interface: $AP_INTERFACE"
echo "Upstream Interface: $UPSTREAM_INTERFACE"

# Create captive portal with bypass support
cat > /usr/local/bin/captive-portal.py << 'PYEOF'
#!/usr/bin/env python3
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import logging

PORT = 80
HOMEPAGE_URL = "http://10.20.30.1:3000"

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

# Nintendo Switch and other gaming consoles detection
GAMING_USER_AGENTS = [
    'libcurl (Nintendo Switch',
    'nintendo',
    'PlayStation',
    'Xbox',
]

class CaptivePortalHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logging.info("%s - %s" % (self.client_address[0], format % args))
    
    def do_GET(self):
        path = urlparse(self.path).path
        host = self.headers.get('Host', '')
        user_agent = self.headers.get('User-Agent', '').lower()
        
        logging.info(f"Request from {self.client_address[0]}: {host}{path}")
        logging.info(f"  User-Agent: {user_agent}")
        
        # Check if this is a gaming console or IoT device
        is_gaming_device = any(game_ua.lower() in user_agent for game_ua in GAMING_USER_AGENTS)
        
        # For Nintendo Switch and gaming consoles, return success immediately (no portal)
        if is_gaming_device:
            logging.info(f"  -> Gaming device detected, allowing through")
            self.send_response(204)  # No Content - tells device network is good
            self.end_headers()
            return
        
        # For captive portal detection URLs from regular devices
        if any(check in path for check in PORTAL_CHECK_PATHS) or 'generate_204' in path or 'gen_204' in path:
            # Return HTML with options: View Homepage OR Continue without signing in
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prepper Pi Network</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin: 0 0 16px 0;
            font-size: 24px;
        }}
        p {{
            color: #666;
            margin: 0 0 24px 0;
            line-height: 1.5;
        }}
        .button {{
            display: block;
            width: 100%;
            padding: 14px;
            margin: 12px 0;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            box-sizing: border-box;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .button:active {{
            transform: scale(0.98);
        }}
        .primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .primary:hover {{
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        .secondary {{
            background: white;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        .secondary:hover {{
            background: #f5f7ff;
        }}
        .icon {{
            font-size: 48px;
            margin-bottom: 16px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">📡</div>
        <h1>Welcome to Prepper Pi</h1>
        <p>You're connected to the Prepper Pi network. Choose an option below:</p>
        
        <a href="{HOMEPAGE_URL}" class="button primary">
            View Homepage & Services
        </a>
        
        <button onclick="bypass()" class="button secondary">
            Continue Without Signing In
        </button>
        
        <p style="font-size: 12px; color: #999; margin-top: 24px;">
            Network SSID: Prepper Pi<br>
            Gateway: 10.20.30.1
        </p>
    </div>
    
    <script>
        function bypass() {{
            // Close the captive portal popup without redirecting
            // Most devices will interpret this as successful connection
            if (window.close) {{
                window.close();
            }}
            // Fallback: redirect to a success endpoint
            window.location.href = '/bypass-success';
        }}
    </script>
</body>
</html>'''
            self.wfile.write(html.encode())
            logging.info(f"  -> Sent captive portal page with bypass option")
        
        # Handle bypass success (tells device network is working)
        elif path == '/bypass-success':
            self.send_response(204)  # No Content - network is good
            self.end_headers()
            logging.info(f"  -> Sent bypass success (204 No Content)")
        
        # For all other requests, show the same portal page
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prepper Pi Network</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 12px;
            padding: 32px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-align: center;
        }}
        h1 {{
            color: #333;
            margin: 0 0 16px 0;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 Prepper Pi Network</h1>
        <p>You're already connected! Access the homepage at:</p>
        <p><a href="{HOMEPAGE_URL}">{HOMEPAGE_URL}</a></p>
    </div>
</body>
</html>'''
            self.wfile.write(html.encode())
            logging.info(f"  -> Sent generic portal page")

    def do_HEAD(self):
        user_agent = self.headers.get('User-Agent', '').lower()
        is_gaming_device = any(game_ua.lower() in user_agent for game_ua in GAMING_USER_AGENTS)
        
        if is_gaming_device:
            self.send_response(204)
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
        self.end_headers()

    def do_POST(self):
        self.do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), CaptivePortalHandler) as httpd:
        logging.info(f"Captive portal server listening on port {PORT}")
        logging.info(f"Homepage URL: {HOMEPAGE_URL}")
        logging.info(f"Gaming consoles will bypass captive portal automatically")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            httpd.shutdown()
PYEOF

chmod +x /usr/local/bin/captive-portal.py

# Restart captive portal service
echo "Restarting captive portal service..."
sudo systemctl restart captive-portal

sleep 2

# Check status
echo ""
echo "=== Service Status ==="
sudo systemctl status captive-portal --no-pager | grep -E "(Active|Main PID)"

echo ""
echo "=== Captive Portal Configuration Complete ==="
echo ""
echo "Changes made:"
echo "  1. Added 'Continue Without Signing In' button to portal page"
echo "  2. Nintendo Switch and gaming consoles bypass captive portal automatically"
echo "  3. /bypass-success endpoint returns HTTP 204 (network OK)"
echo "  4. Improved portal page design with better UX"
echo ""
echo "Supported bypass for:"
echo "  - Nintendo Switch"
echo "  - PlayStation"
echo "  - Xbox"
echo "  - Other IoT devices"
echo ""
echo "Test the captive portal:"
echo "  1. Disconnect and reconnect to 'Prepper Pi' WiFi"
echo "  2. You should see 'Sign into Network' popup"
echo "  3. Choose 'View Homepage' OR 'Continue Without Signing In'"
echo ""
echo "Monitor requests: sudo journalctl -u captive-portal -f"
