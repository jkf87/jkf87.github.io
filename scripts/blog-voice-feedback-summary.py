#!/usr/bin/env python3
"""Summarize accumulated blog Voice SpyRL reports.

Reads JSON reports from memory/voice-feedback and produces a weekly-style
KEEP/AVOID summary. This does not rewrite prompts by itself; it creates a
review artifact so the blog cron can adapt conservatively.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_reports(feedback_dir: Path) -> list[dict]:
    reports = []
    for path in sorted(feedback_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("kind") == "blog-voice-spyrl-gate":
            data["_path"] = str(path)
            reports.append(data)
    return reports


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="../memory/voice-feedback")
    ap.add_argument("--out", default="../memory/voice-feedback/latest-summary.md")
    ap.add_argument("--json-out", default="../memory/voice-feedback/latest-summary.json")
    args = ap.parse_args()

    feedback_dir = Path(args.dir)
    reports = load_reports(feedback_dir)
    tag_counts: Counter[str] = Counter()
    winner_grades: Counter[str] = Counter()
    scores = []
    examples: dict[str, list[str]] = defaultdict(list)

    for report in reports:
        winner_grades[report.get("winnerGrade", "?")] += 1
        if isinstance(report.get("winnerScore"), (int, float)):
            scores.append(float(report["winnerScore"]))
        for tag in report.get("spyTags", []) or []:
            tag_counts[tag] += 1
            if len(examples[tag]) < 5:
                examples[tag].append(report.get("spy") or report.get("winner") or report.get("_path", ""))
        for cand in report.get("candidates", []) or []:
            for tag in cand.get("tags", []) or []:
                tag_counts[tag] += 1
                if len(examples[tag]) < 5:
                    examples[tag].append(cand.get("path", ""))

    avg_score = round(sum(scores) / len(scores), 2) if scores else None
    avoid = [tag for tag, _ in tag_counts.most_common()]
    keep = [
        "결론 먼저 쓰기",
        "짧은 문단 유지",
        "실물/수치/표/명령어로 설명 대체",
        "Quartz 이미지 절대경로 유지",
        "과한 bold와 자문자답 훅 피하기",
    ]

    summary = {
        "kind": "blog-voice-feedback-summary",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "reportCount": len(reports),
        "averageWinnerScore": avg_score,
        "winnerGrades": dict(winner_grades),
        "avoidTags": dict(tag_counts.most_common()),
        "keep": keep,
        "examples": dict(examples),
    }

    md = []
    md.append("# Blog Voice SpyRL Feedback Summary")
    md.append("")
    md.append(f"- generated: {summary['createdAt']}")
    md.append(f"- reports: {len(reports)}")
    md.append(f"- average winner score: {avg_score if avg_score is not None else 'n/a'}")
    md.append(f"- winner grades: {dict(winner_grades)}")
    md.append("")
    md.append("## KEEP")
    for item in keep:
        md.append(f"- {item}")
    md.append("")
    md.append("## AVOID / WATCH")
    if avoid:
        for tag, count in tag_counts.most_common():
            md.append(f"- `{tag}`: {count}")
            for ex in examples.get(tag, [])[:3]:
                md.append(f"  - example: `{ex}`")
    else:
        md.append("- 아직 누적된 spy tag 없음")
    md.append("")
    md.append("## 운영 원칙")
    md.append("- 같은 태그가 반복되면 다음 자동 글에서 먼저 고친다.")
    md.append("- 점수는 보조 신호다. 사용자 피드백이 있으면 사용자 피드백을 우선한다.")
    md.append("- 이 요약은 문체 규칙 제안용이며 자동으로 MEMORY나 skill을 덮어쓰지 않는다.")

    out = Path(args.out)
    json_out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    json_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
