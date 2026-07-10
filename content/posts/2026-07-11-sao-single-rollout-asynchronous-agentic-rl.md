---
title: "GLM-5.2를 만든 비동기 강화학습 — SAO(Single-Rollout Asynchronous Optimization) 완전 해부"
date: 2026-07-11
draft: false
tags:
  - reinforcement-learning
  - LLM
  - agentic-RL
  - GLM
  - asynchronous-training
  - SAO
categories:
  - AI
  - Research
description: "ZAI·청화대 연구팀이 발표한 SAO(Single-rollout Asynchronous Optimization)는 GRPO의 그룹 샘플링을 버리고 단일 롤아웃으로 비동기 RL을 안정화하는 새 패러다임이다. GLM-5.2(750B-A40B) 훈련에 실제로 사용됐으며, SWE-Bench Verified 29.8%, AIME2025 97.3%, BeyondAIME 74.8%를 기록했다. 핵심 설계를 정리한다."
aliases:
  - /posts/2026-07-11-sao-single-rollout-asynchronous-agentic-rl
---

![SAO 성능 개요 — 5개 벤치마크에서 GRPO 대비 일관된 향상](/images/2026-07-11-sao-single-rollout-asynchronous-agentic-rl/fig-p1.png)

## 한 줄 요약

강화학습(RL)이 LLM 포스트트레이닝의 표준이 되면서, **동기식 배치 처리**의 비효율이 병목으로 떠올랐다. SAO는 GRPO가 쓰는 그룹 단위 샘플링을 **단일 롤아웃(single-rollout)**으로 교체하고, 토큰 수준의 양측 클리핑(double-sided clipping)으로 안정성을 확보한다. 그 결과 1,000스텝 이상 안정적으로 훈련되며, SWE-Bench Verified에서 GRPO 대비 +2.8%p, BeyondAIME에서 +20%p 향상을 달성했다. 이 방법론은 **GLM-5.2(750B-A40B)** 모델의 에이전트 RL 파이프라인에 실제로 배포됐다.

---

## 1. 왜 비동기 RL이 필요한가

기존 LLM RL 파이프라인은 대부분 **동기식(synchronous)**이다. 정책 모델이 롤아웃 batch를 생성하고, batch 전체가 완료되어야 최적화가 시작된다. 짧은 트레젝토리는 빨리 끝나지만 긴 트레젝토리가 "straggler"가 되어, GPU 클러스터의 상당 부분이 **가장 느린 롤아웃을 기다리며 유휴 상태**에 빠진다.

이 문제는 **에이전트 코딩(agent coding)** 워크로드에서 특히 심각하다. 코딩 에이전트 하나의 롤아웃은 수천 토큰에 달할 수 있고, 길이 편차가 극심하다.

비동기 RL은 롤아웃이 도착하는 대로 모델을 업데이트해서 활용률과 벽시계 효율을 높인다. 하지만 두 가지 치명적인 문제가 있다:

1. **정책 지연(policy lag)**: 하나의 트레젝토리가 생성되는 동안 롤아웃 엔진이 여러 버전으로 업데이트될 수 있어, 정확한 행동 확률 추적이 불가능해진다.
2. **GRPO의 그룹 샘플링 불일치**: GRPO는 프롬프트마다 여러 응답을 샘플링하고 그룹 평균으로 어드밴티지를 추정한다. 비동기 설정에서는 그룹 내 느린 샘플을 기다려야 하므로 **비동기의 이점을 상쇄**한다.

---

## 2. SAO의 세 가지 핵심 설계

![SAO 아키텍처 — 단일 롤아웃이 완료되는 즉시 훈련에 투입된다](/images/2026-07-11-sao-single-rollout-asynchronous-agentic-rl/fig-p2.png)

### 2.1 Direct Double-Sided Importance Sampling (DIS)

SAO의 첫 번째 혁신은 **중간 정책(π_old)을 추적하는 것을 포기**하는 것이다.

기존 PPO는 세 개의 모델을 유지한다: 현재 정책 π_θ, 이전 정책 π_old, 롤아웃 정책 π_rollout. 비동기 설정에서는 π_old가 여러 버전에 걸쳐 흩어져 있어 추적이 현실적으로 불가능하다.

SAO는 단순하게 **π_rollout의 로그 확률을 직접 사용**하여 π_θ와의 비율을 계산한다:

$$r_t(\theta) = \exp(\log\pi_\theta(a_t|s_t) - \log\pi_{\text{rollout}}(a_t|s_t))$$

그리고 양측 클리핑으로 신뢰 구간 [1−ε_ℓ, 1+ε_h] 밖의 토큰은 **그레이디언트에서 완전히 마스킹**한다. 이는 극단적인 정책 발산으로 인한 불안정성을 차단한다.

> 핵심 통찰: "정확하지만 비싼 π_old 추적" 대신 "대략적이지만 공격적인 클리핑"을 택했다. 계산 복잡도를 크게 줄이면서도 훈련 안정성을 달성한다.

### 2.2 Single-Rollout Sampling (그룹 샘플링의 제거)

GRPO는 프롬프트당 N개의 응답을 생성하고 그룹 평균으로 베이스라인을 삼는다. 이는 동기식에서는 잘 작동하지만, 비동기에서는 **"가장 느린 그룹원"을 기다리는 병목**을 만든다.

SAO는 프롬프트당 **하나의 롤아웃만** 생성하고, 완료되는 즉시 훈련에 투입한다. 이는 환경이 단일 궤적 피드백만 제공하는 **온라인 에이전트 설정**과도 자연스럽게 호환된다.

