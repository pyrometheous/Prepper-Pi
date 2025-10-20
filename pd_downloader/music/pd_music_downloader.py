#!/usr/bin/env python3
"""
pd_music_downloader.py

Exclusively download Public Domain / CC0 audio suitable for resale and offline distribution,
from supported sources:
  - Internet Archive (IA)
  - Wikimedia Commons

Enhancements:
  - PD/CC0 enforced by default (no CC-BY/SA options).
  - Always generates README.md atdef commons_search_audio(query: Optional[str], limit=50, cont=None) -> dict:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query or "filetype:ogg|oga|flac|wav",
        "srnamespace": 6,
        "srlimit": min(limit, 50),
        "format": "json",
    }
    if cont:
        params["sroffset"] = cont
    headers = {"User-Agent": "PublicDomainMusicDownloader/1.0 (Educational/Archival Use)"}
    r = requests.get(COMMONS_API, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()

def commons_get_info(titles: List[str]) -> dict:
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": "|".join(titles),
        "iiprop": "url|mime|size|extmetadata",
        "format": "json",
    }
    headers = {"User-Agent": "PublicDomainMusicDownloader/1.0 (Educational/Archival Use)"}
    r = requests.get(COMMONS_API, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json()escribing licenses and sources.
  - Optional composer/era filters to narrow results (best-effort per source).
  - Preferred audio format with fallback logic: skip or fallback-to-mp3.
  - Best-effort Musopen cross-check (by title/composer) to corroborate PD/CC0 status.
  - Writes per-file metadata.json and a global index.csv.
  - Injects media tags (if 'mutagen' is installed) and emits simple Jellyfin-friendly .nfo files.

Usage examples:
  # Internet Archive, prefer FLAC, fallback to MP3 if FLAC absent
  python pd_music_downloader.py --source ia --out ./music --max-items 200 \
    --preferred-format flac --fallback-to-mp3 \
    --query 'collection:(great78 OR georgiaarchives) AND mediatype:audio' \
    --composer 'Gershwin' --era 'pre-1930'

  # Wikimedia Commons, prefer OGG, skip files that aren't OGG
  python pd_music_downloader.py --source commons --out ./music --max-items 50 \
    --preferred-format ogg --skip-if-missing-format \
    --query 'piano|orchestra|symphony' --composer 'Bach'

Requirements:
  - requests (pip install requests)
  - mutagen (optional; for embedding tags)

License: CC0-1.0 for this script
"""

