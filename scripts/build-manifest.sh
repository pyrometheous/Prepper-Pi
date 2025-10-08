#!/usr/bin/env bash
# SPDX-License-Identifier: LicenseRef-PP-NC-1.0
set -euo pipefail

OUT_DIR="${1:-./release-artifacts}"
mkdir -p "$OUT_DIR"

VERSION_FILE="/etc/prepper-pi/VERSION"
MANIFEST="$OUT_DIR/MANIFEST.txt"

GIT_COMMIT="$(git rev-parse --short=12 HEAD || echo unknown)"
DATE_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Docker image list (edit to match your compose)
IMAGES=(
  "openwrt/rootfs:23.05.2"
  "portainer/portainer-ce:latest"
  "jellyfin/jellyfin:latest"
  "ghcr.io/gethomepage/homepage:latest"
  "dperson/samba:latest"
  "lscr.io/linuxserver/tvheadend:latest"
  "moul/icecast:latest"
)

echo "Prepper-Pi $DATE_ISO"            | tee "$MANIFEST"
echo "git_commit=$GIT_COMMIT"         | tee -a "$MANIFEST"
echo ""                                | tee -a "$MANIFEST"
echo "[docker-images]"                 | tee -a "$MANIFEST"

for img in "${IMAGES[@]}"; do
  echo "Resolving digest for $img..." >&2
  if docker image inspect "$img" >/dev/null 2>&1; then
    DIGEST="$(docker image inspect --format='{{index .RepoDigests 0}}' "$img" 2>/dev/null || echo '')"
    if [[ -n "$DIGEST" && "$DIGEST" != "<no value>" ]]; then
      echo "$img => $DIGEST" | tee -a "$MANIFEST"
    else
      echo "ERROR: Could not resolve digest for $img (may need docker pull)" >&2
      echo "$img => digest_resolution_failed" | tee -a "$MANIFEST"
      exit 1
    fi
  else
    echo "WARNING: Image $img not present locally" >&2
    echo "$img => not_present" | tee -a "$MANIFEST"
  fi
done

# Hash key configs for traceability
echo ""                                         | tee -a "$MANIFEST"
echo "[checksums]"                              | tee -a "$MANIFEST"
for f in docker-compose*.yml *.env; do
  [[ -f "$f" ]] && sha256sum "$f" | tee -a "$MANIFEST"
done

# Ensure VERSION file exists on system images; for dev, write locally too
mkdir -p "$(dirname "$VERSION_FILE")" || true
{
  echo "date=$DATE_ISO"
  echo "git_commit=$GIT_COMMIT"
  echo "manifest_sha256=$(sha256sum "$MANIFEST" | awk '{print $1}')"
} | sudo tee "$VERSION_FILE" >/dev/null

echo "Wrote $MANIFEST and $VERSION_FILE"
