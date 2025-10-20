#!/bin/bash

# Prepper Pi - First Run Setup Script
# This script sets up the complete Prepper Pi environment

set -e  # Exit on any error

echo "🚀 Starting Prepper Pi Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Configuration flags
ENABLE_HOST_AP=${ENABLE_HOST_AP:-0}  # Set to 1 to enable host AP as fallback
ENABLE_MACVLAN=${ENABLE_MACVLAN:-0}  # Set to 1 to enable macvlan network setup
HOST_LAN_IP=${HOST_LAN_IP:-10.20.30.40}

# Detect network interface
print_status "Detecting network interface..."
INTERFACE=$(ip route | grep default | head -1 | awk '{print $5}')
if [ -z "$INTERFACE" ]; then
    print_warning "Could not auto-detect network interface. Please check your network configuration."
    INTERFACE="eth0"
fi
print_status "Using network interface: $INTERFACE"

# Update package list
print_status "Updating package lists..."
apt update

# Install prerequisites for Docker installation
print_status "Installing prerequisites..."
apt install -y ca-certificates curl gnupg lsb-release git wget iproute2 iptables net-tools

# Check if Docker is already installed
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker from official repository..."
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package list with Docker repo
    apt update
    
    # Install Docker Engine, CLI, containerd, and Compose plugin
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    print_success "Docker installed successfully"
else
    print_status "Docker is already installed"
    
    # Ensure Docker Compose plugin is installed even if Docker already exists
    if ! docker compose version &> /dev/null; then
        print_status "Installing Docker Compose plugin..."
        apt install -y docker-compose-plugin
    fi
fi

# Add current user to docker group (if not root)
if [ "$SUDO_USER" ]; then
    print_status "Adding $SUDO_USER to docker group..."
    usermod -aG docker "$SUDO_USER"
fi

# Enable and start Docker
print_status "Enabling and starting Docker service..."
systemctl enable docker
systemctl start docker

# Enable IP forwarding
print_status "Enabling IP forwarding..."
echo 'net.ipv4.ip_forward=1' >> /etc/sysctl.conf
echo 'net.ipv6.conf.all.forwarding=1' >> /etc/sysctl.conf
sysctl -p

# Load necessary kernel modules
print_status "Loading kernel modules..."
modprobe tun
modprobe bridge
modprobe br_netfilter

# Make kernel modules persistent
echo 'tun' >> /etc/modules
echo 'bridge' >> /etc/modules
echo 'br_netfilter' >> /etc/modules

# Create required directories
print_status "Creating directory structure..."
mkdir -p media/{movies,tv,music,books}
mkdir -p shares/{public,documents}
mkdir -p openwrt/{config,data}
mkdir -p homepage/icons

# Set correct permissions
print_status "Setting permissions..."
chown -R 1000:1000 media/ shares/ homepage/
chmod -R 755 media/ shares/ homepage/

# Create media subdirectories
print_status "Setting up media directories..."
mkdir -p media/movies media/tv-shows media/music media/audiobooks
mkdir -p media/documentaries media/podcasts media/radio-recordings

