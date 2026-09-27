---
title: "AI 코딩 에이전트 Claude Code 신기능 어디까지 살아남았나: Auto Mode·Computer Use 현재 상태와 Pro 구독 안전 가이드"
date: 2026-09-27
author: 한준구(코난쌤)
description: "Claude Code 2026년 3~4월 신기능 7편을 2026-09-27 기준 공식 문서로 다시 확인했습니다. Auto Mode는 기본값이 됐고 Ultraplan은 제거됐습니다. Pro 구독 포함 여부와 CLI 위임 안전 상태도 정리했습니다."
tags: [claude-code, ai-coding-agent, anthropic, devtools, subscription]
refactor_hub_id: coding-agents-07
aliases:
  - claude-code-week-13-2026
  - claude-code-week-14-2026
  - claude-code-week-15-2026
  - claude-code-whats-new-2026
  - openclaw-claude-code-cli-guide
  - openclaw-claude-code-delegation-safety
  - claude-code-pro-reversal-2026-04-22
draft: false
---

## 한눈에 보는 결론

2026년 3~4월에 Claude Code 신기능을 주 단위로 정리했던 글 7편을 한 편으로 합쳤습니다. 겹치는 내용은 걷어내고, 모든 주장을 2026-09-27 기준 공식 문서로 다시 확인했습니다. 반년 사이 상태가 달라진 기능이 있어서, 그 변화가 이 글의 본문입니다.

핵심은 이겁니다.

- Auto Mode가 정식 기본값이 됐습니다. 권한 프롬프트를 분류기 모델이 대신 판단하는 모드인데, <span style="background-color: #fff59d"><strong>8월 14일부터 Pro·Max·Team 플랜 새 세션의 시작 권한 모드로 지정됐습니다</strong></span>.
- Computer Use(CLI)는 아직 research preview입니다. <span style="background-color: #fff59d"><strong>macOS에서 Pro 또는 Max 플랜이 필요하고</strong></span> Team·Enterprise에서는 쓸 수 없습니다.
- <span style="background-color: #fff59d"><strong>Ultraplan은 제거됐습니다</strong></span>. 공식 문서가 더는 제공되지 않는다고 명시합니다. <span style="background-color: #fff59d"><strong>로컬 plan mode나 클라우드 세션</strong></span>으로 대체하라고 안내합니다.
- Claude Code는 Pro 플랜에 포함입니다. 가격 페이지와 도움말이 모두 확인해 줍니다. <span style="background-color: #fff59d"><strong>월 20달러, 4월의 표시 혼선은 해소됐습니다</strong></span>.
- OpenClaw의 Claude CLI 위임 방식은 <span style="background-color: #fff59d"><strong>현재 sanctioned 상태입니다</strong></span>. Anthropic 직원이 다시 허용됐다고 확인했다고 OpenClaw 문서에 적혀 있습니다. <span style="background-color: #fff59d"><strong>정책이 또 바뀌면 가장 먼저 흔들리는 경로</strong></span>라는 점은 여전합니다.

| 기능 | 발표 시점 | 2026-09-27 상태 |
|---|---|---|
| Auto Mode | 3월 23–27일 프리뷰 | 신규 세션 기본값(8/14부터) |
| Computer Use(CLI) | 4월 초 프리뷰 | 프리뷰 유지, macOS·Pro/Max 전용 |
| PR 자동 수정 /autofix-pr | 3월 Web, 4월 CLI | 정식 문서 등재 |
| Monitor 툴, /loop | 4월 6–10일 | 정식 문서 등재 |
| Hooks 조건부 if, PowerShell 툴 | 3월 | 정식 문서 등재 |
| Ultraplan | 4월 6–10일 프리뷰 | 제거 공지 |

![Claude Code 2026년 3~4월 신기능의 9월 27일 현재 상태](../media/ai-coding-agent-claude-code-features-safety-2026/chart-01-feature-status-2026-09-27.png)

## 무엇을 비교했나

합친 글 7편과 각각이 기대던 1차 출처입니다.

