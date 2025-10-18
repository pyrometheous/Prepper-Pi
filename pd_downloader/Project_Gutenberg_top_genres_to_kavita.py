#!/usr/bin/env python3
"""
pg_top_genres_epubs_kavita_ready.py

Download the top N EPUB titles for each of the most popular Project Gutenberg subjects,
CLEAN out Project Gutenberg boilerplate, and then OUTPUT in a **Kavita-ready** layout with
embedded OPF metadata for Collections/Genres and standard fields (title/author/language).

Kavita specifics (from docs):
- EPUBs are primarily parsed by internal OPF metadata; filenames/folders are secondary. (wiki)
- Kavita requires each Series to be in its own folder; no files should be at library root. (wiki)
- For EPUBs, Kavita maps OPF tags to fields; supports calibre series tags and EPUB 3 collection props. (wiki)
  OPF→Kavita mapping highlights:
    * dc:title → Chapter Title (displayed)
    * calibre:series → Series Name
    * calibre:series_index → Volume
    * dc:subject → Genres
    * dc:language → Language
    * belongs-to-collection + group-position (EPUB3) → Grouping/Collections
- Kavita can create Collections/Reading Lists from metadata (server setting). (wiki)

This script:
1) Scrapes popular **Subjects** from Gutenberg (top 10 by downloads by default).
2) Uses Gutendex API to fetch **EPUB** results sorted by popularity.
3) Downloads from a **mirror** (default: https://gutenberg.pglaf.org) with a polite sleep, sequentially.
4) CLEANS EPUBs to remove any Project Gutenberg branding/license blocks.
5) EMBEDS/normalizes OPF metadata:
   - Ensures dc:title, dc:creator(s), dc:language.
   - Injects dc:subject entries (includes the selected Subject).
   - (Optional) Adds EPUB3 `meta property="belongs-to-collection"` with the Subject name and an ordering
     `meta property="group-position"` (1..N) so Kavita can build a Collection/Reading List (if enabled).
   - Leaves existing calibre:series/series_index untouched if present. Does not invent "fake" series.
6) Writes to a Kavita-ready structure:
   LibraryRoot/
     <SeriesName>/
       <sanitized file>.epub
   Where SeriesName is taken from embedded metadata if available; otherwise, **Title** (Kavita falls back to Title).

It also writes a CSV report with pass/fail compliance notes and a `collections.csv` that lists the
embedded collection per title to aid verification.

USAGE
  python pg_top_genres_epubs_kavita_ready.py --out ./KavitaLibrary --sleep 2 --count-per-genre 20

Deps
  pip install requests lxml

Notes
- Best-effort cleaning & metadata embedding. You must still verify public-domain status and distribution rights.
- If an EPUB is malformed (no container.xml/OPF), a minimal OPF is added under OEBPS/ per EPUB 3 norms.
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

PG_SUBJECTS_URL = "https://www.gutenberg.org/ebooks/subjects/search/?sort_order=downloads"
GUTENDEX_API = "https://gutendex.com/books"
MIRROR_BASE = "https://gutenberg.pglaf.org"
UA = "PG-Top-Genres-EPUB-Kavita/0.6 (+no-email)"

# Case-insensitive patterns we nuke from EPUB internals during cleaning
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
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    # meta `property=` don't need a prefix
}

# ---------------------------- Helpers ----------------------------

session = requests.Session()
session.headers.update({"User-Agent": UA})


def log(msg: str) -> None:
    print(f"[pg-kavita-ready] {msg}", flush=True)


def slugify(s: str) -> str:
    s = s.strip()
    s = re.sub(r"[\\/:*?\"<>|]+", "-", s)  # Windows-incompatible
    s = re.sub(r"\s+", " ", s).strip()
    return s


def series_folder_from_meta(title: str, series: Optional[str]) -> str:
    # If a series is present, use it; else Title as series folder (Kavita fallback)
    base = series.strip() if series else title.strip()
    return slugify(base) or "Untitled"


def ensure_dirs(base_out: Path) -> Dict[str, Path]:
    reports = base_out / "_reports"
    reports.mkdir(parents=True, exist_ok=True)
    return {"reports": reports}


# ---------------------------- Subject discovery ----------------------------

SUBJECT_LINE_RE = re.compile(
    r"(?P<name>[^<>\n]+?)\s+(\d[\d,]*)\s+downloads", re.IGNORECASE
)

def scrape_top_subjects(limit: int) -> List[str]:
    """Scrape Gutenberg's 'Subjects by downloads' page to get top N names."""
    log(f"Fetching subjects by popularity: {PG_SUBJECTS_URL}")
    r = session.get(PG_SUBJECTS_URL, timeout=30)
    r.raise_for_status()
    text = unescape(r.text)
    names: List[str] = []
    for m in SUBJECT_LINE_RE.finditer(text):
        name = m.group("name").strip()
        if name and name not in names:
            names.append(name)
        if len(names) >= limit:
            break
    if not names:
        names = [
            "Science fiction",
            "Short stories",
            "Adventure stories",
            "Historical fiction",
            "Horror tales",
            "Detective and mystery stories",
            "Fantasy fiction",
            "Love stories",
            "Psychological fiction",
            "Gothic fiction",
        ][:limit]
        log("WARN: subject scrape failed; using fallback list.")
    log(f"Top subjects: {', '.join(names)}")
    return names


