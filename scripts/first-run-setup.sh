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

# Detect if running on Raspberry Pi and set up compose files
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    print_status "Raspberry Pi detected - using Pi-specific configuration"
    COMPOSE_FILES=(-f docker-compose.yml -f compose/docker-compose.pi.yml)
else
    print_status "Non-Pi system detected - using standard configuration"
    COMPOSE_FILES=(-f docker-compose.yml)
fi

# Download Docker images
print_status "Pulling Docker images..."
echo "DEBUG: Running: docker compose ${COMPOSE_FILES[@]} pull"
docker compose "${COMPOSE_FILES[@]}" pull

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
echo "OpenWRT Status:"
docker exec openwrt uci show network 2>/dev/null || echo "OpenWRT not running"
EOF

chmod +x status.sh

# Restart script
cat > restart.sh << 'EOF'
#!/bin/bash
echo "🔄 Restarting Prepper Pi services..."
if grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null || grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    COMPOSE_FILES=(-f docker-compose.yml -f compose/docker-compose.pi.yml)
else
    COMPOSE_FILES=(-f docker-compose.yml)
fi
docker compose "${COMPOSE_FILES[@]}" down
[ "${ENABLE_MACVLAN:-0}" = "1" ] && ./setup-host-bridge.sh
docker compose "${COMPOSE_FILES[@]}" up -d
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
cat > POST-SETUP.md << EOF
# Prepper Pi - Post Setup Instructions

## 🎉 Setup Complete!

Your Prepper Pi is now configured. Here's what's been set up:

### 🔧 Services Running:
- **OpenWRT**: Router/firewall at `10.20.30.1`
- **Homepage**: Landing page at `http://prepper-pi.local:3000`
- **Portainer**: Container management at `http://10.20.30.1:9000`
- **Jellyfin**: Media server at `http://10.20.30.1:8096`
- **Samba**: File sharing (\\\\10.20.30.1)

### 📁 Directory Structure:
- `media/`: Place your media files here for Jellyfin
- `shares/`: Public file sharing via Samba
- `openwrt/config/`: OpenWRT configuration files

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
docker compose "${COMPOSE_FILES[@]}" up -d

# Wait for services to start
print_status "Waiting for services to initialize..."
sleep 30

# Check status
print_status "Checking service status..."
docker compose ps

print_success "Prepper Pi setup completed successfully!"
print_success "Please read POST-SETUP.md for next steps"

echo ""
echo "🌟 Quick Access URLs:"
echo "   - Landing Page: http://prepper-pi.local:3000"
echo "   - OpenWRT Admin: http://10.20.30.1"
echo "   - Portainer: http://10.20.30.1:9000"
echo "   - Jellyfin: http://10.20.30.1:8096"
echo ""
echo "📖 For detailed instructions, see: POST-SETUP.md"
echo "🔧 Check status anytime with: ./status.sh"
