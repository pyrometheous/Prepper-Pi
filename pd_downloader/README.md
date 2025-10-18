# Public Domain Media Downloader Suite

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

## Overview

This suite contains three Python scripts for downloading public domain media with built-in copyright protection measures:

### 1. **Public Domain Movies** (`public_domain_movies.py`)
Downloads verified public domain films from trusted sources:
- **Internet Archive** (archive.org) - Digital library with extensive PD film collections
- **Wikimedia Commons** - Community-verified public domain media
- **Direct URLs** - Pre-verified public domain sources

All downloads are tracked with SHA256 checksums and provenance information.

### 2. **Project Gutenberg Ebooks** (`Project_Gutenberg_top_genres_to_kavita.py`)
Downloads top-rated ebooks from Project Gutenberg by genre:
- Scrapes popular subjects from PG's catalog
- Downloads EPUBs and **cleans out Project Gutenberg boilerplate/branding**
- Embeds **Kavita-friendly OPF metadata** (subjects, collections, series info)
- Outputs in Kavita-ready folder structure (one folder per Series/Title)
- Generates CSV reports with validation status

### 3. **Standard Ebooks Library** (`standard_ebooks_to_kavita.py`)
Downloads the entire Standard Ebooks library:
- Uses OPDS feed with API key authentication (Patrons Circle required)
- Standard Ebooks editions are CC0 (public domain dedication)
- Embeds Kavita-compatible metadata with "Standard Ebooks" collection tags
- Supports resume capability (skips existing files)
- Optional subject filtering
- Sequential downloads with configurable rate limiting

## Copyright Protection Measures for **Public Domain Movies** (`public_domain_movies.py`)

This tool implements multiple safeguards to prevent copyright infringement:

### 1. **Curated Manifest System**
- Uses a CSV manifest (`manifest.csv`) with hand-selected public domain titles
- Each entry includes year, title, and verified source information
- Prevents arbitrary or automated downloads of unverified content

### 2. **Trusted Source Verification**
- **Internet Archive**: Only downloads from IA's public domain collections
- **Wikimedia Commons**: Uses files marked as public domain by the community
- **Direct URLs**: Only downloads from pre-approved public domain sources

### 3. **Provenance Tracking**
- Creates `_provenance.csv` with complete download history
- Records SHA256 checksums for file integrity verification
- Documents source URLs for audit trail
- Enables verification of public domain status

### 4. **Manual Curation Notes**
The manifest includes important warnings:
- Music licensing issues (e.g., "Watch music claims")
- Trademark considerations (e.g., "Mind trademarks" for Steamboat Willie)
- Restoration copyright warnings (e.g., "Prefer plain unrestored transfer")
- Content advisories (e.g., "Controversial; include only if desired")

### 5. **No Automated Discovery**
- Does NOT automatically search for or download content
- Requires explicit manifest entry for each film
- No bulk or automated scraping capabilities

## Installation & Prerequisites

### Python Requirements
```powershell
# Python 3.6 or higher required
python --version
```

### Install Dependencies
```powershell
# Install required packages for ebook downloaders
pip install -r requirements.txt

# This installs:
# - requests>=2.31.0 (for HTTP operations)
# - lxml>=4.9.0 (for EPUB/XML processing)
```

**Note:** `public_domain_movies.py` uses only Python standard library and requires no external dependencies.

---

## Usage Guide

### 📽️ Public Domain Movies

Downloads public domain films from a curated manifest.

```powershell
# Basic usage
python public_domain_movies.py --manifest manifest.csv --out downloads
```

**Command-Line Arguments:**
- `--manifest` (required): Path to the CSV manifest file
- `--out` (required): Output directory for downloaded films

**Manifest Format:**

The `manifest.csv` file uses the following columns:

```csv
title,year,source_type,source_id,query,notes
Night of the Living Dead,1968,ia_search,,Night of the Living Dead 1968,Use original not restored
```

**Columns:**
- `title`: Film title
- `year`: Release year
- `source_type`: Download method (`ia`, `ia_search`, `commons`, `direct`)
- `source_id`: Identifier or URL for the source
- `query`: Search query (for `ia_search` type)
- `notes`: Important warnings or information

**Source Types:**
- `ia`: Direct Internet Archive identifier
- `ia_search`: Search Internet Archive and download top result
- `commons`: Wikimedia Commons file title
- `direct`: Direct download URL

