#!/usr/bin/env python3
"""Preflight quality gate for Blog -> Threads payloads.

This gate intentionally checks the presentation contract, not Threads API auth.
It prevents ugly root-only posts, bare-link preview dependence, and missing images.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

URL_RE = re.compile(r"https?://\S+")
THREADS_INTERNAL_ID_RE = re.compile(r"(?<!\d)\d{15,22}(?!\d)")
INTERNAL_LOG_MARKERS = (
    "main.create",
    "main.publish",
    "reply.create",
    "reply.publish",
    "threads_root_id",
    "threads_reply_ids",
    "creation_id",
    "reply_to_id",
    "media_type",
    "access_token",
)


def fail(msg: str) -> None:
    print(f"threads-quality-gate: FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_payload(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot read JSON payload {path}: {exc}")


def normalize_images(raw: object) -> dict[int, str]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        fail("postImages must be an object mapping 1-indexed post numbers to URLs")
    out: dict[int, str] = {}
    for key, value in raw.items():
        try:
            idx = int(key)
        except Exception as exc:  # noqa: BLE001
            fail(f"postImages key is not an integer: {key!r}: {exc}")
        if not isinstance(value, str) or not value.strip():
            fail(f"postImages[{idx}] is empty")
        out[idx] = value.strip()
    return out


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def check_http_200(url: str) -> None:
    if not is_http_url(url):
        fail(f"image URL is not public HTTP(S): {url}")
    req = Request(url, method="HEAD", headers={"User-Agent": "threads-quality-gate/1.0"})
    try:
        with urlopen(req, timeout=20) as resp:
            status = getattr(resp, "status", 200)
            ctype = resp.headers.get("content-type", "")
    except Exception:
        # Some static hosts reject HEAD; retry with GET and read one byte.
        req = Request(url, method="GET", headers={"User-Agent": "threads-quality-gate/1.0"})
        try:
            with urlopen(req, timeout=30) as resp:
                status = getattr(resp, "status", 200)
                ctype = resp.headers.get("content-type", "")
                resp.read(1)
        except Exception as exc:  # noqa: BLE001
            fail(f"image URL not reachable: {url}: {exc}")
    if status < 200 or status >= 300:
        fail(f"image URL returned HTTP {status}: {url}")
    if "image/" not in ctype.lower():
        fail(f"image URL content-type is not image/* ({ctype!r}): {url}")


def check_no_internal_artifacts(post: str, idx: int) -> None:
    """Reject API/debug artifacts that must never become visible Threads copy."""
    lowered = post.lower()
    for marker in INTERNAL_LOG_MARKERS:
        if marker in lowered:
            fail(f"post {idx} contains internal publish/log marker: {marker}")

    match = THREADS_INTERNAL_ID_RE.search(post)
    if match:
        fail(
            f"post {idx} contains a long internal-looking numeric ID "
            f"({match.group(0)}). Threads API IDs belong in logs only, never in post text."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Threads payload before publishing.")
    parser.add_argument("payload", type=Path, help="JSON with posts and postImages fields")
    parser.add_argument("--min-posts", type=int, default=3)
    parser.add_argument("--max-posts", type=int, default=8)
    parser.add_argument("--require-root-image", action="store_true", default=True)
    parser.add_argument("--require-all-url-posts-have-image", action="store_true", default=True)
    parser.add_argument("--check-image-http", action="store_true", default=True)
    args = parser.parse_args()

    payload = load_payload(args.payload)
    posts = payload.get("posts")
    if not isinstance(posts, list):
        fail("payload.posts must be a list")
    posts = [str(p).strip() for p in posts]

    if len(posts) < args.min_posts:
        fail(f"expected at least {args.min_posts} posts; got {len(posts)}. Do not publish root-only/one-card Threads.")
    if len(posts) > args.max_posts:
        fail(f"expected at most {args.max_posts} posts; got {len(posts)}")

    for i, post in enumerate(posts, start=1):
        if not post:
            fail(f"post {i} is empty")
        if len(post) > 500:
            fail(f"post {i} exceeds 500 chars ({len(post)})")
        check_no_internal_artifacts(post, i)

    images = normalize_images(payload.get("postImages") or payload.get("post_images"))
    if args.require_root_image and 1 not in images:
        fail("root post must have an explicit image; never depend on a link preview card")
    if len(images) < 2 and len(posts) >= 4:
        fail("4+ part Threads must attach at least two explicit images")

    for idx in images:
        if idx < 1 or idx > len(posts):
            fail(f"postImages index {idx} is outside post count {len(posts)}")

    root_urls = URL_RE.findall(posts[0])
    if root_urls:
        fail("root post must not contain a bare URL; put the blog link in the final reply with an explicit image or no preview dependency")

    if args.require_all_url_posts_have_image:
        for i, post in enumerate(posts, start=1):
            if URL_RE.search(post) and i not in images:
                fail(f"post {i} contains a URL but has no explicit image; this risks an ugly/blank preview card")

    # Blog link belongs near the end, after the hook/context posts.
    link_posts = [i for i, post in enumerate(posts, start=1) if "jkf87.github.io" in post]
    if link_posts and max(link_posts) < len(posts) - 1:
        fail("blog URL appears too early; keep root/replies focused and put the link in the final or penultimate post")

    if args.check_image_http:
        for idx, url in sorted(images.items()):
            check_http_200(url)

    print(json.dumps({
        "ok": True,
        "posts": len(posts),
        "images": len(images),
        "imagePosts": sorted(images),
        "linkPosts": link_posts,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
