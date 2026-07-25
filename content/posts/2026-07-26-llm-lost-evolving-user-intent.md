---
title: "LLMs Get Lost in Evolving User Intent"
slug: 2026-07-26-llm-lost-evolving-user-intent
date: 2026-07-26T07:00:00+09:00
draft: false
description: "GPT-5.5가 6번의 의도 전환만에 수학 99%→80%로 추락한다. Microsoft Research가 밝혀낸, 정적 벤치마크가 보지 못하는 에이전트의 치명적 약점."
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

## 요약: 에이전트는 "대화 속에서 변하는 사용자"를 따라가지 못한다

Microsoft Research의 Jihoon Tack, Philippe Laban, Jennifer Neville는 LLM 에이전트의 가장 근본적인 능력 — **"사용자가 대화하면서 바꾸는 의도를 추적하고 그에 맞춰 행동하는 것"** — 을 정밀하게 측정하는 프레임워크를 제안했다.

결론은 단순하고 충격적이다:

> **정적(single-turn) 벤치마크에서 99%를 받은 모델도, 사용자 의도가 6번만 바뀌면 80% 이하로 추락한다.**

이 문제는 기존 어떤 벤치마크도 잡아내지 못하는 **보이지 않는 결함**이다.

![](/images/2026-07-26-llm-lost-evolving-user-intent/fig-1-p1.png)

## 문제: 벤치마크는 "처음부터 다 정해진 질문"을 가정한다

현재 LLM 평가의 대부분은 단일 턴(single-turn)이다. 처음부터 모든 정보가 주어지고, 모델은 한 번에 답한다. GSM8K, SWE-Bench, BIRD-SQL 전부 이 구조다.

하지만 실제 사용자-에이전트 상호작용은 완전히 다르다:

1. **점진적 공개 (Argument Reveal)**: "뉴욕 식당 찾아줘" → "난 비건이야"
2. **정정 (Argument Revision)**: "뉴욕"이라고 했는데 → "브루클린으로 바꿔줘"
3. **작업 전환 (Function Switch)**: "식당 찾기" → "그 식당 예약해줘"

사용자는 처음부터 완벽한 지시를 주지 않는다. 대화하면서 **의도를 만들어간다.**

![](/images/2026-07-26-llm-lost-evolving-user-intent/fig-2-p3.png)

## 방법론: 단일 턴 벤치마크를 다중 턴으로 "역공학"하다

연구팀의 핵심 통찰은 **기존 벤치마크를 버릴 필요가 없다**는 것이다. 대신:

1. 원본 데이터의 정답을 **마지막 턴의 앵커(anchor)**로 둔다
2. 그 앵커로 거슬러 올라가며, **그럴듯한 이전 대화**를 합성한다
3. 의도 전환(reveal, revision, switch)을 스케줄링하여 각 턴에 배분한다
4. 원본 데이터셋의 검증기(verifier)를 그대로 사용해 최종 답을 채점한다

![](/images/2026-07-26-llm-lost-evolving-user-intent/fig-3-p4.png)

이렇게 하면 **추가 어노테이션 없이** 기존 벤치마크를 다중 턴 진화 의도 시나리오로 변환할 수 있다. 연구팀은 GSM8K(수학), BIRD-SQL(데이터베이스), BrowseComp+(검색), SWE-Bench Verified(코딩) 4개 도메인에 이 프레임워크를 적용했다.

## 결과: 모든 모델이, 모든 도메인에서, 무너졌다

### 헤드라인 숫자

| 모델 | 도메인 | Single → Evolve (6회 전환) | 변화 |
|---|---|---|---|
| GPT-5.5 | GSM8K (수학) | 99.0% → 80.5% | **-18.7%** |
| GPT-5.5 | SWE-Bench (코딩) | 86.0% → 80.0% | -7.0% |
| GPT-5.1 | SWE-Bench (코딩) | 72.0% → 0.0% | **-100%** |
| DeepSeek V3.2 | BrowseComp+ (검색) | 36.0% → 15.0% | **-58.3%** |
| Mistral Large 3 | BrowseComp+ (검색) | 17.0% → 5.0% | **-70.6%** |
| Kimi K2.5 | GSM8K (수학) | 97.0% → 75.5% | **-22.2%** |

GPT-5.1과 Grok 4.20은 SWE-Bench에서 **0%**로 붕괴했다. 6번의 의도 전환만에 코딩 능력이 완전히 무너진 것이다.

### 의도 전환 유형별 영향

![](/images/2026-07-26-llm-lost-evolving-user-intent/fig-4-p6.png)