# ---------------------------- Gutendex query ----------------------------

def topic_query_epub(topic: str, languages: str, page: int = 1) -> dict:
    params = {
        "topic": topic,
        "mime_type": "application/epub+zip",
        "languages": languages,
        "copyright": "false",
        "sort": "popular",
        "page": page,
    }
    r = session.get(GUTENDEX_API, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def rewrite_to_mirror(url: str, mirror_base: str) -> str:
    parsed = urlparse(url)
    if "gutenberg.org" in parsed.netloc or "pglaf.org" in parsed.netloc or "aleph.gutenberg" in parsed.netloc:
        return mirror_base.rstrip("/") + parsed.path
    return url


# ---------------------------- EPUB cleaning ----------------------------

def strip_headers_footers_html(html: str) -> str:
    s = html.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"(?is)<!--.*?project gutenberg.*?-->", "", s)
    s = re.sub(r"(?is)<(div|p|span|section|footer)[^>]*>.*?project gutenberg.*?</\1>", "", s)
    s = re.sub(r"(?is)\*{3}\s*start of.*?project gutenberg.*?\*{3}", "", s)
    s = re.sub(r"(?is)\*{3}\s*end of.*?project gutenberg.*?\*{3}", "", s)
    s = re.sub(r'(?is)href="https?://[^"]*gutenberg[^"]*"', 'href="#"', s)
    s = re.sub(r"(?is)project\s+gutenberg", "", s)
    s = re.sub(r"(?is)gutenberg\-tm", "", s)
    s = re.sub(r"(?is)gutenberg\.org", "", s)
    return s.strip()


def clean_epub_bytes(epub_bytes: bytes) -> bytes:
    """Remove Gutenberg references from EPUB internals and return a new EPUB blob."""
    in_mem = io.BytesIO(epub_bytes)
    zin = zipfile.ZipFile(in_mem, "r")
    out_mem = io.BytesIO()
    zout = zipfile.ZipFile(out_mem, "w", compression=zipfile.ZIP_DEFLATED)

    text_exts = (".xhtml", ".html", ".htm", ".xml", ".opf", ".ncx", ".txt", ".css")
    for info in zin.infolist():
        data = zin.read(info.filename)
        fn_lower = info.filename.lower()
        if fn_lower.endswith(text_exts):
            # attempt a couple of encodings
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


# ---------------------------- OPF helpers ----------------------------

def find_opf_path(zipf: zipfile.ZipFile) -> Optional[str]:
    """Find OPF via META-INF/container.xml; fallback to first .opf found."""
    try:
        data = zipf.read("META-INF/container.xml")
        root = etree.fromstring(data)
        rootfile = root.find(".//container:rootfile", namespaces=NSMAP)
        if rootfile is not None:
            return rootfile.get("full-path")
    except Exception:
        pass
    # Fallback
    for name in zipf.namelist():
        if name.lower().endswith(".opf"):
            return name
    return None


def parse_opf(zipf: zipfile.ZipFile, opf_path: str) -> Tuple[etree._ElementTree, etree._Element]:
    data = zipf.read(opf_path)
    parser = etree.XMLParser(remove_blank_text=False, recover=True)
    tree = etree.fromstring(data, parser=parser)
    # Ensure metadata element exists
    md = tree.find(".//opf:metadata", namespaces=NSMAP)
    if md is None:
        md = etree.Element("{%s}metadata" % NSMAP["opf"], nsmap=tree.nsmap)
        tree.insert(0, md)
    return etree.ElementTree(tree), md


