# Blog workflow v5 — REFACTOR-FIRST, DAILY OWNER REVIEW

Replaces the payload of `daily-blog-publish-v2-quality-gated` ("Aggressive blog publish v4"). Keep the schedule `0 7,10,13,16,19,22 * * *` (Asia/Seoul) and the model.

Why: AdSense refused conanssam.com for (1) Google-served ads on screens with replicated content and (2) low value content. Google's publisher policy forbids ads on auto-generated content that lacks human review or curation. AdSense help says to expand similar pages or merge them into one. So we keep every old post. The 810 queued posts are unpublished (`draft: true`) and nothing is deleted. The job now rebuilds them into fewer, better pages, and each page goes live only after the owner merges it.

Repo: `/Users/conanssam-m4/.openclaw/workspace-blogbot/site`
Queue: `scripts/refactor-queue.json`. Each hub has `hub_id`, `topic`, `treatment` (merge-synthesis | merge-handson | archive | owner-review), `members`, `status`.
Gate: `scripts/blog-refactor-gate.py --mode hub|expand|new`

## What still applies from the v2 runbook

`scripts/runbooks/daily-blog-publish-v2-runbook.md` keeps its voice, Voice SpyRL, highlight, search-first title and wiki-note sections. These parts of it NO LONGER apply: the 6-new-posts-per-day capacity note, candidate scanning for single papers, `## Images` paper-figure extraction, `## Standing CTA`, the multi-post `## Threads contract`, and the older-post SEO/topic-cluster pass. Everything below overrides them.

## Hard rules

- Never draft, queue, merge or alias a post listed in `scripts/keep-posts.json`. Those posts stay public. EXPAND may edit the expand targets in place.
- Never delete a post file. Old posts stay in the repo with `draft: true`. Merging only changes their `refactor_status`.
- Never publish a summary, translation or rewrite of a single source (paper, system card, vendor blog, news, video, talk, README, release notes).
- Never commit copied figures, tables, slides or screenshots from papers or other sites. Every image in a live post lives in `content/media/<slug>/` and is made by you: a diagram or chart from your own analysis, or a capture of your own command output or UI run.
- Never touch hubs with `treatment: archive` (health, off-topic, old drafts) or `owner-review`.
- Write as the author in the first person ("제가 돌려 봤습니다"). The owner reviews every post before merge. Never claim work that was not done in this run or by the owner. (Owner decision 2026-10-08; replaces the old "블로그봇이 실행해 보니" rule.)
- No health, medical, finance, investing, real-estate or politics topics.
- No mandatory book or lecture CTA. Mention the owner's OpenClaw book at most once, and only in OpenClaw-usage hubs.
- Titles must describe the content. Do not reuse the template "~하는 이유: ○○ 논문 정리".

## Each run: exactly one unit of work, in this priority order

0. Branch: always work on the single long-lived branch `refactor/live`. Run `git fetch origin`. If `origin/refactor/live` exists, check it out, `git pull --ff-only origin refactor/live`, then `git merge --no-edit origin/main`. If it does not exist (for example it was merged and deleted), create it from `origin/main`. Keep exactly one open PR `refactor/live` → `main` titled `refactor: 누적 리팩토링` and update its checklist every run. Never create date branches, so work never forks when the owner merges late.
0b. Late arrivals: a late arrival is a live post (`draft` not true) that is NOT listed in `scripts/keep-posts.json`, has no `refactor_hub_id`, and is not in `scripts/expand-targets.json`. Add each one to the closest hub's `members` and run `python3 scripts/mark-refactor-queue.py`. The script is idempotent and refuses protected posts.
0c. Priority: if `scripts/refactor-priority.json` lists hubs whose queue status is still `queued`, do the first of them in this run, before EXPAND. These hubs fix live links that were already shared on Threads.
0d. Never let one unit block the queue. If an EXPAND needs a download or job longer than about 20 minutes, start it in the background (tmux), record progress and resume steps in `sandbox/<slug>/RESUME.md`, and do the next HUB in the same run. Resume that EXPAND in a later run once the job has finished. If verification would need more than 20 GB of downloads, skip it and note that in `## 한계와 반론`.
1. **EXPAND (first):** pick one of the 10 live setup posts in `scripts/expand-targets.json` that has no `verified_at` in its frontmatter.
   - Re-run the documented steps on this machine in `~/.openclaw/workspace-blogbot/sandbox/<slug>/`.
   - Add `## 검증 로그`: the date, OpenClaw and tool versions, the exact commands, and trimmed real output in code blocks.
   - Add at least 2 captures of your own run to `content/media/<slug>/`.
   - Fix anything outdated. Set `verified_at: <date>`.
   - Gate: `--mode expand`.
