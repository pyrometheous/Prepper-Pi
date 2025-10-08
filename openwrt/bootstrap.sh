#!/bin/sh

# OpenWRT Bootstrap Script
# Installs required pa    uci set wireless.@wifi-iface[1].ssid='Prepper Pi'
    uci set wireless.@wifi-iface[1].encryption='psk2'
    uci set wireless.@wifi-iface[1].key='PrepperPi2025!'ges for WiFi AP and captive portal functionality

echo "🚀 Bootstrapping OpenWRT container..."

# Update package lists and install packages (only on first boot)
FLAG=/root/.prepper_pi_bootstrap_done
if [ ! -f "$FLAG" ]; then
    echo "📦 First boot: updating package lists..."
    opkg update
    echo "📡 Installing wireless, firewall and captive portal packages..."
    # Core wireless + portal
    opkg install opennds iw wpad-basic-mbedtls dnsmasq-full uhttpd uhttpd-mod-ubus luci luci-compat
    # Firewall (fw4 / nftables) so DNAT redirects work
    opkg install firewall4 nftables ip-full kmod-nft-core kmod-nft-nat kmod-nft-bridge
    touch "$FLAG"
else
    echo "📦 Packages already installed, skipping update..."
fi

# Enable and configure services with existence checks
echo "⚙️ Enabling services..."
en() { [ -x "/etc/init.d/$1" ] && /etc/init.d/$1 enable; }
rs() { [ -x "/etc/init.d/$1" ] && /etc/init.d/$1 restart; }

en network
en dnsmasq
en opennds
en uhttpd
en rpcd
en firewall

echo "📶 Configuring wireless..."
# Only proceed if at least one 802.11 radio is present
if [ -d /sys/class/ieee80211 ] && [ "$(ls -A /sys/class/ieee80211 2>/dev/null)" ]; then
  # Set regulatory domain first
  iw reg set US
  # Generate fresh config to learn the correct paths, then apply my settings.
  rm -f /etc/config/wireless
  wifi config

  # 2.4 GHz (index 0) — if present
  if uci -q get wireless.@wifi-iface[0] >/dev/null; then
    uci set wireless.@wifi-device[0].country='US'
    uci set wireless.@wifi-device[0].disabled='0'
    uci set wireless.@wifi-iface[0].mode='ap'
    uci set wireless.@wifi-iface[0].network='lan'
    uci set wireless.@wifi-iface[0].ssid='Prepper Pi'
    uci set wireless.@wifi-iface[0].encryption='psk2'
    uci set wireless.@wifi-iface[0].key='PrepperPi2025!'
  fi

  # 5 GHz (index 1) — if present
  if uci -q get wireless.@wifi-iface[1] >/dev/null; then
    uci set wireless.@wifi-device[1].country='US'
    uci set wireless.@wifi-device[1].disabled='0'
    uci set wireless.@wifi-iface[1].mode='ap'
    uci set wireless.@wifi-iface[1].network='lan'
    uci set wireless.@wifi-iface[1].ssid='Prepper Pi 5G'
    uci set wireless.@wifi-iface[1].encryption='psk2'
    uci set wireless.@wifi-iface[1].key='PrepperPi2025!'
  fi

  uci commit wireless
  wifi reload
else
  echo "⚠️  No radios detected; skipping wireless config"
fi

# Set hostname
uci set system.@system[0].hostname='prepper-pi'
uci commit system

# Configure DNS upstreams for offline operation
echo "🌐 Configuring DNS upstreams..."
uci set dhcp.@dnsmasq[0].noresolv='1'
uci add_list dhcp.@dnsmasq[0].server='1.1.1.1'
uci add_list dhcp.@dnsmasq[0].server='9.9.9.9'
uci commit dhcp

echo "🚦 Restarting network and captive portal..."
rs network
rs dnsmasq
rs opennds
rs uhttpd
rs rpcd
rs firewall
wifi reload

echo "✅ Bootstrap complete, starting init..."
