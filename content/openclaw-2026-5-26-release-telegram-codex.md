---
title: "OpenClaw 2026.5.26 업데이트: 텔레그램과 Codex 사용자가 먼저 볼 변화"
date: 2026-05-28
tags:
  - openclaw
  - codex
  - telegram
  - ai-agents
  - release-notes
description: "OpenClaw 2026.5.26 릴리즈를 텔레그램과 Codex 사용자 관점에서 정리합니다. 빨라진 응답, 여러 Codex 계정, Codex CLI 0.134.0, usage-limit 안내 개선을 중심으로 봅니다."
aliases:
  - openclaw-2026-5-26
  - openclaw-telegram-codex-update
draft: false
---

OpenClaw 2026.5.26은 "기능이 많이 늘었다"보다 **실사용 중 덜 답답하게 만드는 릴리즈**에 가깝습니다. 특히 텔레그램으로 OpenClaw를 쓰거나, Codex 계정을 연결해 코딩 작업을 맡기는 사용자라면 바로 체감할 지점이 있습니다.

이번 글은 [공식 GitHub 릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.5.26)를 텔레그램 + Codex 사용자 관점으로 다시 정리한 버전입니다.

## 한 줄 요약

이번 업데이트의 핵심은 네 가지입니다.

| 변화 | 사용자 체감 |
|------|-------------|
| 응답 속도 개선 | 채팅 답장이 먼저 보이고, 무거운 작업은 뒤에서 이어짐 |
| 여러 Codex 계정 지원 | 계정별 인증 프로필을 나눠 quota/usage-limit 상황에 대응 가능 |
| Codex CLI 0.134.0 반영 | OpenClaw와 Codex 런타임 경계가 더 안정적 |
| usage-limit 메시지 개선 | 막혔을 때 "왜 안 되는지"와 "무엇을 해야 하는지"가 더 분명해짐 |

## 1. 답장이 빨라졌다: 채팅 먼저, 작업은 뒤에서

가장 중요한 변화는 **사용자에게 보이는 답장 경로가 빨라졌다는 점**입니다.

이전에는 OpenClaw가 답장을 보내기 전에 플러그인, 채널, 세션, usage-cost, 경고, 예약 작업, 파일시스템 상태 등을 여러 번 확인하면서 지연이 생길 수 있었습니다. 2026.5.26에서는 이 경로가 많이 정리됐습니다.

특히 릴리즈 노트에서 강조한 포인트는 다음입니다.

- Gateway 시작과 답장 hot path에서 반복 스캔을 줄임
- 사용자에게 보이는 메시지 전송과 이후의 느린 후속 작업을 분리
- Telegram typing/progress context를 더 잘 보존
- slash command 시작 메타데이터와 모델 정보 로딩을 lazy-load
- context compaction 같은 유지보수 작업을 답장 뒤로 미룸

즉, OpenClaw가 "생각을 다 끝낸 다음에야 채팅창에 나타나는" 느낌을 줄이고, **먼저 말하고 뒤에서 정리하는 구조**에 가까워졌습니다.

텔레그램 사용자에게는 이 변화가 꽤 큽니다. 모바일 채팅에서는 1~2초 지연도 답답하게 느껴지기 때문입니다. 이번 릴리즈는 정확히 그 체감 지점을 건드립니다.

## 2. 텔레그램 경험이 더 안정적이다

텔레그램 쪽도 작은 수정이 많이 들어갔습니다. 겉으로 화려한 기능이라기보다, 실제 봇을 오래 켜둘 때 생기는 어긋남을 줄이는 쪽입니다.

이번 업데이트에서 텔레그램 관련으로 눈에 띄는 변화는 다음입니다.

- inbound text entity 보존
- 겹치는 DM reply context 처리 개선
- account topic cache sidecar 보존
- forum topic name 전파
- bot command mention 처리 개선
- native progress callback 보존
- `ENETDOWN` 같은 네트워크 장애를 일시 장애로 취급해 재시도 경로 통일

텔레그램 포럼 토픽을 쓰는 사람에게는 topic name/cache 쪽 개선이 반갑습니다. OpenClaw를 그냥 1:1 봇으로만 쓰는 경우보다, 토픽별로 작업을 나눠 쓰는 환경에서 이런 수정이 더 중요합니다.

