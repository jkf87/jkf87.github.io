---
title: "CAFE — 자기 개선 검색 에이전트는 피드백도 같이 진화해야 한다"
date: 2026-08-27
tags:
  - LLM
  - agent
  - search-agent
  - RL
  - self-improvement
  - credit-assignment
draft: false
---

## 결론 먼저

검색 에이전트를 강화학습으로 학습할 때, <span style="background-color: #fff59d"><strong>에이전트만 학습하면 성능이 특정 지점에서 멈춥니다</strong></span>. 피드백을 주는 비평가(critic) 역할도 같은 모델이 번갈아 학습해야 계속 성능이 오릅니다. CAFE(Coupled Agent–Feedback Evolution)는 이 공동 진화를 하나의 프레임워크로 정리한 논문입니다 (Fudan University + Tencent, arXiv:2608.24794).

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>같은 파라미터를 공유하는 모델 하나가 검색 에이전트 역할과 피드백 비평가 역할을 번갈아 수행</strong></span>하고, 온라인 RL과 오프라인 선호 최적화를 교대로 돌립니다.

7개 에이전트 검색 벤치마크에서 Qwen2.5-7B 기반으로 <span style="background-color: #fff59d"><strong>평균 EM 52.5</strong></span>를 달성해서, 가장 강한 RL 베이스라인 IGPO 대비 <span style="background-color: #fff59d"><strong>2.1 EM, 1.3 F1 앞섭니다</strong></span>. 답변 수준 환각률은 <span style="background-color: #fff59d"><strong>17.6%에서 12.6%로 떨어졌습니다</strong></span>.

## 문제 정의

결과 보상(outcome reward)으로만 학습한 검색 에이전트에는 두 한계가 있습니다.

첫 번째, <span style="background-color: #fff59d"><strong>최종 보상은 중간에 낸 실수의 위치를 알려주지 못합니다</strong></span>. 롤아웃이 실패해도 어느 검색 단계에서 방향이 틀렸는지 알 수 없습니다.

두 번째, 진행 중인 트라젝토리를 되돌릴 수 없습니다. 실수는 그대로 이후 단계 전체로 전파됩니다.

기존 연구가 정보 이득(information gain)이나 신뢰도 변화 같은 정밀한 크레딧 신호를 제안했지만, 이런 신호는 <span style="background-color: #fff59d"><strong>평가적(evaluative)일 뿐 교정적(instructive)이지 않다</strong></span>고 논문은 지적합니다.

## CAFE 설계

### 하나의 모델, 두 개의 역할

에이전트의 행동 공간에 `request_feedback` 행동을 추가합니다. <span style="background-color: #fff59d"><strong>에이전트는 스스로 판단해서 피드백을 요청</strong></span>하고, 같은 모델이 critic으로 전환해 교정 피드백을 생성합니다.

### 초기화: 실패에서 만든 회복 데이터

베이스 에이전트 자신의 실패 트라젝토리에서 복구 시연(recovery demonstration)을 만듭니다. <span style="background-color: #fff59d"><strong>실패한 프리픽스를 그대로 두고, 그 지점에 교정 피드백을 삽입하고, 성공한 이어지는 행동을 붙입니다</strong></span>. 이상적인 트라젝토리로 대체하는 게 아니라는 점이 중요합니다. 에이전트의 정책이 실제로 방문하는 상태에서 피드백을 요청·생성·활용하는 법을 배웁니다.

이 초기화만으로 백본 평균이 <span style="background-color: #fff59d"><strong>38.1/47.9 (EM/F1)에서 40.8/50.1로 올라갑니다</strong></span>.

### 온라인 RL: CFE와 어드밴티지 셰이핑

- 비교 피드백 추정(CFE, Comparative Feedback Estimate): 같은 프롬프트에 대해 <span style="background-color: #fff59d"><strong>피드백 요청을 포함한 롤아웃과 생략한 롤아웃의 성공률 차이(call–skip success gap)</strong></span>로 피드백 요청의 반환값을 계산합니다. 중복 요청에는 비용을 부과합니다.
- 피드백 인지 어드밴티지 셰이핑: <span style="background-color: #fff59d"><strong>피드백 전후 토큰의 어드밴티지를 다르게 재가중</strong></span>합니다. 학습 후반에는 피드백 이전 토큰의 어드밴티지가 0 근처로 모이고 이후 토큰은 양의 방향으로 이동합니다. 구출된 트라젝토리와 처음부터 완벽한 트라젝토리에 같은 보상을 주는 크레딧 문제를 푸는 장치입니다.

### 오프라인: RDPO

롤아웃 유도 선호 최적화(RDPO, Rollout-Derived Preference Optimization)는 <span style="background-color: #fff59d"><strong>최신 온라인 롤아웃에서 프리픽스가 매칭된 성공/실패 쌍을 채굴</strong></span>해 선호 쌍으로 학습합니다. 결과 혼란(outcome confounding)을 줄이고, critic이 진화하는 에이전트와 정렬된 상태를 유지하게 합니다.

## 결과

### 메인 테이블

![Table 1: seven agentic SearchQA benchmarks main results](/images/2026-08-27-cafe-co-evolving-feedback-search-agent/fig-table1-main-results.png)

