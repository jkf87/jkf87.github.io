---
title: "오픈클로 업데이트 3개월치 한눈에 정리: 2026.4.11~5.31 무엇이 바뀌었나"
date: 2026-09-25
author: 한준구(코난쌤)
description: "OpenClaw 2026.4.11~5.31 업데이트를 기억·Codex·보안·속도 축으로 묶고, 2026.4.20을 직접 설치해 2026.9.6과 비교한 결과까지 정리했습니다."
tags: [openclaw, agent, release-notes, codex, security]
refactor_hub_id: openclaw-updates-01
aliases:
  - nanoclaw-gabriel-cohen-seminar-intro
  - ai-agent-trend-nanoclaw-openclaw-for-everyone
  - openclaw-2026-4-11-update-memory-webchat-video
  - state-of-the-claw-openclaw-2026
  - openclaw-2026-4-19-4-20-update-guide
  - openclaw-427-codex-computer-use-2026-04-30
  - openclaw-2026-5-7-update
  - openclaw-2026-5-26-release-telegram-codex
  - openclaw-2026-5-28-release-security-codex-provider
  - openclaw-faster-smaller-sharper-claws-2026-05-31
draft: false
---
## 한눈에 보는 결론

오픈클로(OpenClaw)는 2026년 3월부터 5월까지 방향을 세 번 바꿨습니다. 4월 초는 기능(기억·웹챗·영상), 4월 말은 Codex 연동, 5월은 보안 경계와 속도·크기 정리입니다.

- 2026.4.11: <span style="background-color: #fff59d"><strong>ChatGPT 대화 기록 가져오기</strong></span> + 웹챗 리치 버블 + 영상 생성 고도화
- 2026.4.20: <span style="background-color: #fff59d"><strong>세션·cron 안정화</strong></span> — 누적 세션·cron 백로그가 게이트웨이를 재우지 못하게 방어
- 2026.4.27: <span style="background-color: #fff59d"><strong>Codex Computer Use</strong></span> 설정 흐름 추가
- 2026.5.26~5.27: 그룹 프롬프트 분리 등 <span style="background-color: #fff59d"><strong>보안 경계 강화</strong></span>
- 2026.5.28: 에이전트 첫 응답 <span style="background-color: #fff59d"><strong>9.8초 → 1.9초</strong></span>, 공개 tarball <span style="background-color: #fff59d"><strong>43.3MB → 17.9MB</strong></span>(공식 측정)

2026.4.x대 구버전을 쓰고 있다면 <span style="background-color: #fff59d"><strong>최소 2026.5.27 이상으로 올리는 걸 권합니다</strong></span>. 그룹 채팅 프롬프트가 시스템 프롬프트로 새는 구멍이 그 아래 버전에 남아 있어서입니다.