이미 텔레그램 기반으로 OpenClaw를 쓰고 있다면, 이번 릴리즈는 새 기능보다 **덜 끊기고, 덜 엉키고, 진행 상태가 더 자연스럽게 보이는 업데이트**라고 보면 됩니다.

## 3. 여러 Codex 계정 지원: named auth profile

Codex 사용자에게 가장 실용적인 변화는 **named model login profile**입니다.

이제 Hermes, OpenCode, Codex 계정 인증을 이름 있는 프로필로 관리하고, 기존 credential도 마이그레이션할 수 있는 경로가 들어갔습니다. 쉽게 말하면 계정을 하나만 전역으로 물고 가는 방식에서 벗어나, 상황에 따라 인증 프로필을 분리할 수 있는 기반이 생긴 셈입니다.

이게 중요한 이유는 단순합니다.

- 개인 Codex 계정과 작업용 Codex 계정을 나눌 수 있음
- usage-limit가 걸렸을 때 다른 Codex 계정으로 우회하기 쉬움
- 에이전트별, 프로젝트별로 인증 구성을 분리하기 쉬움
- fallback 모델/provider 정책과 조합하기 좋아짐

OpenClaw를 "텔레그램으로 부르는 코딩 비서"처럼 쓰는 사람에게는 이 변화가 꽤 현실적입니다. Codex 작업은 길게 돌다 보면 quota나 usage-limit에 부딪힐 수 있고, 그때 매번 환경변수를 갈아끼우는 방식은 운영하기 피곤합니다.

이번 릴리즈의 auth profile 개선은 그 피로를 줄이는 방향입니다.

## 4. Codex CLI 0.134.0 업데이트 필요

이번 릴리즈에는 **bundled Codex CLI 0.134.0 업데이트**가 포함됐습니다.

Codex를 OpenClaw 안에서 안정적으로 쓰려면 OpenClaw만 올리고 끝내기보다, 로컬 Codex CLI도 버전을 확인하는 편이 좋습니다.

```bash
codex --version
```

버전이 낮다면 Codex CLI를 0.134.0 이상으로 맞추는 것을 권장합니다. 환경에 따라 설치 방식이 다를 수 있지만, npm 기반으로 관리 중이라면 업데이트 후 다시 확인하면 됩니다.

```bash
npm install -g @openai/codex@0.134.0
codex --version
```

중요한 건 "Codex가 실행되기만 하면 된다"가 아니라, **OpenClaw가 기대하는 Codex 런타임 동작과 CLI 버전이 맞아야 한다**는 점입니다. 특히 app-server resume, timeout, compaction, usage-limit recovery 쪽은 OpenClaw와 Codex 사이의 경계가 중요합니다.

## 5. usage-limit 에러 메시지가 좋아졌다

Codex를 쓰다 보면 가장 짜증나는 순간이 usage-limit입니다. 예전에는 막혔다는 사실은 알겠는데, 다음 행동이 명확하지 않은 경우가 있었습니다.

이번 릴리즈에서는 Codex subscription usage-limit 에러가 더 친절해졌습니다. 특히 reset time을 알 수 없는 경우에도 OpenClaw가 그 사실을 분명히 말하고, 가능한 선택지를 안내하도록 개선됐습니다.

사용자 입장에서는 다음처럼 이해하면 됩니다.

- reset 시간이 있으면 기다릴 수 있음
- reset 시간을 알 수 없으면 OpenClaw가 추측하지 않음
- 다른 Codex 계정을 쓰거나
- 다른 configured model/provider로 전환하거나
- Codex 사용 가능 상태가 될 때까지 기다리는 선택지를 안내함

이건 작은 UX 개선처럼 보이지만, 실제 운영에서는 중요합니다. 에이전트가 실패했을 때 가장 나쁜 건 "실패 원인을 숨기는 것"입니다. 이번 변화는 실패를 더 잘 설명하는 쪽으로 갑니다.

## 6. Transcript가 중심 기능으로 올라왔다

이번 릴리즈의 또 다른 큰 축은 transcript입니다.

OpenClaw는 이제 CLI, WebChat, media, hook, Codex mirror, source-provider chunk, meeting summary 등 여러 경로에서 transcript-backed 흐름을 더 일관되게 사용합니다.