1. Claude Code Week 13 정리 글 — [공식 주간 다이제스트](https://code.claude.com/docs/en/whats-new) 3월 23–27일 항목(v2.1.83–85). Auto Mode, Desktop Computer Use, 웹 PR 자동 수정 발표.
2. Week 14 정리 글 — 같은 다이제스트 3월 30일–4월 3일 항목(v2.1.86–91). CLI Computer Use, /powerup, 깜빡임 없는 렌더링, MCP 결과 크기 오버라이드(최대 500K), 플러그인 실행 파일 PATH.
3. Week 15 정리 글 — 같은 다이제스트 4월 6–10일 항목(v2.1.92–101). Ultraplan, Monitor 툴, /autofix-pr CLI, /team-onboarding.
4. What's New 목차 글 — [주간 다이제스트 인덱스](https://code.claude.com/docs/en/whats-new) 역할을 하던 짧은 글.
5. OpenClaw–Claude Code CLI 연결 가이드 — [OpenClaw Anthropic 프로바이더 문서](https://docs.openclaw.ai/providers/anthropic) 기반. CLI 로그인 재사용 방법과 그때의 정책 해석.
6. CLI 위임 안전성 글 — [OpenClaw OAuth 문서](https://docs.openclaw.ai/concepts/oauth) 기반. API 키, CLI 위임, 토큰 직접 삽입, 구독 우회 프록시 비교.
7. Pro 가격표 되돌림 기록 글 — [Claude 가격 페이지](https://claude.com/pricing)와 [Anthropic 인프라 발표](https://www.anthropic.com/news/anthropic-amazon-compute). 4월 22일 가격 표시 충돌과 그 배경.

## 방법 비교

| 기능·경로 | 해결하는 문제 | 핵심 방법 | 근거(2026-09-27 확인) | 비용 | 확인된 한계 |
|---|---|---|---|---|---|
| Auto Mode | 매번 승인하는 수고 | 분류기 모델이 안전/위험을 판정, 위험은 차단 후 질문 | 권한 모드 문서: v2.1.283+ 기본 시작 모드 | 구독 포함 | 분류기 오판 가능성은 문서가 인정 |
| Computer Use(CLI) | API 없는 GUI 앱 검증 | 화면 보기, 클릭, 타이핑 | 문서: macOS research preview, 대화형 세션만 | Pro/Max 필수 | -p 비대화 모드 불가, Team·Enterprise 불가 |
| /autofix-pr | CI 실패 반복 수정 | 클라우드 세션이 PR 감시, 실패 시 수정 푸시 | 명령 문서: gh pr view로 PR 탐지 | 구독 포함 | 감시 대상은 체크아웃 브랜치 기준 |
| Monitor 툴 + /loop | 백그라운드 이벤트 대응 | 감시자 생성, 이벤트를 대화로 스트리밍 | 툴 레퍼런스 표 등재 | 구독 포함 | 이번 실행에서 실습은 못 함 |
| Hooks 조건부 if | 훅 남발 방지 | 권한 규칙 문법으로 훅 실행 조건 한정 | 훅 문서 예시 확인 | 무료 | 문법 오류 시 조용히 미실행 가능 |
| PowerShell 툴 | 윈도우 네이티브 작업 | cmdlet 실행, 객체 파이프 | 툴 레퍼런스 표 등재 | 무료 | 이 머신(macOS)에서 실습 못 함 |
| API 키 인증 | 제3자 도구 연동 | Console 키 발급 후 연결 | OpenClaw 프로바이더 문서 | 사용량 과금 | 예산 관리 필요 |
| CLI 위임(--method cli) | 구독을 다른 도구에서 활용 | 공식 CLI 실행파일의 로그인 재사용 | OpenClaw 문서: sanctioned 분류 | 구독 포함 | 정책 변경 시 최우선 영향 경로 |

Ultraplan 자리는 이렇게 채우면 됩니다. 터미널에서 계획만 빠르게 세울 때는 <span style="background-color: #fff59d"><strong>로컬 plan mode</strong></span>, 브라우저에서 검토하며 다듬을 때는 <span style="background-color: #fff59d"><strong>클라우드 세션</strong></span>입니다. 공식 문서가 제거 안내와 함께 이 두 가지를 대안으로 제시했습니다.

4월의 Pro 가격표 사건은 이렇게 정리됩니다. 가격 표시에서 Pro의 Claude Code가 잠깐 빠진 것처럼 보였고, 몇 시간 뒤 돌아왔습니다. 지금은 <span style="background-color: #fff59d"><strong>가격 페이지에 Pro 항목으로 Claude Code 포함이 명시</strong></span>돼 있고, 도움말 문서(8월 19일 갱신)도 Pro 또는 Max로 안내합니다. 표시 오류였는지 정책 테스트였는지는 공식 설명이 없어서 판단을 유보합니다.

인증 경로는 순위가 명확합니다. <span style="background-color: #fff59d"><strong>API 키가 정책 리스크 최소</strong></span>, CLI 위임은 현재 허용이지만 모니터링 대상, <span style="background-color: #fff59d"><strong>OAuth 토큰 직접 삽입과 구독 우회 프록시는 피하는 쪽</strong></span>입니다.

## 언제 무엇을 쓰나

![권한 모드 스펙트럼과 인증 경로 안전도](../media/ai-coding-agent-claude-code-features-safety-2026/chart-02-auth-permission-map-2026-09-27.png)

- 반복 잡무의 승인 피로가 크면 Auto Mode로 시작합니다. 보호 경로 쓰기는 여전히 묻는 점도 함께 둡니다.
- GUI에서만 재현되는 버그, API 없는 앱 검증은 Computer Use입니다. 범위는 앱 하나로 좁게 잡고 Pro/Max 세션에서 돌립니다.
- PR을 밀어두고 자리 비울 일이 있으면 /autofix-pr로 클라우드 감시를 붙입니다.
- 로그 테일, CI 감시 같은 대기형 작업은 Monitor 툴이나 /loop에 맡깁니다. sleep 폴링은 버립니다.
- 커밋 전 린트처럼 특정 명령에만 걸어야 하는 훅은 if 필드로 조건을 좁힙니다.
- 다른 도구에서 Claude를 쓸 일이 생기면 API 키부터 검토하고, 구독 재사용은 CLI 위임만 씁니다. 토큰 직접 삽입과 프록시는 선택지에서 지웁니다.

## 블로그봇이 직접 확인한 것

- 이 머신에서 claude --version을 실행해 <span style="background-color: #fff59d"><strong>2.1.220</strong></span>을 확인했습니다. --help의 권한·에이전트 관련 옵션도 문서와 대조했습니다.
- 공식 주간 다이제스트에서 Week 13·14·15 항목을 전부 다시 읽고 기능 목록을 대조했습니다.
- 권한 모드 문서에서 Auto Mode 기본화(v2.1.283+, 8월 14일부터 신규 세션 적용)를 확인했습니다.
- Computer Use 문서에서 프리뷰 조건(macOS, Pro/Max, 대화형 세션만)을 확인했습니다.
- Ultraplan 문서가 제거 공지로 대체된 것을 확인했습니다.
- 훅 문서의 if 예시, 툴 레퍼런스의 PowerShell·Monitor 등재, 명령 문서의 /autofix-pr 항목, 전체화면 문서의 CLAUDE_CODE_NO_FLICKER를 확인했습니다.
- claude.com/pricing에서 Pro의 Claude Code 포함과 가격(월 20달러, 연간 결제 17달러)을 확인했습니다.
- OpenClaw 공식 문서의 Anthropic 프로바이더 페이지와 OAuth 개념 페이지에서 CLI 재사용의 sanctioned 분류와 <span style="background-color: #fff59d"><strong>Anthropic 직원이 다시 허용됐다고 확인</strong></span>한 문구를 읽었습니다.
- AWS 확장 발표(<span style="background-color: #fff59d"><strong>최대 5GW, 10년간 1,000억 달러 이상</strong></span>)와 Google Cloud TPU 확대 발표(<span style="background-color: #fff59d"><strong>최대 100만 TPU</strong></span>)를 원문으로 확인했습니다.

## 한계와 반론

- 원래 글이 인용하던 이슈 번호 하나는 삭제했습니다. 실제로 확인해 보니 주제가 달라서 <span style="background-color: #fff59d"><strong>원 주장의 근거가 될 수 없었습니다</strong></span>.
- 4월 당시의 서버 차단 일자와 세부 범위는 이번에 재확인하지 못했습니다. 당시 기록으로만 남깁니다.
- Ultraplan 제거 사유는 공식 문서가 research preview의 수명 규칙 이상을 설명하지 않습니다.
- /powerup, /team-onboarding, MCP 크기 오버라이드는 주간 다이제스트로 확인했지만 현재 문서 페이지에서는 이번 실행으로 재확인하지 못했습니다. 문서 페이지가 길어 전체를 가져오지 못했습니다.
- 가격, 플랜 구성, 문서 상태는 <span style="background-color: #fff59d"><strong>모두 2026-09-27 기준입니다</strong></span>. 이후에 바뀔 수 있습니다.
- 이번 실행에서 Claude Code 세션을 실제로 구동하지는 못했습니다. 구독 로그인이 필요한 부분이라 문서 확인으로 대신했습니다.

## 적용 규칙

- 새 세션은 Auto Mode 기본값을 그대로 쓰되, 보호 경로 쓰기가 자동 승인되지 않는다는 문서 동작을 팀에 미리 공유합니다.
- Computer Use는 GUI 검증이 필요한 최소 범위에만 쓰고, 구조화된 통합(MCP, 플러그인)이 있으면 그걸 먼저 씁니다.
- /autofix-pr는 감시할 PR이 있는 브랜치에서만 켜고, 결과는 커밋 히스토리로 검증합니다.
- 대기형 작업은 Monitor 툴이나 /loop로 넘기고 Bash sleep 폴링은 만들지 않습니다.
- 훅은 if 조건으로 좁혀서 등록하고, 등록 후 한 번은 의도한 발동을 확인합니다.
- 제3자 도구 연동은 API 키 기준으로 설계하고, CLI 위임은 허용 상태를 문서로 계속 확인합니다. 토큰 직접 삽입과 프록시는 운영 환경에서 금지합니다.

## 자주 묻는 질문

### Claude Code는 Pro 플랜에서 쓸 수 있나요?

네. 2026-09-27 가격 페이지에 Pro 항목으로 Claude Code 포함이 명시돼 있고, 도움말 문서도 Pro 또는 Max 구독으로 안내합니다. 월 20달러, 연간 결제로는 17달러입니다.

### Auto Mode는 안전한가요?

안전한 편집과 명령은 분류기가 통과시키고, 파괴적이거나 의심스러운 작업은 차단해 사용자에게 묻는 구조입니다. 보호 경로 쓰기는 자동 승인 대상이 아니라는 점만 함께 두면 됩니다.

### Ultraplan은 왜 없어졌나요?

공식 문서가 research preview 제거 공지만 남겼고, 사유는 설명하지 않았습니다. 계획 작업은 로컬 plan mode나 클라우드 세션으로 대체하라고 안내합니다.

### OpenClaw에서 Claude CLI 위임은 지금도 되나요?

됩니다. OpenClaw 문서는 Anthropic 직원의 재허용 확인에 따라 CLI 재사용을 sanctioned로 분류합니다. 다만 정책이 다시 바뀌면 가장 먼저 영향받는 경로라서, 문서 상태를 주기적으로 확인하는 걸 권합니다.

## 참고 자료

- Claude Code 권한 모드 문서 https://code.claude.com/docs/en/permission-modes
- Claude Code Computer Use 문서 https://code.claude.com/docs/en/computer-use
- Ultraplan 제거 안내 https://code.claude.com/docs/en/ultraplan
- Claude Code 주간 다이제스트 https://code.claude.com/docs/en/whats-new
- Claude Code 훅 레퍼런스 https://code.claude.com/docs/en/hooks
- Claude Code 툴 레퍼런스 https://code.claude.com/docs/en/tools-reference
- Claude 가격 페이지 https://claude.com/pricing
- Claude Code Pro/Max 도움말 https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan
- OpenClaw Anthropic 프로바이더 문서 https://docs.openclaw.ai/providers/anthropic
- OpenClaw OAuth 문서 https://docs.openclaw.ai/concepts/oauth
- Anthropic AWS 확장 발표 https://www.anthropic.com/news/anthropic-amazon-compute
- Anthropic Google Cloud TPU 확대 발표 https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
