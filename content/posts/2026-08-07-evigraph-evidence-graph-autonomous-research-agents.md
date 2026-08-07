---
title: "EviGraph: 자율 연구 에이전트를 증거 그래프로 만들기"
date: 2026-08-07
tags:
  - ai-agent
  - autonomous-research
  - evidence-graph
  - llm
draft: false
description: "연구 에이전트가 주장을 실험으로 추적 가능하게 만드는 typed evidence graph 구조와 검증 루프를 정리했습니다."
---

자율 연구 에이전트가 논문을 쓸 때 가장 큰 문제는 "이 주장이 어디서 나왔는지 추적이 안 된다"는 겁니다. EviGraph는 연구 과정 전체를 typed evidence graph로 표현해서 이 문제를 풉니다.

연구를 순차 파이프라인 대신 노드-엣지 그래프 상태로 다루고, 매 단계마다 증거 체인을 검사하는 게 핵심입니다.

논문: [EviGraph: Evidence-Guided Autonomous Research Agents](https://arxiv.org/abs/2608.04738)

## 구조: 6개 노드 타입과 5개 엣지 타입

EviGraph는 연구 객체를 6가지 타입의 노드로 모델링합니다.

| 노드 타입 | 역할 |
|---|---|
| Problem | 연구 과제 경계 |
| Gap | 선행 연구의 한계 |
| Hypothesis | 검증 가능한 가설 |
| Experiment | 실험 프로토콜과 구현 |
| Finding | 실험에서 얻은 결과 |
| Claim | 논문 수준의 주장 |

엣지는 노드 간의 의존 관계를 정의합니다: identifies, motivates, tested-by, produces, supports.

![EviGraph 프레임워크 워크플로우](/images/2026-08-07-evigraph-evidence-graph-autonomous-research-agents/fig-1-p3.png)

하나의 Claim이 지워지면, 그 Claim을 지탱하던 Finding과 Experiment까지 함께 재검토 대상이 됩니다. 파이프라인에서는 이 연쇄 효과를 잡기 어렵구요.

## 검증 루프: 약한 노드 식별과 하위 노드 재생성

Graph Inspector가 그래프를 순회하면서 약한 노드(weak node)를 찾습니다. 예를 들어:

- Hypothesis가 Gap과 의미적으로 정렬되지 않음 (GAP_MISALIGNMENT)
- Experiment가 현재 Hypothesis를 실제로 테스트하지 않음
- Finding이 실험 기록과 불일치
- Claim이 Finding의 범위를 초과

약한 노드를 발견하면, 해당 노드에 의존하는 모든 하위 노드를 찾아 topological order로 재생성합니다. 중간에 체크포인트를 저장해서, 수정이 오히려 그래프를 악화시키면 롤백합니다.

![EviGraph 실행 트레이스 예시](/images/2026-08-07-evigraph-evidence-graph-autonomous-research-agents/fig-2-p7.png)

논문의 대표 사례에서 H1 가설이 GAP_MISALIGNMENT 판정을 받습니다. H1은 attention entropy에 집중하는데, 연구 Gap G1은 과도하게 복잡한 classification head 문제를 다루고 있었어요. 파이프라인에서는 둘이 문법적으로 연결되어 있어서 이 불일치가 통과됩니다. EviGraph는 의미 검사로 잡아냅니다.

## 증거 준비 게이트: 모든 주장이 추적 가능해야 논문 작성

논문 작성은 그래프가 "준비 완료(Ready)" 상태일 때만 시작됩니다. 준비 조건은:

1. 그래프가 스키마 유효
2. 최소 1개 이상의 retained Claim 존재
3. 모든 retained Claim에 대해 완전한 증거 체인 존재
4. 약한 노드가 0개

이 조건이 충족되지 않으면 Incomplete 상태로 종료하고, Paper Writer를 부르지 않습니다.

## 성능: ARC-Bench-ML Overall 86.45%, Claim Support Rate 40.19% 개선

ARC-Bench-ML(25개 ML 연구 주제)과 NanoResearch-20(20개 연구 과제, 7개 도메인)에서 평가했습니다.

| 지표 | AutoResearchClaw | NanoResearch | EviGraph |
|---|---|---|---|
| ARC-Bench-ML Overall | 60.37% | — | 86.45% |
| ARC-Bench Code Dev | 55% | — | 99% |
| ARC-Bench Code Exec | 57% | — | 88% |
| ARC-Bench Result Analysis | 62.2% | — | 79.4% |
| Claim Support Rate | 27% | 14.4% | 37.85% |
| Exp. Data Consistency | 53% | 96.15% | 87.73% |

Claim Support Rate은 논문 주장 중 연구 기록으로 추적 가능한 비율입니다. 27% → 37.85%로 40.19% 상대 개선했습니다.

Experimental Data Consistency는 보고된 실험 수치가 실제 실행 기록과 일치하는 비율입니다. EviGraph는 87.73%로 NanoResearch의 96.15%에는 못 미치지만, AutoResearchClaw의 53%보다는 훨씬 높습니다.

Result Analysis에서 62.2% → 79.4%로 크게 올라간 건, 가설-실험-결과-주장 간 관계를 명시적으로 유지한 효과로 보입니다.

## 정리

자율 연구 에이전트의 신뢰성 문제를 아키텍처로 풀었다는 점이 흥미롭습니다. 순차 파이프라인에서는 발견하기 어려운 의미적 불일치를 그래프 검사로 잡아내고, 체크포인트 기반 롤백으로 수정 실패를 안전하게 처리합니다.

근데 Alignment 점수가 NanoResearch의 8.8에 비해 6.6으로 낮습니다. 원래 과제 프레이밍에서 벗어나는 경향이 있다는 뜻이라, 후속 연구에서 보완이 필요해 보입니다.

코드는 공개되어 있고, qwen-3.6-plus를 백본으로 사용했습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
