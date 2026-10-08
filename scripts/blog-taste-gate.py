#!/usr/bin/env python3
"""Owner-taste gate for conanssam blog drafts (taste v1, 2026-10-08).

The rules come from the owner's own edit of one Opus-polished post
(context-compaction roundup, 2026-10-08). Each rule cites the edit it came from.
blog-voice-spyrl-gate.py scores generic AI-slop; this gate checks the owner's
specific preferences. Hard rules fail the gate; soft rules are reported for revision.

Usage:
  python3 scripts/blog-taste-gate.py content/posts/a.md [--json out.json]

Exit codes: 0 pass, 1 hard-rule failure, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 문장 끝 분류. "~다."로 끝나도 "니다/습니다"는 존댓말이다.
POLITE_END = re.compile(r"(니다|요|죠|까요|세요)$")
CASUAL_POLITE_END = re.compile(r"(요|죠)$")          # ~요/~죠/~구요: 코난쌤 말투 섞기
PLAIN_END = re.compile(r"(?<!니)다$")                # 평서 "~했다/~이다/~한다"
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

# 오타·비문(코난쌤 수정본에서 실제로 나온 것 + 흔한 것). "구요"는 코난쌤 말투라 허용.
TYPOS = {
    r"이였": "이었",
    r"되요": "돼요",
    r"됬": "됐",
    r"안되요": "안 돼요",
    r"할께": "할게",
    r"몇일": "며칠",
    r"(?<!\.)\.\.(?!\.)": "마침표 두 번",
}

# 설명 없이 쓰면 안 되는 지표·연구 용어. 본문 어딘가에 풀이 표지가 있어야 한다.
JARGON = ["AUROC", "dU@", "yardstick", "코호트", "트랙토리", "트래젝토리", "ablation", "어블레이션"]
GLOSS = re.compile(r"(부릅니다|부른다|라고 합니다|라는 뜻|이란|란 |뜻입니다|말합니다)")

# 기술 현상을 몸 아픈 비유로 쓰지 않는다 (코난쌤: "아프다" → "맥락을 잃어버린다/손해가 크다").
BODY_METAPHOR = re.compile(r"아프[다고]|아픈|아파")

BANNED_SPEAKER = re.compile(r"블로그봇(이|은|는|의|\(| )")
OLD_CLOSING = "운영자가 검토해 발행"
CLOSING_MUST = ["제가", "에이전트를 활용해"]


def split_frontmatter(text: str) -> tuple[str, str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[1], parts[2]
    return "", text


def prose_lines(body: str) -> list[str]:
    """Paragraph and list text only: no headings, tables, code, images or blank lines."""
    out, in_code = [], False
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not s or s.startswith(("#", "|", "![", ">", "<")):
            continue
        item = re.match(r"^([-*]|\d+[.)])\s+", s)
        s = s[item.end():] if item else s
        if item:
            # 목록 맨 앞 굵은 단언문은 제목처럼 쓰는 자리라 평서 '~다'를 허용한다
            # (코난쌤이 결론 목록의 굵은 문장을 '~잃어버린다'로 직접 고쳐 씀).
            s = re.sub(r"^\*\*[^*]+\*\*\s*", "", s)
        out.append(s)
    return out


def sentences(lines: list[str]) -> list[str]:
    sents = []
    for line in lines:
        plain = re.sub(r"<[^>]+>", "", line)
        plain = re.sub(r"\*\*|`|\[([^\]]*)\]\([^)]*\)", r"\1", plain)
        for s in SENT_SPLIT.split(plain):
            s = s.strip()
            core = re.sub(r"[\s\"'”’)\]]*[.!?]?[\s\"'”’)\]]*$", "", s)
            if core and re.search(r"[가-힣]$", core):
                sents.append(core)
    return sents


def section(body: str, keyword: str) -> str:
    m = re.search(rf"^##\s+[^\n]*{keyword}[^\n]*\n(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def evaluate(text: str) -> dict:
    _, body = split_frontmatter(text)
    # 편집기 내보내기가 굵게를 글자마다 쪼갠 흔적을 합친다
    body = body.replace("****", "").replace("** **", " ")
    lines = prose_lines(body)
    sents = sentences(lines)
    polite = [s for s in sents if POLITE_END.search(s)]
    plain = [s for s in sents if PLAIN_END.search(s) and not POLITE_END.search(s)]
    casual = [s for s in polite if CASUAL_POLITE_END.search(s)]
    rules = []

    def add(rid, level, ok, why, evidence=None, metric=None):
        rules.append({"id": rid, "level": level, "pass": ok, "why": why,
                      "metric": metric, "evidence": (evidence or [])[:6]})

    ended = len(polite) + len(plain)
    ratio = len(plain) / ended if ended else 0.0
    add("T1_polite_endings", "hard", ratio <= 0.05,
        "본문은 존댓말(~습니다/~요/~죠). 평서 '~다'는 5% 이하 (코난쌤이 '~다' 문장을 전부 존댓말로 바꿈)",
        plain, {"plain": len(plain), "polite": len(polite), "plain_ratio": round(ratio, 3)})

    share = len(casual) / len(polite) if polite else 0.0
    add("T2_casual_mix", "soft", share >= 0.10,
        "'~습니다'만 이어지지 않게 '~죠/~구요/~요'를 섞는다 (코난쌤: '줄었구요', '하는 식이죠')",
        None, {"casual": len(casual), "polite": len(polite), "share": round(share, 3)})

    speaker = [l for l in lines if BANNED_SPEAKER.search(l)]
    add("T3_first_person", "hard", not speaker,
        "화자는 '제가'. '블로그봇이/블로그봇은'을 쓰지 않는다 (코난쌤: '블로그봇이 직접 확인한 것' → '제가 직접 확인한 것')",
        speaker)

    tail = lines[-1] if lines else ""
    closing_ok = all(k in tail for k in CLOSING_MUST) and OLD_CLOSING not in body
    add("T4_closing_line", "hard", closing_ok,
        "마지막 문장: '제가 … 일부는 에이전트를 활용해 실행하고 확인한 내용으로 발행하였습니다' 형식",
        [tail])

    typos = []
    for pat, fix in TYPOS.items():
        for l in lines:
            for m in re.finditer(pat, l):
                typos.append(f"{l[max(0, m.start()-20):m.end()+10]}  → {fix}")
    add("T5_typos", "hard", not typos, "맞춤법·문장부호 오류 없음 ('구요'는 코난쌤 말투라 허용)", typos)

    joined = "\n".join(lines)
    unexplained = []
    for term in JARGON:
        if term in joined:
            paras = [l for l in lines if term in l]
            if not any(GLOSS.search(p) for p in paras):
                unexplained.append(term)
    add("T6_explain_jargon", "soft", not unexplained,
        "지표·연구 용어는 처음 나올 때 풀어 쓴다. 결과는 독자가 그려지는 현상으로 (예: '맥락을 잃어버린다')",
        unexplained)

    meta = [l for l in lines if BODY_METAPHOR.search(l)]
    add("T7_no_body_metaphor", "soft", not meta,
        "기술 현상을 '아프다' 같은 몸 비유로 쓰지 않는다 (코난쌤: '더 아프다' → '더 손해가 큽니다')", meta)

    verified = section(body, "직접 확인")
    head = re.search(r"^##\s+[^\n]*직접 확인[^\n]*", body, re.M)
    first_person = re.search(r"(제가|저도|저는)", (head.group(0) if head else "") + verified)
    process_ok = bool(verified) and bool(first_person) and re.search(r"(봤|돌렸|찾아|해봤|해 봤)", verified)
    add("T8_process_story", "soft", bool(process_ok),
        "'제가 직접 확인한 것' 절에서 무엇을 해 봤고 무엇은 못 했는지 이야기로 쓴다 (코난쌤: '찾아봤는데 … 아쉽게도 재현은 못 했습니다')",
        None if process_ok else ["직접 확인 절이 없거나 1인칭 과정 서술이 없음"])

    # 목록 맨 앞 굵은 글씨는 항목 이름표라 강조 개수에서 뺀다
    no_labels = re.sub(r"^(\s*([-*]|\d+[.)])\s+)\*\*[^*]+\*\*", r"\1", body, flags=re.M)
    bold = re.findall(r"\*\*[^*]+\*\*", no_labels) + re.findall(r"<span style=\"background-color", no_labels)
    add("T9_highlight_count", "soft", 5 <= len(bold) <= 14,
        "강조는 결론·숫자에만 5~14곳", None, {"bold": len(bold)})

    hard_fail = [r["id"] for r in rules if r["level"] == "hard" and not r["pass"]]
    soft_fail = [r["id"] for r in rules if r["level"] == "soft" and not r["pass"]]
    return {"kind": "blog-taste-gate", "taste_version": "v1-2026-10-08",
            "passed": not hard_fail, "hard_fail": hard_fail, "soft_fail": soft_fail, "rules": rules}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("post")
    ap.add_argument("--json", help="write report here")
    ap.add_argument("--quiet", action="store_true", help="one summary line")
    a = ap.parse_args()
    p = Path(a.post)
    if not p.exists():
        print(f"missing: {p}", file=sys.stderr)
        return 2
    rep = evaluate(p.read_text(encoding="utf-8"))
    rep["post"] = str(p)
    if a.json:
        Path(a.json).write_text(json.dumps(rep, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if a.quiet:
        t1 = next(r for r in rep["rules"] if r["id"] == "T1_polite_endings")["metric"]
        print(f"{'PASS' if rep['passed'] else 'FAIL'}  hard={rep['hard_fail']} soft={rep['soft_fail']} plain={t1['plain']}/{t1['plain']+t1['polite']}  {p.name}")
    else:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
