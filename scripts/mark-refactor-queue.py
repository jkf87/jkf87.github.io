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
    """frontmatter 최상위 키를 제자리에서 바꾸고, 없으면 끝에 붙이고, remove는 지운다. 같은 값이면 텍스트가 그대로다."""
    if not text.startswith("---"):
        text = "---\n---\n" + text
    end = text.find("\n---", 3)
    fm, rest = text[3:end], text[end:]
    out, seen = [], set()
    for l in fm.split("\n"):
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:", l)
        k = m.group(1) if m else None
        if k in remove:
            continue
        if k in updates:
            if k in seen:
                continue
            seen.add(k)
            out.append(f"{k}: {updates[k]}")
            continue
        out.append(l)
    while out and not out[-1].strip():
        out.pop()
    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}: {v}")
    return "---" + "\n".join(out) + rest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--queue", default="scripts/refactor-queue.json")
    ap.add_argument("--undo", action="store_true")
    a = ap.parse_args()

    queue = json.load(open(os.path.join(a.site_root, a.queue), encoding="utf-8"))
    kp = os.path.join(a.site_root, "scripts", "keep-posts.json")
    protected = set()
    if os.path.isfile(kp):
        k = json.load(open(kp, encoding="utf-8"))
        protected = set(k.get("originals", [])) | set(k.get("expand_targets", [])) | set(k.get("site_pages", []))
    changed = missing = refused = 0
    for hub in queue:
        status = "archived" if hub["treatment"] == "archive" else "queued"
        for m in hub["members"]:
            if m["path"] in protected and not a.undo:
                refused += 1
                print(f"refused (keep-posts.json): {m['path']} in {hub['hub_id']}", file=sys.stderr)
                continue
            p = os.path.join(a.site_root, "content", m["path"])
            if not os.path.isfile(p):
                missing += 1
                continue
            t = open(p, encoding="utf-8").read()
            cur = re.search(r"^refactor_status:\s*(\S+)", t.split("\n---", 1)[0], re.M)
            cur = cur.group(1) if cur else ""
            if a.undo:
                new = set_fm(t, {"draft": "false"}, remove=("refactor_hub", "refactor_status"))
            elif cur in ("merged", "published", "in-review"):
                new = set_fm(t, {"draft": "true"})  # 허브에 흡수된 글의 상태·merged_into는 보존
            else:
                new = set_fm(t, {"draft": "true", "refactor_hub": hub["hub_id"], "refactor_status": status})
            if new != t:
                open(p, "w", encoding="utf-8").write(new)
                changed += 1
    print(json.dumps({"changed": changed, "missing": missing, "refused": refused, "undo": a.undo}, ensure_ascii=False))
    return 1 if refused else 0


if __name__ == "__main__":
    sys.exit(main())
