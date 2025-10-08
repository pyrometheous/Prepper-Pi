#!/bin/bash

# Prepper Pi - First Run Setup Script
# This script sets up the complete Prepper Pi environment

# Set up bridge interface for host connectivity
# Create startup script for network setup (only if macvlan enabled)
echo
#!/usr/bin/env bash
# Moved to scripts/first-run-setup.sh
exec "$(dirname "$0")/scripts/first-run-setup.sh" "$@"
