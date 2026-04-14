---
title: "Claude Code Week 13 · 3월 23–27일 신기능 요약"
date: 2026-04-14
tags:
  - claude-code
  - anthropic
  - ai-coding
  - release-notes
description: "Claude Code v2.1.83~v2.1.85 주간 다이제스트. Auto Mode 권한 분류, Desktop Computer Use, PR 자동 수정, 트랜스크립트 검색, PowerShell 툴, 조건부 훅을 소개합니다."
---

# Week 13 · 3월 23–27일, 2026

> **릴리즈:** [v2.1.83 → v2.1.85](https://code.claude.com/docs/en/changelog#2-1-83) | **6개 기능**

---

## 🤖 Auto Mode — *리서치 프리뷰*

Auto Mode는 권한 프롬프트를 분류기에 위임합니다. 안전한 편집과 명령어는 사용자를 방해하지 않고 실행되고, 파괴적이거나 의심스러운 작업은 차단되어 표시됩니다. 모든 파일 쓰기를 일일이 승인하는 것과 `--dangerously-skip-permissions`로 실행하는 것 사이의 중간 지점입니다.

**Shift+Tab**으로 Auto 모드로 전환하거나, 기본값으로 설정할 수 있습니다:

```json
{
  "permissions": {
    "defaultMode": "auto"
  }
}
```

📎 [권한 모드 가이드](https://code.claude.com/docs/en/permission-modes)

---

## 🖥️ Computer Use — Desktop

Claude가 Claude Code Desktop 앱에서 실제 데스크톱을 제어할 수 있습니다: 네이티브 앱 열기, iOS 시뮬레이터 클릭, 하드웨어 제어판 조작, 화면에서 변경사항 확인. 기본적으로 꺼져 있으며 각 작업 전에 확인을 요청합니다. API가 없는 앱, 독점 도구, GUI로만 존재하는 것 등 다른 방법으로는 도달할 수 없는 작업에 최적입니다.

설정에서 활성화하고 OS 권한을 부여한 뒤, Claude에게 엔드투엔드 검증을 요청하세요:

```
> Open the iOS simulator, tap through the onboarding flow, and screenshot each step
```

📎 [Computer Use 가이드](https://code.claude.com/docs/en/desktop#let-claude-use-your-computer)

---

## 🔧 PR 자동 수정 (Auto-fix PR) — Web

PR을 열 때 스위치를 켜고 자리를 비우세요. Claude가 CI를 모니터링하고, 실패를 수정하고, 사소한 지적을 처리하며 모든 것이 통과될 때까지 푸시합니다. 더 이상 6라운드의 린트 에러를 PR에서 baby-sitting할 필요가 없습니다.

Claude Code on the Web에서 PR을 생성한 후 CI 패널에서 Auto fix를 토글하세요.

📎 [PR 자동 수정 가이드](https://code.claude.com/docs/en/claude-code-on-the-web#auto-fix-pull-requests)

---

## 🔍 트랜스크립트 검색 — v2.1.83

트랜스크립트 모드에서 `/`를 눌러 대화를 검색합니다. `n`과 `N`으로 매치를 순회합니다. 400개 메시지 전에 Claude가 실행한 그 Bash 명령어 하나를 찾는 방법이 마침내 생겼습니다.

```bash
Ctrl+O    # 트랜스크립트 열기
/migrate  # "migrate" 검색
n         # 다음 매치
N         # 이전 매치
```

📎 [전체화면 가이드](https://code.claude.com/docs/en/fullscreen#search-and-review-the-conversation)

---

## 💻 PowerShell 툴 — *프리뷰*, v2.1.84

Windows에 Bash와 함께 네이티브 PowerShell 툴이 도입되었습니다. Claude가 cmdlet을 실행하고, 객체를 파이프하며, Git Bash를 거치지 않고 Windows 네이티브 경로로 작업할 수 있습니다.

설정에서 옵트인:

```json
{
  "env": {
    "CLAUDE_CODE_USE_POWERSHELL_TOOL": "1"
  }
}
```

📎 [PowerShell 툴 문서](https://code.claude.com/docs/en/tools-reference#powershell-tool)

---

## 🪝 조건부 훅 (Conditional Hooks) — v2.1.85

훅에 권한 규칙 문법을 사용하는 `if` 필드를 선언할 수 있습니다. pre-commit 체크가 모든 Bash 호출이 아닌 `Bash(git commit *)`에만 실행되도록 하여 바쁜 세션에서 프로세스 오버헤드를 줄입니다.

```json
{
  "hooks": {
    "PreToolUse": [{
      "hooks": [{
        "if": "Bash(git commit *)",
        "type": "command",
        "command": ".claude/hooks/lint-staged.sh"
      }]
    }]
  }
}
```

📎 [훅 레퍼런스](https://code.claude.com/docs/en/hooks)

---

## 기타 개선 사항

- **플러그인 `userConfig` 공개:** 활성화 시 설정 프롬프트, 키체인 기반 시크릿 지원
- **이미지 붙여넣기:** `[Image #N]` 칩이 삽입되어 위치별로 참조 가능
- **`managed-settings.d/`:** 계층화된 정책 프래그먼트용 드롭인 디렉토리
- **`CwdChanged` / `FileChanged` 훅 이벤트:** direnv 스타일 설정 지원
- **에이전트 `initialPrompt`:** 프론트매터에 선언하면 첫 턴을 자동 제출
- **`Ctrl+X Ctrl+E`:** readline과 동일하게 외부 에디터 열기
- **응답 전 중단:** 입력이 자동으로 복원됨
- **`/status` 개선:** Claude가 응답 중에도 사용 가능
- **딥링크:** 첫 번째 감지된 터미널이 아닌 선호하는 터미널에서 열림
- **75분 이상 비활동 시 `/clear` 권장** 메시지 표시
- **VS Code:** 속도 제한 배너, Esc 두 번 누르기 되감기 선택기

📎 [v2.1.83–v2.1.85 전체 체인지로그](https://code.claude.com/docs/en/changelog#2-1-83)
