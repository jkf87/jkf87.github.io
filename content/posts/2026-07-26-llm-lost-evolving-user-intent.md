---
title: "GPT-5.5도 의도가 6번만 바뀌면 무너짐 — 진화하는 사용자 의도 추적 실험"
slug: 2026-07-26-llm-lost-evolving-user-intent
date: 2026-07-26T07:00:00+09:00
draft: false
description: "단일 턴 벤치마크 99%가 의도 전환 6회 만에 80%로 추락함. 정적 평가가 못 보는 에이전트 약점과 의도 상태를 명시적으로 관리해야 하는 이유를 정리함."
tags:
  - LLM
  - agent
  - evaluation
  - multi-turn
  - user-intent
  - harness
  - Microsoft
  - benchmark
authors:
  - jkf87
showToc: true
TocOpen: false
hideSummary: false
searchHidden: false
ShowReadingTime: true
ShowBreadCrumbs: true
ShowPostNav: true
ShowWordCount: true
ShowRssButtonInSectionTermList: true
UseHugoToc: true
cover:
  image: "/images/2026-07-26-llm-lost-evolving-user-intent/fig-1-p1.png"
  alt: "LLMs get lost in evolving user intent - GPT-5.5 성능 추락 그래프"
  relative: false
  hidden: false
---

사용자가 대화하면서 요구를 바꾸는 건 예외가 아니라 일상임. 근데 그 상황에서 모델이 얼마나 무너지는지 정적 벤치마크는 전혀 못 봄. Microsoft Research가 그 빈틈을 측정했음. 원문은 [arXiv:2607.20734](https://arxiv.org/abs/2607.20734).

1. 배경. 기존 평가는 단일 턴이 전제임. 처음부터 정보가 다 주어지고 한 번에 답함. GSM8K(초등 수학 문제 벤치마크), SWE-Bench(실제 GitHub 이슈를 해결하는 코드 작성 벤치마크), BIRD-SQL(실무형 데이터베이스에서 SQL을 작성하게 하는 벤치마크) 전부 이 구조임. 근데 실제 사용자는 "뉴욕 식당 찾아줘" → "난 비건이야" → "브루클린으로 바꿔줘" → "그냥 예약해줘"처럼 대화하면서 의도를 만들어감. 점진적 공개, 정정, 작업 전환 세 가지 패턴이 계속 섞임.

![의도 전환에 따른 성능 추락](/images/2026-07-26-llm-lost-evolving-user-intent/fig-1-p1.png)

![](/images/2026-07-26-llm-lost-evolving-user-intent/gifs/user-indecisive.gif)

2. 방법론이 영리함. 기존 벤치마크를 버리지 않음. 원본 정답을 마지막 턴의 앵커로 두고 거슬러 올라가며 그럴듯한 이전 대화를 합성한 뒤, 의도 전환을 스케줄링해서 각 턴에 배분함. 채점은 원본 검증기를 그대로 씀. 추가 어노테이션 없이 GSM8K·BIRD-SQL·BrowseComp+(웹을 검색해야만 풀 수 있는 질문 벤치마크)·SWE-Bench를 다중 턴 시나리오로 변환함. 이 역공학 구조 자체가 내 평가 파이프라인에 차용할 만함.

![다중 턴 변환 파이프라인](/images/2026-07-26-llm-lost-evolving-user-intent/fig-2-p3.png)

![](/images/2026-07-26-llm-lost-evolving-user-intent/gifs/wait-hold-on.gif)

3. 결과가 충격적임. GPT-5.5가 GSM8K에서 99.0%에서 80.5%로, 의도 전환 6회 만에 18.7%p 하락함. GPT-5.1은 SWE-Bench에서 72.0%에서 0.0%로 붕괴함. DeepSeek V3.2는 BrowseComp+에서 58.3%, Mistral Large 3은 70.6% 하락함. 모든 모델이, 모든 도메인에서, 무너졌음.

4. 전환 유형 중 정정(revision)이 가장 치명적이었음. "뉴욕"을 "브루클린"으로 바꿔달라는 요청에 모델은 이전 턴의 의도에서 멀어지지 못함. 턴이 진행돼도 초기 의도 근처에 계속 머무는 편향이 측정됐음. 한 번 들은 정보를 고치지 못한다는 뜻임.

![모델별 성능 하락 폭](/images/2026-07-26-llm-lost-evolving-user-intent/fig-4-p6.png)

5. 완화 전략 실험도 시사하는 바가 큼. 전체 히스토리 유지는 약간 도움, 매 턴 요약은 그보다 낫고, 의도 상태를 명시적으로 추적하는 외부 메모리가 가장 효과적임. 근데 그것도 정적 성능에는 못 미침. 현재 알려진 어떤 메모리 기법도 "사용자가 처음부터 다 말해주는 것"을 대체하지 못한다는 결론임.

6. 그래서 내 하네스에 붙인 조치. 첫째, "사용자가 지금 무엇을 원하는가"를 컨텍스트 윈도우에 암묵적으로 맡기지 않고 별도의 의도 상태 파일로 명시적으로 관리함. 정정이 들어오면 이전 값을 지우고 현재 유효한 요구사항만 남김. 둘째, 긴 세션에서는 각 턴 시작 시 현재 의도를 재확인하게 프롬프트를 고정함. 7턴쯤 가면 대부분의 모델이 현재 의도를 놓친다는 측정이 있어서임.

7. 메모리와 의도 추적은 다른 문제라는 점이 핵심 통찰임. 요약 메모리는 대화 내용을 압축할 뿐 "현재 유효한 의도 상태"를 유지하지 않음. 의도를 잃은 에이전트는 잘못된 도구를 부르고 불필요한 컨텍스트를 쌓고 사용자가 원하지 않는 행동을 실행함. 도구 선택·컨텍스트 관리·가드레일 전부 의도 추적 위에 서 있음.

8. 문제제기. 이전 대화를 합성으로 만들기 때문에 실제 사용자 대화의 잡음(오타, 비일관성, 감정)과 분포가 다를 수 있음. 그래도 방향은 명확함. 배포 결정을 정적 점수로 하면 안 되고, 진화하는 의도 평가를 통과 못 하는 모델은 프로덕션에 넣으면 안 됨.

9. 결론. "LLM이 강력하다"는 말은 "처음부터 완벽하게 지시받았을 때만" 성립함. 실제 사용자는 완벽하지 않음. 에이전트 설계에서 의도 추적을 1급 시민으로 올리는 게 이 논문의 요구임. 코드는 [github.com/microsoft/evolving-intent](https://github.com/microsoft/evolving-intent)에 공개돼 있어서 내 에이전트를 직접 돌려볼 수 있음.

의도 상태 관리 같은 하네스 설계 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 다뤄볼 수 있음.