이 변화는 텔레그램/Codex 사용자에게도 의미가 있습니다.

- 이전 대화와 작업 맥락을 더 안정적으로 이어감
- Codex mirror 기록이 더 일관되게 남음
- replay나 follow-up 상황에서 유실이 줄어듦
- meeting summary나 media provenance 같은 기능과 같은 기반을 공유함

에이전트는 결국 "기억과 로그" 위에서 움직입니다. transcript 경로가 안정화된다는 건, 나중에 왜 그렇게 답했는지 추적하거나, 이어서 작업할 때 덜 흔들린다는 뜻입니다.

## 7. 관찰성과 디버깅도 강화됐다

Control UI에는 sanitized live tool activity를 보여주는 Activity tab이 추가됐고, Gateway secret 준비 과정, tool/model stream progress, OpenTelemetry LLM span, fast-mode status 같은 관찰성 요소도 보강됐습니다.

일반 사용자에게는 조금 멀게 느껴질 수 있지만, OpenClaw를 직접 운영하는 사람에게는 중요합니다. 에이전트가 느릴 때, 안 보낼 때, 모델이 막혔을 때, 어디서 걸렸는지 볼 수 있는 표면이 늘어났기 때문입니다.

특히 Codex 작업은 시간이 길고 중간에 tool call이 많습니다. Activity tab과 progress 표시가 좋아지면 "멈춘 건지, 아직 하는 중인지"를 구분하기 쉬워집니다.

## 8. 보안과 콘텐츠 경계도 강화됐다

이번 릴리즈에는 성능 개선만 있는 게 아닙니다. 보안과 prompt boundary도 꽤 많이 다듬어졌습니다.

대표적으로는 다음 변화가 있습니다.

- Browser snapshot URL을 SSRF 정책으로 검증
- system-event 텍스트가 nested prompt marker를 흉내 내지 못하도록 sanitize
- fetched file text를 external content로 감싸기
- ClickClack sender allowlist를 agent dispatch 전에 적용
- stale device token 거부
- tool-call 형태의 직렬화 텍스트가 사용자 답장에 새지 않도록 scrub
- `memory_store`에 prompt-like text가 직접 들어오는 경우 차단

OpenClaw처럼 여러 채널, 브라우저, 파일, 에이전트 런타임을 연결하는 도구는 경계가 중요합니다. 이번 업데이트는 "더 많은 일을 한다"와 동시에 "어디까지가 외부 입력인지 더 분명히 표시한다"는 방향입니다.

## 업데이트 전 체크리스트

OpenClaw를 이미 쓰고 있다면 업데이트 후 아래를 확인하는 걸 권장합니다.

```bash
openclaw --version
codex --version
```

그리고 Codex를 자주 쓴다면 다음도 확인하세요.

- Codex CLI가 0.134.0 이상인지
- Codex auth profile이 원하는 계정으로 잡혀 있는지
- usage-limit가 났을 때 fallback 모델/provider가 있는지
- 텔레그램 봇이 topic/reply/progress를 정상적으로 유지하는지
- Gateway status에서 fast-mode, systemd, plugin scan 관련 경고가 없는지

OpenClaw를 처음 설치하거나 Windows 환경에서 구성한다면, 이전에 정리한 [OpenClaw Windows 네이티브 설치 가이드](./openclaw-windows-native-no-wsl.md)도 같이 참고할 만합니다.

## 결론

OpenClaw 2026.5.26은 대형 신기능 하나로 설명되는 릴리즈가 아닙니다. 대신 실제 사용자 입장에서 매일 부딪히는 부분을 많이 줄였습니다.

텔레그램 사용자는 답장 속도와 reply/progress 안정성을 체감할 가능성이 큽니다. Codex 사용자는 여러 계정, CLI 0.134.0, timeout/recovery, usage-limit 메시지 개선이 중요합니다. 운영자는 transcript, Activity tab, telemetry, 보안 경계 강화가 반갑습니다.

정리하면 이번 릴리즈는 **OpenClaw를 더 오래 켜두고, 더 많은 채널에서, 더 예측 가능하게 쓰기 위한 안정화 업데이트**입니다.

---

**출처**: [openclaw/openclaw v2026.5.26 release notes](https://github.com/openclaw/openclaw/releases/tag/v2026.5.26)
