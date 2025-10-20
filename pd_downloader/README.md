
# Public Domain Media Downloader Suite

> ⚠️ **WORK IN PROGRESS** - These tools are actively being developed. There is no guarantee that anything will work as expected. Use at your own risk.

---

## Quick Links

- 📽️ **[Movies README](movies/README.md)** - Public domain film downloader
- 📚 **[Gutenberg README](ebooks/GUTENBERG_README.md)** - Project Gutenberg ebook downloader (includes self-hosted Docker option)
- 📖 **[Standard Ebooks README](ebooks/STANDARD_EBOOKS_README.md)** - Standard Ebooks library downloader

---

## ⚠️ IMPORTANT LEGAL NOTICE

These tools are designed **EXCLUSIVELY** for downloading public domain content (films and ebooks) from verified sources. They must **ONLY** be used for legitimate purposes of obtaining media that is free from copyright restrictions.

### Acceptable Use
- ✅ Downloading films confirmed to be in the public domain
- ✅ Building personal or commercial collections of PD media
- ✅ Archival and preservation of public domain works
- ✅ Educational purposes using PD materials

### Prohibited Use
- ❌ Downloading copyrighted materials without permission
- ❌ Circumventing copyright protections
- ❌ Mass downloading without respecting source terms of service
- ❌ Any use that violates copyright law

**By using this tool, you agree to use it responsibly and in compliance with all applicable laws.**

---

## About This Project

This suite helps you curate a small media library for the M.2 SSD on your **Prepper Pi** device. The goal is to build a compact, offline-accessible collection of public domain films and ebooks that can be stored locally and accessed without an internet connection.

## Overview

This suite contains Python scripts for downloading public domain media with built-in copyright protection measures:

### 📽️ Public Domain Movies
Downloads verified public domain films from trusted sources like Internet Archive and Wikimedia Commons. See the **[Movies README](movies/README.md)** for complete details on usage, manifest format, and copyright safeguards.

### 📚 Project Gutenberg Ebooks
Multiple options available for downloading Project Gutenberg's 70,000+ book catalog, including a self-hosted Docker solution for unlimited access. See the **[Gutenberg README](ebooks/GUTENBERG_README.md)** for setup guides and usage instructions.

**Important:** Project Gutenberg requires removal of their branding/boilerplate from redistributed content per their [trademark policy](https://www.gutenberg.org/policy/trademark_policy.html). This script handles that automatically, however you should **always** check the books yourself to validate that you are in compliance with the Project Gutenberg trademark policy.

### 📖 Standard Ebooks Library
Download the complete Standard Ebooks library (requires Patrons Circle membership). All editions are CC0 (public domain). See the **[Standard Ebooks README](ebooks/STANDARD_EBOOKS_README.md)** for details.

---

## Installation

```powershell
# Python 3.6 or higher required
python --version

# Install dependencies (for ebook downloaders)
pip install -r requirements.txt
```

**Note:** Movie downloader uses only Python standard library and requires no external dependencies.

---

## Getting Started

Each downloader has its own detailed README with complete usage instructions, legal notices, and troubleshooting guides. Click the links above to get started with the specific tool you need.

---

## License & Disclaimer

These tools are provided as-is for legitimate use only. Users are solely responsible for ensuring compliance with all applicable laws and regulations.

**The presence of content in manifests or scripts does NOT constitute legal advice or guarantee of public domain status.** Always verify independently before use, especially for commercial purposes.
