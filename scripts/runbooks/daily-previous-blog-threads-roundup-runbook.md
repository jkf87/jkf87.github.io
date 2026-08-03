# Daily Previous Blog Threads Roundup Runbook

Use this runbook for `daily-previous-blog-threads-roundup`.

Goal: every morning, make a Threads roundup of yesterday's jkf87.github.io Quartz posts.

Style:
- Use the same `kakao/plain` blog voice surface: direct, short, practical.
- No grand hook, no `알아보겠습니다`, no `하지만`, no `첫째/둘째/셋째/넷째`, no `A가 아니라 B다` aphorism.
- Root: common theme of yesterday's posts. No URL in root.
- Replies: one reply per post, short intro + existing Threads root permalink if found, otherwise blog URL.

Dedup first:
- Compute `runDate=today KST`, `forDate=yesterday KST`.
- If `/Users/conanssam-m4/.openclaw/workspace-blogbot/memory/threads-roundup/{runDate}.json` exists with `kind=previous-day-blog-threads-roundup`, do not post again. Announce already posted with rootPermalink.

Workflow:
1. Find yesterday's posts from `/Users/conanssam-m4/.openclaw/workspace-blogbot/site/content/posts` using frontmatter date or slug/date.
2. Search `published-log.json`, MEMORY.md, `memory/*.md`, and if needed Threads Graph API for each post's existing Threads root permalink.
3. If no posts, do not post. Announce `어제 발행된 블로그 글 없음`.
4. Compose root + N replies. Keep each post safely within Threads limit.
5. Use Python list/subprocess with `/Users/conanssam-m4/.openclaw/workspace-agasabot/skills/threads-uploader/scripts/post_threads.py` and env `/Users/conanssam-m4/.openclaw/creds/threads/.env`.
6. Always dry-run first. If dry-run posts array contains literal `\\n`, stop and fix.
7. Publish after dry-run passes.
8. If interrupted, use `/tmp/threads-post-state/<fingerprint>.json` to resume without duplication.
9. After success, write marker JSON to `/Users/conanssam-m4/.openclaw/workspace-blogbot/memory/threads-roundup/{runDate}.json` with rootPermalink, rootId, replyIds, forDate, postedAt, linkFallbacks.
10. Final announce: root permalink, IDs, blog count, fallback count.

External posting is pre-authorized only inside this cron scope.