# Install RaspAP for WiFi AP management
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    print_status "Raspberry Pi detected - installing RaspAP for WiFi management"
    
    # Check if RaspAP is already installed
    if [ ! -d "/var/www/html/raspap" ]; then
        print_status "Downloading and installing RaspAP..."
        
        # Download RaspAP installer
        curl -sL https://install.raspap.com > /tmp/raspap_install.sh
        
        # Run RaspAP Quick Installer (non-interactive)
        print_status "Installing RaspAP with default settings..."
        bash /tmp/raspap_install.sh --yes --openvpn 0 --adblock 0 --wireguard 0
        
        print_success "RaspAP installed successfully"
        
        # Configure RaspAP with custom Prepper Pi settings
        print_status "Configuring Prepper Pi network settings..."
        
        # Configure lighttpd to use port 8080
        if [ -f /etc/lighttpd/lighttpd.conf ]; then
            sed -i 's/server.port.*=.*80/server.port = 8080/' /etc/lighttpd/lighttpd.conf
        fi
        
        # Detect WiFi interfaces - we need two: one for upstream (wlan0), one for AP (wlan1)
        print_status "Detecting WiFi interfaces..."
        if ip link show wlan1 &> /dev/null; then
            print_status "Dual WiFi detected: wlan0 (upstream) and wlan1 (AP)"
            AP_INTERFACE="wlan1"
            UPSTREAM_INTERFACE="wlan0"
        else
            print_warning "Only one WiFi interface detected - using wlan0 for AP"
            AP_INTERFACE="wlan0"
            UPSTREAM_INTERFACE="eth0"
        fi
        
        # Configure hostapd to use the correct AP interface
        if [ -f /etc/hostapd/hostapd.conf ]; then
            print_status "Configuring hostapd on $AP_INTERFACE..."
            sed -i "s/^interface=.*/interface=$AP_INTERFACE/" /etc/hostapd/hostapd.conf
            sed -i 's/^ssid=.*/ssid=Prepper Pi/' /etc/hostapd/hostapd.conf
            sed -i 's/^wpa_passphrase=.*/wpa_passphrase=ChangeMeNow!/' /etc/hostapd/hostapd.conf
            
            # Add or update channel and hardware mode for better compatibility
            if ! grep -q "^channel=" /etc/hostapd/hostapd.conf; then
                echo "channel=6" >> /etc/hostapd/hostapd.conf
            else
                sed -i 's/^channel=.*/channel=6/' /etc/hostapd/hostapd.conf
            fi
        fi
        
        # Note: dnsmasq configuration will be handled by simple-passthrough.sh
        # to avoid DNS wildcard hijacking that breaks internet access
        
        # Configure AP interface with 10.20.30.1
        if [ -f /etc/dhcpcd.conf ]; then
            print_status "Configuring $AP_INTERFACE with static IP 10.20.30.1..."
            # Remove any existing wlan0/wlan1 configuration
            sed -i '/interface wlan[01]/,/nohook wpa_supplicant/d' /etc/dhcpcd.conf
            
            # Add configuration for AP interface
            cat >> /etc/dhcpcd.conf << EOF

# Prepper Pi AP Interface Configuration
interface $AP_INTERFACE
    static ip_address=10.20.30.1/24
    nohook wpa_supplicant
EOF
        fi
        
        # Note: Captive portal configuration (DNS, firewall, detection) is handled by
        # running scripts/simple-passthrough.sh after Docker services are started
        
        # Configure nodogsplash for captive portal (if available)
        if command -v nodogsplash &> /dev/null; then
            print_status "Configuring nodogsplash captive portal..."
            cat > /etc/nodogsplash/nodogsplash.conf << EOF
GatewayInterface $AP_INTERFACE
GatewayAddress 10.20.30.1
MaxClients 250
AuthIdleTimeout 480
RedirectURL http://10.20.30.1:3000
EOF
            systemctl enable nodogsplash
        fi
        
        # Restart services
        print_status "Restarting network services..."
        systemctl restart dhcpcd
        systemctl restart dnsmasq
        systemctl restart hostapd
        systemctl restart lighttpd
        
        print_success "Prepper Pi WiFi configured: SSID='Prepper Pi', Gateway=10.20.30.1"
        print_warning "Default WiFi password: ChangeMeNow! (change via RaspAP)"
        print_warning "RaspAP admin: admin/secret (change immediately)"
        
        # Configure simple internet passthrough (no captive portal)
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ -f "$SCRIPT_DIR/simple-passthrough.sh" ]; then
            print_status "Configuring internet passthrough..."
            bash "$SCRIPT_DIR/simple-passthrough.sh"
        else
            print_warning "simple-passthrough.sh not found. Run it manually after setup."
        fi
    else
        print_status "RaspAP is already installed"
        
        # Configure internet passthrough if not done
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ -f "$SCRIPT_DIR/simple-passthrough.sh" ]; then
            print_status "Configuring internet passthrough..."
            bash "$SCRIPT_DIR/simple-passthrough.sh"
        fi
    fi
else
    print_warning "Not running on Raspberry Pi - skipping RaspAP installation"
fi

# Download Docker images
print_status "Pulling Docker images..."
docker compose pull

# Create macvlan network helper script
print_status "Creating network helper script..."
cat > setup-macvlan.sh << EOF
#!/bin/bash
# Helper script to create macvlan network for OpenWRT

# Remove existing network if it exists
docker network rm openwrt_net 2>/dev/null || true

# Create macvlan network
docker network create -d macvlan \
    --subnet=10.20.30.0/24 \
    --gateway=10.20.30.1 \
    --ip-range=10.20.30.0/24 \
    -o parent=$INTERFACE \
    openwrt_net

echo "Macvlan network created successfully"
EOF

