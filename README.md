# Prepper-Pi

## Quick Start

SSH into the Pi and run the following:

```bash
sudo apt update && sudo apt install -y git && git clone https://github.com/pyrometheous/Prepper-Pi.git && cd Prepper-Pi && bash first-run-setup.sh
```

This will install Docker, deploy the stack, and (in future) configure NVMe storage.

Note: NVMe and Jellyfin setup is temporarily disabled in `first-run-setup.sh`.
