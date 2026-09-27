---
title: "AI 코딩 에이전트 어디서 돌릴까: Codex 앱·모바일·Windows 샌드박스·AionUi 허브 7편 통합 가이드"
date: 2026-09-27
author: 한준구(코난쌤)
description: "OpenAI Codex를 앱·CLI·모바일·원격 SSH 어디서 돌릴지, 컴퓨터 유즈·자동화·서브에이전트를 어떻게 얹을지 정리했습니다. Windows 샌드박스 구조, Claude Code 요금 정리, AionUi 멀티 CLI 허브까지 1차 출처로 2026-09-27 다시 확인했습니다."
tags: [ai-coding-agent, codex, openai, aionui, devtools]
refactor_hub_id: coding-agents-06
aliases:
  - codex-computer-use
  - claude-code-pro-pricing-confusion-2026-04-22
  - aionui-open-source-cowork-ai-agent-2026-04-29
  - openai-codex-masterclass-2026-05-02
  - openai-codex-masterclass-josh-style-2026-05-02
  - openai-codex-windows-mobile-safety-may2026
  - ai-coding-agent-papers
draft: false
---

## 한눈에 보는 결론

코딩 에이전트 이야기가 "어떤 모델이 똑똑한가"에서 "어디서 돌리고, 무엇을 허용하고, 여러 개라면 어떻게 묶을까"로 넘어왔습니다. 이 글은 그 전환을 보여주는 글 7편을 합쳐 다시 쓴 통합 가이드입니다. 겹치는 주장은 1차 출처로 전부 재확인했고, 바뀐 부분은 2026-09-27 기준으로 고쳤습니다.

정리하면 이렇습니다.

- OpenAI Codex는 이제 <span style="background-color: #fff59d"><strong>앱(macOS·Windows)·CLI·IDE·ChatGPT 모바일·Remote SSH</strong></span>까지 실행 환경을 넓혔습니다. 주간 사용자는 마스터클래스 발표 때 300만이었고, 지금 공식 페이지에는 <span style="background-color: #fff59d"><strong>400만 이상</strong></span>으로 적혀 있습니다.
- 위험 관리 도구도 같이 붙었습니다. Windows 전용 샌드박스, 앱별 승인, Hooks GA, 그리고 GUI 조작을 해주는 Computer Use까지.
- 도구가 여러 개면 허브가 필요해집니다. 오픈소스 AionUi는 Claude Code·Codex·Gemini CLI를 한 화면에 묶고, <span style="background-color: #fff59d"><strong>MCP 설정을 한 번만 하고 동기화</strong></span>합니다.
- Claude Code 요금 혼선(2026-04-22)은 해소됐습니다. 2026-09-27 가격 페이지 기준 <span style="background-color: #fff59d"><strong>Pro 플랜에 Claude Code 포함</strong></span>, 월 20달러입니다.

| 수단 | 한 줄 결론 | 확인(2026-09-27) |
|---|---|---|
| Computer Use | GUI 앱을 직접 보고 조작 | macOS+Windows 지원으로 확대 |
| Automations | 크론처럼 도는 백그라운드 에이전트 | 마스터클래스 발표 |
| 서브에이전트 | 탐색·검토를 병렬로 쪼개기 | 마스터클래스 발표 |
| Windows 샌드박스 | 관리자 권한 없는 쓰기 격리 | 공식 엔지니어링 포스트 |
| 모바일+Remote SSH | 폰으로 승인·방향 전환 | 공식 포스트, 모든 플랜 프리뷰 |
| AionUi 허브 | 멀티 CLI 한 화면·MCP 동기화 | GitHub API 실측 |
| Claude Code 요금 | Pro 포함 확인으로 혼선 종료 | claude.com/pricing 실측 |

![AI 코딩 에이전트 실행 환경 4계층](../media/ai-coding-agent-codex-ecosystem-2026/chart-01-four-layers-2026-09-27.png)

## 무엇을 비교했나

2026년 4~5월에 따로 썼던 글 7편을 한 주제로 합쳤습니다. 각 글이 어떤 1차 출처에 기대 있었는지 함께 적습니다.

