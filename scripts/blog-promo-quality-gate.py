#!/usr/bin/env python3
"""Gate for the standing soft CTA on agent/automation blog posts.

Relevant posts must include the OpenClaw book and Loop Engineering lecture note.
This script is intentionally simple and local so cron publishing cannot skip it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BOOK_TITLE = "이게 되네? 오픈클로 미친 활용법 50제"
BOOK_URL = "https://product.kyobobook.co.kr/detail/S000219615902"
LECTURE_TITLE = "모두를 위한 루프 엔지니어링"
LECTURE_URL = "https://aifrenz.liveklass.com/classes/309184"
SOFT_HEADING = "더 실습해보고 싶은 분들께"

RELEVANCE_TERMS = [
    "에이전트", "agent", "agents", "agentic",
    "자동화", "automation",
    "하네스", "harness",
    "루프", "loop",
    "도구", "tool", "MCP",
    "RL", "GRPO", "long-context", "긴 컨텍스트",
]
EXEMPT_TERMS = ["건강", "혈압", "당뇨", "간수치", "치과", "수면", "역사"]


def fail(message: str) -> None:
    print(f"blog-promo-quality-gate: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def looks_relevant(text: str) -> bool:
    lower = text.lower()
    hits = sum(1 for term in RELEVANCE_TERMS if term.lower() in lower)
    if hits == 0:
        return False
    if hits == 1 and any(term in text for term in EXEMPT_TERMS):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("markdown")
    parser.add_argument("--require-relevant", action="store_true", help="fail if relevance terms are absent")
    args = parser.parse_args()

    path = Path(args.markdown)
    if not path.exists():
        fail(f"markdown not found: {path}")
    text = path.read_text(encoding="utf-8")
    relevant = looks_relevant(text)
    if args.require_relevant and not relevant:
        fail("post does not look agent/automation/harness/loop relevant")
    if not relevant:
        print("blog-promo-quality-gate: SKIP: not relevant")
        return 0

    missing = [
        label for label, needle in [
            ("soft heading", SOFT_HEADING),
            ("book title", BOOK_TITLE),
            ("book url", BOOK_URL),
            ("lecture title", LECTURE_TITLE),
            ("lecture url", LECTURE_URL),
        ] if needle not in text
    ]
    if missing:
        fail("missing " + ", ".join(missing))
    print("blog-promo-quality-gate: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
