---
title: "Claude Code Week 14 · 3월 30일–4월 3일 신기능 요약"
date: 2026-04-14
tags:
  - claude-code
  - anthropic
  - ai-coding
  - release-notes
description: "Claude Code v2.1.86~v2.1.91 주간 다이제스트. CLI에서 Computer Use, /powerup 인터랙티브 레슨, 깜빡임 없는 렌더링, MCP 결과 크기 오버라이드, 플러그인 PATH 실행 파일 지원을 소개합니다."
---

# Week 14 · 3월 30일–4월 3일, 2026

> **릴리즈:** [v2.1.86 → v2.1.91](https://code.claude.com/docs/en/changelog#2-1-86) | **5개 기능**

---

## 🖥️ CLI에서 Computer Use — *리서치 프리뷰*

지난주 Desktop 앱에 Computer Use가 도입되었습니다. 이번 주에는 CLI에도 동일하게 도입되었습니다. Claude가 네이티브 앱을 열고, UI를 클릭하고, 자신의 변경사항을 테스트하고, 문제가 발생하면 수정할 수 있습니다. 모든 것이 터미널에서 이루어집니다. 웹 앱은 이미 검증 루프가 있었지만, 네이티브 iOS, macOS 및 기타 GUI 전용 앱은 아니었습니다. 이제 가능합니다. API를 호출할 수 없는 앱과 툴에서 검증 루프를 닫는 데 최적입니다. 아직 초기 단계이므로 rough edge가 있을 수 있습니다.

`/mcp`를 실행하고 `computer-use`를 찾아 토글한 뒤, Claude에게 엔드투엔드 검증을 요청하세요:

```
> Open the iOS simulator, tap through onboarding, and screenshot each step
```

📎 [Computer Use 가이드](https://code.claude.com/docs/en/computer-use)

---

## ⚡ /powerup — v2.1.90

터미널 내에서 애니메이션 데모를 통해 Claude Code 기능을 가르치는 인터랙티브 레슨입니다. Claude Code는 자주 업데이트되며, 지난달에 작업 방식을 바꿀 수 있었던 기능들을 놓치기 쉽습니다. `/powerup`을 한 번만 실행하면 어떤 기능이 있는지 알 수 있습니다.

```
> /powerup
```

📎 [명령어 레퍼런스](https://code.claude.com/docs/en/commands)

---

## 🎨 깜빡임 없는 렌더링 (Flicker-free) — v2.1.89

가상화된 스크롤백을 갖춘 새로운 alt-screen 렌더러를 옵트인할 수 있습니다. 프롬프트 입력이 하단에 고정되고, 긴 대화에서도 마우스 선택이 작동하며, 리드로우 시 깜빡임이 사라집니다. 롤백하려면 `CLAUDE_CODE_NO_FLICKER` 환경변수를 해제하세요.

```bash
export CLAUDE_CODE_NO_FLICKER=1
claude
```

📎 [전체화면 렌더링 가이드](https://code.claude.com/docs/en/fullscreen)

---

## 📏 MCP 결과 크기 오버라이드 — v2.1.91

MCP 서버 작성자가 이제 특정 툴의 잘림 상한을 `tools/list` 응답에 `anthropic/maxResultSizeChars`를 설정하여 올릴 수 있으며, 최대 500K 문자까지 가능합니다. 기존에는 글로벌 제한이 있어서 데이터베이스 스키마나 전체 파일 트리 같은 본질적으로 큰 페이로드를 반환하는 툴이 기본 제한에 걸려 파일 참조로 디스크에 저장되었습니다. 툴별 오버라이드로 해당 툴이 실제로 필요할 때 결과를 인라인으로 유지할 수 있습니다.

서버의 `tools/list` 응답에 어노테이션을 추가하세요:

```json
{
  "name": "get_schema",
  "description": "Returns the full database schema",
  "_meta": {
    "anthropic/maxResultSizeChars": 500000
  }
}
```

📎 [MCP 레퍼런스](https://code.claude.com/docs/en/mcp#raise-the-limit-for-a-specific-tool)

---

## 🔌 플러그인 실행 파일 PATH — v2.1.91

플러그인 루트에 `bin/` 디렉토리를 만들고 실행 파일을 넣으면 Claude Code가 플러그인 활성화 동안 해당 디렉토리를 Bash 툴의 `PATH`에 추가합니다. Claude는 절대 경로나 래퍼 스크립트 없이 모든 Bash 툴 호출에서 바이너리를 직접 호출할 수 있습니다. 명령어, 에이전트, 훅과 함께 CLI 헬퍼를 패키징하기에 편리합니다.

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── bin/
    └── my-tool
```

📎 [플러그인 레퍼런스](https://code.claude.com/docs/en/plugins-reference#file-locations-reference)

---

## 기타 개선 사항

- **Auto Mode 후속 기능:** 새로운 `PermissionDenied` 훅이 분류기 거부 시 실행됩니다 (`retry: true`를 반환하면 Claude가 다른 방법을 시도). `/permissions` → Recent에서 `r`로 수동 재시도 가능
- **`defer` 권한 결정:** `PreToolUse` 훅에서 `permissionDecision`에 새로운 `defer` 값 지원. `-p` 세션이 툴 호출에서 일시 정지하고 `deferred_tool_use` 페이로드로 종료되어 SDK 앱이나 커스텀 UI에서 처리 가능. `--resume`으로 재개
- **`/buddy`:** 코딩을 지켜보는 작은 생물을 부화합니다 (만우절 이스터에그)
- **`disableSkillShellExecution`:** 스킬, 슬래시 명령어, 플러그인 명령어에서 인라인 셸 실행을 차단하는 설정
- **Edit 툴 개선:** `cat`이나 `sed -n`으로 본 파일에 별도 Read 없이 작동
- **훅 출력 50K 초과 시:** 디스크에 저장하고 경로 + 미리보기를 표시 (기존에는 컨텍스트에 직접 주입)
- **Thinking 요약 기본 비활성화:** 인터랙티브 세션에서 기본적으로 꺼짐 (`showThinkingSummaries: true`로 복원)
- **음성 모드:** 푸시투톡 수정자 조합, Windows WebSocket, macOS Apple Silicon 마이크 권한
- **`claude-cli://` 딥링크:** 멀티라인 프롬프트 지원 (`%0A` 인코딩)

📎 [v2.1.86–v2.1.91 전체 체인지로그](https://code.claude.com/docs/en/changelog#2-1-86)
