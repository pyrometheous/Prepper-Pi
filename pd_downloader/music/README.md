# Public Domain Music Downloader

> ⚠️ **WORK IN PROGRESS** - This tool is actively being developed. There is no guarantee that anything will work as expected. Use at your own risk.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Legal Notice](#-critical-legal-notice)
- [Overview & Features](#overview)
- [Storage Requirements](#️-storage-requirements--unlimited-downloads)
- [Installation](#prerequisites)
- [Usage Examples](#usage)
- [Command-Line Reference](#command-line-arguments)
- [Media Server Setup](#media-server-integration)
- [Troubleshooting](#troubleshooting)
- [License Verification](#license-verification-details)
- [FAQ](#faq)

---

## Navigation

- 🏠 **[Main README](../README.md)** - Overview of all downloaders
- 📽️ **[Movies README](../movies/README.md)** - Public domain films
- 📚 **[Gutenberg README](../ebooks/GUTENBERG_README.md)** - Project Gutenberg ebooks
- 📖 **[Standard Ebooks README](../ebooks/STANDARD_EBOOKS_README.md)** - Standard Ebooks library

---

## Quick Start

**🚀 Get started in 3 steps:**

### 1. Install Dependencies

```powershell
# Ensure Python 3.8+ is installed
python --version

# Navigate to this directory
cd *\Prepper-Pi\pd_downloader\music

# Install required packages
pip install -r requirements.txt
```

### 2. Test Download (10 tracks)

```powershell
# Download 10 pre-1930 tracks using smart defaults
python pd_music_downloader.py --out ./test_music --max-items 10
```

### 3. Review Results

```powershell
# Check what was downloaded
Get-Content ./test_music/index.csv | ConvertFrom-Csv | Format-Table

# Read the auto-generated README
Get-Content ./test_music/README.md
```

**That's it!** Now set up your media server (see [Media Server Integration](#media-server-integration)).

---

## ⚠️ CRITICAL LEGAL NOTICE

### Acceptable Use ✅

- ✅ Downloading **confirmed public domain (PD)** music from verified sources
- ✅ Downloading **CC0 (Creative Commons Zero)** licensed music
- ✅ Building personal or commercial music collections for **offline distribution**
- ✅ Archival and educational purposes
- ✅ Resale of public domain/CC0 recordings (verify individually)

### Prohibited Use ❌

- ❌ **ABSOLUTELY NO downloading of copyrighted music without permission**
- ❌ Downloading music with CC-BY, CC-BY-SA, or other attribution-required licenses (script blocks these)
- ❌ Bypassing license verification checks
- ❌ Assuming all old recordings are public domain (they're not!)
- ❌ Downloading from sources not explicitly verified as PD/CC0
- ❌ Abusing Internet Archive or Wikimedia Commons with excessive requests

### ⚠️ Music Copyright is Complex

**Music copyright involves MULTIPLE layers:**

1. **Composition Copyright** (the musical score/lyrics) - Can last 70+ years after composer's death
2. **Recording Copyright** (the actual performance) - Can last 95+ years from publication
3. **Performance Rights** - Separate from composition and recording rights

**Example:** A 1920s song by George Gershwin:
- ✅ The composition *might* be public domain (depends on publication/renewal)
- ❌ A 1985 recording is **definitely still copyrighted**
- ✅ A 1925 recording *might* be public domain (depends on publication/restoration)

**This script only downloads recordings explicitly marked PD or CC0 by trusted sources.**

### U.S. Copyright Law Context

In the United States, sound recordings published:
- **Before 1923**: Generally public domain
- **1923-1946**: Public domain if copyright not renewed
- **1947-1956**: Complicated (published with notice + renewed = protected until 2047+)
- **After 1972**: Protected under federal law until 2067+
- **Pre-1972**: Varied by state law until 2022 (now federalized)

**Other countries have different rules!** Public domain status varies by jurisdiction.

### Verification Safeguards

This script includes **three layers of license verification**:

1. **Source-level filtering**: Only queries Internet Archive and Wikimedia Commons with explicit PD/CC0 license filters
2. **Metadata checking**: Verifies each file's license URL contains "publicdomain" or "cc0" strings
3. **Optional Musopen cross-check**: Best-effort verification against Musopen.org's PD/CC0 catalog

**⚠️ THESE CHECKS ARE NOT LEGAL GUARANTEES.** You are solely responsible for verifying the copyright status of any downloaded content before redistribution.

### Your Responsibilities

When using this tool, you **MUST**:

- ✅ Review the `metadata.json` for each track and verify license status
- ✅ Check the source URLs provided in `index.csv`
- ✅ Understand copyright laws in your jurisdiction
- ✅ Perform additional due diligence before commercial use
- ✅ Respect rate limits and terms of service for Internet Archive and Wikimedia Commons

**If you're unsure about a recording's status, DO NOT use it commercially.**

---

## Overview

Download **public domain and CC0** classical music, jazz, folk recordings, and historical performances with full provenance tracking, metadata embedding, and Jellyfin/Navidrome integration.

This tool is designed for building **legal, offline music collections** suitable for:
- Personal media server libraries
- Educational archives
- Commercial redistribution (after individual verification)
- Historical preservation
- Off-grid entertainment systems

### Features

- ✅ **PD/CC0 Only** - Strict license filtering (no CC-BY, CC-BY-SA)
- ✅ **Multi-source** - Internet Archive and Wikimedia Commons
- ✅ **Composer/Era Filters** - Target specific periods (e.g., "pre-1930", "baroque", "1890-1910")
- ✅ **Format Control** - Prefer FLAC/OGG/WAV with optional MP3 fallback
- ✅ **Metadata Embedding** - ID3/Vorbis/FLAC tags for media servers
- ✅ **NFO Files** - Jellyfin-friendly sidecar metadata
- ✅ **Provenance Tracking** - Full source URLs, licenses, and checksums
- ✅ **Musopen Cross-check** - Optional verification against Musopen.org catalog
- ✅ **Auto-generated README** - License documentation in output directory

---

## Prerequisites

### 1. Python Requirements

```powershell
# Python 3.8 or higher
python --version

# Navigate to music downloader directory
cd *\VSCode\Prepper-Pi\pd_downloader\music

# Install dependencies
pip install -r requirements.txt
```

**Dependencies:**
- `requests>=2.31.0` - HTTP operations
- `mutagen>=1.47.0` - Audio metadata tagging (optional but recommended)

---

## Usage

### Basic Examples

#### Simplest Usage (Smart Defaults)

```powershell
# Download 100 tracks from all sources using smart defaults
# No query needed - script automatically searches PD collections!
python pd_music_downloader.py --out ./music
```

#### Internet Archive - Popular 78rpm Records

```powershell
# Download 200 tracks from pre-1930 78rpm collections (FLAC preferred, fallback to MP3)
# Query is optional - uses smart default if omitted
python pd_music_downloader.py --source ia --out ./music --max-items 200 \
  --preferred-format flac --fallback-to-mp3 \
  --era "pre-1930"
```

#### Wikimedia Commons - Classical Music

```powershell
# Download 50 Bach compositions (OGG only, skip if not available)
# Query is optional - uses smart default for classical music
python pd_music_downloader.py --source commons --out ./music --max-items 50 \
  --preferred-format ogg --skip-if-missing-format \
  --composer "Bach"
```

#### Internet Archive - Jazz Era

```powershell
# Download early jazz recordings by Louis Armstrong (1920s)
python pd_music_downloader.py --source ia --out ./music --max-items 100 \
  --preferred-format flac --fallback-to-mp3 \
  --composer "Louis Armstrong" --era "1920s" \
  --query "collection:(georgeblood OR 78rpm) AND mediatype:audio"
```

#### Baroque Period Collection

```powershell
# Download baroque period music (1600-1750)
python pd_music_downloader.py --source commons --out ./music --max-items 100 \
  --preferred-format flac --fallback-to-mp3 \
  --era "baroque" \
  --query "harpsichord|baroque|vivaldi|bach|handel"
```

### Advanced Examples

```powershell
# Romantic period piano music (1820-1910), WAV format only
python pd_music_downloader.py --source ia --out ./music --max-items 75 \
  --preferred-format wav --skip-if-missing-format \
  --era "romantic" \
  --query "piano AND mediatype:audio"

# Early recordings (pre-1925), any PD-friendly format
python pd_music_downloader.py --source ia --out ./music --max-items 300 \
  --preferred-format flac --fallback-to-mp3 \
  --era "pre-1925" \
  --query "mediatype:audio"
```

---

## ⚠️ STORAGE REQUIREMENTS & UNLIMITED DOWNLOADS

### Understanding Download Sizes

#### Per-Track Estimates (Average)
- **FLAC (Lossless)**: 15-40 MB per track (full album quality)
- **MP3 (320 kbps)**: 5-15 MB per track (high quality)
- **OGG Vorbis**: 3-10 MB per track (good quality)
- **WAV (Uncompressed)**: 30-60 MB per track (archival quality)

#### Collection Size Estimates

| Collection Type | Track Count | Estimated Size (FLAC) | Estimated Size (MP3) |
|----------------|-------------|----------------------|---------------------|
| Small Sample | 100 tracks | ~2-4 GB | ~0.5-1.5 GB |
| Medium Collection | 500 tracks | ~10-20 GB | ~2.5-7.5 GB |
| Large Collection | 2,000 tracks | ~40-80 GB | ~10-30 GB |
| **Unlimited (IA)** | **200,000+** | **~3-8 TB** | **~1-3 TB** |
| **Unlimited (Commons)** | **50,000+** | **~0.75-2 TB** | **~250-750 GB** |

### Unlimited Downloads (`--max-items -1`)

**⚠️ WARNING: Downloading "everything" can result in MASSIVE storage requirements!**

When you use `--max-items -1`, the script will attempt to download:

- **Internet Archive**: ~200,000+ public domain audio files
  - Great 78 Project: ~100,000+ recordings
  - George Blood Collection: ~50,000+ recordings
  - Library of Congress: ~10,000+ recordings
  - Other PD collections: ~40,000+ recordings
  - **Estimated Total**: 1-8 TB depending on format

- **Wikimedia Commons**: ~50,000+ audio files
  - Classical performances: ~20,000+ files
  - Historical recordings: ~15,000+ files
  - Folk/traditional music: ~10,000+ files
  - Spoken word/speeches: ~5,000+ files
  - **Estimated Total**: 250 GB - 2 TB depending on format

### Recommended Disk Space

**Before running unlimited downloads:**

| Your Goal | Recommended Free Space | Format Recommendation |
|-----------|----------------------|----------------------|
| Personal Sample | 10+ GB | MP3 (320 kbps) |
| Small Home Server | 50+ GB | MP3 or OGG |
| Medium Collection | 100+ GB | FLAC with MP3 fallback |
| Large Archival | 500+ GB | FLAC only |
| **Complete IA Archive** | **5+ TB** | **FLAC (use external drives!)** |
| **Everything (IA + Commons)** | **10+ TB** | **FLAC (requires NAS/SAN)** |

### Disk Space Checking

The script **automatically checks** available disk space before downloading and will:

1. **Estimate** total download size based on `--max-items` and source(s)
2. **Display** your current free space vs. estimated requirements
3. **Warn** if download will exceed 80% of free space
4. **Ask for confirmation** before proceeding with large downloads
5. **Cancel** if insufficient space detected (unless you override)

#### Example Disk Space Warning:

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         STORAGE REQUIREMENTS                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚠️  UNLIMITED DOWNLOAD MODE (--max-items -1)
📊 Estimated collection size: ~250,000 tracks
💾 Estimated storage needed: ~1,250.0 GB
   (This could be 100+ GB to 1+ TB depending on format!)

💿 Your disk space:
   Free: 500.0 GB / 1,000.0 GB total

❌ WARNING: Insufficient disk space!
   You need at least 1,250.0 GB free.
   You only have 500.0 GB available.

⚠️  Continue anyway? (yes/no):
```

### Best Practices for Large Downloads

1. **Start Small**: Test with `--max-items 10` before attempting unlimited
2. **Use External Drives**: For collections >500 GB, use external USB/NAS storage
3. **Prefer MP3**: If space is limited, use `--preferred-format mp3` instead of FLAC
4. **Filter by Era**: Use `--era "pre-1925"` to limit scope
5. **Monitor Progress**: Check `index.csv` periodically to track download count
6. **Resume Support**: Script automatically skips duplicates if interrupted
7. **Network Bandwidth**: Unlimited downloads can take **days to weeks** on slow connections

---

### Command-Line Arguments

#### Source Selection
- `--source` - Download source: `ia` (Internet Archive), `commons` (Wikimedia Commons), or `all` (both) (default: `all`)

#### Output Options
- `--out` - Output directory (default: `./output_music`)
- `--max-items` - Maximum tracks to download per source (default: `100`)
  - Use `-1` for unlimited downloads (**WARNING: Can be 100+ GB to multiple TB!**)
  - Disk space check will prompt for confirmation before large downloads

#### Search Filters
- `--query` - Source-specific search query (**OPTIONAL** - smart defaults used if not provided)
  - Internet Archive default: Searches major PD collections (great78, georgeblood, 78rpm, etc.)
  - Wikimedia Commons default: Searches classical/historical music terms
- `--composer` - Filter by composer/creator name (best-effort matching)
- `--era` - Time period filter (see Era Filters section)

#### Audio Format
- `--preferred-format` - Preferred format: `flac`, `ogg`, `wav`, or `mp3` (default: `flac`)
- `--fallback-to-mp3` - Allow MP3 fallback if preferred format unavailable
- `--skip-if-missing-format` - Skip track entirely if preferred format unavailable

### Era Filter Options

The `--era` argument supports:

**Year Ranges:**
- `pre-1930` - Before 1930
- `pre-1925` - Before 1925
- `1890-1910` - Specific range (inclusive)
- `1920s` - Decade (1920-1929)

**Stylistic Periods:**
- `baroque` - Baroque period (1600-1750)
- `classical` - Classical period (1750-1820)
- `romantic` - Romantic period (1820-1910)
- `20th` - 20th century (1900-1999)

**Examples:**
```powershell
--era "pre-1930"      # Anything before 1930
--era "1890-1910"     # Specific 20-year range
--era "baroque"       # Baroque period music
--era "1920s"         # The roaring twenties
```

### Query Syntax

#### Internet Archive Queries

Internet Archive uses Lucene query syntax:

```powershell
# Collections
"collection:(great78 OR georgiaarchives) AND mediatype:audio"

# Specific creator
"creator:\"Gershwin\" AND mediatype:audio"

# Subject tags
"subject:jazz AND mediatype:audio"

# Combined filters
"collection:78rpm AND subject:(jazz OR blues) AND mediatype:audio"
```

**Recommended IA Collections for PD Music:**
- `great78` - Great 78 Project (pre-1923 recordings)
- `georgeblood` - George Blood collection
- `78rpm` - General 78rpm records
- `georgiaarchives` - Georgia Archives
- `loc` - Library of Congress (partial)

#### Wikimedia Commons Queries

Simple text or pipe-separated terms:

```powershell
# Single term
"piano"

# Multiple terms (OR logic)
"piano|orchestra|symphony"

# Specific works
"brandenburg concerto"
```

---

## What This Script Does

### Download Process

1. **Query Construction**
   - Builds source-specific query with PD/CC0 license filters
   - Adds composer and era filters if specified
   - Sorts by popularity/downloads (Internet Archive)

2. **License Verification** (3 layers)
   - Source-level: Only queries PD/CC0 collections
   - Metadata-level: Verifies `licenseurl` contains "publicdomain" or "cc0"
   - Optional: Cross-checks with Musopen.org catalog

3. **Format Selection**
   - Checks for preferred format (FLAC/OGG/WAV/MP3)
   - Falls back to MP3 if enabled
   - Skips track if format unavailable and skip-if-missing enabled

4. **Download & Organization**
   - Downloads audio file with retry logic
   - Organizes by Collection/Creator → Title structure
   - Generates unique, filesystem-safe filenames

5. **Metadata Embedding**
   - Embeds ID3/Vorbis/FLAC tags (requires mutagen):
     - Title, Artist, Album, Year
     - Comment (license URL + source URL)
   - Creates `.nfo` sidecar file for media servers
   - Writes `metadata.json` with full provenance

6. **Reporting**
   - Updates `index.csv` with all downloads
   - Logs source, license, download URL, file path
   - Tracks Musopen verification results

### Output Structure

```
output_music/
  README.md                          # License info, disclaimers, usage tips
  index.csv                          # Master inventory (all tracks)
  Great_78_Project/
    Gershwin_Rhapsody_in_Blue/
      Rhapsody_in_Blue - IA12345.flac
      Rhapsody_in_Blue - IA12345.nfo
      metadata.json
  Wikimedia_Commons/
    Bach_Brandenburg_Concerto_No_1/
      Brandenburg_Concerto_1 - Commons.ogg
      Brandenburg_Concerto_1 - Commons.nfo
      metadata.json
```

### Metadata Files

#### `metadata.json` (per track)

```json
{
  "source": "internet_archive",
  "identifier": "78_rhapsody-in-blue_gershwin-whiteman_12345",
  "collection": "great78",
  "title": "Rhapsody in Blue",
  "creator": "George Gershwin / Paul Whiteman Orchestra",
  "year": "1924",
  "licenseurl": "https://creativecommons.org/publicdomain/mark/1.0/",
  "url": "https://archive.org/details/78_rhapsody-in-blue_gershwin-whiteman_12345",
  "file": "78_rhapsody-in-blue_gershwin-whiteman_12345.flac",
  "format": "FLAC",
  "bytes": 34567890,
  "original": "https://archive.org/download/78_rhapsody.../file.flac",
  "musopen_verified": "true",
  "musopen_hint": "public domain"
}
```

#### `index.csv` (global inventory)

Columns: `source`, `id`, `title`, `creator`, `year`, `license`, `download_url`, `relative_path`

### Auto-Generated README

The script creates `README.md` in the output directory with:
- License information (PD/CC0 explanation)
- Source attribution (Internet Archive, Wikimedia Commons)
- Musopen verification notes
- Jellyfin/Navidrome setup instructions
- Legal disclaimer

---

## Media Server Integration

### Jellyfin (Recommended for Off-Grid)

**Why Jellyfin?**
- ✅ Fully open-source (no commercial dependencies)
- ✅ Works completely offline
- ✅ Reads embedded tags (ID3, Vorbis, FLAC)
- ✅ Supports .nfo sidecar metadata
- ✅ Rich web and mobile clients

**Setup:**

1. **Install Jellyfin**: https://jellyfin.org/downloads
2. **Add Music Library**:
   - Dashboard → Libraries → Add Library
   - Content type: "Music"
   - Browse to your `output_music` folder
3. **Metadata Settings**:
   - Enable "Prefer embedded titles over filenames"
   - Enable "NFO metadata" provider
4. **Scan Library**: Jellyfin reads tags and .nfo files automatically
5. **Browse**: By Artist, Album, Genre, or Folder

### Navidrome (Lightweight Alternative)

**Why Navidrome?**
- ✅ Extremely lightweight (single binary)
- ✅ Subsonic/Airsonic API compatible
- ✅ Perfect for Raspberry Pi / low-power systems
- ✅ Beautiful, modern web interface

**Setup:**

```powershell
# Docker method (easiest)
docker run -d \
  --name navidrome \
  -v /path/to/output_music:/music \
  -v /path/to/data:/data \
  -p 4533:4533 \
  deluan/navidrome:latest
```

Access at: http://localhost:4533

### Funkwhale (Federation-Ready)

**Why Funkwhale?**
- ✅ Open-source, ActivityPub federation
- ✅ Works offline or federated
- ✅ Supports podcasts and radio

**Note:** More complex setup; only use if you need federation features.

### Metadata Mapping

| Script Output | Jellyfin | Navidrome | ID3/Vorbis/FLAC Tag |
|--------------|----------|-----------|---------------------|
| Title | ✅ | ✅ | `TIT2` / `title` |
| Creator | ✅ (Artist) | ✅ | `TPE1` / `artist` |
| Collection | ✅ (Album) | ✅ | `TALB` / `album` |
| Year | ✅ | ✅ | `TDRC` / `date` |
| License + Source | ✅ (Comment) | ✅ | `COMM` / `comment` |
| .nfo file | ✅ | ❌ | N/A |

---

## License Verification Details

### Internet Archive

**Query Filters:**
```python
license_terms = [
    'licenseurl:*publicdomain*',
    'licenseurl:*cc0*'
]
```

**Metadata Check:**
```python
lic = metadata.get('licenseurl', '').lower()
if not (("publicdomain" in lic) or ("cc0" in lic)):
    skip_track()
```

**Safe Collections:**
- `great78` - Pre-1923 78rpm recordings (U.S. PD)
- `georgeblood` - Curated PD audio
- `78rpm` - Historical recordings
- `georgiaarchives` - State archive material

### Wikimedia Commons

**License Bucket Detection:**
```python
def license_bucket_from_extmetadata(meta):
    lic_short = meta.get('LicenseShortName')
    lic_url = meta.get('LicenseUrl')
    
    if 'public domain' in lic_short or 'publicdomain' in lic_url:
        return 'pd'
    if 'cc0' in lic_short or 'creativecommons.org/publicdomain/zero' in lic_url:
        return 'cc0'
    
    return 'other'  # REJECTED

# Only 'pd' and 'cc0' buckets are downloaded
```

### Musopen Cross-Check

**Best-Effort Verification:**

1. Queries Musopen API: `https://musopen.org/api/search/recordings/?q={composer} {title}`
2. Checks top 5 results for PD/CC0 indicators
3. Results stored in `metadata.json`:
   - `"musopen_verified": "true"` - Found matching PD/CC0 recording
   - `"musopen_verified": "not_found"` - No match in Musopen catalog
   - `"musopen_verified": "unknown"` - API error or unreachable

**⚠️ Important:** Musopen verification is **supplementary only**. The primary license gate is the source metadata check.

---

## Troubleshooting

### Common Issues

#### "No files found for identifier"

**Problem:** Internet Archive item has no suitable audio files.

**Solutions:**
- Try different preferred format: `--preferred-format mp3`
- Enable fallback: `--fallback-to-mp3`
- Check if item actually contains audio (visit source URL)

#### "License check failed - skipping"

**Problem:** Track doesn't have explicit PD/CC0 license.

**Solutions:**
- ✅ **This is working correctly!** The script is protecting you from copyrighted content.
- If you believe the track should be PD, check the source URL manually
- Report metadata errors to Internet Archive/Wikimedia Commons

#### Downloads are slow

**Problem:** Rate limiting or network issues.

**Solutions:**
- Internet Archive and Wikimedia Commons may throttle requests
- Script includes 0.4-0.5 second delays between requests (polite)
- Large FLAC files take time to download
- Consider using `--preferred-format mp3` for faster downloads

#### "mutagen not found" warnings

**Problem:** Mutagen library not installed.

**Solutions:**
```powershell
pip install mutagen
```

**Note:** Downloads still work without mutagen, but tags won't be embedded.

#### Musopen verification always returns "unknown"

**Problem:** Musopen API may be unavailable or rate-limiting.

**Solutions:**
- This is **non-critical** - primary license check still works
- Musopen is best-effort only
- No action needed unless you require Musopen corroboration

### Legal Issues

#### "How do I know this is really public domain?"

**Answer:**

1. Check the `metadata.json` file for each track
2. Visit the `url` field to see the source page
3. Review the `licenseurl` field
4. For Internet Archive, look for "public domain mark" or "CC0" badges
5. For commercial use, consider consulting a copyright attorney

#### "I found copyrighted music in my downloads!"

**Action:**

1. ⚠️ **Stop using the file immediately**
2. Check the source URL and license metadata
3. Report the issue to the source (Internet Archive/Wikimedia Commons)
4. Delete the file from your collection
5. File an issue on this project's GitHub if the script's filters failed

**Remember:** Copyright law is complex and jurisdiction-dependent. These tools help but don't replace legal advice.

---

## Rate Limiting & Ethics

### Built-in Safeguards

- **0.4-0.5 second delay** between requests (configurable in code)
- **Sequential downloads** (no parallel abuse)
- **Retry logic** with exponential backoff
- **Respects HTTP error codes** (stops on 403/429)

### Best Practices

✅ **DO:**
- Use reasonable `--max-items` limits (< 500 per session)
- Run during off-peak hours for large downloads
- Support Internet Archive and Wikimedia Commons with donations
- Credit sources when redistributing

❌ **DON'T:**
- Remove the delay logic or parallelize requests
- Hammer APIs repeatedly on errors
- Bypass license checks
- Abuse the service for commercial mass downloading

**These sources provide invaluable free resources. Please be respectful.**

---

## Performance Tips

1. **Format Selection**
   - FLAC: Highest quality, largest files (10-50 MB/track)
   - OGG: Good quality, smaller files (5-15 MB/track)
   - MP3: Compatible, smallest files (3-10 MB/track)
   - WAV: Uncompressed, very large (50-100 MB/track)

2. **Optimize Downloads**
   - Use `--preferred-format mp3 --fallback-to-mp3` for speed
   - Filter by era/composer to reduce total items
   - Run overnight for large collections (200+ tracks)

3. **Storage Planning**
   - 100 FLAC tracks ≈ 2-5 GB
   - 100 MP3 tracks ≈ 500 MB - 1 GB
   - Budget 50-100 MB per track for FLAC

4. **Network Considerations**
   - Internet Archive: Generally fast CDN
   - Wikimedia Commons: May be slower for large files
   - Expect 2-10 Mbps download speeds

---

## Example Workflows

### Build Complete Pre-1930 Jazz Collection

```powershell
# Step 1: Download from Internet Archive great78 collection
python pd_music_downloader.py \
  --source ia \
  --out ./PD_Music/Jazz \
  --max-items 300 \
  --preferred-format flac --fallback-to-mp3 \
  --era "pre-1930" \
  --query "collection:great78 AND subject:jazz AND mediatype:audio"

# Step 2: Point Jellyfin at ./PD_Music/Jazz
# Step 3: Review index.csv and metadata files
# Step 4: Enjoy!
```

### Classical Music Starter Library

```powershell
# Bach
python pd_music_downloader.py --source commons --out ./Classical \
  --max-items 50 --composer "Bach" --era "baroque" \
  --query "bach|brandenburg|fugue|cello|violin"

# Mozart
python pd_music_downloader.py --source commons --out ./Classical \
  --max-items 50 --composer "Mozart" --era "classical" \
  --query "mozart|symphony|piano|concerto"

# Beethoven
python pd_music_downloader.py --source commons --out ./Classical \
  --max-items 50 --composer "Beethoven" --era "romantic" \
  --query "beethoven|symphony|piano|sonata"
```

### Historical Recordings Archive

```powershell
# Pre-1923 recordings (definitely PD in US)
python pd_music_downloader.py \
  --source ia \
  --out ./Historical_Archive \
  --max-items 500 \
  --preferred-format flac \
  --era "pre-1923" \
  --query "mediatype:audio"
```

---

## Requirements File

Create `requirements.txt` in this directory:

```txt
requests>=2.31.0
mutagen>=1.47.0
```

Install with:
```powershell
pip install -r requirements.txt
```

---

## FAQ

### General Questions

#### Q: Is `--max-items` required?

**A:** No! It's optional and defaults to **100 tracks per source** if not specified.

#### Q: Is `--query` required?

**A:** No! The script uses **smart defaults** if you don't provide a query:
- **Internet Archive**: Searches major PD collections (great78, georgeblood, 78rpm, etc.)
- **Wikimedia Commons**: Searches classical/historical music terms

#### Q: What's the simplest command to get started?

**A:** Just specify an output directory:
```powershell
python pd_music_downloader.py --out ./music
```
This downloads 100 tracks from each source using smart defaults!

#### Q: Can I download "everything" available?

**A:** Yes, use `--max-items -1` for unlimited downloads, but be warned:
- **Internet Archive**: ~200,000+ tracks (1-8 TB)
- **Wikimedia Commons**: ~50,000+ tracks (250 GB - 2 TB)
- **Total estimate**: Up to 10 TB for FLAC format!

The script will check your disk space and ask for confirmation.

### Storage Questions

#### Q: How much disk space do I need?

**A:** It depends on your `--max-items` setting:

| Max Items | Format | Estimated Size |
|-----------|--------|---------------|
| 10 | MP3 | 50-150 MB |
| 100 | MP3 | 500 MB - 1.5 GB |
| 100 | FLAC | 1.5-4 GB |
| 1,000 | FLAC | 15-40 GB |
| Unlimited | MP3 | 1-3 TB |
| Unlimited | FLAC | 3-8 TB |

#### Q: What happens if I don't have enough disk space?

**A:** The script automatically:
1. Estimates download size before starting
2. Checks your available disk space
3. Warns you if space is insufficient
4. Asks for confirmation before proceeding
5. Cancels if you decline

#### Q: Can I resume an interrupted download?

**A:** Yes! The script automatically detects existing files and skips duplicates. Just run the same command again.

### Legal Questions

#### Q: Is all this music really public domain?

**A:** The script downloads **only** tracks marked as PD or CC0 by trusted sources, with three layers of verification:
1. Source-level filtering (PD/CC0 collections only)
2. Metadata checking (license URL verification)
3. Optional Musopen cross-check

However, **you are responsible** for verifying copyright status before commercial use.

#### Q: Can I use this music commercially?

**A:** **Maybe**. Public domain recordings can generally be used commercially, but:
- ✅ Personal/educational use is safe
- ⚠️ Commercial use requires individual track verification
- ✅ Check `metadata.json` for each track
- ✅ Visit source URLs to verify license
- ⚠️ Consult a copyright attorney for high-value projects

#### Q: Why was a track rejected/skipped?

**A:** Check `_rejected_tracks.csv` in your output directory. Common reasons:
- License wasn't explicitly PD or CC0
- Metadata missing or incomplete
- File format unavailable (if using `--skip-if-missing-format`)

This is the script **protecting you** from copyrighted content!

### Download Questions

#### Q: Downloads are very slow. Is this normal?

**A:** Yes, several factors affect speed:
- Internet Archive and Wikimedia Commons may throttle requests
- Script includes polite delays (0.4-0.5 seconds between requests)
- FLAC files are large (10-50 MB per track)
- Your internet connection speed

**Solutions:**
- Use `--preferred-format mp3` for faster downloads
- Run overnight for large collections
- Split downloads across multiple days

#### Q: Why does Wikimedia Commons always fail with 403 Forbidden?

**A:** This can happen due to:
- Rate limiting (try again later)
- User-Agent requirements
- Geographic restrictions

The script will skip Commons and continue with Internet Archive.

#### Q: Can I download from just one source?

**A:** Yes! Use `--source ia` or `--source commons`:
```powershell
# Internet Archive only
python pd_music_downloader.py --source ia --out ./music

# Wikimedia Commons only
python pd_music_downloader.py --source commons --out ./music
```

### Technical Questions

#### Q: What if I don't have `mutagen` installed?

**A:** Downloads still work, but audio tags won't be embedded. Install it for best results:
```powershell
pip install mutagen
```

#### Q: How do I verify a track is really public domain?

**A:** For each track:
1. Open the `metadata.json` file
2. Check the `licenseurl` field
3. Visit the `url` field (source page)
4. Verify license on source website
5. Check `musopen_verified` status (if available)

#### Q: What's the difference between FLAC, MP3, OGG, and WAV?

**A:**
- **FLAC**: Lossless compression, best quality, largest files (15-40 MB/track)
- **MP3**: Lossy compression, good quality, smallest files (5-15 MB/track)
- **OGG**: Lossy compression, good quality, small files (3-10 MB/track)
- **WAV**: Uncompressed, archival quality, huge files (30-60 MB/track)

For most users, **FLAC with MP3 fallback** is recommended.

### Usage Questions

#### Q: What's the recommended `--max-items` for a home media server?

**A:** Depends on your needs:
- **Small home** (testing): 100-500 tracks (500 MB - 5 GB)
- **Medium home** (typical): 1,000-2,000 tracks (5-20 GB)
- **Large home** (enthusiast): 5,000-10,000 tracks (25-100 GB)
- **Complete archive**: Unlimited (1+ TB)

Start small and increase as needed!

#### Q: Can I filter by specific composers or time periods?

**A:** Yes! Use these flags:
```powershell
# Filter by composer
--composer "Bach"

# Filter by era
--era "pre-1930"      # Before 1930
--era "baroque"       # Baroque period (1600-1750)
--era "1920s"         # Decade (1920-1929)
--era "1890-1910"     # Specific range
```

#### Q: How do I know if Musopen verification worked?

**A:** Check the `metadata.json` file for each track:
- `"musopen_verified": "true"` - Found matching PD/CC0 recording
- `"musopen_verified": "unknown"` - API unavailable (non-critical)

Musopen verification is **supplementary only** - the primary license check is the source metadata.

### Error Questions

#### Q: "No files found for identifier" error?

**A:** The Internet Archive item doesn't have the requested audio format.

**Solutions:**
- Try `--preferred-format mp3`
- Enable `--fallback-to-mp3`
- Check if item actually contains audio (visit source URL)

#### Q: "License check failed - skipping" message?

**A:** ✅ **This is correct behavior!** The script is protecting you from downloading copyrighted content. The track didn't have an explicit PD/CC0 license.

#### Q: Script crashes or stops unexpectedly?

**A:** Common causes:
1. **Network interruption**: Just re-run (script skips duplicates)
2. **Disk full**: Free up space and re-run
3. **API rate limiting**: Wait 10-15 minutes and try again

---

## Known Limitations

### Script Limitations

1. **No audio fingerprinting** - May download duplicates across sources
2. **Best-effort composer matching** - Not all sources have structured composer metadata
3. **Era filtering approximate** - Relies on year/date metadata (often incomplete)
4. **Musopen API unofficial** - No guarantee of availability or accuracy
5. **No deduplication** - Same recording from different sources will be downloaded twice

### Legal Limitations

1. **U.S.-centric** - Public domain rules vary by country
2. **No guarantee** - Scripts can't legally verify copyright status
3. **Metadata trust** - Relies on source metadata being accurate
4. **Sound recording complexity** - Music copyright has multiple layers

### Source Limitations

1. **Internet Archive**
   - Not all collections properly tagged with licenses
   - Some PD music may not be indexed in searches
   - Metadata quality varies

2. **Wikimedia Commons**
   - Smaller classical music collection
   - Upload quality varies
   - Fewer historical recordings

---

## Future Enhancements

**Under consideration:**

- ✨ Acoustic fingerprinting (Chromaprint) for deduplication
- ✨ Enhanced Musopen integration (direct API key support)
- ✨ Composer/work folder organization option
- ✨ HTML catalog generator for offline browsing
- ✨ Automatic playlist generation (M3U/PLS)
- ✨ Integration with MusicBrainz for enhanced metadata
- ✨ Support for additional PD sources (Musopen direct downloads with membership)

**Submit feature requests on GitHub!**

---

## Support & Resources

### Music Sources

- **Internet Archive**: https://archive.org/
  - Great 78 Project: https://great78.archive.org/
  - Donations: https://archive.org/donate
  
- **Wikimedia Commons**: https://commons.wikimedia.org/
  - Music category: https://commons.wikimedia.org/wiki/Category:Audio_files
  - Donations: https://donate.wikimedia.org/

- **Musopen** (membership required for downloads): https://musopen.org/
  - Free CC0 sheet music and recordings
  - Support musicians and public domain music

### Media Servers

- **Jellyfin**: https://jellyfin.org/
  - Documentation: https://jellyfin.org/docs/
  - Forum: https://forum.jellyfin.org/

- **Navidrome**: https://www.navidrome.org/
  - Documentation: https://www.navidrome.org/docs/
  - Discord: https://discord.gg/xh7j7yF

- **Funkwhale**: https://funkwhale.audio/
  - Documentation: https://docs.funkwhale.audio/

### Copyright Resources

- **U.S. Copyright Office**: https://www.copyright.gov/
- **Public Domain Sherpa**: https://www.publicdomainsherpa.com/
- **Stanford Copyright Renewal Database**: https://exhibits.stanford.edu/copyrightrenewals
- **Cornell Copyright Term Chart**: https://copyright.cornell.edu/publicdomain

---

## Disclaimer

This tool and its documentation are provided **as-is** for legitimate use only. 

**You are solely responsible for:**
- Verifying the copyright status of all downloaded content
- Complying with applicable laws in your jurisdiction
- Obtaining legal advice for commercial use
- Respecting terms of service for Internet Archive and Wikimedia Commons

**The developers of this tool:**
- Make no warranties about copyright status
- Are not liable for misuse or copyright infringement
- Recommend consulting a copyright attorney for commercial redistribution

**When in doubt, don't distribute.** It's better to err on the side of caution with copyright compliance.

---

## License

This script is released under **CC0-1.0** (public domain dedication).

You are free to use, modify, and redistribute this tool for any purpose without attribution (though attribution is appreciated).

**However, downloaded music may have different licenses (PD or CC0).** Always check individual track metadata.

---

## Acknowledgments

- **Internet Archive** - For preserving and providing access to historical recordings
- **Wikimedia Commons** - For hosting and curating public domain media
- **Musopen** - For promoting public domain music and providing verification resources
- **Jellyfin/Navidrome/Funkwhale teams** - For excellent open-source media server software
- **Contributors** - To public domain music digitization and preservation efforts

**Support these organizations if you benefit from their work!**
