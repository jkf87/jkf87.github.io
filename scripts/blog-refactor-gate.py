#!/usr/bin/env python3
"""blog-refactor-gate: conanssam.com 공개 전 '복제·저가치' 신호를 기계적으로 막는다.

모드
  hub     비슷한 글 여러 편을 하나로 합친 주제 허브(리팩토링 큐 처리)
  expand  기존 글을 봇의 실제 실행 기록으로 보강
  new     새 글(운영자 경험 또는 봇 실습 기반)

사용: python3 scripts/blog-refactor-gate.py content/posts/<slug>.md --mode hub [--site-root .]
통과 exit 0, 실패 exit 1 + 사유 JSON.

근거: AdSense '복제된 콘텐츠가 있는 화면'·'가치가 별로 없는 콘텐츠', 게시자 정책(검토·선별 없는 자동 생성 금지),
AdSense 도움말(비슷한 페이지는 확장하거나 통합), 검색 스팸 정책(확장된 콘텐츠 악용).
"""
import argparse, glob, json, os, re, sys

RULES = {
    "hub":    dict(min_chars=3000, min_sources=4, min_images=1, need_table=True,
                   sections=[r"한눈에|결론", r"비교", r"언제|선택", r"한계|반론", r"적용"]),
    "expand": dict(min_chars=2000, min_sources=1, min_images=2, need_table=False,
                   sections=[r"검증 로그|직접 확인", r"한계|막힌"]),
    "new":    dict(min_chars=1800, min_sources=1, min_images=2, need_table=False,
                   sections=[r"직접 해본|직접 확인|검증 로그", r"결과", r"한계|막힌"]),
}
MAX_QUOTE_RATIO = 0.15
MAX_ONE_SOURCE_SHARE = 0.5
TITLE_DUP_JACCARD = 0.5
DISCLOSURE = r"이 글은.*(AI|에이전트|블로그봇).*(확인|검토)"
BANNED = r"혈압|혈당|당화|콜레스테롤|지방간|갑상선|건강검진|질환|증상|치료|영양제|주식|코인|비트코인|ETF|배당|부동산|매매가|재테크"
SINGLE_SOURCE_HEAD = r"^\s*(?:[-*]\s*)?(?:\*\*)?(?:원문|원본|Source)(?:\*\*)?\s*[:：]"
ARXIV = r"(?<!\d)(2\d{3}\.\d{4,5})(?!\d)"


def split_fm(t):
    if t.startswith("---"):
        e = t.find("\n---", 3)
        if e > 0:
            return t[3:e], t[e + 4:]
    return "", t


def fm_get(fm, key):
    m = re.search(rf"^{key}:\s*[\"']?(.*?)[\"']?\s*$", fm, re.M)
    return m.group(1) if m else ""


def fm_list(fm, key):
    m = re.search(rf"^{key}:\s*\[(.*?)\]", fm, re.M)
    if m:
        return [x.strip().strip("\"'") for x in m.group(1).split(",") if x.strip()]
    m = re.search(rf"^{key}:\s*\n((?:\s+-\s*.*\n?)+)", fm, re.M)
    return [x.strip().strip("\"'") for x in re.findall(r"-\s*(.+)", m.group(1))] if m else []


def plain_len(body):
    b = re.sub(r"```.*?```", "", body, flags=re.S)
    b = "\n".join(l for l in b.splitlines() if not l.lstrip().startswith("|"))
    b = re.sub(r"!\[[^\]]*\]\([^)]*\)|<[^>]+>", "", b)
    b = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", b)
    return len(re.sub(r"[\s#>*_`-]", "", b))


