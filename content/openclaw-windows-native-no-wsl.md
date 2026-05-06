---
title: "윈도우에서 오픈클로, WSL 안 깔고 쓰기 — PowerShell 한 줄로 시작하는 AI 어시스턴트"
date: 2026-05-07
tags: [openclaw, AI, 업무자동화, Windows, 설치가이드]
description: "WSL 설치가 어려운 윈도우 사용자를 위한 오픈클로 네이티브 설치 가이드. PowerShell 한 줄로 설치하고, WSL 없이 뭘 할 수 있는지, 안 되는 건 뭔지 정리."
slug: openclaw-windows-native-no-wsl
category: AI도구
---

![윈도우에서 오픈클로 — WSL 없이 시작하기](./images/openclaw-win-comic/4panel-comic.jpg)

오픈클로(OpenClaw) 공식 문서에 보면 "WSL2 권장"이라고 적혀있음.

근데 솔직히 말하면, WSL 설치 자체가 이미 장벽임. `wsl --install` 치고 재부팅하고, Ubuntu 터미널 열면 검은 화면에 이상한 프롬프트가 뜨고, 파일은 `/mnt/c/Users/...` 로 들어가야 하고… 윈도우 쓰던 사람한테는 그냥 "리눅스를 또 배워야 하나?" 싶음.

안 그래도 됨.

**윈도우에 그냥 바로 깔면 됨.** PowerShell 한 줄이면 끝남.

---

## 설치 — 진짜 한 줄임

PowerShell 열고 이거 복사해서 붙여넣기:

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

끝.

이 스크립트가 알아서 하는 일:
1. Node.js 없으면 알아서 깔아줌 (winget → Chocolatey → Scoop 순서로 시도)
2. 오픈클로 npm 패키지 설치
3. PATH 설정까지 정리

설치 끝나면 PowerShell 새로 열고:

```powershell
openclaw --version
```

버전 나오면 성공.

### 설치 후 초기 설정

```powershell
openclaw onboard
```

API 키 입력하고, Telegram/Discord 연결하고, 기본 에이전트 설정하는 대화형 마법사가 시작됨.

---

## WSL 없이 되는 것 — 대부분 다 됨

오픈클로 핵심 기능은 윈도우 네이티브에서 다 돌아감.

### ✅ 되는 것

| 기능 | 설명 |
|------|------|
| **게이트웨이** | `openclaw gateway run` 으로 바로 실행. 서비스 등록도 됨 |
| **메시징 채널** | Telegram, Discord, Slack, WhatsApp, Teams, LINE 등 전부 됨 |
| **AI 모델** | ChatGPT, Claude, Gemini, DeepSeek 등 API 연결 다 됨 |
| **exec (명령어 실행)** | PowerShell 7(`pwsh`) → PowerShell 5.1 순으로 실행. 윈도우 명령어 그대로 씀 |
| **웹검색** | Brave 검색, Tavily 검색 다 됨 |
| **이미지 생성** | DALL-E, Gemini 이미지 생성 다 됨 |
| **이미지 분석** | 사진 보여주면 AI가 분석해줌 |
| **크론 (예약 작업)** | 정해진 시간에 자동 실행. 윈도우 Scheduled Task로 돌아감 |
| **메모리** | 대화 기록, 장기 기억, 파일 기반 메모리 다 됨 |
| **PDF 분석** | PDF 파일 읽고 요약해줌 |
| **웹페이지 읽기** | URL 주면 내용 추출해줌 |
| **Control UI** | 웹 브라우저로 `http://localhost:3777` 접속하면 대화형 UI |
| **스킬 설치** | ClawHub에서 스킬 설치. 근데 bash 필요한 건 안 됨 (아래 참고) |

### 간단 예제 — PowerShell에서 바로 쓰기

설치만 하고 채팅 채널 연결 안 해도, 터미널에서 바로 대화 가능:

```powershell
openclaw agent --local --agent main -m "윈도우 11에서 스크린샷 단축키 알려줘"
```

---

## WSL 없이 안 되는 것 — 솔직히 별로 없음

