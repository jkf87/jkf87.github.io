---
title: "SEED: 에이전트 RL이 완료된 궤적에서 스스로 배우는 자가진화 증류"
date: 2026-07-17T13:00:00+09:00
draft: false
summary: "SEED(SElf-Evolving On-Policy Distillation)는 LLM 에이전트의 희소 보상 RL 문제를 해결한다. 완료된 궤적에서 hindsight skill을 추출하고, 이를 on-policy distillation으로 토큰 수준의 밀집 감독 신호로 변환하여 정책과 분석 능력이 함께 진화한다."
tags: ["agentic-rl", "on-policy-distillation", "self-evolving", "hindsight-learning", "LLM-agent"]
categories: ["AI-Agents"]
cover:
  image: "images/2026-07-17-seed-self-evolving-agentic-rl-distillation/pipeline-github.png"
  alt: "SEED 프레임워크 전체 파이프라인 — Hindsight Skill SFT와 Self-Evolving OPD 단계"
  caption: "SEED의 두 단계: (1) Hindsight Skill SFT로 궤적 분석 능력을 확보하고, (2) Self-Evolving OPD에서 정책과 분석 능력이 공동 진화한다."
  relative: true
---

## 핵심 요약

**SEED(SElf-Evolving On-Policy Distillation)**는 Tsinghua University 등의 연진이 제안한 프레임워크로, LLM 에이전트의 강화학습에서 **희소 보상(sparse reward)** 문제를 해결한다. 완료된 에이전트 궤적(trajectory)으로부터 자연어 **hindsight skill**을 추출하고, 이를 **on-policy distillation(OPD)**을 통해 토큰 수준의 밀집(dense) 감독 신호로 변환한다. 핵심은 정책 모델이 스스로 궤적을 분석하고, 그 결과를 학습에 활용하며, 정책이 개선됨에 따라 분석 능력도 함께 진화한다는 점이다.

> **한 줄 요약**: 에이전트가 자신의 경험을 분석해 "교훈"을 뽑고, 그 교훈을 다시 자신의 행동에 주입하는 자가증류(self-distillation) 루프.

## 문제: 희소 보상의 간극

LLM 에이전트는 다단계 상호작용(multi-turn interaction), 도구 사용(tool use), 환경 피드백을 포함하는 장기 과제(long-horizon tasks)에서 학습된다. 결과 기반 강화학습(outcome-based RL)은 실용적인 최적화 패러다임이지만, **에피소드 수준의 보상만 제공**한다:

- 성공/실패 여부는 알려주지만, **어느 중간 결정이 옳았는지**는 알려주지 않는다
- 실패한 궤적에도 유용한 부분 행동이 있고, 성공한 궤적에도 개선할 점이 있다
- 토큰 수준의 정책 학습과 에피소드 수준의 보상 사이에 **감독의 간극(supervision gap)**이 존재한다

![SEED 프레임워크 개요: 두 단계로 구성된 자가진화 파이프라인](/images/2026-07-17-seed-self-evolving-agentic-rl-distillation/pipeline-github.png)
*Figure 1: SEED의 전체 파이프라인. Stage 1에서는 Hindsight Skill SFT로 궤적 분석 능력을 확보하고, Stage 2에서는 정책과 분석 능력이 공동 진화하며 on-policy distillation이 수행된다.*

## SEED의 해결책: 자가진화 On-Policy Distillation

SEED는 세 가지 요구사항을 충족하는 설계를 제시한다:

### 1. On-Policy (정책 일치)
유용한 교정은 **현재 정책이 만드는 상태, 행동, 실패 패턴**에 의존한다. 외부 고정 교사나 정적 데이터셋이 아닌, 현재 정책이 생성한 궤적에서 hindsight를 추출한다.

### 2. Dense (밀집 감독)
궤적 수준의 hindsight를 **개별 토큰 수준의 학습 신호**로 분해한다. 같은 샘플링된 행동을 일반 맥락과 skill-augmented 맥락에서 각각 평가하여, 확률 변화를 OPD 손실로 사용한다.

### 3. Self-Evolving (자가 진화)
정책이 개선됨에 따라 **결정 능력과 궤적 분석 능력이 함께 향상**된다. 각 RL 업데이트 후 최신 정책 체크포인트가 다음 롤아웃의 행위자이자 분석기가 된다.

## 두 단계 학습 파이프라인

### Stage 1: Hindsight Skill SFT

첫 번째 단계는 정책 모델에 **완료된 궤적을 분석하는 능력**을 부여한다:

1. **오프라인 궤적 수집**: 베이스 정책으로 다수의 에이전트 롤아웃을 수집
2. **Hindsight skill 주석**: 외부 분석기(GPT-4 수준)가 각 궤적에서 재사용 가능한 전략, 결정적 관찰, 실패 회피 규칙을 자연어로 추출
3. **SFT 학습**: 정책 모델이 궤적 입력 → hindsight skill 출력을 학습

이렇게 훈련된 체크포인트는 이후 RL 단계에서 행위자이자 분석기로 동시에 사용된다.

### Stage 2: Self-Evolving OPD during RL

두 번째 단계는 GRPO와 같은 결과 기반 RL에 자가진화 OPD를 결합한다:

1. **온폴리시 궤적 수집**: 현재 정책이 환경에서 롤아웃 수행
2. **동기화된 분석**: 같은 정책 체크포인트가 완료된 궤적에서 hindsight skill 추출
3. **액션 재스코어링**: 샘플링된 행동을 (a) 일반 맥락과 (b) skill-augmented 맥락에서 각각 로그 확률 계산
4. **OPD 손실**: skill에 의한 확률 변화를 토큰 수준 distillation 신호로 변환
5. **공동 최적화**: RL 손실 + OPD 손실을 함께 최적화

