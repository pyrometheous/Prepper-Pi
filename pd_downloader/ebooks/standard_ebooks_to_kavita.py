#!/usr/bin/env python3
"""
Standard Ebooks Library Downloader
Downloads entire Standard Ebooks library via OPDS with Kavita-ready metadata.
See README.md for usage instructions and requirements.
"""

import argparse
import csv
import io
import os
import re
import time
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import urljoin, urlparse

import xml.etree.ElementTree as ET
import requests

DEFAULT_OPDS_URL = "https://standardebooks.org/feeds/opds"
DEFAULT_UA = "SE-Library-Kavita-Full/1.0 (+no-email)"
EPUB_MIME = "application/epub+zip"


def log(msg: str) -> None:
    print(f"[se-kavita] {msg}", flush=True)


def slugify(s: str) -> str:
    s = s.strip()
    s = re.sub(r'[\\/:*?"<>|]', "-", s)
    s = re.sub(r"\\s+", " ", s).strip()
    return s or "Untitled"


def build_session(
    api_key: str, headers: List[str], cookies: List[str]
) -> requests.Session:
    sess = requests.Session()
    sess.headers.update(
        {
            "User-Agent": DEFAULT_UA,
            "Accept": "application/atom+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    # Default Authorization header; user can override via --header/--cookie as needed.
    sess.headers.setdefault("Authorization", f"Bearer {api_key.strip()}")
    for h in headers:
        if ":" in h:
            k, v = h.split(":", 1)
            sess.headers[k.strip()] = v.strip()
    if cookies:
        sess.headers["Cookie"] = "; ".join(cookies)
    return sess


def fetch_feed(sess: requests.Session, url: str, sleep_s: float) -> ET.Element:
    r = sess.get(url, timeout=45)
    r.raise_for_status()
    time.sleep(sleep_s / 2.0)
    return ET.fromstring(r.content)


def find_next_link(feed_root: ET.Element) -> Optional[str]:
    for link in feed_root.findall("{http://www.w3.org/2005/Atom}link"):
        if link.get("rel") == "next" and link.get("href"):
            return link.get("href")
    return None


def parse_entries(feed_root: ET.Element) -> List[Dict]:
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    out = []
    for entry in feed_root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        id_url = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
        authors = [
            a.findtext("atom:name", default="", namespaces=ns) or ""
            for a in entry.findall("atom:author", ns)
        ]
        cats = [
            (c.get("label") or c.get("term") or "").strip()
            for c in entry.findall("atom:category", ns)
        ]
        # Links: pick epub
        epub_href = None
        for ln in entry.findall("atom:link", ns):
            typ = (ln.get("type") or "").lower()
            href = ln.get("href") or ""
            if EPUB_MIME in typ and href:
                epub_href = href
                break
        out.append(
            {
                "title": title,
                "id": id_url,
                "authors": [a for a in authors if a],
                "categories": [c for c in cats if c],
                "epub": epub_href,
            }
        )
    return out


# ---------- EPUB/OPF helpers ----------


def find_opf_path(zf: zipfile.ZipFile) -> Optional[str]:
    # Try META-INF/container.xml first
    try:
        cont = zf.read("META-INF/container.xml")
        root = ET.fromstring(cont)
        ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
        rf = root.find(".//c:rootfile", ns)
        if rf is not None and rf.attrib.get("full-path"):
            return rf.attrib["full-path"]
    except Exception:
        pass
    # Fallback: first .opf in archive
    for name in zf.namelist():
        if name.lower().endswith(".opf"):
            return name
    return None


def ensure_metadata(tree: ET.Element) -> ET.Element:
    # Ensure <metadata> exists under <package>
    md = tree.find(".//{http://www.idpf.org/2007/opf}metadata")
    if md is None:
        md = ET.SubElement(tree, "{http://www.idpf.org/2007/opf}metadata")
    return md


def get_text(el: Optional[ET.Element]) -> str:
    return (el.text or "").strip() if el is not None else ""


def add_dc_subjects(md: ET.Element, subjects: List[str]) -> None:
    existing = {
        get_text(e).lower()
        for e in md.findall("{http://purl.org/dc/elements/1.1/}subject")
    }
    for s in subjects:
        if s and s.lower() not in existing:
            el = ET.SubElement(md, "{http://purl.org/dc/elements/1.1/}subject")
            el.text = s


def has_se_collection(md: ET.Element) -> bool:
    for meta in md.findall("{http://www.idpf.org/2007/opf}meta"):
        if (
            meta.attrib.get("property") == "belongs-to-collection"
            and (meta.text or "").strip().lower() == "standard ebooks"
        ):
            return True
    return False


def add_se_collection(md: ET.Element) -> None:
    # Adds a generic collection so Kavita can build a library-wide Reading List if desired.
    meta = ET.SubElement(md, "{http://www.idpf.org/2007/opf}meta")
    meta.set("property", "belongs-to-collection")
    meta.text = "Standard Ebooks"


def read_series_name(md: ET.Element) -> Optional[str]:
    # Prefer calibre:series (meta @name)
    for meta in md.findall("{http://www.idpf.org/2007/opf}meta"):
        if meta.attrib.get("name") == "calibre:series" and (meta.text or "").strip():
            return meta.text.strip()
    # Then EPUB3 belongs-to-collection of type 'series' (best-effort; many OPFs omit explicit type)
    for meta in md.findall("{http://www.idpf.org/2007/opf}meta"):
        if (
            meta.attrib.get("property") == "belongs-to-collection"
            and (meta.text or "").strip()
        ):
            # Heuristic: if there's also a 'collection-type' meta refining this, prefer when type=series
            # (We skip deep refines resolution to keep things simple and robust.)
            return meta.text.strip()
    return None


def embed_kavita_metadata(
    epub_bytes: bytes, subjects: List[str]
) -> Tuple[bytes, Optional[str]]:
    """
    Merge OPDS subjects into OPF <dc:subject>, add "Standard Ebooks" collection
    if missing, and return (new_epub_bytes, series_name_detected).
    """
    zin = zipfile.ZipFile(io.BytesIO(epub_bytes), "r")
    opf_path = find_opf_path(zin)

    out_mem = io.BytesIO()
    zout = zipfile.ZipFile(out_mem, "w", compression=zipfile.ZIP_DEFLATED)

    # Copy all files; we will overwrite the OPF later
    for info in zin.infolist():
        data = zin.read(info.filename)
        if info.filename == opf_path:
            continue
        zout.writestr(info, data)

    series_name = None

    if opf_path:
        try:
            opf = ET.fromstring(zin.read(opf_path))
            md = ensure_metadata(opf)
            # Collect subjects
            add_dc_subjects(md, subjects)
            # Add library collection tag for Kavita-wide grouping
            if not has_se_collection(md):
                add_se_collection(md)
            # Read series (for folder naming)
            series_name = read_series_name(md)
            # Serialize OPF back
            opf_bytes = ET.tostring(opf, xml_declaration=True, encoding="utf-8")
            zout.writestr(opf_path, opf_bytes)
        except Exception:
            # If OPF parse fails, just copy original OPF
            zout.writestr(opf_path, zin.read(opf_path))
    else:
        # No OPF found; write the EPUB unchanged
        pass

    zin.close()
    zout.close()
    return out_mem.getvalue(), series_name


# ---------- Main download loop ----------


def save_epub(
    epub_bytes: bytes,
    library_root: Path,
    title: str,
    series: Optional[str],
    se_id_hint: str,
    overwrite: bool,
) -> Path:
    series_folder = slugify(series or title)
    dest_dir = library_root / series_folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    fname = slugify(f"{title} - SE{se_id_hint or ''}.epub")
    if not fname.lower().endswith(".epub"):
        fname += ".epub"
    path = dest_dir / fname
    if path.exists() and not overwrite:
        return path
    path.write_bytes(epub_bytes)
    return path


def run(
    opds_url: str,
    out_dir: Path,
    api_key: str,
    headers: List[str],
    cookies: List[str],
    subjects: List[str],
    sleep_s: float,
    overwrite: bool,
) -> None:

    sess = build_session(api_key, headers, cookies)
    out_dir.mkdir(parents=True, exist_ok=True)

    report_rows: List[Dict[str, str]] = []
    seen_ids = set()
    fetched = 0
    page_url = opds_url

    while True:
        log(f"Feed page: {page_url}")
        root = fetch_feed(sess, page_url, sleep_s=sleep_s)
        entries = parse_entries(root)

        for e in entries:
            # Optional subject filter
            if subjects:
                cats_lc = " | ".join([c.lower() for c in e["categories"]])
                if not any(sub.lower() in cats_lc for sub in subjects):
                    continue
            if not e["epub"]:
                continue
            if e["id"] in seen_ids:
                continue
            seen_ids.add(e["id"])

            dl_url = urljoin(page_url, e["epub"])
            title = e["title"] or "Untitled"
            author_str = ", ".join(e["authors"]) if e["authors"] else "Unknown"
            se_id_hint = ""
            try:
                p = urlparse(e["id"])
                se_id_hint = p.path.strip("/").split("/")[-1].replace("/", "_")
            except Exception:
                pass

            status = "OK"
            notes = []
            saved_path = ""

            try:
                log(f"  GET {dl_url}")
                r = sess.get(dl_url, timeout=60)
                r.raise_for_status()
                raw_epub = r.content

                # Embed Kavita-friendly metadata (subjects + SE collection)
                mod_epub, series = embed_kavita_metadata(raw_epub, e["categories"])

                # Save in Kavita layout
                final_path = save_epub(
                    mod_epub,
                    out_dir,
                    title=title,
                    series=series,
                    se_id_hint=se_id_hint,
                    overwrite=overwrite,
                )
                saved_path = str(final_path)
                fetched += 1
                time.sleep(sleep_s)

            except requests.HTTPError as he:
                status = "HTTPERROR"
                notes.append(str(he))
            except Exception as ex:
                status = "ERROR"
                notes.append(str(ex))

            report_rows.append(
                {
                    "title": title,
                    "authors": author_str,
                    "id": e["id"],
                    "download_url": dl_url,
                    "categories": "; ".join(e["categories"]),
                    "saved_path": saved_path,
                    "status": status,
                    "notes": "; ".join(notes),
                }
            )

        next_url = find_next_link(root)
        if not next_url:
            break
        page_url = urljoin(page_url, next_url)

    # Write report
    rep_dir = out_dir / "_reports"
    rep_dir.mkdir(parents=True, exist_ok=True)
    report_csv = rep_dir / "se_library_report.csv"
    with report_csv.open("w", newline="", encoding="utf-8") as f:
        cols = [
            "title",
            "authors",
            "id",
            "download_url",
            "categories",
            "saved_path",
            "status",
            "notes",
        ]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in report_rows:
            w.writerow(row)

    log(f"Done. Saved {fetched} item(s). Report: {report_csv}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Download the entire Standard Ebooks library (EPUB), embedding Kavita-friendly metadata and organizing by Series/Title."
    )
    ap.add_argument(
        "--api-key",
        required=True,
        help="Your Patrons Circle API key/token (required). Sent as Authorization: Bearer by default.",
    )
    ap.add_argument(
        "--opds-url",
        default=DEFAULT_OPDS_URL,
        help=f"OPDS catalog URL (default: {DEFAULT_OPDS_URL})",
    )
    ap.add_argument(
        "--out", default="./KavitaSE", help="Output library root (default: ./KavitaSE)"
    )
    ap.add_argument(
        "--sleep",
        type=float,
        default=1.5,
        help="Seconds to sleep between requests (default: 1.5)",
    )
    ap.add_argument(
        "--subjects",
        default="",
        help="Optional comma-separated subject filters (case-insensitive). Leave blank to fetch ALL.",
    )
    ap.add_argument(
        "--header",
        action="append",
        default=[],
        help="Extra header(s) 'Name: value'. Can repeat.",
    )
    ap.add_argument(
        "--cookie",
        action="append",
        default=[],
        help="Cookie(s) 'name=value'. Can repeat.",
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files if present (default: skip existing).",
    )
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    out_dir = Path(args.out).resolve()
    subjects = [s.strip() for s in args.subjects.split(",") if s.strip()]
    run(
        opds_url=args.opds_url,
        out_dir=out_dir,
        api_key=args.api_key,
        headers=args.header,
        cookies=args.cookie,
        subjects=subjects,
        sleep_s=args.sleep,
        overwrite=args.overwrite,
    )


if __name__ == "__main__":
    main()
