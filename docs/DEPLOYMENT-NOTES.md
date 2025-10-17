<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Deployment Notes - Fresh Install Testing

## Successful Deployment - October 16, 2025

### Test Environment
- **Hardware**: Raspberry Pi 5 (8GB)
- **OS**: Raspberry Pi OS Lite (64-bit, Debian Trixie)
- **Branch**: `feature/native-hostapd`
- **Method**: SSH deployment from Windows machine

### Critical Discovery: SSH PTY Requirement

**Problem**: RaspAP installer fails when run via SSH without a pseudo-TTY because it uses `tput` for terminal control.

**Error seen without `-t` flag**:
```
tput: unknown terminal "unknown"
RaspAP Install: Checking internet connectivity...
[Script exits]
```

**Solution**: Use `ssh -t` to allocate a pseudo-TTY

```bash
# ✅ Correct - with -t flag
ssh -t admin@192.168.50.99 "cd Prepper-Pi && sudo bash scripts/first-run-setup.sh"

# ❌ Incorrect - without -t flag  
ssh admin@192.168.50.99 "cd Prepper-Pi && sudo bash scripts/first-run-setup.sh"
```

### Deployment Process That Works

1. **Fresh Raspberry Pi OS Installation**
   - Use Raspberry Pi Imager
   - Enable SSH
   - Configure WiFi for internet access (wlan0)
   - Set hostname: `prepper-pi`
   - Set user: `admin`

2. **Clone Repository**
   ```bash
   ssh admin@<pi-ip>
   git clone https://github.com/pyrometheous/Prepper-Pi.git
   cd Prepper-Pi
   git checkout feature/native-hostapd
   ```

3. **Run Setup Script**
   ```bash
   sudo bash scripts/first-run-setup.sh
   ```
   
   Or remotely with `-t`:
   ```bash
   ssh -t admin@<pi-ip> "cd Prepper-Pi && sudo bash scripts/first-run-setup.sh"
   ```

4. **What Gets Installed Automatically**:
   - ✅ Docker & Docker Compose
   - ✅ RaspAP (WiFi AP management)
   - ✅ Captive portal (Python HTTP server)
   - ✅ DNS configuration (upstream servers, no wildcard hijacking)
   - ✅ Firewall rules (NAT + FORWARD chains)
   - ✅ Docker services (Homepage, Portainer, Jellyfin, Samba)

### Post-Installation Status

**Services running after successful deployment**:
```bash
● docker.service - running
● hostapd.service - running (WiFi AP)
● dnsmasq.service - running (DNS/DHCP)
● captive-portal.service - running (port 80 redirects)
● lighttpd.service - running (RaspAP web UI on port 8080)
```

**Docker containers**:
```
homepage    - Port 3000 (landing page)
portainer   - Port 9000 (container management)
samba       - Port 445 (file sharing)
```

### Issues Found & Fixed

#### 1. POST-SETUP.md Creation Error
**Error**:
```
scripts/first-run-setup.sh: line 421: 10.20.30.1: command not found
scripts/first-run-setup.sh: line 421: http://prepper-pi.local:3000: No such file or directory
```

**Cause**: Heredoc using `EOF` instead of `'EOF'` - backticks and special characters were being interpreted

**Fix**: Change `cat > POST-SETUP.md << EOF` to `cat > POST-SETUP.md << 'EOF'`

**Status**: ✅ Fixed in commit [pending]

#### 2. WiFi AP Not Broadcasting After Install
**Issue**: After installation completes, WiFi AP "Prepper Pi" not visible

**Potential causes**:
- hostapd may need manual start after RaspAP installation
- wlan1 interface may not be configured yet
- May need reboot to apply all network changes

**Next steps**: 
- Check `systemctl status hostapd`
- Check `iw dev` for interface status
- Verify `/etc/hostapd/hostapd.conf` configuration
- May need to run RaspAP initial setup via web UI

### Verification Checklist

After deployment, verify:

- [ ] `systemctl status docker` - Docker running
- [ ] `systemctl status hostapd` - WiFi AP service running
- [ ] `systemctl status dnsmasq` - DNS/DHCP running
- [ ] `systemctl status captive-portal` - Portal redirect running
- [ ] `docker ps` - All containers running
- [ ] `iw dev` - wlan1 interface in AP mode
- [ ] WiFi SSID "Prepper Pi" visible
- [ ] Can connect to WiFi and get 10.20.30.x IP
- [ ] Can access http://10.20.30.1:3000 (Homepage)
- [ ] Can access http://10.20.30.1:8080 (RaspAP)
- [ ] Internet passthrough works

### Deployment Time

**Total time**: ~10-12 minutes
- Package updates: 1-2 min
- Docker installation: 3-4 min
- RaspAP installation: 4-5 min
- Captive portal setup: 1 min
- Docker image pulls: 2-3 min

### Known Good Configuration

**Network interfaces**:
- `wlan0`: Upstream WiFi (internet connection)
- `wlan1`: AP interface (10.20.30.1/24) - requires ALFA AWUS036ACM or similar

**Firewall rules**:
```bash
# NAT for internet passthrough
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE

# FORWARD chain rules
iptables -I FORWARD 1 -i wlan1 -o wlan0 -j ACCEPT
iptables -I FORWARD 2 -i wlan0 -o wlan1 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

**DNS configuration** (`/etc/dnsmasq.d/090_raspap.conf`):
- Upstream DNS: 8.8.8.8, 8.8.4.4
- No wildcard hijacking
- Specific domains for captive portal detection

### Recommendations

1. **Always use `ssh -t` for remote deployments**
2. **Test WiFi AP after installation** - may need manual start/reboot
3. **Change default passwords immediately**:
   - RaspAP: admin/secret
   - WiFi: ChangeMeNow!
4. **Verify internet passthrough** before considering deployment complete
5. **Document any hardware-specific configurations** (WiFi adapter, etc.)

### Next Steps

1. Debug why WiFi AP doesn't start automatically
2. Test complete workflow: WiFi connects → internet works → captive portal appears
3. Validate on fresh Pi image to ensure repeatability
4. Consider adding post-install verification script
5. Add reboot step if needed for network changes to take effect

---

**Deployment validated**: October 16, 2025  
**Branch**: feature/native-hostapd  
**Tester**: pyrometheous  
**Platform**: Raspberry Pi 5, Pi OS Trixie 64-bit