chmod +x setup-macvlan.sh

# Set up bridge interface for host connectivity
print_status "Setting up host bridge interface..."
cat > setup-host-bridge.sh << EOF
#!/bin/bash
# Create bridge interface for host to communicate with macvlan network

# Create macvlan interface for host
ip link add macvlan-host link $INTERFACE type macvlan mode bridge
ip addr add ${HOST_LAN_IP:-10.20.30.40}/24 dev macvlan-host
ip link set macvlan-host up

# Add route to reach OpenWRT network
ip route add 10.20.30.0/24 dev macvlan-host

echo "Host bridge interface created"
EOF

chmod +x setup-host-bridge.sh

# Create startup script for network setup (only if macvlan enabled)
if [ "${ENABLE_MACVLAN:-0}" = "1" ]; then
    print_status "Creating network startup script..."
    cat > /etc/systemd/system/prepper-pi-network.service << 'EOF'
[Unit]
Description=Prepper Pi Network Setup
After=network.target docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=$(pwd)/setup-host-bridge.sh
StandardOutput=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl enable prepper-pi-network.service
fi

# Create WiFi USB adapter configuration script and a fallback host AP script
print_status "Creating WiFi adapter setup scripts..."

# Main adapter info/helper (placeholder for future expansion)
cat > setup-wifi-adapter.sh << 'EOF_SETUP_WIFI'
#!/usr/bin/env bash
set -euo pipefail

echo "This script is a placeholder for adapter-specific tweaks."
echo "For emergency host-based AP (fallback), run: ./setup-wifi-adapter-fallback.sh"
EOF_SETUP_WIFI

# Fallback host-based AP (only if container AP fails)
cat > setup-wifi-adapter-fallback.sh << 'EOF_FALLBACK'
#!/usr/bin/env bash
set -euo pipefail

echo "⚠️  Setting up fallback host-based WiFi AP..."
echo "⚠️  This conflicts with OpenWRT container AP mode!"
echo "⚠️  Only run this if container AP fails."

read -p "Continue with host AP setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo "[INFO] Setting up WiFi adapter for AP mode..."

# Install required packages for WiFi AP
apt update
apt install -y hostapd dnsmasq

# Stop services
systemctl stop hostapd || true
systemctl stop dnsmasq || true

# Backup original configurations
cp /etc/hostapd/hostapd.conf /etc/hostapd/hostapd.conf.backup 2>/dev/null || true
cp /etc/dnsmasq.conf /etc/dnsmasq.conf.backup 2>/dev/null || true

# Create hostapd configuration for external WiFi adapter
cat > /etc/hostapd/hostapd.conf << 'EOL'
interface=wlan1
driver=nl80211
ssid=Prepper Pi Setup
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
EOL

# Configure dnsmasq for setup mode
cat > /etc/dnsmasq.conf << 'EOL'
interface=wlan1
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOL

echo "[INFO] Host WiFi AP configured. This may conflict with OpenWRT container."
echo "[WARN] Note: The host-based AP conflicts with the OpenWrt container AP. Prefer one approach at a time."
EOF_FALLBACK

chmod +x setup-wifi-adapter.sh setup-wifi-adapter-fallback.sh

# Create convenience scripts
print_status "Creating convenience scripts..."

# Status check script
cat > status.sh << EOF
#!/bin/bash
echo "🔍 Prepper Pi Status Check"
echo "=========================="
echo "Docker Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Network Interfaces:"
ip addr show | grep -E "(inet|UP|DOWN)"
echo ""
echo "RaspAP Status:"
systemctl status lighttpd | grep -E "(Active|Main PID)" || echo "RaspAP not running"
systemctl status hostapd | grep -E "(Active|Main PID)" || echo "hostapd not running"
EOF

chmod +x status.sh

# Restart script
cat > restart.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting Prepper Pi services..."
docker compose down
[ "${ENABLE_MACVLAN:-0}" = "1" ] && ./setup-host-bridge.sh
docker compose up -d
echo "Restarting RaspAP services..."
systemctl restart lighttpd
systemctl restart hostapd
echo "✅ Services restarted"
EOF

chmod +x restart.sh

# Logs script
cat > logs.sh << EOF
#!/bin/bash
if [ "$1" ]; then
    docker compose logs -f "$1"
else
    echo "Available services:"
    docker compose ps --services
    echo ""
    echo "Usage: ./logs.sh [service-name]"
    echo "Example: ./logs.sh openwrt"
