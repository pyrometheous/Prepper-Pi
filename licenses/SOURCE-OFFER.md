# Corresponding Source Availability (GPL/LGPL Components)

We may publish device images, container images, or other binaries that include GPL/LGPL-licensed software (e.g., OpenWrt packages, Jellyfin, Tvheadend). To comply with those licenses, we follow the **concurrent source distribution** model:

## How to get the Corresponding Source
- For **every image/binary release**, we publish a matching **GitHub Release** that includes a `source/` archive with:
  - Exact upstream source (or upstream commit references),
  - Any local patches and build/config scripts (Dockerfiles, compose files),
  - A `MANIFEST.txt` enumerating components and versions/commits, plus SHA-256 checksums of binaries and sources.

➡️ **Releases:** https://github.com/pyrometheous/Prepper-Pi/releases

### Version mapping on the device/image
Each image includes `/etc/prepper-pi/VERSION` with:
- Git commit of this repo,
- Tags/digests for included container images,
- The URL of the matching GitHub Release.

## Retention period
We will keep the corresponding source available **for at least 3 years** after the relevant image/binary release date by retaining the tagged GitHub Release and its `source/` archive.

## Notes on alternative compliance
We are intentionally **not** using the "written offer" method at this time because concurrent source distribution (GPLv2 §3(a); GPLv3 §6) avoids the need for separate postal/email contact details. If at some future point we cannot host the source concurrently, we will update this document to include a written offer valid for 3 years.

---

*This document describes how recipients obtain Corresponding Source; it does not alter any third-party licenses.*
