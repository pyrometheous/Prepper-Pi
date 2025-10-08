# Prepper-Pi Documentation

This directory contains the complete technical documentation for the Prepper-Pi project.

## 📚 Documentation Index

### 🔧 [Components List](components.md)
Complete bill of materials with specifications, part numbers, and development phase status. Organized by category with current vs. future hardware clearly marked.

### ⚡ [Wiring & Assembly Guide](wiring.md)
Detailed electrical specifications, system diagrams, safety guidelines, and assembly instructions. Includes power calculations, fuse tables, and component interconnections.

### 📡 [WiFi AP Testing Guide](wifi-testing.md)
Hardware validation protocol for WiFi access point functionality. Documents configuration issues and testing procedures for OpenWRT-in-Docker setup.

### 🔍 [AP Verification Script](../scripts/verify-ap.sh)
Automated validation script to check OpenWRT container configuration, WiFi device access, and future hardware readiness. Run with `./verify-ap.sh` after deployment.

---

## 🏗️ Project Structure

```
Prepper-Pi/
├── docs/
│   ├── README.md          # This file - documentation index
│   ├── components.md      # Complete components list and BOM
│   └── wiring.md         # Technical specifications and assembly guide
├── README.md             # Main project overview and setup instructions
├── docker-compose.yml    # Base service stack (override files in compose/)
├── compose/
│   ├── docker-compose.pi.yml           # Pi-specific overrides
│   └── override.example.yml            # Example override template
├── scripts/
│   ├── first-run-setup.sh              # Automated installation script
│   ├── startup.sh                      # Start services and health checks
│   ├── cleanup.sh                      # Uninstall and cleanup
│   └── verify-ap.sh                    # AP verification tests
└── ...                  # Additional project files
```

## 🚀 Quick Navigation

- **Getting Started:** See [../README.md](../README.md) for project overview and installation
- **Hardware Planning:** See [components.md](components.md) for complete parts list
- **Assembly Guide:** See [wiring.md](wiring.md) for technical specifications
- **Development Status:** See [../README.md#system-development](../README.md#-system-development) for current progress

---

*Documentation last updated: 2025-09-30*
