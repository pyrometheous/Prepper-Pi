#!/bin/sh
set -e

# OpenWrt Bootstrap Script
# Installs required packages for WiFi AP and captive portal functionality

echo "🚀 Bootstrapping OpenWRT container..."

# WiFi configuration (overridable via container env)
WIFI_COUNTRY=${WIFI_COUNTRY:-US}
WIFI_SSID_24=${WIFI_SSID_24:-Prepper Pi}
WIFI_SSID_5G=${WIFI_SSID_5G:-Prepper Pi 5G}
WIFI_PASS=${WIFI_PASS:-ChangeMeNow!}
WIFI_ENC=${WIFI_ENC:-psk2}

# Update package lists and install packages (only on first boot)
FLAG=/root/.prepper_pi_bootstrap_done
if [ ! -f "$FLAG" ]; then
    echo "📦 First boot: updating package lists..."
    opkg update
  echo "📡 Installing wireless, firewall and captive portal packages..."
  # Core wireless + portal
  opkg install opennds iw wpad-basic-mbedtls dnsmasq-full uhttpd uhttpd-mod-ubus luci luci-compat || true
  # Firewall (fw4 / nftables) so DNAT redirects work (kernel modules may already be present on host)
  opkg install firewall4 nftables ip-full || true
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
  iw reg set "$WIFI_COUNTRY"
  # Generate fresh config to learn the correct paths, then apply my settings.
  rm -f /etc/config/wireless
  wifi config

  # 2.4 GHz (index 0) — if present
  if uci -q get wireless.@wifi-iface[0] >/dev/null; then
    uci set wireless.@wifi-device[0].country="$WIFI_COUNTRY"
    uci set wireless.@wifi-device[0].disabled='0'
    uci set wireless.@wifi-iface[0].mode='ap'
    uci set wireless.@wifi-iface[0].network='lan'
    uci set wireless.@wifi-iface[0].ssid="$WIFI_SSID_24"
    uci set wireless.@wifi-iface[0].encryption="$WIFI_ENC"
    uci set wireless.@wifi-iface[0].key="$WIFI_PASS"
  fi

  # 5 GHz (index 1) — if present
  if uci -q get wireless.@wifi-iface[1] >/dev/null; then
    uci set wireless.@wifi-device[1].country="$WIFI_COUNTRY"
    uci set wireless.@wifi-device[1].disabled='0'
    uci set wireless.@wifi-iface[1].mode='ap'
    uci set wireless.@wifi-iface[1].network='lan'
    uci set wireless.@wifi-iface[1].ssid="$WIFI_SSID_5G"
    uci set wireless.@wifi-iface[1].encryption="$WIFI_ENC"
    uci set wireless.@wifi-iface[1].key="$WIFI_PASS"
  fi

  uci commit wireless
  wifi reload
else
  echo "⚠️  No radios detected; skipping wireless config"
fi

# Set hostname (safe even if overridden by mounted config)
uci set system.@system[0].hostname='prepper-pi'
uci commit system

# Configure DNS upstreams for offline operation
echo "🌐 Configuring DNS upstreams..."
uci set dhcp.@dnsmasq[0].noresolv='1'
uci -q del_list dhcp.@dnsmasq[0].server='1.1.1.1' 2>/dev/null || true
uci -q del_list dhcp.@dnsmasq[0].server='9.9.9.9' 2>/dev/null || true
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
