---
title: "Recursive Harness Self-Improvement: 에이전트 하네스를 스스로 진화시키는 루프"
date: 2026-07-21
draft: false
summary: "Sakana AI의 RHI(Recursive Harness Self-Improvement)는 에이전트 하네스를 prompt-level 명세로 표현하고, 자기 수정 이력에서 얻은 pairwise feedback으로 반복적으로 개선하는 방법입니다. 30개의 ML 연구 태스크에서 단 몇 번의 RHI 반복만으로 저비용 추론 에이전트의 성능 한계를 최대 추론 노력 설정보다 높게 끌어올리면서도 추론 비용을 최대 60% 절감했습니다."
tags:
  - agent
  - harness
  - LLM
  - automation
  - self-improvement
  - SakanaAI
categories:
  - AI논문리뷰
cover:
  image: "/images/2026-07-21-recursive-harness-self-improvement/fig-1-p1.png"
  alt: "RHI: Few-shot 반복으로 test-time scaling 성능 한계 상승"
  caption: "Figure 1: Few-shot RHI가 test-time scaling의 성능 한계를 끌어올리는 모습 (출처: 원 논문)"
  relative: true
---

## 핵심 한 줄 요약

> 에이전트 하네스(추론 시점 스캐폴드)를 prompt 수준에서 명세하고, **자기 실행 이력에서 얻은 pairwise feedback**으로 단 몇 번 반복해서 최적화하면 — 비싼 모델의 최대 추론 설정보다 더 높은 성능을 60% 더 적은 비용으로 달성할 수 있다.

## 배경: 모델-하네스 공진화(Model–Harness Co-evolution)

LLM 에이전트 시스템에서 "하네스(harness)"는 추론 시점에 모델을 감싸는 스캐폴드 — 시스템 프롬프트, 에이전트 루프 정의, 도구 호출 규약, 서브 에이전트 간 정보 흐름 구조 등을 포함합니다. 최근 모델-하네스 공진화 패러다임에서 하네스는 단순한 실행 틀 이상으로, 실행 궤적(trajectory)의 품질을 결정하는 데이터 생성 컴포넌트로 이해되고 있습니다.

문제는 **하네스 최적화가 사람의 수작업에 의존**한다는 점입니다. provider가 제공하는 스캐폴드를 지속적으로 업데이트하는 것은 비용과 노력이 많이 듭니다. 사용자가 직접 구성한 하네스 역시 task-specific하게 튜닝하기 어렵습니다.

## RHI(Recursive Harness Self-Improvement): 자기 반복으로 하네스를 진화시키다

Sakana AI가 발표한 **Recursive Harness Self-Improvement(RHI)**는 이 문제를 정면으로 다룹니다. 핵심 아이디어는:

1. **하네스를 prompt-level 명세로 표현**: 에이전트 루프 자체를 자연어 프롬프트로 서술합니다. 어떤 서브 에이전트가 있고, 어떤 순서로 호출하며, 중간 결과를 어떻게 전달할지를 프롬프트로 정의합니다.
2. **Pairwise feedback으로 반복 개선**: 이전 반복에서 생성된 하네스 버전들을 짝지어 비교하고, 어떤 변경이 성능 향상으로 이어졌는지 자동으로 분석합니다. 이 비교 결과를 다음 하네스 개정에 활용합니다.
3. **극소수 반복으로 수렴**: 30개의 합성 ML 연구 태스크(양적 금융, 로보틱스, 약학 도메인)에서 **단 2–3회 반복**만으로 충분한 개선을 달성합니다.

### 작동 방식

![RHI 전체 파이프라인](/images/2026-07-21-recursive-harness-self-improvement/fig-2-p6.png)
*Figure 2: RHI 전체 파이프라인. 반복 i에서 코딩 에이전트가 하네스 H(i)를 받아 태스크를 실행하고, 실행 궤적을 평가 에이전트가 분석하여 pairwise feedback을 생성한다. 이 피드백으로 다음 하네스 H(i+1)을 개정한다.*

RHI 프로세스를 단계별로 풀면:

- **초기 하네스 H⁰**: 범용 에이전트 루프 정의 (예: planner-coder-reviewer 구조)
- **실행**: 코딩 에이전트가 현재 하네스로 30개 태스크 실행
- **평가**: 각 태스크의 성공/실패를 기록하고, 서로 다른 하네스 버전 간 성능 차이를 분석
- **Pairwise feedback**: "버전 A에서는 서브 에이전트 간 데이터 전달이 명시적이었고, 버전 B에서는 암시적이었다. A가 12% 더 높은 성공률을 보였다" 식의 구체적 비교
- **하네스 개정**: 코딩 에이전트가 피드백을 받아 다음 버전의 하네스 프롬프트 작성

이 과정이 정보 흐름(information flow) 최적화로 수렴한다는 점이 RHI의 핵심 통찰입니다.

