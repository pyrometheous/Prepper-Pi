# Native hostapd + RaspAP Implementation

This branch uses native Raspberry Pi networking with RaspAP web interface instead of OpenWrt container.

## What Changed

### Removed
- OpenWrt Docker container
- Complex multi-compose file setup
- OpenWrt-specific configurations

### Added
- **RaspAP** - Web-based WiFi management interface
- Native hostapd/dnsmasq for AP functionality
- Simplified setup process

## Features

### RaspAP Web Interface (Port 8080)
- **WiFi Configuration**: SSID, password, channel, country code
- **DHCP Server**: IP range management
- **Internet Passthrough**: Share internet connection via WiFi AP
- **Client Management**: View connected devices
- **System Information**: Resource monitoring
- **Network Settings**: Advanced networking options

### Default Configuration
- **RaspAP URL**: `http://prepper-pi.local:8080`
- **Default Login**: `admin` / `secret`
- **Default SSID**: `raspi-webgui`
- **Default WiFi Password**: `ChangeMe`

## Installation

Same as main branch:

```bash
sudo apt update && sudo apt install -y git && \
git clone -b feature/native-hostapd https://github.com/pyrometheous/Prepper-Pi.git && \
cd Prepper-Pi && \
sudo bash scripts/first-run-setup.sh
```

## Post-Installation Steps

1. **Access RaspAP**: http://prepper-pi.local:8080
   - Login with `admin` / `secret`

2. **Configure WiFi**:
   - Navigate to "Hotspot" > "Basic"
   - Change SSID from `raspi-webgui` to your desired name
   - Set WiFi password (minimum 8 characters)
   - Select your country code
   - Click "Save settings" and "Restart hotspot"

3. **Change RaspAP Password**:
   - Navigate to "System" > "Authentication"
   - Change admin password from default `secret`

4. **Configure Internet Passthrough**:
   - RaspAP handles this automatically
   - Check "Hotspot" > "Advanced" for routing options
   - Ensure "Internet sharing" is enabled

5. **Access Homepage Dashboard**: http://prepper-pi.local:3000
   - RaspAP link is in the "System" section

## Architecture

```
┌─────────────────────────────────────┐
│       Raspberry Pi Host             │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ RaspAP (Port 8080)            │ │
│  │  - hostapd (WiFi AP)          │ │
│  │  - dnsmasq (DHCP)             │ │
│  │  - lighttpd (Web UI)          │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ Docker Containers             │ │
│  │  - Homepage (3000)            │ │
│  │  - Portainer (9000)           │ │
│  │  - Jellyfin (8096)            │ │
│  │  - Samba (445)                │ │
│  └───────────────────────────────┘ │
│                                     │
│  wlan0: WiFi AP                    │
│  eth0/wlan1: Internet connection   │
└─────────────────────────────────────┘
```

## Advantages Over OpenWrt Container

1. **Better Pi Integration**: Native tools designed for Raspberry Pi
2. **Lighter Resource Usage**: ~50-100MB RAM vs 200-300MB for OpenWrt
3. **Easier Troubleshooting**: Standard Pi networking tools
4. **Direct Hardware Access**: No container passthrough needed
5. **Proven Reliability**: Used by thousands of Pi users
6. **Simple Updates**: Standard apt package management

## RaspAP Features

### Included
- ✅ WiFi Access Point management
- ✅ DHCP server configuration
- ✅ Internet connection sharing
- ✅ Client device monitoring
- ✅ Basic firewall rules
- ✅ System information display
- ✅ Multiple WiFi configurations
- ✅ Wireless regulatory domain setting

### Optional (Can be enabled)
- 🔌 OpenVPN client
- 🔌 WireGuard VPN
- 🔌 Ad blocking (Pi-hole style)
- 🔌 Captive portal
- 🔌 Tor proxy

## Troubleshooting

### WiFi AP not broadcasting
```bash
sudo systemctl status hostapd
sudo systemctl restart hostapd
```

### Can't access RaspAP web interface
```bash
sudo systemctl status lighttpd
# Check if running on port 8080
sudo netstat -tlnp | grep 8080
```

### No internet on connected clients
```bash
# Check IP forwarding
cat /proc/sys/net/ipv4/ip_forward  # Should be 1

# Check iptables rules
sudo iptables -t nat -L -v
```

### RaspAP logs
```bash
sudo journalctl -u hostapd
sudo journalctl -u dnsmasq
sudo tail -f /var/log/lighttpd/error.log
```

## Useful Commands

```bash
# Check WiFi interface
iw dev

# See connected clients
iw dev wlan0 station dump

# RaspAP service status
sudo systemctl status raspap

# Restart WiFi services
sudo systemctl restart hostapd dnsmasq

# View hostapd configuration
cat /etc/hostapd/hostapd.conf

# View DHCP leases
cat /var/lib/misc/dnsmasq.leases
```

## Customization

### Change RaspAP Port
```bash
sudo nano /etc/lighttpd/lighttpd.conf
# Change: server.port = 8080
sudo systemctl restart lighttpd
```

### Custom WiFi Defaults
Edit before first-run-setup:
```bash
# In scripts/first-run-setup.sh
# Look for RaspAP installation section
# Modify default SSID/password after installation via web UI
```

## Security Recommendations

1. **Change RaspAP password** from default `secret`
2. **Set strong WiFi password** (WPA2 recommended)
3. **Keep system updated**: `sudo apt update && sudo apt upgrade`
4. **Configure firewall** via RaspAP if exposing to internet
5. **Disable WPS** in RaspAP settings
6. **Use MAC filtering** if needed (Advanced settings)

## Comparison: RaspAP vs OpenWrt

| Feature | RaspAP | OpenWrt Container |
|---------|--------|-------------------|
| Setup Time | ~5 minutes | ~15 minutes |
| RAM Usage | 50-100 MB | 200-300 MB |
| Web UI | Simple, focused | Feature-rich, complex |
| Pi Support | Excellent | Moderate |
| Package Ecosystem | Limited | Extensive (opkg) |
| Captive Portal | Optional addon | Built-in (openNDS) |
| VLANs | Basic | Advanced |
| Updates | apt-get | opkg/rebuild image |

## Additional Resources

- [RaspAP Documentation](https://docs.raspap.com/)
- [RaspAP GitHub](https://github.com/RaspAP/raspap-webgui)
- [hostapd Documentation](https://w1.fi/hostapd/)
- [Raspberry Pi Networking](https://www.raspberrypi.com/documentation/computers/configuration.html#wireless-networking)
