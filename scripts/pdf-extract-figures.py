#!/usr/bin/env python3
"""Extract real Figure/Table regions from academic PDFs.

Unlike the old version, this script does NOT treat page-top screenshots as a
successful figure extraction. It prefers caption-anchored crops and writes
`extract-meta.json` with accepted/rejected status for downstream gates.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen

import fitz

CAPTION_RE = re.compile(r"^\s*(Figure|Fig\.|Table)\s*([0-9]+[A-Za-z]?)\b", re.I)
BAD_TEXT_RE = re.compile(r"^(abstract|introduction|references|appendix|acknowledg|related work)\b", re.I)


@dataclass
class ExtractResult:
    page: int
    file: str = ""
    method: str = ""
    status: str = "rejected"
    reason: str = ""
    size_kb: int = 0
    width: int = 0
    height: int = 0
    caption: str = ""
    crop: list[float] | None = None


def parse_pages(value: str | None, n_pages: int) -> list[int]:
    if not value:
        return list(range(1, n_pages + 1))
    out: list[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = [int(x) for x in part.split("-", 1)]
            out.extend(range(a, b + 1))
        else:
            out.append(int(part))
    return sorted({p for p in out if 1 <= p <= n_pages})


def open_pdf(source: str) -> fitz.Document:
    if source.startswith(("http://", "https://")):
        with urlopen(source, timeout=120) as resp:
            data = resp.read()
        return fitz.open(stream=data, filetype="pdf")
    return fitz.open(source)


def line_text(line: dict) -> str:
    return " ".join(span.get("text", "") for span in line.get("spans", [])).strip()


def text_lines(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
    lines: list[tuple[fitz.Rect, str]] = []
    for block in page.get_text("dict").get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            txt = line_text(line)
            if txt:
                lines.append((fitz.Rect(line["bbox"]), txt))
    return lines


def find_captions(page: fitz.Page) -> list[tuple[fitz.Rect, str, str, str]]:
    caps = []
    for rect, txt in text_lines(page):
        m = CAPTION_RE.match(txt)
        if m:
            caps.append((rect, txt, m.group(1).lower(), m.group(2)))
    return caps


def union_rect(rects: Iterable[fitz.Rect]) -> fitz.Rect | None:
    rects = [r for r in rects if r and r.width > 2 and r.height > 2]
    if not rects:
        return None
    out = fitz.Rect(rects[0])
    for r in rects[1:]:
        out |= r
    return out


def candidate_graphics_above(page: fitz.Page, caption_rect: fitz.Rect) -> list[fitz.Rect]:
    page_rect = page.rect
    y_min = max(0, caption_rect.y0 - page_rect.height * 0.62)
    y_max = caption_rect.y0 - 3
    rects: list[fitz.Rect] = []

    for d in page.get_drawings():
        r = fitz.Rect(d.get("rect"))
        if r.width < 25 or r.height < 12:
            continue
        if r.y1 <= y_min or r.y0 >= y_max:
            continue
        # Avoid tiny text underline/table ruling fragments unless they form a group later.
        rects.append(r)

    for img in page.get_images(full=True):
        xref = img[0]
        try:
            rects.extend(page.get_image_rects(xref))
        except Exception:
            continue

    # Prefer objects horizontally near the caption, but allow full-width tables/figures.
    cap_mid = (caption_rect.x0 + caption_rect.x1) / 2
    filtered = []
    for r in rects:
        r_mid = (r.x0 + r.x1) / 2
        if abs(r_mid - cap_mid) < page_rect.width * 0.45 or r.width > page_rect.width * 0.45:
            filtered.append(r)
    return filtered


def crop_for_caption(page: fitz.Page, caption_rect: fitz.Rect, kind: str) -> tuple[fitz.Rect | None, str]:
    page_rect = page.rect
    graphics = candidate_graphics_above(page, caption_rect)

    if graphics:
        # Keep only graphics in the vertical band closest to the caption.
        graphics.sort(key=lambda r: caption_rect.y0 - r.y1)
        nearest_gap = caption_rect.y0 - graphics[0].y1
        band = [r for r in graphics if (caption_rect.y0 - r.y1) <= nearest_gap + 120]
        g = union_rect(band)
        if g:
            x0 = max(0, min(g.x0, caption_rect.x0) - 12)
            x1 = min(page_rect.width, max(g.x1, caption_rect.x1) + 12)
            y0 = max(0, g.y0 - 12)
            y1 = min(page_rect.height, caption_rect.y1 + 18)
            return fitz.Rect(x0, y0, x1, y1), "caption_crop"

    # Table captions are sometimes above the table; look below too.
    if kind.startswith("table"):
        below = []
        for d in page.get_drawings():
            r = fitz.Rect(d.get("rect"))
            if r.width > 35 and r.height > 10 and caption_rect.y1 < r.y0 < caption_rect.y1 + 260:
                below.append(r)
        g = union_rect(below)
        if g:
            return fitz.Rect(max(0, min(g.x0, caption_rect.x0) - 12), max(0, caption_rect.y0 - 8), min(page_rect.width, max(g.x1, caption_rect.x1) + 12), min(page_rect.height, g.y1 + 12)), "caption_crop_table_below"

    return None, "no_graphics_near_caption"


def validate_crop(page: fitz.Page, crop: fitz.Rect, caption: str, *, allow_large: bool = False) -> tuple[bool, str]:
    pr = page.rect
    area_ratio = (crop.width * crop.height) / (pr.width * pr.height)
    if crop.width < 120 or crop.height < 90:
        return False, f"crop too small ({crop.width:.0f}x{crop.height:.0f}pt)"
    if area_ratio > (0.72 if allow_large else 0.55):
        return False, f"crop too page-like (area_ratio={area_ratio:.2f})"
    if not CAPTION_RE.match(caption):
        return False, "missing figure/table caption"
    if BAD_TEXT_RE.match(caption):
        return False, "caption looked like body section"
    return True, "accepted"


def render_crop(page: fitz.Page, crop: fitz.Rect, out_path: Path, zoom: float) -> tuple[int, int, int]:
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=crop, alpha=False)
    pix.save(out_path)
    return pix.width, pix.height, out_path.stat().st_size // 1024


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract caption-anchored figures/tables from academic PDF")
    parser.add_argument("pdf", help="Path or URL to PDF")
    parser.add_argument("pages", nargs="?", help="Optional pages, e.g. 1,3,5-7. Omit to auto-scan all pages.")
    parser.add_argument("--outdir", default=".")
    parser.add_argument("--zoom", type=float, default=3.0)
    parser.add_argument("--max", type=int, default=8, help="Max accepted crops")
    parser.add_argument("--allow-large", action="store_true", help="Allow large table-like crops")
    parser.add_argument("--allow-fallback", action="store_true", help="Legacy unsafe mode: write page-top fallback crops when no caption crop is found")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    doc = open_pdf(args.pdf)
    pages = parse_pages(args.pages, doc.page_count)
    results: list[ExtractResult] = []
    accepted = 0

    for page_num in pages:
        page = doc[page_num - 1]
        caps = find_captions(page)
        if not caps:
            if args.allow_fallback and accepted < args.max:
                crop = fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.45)
                name = f"fig-p{page_num}-fallback.png"
                w, h, kb = render_crop(page, crop, outdir / name, args.zoom)
                results.append(ExtractResult(page_num, name, f"fallback_top45 ({w}x{h})", "rejected", "fallback is not accepted for publishing", kb, w, h, "", [crop.x0, crop.y0, crop.x1, crop.y1]))
            continue

        for cap_idx, (cap_rect, cap_text, kind, num) in enumerate(caps, start=1):
            if accepted >= args.max:
                break
            crop, method = crop_for_caption(page, cap_rect, kind)
            if not crop:
                results.append(ExtractResult(page_num, method=method, status="rejected", reason="no crop", caption=cap_text))
                continue
            ok, reason = validate_crop(page, crop, cap_text, allow_large=args.allow_large or kind.startswith("table"))
            if not ok:
                results.append(ExtractResult(page_num, method=method, status="rejected", reason=reason, caption=cap_text, crop=[crop.x0, crop.y0, crop.x1, crop.y1]))
                continue
            label = "table" if kind.startswith("table") else "fig"
            safe_num = re.sub(r"[^0-9A-Za-z_-]", "", num)
            name = f"{label}-{safe_num}-p{page_num}.png"
            # Avoid overwrite if multiple captions share number/page.
            if (outdir / name).exists():
                name = f"{label}-{safe_num}-p{page_num}-{cap_idx}.png"
            w, h, kb = render_crop(page, crop, outdir / name, args.zoom)
            results.append(ExtractResult(page_num, name, f"{method} ({w}x{h})", "accepted", reason, kb, w, h, cap_text, [round(crop.x0, 2), round(crop.y0, 2), round(crop.x1, 2), round(crop.y1, 2)]))
            accepted += 1

    doc.close()

    meta_path = outdir / "extract-meta.json"
    meta_path.write_text(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for r in results:
        if r.file:
            print(f"  p{r.page}: {r.status} {r.method} -> {r.file} ({r.size_kb}KB) {r.caption[:80]}")
        else:
            print(f"  p{r.page}: {r.status} {r.method} ({r.reason}) {r.caption[:80]}")

    if accepted == 0:
        print(f"No accepted figure/table crops. See {meta_path}", file=sys.stderr)
        return 2
    print(f"\nAccepted {accepted} figure/table crop(s) -> {outdir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
