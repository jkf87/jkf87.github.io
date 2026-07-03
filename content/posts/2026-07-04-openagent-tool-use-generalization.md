---
title: "OpenAgent: LLM 에이전트, 도구 사용의 일반화는 얼마나 취약한가"
date: 2026-07-04
draft: false
description: "ICML 2026 — 정적 훈련 환경에서 near-perfect를 기록한 SFT/RL 에이전트가 개방 세계(open-world)에서 어떻게 붕괴하는지, 그리고 해결책 PAFT를 분석한다."
tags: [LLM, Agent, Tool-Use, Generalization, ICML2026, SFT, RL]
categories: [AI Research]
author: Conan's Blog Bot
---

> **논문**: [Can Agents Generalize to the Open World? Unveiling the Fragility of Static Training in Tool Use](https://arxiv.org/abs/2607.01084)
> **학회**: ICML 2026 | **코드**: [github.com/LAMDA-NeSy/OpenAgent](https://github.com/LAMDA-NeSy/OpenAgent)

## TL;DR

LLM 에이전트가 기존 벤치마크에서 90%+ 성공률을 기록해도, **실제 환경에서 도구 스키마가 조금만 바뀌어도 성능이 처참히 붕괴**한다. 이 논문은 그 이유를 **SFT의 symbolic anchoring**과 **RL의 boundary blindness**로 진단하고, 훈련 데이터에 제어된 섭동(perturbation)을 주입하는 **PAFT(Perturbation-Augmented Fine-Tuning)** 로 일부 복구하는 방법을 제안한다.

---

## 1. 문제의 출발점: 정적 세계의 환상

최근 LLM 에이전트는 Tool Learning과 MCP(Model Context Protocol)를 통해 외부 환경과 상호작용하며 복잡한 작업을 수행한다. SFT(Supervised Fine-Tuning)와 RL(Reinforcement Learning)로 훈련된 오픈소스 모델들이 GPT-4급 도구 호출 능력을 보여주고 있다.

![Figure 1: 정적 환경에서 SFT와 RL 에이전트의 성능 향상 — 닫힌 세계에서는 완벽에 가깝다](/images/2026-07-04-openagent-tool-use-generalization/fig-p3.jpeg)

하지만 이것은 **닫힌 세계(closed-set)의 환상**이다. 실제 배포 환경에서는 API가 폐기되고, 도구 스키마가 진화하며, 사용자 지시는 모호하다. 연구진은 이를 정식화하여 **OpenAgent**라는 문제 설정을 제안한다.

## 2. OpenAgent: 네 가지 분포 이동(distributional shift)

에이전트-환경 루프에서 발생하는 이동을 네 차원으로 정의한다:

| 차원 | 기호 | 의미 |
|------|------|------|
| Query | Δ𝒬 | 사용자 의도와 언어 표현의 변화 |
| Action(Tool) | Δ𝒜 | 도구 이름 변경, 스키마 수정, 신규 도구 추가 |
| Observation | Δ𝒪 | None/Error 응답, 포맷 변경 등 관측의 변화 |
| Domain | Δ𝒟 | 위 모든 것이 동시에 바뀌는 도메인 전환 |

핵심은 도구 사용 에이전트에서 이동이 **누적된다는 것**이다. step *t*에서의 섭동이 이후 모든 step의 의사결정에 영향을 미친다.

### 4단계 진단 프레임워크

연구진은 환경 변화를 깊이에 따라 4단계로 분류했다:

![Figure 3: 4단계 평가 과제 구조도 — Perception, Interaction, Reasoning, Internalization](/images/2026-07-04-openagent-tool-use-generalization/fig-p7.png)

1. **Perception (Tier 1)**: 도구 이름/파라미터 라벨 변경 등 표면적 변화
2. **Interaction (Tier 2)**: 도구 동작의 의미적 변경, 신규 도구 도입
3. **Reasoning (Tier 3)**: 도구 간 논리적 의존성 역전 (병합/분할/역순)
4. **Internalization (Tier 4)**: 치명적 오류(Fatal Error) 상황에서의 회복력

## 3. 충격적인 실험 결과: SFT와 RL 모두 붕괴

### SFT 에이전트: Symbolic Anchoring

SFT 에이전트는 **트라젝토리 과적합(trajectory overfitting)** 에 빠진다. 학습 시 본 clean trajectory에만 최적화되어, 도구 이름이 바뀌거나 관측 포맷이 달라지면 즉시 성능이 하락한다.

정확도 변화(Δ)를 보면:

| 단계 | Tier-1 Δ | Tier-2 Δ | Tier-3 Δ | Tier-4 RR |
|------|----------|----------|----------|-----------|
| Base | -29.8 | -8.5 | -8.5 | 12.2 |
| SFT-200 | **-67.7** | -48.2 | -39.9 | 0.3 |
| SFT-400 | -53.9 | -45.4 | -32.5 | 0.0 |
| SFT-800 | -50.4 | -45.3 | -28.0 | 0.2 |

> SFT-200 단계에서 Tier-1 정확도가 **67.7%p 하락**. 학습할수록 정적 패턴에 더 깊이 갇힌다.

### RL 에이전트: Boundary Blindness

RL 에이전트는 SFT보다 나은 **의미적 기반(semantic grounding)** 을 보이지만, 보상 구조의 **teleological bias** 때문에 경계 상황에 취약하다. 목표 달성 보상에 최적화되다 보니, 도구가 반환하는 오류 신호를 제대로 처리하지 못한다.

## 4. PAFT: Perturbation-Augmented Fine-Tuning

연구진이 제안하는 해결책은 의외로 단순하다. SFT 훈련 데이터에 **제어된 섭동을 주입**하는 것.

![Figure 8: PAFT 적용 후 성능 변화 — 섭동 주입만으로 회복률이 극적으로 개선된다](/images/2026-07-04-openagent-tool-use-generalization/fig-p8.png)

PAFT는 세 가지 섭동을 조합한다:
- **EFP** (Error Feedback Perturbation): 관측에 에러/None 주입
- **SBP** (Symbolic Perturbation): 도구 이름/파라미터 라벨 교체
- **SRP** (Semantic Perturbation): 도구 동작 설명 변형

### 결과: 붕괴를 회복으로 뒤집기

| 단계 | Tier-1 Δ | Tier-2 Δ | Tier-3 Δ | Tier-4 RR |
|------|----------|----------|----------|-----------|
| SFT-200 | -67.7 | -48.2 | -39.9 | 0.3 |
| **+PAFT** | **+28.6** | **+26.5** | **+22.7** | **99.3** |
| SFT-400 | -53.9 | -45.4 | -32.5 | 0.0 |
| **+PAFT** | **+5.6** | **+4.9** | **-2.8** | **97.8** |

> 주목할 점: SFT-200 + PAFT는 Tier-1에서 **-67.7 → +28.6**로 반전된다. Tier-4 회복률(RR)은 0.3% → 99.3%로 극적 개선.

### Ablation: 섭동 비율 α의 영향

| α | Tier-1 Δ | Tier-2 Δ | Tier-3 Δ | Tier-4 RR |
|---|----------|----------|----------|-----------|
| 0.2 | -6.9 | -7.7 | -15.8 | 90.4 |
| **0.3 (default)** | **-4.1** | **-5.3** | **-9.8** | **99.6** |
| 0.4 | -5.3 | -7.8 | -11.1 | 96.4 |

α=0.3이 최적의 sweet spot이며, 너무 많은 섭동(α=0.4)은 오히려 학습을 방해한다.

## 5. 핵심 인사이트

1. **정적 벤치마크 성적은 거짓말이다**: closed-set에서 near-perfect라도 open-world에서는 처참히 무너진다.
2. **SFT는 더 학습할수록 더 취약해진다**: clean trajectory에 과적합되어 유연성이 감소한다.
3. **RL이 SFT보다 낫지만 완벽하지는 않다**: 의미적 이해는 좋지만 보상 구조의 편향으로 경계 상황에 무너진다.
4. **간단한 데이터 증강만으로도 극적 개선**: PAFT는 복잡한 아키텍처 변경 없이 훈련 데이터에 노이즈를 섞는 것만으로 큰 효과를 본다.
5. **초기 모델일수록 PAFT 효과가 크다**: 과적합이 진행되기 전에 개입할수록 효과적이다.

## 6. 의의와 한계

### 의의
- 도구 사용 에이전트의 **일반화 문제를 최초로 체계적으로 정식화**
- SFT vs RL의 구조적 약점을 **서로 다른 failure mode로 분리 진단**
- 실용적으로 적용 가능한 **PAFT라는 간단한 해법** 제공
- ICML 2026 채택

### 한계
- 제어된 샌드박스 환경이 실제 복잡한 배포 환경을 완전히 대변하지 못함
- PAFT가 완전한 복구를 달성하지 못함 (후기 단계 Tier-3에서 여전히 음수 Δ)
- RL에 대한 별도의 데이터 증강 전략이 부재

## 마무리

이 논문은 "에이전트가 벤치마크를 잘 통과한다"와 "에이전트가 실제로 유용하다" 사이의 간극을 날카롭게 보여준다. 도구 사용 에이전트를 프로덕션에 배포하려는 모든 팀이 읽어야 할 연구다. 특히 PAFT는 구현이 간단하므로, 도구 사용 미세조정을 수행하는 경우 기본적으로 적용을 고려할 만하다.

---

*이 포스트는 arXiv:2607.01084 (ICML 2026)의 내용을 기반으로 작성되었습니다.*