def get_text(el: Optional[etree._Element]) -> str:
    return (el.text or "").strip() if el is not None else ""


def find_first(tree: etree._Element, xpath: str) -> Optional[etree._Element]:
    return tree.find(xpath, namespaces=NSMAP)


def ensure_dc(md: etree._Element, tag: str, text: str) -> etree._Element:
    el = md.find(f"dc:{tag}", namespaces=NSMAP)
    if el is None:
        el = etree.SubElement(md, "{%s}%s" % (NSMAP["dc"], tag))
    if text and not get_text(el):
        el.text = text
    return el


def add_subjects(md: etree._Element, subjects: List[str]) -> None:
    existing = {get_text(el).lower() for el in md.findall("dc:subject", namespaces=NSMAP)}
    for s in subjects:
        if s and s.lower() not in existing:
            el = etree.SubElement(md, "{%s}subject" % NSMAP["dc"])
            el.text = s


def add_collection_tags(md: etree._Element, collection_name: str, position: Optional[int]) -> None:
    """
    Add EPUB3 collection metadata:
      <meta property="belongs-to-collection" id="col-1">Science fiction</meta>
      <meta refines="#col-1" property="group-position">3</meta>
    """
    # Create a unique-ish id for the collection entry
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
    # Prefer calibre:series if present
    for el in md.findall("meta", namespaces=NSMAP):
        if el.get("name") == "calibre:series" and (el.text or "").strip():
            return el.text.strip()
    # EPUB3 collection grouping could also represent a series for some books.
    for el in md.findall("meta", namespaces=NSMAP):
        if el.get("property") == "belongs-to-collection" and (el.text or "").strip():
            return el.text.strip()
    return None


def write_tree_back(tree: etree._ElementTree) -> bytes:
    return etree.tostring(tree.getroot(), xml_declaration=True, encoding="utf-8")


def embed_kavita_metadata(epub_bytes: bytes,
                          title: str,
                          authors: List[str],
                          language: str,
                          subjects: List[str],
                          collection_name: Optional[str],
                          collection_position: Optional[int]):
    """
    Ensure OPF contains needed metadata and optional collection tags, then write back into EPUB.
    Returns (new_epub_bytes, series_name_detected_or_None)
    """
    zin = zipfile.ZipFile(io.BytesIO(epub_bytes), "r")
    opf_path = find_opf_path(zin)

    # Prepare a new zip to write to
    out_mem = io.BytesIO()
    zout = zipfile.ZipFile(out_mem, "w", compression=zipfile.ZIP_DEFLATED)

    # If no OPF, we will inject a minimal structure under OEBPS/content.opf
    created_minimal = False
    if opf_path is None:
        created_minimal = True
        opf_path = "OEBPS/content.opf"
        # Also ensure META-INF/container.xml points to it
        container_xml = f"""<?xml version="1.0"?>
<container version="1.0" xmlns="{NSMAP['container']}">
  <rootfiles>
    <rootfile full-path="{opf_path}" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""".encode("utf-8")
        zout.writestr("META-INF/container.xml", container_xml)
        # If there is no mimetype, add a standard one
        if "mimetype" not in zin.namelist():
            zout.writestr("mimetype", b"application/epub+zip")

    # Copy over all files except OPF (we'll replace) and possibly container.xml if we created minimal
    for info in zin.infolist():
        name = info.filename
        if name == opf_path:
            continue
        if created_minimal and name == "META-INF/container.xml":
            continue
        data = zin.read(name)
        zout.writestr(info, data)

    # Parse or create OPF
    if not created_minimal:
        tree, md = parse_opf(zin, opf_path)
    else:
        # Minimal OPF skeleton
        pkg = etree.Element("{%s}package" % NSMAP["opf"], nsmap={"opf": NSMAP["opf"], "dc": NSMAP["dc"]})
        pkg.set("unique-identifier", "BookId")
        md = etree.SubElement(pkg, "{%s}metadata" % NSMAP["opf"])
        # add a minimal manifest/spine
        etree.SubElement(pkg, "{%s}manifest" % NSMAP["opf"])
        etree.SubElement(pkg, "{%s}spine" % NSMAP["opf"])
        tree = etree.ElementTree(pkg)

    # Ensure title/creators/lang
    md_title = ensure_dc(md, "title", title)
    # creators
    existing_creators = [get_text(el) for el in md.findall("dc:creator", namespaces=NSMAP)]
    for a in authors:
        if a and a not in existing_creators:
            el = etree.SubElement(md, "{%s}creator" % NSMAP["dc"])
            el.text = a
    # language: use first language
    if language:
        ensure_dc(md, "language", language)

    # Subjects/Genres
    add_subjects(md, subjects)

    # Optional: Add a collection for genre (helps building Collections/Reading Lists if enabled)
    if collection_name:
        add_collection_tags(md, collection_name, collection_position)

    # Read series name if present
    series_name = read_series_from_opf(md)

    # Write OPF back
    opf_bytes = write_tree_back(tree)
    zout.writestr(opf_path, opf_bytes)

    zin.close()
    zout.close()
    final_bytes = out_mem.getvalue()
    return final_bytes, (series_name or None)


