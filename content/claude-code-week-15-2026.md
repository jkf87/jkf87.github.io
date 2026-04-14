---
title: "Claude Code Week 15 · 4월 6–10일 신기능 요약"
date: 2026-04-14
tags:
  - claude-code
  - anthropic
  - ai-coding
  - release-notes
description: "Claude Code v2.1.92~v2.1.101 주간 다이제스트. Ultraplan 클라우드 계획 모드, Monitor Tool, /autofix-pr CLI 명령어, /team-onboarding 팀 온보딩 가이드 생성 기능을 소개합니다."
---

# Week 15 · 4월 6–10일, 2026

> **릴리즈:** [v2.1.92 → v2.1.101](https://code.claude.com/docs/en/changelog#2-1-92) | **4개 기능**

---

## 🔮 Ultraplan — *리서치 프리뷰*

터미널에서 클라우드 기반 계획 모드를 시작하고, 결과를 브라우저에서 검토합니다. Claude가 Claude Code on the Web 세션에서 계획을 작성하는 동안 터미널은 자유롭게 사용할 수 있습니다. 준비가 완료되면 개별 섹션에 코멘트를 달거나 수정을 요청하고, 원격에서 실행하거나 CLI로 되돌려 보낼 수 있습니다. v2.1.101부터 첫 실행 시 기본 클라우드 환경이 자동 생성되므로 별도 웹 설정 없이 바로 사용할 수 있습니다.

명령어를 실행하거나, 프롬프트에 키워드를 포함하세요:

```
> /ultraplan migrate the auth service from sessions to JWTs
```

📎 [Ultraplan 가이드](https://code.claude.com/docs/en/ultraplan)

---

## 📡 Monitor Tool — v2.1.98

백그라운드 감시자를 생성하고 이벤트를 대화에 실시간으로 스트리밍하는 새로운 내장 툴입니다. 각 이벤트가 새 트랜스크립트 메시지로 도착하고 Claude가 즉시 반응합니다. 학습 실행을 모니터링하거나, PR의 CI를 지켜보거나, 개발 서버 충돌을 순간적으로 자동 수정할 수 있습니다. Bash `sleep` 루프로 턴을 열어둘 필요가 없습니다.

Claude에게 무언가를 감시하도록 요청하세요:

```
> Tail server.log in the background and tell me the moment a 5xx shows up
```

이 기능은 `/loop`와 함께 사용하면 더 강력합니다. 이제 간격을 생략하면 Claude가 작업에 따라 다음 틱을 스케줄링하거나, Monitor Tool을 사용하여 폴링을 완전히 건너뜁니다.

```
> /loop check CI on my PR
```

📎 [Monitor Tool 레퍼런스](https://code.claude.com/docs/en/tools-reference#monitor-tool)

---

## 🔧 /autofix-pr — CLI

Week 13에 Claude Code on the Web에서 PR 자동 수정이 도입되었습니다. 이제 터미널을 떠나지 않고 사용할 수 있습니다. `/autofix-pr`은 현재 브랜치의 열린 PR을 자동 감지하고 Claude Code on the Web에서 자동 수정을 한 단계에 활성화합니다. 브랜치를 푸시하고 명령어를 실행한 후 자리를 비우세요. Claude가 CI와 리뷰 코멘트를 모니터링하며 모든 것이 통과될 때까지 수정을 푸시합니다.

PR 브랜치에서 실행:

```
> /autofix-pr
```

📎 [PR 자동 수정 가이드](https://code.claude.com/docs/en/claude-code-on-the-web#auto-fix-pull-requests)

---

## 👥 /team-onboarding — v2.1.101

로컬 Claude Code 사용 기록에서 팀원 램프업 가이드를 생성합니다. 잘 아는 프로젝트에서 실행한 뒤 결과물을 새 팀원에게 전달하면, 기본 설정부터 시작하는 대신 설정을 재현할 수 있습니다.

```
> /team-onboarding
```

📎 [명령어 레퍼런스](https://code.claude.com/docs/en/commands)

---

## 기타 개선 사항

- **Focus View:** 깜빡임 없는 모드에서 `Ctrl+O`를 누르면 마지막 프롬프트, 한 줄 툴 요약(diffstats 포함), Claude의 최종 응답만 표시되도록 화면이 축소됩니다
- **Bedrock / Vertex AI 설정 마법사:** 로그인 화면에서 "3rd-party platform" 선택 시 인증, 리전, 자격 증명 확인, 모델 고정까지 단계별로 안내합니다
- **`/agents` 탭 레이아웃:** Running 탭에서 실행 중인 서브에이전트를 `● N running` 카운트와 함께 표시하고, Library 탭에서 Run agent / View running instance 액션을 제공합니다
- **기본 노력 수준 상향:** API-key, Bedrock, Vertex, Foundry, Team, Enterprise 사용자의 기본값이 `high`로 변경되었습니다 (`/effort`로 제어)
- **`/cost` 개선:** 구독 사용자에게 모델별 + 캐시 적중 분석을 표시합니다
- **`/release-notes` 인터랙티브 버전 선택:** 이제 버전을 직접 선택할 수 있습니다
- **상태 표시줄:** `refreshInterval` 설정으로 N초마다 명령어를 자동 재실행하고, JSON 입력에 `workspace.git_worktree`를 지원합니다
- **Perforce 모드:** `CLAUDE_CODE_PERFORCE_MODE` 환경변수로 읽기 전용 파일에서 Edit/Write 실패 시 `p4 edit` 힌트를 표시합니다 (기존에는 조용히 덮어씀)
- **OS CA 인증서 저장소 기본 신뢰:** 기업 TLS 프록시가 별도 설정 없이 동작합니다 (`CLAUDE_CODE_CERT_STORE=bundled`으로 옵트아웃)
- **Bedrock Mantle 지원:** `CLAUDE_CODE_USE_MANTLE=1` 설정
- **Bash 툴 권한 강화:** 백슬래시 이스케이프 플래그, 환경변수 접두사, `/dev/tcp` 리다이렉트, 복합 명령어가 올바르게 프롬프트를 표시합니다
- **`UserPromptSubmit` 훅:** `hookSpecificOutput.sessionTitle`로 세션 제목 설정 가능

📎 [v2.1.92–v2.1.101 전체 체인지로그](https://code.claude.com/docs/en/changelog#2-1-92)
