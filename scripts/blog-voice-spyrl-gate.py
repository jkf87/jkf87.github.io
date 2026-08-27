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

# Korean no-ai-slop overlay. These are suspicious patterns, not hard bans:
# the goal is to flag "AI-smooth" blog prose while preserving ConanSam's plain voice.
KOREAN_SLOP_PHRASES = {
    "결국 중요한 것은": "generic_takeaway",
    "중요한 것은": "generic_takeaway",
    "핵심은 바로": "faux_insight_setup",
    "시사점은 명확합니다": "fake_clarity",
    "단순한 기술 변화가 아닙니다": "binary_contrast",
    "단순한 변화가 아닙니다": "binary_contrast",
    "의미가 큽니다": "importance_puffery",
    "중요한 전환점": "importance_puffery",
    "새로운 패러다임": "importance_puffery",
    "패러다임이 바뀌": "importance_puffery",
    "게임 체인저": "importance_puffery",
    "혁신적인": "importance_puffery",
    "앞으로의 AI 시대": "era_diagnosis",
    "AI 시대에는": "era_diagnosis",
    "이 글에서는": "throat_clearing",
    "살펴보겠습니다": "throat_clearing",
    "한마디로": "faux_simplifier",
    "쉽게 말해": "faux_simplifier",
    "놀라운 점은": "faux_insight_setup",
    "여기서 끝이 아닙니다": "dramatic_fragment",
    "미래는 이미": "fake_profound_ending",
    "미래가 이미": "fake_profound_ending",
    "많은 연구자": "weasel_attribution",
    "업계에서는": "weasel_attribution",
    "전문가들은": "weasel_attribution",
    "정도로 넓혀도": "gpt5x_ai_diction",
    "N건 수준": "gpt5x_ai_diction",
    "건 수준이라": "gpt5x_ai_diction",
    "넓히": "gpt5x_ai_diction",
    "좁히": "gpt5x_ai_diction",
    "열어": "gpt5x_ai_diction",
    "열고": "gpt5x_ai_diction",
    "열 수": "gpt5x_ai_diction",
    "닫아": "gpt5x_ai_diction",
    "닫고": "gpt5x_ai_diction",
    "닫습니다": "gpt5x_ai_diction",
    "굴리": "gpt5x_ai_diction",
    "두께": "gpt5x_ai_diction",
    "두텁": "gpt5x_ai_diction",
    "척추": "gpt5x_ai_diction",
    "지는 않았습니다": "gpt5x_ai_diction",
    "쪽이었고": "gpt5x_ai_diction",
    "가 아니라": "gpt5x_ai_diction",
    "가 아닌": "gpt5x_ai_diction",
    "하기보다": "gpt5x_ai_diction",
    "로 봅니다": "gpt5x_ai_diction",
    "로 보지 않고": "gpt5x_ai_diction",
    "그 위에서": "gpt5x_ai_diction",
    " 위에서": "gpt5x_ai_diction",
    "로 자리합니다": "gpt5x_ai_diction",
    "에 자연스럽게 맞습니다": "gpt5x_ai_diction",
    "가 잘 맞습니다": "gpt5x_ai_diction",
    "하는 공간으로": "gpt5x_ai_diction",
    "을 보장하며": "gpt5x_ai_diction",
    "을 반영하며": "gpt5x_ai_diction",
    "일 수도 있다고 볼 수도 있습니다": "gpt5x_ai_diction",
    "역할을 합니다": "gpt5x_ai_diction",
}

# A가 아니라 B다 aphorism frame. 구어 "그게 아니라"는 문맥상 예외로 둔다.
APHORISM_RE = re.compile(r"(?<!그게 )(?<!그건 )(?<!이게 )(?<!아 그게 )가 아니라")
NOT_X_BUT_Y_RE = re.compile(r"(?:이|그|단순한|단지|그저)?[^.!?\n]{0,35}(?:이|가|은|는)\s+아니(?:라|고)[^.!?\n]{0,60}(?:이다|입니다|한다|합니다|된다|됩니다)")
RHETORICAL_QA_RE = re.compile(r"[^\n?.!]{2,45}\?\s*(?:아닙니다|맞습니다|그렇습니다|이겁니다|바로|결국)")
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
    "korean_ai_slop": "한국어 AI slop 표현",
    "binary_contrast": "대구/이분법 프레임",
    "aphorism": "A가 아니라 B다 프레임",
    "rhetorical_qa": "자문자답 문장",
    "importance_puffery": "의미부여/과장어",
    "era_diagnosis": "시대 진단 문장",
    "weasel_attribution": "출처 없는 일반화",
    "bold_overuse": "볼드 과함",
    "no_images": "이미지 없음",
    "few_numbers": "실물/수치 부족",
    "grand_closing": "여운형 마무리",
    "question_heading": "자문자답 제목",
    "metaphor_heading": "은유형 제목 의심",
    "gpt5x_ai_diction": "GPT 5.x/Opus/Fable식 AI 말투",
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
    slop_counts = {k: body.count(k) for k in KOREAN_SLOP_PHRASES}
    slop_by_category: dict[str, int] = {}
    for phrase, category in KOREAN_SLOP_PHRASES.items():
        slop_by_category[category] = slop_by_category.get(category, 0) + slop_counts[phrase]
    aphorism = len(APHORISM_RE.findall(body))
    binary_contrast = len(NOT_X_BUT_Y_RE.findall(body))
    rhetorical_qa = len(RHETORICAL_QA_RE.findall(body))
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
    slop_total = sum(slop_counts.values())
    if banned_total:
        penalty += 9 * banned_total
        tags.append("banned_phrase")
        notes.append(f"금지 표현 {banned_total}회")
    if slop_total:
        penalty += min(28, 3.5 * slop_total)
        tags.append("korean_ai_slop")
        notes.append(f"한국어 AI slop 표현 {slop_total}회")
        for category, count in sorted(slop_by_category.items()):
            if not count:
                continue
            tags.append(category if category in AVOID_TAGS else "korean_ai_slop")
    if aphorism:
        penalty += 10 * aphorism
        tags.append("aphorism")
        notes.append(f"A가 아니라 B다 프레임 {aphorism}회")
    if binary_contrast:
        penalty += 5 * binary_contrast
        tags.append("binary_contrast")
        notes.append(f"대구/이분법 문장 {binary_contrast}회")
    if rhetorical_qa:
        penalty += 4 * rhetorical_qa
        tags.append("rhetorical_qa")
        notes.append(f"자문자답 문장 {rhetorical_qa}회")
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
        "korean_slop_total": slop_total,
        "aphorism_frame": aphorism,
        "binary_contrast": binary_contrast,
        "rhetorical_qa": rhetorical_qa,
        "bold_spans": bold,
        "images": len(images),
        "bad_image_paths": abs_image_bad,
        "numbers": numbers,
        "table_lines": tables,
        "question_headings": question_headings,
        "metaphor_headings": metaphor_headings,
    }
    counts.update({f"phrase:{k}": v for k, v in banned_counts.items() if v})
    counts.update({f"slop:{k}": v for k, v in slop_counts.items() if v})
    counts.update({f"slop_category:{k}": v for k, v in slop_by_category.items() if v})
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
