"""Lawful reference asset crawler/ingester for Blueprint.

Default mode is dry-run. The crawler only follows sources declared in
20_dataset/reference_assets/sources.json and records provenance for every file.
It is intentionally conservative: uncertain licenses should be quarantined,
not mixed into training data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "20_dataset" / "reference_assets"
SOURCES = ROOT / "sources.json"
INDEX = ROOT / "_index.jsonl"
INCOMING = ROOT / "_incoming"
QUARANTINE = ROOT / "_quarantine"
CACHE = ROOT / "_cache"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() not in {"a", "link"}:
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_sources() -> dict[str, Any]:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def allowed_extensions(config: dict[str, Any]) -> set[str]:
    return {str(ext).lower() for ext in config.get("allowed_extensions", [])}


def safe_name(text: str, fallback: str = "asset") -> str:
    text = urllib.parse.unquote(text)
    text = text.replace("\\", "/").rstrip("/").split("/")[-1] or fallback
    text = re.sub(r"[^A-Za-z0-9._+-]+", "_", text)
    return text[:180] or fallback


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_kind(path_or_url: str) -> str:
    ext = Path(urllib.parse.urlparse(path_or_url).path).suffix.lower()
    if ext in {".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".fcstd", ".scad", ".vsp3"}:
        return "cad"
    if ext in {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf"}:
        return "image_or_drawing"
    return "metadata"


def is_remote_asset_candidate(url: str, source: dict[str, Any], config: dict[str, Any]) -> bool:
    crawl = source.get("crawl") or {}
    include = re.compile(crawl.get("include_url_regex") or ".*")
    exclude = re.compile(crawl.get("exclude_url_regex") or r"$^")
    if exclude.search(url):
        return False
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in allowed_extensions(config):
        return False
    cad_like = ext in {".step", ".stp", ".iges", ".igs", ".stl", ".obj", ".3mf", ".fcstd", ".scad", ".vsp3"}
    document_like = ext in {".pdf", ".svg"}
    return bool(cad_like or document_like or include.search(url))


def read_index() -> list[dict[str, Any]]:
    if not INDEX.exists():
        return []
    rows = []
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def append_index(rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    ROOT.mkdir(parents=True, exist_ok=True)
    with INDEX.open("a", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def unique_target(seed: str, kind: str, name: str) -> Path:
    folder = ROOT / seed / ("cad" if kind == "cad" else "images" if kind == "image_or_drawing" else "metadata")
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / name
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    for i in range(2, 10000):
        candidate = folder / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"could not allocate unique target for {target}")


def robots_allowed(url: str, user_agent: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True


def fetch_url(url: str, user_agent: str, timeout: int = 30, max_mb: int = 250) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content_type = resp.headers.get("content-type", "")
        size = resp.headers.get("content-length")
        if size and int(size) > max_mb * 1024 * 1024:
            raise RuntimeError(f"remote file too large: {int(size)} bytes > {max_mb} MB")
        data = resp.read(max_mb * 1024 * 1024 + 1)
        if len(data) > max_mb * 1024 * 1024:
            raise RuntimeError(f"remote file too large after read > {max_mb} MB")
        return data, content_type


def fetch_json(url: str, user_agent: str, timeout: int = 30) -> dict[str, Any]:
    data, _content_type = fetch_url(url, user_agent, timeout=timeout, max_mb=25)
    return json.loads(data.decode("utf-8", errors="ignore"))


def discover_links(source: dict[str, Any], config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    crawl = source.get("crawl") or {}
    if not crawl.get("enabled"):
        return []
    base = source.get("base_url")
    if not base:
        return []
    include = re.compile(crawl.get("include_url_regex") or ".*")
    exclude = re.compile(crawl.get("exclude_url_regex") or r"$^")
    max_depth = int(crawl.get("max_depth", 1))
    exts = allowed_extensions(config)
    user_agent = args.user_agent
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    q: deque[tuple[str, int]] = deque([(base, 0)])
    while q and len(found) < args.limit:
        url, depth = q.popleft()
        if url in seen:
            continue
        seen.add(url)
        if config.get("policy", {}).get("respect_robots_txt", True) and not robots_allowed(url, user_agent):
            print(f"[skip robots] {url}")
            continue
        try:
            data, content_type = fetch_url(url, user_agent, timeout=args.timeout, max_mb=args.max_page_mb)
        except Exception as exc:
            print(f"[warn] fetch failed {url}: {type(exc).__name__}: {exc}")
            continue
        path_ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if path_ext in exts and is_remote_asset_candidate(url, source, config):
            found.append({"url": url, "content_type": content_type, "source": source})
            continue
        if depth >= max_depth:
            continue
        if "html" not in content_type.lower() and path_ext not in {"", ".html", ".htm"}:
            continue
        parser = LinkParser()
        try:
            parser.feed(data.decode("utf-8", errors="ignore"))
        except Exception:
            continue
        for href in parser.links:
            child = urllib.parse.urljoin(url, href)
            child = urllib.parse.urldefrag(child)[0]
            if not child.startswith(("http://", "https://")):
                continue
            if urllib.parse.urlparse(child).netloc != urllib.parse.urlparse(base).netloc:
                continue
            if exclude.search(child):
                continue
            if include.search(child) or Path(urllib.parse.urlparse(child).path).suffix.lower() in exts:
                q.append((child, depth + 1))
        time.sleep(float(config.get("policy", {}).get("rate_limit_seconds", 1.0)))
    return found


def ingest_bytes(url: str, data: bytes, content_type: str, source: dict[str, Any], seed: str, args: argparse.Namespace) -> dict[str, Any]:
    name = safe_name(urllib.parse.urlparse(url).path, fallback=f"{source.get('id', 'source')}.asset")
    ext = Path(name).suffix.lower()
    if not ext:
        guessed = mimetypes.guess_extension(content_type.split(";")[0].strip()) if content_type else None
        if guessed:
            name += guessed
    kind = file_kind(name)
    target = unique_target(seed, kind, name)
    target.write_bytes(data)
    digest = sha256_file(target)
    return {
        "schema": "blueprint_reference_asset_v1",
        "indexed_at": now_iso(),
        "seed": seed,
        "source_id": source.get("id"),
        "source_label": source.get("label"),
        "source_url": url,
        "license_hint": source.get("license_hint"),
        "license_status": "needs_review" if args.quarantine_unknown_license else "source_hint",
        "asset_kind": kind,
        "path": str(target.relative_to(REPO)).replace("\\", "/"),
        "filename": target.name,
        "extension": target.suffix.lower(),
        "sha256": digest,
        "bytes": target.stat().st_size,
        "training_use": "blocked_until_license_review" if args.quarantine_unknown_license else "candidate_reference",
        "notes": "Downloaded by manifest-bound crawler; verify license before model training use.",
    }


def ingest_github_file(repo: str, branch: str, file_path: str, data: bytes, source: dict[str, Any],
                       seed: str, args: argparse.Namespace) -> dict[str, Any]:
    kind = file_kind(file_path)
    safe_rel = file_path.replace("\\", "/").strip("/")
    name = safe_name(safe_rel.replace("/", "__"))
    target = unique_target(seed, kind, name)
    target.write_bytes(data)
    digest = sha256_file(target)
    raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{urllib.parse.quote(safe_rel)}"
    return {
        "schema": "blueprint_reference_asset_v1",
        "indexed_at": now_iso(),
        "seed": seed,
        "source_id": source.get("id"),
        "source_label": source.get("label"),
        "source_url": raw_url,
        "github_repo": repo,
        "github_branch": branch,
        "github_path": safe_rel,
        "license_hint": source.get("license_hint"),
        "license_status": "needs_review" if args.quarantine_unknown_license else "source_hint",
        "asset_kind": kind,
        "path": str(target.relative_to(REPO)).replace("\\", "/"),
        "filename": target.name,
        "extension": target.suffix.lower(),
        "sha256": digest,
        "bytes": target.stat().st_size,
        "training_use": "blocked_until_license_review" if args.quarantine_unknown_license else "candidate_reference",
        "notes": "Downloaded from GitHub tree; verify repository license and file provenance before model training use.",
    }


def ingest_local(path: Path, seed: str, config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    exts = allowed_extensions(config)
    paths = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
    existing_hashes = {r.get("sha256") for r in read_index()}
    rows = []
    for src in paths:
        if src.suffix.lower() not in exts:
            continue
        digest = sha256_file(src)
        if digest in existing_hashes:
            print(f"[skip duplicate] {src}")
            continue
        kind = file_kind(src.name)
        target = unique_target(seed, kind, safe_name(src.name))
        if args.dry_run:
            print(f"[dry-run local] {src} -> {target}")
            continue
        shutil.copy2(src, target)
        rows.append({
            "schema": "blueprint_reference_asset_v1",
            "indexed_at": now_iso(),
            "seed": seed,
            "source_id": "user_local_ingest",
            "source_label": "User local ingest",
            "source_url": str(src),
            "license_hint": args.license_hint or "User supplied; verify before training use.",
            "license_status": "needs_review" if args.quarantine_unknown_license else "user_asserted",
            "asset_kind": kind,
            "path": str(target.relative_to(REPO)).replace("\\", "/"),
            "filename": target.name,
            "extension": target.suffix.lower(),
            "sha256": digest,
            "bytes": target.stat().st_size,
            "training_use": "blocked_until_license_review" if args.quarantine_unknown_license else "candidate_reference",
            "notes": "Local file ingested; keep provenance and license evidence with the asset.",
        })
        existing_hashes.add(digest)
        print(f"[local] {src} -> {target}")
    return rows


def crawl_sources(config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    existing_hashes = {r.get("sha256") for r in read_index()}
    rows: list[dict[str, Any]] = []
    sources = config.get("sources") or []
    selected_ids = set(args.source) if args.source else None
    for source in sources:
        if selected_ids and source.get("id") not in selected_ids:
            continue
        seed_targets = source.get("seed_targets") or ["unknown"]
        if args.seed:
            seed_targets = [args.seed]
        print(f"[source] {source.get('id')} · {source.get('base_url')}")
        discovered = discover_links(source, config, args)
        for item in discovered[: args.limit]:
            url = item["url"]
            seed = seed_targets[0]
            print(f"[found] {seed} · {url}")
            if args.dry_run or not args.download:
                continue
            if config.get("policy", {}).get("respect_robots_txt", True) and not robots_allowed(url, args.user_agent):
                print(f"[skip robots] {url}")
                continue
            try:
                data, content_type = fetch_url(url, args.user_agent, timeout=args.timeout, max_mb=args.max_file_mb)
                digest = hashlib.sha256(data).hexdigest()
                if digest in existing_hashes:
                    print(f"[skip duplicate] {url}")
                    continue
                row = ingest_bytes(url, data, content_type, source, seed, args)
                rows.append(row)
                existing_hashes.add(row["sha256"])
                print(f"[download] {row['path']}")
            except Exception as exc:
                print(f"[warn] download failed {url}: {type(exc).__name__}: {exc}")
            time.sleep(float(config.get("policy", {}).get("rate_limit_seconds", 1.0)))
    return rows


def crawl_direct_urls(config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not args.url:
        return rows
    if not args.seed:
        print("[error] --url requires --seed", file=sys.stderr)
        return rows
    source = {
        "id": "direct_url",
        "label": "Direct user-approved URL",
        "license_hint": args.license_hint or "Direct URL supplied by user; verify license before training use.",
        "crawl": {
            "enabled": True,
            "mode": "direct_url",
            "max_depth": args.depth,
            "include_url_regex": args.include_regex or "(?i)(cad|model|download|3d|stl|step|obj|iges|vsp|github|docs|hardware|assembly)",
            "exclude_url_regex": args.exclude_regex or "(?i)(login|account|cart|checkout|favicon|apple-touch-icon|logo|theme|sprite)",
        },
    }
    existing_hashes = {r.get("sha256") for r in read_index()}
    for url in args.url:
        print(f"[url] {args.seed} · {url}")
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if ext in allowed_extensions(config) and is_remote_asset_candidate(url, source, config):
            discovered = [{"url": url, "content_type": "", "source": source}]
        else:
            source["base_url"] = url
            discovered = discover_links(source, config, args)
        for item in discovered[: args.limit]:
            asset_url = item["url"]
            print(f"[found] {args.seed} · {asset_url}")
            if args.dry_run or not args.download:
                continue
            try:
                data, content_type = fetch_url(asset_url, args.user_agent, timeout=args.timeout, max_mb=args.max_file_mb)
                digest = hashlib.sha256(data).hexdigest()
                if digest in existing_hashes:
                    print(f"[skip duplicate] {asset_url}")
                    continue
                row = ingest_bytes(asset_url, data, content_type, source, args.seed, args)
                rows.append(row)
                existing_hashes.add(row["sha256"])
                print(f"[download] {row['path']}")
            except Exception as exc:
                print(f"[warn] download failed {asset_url}: {type(exc).__name__}: {exc}")
    return rows


def github_file_allowed(path: str, config: dict[str, Any], args: argparse.Namespace) -> bool:
    ext = Path(path).suffix.lower()
    if ext not in allowed_extensions(config):
        return False
    if args.cad_only:
        return file_kind(path) == "cad"
    include = re.compile(args.include_regex or r"(?i)(cad|mesh|model|hardware|mechanical|assembly|print|3d|stl|step|obj|iges|vsp|onshape|parts|docs)")
    exclude = re.compile(args.exclude_regex or r"(?i)(__pycache__|node_modules|\.git/|favicon|logo|teaser|website|paper|video)")
    return bool(include.search(path) and not exclude.search(path))


def crawl_github_repos(config: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not args.github_repo:
        return rows
    if not args.seed:
        print("[error] --github-repo requires --seed", file=sys.stderr)
        return rows
    existing_hashes = {r.get("sha256") for r in read_index()}
    for repo in args.github_repo:
        repo = repo.replace("https://github.com/", "").strip("/")
        if repo.endswith(".git"):
            repo = repo[:-4]
        if repo.count("/") != 1:
            print(f"[warn] invalid repo {repo!r}; expected owner/name")
            continue
        api = f"https://api.github.com/repos/{repo}"
        try:
            meta = fetch_json(api, args.user_agent, timeout=args.timeout)
        except Exception as exc:
            print(f"[warn] GitHub repo metadata failed {repo}: {type(exc).__name__}: {exc}")
            continue
        branch = args.github_branch or meta.get("default_branch") or "main"
        license_obj = meta.get("license") or {}
        license_hint = args.license_hint or f"GitHub repo license: {license_obj.get('spdx_id') or license_obj.get('name') or 'unknown'}"
        source = {
            "id": f"github:{repo}",
            "label": f"GitHub {repo}",
            "license_hint": license_hint,
        }
        tree_url = f"https://api.github.com/repos/{repo}/git/trees/{urllib.parse.quote(branch)}?recursive=1"
        try:
            tree = fetch_json(tree_url, args.user_agent, timeout=args.timeout)
        except Exception as exc:
            print(f"[warn] GitHub tree failed {repo}@{branch}: {type(exc).__name__}: {exc}")
            continue
        candidates = [
            item for item in tree.get("tree", [])
            if item.get("type") == "blob" and github_file_allowed(str(item.get("path") or ""), config, args)
        ]
        print(f"[github] {repo}@{branch} candidates={len(candidates)} license={license_hint}")
        for item in candidates[: args.limit]:
            file_path = item.get("path")
            raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{urllib.parse.quote(file_path)}"
            print(f"[found] {args.seed} · {repo}/{file_path}")
            if args.dry_run or not args.download:
                continue
            try:
                data, content_type = fetch_url(raw_url, args.user_agent, timeout=args.timeout, max_mb=args.max_file_mb)
                digest = hashlib.sha256(data).hexdigest()
                if digest in existing_hashes:
                    print(f"[skip duplicate] {repo}/{file_path}")
                    continue
                row = ingest_github_file(repo, branch, file_path, data, source, args.seed, args)
                rows.append(row)
                existing_hashes.add(row["sha256"])
                print(f"[download] {row['path']}")
            except Exception as exc:
                print(f"[warn] GitHub download failed {repo}/{file_path}: {type(exc).__name__}: {exc}")
            time.sleep(float(config.get("policy", {}).get("rate_limit_seconds", 1.0)))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true", help="download discovered files; default is discovery only")
    ap.add_argument("--dry-run", action="store_true", help="show actions without writing assets")
    ap.add_argument("--source", action="append", help="source id to crawl; may be repeated")
    ap.add_argument("--url", action="append", help="direct approved page/file URL to discover or download; may be repeated")
    ap.add_argument("--github-repo", action="append", help="GitHub repo owner/name or URL to scan; may be repeated")
    ap.add_argument("--github-branch", default="", help="GitHub branch/ref; default is repo default_branch")
    ap.add_argument("--seed", help="force seed target for downloads or local ingest")
    ap.add_argument("--depth", type=int, default=1, help="direct URL discovery depth")
    ap.add_argument("--include-regex", default="", help="override direct URL include regex")
    ap.add_argument("--exclude-regex", default="", help="override direct URL exclude regex")
    ap.add_argument("--limit", type=int, default=50, help="maximum discovered/downloaded links")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--max-page-mb", type=int, default=25)
    ap.add_argument("--max-file-mb", type=int, default=250)
    ap.add_argument("--user-agent", default="BlueprintReferenceCrawler/1.0 (+local research; contact user)")
    ap.add_argument("--ingest-local", help="copy local files/folder into reference_assets with provenance")
    ap.add_argument("--license-hint", default="")
    ap.add_argument("--allow-training-use", action="store_true",
                    help="mark ingested assets as candidate_reference instead of blocked_until_license_review")
    ap.add_argument("--cad-only", action="store_true", help="only keep CAD/mesh extensions from GitHub repos")
    args = ap.parse_args(argv)
    args.quarantine_unknown_license = not args.allow_training_use
    if not args.download and not args.ingest_local:
        args.dry_run = True

    ROOT.mkdir(parents=True, exist_ok=True)
    INCOMING.mkdir(parents=True, exist_ok=True)
    QUARANTINE.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    config = load_sources()
    rows: list[dict[str, Any]] = []
    if args.ingest_local:
        if not args.seed:
            print("[error] --ingest-local requires --seed", file=sys.stderr)
            return 2
        rows.extend(ingest_local(Path(args.ingest_local), args.seed, config, args))
    elif args.github_repo:
        rows.extend(crawl_github_repos(config, args))
    elif args.url:
        rows.extend(crawl_direct_urls(config, args))
    else:
        rows.extend(crawl_sources(config, args))
    if rows and not args.dry_run:
        append_index(rows)
    print(f"[done] indexed_new={len(rows)} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
