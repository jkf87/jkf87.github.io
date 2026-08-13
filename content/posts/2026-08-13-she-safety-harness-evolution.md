---
title: "SHE: Trajectory-driven Safety Harness Evolution for LLM Agents — 에이전트 안전 하네스의 자동 진화"
date: 2026-08-13
tags:
  - agent
  - harness
  - LLM
  - safety
  - self-evolution
  - tool-use
  - security
  - attribution
  - loop
  - automation
draft: false
---

## 개요

Qu et al.(2026)은 LLM 에이전트의 안전성이 모델 가중치뿐 아니라 에이전트 하네스(harness)에 의존한다는 점에 주목한다. 하네스는 컨텍스트 관리, 메모리, 도구 접근, 권한 제어, 런타임 상태를 관리하는 비매개변수 실행 계층이다. 기존 안전 메커니즘(SafeHarness, LlamaFirewall, NeMo Guardrails 등)은 배포 후 고정되어 새로운 위험에 적응하지 못한다.

SHE(Safety Harness Evolution)는 하네스를 편집 가능한 4종 아티팩트로 분해하고, 실행 궤적에서 안전 실패를 진단·귀인하여 해당 아티팩트만 국소 수정하는 진화 루프를 제안한다.

Shanghai AI Lab, Fudan University, SJTU, HKUST 공동 연구이며 코드를 공개했다: [github.com/RainbowQTT/SHE](https://github.com/RainbowQTT/SHE)

## 방법론

### 하네스 아티팩트 분해

SHE는 하네스 H를 다음 네 가지 아티팩트의 튜플로 정의한다:

H = (P_sys, R_bank, M_safe, Q_tool)

| 아티팩트 | 역할 | 제어 방식 |
|---|---|---|
| System Prompt (P_sys) | 전역 안전 행동 규약 | 텍스트 명세 |
| Rule Bank (R_bank) | 위험 분류 + 개입 규칙 | 조건부 액션 (allow/warn/block/sanitize/judge) |
| Safety Memory (M_safe) | 미해결 실패 경험 저장 | 텍스트 명세 |
| Tool Policy (Q_tool) | 도구 권한 및 런타임 강제 | 조건부 액션 |

![SHE 프레임워크 개요](/images/2026-08-13-she-safety-harness-evolution/fig-2-p4.png)

### 진화 루프

각 진화 라운드 k에서:

1. 현재 best 하네스로 롤아웃 수행 (Agent-SafetyBench 15 태스크 × 6 공격 조건 × 2회 = 180 궤적)
2. 안전 관련 실패 식별 (RiskRelevant)
3. 구조화 위험 진단 — harm domain, attack surface, failure mode 3차원 분류
4. 아티팩트 라우팅 — 진단 결과 → 수정 대상 아티팩트 결정
5. 국소 편집 (bounded edit) — 라우팅된 아티팩트만 수정
6. 유효성 검사 + best-so-far 선택 — 안전성·유용성 jointly 평가

![SHE 동기](/images/2026-08-13-she-safety-harness-evolution/fig-1-p2.png)

총 20라운드 수행. R00, R03, R04, R05, R17에서만 수용(accept)되었다. 나머지 라운드의 후보는 안전성·유용성 기준을 충족하지 못해 기각(reject)되었으며, 기각된 후보는 부정 증거(negative evidence)로 보존된다.

## 실험 결과

### Agent-SafetyBench (held-in)

| 지표 | Non-evolved | SafeHarness | SHE |
|---|---|---|---|
| 평균 ASR | 8.6% | 17.1% | 5.5% |
| Clean UBR | 25.7% | — | 19.8% |
| 평균 UA | 33.5% | 31.6% | 47.6% |

SafeHarness 대비 ASR 3.1× 감소, UA 50.6% 향상.

### AgentHarm (held-out 일반화)

| 지표 | Non-evolved | SHE |
|---|---|---|
| Harm Score | 19.8% | 9.8% |
| Harm Refusal | 78.4% | 86.4% |

진화에 사용되지 않은 AgentHarm 태스크에서도 안전성 향상이 확인되었다.

### 크로스모델 전이

![크로스모델 전이](/images/2026-08-13-she-safety-harness-evolution/fig-3-p7.png)

DeepSeek-V3.2 기반으로 진화한 하네스를 Kimi K2.6, GLM-5.2에 적용해도 ASR이 감소한다. 모델 교체 시 진화를 다시 수행할 필요가 없다.

### Ablation

![진화 프레임워크 ablation](/images/2026-08-13-she-safety-harness-evolution/fig-4-p8.png)

아티팩트 라우팅 제거, best-so-far 선택 제거 시 ASR이 유의하게 상승한다. 진단 정보 없는 무작위 편집, 전체 아티팩트 동시 수정보다 국소 수정이 효과적이다.

### 구체 사례

![앱 권한 획득 공격 진화 사례](/images/2026-08-13-she-safety-harness-evolution/fig-5-p9.png)

Tool output에 악성 명령이 주입되는 공격 시나리오에서, 비진화 하네스는 명령을 실행한다. SHE는 실패를 tool policy로 라우팅하고, tool output 기반 명령 차단 규칙을 추가한다.

## 크로스모델 전이 테이블

![크로스모델 전이 결과 테이블](/images/2026-08-13-she-safety-harness-evolution/table-3-p9.png)

## 결론

SHE는 하네스 안전을 정적 배포에서 궤적 기반 진화로 전환한다. 주요 특성:

- 모델 가중치 불변, 하네스 아티팩트만 진화
- 기능적 분해로 국소 수정 가능
- 진화 규칙의 크로스모델 전이
- SafeHarness 대비 ASR 3.1× 감소, UA 50.6% 향상

한계로는 진화에 GPT-5.5를 진단/편집 모델로 사용한다는 점, Agent-SafetyBench 15개 태스크 분할에 대한 의존성, 그리고 안전성과 유용성 사이의 트레이드오프가 라운드별로 변동한다는 점이 있다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [arXiv:2608.09885](https://arxiv.org/abs/2608.09885)
코드: [github.com/RainbowQTT/SHE](https://github.com/RainbowQTT/SHE)
