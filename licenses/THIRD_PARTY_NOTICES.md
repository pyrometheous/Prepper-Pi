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
| Homepage (dashboard) | MIT | https://gethomepage.dev / https://github.com/gethomepage/homepage |
| Portainer **Community Edition** | zlib | https://www.portainer.io / https://github.com/portainer/portainer |
| Jellyfin | GPL-2.0 | https://jellyfin.org / https://github.com/jellyfin/jellyfin |
| **FFmpeg** (used by Jellyfin) | LGPL-2.1+ and GPL (configuration-dependent) | https://ffmpeg.org / https://github.com/FFmpeg/FFmpeg |
| Samba (dperson/samba image) | GPL-3.0+ | https://www.samba.org / https://github.com/dperson/samba |
| Icecast\* | GPL-2.0 | https://icecast.org / https://gitlab.xiph.org/xiph/icecast-server |
| SoX\* | GPL-2.0+ | https://sourceforge.net/projects/sox/ |
| Tvheadend\* | GPL-3.0 | https://tvheadend.org / https://github.com/tvheadend/tvheadend |
| Kavita\* | GPL-3.0 | https://www.kavitareader.com / https://github.com/Kareadita/Kavita |
| Meshtastic (protocol/firmware/tools)\* | GPL-3.0 (trademark policy applies) | https://meshtastic.org / https://github.com/meshtastic/ |
| MeshCore\* | MIT | https://meshcore.co.uk / https://github.com/meshcore |
| Kiwix\* | GPL-3.0 | https://www.kiwix.org / https://github.com/kiwix/ |
| LinuxServer.io images (where used) | Varies by upstream | https://www.linuxserver.io |
| Docker Engine / CLI | Apache-2.0 | https://www.docker.com / https://github.com/moby/moby |
| Raspberry Pi OS / Debian packages | Various | https://www.raspberrypi.com/software / https://www.debian.org |

\* *Currently "planned" per the README. If/when these components are included in shipped images, their licenses and any trademark policies will apply to those builds and will be reflected in the MANIFEST and source bundle for that release.*

Image metadata may also include license files (e.g., in LinuxServer.io images), but this document is the canonical third-party notice list for releases.

Licensing for Jellyfin/Tvheadend/FFmpeg components depends on the build configuration and distribution packages used in a given release; see the release MANIFEST and source bundle for the exact versions and flags.

**Data Licenses**
- OpenStreetMap data: **ODbL 1.0** — https://www.openstreetmap.org/copyright

**Trademarks**
- All third-party names/logos are trademarks of their respective owners. No affiliation or endorsement implied.
