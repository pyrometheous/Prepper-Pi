import csv, json, os, re, sys, time, hashlib, argparse
from pathlib import Path
import urllib.parse
import urllib.request

ACCEPT_EXTS = [
    ".mp4",
    ".mkv",
    ".webm",
    ".mov",
    ".mpg",
    ".mpeg",
    ".mp2",
    ".m4v",
    ".avi",
    ".ogv",
]


def slugify(name: str) -> str:
    import unicodedata

    name = unicodedata.normalize("NFKD", name)
    s = re.sub(r"[^\w\-.]+", "_", name.strip())
    s = re.sub(r"_+", "_", s)
    return s.strip("_")


def http_get_json(url, headers=None, retries=3, timeout=30):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if attempt + 1 >= retries:
                raise
            time.sleep(2 * (attempt + 1))


def http_stream_download(url, dest_path: Path, headers=None, retries=3, timeout=60):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as resp, open(
                dest_path, "wb"
            ) as f:
                while True:
                    chunk = resp.read(1024 * 256)
                    if not chunk:
                        break
                    f.write(chunk)
            return
        except Exception as e:
            if attempt + 1 >= retries:
                raise
            time.sleep(2 * (attempt + 1))


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


# -------- Internet Archive helpers --------


def ia_advanced_search(title, year=None, max_rows=10):
    q = f'title:("{title}") AND mediatype:(movies)'
    if year:
        q += f" AND year:({year})"
    params = {
        "q": q,
        "fl[]": ["identifier", "title", "year", "downloads", "creator", "collection"],
        "rows": str(max_rows),
        "page": "1",
        "output": "json",
        "sort[]": ["downloads desc", "year asc"],
    }
    url = "https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(
        params, doseq=True
    )
    data = http_get_json(url)
    return data.get("response", {}).get("docs", [])


def ia_get_files(identifier):
    url = f"https://archive.org/metadata/{identifier}"
    data = http_get_json(url)
    files = data.get("files", []) if data else []
    return files


def ia_pick_best_file(files, preferred_exts=ACCEPT_EXTS):
    best = None
    for f in files:
        name = f.get("name", "")
        ext = os.path.splitext(name)[1].lower()
        if ext in preferred_exts and not name.lower().endswith("_sample.mp4"):
            try:
                size = int(f.get("size", 0))
            except:
                size = 0
            meta = {"name": name, "size": size}
            if best is None or size > best["size"]:
                best = meta
    return best


def ia_download(identifier, outdir: Path, title: str, year: str, provenance_rows: list):
    files = ia_get_files(identifier)
    if not files:
        raise RuntimeError(f"No files for IA identifier {identifier}")
    pick = ia_pick_best_file(files)
    if not pick:
        for f in files:
            name = f.get("name", "")
            ext = os.path.splitext(name)[1].lower()
            if ext in ACCEPT_EXTS:
                pick = {"name": name, "size": int(f.get("size", 0) or 0)}
                break
    if not pick:
        raise RuntimeError(
            f"No suitable downloadable file for IA identifier {identifier}"
        )
    file_url = (
        f"https://archive.org/download/{identifier}/{urllib.parse.quote(pick['name'])}"
    )
    safe_name = slugify(f"{title} ({year})") if year else slugify(title)
    ext = os.path.splitext(pick["name"])[1]
    dest = outdir / f"{safe_name}{ext}"
    http_stream_download(file_url, dest)
    checksum = sha256sum(dest)
    provenance_rows.append(
        {
            "title": title,
            "year": year or "",
            "source_type": "ia",
            "source_id": identifier,
            "download_url": file_url,
            "saved_as": str(dest),
            "sha256": checksum,
        }
    )


# -------- Wikimedia Commons helpers --------


def commons_get_original_url(file_title: str):
    api = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url|mime|size",
        "format": "json",
    }
    url = api + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        infos = page.get("imageinfo", [])
        if infos:
            return infos[0].get("url")
    return None


def commons_download(
    file_title: str, outdir: Path, title: str, year: str, provenance_rows: list
):
    url = commons_get_original_url(
        f"File:{file_title}" if not file_title.startswith("File:") else file_title
    )
    if not url:
        raise RuntimeError(f"Could not resolve Commons URL for {file_title}")
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1]
    safe_name = slugify(f"{title} ({year})") if year else slugify(title)
    dest = outdir / f"{safe_name}{ext}"
    http_stream_download(url, dest)
    checksum = sha256sum(dest)
    provenance_rows.append(
        {
            "title": title,
            "year": year or "",
            "source_type": "commons",
            "source_id": file_title,
            "download_url": url,
            "saved_as": str(dest),
            "sha256": checksum,
        }
    )


# -------- Direct helpers (LoC or any URL) --------


def generic_direct_download(
    url: str, outdir: Path, title: str, year: str, provenance_rows: list
):
    ext = os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".mp4"
    safe_name = slugify(f"{title} ({year})") if year else slugify(title)
    dest = outdir / f"{safe_name}{ext}"
    http_stream_download(url, dest)
    checksum = sha256sum(dest)
    provenance_rows.append(
        {
            "title": title,
            "year": year or "",
            "source_type": "direct",
            "source_id": url,
            "download_url": url,
            "saved_as": str(dest),
            "sha256": checksum,
        }
    )


def process_manifest(manifest_path: Path, outdir: Path):
    provenance = []
    with open(manifest_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "").strip()
            year = row.get("year", "").strip()
            stype = row.get("source_type", "").strip()
            sid = row.get("source_id", "").strip()
            query = row.get("query", "").strip()

            try:
                if stype == "ia":
                    print(f"[IA ID] {title} ({year})  ->  {sid}")
                    ia_download(sid, outdir, title, year, provenance)
                elif stype == "ia_search":
                    q_title = sid or query or title
                    print(f"[IA SEARCH] {title} ({year})  ->  '{q_title}'")
                    results = ia_advanced_search(q_title, year or None, max_rows=10)
                    if not results:
                        raise RuntimeError("No IA search results")
                    identifier = results[0]["identifier"]
                    print(f"  -> Using IA identifier: {identifier}")
                    ia_download(identifier, outdir, title, year, provenance)
                elif stype == "commons":
                    print(f"[Commons] {title} ({year})  ->  {sid}")
                    commons_download(sid, outdir, title, year, provenance)
                elif stype == "direct":
                    print(f"[Direct] {title} ({year})  ->  {sid}")
                    generic_direct_download(sid, outdir, title, year, provenance)
                else:
                    print(f"[SKIP] Unknown source_type for '{title}': {stype}")
            except Exception as e:
                print(f"[ERROR] {title} ({year}): {e}")

    prov_path = outdir / "_provenance.csv"
    with open(prov_path, "w", newline="", encoding="utf-8") as pf:
        writer = csv.DictWriter(
            pf,
            fieldnames=[
                "title",
                "year",
                "source_type",
                "source_id",
                "download_url",
                "saved_as",
                "sha256",
            ],
        )
        writer.writeheader()
        for r in provenance:
            writer.writerow(r)
    print(f"\nWrote provenance: {prov_path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Public-domain film fetcher (IA/Commons/Direct)."
    )
    ap.add_argument(
        "--manifest", required=True, help="CSV manifest with titles and sources"
    )
    ap.add_argument("--out", required=True, help="Output directory")
    args = ap.parse_args()

    outdir = Path(args.out).absolute()
    outdir.mkdir(parents=True, exist_ok=True)
    process_manifest(Path(args.manifest), outdir)
