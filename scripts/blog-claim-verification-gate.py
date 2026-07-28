#!/usr/bin/env python3
"""Claim verification gate for blog posts.

Extracts factual claims from a Korean Quartz markdown post, checks for
red flags (unsupported superlatives, weasel words, missing source), and
outputs a structured claim list for the agent to verify against the source.

This gate is intentionally deterministic — it cannot do semantic verification
(that is the agent's job), but it CAN catch structural issues and provide
a systematic checklist that makes verification tractable.

Usage:
    python3 blog-claim-verification-gate.py content/posts/<slug>.md
    python3 blog-claim-verification-gate.py content/posts/<slug>.md --source-url https://...
    python3 blog-claim-verification-gate.py content/posts/<slug>.md --strict
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ── Red flag patterns ──────────────────────────────────────────────

# Superlatives that often mask unsupported claims
SUPERLATIVES = [
    "최고의", "가장 완벽한", "혁신적인", "혁명적인", "절대적으로",
    "100%", "무조건", "완벽하게", "단연코", "압도적으로",
    "전례 없는", "상상 초월", "게임 체인저", "패러다임 전환",
]

# Weasel words that dilute or obscure claims
WEASEL_WORDS = [
    "일부 전문가들은", "많은 사람들이", "업계에서는", "관찰자들은",
    "관련 업계에 따르면", "소문에 따르면", "알려진 바에 따르면",
    "일반적으로", "대체로", "대부분",
]

# Unverifiable hedges that should be replaced with specifics
VAGUE_HEDGES = [
    "상당한", "큰", "많은", "꽤", "어느 정도", "다소",
]

# Source reference patterns — the post must cite where claims come from
SOURCE_PATTERNS = [
    r"https?://arxiv\.org/abs/",
    r"https?://arxiv\.org/pdf/",
    r"https?://www\.youtube\.com/watch",
    r"https?://youtu\.be/",
    r"https?://[^\s]+\.com/[^\s]+",  # general URL
    r"이미지 출처",
    r"출처\s*:",
    r"참고문헌",
    r"원문\s*:",
]

# Claim-bearing patterns — sentences likely to contain factual assertions
CLAIM_PATTERNS = [
    # Numbers / percentages / measurements
    r"\d+\.?\d*\s*%",
    r"\d+\.?\d*\s*(배|개|명|건|시간|일|주|월|년|토큰|에이전트|프롬프트)",
    r"\d+\.?\d*\s*(x|X|차)",
    # Comparisons
    r"(비해|대비|보다|차이|차)",
    r"(개선|향상|증가|감소|하락|상승|하향|상향)",
    r"(최고|최저|최대|최소|평균)",
    # Technical assertions
    r"(제안|발표|출시|공개|입증|증명|보여준|보였다|달성)",
    r"(framework|프레임워크|모델|알고리즘|방법론)",
    # Causal claims
    r"(때문에|로 인해|결과로|원인은|이유는)",
    # Capability claims
    r"(할 수 있다|가능하다|가능해졌|수 있다|한다|했다)",
]


def fail(message: str) -> None:
    print(f"blog-claim-verification-gate: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def info(message: str) -> None:
    print(f"blog-claim-verification-gate: {message}")


def extract_frontmatter(text: str) -> dict:
    """Extract Quartz YAML frontmatter."""
    fm = {}
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return fm
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


def strip_markdown(text: str) -> str:
    """Strip frontmatter, code blocks, image syntax, URLs for cleaner claim extraction."""
    # Remove frontmatter
    text = re.sub(r"^---\n.*?\n---\n*", "", text, flags=re.DOTALL)
    # Remove code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", "", text)
    # Remove image syntax but keep alt text
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    # Remove markdown links but keep text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # Remove headers markers
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    # Remove blockquote markers
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r"^---+\s*$", "", text, flags=re.MULTILINE)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split Korean text into sentences. Handles ~. ~! ~? and Korean enders."""
    # Split on sentence-ending punctuation including Korean enders
    parts = re.split(r"(?<=[.!?다요죠임음])\s+(?=[가-힣A-Z])", text)
    # Also handle sentences ending with closing quote/paren
    parts = [p.strip() for p in parts if p.strip()]
    # Filter out very short fragments
    return [p for p in parts if len(p) > 15]


