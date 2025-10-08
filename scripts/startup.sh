#!/bin/bash

# Prepper Pi - Startup Script
# This script starts the Prepper Pi services and performs health checks

set -e

echo "🚀 Starting Prepper Pi..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Configuration flags
ENABLE_MACVLAN=${ENABLE_MACVLAN:-0}
HOST_LAN_IP=${HOST_LAN_IP:-10.20.30.40}

# Check if Docker is running
print_status "Checking Docker service..."
if ! systemctl is-active --quiet docker; then
    print_status "Starting Docker service..."
    sudo systemctl start docker
    sleep 5
fi

# Check network interface
print_status "Checking network setup..."
INTERFACE=$(ip route | grep default | head -1 | awk '{print $5}')
if [ -z "$INTERFACE" ]; then
    print_warning "No default network interface found"
    INTERFACE="eth0"
fi
print_status "Using network interface: $INTERFACE"

# Set up host bridge if enabled and doesn't exist
if [ "$ENABLE_MACVLAN" = "1" ] && ! ip link show macvlan-host > /dev/null 2>&1; then
    print_status "Setting up host bridge interface..."
    sudo ip link add macvlan-host link $INTERFACE type macvlan mode bridge
    sudo ip addr add ${HOST_LAN_IP:-10.20.30.40}/24 dev macvlan-host
    sudo ip link set macvlan-host up
    sudo ip route add 10.20.30.0/24 dev macvlan-host 2>/dev/null || true
fi

# Check if macvlan network exists (only if enabled)
if [ "$ENABLE_MACVLAN" = "1" ] && ! docker network ls | grep -q openwrt_net; then
    print_status "Creating macvlan network..."
    docker network create -d macvlan \
        --subnet=10.20.30.0/24 \
        --gateway=10.20.30.1 \
        --ip-range=10.20.30.0/24 \
        -o parent=$INTERFACE \
        openwrt_net
fi

# Create required directories
print_status "Creating directories..."
mkdir -p media/{movies,tv,music,books}
mkdir -p shares/{public,documents}
mkdir -p openwrt/{config,data}
mkdir -p homepage/icons

# Start services
print_status "Starting Prepper Pi services..."
docker-compose up -d

# Wait for services to start
print_status "Waiting for services to initialize..."
sleep 30

# Health checks
print_status "Performing health checks..."

# Check OpenWRT
if docker exec openwrt uci show network > /dev/null 2>&1; then
    print_success "✅ OpenWRT is running"
else
    print_warning "⚠️  OpenWRT may need configuration"
fi

# Check Homepage
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    print_success "✅ Homepage is accessible"
else
    print_warning "⚠️  Homepage not accessible yet"
fi

# Check Portainer
if curl -s http://localhost:9000 > /dev/null 2>&1; then
    print_success "✅ Portainer is accessible"
else
    print_warning "⚠️  Portainer not accessible yet"
fi

# Check Jellyfin
if curl -s http://localhost:8096 > /dev/null 2>&1; then
    print_success "✅ Jellyfin is accessible"
else
    print_warning "⚠️  Jellyfin not accessible yet"
fi

# Display status
print_status "Current service status:"
docker-compose ps

echo ""
print_success "Prepper Pi startup completed!"
echo ""
echo "🌟 Access URLs:"
echo "   - Landing Page: http://10.20.30.1:3000 or http://prepper-pi.local:3000"
echo "   - OpenWRT: http://10.20.30.1"
echo "   - Portainer: http://10.20.30.1:9000"
echo "   - Jellyfin: http://10.20.30.1:8096"
echo ""
echo "📱 WiFi Hotspot: Connect to 'Prepper Pi' (WPA2, password: PrepperPi2025!)"
echo "🔧 System Status: ./status.sh"
echo "📋 View Logs: ./logs.sh [service-name]"
