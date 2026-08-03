---
title: "TAPO: 에이전트 RL에 전이 감독을 끼워넣는 가장 싼 방법"
date: 2026-08-04
tags:
  - agent
  - reinforcement-learning
  - LLM
  - post-training
  - transition-supervision
  - policy-optimization
  - agentic-RL
  - loop
---

![TAPO와 표준 agentic RL의 비교. 표준 RL은 보상 신호만 사용하고, TAPO는 전이 감독을 추가로 활용한다.](/images/2026-08-04-tapo-transition-aware-policy-optimization/fig-1-p2.png)

TAPO(Transition-Aware Policy Optimization, arXiv:2607.27973)는 LLM 에이전트의 강화학습 훈련에 전이 감독(transition supervision)을 교대로 적용하는 프레임워크이다. 추가 환경 상호작용, 전문가 데이터, 추론 시간 오버헤드 없이 WebShop과 ALFWorld에서 일관된 성능 향상을 달성했다.

---

## 배경

LLM 에이전트의 강화학습 포스트트레이닝에서 GRPO, GiGPO, RAGEN, ARPO 등의 방법이 제안되었다. 이 방법들은 에피소드 단위의 sparse reward로부터 궤적 수준 또는 스텝 수준 어드밴티지를 계산하여 정책을 최적화한다.

이론 연구(UNREAL, DeepMDP, SPR 등)에 따르면, 목표 지향적 다중 스텝 과제에서 일반화하려면 에이전트가 환경의 전이 역학(transition dynamics)을 암묵적으로 모델링해야 한다. 그런데 기존 agentic RL 방법은 이를 명시적으로 훈련하지 않는다.

TAPO는 온라인 RL 롤아웃에서 자연히 수집되는 $(s_t, a_t, s_{t+1})$ 튜플을 활용하여, 정책 최적화와 전이 감독을 번갈아 수행하는 방법을 제안한다.

---

## 방법

### 전이 신호 구성

에이전트가 환경과 상호작용하며 궤적 $\tau = \{(s_1, a_1, r_1), \ldots, (s_T, a_T, r_T)\}$를 생성한다. 각 스텝에서 환경 전이 $(s_t, a_t) \rightarrow s_{t+1}$을 관측할 수 있다. 이 튜플들은 추가 수집 없이 기존 롤아웃에서 직접 얻는다.

### 전이 감독 목적

전이 감독 손실은 다음 상태의 조건부 로그 가능도를 최대화한다:

$$\mathcal{L}_{\text{TS}}(\theta) = -\mathbb{E}_{(s_t, a_t, s_{t+1}) \sim \mathcal{D}} [\log p_\theta(s_{t+1} | s_t, a_t)]$$

teacher-forcing으로 다음 관측 토큰 시퀀스를 예측한다. 이 손실은 정책 최적화 목적과 백본 파라미터를 공유한다.

### 교대 학습

![TAPO의 전체 구조. 에이전트가 환경과 상호작용한 뒤, 롤아웃 데이터로 정책 학습과 전이 감독을 번갈아 수행한다.](/images/2026-08-04-tapo-transition-aware-policy-optimization/fig-2-p6.png)

정책 최적화 $I$회마다 전이 감독을 1회 수행한다. $I=4$가 기본값이며, 2~5 범위에서 안정적이다.

---

## 실험

### WebShop

![WebShop과 ALFWorld에서의 메인 결과. TAPO는 모든 모델 스케일과 RL 알고리즘에서 일관된 향상을 보인다.](/images/2026-08-04-tapo-transition-aware-policy-optimization/table-1-p6.png)

| 모델 | 방법 | 점수 | 성공률(%) |
|---|---|---|---|
| Qwen2.5-1.5B | GRPO | 75.8±3.5 | 56.8±3.8 |
| Qwen2.5-1.5B | TAPO-GRPO | 81.2±2.8 | 66.2±4.9 |
| Qwen2.5-1.5B | GiGPO | 83.5±1.8 | 67.4±4.5 |
| Qwen2.5-1.5B | TAPO-GiGPO | 86.5±2.0 | 71.7±3.3 |
| Qwen2.5-7B | GRPO | 79.3±2.8 | 66.1±3.7 |
| Qwen2.5-7B | TAPO-GRPO | 85.6±3.9 | 73.7±4.0 |
| Qwen2.5-7B | GiGPO | 86.2±2.6 | 75.2±3.8 |
| Qwen2.5-7B | TAPO-GiGPO | 89.0±3.2 | 77.9±3.7 |

### ALFWorld

Qwen2.5-7B 기준 TAPO-GiGPO는 93.6% 성공률을 달성했으며, 이는 Early Experience(82.8%), RWML(90.1%)보다 높다.

### 전이 모델링 분석

next-state perplexity 측정 결과, GRPO만 훈련한 모델은 환경 변화를 예측하지 못하는 반면, TAPO는 행동 결과를 정확히 예측한다.

### 교대 주기 민감도 분석

![교대 주기 I에 대한 민감도 분석. I=4에서 최적이며, 넓은 범위에서 안정적이다.](/images/2026-08-04-tapo-transition-aware-policy-optimization/table-3-p8.png)

---

## 한계

- GSM8K에서 도메인 외 능력 저하 관찰 (base 59.1% → GRPO 57.9% → TAPO-GRPO 56.5%)
- WebShop, ALFWorld 두 환경만으로 검증되어 일반성 확인 필요
- 교대 주기 $I$에 대한 민감도는 낮지만 최적값 탐색이 필요

---

## 기여 요약

TAPO는 기존 agentic RL 파이프라인에 전이 감독 교대 단계를 추가하는 것만으로, 추가 비용 없이 일관된 성능 향상을 달성했다. 롤아웃 데이터 재사용이라는 실용적 관점을 제시한 점이 주요 기여다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

---

> **원문**: [TAPO: Transition-Aware Policy Optimization for LLM Agents, arXiv:2607.27973](https://arxiv.org/abs/2607.27973)