# ---------------------------- Validation ----------------------------

def validate_epub_clean(epub_bytes: bytes) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    try:
        mem = io.BytesIO(epub_bytes)
        z = zipfile.ZipFile(mem, "r")
        for name in z.namelist():
            if name.lower().endswith((".xhtml", ".html", ".htm", ".xml", ".opf", ".ncx", ".txt", ".css")):
                t = z.read(name).decode("utf-8", errors="ignore")
                for pat in TRADEMARK_TERMS:
                    if re.search(pat, t, flags=re.IGNORECASE):
                        issues.append(f"PG marker remains in EPUB member: {name}")
                        raise StopIteration
        z.close()
    except StopIteration:
        pass
    except Exception as e:
        issues.append(f"EPUB parse error: {e}")

    if len(epub_bytes) < 200:
        issues.append("Output too small (possible over-trim)")

    return (len(issues) == 0, issues)


# ---------------------------- Main routine ----------------------------

def download(url: str, sleep_s: float) -> bytes:
    r = session.get(url, timeout=60)
    r.raise_for_status()
    data = r.content
    time.sleep(sleep_s)
    return data


def run(out_dir: Path,
        languages: str,
        mirror: str,
        sleep_s: float,
        count_per_genre: int,
        genres_top: int,
        genres_list: Optional[List[str]],
        no_collections: bool) -> None:

    ensure_dirs(out_dir)
    # Determine subjects
    if genres_list:
        subjects = genres_list
    else:
        subjects = scrape_top_subjects(limit=genres_top)

    report_rows: List[Dict[str, str]] = []
    collections_rows: List[Dict[str, str]] = []
    seen_global = set()

    for gi, subject in enumerate(subjects, 1):
        log(f"[{gi}/{len(subjects)}] Subject: {subject}")
        picked: List[dict] = []
        page = 1
        while len(picked) < count_per_genre:
            data = topic_query_epub(topic=subject, languages=languages, page=page)
            results = data.get("results", [])
            if not results:
                break
            for b in results:
                if len(picked) >= count_per_genre:
                    break
                gid = b.get("id")
                if gid in seen_global:
                    continue  # avoid dupes across subjects
                fmts = b.get("formats", {})
                epub_url = fmts.get("application/epub+zip")
                if not epub_url:
                    continue
                picked.append(b)
                seen_global.add(gid)
            if not data.get("next"):
                break
            page += 1

        log(f"  Selected {len(picked)} EPUBs")

        for idx, b in enumerate(picked, 1):
            gid = b.get("id")
            title = (b.get("title") or "").strip().replace("\n", " ")
            authors = [a.get("name", "") for a in b.get("authors", []) if a.get("name")]
            language = (b.get("languages") or ["en"])[0]
            rights = b.get("rights") or ""
            is_pd_usa = (b.get("copyright") is False) or ("Public domain in the USA" in rights)
            subjects_list = b.get("subjects") or []
            # Gutendex subjects are usually a list of strings; ensure strings
            subjects_list = [s if isinstance(s, str) else str(s) for s in subjects_list]
            if subject not in subjects_list:
                subjects_list = [subject] + subjects_list  # ensure chosen subject present

            epub_url = b["formats"].get("application/epub+zip")
            dl_url = rewrite_to_mirror(epub_url, mirror)

            status = "OK"
            notes: List[str] = []
            series_name_used: str = ""
            try:
                log(f"    [{idx}/{len(picked)}] GET {dl_url}")
                raw = download(dl_url, sleep_s=sleep_s)

                # Clean EPUB
                cleaned = clean_epub_bytes(raw)

                # Embed OPF metadata (collections by subject unless disabled)
                collection_name = None if no_collections else subject
                collection_position = None if no_collections else idx
                embedded, series_name = embed_kavita_metadata(
                    cleaned,
                    title=title,
                    authors=authors,
                    language=language,
                    subjects=list(dict.fromkeys(subjects_list)),
                    collection_name=collection_name,
                    collection_position=collection_position
                )

                # Validate cleaned
                ok, issues = validate_epub_clean(embedded)
                if not ok:
                    status = "NONCOMPLIANT"
                    notes.extend(issues)
                if not is_pd_usa:
                    status = "NONCOMPLIANT"
                    notes.append("Not clearly flagged PD in USA via metadata")

                # Determine Series folder
                series_name_used = series_folder_from_meta(title, series_name)
                series_dir = out_dir / series_name_used
                series_dir.mkdir(parents=True, exist_ok=True)

                # Write final file
                file_slug = slugify(f"{title} - Gutenberg{gid}.epub")
                final_path = series_dir / file_slug
                final_path.write_bytes(embedded)

                # Record collection entry
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
                status = "ERROR"
                notes.append(str(e))

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
        cols = ["subject","gutenberg_id","title","authors","download_url","series_folder","rights","status","notes"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in report_rows:
            w.writerow(row)

    with (out_reports / "collections.csv").open("w", newline="", encoding="utf-8") as f:
        cols = ["collection","position","series_folder","file","title","authors","gutenberg_id"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in collections_rows:
            w.writerow(row)

    # Write a README with basic instructions
    readme = f"""# Kavita-ready EPUB dump

- Library root: `{out_dir}`
- Each **Series** is a folder. For singletons, Series = Title (per Kavita EPUB rules).
- Embedded OPF metadata includes:
  - `dc:title`, `dc:creator`, `dc:language`, `dc:subject` (includes the chosen subject).
  - `meta property="belongs-to-collection"` with subject name and `group-position` so Kavita
    can generate Collections/Reading Lists (enable in **Libraries → Manage Collections/Reading Lists**).
- Reports in `_reports/`:
  - `kavita_epub_report.csv`: Per-title status and notes.
  - `collections.csv`: Collection (subject) mapping and ordering.
"""
    (out_reports / "README.txt").write_text(readme, encoding="utf-8")

    log(f"Done. Library root: {out_dir}")
    log(f"Reports in: {out_reports}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Download top EPUBs per popular Gutenberg subject, clean + embed Kavita metadata, and output a Kavita-ready library.")
    ap.add_argument("--out", type=str, default="./KavitaLibrary", help="Kavita library root (default: ./KavitaLibrary)")
    ap.add_argument("--languages", type=str, default="en", help="Comma-separated language codes (default: en)")
    ap.add_argument("--mirror", type=str, default=MIRROR_BASE, help=f"Download mirror base (default: {MIRROR_BASE})")
    ap.add_argument("--sleep", type=float, default=2.0, help="Seconds to sleep between downloads (default: 2.0)")
    ap.add_argument("--count-per-genre", type=int, default=20, help="Titles per subject (default: 20)")
    ap.add_argument("--genres-top", type=int, default=10, help="How many top subjects to auto-scrape (default: 10)")
    ap.add_argument("--genres", type=str, default="", help="Comma-separated subject list (overrides auto)." )
    ap.add_argument("--no-collections", action="store_true", help="Do not embed belongs-to-collection metadata")
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    languages = args.languages
    mirror = args.mirror
    sleep_s = args.sleep
    count_per_genre = args.count_per_genre
    genres_top = args.genres_top
    genres_list = [g.strip() for g in args.genres.split(",") if g.strip()] if args.genres.strip() else None
    run(out_dir=out_dir,
        languages=languages,
        mirror=mirror,
        sleep_s=sleep_s,
        count_per_genre=count_per_genre,
        genres_top=genres_top,
        genres_list=genres_list,
        no_collections=args.no_collections)


if __name__ == "__main__":
    main()
