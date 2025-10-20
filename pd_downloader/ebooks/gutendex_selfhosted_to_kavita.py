#!/usr/bin/env python3
"""
Project Gutenberg Ebook Downloader (Self-Hosted Gutendex Version)
Downloads top ebooks by genre using a self-hosted Gutendex instance.
Cleans Project Gutenberg branding and embeds proper OPF metadata for Kavita.

This version is designed to work with your own Gutendex instance running locally
or on your network, giving you unlimited API access without rate limits or 500 errors.

See SELF_HOST_GUTENDEX.md for setup instructions.
"""

import argparse
import csv
import io
import os
import random
import re
import time
import zipfile
from dataclasses import dataclass
from html import unescape
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import requests
from lxml import etree

# ---------------------------- Config ----------------------------

# Default to local Gutendex instance
DEFAULT_GUTENDEX_API = "http://localhost:8000/books"
MIRROR_BASE = "https://gutenberg.pglaf.org"
UA = "SelfHosted-Gutendex-Kavita/1.0"

# Retry configuration (more lenient since we control the server)
MAX_RETRIES = 3
INITIAL_BACKOFF = 0.5
MAX_BACKOFF = 5.0
REQUEST_TIMEOUT = 30

# Trademark cleanup patterns
TRADEMARK_TERMS = [
    r"project\s+gutenberg",
    r"gutenberg\-tm",
    r"www\.gutenberg\.org",
    r"gutenberg\.org",
    r"full project gutenberg\-tm license",
]

# Namespaces for EPUB/OPF/DC
NSMAP = {
    "container": "urn:oasis:names:tc:opendocument:xmlns:container",
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
}

# ---------------------------- Helpers ----------------------------

session = requests.Session()
session.headers.update({"User-Agent": UA})


def log(msg: str) -> None:
    print(f"[gutendex-self-hosted] {msg}", flush=True)


