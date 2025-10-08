#!/usr/bin/env bash
set -euo pipefail

GATEWAY="${1:-10.20.30.1}"

echo "[*] Checking wireless capabilities..."
iw list | grep -q "AP$" && echo "[OK] AP mode supported" || echo "[WARN] AP mode not listed"

echo "[*] Checking DHCP on $GATEWAY..."
ping -c1 -W1 "$GATEWAY" >/dev/null && echo "[OK] Gateway reachable" || echo "[FAIL] Gateway unreachable"

echo "[*] DNS sanity (via $GATEWAY)..."
nslookup example.com "$GATEWAY" >/dev/null 2>&1 && echo "[OK] DNS resolves" || echo "[FAIL] DNS failed"

echo "[*] Captive portal HTTP redirect..."
CODE="$(curl -s -o /dev/null -w '%{http_code}' http://neverssl.com/ --connect-timeout 3 || true)"
[[ "$CODE" =~ ^30[12378]$ ]] && echo "[OK] Redirect observed ($CODE)" || echo "[WARN] No redirect ($CODE)"

echo "[*] Service ports via $GATEWAY..."
for port in 3000 8096 9000; do
  nc -z -w 2 "$GATEWAY" "$port" && echo "[OK] Port $port open" || echo "[WARN] Port $port closed"
done
