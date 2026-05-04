---
title: "Claude Code에 브라우저 스킬 11개를 몰아넣은 Browserbase, 뭐가 달라지나"
slug: "browserbase-skills-claude-code-plugin-review-2026-05-04"
date: "2026-05-04"
tags: ["AI 코딩", "Claude Code", "Browserbase", "브라우저 자동화", "browse CLI", "웹스크래핑", "Stagehand"]
description: "Browserbase가 Claude Code용 스킬 플러그인 11개를 공개했다. 브라우저 자동화, CAPTCHA 우회, 서버리스 함수 배포, UI 테스트, 디버깅까지. 설치 한 번에 전부 가능한 구조가 어떤 의미인지 정리했다."
hero: ""
category: "AI 도구 리뷰"
author: "코난쌤"
---

## Claude Code가 브라우저를 직접 만진다

AI 코딩 에이전트가 터미널과 에디터만 다루던 시대가 끝났다.

Browserbase가 Claude Code용 스킬 플러그인 11개를 GitHub에 공개했다. (`browserbase/skills`) 설치 한 번이면 Claude Code가 **실제 브라우저를 띄워서 클릭하고, 폼을 채우고, 스크린샷을 찍고, CAPTCHA를 풀고, 서버리스 함수를 배포**한다.

문제는 간단하다. 기존에도 Playwright나 Selenium 같은 도구가 있었음. 근데 AI 에이전트가 이걸 "자연어로" 쓰게 만든 건 Browserbase가 처음이다.

## 설치, 한 줄이면 끝

```bash
npx skills add browserbase/skills
```

또는 Claude Code 안에서:

```
/plugin marketplace add browserbase/skills
/plugin install browse@browserbase
```

재시작하면 Claude가 `browse` 명령을 쓸 수 있다. 끝.

로컬 모드는 Chrome만 있으면 되고, 원격 모드는 Browserbase API 키만 설정하면 된다. 복잡한 설정 파일이나 Docker 컨테이너 같은 건 없음.

## 11개 스킬, 한번에 정리

### 1. browser — 핵심. 브라우저 조작

가장 중요한 스킬이다. `browse` CLI로 웹 페이지를 열고, 클릭하고, 텍스트를 입력하고, 스크린샷을 찍는다.

```bash
browse open https://news.ycombinator.com
browse snapshot    # 페이지 구조 파악 (accessibility tree)
browse click @0-5  # 요소 클릭
browse get text body  # 본문 텍스트 추출
browse stop
```

`browse snapshot`이 핵심이다. 페이지를 시각 이미지로 보는 게 아니라 **접근성 트리**로 구조화해서 읽는다. 그래서 Claude가 "이 버튼이 어디 있는지" 빠르게 파악할 수 있음. 스크린샷은 비싸니까 꼭 필요할 때만.

**로컬 모드 vs 원격 모드:**

| | 로컬 | Browserbase 원격 |
|---|---|---|
| 속도 | 빠름 | 약간 느림 |
| 설치 | Chrome 필요 | API 키 필요 |
| 스텔스 모드 | 없음 | 있음 (안티봇 핑거프린팅) |
| CAPTCHA 해결 | 없음 | 자동 (reCAPTCHA, hCaptcha) |
| 주거IP 프록시 | 없음 | 있음 (201개국) |
| 세션 유지 | 없음 | 있음 (context 기반) |

단순 문서 사이트는 로컬이면 충분함. Cloudflare 방어벽, 로그인 벽, CAPTCHA가 있는 곳은 원격 모드로 전환하면 된다.

### 2. browserbase-cli — 플랫폼 관리

`bb` CLI로 Browserbase 플랫폼 자체를 관리한다. 세션 생성, 프로젝트 조회, 컨텍스트 관리, 익스텐션 설치 등.

### 3. functions — 서버리스 브라우저 자동화

이게 재밌다. 브라우저 자동화를 **클라우드 함수**로 배포한다.

```bash
pnpm dlx @browserbasehq/sdk-functions init my-function
cd my-function
# index.ts 작성
pnpm bb publish index.ts
```

Playwright 코드를 작성하면 Browserbase 클라우드에서 실행되는 서버리스 함수가 됨. 크론 스케줄, 웹훅 엔드포인트, 클라우드 자동화 — 로컬 컴퓨터 켜둘 필요 없다.

### 4. ui-test — AI 적대적 UI 테스트

단순히 "버튼 있나요?"를 확인하는 게 아니라 **의도적으로 부숴보는** 테스트다.

- **Diff 기반**: git diff를 분석해서 바뀐 부분만 테스트
- **탐색형**: 앱 전체를 돌아다니며 개발자가 생각 못 한 버그를 찾음
- **병렬**: 여러 Browserbase 브라우저에 테스트 그룹을 분산 실행

테스트 계획을 3라운드로 짠다:
1. **Functional**: 핵심 사용자 플로우가 작동하는가
2. **Adversarial**: 빈 폼 제출, 더블클릭, 특수문자, 경쟁 상태 같은 엣지 케이스
3. **Coverage**: 접근성(a11y), 모바일 뷰포트, 콘솔 에러

