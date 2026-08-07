---
title: "AgentOPSD: Agentic RL을 위한 재귀적 자기증류 턴별 크레딧 할당"
date: 2026-08-07
tags:
  - agent
  - reinforcement-learning
  - LLM
  - credit-assignment
  - self-distillation
  - GRPO
  - Bayesian
  - turn-level
  - agentic-RL
  - loop
authors:
  - conanssam
source: https://arxiv.org/abs/2608.05987
github: https://github.com/ZethWang/AgentOPSD
---

## 개요

AgentOPSD는 agentic reinforcement learning에서 턴별 크레딧 할당 문제를 해결하는 critic-free 방법이다. Tsinghua University, Zhejiang University, Meituan의 연구진이 2026년 8월에 발표했다.

핵심 기여는 token-level teacher-student log-probability gap을 turn-level evidence로 집계하고, 이를 Bayesian belief state에 재귀적으로 갱신하여 trajectory-level advantage를 턴별로 재분배하는 것이다.

## 배경

GRPO(Group Relative Policy Optimization)는 검증 가능한 보상(verifiable rewards)을 사용하는 RL 방법으로, trajectory-level advantage를 계산하여 궤적 내 모든 토큰에 균등하게 전달한다.

이 접근의 한계는 다음과 같다:

1. 궤적 내 개별 턴의 기여도를 구분할 수 없다
2. 호라이즌이 길어질수록 균등 할당의 비효율이 커진다
3. 성공한 궤적의 무의미한 행동도 보상을 받는다

## 방법론

### 턴별 증거 집계

privileged self-distillation을 사용하여 턴별 evidence를 계산한다. 동일한 모델 파라미터를 사용하되, teacher branch는 추가 컨텍스트(스킬 `c+`)를 받는다.

턴 k의 evidence:

```
e_k = Σ_t [log π(y_{k,t} | s_k, c+, y_{k,<t}) - log π(y_{k,t} | s_k, y_{k,<t})]
```

### 재귀적 벨리프 갱신

log-odds 공간에서 Bayesian belief를 재귀적으로 갱신한다:

```
B_0 = clip(R̄, ε, 1-ε)
c_k = γ·c_{k-1} + e_k
B_k = σ(logit(B_0) + c_k)
ΔB_k = B_k - B_{k-1}
```

여기서 R̄은 그룹 성공률, γ는 감쇠 계수, σ는 시그모이드 함수이다.

ΔB_k는 턴 k가 성공 확률에 대한 믿음을 얼마나 수정했는지를 나타낸다.

### Bounded Advantage Reshaping

trajectory-level advantage를 터별로 재분배한다:

```
q_k = sign(A_seq) · ΔB_k
z_k = (q_k - μ_q) / (σ_q + ε)
w_k = clip(1 + b·z_k, 1-b, 1+b)
Ã_k = A_seq · [(1-λ) + λ·w_k]
```

w_k는 [1-b, 1+b] 범위로 클리핑되어 GRPO의 안정성을 유지한다.

![Figure 1: 훈련 역학 및 호라이즌 robustness](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x1.png)

x1.png는 Figure 1 — 훈련 역학(검증 성공률, 호라이즌 민감도, 정책 엔트로피)입니다.

## 실험 결과

![Table 4: 환경별 훈련 설정](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x4.png)

세 환경에서 Qwen2.5 3B/7B 모델로 평가했다.

ALFWorld (Qwen2.5-7B):
- GRPO: 85.7%
- AgentOPSD: 89.1% (+3.4pp)

Search-QA (Qwen2.5-7B):
- GRPO: 42.8%
- AgentOPSD: 46.9% (+4.1pp)

WebShop (Qwen2.5-7B):
- GRPO: 61.6/56.8 (Score/Acc)
- AgentOPSD: 63.9/58.5

![Figure 2: 방법론 개요](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x2.png)

## 분석

### 호라이즌 효과

호라이즌이 긴 ALFWorld(평균 5-6턴)에서 개선이 크고, 짧은 Search-QA(4턴)에서는 개선이 작다. 이는 재귀 벨리프 갱신이 긴 궤적에서 더 큰 효과를 발휘함을 시사한다.

### Ablation

턴 경계 집계(aggregation)와 재귀 벨리프 갱신(recursive belief) 각각을 제거한 실험에서 두 구성 요소 모두 기여한다. 특히 재귀 벨리프가 호라이즌 robustness에 핵심 역할을 한다.

![Figure 3: 하이퍼파라미터 민감도 분석](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x3.png)

## 기존 방법과의 관계

| 방법 | 크리틱 | 추가 롤아웃 | 크레딧 단위 |
|---|---|---|---|
| PPO/GAE | 필요 | 아니오 | 스텝별 |
| VinePPO | 필요 | 필요 | 스텝별 |
| GRPO | 불필요 | 불필요 | 궤적 전체 |
| StepOPSD | 불필요 | 불필요 | 스텝별 (local) |
| AgentOPSD | 불필요 | 불필요 | 터별 (recursive) |

GiGPO는 환경 보상으로 스텝 어드밴티지를 추정하고, AgentOPSD는 self-distillation 증거를 사용하므로 상호 보완적이다.

## 코드

https://github.com/ZethWang/AgentOPSD

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
