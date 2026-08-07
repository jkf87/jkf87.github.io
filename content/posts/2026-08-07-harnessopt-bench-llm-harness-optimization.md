---
title: "HarnessOpt-Bench: Evaluating LLMs at Harness Optimization — 벤치마크 분석"
publishDate: 2026-08-07
tags:
  - agent
  - harness
  - LLM
  - benchmark
  - evaluation
  - ScaleAI
  - self-improvement
  - automation
  - loop
  - tool-use
---

## 개요

ScaleAI는 2026년 8월 6일, LLM이 다른 LLM 에이전트의 하네스(프롬프트, 도구, 제어 흐름, 메모리, 오케스트레이션 코드)를 자동으로 최적화하는 능력을 측정하는 벤치마크 HarnessOpt-Bench를 발표했다 (arXiv:2608.06301).

하네스 최적화는 일반적인 코드 최적화와 평가 비용 측면에서 본질적으로 다르다. 코드 정답은 단위 테스트로 저렴하게 검증되지만, 하네스 변경의 효과는 stochastic한 에이전트를 여러 케이스에서 반복 실행해야 측정할 수 있어 비용이 높다. HarnessOpt-Bench는 이러한 특성을 반영한 최초의 통합 평가 프로토콜을 제공한다.

## 벤치마크 프로토콜

HarnessOpt-Bench의 프로토콜은 다음 요소로 구성된다:

- 후보 하네스 H: 실행 가능한 코드베이스. prompt, tool definition, memory, control flow 등의 의미적 분할 없이 전체가 수정 대상
- 불변값 θ = (M, E, V): 사용 가능한 모델 M, 환경 E, 검증자 V. 옵티마이저가 변경할 수 없는 고정값
- 데이터 분할: 개발(𝒟_dev), 검증(𝒟_val), 테스트(𝒟_test)의 비중첩 분할. 테스트 분할은 검색 중 접근 불가
- 예산 B: 파티션당 100회 평가 호출, 4패스 전체 케이스 통과, 타겟 모델 토큰 한도
- 목적 함수: normalized gain g = (E_θ(H⁺) − E_θ(H₀)) / (1 − E_θ(H₀))

신뢰 실행 환경은 VeRO 인프라를 기반으로 구축되었으며, 옵티마이저 샌드박스와 평가 서버를 분리하여 접근 권한과 예산을 강제한다.

![](/images/2026-08-07-harnessopt-bench-llm-harness-optimization/fig-1-p2.png)

## 실험 구성

### 작업

| 작업 | 도메인 | Seed 상태 | 타겟 모델 |
|---|---|---|---|
| OfficeQA | 문서 QA | competent (~130줄) | pinned |
| BrowseComp-Plus | 딥 리서치 | competent | pinned |
| Terminal-Bench | 터미널 사용 | competent | pinned |
| GAIA | 범용 에이전트 | non-functional stub | pinned |

각 작업은 |M| = 1 (단일 타겟 모델)을 사용하며, seed는 측정 가능한 중간 성능을 보이도록 선택되었다.

### 옵티마이저

5개 프론티어 모델 (GPT 2종, Claude Opus 2종, Kimi 1종)을 공용 코딩 하네스와 각각의 네이티브 하네스 양쪽에서 평가했다. 총 111개의 scored run을 수집했다.

## 주요 결과

### RQ1: 모델이 코딩 하네스보다 더 크게 구분된다 (Figure 2)

- 작업·하네스 고정 후 모델 변경 시: gain 평균 0.142 이동
- 작업·모델 고정 후 하네스 변경 시: gain 평균 0.079 이동
- 모델 효과가 하네스 효과의 약 1.8배

![](/images/2026-08-07-harnessopt-bench-llm-harness-optimization/fig-2-p4.png)

### RQ2: 모델 릴리즈 간 민감도 (Figure 3)

OfficeQA에서 두 릴리즈 시리즈를 추적한 결과:

- GPT 5 릴리즈: +0.03 → +0.49 단조 증가, 4단계 중 3단계가 해상도 밴드 초과
- Claude Opus 5 릴리즈: +0.37 ~ +0.59, 비단조적이나 첫-끝 차이가 해상도 밴드 초과

### RQ3: 네이티브 하네스의 일관된 우위는 없다

20개 모델-작업 쌍에서 공용 하네스 11승, 네이티브 하네스 9승. GPT 모델에서는 네이티브(codex)가 우세했으나 Claude와 Kimi에서는 유의미한 차이가 없었다.

### 탐색 행태 분석 (Figure 4)

8가지 하네스 레버(prompt, context management, step cap, retry/timeout, tool schema, answer extraction, retrieval policy, reasoning effort)에 대한 탐색 폭과 gain의 상관:

- 레버 커버리지 vs gain: Spearman ρ = +0.34 ~ +0.88 (모든 작업에서 양수)
- Trace 읽기 비율 vs gain: ρ = −0.31 ~ −0.64 (모든 작업에서 음수)
- 상세 trace 요청: 111개 셀 중 7개만 16회 요청

![](/images/2026-08-07-harnessopt-bench-llm-harness-optimization/fig-4-p9.png)

### 예산 소비 패턴

- 중위 옵티마이저: 호출 8회 (4%), 케이스 예산 82% 소진
- 100개 셀 중 55개가 최소 한 파티션의 케이스 예산 전부 소진
- 평가 호출 한도가 아닌 실제 케이스 실행 횟수가 병목

### 검증-테스트 갭

대부분의 실행에서 검증 최고 점수가 테스트 점수보다 높다. held-out 테스트 분할의 필요성을 확인한다.

### GAIA에서의 하네스 효과 (Figure 5)

GAIA는 코딩 하네스 축이 4레벨 이상인 유일한 작업이다. 하네스 랭크가 모델에 따라 교차하며, 어떤 하네스도 모든 모델에서 일관되게 우세하지 않다. 네이티브 하네스 이점은 GPT 모델에 집중되어 있다.

![](/images/2026-08-07-harnessopt-bench-llm-harness-optimization/fig-5-p10.png)

## 논의

HarnessOpt-Bench는 하네스 최적화 능력을 재현 가능한 평가 대상으로 정의한다. 현재 프론티어 모델은 이 능력을 보유하고 있으나, 작업 간 분산이 크고 중간 순위 모델 간 구분은 해상도 밴드 이내인 경우가 많다. 모델 릴리즈가 거듭될수록 이 능력은 향상되고 있으며, 넓은 탐색이 gain과 양의 상관이 있다는 발견은 실용적 시사점을 제공한다. 후속 연구에서는 seed 난이도를 체계적으로 변화시키고, 언어/런타임/아키텍처 일반화를 검증할 필요가 있다.

ScaleAI는 하네스 최적화 능력을 재현 가능한 평가 대상으로 정의하며, 이 능력을 갖춘 모델이 다음 프론티어라고 요약한다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고자료

- 논문: [HarnessOpt-Bench: Evaluating LLMs at Harness Optimization](https://arxiv.org/abs/2608.06301) (ScaleAI, 2026-08-06)
- 관련 연구: VeRO [Ursekar et al.], MetaHarness [Lee et al.], ShinkaEvolve, GEPA, ADAS, STOP, AFlow
