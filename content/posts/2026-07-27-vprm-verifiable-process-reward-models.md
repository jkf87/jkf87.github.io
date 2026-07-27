---
title: "VPRM: 결괏값만 맞추는 RL을 넘어 — 추론 과정까지 검증 가능한 보상 모델"
date: 2026-07-27T13:20:00+09:00
draft: false
tags:
  - RLVR
  - process-supervision
  - reward-model
  - medical-ai
  - reasoning
  - LLM
  - systematic-review
  - risk-of-bias
categories:
  - AI Research
summary: "RLVR가 결과만 검증한다면, VPRM은 추론의 매 단계를 규칙 기반으로 검증한다. 의료 evidence synthesis의 risk-of-bias 평가에서 F1 최대 20% 향상을 입증한 IBM Research의 새로운 접근을 해부한다."
---

> **논문**: [Beyond Outcome Verification: Verifiable Process Reward Models for Structured Reasoning](https://arxiv.org/abs/2601.17223)
> **저자**: Massimiliano Pronesti (IBM Research Europe · Dublin City University), Anya Belz (DCU), Yufang Hou (IBM Research Europe · IT:U Austria)
> **공개**: 2026년 1월 23일 · arXiv 2601.17223

---

## RLVR의 맹점: 결괏값은 맞는데 과정은 틀릴 수 있다

강화학습 기반 검증 보상(RLVR, Reinforcement Learning with Verifiable Rewards)은 LLM 추론 능력을 끌어올리는 핵심 기술이 됐다. 코드 생성의 유닛 테스트, 수학의 정답 매칭처럼 **결과를 결정론적으로 검증**할 수 있는 태스크에서 GRPO, DAPO 같은 알고리즘이 큰 성과를 거뒀다.

하지만 여기엔 구멍이 있다. RLVR은 **최종 결과만 맞으면 보상**을 준다. 중간 추론 과정이 엉망이어도 정답만 맞으면 된다. 이건 수학이나 코드에서는 큰 문제가 아닐 수 있지만, **의료 진단vidence synthesis**처럼 과정의 투명성이 결과만큼 중요한 도메인에서는 치명적이다.

반대로, 기존 process supervision(단계별 감독)은 어떤가? 신경망 판단자(neural judge)가 CoT 사고 단계를 평가한다. 하지만 이 신경망 자체가 불투명하고, 편향되어 있고, reward hacking에 취약하다.

**VPRM(Verifiable Process Reward Models)**은 이 두 세계의 장점을 결합하려 한다: RLVR의 결정론적 검증 + process supervision의 단계별 보상. 핵심 질문은 이것이다:

> *"강화학습으로 모델을 훈련시키되, 추론의 모든 중간 단계가 도메인 규칙을 만족할 때만 보상을 줄 수 있는가?"*

## 핵심 아이디어: 규칙 기반 단계별 검증

VPRM의 프레임워크를 이해하려면 먼저 두 가지 보상의 차이를 봐야 한다.

![Figure 2: 결과 보상 vs 과정 보상](/images/2026-07-27-vprm-verifiable-process-reward-models/fig-2-p4.png)

왼쪽은 기존의 verifiable outcome reward: 최종 risk label만 검사한다. 오른쪽이 VPRM의 verifiable process reward: 각 추론 단계와 그에 따른 label을 규칙 기반으로 검증한 뒤, 최종 결과까지 확인한다.

### 추론 궤적의 구조

모델이 입력 $x$에 대해 추론 궤적 $Y = (o_1, \ldots, o_T)$를 생성한다. 각 단계 $t$는 두 가지 출력을 갖는다:

1. **단계 식별자(step identifier)** $s_t$: "무엇을 확인해야 하는가?" (예: "무작위 배정 방법 확인")
2. **단계 라벨(step label)** $\hat{\ell}_t$: "이 단계의 답은 무엇인가?" (예: "비무작위")

도메인 가이드라인은 각 단계마다 정답 식별자 $s_t^*$와 정답 라벨 $\ell_t^*$를 규칙으로 정의한다.

### 단계별 보상 계산

각 단계의 보상은 결정론적 스코어링 함수로 계산된다:

$$r_t(Y; x) = w_t^n \cdot s_t^n(s_t, s_t^*) + w_t^l \cdot s_t^l(\hat{\ell}_t, \ell_t^*)$$

전체 보상은 모든 단계 보상의 합에 최종 결과 보상을 더한 값이다:

$$R(Y; x) = \sum_{t=1}^{T} r_t(Y; x) + r_{\text{label}}$$

**모든 보상이 규칙 기반으로 결정론적으로 계산된다.** 신경망 판단자는 개입하지 않는다.

## 적용 도메인: 의료 evidence synthesis의 risk-of-bias 평가

왜 하필 의료의 risk-of-bias(RoB) 평가일까? 이 도메인이 VPRM에 특히 적합한 이유가 있다.

![Figure 1: risk-of-bias 평가의 검증 가능한 추론 구조](/images/2026-07-27-vprm-verifiable-process-reward-models/fig-1-p2.png)

Cochrane RoB 2.0 도구는 임상시험의 편향 위험을 평가하는 표준 가이드라인이다. 각 편향 도메인(무작위 배정, 배정 은닉, 눈가림, 결과 누락 등)마다 **명확한 의사결정 트리**가 존재한다. 이 트리는 규칙 기반으로 프로그래밍할 수 있다.

예를 들어 '무작위 배정(A형 편향)' 평가는:
1. 무작위 배정이 보고되었는가? → 보고되지 않음 → **중간 위험**
2. 무작위 방법인가? → 비무작위 → **높은 위험**
3. 순서 예측 가능? → 예측 가능 → **중간 위험**
4. 기준선 불균형? → 있음 → **높은 위험**
5. 위 해당 없음 → **낮은 위험**

이러한 결정 규칙이 VPRM의 verifier로 직접 구현된다.

### 데이터셋 구성

CochraneForest와 RoBBR 벤치마크를 사용했다:
- **CochraneForestExt**: 104개 체계적 문헌고찰에서 추출한 2,946개 인스턴스 (4M 토큰)
- **RoBBR Cochrane**: 204편 논문, 58개 Cochrane 리뷰
- **RoBBR Non-Cochrane**: 496편 논문, 496개 비-Cochrane 리뷰

## 실험 결과: VPRM이 보여준 일관된 우위

### 메인 결과

![Table 2: 세 데이터셋에서의 정확도 및 macro-F1 비교](/images/2026-07-27-vprm-verifiable-process-reward-models/table-2-p7.png)

Qwen2.5-7B 기준으로 비교했다:

| 설정 | 핵심 차이 |
|------|-----------|
| Pretrained | RL 없이 프롬프트만 |
| SFT | 감독 미세조정 (추론 궤적 포함) |
| RLVR (outcome only) | 결과만 검증 |
| **VPRM** | **결과 + 과정 모두 검증** |

VPRM은 세 데이터셋 모두에서 일관되게 최고 성능을 기록했다. 특히 CochraneForest에서 VPRM은 **최대 20% 높은 F1**을 달성했고, 결과만 검증하는 RLVR 대비 **6.5% 높은 F1**을 보였다.

RoBBR Non-Cochrane에서의 향상은 훈련 분포를 넘어선 일반화 가능성을 시사한다. 데이터셋 특유의 패턴을 착취한 것이 아니다.

### 신경망 PRM과의 비교

![Table 3: 신경망 판단자 vs 규칙 기반 VPRM 비교](/images/2026-07-27-vprm-verifiable-process-reward-models/table-3-p7.png)

LLLM-as-judge(신경망 판단자)와 MedPRM(의료 특화 PRM)을 베이스라인으로 사용했다. 둘 다 결과 전용 RLVR보다는 낫지만, VPRM에는 미치지 못했다. 학습된 판단자가 노이즈와 불일치를 도입하기 때문이다.

이 결과가 시사하는 바: **결정론적 규칙 기반 검증이 신경망 판단보다 더 깨끗하고 안정적인 최적화 신호를 제공한다.**

### Ablation: 어떤 구성 요소가 중요한가?

![Table 4: 결과 보상과 과정 보상 구성 요소 ablation](/images/2026-07-27-vprm-verifiable-process-reward-models/table-4-p7-4.png)

- 결과 보상을 빼면 성능이 크게 떨어진다 → 과정만으로는 부족
- 단계 구조만 확인(steps-only)하는 것보다, 각 단계의 정답 여부까지 확인하는 full VPRM이 항상 우위
- 결과 보상 + 과정 보상의 결합이 가장 강력한 학습 신호를 만든다

### 일관성(Coherence) 분석

![Table 5: Coherence 및 Coherent Accuracy 비교](/images/2026-07-27-vprm-verifiable-process-reward-models/table-5-p8.png)

Coherence는 모델의 최종 예측이 자신의 중간 추론 단계와 일치하는 비율이다. 사전 학습된 모델은 coherence도 낮고, 일관적일 때도 정답률이 낮다. VPRM 훈련 모델은 **높은 coherence와 높은 coherent accuracy**를 동시에 달성했다.

이건 단순히 정답을 맞추는 게 아니라, **올바른 추론 경로를 통해 정답에 도달한다**는 의미다.

## 이론적 보장: 왜 이것이 작동하는가

VPRM의 이론적 핵심은 의외로 단순하다. GRPO나 DAPO에서 정규화된 어드밴티지 $\hat{A}(Y)$는 올바른 추론 궤적에는 양의 기댓값을, 잘못된 궤적에는 음의 기댓값을 갖는다.

증명의 핵심 아이디어:
- 올바른 궤적의 평균 보상 $\mu_c$가 잘못된 궤적의 평균 보상 $\mu_i$보다 크면 ($\mu_c > \mu_i$)
- 그룹 충분히 크면 ($G \to \infty$)
- $\mathbb{E}[\hat{A}(Y) \mid \mathcal{C}] = (1-p)(\mu_c - \mu_i) / \sigma > 0$
- $\mathbb{E}[\hat{A}(Y) \mid \mathcal{C}^c] = -p(\mu_c - \mu_i) / \sigma < 0$

즉, **올바른 추론은 양의 그래디언트를, 잘못된 추론은 음의 그래디언트를 받는다**. 이는 Wen et al. (2025)의 RLVR 이론을 과정 보상으로 확장한 것이다.

## 한계와 의의

논문이 솔직하게 인정하는 한계:

1. **도메인 의존성**: 결정론적 규칙이 존재하는 도메인에서만 작동한다. 개방형 추론에는 직접 적용 불가
2. **평가 범위**: 현재 risk-of-bias 평가로만 검증됐다. 다른 구조화된 추론 태스크로의 일반화는 미제
3. **출력 형식 의존**: 모델이 verifier가 기대하는 형식으로 추론을 생성해야 한다
4. **가이드라인 불완전성**: 규칙 자체가 완벽하지 않을 수 있다

그럼에도 VPRM의 의의는 명확하다. **RLVR의 결정론적 검증 철학을 과정 수준으로 끌어올린 최초의 프레임워크**이며, 신경망 판단자의 불투명성 문제를 구조적으로 회피했다. 의료 evidence synthesis뿐 아니라, 법률 분석, 규제 준수, 품질 관리 등 "명확한 절차 규칙이 있는" 모든 도메인에 적용 가능성이 열려 있다.

## 더 실습해보고 싶은 분들께

RLVR과 process supervision의 결합은 단순한 학술 호기심이 아니다. 에이전트 루프 설계, 보상 설계, 검증 가능한 추론 파이프라인 구축에 직접적으로 연결되는 기술이다. 더 깊이 실습해보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — AI 에이전트 루프와 자동화 파이프라인을 직접 구성해보는 실전 가이드
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 보상 설계부터 검증 루프까지, 에이전트 시스템을 엔지니어링하는 방법론

---

**관련 링크**: [arXiv 전문](https://arxiv.org/abs/2601.17223) · [CochraneForest 데이터셋](https://arxiv.org/abs/2605.14678) · [RoB 2.0 도구](https://www.bmj.com/content/366/bmj.l4898)
