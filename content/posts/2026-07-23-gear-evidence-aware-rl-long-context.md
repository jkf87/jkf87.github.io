---
title: "GEAR: LLM이 긴 컨텍스트에서 '복사 붙여넣기'에 빠질 때 — 증거 기반 RL로 탈출시키는 법"
date: 2026-07-23
tags:
  - LLM
  - long-context
  - reinforcement-learning
  - reasoning
  - agent
  - RLVR
draft: false
summary: "긴 컨텍스트에서 추론하는 LLM이 입력을 그대로 복사하는 'repetitive copying' 문제를 분석하고, 증거 기반 보상 설계(GEAR)로 이를 해결한 Peking University·Alibaba의 연구를 깊이 있게 분해한다."
coverCaption: "GEAR: 복사하는 모델 vs 증거에 기반해 추론하는 모델"
---

## 핵심 요약

긴 컨텍스트(long-context)에서 추론하는 LLM에는 치명적인 실패 패턴이 있다. 바로 **'반복 복사(repetitive copying)'**다. 모델이 입력 텍스트를 이해하고 추론하는 대신, 프롬프트의 텍스트를 그대로 사고 흐름(reasoning trace)에 복사해 넣는다. 컨텍스트가 길어질수록 이 현상은 심해지며, 정확도는 떨어지고 토큰 소모만 늘어난다.

Peking University와 Alibaba Group이 2026년 7월에 발표한 **GEAR(Grounding Evidence-Aware Reward)**는 이 문제를 RL 훈련 단계에서 정면으로 공격한다. 핵심 아이디어는 단순하다: 모델이 **작업에 관련된 증거(key evidence)**와 **관련 없는 방해물(distractor)**을 구분해서 복사하도록 보상을 설계하는 것이다.

> 논문: "Copy Less, Ground More: Overcoming Repetitive Copying in Long-Context Reasoning via Evidence-Aware Reinforcement Learning" (arXiv:2607.19345, Fang et al., 2026)

## 반복 복사: 모든 모델이 겪는 문제

연구진은 7개의 프런티어 LLM(Claude-Opus-4.5, DeepSeek-V3.2, Qwen-3.5-Plus, GLM-4.7, QwQ-32B, Qwen3.5-35B-A3B, Qwen3.5-9B)을 대상으로 GSM-Infinite 벤치마크에서 n-gram 중복률을 측정했다. 결과는 충격적이다.

![Figure 1: 모델별 n-gram overlap rate — 컨텍스트가 길어질수록 모든 모델이 더 많이 복사한다](/images/2026-07-23-gear-evidence-aware-rl-long-context/fig-1-p4.png)

8K 컨텍스트에서도 3-gram 중복률이 20%(Claude)에서 43.7%(Qwen3.5-9B)에 달한다. 컨텍스트가 64K로 늘어나면 Qwen-3.5-Plus는 70.8%까지 치솟는다. 10-gram 중복률도 비슷한 패턴을 보이는데, 이는 우연한 어휘 중복이 아니라 **의도적인 텍스트 전사**가 일어나고 있음을 의미한다.

## 복사가 성능을 망친다

DeepSeek-V3.2를 64K 컨텍스트에서 분석하면, 패턴이 명확해진다.

![Figure 2: 중복률이 높아질수록 정확도는 추락하고 사고 길이는 폭증한다](/images/2026-07-23-gear-evidence-aware-rl-long-context/fig-2-p5.png)

- **중복률 0.4 미만**: 정확도 55-64%, 사고 길이 ~21K 토큰
- **중복률 0.4 이상**: 정확도 11%로 추락
- **중복률이 더 높으면**: 정확도 0%, 사고 길이 58K 토큰 이상

모델이 입력을 이해하고 추론하는 대신, 토큰 예산을 입력 텍스트 전사에 낭비하고 있는 것이다.

## 근본 원인: 무차별 복사

여기서 핵심 질문이 나온다. 복사 자체가 문제인가, 아니면 **무엇을** 복사하느냐가 문제인가?

연구진은 GSM-Infinite의 구조적 특성을 활용해 프롬프트를 **핵심 증거(key evidence)**와 **방해 컨텍스트(distractor)**로 분리한 뒤, 모델이 각각을 얼마나 복사하는지 측정했다.

![Figure 3: 정답을 맞힌 샘플이 핵심 증거에 더 집중한다](/images/2026-07-23-gear-evidence-aware-rl-long-context/fig-3-p6.png)

결과는 명확하다:
- **정답 샘플**: 핵심 증거에 대한 중복률이 높고, 방해물에 대한 중복률이 낮다 (grounding ratio가 높다)
- **오답 샘플**: 핵심 증거와 방해물을 가리지 않고 무차별적으로 복사한다

즉, 문제는 복사 자체가 아니라 **무엇을 복사하느냐**다. 관련 증거에 집중하는 모델이 정답을 맞힌다.

## GEAR: 증거 기반 보상 설계

이 진단를 바탕으로 연구진은 GEAR를 제안한다. GEAR는 표준 정확도 보상에 두 가지 보정을 추가한다:

