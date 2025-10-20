#!/bin/bash
#
# Fix Homepage YAML parsing errors
#

echo "=== Fixing Homepage Configuration ==="

cd /home/admin/Prepper-Pi

# Fix widgets.yaml - comment out invalid provider keys
echo "Fixing widgets.yaml..."
cat > homepage/widgets.yaml << 'EOF'
---
# Remove provider placeholders that cause errors
# providers:
#   openweathermap: openweathermapapikey
#   weatherapi: weatherapiapikey

resources:
  backend: resources/widgets.py
  cpu: true
  memory: true
  disk: /
  cputemp: true
  uptime: true
  units: metric
  refresh: 3000
  diskUnits: bytes
EOF

echo "Restarting Homepage container..."
docker restart homepage

echo "Waiting for Homepage to start..."
sleep 5

echo "Checking Homepage logs..."
docker logs homepage 2>&1 | tail -10

echo ""
echo "=== Fix Complete ==="
echo "Homepage should now load without errors."
echo "Check http://10.20.30.1:3000 - Administration section should now be visible."
