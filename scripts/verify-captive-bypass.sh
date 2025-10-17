#!/bin/bash
#
# Simple test to verify the captive portal bypass is working
# Run this on the Pi to see what's actually deployed
#

echo "=== Captive Portal Bypass Verification ==="
echo ""

echo "1. Checking if captive-portal.py exists:"
ls -lh /usr/local/bin/captive-portal.py
echo ""

echo "2. Checking bypass button URL (should contain 'bypassed=true'):"
grep -A 1 "Continue Without Signing In" /usr/local/bin/captive-portal.py
echo ""

echo "3. Checking if bypass logic exists (should find 'has_bypassed'):"
grep "has_bypassed" /usr/local/bin/captive-portal.py
echo ""

echo "4. Service status:"
sudo systemctl status captive-portal --no-pager | grep -E "(Active|Main PID)"
echo ""

echo "5. Testing the bypass URL manually:"
echo "   Testing: curl -v 'http://10.20.30.1/generate_204?bypassed=true'"
curl -v 'http://10.20.30.1/generate_204?bypassed=true' 2>&1 | grep -E "(HTTP|< )"
echo ""

echo "=== Verification Complete ==="