서브에이전트들이 병렬로 실행하고, 메인 에이전트가 결과를 병합해서 리포트를 낸다. `Tests: 20 | Passed: 14 | Failed: 4 | Skipped: 2` 형식.

### 5. site-debugger — 자동화 실패 디버깅

브라우저 자동화가 실패했을 때 원인을 분석한다. 봇 탐지, 셀렉터 변경, 타이밍 이슈, 인증 문제, CAPTCHA — 문제를 진단하고 수정된 site playbook을 생성한다.

### 6. browser-trace — CDP 전체 캡처

DevTools 프로토콜(CDP) 이벤트를 전부 녹화한다. 네트워크 요청, 콘솔 로그, DOM 변화, 스크린샷을 시간순으로 기록하고, 페이지 단위로 분할한다.

핵심은 **메인 자동화를 방해하지 않는다**는 것. CDP는 여러 클라이언트를 동시에 허용하니까, 읽기 전용 두 번째 클라이언트로 관찰만 함.

### 7. cookie-sync — 쿠키 동기화

로컬 Chrome의 쿠키를 Browserbase 컨텍스트로 복사한다. 로그인 상태를 원격 세션에서 그대로 쓸 수 있음.

### 8. fetch — 브라우저 없는 HTTP 요청

브라우저를 띄울 필요 없이 HTML이나 JSON을 가져온다. 상태 코드, 헤더, 리다이렉트까지 확인. 가벼운 작업에 적합.

### 9. search — 브라우저 없는 웹 검색

검색 결과를 구조화된 데이터(제목, URL, 메타데이터)로 반환한다. 역시 브라우저 세션 불필요.

### 10. bb-usage — 사용량 대시보드

Browserbase 사용량, 세션 분석, 비용 예측을 터미널에서 보여준다.

### 11. cookie-sync (상세)

위와 동일. 인증이 필요한 사이트를 원격에서 자동화할 때 필수.

## 왜 이게 달라야 하나

기존 AI + 브라우저 자동화의 문제는 세 가지였음.

**첫째, AI가 브라우저를 "이해"하지 못했다.** Selenium 스크립트를 짜는 건 여전히 프로그래밍이었음. Browserbase는 `browse snapshot`으로 페이지를 접근성 트리로 읽어서 Claude가 구조를 바로 파악하게 만들었다.

**둘째, 봇 탐지를 우회하지 못했다.** AI가 스크래핑하다가 Cloudflare에 막히면 거기서 끝. Browserbase 원격 모드는 안티봇 핑거프린팅, 주거IP 프록시, 자동 CAPTCHA 해결을 기본으로 제공한다.

**셋째, 배포가 안 됐다.** 로컬에서만 돌아가는 자동화는 데모일 뿐임. `functions` 스킬이 서버리스 배포를 한 명령으로 만들었다.

## 어떤 사람한테 필요한가

- **웹 스크래핑 하는 사람**: 봇 탐지, CAPTCHA, IP 차단 문제가 사라짐
- **QA 엔지니어**: UI 테스트를 자연어로 지시하고 AI가 적대적 테스트까지 돌려줌
- **Claude Code 사용자**: 터미널 밖의 세계(웹)를 Claude가 직접 다룰 수 있음
- **자동화 파이프라인 만드는 사람**: 로컬뿐 아니라 클라우드에서도 브라우저 자동화를 서버리스로 배포 가능

## 한계

- Browserbase 원격 모드는 **유료**다. API 키 발급 후 사용량에 따라 과금.
- `browse` CLI 자체는 오픈소스지만, 진짜 가치(스텔스, CAPTCHA, 프록시)는 Browserbase 클라우드에 종속됨.
- Claude Code 외에 다른 AI 에이전트에서 쓰려면 스킬 포맷 변환이 필요. (Skills는 Claude Code 플러그인 아키텍처에 맞춰져 있음)

## 핵심은 "스킬"이라는 단위

Browserbase가 만든 건 브라우저 자동화 도구가 아니다. **AI 에이전트가 쓸 수 있는 능력 단위**를 만든 거다.

`browse open` → `browse snapshot` → `browse click` → `browse snapshot` 사이클이 사람이 브라우저를 쓰는 방식과 거의 같다. 페이지를 열고, 구조를 파악하고, 클릭하고, 결과를 확인하고. 이걸 Claude가 자연어 지시만으로 수행한다.

11개 스킬이 각자 독립적이면서도 `browse` CLI라는 하나의 인터페이스로 묶여 있다는 게 설계의 핵심. 브라우저 조작, 테스트, 디버깅, 배포, 모니터링이 다 같은 CLI 생태계 안에서 돌아간다.

## 실제로 써보려면

```bash
# browse CLI 설치
npm install -g @browserbasehq/browse-cli

# Browserbase API 키 (원격 모드용, 무료 티어 있음)
# https://browserbase.com/settings

# Claude Code에 스킬 추가
npx skills add browserbase/skills
```

로컬 모드만 쓸 거면 Chrome만 있으면 당장 시작할 수 있다.

---

**참고**
- GitHub: <https://github.com/browserbase/skills>
- Stagehand 문서: <https://github.com/browserbase/stagehand>
- Claude Code Skills 설명: <https://support.claude.com/en/articles/12512176-what-are-skills>
