#!/usr/bin/env bash
# Test version of build-manifest.sh without sudo requirements
set -euo pipefail

OUT_DIR="${1:-./test-artifacts}"
mkdir -p "$OUT_DIR"

MANIFEST="$OUT_DIR/MANIFEST.txt"

GIT_COMMIT="$(git rev-parse --short=12 HEAD || echo unknown)"
DATE_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Discover active images from compose files (ignores commented lines)
readarray -t IMAGES < <(
  awk '
    /^[[:space:]]*#/ { next }                                           # ignore commented lines
    match($0, /^[[:space:]]*image:[[:space:]]*([^[:space:]]+)/, m) {    # image: repo[:tag|@sha]
      print m[1]
    }
  ' docker-compose*.yml 2>/dev/null | sort -u
)

if [[ ${#IMAGES[@]} -eq 0 ]]; then
  echo "ERROR: No active images discovered in docker-compose*.yml" >&2
  exit 1
fi

echo "Prepper-Pi $DATE_ISO"            | tee "$MANIFEST"
echo "git_commit=$GIT_COMMIT"         | tee -a "$MANIFEST"
echo ""                                | tee -a "$MANIFEST"
echo "[docker-images]"                 | tee -a "$MANIFEST"

# For demo purposes, show what images were discovered
echo "Discovered active images:" >&2
printf '  %s\n' "${IMAGES[@]}" >&2
echo "" >&2

# Simulate digest resolution (docker may not be available)
for img in "${IMAGES[@]}"; do
  echo "Would resolve digest for $img..." >&2
  # For demo: simulate successful digest resolution
  case "$img" in
    "openwrt/rootfs:23.05.2")
      echo "$img => openwrt/rootfs@sha256:1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef" | tee -a "$MANIFEST"
      ;;
    "portainer/portainer-ce:latest")
      echo "$img => portainer/portainer-ce@sha256:abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890" | tee -a "$MANIFEST"
      ;;
    "jellyfin/jellyfin:latest")
      echo "$img => jellyfin/jellyfin@sha256:fedcba0987654321fedcba0987654321fedcba0987654321fedcba0987654321" | tee -a "$MANIFEST"
      ;;
    "ghcr.io/gethomepage/homepage:latest")
      echo "$img => ghcr.io/gethomepage/homepage@sha256:567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234" | tee -a "$MANIFEST"
      ;;
    "dperson/samba:latest")
      echo "$img => dperson/samba@sha256:890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678" | tee -a "$MANIFEST"
      ;;
    *)
      echo "$img => example/repo@sha256:1111111111111111111111111111111111111111111111111111111111111111" | tee -a "$MANIFEST"
      ;;
  esac
done

# Hash key configs for traceability
echo ""                                         | tee -a "$MANIFEST"
echo "[checksums]"                              | tee -a "$MANIFEST"
for f in docker-compose*.yml *.env; do
  [[ -f "$f" ]] && sha256sum "$f" | tee -a "$MANIFEST"
done

# Sanity: ensure all recorded images use immutable digests
if grep -Eq '=>[[:space:]]+[^[:space:]]+:(latest|[0-9]+\.[0-9]+(\.[0-9]+)?)$' "$MANIFEST"; then
  echo "ERROR: MANIFEST contains tag-only references; immutable digests are required." >&2
  exit 1
fi

echo "Generated sample $MANIFEST"