---

### 📚 Project Gutenberg Ebooks

Downloads top ebooks by genre from Project Gutenberg with Kavita-ready metadata.

```powershell
# Download top 20 titles from top 10 genres (default)
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaLibrary

# Download 30 titles per genre from top 15 genres
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaLibrary --count-per-genre 30 --genres-top 15

# Download specific genres only
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaLibrary --genres "Science fiction,Horror tales,Fantasy fiction"

# Adjust download speed (seconds between requests)
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaLibrary --sleep 3

# Different languages (comma-separated ISO codes)
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaLibrary --languages "en,fr,de"

# Disable collection metadata embedding
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaLibrary --no-collections
```

**Command-Line Arguments:**
- `--out`: Output library root (default: `./KavitaLibrary`)
- `--count-per-genre`: Titles per subject (default: 20)
- `--genres-top`: How many top subjects to auto-scrape (default: 10)
- `--genres`: Comma-separated subject list (overrides auto-scraping)
- `--languages`: Comma-separated language codes (default: `en`)
- `--sleep`: Seconds between downloads (default: 2.0)
- `--mirror`: Download mirror base (default: `https://gutenberg.pglaf.org`)
- `--no-collections`: Skip embedding belongs-to-collection metadata

**What it does:**
1. Scrapes popular subjects from Gutenberg's catalog
2. Queries Gutendex API for top titles per subject
3. Downloads EPUBs from mirror with polite rate limiting
4. **Removes all Project Gutenberg branding and boilerplate** from EPUB internals
5. Embeds/normalizes OPF metadata (title, author, language, subjects)
6. Adds EPUB3 collection tags for Kavita Reading Lists
7. Organizes by Series (if present) or Title folders
8. Generates `_reports/kavita_epub_report.csv` and `_reports/collections.csv`

---

### 📖 Standard Ebooks Library

Downloads the entire Standard Ebooks library with Kavita-ready metadata.

**⚠️ REQUIRES API KEY:** You must be a Standard Ebooks Patrons Circle member to access their OPDS feed.

```powershell
# Basic usage (downloads entire library)
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE

# With custom sleep interval
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --sleep 1.5

# Filter by subjects
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --subjects "Science fiction,Horror,Fantasy"

# Overwrite existing files
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --overwrite

# Custom headers/cookies (if needed)
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --header "X-Custom: value" --cookie "session=abc123"
```

**Command-Line Arguments:**
- `--api-key` (required): Your Patrons Circle API key/token
- `--opds-url`: OPDS catalog URL (default: `https://standardebooks.org/feeds/opds`)
- `--out`: Output library root (default: `./KavitaSE`)
- `--sleep`: Seconds between requests (default: 1.5)
- `--subjects`: Optional comma-separated subject filters (blank = fetch all)
- `--header`: Extra header(s) in format `Name: value` (can repeat)
- `--cookie`: Cookie(s) in format `name=value` (can repeat)
- `--overwrite`: Overwrite existing files (default: skip existing)

**What it does:**
1. Authenticates with Standard Ebooks OPDS feed
2. Follows pagination to fetch all entries
3. Downloads EPUBs with embedded metadata
4. Adds Kavita-friendly subjects and "Standard Ebooks" collection tag
5. Organizes by Series (if present) or Title folders
6. Generates `_reports/se_library_report.csv`
7. Supports resume (safely skip already-downloaded files)

## Verifying Public Domain Status

Before adding films to the manifest, verify their public domain status:

### U.S. Public Domain Rules (Simplified)
- Published before 1929: Generally in public domain
- Published 1929-1963: PD if copyright not renewed
- Published 1964-1977: May be PD depending on renewal/notice
- Published after 1977: Generally still under copyright

### Important Considerations

1. **Different Versions**: A restored version may have new copyright even if the original is PD
2. **Music Rights**: Film may be PD but soundtrack separately copyrighted
3. **Trademark Issues**: Characters/logos may be trademarked (e.g., Mickey Mouse)
4. **International Differences**: PD status varies by country

