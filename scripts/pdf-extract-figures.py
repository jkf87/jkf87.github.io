#!/usr/bin/env python3
"""
pdf-extract-figures.py — 학술 논문 PDF에서 Figure 영역을 크롭하는 스크립트

사용법:
  python3 pdf-extract-figures.py <pdf_path> <page_numbers> [--outdir DIR] [--zoom 3]

예시:
  python3 pdf-extract-figures.py paper.pdf 3,8,28 --outdir content/images/paper-slug
"""
import fitz
import re
import os
import sys
import json
import argparse


def find_figure_region(page):
    """페이지에서 벡터 그래픽 Figure 영역과 캡션 위치를 찾는다."""
    page_rect = page.rect
    drawings = page.get_drawings()
    
    # 충분히 큰 drawing만 필터
    big_draws = [d for d in drawings if d["rect"].width > 40 and d["rect"].height > 20]
    
    if not big_draws:
        return None, None
    
    # y 기준 클러스터링 (간격 < 30pt)
    big_draws.sort(key=lambda d: d["rect"].y0)
    groups = [[big_draws[0]]]
    for i in range(1, len(big_draws)):
        if big_draws[i]["rect"].y0 - groups[-1][-1]["rect"].y1 < 30:
            groups[-1].append(big_draws[i])
        else:
            groups.append([big_draws[i]])
    
    # 가장 큰 면적 그룹 = Figure
    best = max(groups, key=lambda g: sum(d["rect"].width * d["rect"].height for d in g))
    fig_y0 = min(d["rect"].y0 for d in best) - 10
    fig_y1 = max(d["rect"].y1 for d in best) + 10
    fig_x0 = max(0, min(d["rect"].x0 for d in best) - 10)
    fig_x1 = min(page_rect.width, max(d["rect"].x1 for d in best) + 10)
    
    # Figure 캡션 찾기
    caption_y_end = fig_y1
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            text = " ".join([s["text"] for s in line["spans"]]).strip()
            if re.match(r'^(Figure|Fig\.)\s*\d+', text, re.IGNORECASE):
                ly = line["bbox"][3]
                if abs(ly - fig_y1) < 80:
                    caption_y_end = ly + 5
    
    crop_y1 = max(fig_y1, caption_y_end) + 10
    
    region = fitz.Rect(fig_x0, max(0, fig_y0), fig_x1, min(page_rect.height, crop_y1))
    if region.height < 150:
        region.y1 = region.y0 + 180
    
    return region, best


def extract_embedded_images(doc, page):
    """페이지에서 임베드된 래스터 이미지를 추출한다."""
    images = page.get_images(full=True)
    if not images:
        return None
    
    best = None
    best_area = 0
    for img_info in images:
        xref = img_info[0]
        base_image = doc.extract_image(xref)
        if base_image:
            area = base_image["width"] * base_image["height"]
            if area > best_area:
                best_area = area
                best = base_image
    
    # 너무 작은 이미지 (로고/아이콘) 제외
    if best and best["width"] > 200 and best["height"] > 150:
        return best
    return None


def main():
    parser = argparse.ArgumentParser(description="Extract figures from academic PDF")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("pages", help="Comma-separated page numbers (1-indexed)")
    parser.add_argument("--outdir", default=".", help="Output directory")
    parser.add_argument("--zoom", type=float, default=3, help="Zoom factor for rendering")
    args = parser.parse_args()
    
    os.makedirs(args.outdir, exist_ok=True)
    doc = fitz.open(args.pdf)
    pages = [int(p.strip()) for p in args.pages.split(",")]
    mat = fitz.Matrix(args.zoom, args.zoom)
    
    results = []
    
    for page_num in pages:
        page = doc[page_num - 1]
        out_name = f"fig-p{page_num}.png"
        out_path = os.path.join(args.outdir, out_name)
        
        # 전략 1: 임베드 이미지 추출 (벡터가 아닌 래스터 이미지)
        embedded = extract_embedded_images(doc, page)
        
        # 전략 2: 벡터 그래픽 Figure 영역 크롭
        region, draw_group = find_figure_region(page)
        
        if embedded and embedded["width"] > 300:
            # 래스터 이미지가 충분히 크면 사용
            ext = embedded["ext"]
            img_bytes = embedded["image"]
            out_name = f"fig-p{page_num}.{ext}"
            out_path = os.path.join(args.outdir, out_name)
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            method = f"embedded ({embedded['width']}x{embedded['height']})"
        elif region and region.width > 100:
            # 벡터 Figure 영역 렌더링
            pix = page.get_pixmap(matrix=mat, clip=region)
            pix.save(out_path)
            method = f"vector_crop ({pix.width}x{pix.height})"
        else:
            # 폴백: 페이지 상단 45% 렌더링
            pr = page.rect
            crop = fitz.Rect(0, 0, pr.width, pr.height * 0.45)
            pix = page.get_pixmap(matrix=mat, clip=crop)
            pix.save(out_path)
            method = f"fallback_top45 ({pix.width}x{pix.height})"
        
        size_kb = os.path.getsize(out_path) // 1024
        results.append({
            "page": page_num,
            "file": out_name,
            "method": method,
            "size_kb": size_kb
        })
        print(f"  p{page_num}: {method} → {out_name} ({size_kb}KB)")
    
    doc.close()
    
    # 메타데이터 저장
    meta_path = os.path.join(args.outdir, "extract-meta.json")
    with open(meta_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nExtracted {len(results)} figures → {args.outdir}/")
    return results


if __name__ == "__main__":
    main()