2WikiMultihopQA를 인도메인으로 학습하고 HotpotQA, MuSiQue, PopQA, Bamboogle, NQ, TriviaQA 6개를 아웃도메인으로 평가했습니다.

| 단계 | 평균 EM | 평균 F1 |
|---|---|---|
| Qwen2.5-7B 백본 | 38.1 | 47.9 |
| 피드백 SFT | 40.8 | 50.1 |
| GRPO | 49.7 | 58.0 |
| CAFE | 52.5 | 60.7 |

GRPO 대비 <span style="background-color: #fff59d"><strong>모든 벤치마크에서 두 지표가 모두 개선</strong></span>됐고, 6개 아웃도메인 전체에서 이득이 유지됩니다. Search-R1 대비로는 <span style="background-color: #fff59d"><strong>멀티홉 4개 벤치마크에서 7.4 EM, 5.9 F1</strong></span>, 싱글홉 3개에서 1.3 EM, 1.3 F1 향상이라서 멀티홉에서 이득이 큽니다. 이건 설계 의도와 일치합니다. 중간 검색 오류가 이후 검색 단계로 번지기 전에 잡는 구조라서 긴 트라젝토리에서 이득이 커집니다.

3B 스케일에서도 같은 경향이 재현됐고, <span style="background-color: #fff59d"><strong>BrowseComp-Plus 같은 롱호라이즌 딥리서치 설정에서도 각 학습 단계마다 성능이 올라갑니다</strong></span>.

### 편향 제거: 한쪽만 학습하면 멈춘다

![Figure 3: agent-critic cross-play](/images/2026-08-27-cafe-co-evolving-feedback-search-agent/fig3-crossplay.png)

핵심 결과는 소거 실험(ablation)입니다. 2Wiki에서 <span style="background-color: #fff59d"><strong>에이전트만 학습하면 84.2에서 정점을 찍고 멈춥니다</strong></span>. 피드백 모델만 학습하면 67.7에서 71.3까지밖에 못 갑니다. 둘을 교대로 학습하면 계속 올라갑니다.

크로스플레이 분석도 같은 결론을 보여줍니다. <span style="background-color: #fff59d"><strong>초기 에이전트는 초기 critic과, 후기 에이전트는 후기 critic과 짝일 때 성능이 가장 좋습니다</strong></span>. 즉 정책과 피드백이 서로 맞춰 진화했다는 뜻입니다.

### 환각 감소

![Figure 4: hallucination analysis](/images/2026-08-27-cafe-co-evolving-feedback-search-agent/fig4-hallucination.png)

답변에 검색 트라젝토리 근거로 뒷받침되지 않는 주장이 하나라도 있으면 환각으로 판정했습니다.

| 모델 | 평균 환각률 |
|---|---|
| 베이스 | 29.9% |
| GRPO | 17.6% |
| CAFE | 12.6% |

GRPO 대비 모든 벤치마크에서 감소했고, <span style="background-color: #fff59d"><strong>NQ에서 10.8%p, MuSiQue에서 9.4%p 감소가 가장 컸습니다</strong></span>.

### 온라인 구성요소 소거

CFE 단독은 49.7/58.0에서 50.8/58.4로 이득이 작습니다. 어드밴티지 셰이핑이 51.2/59.4까지 끌어올리고, 둘 다 쓰면 51.9/60.3으로 모든 벤치마크에서 개선됩니다.

## 내 해석

이 논문의 기여는 개별 기법보다 문제 정식화에 가깝습니다. 자기 개선(self-improvement)을 <span style="background-color: #fff59d"><strong>"정책과 정책을 안내하는 피드백의 결합 학습 문제"로 재정의</strong></span>했습니다. 정적 critic은 진화하는 정책과 어긋나고, 정책만 학습하면 plateau에 닿는다는 건 RL 에이전트 전반에 적용되는 구조적 관찰입니다.

실무 관점에서 눈여겨볼 점 두 가지.

- <span style="background-color: #fff59d"><strong>학습 데이터를 에이전트 자신의 실패 트라젝토리에서 만든다는 아이디어</strong></span>는 도메인 특화 에이전트 파인튜닝에 바로 옮겨질 수 있습니다. 완벽한 시연을 모으는 것보다 실패 복구 쌍을 만드는 게 쌉니다.
- call–skip success gap은 <span style="background-color: #fff59d"><strong>별도 보상 모델 없이 프롬프트 수준 비교만으로 개입 가치를 측정</strong></span>합니다. 피드백 요청이 실제로 도움이 되는지 A/B로 측정하는 셈이라 다른 개입형 도구 호출에도 재사용 가능한 패턴입니다.

한계도 있습니다. shared-parameter 구조라 역할 충돌 가능성이 있고, <span style="background-color: #fff59d"><strong>논문은 Qwen2.5 7B/3B만 평가했습니다</strong></span>. 더 큰 백본에서 co-evolution 이득이 유지되는지는 미확인입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: [CAFE: Self-Improving Search Agents Need Co-Evolving Feedback (arXiv:2608.24794)](https://arxiv.org/abs/2608.24794)
- 베이스라인: Search-R1, R-Search, IGPO, StepSearch, WebSeer
- 백본: Qwen2.5-7B/3B-Instruct
