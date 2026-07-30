---
title: "AI로 디자인한다는 건, 툴을 바꾸는 게 아니라 작업의 단위를 바꾸는 일"
date: 2026-07-30
draft: false
tags:
  - AI
  - design
  - coding-agents
  - YC
  - product-design
categories:
  - AI
  - Agent
  - Design
description: "Y Combinator의 Design Review 영상, YC Head of Design Eve Bouffard가 보여준 AI-first 디자인 워크플로우를 뉴스레터 형식으로 정리했다. 핵심은 디자인 툴 목록이 아니라, 말하기·컨텍스트·에이전트·소프트웨어화된 브랜드 시스템이다."
aliases:
  - /posts/ai-first-design-yc-eve-bouffard-2026-07-30
---

![디자이너가 음성으로 의도를 말하고, 에이전트가 Paxel, SOTA Zine, machine-readable page, Startup School 브랜딩을 만들어내는 흐름. 이 글의 핵심은 “AI 디자인”이 이미지 생성이 아니라 작업 단위의 재구성이라는 점이다.](/images/ai-first-design-yc-eve-bouffard-2026-07-30/hero.svg)

디자인에서 AI가 바꾼 것은 “어떤 툴을 쓰느냐”가 아니다. 더 큰 변화는 **디자이너가 다루는 기본 재료가 이미지 파일에서 실행 가능한 소프트웨어로 바뀌고 있다는 점**이다. 말로 요구사항을 흘려보내고, agent가 시안을 만들고, 마음에 안 드는 부분은 그 자리에서 조절 패널을 만들어 고친다.