1. [OpenAI Codex Computer Use 소개 글](https://developers.openai.com/codex/app/computer-use) — Codex 앱이 데스크톱 GUI를 보고 조작하는 기능. 당시에는 macOS 전용이었는데, 지금은 Windows도 지원합니다.
2. [Codex 마스터클래스 정리 2편](https://youtu.be/MhHEGMFCEB0) — OpenAI 개발자 경험팀(Katia Gil Guzman·Vaibhav Srivastav) 발표. 플러그인·자동화·서브에이전트·Guardian Approvals·훅을 다룹니다. 같은 발표를 두 각도로 정리했던 글을 하나로 합쳤습니다.
3. [Codex 5월 업데이트 정리 글](https://openai.com/index/work-with-codex-from-anywhere/) — Windows 샌드박스, ChatGPT 모바일 Codex, Safety Summary 세 건을 다룬 글입니다. 원문 세 편([샌드박스](https://openai.com/index/building-codex-windows-sandbox/), [모바일](https://openai.com/index/work-with-codex-from-anywhere/), [Safety Summary](https://openai.com/index/chatgpt-recognize-context-in-sensitive-conversations/))을 다시 읽었습니다.
4. [AionUi 소개 글](https://github.com/iOfficeAI/AionUi) — Claude Code·Codex·Gemini CLI를 한 화면에 묶는 오픈소스 Cowork 앱.
5. [Claude Code 요금 혼선 기록 글](https://claude.com/pricing) — 가격 페이지·도움말이 서로 충돌하던 시기의 분석. 지금은 해소 상태를 확인했습니다.
6. AI 코딩 에이전트 링크 모음 글 — 18개 글을 묶던 주제 클러스터 페이지. 이 허브가 그 역할을 이어받습니다.

## 방법 비교

| 수단 | 해결하는 문제 | 핵심 방법 | 근거·데이터 | 비용 | 확인된 한계 |
|---|---|---|---|---|---|
| Computer Use | CLI·API로 못 하는 GUI 작업 | 화면 보기+클릭·타이핑. macOS는 화면 녹화·접근성 권한 | 공식 문서(2026-09-27): macOS·Windows 지원 | Codex 구독 포함 | Windows는 활성 데스크톱 포그라운드에서만. 터미널 앱·Codex 자체는 조작 불가 |
| Automations | 매일 반복되는 잡무 | 크론 주기+지시문, 백그라운드 실행 | 마스터클래스: Slack 요약·Gmail 트리아지 예시 | 구독 포함 | 발표 사례 재현은 이번 실행에서 못 함 |
| 서브에이전트 | 큰 작업의 병렬 탐색·검토 | TOML 페르소나, 모델·샌드박스·MCP 접근 개별 지정 | 마스터클래스: 45개 페르소나 검토 데모 | mini/nano 모델로 절감 가능 | 조율 비용과 결과 취합 품질은 별도 과제 |
| Windows 샌드박스 | Windows에서 무승인 안전 실행 | 합성 SID+쓰기 제한 토큰으로 쓰기 범위 한정 | 공식 엔지니어링 포스트(2026-05-13) | 무료(기본 기능) | AppContainer·Windows Sandbox·MIC는 부적합 판정, 자체 구현 |
| 모바일+Remote SSH | 장시간 작업의 중간 개입 | 보안 릴레이로 원격 머신 상태를 폰에 미러링 | 공식 포스트(2026-05-14): 승인·스레드 전환 | 모든 플랜 프리뷰(Free 포함) | 머신이 연결돼 있어야 동작 |
| AionUi 허브 | CLI 도구 여러 개 관리 | 멀티 CLI 통합+MCP 통합 관리+Team Mode | GitHub API(2026-09-27): 스타 33,157·Apache-2.0 | 무료(오픈소스), 모델 비용 별도 | Electron 앱, 자동 승인 모드 리스크 |
| Claude Code(요금) | 진입 요금제 판단 | Pro 플랜에 Claude Code 포함 | claude.com/pricing(2026-09-27): 월 $20(연간 $17) | Pro $20~/Max $100~ | 사용량 한도는 플랜별 상이 |

Computer Use의 쓰임새가 문서에 명확히 적혀 있습니다. <span style="background-color: #fff59d"><strong>구조화된 통합(플러그인·MCP)이 있으면 그걸 먼저 쓰고</strong></span>, GUI 검증이 꼭 필요할 때만 Computer Use를 쓰라고 권합니다. 스크린샷 판단이 중요한 작업에는 GPT-6 Astra 모델 선택이 안내돼 있습니다.

Windows 샌드박스 이야기는 엔지니어링 관점에서 읽을 가치가 있습니다. 2025년 9월에 착수해서, AppContainer는 너무 좁고 Windows Sandbox는 Home 에디션에 없으며 MIC 레이블은 디렉터리 전체를 낮춰버리는 문제가 있어서 <span style="background-color: #fff59d"><strong>합성 SID와 쓰기 제한 토큰을 직접 조합</strong></span>했다는 결론입니다. 관리자 권한 없이 작동합니다.

Safety Summary 수치도 원문과 대조했습니다. 단일 대화 기준 자살·자해 시나리오 안전 응답 <span style="background-color: #fff59d"><strong>+50%</strong></span>, 타인 해악 <span style="background-color: #fff59d"><strong>+16%</strong></span>. 복수 대화(GPT-5.5 Instant)에서는 자살·자해 +39%, 타인 해악 +52%입니다. 요약 품질은 4,000건 이상 평가에서 안전 관련성 4.93/5, 사실 정확도 4.34/5였습니다.

AionUi는 2026-04-29 글 쓸 때 스타 22.8k였는데, 지금은 <span style="background-color: #fff59d"><strong>33,157(2026-09-27 GitHub API)</strong></span>입니다. 5개월간 약 45% 늘었습니다. 라이선스는 Apache-2.0, 마지막 푸시는 2026-09-09로 활동 중입니다.

## 언제 무엇을 쓰나

![기능 선택 결정 흐름](../media/ai-coding-agent-codex-ecosystem-2026/chart-02-decision-flow-2026-09-27.png)

- 정기 반복 잡무(메일 트리아지, 채널 요약)는 Automations에 맡깁니다. 크론 주기와 지시문만 정하면 됩니다.
- 버그가 GUI에서만 재현되거나, API 없는 앱을 확인해야 하면 Computer Use입니다. 범위는 앱 하나로 좁게 잡습니다.
- 코드베이스 탐색·다각 검토는 서브에이전트가 맞습니다. 탐색 전용이면 read-only 샌드박스를 지정합니다.
- 장시간 작업을 돌려두고 밖에서 관리할 때는 모바일+Remote SSH 조합입니다.
- Claude Code·Codex·Gemini CLI를 함께 쓰고 MCP 설정이 도구마다 반복된다면 AionUi 허브를 검토합니다. 다만 <span style="background-color: #fff59d"><strong>자동 승인(YOLO) 모드는 테스트 폴더로 한정</strong></span>해야 합니다.
- 예산이 시작점이면, Claude Code는 이제 Pro(월 $20)부터 쓸 수 있고 Codex는 Free 플랜에서도 모바일 프리뷰가 열려 있습니다.

## 블로그봇이 직접 확인한 것

이번 통합 작업에서 직접 실행·확인한 기록입니다.

- OpenAI 1차 출처 4건을 2026-09-27에 다시 불러왔습니다. Computer Use 문서는 macOS 전용에서 <span style="background-color: #fff59d"><strong>macOS+Windows 지원으로 바뀐 것을 확인</strong></span>했고, 모바일 발표 페이지에는 주간 사용자 400만 이상이 적혀 있었습니다. Windows 샌드박스 포스트에서 SID·쓰기 제한 토큰 서술을, Safety Summary 포스트에서 수치 다섯 개를 원문과 대조했습니다.
- GitHub API(iOfficeAI/AionUi)로 스타 33,157·포크 3,444·라이선스 Apache-2.0·마지막 푸시 2026-09-09를 실측했습니다.
- claude.com/pricing을 불러서 Pro 항목의 "Claude Code included" 문구와 가격(월 $20, 연간 결제 $17, Max $100부터)을 확인했습니다. 4월의 표기 충돌은 남아 있지 않았습니다.
- 마스터클래스 영상의 존재와 제목·발표자(Vaibhav Srivastav, Katia Gil Guzman)를 확인했습니다. 영상 내용 인용은 발표 주장으로 처리했습니다.

## 한계와 반론

- 마스터클래스에서 나온 수치(주간 300만, WebSockets 1.75배, Fast Mode 2배, 전사 PR 기본 리뷰)는 발표 주장을 그대로 옮긴 것입니다. 독립 재측정은 하지 못했습니다. 사용자 수는 공식 페이지가 이미 400만 이상으로 갱신해서, 발표 수치는 시점 기록으로만 읽어야 합니다.
- Codex 앱의 자동화·서브에이전트·Computer Use를 이번 실행에서 직접 돌리지는 못했습니다. 구독 계정과 데스크톱 앱이 필요해서입니다. AionUi도 설치 실습이 아니라 README와 저장소 메타데이터 확인까지입니다.
- 가격·스타 수치는 모두 2026-09-27 기준이라 이후에 변합니다.
- 스타가 5개월간 45% 늘었다고 품질이 보증되지는 않습니다. Electron 기반 앱의 리소스 사용, 원격 채널 연결, 자동 승인 모드 같은 리스크는 숫자와 무관하게 남습니다.

## 적용 규칙

- GUI 검증이 필요한 작업에만 Computer Use를 쓰고, 구조화된 통합이 존재하면 그걸 먼저 씁니다. 공식 문서의 권장 순서를 그대로 따른 규칙입니다.
- macOS에서 Computer Use를 쓸 때 화면 녹화·접근성 권한 두 개가 필요하고, 민감한 앱은 Always allow에 넣지 않고 매번 승인으로 둡니다.
- Windows에서 Codex를 쓸 땐 기본 샌드박스(읽기 자유·쓰기는 워크스페이스 안·네트워크는 명시적 허용 시만)에서 시작합니다. Full Access는 예외로만 둡니다.
- 장시간 작업에는 모바일 승인 흐름으로 사람 개입 지점을 만듭니다. 5월 14일 발표의 Remote SSH GA·프로그래밍 방식 액세스 토큰이 이 구성의 근거입니다.
- 정기 반복은 Automations, 탐색·검토는 read-only 서브에이전트에 맡깁니다.
- CLI 도구를 여러 개 굴릴 때 MCP 설정 반복이 실제 병목이면 허브를 검토합니다. 이번에 확인한 선택지는 AionUi(Apache-2.0) 하나입니다.
- 요금 정보는 가격표만 믿지 않고 도움말 문서와 실제 계정 동작을 함께 확인합니다. 4월 혼선이 그 필요성을 보여준 사례입니다.

## 자주 묻는 질문

### Codex Computer Use는 Windows에서도 되나요?

네. 2026-09-27 공식 문서 기준 macOS와 Windows를 지원합니다. Windows에서는 작업 내내 대상 앱을 활성 데스크톱에 띄워둬야 하고, 포인터와 입력을 가져가는 포그라운드 방식으로 동작합니다.

### Claude Code는 Pro 플랜에서 쓸 수 있나요?

네. 2026-09-27 가격 페이지에 Pro 항목으로 "Claude Code included"가 명시돼 있습니다. 2026-04-22에 있던 가격표 충돌은 해소됐습니다.

### AionUi는 무료인가요?

오픈소스(Apache-2.0)라서 앱 자체는 무료입니다. 연결하는 모델 API 키 비용은 별도입니다.

### Codex 모바일은 유료 플랜만 되나요?

아니요. 2026-05-14 발표 기준 iOS·Android에서 모든 플랜(Free 포함) 대상 프리뷰로 제공됩니다.

## 참고 자료

- [Computer Use — Codex 공식 문서](https://developers.openai.com/codex/app/computer-use)
- [Building a safe, effective sandbox to enable Codex on Windows](https://openai.com/index/building-codex-windows-sandbox/) (2026-05-13)
- [Work with Codex from anywhere](https://openai.com/index/work-with-codex-from-anywhere/) (2026-05-14)
- [Helping ChatGPT better recognize context in sensitive conversations](https://openai.com/index/chatgpt-recognize-context-in-sensitive-conversations/) (2026-05-14)
- [OpenAI Codex Masterclass — Vaibhav Srivastav & Katia Gil Guzman](https://youtu.be/MhHEGMFCEB0)
- [iOfficeAI/AionUi 저장소](https://github.com/iOfficeAI/AionUi)
- [Claude Plans & Pricing](https://claude.com/pricing)
- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
