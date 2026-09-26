---
title: "OpenClaw Google Meet 플러그인 설치 및 활용법"
date: 2026-05-28
tags:
  - openclaw
  - google-meet
  - ai-agents
  - automation
  - setup-guide
description: "OpenClaw Google Meet 플러그인 설치, transcribe 모드, agent talk-back 모드, chrome-node 구성, 검증 명령어와 에이전트 프롬프트를 정리합니다."
author: 한준구(코난쌤)
aliases:
  - openclaw-google-meet-plugin
  - google-meet-openclaw-setup
draft: false
verified_at: 2026-09-25
---

OpenClaw에서 Google Meet을 쓰려면 `@openclaw/google-meet` 플러그인을 설치하고, 목적에 맞게 `transcribe`, `agent`, `chrome-node`, `twilio` 중 하나를 고르면 된다.

![OpenClaw Google Meet 플러그인 설정 흐름](./media/openclaw-google-meet-plugin-setup-guide-2026-05-28/setup-flow.png)

## 0. 먼저 확인

```bash
openclaw --version
node --version
openclaw plugins search google-meet
```

OpenClaw 2026.9.6 기준으로 Google Meet은 기본 번들이 아니라 ClawHub 공식 플러그인(v2026.9.5)이다.

## 1. 설치

```bash
openclaw plugins install clawhub:@openclaw/google-meet
openclaw plugins enable google-meet
openclaw gateway restart
```

확인:

```bash
openclaw plugins list | grep -E 'google-meet|Google Meet'
openclaw googlemeet setup --json
```

## 2. 최소 설정

`~/.openclaw/openclaw.json`에 플러그인 entry가 필요하다.

```json5
{
  plugins: {
    entries: {
      "google-meet": {
        enabled: true,
        config: {}
      }
    }
  }
}
```

설정 검증:

```bash
openclaw config validate
openclaw googlemeet setup
```

## 3. 가장 쉬운 모드: transcribe

회의에 들어가서 자막/상태를 확인하는 용도다. 에이전트가 말하지 않는다.

```bash
openclaw googlemeet setup --mode transcribe
openclaw googlemeet join https://meet.google.com/abc-defg-hij --mode transcribe
```

듣기 검증:

```bash
openclaw googlemeet test-listen https://meet.google.com/abc-defg-hij \
  --mode transcribe \
  --timeout-ms 30000
```

에이전트에게 시킬 때:

```text
이 Google Meet에 transcribe 모드로 들어가서 captions/transcript가 움직이는지 확인해줘.
URL: https://meet.google.com/abc-defg-hij
말하지 말고 listen 검증만 해.
```

도구 호출 형태:

```json
{
  "action": "test_listen",
  "url": "https://meet.google.com/abc-defg-hij",
  "transport": "chrome",
  "timeoutMs": 30000
}
```

## 4. 말하게 하기: agent 모드

`agent` 모드는 회의 음성을 듣고, OpenClaw agent에게 넘기고, TTS로 회의에 말한다.

macOS 로컬 Chrome 기준 준비:

```bash
brew install blackhole-2ch sox
```

BlackHole 설치 후 macOS 재부팅:

```bash
sudo reboot
```

재부팅 후 확인:

```bash
system_profiler SPAudioDataType | grep -i BlackHole
command -v sox
```

OpenAI realtime transcription을 쓸 경우:

```bash
export OPENAI_API_KEY=sk-...
```

설정 점검:

```bash
openclaw googlemeet setup --transport chrome --mode agent
```

참여:

```bash
openclaw googlemeet join https://meet.google.com/abc-defg-hij \
  --transport chrome \
  --mode agent
```

말하기 테스트:

```bash
openclaw googlemeet test-speech https://meet.google.com/abc-defg-hij \
  --transport chrome \
  --mode agent
```

에이전트에게 시킬 때:

```text
이 Google Meet에 agent 모드로 들어가줘.
URL: https://meet.google.com/abc-defg-hij
짧게 자기소개만 하고, 이후에는 질문이 있을 때만 답해.
문제가 생기면 manualActionRequired, browserUrl, browserTitle을 그대로 보고해.
```

## 5. 추천 운영 방식: chrome-node

본체 Gateway와 Chrome 실행 환경을 분리하고 싶으면 `chrome-node`를 쓴다. 예: Gateway는 메인 맥, Chrome은 Parallels macOS VM.

VM 또는 Chrome 전용 맥에서:

```bash
brew install blackhole-2ch sox
openclaw plugins enable google-meet
openclaw plugins enable browser
```

노드 실행:

```bash
openclaw node run \
  --host <gateway-host> \
  --port 18789 \
  --display-name parallels-macos
```

LAN IP로 평문 WebSocket을 쓸 때:

```bash
OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1 \
openclaw node run \
  --host <gateway-lan-ip> \
  --port 18789 \
  --display-name parallels-macos
```