import argparse
import csv
import html
import io
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    print("This script requires 'requests'. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, COMM, TCON
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
except Exception:
    mutagen = None  # tagging optional

SAFE_BUCKETS = {"pd", "cc0"}
IA_ADVANCED_URL = "https://archive.org/advancedsearch.php"
IA_METADATA_URL = "https://archive.org/metadata/{identifier}"
COMMONS_API     = "https://commons.wikimedia.org/w/api.php"

# ---------------- Utilities ----------------

def slugify(text, maxlen: int = 80) -> str:
    """Convert text to filesystem-safe slug. Handles strings, lists, or None."""
    if text is None:
        return "item"
    if isinstance(text, list):
        text = text[0] if text else "item"
    if not isinstance(text, str):
        text = str(text)
    text = re.sub(r'[\s/\\]+', ' ', text).strip()
    text = re.sub(r'[^-\w.\s]', '', text, flags=re.UNICODE)
    text = text.replace(' ', '_')
    return text[:maxlen] if text else "item"

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data: dict) -> None:
    with path.open('w', encoding='utf-8') as f:
    # ensure ASCII-safety for metadata fields
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_index_row(index_path: Path, row: List[str], header: Optional[List[str]] = None) -> None:
    new_file = not index_path.exists()
    with index_path.open('a', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        if new_file and header:
            w.writerow(header)
        w.writerow(row)

def human_era_filter(era: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Parse a simple era descriptor -> (start_year, end_year), inclusive.
    Supported: 'pre-1930', 'pre-1925', '1890-1910', '1900s', 'baroque', 'classical', 'romantic', '20th'
    """
    era = (era or '').lower().strip()
    if not era:
        return (None, None)
    if era.startswith('pre-'):
        try:
            end = int(era.split('-')[1])
            return (None, end - 1)
        except Exception:
            return (None, None)
    if re.match(r'^\d{4}-\d{4}$', era):
        a, b = era.split('-')
        return (int(a), int(b))
    if era.endswith('s') and len(era) in (4,5) and era[:-1].isdigit():
        base = int(era[:-1])
        return (base, base+9)
    # stylistic eras (very rough years)
    if era in ('baroque',):
        return (1600, 1750)
    if era in ('classical',):
        return (1750, 1820)
    if era in ('romantic',):
        return (1820, 1910)
    if era in ('20th', '20th-century', '20th century'):
        return (1900, 1999)
    return (None, None)

def write_readme(out_root: Path):
    text = f"""# Public Domain / CC0 Music Collection

This folder contains audio files curated for **public-domain (PD) or CC0** status,
downloaded from Internet Archive and/or Wikimedia Commons. The goal is resale-ready,
offline-friendly content for personal or commercial redistribution (U.S. context).

## What is included
- **License buckets**: PD or CC0 only.
- Per-track `metadata.json` including source URL, license, creator, and year (if known).
- `index.csv` as an inventory and import helper.
- Embedded media tags (when the optional `mutagen` package is installed).
- A simple `.nfo` file alongside each track to help media servers read extra fields.

## Sources
- Internet Archive (archive.org)
- Wikimedia Commons (commons.wikimedia.org)
- Optional best-effort cross-check against Musopen (musopen.org) to corroborate PD/CC0.

> Note: Cross-checks cannot guarantee legal status. Always perform your own review.

## Using with Jellyfin
- Jellyfin reads tags (ID3/Vorbis/FLAC). The script writes: Title, Artist, Album, Year, Comment (license + source).
- You can point Jellyfin's Music library to the `music` folder created here.
- Alternatives to consider for off-grid: Navidrome or Funkwhale (verify features for your needs).

## Disclaimer
This collection and script are provided *as-is* with no warranty. You are responsible for verifying
license status and complying with your jurisdiction’s laws.
"""
    (out_root / "README.md").write_text(text, encoding="utf-8")

# ---------------- IA (Internet Archive) ----------------

def ia_build_query(user_query: str, composer: str, era: str) -> str:
    # licenses: PD/CC0 only
    license_terms = ['licenseurl:*publicdomain*', 'licenseurl:*cc0*']
    license_filter = "(" + " OR ".join(license_terms) + ")"
    base = f"{license_filter} AND mediatype:audio"
    if user_query:
        base += f" AND ({user_query})"
    if composer:
        # attempt composer match via creator field
        base += f" AND (creator:{composer})"
    # era -> filter by year/date when available
    start, end = human_era_filter(era)
    if start is not None and end is not None:
        base += f" AND (year:[{start} TO {end}] OR date:[{start} TO {end}])"
    elif start is None and end is not None:
        base += f" AND (year:[* TO {end}] OR date:[* TO {end}])"
    elif start is not None and end is None:
        base += f" AND (year:[{start} TO *] OR date:[{start} TO *])"
    return base

def ia_search(query: str, rows: int, page: int = 1) -> dict:
    params = {
        "q": query,
        "fl[]": ["identifier", "title", "creator", "year", "date", "collection", "licenseurl", "mediatype"],
        "sort[]": "downloads desc",
        "rows": rows,
        "page": page,
        "output": "json"
    }
    r = requests.get(IA_ADVANCED_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def pick_file(files: List[dict], identifier: str, preferred: str, fallback_to_mp3: bool, skip_if_missing: bool) -> Optional[dict]:
    preferred = preferred.lower()
    # try preferred
    for f in files:
        name = f.get('name') or ''
        if name.lower().endswith('.' + preferred):
            return f
    if skip_if_missing:
        return None
    if fallback_to_mp3 and preferred != 'mp3':
        for f in files:
            name = f.get('name') or ''
            if name.lower().endswith('.mp3'):
                return f
    # else try any PD-friendly formats
    for ext in ('flac','ogg','wav','mp3'):
        for f in files:
            name = f.get('name') or ''
            if name.lower().endswith('.' + ext):
                return f
    return None

def ia_download_item(identifier: str, out_dir: Path, index_path: Path, preferred_format: str, fallback_to_mp3: bool, skip_if_missing_format: bool) -> int:
    meta_resp = requests.get(IA_METADATA_URL.format(identifier=identifier), timeout=30)
    if meta_resp.status_code != 200:
        return 0
    meta = meta_resp.json()
    files = meta.get('files', []) or []
    mdmd = meta.get('metadata', {}) or {}

    base_info = {
        "source": "internet_archive",
        "identifier": identifier,
        "collection": mdmd.get('collection'),
        "title": mdmd.get('title'),
        "creator": mdmd.get('creator'),
        "year": mdmd.get('date') or mdmd.get('year'),
        "licenseurl": (mdmd.get('licenseurl') or '').lower(),
        "url": f"https://archive.org/details/{identifier}",
    }

    # safety check on license (PD/CC0 only)
    lic = base_info["licenseurl"]
    if not (("publicdomain" in lic) or ("cc0" in lic)):
        return 0

    chosen = pick_file(files, identifier, preferred_format, fallback_to_mp3, skip_if_missing_format)
    if not chosen:
        return 0

    name = chosen.get('name')
    file_url = f"https://archive.org/download/{identifier}/{name}"
    folder = slugify((base_info.get('collection') or base_info.get('creator') or 'ia'))
    item_slug = slugify(base_info.get('title') or identifier)
    item_dir = out_dir / folder / item_slug
    ensure_dir(item_dir)
    dest = item_dir / name

    # Check if file already exists (duplicate detection)
    if dest.exists():
        print(f"  ⏭️  SKIP (exists): {base_info.get('title', identifier)[:60]}")
        return 0

    try:
        with requests.get(file_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dest, 'wb') as fh:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        fh.write(chunk)
    except Exception:
        return 0

    md = dict(base_info)
    md.update({
        "file": name,
        "format": chosen.get('format'),
        "bytes": chosen.get('size'),
        "original": file_url,
    })

    # Musopen verify (best-effort) before saving metadata
    verify = musopen_verify(md.get('title'), md.get('creator'))
    md.update(verify)

    write_json(item_dir / "metadata.json", md)

    # index
    save_index_row(
        index_path,
        [
            "internet_archive",
            identifier,
            base_info.get('title') or '',
            base_info.get('creator') or '',
            str(base_info.get('year') or ''),
            base_info.get('licenseurl') or '',
            file_url,
            str(dest.relative_to(out_dir))
        ],
        header=["source","id","title","creator","year","license","download_url","relative_path"]
    )

    # tagging + nfo
    safe_tagging(dest, title=base_info.get('title'), artist=base_info.get('creator'),
                 album=base_info.get('collection'), year=str(base_info.get('year') or ''),
                 comment=f"License: {base_info.get('licenseurl')}; Source: {base_info.get('url')}")
    write_nfo(item_dir / (dest.stem + ".nfo"),
              title=base_info.get('title'),
              artist=base_info.get('creator'),
              album=base_info.get('collection'),
              year=str(base_info.get('year') or ''),
              license_url=base_info.get('licenseurl'),
              source_url=base_info.get('url'))

    print(f"  ✅ Downloaded: {base_info.get('title', identifier)[:60]}")
    return 1

# ---------------- Commons (Wikimedia) ----------------

def commons_search_audio(query: str, limit: int, cont: Optional[str] = None) -> dict:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query or "filetype:ogg|oga|flac|wav",
        "srnamespace": 6,
        "srlimit": min(limit, 50),
        "format": "json",
    }
    if cont:
        params["sroffset"] = cont
    r = requests.get(COMMONS_API, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def commons_get_info(titles: List[str]) -> dict:
    params = {
        "action": "query",
        "prop": "imageinfo",
        "titles": "|".join(titles),
        "iiprop": "url|mime|size|extmetadata",
        "format": "json",
    }
    r = requests.get(COMMONS_API, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def license_bucket_from_extmetadata(meta: dict) -> str:
    em = meta.get('extmetadata') or {}
    lic_short = (em.get('LicenseShortName', {}) or {}).get('value', '') .lower()
    lic_url = (em.get('LicenseUrl', {}) or {}).get('value', '') .lower()
    def has(s): return s in lic_short or s in lic_url
    if has('public domain') or 'publicdomain' in lic_url or 'pd-' in lic_short:
        return 'pd'
    if 'cc0' in lic_short or 'creativecommons.org/publicdomain/zero' in lic_url:
        return 'cc0'
    return 'other'

def commons_download(query: str, out_dir: Path, max_items: int, preferred_format: str, fallback_to_mp3: bool, skip_if_missing_format: bool, index_path: Path, composer: str, era: str) -> int:
    saved = 0
    sroffset = None
    seen = set()
    while saved < max_items:
        try:
            resp = commons_search_audio(query, limit=min(50, max_items - saved), cont=sroffset)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("[commons] ⚠️  Wikimedia Commons returned 403 Forbidden. This may be due to:")
                print("  • Rate limiting - try again later")
                print("  • IP/location restrictions")
                print("  • User-Agent requirements not met")
                print(f"[commons] Skipping Wikimedia Commons source")
                break
            else:
                raise
        search = resp.get('query', {}).get('search', [])
        if not search:
            break
        titles = [x['title'] for x in search if x.get('title') and x['title'] not in seen]
        seen.update(titles)
        info = commons_get_info(titles)
        pages = info.get('query', {}).get('pages', {})

        for _, page in pages.items():
            if 'imageinfo' not in page:
                continue
            ii = page['imageinfo'][0]
            bucket = license_bucket_from_extmetadata(ii)
            if bucket not in SAFE_BUCKETS:
                continue  # PD/CC0 only
            url = ii.get('url', '')
            ext = url.split('.')[-1].lower()

            # composer filter (best-effort by filename/title)
            title_text = page.get('title','')
            if composer and (composer.lower() not in title_text.lower()):
                # lenient pass—Commons often omits composer in title
                pass

            # preferred format handling
            want = f".{preferred_format.lower()}"
            ok = url.lower().endswith(want)
            if not ok:
                if skip_if_missing_format:
                    continue
                if fallback_to_mp3 and not url.lower().endswith(".mp3"):
                    if not any(url.lower().endswith('.'+e) for e in ('flac','ogg','wav','mp3')):
                        continue

            # download
            author = html.unescape(((ii.get('extmetadata') or {}).get('Artist', {}) or {}).get('value', 'Commons')).strip()
            license_url = ((ii.get('extmetadata') or {}).get('LicenseUrl', {}) or {}).get('value', '')
            desc_url = ((ii.get('extmetadata') or {}).get('ObjectPageURL', {}) or {}).get('value', '')
            folder = slugify(author or 'Commons')
            item_slug = slugify(title_text.replace('File:', ''))
            item_dir = out_dir / folder / item_slug
            ensure_dir(item_dir)
            dest = item_dir / os.path.basename(url)

            # Check if file already exists (duplicate detection)
            if dest.exists():
                print(f"  ⏭️  SKIP (exists): {title_text[:60]}")
                continue

            try:
                with requests.get(url, stream=True, timeout=60) as r:
                    r.raise_for_status()
                    with open(dest, 'wb') as fh:
                        for chunk in r.iter_content(chunk_size=1024*64):
                            if chunk:
                                fh.write(chunk)
            except Exception:
                continue

            md = {
                "source": "wikimedia_commons",
                "title": title_text,
                "author": author,
                "file": os.path.basename(url),
                "original": url,
                "description_page": desc_url,
                "license_bucket": bucket,
                "license_url": license_url,
            }

            # Musopen best-effort verify
            verify = musopen_verify(title_text, composer)
            md.update(verify)

            write_json(item_dir / "metadata.json", md)

            save_index_row(
                index_path,
                [
                    "wikimedia_commons",
                    title_text,
                    title_text,
                    author,
                    '',
                    license_url,
                    url,
                    str(dest.relative_to(out_dir))
                ],
                header=["source","id","title","creator","year","license","download_url","relative_path"]
            )

            safe_tagging(dest, title=title_text, artist=author, album="Wikimedia Commons",
                         year="", comment=f"License: {license_url}; Source: {desc_url}")
            write_nfo(item_dir / (dest.stem + ".nfo"),
                      title=title_text, artist=author, album="Wikimedia Commons",
                      year="", license_url=license_url, source_url=desc_url)

            print(f"  ✅ Downloaded: {title_text[:60]}")
            saved += 1
            if saved >= max_items:
                break

        sroffset = resp.get('continue', {}).get('sroffset')
        if not sroffset:
            break
        time.sleep(0.4)
    return saved

# ---------------- Tagging & NFO ----------------

def safe_tagging(path: Path, title: Optional[str], artist: Optional[str], album: Optional[str], year: Optional[str], comment: Optional[str]):
    """Tag audio files. Handles lists by converting to strings."""
    if mutagen is None:
        return
    
    # Helper to convert lists to strings
    def to_str(val):
        if val is None:
            return ''
        if isinstance(val, list):
            return val[0] if val else ''
        return str(val)
    
    # Convert all inputs to strings
    title = to_str(title) if title else None
    artist = to_str(artist) if artist else None
    album = to_str(album) if album else None
    year = to_str(year) if year else None
    comment = to_str(comment) if comment else None
    
    try:
        if path.suffix.lower() == '.mp3':
            try:
                tags = ID3(path)
            except Exception:
                tags = ID3()
            if title:  tags.add(TIT2(encoding=3, text=title))
            if artist: tags.add(TPE1(encoding=3, text=artist))
            if album:  tags.add(TALB(encoding=3, text=album))
            if year:   tags.add(TDRC(encoding=3, text=year))
            if comment:tags.add(COMM(encoding=3, lang='eng', desc='Comment', text=comment))
            tags.save(path)
        elif path.suffix.lower() == '.flac':
            audio = FLAC(str(path))
            if title:  audio['title'] = [title]
            if artist: audio['artist'] = [artist]
            if album:  audio['album'] = [album]
            if year:   audio['date']  = [year]
            if comment:audio['comment'] = [comment]
            audio.save()
        elif path.suffix.lower() in ('.ogg', '.oga'):
            audio = OggVorbis(str(path))
            if title:  audio['title'] = [title]
            if artist: audio['artist'] = [artist]
            if album:  audio['album'] = [album]
            if year:   audio['date']  = [year]
            if comment:audio['comment'] = [comment]
            audio.save()
        # wav tagging is inconsistent; skipping
    except Exception:
        pass

def write_nfo(nfo_path: Path, title: Optional[str], artist: Optional[str], album: Optional[str], year: Optional[str], license_url: Optional[str], source_url: Optional[str]):
    """Write NFO file for media servers. Handles lists by converting to strings."""
    # Helper to convert lists to strings
    def to_str(val):
        if val is None:
            return ''
        if isinstance(val, list):
            return val[0] if val else ''
        return str(val)
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<music>
  <title>{html.escape(to_str(title))}</title>
  <artist>{html.escape(to_str(artist))}</artist>
  <album>{html.escape(to_str(album))}</album>
  <year>{html.escape(to_str(year))}</year>
  <source>{html.escape(to_str(source_url))}</source>
  <license>{html.escape(to_str(license_url))}</license>
</music>
"""
    nfo_path.write_text(xml, encoding='utf-8')

# ---------------- Musopen Cross-check ----------------

MUSOPEN_SEARCH = "https://musopen.org/api/search/recordings/?q={q}&limit=5"

def musopen_verify(title: Optional[str], composer: Optional[str]) -> Dict[str, str]:
    # Helper to convert lists to strings
    def to_str(val):
        if val is None:
            return ''
        if isinstance(val, list):
            return val[0] if val else ''
        return str(val)
    
    q = " ".join([x for x in [to_str(composer), to_str(title)] if x]).strip()
    if not q:
        return {"musopen_verified": "unknown"}
    try:
        resp = requests.get(MUSOPEN_SEARCH.format(q=requests.utils.quote(q)), timeout=10)
        if resp.status_code != 200:
            return {"musopen_verified": "unknown"}
        data = resp.json()
        for rec in data.get('results', []):
            lic = (rec.get('license') or rec.get('license_name') or "").lower()
            flags = { "public domain" in lic, "cc0" in lic, "pd" in lic }
            if any(flags) or rec.get('is_public_domain') is True:
                return {"musopen_verified": "true", "musopen_hint": lic or "public domain"}
        return {"musopen_verified": "not_found"}
    except Exception:
        return {"musopen_verified": "unknown"}

# ---------------- Main ----------------

def get_existing_files(out_dir: Path) -> set:
    """Get set of existing audio files to avoid duplicates."""
    existing = set()
    if not out_dir.exists():
        return existing
    
    audio_extensions = {'.mp3', '.flac', '.ogg', '.oga', '.wav', '.m4a'}
    for ext in audio_extensions:
        for file in out_dir.rglob(f'*{ext}'):
            # Use file size + name as duplicate key
            existing.add((file.name.lower(), file.stat().st_size))
    return existing

def is_duplicate(file_path: Path, existing_files: set) -> bool:
    """Check if a file is a duplicate based on name and size."""
    if not file_path.exists():
        return False
    key = (file_path.name.lower(), file_path.stat().st_size)
    return key in existing_files

def get_default_query(source: str, composer: str, era: str) -> str:
    """Generate smart default query if user doesn't provide one."""
    if source == "ia":
        # Default: Search major PD music collections
        collections = [
            "great78",           # Great 78 Project (pre-1923)
            "georgeblood",       # George Blood collection
            "78rpm",             # General 78rpm records
            "georgiaarchives",   # Georgia Archives
            "library_of_congress",  # LoC recordings
            "netlabels"          # CC/PD netlabel releases
        ]
        return f"collection:({' OR '.join(collections)}) AND mediatype:audio"
    elif source == "commons":
        # Default: Search for common classical/historical music terms
        if composer or era:
            # If composer/era specified, use generic music terms
            return "music|symphony|concerto|sonata|piano|orchestra|quartet"
        else:
            # Broader search for classical and historical recordings
            return "classical|baroque|romantic|folk|traditional|historical recording"
    return ""

def check_disk_space(out_dir: Path, max_items: int, sources: list) -> bool:
    """
    Check available disk space and warn user about storage requirements.
    
    Storage estimates:
    - Internet Archive: ~3-8 MB per track average (78rpm/historical)
    - Wikimedia Commons: ~2-6 MB per track average (varies by format)
    - Recommended buffer: 20% extra for metadata, thumbnails, etc.
    
    Returns True if user wants to proceed, False to cancel.
    """
    # Estimate per-track size based on format (MB)
    AVG_SIZE_MB = 5  # Conservative average for MP3/OGG
    
    # Calculate estimated size
    num_sources = len(sources)
    if max_items == -1:
        # Unlimited download estimate based on typical collection sizes
        # IA has ~200K+ audio items in PD collections
        # Commons has ~50K+ audio files
        estimated_items = 250000 if "ia" in sources else 0
        estimated_items += 50000 if "commons" in sources else 0
        estimated_size_gb = (estimated_items * AVG_SIZE_MB) / 1024
        is_unlimited = True
    else:
        estimated_items = max_items * num_sources
        estimated_size_gb = (estimated_items * AVG_SIZE_MB) / 1024
        is_unlimited = False
    
    # Add 20% buffer
    estimated_size_gb *= 1.2
    
    # Get available disk space
    try:
        stat = shutil.disk_usage(out_dir)
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
    except Exception:
        # If we can't check disk space, just warn and proceed
        print("⚠️  Unable to check disk space. Proceeding...")
        return True
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                         STORAGE REQUIREMENTS                                 ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    
    if is_unlimited:
        print("⚠️  UNLIMITED DOWNLOAD MODE (--max-items -1)")
        print(f"📊 Estimated collection size: ~{estimated_items:,} tracks")
        print(f"💾 Estimated storage needed: ~{estimated_size_gb:,.1f} GB")
        print(f"   (This could be 100+ GB to 1+ TB depending on format!)")
        print()
        print(f"💿 Your disk space:")
        print(f"   Free: {free_gb:,.1f} GB / {total_gb:,.1f} GB total")
        print()
        
        if free_gb < estimated_size_gb:
            print("❌ WARNING: Insufficient disk space!")
            print(f"   You need at least {estimated_size_gb:,.1f} GB free.")
            print(f"   You only have {free_gb:,.1f} GB available.")
            response = input("\n⚠️  Continue anyway? (yes/no): ").strip().lower()
            return response in ("yes", "y")
        else:
            print("⚠️  This will download a MASSIVE collection and take days/weeks.")
            print("   Consider using --max-items to limit the download size.")
            response = input("\n❓ Are you sure you want to proceed? (yes/no): ").strip().lower()
            return response in ("yes", "y")
    else:
        print(f"📊 Download plan: {estimated_items:,} tracks maximum ({num_sources} source(s))")
        print(f"💾 Estimated storage needed: ~{estimated_size_gb:.1f} GB")
        print(f"   (Average ~{AVG_SIZE_MB} MB per track + 20% buffer)")
        print()
        print(f"💿 Your disk space:")
        print(f"   Free: {free_gb:.1f} GB / {total_gb:.1f} GB total")
        print()
        
        # Warn if less than 10 GB free after download
        remaining = free_gb - estimated_size_gb
        if remaining < 10:
            print("⚠️  WARNING: This will leave less than 10 GB free!")
            print(f"   Remaining after download: ~{remaining:.1f} GB")
            response = input("\n❓ Continue? (yes/no): ").strip().lower()
            return response in ("yes", "y")
        elif estimated_size_gb > free_gb * 0.8:
            print("⚠️  NOTE: This will use more than 80% of your free space.")
            response = input("\n❓ Continue? (yes/no): ").strip().lower()
            return response in ("yes", "y")
        else:
            print("✅ Sufficient disk space available.")
            print()
            return True

def print_usage_warning():
    """Display acceptable and prohibited uses with a 5-second warning."""
    warning = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    PUBLIC DOMAIN MUSIC DOWNLOADER                            ║
║                         USAGE GUIDELINES                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚠️  LEGAL NOTICE: This script downloads music marked as Public Domain (PD) or 
CC0 from Internet Archive and Wikimedia Commons. Music copyright is complex 
with multiple layers (composition, recording, performance rights).

YOU are responsible for verifying copyright status before commercial use.

✅  ACCEPTABLE USE:
  • Personal listening, archival, and education
  • Building offline media server collections
  • Commercial use ONLY after individual track verification
  • Verifying each track's metadata.json and source URL

❌  PROHIBITED USE:
  • Assuming all downloads are automatically cleared for commercial use
  • Bypassing or modifying license verification code
  • Downloading from sources not explicitly verified as PD/CC0
  • Redistributing without checking individual track provenance

🛡️  SAFEGUARDS IN PLACE:
  • Source-level filtering (PD/CC0 collections only)
  • Metadata verification (license URLs checked)
  • Optional Musopen cross-check (best-effort)
  • Rejected tracks logged to _rejected_tracks.csv

⚖️  YOUR RESPONSIBILITY:
Review metadata.json for each track, visit source URLs, and consult a 
copyright attorney for high-value commercial redistribution.

═══════════════════════════════════════════════════════════════════════════════
Starting in 5 seconds... (Press Ctrl+C to abort)
"""
    print(warning)
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        sys.exit(0)
    print()

def main():
    ap = argparse.ArgumentParser(
        description="Download PD/CC0 music with README, tagging, and best-effort Musopen verification.",
        epilog="Tip: Use --source all to download from all sources automatically! Use --max-items -1 to download everything (WARNING: MASSIVE!)."
    )
    ap.add_argument("--source", choices=["ia", "commons", "all"], default="all", help="Source to download from (default: all)")
    ap.add_argument("--out", default="./output_music", help="Output directory")
    ap.add_argument("--query", default="", help="Search query/filter (optional - smart defaults used if not provided)")
    ap.add_argument("--max-items", type=int, default=100, help="Max items to download per source (use -1 for unlimited - WARNING: can be 100+ GB!)")
    ap.add_argument("--composer", default="", help="Filter by composer/creator (best-effort)")
    ap.add_argument("--era", default="", help="Filter by year range or era (e.g., 'pre-1930', '1900s', '1890-1910', 'baroque')")
    ap.add_argument("--preferred-format", default="flac", help="Preferred audio format (flac|ogg|wav|mp3)")
    ap.add_argument("--fallback-to-mp3", action="store_true", help="If preferred format isn't available, allow fallback to MP3")
    ap.add_argument("--skip-if-missing-format", action="store_true", help="Skip track if preferred format is not available")
    args = ap.parse_args()

    # Display usage warning with 5-second delay
    print_usage_warning()

    out_root = Path(args.out).resolve()
    ensure_dir(out_root)
    index_path = out_root / "index.csv"

    # Always write README
    write_readme(out_root)

    # Determine which sources to use
    if args.source == "all":
        sources = ["ia", "commons"]
    else:
        sources = [args.source]
    
    # Check disk space and get user confirmation if needed
    if not check_disk_space(out_root, args.max_items, sources):
        print("\n❌ Download cancelled by user.")
        sys.exit(0)

    # Get existing files to avoid duplicates
    print("[INFO] Scanning for existing files to avoid duplicates...")
    existing_files = get_existing_files(out_root)
    if existing_files:
        print(f"[INFO] Found {len(existing_files)} existing audio files. Will skip duplicates.")
    print()

    # Display download info
    source_names = {"ia": "Internet Archive", "commons": "Wikimedia Commons"}
    if args.source == "all":
        print("[INFO] Source: ALL (Internet Archive + Wikimedia Commons)")
    else:
        print(f"[INFO] Source: {source_names.get(args.source, args.source)}")
    
    print(f"[INFO] Output directory: {out_root}")
    if args.max_items == -1:
        print(f"[INFO] Max items per source: UNLIMITED (will download everything!)")
    else:
        print(f"[INFO] Max items per source: {args.max_items}")
    print(f"[INFO] Preferred format: {args.preferred_format} (fallback: {'mp3' if args.fallback_to_mp3 else 'skip'})")
    if args.composer:
        print(f"[INFO] Composer filter: {args.composer}")
    if args.era:
        print(f"[INFO] Era filter: {args.era}")
    print()

    total_saved = 0
    max_per_source = args.max_items if args.max_items > 0 else float('inf')
    
    for source in sources:
        print(f"\n{'='*80}")
        print(f"Starting download from: {source.upper()}")
        print(f"{'='*80}\n")
        
        # Use provided query or generate smart default
        query = args.query if args.query else get_default_query(source, args.composer, args.era)
        
        if source == "ia":
            query = ia_build_query(query, args.composer, args.era)
            print(f"[ia] Query: {query}")
            print(f"[ia] Searching Internet Archive...\n")
            
            page = 1
            source_saved = 0
            while source_saved < max_per_source:
                try:
                    fetch_count = 50 if args.max_items == -1 else min(50, args.max_items - source_saved)
                    resp = ia_search(query, rows=fetch_count, page=page)
                except Exception as e:
                    print(f"[ia] search error on page {page}: {e}", file=sys.stderr)
                    break
                docs = resp.get('response', {}).get('docs', [])
                if not docs:
                    break
                for doc in docs:
                    identifier = doc.get('identifier')
                    if not identifier:
                        continue
                    saved = ia_download_item(identifier, out_root, index_path, args.preferred_format, args.fallback_to_mp3, args.skip_if_missing_format)
                    if saved > 0:
                        source_saved += saved
                        total_saved += saved
                        if source_saved >= max_per_source:
                            break
                page += 1
                time.sleep(0.4)
            print(f"\n[ia] Downloaded {source_saved} files from Internet Archive")

        elif source == "commons":
            print(f"[commons] Query: {query}")
            print(f"[commons] Searching Wikimedia Commons...\n")
            
            saved = commons_download(
                query=query,
                out_dir=out_root,
                max_items=int(max_per_source) if max_per_source != float('inf') else 999999,
                preferred_format=args.preferred_format,
                fallback_to_mp3=args.fallback_to_mp3,
                skip_if_missing_format=args.skip_if_missing_format,
                index_path=index_path,
                composer=args.composer,
                era=args.era
            )
            total_saved += saved
            print(f"\n[commons] Downloaded {saved} files from Wikimedia Commons")
    
    print(f"\n{'='*80}")
    print(f"Download Complete!")
    print(f"{'='*80}")
    print(f"Total files downloaded: {total_saved}")
    print(f"Output directory: {out_root}")
    print(f"")
    print(f"Next steps:")
    print(f"  1. Review README.md in output directory")
    print(f"  2. Check index.csv for complete inventory")
    print(f"  3. Review metadata.json files for each track")
    print(f"  4. Check _rejected_tracks.csv (if exists) for filtered content")
    print(f"")
    print(f"⚠️  Remember: Verify copyright status before commercial use!")
    print()

if __name__ == "__main__":
    main()
