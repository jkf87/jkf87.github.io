#!/usr/bin/env python3
"""리팩토링 큐에 든 글을 '지우지 않고' 비공개로 돌린다.

각 글의 frontmatter에 아래 세 줄을 넣거나 고친다. 본문과 파일 위치는 건드리지 않는다.
  draft: true                 # Quartz RemoveDrafts 필터가 빌드에서 뺀다
  refactor_hub: <hub_id>      # scripts/refactor-queue.json의 허브
  refactor_status: queued     # queued → merged(허브에 흡수됨) / archived(보관)

사용: python3 scripts/mark-refactor-queue.py [--site-root .] [--queue scripts/refactor-queue.json] [--undo]
--undo 는 이 스크립트가 넣은 표시를 지우고 draft: false 로 되돌린다.
"""
import argparse, json, os, re, sys


def set_fm(text, updates, remove=()):
    """frontmatter의 최상위 키만 교체·삭제한다. text[3:end]는 '\n'으로 시작하고 rest는 '\n---'로 시작한다."""
    if not text.startswith("---"):
        text = "---\n---\n" + text
    end = text.find("\n---", 3)
    fm, rest = text[3:end], text[end:]
    keys = set(updates) | set(remove)
    lines = [l for l in fm.split("\n") if not any(re.match(rf"^{re.escape(k)}\s*:", l) for k in keys)]
    while lines and not lines[-1].strip():
        lines.pop()
    for k, v in updates.items():
        lines.append(f"{k}: {v}")
    return "---" + "\n".join(lines) + rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--queue", default="scripts/refactor-queue.json")
    ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()

    queue = json.load(open(os.path.join(a.site_root, a.queue), encoding="utf-8"))
    changed = missing = 0
    for hub in queue:
        status = "archived" if hub["treatment"] == "archive" else "queued"
        for m in hub["members"]:
            p = os.path.join(a.site_root, "content", m["path"])
            if not os.path.isfile(p):
                missing += 1
                continue
            t = open(p, encoding="utf-8").read()
            if a.undo:
                new = set_fm(t, {"draft": "false"}, remove=("refactor_hub", "refactor_status"))
            else:
                new = set_fm(t, {"draft": "true", "refactor_hub": hub["hub_id"], "refactor_status": status})
            if new != t:
                open(p, "w", encoding="utf-8").write(new)
                changed += 1
    print(json.dumps({"changed": changed, "missing": missing, "undo": a.undo}, ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
