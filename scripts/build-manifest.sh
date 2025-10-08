#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-./release-artifacts}"
mkdir -p "$OUT_DIR"

VERSION_FILE="/etc/prepper-pi/VERSION"
MANIFEST="$OUT_DIR/MANIFEST.txt"

GIT_COMMIT="$(git rev-parse --short=12 HEAD || echo unknown)"
DATE_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Docker image list (edit to match your compose)
IMAGES=(
  "lscr.io/linuxserver/jellyfin"
  "portainer/portainer-ce"
  "tvheadend/tvheadend"
  "ghcr.io/gethomepage/homepage"
  "openwrt/openwrt"
)

echo "Prepper-Pi $DATE_ISO"            | tee "$MANIFEST"
echo "git_commit=$GIT_COMMIT"         | tee -a "$MANIFEST"
echo ""                                | tee -a "$MANIFEST"
echo "[docker-images]"                 | tee -a "$MANIFEST"

for img in "${IMAGES[@]}"; do
  if docker image inspect "$img:latest" >/dev/null 2>&1; then
    DIGEST="$(docker image inspect --format='{{index .RepoDigests 0}}' "$img:latest" || true)"
    echo "$img => ${DIGEST:-unknown}" | tee -a "$MANIFEST"
  else
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
