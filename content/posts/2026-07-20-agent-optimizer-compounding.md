---
slug: 2026-07-20-agent-optimizer-compounding
title: "에이전트 최적화는 누적되는가 — Terminal-Bench 2.0에서 돌려본 세 가지 하네스 옵티마이저의 지옥"
source_url: https://arxiv.org/abs/2607.14004
date: 2026-07-20
tags:
  - agent
  - harness
  - optimization
  - LLM
  - continual-learning
  - automation
draft: false
---

## 한 줄 요약

대부분의 에이전트 최적화 논문은 "한 번 최적화했더니 점수가 올랐다"고 보고한다. 하지만 실제 배포 환경에서는 최적화를 반복해야 한다. **두 번째 최적화가 첫 번째 최적화의 성과를 망치지 않고 누적되는가?** RELAI의 새 연구는 Terminal-Bench 2.0으로 이 질문을 직접 테스트했다. 결과: 세 방법 중 하나(RELAI-VCL)만이 누적 개선을 달성했고, 나머지는 전이 실패 또는 정체를 보였다.

---

## 문제의식: 원샷 벤치마크의 함정

GEPA, Meta Harness, MIPROv2, Maestro… 최근 에이전트 하네스(프롬프트·도구·메모리·제어 코드)를 자동으로 최적화하는 방법이 쏟아지고 있다. 이들은 공통적으로 하나의 고정된 벤치마크에서 최적화하고, 점수가 오르면 "작동한다"고 선언한다.

하지만 production 에이전트는 한 번만 최적화되지 않는다. 새로운 실패 모드가 발견되면, 새로운 작업 유형이 추가되면, 다시 최적화를 수행한다. **이때 직전 라운드에서 얻은 개선이 유지되는가?** 이것이 본 논문의 핵심 질문이다.

> An optimizer that compounds should (i) produce updates from the first round that generalize at least somewhat to tasks it did not see during search, and (ii) continue to make progress in a second round of optimization without regressing on tasks it had already solved.

논문은 이를 **compounding question**이라 부른다.

---

## 평가 프로토콜: 2단계 지속 학습

![Phase 1 최적화 후 작업별 합격률](/images/2026-07-20-agent-optimizer-compounding/fig-2-p7.png)
*Figure 2: Phase 1 최적화 후 12개 작업별 합격률 — 세 방법 모두 베이스라인을 초과한다.*

설계는 깔끔하다:

1. **Phase 1**: 초기 작업 집합 T₁(12개 Terminal-Bench 2.0 하드 태스크)에서 각 옵티마이저에게 동일한 예산을 주고 최적화
2. **Transfer 평가**: Phase 1 결과물을 T₁∪T₂(22개)에서 평가 — T₂를 본 적 없이
3. **Phase 2**: T₁∪T₂ 전체에서 추가 최적화 예산 할당
4. **Final 평가**: T₁∪T₂에서 최종 합격률 측정

이렇게 하면 정적 최적화 강도, 전이 능력, 재최적화 능력을 분리해서 측정할 수 있다.

![주요 결과 표](/images/2026-07-20-agent-optimizer-compounding/table-1-p2.png)
*Table 1: 단계별 합격률 — RELAI-VCL이 모든 단계에서 1위*

---

## 세 옵티마이저, 세 가지 결말

### GEPA: Phase 1에 과적합

GEPA는 반성적 진화 검색(reflective evolutionary search)으로 프롬프트를 최적화한다. Phase 1에서는 70.8%로 가장 강력한 결과를 보인다. 하지만 T₂가 추가된 전이 평가에서 **54.5%로 베이스라인(56.8%) 아래로 추락**한다. Phase 1 작업에 맞춘 프롬프트 변화가 새로운 작업에서는 독이 된 것이다.

### Meta Harness: 전이는 잘 되지만 정체

