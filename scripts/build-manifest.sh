#!/usr/bin/env bash
# SPDX-License-Identifier: LicenseRef-PP-NC-1.0
set -euo pipefail

OUT_DIR="${1:-./release-artifacts}"
mkdir -p "$OUT_DIR"

VERSION_FILE="/etc/prepper-pi/VERSION"
MANIFEST="$OUT_DIR/MANIFEST.txt"

GIT_COMMIT="$(git rev-parse --short=12 HEAD || echo unknown)"
DATE_ISO="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

#
# Discover active images from compose files (ignores commented lines).
# Works without yq: we skip lines that start with '#' and capture the value after 'image:'.
#
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

for img in "${IMAGES[@]}"; do
  echo "Resolving digest for $img..." >&2
  # Always ensure local metadata is fresh
  docker pull "$img" >/dev/null 2>&1 || true
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

# Sanity: ensure all recorded images use immutable digests
if grep -Eq '=>[[:space:]]+[^[:space:]]+:(latest|[0-9]+\.[0-9]+(\.[0-9]+)?)$' "$MANIFEST"; then
  echo "ERROR: MANIFEST contains tag-only references; immutable digests are required." >&2
  exit 1
fi

echo "Wrote $MANIFEST and $VERSION_FILE"
