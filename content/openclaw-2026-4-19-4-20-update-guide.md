---
title: "OpenClaw 2026.4.19, 2026.4.20 업데이트 총정리: 핵심 변화와 바로 쓰는 법"
date: 2026-04-22
tags:
  - openclaw
  - 오픈클로
  - openclaw-update
  - release-notes
  - ai-agent
  - cron
  - telegram
  - codex
  - 업무자동화
  - ai-비서
description: "OpenClaw 2026.4.19-beta.2와 2026.4.20 업데이트 핵심 정리. 텔레그램, 크론, 상태 표시, Codex, 보안 강화까지 실제 체감 변화와 바로 써보는 사용법을 한 번에 정리했습니다."
---

- **GitHub Releases**: [v2026.4.19-beta.2](https://github.com/openclaw/openclaw/releases/tag/v2026.4.19-beta.2), [v2026.4.20](https://github.com/openclaw/openclaw/releases/tag/v2026.4.20)
- **GitHub 저장소**: [openclaw/openclaw](https://github.com/openclaw/openclaw)
- **공식 문서**: [docs.openclaw.ai](https://docs.openclaw.ai)
- **공식 웹사이트**: [openclaw.ai](https://openclaw.ai)

OpenClaw 2026.4.19와 2026.4.20 업데이트는 결이 다릅니다. **2026.4.19-beta.2는 핫픽스**였고, **2026.4.20은 대형 안정화 릴리즈**였습니다. 새 기능 몇 개가 붙었다기보다, 오래 돌릴수록 거슬리던 부분을 한꺼번에 정리한 버전에 가깝습니다.

특히 이번 두 버전은 이런 사람에게 체감이 큽니다.

- Telegram으로 OpenClaw를 오래 붙여 쓰는 사람
- cron으로 리마인더나 반복 작업을 돌리는 사람
- `/status` 숫자와 비용 표시를 자주 보는 사람
- Codex/OpenAI-compatible 백엔드를 섞어 쓰는 사람
- 보안 경계를 민감하게 보는 운영자

## 1. 한눈에 보면, 4.19는 핫픽스였고 4.20은 안정화 릴리즈였음

2026.4.19-beta.2는 PR 3개짜리 작은 릴리즈였습니다. 근데 체감은 작지 않았습니다. 이유는 단순합니다. **보이는 숫자와 실제 상태가 안 맞던 문제**를 바로 건드렸기 때문입니다.

핵심은 세 가지였습니다.

- OpenAI 호환 백엔드에서 usage가 비어 있을 때 `/status`가 흔들리던 문제 완화
- nested agent lane이 다른 세션까지 막아버리던 병목 해소
- streaming 시 usage 정보가 빠져 context usage가 0%처럼 보이던 문제 수정

반면 2026.4.20은 범위가 훨씬 넓습니다. **세션, 비용 집계, cron, Telegram, pairing, plugin runtime, Codex transport, 보안 경계**를 폭넓게 손봤습니다.

그러니까 이렇게 이해하면 됩니다.

- **4.19**: 숫자와 상태를 믿을 수 있게 만든 버전
- **4.20**: 장기 운용에서 덜 삐걱거리게 만든 버전

## 2. OpenClaw 2026.4.19-beta.2, 가장 중요한 건 상태 숫자를 믿을 수 있게 된 점임

이 버전에서 제일 중요한 변화는 **usage 표시 신뢰성**입니다.

OpenClaw는 모델 사용량, 비용, 토큰, 추론 상태를 자주 보여줍니다. 강의할 때도 중요하고, 실제 운영할 때도 중요합니다. 근데 provider가 usage를 일부 생략하거나, OpenAI-compatible proxy가 usage를 다 안 보내면 `/status` 숫자가 흔들리기 쉬웠습니다.

이번 핫픽스에서 들어간 변화가 이겁니다.

| 변화 | 체감 포인트 |
|------|-------------|
| streaming 시 `include_usage` 강제 전송 | OpenAI 호환 백엔드에서 context usage가 0처럼 보이던 문제 완화 |
| provider usage 누락 시 session totalTokens 보존 | `/status`, `openclaw sessions` 숫자가 덜 흔들림 |
| nested lane을 target session 기준으로 분리 | 한 작업이 다른 세션까지 막는 현상 감소 |

이건 겉으론 사소해 보여도 실제로 큽니다. 예를 들어 강의 중에 `/status`를 띄웠는데 숫자가 0이거나 unknown으로 흔들리면, 사용자 입장에서는 "지금 제대로 돌고 있는 건가"부터 헷갈립니다. 이번 버전은 그 불신을 줄였습니다.

## 3. OpenClaw 2026.4.20, 진짜 핵심은 운영 신뢰성 정리였음

2026.4.20은 PR이 94개 붙은 큰 릴리즈였습니다. 다 읽을 필요는 없습니다. 사용자는 네 덩어리만 보면 됩니다.

### 3-1. 대화와 세션이 더 덜 꼬이게 됨

이 릴리즈에서는 **세션 유지, 비용 집계, compaction, failover, Codex transport**가 함께 정리됐습니다.

대표적인 것만 뽑으면 이렇습니다.

- `/new`, `/reset` 때 자동 소스 모델/인증 override를 정리해서 이전 상태가 덜 끌려감 (#69419)
- auto-failover override를 턴마다 초기화해서 primary 모델 재시도가 다시 정상화됨 (#69365)
- estimated cost를 누적이 아니라 스냅샷 방식으로 잡아 비용 과대계산 문제를 수정함 (#69403)
- cost usage cache에 상한과 FIFO eviction을 둬서 메모리 사용을 제어함 (#68842)
- compaction 시작/완료 알림이 들어가서 긴 세션에서 무슨 일이 일어나는지 더 잘 보임 (#67830)
- 세션 저장소를 prune on load 하도록 바꿔 gateway OOM 위험을 줄임 (#69404)

한 줄로 말하면, **오래 대화하거나 여러 세션을 굴릴 때 덜 무너짐**입니다.

### 3-2. Telegram과 cron이 훨씬 현실적으로 안정화됨

Telegram과 cron은 실제 사용자 체감이 가장 큰 부분입니다. OpenClaw를 메신저 기반 비서로 쓰는 사람은 여기서 효과를 바로 느낍니다.

Telegram 쪽은 이런 개선이 들어갔습니다.

- polling stall 기준을 90초에서 300초로 늘려서 장시간 동작 시 멈춤 오탐을 줄임 (#57737)
- `getUpdates` 쪽 timeout 처리 보강 (#50368)
- status reaction 정리, ack 제거 정책 개선 (#68067)
- setup에서 `allowFrom`은 숫자 ID만 받도록 정리 (#69191)

특히 마지막 건 중요합니다. 예전처럼 `@username`만 믿고 Telegram DM 권한을 잡는 흐름이 아니라, **숫자 sender ID를 기준으로 더 명확하게 관리**하는 방향으로 갔습니다.

cron 쪽은 더 크게 바뀌었습니다.

- `jobs.json`을 설정과 런타임 상태 파일로 분리 (#63105)
- recurring delivery dedupe 기준을 execution 기준으로 보정 (#69000)
- announce delivery 정책 수정 (#69587)
- `last` 타겟이 literal 값으로 잘못 남는 문제 수정 (#68829)
- delivery validation을 gateway 경계에서 더 엄격히 검사 (#69015, #69040)
- isolated message target 보존, 명시 recipient 요구 등 edge case 정리 (#69153, #69163)

이건 실무적으로 정말 큽니다. 예전에는 cron이 "가끔은 잘 되는데 가끔 이상하게 중복되거나, 엉뚱한 타겟으로 가거나, 설정은 저장됐는데 런타임에서 터지는" 류의 문제를 만들 수 있었습니다. 이번 릴리즈는 그 부분을 많이 닦았습니다.

### 3-3. Codex와 OpenAI transport가 더 덜 깨짐

OpenClaw를 Codex나 OpenAI 계열과 섞어 쓰는 사람도 이번 릴리즈를 크게 느낄 겁니다.

주요 변화는 이렇습니다.

- legacy override를 Codex transport로 정상화 (#45304, #42194)
- Codex base URL을 `/backend-api/codex/`로 정리 (#69336)
- app-server에서 projector 예외 시 session lane release 처리 (#69072)
- approvals 기본값을 on-request로 정리 (#68721)
- reasoning/thinking 관련 400 오류 계열 수정 (#61982)
- vision turn에서 image tool loop 회피 (#65061)

쉽게 말하면, **예전엔 되던 설정이 어느 날 갑자기 400이나 HTML 응답으로 꼬이는 문제**가 줄어듭니다. Codex를 실전 워크플로우에 넣는 사람에게는 꽤 중요한 안정화입니다.

### 3-4. 보안 경계가 여러 층에서 더 단단해짐

이번 버전은 기능보다 보안 경계가 더 인상적입니다.

대표적인 보안 강화 포인트는 이렇습니다.

- QQBot direct upload URL 경로 SSRF guard (#69595)
- workspace `.env` 기반 URL 라우팅 차단, MINIMAX_API_HOST env injection 방지 (#67300)
- MCP stdio env override 차단 (#69540)
- gateway websocket broadcast에 read scope 요구 (#69373)
- gateway config mutation guard 강화 (#69377)
- pairing action을 호출한 device 범위로 제한 (#69375)
- loopback shared-secret client를 local로 분류해 pairing 처리 명확화 (#69431)
- pairing-required 복구 상세 메시지, scope upgrade 설명 강화 (#69227, #69221, #69226, #69210)

이건 사용자 입장에선 "뭔가 더 안전해졌다" 정도로 느낄 수 있지만, 운영자 입장에선 꽤 큽니다. **환경변수 주입, paired-device 권한 혼선, broadcast scope 누수** 같은 애매한 경계를 계속 좁히고 있다는 뜻이기 때문입니다.

## 4. 그래서 누가 이 업데이트를 가장 체감하냐면 이 사람들임

| 사용자 유형 | 이번 업데이트에서 가장 체감되는 변화 |
|------|------------------------------|
| Telegram 중심 사용자 | polling stall 완화, ack/reaction 정리, allowFrom 숫자 ID 정리 |
| cron 리마인더 많이 쓰는 사용자 | delivery, dedupe, target 보존, validation 강화 |
| `/status` 자주 보는 사용자 | usage/cost 표시 일관성 개선 |
| Codex/OpenAI backend 사용자 | transport 정상화, reasoning 오류 완화 |
| 장기 세션 운영자 | compaction notice, session prune, active-memory fail-soft |
| 보안 민감 운영자 | SSRF, env injection, pairing scope, gateway guard 강화 |

결국 포인트는 이겁니다. **새 기능 자랑보다, 실제로 오래 켜두고 써도 덜 불안한 버전**이 됐다는 점입니다.

## 5. 업데이트 후 바로 써볼 사용법은 이 순서가 좋음

릴리즈 노트를 읽고 끝내면 체감이 잘 안 옵니다. 아래 순서로 직접 만져보면 이번 변경점이 왜 중요한지 빨리 보입니다.

### 5-1. 먼저 버전과 상태부터 다시 확인

터미널에서는 이걸 먼저 봅니다.

```bash
openclaw status
```

채팅 안에서는 `/status`를 바로 띄워보면 됩니다.

여기서 확인할 포인트는 세 가지입니다.

- usage 숫자가 예전보다 덜 흔들리는지
- estimated cost가 이상하게 부풀지 않는지
- 현재 세션 모델/override가 `/new`, `/reset` 뒤에 제대로 초기화되는지

### 5-2. `/think`와 reasoning 상태를 한 번 직접 써보기

2026.4.20에서는 reasoning 관련 transport와 thinking 기본값 쪽도 꽤 정리됐습니다. 그래서 `/think`를 켜고 끄는 흐름이 예전보다 덜 헷갈립니다.

추천 테스트는 간단합니다.

1. `/think`를 켠다
2. 조금 복잡한 질문을 한다
3. `/status`로 reasoning 상태와 모델 상태를 본다
4. `/new` 또는 `/reset` 뒤에 override가 남아 있는지 본다

이 흐름에서 예전보다 상태가 일관되게 보이면, 이번 릴리즈 이점을 바로 느낄 수 있습니다.

### 5-3. cron을 쓰는 사람은 기존 job부터 점검

이번 릴리즈에서 cron은 내부 구조가 꽤 바뀌었습니다. 그래서 기존에 잘 쓰던 cron도 한 번 점검하는 게 좋습니다.

특히 이 항목을 체크하면 됩니다.

- recurring job이 중복 전달되지 않는지
- `delivery.mode`, `announce`, `none` 설정이 의도대로 가는지
- 특정 채널/상대/스레드 타겟이 유지되는지
- `last` 같은 암묵적 타겟 의존이 남아 있지 않은지

cron을 메신저 알림용으로 오래 돌렸다면, 이번 업데이트는 거의 필수에 가깝습니다.

### 5-4. Telegram 설정은 숫자 ID 기준으로 다시 보는 게 안전함

이제 Telegram 쪽은 `allowFrom`에서 `@username`보다 **숫자 sender ID**를 기준으로 잡는 쪽이 더 안전합니다.

왜냐하면 username은 바뀔 수 있고, 해석 경로도 불안정할 수 있기 때문입니다. 반면 숫자 ID는 훨씬 명확합니다.

실무적으로는 이렇게 이해하면 됩니다.

- setup에서 `allowFrom`을 물으면 숫자 ID를 넣는다
- DM 운영이면 허용 발신자 목록을 숫자 ID로 유지한다
- 강의/데모 환경에서도 username 기준 설명보다 ID 기준 설명이 덜 흔들린다

### 5-5. Codex나 OpenAI-compatible backend를 쓰면 transport를 다시 확인

로컬 프록시, OpenAI-compatible API, Codex를 섞어 쓰는 사람은 이번 릴리즈 뒤에 한 번 테스트를 권합니다.

확인 포인트는 간단합니다.

- streaming usage가 제대로 보이는지
- reasoning 관련 400 오류가 줄었는지
- base URL이 예전 legacy 경로에 묶여 있지 않은지
- vision turn에서 image tool loop가 생기지 않는지

이건 "원래 되던 게 어느 날부터 깨졌다" 류의 문제를 많이 줄여줍니다.

## 6. 발표용으로는 이 PR들만 집어도 충분함

94개를 다 소개할 필요는 없습니다. 발표나 공유용이면 아래 10개 정도만 집어도 핵심이 보입니다.

| PR | 왜 중요한가 |
|----|-------------|
| #68746 | streaming usage 포함으로 상태 표시 신뢰성 개선 |
| #67785 | nested agent blocking 완화 |
| #67695 | provider usage 누락 시 totalTokens 보존 |
| #63105 | cron 상태/설정 파일 분리 |
| #69587 | cron chat delivery policy 정리 |
| #69404 | session prune로 gateway OOM 예방 |
| #69403 | 비용 과대집계 수정 |
| #69336 | Codex backend base URL 정상화 |
| #69375 | paired-device action 범위 제한 |
| #69377 | gateway config mutation guard 강화 |

## 7. 이번 버전은 화려한 기능보다 믿고 돌릴 수 있게 만든 릴리즈였음

OpenClaw 2026.4.19-beta.2와 2026.4.20을 한 줄로 묶으면 이렇습니다.

- **4.19는 숫자와 상태를 맞춘 핫픽스**였고
- **4.20은 장기 운용 신뢰성을 끌어올린 안정화 릴리즈**였습니다.

특히 Telegram, cron, `/status`, Codex, pairing, gateway 보안 같은 건 겉으론 소소해 보여도 실제 사용자는 매일 밟는 부분입니다. 이번 업데이트는 바로 그 마찰을 줄였습니다.

이전 버전에서 "가끔 상태가 이상함", "크론이 애매함", "텔레그램이 장시간 지나면 불안함", "Codex가 어느 날부터 꼬임" 같은 경험이 있었다면, 이번 버전은 그냥 릴리즈 노트용 버전이 아닙니다. **실사용자용 정리 버전**에 가깝습니다.

이미 OpenClaw를 쓰고 있다면, 이번 두 버전은 꼭 한 번 훑고 직접 만져볼 가치가 있습니다.

## 같이 보면 좋은 글

- [OpenClaw 2026.4.15 릴리스: Claude Opus 4.7 탑재, Gemini TTS, 더 가벼운 컨텍스트](./openclaw-2026-4-15-release-opus-gemini-tts)
