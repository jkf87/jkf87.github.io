---
title: "DarwinX: 하네스를 자연선택으로 진화시키는 코딩 에이전트"
slug: 2026-08-13-winx-darwinx-harness-natural-selection
date: 2026-08-13
tags:
  - agent
  - harness
  - LLM
  - self-evolution
  - natural-selection
  - coding-agent
  - Salesforce
  - loop
source: arxiv
source_url: https://arxiv.org/abs/2608.07545
authors:
  - conanssam
draft: false
cover:
  relative: true
  name: fig-1-p2.png
---

## 요약

Salesforce AI Research의 DarwinX(arXiv:2608.07545)는 코딩 에이전트의 하네스를 집단 수준의 자연선택으로 진화시키는 프레임워크입니다. 모델 가중치를 동결한 상태에서 하네스만 편집하여 Terminal-Bench 2.1 avg@5 84.7%, WebArena-Infinity 실제 작업 pass@1 93.0%를 달성했습니다. 진화한 하네스는 SWE-bench Verified에 그대로 옮겨도 효과가 유지됩니다.

원문: [DarwinX: Evolving Agent Harnesses Through Natural Selection (arXiv:2608.07545)](https://arxiv.org/abs/2608.07545)

![](/images/2026-08-13-winx-darwinx-harness-natural-selection/fig-1-p2.png)

Figure 1: 모델 가중치 동결 상태에서 하네스만 진화시킨 결과. 4개 벤치마크에서의 성능.

## 기존 자가진화의 두 가지 실패 모드

SICA, DGM 같은 자가진화 에이전트는 단일 계통(lineage)에서 keep-best 방식으로 동작합니다. Robeyns et al. (2025)가 보고한 실패 모드는 다음과 같습니다.

경로 의존성(path dependence)은 초반 편집이 이후 검색 방향을 고정시켜 성능이 평탄기에 진입하는 현상입니다. 교차 작업 간섭(cross-task interference)은 한 작업군을 개선하는 편집이 다른 작업군에서 조용히 회귀를 유발합니다. 작업 분포가 넓을수록 간섭이 심해집니다.

DarwinX는 집단 수준의 선택과 재조합으로 이 두 문제를 해결합니다.

## preserve-and-extend 계약

자식 변종이 부모가 풀던 작업을 잃지 않으면서 새로운 작업을 추가로 풀어야 한다는 것이 DarwinX의 핵심 선택 규칙입니다. 수식으로 표현하면 순이득 g(c) > 0 이고 회귀 R(c) ≤ δ 입니다.

이 조건을 통과한 변종만 다음 세대의 부모가 될 수 있습니다. 모든 측정은 avg@k 기반이고, 벤치마크 자체의 검증기를 사용합니다. gold solution이나 수동 선정은 없습니다.

![](/images/2026-08-13-winx-darwinx-harness-natural-selection/fig-2-p5.png)

Figure 2: DarwinX의 선택 루프. preserve-and-extend 계약, 대체 계통 아카이브, 세대 간 공유 메모리.

## 학습 신호 구성

DarwinX는 세 가지 증거를 하네스 편집으로 변환합니다. 모델 가중치는 변경하지 않습니다.

| 신호 유형 | 설명 | 적용 시점 |
|---|---|---|
| 실패 유도 (∇) | 실패한 궤적에서 누락된 능력 진단 | 일반적인 돌연변이 |
| 교사 유도 (π*) | 참조 솔버의 성공 궤적을 접근법으로 증류 | 성공 롤아웃이 없는 작업 |
| 자기 유도 (AA) | 에이전트의 성공/실패 궤적 비교 | 성공/실패가 혼재한 작업 |

## 집단 아카이브와 재조합

모든 변종은 아카이브에 보관됩니다. 개선자는 부모의 해집합을 포함하면서 확장하고, 중립은 동일하고, 스테핑 스톤은 진부분집합이지만 고유한 해를 보유하고, 보관 노드는 일부 해를 교환하면서 고유한 해를 보유합니다.

서로 다른 계통에서 보완적인 작업을 푸는 전문가 변종들이 발견되면, DarwinX는 그 additive edit을 병합합니다. 병합된 자식이 부모들의 해집합 합집합을 커버하면 유지됩니다.

![](/images/2026-08-13-winx-darwinx-harness-natural-selection/fig-3-p7.png)

Figure 3: 세대별 연산자. 돌연변이 루프, 변종 분류, 병합 연산자.

## Terminal-Bench 2.1 결과

| 구성 | avg@5 |
|---|---|
| Monet (base) | 77.0% |
| Monet (DarwinX), matched base | 83.2% |
| Monet (DarwinX), stronger base | 84.7% |

스킬 번들 분석(ablation)에서 검증/계약 스킬이 주요 기여를 합니다. 클러스터별로 보면 numerical ML, low-level systems, bio/assembly, parsing/text tools, database/data 작업 영역 전반에 걸쳐 avg@5가 상승합니다.

## TerminalWorld held-out 일반화

진화에 사용하지 않은 held-out 작업에서 68.3%를 달성했습니다. 모든 오프더셸프 에이전트보다 앞섭니다.


## WebArena-Infinity 합성-실제 일반화

합성 intent로만 진화하고 실제 작업에서 평가했을 때 pass@1이 43.5%에서 93.0%로 상승했습니다. 감사 결과도 클린합니다.

## SWE-bench Verified 교차 전이

Terminal-Bench 2.1에서 진화한 하네스를 SWE-bench Verified에 그대로 적용했습니다. 인도메인 피드백 없이도 유효합니다. 벤치마크 특화 튜닝이 아닌 일반 에이전트 능력의 진화를 시사합니다.

## 논의

DarwinX는 하네스 자가진화에서 path dependence와 cross-task interference를 동시에 해결하는 집단 선택 레시피입니다. 모델 가중치를 변경하지 않고 4개 벤치마크에서 일관된 향상을 보였으며, 진화한 하네스의 교차 벤치마크 전이가 확인되었습니다. 하네스가 진화의 단위라면 평가 컴퓨팅이 곧 에이전트 능력이라는 명제가 성립합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
