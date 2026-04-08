import argparse
import json
import re
import ssl
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_URLS = [
    "https://tbi.hcmut.edu.vn/",
    "https://hcmut.edu.vn/tintuc/Innovation-Fablab-phong-thi-nghiem-che-tao-san-pham-ho-tro-khoi-nghiep-truong-DH-Bach-khoa",
]


def fetch_html(url: str) -> str:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    # Prefer verified TLS using certifi bundle (works better on some Windows Python setups).
    ssl_context = None
    try:
        import certifi  # type: ignore

        ssl_context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ssl_context = ssl.create_default_context()

    try:
        with urlopen(req, timeout=20, context=ssl_context) as response:
            html = response.read().decode("utf-8", errors="ignore")
    except URLError as ex:
        reason = getattr(ex, "reason", None)
        if isinstance(reason, ssl.SSLCertVerificationError):
            # Last resort fallback to keep ingestion running in local/dev environments.
            print(f"[warn] TLS verify failed for {url}, retrying without certificate verification")
            insecure_context = ssl._create_unverified_context()
            with urlopen(req, timeout=20, context=insecure_context) as response:
                html = response.read().decode("utf-8", errors="ignore")
        else:
            raise
    return html


def fetch_text(url: str) -> str:
    html = fetch_html(url)
    return extract_text_from_html(html)


def extract_text_from_html(html: str) -> str:

    html = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style.*?>.*?</style>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_internal_links(base_url: str, html: str, max_links: int = 20) -> list[str]:
    parsed_base = urlparse(base_url)
    raw_links = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)
    links: list[str] = []
    seen: set[str] = set()
    for raw in raw_links:
        if raw.startswith("#") or raw.startswith("javascript:") or raw.startswith("mailto:"):
            continue
        full = urljoin(base_url, raw)
        parsed = urlparse(full)
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc != parsed_base.netloc:
            continue
        lower_path = parsed.path.lower()
        if any(
            lower_path.endswith(ext)
            for ext in (
                ".css",
                ".js",
                ".png",
                ".jpg",
                ".jpeg",
                ".svg",
                ".gif",
                ".ico",
                ".woff",
                ".woff2",
                ".ttf",
                ".map",
                ".xml",
                ".pdf",
            )
        ):
            continue
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
        if normalized in seen:
            continue
        seen.add(normalized)
        links.append(normalized)
        if len(links) >= max_links:
            break
    return links


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list[str]:
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += max(1, chunk_size - overlap)
    return chunks


def build(
    urls: list[str],
    out_file: Path,
    max_chunks_per_url: int = 8,
    crawl_internal_links: bool = True,
    max_internal_links: int = 12,
    local_html_files: list[str] | None = None,
) -> None:
    items = []
    visited: set[str] = set()
    for url in urls:
        if url in visited:
            continue
        visited.add(url)
        try:
            html = fetch_html(url)
            text = extract_text_from_html(html)
            chunks = chunk_text(text)[:max_chunks_per_url]
            for idx, c in enumerate(chunks, 1):
                items.append(
                    {
                        "title": f"{url} chunk {idx}",
                        "sourceUrl": url,
                        "content": c,
                    }
                )
            print(f"[ok] {url} -> {len(chunks)} chunks")

            if crawl_internal_links:
                child_links = extract_internal_links(url, html, max_links=max_internal_links)
                for child in child_links:
                    if child in visited:
                        continue
                    visited.add(child)
                    try:
                        child_text = fetch_text(child)
                        child_chunks = chunk_text(child_text)[: max(1, max_chunks_per_url // 2)]
                        for idx, c in enumerate(child_chunks, 1):
                            items.append(
                                {
                                    "title": f"{child} chunk {idx}",
                                    "sourceUrl": child,
                                    "content": c,
                                }
                            )
                        if child_chunks:
                            print(f"[ok] {child} -> {len(child_chunks)} chunks")
                    except Exception as child_ex:
                        print(f"[warn] failed to fetch child {child}: {child_ex}")
        except Exception as ex:
            print(f"[warn] failed to fetch {url}: {ex}")

    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Optional: ingest local HTML snapshots exported from browser
    for local_html in local_html_files or []:
        local_path = Path(local_html)
        if not local_path.exists():
            print(f"[warn] local html not found: {local_html}")
            continue
        try:
            html = local_path.read_text(encoding="utf-8", errors="ignore")
            text = extract_text_from_html(html)
            chunks = chunk_text(text)[:max_chunks_per_url]
            for idx, c in enumerate(chunks, 1):
                items.append(
                    {
                        "title": f"{local_path.name} chunk {idx}",
                        "sourceUrl": f"file://{local_path.as_posix()}",
                        "content": c,
                    }
                )
            print(f"[ok] local {local_path} -> {len(chunks)} chunks")
        except Exception as ex:
            print(f"[warn] failed to parse local html {local_html}: {ex}")

    out_file.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[done] wrote {len(items)} chunks to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build JSON corpus for Gemini RAG.")
    parser.add_argument(
        "--out",
        default="../RobotHri/Resources/Raw/Rag/hcmut_seed.json",
        help="Output JSON path",
    )
    parser.add_argument("--url", action="append", default=None, help="Add URL (can repeat)")
    parser.add_argument(
        "--no-crawl-internal-links",
        action="store_true",
        help="Disable extracting and crawling internal links from each URL",
    )
    parser.add_argument(
        "--max-internal-links",
        type=int,
        default=12,
        help="Maximum internal links to crawl per root URL",
    )
    parser.add_argument(
        "--local-html",
        action="append",
        default=None,
        help="Local saved HTML file path (can repeat) for dynamic websites",
    )
    args = parser.parse_args()

    urls = args.url if args.url else DEFAULT_URLS
    build(
        urls,
        Path(args.out),
        crawl_internal_links=not args.no_crawl_internal_links,
        max_internal_links=args.max_internal_links,
        local_html_files=args.local_html,
    )
