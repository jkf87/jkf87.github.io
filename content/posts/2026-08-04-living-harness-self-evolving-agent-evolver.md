---
title: "Living-Harness: 에이전트 하네스가 실패에서 스스로 배우는 방법"
date: 2026-08-04
draft: false
summary: "완료된 에피소드의 실패를 하네스 상태에 영구 저장해서 다음 에피소드에서 반복하지 않는 프레임워크"
tags:
  - agent
  - harness
  - LLM
  - self-evolution
  - memory
  - interactive-agent
  - loop
  - automation
authors:
  - conanssam
---

에이전트가 같은 실수를 반복하는 현상, 처음 보는 건 아닙니다. Reflexion이든 뭐든 피드백을 주면 그 순간은 고치는데, 다음 에피소드에서 또 같은 실패가 나타납니다. 왜 그럴까요? 교훈이 에피소드와 함께 사라지니까요.

Living-Harness는 여기서 출발합니다. "실패에서 배운 것을 하네스에 영구 저장하자." 단, 모호한 텍스트 교훈이 아니라 실행 가능한 절차—트리거 조건, 필요한 도구 액션, 상태 전이—로 저장하자는 거죠.

논문: [Living-Harness Is an Interactive-Agent Evolver](https://arxiv.org/abs/2607.26598)

## 정적 하네스와 진화 하네스

![](/images/2026-08-04-living-harness-self-evolving-agent-evolver/fig-1-p1.png)

기존 하네스는 배포하면 끝입니다. 도구, 프롬프트, 메모리 구조가 고정되어 있죠. Living-Harness는 이걸 두 영역으로 나눕니다.

고정 영역은 도구, 기본 컨텍스트, 도메인 규칙입니다. 여기는 손대지 않습니다.

진화 영역은 에피소드 메모리와 상태 그래프입니다. 에피소드가 끝날 때마다 업데이트됩니다.

핵심은 도구와 컨텍스트를 얼려둔 채로 절차적 수리만 축적한다는 점입니다. 무분별한 자기수정이 아니라 제약된 진화입니다.

## 어떻게 동작하나

![](/images/2026-08-04-living-harness-self-evolving-agent-evolver/fig-2-p3.png)

rollout–evaluate–update 루프를 돕니다.

1. 현재 작업에 맞는 메모리/그래프 항목을 검색
2. 에이전트가 환경과 상호작용 (이때 하네스 상태는 고정)
3. 에피소드 종료 후 평가
4. Evolution-SOP가 실패를 구조화된 증거로 변환
5. 메모리와 그래프에 커밋 (다음 에피소드부터 적용)

Evolution-SOP는 도메인 수준의 고정된 프로토콜입니다. 단순한 자기비판이 아니라 도메인 제약 아래에서 어떤 수리를 받아들일지 판단합니다.

## 성능 검증

### τ²-Bench

| 모델 | 평균 Pass@1 |
|---|---|
| Gemini 3 Pro | 82.92 |
| Reflexion (GPT-5.2) | 73.02 |
| **Living-Harness (GPT-5.2)** | **83.09** |

GPT-5.2 기반인데 Gemini 3 Pro를 넘습니다.

### MultiWOZ-2.4

| 모델 | 평균 |
|---|---|
| ReasoningBank | 55.59 |
| **Living-Harness** | **65.50** |

특히 멀티 도메인 작업에서 강합니다. 절차 수리가 도메인 경계를 넘어 전이되는 효과입니다.

### 진화 사이클별로 보면

![](/images/2026-08-04-living-harness-self-evolving-agent-evolver/table-2-p6.png)

첫 진화 사이클에서 폭발적 개선이 일어나고, 그 후로는 정제 단계입니다. 이건 초기에 누락된 워크플로우 단계를 수리하고, 후속으로는 세밀한 조정이 이루어진다는 해석과 맞습니다.

## 컴포넌트 제거 실험

![](/images/2026-08-04-living-harness-self-evolving-agent-evolver/fig-3-p6.png)

제거 실험에서 Evolution-SOP를 빼면 83.09 → 73.38로 가장 큰 하락이 옵니다. 메모리나 그래프를 붙이기만 해서는 안 되고, 구조화된 후해석과 검증된 커밋 게이트가 필요하다는 뜻입니다.

## 크로스 모델 전이

![](/images/2026-08-04-living-harness-self-evolving-agent-evolver/table-3-p6.png)

GPT-5.2로 진화시킨 하네스 상태를 Gemini 3 Pro, GLM-5, Qwen3-max, Kimi-k2에 검색만으로 전이합니다. 추가 학습 없이요.

Taxi 도메인에서 GLM-5/Qwen3-max/Kimi-k2가 0점에서 43~45점으로 올라갑니다. 강한 모델인 Gemini 3 Pro도 개선됩니다. 하네스 상태가 모델에 종속되지 않는다는 증거입니다.

## 케이스 스터디: transfer_to_human_agents()

Telecom 도메인에서 사용자를 휴먼 에이전트에게 전환해야 하는 상황이 있습니다. Reflexion은 매번 "전환해야 한다"고 교훈을 만드는데 정작 `transfer_to_human_agents()`를 안 부릅니다.

Living-Harness는 이걸 두 형태로 저장합니다:
- 메모리: "사용자가 전환을 요청하면 transfer_to_human_agents() 호출"
- 그래프: "terminal-suspension 상태 → transfer_to_human_agents() 전이"

다음 사이클에서 한 번에 성공합니다. "알겠다"와 "실행한다"의 차이입니다.

## 결론

Living-Harness가 보여주는 것은 명확합니다. 에이전트 시스템에서 "다음 응답을 개선하는 것"과 "미래 작업의 절차를 개선하는 것"은 다른 문제입니다. 후자를 해결하려면 실패를 실행 가능한 절차로 저장하고, 제약 아래에서 진화시키고, 다른 모델에도 전이할 수 있게 만들어야 합니다. 그리고 그건 모델을 바꾸지 않고도 할 수 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
