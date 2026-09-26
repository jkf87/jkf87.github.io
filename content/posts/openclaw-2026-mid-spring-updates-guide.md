---
title: "오픈클로 음성·Steer 어떻게 바뀌었나: 2026.4.15~5.28 업데이트 9편 통합 정리"
date: 2026-09-25
author: 한준구(코난쌤)
description: "오픈클로 2026.4.15~5.28 중간 업데이트를 음성·Steer·플러그인·Doctor 네 축으로 묶고, 2026.4.29 직접 설치, npm 11버전 크기 실측, macOS 로컬 TTS 실행까지 확인한 통합 가이드입니다."
tags: [openclaw, agent, release-notes, tts]
refactor_hub_id: openclaw-updates-02
aliases:
  - openclaw-2026-4-15-release-opus-gemini-tts
  - openclaw-2026-4-25-update
  - openclaw-4-26-update-local-tts-2026-04-28
  - openclaw-2026-4-29-release-steer-nvidia-memory
  - openclaw-2026-5-2-update
  - openclaw-2026-5-4-update
  - openclaw-update-2026-05-05-06
  - posts/2026-06-01-openclaw-528-update
draft: false
---
## 한눈에 보는 결론

4월 중순부터 5월 말까지 오픈클로(OpenClaw)가 두 달 동안 어떻게 바뀌었는지, 기존 글 9편을 하나로 합쳤습니다.

"AI한테 말 걸기 방식이 바뀌었다"가 4.29의 제목이었는데, 실제로 그렇습니다. <span style="background-color: #fff59d"><strong>4.29부터 작업 중에 보낸 메시지가 Steer로 처리</strong></span>됩니다. 에이전트가 현재 작업을 끝내는 순간 쌓인 메시지를 한 번에 반영합니다. 줄 세우던 Queue는 레거시가 됐습니다.

음성도 이 두 달에 자리를 잡았습니다. 4.15에 Gemini TTS가 번들로 들어오고, <span style="background-color: #fff59d"><strong>4.25에 TTS가 전면 개편</strong></span>되면서 채팅·에이전트·계정 단위로 다른 목소리를 쓸 수 있게 됐습니다. <span style="background-color: #fff59d"><strong>API 키 없이 쓰는 로컬 CLI 프로바이더</strong></span>도 이때 생겼습니다. 5.4는 구글 미트 실시간 음성 브릿지입니다.

구조적으로는 5.2~5.3의 플러그인 npm 외부화가 가장 큽니다. npm 메타데이터를 직접 조회하니 <span style="background-color: #fff59d"><strong>코어 크기가 88.6MB에서 53.5MB로 줄었습니다</strong></span>(-40%).

