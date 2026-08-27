# Daily Blog Publish v2 Runbook

Use this runbook for `daily-blog-publish-v2-quality-gated`.

## Goal
Publish at most one high-confidence Korean Quartz blog post per run, then optionally publish a Threads thread only after all gates pass.

## Hard stops
- `already published today` / `하루 최대 1포스트` 같은 당일 게시 수 이유로 실행을 스킵하지 않는다. 이 잡은 하루 6회(07/10/13/16/19/22 KST) 돌고 실행당 최대 1포스트, 즉 하루 최대 6포스트가 의도된 운영이다(2026-08-18 사용자 재확인). 당일 게시 수는 리포트용일 뿐이다.
- Missing required local path/tool → report `blocked: missing local tool`.
- No strong AI/LLM/agent candidate after scanning up to 12 candidates → report `skipped: no candidate`.
- Duplicate source/title/slug in `published-log.json` → skip that candidate.
- Do not commit `public/`.
- Do not call Threads API until blog image gate, promo gate, live CTA check, and Threads quality gate all pass.
- Do not use Gemini.
- Do not use direct OpenAI API keys for images.

## Required paths
- Quartz repo: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site`
- Published log: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/published-log.json`
- Voice repo: `/Users/conanssam-m4/.openclaw/workspace-blogbot/conanssam-voice`
- Kakao pack: `/Users/conanssam-m4/.openclaw/workspace-blogbot/conanssam-voice/references/packs/kakao.md`
- Voice SpyRL gate: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/scripts/blog-voice-spyrl-gate.py`
- Figure extraction: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/scripts/pdf-extract-figures.py`
- Blog image gate: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/scripts/blog-image-quality-gate.py`
- Blog promo gate: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/scripts/blog-promo-quality-gate.py`
- Blog SEO/AEO gate: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/scripts/blog-seo-aeo-gate.py`
- Threads quality gate: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/scripts/threads-quality-gate.py`
- Threads script: `/Users/conanssam-m4/.openclaw/workspace-agasabot/skills/threads-uploader/scripts/post_threads.py`
- Threads env: `/Users/conanssam-m4/.openclaw/creds/threads/.env`
- Wiki vault: `/Users/conanssam-m4/.openclaw/wiki/main`
- Voice feedback dir: `/Users/conanssam-m4/.openclaw/workspace-blogbot/memory/voice-feedback`

## Default blog voice
Use `conanssam-voice` `kakao` / `plain` as the default blog surface style.

Target:
- 결론 먼저.
- 짧은 문단.
- 실물/수치/명령어/표가 설명을 대신함.
- 원문 근거와 내 해석을 구분.
- 섹션 제목은 은유보다 설명형.
- 자연스러운 표현: `정리했습니다`, `핵심은 이겁니다`, `근데`, `~구요`, `~하면 됩니다`.

Avoid:
- `알아보겠습니다`
- `하지만`
- `첫째/둘째/셋째/넷째`
- `A가 아니라 B다` 경구 프레임
- 과한 bold
- 자문자답 훅
- 웅장한 마무리
- 조쉬/뉴스레터식 과장된 장면 도입, unless the source is specifically a video/interview and it still stays kakao/plain.

## Voice SpyRL gate
Before build, run the self-verifiable style gate. This implements the user's approved RLSVR/SpyRL idea as a style eval, not model training.

Default mode is now multi-candidate.

Create 3 draft variants before finalizing:
- A: `kakao/plain` best effort. This should be the intended publish candidate.
- B: more newsletter/bloggy version. It may have more hook/scene framing.
- C: stricter translation/summary version. It may be flatter and more formal.

Write them outside the post directory first, for example:

```bash
mkdir -p /tmp/blog-spyrl/<slug>
# /tmp/blog-spyrl/<slug>/a-kakao.md
# /tmp/blog-spyrl/<slug>/b-newsletter.md
# /tmp/blog-spyrl/<slug>/c-formal.md
```

Then run:

```bash
python3 scripts/blog-voice-spyrl-gate.py \
  /tmp/blog-spyrl/<slug>/a-kakao.md \
  /tmp/blog-spyrl/<slug>/b-newsletter.md \
  /tmp/blog-spyrl/<slug>/c-formal.md \
  --out ../memory/voice-feedback/<YYYY-MM-DD>-<slug>-spyrl.json
```

Rules:
- Publish the `winner` from the JSON report, not automatically A.
- If the winner is not A, copy the winning draft to `content/posts/<slug>.md` and then do content/fact/image/CTA checks again.
- If no candidate passes, revise A using the top `spyTags`, create a fresh candidate, and rerun.
- If time/tool budget is genuinely tight, one-candidate fallback is allowed with `--allow-single`, but the final report must say `Voice SpyRL mode: fallback-single`.
- Treat `spyTags` as concrete edit instructions, e.g. `too_long_paragraph`, `banned_phrase`, `aphorism`, `bold_overuse`, `question_heading`, `metaphor_heading`, `gpt5x_ai_diction`.
- Keep every report in `memory/voice-feedback/`; this becomes the preference feedback dataset.
- If user feedback arrives later, append it to a matching voice-feedback note/report and use it in future manual judgment.

Weekly feedback summary:

```bash
python3 scripts/blog-voice-feedback-summary.py \
  --dir ../memory/voice-feedback \
  --out ../memory/voice-feedback/latest-summary.md \
  --json-out ../memory/voice-feedback/latest-summary.json
```

Read `../memory/voice-feedback/latest-summary.md` when available before drafting. Use repeated AVOID tags as first-pass edit targets.


