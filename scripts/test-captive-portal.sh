#!/bin/bash
#
# Test captive portal detection from a connected device
# Run this from a device connected to the Prepper Pi WiFi
#

echo "=== Testing Captive Portal Detection ==="
echo ""

# Test iOS detection URLs
echo "1. Testing iOS detection (captive.apple.com)..."
curl -v http://captive.apple.com/hotspot-detect.html 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

echo "2. Testing iOS alternate (apple.com/library)..."
curl -v http://apple.com/library/test/success.html 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

# Test Android detection URLs
echo "3. Testing Android detection (connectivitycheck.gstatic.com)..."
curl -v http://connectivitycheck.gstatic.com/generate_204 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

echo "4. Testing Android alternate (google.com/gen_204)..."
curl -v http://google.com/gen_204 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

# Test Windows detection
echo "5. Testing Windows detection (msftconnecttest.com)..."
curl -v http://www.msftconnecttest.com/connecttest.txt 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

# Test Firefox detection
echo "6. Testing Firefox detection (detectportal.firefox.com)..."
curl -v http://detectportal.firefox.com/success.txt 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

# Test direct connection to captive portal
echo "7. Testing direct connection to 10.20.30.1..."
curl -v http://10.20.30.1/ 2>&1 | grep -E "(HTTP|Location|<)"
echo ""

echo "=== DNS Resolution Tests ==="
echo ""

# Test DNS resolution
echo "8. Testing DNS resolution for captive domains..."
nslookup captive.apple.com 10.20.30.1
echo ""
nslookup connectivitycheck.gstatic.com 10.20.30.1
echo ""
nslookup www.msftconnecttest.com 10.20.30.1
echo ""

echo "=== Test Complete ==="
echo ""
echo "Expected results:"
echo "  - All captive detection URLs should return HTTP 200"
echo "  - Response should contain HTML with redirect to http://10.20.30.1:3000"
echo "  - DNS queries should resolve to 10.20.30.1"
echo ""
echo "If you see HTTP 204 or different IP addresses, the captive portal is misconfigured."