def retry_with_backoff(func, *args, **kwargs):
    """Retry a function with exponential backoff."""
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            
            backoff = min(INITIAL_BACKOFF * (2 ** attempt), MAX_BACKOFF)
            status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
            log(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            if status_code:
                log(f"  HTTP Status: {status_code}")
            log(f"  Retrying in {backoff:.1f}s...")
            time.sleep(backoff)
    
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts")


def slugify(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def series_folder_from_meta(title: str, series: Optional[str]) -> str:
    base = series.strip() if series else title.strip()
    return slugify(base) or "Untitled"


def ensure_dirs(base_out: Path) -> Dict[str, Path]:
    reports = base_out / "_reports"
    reports.mkdir(parents=True, exist_ok=True)
    return {"reports": reports}


# ---------------------------- Gutendex API queries ----------------------------


def test_gutendex_connection(api_url: str) -> bool:
    """Test if Gutendex API is accessible."""
    try:
        # Try to fetch just one book to test connection
        test_url = api_url.rstrip('/books') if api_url.endswith('/books') else api_url
        r = session.get(f"{test_url}/books", params={"page_size": 1}, timeout=10)
        r.raise_for_status()
        data = r.json()
        count = data.get("count", 0)
        log(f"✓ Gutendex API connected: {count:,} books available")
        return True
    except Exception as e:
        log(f"✗ Failed to connect to Gutendex API at {api_url}")
        log(f"  Error: {e}")
        log(f"\n  Make sure Gutendex is running:")
        log(f"    docker-compose -f docker-compose.gutendex.yml up -d")
        log(f"  Or check SELF_HOST_GUTENDEX.md for setup instructions.")
        return False


def topic_query_epub(api_url: str, topic: str, languages: str, page: int = 1) -> dict:
    """Query Gutendex for EPUBs by topic."""
    params = {
        "topic": topic,
        "mime_type": "application/epub+zip",
        "languages": languages,
        "copyright": "false",
        "sort": "popular",
        "page": page,
    }
    
    def _fetch():
        r = session.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    
    return retry_with_backoff(_fetch)


def get_popular_books(api_url: str, languages: str, limit: int, debug: bool = False) -> List[dict]:
    """Get the most popular books."""
    params = {
        "mime_type": "application/epub+zip",
        "languages": languages,
        "copyright": "false",
        "sort": "popular",
        "page": 1,
    }
    
    books = []
    page = 1
    
    while len(books) < limit:
        params["page"] = page
        
        def _fetch():
            r = session.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        
        try:
            data = retry_with_backoff(_fetch)
            results = data.get("results", [])
            if not results:
                break
            
            # Debug: print first book's data
            if debug and len(books) == 0 and results:
                import json
                log("=" * 70)
                log("DEBUG: First book data from API:")
                log("=" * 70)
                print(json.dumps(results[0], indent=2))
                log("=" * 70)
            
            books.extend(results)
            
            if not data.get("next") or len(books) >= limit:
                break
            
            page += 1
        except Exception as e:
            log(f"Error fetching page {page}: {e}")
            break
    
    return books[:limit]


def get_all_subjects(api_url: str, languages: str, min_books: int = 10) -> List[Tuple[str, int]]:
    """
    Get all subjects/genres with book counts from Gutendex.
    Returns list of (subject_name, book_count) tuples.
    """
    log("Discovering all available subjects from Gutendex...")
    
    # Fetch a large sample of books to extract subjects
    params = {
        "languages": languages,
        "copyright": "false",
        "sort": "popular",
        "page_size": 32,  # Gutendex max
    }
    
    subject_counts: Dict[str, int] = {}
    pages_to_check = 50  # Check ~1600 books (32 * 50)
    
    for page in range(1, pages_to_check + 1):
        params["page"] = page
        try:
            r = session.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            
            for book in data.get("results", []):
                # Count subjects
                for subj in book.get("subjects", []):
                    subject_counts[subj] = subject_counts.get(subj, 0) + 1
                # Count bookshelves as subjects too
                for shelf in book.get("bookshelves", []):
                    subject_counts[shelf] = subject_counts.get(shelf, 0) + 1
            
            if not data.get("next"):
                break
                
        except Exception as e:
            log(f"Error fetching subjects on page {page}: {e}")
            break
    
    # Filter and sort
    subjects = [(s, c) for s, c in subject_counts.items() if c >= min_books]
    subjects.sort(key=lambda x: x[1], reverse=True)
    
    log(f"Found {len(subjects)} subjects with {min_books}+ books")
    return subjects


# ---------------------------- EPUB cleaning (same as original) ----------------------------


def strip_headers_footers_html(html: str) -> str:
    s = html.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"(?is)<!--.*?project gutenberg.*?-->", "", s)
    s = re.sub(
        r"(?is)<(div|p|span|section|footer)[^>]*>.*?project gutenberg.*?</\1>", "", s
    )
    s = re.sub(r"(?is)\*{3}\s*start of.*?project gutenberg.*?\*{3}", "", s)
    s = re.sub(r"(?is)\*{3}\s*end of.*?project gutenberg.*?\*{3}", "", s)
    s = re.sub(r'(?is)href="https?://[^"]*gutenberg[^"]*"', 'href="#"', s)
    s = re.sub(r"(?is)project\s+gutenberg", "", s)
    s = re.sub(r"(?is)gutenberg\-tm", "", s)
    s = re.sub(r"(?is)gutenberg\.org", "", s)
    return s.strip()


def clean_epub_bytes(epub_bytes: bytes) -> bytes:
    """Remove Gutenberg references from EPUB internals."""
    in_mem = io.BytesIO(epub_bytes)
    zin = zipfile.ZipFile(in_mem, "r")
    out_mem = io.BytesIO()
    zout = zipfile.ZipFile(out_mem, "w", compression=zipfile.ZIP_DEFLATED)

    text_exts = (".xhtml", ".html", ".htm", ".xml", ".opf", ".ncx", ".txt", ".css")
    for info in zin.infolist():
        data = zin.read(info.filename)
        fn_lower = info.filename.lower()
        if fn_lower.endswith(text_exts):
            txt = None
            for enc in ("utf-8", "windows-1252", "latin-1"):
                try:
                    txt = data.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if txt is None:
                zout.writestr(info, data)
                continue
            cleaned = strip_headers_footers_html(txt)
            for pat in TRADEMARK_TERMS:
                cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
            zout.writestr(info, cleaned.encode("utf-8"))
        else:
            zout.writestr(info, data)

    zin.close()
    zout.close()
    return out_mem.getvalue()


# ---------------------------- OPF metadata (same as original) ----------------------------


def find_opf_path(zipf: zipfile.ZipFile) -> Optional[str]:
    try:
        data = zipf.read("META-INF/container.xml")
        root = etree.fromstring(data)
        rootfile = root.find(".//container:rootfile", namespaces=NSMAP)
        if rootfile is not None:
            return rootfile.get("full-path")
    except Exception:
        pass
    for name in zipf.namelist():
        if name.lower().endswith(".opf"):
            return name
    return None


def parse_opf(zipf: zipfile.ZipFile, opf_path: str) -> Tuple[etree._ElementTree, etree._Element]:
    data = zipf.read(opf_path)
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    tree = etree.fromstring(data, parser=parser)
    md = tree.find(".//opf:metadata", namespaces=NSMAP)
    if md is None:
        md = etree.Element("{%s}metadata" % NSMAP["opf"], nsmap=tree.nsmap)
        tree.insert(0, md)
    return etree.ElementTree(tree), md


def ensure_dc(md: etree._Element, tag: str, text: str) -> etree._Element:
    el = md.find(f"dc:{tag}", namespaces=NSMAP)
    if el is None:
        el = etree.SubElement(md, "{%s}%s" % (NSMAP["dc"], tag))
    if text and not (el.text or "").strip():
        el.text = text
    return el


def add_subjects(md: etree._Element, subjects: List[str]) -> None:
    existing = {
        (el.text or "").strip().lower() for el in md.findall("dc:subject", namespaces=NSMAP)
    }
    for s in subjects:
        if s and s.lower() not in existing:
            el = etree.SubElement(md, "{%s}subject" % NSMAP["dc"])
            el.text = s


def add_collection_tags(md: etree._Element, collection_name: str, position: Optional[int]) -> None:
    col_id = f"col-{abs(hash(collection_name)) % (10**8)}"
    meta1 = etree.SubElement(md, "meta")
    meta1.set("property", "belongs-to-collection")
    meta1.set("id", col_id)
    meta1.text = collection_name
    if position is not None:
        meta2 = etree.SubElement(md, "meta")
        meta2.set("refines", f"#{col_id}")
        meta2.set("property", "group-position")
        meta2.text = str(position)


def read_series_from_opf(md: etree._Element) -> Optional[str]:
    for el in md.findall("meta", namespaces=NSMAP):
        if el.get("name") == "calibre:series" and (el.text or "").strip():
            return el.text.strip()
    for el in md.findall("meta", namespaces=NSMAP):
        if el.get("property") == "belongs-to-collection" and (el.text or "").strip():
            return el.text.strip()
    return None


def embed_kavita_metadata(
    epub_bytes: bytes,
    title: str,
    authors: List[str],
    language: str,
    subjects: List[str],
    collection_name: Optional[str],
    collection_position: Optional[int],
) -> Tuple[bytes, Optional[str]]:
    """Embed Kavita metadata into EPUB."""
    zin = zipfile.ZipFile(io.BytesIO(epub_bytes), "r")
    opf_path = find_opf_path(zin)

    out_mem = io.BytesIO()
    zout = zipfile.ZipFile(out_mem, "w", compression=zipfile.ZIP_DEFLATED)

    created_minimal = False
    if opf_path is None:
        created_minimal = True
        opf_path = "OEBPS/content.opf"
        container_xml = f"""<?xml version="1.0"?>
<container version="1.0" xmlns="{NSMAP['container']}">
  <rootfiles>
    <rootfile full-path="{opf_path}" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""".encode("utf-8")
        zout.writestr("META-INF/container.xml", container_xml)
        if "mimetype" not in zin.namelist():
            zout.writestr("mimetype", b"application/epub+zip")

    for info in zin.infolist():
        name = info.filename
        if name == opf_path or (created_minimal and name == "META-INF/container.xml"):
            continue
        zout.writestr(info, zin.read(name))

    if not created_minimal:
        tree, md = parse_opf(zin, opf_path)
    else:
        pkg = etree.Element(
            "{%s}package" % NSMAP["opf"], nsmap={"opf": NSMAP["opf"], "dc": NSMAP["dc"]}
        )
        pkg.set("unique-identifier", "BookId")
        md = etree.SubElement(pkg, "{%s}metadata" % NSMAP["opf"])
        etree.SubElement(pkg, "{%s}manifest" % NSMAP["opf"])
        etree.SubElement(pkg, "{%s}spine" % NSMAP["opf"])
        tree = etree.ElementTree(pkg)

    ensure_dc(md, "title", title)
    existing_creators = [(el.text or "").strip() for el in md.findall("dc:creator", namespaces=NSMAP)]
    for a in authors:
        if a and a not in existing_creators:
            el = etree.SubElement(md, "{%s}creator" % NSMAP["dc"])
            el.text = a
    if language:
        ensure_dc(md, "language", language)

    add_subjects(md, subjects)

    if collection_name:
        add_collection_tags(md, collection_name, collection_position)

    series_name = read_series_from_opf(md)

    opf_bytes = etree.tostring(tree.getroot(), xml_declaration=True, encoding="utf-8")
    zout.writestr(opf_path, opf_bytes)

    zin.close()
    zout.close()
    return out_mem.getvalue(), series_name


# ---------------------------- Download ----------------------------


def download(url: str, sleep_s: float) -> bytes:
    def _fetch():
        r = session.get(url, timeout=REQUEST_TIMEOUT * 2)
        r.raise_for_status()
        return r.content
    
    data = retry_with_backoff(_fetch)
    time.sleep(sleep_s)
    return data


def rewrite_to_mirror(url: str, mirror_base: str) -> str:
    """
    Rewrite Gutenberg.org URL to use proper download paths.
    Project Gutenberg EPUB files are at: /cache/epub/{id}/pg{id}-images.epub
    """
    parsed = urlparse(url)
    if "gutenberg.org" in parsed.netloc or "pglaf.org" in parsed.netloc:
        # Extract book ID from URLs like /ebooks/84.epub3.images
        import re
        match = re.search(r'/ebooks/(\d+)\.epub', parsed.path)
        if match:
            book_id = match.group(1)
            # Construct proper cache path
            # Try with images first: /cache/epub/{id}/pg{id}-images.epub
            return f"{mirror_base.rstrip('/')}/cache/epub/{book_id}/pg{book_id}-images.epub"
        
        # If not an ebooks URL, use as-is
        return mirror_base.rstrip("/") + parsed.path
    return url


# ---------------------------- Main logic ----------------------------


def run(
    gutendex_api: str,
    out_dir: Path,
    mode: str,
    languages: str,
    mirror: str,
    sleep_s: float,
    count_per_genre: int,
    genres_top: int,
    genres_list: Optional[List[str]],
    no_collections: bool,
    discover_subjects: bool,
    debug: bool = False,
) -> int:
    """
    Run the download process.
    Returns: 0 on success, 1 if some downloads failed, 2 if all downloads failed.
    """

    # Test Gutendex connection first
    if not test_gutendex_connection(gutendex_api):
        return 2

    ensure_dirs(out_dir)
    
    # Determine subjects
    if discover_subjects:
        log("Discovering subjects from your Gutendex instance...")
        all_subjects = get_all_subjects(gutendex_api, languages, min_books=count_per_genre)
        subjects = [s[0] for s in all_subjects[:genres_top]]
        log(f"Top {len(subjects)} subjects by popularity:")
        for i, (name, count) in enumerate(all_subjects[:genres_top], 1):
            log(f"  {i}. {name} ({count} books)")
    elif mode == "popular":
        log(f"Downloading top {count_per_genre} most popular books...")
        subjects = ["Popular"]
        if debug:
            log("Debug mode enabled - will show first book's data structure")
    elif genres_list:
        subjects = genres_list
    else:
        # Fallback subjects
        subjects = [
            "Science fiction",
            "Short stories",
            "Adventure stories",
            "Historical fiction",
            "Horror tales",
        ][:genres_top]

    report_rows: List[Dict[str, str]] = []
    collections_rows: List[Dict[str, str]] = []
    seen_global = set()
    
    # Track success/failure statistics
    total_attempted = 0
    total_success = 0
    total_failed = 0
    error_summary: Dict[str, int] = {}

    for gi, subject in enumerate(subjects, 1):
        log(f"[{gi}/{len(subjects)}] Subject: {subject}")
        
        if mode == "popular" and subject == "Popular":
            # Get most popular books regardless of subject
            picked = get_popular_books(gutendex_api, languages, count_per_genre, debug=debug)
            for b in picked:
                gid = b.get("id")
                if gid:
                    seen_global.add(gid)
        else:
            # Get books by subject
            picked: List[dict] = []
            page = 1
            
            while len(picked) < count_per_genre:
                try:
                    data = topic_query_epub(gutendex_api, topic=subject, languages=languages, page=page)
                    results = data.get("results", [])
                    if not results:
                        break
                    for b in results:
                        if len(picked) >= count_per_genre:
                            break
                        gid = b.get("id")
                        if gid in seen_global:
                            continue
                        fmts = b.get("formats", {})
                        epub_url = fmts.get("application/epub+zip")
                        if not epub_url:
                            continue
                        picked.append(b)
                        seen_global.add(gid)
                    if not data.get("next"):
                        break
                    page += 1
                except Exception as e:
                    log(f"  ERROR: Failed to query Gutendex for subject '{subject}', page {page}: {e}")
                    log(f"  Continuing with {len(picked)} books found so far...")
                    break

        log(f"  Selected {len(picked)} EPUBs")

        for idx, b in enumerate(picked, 1):
            total_attempted += 1
            gid = b.get("id")
            title = (b.get("title") or "").strip().replace("\n", " ")
            authors = [a.get("name", "") for a in b.get("authors", []) if a.get("name")]
            language = (b.get("languages") or [languages])[0]
            rights = b.get("rights") or ""
            is_pd_usa = (b.get("copyright") is False) or ("Public domain in the USA" in rights)
            subjects_list = b.get("subjects") or []
            subjects_list = [s if isinstance(s, str) else str(s) for s in subjects_list]
            if subject not in subjects_list and subject != "Popular":
                subjects_list = [subject] + subjects_list

            epub_url = b["formats"].get("application/epub+zip")
            dl_url = rewrite_to_mirror(epub_url, mirror)

            status = "OK"
            notes: List[str] = []
            series_name_used: str = ""
            
            try:
                log(f"    [{idx}/{len(picked)}] GET {dl_url}")
                raw = download(dl_url, sleep_s=sleep_s)
                cleaned = clean_epub_bytes(raw)

                collection_name = None if no_collections else subject
                collection_position = None if no_collections else idx
                embedded, series_name = embed_kavita_metadata(
                    cleaned,
                    title=title,
                    authors=authors,
                    language=language,
                    subjects=list(dict.fromkeys(subjects_list)),
                    collection_name=collection_name,
                    collection_position=collection_position,
                )

                series_name_used = series_folder_from_meta(title, series_name)
                series_dir = out_dir / series_name_used
                series_dir.mkdir(parents=True, exist_ok=True)

                file_slug = slugify(f"{title} - Gutenberg{gid}.epub")
                final_path = series_dir / file_slug
                final_path.write_bytes(embedded)
                
                total_success += 1

                if collection_name:
                    collections_rows.append({
                        "collection": collection_name,
                        "position": str(collection_position or ""),
                        "series_folder": series_name_used,
                        "file": str(final_path.relative_to(out_dir)),
                        "title": title,
                        "authors": "; ".join(authors) if authors else "Unknown",
                        "gutenberg_id": str(gid),
                    })

            except Exception as e:
                total_failed += 1
                status = "ERROR"
                error_msg = str(e)
                notes.append(error_msg)
                
                # Track error types
                if "404" in error_msg:
                    error_summary["404 Not Found"] = error_summary.get("404 Not Found", 0) + 1
                elif "Connection" in error_msg or "connection" in error_msg:
                    error_summary["Connection Error"] = error_summary.get("Connection Error", 0) + 1
                elif "Timeout" in error_msg or "timeout" in error_msg:
                    error_summary["Timeout"] = error_summary.get("Timeout", 0) + 1
                else:
                    error_summary["Other Error"] = error_summary.get("Other Error", 0) + 1

            report_rows.append({
                "subject": subject,
                "gutenberg_id": str(gid),
                "title": title,
                "authors": "; ".join(authors) if authors else "Unknown",
                "download_url": dl_url,
                "series_folder": series_name_used or series_folder_from_meta(title, None),
                "rights": rights,
                "status": status,
                "notes": "; ".join(notes),
            })

    # Write reports
    out_reports = out_dir / "_reports"
    out_reports.mkdir(parents=True, exist_ok=True)

    with (out_reports / "kavita_epub_report.csv").open("w", newline="", encoding="utf-8") as f:
        cols = ["subject", "gutenberg_id", "title", "authors", "download_url",
                "series_folder", "rights", "status", "notes"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(report_rows)

    with (out_reports / "collections.csv").open("w", newline="", encoding="utf-8") as f:
        cols = ["collection", "position", "series_folder", "file", "title", "authors", "gutenberg_id"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(collections_rows)

    readme = f"""# Kavita-ready EPUB dump (Self-Hosted Gutendex)

- Library root: `{out_dir}`
- Gutendex API: {gutendex_api}
- Mode: {mode}
- Each **Series** is a folder
- Embedded OPF metadata includes title, creators, language, subjects, and collections
- Reports in `_reports/`:
  - `kavita_epub_report.csv`: Per-title status
  - `collections.csv`: Collection mapping

## Download Statistics
- Total attempted: {total_attempted}
- Successful: {total_success}
- Failed: {total_failed}
- Success rate: {(total_success / total_attempted * 100) if total_attempted > 0 else 0:.1f}%
"""
    (out_reports / "README.txt").write_text(readme, encoding="utf-8")

    # Print summary
    print()  # Blank line for readability
    log("=" * 60)
    log(f"Download Summary:")
    log(f"  Total attempted: {total_attempted}")
    log(f"  Successful:      {total_success}")
    log(f"  Failed:          {total_failed}")
    
    if total_attempted > 0:
        success_rate = (total_success / total_attempted) * 100
        
        if total_failed == 0:
            log(f"  Success rate:    {success_rate:.1f}% ✓")
        elif total_success > 0:
            log(f"  Success rate:    {success_rate:.1f}% ⚠")
        else:
            log(f"  Success rate:    {success_rate:.1f}% ✗")
    
    if error_summary:
        log(f"\nError breakdown:")
        for error_type, count in sorted(error_summary.items(), key=lambda x: x[1], reverse=True):
            log(f"  {error_type}: {count}")
    
    log("=" * 60)
    log(f"\nLibrary root: {out_dir}")
    log(f"Reports in: {out_reports}")
    
    # Return appropriate exit code
    if total_failed == total_attempted and total_attempted > 0:
        return 2  # All failed
    elif total_failed > 0:
        return 1  # Some failed
    else:
        return 0  # All succeeded


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Download EPUBs using self-hosted Gutendex with Kavita metadata"
    )
    ap.add_argument(
        "--gutendex-url",
        type=str,
        default=DEFAULT_GUTENDEX_API,
        help=f"Gutendex API URL (default: {DEFAULT_GUTENDEX_API})"
    )
    ap.add_argument(
        "--out",
        type=str,
        default="./KavitaLibrary",
        help="Output directory (default: ./KavitaLibrary)"
    )
    ap.add_argument(
        "--mode",
        type=str,
        choices=["genres", "popular", "discover"],
        default="genres",
        help="Download mode: genres (by subject), popular (most downloaded), or discover (auto-find genres)"
    )
    ap.add_argument(
        "--languages",
        type=str,
        default="en",
        help="Comma-separated language codes (default: en)"
    )
    ap.add_argument(
        "--mirror",
        type=str,
        default=MIRROR_BASE,
        help=f"EPUB download mirror (default: {MIRROR_BASE})"
    )
    ap.add_argument(
        "--sleep",
        type=float,
        default=1.0,
        help="Seconds between EPUB downloads (default: 1.0)"
    )
    ap.add_argument(
        "--count-per-genre",
        type=int,
        default=20,
        help="Books per subject (default: 20)"
    )
    ap.add_argument(
        "--genres-top",
        type=int,
        default=10,
        help="How many top subjects (default: 10)"
    )
    ap.add_argument(
        "--genres",
        type=str,
        default="",
        help="Comma-separated subject list (overrides auto)"
    )
    ap.add_argument(
        "--no-collections",
        action="store_true",
        help="Skip collection metadata"
    )
    ap.add_argument(
        "--debug",
        action="store_true",
        help="Print first book's data structure for debugging"
    )
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    genres_list = (
        [g.strip() for g in args.genres.split(",") if g.strip()]
        if args.genres.strip()
        else None
    )
    
    return run(
        gutendex_api=args.gutendex_url,
        out_dir=out_dir,
        mode=args.mode,
        languages=args.languages,
        mirror=args.mirror,
        sleep_s=args.sleep,
        count_per_genre=args.count_per_genre,
        genres_top=args.genres_top,
        genres_list=genres_list,
        no_collections=args.no_collections,
        discover_subjects=(args.mode == "discover"),
        debug=args.debug,
    )


if __name__ == "__main__":
    import sys
    sys.exit(main())
