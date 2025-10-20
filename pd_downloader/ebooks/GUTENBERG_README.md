# Project Gutenberg Ebook Downloader

> ⚠️ **WORK IN PROGRESS** - These tools are actively being developed. There is no guarantee that anything will work as expected. Use at your own risk.

---

## Table of Contents

- [Legal Notice](#️-important-legal-notice)
- [Overview & Options](#overview)
- [Self-Hosted Setup (Recommended)](#option-1-self-hosted-gutendex--recommended)
- [Quick Start](#quick-start-fully-automated)
- [Usage Examples](#usage-examples)
- [Kavita Integration](#kavita-media-server-integration)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## Navigation

- 🏠 **[Main README](../README.md)** - Overview of all downloaders
- 🎵 **[Music README](../music/README.md)** - Public domain music
- 📽️ **[Movies README](../movies/README.md)** - Public domain films
- 📖 **[Standard Ebooks README](STANDARD_EBOOKS_README.md)** - Standard Ebooks library

---

## ⚠️ IMPORTANT LEGAL NOTICE

### Acceptable Use
- ✅ Downloading public domain ebooks from Project Gutenberg
- ✅ Building personal or commercial collections
- ✅ Educational and archival purposes

### Prohibited Use
- ❌ Downloading copyrighted materials without permission
- ❌ Redistributing Project Gutenberg ebooks WITH their branding/boilerplate (violates their trademark policy)
- ❌ Mass downloading without respecting rate limits

### Project Gutenberg Redistribution Requirements

**Important:** Project Gutenberg requires removal of their branding, headers, and boilerplate text from ebooks before redistribution. Per their [trademark policy](https://www.gutenberg.org/policy/trademark_policy.html):

> If you remove the Project Gutenberg header and footer, you may distribute the ebook without using the Project Gutenberg trademark.

**This script automatically handles the cleanup** by removing all Project Gutenberg branding/boilerplate from downloaded EPUBs, making them compliant for redistribution. You should always validate the results yourself before asuming the EPUB downloads are cleaned up.

---

## Overview

Download public domain ebooks from Project Gutenberg with clean, Kavita-ready formatting. This suite provides **three different options** for accessing Project Gutenberg's 70,000+ book catalog:

### Quick Comparison

| Method | Reliability | Setup | API Limits | Cost | Best For |
|--------|------------|-------|-----------|------|----------|
| **Self-Hosted (Recommended)** ⭐ | ✅✅ Excellent | Docker required | ✅ None | Free | Full library access |
| Public Gutendex API | ⚠️ Unreliable (500 errors) | Easy | Free tier limits | Free | Quick testing only |
| Commercial GutenbergAPI | ✅ Good | API key needed | 500 req/month free | Paid tiers | Metadata search |

---

## Option 1: Self-Hosted Gutendex (⭐ RECOMMENDED)

Run your own Gutendex API instance locally using Docker for **unlimited, reliable access** to the entire Project Gutenberg catalog.

### Why Self-Host?

- ✅✅ **Unlimited API requests** - No rate limits!
- ✅✅ **Always available** - You control uptime
- ✅ **Full catalog** - All 76,000+ books
- ✅ **Fastest queries** - Local database
- ✅ **Free forever** - Just server costs
- ✅ **Can download ENTIRE library**

### Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
   - Windows 10/11 Pro/Enterprise with WSL 2, or Windows 10/11 Home with WSL 2
   - Minimum 8GB RAM, 5GB free disk space
   - Internet connection for initial setup

2. **Python 3.8+** with pip
   ```powershell
   python --version  # Should show 3.8 or higher
   ```

3. **Python Dependencies**
   ```powershell
   cd c:\Users\Delgado\VSCode\Prepper-Pi\pd_downloader\ebooks
   pip install -r requirements.txt
   ```
   This installs:
   - `requests>=2.31.0` - HTTP operations
   - `lxml>=4.9.0` - EPUB/XML processing

### Quick Start (Fully Automated)

**Easiest method** - One command does everything:

```powershell
# Downloads 100 most popular books and manages Docker automatically
python automated_gutendex_download.py --mode popular --count 100
```

This script:
1. ✅ Checks Docker is installed and running
2. ✅ Starts Gutendex containers if needed
3. ✅ Waits for API to be ready (auto-detects catalog download)
4. ✅ Downloads your specified books
5. ✅ Stops containers when done (or keeps running with `--keep-running`)

### Usage Examples

```powershell
# Download top 100 popular books
python automated_gutendex_download.py --mode popular --count 100

# Auto-discover top 20 genres, 50 books each, keep containers running
python automated_gutendex_download.py --mode discover --genres-top 20 --count 50 --keep-running

# Download specific genres
python automated_gutendex_download.py --genres "Science Fiction,Fantasy,Mystery" --count 30

# Just start the containers (no download)
python automated_gutendex_download.py --start-only

# Just stop the containers
python automated_gutendex_download.py --stop-only

# Debug mode - see book data structure
python automated_gutendex_download.py --mode popular --count 5 --debug
```

### Command-Line Arguments

**Download Options:**
- `--mode` - Download mode: `popular`, `genres`, or `discover` (default: `popular`)
- `--genres` - Comma-separated genre list (e.g., `"Science Fiction,Fantasy"`)
- `--count` - Books per genre (default: 20)
- `--genres-top` - Number of top genres for auto-discover (default: 10)

**Output Options:**
- `--out` - Output directory (default: `./KavitaLibrary`)
- `--languages` - Language codes (default: `en`)
- `--sleep` - Seconds between downloads (default: 1.0)
- `--no-collections` - Skip collection metadata

**Container Management:**
- `--keep-running` - Keep containers running after download
- `--start-only` - Only start containers, don't download
- `--stop-only` - Only stop containers
- `--skip-wait` - Skip API ready check (use if already running)
- `--show-logs` - Show container logs before exiting

**Debugging:**
- `--debug` - Print first book's data structure for debugging

### Manual Method (Advanced Users)

If you prefer manual control:

```powershell
# 1. Start Gutendex containers
docker-compose -f docker-compose.gutendex.yml up -d

# 2. Wait for containers to be ready (10-15 minutes on first run)
# Check status: docker-compose -f docker-compose.gutendex.yml logs gutendex

# 3. Verify API is responding (should show book count)
curl http://localhost:8000/books?page_size=1

# 4. Download books
python gutendex_selfhosted_to_kavita.py --mode popular --count-per-genre 100

# 5. Stop containers when done
docker-compose -f docker-compose.gutendex.yml down
```

### First-Time Setup

**Initial startup takes 10-15 minutes** while Gutendex:
1. Pulls Docker images (~500MB)
2. Initializes PostgreSQL database
3. Downloads Project Gutenberg catalog (~5GB via rsync)
4. Populates database with 76,000+ book records

**Subsequent startups are fast** (~30 seconds) since the catalog is cached.

### Troubleshooting

**Docker not found:**
- Install Docker Desktop: https://www.docker.com/products/docker-desktop
- Ensure Docker Desktop is running (check system tray)

**Containers stuck "Downloading catalog":**
- First run takes 10-15 minutes - this is normal
- Check progress: `docker-compose -f docker-compose.gutendex.yml logs -f gutendex`
- Catalog is ~5GB and downloads via rsync

**API returns 0 books:**
- Catalog download may still be in progress
- Wait for logs to show "Starting Gunicorn" before downloading

**All downloads fail with 404:**
- This was a URL format issue - now fixed in latest version
- URLs should be `/cache/epub/{id}/pg{id}-images.epub`
- Use `--debug` flag to see actual URLs being tried

**Port 8000 already in use:**
- Another application is using port 8000
- Stop other services or modify `docker-compose.gutendex.yml` to use different port

---

## Option 2: Public Gutendex API

Uses the free public Gutendex API (currently unreliable).

**Status:** ⚠️ Currently experiencing 500 errors

```powershell
# Not recommended - use self-hosted instead
python Project_Gutenberg_top_genres_to_kavita.py --count-per-genre 20 --genres-top 10
```

---

## Option 3: Commercial GutenbergAPI

Uses RapidAPI's commercial GutenbergAPI service.

**Requires:** RapidAPI key from https://rapidapi.com/

```powershell
python gutenbergapi_to_kavita.py --api-key YOUR_KEY --mode popular --limit 100
```

See `README_GUTENBERGAPI.md` for details.

---

## What the Scripts Do

All scripts:
1. Query Gutenberg catalog for books
2. Download EPUBs from Project Gutenberg mirrors
3. **Remove all Project Gutenberg branding/boilerplate** from EPUB internals
4. Embed/normalize OPF metadata:
   - Title, authors, language, subjects
   - EPUB3 collection tags for Kavita Reading Lists
   - Series information (if available)
5. Organize into Kavita-ready folder structure (one folder per Series/Title)
6. Generate CSV reports with download status

### Output Structure

```
KavitaLibrary/
  Frankenstein/
    Frankenstein - Gutenberg84.epub
  Sherlock_Holmes/
    A_Study_in_Scarlet - Gutenberg244.epub
    The_Hound_of_the_Baskervilles - Gutenberg2852.epub
  _reports/
    kavita_epub_report.csv
    collections.csv
    README.txt
```

### Metadata Embedded

- `dc:title` → Book title
- `dc:creator` → Authors
- `dc:language` → Language code
- `dc:subject` → Genres/topics
- `calibre:series` → Series name (if present)
- `belongs-to-collection` → Collection/genre for Kavita Reading Lists

---

## Kavita Media Server Integration

These scripts are optimized for **Kavita**, a free, open-source ebook/manga server.

### Setting Up Kavita

1. **Install Kavita**: https://www.kavitareader.com/
2. **Add Library**:
   - Go to Libraries → Add Library
   - Browse to your `KavitaLibrary` folder
   - Set Library Type to "Book"
3. **Enable Collections**:
   - Settings → Libraries → Manage Collections
   - Enable "Import from metadata"
4. **Scan Library**: Kavita will parse embedded OPF metadata
5. **Browse**: By Series, Collections, or Reading Lists

---

## Advanced Configuration

### Docker Compose Services

The `docker-compose.gutendex.yml` file defines:

- **postgres**: PostgreSQL 16 database (stores book metadata)
- **gutendex**: Django API server (serves book data)
- **catalog-updater**: Daily cron job (keeps catalog up-to-date)

### Volumes & Persistence

All data persists across container restarts:
- `gutendex-postgres-data`: Database files
- `gutendex-catalog-files`: Project Gutenberg rsync catalog
- `gutendex-static-files`: Django static assets
- `gutendex-media-files`: Uploaded media
- `gutendex-application`: Application code

### Health Checks

Containers include health checks:
- PostgreSQL: Connection test every 30s
- Gutendex: HTTP check on port 8000

### Resource Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 5GB for catalog + space for downloaded books
- **Network**: Broadband for initial catalog download

---

## Performance Tips

1. **Keep containers running** between downloads (`--keep-running`)
2. **Adjust sleep time** based on your network (`--sleep 0.5` for faster)
3. **Use genre filtering** to download only what you need
4. **Monitor disk space** - full library can exceed 10GB

---

## Files Included

- `automated_gutendex_download.py` - **Main script** (recommended)
- `gutendex_selfhosted_to_kavita.py` - Manual download script
- `docker-compose.gutendex.yml` - Docker infrastructure
- `requirements.txt` - Python dependencies
- Various documentation files (QUICK_START, SELF_HOST_GUTENDEX, etc.)

---

## License & Disclaimer

This tool is provided as-is for legitimate use only. Users are solely responsible for ensuring compliance with applicable laws and regulations.

**Project Gutenberg Compliance:** This script removes branding/boilerplate to comply with Project Gutenberg's [trademark policy](https://www.gutenberg.org/policy/trademark_policy.html) regarding redistribution.

All Project Gutenberg books downloaded are in the public domain in the United States.