### Verification Resources
- [Internet Archive Public Domain Collections](https://archive.org/details/publicdomain)
- [Wikimedia Commons PD Category](https://commons.wikimedia.org/wiki/Category:Public_domain)
- [Stanford Copyright Renewal Database](https://collections.stanford.edu/copyrightrenewals/)
- [Cornell Public Domain Chart](https://copyright.cornell.edu/publicdomain)

---

## Output Structure & Reports

### Movies Output
Films are saved with sanitized filenames:
```
downloads/
  The_Brain_That_Wouldn_t_Die_1962.mpg
  Night_of_the_Living_Dead_1968.mp4
  _provenance.csv
```

**Provenance File** (`_provenance.csv`):
```csv
title,year,source_type,source_id,download_url,saved_as,sha256
Night of the Living Dead,1968,ia_search,night_of_the_living_dead,https://...,downloads/Night_of_the_Living_Dead_1968.mp4,abc123...
```
Use for: file integrity verification (SHA256), source documentation, audit trails

### Ebooks Output (Kavita-Ready)
Both ebook scripts organize content for Kavita media server:
```
KavitaLibrary/
  The_Time_Machine/
    The_Time_Machine - Gutenberg123.epub
  Sherlock_Holmes/
    A_Study_in_Scarlet - Gutenberg456.epub
    The_Hound_of_the_Baskervilles - Gutenberg789.epub
  _reports/
    kavita_epub_report.csv
    collections.csv
    README.txt
```

**Key Features:**
- **One folder per Series** (Kavita requirement)
- For books without series → Title becomes the series folder
- Embedded OPF metadata includes:
  - `dc:title`, `dc:creator`, `dc:language`, `dc:subject`
  - EPUB3 `belongs-to-collection` tags for Kavita Collections/Reading Lists
  - Preserves existing `calibre:series` metadata
- Reports document download status, compliance, and collection mappings

## Resale Rights

While this tool downloads public domain films, **you are responsible for verifying resale rights**:

### Safe for Resale
✅ Original public domain films without modifications
✅ Films with verified PD status in your jurisdiction
✅ Content with clear provenance documentation

### Potential Issues
⚠️ Restored versions may have restoration copyright
⚠️ Some soundtracks may be separately copyrighted
⚠️ Trademark issues with characters/branding
⚠️ Different PD status in different countries

**Always consult legal counsel if you plan to commercially distribute downloaded content.**

## Best Practices

1. **Review the Notes**: Check manifest notes for warnings about specific films
2. **Verify Independently**: Cross-reference public domain status before commercial use
3. **Keep Provenance**: Maintain the `_provenance.csv` file for documentation
4. **Respect Sources**: Don't abuse Internet Archive or other sources with excessive requests
5. **Original Versions**: Prefer original transfers over restored versions when possible
6. **Stay Updated**: PD status can change; verify current status before distribution

## Rate Limiting & Ethics

- The script includes retry logic and reasonable timeouts
- Downloads one file at a time (no parallel abuse)
- Uses 256KB chunks to avoid memory issues
- Respects source server availability

**Please be considerate of the free services provided by Internet Archive and other sources.**

---

## Troubleshooting

### Movies

**"No files for IA identifier"**
- The Internet Archive item may have been removed
- Try searching manually on archive.org to verify availability

**"No suitable downloadable file"**
- The item may only contain non-video formats
- Check the Internet Archive page for available formats

**Download timeout**
- Large files may take time; the script retries up to 3 times
- Check your internet connection
- Some IA servers may be slow; try again later

### Project Gutenberg

**"No IA search results"**
- Title/year combination may not match any items
- Try adjusting the query in manifest.csv
- Check Gutendex API manually: https://gutendex.com/books

**NONCOMPLIANT status in report**
- Project Gutenberg markers were not fully removed (rare)
- Or item not clearly flagged as PD in USA
- Review the notes column for specifics

**HTTP errors**
- Gutenberg mirror may be temporarily down
- Try again later or specify different `--mirror`

### Standard Ebooks

**401 Unauthorized**
- Invalid API key or expired Patrons Circle membership
- Check your key at https://standardebooks.org/donate#patrons-circle

**HTTP 403/404**
- OPDS feed URL may have changed
- Check Standard Ebooks website for current feed URL

**SSL/Certificate errors**
- Update Python's certifi package: `pip install --upgrade certifi`

### General

**ModuleNotFoundError: requests/lxml**
- Run: `pip install -r requirements.txt`

**Out of disk space**
- Full libraries can be 10GB+ for ebooks, much larger for movies
- Monitor disk space and adjust `--count-per-genre` or use `--subjects` filter

**Slow downloads**
- Increase `--sleep` value to be more polite to servers
- Check your internet connection speed
- Some sources throttle based on IP; wait and retry later

---

## Example Workflows

### Complete Movie Collection Setup
```powershell
# 1. Review and customize manifest
notepad manifest.csv

# 2. Download films
python public_domain_movies.py --manifest manifest.csv --out pd_movies

# 3. Verify downloads
Get-ChildItem pd_movies\*.mp4, pd_movies\*.mpg

# 4. Review provenance
Import-Csv pd_movies\_provenance.csv | Format-Table
```

### Complete Ebook Library Setup
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Download Project Gutenberg library (top 10 genres, 20 each = ~200 books)
python Project_Gutenberg_top_genres_to_kavita.py --out ./KavitaPG --sleep 2

# 3. Download Standard Ebooks library (requires API key)
python standard_ebooks_to_kavita.py --api-key YOUR_KEY --out ./KavitaSE --sleep 1.5

# 4. Check reports
Import-Csv ./KavitaPG/_reports/kavita_epub_report.csv | Where-Object {$_.status -eq "OK"} | Measure-Object
Import-Csv ./KavitaSE/_reports/se_library_report.csv | Where-Object {$_.status -eq "OK"} | Measure-Object

# 5. Point Kavita at your library folders
# In Kavita: Libraries → Add Library → Browse to KavitaPG and KavitaSE
```

### Selective Genre Download
```powershell
# Download only specific genres you want
python Project_Gutenberg_top_genres_to_kavita.py \
  --out ./KavitaLibrary \
  --genres "Science fiction,Horror tales,Detective and mystery stories,Fantasy fiction" \
  --count-per-genre 50 \
  --sleep 2
```

---

## Kavita Media Server Integration

Both ebook downloaders are optimized for **Kavita**, a free, open-source comics/ebooks/manga server.

### Why Kavita?
- Modern web-based interface
- OPDS support for reading apps
- Collections and Reading Lists
- Progress tracking across devices
- Metadata-driven organization

### Setting Up Kavita

1. **Install Kavita**: https://www.kavitareader.com/
2. **Add Library**:
   - Go to Libraries → Add Library
   - Browse to your KavitaLibrary folder
   - Set Library Type to "Book"
3. **Enable Collections** (for genre-based grouping):
   - Settings → Libraries → Manage Collections
   - Enable "Import from metadata"
4. **Scan Library**: Kavita will parse embedded OPF metadata
5. **Enjoy**: Browse by Series, Collections, or Reading Lists

### Metadata Mapping
The scripts embed metadata that Kavita automatically reads:
- `dc:title` → Chapter/Book Title
- `dc:creator` → Author(s)
- `dc:language` → Language
- `dc:subject` → Genres/Tags
- `calibre:series` → Series Name
- `calibre:series_index` → Volume Number
- `belongs-to-collection` → Collections/Reading Lists (if enabled)

---

## License & Disclaimer

These tools are provided as-is for legitimate use only. The authors are not responsible for misuse or copyright violations. Users are solely responsible for ensuring compliance with applicable laws and regulations.

**The presence of content in manifests or scripts does NOT constitute legal advice or guarantee of public domain status.** Always verify independently before commercial use.

**Project Gutenberg Compliance:** The PG script removes branding/boilerplate to comply with Project Gutenberg's [trademark policy](https://www.gutenberg.org/policy/trademark_policy.html) regarding redistribution.

**Standard Ebooks:** All SE editions are released under CC0 (public domain dedication), but API access requires Patrons Circle membership.

---

## Support & Questions

### For Script Issues
1. Verify Python 3.6+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Check your internet connection
4. Review error messages in console output
5. Check generated CSV reports for specific failures

### For Public Domain Verification
Consult the verification resources listed above or seek legal counsel.

### For Kavita Setup
- Kavita Documentation: https://wiki.kavitareader.com/
- Kavita Discord: https://discord.gg/kavita

---

## Contributing & Updates

This is a static toolset designed for archival and personal library building. To add more sources or titles:
- **Movies**: Edit `manifest.csv` with new verified PD films
- **PG Ebooks**: Adjust `--genres` or `--count-per-genre` parameters
- **SE Ebooks**: Filter by `--subjects` or download entire library

For bugs or feature requests related to the Prepper-Pi project, see the main repository.
