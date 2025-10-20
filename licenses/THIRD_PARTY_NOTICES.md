<!--
SPDX-License-Identifier: CC-BY-NC-4.0
-->

# Third-Party Notices

This device/software distribution includes (or may fetch at install time) third-party components. Each component's license governs its use. Where applicable, corresponding source is available as described in `SOURCE-OFFER.md`.

| Project / Component | License | Home / Source |
|---|---|---|
| OpenWrt (incl. dnsmasq, firewall4/nftables, uhttpd, LuCI) | GPL-2.0 and others | https://openwrt.org / https://github.com/openwrt/openwrt |
| **BusyBox** (via OpenWrt base) | GPL-2.0 | https://busybox.net / https://git.busybox.net/busybox/ |
| nftables / libnftnl (OpenWrt firewall stack) | GPL-2.0+ / LGPL | https://netfilter.org/projects/nftables/ |
| iproute2 | GPL-2.0 | https://wiki.linuxfoundation.org/networking/iproute2 |
| openNDS (captive portal) | GPL-2.0 | https://github.com/openNDS/openNDS |
| Homepage (dashboard) | GPL-3.0 | https://gethomepage.dev / https://github.com/gethomepage/homepage |
| Portainer **Community Edition** | zlib | https://www.portainer.io / https://github.com/portainer/portainer |
| Jellyfin | GPL-2.0 | https://jellyfin.org / https://github.com/jellyfin/jellyfin |
| **FFmpeg** (used by Jellyfin) | LGPL-2.1+ and GPL (configuration-dependent) | https://ffmpeg.org / https://github.com/FFmpeg/FFmpeg |
| Samba (dperson) | AGPL-3.0 (wrapper); Samba inside: GPL-3.0 | https://hub.docker.com/r/dperson/samba / https://github.com/dperson/samba |
| Icecast (moul/icecast)\* | GPL-2.0 | https://icecast.org / https://hub.docker.com/r/moul/icecast |
| SoX\* | GPL-2.0+ | https://sourceforge.net/projects/sox/ |
| rtl-sdr (librtlsdr, rtl_fm)\* | GPL-2.0 | https://osmocom.org/projects/sdr/wiki/rtl-sdr |
| libmp3lame (if present)\* | LGPL-2.1+ (confirm per build) | https://lame.sourceforge.io/ |
| Tvheadend (linuxserver image)\* | GPL-3.0 | https://github.com/tvheadend/tvheadend / https://lscr.io/linuxserver/tvheadend |
| Kavita\* | GPL-3.0 | https://www.kavitareader.com / https://github.com/Kareadita/Kavita |
| Meshtasticd\* | GPL-3.0 (trademark policy applies) | https://github.com/meshtastic/meshtasticd |
| MeshCore\* | MIT | https://meshcore.co.uk / https://github.com/meshcore |
| Kiwix\* | GPL-3.0 | https://www.kiwix.org / https://github.com/kiwix/ |
| LinuxServer.io images (where used) | Varies by upstream | https://www.linuxserver.io |
| Docker Engine / CLI | Apache-2.0 | https://www.docker.com / https://github.com/moby/moby |
| Raspberry Pi OS / Debian packages | Various | https://www.raspberrypi.com/software / https://www.debian.org |

\* *Currently "planned" per the README. If/when these components are included in shipped images, their licenses and any trademark policies will apply to those builds and will be reflected in the MANIFEST and source bundle for that release.*

Image metadata may also include license files (e.g., in LinuxServer.io images), but this document is the canonical third-party notice list for releases.

Licensing for Jellyfin/Tvheadend/FFmpeg components depends on the build configuration and distribution packages used in a given release; see the release MANIFEST and source bundle for the exact versions and flags.

For AGPL-licensed containers (e.g., dperson/samba), if modified and network-accessible, the AGPL's network clause may require offering the corresponding source of the modified work to users interacting with the service.

**Data Licenses**
- OpenStreetMap data: **ODbL 1.0** — https://www.openstreetmap.org/copyright

**Trademarks**
- All third-party names/logos are trademarks of their respective owners. No affiliation or endorsement implied.
