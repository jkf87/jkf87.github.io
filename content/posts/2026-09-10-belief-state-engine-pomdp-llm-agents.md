---
title: "Belief-State Engine: LLM 에이전트에 POMDP 신념 상태를 외장으로 붙이기"
date: 2026-09-10T19:00:00+09:00
tags:
  - LLM에이전트
  - POMDP
  - 벨리프상태
  - 베이즈필터
  - 부분관측
draft: false
description: "LLM 에이전트가 부분 관측 환경에서 실패하는 구조적 원인을 원시 히스토리 조건부 정책에서 찾고, LLM 바깥에 베이즈 사후분포를 유지하는 Belief-State Engine(BSE)을 붙이면 Tiger POMDP에서 성공률 80%→95%로 오른다는 논문(arXiv 2609.10036)을 정리했습니다."
---

## 결론 먼저

논문 정보 정리.

- 제목: Belief-State Engine: Augmenting LLMs for Principled Planning Under Partial Observability
- 링크: https://arxiv.org/abs/2609.10036 (arXiv 2609.10036, 2026-09-09 공개, v1 기준일 2026-09-10)
- 주장: 현재의 LLM 에이전트는 <span style="background-color: #fff59d"><strong>원시 행동-관측 히스토리를 조건으로 하는 정책이며 숨은 상태에 대한 명시적 신념이 없다</strong></span>. 이것이 부분 관측 환경 실패의 구조적 원인이다.
- 제안: LLM 외부에 Belief-State Engine(BSE)을 배치하고 <span style="background-color: #fff59d"><strong>베이즈 사후분포만 LLM에 노출</strong></span>한다. 원시 히스토리는 프롬프트에 포함하지 않는다.
- 주요 결과: Tiger POMDP에서 <span style="background-color: #fff59d"><strong>성공률 80.0%에서 95.0%, 평균 할인 수익 -12.00에서 +3.06</strong></span> (N=40, gpt-4o, τ=0.3).

## 아키텍처

BSE는 환경과 LLM 사이의 추론 모듈이다. 각 스텝에서 환경의 관측을 받아 POMDP 모델 (T, Z)로 <span style="background-color: #fff59d"><strong>2단계 베이즈 필터(예측 단계, 관측 정정 단계)</strong></span>를 수행하고, 갱신된 신념을 직렬화기가 프롬프트로 변환해 LLM에 전달한다.

LLM은 ACTION 한 줄 형식으로 행동을 출력하고 파서가 이를 행동 공간의 원소로 변환한다. <span style="background-color: #fff59d"><strong>원시 행동-관측 트레이스는 결정 시점에 LLM에 노출되지 않는다</strong></span>.

![Fig. 1. BSE 제어 흐름](/images/2026-09-10-belief-state-engine-pomdp-llm-agents/fig-1-p7.png)

Fig. 1 출처: 논문 Fig. 1 (arXiv 2609.10036v1 p7).

직렬화기는 세 종류이다. 전체 상태를 확률과 함께 나열하는 테이블형, 상위 k개 상태만 보여주는 top-k형, 전체 지지집합을 확률 내림차순으로 정렬하는 형식이다. 어느 쪽이든 <span style="background-color: #fff59d"><strong>자유 서술은 포함하지 않으며 구조화된 수치 입력만</strong></span> 준다.

## 이론적 내용

논문은 신념-정합적 내부 상태의 최소 공리로 4개를 제시한다. A1 재귀 갱신 가능성, A2 예측 충분성, A3 상태 공간이 확률단체일 것, A4 정책이 신념 외의 히스토리 표면 특징을 참조하지 않을 것이다.

정리 2는 사후분포가 공리 A1-A3를 만족하는 표현 중 가장 굵은(coarsest) 표현임을, 정리 4는 표현을 사후분포로 고정하면 베이즈 갱신이 유일함을 보인다.

정리 9는 핵심 결과다. <span style="background-color: #fff59d"><strong>LLM+BSE 합성은 신념 MDP 위의 건전한 마르코프 정책이 되어 고전 POMDP 이론의 벨만 최적성 보장을 상속받는다</strong></span>. 결정 시점에 원시 트레이스를 노출하면 A4를 위반하여 보장이 무효가 된다.

## 실험 설정

두 환경에서 평가한다. 하나는 표준 Tiger POMDP(상태 2개, 관측 정확도 0.85, 정답 +10, 오답 -100, 듣기 -1, T=20, γ=0.95)이고, 다른 하나는 K개 호스트 노드의 이분 상태를 가진 레드팀 공격 그래프(K=6일 때 |S|=64, T=30, γ=0.95)이다.

베이스라인은 6개가 설계되었으나 실행된 것은 3개다. Reactive(최신 관측만), NL-Tracker(LLM이 자연어 신념을 유지), BSE가 그것이다. CoT, ReAct, QMDP, POMCP는 실행되지 않았다. 메인 비교 N=40, 절제 실험 N=25로 설계(N=300×3)보다 축소되었다.

## 결과

### Tiger POMDP

| 지표 (N=40) | Reactive | BSE | NL-Tracker |
| --- | --- | --- | --- |
| 성공률 | 32/40 (80.0%) | <span style="background-color: #fff59d"><strong>38/40 (95.0%)</strong></span> | 32/40 (80.0%) |
| 평균 할인 수익 [95% CI] | -12.00 [-25.75, 1.75] | <span style="background-color: #fff59d"><strong>+3.06 [-4.41, 8.24]</strong></span> | -12.00 [-25.75, 1.75] |
| 평균 listen 행동 수 | 0.00 | 1.45 | 0.00 |
| 평균 Brier 점수 | 0.325 | 0.234 | 0.500 |
| 에피소드당 평균 토큰 | 459 | 1,270 | 249 |