## Fire-your-SEO-Agency pass
After the final post passes voice/content revision and before build, run a search/answer-engine structure pass inspired by `fire-your-seo-agency`. This is mandatory for cron blog work from 2026-08-27.

Required structure for every published post:
- Frontmatter must include `description` in addition to `title`, `date`, `tags`, and `draft`. Keep the description specific and roughly 70-160 Korean characters.
- Do not add a body-level `#` heading. Quartz already renders the frontmatter title as the page H1; use `##` inside posts.
- The opening section must give the direct answer first. Use a visible cue such as `## 결론 먼저`, `## 핵심 요약`, or an equivalent first-screen summary.
- Add one markdown table near the top when facts/numbers/entities are involved. Prefer item-value or comparison tables that a crawler can extract.
- Include source/original URLs and visible source context. For papers, include arXiv/OpenReview/GitHub/DOI as applicable.
- Add a bottom FAQ/search-question section with at least 3 question-like items. Use only questions answered by the visible post; do not invent claims for JSON-LD or snippets.
- Make 기준일/date signals visible when numbers or benchmark claims are used.

Run before build:

```bash
python3 scripts/blog-seo-aeo-gate.py content/posts/<slug>.md
```

If it fails, revise and rerun. `--strict` is optional for manual audits; cron publish only needs the default hard gate.

## Highlight markup
After the final post passes voice/content revision and before build, reread the body and mark important expressions with a yellow highlighter feel. This is mandatory for cron blog work from 2026-08-14.

Rules:
- Select roughly 10–20 high-signal expressions: core thesis, key numbers, source claims, warnings, API migration notes, and final takeaway.
- Use Quartz-compatible inline HTML exactly like:

```html
<span style="background-color: #fff59d"><strong>important expression</strong></span>
```

- Do not highlight whole long paragraphs or every sentence. Keep the user's anti-slop preference: emphasis should guide reading, not shout.
- Avoid nested markdown bold around the span; use `<strong>` inside the span.
- After `npx quartz build`, verify the final markdown contains highlights and, after deploy, public HTML includes `#fff59d` / `<strong>`. Include highlight count in the final report.

## Images
For papers, use caption/source-anchored figures only. Prefer official HTML/project/arXiv assets when cleaner.

Accepted image methods include source/official/html_source/caption_crop/vector_crop/embedded_crop. Do not publish page-top crops, full-page screenshots, unreadable crops, or fallback_top45.

Quartz rule:
- Files: `content/images/<slug>/...`
- Markdown refs: `/images/<slug>/...`

Run before build:

```bash
python3 scripts/blog-image-quality-gate.py content/posts/<slug>.md --site-root . --paper --min-images 1
```

Use non-paper mode only for official blog/repo posts where a paper figure is not applicable.

## Standing CTA
For 에이전트/agent/agentic/automation/하네스/harness/루프/loop/MCP/tool use/긴 컨텍스트 에이전트/RL agent topics, add:

`## 더 실습해보고 싶은 분들께`

Include both links:
- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

Run:

```bash
python3 scripts/blog-promo-quality-gate.py content/posts/<slug>.md --require-relevant
```

## Build/publish workflow
1. Verify required paths.
2. Work in `/Users/conanssam-m4/.openclaw/workspace-blogbot/site`.
3. Read `published-log.json`; avoid duplicates. Daily count is only for reporting, never a skip reason.
4. Select one strong candidate.
5. Prepare verified local images before writing the final post.
6. Create 3 temporary Korean draft variants under `/tmp/blog-spyrl/<slug>/`.
7. Run the multi-candidate Voice SpyRL gate and select the JSON `winner`.
8. Copy the winner to `content/posts/<slug>.md`.
9. Add CTA if relevant.
10. Add mandatory highlight markup to 10–20 important expressions using `<span style="background-color: #fff59d"><strong>...</strong></span>`.
11. Verify image refs resolve and are absolute `/images/...` refs.
12. Run Voice SpyRL gate again on the final post path; fix failures.
13. Run SEO/AEO gate: `python3 scripts/blog-seo-aeo-gate.py content/posts/<slug>.md`; fix failures.
14. Run image gate.
15. Run promo gate.
16. Run `npx quartz build`.
17. Git add only intended files: post, `content/images/<slug>/`, `published-log.json`, wiki note if inside repo, intentional script changes. Never add `public/`.
18. Commit and push to `main`.
19. Confirm public blog URL and image URLs return HTTP 200.
20. Fetch public blog URL and verify both CTA links are live before Threads.
21. Prepare Threads JSON payload and run `python3 scripts/threads-quality-gate.py /tmp/<slug>-threads-payload.json`.
22. Publish Threads only after gate passes.
23. Create wiki note: `/Users/conanssam-m4/.openclaw/wiki/main/sources/blog-research/<YYYY-MM-DD>-<slug>.md`.

## Threads contract
- Root-only is forbidden.
- Minimum 3 posts, recommended 4–6.
- Root has explicit image and no bare URL.
- Blog link goes in final or penultimate reply.
- If 4+ posts, attach at least 2 explicit images.
- Use Python list/subprocess or safe quoting. Dry-run must not contain literal `\\n`.

## Final report
Include:
- Blog URL and HTTP status
- Today's count after publish
- Image URLs and HTTP status
- Voice SpyRL mode (`multi-candidate` or `fallback-single`), winner, spy, score, tags, and report path
- Blog image gate result
- Blog promo gate result
- Blog SEO/AEO gate result
- Highlight markup count and public HTML verification
- Live CTA verification
- Original paper Figure/Table included? yes/no
- Commit hash
- Threads quality gate result
- Threads IDs and image post numbers
- Wiki note path
- Exact skip/block reason if stopped
