#!/usr/bin/env python3
"""Quality gate for Quartz blog images extracted from papers.

Rejects page-top screenshots, fallback crops, tiny/illegible figures, huge likely-full-page
raster dumps, and markdown image refs that do not resolve.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat

IMG_REF_RE = re.compile(r"!\[[^\]]*\]\((/images/[^)]+)\)")
BAD_METHOD_RE = re.compile(r"fallback|top45|page(?:_|-)?crop|full(?:_|-)?page", re.I)
GOOD_METHOD_RE = re.compile(r"caption_crop|embedded_crop|vector_crop|html|source|official", re.I)


def fail(msg: str) -> None:
    print(f"blog-image-quality-gate: FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def warn(msg: str) -> None:
    print(f"blog-image-quality-gate: WARN: {msg}", file=sys.stderr)


def image_stats(path: Path) -> dict[str, Any]:
    try:
        im = Image.open(path).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot open image {path}: {exc}")
    w, h = im.size
    stat = ImageStat.Stat(im)
    mean = sum(stat.mean) / 3
    extrema = im.convert("L").getextrema()
    contrast = extrema[1] - extrema[0]
    return {"width": w, "height": h, "mean": mean, "contrast": contrast, "bytes": path.stat().st_size}


def load_meta(imgdir: Path) -> list[dict[str, Any]]:
    meta_path = imgdir / "extract-meta.json"
    if not meta_path.exists():
        return []
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(f"cannot parse {meta_path}: {exc}")
    if not isinstance(data, list):
        fail(f"{meta_path} must contain a list")
    return [x for x in data if isinstance(x, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate extracted blog images before publish")
    parser.add_argument("post", type=Path, help="Quartz markdown post")
    parser.add_argument("--site-root", type=Path, default=Path("."))
    parser.add_argument("--paper", action="store_true", help="Require paper Figure/Table quality")
    parser.add_argument("--min-images", type=int, default=1)
    parser.add_argument("--min-width", type=int, default=700)
    parser.add_argument("--min-height", type=int, default=350)
    parser.add_argument("--max-dimension", type=int, default=6000)
    parser.add_argument("--allow-fallback", action="store_true")
    args = parser.parse_args()

    post = args.post
    if not post.exists():
        fail(f"post not found: {post}")
    site_root = args.site_root.resolve()
    text = post.read_text(encoding="utf-8", errors="replace")
    refs = IMG_REF_RE.findall(text)
    if len(refs) < args.min_images:
        fail(f"expected at least {args.min_images} markdown image refs; got {len(refs)}")

    checked = []
    good_paper_images = 0
    bads = []

    for ref in refs:
        rel = ref.removeprefix("/images/")
        path = site_root / "content" / "images" / rel
        if not path.exists():
            bads.append(f"missing image ref {ref} -> {path}")
            continue
        st = image_stats(path)
        if st["width"] < args.min_width or st["height"] < args.min_height:
            bads.append(f"too small/likely illegible {ref}: {st['width']}x{st['height']}")
        if st["width"] > args.max_dimension or st["height"] > args.max_dimension:
            bads.append(f"suspicious huge/full-page raster {ref}: {st['width']}x{st['height']}")
        if st["contrast"] < 25 or st["mean"] > 248:
            bads.append(f"blank/low-contrast image {ref}: mean={st['mean']:.1f}, contrast={st['contrast']}")

        imgdir = path.parent
        meta = load_meta(imgdir)
        by_file = {m.get("file"): m for m in meta}
        m = by_file.get(path.name)
        method = str(m.get("method", "")) if m else ""
        status = str(m.get("status", "")) if m else ""
        if method and BAD_METHOD_RE.search(method) and not args.allow_fallback:
            bads.append(f"fallback/page screenshot method used by referenced image {ref}: {method}")
        if status and status not in {"accepted", "ok"}:
            bads.append(f"referenced image {ref} has non-accepted status: {status}")
        if args.paper:
            if (m and GOOD_METHOD_RE.search(method) and not BAD_METHOD_RE.search(method)) or not meta:
                good_paper_images += 1
        checked.append({"ref": ref, **st, "method": method, "status": status})

    if args.paper and good_paper_images < args.min_images:
        bads.append(f"paper post needs at least {args.min_images} accepted original Figure/Table images; got {good_paper_images}")

    if bads:
        for b in bads:
            print(f" - {b}", file=sys.stderr)
        fail(f"{len(bads)} image quality issue(s)")

    print(json.dumps({"ok": True, "refs": len(refs), "checked": checked}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
