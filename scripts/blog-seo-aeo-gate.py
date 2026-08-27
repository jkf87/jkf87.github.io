#!/usr/bin/env python3
"""SEO/AEO/GEO structural gate for Korean Quartz blog posts.

This is a deterministic pre-publish gate inspired by the fire-your-seo-agency
playbook. It does not promise ranking. It checks whether a post is structured so
search crawlers and answer engines can extract a direct, source-backed answer.

Usage:
    python3 scripts/blog-seo-aeo-gate.py content/posts/<slug>.md
    python3 scripts/blog-seo-aeo-gate.py content/posts/<slug>.md --strict
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

URL_RE = re.compile(r"https?://[^\s)>'\"]+")
DATE_RE = re.compile(r"20\d{2}[-./년]\s?\d{1,2}[-./월]\s?\d{0,2}|20\d{2}년|\d{4}-\d{2}-\d{2}")
QUESTION_RE = re.compile(r"[?？]|(무엇|왜|어떻게|언제|얼마나|가능한가|다른가|한계|방법|이유)")

REQUIRED_FRONTMATTER = ["title", "date", "tags", "draft", "description"]
SOURCE_HINTS = [
    "arxiv.org", "openreview.net", "github.com", "huggingface.co", "doi.org",
    "youtube.com", "youtu.be", "blog.google", "openai.com", "anthropic.com",
    "microsoft.com", "naver.com", "출처", "원문", "논문", "공개",
]


def fail(message: str) -> None:
    print(f"blog-seo-aeo-gate: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def info(message: str) -> None:
    print(f"blog-seo-aeo-gate: {message}")


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return {}, text
    fm_text = match.group(1)
    body = text[match.end():]
    fm: dict[str, str] = {}
    current_key: str | None = None
    for line in fm_text.splitlines():
        if not line.strip():
            continue
        if re.match(r"^\s+-\s+", line) and current_key:
            fm[current_key] = (fm.get(current_key, "") + " " + line.strip()).strip()
            continue
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            current_key = key.strip()
            fm[current_key] = val.strip().strip('"').strip("'")
    return fm, body


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def first_meaningful_paragraph(body: str) -> str:
    body = re.sub(r"^# .*$", "", body, flags=re.MULTILINE)
    parts = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    for part in parts:
        if part.startswith("!") or part.startswith("|") or part.startswith("-"):
            continue
        if part.startswith("##") and len(parts) > 1:
            continue
        clean = strip_markdown(re.sub(r"^#{1,6}\s*", "", part))
        if len(clean) >= 35:
            return clean
    return ""


def has_markdown_table(body: str) -> bool:
    lines = body.splitlines()
    for i in range(len(lines) - 1):
        if "|" in lines[i] and re.search(r"\|?\s*:?-{3,}:?\s*\|", lines[i + 1]):
            return True
    return False


def faq_question_count(body: str) -> int:
    faq_match = re.search(r"^##\s*(자주 묻는 질문|FAQ|검색 질문|함께 물어볼 질문).*?(?=^##\s|\Z)", body, re.M | re.S | re.I)
    if not faq_match:
        return 0
    section = strip_markdown(faq_match.group(0))
    # Count explicit question-like list items/headings, not every occurrence of 왜/무엇 in prose.
    count = 0
    for line in section.splitlines():
        line = line.strip(" -*#\t")
        if len(line) >= 8 and QUESTION_RE.search(line):
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="SEO/AEO/GEO structural gate for Quartz blog posts")
    parser.add_argument("markdown")
    parser.add_argument("--strict", action="store_true", help="fail on warnings as well as hard errors")
    args = parser.parse_args()

    path = Path(args.markdown)
    if not path.exists():
        fail(f"markdown not found: {path}")

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)
    clean_body = strip_markdown(body)
    issues: list[str] = []
    warnings: list[str] = []

    missing = [key for key in REQUIRED_FRONTMATTER if key not in fm or not str(fm.get(key, "")).strip()]
    if missing:
        issues.append("missing frontmatter: " + ", ".join(missing))

    title = fm.get("title", "")
    if title:
        if len(title) < 22:
            warnings.append("title may be too short for search intent (<22 chars)")
        if len(title) > 80:
            warnings.append("title may be too long for search display (>80 chars)")
        if not QUESTION_RE.search(title) and not any(ch.isdigit() for ch in title):
            warnings.append("title lacks question/search-intent wording or a concrete number")

    desc = fm.get("description", "")
    if desc:
        if len(desc) < 70:
            warnings.append("description is short; target roughly 70-160 Korean chars")
        if len(desc) > 180:
            warnings.append("description is long; target roughly 70-160 Korean chars")

    body_h1 = re.findall(r"^#\s+", body, flags=re.M)
    if body_h1:
        issues.append("body contains # H1; Quartz already renders frontmatter title as H1, use ## inside the post")

    first_para = first_meaningful_paragraph(body)
    first_window = strip_markdown("\n".join(body.splitlines()[:18]))
    if not first_para:
        issues.append("no readable opening paragraph")
    else:
        if len(first_para) > 650:
            warnings.append("opening paragraph is long; answer engines prefer a short direct answer first")
        if not any(needle in first_window for needle in ["결론", "핵심", "요약", "정리하면", "이 글은", "이 논문은", "이 모델은", "이 시스템은", "이 프레임워크는"]):
            issues.append("opening section does not look like a direct answer/summary")
        if not (DATE_RE.search(first_para) or DATE_RE.search(clean_body[:1200]) or fm.get("date")):
            issues.append("no visible baseline date near the top")

    if not has_markdown_table(body):
        issues.append("no markdown table; add an item-value summary table for AEO/NEO extraction")

    urls = URL_RE.findall(text)
    if not urls:
        issues.append("no source URL found")
    elif not any(any(hint.lower() in text.lower() for hint in SOURCE_HINTS) for _ in [0]):
        warnings.append("URLs exist, but source/original context is weak")

    fq = faq_question_count(body)
    if fq < 3:
        issues.append(f"FAQ/search-question section has {fq} question-like items; need at least 3")

    if "기준" not in clean_body and not DATE_RE.search(clean_body):
        warnings.append("few explicit 기준일/date signals in body")

    info(f"post: {path}")
    info(f"title chars: {len(title) if title else 0} | description chars: {len(desc) if desc else 0} | urls: {len(urls)} | FAQ questions: {fq}")

    for warning in warnings:
        info("WARN: " + warning)

    if issues:
        for issue in issues:
            print("blog-seo-aeo-gate: ISSUE: " + issue, file=sys.stderr)
        fail(f"{len(issues)} hard issue(s)")

    if args.strict and warnings:
        fail(f"{len(warnings)} warning(s) in --strict mode")

    print("blog-seo-aeo-gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