fi
EOF

chmod +x logs.sh

# Create README for post-setup
print_status "Creating post-setup README..."
cat > POST-SETUP.md << 'EOF'
# Prepper Pi - Post Setup Instructions

## 🎉 Setup Complete!

Your Prepper Pi is now configured. Here's what's been set up:

### 🔧 Services Running:
- **RaspAP**: WiFi AP management at http://10.20.30.1:8080
- **Homepage**: Landing page at http://10.20.30.1:3000
- **Portainer**: Container management at http://10.20.30.1:9000
- **Jellyfin**: Media server at http://10.20.30.1:8096
- **Samba**: File sharing (\\10.20.30.1)

### 📁 Directory Structure:
- media/: Place your media files here for Jellyfin
- shares/: Public file sharing via Samba

### 🔨 Useful Commands:
- `./status.sh`: Check system status
- `./restart.sh`: Restart all services
- `./logs.sh [service]`: View service logs
- `docker compose up -d`: Start services
- `docker compose down`: Stop services

### 🌐 Next Steps:

1. **Configure External WiFi Adapter (ALFA AWUS036ACM)**:
   ```bash
   sudo ./setup-wifi-adapter.sh
   ```

2. **Access the Landing Page**:
   - Connect to your network
   - Visit `http://prepper-pi.local:3000` or `http://10.20.30.1:3000`

3. **Configure OpenWRT**:
   - Visit `http://10.20.30.1`
   - Set up your wireless networks and routing

4. **Add Media to Jellyfin**:
   - Copy media files to `media/` subdirectories
   - Configure Jellyfin libraries

5. **Test WiFi Hotspot**:
   - OpenWRT should broadcast "Prepper Pi" SSID
   - Connect and test access to services

### 📱 Mobile Access:
Once the WiFi hotspot is active, connect to "Prepper Pi" and visit:
- `http://10.20.30.1` - Captive portal landing page
- `http://10.20.30.1:3000` - Homepage dashboard
- `http://10.20.30.1` - Router admin

### 🚨 Troubleshooting:
- Check status: `./status.sh`
- View logs: `./logs.sh openwrt`
- Restart services: `./restart.sh`
- Check network: `ip addr show`

Enjoy your Prepper Pi! 🥧
EOF

# Final setup steps
print_status "Running final setup steps..."

# Set up host bridge (only if macvlan enabled)
[ "${ENABLE_MACVLAN:-0}" = "1" ] && ./setup-host-bridge.sh

# Start services
print_status "Starting Prepper Pi services..."
docker compose up -d

# Wait for services to start
print_status "Waiting for services to initialize..."
sleep 30

# Check status
print_status "Checking service status..."
docker compose ps

print_success "Prepper Pi setup completed successfully!"
print_success "Please read POST-SETUP.md for next steps"

echo ""
echo "🌟 Quick Access URLs (from WiFi clients):"
echo "   - Landing Page: http://10.20.30.1:3000 (auto-opens on connect)"
echo "   - RaspAP Router: http://10.20.30.1:8080 (admin/secret)"
echo "   - Portainer: http://10.20.30.1:9000"
echo "   - Jellyfin: http://10.20.30.1:8096"
echo ""
echo "📡 WiFi Access Point:"
echo "   SSID: Prepper Pi"
echo "   Password: ChangeMeNow!"
echo "   Gateway: 10.20.30.1"
echo "   DHCP Range: 10.20.30.100-199"
echo ""
echo "🔒 IMPORTANT - Change these immediately:"
echo "   1. WiFi password via RaspAP: http://10.20.30.1:8080"
echo "   2. RaspAP admin password (currently: admin/secret)"
echo "   3. Portainer admin password on first login"
echo ""
echo "📖 For detailed instructions, see: POST-SETUP.md"
echo "🔧 Check status anytime with: ./status.sh"
echo ""
echo "⚠️  NEXT STEPS:"
echo "   1. Start Docker services:"
echo "      cp compose/docker-compose.pi.yml docker-compose.override.yml"
echo "      docker compose up -d"
echo ""
echo "   2. Test connectivity from a WiFi client:"
echo "      - Connect to 'Prepper Pi' WiFi"
echo "      - Test internet access"
echo "      - Browse to http://10.20.30.1:3000"
echo ""
echo "   See docs/QUICK-DEPLOY-CHECKLIST.md for full testing guide"
echo ""