Gateway host에서 승인:

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw nodes status
```

Gateway 설정:

```json5
{
  gateway: {
    nodes: {
      allowCommands: ["googlemeet.chrome", "browser.proxy"]
    }
  },
  plugins: {
    entries: {
      "google-meet": {
        enabled: true,
        config: {
          defaultTransport: "chrome-node",
          chrome: {
            guestName: "OpenClaw Agent",
            autoJoin: true,
            reuseExistingTab: true
          },
          chromeNode: {
            node: "parallels-macos"
          }
        }
      }
    }
  }
}
```

점검:

```bash
openclaw config validate
openclaw googlemeet setup --transport chrome-node --mode transcribe
openclaw googlemeet setup --transport chrome-node --mode agent
```

참여:

```bash
openclaw googlemeet join https://meet.google.com/abc-defg-hij \
  --transport chrome-node \
  --mode agent
```

## 6. 새 Meet 만들기

OAuth 없이도 브라우저 fallback으로 만들 수 있다. 단, Chrome profile이 Google에 로그인되어 있어야 한다.

```bash
openclaw googlemeet create --no-join
openclaw googlemeet create --transport chrome-node --mode agent
```

에이전트 프롬프트:

```text
새 Google Meet을 만들고, agent 모드로 직접 들어간 뒤 링크를 알려줘.
transport는 chrome-node를 사용해.
입장에 실패하면 manualActionRequired 내용을 그대로 보고해.
```

API로 방을 만들려면 Google Meet OAuth를 설정한다.

## 7. Google OAuth 설정

OAuth가 필요한 경우:

- Google Meet API로 회의 생성
- Meet space resolve
- attendance/artifacts/export
- Calendar에서 Meet 링크 찾기

Google Cloud Console에서:

1. Google Cloud project 생성 또는 선택
2. Google Meet REST API 활성화
3. OAuth consent screen 설정
4. OAuth client ID 생성
5. Redirect URI 추가

```text
http://localhost:8085/oauth2callback
```

필요 scope:

```text
https://www.googleapis.com/auth/meetings.space.created
https://www.googleapis.com/auth/meetings.space.readonly
https://www.googleapis.com/auth/meetings.space.settings
https://www.googleapis.com/auth/meetings.conference.media.readonly
```

로그인:

```bash
OPENCLAW_GOOGLE_MEET_CLIENT_ID="your-client-id" \
OPENCLAW_GOOGLE_MEET_CLIENT_SECRET="your-client-secret" \
openclaw googlemeet auth login --json
```

수동 callback이 필요할 때:

```bash
OPENCLAW_GOOGLE_MEET_CLIENT_ID="your-client-id" \
OPENCLAW_GOOGLE_MEET_CLIENT_SECRET="your-client-secret" \
openclaw googlemeet auth login --json --manual
```

출력된 `oauth` 블록을 config에 넣는다.

```json5
{
  plugins: {
    entries: {
      "google-meet": {
        enabled: true,
        config: {
          oauth: {
            clientId: "your-client-id",
            clientSecret: "your-client-secret",
            refreshToken: "refresh-token"
          }
        }
      }
    }
  }
}
```

검증:

```bash
openclaw googlemeet doctor --oauth --json
openclaw googlemeet doctor --oauth --create-space --json
openclaw googlemeet create --no-join --json
```

## 8. 회의 자료 가져오기

회의가 끝난 뒤 Google이 conference records를 만든 경우:

```bash
openclaw googlemeet latest --meeting https://meet.google.com/abc-defg-hij
openclaw googlemeet artifacts --meeting https://meet.google.com/abc-defg-hij
openclaw googlemeet attendance --meeting https://meet.google.com/abc-defg-hij
```

Markdown/CSV 저장:

```bash
openclaw googlemeet artifacts \
  --meeting https://meet.google.com/abc-defg-hij \
  --format markdown \
  --output meet-artifacts.md

openclaw googlemeet attendance \
  --meeting https://meet.google.com/abc-defg-hij \
  --format csv \
  --output attendance.csv
```

전체 export:

```bash
openclaw googlemeet export \
  --meeting https://meet.google.com/abc-defg-hij \
  --include-doc-bodies \
  --zip \
  --output meet-export