Meta Harness는 에이전트 제안자(LLM 기반 코딩 에이전트)가 하네스 코드를 직접 수정하는 방식이다. Phase 1에서 66.6%, 전이 평가에서 68.2%로 **전이는 성공**한다. 하지만 Phase 2 재최적화에서 59.1%로 오히려 하락한다. 전이는 잘 되지만, 두 번째 최적화 라운드에서 막히는 것이다.

### RELAI-VCL: 유일하게 누적되는 최적화

![Phase 2 후 합격률](/images/2026-07-20-agent-optimizer-compounding/fig-4-p8.png)
*Figure 4: Phase 2 재최적화 후 22개 작업 합격률 — RELAI-VCL만이 지속적으로 개선된다.*

RELAI-VCL(Verifiable Continual Learning)이 세 방법 중 유일하게 전이와 재최적화 모두에서 개선을 보였다:

- Phase 1: **79.2%** (압도적 1위)
- Transfer: **72.7%** (유일하게 베이스라인 대비 양의 전이)
- Phase 2 Final: **77.3%** (추가 개선 달성)
- Lifelong Average: **76.4%**

![Lifelong Average 합격률](/images/2026-07-20-agent-optimizer-compounding/fig-5-p9.png)
*Figure 5: Lifelong Average — RELAI-VCL(76.4%) vs GEPA(66.0%) vs Meta Harness(64.6%) vs Baseline(58.7%)*

---

## 핵심 통찰: 회귀 제어가 루프 안에 있어야 한다

논문의 핵심 발견은 단순하다:

> Optimization gains compounded only when regression control was built into the optimization loop, providing an inductive bias against shortcut solutions that fail to generalize.

RELAI-VCL이 다른 두 방법과 근본적으로 다른 점은 **최적화 루프 안에 회귀 검사를 내장**한다는 것이다. 새로운 작업에서 점수를 올리면서 기존 작업에서 퇴보하는 후보를 거부한다. GEPA와 Meta Harness는 이런 제약 없이 탐색하므로, Phase 1 작업에 특화된 "지름길"을 찾기 쉽고 그 지름길은 새로운 작업에서 일반화되지 않는다.

이는 지속 학습(continual learning) 분야의 EWC(Elastic Weight Consolidation)와 유사하다. EWC가 모델 가중치에 대한 정규화라면, RELAI-VCL은 하네스 편집에 대한 제약이다.

---

## 왜 중요한가

이 논문이 중요한 이유는 **에이전트 최적화 분야의 평가 패러다임을 바꾼다**:

1. **정적 벤치마크 점수로는 부족하다**: 한 번의 최적화 결과만 보고 "작동한다"고 할 수 없다.
2. **Compounding이 진짜 지표다**: 반복 최적화가 가능해야 production에서 의미 있다.
3. **회귀 제어의 위치가 중요하다**: 사후 검증이 아니라 탐색 루프 안에 있어야 한다.

현재 대부분의 에이전트 최적화 논문과 제품(HALO, LangSmith Engine, Hermes 등)이 사후 검증에 의존한다. 이 논문은 그것으로는 충분하지 않음을 경험적으로 보인다.

---

## 더 실습해보고 싶은 분들께

에이전트 하네스 최적화, 지속 학습, 그리고 자동화된 에이전트 개선은 지금 가장 활발한 연구 영역 중 하나다. 직접 에이전트를 만들어보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 실제 에이전트 하네스와 도구 활용을 다루는 실전 가이드
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 최적화를 체계적으로 배우는 강의

---

## 논문 정보

- **제목**: Do Agent Optimizers Compound? A Continual-Learning Evaluation on Terminal-Bench 2.0
- **저자**: Wenxiao Wang, Priyatham Kattakinda, Soheil Feizi (RELAI.ai)
- **arXiv**: [2607.14004](https://arxiv.org/abs/2607.14004)
- **코드**: [github.com/relai-ai/Continual-Learning-Terminal-Bench](https://github.com/relai-ai/Continual-Learning-Terminal-Bench)
