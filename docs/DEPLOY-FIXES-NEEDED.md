<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Fresh Deploy Issues to Fix

## Problem
The `scripts/first-run-setup.sh` currently has the OLD DNS configuration that breaks internet passthrough. It adds the wildcard DNS hijacking (`address=/#/10.20.30.1`) which redirects ALL domains to the Pi, blocking internet access.

## Required Changes

### 1. Update `scripts/first-run-setup.sh`

**Current problematic code (lines 172-179 and 191-194):**
```bash
if [ -f /etc/dnsmasq.d/090_raspap.conf ]; then
    cat > /etc/dnsmasq.d/090_raspap.conf << 'EOF'
interface=wlan0
domain-needed
bogus-priv
dhcp-range=10.20.30.100,10.20.30.199,255.255.255.0,24h
address=/#/10.20.30.1  # <-- REMOVES ALL INTERNET ACCESS!
EOF
fi

# Later in the script:
if [ -f /etc/dnsmasq.d/090_raspap.conf ]; then
    # Add captive portal DNS hijacking
    echo "address=/#/10.20.30.1" >> /etc/dnsmasq.d/090_raspap.conf  # <-- DUPLICATE!
fi
```

**Should be:**
- Remove the wildcard DNS hijacking
- Let RaspAP installer create the initial config
- Let `captive-portal-setup.sh` handle the proper DNS configuration

**Solution:**
1. Remove the section that overwrites `090_raspap.conf` (lines 171-179)
2. Remove the section that appends wildcard DNS (lines 191-194)
3. Let RaspAP installer handle initial dnsmasq setup
4. User will run `captive-portal-setup.sh` afterward to configure proper DNS + firewall

### 2. Workflow After Fix

The correct deployment flow should be:

```bash
# Step 1: First-run setup (installs RaspAP, Docker, basic config)
sudo bash scripts/first-run-setup.sh

# Step 2: Start Docker services
cp compose/docker-compose.pi.yml docker-compose.override.yml
docker compose up -d

# Step 3: Configure captive portal + internet passthrough
sudo bash scripts/captive-portal-setup.sh
```

This way:
- ✅ `first-run-setup.sh` installs dependencies and RaspAP
- ✅ `captive-portal-setup.sh` configures DNS, firewall, and portal properly
- ✅ No DNS wildcard hijacking that breaks internet
- ✅ Clear separation of concerns

### 3. Alternative: Integrate captive-portal-setup.sh

Instead of running two scripts, we could integrate the captive portal setup into first-run-setup.sh:

```bash
# At end of first-run-setup.sh, after RaspAP installation:
if [ -f "$(dirname "$0")/captive-portal-setup.sh" ]; then
    print_status "Configuring captive portal and internet passthrough..."
    bash "$(dirname "$0")/captive-portal-setup.sh"
else
    print_warning "Run scripts/captive-portal-setup.sh after Docker services are started"
fi
```

## Recommendation

**Option 1 (Simpler):** Keep scripts separate
- Fix `first-run-setup.sh` to NOT touch dnsmasq config
- Document that users must run `captive-portal-setup.sh` afterward
- Clear separation makes troubleshooting easier

**Option 2 (More automated):** Integrate scripts
- Have `first-run-setup.sh` call `captive-portal-setup.sh` at the end
- One command does everything
- More complex, harder to debug if something fails

**I recommend Option 1** - it's clearer and allows testing each component separately.

## Testing After Fix

After updating first-run-setup.sh:

1. Fresh image Raspberry Pi OS
2. Run `sudo bash scripts/first-run-setup.sh`
3. Verify RaspAP installed but NO DNS wildcard
4. Start Docker services
5. Run `sudo bash scripts/captive-portal-setup.sh`
6. Test internet passthrough
7. Test all services

This matches how we manually fixed the working Pi.