신뢰성 축도 있습니다. 5.5의 Doctor --fix가 <span style="background-color: #fff59d"><strong>유효한 Codex OAuth 라우트를 openai/*로 덮어쓴 문제</strong></span>를 5.6이 되돌렸습니다. Codex를 쓴다면 5.6 이상이 필수입니다.

한 건 정정했습니다. 5.3의 'file-transfer 플러그인'은 <span style="background-color: #fff59d"><strong>릴리즈 노트와 npm 어디에서도 확인되지 않아서 이 글에서 뺐습니다</strong></span>. 예전 URL은 전부 이 글로 redirect 됩니다.

## 무엇을 비교했나

1. GitHub 릴리즈 노트 10건(4.15, 4.25, 4.26, 4.29, 5.2, 5.3, 5.4, 5.5, 5.6, 5.28) — 전부 2026-09-25에 다시 열어 대조
2. Windows 공식 install.ps1 원문
3. npm 레지스트리 메타데이터 11버전(npm view 직접 조회)
4. 기존 글 9편(각각 릴리즈 노트 1건 요약 형태)
5. 이 맥북에서 직접 실행한 2026.4.29와 설치되어 있는 2026.9.6

기존 글 9편은 소스 하나를 요약한 형태라 검색 중복 항목이 됐습니다. 이 허브로 합치면서 원문 대조와 직접 실행 검증을 한 번 더 얹었습니다.

## 방법 비교

기간별 핵심 변화와 제 검증 결과입니다.

| 버전 | 날짜 | 핵심 변화 | 블로그봇 확인 |
|------|------|-----------|--------------|
| 4.15 | 04-15 | Claude Opus 4.7 기본 모델화, Gemini TTS 번들 | 노트 대조 일치 |
| 4.25 | 04-25 | TTS 전면 개편: /tts latest, 계층별 오버라이드, 프로바이더 대거 추가 | 노트 대조 일치 |
| 4.26 | 04-26 | 패치: 채널·게이트웨이 안정화 | 로컬 TTS 실행으로 실사용 확인 |
| 4.29 | 04-29 | Steer 기본화, NVIDIA 제공자, 사람 인식 메모리 | 노트 대조 + 직접 설치 실행 |
| 5.2~5.3 | 05-02/03 | 플러그인 npm 외부화, 게이트웨이 핫패스 정리 | 노트 대조 + 크기 실측(-35.1MB) |
| 5.4~5.6 | 05-05/06 | 구글 미트 실시간 음성 브릿지, Doctor 수정→되돌리기 | 노트 대조(복구 명령어 원문 일치) |
| 5.28 | 05-28 | 런타임 회복력, 채널 안정화, iOS Pro UI | 노트 대조 일치 |
| Windows | — | WSL 없이 install.ps1 한 줄 설치 | 스크립트 원문 확인 |

축으로 자르면 이렇습니다.

| 축 | 이전 | 이후 | 바뀐 시점 |
|----|------|------|----------|
| 음성 답장 | 전역 설정 1개 | 채팅/에이전트/계정 3층 오버라이드 + 로컬 CLI | 4.25 |
| 작업 중 메시지 | Queue(하나씩 순차) | Steer(끝나면 한 번에 반영) | 4.29 |
| 플러그인 | 코어 번들 | @openclaw/* 개별 패키지 | 5.2~5.3 |
| Codex 라우트 | — | Doctor가 openai-codex/*를 잘못 덮어씀 → 5.6 되돌림 | 5.5→5.6 |

TTS 프로바이더는 4.25 기준 <span style="background-color: #fff59d"><strong>Azure Speech, Xiaomi, Local CLI, Inworld, Volcengine, ElevenLabs v3 추가</strong></span>입니다. 이 중 API 키가 필요 없는 건 Local CLI와 Microsoft뿐입니다. macOS라면 기본 내장 say 명령으로 바로 쓸 수 있습니다.

Steer에는 <span style="background-color: #fff59d"><strong>500ms 디바운스</strong></span>가 붙어 있습니다. 빠르게 연달아 보낸 메시지가 두 번 처리되지 않게 묶어 주는 장치입니다. 이전 Queue로 되돌리려면 채팅에서 /queue queue 한 줄이면 됩니다.

## 언제 무엇을 쓰나

- 음성 답장을 쓰고 싶다 → 4.25 이상. <span style="background-color: #fff59d"><strong>로컬 TTS부터 키 없이 시도</strong></span>하면 됩니다. macOS는 say, 다른 OS는 piper 같은 로컬 엔진을 tts-local-cli로 연결합니다.
- 긴 과제 중간에 방향을 바꾸고 싶다 → 4.29 이상. Steer가 기본이라 그냥 메시지를 보내면 됩니다.
- Discord·Telegram 등 채널을 여러 개 붙여 쓴다 → 5.2~5.4. 이 구간에 채널별 수정이 몰려 있습니다.
- Codex OAuth로 GPT-5.5를 쓴다 → <span style="background-color: #fff59d"><strong>5.6 미만은 위험</strong></span>합니다. 복구는 openclaw models set openai-codex/gpt-5.5 && openclaw config validate.
- 윈도우에서 처음 설치한다 → WSL 없이 powershell -c "irm https://openclaw.ai/install.ps1 | iex" 한 줄이면 됩니다.

버전을 올리기 전에 크기부터 확인하고 싶다면 이 명령으로 됩니다.

```bash
npm view openclaw@2026.5.28 dist.unpackedSize dist.fileCount
```

## 블로그봇이 직접 확인한 것

2026-09-25 밤, 맥북 프로 M2 Max 32GB(macOS 26.5.1)에서 실행했습니다. 같은 회선에서 20GB MLX 모델을 받고 있어서 느린 조건이었습니다.

### 1) 릴리즈 노트 원문 대조

- 4.15: Opus 4.7 기본화(opus 별칭, CLI 기본값, 이미지 이해까지), Gemini TTS(WAV·PCM 전화 출력) 일치.
- 4.25: /tts latest, /tts chat on|off|default, 콜드 퍼시스티드 레지스트리, OTEL 확장, PWA/Web Push 전부 일치.
- 4.29: "active-run steering by default" 문구로 Steer 기본화 확인. 사람 인식 위키, NVIDIA 온보딩도 일치.
- 5.4: 구글 미트 브릿지(paced audio streaming, backpressure buffering, barge-in, TwiML 폴백 제거) 일치.
- 5.6: <span style="background-color: #fff59d"><strong>5.5 Doctor 버그 설명과 복구 명령어가 기존 글과 한 단어까지 일치</strong></span>합니다.
- 정정: @openclaw/file-transfer 패키지는 npm에 없고(E404), 5.3 노트 본문에도 관련 문구가 없습니다. 관련 주장은 뺐습니다.

### 2) 2026.4.29 직접 설치·실행

sandbox에 새로 설치했습니다. 첫 시도는 회선 공유 탓에 580초 제한에 걸려 중단됐고, 재실행하니 캐시에서 이어서 완료됐습니다.

```bash
$ npm install --no-audit --no-fund --ignore-scripts openclaw@2026.4.29
up to date in 397ms
$ ./node_modules/.bin/openclaw --version
OpenClaw 2026.4.29 (a448042)
```

4.29에 plugins registry, browser start --headless, doctor가 이미 있고, 2026.9.6에서도 같은 명령들이 살아 있습니다. <span style="background-color: #fff59d"><strong>4.25에 들어온 플러그인 레지스트리와 브라우저 명령이 4개월 넘게 유지</strong></span>되고 있는 셈입니다.

### 3) npm 레지스트리 11버전 조회

| 버전 | 크기(MB) | 파일 수 |
|------|---------|--------|
| 4.15 | 55.4 | 7,379 |
| 4.25 | 70.5 | 8,844 |
| 4.26 | 71.8 | 9,084 |
| 4.29 | 74.6 | 9,309 |
| 5.2 | 88.6 | 9,882 |
| 5.3 | 53.5 | 9,185 |
| 5.4 | 74.5 | 9,692 |
| 5.5 | 74.6 | 9,705 |
| 5.6 | 74.6 | 9,706 |
| 5.28 | 81.0 | 9,082 |
| 9.6 | 311.4 | 12,583 |

<span style="background-color: #fff59d"><strong>5.3에서 코어가 35.1MB(40%) 줄었습니다</strong></span>. 외부화 효과가 숫자로 보입니다. 근데 9.6은 311.4MB까지 다시 커졌습니다. <span style="background-color: #fff59d"><strong>플러그인 생태계가 코어를 다시 키우는 추세</strong></span>라서 디스크 여유는 버전 올리기 전에 확인해야 합니다.

![OpenClaw 버전별 npm 패키지 크기: 5.3 외부화 딥과 9.6 재성장](../media/openclaw-2026-mid-spring-updates-guide/chart-01-npm-size-415-596.png)

### 4) macOS 로컬 TTS 실행

4.26 글의 tts-local-cli 설정에서 쓰는 say 명령을 그대로 실행해 봤습니다.

```bash
$ say -o tts-say-test.wav --data-format=LEF32@22050 '두 번째 로컬 TTS 캡처입니다'
$ afinfo tts-say-test.wav
Data format: 1 ch, 22050 Hz, Float32
estimated duration: 2.213605 sec
```

<span style="background-color: #fff59d"><strong>설정 파일에 적은 명령 그대로 WAV가 만들어집니다</strong></span>. API 키도 외부 서비스도 필요 없었습니다.

### 5) Windows 설치 스크립트 확인

install.ps1을 직접 내려받아 확인했습니다. <span style="background-color: #fff59d"><strong>공식 안내 문구는 irm ... | iex 한 줄</strong></span>이고, 설치 방식은 npm 기본, 태그 지정, Node 별도 설치 옵션이 있습니다. 맥 환경이라 실행까지는 못 했습니다.

![2026.4.29 설치·버전 확인 캡처](../media/openclaw-2026-mid-spring-updates-guide/verify-01-429-install.png)

![npm 레지스트리 조회·file-transfer 404 캡처](../media/openclaw-2026-mid-spring-updates-guide/verify-02-registry-filetransfer.png)

![로컬 TTS say 실행 캡처](../media/openclaw-2026-mid-spring-updates-guide/verify-03-say-tts.png)

## 한계와 반론

- 구글 미트 음성 브릿지의 실제 음질, OTEL 지표, PWA 푸시는 이번에 실행하지 못했습니다. 회선을 20GB 모델 다운로드와 공유 중이라 무거운 실측을 줄였습니다.
- 4.26의 세부 변경(채널 add 비대화형 플래그 등)은 노트 발췌에서 직접 확인하지 못했습니다. 현재 버전 도움말에 해당 플래그가 있는 것까지만 확인했습니다.
- 5.5의 "수정 50개 이상"은 기존 글 주장이고, 제가 확인한 분량은 그보다 적습니다. 정확한 개수는 노트 전문에서 세야 합니다.
- 5.28 신규 모델 목록(Opus 4.8 등)은 노트 앞부분 확인 분량에 없어서 링크로 대체했습니다.
- Windows 설치는 맥에서 실행하지 못했습니다. 스크립트 원문 확인으로 대체했습니다.

## 교실·업무에 적용한다면

- 듣기 자료는 로컬 TTS로 만들면 됩니다. say 한 줄로 음원이 나오니 인터넷 없는 교실 환경에서도 돌아갑니다.
- 에이전트에 긴 과제를 맡길 때는 중간 지시를 참지 말고 바로 보내면 됩니다. Steer가 묶어서 반영합니다. 수업 시연에서도 이 흐름이 이해시키기 쉽습니다.
- 팀에서 버전을 통일할 때는 Codex 사용 여부부터 물어보세요. Codex 쓰는 팀은 5.6을 못 넘습니다.
- 입문자는 실전 예제 중심 교재 하나면 충분합니다. 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』가 그 출발점입니다.

## 참고 자료

- [Release 2026.4.15](https://github.com/openclaw/openclaw/releases/tag/v2026.4.15) — Opus 4.7 기본화·Gemini TTS
- [Release 2026.4.25](https://github.com/openclaw/openclaw/releases/tag/v2026.4.25) — TTS 전면 개편·콜드 레지스트리
- [Release 2026.4.26](https://github.com/openclaw/openclaw/releases/tag/v2026.4.26) — 패치
- [Release 2026.4.29](https://github.com/openclaw/openclaw/releases/tag/v2026.4.29) — Steer 기본화·NVIDIA
- [Release 2026.5.2](https://github.com/openclaw/openclaw/releases/tag/v2026.5.2) — 플러그인 npm 전환
- [Release 2026.5.3](https://github.com/openclaw/openclaw/releases/tag/v2026.5.3) — 외부화 정리
- [Release 2026.5.4](https://github.com/openclaw/openclaw/releases/tag/v2026.5.4) — 구글 미트 브릿지
- [Release 2026.5.5](https://github.com/openclaw/openclaw/releases/tag/v2026.5.5) — 대량 수정
- [Release 2026.5.6](https://github.com/openclaw/openclaw/releases/tag/v2026.5.6) — Doctor 되돌리기
- [Release 2026.5.28](https://github.com/openclaw/openclaw/releases/tag/v2026.5.28) — 런타임 회복력
- [openclaw.ai/install.ps1](https://openclaw.ai/install.ps1) — Windows 공식 설치 스크립트
- [오픈클로 2026.4.11~5.31 통합본](/posts/openclaw-2026-spring-updates-summary) — 같은 기간 대형 릴리즈 정리

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.