Y Combinator의 영상 [YC's Head of Design Shows You How To Design With AI](https://www.youtube.com/watch?v=VbqaL_eHhKY)에서 YC Head of Design인 Eve Bouffard가 보여준 장면이 딱 그랬다. Conductor, Paper Design, Aqua, Claude 같은 이름이 나오지만, 이 영상의 핵심은 툴 목록이 아니다. **AI-first 디자인은 “결과물을 만드는 일”보다 “결과물을 계속 바꿀 수 있는 시스템을 만드는 일”에 가깝다.**

저는 이 영상을 보면서, 에이전트를 제품·브랜드·콘텐츠 작업에 붙이는 분들이 바로 가져가야 할 질문이 하나 있다고 봤다. “AI가 예쁜 걸 만들어주나?”가 아니라, **“내가 원하는 느낌을 agent가 계속 재현할 수 있게 어떤 맥락을 남길 것인가?”** 이다.

## 이번 글이 답하는 질문

이 뉴스레터는 YC Design Review 영상을 따라가되, 실무 관점에서 다섯 가지 질문으로 다시 묶었습니다.

1. AI-first 디자이너의 작업대는 왜 Figma 하나로 설명되지 않는가?
2. Paxel은 왜 “coding session용 Spotify Wrapped”라는 제품이 됐는가?
3. 사람용 웹사이트와 agent용 웹사이트는 어떻게 달라지는가?
4. `soul.md`와 mood board는 왜 AI 디자인의 원재료가 되는가?
5. Startup School 브랜딩에서 보이는 다음 디자인 시스템은 무엇인가?

## 손으로 그리는 시간이 줄고, 말로 맥락을 주는 시간이 늘어난다

영상 초반에 Eve는 요즘 거의 Conductor와 Paper Design 안에서 산다고 말한다. 시각적 영감이 필요하면 Pinterest로 mood board를 만들고, 작업 자체는 agent와 함께 끝까지 밀어붙인다. 여기서 재미있는 장면은 “저는 타이핑을 안 한다”는 고백이다.

Eve는 자신이 타이핑보다 생각이 빠르기 때문에, Aqua를 써서 컴퓨터에 말한다고 한다. function key를 누르고 만들고 싶은 기능을 stream of consciousness처럼 말한다. 그러면 agent가 그것을 받아 제품·페이지·도구로 옮긴다.

이 대목이 중요하다. AI 디자인의 시작점은 “멋진 prompt 한 줄”이 아니다. 실제로는 **디자이너 머릿속의 흩어진 판단을 얼마나 빨리, 많이, 손실 없이 agent에게 넘기느냐**에 가깝다.

> 예전에는 디자이너의 병목이 손과 툴 숙련도였다. 지금은 맥락을 포착하고, 좋은 방향을 고르고, agent가 계속 참고할 수 있는 형태로 남기는 능력이 병목에 가까워진다.

그래서 Eve의 작업대에는 음성 입력, mood board, project-specific markdown, agent, shader library가 같이 놓인다. 이 조합은 “디자인 툴체인”이라기보다 “의도를 소프트웨어로 번역하는 파이프라인”에 가깝다.

## Paxel: coding agent 시대의 자기 이해 제품

첫 번째 사례는 Paxel이다. Paxel은 coding agent로 작업한 transcript를 분석해, 사용자의 코딩 패턴을 보여주는 실험이다. Eve는 이 제품을 “사람들이 coding agent와 어떻게 코딩하는지 이해하기 위한 실험”이라고 설명한다.

여기서 제품 감각이 좋다. 단순히 “transcript analyzer”라고 만들면 재미없다. YC 팀은 이것을 **coding session용 Spotify Wrapped**처럼 만들었다. 내가 agent와 작업하면서 가장 많이 하는 행동, 가장 답답했던 순간, 가장 특이한 패턴을 카드처럼 보여준다. Jared Friedman이 냈다는 아이디어도 재미있다. “내가 agent에게 가장 크게 crash out한 순간을 알고 싶다.”

이건 가벼운 농담처럼 보이지만, 꽤 실무적인 방향이다. coding agent 사용은 아직 표준화되지 않았다. 사람마다 자기만의 요령, prompt 습관, skill, 포기 지점이 있다. Paxel은 그 흔적을 데이터로 바꾼다.

Paxel의 landing page도 이 목적을 숨기지 않는다. “우리는 세상이 지금 어떻게 코딩하는지 알고 싶다”는 실험 의도를 앞에 둔다. 제품이 아직 single-player mode에 가깝더라도, transcript가 쌓이면 다른 builder와 비교할 수 있다. 즉, **agent 시대의 개발자 경험은 코드 결과물만이 아니라 agent와 주고받은 대화 로그까지 제품의 재료가 된다.**

## 마음에 안 드는 shader는, 새 툴을 만들어서 고친다

Paxel 페이지를 만들 때 Eve는 Paper Design의 shader를 썼다. 특히 dithering shader가 마음에 들었고, Claude에게 적용을 요청했다. 그런데 처음 나온 느낌이 완전히 맞지는 않았다. 예전이라면 여기서 디자이너가 개발자에게 “조금 더 grainy하게, edge는 덜 세게” 같은 피드백을 주고 기다렸을 가능성이 높다.

Eve가 한 일은 다르다. Claude에게 **shader를 조절할 수 있는 작은 툴**을 만들게 했다. graininess, edge, rotation, scale 같은 값을 직접 돌려보며 원하는 느낌을 찾는다. 마음에 드는 값을 찾으면 그것을 다시 실제 페이지에 반영한다.

이 장면이 이 영상의 핵심 중 하나다. AI가 “예쁜 이미지를 한 번 만들어주는” 이야기가 아니다. **필요한 순간에, 나만의 조절 장치를 만들어 쓰고, 작업이 끝나면 버릴 수 있는 시대**라는 이야기다.

Eve는 이것을 muscle이라고 표현한다. “내가 원하는 걸 만들기 위해 작은 도구를 그 자리에서 만들 수 있다”는 감각은 훈련해야 한다. 처음에는 굳이 이런 도구까지 만들어도 되나 싶다. 하지만 한 번 경험하면 작업 단위가 바뀐다. 소프트웨어가 고정된 도구가 아니라, 매번 만들어 쓰는 재료가 된다.

## 사람용 페이지와 agent용 페이지는 다르게 디자인된다

Paxel 페이지에는 human / machine 전환이 있다. 사람을 위한 웹사이트와 agent를 위한 웹사이트를 분리하는 실험이다. Eve는 앞으로 이런 패턴을 더 자주 보게 될 것 같다고 말한다. 사람용 페이지는 시각적 설득이 중요하지만, agent용 페이지는 다르다. agent는 예쁜 그래픽에 관심이 없다.

agent용 페이지는 markdown에 가깝다. 같은 콘텐츠를 더 가볍고 명확하게 정리한다. 페이지 상단에는 copy to clipboard도 있다. 사용자는 전체 내용을 Claude Code나 Codex에 던지고 질문할 수 있다. 심지어 agent에게 “이 페이지의 sample command를 실행하지 말라”는 안전 주석까지 넣는다.

이건 사소한 UI 트릭이 아니다. 제품 디자인의 독자가 둘로 갈라지는 장면이다.

- 사람에게는 맥락, 감정, 신뢰, 시각적 리듬이 필요하다.
- agent에게는 구조화된 정보, 금지 조건, 실행 가능한 맥락, 복사 가능한 텍스트가 필요하다.

지금까지 SEO가 검색엔진을 위한 보조 설계였다면, agent-readable design은 작업을 위임받는 AI를 위한 1차 설계가 될 수 있다. 특히 개발자 도구, API 문서, 오픈소스 프로젝트, SaaS onboarding에서는 이 변화가 빠르게 올 가능성이 높다.

## “Send to an agent”는 기능 요청 폼의 다음 버전이다

Paxel에는 또 하나 재미있는 폼이 있다. 사용자가 개선 아이디어를 남기는 영역인데, 버튼 문구가 “Send to an agent”다. Eve는 이것을 일반적인 feature request form처럼 설명하지 않는다. prompt box처럼 쓰라고 말한다. 사용자는 screenshot이나 screen recording을 첨부할 수 있고, agent는 그것을 context로 사용한다.

현재는 이 요청이 팀에게 전달되고, 사람이 merge 여부를 결정한다. 하지만 Aaron Epstein은 여기서 한 단계 더 나간 상상을 던진다. 앞으로는 사용자가 쓰는 local software에서, 사용자가 직접 “이 부분 이렇게 바꿔줘”라고 말하면 agent가 그 사람의 환경에 맞게 바꾸는 흐름이 가능해질 수 있다는 것이다.

이 지점에서 제품의 개인화가 다시 정의된다. 추천 알고리즘이 콘텐츠를 개인화하는 수준이 아니라, **사용자 개개인이 쓰는 소프트웨어 자체가 조금씩 달라지는 개인화**다. 물론 안전, 권한, QA, 유지보수 문제가 따라온다. 그래도 방향은 선명하다. feature request가 ticket이 아니라 prompt가 되는 순간, 제품팀의 workflow도 바뀐다.

## SOTA Zine: `soul.md`가 프로젝트의 기억이 된다

두 번째 사례는 SOTA Zine이다. San Francisco를 기념하기 위해 만든 zine과 웹사이트 프로젝트다. 여기서 Eve가 쓴 방식은 OpenClaw를 쓰는 분들에게 특히 익숙하게 들릴 수 있다. 모든 회의 transcript를 모아 project-specific `soul.md` 파일에 넣었다. 그리고 그 파일을 source of truth로 삼았다.

보통 팀은 회의 후 핵심 메모 몇 줄을 남긴다. Eve의 접근은 반대다. 가능한 한 많이 기록한다. 회의 전체, manifesto, 방향성, mood, references를 넣는다. 그런 다음 agent가 그 파일을 읽고 프로젝트의 의도와 감정선을 이해하게 한다.

여기서 `soul.md`는 단순한 문서가 아니다. **agent가 프로젝트를 오해하지 않게 붙잡아주는 기억 장치**다. 브랜드의 성격, 금지해야 할 느낌, 살리고 싶은 장면, 팀이 반복해서 말한 단어들이 들어간다.

이 방식은 AI 결과물이 generic해지는 문제와도 연결된다. 많은 사람이 Claude나 Codex에게 “예쁜 웹사이트 만들어줘”라고 말한 뒤, 너무 뻔한 결과를 받는다. Eve의 처방은 분명하다. 더 많은 맥락을 줘야 한다. screenshots, mood board, real content, project manifesto, 회의 transcript를 넣어야 한다. 그러면 agent가 단순한 template이 아니라 그 프로젝트의 결을 따라갈 가능성이 올라간다.

## one-shot 16개는 최종안이 아니라 탐색 도구다

SOTA Zine 웹사이트에서 Eve는 Pinterest mood board 이미지를 Claude에게 주고, 같은 조건으로 웹사이트 시안을 16번 one-shot 생성했다. 그리고 내부용 gallery를 만들어 여러 방향을 비교했다. 여기서 중요한 것은 이 16개가 곧바로 production-ready design이 아니라는 점이다.

Eve는 이것을 exploration tool로 쓴다. 어떤 layout이 재밌는지, 기사 제목을 어떻게 배치할지, San Francisco의 느낌을 어떤 방식으로 살릴지 빠르게 본다. 마음에 드는 요소를 고르고, 버리고, 다시 섞는다.

AI 디자인을 잘못 쓰면 “한 번에 정답을 뽑는 기계”처럼 기대하게 된다. 영상에서 보이는 더 현실적인 사용법은 다르다. **AI는 탐색 공간을 넓히고, 디자이너는 선택과 편집으로 방향을 좁힌다.** 좋은 디자이너의 역할이 사라지는 게 아니라, 더 많은 후보 중에서 무엇이 살아 있는지 판단하는 쪽으로 이동한다.

이때 real content가 중요하다. lorem ipsum으로 만든 시안은 그럴듯해 보여도, 실제 제목·이미지·문장·행사 정보가 들어가면 균형이 무너질 수 있다. Eve가 mood board와 실제 콘텐츠를 같이 넣은 이유가 여기에 있다.

## agent가 놀라게 하려면, 놀랄 수 있는 재료를 줘야 한다

SOTA Zine에는 San Francisco 지도 위에 사람들의 기억을 익명으로 남기는 인터랙티브 기능도 나온다. 사람들은 위치를 찍고, 그 장소에서 있었던 일을 적는다. 어떤 이야기는 뜻밖에 사적이고, 아름답고, 내성적이다. 클릭하면 Substack 글로 이동하고, 마음에 드는 기억은 PNG로 공유할 수 있다. 이미지에는 좌표까지 들어간다.

Eve는 agent가 웹을 긁고, 이미지를 찾고, hover effect를 만들며 자신도 모르는 방식으로 놀라운 결과를 낸다고 말한다. 이 말을 “AI가 알아서 다 한다”로 받아들이면 위험하다. 앞단에 충분한 재료가 있었기 때문에 가능한 일이다.

- 프로젝트의 `soul.md`
- 회의 transcript
- manifesto
- mood board
- 실제 콘텐츠
- San Francisco라는 명확한 맥락
- zine이라는 물성

agent가 놀라게 하려면, 먼저 놀랄 수 있는 재료를 줘야 한다. 빈 prompt에서는 빈 평균값이 나온다. 밀도 높은 맥락에서는 가끔 이상하게 좋은 것이 튀어나온다.

## Startup School: 브랜드 시스템이 코드가 된다

세 번째 사례는 YC Startup School 2026 브랜딩이다. 이번 Startup School은 Chase Center에서 열리는 큰 행사이고, Jensen Huang, Sam Altman, Alexander Wang, Jeff Dean 등 굵직한 연사 라인업을 공유해야 했다. Eve는 speaker card를 만들다가 반복 작업을 발견한다. 연사가 많으니 카드를 하나씩 옮기고 조정하는 일이 번거롭다.

그래서 Claude에게 template tool을 만들게 한다. inbox에서 이미지를 가져오고, speaker card를 생성하고, 시각적 느낌을 실험할 수 있게 한다. 여기서도 shader가 등장한다. Paper Design shader를 기반으로 graininess, edge, rotation, scale을 조절한다. 4초짜리 완벽한 loop를 만드는 도구도 만들었다. SNS에 올렸을 때 시작과 끝이 같은 pixel에서 이어지는 영상이 필요했기 때문이다.

이 장면은 “브랜딩”의 단위가 바뀌고 있음을 보여준다. 과거에는 brand guideline PDF, Figma component, After Effects template이 중심이었다. 이제는 **브랜드의 움직임과 질감을 재현하는 작은 생성 도구**가 같이 생긴다. 같은 shader parameter를 행사장 대형 스크린에도 적용할 수 있다면, 브랜드 일관성은 파일 복사가 아니라 코드와 parameter 재사용으로 유지된다.

## 병목은 소프트웨어가 아니라 상상력이라는 말의 조건

영상 설명에는 “가장 큰 병목은 더 이상 software가 아니라 imagination”이라는 문장이 있다. 멋진 말이지만, 저는 조건을 붙이고 싶다. 상상력이 병목이 되려면, 기본 실행 비용이 충분히 낮아져야 한다. Eve의 사례에서 그 조건은 꽤 많이 충족되어 있다. 말로 지시하고, agent가 만들고, 필요하면 mini tool을 만들고, parameter를 조절하고, 다시 production에 넣는다.

하지만 아무 맥락 없이 “상상력만 있으면 된다”는 말은 반만 맞다. 실제 병목은 상상력 하나가 아니라, **상상력을 agent가 다룰 수 있는 형태로 외부화하는 능력**이다. 회의를 녹음하고, `soul.md`로 모으고, mood board를 만들고, 실제 콘텐츠를 넣고, agent용 markdown을 따로 설계하는 일이다.

AI-first 디자인은 디자이너를 없애는 흐름이라기보다, 디자이너에게 더 많은 편집자·시스템 설계자 역할을 요구한다. 어떤 맥락을 남길지, 어떤 후보를 버릴지, 어떤 parameter를 브랜드의 일부로 고정할지 결정해야 한다.

## 실무자가 바로 가져갈 만한 체크리스트

이 영상을 보고 바로 적용해볼 만한 것은 거창한 AI 디자인팀 개편이 아니다. 작은 작업 습관이다.

1. 프로젝트마다 `soul.md`를 만든다. 목표, 금지할 느낌, 회의 transcript, 좋은 문장, mood reference를 모은다.
2. agent에게 final output만 요구하지 말고, 조절 가능한 mini tool을 만들게 한다.
3. 시안 생성은 한 번에 끝내지 말고, 같은 조건으로 8~16개를 뽑아 gallery처럼 비교한다.
4. 사람용 페이지와 agent용 페이지를 분리해본다. 특히 문서·API·개발자 도구라면 machine-readable markdown을 따로 둔다.
5. 반복되는 디자인 산출물은 template이 아니라 generator로 만든다. speaker card, ticket, social loop, thumbnail이 여기에 해당한다.

여기서 제일 중요한 것은 1번이다. 맥락이 빈약하면 agent는 평균으로 돌아간다. 반대로 맥락이 충분하면, agent는 가끔 디자이너가 예상하지 못한 좋은 변주를 만든다.

## 디자인은 더 소프트웨어가 되고, 소프트웨어는 더 개인화된다

이 영상의 인상적인 점은 “AI가 디자인을 잘한다”는 단순한 주장이 아니라, 디자인 작업 전체가 점점 소프트웨어화된다는 장면을 보여준다는 데 있다. shader는 이미지 효과가 아니라 조절 가능한 모델이 된다. 브랜드 카드는 파일이 아니라 생성기가 된다. 웹사이트는 사람용 화면과 agent용 markdown으로 나뉜다. feature request는 ticket이 아니라 “send to an agent”가 된다.

그래서 이 흐름을 따라가려면 새 툴 이름만 외우는 것으로는 부족하다. 더 중요한 것은 작업물을 남기는 방식이다. 내가 왜 이 느낌을 원하는지, 무엇을 피하고 싶은지, 어떤 예시가 좋은지, 어떤 문장을 계속 살려야 하는지를 기록해야 한다.

저는 이 영상이 AI 디자인의 현재를 꽤 정확히 보여준다고 봤다. 예쁜 결과물 하나보다 중요한 것은 **agent가 계속 일관된 취향으로 움직일 수 있게 만드는 기억과 조절 장치**다. 앞으로의 디자인 시스템은 색상표와 컴포넌트 라이브러리만이 아니라, `soul.md`, agent-readable docs, shader parameters, 생성 스크립트까지 포함하게 될 가능성이 높다.

AI로 디자인한다는 말은, 결국 이렇게 바뀌고 있다. “툴로 결과물을 만든다”에서 “맥락과 도구를 같이 만들어, 결과물이 계속 변할 수 있게 한다”로.

---

더 실습해보고 싶은 분들을 위한 참고 자료도 남겨둡니다. agent와 workflow를 실제로 굴려보는 관점에서는 코난쌤의 책 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902), 그리고 [AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)이 이어서 보기 좋습니다. 이 글에서 말한 `soul.md`, agent-readable docs, 반복 루프 설계 같은 주제와도 자연스럽게 연결됩니다.

## 원문

- Y Combinator, [YC's Head of Design Shows You How To Design With AI](https://www.youtube.com/watch?v=VbqaL_eHhKY), 2026-07-10.
- Paxel: <https://paxel.ycombinator.com>
- SOTA Zine: <https://www.sotazine.com>
- YC Startup School: <https://www.ycombinator.com/startupschool>
