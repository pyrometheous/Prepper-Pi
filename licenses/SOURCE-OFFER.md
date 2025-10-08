# Corresponding Source Offer (GPL/LGPL Components)

We distribute devices and/or images that include GPL/LGPL-licensed software (e.g., Jellyfin, Tvheadend, OpenWrt packages). In accordance with those licenses, we provide the **Corresponding Source** as follows:

1. **Public Download (Preferred)**
   - Source bundles and build scripts corresponding to each release will be hosted for **at least 3 years** from the last device shipment date at:
   - **URL:** https://github.com/pyrometheous/Prepper-Pi/releases
   - Each release folder contains:
     - Exact upstream source (or upstream commit references),
     - Our patch sets (if any),
     - Build/config scripts (e.g., Dockerfiles, compose files),
     - A `MANIFEST.txt` enumerating versions/commits.

2. **Written Offer (Mail)**
   - You may request physical media containing the Corresponding Source for a nominal charge to cover distribution costs. Send your device serial number and firmware/image version to:
   - **Email:** pyrometheous@github.com
   - **Mailing Address:** Available upon written request to above email

3. **How We Track Versions**
   - The running image contains a `/etc/prepper-pi/VERSION` file with:
     - Git commit of this repo,
     - Tagged versions of each included container image,
     - A link back to the matching source bundle.

4. **Installation Information (if applicable)**
   - If any component falls under **GPLv3** and the device becomes locked-down, we will additionally provide any required **Installation Information** so recipients can install modified software on the same device.

> This offer is valid for **no less than 3 years** from the later of the last device distribution or the last public posting of the relevant image.
