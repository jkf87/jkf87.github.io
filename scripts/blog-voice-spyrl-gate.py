#!/usr/bin/env python3
"""SpyRL-inspired style gate for conanssam blog drafts.

This is not model training. It converts the fuzzy question
"does this match ConanSam's approved blog voice?" into a small
self-verifiable comparison game:
- score each candidate against the kakao/plain blog overlay
- identify the most suspicious "spy" candidate
- recommend the least-suspicious draft
- write a JSON report that can be accumulated as voice feedback

Usage:
  python3 scripts/blog-voice-spyrl-gate.py content/posts/a.md [content/posts/b.md ...] \
    --out ../memory/voice-feedback/report.json

Exit codes:
  0: winner is publishable
  1: no candidate passes the minimum style threshold
  2: usage/input error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

BANNED = {
    "알아보겠습니다": "AI식 예고문",
    "하지만": "딱딱한 전환어",
    "첫째": "상투적 순서표현",
    "둘째": "상투적 순서표현",
    "셋째": "상투적 순서표현",
    "넷째": "상투적 순서표현",
    "마지막으로": "상투적 마무리",
    "결론적으로": "요약형 봉합",
}

# A가 아니라 B다 aphorism frame. 구어 "그게 아니라"는 문맥상 예외로 둔다.
APHORISM_RE = re.compile(r"(?<!그게 )(?<!그건 )(?<!이게 )(?<!아 그게 )가 아니라")
BOLD_RE = re.compile(r"\*\*[^*]+\*\*")
HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.M)
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
TABLE_LINE_RE = re.compile(r"^\s*\|.+\|\s*$", re.M)

GOOD_PATTERNS = {
    "핵심은 이겁니다": 2.0,
    "정리했습니다": 1.5,
    "입니다": 0.4,
    "합니다": 0.4,
    "근데": 0.8,
    "구요": 0.8,
    "보시면 됩니다": 1.0,
    "하면 됩니다": 1.0,
    "해보시면": 0.8,
}

AVOID_TAGS = {
    "too_long_paragraph": "문단 김",
    "banned_phrase": "금지 표현",
    "aphorism": "A가 아니라 B다 프레임",
    "bold_overuse": "볼드 과함",
    "no_images": "이미지 없음",
    "few_numbers": "실물/수치 부족",
    "grand_closing": "여운형 마무리",
    "question_heading": "자문자답 제목",
    "metaphor_heading": "은유형 제목 의심",
}

GRAND_CLOSINGS = [
    "남깁니다", "기억해야 합니다", "시대가 옵니다", "질문입니다", "첫 줄이 됩니다",
    "바꿔놓을 겁니다", "새로운 기준입니다",
]

@dataclass
class CandidateReport:
    path: str
    score: float
    suspicion: float
    grade: str
    tags: list[str]
    counts: dict[str, int | float]
    notes: list[str]


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def paragraphs(body: str) -> list[str]:
    paras = []
    current = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            if current:
                paras.append(" ".join(current).strip())
                current = []
            continue
        if s.startswith(("#", "- ", "* ", ">", "|")) or re.match(r"\d+[.)]\s", s):
            if current:
                paras.append(" ".join(current).strip())
                current = []
            paras.append(s)
        else:
            current.append(s)
    if current:
        paras.append(" ".join(current).strip())
    return [p for p in paras if p]


def grade_from_score(score: float) -> str:
    if score >= 82:
        return "A"
    if score >= 70:
        return "B"
    if score >= 58:
        return "C"
    return "D"


def evaluate(path: Path) -> CandidateReport:
    raw = path.read_text(encoding="utf-8")
    body = strip_frontmatter(raw)
    ps = paragraphs(body)
    para_lens = [len(p) for p in ps if not p.startswith(("#", "|"))]
    avg_para = mean(para_lens) if para_lens else 0
    long_paras = sum(1 for n in para_lens if n > 260)
    very_long_paras = sum(1 for n in para_lens if n > 420)
    banned_counts = {k: body.count(k) for k in BANNED}
    aphorism = len(APHORISM_RE.findall(body))
    bold = len(BOLD_RE.findall(body))
    images = IMAGE_RE.findall(body)
    abs_image_bad = sum(1 for img in images if not img.startswith("/images/"))
    headings = HEADING_RE.findall(body)
    question_headings = sum(1 for h in headings if "?" in h or "까요" in h or "나요" in h)
    # rough metaphor signal: headings with em dash or poetic commas and no concrete tech nouns/numbers
    concrete_words = ["Task", "Harness", "Verifier", "Reward", "RL", "LLM", "환경", "모델", "결과", "실험", "코드", "수치", "방법", "구조", "데이터"]
    metaphor_headings = 0
    for h in headings:
        if ("—" in h or "-" in h or "," in h) and not any(w in h for w in concrete_words):
            metaphor_headings += 1
    numbers = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", body))
    tables = len(TABLE_LINE_RE.findall(body))
    good_hits = {k: body.count(k) for k in GOOD_PATTERNS}
    good_score = sum(GOOD_PATTERNS[k] * v for k, v in good_hits.items())

    score = 74.0
    notes: list[str] = []
    tags: list[str] = []

    penalty = 0.0
    banned_total = sum(banned_counts.values())
    if banned_total:
        penalty += 9 * banned_total
        tags.append("banned_phrase")
        notes.append(f"금지 표현 {banned_total}회")
    if aphorism:
        penalty += 10 * aphorism
        tags.append("aphorism")
        notes.append(f"A가 아니라 B다 프레임 {aphorism}회")
    if bold > 4:
        penalty += min(18, (bold - 4) * 2.5)
        tags.append("bold_overuse")
        notes.append(f"bold {bold}회")
    elif bold:
        penalty += bold * 0.5
    if long_paras:
        penalty += long_paras * 2.0 + very_long_paras * 3.0
        tags.append("too_long_paragraph")
        notes.append(f"긴 문단 {long_paras}개, 매우 긴 문단 {very_long_paras}개")
    if not images:
        penalty += 8
        tags.append("no_images")
        notes.append("이미지 없음")
    if abs_image_bad:
        penalty += 6 * abs_image_bad
        notes.append(f"Quartz 절대 이미지 경로 위반 {abs_image_bad}개")
    if numbers < 8 and tables < 4:
        penalty += 4
        tags.append("few_numbers")
        notes.append("수치/표가 적음")
    if question_headings:
        penalty += 2.5 * question_headings
        tags.append("question_heading")
        notes.append(f"자문자답형 제목 {question_headings}개")
    if metaphor_headings:
        penalty += 2.0 * metaphor_headings
        tags.append("metaphor_heading")
        notes.append(f"은유형 제목 의심 {metaphor_headings}개")
    tail = "\n".join([p for p in ps[-4:] if p])
    if any(x in tail for x in GRAND_CLOSINGS):
        penalty += 3
        tags.append("grand_closing")
        notes.append("여운형 마무리 의심")

    bonus = min(12, good_score)
    if avg_para and avg_para <= 180:
        bonus += 4
    elif avg_para <= 230:
        bonus += 2
    if images:
        bonus += min(5, len(images))
    if numbers >= 12:
        bonus += 3
    if tables >= 4:
        bonus += 2

    score = max(0.0, min(100.0, score + bonus - penalty))
    suspicion = max(0.0, min(100.0, 100 - score + penalty * 0.15))
    tags = sorted(set(tags))
    counts = {
        "paragraphs": len(ps),
        "avg_paragraph_chars": round(avg_para, 1),
        "long_paragraphs": long_paras,
        "very_long_paragraphs": very_long_paras,
        "banned_total": banned_total,
        "aphorism_frame": aphorism,
        "bold_spans": bold,
        "images": len(images),
        "bad_image_paths": abs_image_bad,
        "numbers": numbers,
        "table_lines": tables,
        "question_headings": question_headings,
        "metaphor_headings": metaphor_headings,
    }
    counts.update({f"phrase:{k}": v for k, v in banned_counts.items() if v})
    return CandidateReport(
        path=str(path),
        score=round(score, 2),
        suspicion=round(suspicion, 2),
        grade=grade_from_score(score),
        tags=tags,
        counts=counts,
        notes=notes or ["큰 문체 위반 없음"],
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidates", nargs="+", help="Markdown candidate files")
    ap.add_argument("--out", help="Write JSON report")
    ap.add_argument("--min-score", type=float, default=70.0)
    ap.add_argument("--allow-single", action="store_true", help="Allow one candidate; still scores it")
    args = ap.parse_args()

    paths = [Path(p) for p in args.candidates]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        print(json.dumps({"error": "missing candidates", "missing": missing}, ensure_ascii=False), file=sys.stderr)
        return 2
    if len(paths) < 2 and not args.allow_single:
        print(json.dumps({"error": "need at least 2 candidates or --allow-single"}, ensure_ascii=False), file=sys.stderr)
        return 2

    reports = [evaluate(p) for p in paths]
    ranked = sorted(reports, key=lambda r: (r.score, -r.suspicion), reverse=True)
    spy = sorted(reports, key=lambda r: (r.suspicion, -r.score), reverse=True)[0]
    winner = ranked[0]
    passed = winner.score >= args.min_score and winner.grade in {"A", "B"}
    result = {
        "kind": "blog-voice-spyrl-gate",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "policy": "conanssam-voice kakao/plain blog overlay",
        "passed": passed,
        "winner": winner.path,
        "winnerScore": winner.score,
        "winnerGrade": winner.grade,
        "spy": spy.path,
        "spySuspicion": spy.suspicion,
        "spyTags": spy.tags,
        "candidates": [asdict(r) for r in reports],
        "recommendation": "publish winner" if passed else "revise winner before publish",
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
