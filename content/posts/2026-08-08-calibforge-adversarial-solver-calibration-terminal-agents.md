---
title: "CalibForge: 터미널 에이전트 훈련 데이터를 자동으로 만들고 검증하는 루프"
date: 2026-08-08
draft: false
description: "터미널 에이전트를 위한 훈련 태스크를 합성할 때, 솔버 행동을 피드백으로 써서 '배울 수 있는 영역'에 있는 태스크만 남기는 Adversarial Solver Calibration 방법을 정리했습니다."
tags:
  - agent
  - terminal-agent
  - coding-agent
  - LLM
  - harness
  - RL
  - automation
  - loop
  - tool-use
  - benchmark
authors:
  - conanssam
---

## 핵심 한 줄

터미널 에이전트 훈련 태스크를 자동 합성할 때, "실행 가능한가"만 확인하면 부족합니다. CalibForge는 솔버 에이전트들의 실제 pass/fail 행동을 피드백으로 삼아, 강한 모델은 풀고 약한 모델은 못 푸는 "학습 가능 영역(learnable zone)"에 있는 태스크만 남깁니다. 이렇게 만든 5,431개 태스크로 파인튜닝한 Qwen3.5-35B가 Terminal-Bench 2.0에서 47.57%를 기록했습니다.

## 왜 기존 방식이 문제인가

터미널 에이전트 훈련에는 "실행 가능하고 검증 가능한 태스크"가 필요합니다. 기존 합성 시스템(TermiGen, Endless Terminals, CLI-Gym 등)은 태스크를 만들고 구조 검사 + 자가 풀기(self-solving)로 검증합니다.

근데 이 검증은 "풀 수 있는가"만 알려줄 뿐, "적절한 난이도인가"는 알려주지 않습니다. 너무 쉬워서 모든 모델이 다 풀거나, 너무 어려워서 아무도 못 풀거나, 심지어 검증 코드가 깨져 있을 수도 있습니다.

CalibForge의 출발점은 이겁니다. 태스크의 학습 가치는 솔버 행동으로만 판단할 수 있다.

## CalibForge 작동 방식

![CalibForge 전체 파이프라인](/images/2026-08-08-calibforge-adversarial-solver-calibration-terminal-agents/fig-1-p1.png)

전체 흐름은 두 단계입니다.

### 1단계: 태스크 작성 및 검증

클루(clue)에서 출발합니다. 작성 에이전트가 웹 검색으로 구체적인 엔지니어링 문제를 찾습니다 — 버전별 호환성, 의존성 충돌, 설정 함정, 재현 가능한 엣지 케이스 등. 이걸 바탕으로 태스크 명령문, Dockerfile, 검증 테스트를 함께 만듭니다.

구조 검사: 필수 파일이 있는지, 빌드가 되는지, 초기 상태에서 테스트가 전부 실패하는지 확인합니다.

자가 풀기: 작성 에이전트가 격리된 샌드박스에서 직접 풀어봅니다. 풀리면 검증 통과.

### 2단계: 적대적 솔버 캘리브레이션

여기가 이 논문의 핵심입니다. 검증을 통과한 태스크를 솔버 에이전트들에게 풀게 합니다. 솔버들의 pass/fail 패턴을 보고 태스크를 유지할지, 수정할지, 버릴지 결정합니다.

두 가지 전략이 있습니다.

**멀티 솔버 캘리브레이션**: 서로 다른 모델 3개(DeepSeek-V4-Flash, GLM-5, Kimi K2.5)가 독립적으로 풉니다. 최소 한 개는 통과하고 최소 한 개는 실패해야 합니다. 전부 통과하면 너무 쉬운 거고, 전부 실패하면 너무 어렵거나 깨진 태스크입니다.

**대조 솔버 캘리브레이션**: 지정된 강한 솔버(DeepSeek-V4-Pro)는 통과하고 약한 솔버(DeepSeek-V4-Flash)는 실패해야 합니다. 이 조건이 안 맞으면 작성 에이전트가 피드백을 받고 태스크를 수정한 뒤 다시 검증합니다.

![CalibForge 파이프라인 상세](/images/2026-08-08-calibforge-adversarial-solver-calibration-terminal-agents/fig-2-p3.png)

수정 루프는 최대 50라운드까지 돕니다. 각 라운드에서 솔버 결과 + 전체 궤적을 작성 에이전트에게 줍니다. 작성 에이전트는 웹 검색으로 돌아가거나, 명령문/환경/검증 코드를 수정합니다.

