#!/bin/sh

# OpenWRT Bootstrap Script
# Installs required packages for WiFi AP and captive portal functionality

echo "🚀 Bootstrapping OpenWRT container..."

# Update package lists
echo "📦 Updating package lists..."
opkg update

# Install essential wireless and captive portal packages
echo "📡 Installing wireless and captive portal packages..."
opkg install opennds iw wpad-basic-mbedtls dnsmasq-full

# Enable and configure services
echo "⚙️ Enabling services..."
/etc/init.d/opennds enable
/etc/init.d/network enable
/etc/init.d/wireless enable
/etc/init.d/dnsmasq enable
/etc/init.d/firewall enable

echo "📶 Configuring wireless..."
# Always generate fresh to learn the correct 'path' for radios, then apply our settings.
rm -f /etc/config/wireless
wifi config

# Apply our SSIDs and WPA2 to the generated radios
uci set wireless.@wifi-device[0].country='US'
uci set wireless.@wifi-device[0].disabled='0'
uci set wireless.@wifi-iface[0].ssid='Prepper Pi'
uci set wireless.@wifi-iface[0].encryption='psk2'
uci set wireless.@wifi-iface[0].key='PrepperPi2024!'

# Configure 5GHz radio if present
[ -n "$(uci -q get wireless.@wifi-iface[1])" ] && {
  uci set wireless.@wifi-device[1].country='US'
  uci set wireless.@wifi-device[1].disabled='0'
  uci set wireless.@wifi-iface[1].ssid='Prepper Pi 5G'
  uci set wireless.@wifi-iface[1].encryption='psk2'
  uci set wireless.@wifi-iface[1].key='PrepperPi2024!'
}

uci commit wireless
wifi reload

echo "✅ Bootstrap complete, starting init..."
