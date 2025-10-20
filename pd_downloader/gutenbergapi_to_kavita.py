#!/usr/bin/env python3
"""
Project Gutenberg Ebook Downloader using GutenbergAPI.com
Downloads EPUBs based on metadata from GutenbergAPI (via RapidAPI) with Kavita-ready metadata.
Requires RapidAPI key for the Project Gutenberg Free Books API.

See README.md for usage instructions and requirements.
"""

import argparse
import csv
import io
import os
import re
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

import requests
from lxml import etree

# ---------------------------- Config ----------------------------

GUTENBERG_API_BASE = "https://project-gutenberg-books-api.p.rapidapi.com"
GUTENBERG_EPUB_BASE = "https://www.gutenberg.org/ebooks"
MIRROR_BASE = "https://gutenberg.pglaf.org"
UA = "GutenbergAPI-EPUB-Kavita/1.0"

# Retry configuration
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0
MAX_BACKOFF = 30.0
REQUEST_TIMEOUT = 30

# RapidAPI Free tier: 500 requests/month
# We'll be conservative and add rate limiting
RATE_LIMIT_DELAY = 0.5  # seconds between API calls

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
    print(f"[gutenberg-api-kavita] {msg}", flush=True)


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


# ---------------------------- GutenbergAPI queries ----------------------------


def query_books(
    api_key: str,
    query: Optional[str] = None,
    language: Optional[str] = None,
    subject: Optional[str] = None,
    author: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
) -> dict:
    """
    Query the GutenbergAPI for books.
    
    Args:
        api_key: RapidAPI key
        query: Full-text search query
        language: Language code (e.g., 'en')
        subject: Subject/genre filter
        author: Author name filter
        page: Page number (1-indexed)
        page_size: Results per page (max 100)
    
    Returns:
        API response dict with 'results', 'next', 'previous' keys
    """
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "project-gutenberg-books-api.p.rapidapi.com"
    }
    
    params = {
        "page": page,
        "page_size": min(page_size, 100),  # API max is 100
    }
    
    if query:
        params["q"] = query
    if language:
        params["language"] = language
    if subject:
        params["subject"] = subject
    if author:
        params["author"] = author
    
    def _fetch():
        url = f"{GUTENBERG_API_BASE}/books"
        r = session.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        time.sleep(RATE_LIMIT_DELAY)  # Rate limiting
        return r.json()
    
    return retry_with_backoff(_fetch)


def get_popular_books(
    api_key: str,
    language: str = "en",
    limit: int = 100,
) -> List[dict]:
    """
    Get the most popular books (by download count).
    
    Args:
        api_key: RapidAPI key
        language: Language filter
        limit: Maximum number of books to retrieve
    
    Returns:
        List of book metadata dicts
    """
    books = []
    page = 1
    
    while len(books) < limit:
        try:
            data = query_books(
                api_key=api_key,
                language=language,
                page=page,
                page_size=100,
            )
            
            results = data.get("results", [])
            if not results:
                break
            
            # Sort by download_count descending
            results.sort(key=lambda x: x.get("download_count", 0), reverse=True)
            books.extend(results)
            
            if not data.get("next") or len(books) >= limit:
                break
            
            page += 1
        except Exception as e:
            log(f"Error fetching page {page}: {e}")
            break
    
    # Final sort and limit
    books.sort(key=lambda x: x.get("download_count", 0), reverse=True)
    return books[:limit]


def get_books_by_subject(
    api_key: str,
    subject: str,
    language: str = "en",
    limit: int = 50,
) -> List[dict]:
    """Get books filtered by subject/genre."""
    books = []
    page = 1
    
    while len(books) < limit:
        try:
            data = query_books(
                api_key=api_key,
                subject=subject,
                language=language,
                page=page,
                page_size=100,
            )
            
            results = data.get("results", [])
            if not results:
                break
            
            # Sort by download_count
            results.sort(key=lambda x: x.get("download_count", 0), reverse=True)
            books.extend(results)
            
            if not data.get("next") or len(books) >= limit:
                break
            
            page += 1
        except Exception as e:
            log(f"Error fetching subject '{subject}' page {page}: {e}")
            break
    
    books.sort(key=lambda x: x.get("download_count", 0), reverse=True)
    return books[:limit]


