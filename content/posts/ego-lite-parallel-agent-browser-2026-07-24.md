---
title: "ego lite: 사람과 AI 에이전트가 같은 브라우저를 나눠 쓰면 생기는 일"
date: 2026-07-24
draft: false
tags:
  - ego-lite
  - AI-agent
  - browser-automation
  - Chromium
  - agent-browser
  - browser-use
categories:
  - AI
  - Agent
description: "CitroLabs ego lite를 README 기준으로 읽었다. 핵심은 브라우저 자동화 라이브러리가 아니라, 사람과 AI 에이전트가 같은 Chromium 브라우저를 병렬로 쓰도록 만든 일상용 브라우저라는 점이다."
aliases:
  - /posts/ego-lite-parallel-agent-browser-2026-07-24
---

![ego lite README의 배너. 이 프로젝트가 말하는 핵심은 에이전트용 별도 브라우저가 아니라, 사람이 쓰는 브라우저 안에 에이전트용 작업공간을 함께 두는 것이다.](/images/ego-lite-parallel-agent-browser-2026-07-24/banner.png)

브라우저 자동화에서 제일 답답한 순간은 대개 모델 성능 문제가 아닙니다. 로그인입니다. 세션입니다. 내가 보고 있던 탭을 에이전트가 빼앗아 가는 문제입니다.

CitroLabs가 공개한 **ego lite**는 이 문제를 정면으로 건드립니다. 한마디로 말하면 **사람과 AI 에이전트가 동시에 쓰는 Chromium 기반 브라우저**입니다. 내 탭은 내 탭대로 쓰고, 에이전트는 자기 **Space**에서 따로 일합니다. Chrome 로그인, 쿠키, 확장 프로그램, 북마크까지 가져올 수 있으니, 에이전트가 “깨끗한 빈 브라우저”가 아니라 내가 실제로 쓰는 웹 환경 위에서 움직입니다.

## 데모를 보면 포지셔닝이 바로 보인다

README에 있는 데모 영상부터 보는 게 제일 빠릅니다. ego lite 안에서 에이전트가 별도 Space를 열고, 사용자의 일반 브라우징을 방해하지 않은 채 페이지를 읽고 조작하는 흐름을 보여줍니다.

<video controls src="https://github.com/user-attachments/assets/ffe7954b-58ee-411e-b35d-ec30c58a08bc" style="width: 100%; border-radius: 12px;" title="ego lite demo video"></video>