def extract_claims(sentences: list[str]) -> list[dict]:
    """Extract sentences that contain factual claims."""
    claims = []
    for i, sent in enumerate(sentences):
        reasons = []
        for pattern in CLAIM_PATTERNS:
            if re.search(pattern, sent, re.IGNORECASE):
                reasons.append(pattern[:20])

        # Score: how many claim patterns match
        score = len(reasons)
        if score > 0:
            claims.append({
                "index": i,
                "text": sent[:200],
                "score": score,
                "patterns": reasons,
            })

    # Sort by score descending (most claim-dense first)
    claims.sort(key=lambda c: c["score"], reverse=True)
    return claims


def check_red_flags(text: str) -> list[str]:
    """Check for red flags that indicate quality issues."""
    issues = []

    # Superlatives
    found_super = [s for s in SUPERLATIVES if s in text]
    if found_super:
        issues.append(f"과장 표현 (unsupported superlatives): {', '.join(found_super[:3])}")

    # Weasel words
    found_weasel = [w for w in WEASEL_WORDS if w in text]
    if found_weasel:
        issues.append(f"애매한 출처 (weasel words): {', '.join(found_weasel[:3])}")

    # Vague quantifiers without specifics
    # Only flag if there are many and few numbers
    found_vague = [v for v in VAGUE_HEDGES if v in text]
    number_count = len(re.findall(r"\d+\.?\d*", text))
    if len(found_vague) >= 3 and number_count < 5:
        issues.append(f"구체적 수치 부족 (vague quantifiers without numbers): {', '.join(found_vague[:3])}")

    return issues


def check_source_reference(text: str) -> bool:
    """Check if the post references any source."""
    for pattern in SOURCE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Claim verification gate")
    parser.add_argument("markdown", help="path to the blog post markdown")
    parser.add_argument("--source-url", default=None, help="expected source URL")
    parser.add_argument("--strict", action="store_true", help="fail on any red flag")
    parser.add_argument("--min-claims", type=int, default=3, help="minimum claims required")
    parser.add_argument("--max-claims", type=int, default=60, help="maximum claims before density warning")
    args = parser.parse_args()

    path = Path(args.markdown)
    if not path.exists():
        fail(f"markdown not found: {path}")

    raw = path.read_text(encoding="utf-8")
    fm = extract_frontmatter(raw)
    clean = strip_markdown(raw)
    sentences = split_sentences(clean)

    if not sentences:
        fail("no readable sentences found after stripping markdown")

    # ── Extract claims ─────────────────────────────────────────
    claims = extract_claims(sentences)
    claim_count = len(claims)

    info(f"post: {path.name}")
    info(f"sentences: {len(sentences)} | claims extracted: {claim_count}")

    # ── Check claim density ────────────────────────────────────
    if claim_count < args.min_claims:
        fail(f"너무 적은 핵심 내용 (only {claim_count} claims, need >= {args.min_claims}). "
             f"내용이 빈약하거나 사실 관계보다는 서술에 치우쳐 있을 수 있습니다.")

    if claim_count > args.max_claims:
        info(f"WARN: 높은 claim 밀도 ({claim_count} claims). 가독성 저하 가능.")

    # ── Check source reference ─────────────────────────────────
    has_source = check_source_reference(raw)
    if not has_source:
        fail("출처 참조 없음 (no source reference found). "
             "모든 핵심 내용은 원본 소스로 추적 가능해야 합니다.")

    if args.source_url and args.source_url not in raw:
        fail(f"지정된 소스 URL이 글에 없음: {args.source_url}")

    # ── Check red flags ────────────────────────────────────────
    red_flags = check_red_flags(clean)
    if red_flags:
        for flag in red_flags:
            info(f"RED FLAG: {flag}")
        if args.strict:
            fail(f"레드플래그 {len(red_flags)}건 (--strict 모드). 수정 후 재실행하세요.")
    else:
        info("red flags: none")

    # ── Output claim list for agent verification ───────────────
    print("\n" + "=" * 60)
    print("CLAIM VERIFICATION CHECKLIST — agent must verify each claim")
    print("against the source material (paper/video/article).")
    print("Fix or remove any unsupported claims before publishing.")
    print("=" * 60)

    for i, claim in enumerate(claims[:30], 1):
        verified = "[ ]"
        print(f"\n{verified} Claim {i} (score {claim['score']}):")
        print(f"    {claim['text']}")
        if i >= 30:
            print(f"\n    ... {claim_count - 30} more claims (see --max-claims to adjust)")
            break

    print("\n" + "=" * 60)
    print(f"blog-claim-verification-gate: PASS ({claim_count} claims, "
          f"{len(red_flags)} red flags)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