# ---------------------------- EPUB download & metadata ----------------------------


def get_epub_url(gutenberg_id: int, mirror: str = MIRROR_BASE) -> str:
    """Construct the EPUB download URL for a Gutenberg ID."""
    return f"{mirror}/{gutenberg_id}/pg{gutenberg_id}.epub"


def download_epub(url: str, sleep_s: float = 1.0) -> bytes:
    """Download EPUB with retry logic."""
    def _fetch():
        r = session.get(url, timeout=REQUEST_TIMEOUT * 2)
        r.raise_for_status()
        return r.content
    
    data = retry_with_backoff(_fetch)
    time.sleep(sleep_s)
    return data


# ---------------------------- EPUB cleaning (reuse from original script) ----------------------------


def strip_headers_footers_html(html: str) -> str:
    """Remove Project Gutenberg headers/footers from HTML content."""
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
    """Remove Gutenberg references from EPUB."""
    TRADEMARK_TERMS = [
        r"project\s+gutenberg",
        r"gutenberg\-tm",
        r"www\.gutenberg\.org",
        r"gutenberg\.org",
    ]
    
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


# ---------------------------- OPF metadata embedding ----------------------------


def find_opf_path(zipf: zipfile.ZipFile) -> Optional[str]:
    """Find OPF via META-INF/container.xml."""
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
    """Add EPUB3 collection metadata."""
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
    """Extract series name from OPF metadata."""
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
    """Embed metadata into EPUB OPF file."""
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


# ---------------------------- Main logic ----------------------------


def run(
    api_key: str,
    out_dir: Path,
    mode: str,
    subject: Optional[str],
    limit: int,
    language: str,
    mirror: str,
    sleep_s: float,
    no_collections: bool,
) -> None:
    """
    Main execution logic.
    
    Args:
        api_key: RapidAPI key
        out_dir: Output directory
        mode: 'popular' or 'subject'
        subject: Subject name (for subject mode)
        limit: Max books to download
        language: Language filter
        mirror: EPUB download mirror
        sleep_s: Sleep between downloads
        no_collections: Skip collection metadata
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = out_dir / "_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    log(f"Mode: {mode}")
    log(f"Language: {language}")
    log(f"Limit: {limit}")

    # Fetch book metadata from API
    if mode == "popular":
        log("Fetching most popular books...")
        books = get_popular_books(api_key=api_key, language=language, limit=limit)
    elif mode == "subject":
        if not subject:
            raise ValueError("Subject required for subject mode")
        log(f"Fetching books for subject: {subject}")
        books = get_books_by_subject(api_key=api_key, subject=subject, language=language, limit=limit)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    log(f"Found {len(books)} books to download")

    report_rows: List[Dict[str, str]] = []
    collections_rows: List[Dict[str, str]] = []

    for idx, book in enumerate(books, 1):
        gid = book.get("id")
        title = (book.get("title") or "").strip().replace("\n", " ")
        authors_data = book.get("authors", [])
        authors = [a.get("name", "") for a in authors_data if isinstance(a, dict) and a.get("name")]
        if not authors:
            authors = ["Unknown"]
        
        lang = book.get("language", language)
        subjects_list = book.get("subjects", [])
        if isinstance(subjects_list, str):
            subjects_list = [subjects_list]
        
        bookshelves = book.get("bookshelves", [])
        if isinstance(bookshelves, str):
            bookshelves = [bookshelves]
        
        # Combine subjects and bookshelves
        all_subjects = list(dict.fromkeys(subjects_list + bookshelves))
        
        download_count = book.get("download_count", 0)
        
        epub_url = get_epub_url(gid, mirror)
        
        status = "OK"
        notes: List[str] = []
        series_name_used = ""
        
        try:
            log(f"  [{idx}/{len(books)}] Downloading: {title} (ID: {gid})")
            log(f"    URL: {epub_url}")
            
            raw = download_epub(epub_url, sleep_s=sleep_s)
            cleaned = clean_epub_bytes(raw)
            
            collection_name = None if no_collections else (subject if mode == "subject" else "Popular")
            collection_position = None if no_collections else idx
            
            embedded, series_name = embed_kavita_metadata(
                cleaned,
                title=title,
                authors=authors,
                language=lang,
                subjects=all_subjects,
                collection_name=collection_name,
                collection_position=collection_position,
            )
            
            series_name_used = series_folder_from_meta(title, series_name)
            series_dir = out_dir / series_name_used
            series_dir.mkdir(parents=True, exist_ok=True)
            
            file_slug = slugify(f"{title} - Gutenberg{gid}.epub")
            final_path = series_dir / file_slug
            final_path.write_bytes(embedded)
            
            log(f"    Saved: {final_path.relative_to(out_dir)}")
            
            if collection_name:
                collections_rows.append({
                    "collection": collection_name,
                    "position": str(collection_position or ""),
                    "series_folder": series_name_used,
                    "file": str(final_path.relative_to(out_dir)),
                    "title": title,
                    "authors": "; ".join(authors),
                    "gutenberg_id": str(gid),
                })
        
        except Exception as e:
            status = "ERROR"
            notes.append(str(e))
            log(f"    ERROR: {e}")
        
        report_rows.append({
            "gutenberg_id": str(gid),
            "title": title,
            "authors": "; ".join(authors),
            "language": lang,
            "subjects": "; ".join(all_subjects[:5]),  # Limit for CSV
            "download_count": str(download_count),
            "download_url": epub_url,
            "series_folder": series_name_used or series_folder_from_meta(title, None),
            "status": status,
            "notes": "; ".join(notes),
        })

    # Write reports
    with (reports_dir / "kavita_epub_report.csv").open("w", newline="", encoding="utf-8") as f:
        cols = ["gutenberg_id", "title", "authors", "language", "subjects", "download_count",
                "download_url", "series_folder", "status", "notes"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(report_rows)

    if collections_rows:
        with (reports_dir / "collections.csv").open("w", newline="", encoding="utf-8") as f:
            cols = ["collection", "position", "series_folder", "file", "title", "authors", "gutenberg_id"]
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(collections_rows)

    readme = f"""# Kavita-ready EPUB Library (GutenbergAPI)