핵심은 솔버 행동이 태스크 자체를 개선한다는 점입니다. 단순히 필터링하는 게 아닙니다. 논문 부록에 나온 실제 사례를 보면:

- 두 솔버가 다 통과했을 때 → 명령문에서 해결 경로를 너무 직접적으로 알려주고 있었다. 힌트를 제거하니 강한 솔버는 통과, 약한 솔버는 실패.
- 전부 실패했을 때 → 명령문의 비교 기준이 모호했다. 의미를 명확히 하니 2개는 통과, 1개는 실패.
- 역전(약한 놈이 통과, 강한 놈이 실패) → 검증 코드가 너무 경직되어 있었다. 검증을 일반화하니 정상적인 strong-pass/weak-fail 패턴.

### 캘리브레이션 효과

태스크 작성 + 검증만 한 버전(no solver) 대비 결과:

| 변형 | TB2 정확도 | Δ |
|---|---|---|
| 솔버 피드백 없음 | 22.47% | — |
| 단일 솔버 피드백 | 24.34% | +1.87 |
| 멀티 솔버 캘리브레이션 | 29.21% | +6.74 |
| 대조 솔버 캘리브레이션 | 31.09% | +8.62 |

단일 솔버 피드백보다 대조 캘리브레이션이 6.75pp 더 좋습니다. 궤적 수로 설명할 수 없는 겁니다 — 멀티 솔버는 no-solver보다 SFT 궤적이 더 적은데도 성능이 더 높습니다.

첫 솔버 프로브에서 대조 조건(strong-pass/weak-fail)을 만족하는 태스크는 19%에 불과했습니다. 수정 루프를 거치면 96%가 통과합니다. 즉 검증 통과 = 학습 가능이 아닙니다. 솔버 행동으로 캘리브레이션해야 진짜 학습 가치가 생깁니다.

## 메인 결과

| 모델 | TB2 Acc. | SWE-bench Pro | Doc2Repo |
|---|---|---|---|
| CalibForge-30B-A3B | 32.58% | 38.20% | 43.54% |
| CalibForge-35B-A3B | 47.57% | 44.32% | 48.77% |

![메인 결과 표](/images/2026-08-08-calibforge-adversarial-solver-calibration-terminal-agents/table-1-p7.png)

CalibForge-35B-A3B는 Terminal-Bench 2.0에서 가장 강한 베이스라인 대비 +6.75pp, SWE-bench Pro에서 44.32%, Doc2Repo에서 48.77%를 기록했습니다. 같은 백본(Qwen3.5-35B-A3B)을 쓰고 같은 티처(DeepSeek-V4-Pro)로 궤적을 증류했을 때, 태스크 소스만 바꿔도 이 격차가 납니다.

## 도메인 분포

![태스크 도메인 분포](/images/2026-08-08-calibforge-adversarial-solver-calibration-terminal-agents/fig-4-p8.png)

CalibForge 태스크는 데이터 처리, 파일/시스템, 웹/API, 패키지 관리, 테스트/CI 등 넓은 도메인을 커버합니다. 기존 합성 데이터셋이 특정 영역에 치우친 것과 대조적입니다.

## 5,431개 태스크의 규모

![태스크 통계](/images/2026-08-08-calibforge-adversarial-solver-calibration-terminal-agents/table-2-p9.png)

태스크당 평균 7개 검증 함수, 평균 2개 환경 의존성, 평균 362개 초기 파일이 들어갑니다. 단순한 커맨드라인 퍼즐이 아니라 실제 소프트웨어 엔지니어링 환경입니다.

## 왜 중요한가

이 논문이 말하는 건 단순합니다. 태스크 합성 시스템이 "실행 가능한 태스크를 많이 만들었다"로 끝나면 안 됩니다. 그 태스크가 실제로 모델을 가르치는지를 솔버 행동으로 확인해야 합니다.

이건 인간이 문제집을 낼 때랑 같습니다. 정답이 맞는지 확인하는 거랑, 학생 수준에 적절한지 확인하는 건 다른 문제입니다. CalibForge는 후자를 자동화한 겁니다.

코드와 데이터셋이 공개되어 있습니다:
- GitHub: https://github.com/AweAI-Team/CalibForge
- 데이터셋: https://huggingface.co/datasets/AweAI-Team/CalibForge

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