![Fig. 2. Tiger 메인 비교](/images/2026-09-10-belief-state-engine-pomdp-llm-agents/fig-2-p11.png)

Fig. 2 출처: 논문 Fig. 2 (p11).

BSE만 신뢰구간이 0을 제외한다. Reactive와 NL-Tracker는 첫 턴에 곧바로 문을 열어 관측 정확도에 상응하는 약 80% 성공률을 보인다. BSE는 <span style="background-color: #fff59d"><strong>평균 1.45회 관측 후 커밋</strong></span>한다.

자연어로 신념을 유지한 NL-Tracker는 Reactive와 결과가 동일했다. <span style="background-color: #fff59d"><strong>효과를 만든 것은 확률 벡터 형태의 신념이었고 자연어 신념은 아니었다</strong></span>.

![Fig. 3. Tiger 절제 실험](/images/2026-09-10-belief-state-engine-pomdp-llm-agents/fig-3-p11.png)

Fig. 3 출처: 논문 Fig. 3 (p11).

### 레드팀 공격 그래프

| 지표 (N=40) | Reactive | BSE | NL-Tracker |
| --- | --- | --- | --- |
| 평균 할인 수익 [95% CI] | -5.40 [-17.4, 7.0] | -2.80 [-16.0, 10.7] | +7.87 [-5.2, 21.1] |
| 침해 커버리지 | 32.5% | 42.1% | 40.8% |
| 첫 침해까지 평균 스텝 | 1.41 | 2.58 | 2.09 |
| 결정 일관성 JSD 중앙값 | 0.0 | 0.0 | 0.043 |

![Fig. 4. 공격 그래프 메인 비교](/images/2026-09-10-belief-state-engine-pomdp-llm-agents/fig-4-p12.png)

Fig. 4 출처: 논문 Fig. 4 (p12).

수익 차이는 통계적으로 구분되지 않는다. BSE는 <span style="background-color: #fff59d"><strong>침해 커버리지(42.1%)와 결정 일관성에서 최상위</strong></span>다. NL-Tracker의 자연어 신념 형식은 같은 사후분포를 가진 히스토리 쌍에서 다른 행동 분포를 내는 편차(JSD 중앙값 0.043)를 보였다.

### 절제 실험

![Fig. 5. 공격 그래프 절제 실험](/images/2026-09-10-belief-state-engine-pomdp-llm-agents/fig-5-p13.png)

Fig. 5 출처: 논문 Fig. 5 (p13).

관측 정정 제거(AB2) 시 <span style="background-color: #fff59d"><strong>신념이 균등 사전에 고정되어 오픈루프 동작</strong></span>이 된다(Tiger 성공률 4.0%, 공격 그래프 커버리지 26.7%). 예측 단계 제거(AB1)는 공격 그래프에서 거의 효과가 없었는데 이는 <span style="background-color: #fff59d"><strong>참조 환경의 전이 커널이 항등행렬인 미구현 플레이스홀더</strong></span>이기 때문이라고 논문이 명시한다.

## 한계

논문이 명시하는 한계는 다음과 같다. <span style="background-color: #fff59d"><strong>6개 베이스라인 중 3개만 실행</strong></span>되었고 CoT, ReAct, QMDP, POMCP 결과가 없다. 표본 크기가 설계보다 한 자리 작아 신뢰구간이 넓고 <span style="background-color: #fff59d"><strong>포인트 추정은 시사적(suggestive)으로 읽어야 한다</strong></span>.

gpt-4o가 동일 설정의 별도 호출에서 결정론적이지 않아 두 라이브 라운드 수치가 일치하지 않았다. 오픈 웨이트 복제는 실행되지 않았다. <span style="background-color: #fff59d"><strong>모델 (T, Z)이 오명세되면 보장이 사라진다</strong></span>.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### BSE가 LLM 에이전트에서 하는 일이 뭔가요?
LLM 바깥에서 POMDP 모델로 베이즈 필터를 돌려 숨은 상태의 사후분포를 계산하고, 그 사후분포만 매 스텝 LLM 프롬프트로 주입하는 추론 모듈입니다. 원시 행동-관측 히스토리는 프롬프트에 포함되지 않습니다.

### 성능이 얼마나 올랐나요?
Tiger POMDP에서 성공률 80.0%에서 95.0%, 평균 할인 수익 -12.00에서 +3.06입니다(N=40, gpt-4o, τ=0.3). 공격 그래프 과제에서는 수익 차이가 통계적으로 구분되지 않았습니다.

### CoT나 ReAct와 비교한 결과도 있나요?
아니요. 실행된 베이스라인은 Reactive, NL-Tracker, BSE 3개이며 CoT, ReAct, QMDP, POMCP는 설계에만 존재합니다. 라이브 API 예산(약 10^5 호출) 문제라고 논문이 명시합니다.

### 기존 에이전트 프레임워크에 어떻게 붙이나요?
POMDPModel 인스턴스와 도메인 헤더만 교체하면 필터, 직렬화기, LLM 인터페이스는 변경 없이 재사용됩니다. 참조 구현은 400줄 미만 파이썬 모듈입니다.

### 이 접근의 가장 큰 리스크는 뭔가요?
POMDP 모델 (T, Z)의 오명세입니다. 모델이 틀리면 <span style="background-color: #fff59d"><strong>벨만 최적성 보장이 사라지며</strong></span>, 논문은 모델이 아예 틀리면 어떤 보장도 살아남지 않는다고 명시합니다. BSE가 기록하는 영확률 관측 이벤트가 모델 오류의 진단 신호로 쓰입니다.
