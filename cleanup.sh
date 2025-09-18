#!/bin/bash

# Prepper Pi - Cleanup Script
# This script removes all Prepper Pi components and configurations

set -e

echo "🧹 Starting Prepper Pi Cleanup..."

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

# Confirmation prompt
print_warning "This will completely remove all Prepper Pi components!"
print_warning "This includes:"
print_warning "  - All Docker containers and images"
print_warning "  - All configuration files"
print_warning "  - All media and share files"
print_warning "  - Network configurations"
print_warning "  - System services"

read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Cleanup cancelled."
    exit 0
fi

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Stop and remove Docker containers
print_status "Stopping and removing Docker containers..."
docker-compose down -v --remove-orphans 2>/dev/null || true

# Remove Docker images
print_status "Removing Docker images..."
docker rmi $(docker images -q --filter "reference=openwrt/*") 2>/dev/null || true
docker rmi $(docker images -q --filter "reference=traefik:*") 2>/dev/null || true
docker rmi $(docker images -q --filter "reference=portainer/*") 2>/dev/null || true
docker rmi $(docker images -q --filter "reference=jellyfin/*") 2>/dev/null || true
docker rmi $(docker images -q --filter "reference=ghcr.io/gethomepage/*") 2>/dev/null || true
docker rmi $(docker images -q --filter "reference=dperson/samba") 2>/dev/null || true

# Remove Docker networks
print_status "Removing Docker networks..."
docker network rm openwrt_net 2>/dev/null || true

# Remove macvlan host interface
print_status "Removing host network interfaces..."
ip link delete macvlan-host 2>/dev/null || true

# Remove system service
print_status "Removing system service..."
systemctl stop prepper-pi-network.service 2>/dev/null || true
systemctl disable prepper-pi-network.service 2>/dev/null || true
rm -f /etc/systemd/system/prepper-pi-network.service
systemctl daemon-reload

# Clean up hostapd and dnsmasq configurations
print_status "Cleaning up WiFi configurations..."
systemctl stop hostapd 2>/dev/null || true
systemctl stop dnsmasq 2>/dev/null || true

# Restore backups if they exist
if [ -f "/etc/hostapd/hostapd.conf.backup" ]; then
    mv /etc/hostapd/hostapd.conf.backup /etc/hostapd/hostapd.conf
fi

if [ -f "/etc/dnsmasq.conf.backup" ]; then
    mv /etc/dnsmasq.conf.backup /etc/dnsmasq.conf
fi

# Remove IP forwarding settings (comment them out instead of removing)
print_status "Disabling IP forwarding..."
sed -i 's/^net.ipv4.ip_forward=1/#net.ipv4.ip_forward=1/' /etc/sysctl.conf 2>/dev/null || true
sed -i 's/^net.ipv6.conf.all.forwarding=1/#net.ipv6.conf.all.forwarding=1/' /etc/sysctl.conf 2>/dev/null || true

# Remove kernel modules from auto-load
print_status "Removing kernel modules from auto-load..."
sed -i '/^tun$/d' /etc/modules 2>/dev/null || true
sed -i '/^bridge$/d' /etc/modules 2>/dev/null || true
sed -i '/^br_netfilter$/d' /etc/modules 2>/dev/null || true

# Clean up project files (but preserve user data)
print_status "Cleaning up project files..."
rm -f setup-macvlan.sh
rm -f setup-host-bridge.sh
rm -f setup-wifi-adapter.sh
rm -f status.sh
rm -f restart.sh
rm -f logs.sh
rm -f POST-SETUP.md

# Remove empty directories
print_status "Removing empty directories..."
find openwrt homepage -type d -empty -delete 2>/dev/null || true

# Remove Docker volumes
print_status "Removing Docker volumes..."
docker volume rm $(docker volume ls -q --filter "name=prepper-pi") 2>/dev/null || true
docker volume rm portainer_data 2>/dev/null || true
docker volume rm jellyfin_config 2>/dev/null || true
docker volume rm jellyfin_cache 2>/dev/null || true

# System cleanup
print_status "Cleaning up system..."
docker system prune -af 2>/dev/null || true

# Optional: Remove Docker entirely
print_warning "Docker and related packages are still installed."
read -p "Do you want to remove Docker and related packages? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Removing Docker and related packages..."
    apt remove -y docker.io docker-compose
    apt autoremove -y
    
    # Remove user from docker group
    if [ "$SUDO_USER" ]; then
        deluser "$SUDO_USER" docker 2>/dev/null || true
    fi
fi

# Final cleanup
print_status "Performing final cleanup..."
apt autoremove -y 2>/dev/null || true

print_success "Prepper Pi cleanup completed!"
print_status "The following directories contain your data and were preserved:"
print_status "  - media/ (your media files)"
print_status "  - shares/ (your shared files)"
print_status ""
print_warning "To completely remove all data, manually delete:"
print_warning "  rm -rf media/ shares/"
print_status ""
print_success "System restored to pre-Prepper Pi state."
# cleanup script placeholder