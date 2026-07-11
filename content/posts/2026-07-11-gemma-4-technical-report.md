---
title: "Gemma 4 — 구글의 2.3B부터 31B까지, thinking·MoE·인코더 없는 통합 아키텍처"
date: 2026-07-11
draft: false
summary: "구글 Gemma 팀이 발표한 Gemma 4. dense 2.3B·4.5B·12B·31B와 MoE 26B-A4B까지 5개 변형, thinking mode, encoder-free 12B 통합 아키텍처, QAT + MTP로 효율을 끌어올렸다. AIME 2026 89.2%, MMLU Pro 85.2% — 같은 크기 모델 중 최상위권이다."
tags: [AI, LLM, Gemma, Google, open-weight, MoE]
categories: [논문리뷰]
cover: /images/2026-07-11-gemma-4-technical-report/fig-p2.png
---

> **논문:** [Gemma 4 Technical Report](https://arxiv.org/abs/2607.02770)
> **저자:** Gemma Team (Google)
> **라이선스:** Apache 2.0

구글이 Gemma 4를 발표했다. 2.3B부터 31B까지, dense와 MoE를 아우르는 5개 변형에 thinking mode까지 넣었다. 같은 크기 대역에서 가장 강력한 오픈웨이트 모델이라는 게 구글의 주장인데, 벤치마크 숫자를 보면 설득력이 있다.

![Gemma 4 모델 패밀리 개요](/images/2026-07-11-gemma-4-technical-report/fig-p2.png)

## 라인업: 5개 모델, 한 가족

Gemma 4는 다섯 가지 크기로 나온다. 핵심은 "hardware 환경에 맞춰 골라 쓰라"는 설계 철학이다.

| 모델 | 타입 | 총 파라미터 | 활성 파라미터 | 비고 |
|---|---|---|---|---|
| E2B | Dense | 5B | 2.3B | per-layer embedding, 온디바이스 |
| E4B | Dense | 8B | 4.5B | per-layer embedding, 온디바이스 |
| 12B | Dense | 12B | 12B | **encoder-free 통합 아키텍처** |
| 26B-A4B | MoE | 26B | 3.8B | 4B 활성으로 26B 성능 |
| 31B | Dense | 31B | 31B | 최상위, thinking mode |

E2B·E4B는 Gemma 3n에서 도입된 per-layer embedding 방식을 계승한다. 총 파라미터는 5B·8B지만, 실제 추론에 사용하는 effective 파라미터는 2.3B·4.5B로 메모리를 아낀다.

## 핵심 설계 4가지

### 1. Thinking Mode

Gemma 4는 응답 전에 reasoning trace를 생성하는 thinking mode를 통합했다. 모델이 "생각"한 뒤 대답하는 구조. 복잡한 추론·수학·코딩 작업에서 성능을 끌어올리는 장치다.

### 2. Encoder-Free 통합 아키텍처 (12B)

12B 모델은 비전 인코더와 오디오 인코더를 거치지 않고, raw image patch와 raw audio를 직접 처리한다. 별도 인코더 모듈 없이 텍스트·이미지·오디오를 하나의 아키텍처에서 소화하는 설계. 모델이 단순해지고 추론 파이프라인이 깔끔해진다.

### 3. Long-Context 효율화

긴 컨텍스트에서 메모리 병목을 완화하기 위해 세 가지를 적용했다:
- **local-to-global attention 비율 최적화** — 가까운 토큰은 dense, 먼 토큰은 sparse하게
- **positional encoding 개선**
- **KV cache sharing** — 반복되는 KV를 공유해서 메모리 절약

### 4. QAT + MTP로 추론 효율 극대화

- **QAT (Quantization-Aware Training)** — 양자화를 학습에 반영해서, 실제 배포 시 정확도 손실 없이 더 빠르고 가볍게
- **MTP (Multi-Token Prediction) Drafters** — 한 번에 여러 토큰을 예측하는 초안 모델(drafter)로 speculative decoding을 가속. 메모리 효율과 추론 속도를 동시에 잡았다.

![아키텍처 및 학습 구성](/images/2026-07-11-gemma-4-technical-report/fig-p4.png)

## 벤치마크: 같은 크기 중 최상위권

핵심 벤치마크 숫자를 Gemma 3 27B(non-thinking)와 비교했다.

| 벤치마크 | 31B | 26B-A4B | 12B | E4B | E2B | Gemma 3 27B |
|---|---|---|---|---|---|---|
| MMLU Pro | **85.2** | 82.6 | 77.2 | 69.4 | 60.0 | 67.6 |
| AIME 2026 (no tools) | **89.2** | 88.3 | 77.5 | 42.5 | 37.5 | 20.8 |
| LiveCodeBench v6 | **80.0** | 77.1 | 72.0 | 52.0 | 44.0 | 29.1 |
| Codeforces Elo | **2150** | 1718 | 1659 | 940 | 633 | 110 |
| GPQA Diamond | **84.3** | 82.3 | 78.8 | 58.6 | 43.4 | 42.4 |
| SciCode | **43.0** | 40.0 | 38.0 | 24.0 | 21.0 | 21.0 |
| IFEval | **98.9** | 98.5 | 97.2 | 96.7 | 94.6 | 90.4 |

![주요 벤치마크 결과](/images/2026-07-11-gemma-4-technical-report/fig-p6.png)

숫자가 말한다:

- **AIME 2026 89.2%** — 이전 세대 27B가 20.8%였으니 4배 이상 도약. thinking mode가 수학 추론을 완전히 바꿨다.
- **Codeforces Elo 2150** — 이전 27B가 110이었다. 31B가 2150이라면 Candidate Master 경권. 오픈웨이트 31B 모델이 이 점수를 낸 건 인상적이다.
- **26B-A4B MoE**가 주목할 만하다 — 3.8B 파라미터만 활성화하는데 12B dense와 맞먹는 성능을 낸다. 추론 비용 대비 효율이 핵심 무기.
- **E4B(4.5B effective)**가 Gemma 3 27B(67.6 vs 69.4 MMLU Pro)에 근접한다. 온디바이스 모델이 이전 세대 대형 모델을 추격한 셈.

## 학습 인프라

TPU 기반으로 각 모델 크기별로 다른 칩을 배정했다:

| 모델 | TPU | 칩 수 | 데이터 shards | 시퀀스 | replica |
|---|---|---|---|---|---|
| E2B | v6e | 4,096 | 16 | 8 | 32 |
| E4B | v6e | 6,144 | 16 | 16 | 24 |
| 12B | v5p | 12,288 | 16 | 16 | 48 |
| 26B-A4B | v6e | 6,144 | 16 | 16 | 24 |
| 31B | v6e | 10,240 | 16 | 16 | 40 |

12B만 v5p를 쓰고 나머지는 v6e. 31B에 10,240칩, E2B에 4,096칩을 할당했다.

![학습 및 추론 구성](/images/2026-07-11-gemma-4-technical-report/fig-p9.png)

## 멀티모달: 텍스트·이미지·오디오를 한번에

모든 모델 크기에 비전 인코더와 오디오 인코더가 포함된다. 12B는 앞서 말한 대로 인코더 없이 raw patch를 직접 처리한다. STEM·멀티모달·long-context 벤치마크 전반에서 큰 폭으로 성능이 올랐다고 밝혔다.

인간 평가(Arena) 기준으로 "significantly larger" 모델과 맞먹는 수준이라고 한다. 정확히 어느 모델과 비교했는지는 숫자가 더 나와야 알 수 있겠지만, 방향성은 분명하다.

## 의미: "frontier 오픈웨이트"가 31B에서 가능해졌다

Gemma 4가 던지는 시그널은 세 가지다.

1. **오픈웨이트 31B로 frontier급 성능이 가능하다.** AIME 89.2%, MMLU Pro 85.2%는 1년 전만 해도 100B+ 클래스 모델의 영역이었다.
2. **MoE 4B 활성으로 12B급 성능.** 26B-A4B는 추론 비용 측면에서 실용적 대안이다. 3.8B만 쓰면서 12B dense와 비슷한 벤치마크를 낸다.
3. **온디바이스가 이전 세대 대형 모델을 추격한다.** E4B(4.5B)가 Gemma 3 27B에 필적하는 성능을 보인다. 로컬 추론의 실용성이 한 단계 올랐다.

Apache 2.0 라이선스로 풀렸으니, 연구자·개발자 누구나 가져다 쓸 수 있다. 구글이 오픈웨이트 생태계에서 얼마나 영향력을 확보할 수 있을지는 실제 파인튜닝·배포 사례가 쌓이면 더 명확해질 것이다.

![모델 성능 비교](/images/2026-07-11-gemma-4-technical-report/fig-p10.png)

---

**한 줄 요약:** 구글 Gemma 4는 2.3B~31B까지 5개 변형에 thinking mode·MoE·encoder-free 통합 아키텍처를 담았다. 같은 크기 대역에서 최상위권 성능, Apache 2.0 오픈웨이트.
