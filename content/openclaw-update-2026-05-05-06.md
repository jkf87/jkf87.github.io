---
title: "OpenClaw 2026.5.4~5.6 업데이트: 구글 미트 음성 브릿지부터 Doctor 긴급 수정까지"
slug: "openclaw-update-2026-05-05-06"
date: 2026-05-07
tags: ["OpenClaw", "업데이트", "구글미트", "AI에이전트", "음성브릿지", "디스코드", "Codex"]
description: "OpenClaw 5월 5-6일 업데이트 요약. 구글 미트 음성 브릿지, 50개 넘는 버그 수정, Codex OAuth 긴급 복구까지."
---

5월 5일, 6일 이틀 연속으로 OpenClaw가 업데이트되었습니다. 하이라이트 하나에 수정 50개 넘게 쏟아진 뒤, 이틀째 긴급 패치까지 이어진 이번 릴리즈를 정리해봅니다.

## 구글 미트에서 AI와 대화한다 — 2026.5.4

가장 눈에 띄는 변화는 **Google Meet/Twilio 다이얼인**입니다.

구글 미트 회의실에 OpenClaw 음성 에이전트가 참가할 수 있습니다. 참가자가 말하면 Gemini가 실시간으로 음성을 인식하고, 에이전트가 응답을 음성으로 되돌려줍니다. backpressure-aware buffering으로 네트워크가 불안정해도 끊김을 최소화하고, barge-in으로 말 중간에 끼어드는 것도 가능합니다.

실시간 회의에서 AI 에이전트가 발표자 질문에 답하거나, 회의 내용을 요약해 참가자에게 전달하는 시나리오가 바로 가능해졌습니다.

이 외에도 5.4에는 몇 가지 실용적인 개선이 들어갔습니다.

- **Windows 루프백 수정**: 기본 리스너가 `127.0.0.1`로 바인딩되어 `::1` 듀얼스택 충돌이 해결됐습니다. Windows 사용자에게는 골치거리 하나가 사라진 셈입니다.
- **플러그인 마이그레이션 힌트**: 아직 설치하지 않은 공식 플러그인에 대해 catalog 기반 설치 힌트가 표시됩니다. 뭘 깔아야 할지 헤맬 필요가 줄었습니다.
- **Slack 스트리밍**: Block Kit 기반 rich progress drafts가 지원됩니다. 진행 상황이 슬랙에서 보기 좋게 표시됩니다.
- **Discord**: npm으로 배포된 채널 플러그인의 SecretRef를 external-contract 로더로 해결합니다.
- **성능**: model catalog/manifest 리더가 workspace-scoped plugin metadata snapshot을 재사용해 cold scan이 줄었습니다.

## 50개 넘는 수정이 한꺼번에 — 2026.5.5

5.5는 분량부터가 다릅니다. **버그 수정만 50개 이상** 들어갔고, 거의 모든 영역에 손이 갔습니다.

### 채널·메시징 안정성

Feishu 토픽의 스레드 ID 하이드레이션이 수정됐고, LINE의 dmPolicy 검증이 추가됐습니다. Telegram과 Codex에서 진행 드래프트가 중복 표시되던 문제가 해결됐고, Discord는 heartbeat ACK 타이밍과 guild 명령어 라우팅이 수정됐습니다. Matrix는 승인 요청이 실패 시 최대 3회 재시도하며, Slack은 에러 발생 시 컨텍스트가 보존됩니다.

채널 플랫폼 전반에서 메시지 유실·중복·라우팅 오류가 광범위하게 잡혔습니다. 여러 채널을 동시에 쓰는 환경일수록 체감이 큰 업데이트입니다.

### 프로바이더

xAI Grok 4.3에서 reasoning effort 파라미터 처리 오류가 수정됐고, Fireworks의 Kimi K2.5/K2.6에서는 thinking 파라미터가 비활성화되어 불필요한 에러가 사라졌습니다.

### iOS 페어링

LAN과 `.local` 주소로 게이트웨이에 연결할 때 `ws://` 연결이 허용됩니다. Tailscale은 기존처럼 `wss://`를 유지합니다. 같은 네트워크에서 아이폰으로 연결할 때 더 매끄럽게 페어링됩니다.

### TUI/CLI

heartbeat 세션이 복원을 차단하는 문제가 수정됐고, 세션 피커에 바운드가 걸려 몇 주 된 트랜스크립트가 의도치 않게 로드되는 일이 막아졌습니다. `openclaw status`에 에이전트 runtime 정보가 표시되고, 오래된 artifact도 자동 정리됩니다.

### Control UI

채팅 히스토리를 리로드할 때 assistant의 진행 텍스트가 사라지던 버그가 수정됐습니다. 세션 checkpoint 카드가 추가됐고, 채널 탭 응답성도 개선됐습니다.

### Doctor와 Codex

5.4까지 `openai-codex/*` 경로로 설정된 모델이 legacy로 인식되는 문제가 있었습니다. 5.5에서는 Codex 플러그인이 설치된 경우에만 codex harness를 선택하고, 그 외에는 `openai/*` 라우트로 복구합니다.

### 보안: Docker

Docker 컨테이너에서 `NET_RAW`, `NET_ADMIN` capability가 drop되고 `no-new-privileges`가 적용됩니다. 컨테이너 권한이 최소화됩니다.

### 그 외

- 공식 npm/ClawHub 플러그인 업데이트 동기화와 peer link 재설정이 개선됐습니다.
- 중복 미디어 포스트가 방지되고, 비디오 생성에 aspect-ratio/resolution 힌트가 추가됐습니다. MiniMax는 720P가 768P로 정규화됩니다.
- 게이트웨이에서 OpenAI 호환 스트리밍의 첫 chunk 지연이 해결됐고, shutdown 시 orphaned timer가 방지됩니다.
- Windows Exec에서 rename-overwrite가 실패하면 guarded copy로 폴백합니다.

## Doctor가 손본 걸 다시 되돌리다 — 2026.5.6

5.5의 Doctor `--fix`가 유효한 `openai-codex/*` OAuth 라우트까지 `openai/*`로 덮어쓰는 부작용이 있었습니다. Codex를 사용 중이던 사용자에게는 모델 라우팅이 깨지는 심각한 문제였습니다.

5.6에서는 이 변경이 되돌려졌습니다. 복구하려면 다음 명령을 실행합니다:

```bash
openclaw models set openai-codex/gpt-5.5
openclaw config validate
```

이 외에도 서드파티 심볼 메타데이터 때문에 플러그인 요청이 reject되던 문제, debug proxy의 헤더 정규화, web fetch 타임아웃 후 tool lane이 비활성화로 잔류하던 문제도 함께 수정됐습니다.

## 가져갈 것

1. **구글 미트 음성 브릿지**를 쓸 일이 있다면 바로 5.4 이상으로 업데이트하세요. 실시간 음성 대화가 가능해졌습니다.
2. **5.5의 수정 규모가 큽니다.** 채널 안정성, CLI, Docker 보안까지 넓게 건드렸으니 여러 환경을 쓰는 분일수록 업데이트 이득이 큽니다.
3. **Codex 사용자는 5.6이 필수입니다.** 5.5의 Doctor가 라우트를 덮어쓴 문제가 복구됩니다. `openclaw models set openai-codex/gpt-5.5 && openclaw config validate`로 확인까지 마치는 게 좋습니다.

---

OpenClaw 활용법이 궁금하다면 《[이게 되네? 오픈클로 미친 활용법 50제](https://www.yes24.com/product/goods/185166276)》도 한 번 살펴보세요.
