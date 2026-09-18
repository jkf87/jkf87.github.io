---
title: "자율 연구 에이전트의 주장이 어디서 왔는지 추적하는 법 — EviGraph 구조 정리"
date: 2026-08-07
tags:
  - ai-agent
  - autonomous-research
  - evidence-graph
  - llm
draft: false
description: "연구 에이전트의 주장을 실험 기록까지 추적 가능하게 만드는 typed evidence graph와 검증 루프를 자동화 관점에서 정리함."
---

자율 연구 에이전트가 논문을 쓸 때 최대 문제는 주장의 출처가 추적 안 된다는 것임. EviGraph는 연구 과정 전체를 typed evidence graph로 표현해서 이걸 풂. 순차 파이프라인 대신 노드-엣지 그래프 상태로 연구를 다루고 매 단계 증거 체인을 검사하는 게 핵심임.

1. 구조부터. 연구 객체를 6개 노드 타입으로 모델링함. Problem은 연구 과제 경계, Gap은 선행 연구의 한계, Hypothesis는 검증 가능한 가설, Experiment는 실험 프로토콜과 구현, Finding은 실험 결과, Claim은 논문 수준의 주장임. 엣지는 identifies, motivates, tested-by, produces, supports로 의존 관계를 정의함.

![EviGraph 워크플로우](/images/2026-08-07-evigraph-evidence-graph-autonomous-research-agents/fig-1-p3.png)

2. 그래프로 만들면 얻는 첫 이점은 연쇄 효과 추적임. 하나의 Claim이 무너지면 그 Claim을 지탱하던 Finding과 Experiment까지 함께 재검토 대상이 됨. 순차 파이프라인에서는 이 연쇄를 잡기 어려웠음.

3. Graph Inspector가 그래프를 순회하며 약한 노드를 찾음. Hypothesis가 Gap과 의미적으로 안 맞는 GAP_MISALIGNMENT, Experiment가 현재 Hypothesis를 실제로 안 테스트하는 경우, Finding이 실험 기록과 불일치하는 경우, Claim이 Finding 범위를 초과하는 경우임.

4. 약한 노드를 발견하면 그에 의존하는 하위 노드 전부를 위상 정렬로 재생성함. 그리고 중간 체크포인트를 저장해서 수정이 오히려 그래프를 악화시키면 롤백함. 자동 수정에 안전장치를 다는 구조가 벤치마킹할 만함.

5. 대표 사례가 직관적임. H1 가설이 GAP_MISALIGNMENT 판정을 받음. H1은 attention entropy에 집중하는데 Gap G1은 과도하게 복잡한 classification head 문제였음. 파이프라인에선 둘이 문법적으로 연결돼 있어서 통과됐지만 EviGraph는 의미 검사로 잡아냄. 문법적 연결과 의미적 정렬은 다르다는 것임.

![실행 트레이스](/images/2026-08-07-evigraph-evidence-graph-autonomous-research-agents/fig-2-p7.png)

6. 증거 준비 게이트도 좋은 설계임. 논문 작성은 그래프가 Ready 상태일 때만 시작됨. 준비 조건은 스키마 유효, retained Claim 최소 1개, 모든 Claim에 완전한 증거 체인, 약한 노드 0개임. 조건이 안 채워지면 Incomplete로 종료하고 Paper Writer를 안 부름.

7. 결과. ARC-Bench-ML(25개 ML 주제)에서 Overall 86.45%. AutoResearchClaw의 60.37%와 큰 격차임. Code Dev 55%→99%, Code Exec 57%→88%, Result Analysis 62.2%→79.4%임.

8. 제일 중요한 지표는 Claim Support Rate임. 논문 주장 중 연구 기록으로 추적 가능한 비율임. 27%→37.85%로 40.19% 상대 개선됨. Experimental Data Consistency도 AutoResearchClaw의 53%보다 훨씬 높은 87.73%임. NanoResearch의 96.15%엔 못 미치지만 견고함.

9. Result Analysis가 크게 오른 건 가설-실험-결과-주장 관계를 명시적으로 유지한 효과로 보임. 관계를 암묵적 컨텍스트가 아니라 구조로 들고 있으면 분류·집계 품질이 같이 올라감.

10. 실무 채점. 이 구조는 연구 에이전트 말고도 쓸 데가 많음. 우리 자동화 파이프라인의 산출물(보고서, 분석, 요약)도 "주장→근거→원본 기록"의 체인을 그래프로 들고 있으면 검증 게이트를 만들 수 있음. 특히 근거 없는 주장 차단을 문법이 아니라 의미 정렬 검사로 해야 한다는 교훈이 핵심임.

11. 베낄 것 두 개. 첫째, 수정 시 체크포인트-롤백. 자동 개선 루프가 그래프를 악화시키는 걸 원천 차단함. 둘째, 준비 게이트. 산출 단계가 입력 상태가 충분할 때만 돌게 하는 것임. "어쨌든 결과물은 냄" 구조를 끊는 원칙임.

12. 한계. Alignment 점수가 NanoResearch의 8.8 대비 6.6으로 낮음. 원래 과제 프레이밍에서 벗어나는 경향이 있다는 뜻으로 후속 보완이 필요함. 그래프 구축·유지 비용도 만만치 않을 것임.

13. 그래도 방향은 유효함. 자율 에이전트의 신뢰성 문제를 모델 능력이 아니라 아키텍처로 푼 사례임. 주장의 추적 가능성을 구조로 강제하는 것이 에이전트 산출물의 품질을 결정한다는 것임.

원문: [arXiv:2608.04738](https://arxiv.org/abs/2608.04738)