하지만 단일 롤아웃은 분산이 높다. SAO는 이를 **가치 모델(value model)** 최적화로 보완한다:

- **Critic을 Actor보다 더 자주 업데이트** (2:1 비율)
- **Frozen Attention**: 가치 모델의 어텐션 층은 고정하고 FFN만 미세조정

### 2.3 Skip-Observation GAE

에이전트 트레젝토리는 모델이 생성한 액션 토큰과 환경이 반환한 관찰(observations) 토큰이 교차한다. 관찰 토큰은 모델이 생성한 것이 아니므로, 여기에 그레이디언트를 전파하면 노이즈가 된다.

SAO는 **관찰 토큰을 건너뛰고 액션-투-액션 경계에서 GAE를 계산**하는 skip-observation 추정자를 도입했다.

---

## 3. 실험 결과

![주요 벤치마크 성능 비교](/images/2026-07-11-sao-single-rollout-asynchronous-agentic-rl/fig-p6.png)

### 3.1 수학 추론 벤치마크

Qwen3-30B-A3B를 베이스라인으로 SAO를 적용한 결과:

| 벤치마크 | SFT (baseline) | GRPO | **SAO** |
|---|---|---|---|
| AIME2025 | 80.4 | 84.2 | **97.3** |
| BeyondAIME | 53.3 | 54.8 | **74.8** |
| HMMT Nov 2025 | 75.2 | 76.0 | **88.3** |
| IMOAnswerBench | 53.3 | 55.8 | **74.0** |

BeyondAIME에서 GRPO 대비 **+20%p**의 향상은 압도적이다.

### 3.2 코딩 에이전트: SWE-Bench Verified

| 방법 | 정확도(%) |
|---|---|
| Qwen3-30B-A3B (baseline) | 23.0 |
| + GRPO (w/ DIS) | 27.0 |
| **+ SAO (ours)** | **29.8** |

### 3.3 GPT-5 및 Claude와의 비교

| 모델 | AIME2025 | BeyondAIME | IMOAnswerBench |
|---|---|---|---|
| Claude-Sonnet-4.5 | 87.0 | 62.0 | 65.8 |
| GPT-5 High | 94.6 | 74.0 | 76.0 |
| GLM-4.7 | 95.7 | — | 93.5 |
| Qwen3-30B + **SAO** | **97.3** | **74.8** | **74.0** |

Qwen3-30B에 SAO를 적용한 모델이 AIME2025에서 GPT-5 High와 Claude-Sonnet-4.5를 능가하는 97.3%를 기록했다.

---

## 4. Ablation: 무엇이 효과가 있었나

![Ablation study — 각 컴포넌트의 기여도](/images/2026-07-11-sao-single-rollout-asynchronous-agentic-rl/fig-p9.png)

| 설정 | AIME2025 | BeyondAIME |
|---|---|---|
| **SAO (full)** | **97.3** | **74.8** |
| w/o Faster value update | 95.0 | 69.8 |
| w/o Frozen attention | 90.6 | 74.5 |
| Vanilla VAPO (w/o DIS) | 91.3 | 69.0 |
| Running mean baseline | 79.8 | 55.3 |

가장 큰 영향을 미친 요소는 **running mean baseline의 제거** (−17.5%p)와 **frozen attention** (−6.7%p)이었다. 가치 모델의 설계가 단일 롤아웃 RL의 성공을 좌우한다는 것을 보여준다.

---

## 5. 온라인 학습 시뮬레이션

SAO의 단일 롤아웃 전략은 **시뮬레이션된 온라인 학습 환경**에서 빛을 발한다. 환경이 변화할 때, GRPO는 그룹 전체가 새로운 환경에 대해 재평가되어야 하지만, SAO는 각 롤아웃이 도착하는 즉시 적응한다.

이는 실제 에이전트 배포 시나리오 — API가 변경되거나, 워크플로우가 업데이트되거나, 새로운 도구가 추가되는 상황 — 에서 결정적인 이점이다.

---

## 6. GLM-5.2와의 연결

SAO는 단순한 학술贡献이 아니다. **GLM-5.2(750B-A40B)** 모델의 에이전트 RL 파이프라인에 실제로 배포되었다. 750B 매개변수에 40B가 활성화되는 MoE 아키텍처를 비동기 RL로 훈련한 것이다.

이는 GLM 시리즈가 GPT-5, Claude와 경쟁하는 성능을 달성하는 데 SAO가 핵심 역할을 했음을 시사한다.

---

## 7. 의의와 한계

### 의의

- **GRPO 패러다임의 전환**: 그룹 샘플링 없이도 안정적인 RL이 가능함을 증명
- **실용적 가치**: 동기식의 유휴 시간 문제를 해결하면서도 성능을 향상
- **오픈소스 생태계 기여**: GLM-5.2 모델 훈련에 직접 사용

### 남은 질문

- 더 큰 규모(1T+ 매개변수)에서도 단일 롤아웃이 안정적인가?
- 가치 모델의 frozen attention이 다른 아키텍처(Transformer 이외)에서도 유효한가?
- 온라인 학습 시뮬레이션의 실제 배포 시나리오 검증이 필요

---

## 참고

- **논문**: [Single-Rollout Asynchronous Optimization for Agentic Reinforcement Learning](https://arxiv.org/abs/2607.07508), arXiv:2607.07508
- **저자**: Zhenyu Hou, Yujiang Li, Jie Tang, Yuxiao Dong (Tsinghua University / ZAI)
- **코드/모델**: GLM-5.2 (750B-A40B), 오픈소스
- **벤치마크**: SWE-Bench Verified, AIME2025, BeyondAIME, HMMT Nov 2025, IMOAnswerBench
