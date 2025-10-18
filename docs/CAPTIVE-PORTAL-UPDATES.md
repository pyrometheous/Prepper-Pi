# Captive Portal and Homepage Updates - October 16, 2025

## Changes Made

### Captive Portal Improvements

**Problem**: Captive portal popup not appearing on devices when connecting to "Prepper Pi" WiFi.

**Solution**: Enhanced the captive portal detection to support more platforms:

1. **Added More Detection URLs**:
   - iOS: `/hotspot-detect.html`, `/library/test/success.html`
   - Android: `/generate_204`, `/gen_204`
   - Windows: `/connecttest.txt`, `/redirect`
   - Firefox: `/success.txt`
   - Ubuntu/Linux: `/canonical.html`, `/connectivity-check.html`

2. **Improved HTTP Responses**:
   - Changed from HTTP 204 (No Content) to HTTP 200 with HTML content
   - Added cache control headers (`no-cache`, `no-store`, `must-revalidate`)
   - Better HEAD request handling

3. **How It Works**:
   - When a device connects to WiFi, it sends requests to detection URLs
   - Our captive portal returns HTML with auto-redirect to homepage
   - Device detects this and shows "Sign in to WiFi network" popup
   - Clicking popup opens homepage at `http://10.20.30.1:3000`

**Files Modified**: `scripts/captive-portal-setup.sh`

---

### Homepage Improvements

**Changes**:

1. **WiFi Network Information Banner** (New)
   - Prominent banner at top of homepage
   - Shows current WiFi SSID: "Prepper Pi"
   - Shows WiFi password: "ChangeMeNow!"
   - Purple gradient design with lock icon
   - Auto-refreshes every 5 minutes

2. **Reorganized Service Sections**:
   - **Network Info**: WiFi credentials display
   - **Administration**: RaspAP (WiFi management) and Portainer (containers)
   - **System**: System monitor
   - **Media**: Jellyfin, file shares
   - **Network**: WiFi config, DHCP, connected devices, firewall
   - **Tools**: Future features (SDR, offline content, etc.)

3. **Custom Styling** (`homepage/custom.css`):
   - WiFi info banner with gradient background
   - Animated WiFi pulse icon
   - Service section headers
   - Responsive design

4. **Custom JavaScript** (`homepage/custom.js`):
   - Dynamically adds WiFi banner to page
   - Attempts to fetch real WiFi credentials from RaspAP API
   - Falls back to default values if API unavailable
   - Auto-refresh functionality

**Files Modified**:
- `homepage/services.yaml`
- `homepage/custom.css` (NEW)
- `homepage/custom.js` (NEW)

---

## How to Apply Updates

### On Fresh Installation
Updates are automatically included when running `scripts/first-run-setup.sh`

### On Existing Installation

**Option 1**: Use update script (recommended)
```bash
ssh admin@prepper-pi.local
cd Prepper-Pi
sudo bash scripts/update-prepper-pi.sh
```

**Option 2**: Manual update
```bash
ssh admin@prepper-pi.local
cd Prepper-Pi

# Fix permissions
sudo chown -R admin:admin .

# Pull latest changes
git fetch origin
git reset --hard origin/feature/native-hostapd

# Update captive portal
sudo bash scripts/captive-portal-setup.sh

# Restart services
docker compose restart
```

---

## Testing Captive Portal

### What to Test:

1. **iOS Device** (iPhone/iPad):
   - Connect to "Prepper Pi" WiFi
   - Should see "Sign in to Wi-Fi network" notification
   - Tap notification → opens homepage

2. **Android Device**:
   - Connect to "Prepper Pi" WiFi
   - Should see "Wi-Fi has no internet access" with "Sign in" button
   - Tap "Sign in" → opens homepage

3. **Windows PC**:
   - Connect to "Prepper Pi" WiFi
   - Should see "Action needed" notification in system tray
   - Click notification → opens browser to homepage

4. **Linux (Ubuntu/Fedora)**:
   - Connect to "Prepper Pi" WiFi
   - May see browser popup automatically
   - Or manually browse to any HTTP site → redirects to homepage

### Expected Behavior:
- ✅ Devices show captive portal notification
- ✅ Clicking notification opens `http://10.20.30.1:3000`
- ✅ Homepage shows WiFi banner with network name and password
- ✅ Internet access works normally after accepting portal

### Devices That Won't Show Portal:
- ❌ Nintendo Switch (no captive portal support)
- ❌ Some smart TVs (limited browser support)
- ❌ IoT devices without displays

These devices can still connect and use internet, they just won't see the popup.

---

## Troubleshooting

### Captive Portal Not Appearing

**Check service is running**:
```bash
sudo systemctl status captive-portal
```

**Restart captive portal**:
```bash
sudo systemctl restart captive-portal
sudo systemctl restart dnsmasq
```

**Test detection URLs manually** (from Pi):
```bash
curl -I http://captive.apple.com
curl -I http://connectivitycheck.gstatic.com
```

Should return HTTP 200 with redirect to homepage.

### Homepage Not Showing WiFi Info

**Check custom files exist**:
```bash
ls -l /home/admin/Prepper-Pi/homepage/custom.*
```

Should show:
- `custom.css`
- `custom.js`

**Restart Homepage container**:
```bash
docker restart homepage
```

**Check Homepage logs**:
```bash
docker logs homepage
```

### WiFi Credentials Not Updating

The banner currently shows default values ("Prepper Pi" / "ChangeMeNow!"). 

To update after changing in RaspAP:
1. Change SSID/password in RaspAP web UI (`http://10.20.30.1:8080`)
2. Edit `homepage/custom.js` and update default values
3. Restart homepage: `docker restart homepage`

**Future Enhancement**: Create RaspAP API endpoint to fetch real-time credentials.

---

## Security Notes

1. **Change Default Passwords**:
   - WiFi password: Change "ChangeMeNow!" via RaspAP
   - RaspAP admin: Change admin/secret
   - Update Homepage banner after changing

2. **Captive Portal Security**:
   - Runs on port 80 (HTTP only)
   - Only redirects to internal homepage
   - No user authentication required (open network portal)
   - Internet access works after acknowledgment

3. **Homepage Access**:
   - Accessible only from WiFi clients (10.20.30.x)
   - Not exposed to upstream network
   - Shows network credentials to all connected users

---

## Future Improvements

1. **Dynamic WiFi Credentials**:
   - Create RaspAP API endpoint to serve current SSID/password
   - Update Homepage JavaScript to fetch from API
   - Auto-update banner when credentials change

2. **Terms of Service Page**:
   - Add TOS acceptance before internet access
   - Log acceptance for compliance
   - Configurable terms via RaspAP

3. **Captive Portal Customization**:
   - Configurable redirect URL
   - Custom welcome message
   - Branding/logo support

4. **Device-Specific Detection**:
   - Detect device type (phone/tablet/laptop)
   - Show different content based on device
   - Skip portal for known IoT devices

---

## Related Documentation

- `docs/DEPLOYMENT-NOTES.md` - Fresh deployment process
- `docs/QUICK-DEPLOY-CHECKLIST.md` - Quick setup guide
- `scripts/captive-portal-setup.sh` - Captive portal configuration
- `scripts/update-prepper-pi.sh` - Update script for existing installations