[데모 영상 원본 보기](https://github.com/user-attachments/assets/ffe7954b-58ee-411e-b35d-ec30c58a08bc)

여기서 중요한 건 “AI가 브라우저를 조작한다”가 아닙니다. 그건 이미 browser-use, Playwright 기반 도구, agent-browser 같은 쪽에서 오래 해온 일입니다. ego lite의 질문은 다릅니다. **사람이 쓰는 브라우저와 에이전트가 쓰는 브라우저를 왜 계속 분리해야 하지?** 이 질문입니다.

## 자동화 라이브러리가 아니라 같이 쓰는 브라우저다

기존 브라우저 자동화 프레임워크는 보통 에이전트가 별도 브라우저를 띄워서 조작합니다. 그러면 바로 문제가 생깁니다. 로그인 세션이 없습니다. 2FA가 걸립니다. 내가 쓰는 확장 프로그램도 없습니다. 페이지 하나를 조작하려고 해도 “명령 실행 → 결과 확인 → 다시 명령 실행” 루프가 길어집니다.

ego lite는 접근을 바꿉니다. 브라우저 기능을 에이전트가 호출할 수 있는 **JavaScript 함수**로 감싸서 제공합니다. snapshot, fill, click, wait, navigate, capture 같은 기능을 에이전트가 코드로 조합합니다. README 표현대로라면, 에이전트가 가장 잘하는 일인 “코드 작성”으로 브라우저 워크플로우를 한 번에 구성하게 하는 방식입니다.

이 차이가 실제로 의미 있는 지점은 복잡한 작업입니다. CitroLabs는 ego lite가 Vercel의 agent-browser 대비 복잡한 브라우저 자동화 작업에서 **최대 2.5배 빠르게** 끝났고, 토큰도 상당히 적게 썼다고 주장합니다. 독립 벤치마크는 아니므로 숫자는 제품 측 주장으로 읽어야 합니다. 그래도 포인트는 분명합니다. CLI 호출을 반복하는 브라우저 자동화보다, 브라우저 액션을 코드 단위로 합성하는 방식이 에이전트에는 더 자연스럽다는 이야기입니다.

![ego lite README의 벤치마크 이미지. 네 개의 복잡한 브라우저 자동화 태스크에서 ego lite와 Vercel agent-browser를 비교하며, 작업이 복잡할수록 실행 시간과 토큰 차이가 벌어진다고 설명한다.](/images/ego-lite-parallel-agent-browser-2026-07-24/ego-vs-agent-benchmark.png)

## Space는 에이전트용 격리 작업대다

README에서 제일 눈에 띄는 개념은 **Space**입니다. 에이전트마다 독립된 작업공간을 주는 구조입니다. Claude Code가 10개의 리드를 10개의 Space에서 보강하고, Codex가 5개의 경쟁사 사이트를 5개의 Space에서 긁어오는 식의 병렬 작업을 상정합니다.

이 말은 단순히 탭을 여러 개 연다는 뜻이 아닙니다. 브라우저 안에 “내가 일하는 공간”과 “에이전트가 일하는 공간”을 분리합니다. 내 마우스 커서는 그대로 있고, 내 탭도 그대로입니다. 에이전트가 뭔가 하다가 인증이 필요하면 내가 그 Space로 들어가서 로그인만 도와줄 수 있고, 이상하게 흘러가면 중단하거나 직접 접管(take over)할 수 있습니다.

에이전트 브라우저의 가장 큰 불안은 통제감입니다. 내가 모르는 탭에서 뭔가 벌어지고, 내 세션으로 클릭이 일어나고, 언제 멈출지 모르면 도구가 좋아도 쓰기 어렵습니다. Space는 이 불안을 줄이기 위한 UI 개념에 가깝습니다. “에이전트가 내 브라우저를 쓴다”가 아니라 “에이전트에게 눈에 보이는 작업대를 하나 준다”에 가깝습니다.

## 비교표에서 보이는 세 가지 카테고리

README의 비교 표는 ego lite의 포지셔닝을 꽤 노골적으로 보여줍니다. 그대로 옮기면 다음과 같습니다.

| Capability                       | ego lite | Browser-Use | agent-browser (Vercel) | ChatGPT Atlas | Perplexity Comet |
| -------------------------------- | :------: | :---------: | :--------------------: | :-----------: | :--------------: |
| Multitask in parallel            |    ✓     |      —      |           —            |       —       |        —         |
| Reusable skills                  |    ✓     |      —      |           —            |       —       |        —         |
| Inherits Chrome's data           |    ✓     |      —      |           —            |       ✓       |        ✓         |
| Same browser, separate workspace |    ✓     |      —      |           —            |       —       |        —         |
| Compressed semantic input        |    ✓     |      —      |           ✓            |       —       |        —         |
| Controllable by external agents  |    ✓     |      ✓      |           ✓            |       —       |        —         |
| Data stored locally              |    ✓     |      ✓      |           ✓            |       —       |        —         |
| No login friction                |    ✓     |      —      |           —            |       ✓       |        ✓         |
| Daily-use browser                |    ✓     |      —      |           —            |       ✓       |        ✓         |
| Free                             |    ✓     |      ✓      |           ✓            |       —       |        —         |

이 표를 보면 시장이 세 갈래로 나뉩니다.

첫째, **Browser-Use나 Vercel agent-browser 같은 자동화 프레임워크**입니다. 에이전트가 부르는 라이브러리입니다. 장점은 유연성입니다. 단점은 자체 브라우저가 아니라서 로그인과 실제 사용 환경이 매번 걸립니다.

둘째, **ChatGPT Atlas나 Perplexity Comet 같은 AI 브라우저**입니다. 일상용 브라우저를 지향하고 로그인 마찰은 줄일 수 있습니다. 대신 내장된 에이전트가 중심입니다. Claude Code, Codex, Cursor처럼 내가 이미 쓰는 외부 에이전트를 마음대로 붙이는 그림과는 거리가 있습니다.

셋째, **ego lite**입니다. ego lite는 “브라우저 자동화 라이브러리”와 “AI 브라우저” 사이에 걸쳐 있습니다. Chromium 기반 일상용 브라우저인데, 동시에 외부 에이전트가 `ego-browser`를 통해 제어할 수 있습니다. 이 조합이 이 프로젝트의 핵심입니다.

## Chrome 데이터를 가져온다는 말의 무게

첫 실행 때 ego lite는 Chrome 데이터를 가져올지 묻는다고 합니다. 여기서 예를 선택하면 로그인 상태, 쿠키, 확장 프로그램, 북마크가 이동합니다. 즉 에이전트가 빈 브라우저가 아니라 실제 사용자의 로그인된 웹 환경을 쓰게 됩니다.

이건 강력하지만, 동시에 조심해야 할 부분입니다. API가 없는 SaaS 백엔드, 로그인 뒤에 숨어 있는 대시보드, 결제 직전 단계, 채용 사이트, 부동산 사이트, CRM 같은 곳까지 에이전트가 접근할 수 있다는 뜻입니다. 편합니다. 하지만 권한 범위와 중단 지점이 명확해야 합니다.

README의 사용 예시는 전부 이 지점을 향합니다.

- X, LinkedIn, Threads, Reddit에서 팔로우, 예약, 멘션 모니터링
- LinkedIn, Wellfound, YC Startup Jobs에서 채용 공고 필터링 후 ATS 진입
- Redfin, Zillow, Amazon, Costco 같은 로그인 기반 검색과 비교
- 항공권, 호텔, 레스토랑 예약 플로우를 결제 직전까지 진행
- HubSpot, Salesforce, Notion, Airtable, Linear, Stripe, GA4에서 리포트 추출과 필드 업데이트

공통점은 간단합니다. **API가 없거나 불완전하고, 로그인이 필요한 웹 업무**입니다. 지금의 에이전트 자동화가 가장 자주 막히는 구간도 정확히 여기입니다.

## 현재는 macOS 전용이고, 브라우저 전체가 오픈소스는 아니다

설치 방법은 세 가지입니다. macOS 앱을 직접 내려받거나, `npx skills add citrolabs/ego-lite`로 `ego-browser` 스킬을 먼저 설치하거나, 에이전트에게 설치 절차를 맡기는 방식입니다. 현재는 **macOS 전용**이고 Windows/Linux는 로드맵에 있습니다.

또 하나의 단서는 라이선스입니다. GitHub 저장소의 내용은 MIT로 공개되어 있지만, README는 **ego lite browser는 별도의 무료 다운로드**라고 구분합니다. 즉 에이전트 대면 도구와 문서는 열려 있지만, 브라우저 제품 전체를 오픈소스 브라우저로 받아들이면 안 됩니다.

이건 채택 판단에서 중요합니다. 로그인 세션과 브라우징 데이터를 다루는 도구라면, “어디까지 로컬에 남는가”, “무엇이 기록되는가”, “브라우저 바이너리를 얼마나 신뢰할 수 있는가”를 봐야 합니다. README는 브라우징 데이터가 기기에 남고, ego lite가 기록하는 것은 설정 중 Chrome migration opt-in 여부뿐이라고 설명합니다. 그래도 조직에서 쓰려면 보안 검토가 먼저일 수밖에 없습니다.

## 제가 흥미롭게 본 지점

저는 이 프로젝트를 “또 하나의 브라우저 자동화 도구”라기보다, **에이전트 시대의 브라우저 UX 실험**으로 보는 쪽이 맞다고 봅니다.

에이전트가 웹을 잘 쓰려면 모델이 똑똑해야 합니다. 그런데 그 못지않게 중요한 건 작업 환경입니다. 로그인은 이어져야 하고, 사용자는 방해받지 않아야 하고, 에이전트가 어디서 뭘 하는지 보여야 하고, 필요하면 사람이 중간에 들어가야 합니다.

ego lite가 던지는 질문은 이겁니다. **AI 에이전트가 정말 일상 업무에 들어온다면, 브라우저는 “한 사람이 쓰는 앱”으로 남을 수 있을까?**

아마 아닐 가능성이 큽니다. 브라우저는 점점 사람 혼자 쓰는 창이 아니라, 사람과 여러 에이전트가 각자의 작업대를 두고 병렬로 움직이는 운영 공간에 가까워질 겁니다. ego lite는 그 방향을 꽤 선명하게 보여주는 초기 사례입니다.

더 실습해보고 싶은 분들을 위한 참고 자료도 붙여둡니다. 이런 브라우저 에이전트 흐름을 직접 손으로 다뤄보고 싶다면 코난쌤의 책 **[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)**와 **[AI 에이전트 실전 강의: 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)** 쪽이 이어서 보기 좋습니다. ego lite 같은 제품도 결국 “에이전트가 실패하고, 관찰하고, 다시 시도하는 루프”를 브라우저라는 생활 공간 안으로 가져오는 문제이기 때문입니다.

## 링크

- GitHub: [citrolabs/ego-lite](https://github.com/citrolabs/ego-lite)
- 문서: [lite.ego.app/document](https://lite.ego.app/document/)
- Roadmap: [lite.ego.app/roadmap](https://lite.ego.app/roadmap)
- X: [@ego_agent](https://x.com/ego_agent)
- Discord: [ego lite Discord](https://discord.gg/5eGZVvHbTq)