![SEED의 메인 결과: ALFWorld, WebShop, Search-QA에서 GRPO 대비 일관된 성능 향상](/images/2026-07-17-seed-self-evolving-agentic-rl-distillation/results-github.png)
*Figure 2: ALFWorld, WebShop, Search-based QA 세 벤치마크에서 SEED가 GRPO 베이스라인을 일관되게 능가한다.*

## 핵심 기술적 통찰

### Skill을 내재화하는 것이 프롬프팅보다 낫다

SEED는 hindsight skill을 **훈련 시에만** 사용하고, 추론 시에는 학습된 정책만 사용한다. 놀랍게도, skill을 추론 시 프롬프트로 제공하는 것보다 **훈련 시 내재화**하는 것이 더 효과적이다. 정책이 skill의 행동적 효과를 파라미터에 통합하기 때문이다.

### 자가진화가 정적 증류를 능가한다

고정된 분석기나 한 번의 distillation은 정책이 새로운 상태와 실패 모드를 접하면서 빠르게 진부해진다. SEED의 루프는 **각 업데이트마다 분석기가 최신 정책으로 갱신**되므로, hindsight 감독이 정책의 진화하는 행동 분포와 정렬된다.

### 확률 변화를 통한 게이팅

OPD 손실은 단순히 skill을 따라하는 것이 아니다. 같은 행동 토큰에 대해 일반 맥락과 skill-augmented 맥락의 **로그 확률 차이**를 사용한다. 이는 skill이 실제로 행동 선택에 영향을 미치는 토큰에서만 강한 신호를 제공하는 효과적인 게이팅 메커니즘이다.

![SEED 최적화 역학: GRPO 대비 학습 곡선과 데이터 효율성](/images/2026-07-17-seed-self-evolving-agentic-rl-distillation/fig-3-p10.png)
*Figure 3: ALFWorld에서 SEED와 GRPO의 최적화 역학 비교. SEED가 더 빠르게 수렴하고 더 높은 성공률에 도달한다.*

## 실험 결과

SEED는 세 가지 대표적 에이전트 벤치마크에서 평가되었다:

| 벤치마크 | 도메인 | 주요 결과 |
|---------|--------|----------|
| **ALFWorld** | 텍스트 기반 임바디드 상호작용 | GRPO 대비 일관된 성능 향상 |
| **WebShop** | 웹 탐색 및 쇼핑 | 견고한 일반화 |
| **Search-based QA** | 검색 기반 질의응답 | 우수한 샘플 효율성 |

![SEED 구성 요소 기여도 분석: ablation study 결과](/images/2026-07-17-seed-self-evolving-agentic-rl-distillation/table-2-p10.png)
*Table 2: SEED의 세 핵심 구성 요소(hindsight skill, on-policy distillation, self-evolving)의 기여도를 분석한 ablation study.*

세 가지 핵심 발견:

1. **밀집 hindsight 감독은 결과 전용 RL을 개선한다**: SEED는 궤적 수준의 hindsight를 토큰 수준 OPD 신호로 변환하여 GRPO를 일관되게 능가
2. **Skill 내재화가 skill 프롬프팅보다 낫다**: 훈련 시에만 skill을 사용해도 추론 시 skill을 프롬프트로 제공하는 것보다 우수
3. **자가진화 증류가 정적 증류를 이긴다**: 분석기를 최신 정책으로 갱신하는 것이 hindsight 감독을 정책의 진화하는 행동에 정렬시킴

![SEED의 데이터 효율성: 적은 데이터로도 GRPO 수준 이상 달성](/images/2026-07-17-seed-self-evolving-agentic-rl-distillation/fig-4-p10.png)
*Figure 4: 데이터 분율에 따른 SEED와 GRPO 비교. SEED는 적은 데이터 분율에서도 GRPO를 능가하거나 필적한다.*

## 의의 및 시사점

SEED는 에이전트 RL의 근본적 문제인 희소 보상을 **정책 자체의 자기반성 능력**으로 해결한다는 점에서 주목할 만하다:

- **추론 시 오버헤드 제로**: 학습된 정책만 배포하면 된다. 외부 메모리, skill 뱅크, 검색 모듈, 추가 프롬프트가 불필요
- **범용성**: 텍스트 기반 환경, 웹 탐색, 시각 인식 및 계획 등 다양한 에이전트 도메인에 적용 가능
- **확장성**: 모델 크기가 커져도 일관된 향상을 보임
- **실용성**: GRPO 등 기존 RL 파이프라인에 OPD 손실항을 추가하는 것만으로 구현 가능

이 연구는 "정책이 경험에서 배우는 것"과 "정책이 경험을 분석하는 것"을 분리하지 않고 **하나의 모델에서 통합**했다는 점에서, 에이전트 자가개선(self-improvement) 연구의 중요한 이정표가 될 것이다.

## 코드 및 자료

- **논문**: [arXiv:2607.14777](https://arxiv.org/abs/2607.14777)
- **코드**: [github.com/jinyangwu/SEED](https://github.com/jinyangwu/SEED)
- **데모 페이지**: [jinyangwu.github.io/seed](https://jinyangwu.github.io/seed/)
- **모델**: [HuggingFace - Seed-AlfWorld-3B](https://huggingface.co/Jinyang23/Seed-AlfWorld-3B)

---

*이 글은 SEED 논문(Wu et al., 2026)의 핵심 아이디어를 한국어로 정리한 것입니다. 원문의 수식과 세부 실험은 논문을 직접 참조하세요.*