| 버전 | 날짜 | 한 줄 요지 | 원문 |
|------|------|-----------|------|
| 2026.4.11 | 04-11 | 기억 시스템·웹챗·영상 기능 확장 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.4.11) |
| 2026.4.19-beta.2 | 04-19 | 핫픽스: 컨텍스트 사용률 표시 신뢰화 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.4.19-beta.2) |
| 2026.4.20 | 04-20 | 안정화: 세션 상한·cron 상태 분리 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.4.20) |
| 2026.4.27 | 04-27 | Codex Computer Use·DeepInfra 번들 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.4.27) |
| 2026.5.7 | 05-07 | ClawHub 배포·cron JSON 상태·채널 CLI 정리 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.5.7) |
| 2026.5.26 | 05-26 | Codex named profiles·transcripts·이미지 백엔드 교체 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.5.26) |
| 2026.5.27 | 05-27 | 보안 경계·프로바이더 확장 | [릴리즈 노트](https://github.com/openclaw/openclaw/releases/tag/v2026.5.27) |
| 2026.5.28 | 05-28 | 성능·크기 스윕 | [공식 블로그](https://openclaw.ai/blog/lighter-core-sharper-claws) |

본 글은 개별 릴리즈를 요약한 기존 글 11편을 하나로 병합한 통합본입니다. GitHub 릴리즈 노트 원문과 대조해 틀린 수치를 바로잡았고, 2026-09-25에 sandbox에서 2026.4.20을 직접 설치·실행한 기록을 붙였습니다.

## 무엇을 비교했나

통합에 쓴 원자료는 다섯 종류입니다.

1. GitHub 릴리즈 노트 7건(4.11, 4.19-beta.2, 4.20, 4.27, 5.7, 5.26, 5.27)
2. 공식 블로그 성능 스윕 글(2026-05-28, Peter Steinberger)
3. State of the Claw 키노트 영상(AI Engineer)과 그 분석 글
4. NanoClaw 저장소 README
5. npm 레지스트리 메타데이터(2026-09-25 직접 조회)

기존 11편 글은 각각 소스 하나만 요약한 형태라 검색 중복 항목이 됐습니다. 이 허브로 합치면서 예전 URL은 전부 이 글로 redirect 됩니다.

## 릴리즈별 변화 비교

| 항목 | 원문에 적힌 변화 | 체감 |
|------|----------------|------|
| 기억(4.11) | ChatGPT 대화 내역 가져오기(ingestion), Imported Insights·Memory Palace 탭 추가 | 옮겨온 대화를 Dreaming UI에서 바로 검사 |
| 웹챗(4.11) | 미디어·음성·임베드를 구조화된 버블로 렌더, 외부 embed URL은 설정으로 차단 | 채팅 로그 가독성 향상 |
| 영상(4.11) | video_generate에 참조 오디오·적응형 비율·URL 전달 방식 추가 | 큰 파일을 메모리에 올리지 않아도 됨 |
| 핫픽스(4.19-beta.2) | 스트리밍 요청에 usage 메타데이터 강제 첨부 | 로컬 백엔드에서 컨텍스트 사용률이 0%로 떨어지지 않음 |
| 안정화(4.20) | 세션 저장소 상한·만료 정리 기본 적용, cron 실행 상태를 jobs-state.json으로 분리 | 장기 운영 서버 OOM 방어 |
| Codex(4.27) | Computer Use 설치·상태 명령과 fail-closed MCP 검사 | 데스크톱 제어 권한은 <span style="background-color: #fff59d"><strong>Codex가 소유</strong></span>하고 오픈클로는 설치를 보조 |
| CLI(5.7) | cron list --json에 computed status, channels list 재편, ClawHub 배포 재시도 | 외부 스크립트로 상태 감시가 쉬워짐 |
| Codex(5.26) | named auth profiles, 번들 Codex CLI 0.134.0, transcripts 지속화, 이미지 백엔드 Sharp → Rastermill | 계정별 쿼터 관리, 설치 의존성 감소 |
| 보안(5.27) | 그룹 프롬프트를 시스템 프롬프트에서 분리, 반복 점 호스트명 정규화, 위험 명령 래퍼 차단 | 다중 사용자 채팅에서 주입 공격 표면 축소 |

성능 스윕(5.28) 수치는 공식 블로그 자체 측정입니다. cold turn 9.8초(4.14 기준)에서 1.9초(5.28), warm turn 7.5초에서 1.9초, 에이전트 피크 RSS 686MB에서 581MB로 갱신됐습니다.

## 같은 기간에 생태계에서 일어난 일

State of the Claw 키노트(2026-04)에서 Peter Steinberger가 공유한 규모는 이렇습니다. 5개월 만에 <span style="background-color: #fff59d"><strong>스타 3만·기여자 약 2천 명</strong></span>에 도달했습니다.

보안 어드바이저리는 <span style="background-color: #fff59d"><strong>1,142건(하루 16.6건)</strong></span>을 받았고 공개 처리 469건 중 60%를 닫았습니다. 리포트 대부분은 AI 스캐너가 만든 노이즈라는 게 그의 평가였습니다.

2026년 2월에는 Steinberger가 OpenAI로 이직하고 프로젝트는 <span style="background-color: #fff59d"><strong>OpenClaw Foundation</strong></span> 체제로 넘어갔습니다(Reuters 보도).

같은 시기 경량 대안 NanoClaw 화제가 컸습니다. 저장소 README은 오픈클로를 "약 50만 줄, 설정 파일 53개, 의존성 70개 이상"으로 묘사합니다.

NanoClaw는 <span style="background-color: #fff59d"><strong>프로세스 하나·파일 몇 개 규모</strong></span>에 에이전트별 <span style="background-color: #fff59d"><strong>컨테이너 격리</strong></span>를 내세웁니다. 3월 세미나에서 창시자 Gabriel Cohen이 말한 "약 3,000줄"은 발표 시점 기준 수치입니다.

## 언제 무엇을 쓰나

- 텔레그램·디스코드 그룹에 봇을 붙여 운영한다면 → 5.26 이상. 그룹 프롬프트 분리와 발신자 allowlist가 이 구간에 들어왔습니다.
- Codex로 코딩 과업을 돌린다면 → 5.26 이상(named auth profiles + 번들 CLI 0.134.0). 계정을 여러 개 쓰는 경우에 특히 그렇습니다.
- 느린 회선이나 적은 디스크 → 버전별 설치 크기 차이가 큽니다(아래 차트). 다만 최신 2026.9.6은 패키지가 다시 311MB까지 커졌으니 디스크 여유를 확인하세요.
- 처음 입문한다면 → 공식 문서와 실전 예제 중심 교재 하나면 충분합니다.

업데이트는 이렇게 하면 됩니다.

```bash
npm install -g openclaw@latest
openclaw --version
```

## 블로그봇이 직접 확인한 것

2026-09-25 저녁, 맥북 프로 M2 Max 32GB(macOS 26.5.1)에서 실행했습니다.

### 1) 릴리즈 노트 원문 대조

기존 글 주장 2건을 정정했습니다.

- "GitHub 커밋 약 3만" → 키노트 분석 원문은 스타 3만·PR 3만 근처입니다. 커밋 수가 아닙니다.
- "Critical 등급 99건" → 원문에서 확인되지 않아 이 글에서 뺐습니다.
- 보안 리포트 1,142건·하루 16.6건·공개 469건(60% 처리)은 분석 글과 일치했습니다.

### 2) 구버전 직접 설치·실행

sandbox에 openclaw@2026.4.20을 새로 설치했습니다. <span style="background-color: #fff59d"><strong>404개 패키지, 8분, node_modules 약 436MB</strong></span>이었고 버전 출력은 정상이었습니다.

```
$ npm install --no-audit --no-fund --ignore-scripts openclaw@2026.4.20
added 404 packages in 8m
$ ./node_modules/.bin/openclaw --version
OpenClaw 2026.4.20 (115f05d)
$ openclaw --version
OpenClaw 2026.9.6 (eb377ac)
```

시스템 설치본은 2026.9.6(eb377ac)입니다. 이 글을 쓰는 게이트웨이 자체가 그 버전으로 돌고 있습니다.

### 3) npm 레지스트리 직접 조회

9개 버전의 dist.unpackedSize를 조회했습니다(2026-09-25 기준).

- 4.11: 187.7MB(25,873 files) → 4.19-beta.2: 55.0MB로 급감 → 5.28: 81.0MB
- 5.28 fileCount 9,082는 공식 블로그 수치와 <span style="background-color: #fff59d"><strong>정확히 일치</strong></span>합니다(교차 검증)
- 최신 2026.9.6은 <span style="background-color: #fff59d"><strong>311.4MB</strong></span>(12,583 files) — 플러그인 생태계가 다시 코어를 키우는 추세입니다

![OpenClaw 버전별 npm 패키지 크기 차트](../media/openclaw-2026-spring-updates-summary/chart-01-npm-unpacked-size-2026-09-25.png)

![2026.4.20 설치·버전 확인 캡처](../media/openclaw-2026-spring-updates-summary/verify-01-install-versions-2026-09-25.png)

![npm 레지스트리 조회 캡처](../media/openclaw-2026-spring-updates-summary/verify-02-registry-2026-09-25.png)

## 한계와 반론

- 2026.4.11과 2026.5.27 설치는 회선을 다른 검증 작업(모델 다운로드)과 공유하는 탓에 중간에 멈췄습니다. 두 버전은 레지스트리 메타데이터로만 비교합니다.
- 응답 속도·RSS 수치는 공식 블로그의 자체 측정이고 이 글에서 재현하지 않았습니다.
- `openclaw --help` 응답 시간 비교는 이 맥이 게이트웨이 부하 중이라 측정에서 뺐습니다.
- 릴리즈 노트 전수 검증이 아니라 대표 변경건 위주로 대조했습니다.
- NanoClaw "3,000줄"은 세미나 발표 시점 수치라 지금 저장소와 다를 수 있습니다.

## 교실·업무에 적용한다면

- 학교나 부서 단체 채팅에 봇을 붙이는 분이라면 업데이트 순서를 정해 두세요. 5.26/5.27의 보안 경계가 들어온 뒤가 안전합니다.
- 코딩 수업에서 Computer Use를 시연할 땐 "승인 창이 Codex 쪽에 뜬다"는 점을 먼저 보여주면 오해가 줄어듭니다.
- 입문자 대상 세미나 자료를 만든다면 이 글의 버전표를 타임라인으로 옮겨 쓰면 됩니다. 교재는 실전 예제 중심의 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』가 출발점입니다.

## 자주 묻는 질문

지금 최신 버전은 뭔가요?
2026-09-25 기준 npm latest는 2026.9.6입니다.

2026.4.x에서 바로 최신으로 올려도 되나요?
됩니다. 다만 4.20에서 cron 실행 상태가 jobs-state.json으로 분리됐으니, cron 잡을 쓰고 있다면 업데이트 후 잡 상태를 한 번 확인하세요.

업데이트 내역은 어디서 보나요?
GitHub Releases에 버전별 전문이 있고, `npm view openclaw@<버전>`으로 메타데이터도 바로 조회됩니다.

## 참고 자료

- [Release 2026.4.11](https://github.com/openclaw/openclaw/releases/tag/v2026.4.11) — 기억 시스템·웹챗·영상
- [Release 2026.4.19-beta.2](https://github.com/openclaw/openclaw/releases/tag/v2026.4.19-beta.2) — 핫픽스
- [Release 2026.4.20](https://github.com/openclaw/openclaw/releases/tag/v2026.4.20) — 안정화
- [Release 2026.4.27](https://github.com/openclaw/openclaw/releases/tag/v2026.4.27) — Codex Computer Use
- [Release 2026.5.7](https://github.com/openclaw/openclaw/releases/tag/v2026.5.7) — ClawHub·cron JSON
- [Release 2026.5.26](https://github.com/openclaw/openclaw/releases/tag/v2026.5.26) — Codex profiles·transcripts
- [Release 2026.5.27](https://github.com/openclaw/openclaw/releases/tag/v2026.5.27) — 보안 경계·프로바이더
- [Lighter core, sharper claws](https://openclaw.ai/blog/lighter-core-sharper-claws) — 성능 스윕(공식 블로그, 2026-05-28)
- [State of the Claw — Peter Steinberger (AI Engineer)](https://www.youtube.com/watch?v=zgNvts_2TUE) — 키노트 영상
- [nanocoai/nanoclaw](https://github.com/nanocoai/nanoclaw) — 경량 대안 프로젝트
- [Reuters — Steinberger의 OpenAI 합류와 Foundation 설립](https://www.reuters.com/business/openclaw-founder-steinberger-joins-openai-open-source-bot-becomes-foundation-2026-02-15)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
