#!/bin/sh

# OpenWRT Bootstrap Script
# Installs required packages for WiFi AP and captive portal functionality

echo "🚀 Bootstrapping OpenWRT container..."

# Update package lists
echo "📦 Updating package lists..."
opkg update

# Install essential wireless and captive portal packages
echo "📡 Installing wireless and captive portal packages..."
opkg install opennds iw wpad-basic-mbedtls hostapd dnsmasq-full

# Enable and configure services
echo "⚙️ Enabling services..."
/etc/init.d/opennds enable
/etc/init.d/network enable
/etc/init.d/wireless enable
/etc/init.d/dnsmasq enable
/etc/init.d/firewall enable

# Set up initial wireless configuration if it doesn't exist
echo "📶 Configuring wireless..."
if [ ! -f /etc/config/wireless ] || [ ! -s /etc/config/wireless ]; then
    echo "🔧 Generating initial wireless config..."
    wifi config
    wifi reload
fi

echo "✅ Bootstrap complete, starting init..."
