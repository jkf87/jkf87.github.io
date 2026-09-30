#!/usr/bin/env python3
"""scripts/refactor-queue.json 의 허브 하나를 고치고, 파일을 항상 같은 형식으로 쓴다.

큐 파일은 여러 실행이 같이 고친다. 실행마다 json.dump 옵션이 다르면 파일 전체의
들여쓰기가 바뀌어 13,000줄짜리 diff 와 병합 충돌이 난다(2026-09-30 병렬 레인에서 발생).
그래서 큐는 손으로 고치지 말고 이 스크립트로만 고친다. 형식은 indent=1,
ensure_ascii=False, 끝 줄바꿈 없음으로 고정이다.

  python3 scripts/queue-set.py --hub ux-laws-01 --status in-review --hub-slug posts/<slug>
  python3 scripts/queue-set.py --canon        # 내용은 그대로 두고 형식만 고정 형식으로

병합 충돌이 큐 파일에서 나면: 원격 쪽을 통째로 받고(`git checkout --theirs`)
이 스크립트로 자기 허브만 다시 적용한다. 같은 명령을 여러 번 돌려도 결과가 같다.
"""
import argparse
import json
import sys
from pathlib import Path

QUEUE = Path(__file__).resolve().parent / "refactor-queue.json"
ALLOWED = {"queued", "in-review", "published", "archived", "owner",
           "reserved-b", "reserved-c", "reserved-d"}


def write(q):
    QUEUE.write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hub")
    ap.add_argument("--status")
    ap.add_argument("--hub-slug")
    ap.add_argument("--note", help="note 를 이 값으로 쓴다. 빈 문자열이면 지운다")
    ap.add_argument("--canon", action="store_true", help="형식만 고정 형식으로 다시 쓴다")
    a = ap.parse_args()

    q = json.loads(QUEUE.read_text(encoding="utf-8"))
    if a.canon and not a.hub:
        write(q)
        print("canonical format written")
        return 0
    if not a.hub:
        ap.error("--hub 또는 --canon 이 필요하다")

    hubs = [h for h in q if h.get("hub_id") == a.hub]
    if len(hubs) != 1:
        print(f"hub not found or duplicated: {a.hub} ({len(hubs)})", file=sys.stderr)
        return 2
    h = hubs[0]
    if a.status:
        if a.status not in ALLOWED:
            print(f"unknown status: {a.status}", file=sys.stderr)
            return 2
        h["status"] = a.status
        if a.status in ("in-review", "published", "queued"):
            h.pop("note", None)          # 예약 메모는 예약이 풀리면 지운다
    if a.hub_slug:
        h["hub_slug"] = a.hub_slug
    if a.note is not None:
        if a.note:
            h["note"] = a.note
        else:
            h.pop("note", None)
    write(q)
    print(f"{a.hub}: status={h.get('status')} hub_slug={h.get('hub_slug')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
