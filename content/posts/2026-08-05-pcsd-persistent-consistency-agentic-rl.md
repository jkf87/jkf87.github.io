---
title: "PCSD: 에이전트 RL에서 교사 신호를 토큰별로 신뢰하는 방법"
date: 2026-08-05
tags:
  - agent
  - reinforcement-learning
  - LLM
  - self-distillation
  - agentic-RL
  - credit-assignment
  - GRPO
  - loop
draft: false
---

에이전트 강화학습에서 가장 큰 문제는 보상이 희소하다는 겁니다. 수십 턴에 걸친 궤적 끝에 성공/실패 하나만 돌아오는데, 그 사이 어떤 토큰이 도움이 됐는지 알기 어렵습니다. PCSD(Persistent Consistency Self-Distillation)는 이 문제를 토큰 수준에서 푸는 방법입니다.

핵심은 이겁니다: privileged teacher가 학생 에이전트가 생성한 토큰에 대해 높은 확률을 할당하는 구간이 주변 토큰들까지 일관되게 지속되면, 그 신호를 신뢰하고 증류 가중치를 높입니다. 반대로 고립된 점 하나만 높으면 노이즈로 판단하고 무시합니다.

## 문제 설정

멀티턴 에이전트 RL에서 궤적 하나에 보상이 하나씩 떨어집니다. GRPO는 그룹 내 상대적 보상으로 advantage를 만들지만, 궤적 내 모든 토큰에 같은 advantage를 줍니다. 어떤 액션이 성공에 기여했는지 구분이 안 됩니다.

기존 self-distillation 방법(OPSD, SDAR, RLSD)은 teacher에게 privileged context(스킬, 정답 등)를 주고 학생 토큰을 평가합니다. 근데 teacher가 모든 토큰에서 똑같이 신뢰할 수 있는 건 아닙니다. 토큰 하나하나 따져보면 teacher의 판단이 들쭉날쭉합니다.

## PCSD의 세 가지 메커니즘

![](/images/2026-08-05-pcsd-persistent-consistency-agentic-rl/fig-2-p4.png)

그림 2가 전체 프레임워크입니다. 학생이 궤적을 만들고, frozen teacher가 학생 토큰을 평가합니다. 그 다음 세 단계를 거칩니다.

**1. Adaptive Aggregation** — teacher-student log-prob gap을 로컬 윈도우에서 모아서 봅니다. 짧은 윈도우(N=1)와 긴 윈도우(N=8)를 쓰는데, 지역 분산이 낮으면 짧은 윈도우로 세밀하게, 높으면 긴 윈도우로 평탄하게 만듭니다. 중간 값은 연속 보간합니다.

**2. Trend Modulation** — 윈도우 내에서 teacher 지지가 감소 추세면 가중치를 깎습니다. OLS 기울기를 구해서 음수 방향으로 떨어지면 `η = 1 - γ·ReLU(-slope/scale)`로 감쇠합니다. 양수 방향으로는 증폭하지 않습니다. 감소하는 신호만 약화시키는 단방향 설계입니다.

**3. Continuous Gating** — 최종 가중치를 sigmoid로 매핑합니다. `w = σ(β·δ_adaptive)·η`. 게이트 비율은 20%–28% 정도의 토큰이 0.5 이상의 가중치를 받습니다. 하드 셀렉션이 아니라 연속 분배입니다.

## 학습 목표

PCSD 손실을 GRPO와 결합합니다.

```
L_total = L_GRPO + λ_PCSd · L_PCSd
```

λ=0.01이 최적이었습니다. 0.05로 올리면 teacher 신호가 너무 강해져서 RL 탐색이 약해집니다.

![](/images/2026-08-05-pcsd-persistent-consistency-agentic-rl/fig-3-p7-1.png)

그림 3은 학습 중 teacher-student gap과 게이트 활성 비율입니다. 학습이 진행될수록 gap이 상승합니다. 학생이 teacher에게 가까워지고 있다는 뜻입니다.

## 결과

ALFWorld 기준 Qwen2.5-3B-Instruct 사용 시:

| 방법 | Overall |
|---|---|
| GRPO | 75.0% |
| GRPO+OPSD | 81.2% |
| SDAR | 84.4% |
| **PCSD** | **90.6%** |

GRPO 대비 +15.6pp, 가장 강력한 경쟁자 SDAR 대비 +6.2pp입니다.

![](/images/2026-08-05-pcsd-persistent-consistency-agentic-rl/fig-1-p2.png)

WebShop에서도 Score 85.0으로 최상위권입니다. unseen 환경에서도 86.7%로 GRPO(70.9%)와 SDAR(72.7%)을 크게 앞섭니다.

## 컴포넌트별 기여

![](/images/2026-08-05-pcsd-persistent-consistency-agentic-rl/table-2-p7-3.png)

적응 집계를 빼면 82.8%, 트렌드 변조를 빼면 83.6%, 감쇠를 빼면 85.1%입니다. 세 메커니즘이 각자 다른 방식으로 기여합니다.

## 민감도

![](/images/2026-08-05-pcsd-persistent-consistency-agentic-rl/table-3-p7-6.png)

λ_PCSd가 0.005→0.01→0.05로 갈 때 87.5→90.6→83.6%입니다. 0.01이 최적이고, 너무 강하면 역효과가 납니다.

## 왜 작동하는가

PCSD의 핵심 가정은 "teacher가 신뢰할 수 있는 구간은 주변 토큰까지 일관되게 지속된다"입니다. 고립된 점 하나의 높은 값은 샘플링 노이즈일 가능성이 높습니다. 여러 토큰에 걸쳐 일관된 teacher 지지가 있을 때만 증류 가중치를 높입니다.

이게 단순 토큰별 gap(SDAR)이나 스텝별 가중치보다 안정적이라는 걸 실험으로 확인했습니다. teacher 품질 섭동(스킬 제거, 셔플)에 대해서도 PCSD는 가중치 순위를 더 잘 보존합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [arXiv:2608.01837](https://arxiv.org/abs/2608.01837)
