#!/bin/bash
# Update Prepper Pi with latest changes from repository
# Usage: sudo bash scripts/update-prepper-pi.sh

set -e

echo "=== Updating Prepper Pi ==="

# Fix permissions if needed
echo "Fixing file permissions..."
chown -R admin:admin /home/admin/Prepper-Pi

# Update from git
echo "Pulling latest changes..."
cd /home/admin/Prepper-Pi
sudo -u admin git fetch origin
sudo -u admin git reset --hard origin/feature/native-hostapd

# Update captive portal
echo "Updating captive portal..."
bash scripts/captive-portal-setup.sh

# Restart services
echo "Restarting Docker services..."
docker compose restart

echo ""
echo "=== Update Complete ==="
echo ""
echo "Services restarted:"
echo "  - Captive Portal"
echo "  - Homepage"
echo "  - All Docker containers"
echo ""
echo "Changes applied:"
echo "  - Latest captive portal detection"
echo "  - Updated Homepage configuration"
echo "  - WiFi info display"
