# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Quartz Blog (jkf87.github.io)

**이미지 경로 규칙 — 반드시 준수:**

- 이미지 파일 위치: `content/images/<post-slug>/` (절대경로 컨벤션)
- 마크다운 참조: `/images/<post-slug>/file.jpg` (슬래시로 시작하는 **절대경로**)
- ❌ 절대 금지: `images/...` 상대경로 → Quartz 빌드 시 `../images/`로 변환되어 404 발생
- Quartz 빌드: `content/images/` → `public/images/` 로 복사
- `content/posts/images/` 에 넣으면 `public/posts/images/` 에만 복사됨 (포스트 HTML에선 `/images/`를 찾으므로 깨짐)

**배포 구조:**
- 저장소: `jkf87/jkf87.github.io` (Quartz 프로젝트 = 배포 레포)
- 배포 브랜치: `main`
- 빌드: GitHub Actions (`deploy.yml`) → `npx quartz build` → `public/` 업로드 → Pages 배포
- `public/`에 직접 파일 추가해도 다음 빌드 시 덮어씀 → 반드시 소스(`content/`)에서 수정

## Related

- [Agent workspace](/concepts/agent-workspace)