def bigrams(s):
    s = re.sub(r"[\s\W_]+", "", s.lower())
    return {s[i:i + 2] for i in range(len(s) - 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post")
    ap.add_argument("--mode", choices=RULES, required=True)
    ap.add_argument("--site-root", default=".")
    a = ap.parse_args()
    R = RULES[a.mode]

    text = open(a.post, encoding="utf-8").read()
    fm, body = split_fm(text)
    slug = os.path.splitext(os.path.basename(a.post))[0]
    title = fm_get(fm, "title") or slug
    fails = []

    if fm_get(fm, "draft").lower() == "true":
        fails.append("draft: true 상태")
    if not re.search(r"^author:\s*\S", fm, re.M):
        fails.append("author(사람 저자 바이라인) 없음")

    n = plain_len(body)
    if n < R["min_chars"]:
        fails.append(f"본문 {n}자 < {R['min_chars']}자")
    for pat in R["sections"]:
        if not re.search(rf"^#+\s*.*(?:{pat})", body, re.M):
            fails.append(f"필수 섹션 없음: {pat}")
    if R["need_table"] and not re.search(r"^\|.*\|\s*$\n^\|\s*:?-{3,}", body, re.M):
        fails.append("비교 표 없음")
    if re.search(SINGLE_SOURCE_HEAD, body[:600], re.M):
        fails.append("글머리가 '원문:' 단일 출처 요약 형식")
    if re.search(BANNED, title + " " + fm_get(fm, "description")):
        fails.append("금지 주제(건강·의료·투자·부동산)")
    if "[OWNER-" in body or "[TODO" in body:
        fails.append("자리표시자가 남아 있음")
    if not re.search(DISCLOSURE, body[-800:]):
        fails.append("AI 활용·검토 공개 문장 없음(글 끝)")

    # 출처 다양성: arXiv id와 외부 링크 도메인+경로 기준
    links = re.findall(r"\]\((https?://[^)\s]+)\)", body)
    srcs = [("arxiv:" + m) for m in re.findall(ARXIV, body)] + [re.sub(r"[#?].*$", "", u).rstrip("/") for u in links if "arxiv.org" not in u]
    distinct = {s for s in srcs}
    if len(distinct) < R["min_sources"]:
        fails.append(f"서로 다른 출처 {len(distinct)}개 < {R['min_sources']}개")
    if a.mode == "hub" and srcs:
        top = max(srcs.count(s) for s in distinct)
        if top / len(srcs) > MAX_ONE_SOURCE_SHARE:
            fails.append(f"한 출처가 인용의 {top / len(srcs):.0%}를 차지 — 단일 출처 요약에 가까움")

    # 이미지: media/<slug>/ 안의 자체 이미지만 허용
    imgs = [u for u in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", body)]
    ext = [u for u in imgs if u.startswith("http")]
    own = [u for u in imgs if not u.startswith("http") and f"media/{slug}/" in u]
    other = [u for u in imgs if not u.startswith("http") and u not in own]
    if len(own) < R["min_images"]:
        fails.append(f"자체 이미지 {len(own)}장 < {R['min_images']}장 (media/{slug}/)")
    if other:
        fails.append(f"media/{slug}/ 밖 이미지 {len(other)}장 — 논문·타 사이트 그림 전재 금지")
    if ext:
        fails.append(f"외부 이미지 핫링크 {len(ext)}장")
    for u in own:
        p = os.path.normpath(os.path.join(os.path.dirname(a.post), u)) if not u.startswith("/") else os.path.join(a.site_root, "content", u.lstrip("/"))
        if not os.path.isfile(p):
            fails.append(f"이미지 파일 없음: {u}")

    lines = [l for l in body.splitlines() if l.strip()]
    quoted = sum(len(l) for l in lines if l.lstrip().startswith(">"))
    total = sum(len(l) for l in lines) or 1
    if quoted / total > MAX_QUOTE_RATIO:
        fails.append(f"인용 비율 {quoted / total:.0%} > {MAX_QUOTE_RATIO:.0%}")

    # 허브: 큐에 적힌 멤버 전원이 aliases에 있어야 옛 URL이 새 허브로 넘어간다
    if a.mode == "hub":
        hub_id = fm_get(fm, "refactor_hub_id")
        qpath = os.path.join(a.site_root, "scripts", "refactor-queue.json")
        if not hub_id:
            fails.append("refactor_hub_id 없음")
        elif os.path.isfile(qpath):
            q = {h["hub_id"]: h for h in json.load(open(qpath, encoding="utf-8"))}
            if hub_id not in q:
                fails.append(f"큐에 없는 hub_id: {hub_id}")
            else:
                need = {re.sub(r"\.md$", "", m["path"]) for m in q[hub_id]["members"]}
                have = set(fm_list(fm, "aliases"))
                miss = sorted(need - have)
                if miss:
                    fails.append(f"aliases 누락 {len(miss)}개(옛 URL 리디렉트): {miss[:3]}")

    # 중복: 공개 중인 다른 글과 제목·논문 겹침
    mine_ids = set(re.findall(ARXIV, title + body))
    B = bigrams(title)
    for p in glob.glob(os.path.join(a.site_root, "content", "**", "*.md"), recursive=True):
        if os.path.abspath(p) == os.path.abspath(a.post):
            continue
        ofm, obody = split_fm(open(p, encoding="utf-8").read())
        if fm_get(ofm, "draft").lower() == "true":
            continue  # 비공개(큐·보관) 글은 비교 대상에서 뺀다
        ob = bigrams(fm_get(ofm, "title"))
        if B and ob and len(B & ob) / len(B | ob) >= TITLE_DUP_JACCARD:
            fails.append(f"공개 글과 제목 중복 의심: {os.path.relpath(p, a.site_root)}")
        shared = mine_ids & set(re.findall(ARXIV, obody))
        if a.mode != "hub" and shared:
            fails.append(f"같은 논문을 다룬 공개 글: {os.path.relpath(p, a.site_root)} — 기존 글 갱신")

    res = {"post": a.post, "mode": a.mode, "pass": not fails, "chars": n,
           "sources": len(distinct), "own_images": len(own), "fails": fails}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