| 기능 | 이유 | 대안 |
|------|------|------|
| **bash 기반 스킬 일부** | 리눅스 명령어(`grep`, `sed`, `awk` 등)를 직접 쓰는 스킬은 PowerShell에서 안 돌아감 | 해당 스킬만 안 쓰면 됨. 대부분의 스킬은 플랫폼 무관 |
| **Google Meet 실시간 음성** | macOS BlackHole 오디오 라우팅에 의존하는 부분이 있음 | 음성 없이 텍스트 기반으로는 Meet 참가 가능 |
| **음성 웨이크("Hey OpenClaw")** | macOS 전용 | 윈도우에선 안 됨 |
| **컴패니언 앱** | macOS엔 메뉴바 앱, iOS/Android엔 모바일 앱 있음. Windows 앱은 아직 계획 중 | Control UI(웹)로 대체 가능 |
| **일부 스킬의 `os` 제한** | 스킬 manifest에 `os: ["darwin", "linux"]`만 적혀있으면 Windows에선 설치 안 됨 | 해당 스킬이 Windows 지원 추가할 때까지 대기 |

**요약하면:** 핵심 기능은 다 됨. bash 스크립트 직접 실행이나 macOS 전용 오디오 기능만 빠짐.

---

## 파일 어디에 있나 — 그냥 윈도우 경로임

WSL 쓰면 파일이 `/home/사용자/.openclaw/` 에 있어서 윈도우 탐색기로 찾기 어려움.

윈도우 네이티브는 그냥 여기:

```
C:\Users\사용자이름\.openclaw\
```

탐색기로 바로 열 수 있음. 메모장으로 편집도 됨.

주요 파일:
- `openclaw.json` — 설정 파일
- `workspace\` — 에이전트 작업 공간
- `memory\` — 대화 기록

---

## 게이트웨이 서비스 등록 — 컴퓨터 켤 때 자동 실행

```powershell
openclaw gateway install
openclaw gateway status --json
```

윈도우 Scheduled Task로 등록됨. 컴퓨터 켤 때마다 자동으로 오픈클로가 시작됨.

Scheduled Task 권한 문제가 있으면 자동으로 Startup 폴더 폴백으로 넘어감. 둘 다 로그인 후 자동 시작은 보장됨.

---

## 업데이트

설치 명령어랑 똑같음:

```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

이미 설치되어 있으면 업데이트로 동작함.

---

## 나중에 WSL이 필요해지면?

윈도우 네이티브로 쓰다가, bash 스크립트를 돌려야 하거나 WSL 전용 기능이 필요해지면 그때 설치해도 늦지 않음.

WSL 설치는 PowerShell(관리자)에서:

```powershell
wsl --install
```

재부팅 후 Ubuntu 터미널 열고, 같은 명령어로 오픈클로 설치:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

기존에 윈도우에서 쓰던 설정은 `C:\Users\사용자\.openclaw\`에 그대로 있음. WSL에서도 `/mnt/c/Users/사용자/.openclaw/`로 접근 가능.

---

## 정리

| | WSL2 | 윈도우 네이티브 |
|--|------|----------------|
| 설치 난이도 | 중간 (WSL + Ubuntu + 재부팅) | **낮음 (PowerShell 한 줄)** |
| 파일 경로 | `/mnt/c/...` 헷갈림 | **`C:\Users\...` 익숙함** |
| 핵심 기능 | 전부 됨 | 거의 다 됨 (95%+) |
| bash 스크립트 | O | X (PowerShell 사용) |
| Google Meet 음성 | O | 제한적 |
| 컴패니언 앱 | X | X |
| 추천 대상 | 개발자, 리눅스 경험 있음 | **일반 사용자, 윈도우만 쓰는 사람** |

WSL이 어려우면 안 해도 됨. 윈도우에서 그냥 깔면 됨.

---

*오픈클로 v2026.5.4 기준. 전체 문서: <https://docs.openclaw.ai> | GitHub: <https://github.com/openclaw/openclaw>*

<https://www.yes24.com/product/goods/185166276>
