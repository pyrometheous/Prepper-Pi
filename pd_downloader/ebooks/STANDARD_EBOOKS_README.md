# Standard Ebooks Library Downloader

> ⚠️ **WORK IN PROGRESS** - This tool is actively being developed. There is no guarantee that anything will work as expected. Use at your own risk.

---

## Table of Contents

- [Legal Notice](#️-important-legal-notice)
- [Overview & Features](#overview)
- [Installation](#prerequisites)
- [Usage Examples](#usage)
- [Command-Line Reference](#command-line-arguments)
- [Kavita Integration](#kavita-integration)
- [About Standard Ebooks](#about-standard-ebooks)
- [Troubleshooting](#troubleshooting)

---

## Navigation

- 🏠 **[Main README](../README.md)** - Overview of all downloaders
- 🎵 **[Music README](../music/README.md)** - Public domain music
- 📽️ **[Movies README](../movies/README.md)** - Public domain films
- 📚 **[Gutenberg README](GUTENBERG_README.md)** - Project Gutenberg ebooks

---

## ⚠️ IMPORTANT LEGAL NOTICE

### Acceptable Use
- ✅ Downloading Standard Ebooks library (requires Patrons Circle membership)
- ✅ Building personal or commercial collections
- ✅ Educational and archival purposes
- ✅ Modifying and redistributing (all editions are CC0)

### Prohibited Use
- ❌ Sharing API keys or credentials
- ❌ Downloading without Patrons Circle membership
- ❌ Abusing the OPDS feed with excessive requests

### Standard Ebooks License

**All Standard Ebooks editions are released under CC0** (Creative Commons Zero / Public Domain Dedication). This means:
- ✅ Free to use for any purpose
- ✅ Free to modify and create derivatives
- ✅ Free to redistribute commercially
- ✅ No attribution required (though appreciated)

However, **OPDS feed access requires** a Patrons Circle membership at the appropriate price bracket to support the project.

---

## Overview

Download the entire **Standard Ebooks** library with Kavita-ready metadata. Standard Ebooks provides beautifully formatted, professionally edited public domain ebooks with modern typography and thoughtful design.

All Standard Ebooks editions are released under **CC0** (public domain dedication), making them free to use, share, and modify for any purpose.

---

## Prerequisites

### 1. Patrons Circle Membership (Required)

**⚠️ REQUIRES API KEY:** You must be a Standard Ebooks Patrons Circle member to access their OPDS feed.

- **Sign up**: [Become a patron](https://standardebooks.org/donate#patrons-circle)
- **Minimum tier**: $5/month or $50/year (this may be out of date)
- **Benefits**: OPDS feed access, support quality public domain ebooks

After signing up, you'll receive an API key/token for accessing the OPDS feed. (verify on their website directly, this information may be out of date or inaccurate)

### 2. Python Requirements

```powershell
# Python 3.8 or higher
python --version

# Install dependencies
cd c:\Users\Delgado\VSCode\Prepper-Pi\pd_downloader\ebooks
pip install -r requirements.txt
```

**Dependencies installed:**
- `requests>=2.31.0` - HTTP operations
- `lxml>=4.9.0` - EPUB/XML processing

---

## Usage

### Basic Usage

```powershell
# Download entire Standard Ebooks library
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE
```

This will:
1. Authenticate with Standard Ebooks OPDS feed
2. Follow pagination to fetch all entries (~600+ books)
3. Download EPUBs with embedded metadata
4. Add Kavita-friendly subjects and "Standard Ebooks" collection tag
5. Organize by Series (if present) or Title folders
6. Generate `_reports/se_library_report.csv`
7. Support resume (safely skip already-downloaded files)

### Advanced Examples

```powershell
# Custom sleep interval (be polite to servers)
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --sleep 2.0

# Filter by specific subjects
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --subjects "Science fiction,Horror,Fantasy"

# Overwrite existing files (default: skip existing)
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --overwrite

# Custom headers/cookies (if needed)
python standard_ebooks_to_kavita.py --api-key YOUR_API_KEY --out ./KavitaSE --header "X-Custom: value" --cookie "session=abc123"
```

### Command-Line Arguments

**Required:**
- `--api-key` - Your Patrons Circle API key/token

**Optional:**
- `--opds-url` - OPDS catalog URL (default: `https://standardebooks.org/feeds/opds`)
- `--out` - Output library root (default: `./KavitaSE`)
- `--sleep` - Seconds between requests (default: 1.5)
- `--subjects` - Comma-separated subject filters (blank = fetch all)
- `--header` - Extra header(s) in format `Name: value` (can repeat)
- `--cookie` - Cookie(s) in format `name=value` (can repeat)
- `--overwrite` - Overwrite existing files (default: skip existing)

---

## What This Script Does

1. **Authenticates** with Standard Ebooks OPDS feed using your API key
2. **Fetches catalog** - Follows pagination to get all book entries
3. **Filters** (optional) - By subject if `--subjects` specified
4. **Downloads EPUBs** - From Standard Ebooks CDN with polite rate limiting
5. **Embeds metadata** - Adds Kavita-friendly collection and subject tags
6. **Organizes files** - Creates Series/Title folder structure for Kavita
7. **Generates reports** - CSV file documenting all downloads
8. **Resumes safely** - Skips already-downloaded files (unless `--overwrite`)

---

## Output Structure

Books are organized in Kavita-ready folder structure:

```
KavitaSE/
  Pride_and_Prejudice/
    Pride_and_Prejudice - StandardEbooks.epub
  Sherlock_Holmes/
    A_Study_in_Scarlet - StandardEbooks.epub
    The_Sign_of_the_Four - StandardEbooks.epub
  _reports/
    se_library_report.csv
    README.txt
```

### Features

- **One folder per Series** - Kavita requirement for proper organization
- **Books without series** - Title becomes the folder name
- **Embedded metadata** includes:
  - Title, authors, language, subjects
  - "Standard Ebooks" collection tag
  - Existing series information preserved
- **Reports** document download status and file locations

---

## Kavita Integration

### Why Kavita?

Standard Ebooks downloader is optimized for **Kavita**, a free, open-source ebook server:

- Modern web-based interface
- OPDS support for reading apps
- Collections and Reading Lists
- Progress tracking across devices
- Metadata-driven organization

### Setting Up Kavita

1. **Install Kavita**: https://www.kavitareader.com/
2. **Add Library**:
   - Go to Libraries → Add Library
   - Browse to your `KavitaSE` folder
   - Set Library Type to "Book"
3. **Enable Collections**:
   - Settings → Libraries → Manage Collections
   - Enable "Import from metadata"
4. **Scan Library**: Kavita will parse embedded OPF metadata
5. **Browse**: By Series, Collections ("Standard Ebooks"), or Reading Lists

### Metadata Mapping

The script embeds metadata that Kavita automatically reads:

- `dc:title` → Book Title
- `dc:creator` → Author(s)
- `dc:language` → Language
- `dc:subject` → Genres/Tags
- `calibre:series` → Series Name
- `calibre:series_index` → Volume Number
- `belongs-to-collection` → "Standard Ebooks" (for Kavita Collections)

---

## About Standard Ebooks

### What Makes Standard Ebooks Special?

- **Modern typography** - Professional book design principles
- **Semantic markup** - Proper HTML5 semantic elements
- **Accessibility** - Screen reader friendly, high-quality metadata
- **Consistent quality** - Every book hand-edited by volunteers
- **Beautiful covers** - Original artwork for each edition
- **Free forever** - CC0 public domain dedication

### Collection Size

- **600+ books** and growing
- Focus on English-language classics
- Includes fiction, non-fiction, poetry, drama
- Regular new releases (several per month)

### Quality Standards

All Standard Ebooks editions include:
- Modern, readable typography
- Corrected OCR errors from original scans
- Semantic HTML5 markup
- Proper metadata and subject tags
- High-resolution cover art
- Thoughtful design choices

---

## Rate Limiting & Ethics

- Default 1.5 second delay between requests (configurable with `--sleep`)
- Downloads sequentially (no parallel abuse)
- Respects server availability
- Skips existing files by default (resume capability)

**Please be considerate** of Standard Ebooks' bandwidth and infrastructure. They provide this service through donations and volunteer work.

---

## Troubleshooting

### Authentication Issues

**401 Unauthorized**
- Invalid API key or expired Patrons Circle membership
- Check your key at https://standardebooks.org/donate#patrons-circle
- Verify you copied the complete key (no extra spaces)

**403 Forbidden**
- API key may be rate-limited or suspended
- Contact Standard Ebooks support

### Download Issues

**HTTP 404 Not Found**
- Book may have been removed or URL changed
- Check Standard Ebooks website to verify book exists
- Try again later (temporary CDN issue)

**SSL/Certificate Errors**
- Update Python's certifi package: `pip install --upgrade certifi`
- Check system time is correct

**Connection Timeouts**
- Increase sleep time: `--sleep 3`
- Check your internet connection
- Try again during off-peak hours

### General Issues

**ModuleNotFoundError: requests/lxml**
- Run: `pip install -r requirements.txt`
- Ensure you're in the correct directory

**Out of disk space**
- Full library is ~2-3GB
- Monitor disk space before starting
- Use `--subjects` filter to download selectively

**Slow downloads**
- Increase `--sleep` value to be more polite
- Check internet connection speed
- Standard Ebooks may throttle based on IP

---

## Performance Tips

1. **Use `--subjects` filter** to download only genres you want
2. **Keep existing files** - Script skips them automatically (fast resume)
3. **Adjust `--sleep`** based on your network (0.5-3 seconds recommended)
4. **Run overnight** for full library (takes 1-2 hours at 1.5s delay)

---

## Example Workflows

### Complete Library Download

```powershell
# Download everything (600+ books, ~2-3GB, 1-2 hours)
python standard_ebooks_to_kavita.py --api-key YOUR_KEY --out ./KavitaSE

# Check report
Import-Csv ./KavitaSE/_reports/se_library_report.csv | Where-Object {$_.status -eq "OK"} | Measure-Object

# Point Kavita at library
# In Kavita: Libraries → Add Library → Browse to KavitaSE
```

### Selective Genre Download

```powershell
# Download only specific subjects
python standard_ebooks_to_kavita.py \
  --api-key YOUR_KEY \
  --out ./KavitaSE \
  --subjects "Science fiction,Horror,Fantasy,Adventure" \
  --sleep 2
```

### Update Existing Library

```powershell
# Resume/update - only downloads new books
python standard_ebooks_to_kavita.py --api-key YOUR_KEY --out ./KavitaSE

# The script automatically skips existing files
```

---

## License & Disclaimer

This tool is provided as-is for legitimate use only. Users are solely responsible for ensuring compliance with applicable laws and Standard Ebooks' terms of service.

**Standard Ebooks License:** All SE editions are released under CC0 (public domain dedication), meaning they are free to use, share, and modify for any purpose. However, OPDS feed access requires Patrons Circle membership.

**Support Standard Ebooks:** Consider maintaining your Patrons Circle membership even after downloading to support their ongoing work producing high-quality public domain ebooks.

---

## Support & Resources

### Standard Ebooks
- Website: https://standardebooks.org/
- Donate/Patrons Circle: https://standardebooks.org/donate
- Manual catalog: https://standardebooks.org/ebooks

### Kavita
- Documentation: https://wiki.kavitareader.com/
- Discord: https://discord.gg/kavita
- Website: https://www.kavitareader.com/

### Script Issues
1. Verify Python 3.8+ installed
2. Install dependencies: `pip install -r requirements.txt`
3. Check your internet connection
4. Verify API key is valid
5. Review error messages in console output
6. Check generated CSV report for specific failures