2. **HUB:** pick the next hub with `status: queued`. Take `merge-handson` first, then `merge-synthesis` in this topic order: openclaw-updates, dev-tools, coding-agents, harness-self-improve, agent-memory, agent-rl, eval-benchmarks, agent-safety, multi-agent, web-gui-agents, research-agents, reasoning-efficiency, model-releases, multimodal-world, ai-trends-misc, ux-laws, llm-course-notes.
   - Read every member post, then verify key claims against primary sources (arXiv abstract page, official docs). Drop claims you cannot verify.
   - `merge-handson`: install and run the tools in the sandbox (see Safety) and compare them on the same small task. Record results in a table.
   - `merge-synthesis`: compare the methods on common axes (problem, key idea, data or benchmark, results, cost, limits). Make at least one original diagram or chart from that comparison.
   - `ux-laws`: turn the laws into a guide for designing classroom and work materials, with original examples.
   - Write `content/posts/<new-slug>.md` with this frontmatter:
     ```yaml
     title: "<descriptive Korean title>"
     date: <today>
     author: 한준구(코난쌤)
     description: "<1–2 sentences>"
     tags: [<≤5 tags>]
     refactor_hub_id: <hub_id>
     aliases:            # every member path without .md, so old URLs redirect here
       - <member path 1>
       - <member path 2>
     draft: false
     ```
   - Owner taste (2026-10-08, overrides older voice notes where they conflict): read `scripts/taste/taste-v1.md`, then `scripts/taste/taste-v2.md` (v2 wins where they differ), then the primary example `scripts/taste/example-owner-approved-verifier.md`, and match that voice, length and layout.
   - Voice and polish: keep the owner's approved style from `scripts/runbooks/daily-blog-publish-v2-runbook.md`. Follow `## Default blog voice` (conanssam-voice kakao/plain 실무 정리체). Run `## Voice SpyRL gate` with A/B/C variants and publish the winner. Apply `## Highlight markup` (5–14 key expressions, conclusions and numbers only). Use `## Search-first title policy`, but never the single-paper template.
   - Use these sections:
     - `## 한눈에 보는 결론`
     - `## 무엇을 비교했나` (numbered source list with links)
     - `## 방법 비교` (a table)
     - `## 언제 무엇을 쓰나` (a decision guide)
     - `## 제가 직접 확인한 것` (required for handson; for synthesis, e.g. code availability, license or a small reproduction)
     - `## 한계와 반론`
     - `## 적용 규칙` — what a reader who will actually use this should do. Every rule comes from what you measured or verified in this unit. Do not speculate.
       A classroom or office angle is OPTIONAL and goes here only when the topic genuinely has one. Never invent a teaching scenario to fill the section: no "수업 시연에서도", no "학습 지원 에이전트를 만든다면". A forced school frame reads as padding. When the topic has no such angle, write the rules plainly and stop.
     - `## 참고 자료`
   - Reference images from `content/posts/` as `../media/<new-slug>/<file>.png`.
   - End with this line: `이 글은 제가 여러 자료를 비교·정리하고 일부는 에이전트를 활용해 실행하고 확인한 내용으로 발행하였습니다.`
   - In each member post's frontmatter, set only `refactor_status: merged` and `merged_into: posts/<new-slug>`. Keep `draft: true`.
   - In the queue, set this hub's `status: in-review` and `hub_slug: posts/<new-slug>` with the helper:
     `python3 scripts/queue-set.py --hub <hub_id> --status in-review --hub-slug posts/<new-slug>`
     Never edit or rewrite `scripts/refactor-queue.json` by hand or with your own `json.dump`. A rewrite changes the indentation of all 13,000 lines, hides the real change and breaks merges. The helper changes three lines and keeps the format fixed. Use it for `published` too.
   - Add the hub link to the matching section of `content/categories.md`, creating the section if needed.
   - Gate: `--mode hub`.