- Library root: `{out_dir}`
- Downloaded: {len(books)} books
- Mode: {mode}
- Language: {language}

## Reports
- `kavita_epub_report.csv`: Per-title status and download info
- `collections.csv`: Collection mapping (if enabled)

## Usage
Point Kavita to this directory as a library root.
"""
    (reports_dir / "README.txt").write_text(readme, encoding="utf-8")

    log(f"\nDone! Downloaded {len([r for r in report_rows if r['status'] == 'OK'])}/{len(books)} books")
    log(f"Library root: {out_dir}")
    log(f"Reports: {reports_dir}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Download Project Gutenberg EPUBs using GutenbergAPI.com with Kavita-ready metadata"
    )
    ap.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="RapidAPI key for Project Gutenberg Free Books API"
    )
    ap.add_argument(
        "--out",
        type=str,
        default="./GutenbergAPILibrary",
        help="Output directory (default: ./GutenbergAPILibrary)"
    )
    ap.add_argument(
        "--mode",
        type=str,
        choices=["popular", "subject"],
        default="popular",
        help="Download mode: 'popular' (most downloaded) or 'subject' (by genre)"
    )
    ap.add_argument(
        "--subject",
        type=str,
        help="Subject/genre name (required if mode=subject)"
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum books to download (default: 100)"
    )
    ap.add_argument(
        "--language",
        type=str,
        default="en",
        help="Language code (default: en)"
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
        "--no-collections",
        action="store_true",
        help="Skip embedding collection metadata"
    )
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    
    if args.mode == "subject" and not args.subject:
        raise ValueError("--subject required when --mode=subject")
    
    run(
        api_key=args.api_key,
        out_dir=Path(args.out).resolve(),
        mode=args.mode,
        subject=args.subject,
        limit=args.limit,
        language=args.language,
        mirror=args.mirror,
        sleep_s=args.sleep,
        no_collections=args.no_collections,
    )


if __name__ == "__main__":
    main()
