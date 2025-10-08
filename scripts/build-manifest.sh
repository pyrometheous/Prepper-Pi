#!/bin/bash
# Build manifest for GPL compliance tracking
# This script generates version tracking files for source code offer compliance

set -e

MANIFEST_FILE="MANIFEST.txt"
VERSION_FILE="/etc/prepper-pi/VERSION"
GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Building compliance manifest..."

# Create version file content
mkdir -p "$(dirname "$VERSION_FILE")" 2>/dev/null || true
cat > "$VERSION_FILE" << EOF
# Prepper Pi Version Information
# Generated: $BUILD_DATE

GIT_COMMIT=$GIT_COMMIT
GIT_BRANCH=$GIT_BRANCH
BUILD_DATE=$BUILD_DATE
SOURCE_OFFER_URL=https://github.com/pyrometheous/Prepper-Pi/releases
THIRD_PARTY_NOTICES=licenses/THIRD_PARTY_NOTICES.md
EOF

# Create manifest for source distribution
cat > "$MANIFEST_FILE" << EOF
# Prepper Pi Source Manifest
# Generated: $BUILD_DATE
# Git Commit: $GIT_COMMIT

# Core Components
Repository: https://github.com/pyrometheous/Prepper-Pi.git
Commit: $GIT_COMMIT
Branch: $GIT_BRANCH

# Container Images (update with actual versions used)
OpenWrt: openwrt/openwrt:latest
Homepage: ghcr.io/gethomepage/homepage:latest
Portainer: portainer/portainer-ce:latest
Jellyfin: lscr.io/linuxserver/jellyfin:latest
Kavita: lscr.io/linuxserver/kavita:latest

# Build Dependencies
Docker Compose Version: $(docker compose version --short 2>/dev/null || echo "unknown")
System: $(uname -a)

# License Information
Project License: Prepper Pi Noncommercial License (PP-NC-1.0)
Documentation License: CC BY-NC 4.0
Third-Party Notices: licenses/THIRD_PARTY_NOTICES.md
Source Offer: licenses/SOURCE-OFFER.md
EOF

echo "Manifest files generated:"
echo "  - $MANIFEST_FILE"
echo "  - $VERSION_FILE"

# If running in container, also copy to a standard location
if [ -f /.dockerenv ] || [ -n "$CONTAINER" ]; then
    cp "$VERSION_FILE" /tmp/prepper-pi-version 2>/dev/null || true
    echo "  - /tmp/prepper-pi-version (container copy)"
fi

echo "Done!"