### 1. Grounding Reward (R_ground)
핵심 증거와의 n-gram 중복을 보상한다. 모델이 관련 정보를 찾아 활용하도록 유도한다.

$$R_{ground} = \alpha \cdot \text{Overlap}_n(y \| x^{key})$$

### 2. Distractor Penalty (R_dist)
방해 컨텍스트와의 n-gram 중복에 페널티를 부과한다. 무차별 복사를 억제한다.

$$R_{dist} = -\beta \cdot \text{Overlap}_n(y \| x^{dist})$$

### 최종 보상

$$R_{GEAR} = R_{acc} + \alpha \cdot R_{ground} - \beta \cdot R_{dist}$$

기본값은 α=0.1, β=0.3으로, **방해물 페널티가 증거 보상보다 3배 강하다**. 이는 "적당히 관련 정보를 끌어오되, 관련 없는 내용을 복사하는 것은 강하게 억제"한다는 설계 의도를 반영한다.

## 자동 데이터 파이프라인

GEAR를 자연어 문서로 확장하려면 '핵심 증거' annotation이 필요하다. 연구진은 3단계 자동 파이프라인을 구축했다:

1. **문서 분할**: 긴 문서를 의미 단위 청크로 분할
2. **QA 쌍 생성**: 각 청크에서 질문-정답 쌍을 자동 생성하고, 해당 청크를 핵심 증거로 지정
3. **방해물 삽입**: 다른 청크의 내용을 방해 컨텍스트로 추가

이 파이프라인으로 임의의 문서 코퍼스에서 GEAR 훈련 데이터를 만들 수 있다.

## 실험 결과: 5개 벤치마크에서 일관된 개선

Qwen3.5-9B, 35B-A3B, 35B-A3B 세 모델을 GSPO로 훈련시켜 5개 벤치마크에서 평가했다:

| 구분 | 정확도 보상만 | GEAR 추가 | 개선 |
|------|:---:|:---:|:---:|
| Ruler (32K) | 78.5 | 81.3 | +2.8 |
| Ruler (128K) | 65.2 | 69.8 | +4.6 |
| LongBench-v2 | 42.1 | 46.7 | +4.6 |
| GSM-Infinite (32K) | 71.2 | 75.9 | +4.7 |
| AA-LCR (128K) | 38.4 | 41.2 | +2.8 |

GEAR는 **모든 벤치마크에서 일관되게 개선**을 보여주며, 특히 컨텍스트가 길어질수록(128K) 개선 폭이 크다. 동시에 **반복 복사율과 사고 길이를 모두 줄여준다** — 모델이 더 적은 토큰으로 더 정확하게 추론한다.

## 케이스 스터디: GEAR가 추론을 어떻게 바꾸는가

논문의 부록에 실린 케이스 스터디가 GEAR의 효과를 생생하게 보여준다.

**Base 모델** (16,384 토큰, 97.6% 중복률, 오답): 입력 텍스트 전체를 사고 흐름에 복사하다가 토큰 예산을 전부 소진. 답변 생성 불가.

**GSPO만 적용** (16,384 토큰, 0% 중복률, 오답): 입력 복사는 피했지만, 단일 토큰("hldjac")을 끝없이 반복하며 토큰 예산 소진.

**GEAR 적용** (2,920 토큰, 0.6% 중복률, 정답 ✓): 전략적으로 접근 → 빈도 추정 → 답 도출. 82% 적은 토큰으로 정답 도출.

## 왜 중요한가

이 연구는 긴 컨텍스트 LLM의 **실제 실패 모드**를 처음으로 체계적으로 진단하고, 그 해법을 RL 훈련에 직접 적용했다는 점에서 의미가 크다. 특히:

1. **진단의 정확성**: "복사가 문제"가 아니라 "무엇을 복사하느냐가 문제"라는 통찰
2. **단순한 해법**: n-gram 통계만으로 복잡한 grounding 행동을 보상할 수 있다는 발견
3. **일반화성**: 자동 데이터 파이프라인으로 임의의 문서에 적용 가능
4. **컨텍스트 길이 일반화**: 32K로 훈련하고 128K에서 평가해도 개선 효과 유지

긴 컨텍스트 에이전트나 RAG 시스템을 구축하는 실무자에게, 이 연구는 "모델이 컨텍스트를 얼마나 잘 활용하는가"를 평가하고 개선하는 구체적인 도구를 제공한다.

## 더 실습해보고 싶은 분들께

LLM 에이전트의 컨텍스트 활용, RL 훈련 루프 설계, 긴 컨텍스트 최적화 등에 관심이 있다면 다음 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 자동화와 컨텍스트 엔지니어링을 실습하는 데 바로 써먹을 수 있는 활용 패턴 50선
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — RL 훈련 루프부터 에이전트 하네스 설계까지, 실제 구현 관점에서 깊이 다루는 강의

---

> **원문**: Fang et al., "Copy Less, Ground More: Overcoming Repetitive Copying in Long-Context Reasoning via Evidence-Aware Reinforcement Learning", arXiv:2607.19345, July 2026. [논문 링크](https://arxiv.org/abs/2607.19345)
