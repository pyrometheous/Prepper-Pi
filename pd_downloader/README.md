# Public Domain Movie Downloader

## ⚠️ IMPORTANT LEGAL NOTICE

This tool is designed **EXCLUSIVELY** for downloading public domain films from verified sources. It must **ONLY** be used for legitimate purposes of obtaining media that is free from copyright restrictions.

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

The Public Domain Movie Downloader (`pd_downloader.py`) is a Python script that downloads verified public domain films from trusted sources including:
- **Internet Archive** (archive.org) - A digital library with extensive public domain collections
- **Wikimedia Commons** - Community-verified public domain media
- **Direct URLs** - Pre-verified public domain sources

All downloads are tracked with SHA256 checksums and provenance information to ensure authenticity and traceability.

## Copyright Protection Measures

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

## How to Use

### Prerequisites

```powershell
# Python 3.6 or higher required
python --version
```

No external dependencies needed - uses only Python standard library.

### Basic Usage

```powershell
# Download films from the manifest
python pd_downloader.py --manifest manifest.csv --out downloads
```

### Command-Line Arguments

- `--manifest` (required): Path to the CSV manifest file
- `--out` (required): Output directory for downloaded films

### Manifest Format

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

## Output

### Downloaded Files
Films are saved with sanitized filenames:
```
The_Brain_That_Wouldn_t_Die_1962.mpg
Night_of_the_Living_Dead_1968.mp4
```

### Provenance File
`_provenance.csv` contains:
```csv
title,year,source_type,source_id,download_url,saved_as,sha256
Night of the Living Dead,1968,ia_search,night_of_the_living_dead,https://...,downloads/Night_of_the_Living_Dead_1968.mp4,abc123...
```

Use this file to:
- Verify file integrity (SHA256 checksums)
- Document source and public domain status
- Maintain audit trail for commercial use

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

## Troubleshooting

### "No files for IA identifier"
- The Internet Archive item may have been removed
- Try searching manually on archive.org to verify availability

### "No suitable downloadable file"
- The item may only contain non-video formats
- Check the Internet Archive page for available formats

### Download timeout
- Large files may take time; the script retries up to 3 times
- Check your internet connection
- Some IA servers may be slow; try again later

## Example Workflow

```powershell
# 1. Review and customize manifest.csv
notepad manifest.csv

# 2. Create output directory
mkdir pd_movies

# 3. Download films (this may take hours for many films)
python pd_downloader.py --manifest manifest.csv --out pd_movies

# 4. Verify downloads
Get-ChildItem pd_movies\*.mp4, pd_movies\*.mpg

# 5. Review provenance
Import-Csv pd_movies\_provenance.csv | Format-Table
```

## License & Disclaimer

This tool is provided as-is for legitimate use only. The authors are not responsible for misuse or copyright violations. Users are solely responsible for ensuring compliance with applicable laws and regulations.

**The presence of a film in the manifest does NOT constitute legal advice or guarantee of public domain status.** Always verify independently before commercial use.

---

## Support & Questions

For issues specific to this downloader, check:
1. Manifest format is correct
2. Python 3.6+ is installed
3. Internet connection is stable
4. Source URLs are still valid

For public domain verification questions, consult the verification resources listed above or seek legal counsel.