### 하네스 구조 분해

![RHI 하네스 분해](/images/2026-07-21-recursive-harness-self-improvement/fig-3-p9.png)
*Figure 3: RHI 하네스를 두 가지 주요 컴포넌트로 분해. 논문에서 하네스의 개선이 어디서 오는지를 체계적으로 분석한다.*

RHI가 최적화하는 하네스는 크게 두 영역으로 나뉩니다:

- **Context management**: 태스크 맥락, 이전 단계 결과, 오류 내역을 어떻게 서브 에이전트에게 전달할지
- **Inter-agent information flow**: 여러 서브 에이전트 간에 산출물을 어떻게 주고받을지

![하네스 프롬프트 구조](/images/2026-07-21-recursive-harness-self-improvement/fig-4-p10.png)
*Figure 4: prompt-represented 하네스 H(i)의 구조. 후보 에이전트, 역할 정의, 정보 흐름 규칙 등을 포함한다.*

## 실험 결과: 비용을 줄이면서 성능 한계를 높이다

RHI의 실험 결과는 인상적입니다. 30개의 합성 ML 연구 태스크(양적 금융, 로보틱스, 약학)에서:

### 핵심 숫자

| 지표 | 결과 |
|------|------|
| **추론 비용 절감** | 최대 **60%** |
| **저비용 에이전트의 성능 한계** | 최대 추론 노력(max reasoning effort) 설정 **초과 달성** |
| **반복 횟수** | 2–3회면 충분 |
| **태스크 도메인** | 양적 금융, 로보틱스, 약학 (30개 합성 ML 연구 태스크) |

![Sonnet 모델에서의 RHI 효과](/images/2026-07-21-recursive-harness-self-improvement/fig-5-p12.png)
*Figure 5: 2회 반복 후, RHI는 sonnet-4.6 test-time scaling의 경험적 한계를 상승시킨다.*

![Opus 모델에서의 RHI 효과](/images/2026-07-21-recursive-harness-self-improvement/fig-6-p13.png)
*Figure 6: 1회 반복 후, RHI는 opus-4.7 test-time scaling의 경험적 한계를 상승시킨다.*

### 왜 더 추론 비용을 안 들여도 성능이 오르는가?

RHI의 성능 향상은 더 긴 추론이 아니라 **더 나은 맥락 관리**에서 옵니다. 논문은 이를 정보이론적 가설로 정식화합니다:

- 하네스는 본질적으로 **태스크 관련 정보의 병목(channel)** 역할을 한다
- RHI는 이 병목의 처리량(information throughput)을 암시적으로 최적화한다
- 결과적으로 더 많은 토큰을 소모하지 않고도, 모델이 더 정확한 결정을 내릴 수 있다

이는 단순히 "프롬프트를 더 길게"가 아니라 **정보 흐름 구조 자체를 최적화**한다는 의미입니다.

## 의미와 시사점

RHI가 시사하는 바는 에이전트 시스템 설계에 있어 근본적인 전환점입니다:

1. **하네스도 최적화 대상이다**: 모델만 튜닝하는 시대를 지나, 모델을 감싸는 실행 환경 자체를 자동 최적화해야 할 때입니다.
2. **사람의 수작업 없이도 가능하다**: 단 몇 번의 자동 반복으로 task-specific 하네스를 만들 수 있습니다.
3. **비용 효율성**: 최대 추론 설정(max reasoning effort)을 쓰는 대신, 하네스 구조 개선으로 더 적은 토큰에 더 높은 성능을 달성할 수 있습니다.
4. **지속적 학습의 토대**: model-harness 공진화 패러다임에서 RHI는 하네스 측의 학습 루프를 담당합니다.

### 한계

- 30개의 **합성(synthetic)** ML 연구 태스크로 평가되었으므로, 실제 프로덕션 환경에서의 일반화는 추가 검증이 필요합니다.
- 도메인이 양적 금융, 로보틱스, 약학으로 제한되어 있어 더 넓은 태스크 유형에서의 효과는 미지수입니다.
- 하네스를 prompt-level로 표현해야 하므로, 코드 수준의 하네스 구조 변경(예: 새 도구 추가)은 다루지 않습니다.

## 더 실습해보고 싶은 분들께

에이전트 하네스 최적화, 루프 엔지니어링, 모델-하네스 공진화 같은 개념을 직접 실험해보고 싶다면 아래 두 가지를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 실제 에이전트 자동화 사례 50가지를 다루며, 하네스와 루프 설계의 실무 감각을 익히는 데 도움이 됩니다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프의 구조적 설계와 최적화를 체계적으로 배울 수 있는 강의입니다.

---

**논문 정보**
- 제목: Recursive Harness Self-Improvement
- 저자: Sakana AI 팀
- arXiv: [2607.15524](https://arxiv.org/abs/2607.15524)
- 발표: 2026년 7월 17일