세 가지 전환 유형 중 **정정(revision)**이 가장 치명적이다. 모델은 한 번 들은 정보를 고치지 못한다. 특히 인수 개수가 늘어날수록, 전환 횟수가 많아질수록 정확도는 단조롭게 하락한다.

### 이전 의도에서 멀어지지 못한다

![](/images/2026-07-26-llm-lost-evolving-user-intent/fig-5-p7.png)

모델이 이전 턴의 의도에 얼마나 편향되어 있는지를 측정한 그래프다. 턴이 진행될수록 모델은 **초기 의도에서 멀어지지 않고 그 자리에 머무른다.** 사용자가 "브루클린으로 바꿔줘"라고 해도, 모델은 여전히 "뉴욕" 근처를 맴도는 것이다.

### 메모리 메커니즘은 도움이 되지만…충분하지 않다

![](/images/2026-07-26-llm-lost-evolving-user-intent/fig-6-p8.png)

연구팀은 세 가지 완화 전략을 테스트했다:

- **Full History**: 전체 대화 기록 유지 — 약간 도움
- **Summary**: 매 턴 요약 — Full History보다 낫지만 여전히 큰 격차
- **Explicit Memory**: 의도 상태를 명시적으로 추적하는 외부 메모리 — 가장 효과적이지만, **정적 성능에는 여전히 미치지 못함**

즉, 현재 알려진 어떤 메모리 기법도 "사용자가 처음부터 다 말해주는 것"을 대체하지 못한다.

### 턴별 의도 추적 성능

![](/images/2026-07-26-llm-lost-evolving-user-intent/table-3-p8.png)

턴이 진행될수록 현재 의도를 정확히 식별하는 능력이 지속적으로 저하된다. 7턴째가 되면 대부분의 모델이 현재 사용자가 원하는 것을 놓친다.

## 핵심 통찰: 에이전트 설계가 바뀌어야 한다

이 연구가 에이전트 설계에 시사하는 바는 명확하다:

1. **정적 벤치마크 점수는 에이전트 배포 결정의 근거가 될 수 없다.** SWE-Bench 86%가 진짜 실력이라도, 사용자가 6번 요구사항을 바꾸면 80%로 떨어진다.

2. **의도 추적(intent tracking)은 1급 시민이 되어야 한다.** 현재 하네스 설계에서 "사용자가 지금 무엇을 원하는가"는 암묵적으로 컨텍스트 윈도우에 맡겨진다. 이 논문은 그 신뢰가 얼마나 위험한지 보여준다.

3. **메모리 ≠ 의도 추적.** 요약이나 요약 메모리는 대화 내용을 압축할 뿐, "현재 유효한 의도 상태"를 유지하지 않는다. 에이전트에게는 *상태 추적 메커니즘*이 별도로 필요하다.

4. **"진화하는 의도"는 도구 선택, 컨텍스트 관리, 안전 가드레일 모두에 영향을 미친다.** 의도를 잃은 에이전트는 잘못된 도구를 부르고, 불필요한 컨텍스트를 쌓고, 사용자가 원하지 않는 행동을 실행한다.

## 더 실습해보고 싶은 분들께

에이전트가 사용자 의도를 추적하지 못하는 문제는, 하네스 설계와 루프 엔지니어링에서 가장 먼저 다뤄야 할 주제 중 하나입니다. 실제 에이전트 루프에서 의도 상태를 어떻게 명시적으로 관리할 수 있는지, 컨텍스트 전환에 강건한 하네스를 어떻게 만드는지 더 깊이 실습해보고 싶다면 다음 두 가지를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 마무리

"LLM이 강력하다"는 이제 상식이다. 하지만 이 논문이 보여주는 것은, 그 강력함이 **"처음부터 완벽하게 지시받았을 때만"** 발휘된다는 것이다. 실제 사용자는 완벽하지 않다. 말을 바꾸고, 요구사항을 추가하고, 아예 다른 일을 하자고 한다.

이 연구가 제안하는 프레임워크는 기존 벤치마크를 그대로 재활용하면서도, 이 "보이지 않는 결함"을 정량적으로 측정할 수 있게 해준다. 에이전트를 만드는 사람이라면, 이 평가를 통과하지 못하는 모델을 절대 프로덕션에 배포해서는 안 된다.

> **논문:** [LLMs Get Lost in Evolving User Intent (arXiv:2607.20734)](https://arxiv.org/abs/2607.20734)
> **코드:** [github.com/microsoft/evolving-intent](https://github.com/microsoft/evolving-intent)
> **저자:** Jihoon Tack, Philippe Laban, Jennifer Neville (Microsoft Research)