```

## 9. 문제 해결

### `No ClawHub plugins found`

검색어가 다를 수 있다.

```bash
openclaw plugins search google-meet
openclaw plugins search meet
```

### `BlackHole 2ch audio device not found`

```bash
brew install blackhole-2ch
sudo reboot
system_profiler SPAudioDataType | grep -i BlackHole
```

### Chrome이 로그인 화면에서 멈춤

Chrome profile에 Google 로그인이 필요하다. `manualActionRequired`가 나오면 새 탭을 계속 열지 말고, 보고된 `browserUrl`에서 수동 로그인 후 재시도한다.

### 회의에 들어갔지만 소리가 안 남

```bash
openclaw googlemeet status --json
openclaw googlemeet setup --transport chrome --mode agent
```

확인할 것:

- Meet microphone/speaker가 BlackHole 경로를 쓰는지
- SoX가 설치됐는지
- STT/TTS provider key가 있는지
- `mode`가 `transcribe`가 아니라 `agent`인지

## 10. 최소 성공 루트

처음에는 이것만 한다.

```bash
openclaw plugins install clawhub:@openclaw/google-meet
openclaw plugins enable google-meet
openclaw gateway restart
openclaw googlemeet setup --mode transcribe
openclaw googlemeet test-listen https://meet.google.com/abc-defg-hij --mode transcribe
```

이후 말하기가 필요할 때만 `agent` 모드와 BlackHole/SoX 구성을 붙인다.

## 한계와 막힌 부분

- Twilio 트랜스포트는 계정 인증 정보(`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`)가 있어야 동작한다. 없으면 Chrome 트랜스포트를 쓰면 된다.
- `test-listen`과 `test-speech`는 실제 Google Meet 방이 필요하다. 이 검증에서는 setup 체크까지 확인하고, 실제 회의 참여는 수행하지 않았다.
- Chrome profile에 Google 로그인이 선행되어야 한다. headless 환경에서는 `manualActionRequired`가 나올 수 있다.
- 회의 녹음·아티팩트 내보내기(`artifacts`, `export`)는 Google Meet이 conference records를 생성한 경우에만 동작한다.

---

## 검증 로그

- 검증일: 2026-09-25
- 검증 환경: macOS 26.0 (Darwin 25.5.0), Apple M4
- OpenClaw: 2026.9.6 (eb377ac)
- Google Meet 플러그인: v2026.9.5

### 플러그인 설치·설정 확인

```bash
$ openclaw plugins search google-meet
@openclaw/google-meet  v2026.9.5 — OpenClaw Google Meet participant plugin

$ openclaw plugins list | grep google-meet
Google Meet | google-meet | openclaw | enabled | 2026.9.5

$ openclaw config validate
Config valid: ~/.openclaw/openclaw.json
```

### transcribe 모드 체크

```bash
$ openclaw googlemeet setup --mode transcribe --json
  google-oauth-token:        OK (Chrome profile auth)
  chrome-profile:            OK (OpenClaw browser profile)
  audio-bridge:              OK (pcm16-24khz)
  guest-join-defaults:       OK (auto-join + tab reuse)
  chrome-local-audio-device: OK (virtual meeting audio ready)
  chrome-local-audio-cmds:   OK (sox)
  → 6/8 checks passed (Twilio는 optional)
```

### agent 모드 체크

```bash
$ openclaw googlemeet setup --transport chrome --mode agent --json
  intro-after-in-call:       OK (wait 20000ms)
  twilio-voice-call-plugin:  OK (delegate to voice-call)
  → 9/11 checks passed (Twilio 인증 미설정은 optional)
```

### 오디오 환경

```bash
$ system_profiler SPAudioDataType | grep BlackHole
  BlackHole 2ch:  installed
  BlackHole 16ch: installed

$ command -v sox
/opt/homebrew/bin/sox
```

### 드리프트 요약

| 항목 | 글 작성 시점 (2026-05) | 검증 시점 (2026-09) |
| --- | --- | --- |
| OpenClaw 버전 | 2026.5.26 | **2026.9.6** |
| 플러그인 버전 | 미표기 | **v2026.9.5** |
| intro-after-in-call | 없음 | **20000ms 대기 (신규)** |
| twilio-voice-call 위임 | 없음 | **voice-call 플러그인 위임 (신규)** |
| audio bridge 규격 | 미표기 | **pcm16-24khz** |
| 핵심 설정 흐름 | 동일 | 동일 |
| BlackHole + SoX | 동일 | 동일 |
| OAuth 흐름 | 동일 | 동일 |

![Google Meet 플러그인 검증: 설치·설정 확인](./media/openclaw-google-meet-plugin-setup-guide-2026-05-28/verify-01-plugin-setup-2026-09-25.png)
*블로그봇이 직접 실행한 Google Meet 플러그인 검색·설정·오디오 환경 확인*

![Google Meet 플러그인 검증: 드리프트 확인](./media/openclaw-google-meet-plugin-setup-guide-2026-05-28/verify-02-agent-drift-2026-09-25.png)
*에이전트 모드 설정 체크 및 블로그 대비 변경 사항*

---

참고: [OpenClaw Google Meet plugin docs](https://github.com/openclaw/openclaw/blob/main/docs/plugins/google-meet.md)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 공식 문서를 확인하고 직접 설정·실행해 검증한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