3. **NEW (only when both queues are empty, at most one per day):** a roundup comparing 4 or more recent papers on one theme (hub rules apply), or a hands-on test of one tool (`--mode new`). Never a single-paper post.
   - **Writing about a paper? These three are not optional.** They come from a post that had to be retracted on 2026-09-26.
     a. Read the paper body, not the abstract. Then look for author code and data (repo, HF dataset, appendix). If released, open it. Public results files often let you recompute the headline numbers with no API calls — do that before writing a single number.
     b. Before calling anything your own finding, read the paper's contributions list and check it is not already there. The retracted post presented the paper's own contribution #2 as its discovery.
     c. If you build your own eval items, check for label leakage: does the wording of the "clean" answer give the label away? Fix or disclose it. Prefer the paper's released data over items you invent.
     Record both answers in frontmatter — the gate requires them for any post citing an arXiv id:
     `sources_read:` what you actually read (must name 본문 and the code/data, or say none exists)
     `novelty_vs_paper:` one line separating the paper's claims from yours

## Gates, build, review

- Run `python3 scripts/blog-refactor-gate.py <post> --mode <mode> --site-root .`, then `python3 scripts/blog-claim-verification-gate.py <post>`, then `python3 scripts/blog-taste-gate.py <post>` (fix every hard failure and the soft items it lists), then `npx quartz build`. Any failure: fix and rerun once. If it still fails, revert your changes for this unit and report the exact failures.
- Commit only this unit: the post, its `content/media/<slug>/`, the member frontmatter flags, `scripts/refactor-queue.json` and `content/categories.md`. Push the branch.
- Open or update one PR per day titled `refactor: <date>`, with a checklist of units, gate results and preview notes. At the end of every run that committed a unit, send the owner the PR link on Telegram. (The job has a trigger, `~/.openclaw/workspace-blogbot/scripts/blog_has_work.py`, that skips runs with no work, so there is no fixed 22:00 run any more.) If `gh` is unavailable, push the branch and send `https://github.com/jkf87/jkf87.github.io/compare/main...<branch>` instead. The owner merging the PR is the human review. After merge, set the merged hubs' queue status to `published` (`python3 scripts/queue-set.py --hub <hub_id> --status published`).
- For every unit, create the Obsidian note `/Users/conanssam-m4/.openclaw/wiki/main/sources/blog-research/<YYYY-MM-DD>-<slug>.md` as before.
- Threads (optional): after a merge, at most one post per published hub, linking to the hub. Never link to a post whose live URL is not HTTP 200.
- `REVIEW_MODE=pr` is the default. Switch to `auto` (push straight to `main` when every gate passes) only after the owner says so. Do not switch before AdSense approval.

## Safety for hands-on runs

- Only run tools from the queue's posts, and only from well-known orgs or popular repos. Never pipe remote scripts into a shell from unknown domains. Never use sudo.
- Use a venv or npx inside the sandbox dir. Cap each command at 10 minutes. Never expose credentials or env files to the tool, and redact paths and tokens from captures.
- If a tool needs paid APIs, a GPU you lack, or credentials, skip the run and say so in `## 한계와 반론`.

## Report (every run)

Unit type and id, branch, commit, gate results, PR link, and what you could not verify.
