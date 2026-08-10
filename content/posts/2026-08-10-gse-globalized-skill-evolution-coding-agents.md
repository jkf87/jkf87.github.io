---
title: "GSE: 코딩 에이전트 스킬의 전역 진화 프레임워크"
date: 2026-08-10
tags:
  - agent
  - skill-evolution
  - coding-agent
  - LLM
  - harness
  - software-engineering
  - test-generation
  - bug-filtering
  - self-evolution
  - loop
---

## 개요

GSE(Globalized Skill Evolution)는 코딩 에이전트의 스킬 뱅크를 전역 최적화 관점에서 진화시키는 프레임워크입니다. Tianjin University와 Tsinghua 연구팀이 제안했으며, arXiv 2608.06153에 게재되었습니다.

## 문제 정의

기존 스킬 진화 기법(Live-SWE-agent, Trace2Skill 등)은 개별 실행 궤적에서 국소적 업데이트를 생성하여 스킬 뱅크에 직접 반영합니다. 이 방식에는 두 가지 문제가 있습니다.

1. **호환성 문제**: 한 스킬의 수정이 다른 스킬의 전제를 훼손할 수 있음
2. **과적합 문제**: 특정 궤적에 특화된 업데이트가 다른 작업에서 회귀를 유발

## 방법론

### 스킬 관계 그래프 (SRG)

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/fig-1-p4.png)

스킬 뱅크를 방향 그래프 G=(V,E)로 모델링합니다. 노드는 스킬, 엣지는 세 가지 관계 타입(dependency, co-usage, conflict)을 나타냅니다.

업데이트 생성 시 SRG를 참조하여 연관 스킬에 미치는 영향을 추론하고, 일관성을 유지하기 위한 보조 진화 제안을 함께 생성합니다.

### 진화 제안 DSL

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/fig-2-p6.png)

진화 제안은 DSL로 구조화되며, operation, target skill, content, rationale, expected effect를 포함합니다.

### 클러스터 기반 스킬 일반화

1. 검증된 제안을 클러스터링하여 공통 능력 패턴 식별
2. 클러스터 내 제안을 통합하여 상위 수준 스킬 생성
3. 과거 케이스에 대한 리플레이 검증으로 회귀 방지

## 실험

### RQ1: 버그 발생 테스트 생성

- 데이터: Java 108 버그, 9개 오픈소스 프로젝트 (Multi-SWE-Bench 기반)
- 에이전트: OpenHands, mini-SWE-agent

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/fig-3-p11.png)

| 설정 | OpenHands F1 | mini-SWE-agent F1 |
|---|---|---|
| 베이스 | 0.08 | 0.28 |
| Human Skills | 0.16 | 0.26 |
| Live-SWE-agent | 0.22 | 0.29 |
| Trace2Skill | 0.19 | 0.29 |
| GSE | 0.31 | 0.38 |

정밀도 6.1%~34.1%, 재현율 31.8%~180.0% 개선.

### RQ2: 오탐 버그 리포트 필터링

- 데이터: IndustrialBugs (ByteDance, 500건, 8개 프로덕션 저장소)

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/table-2-p11.png)

정밀도 15.4%~96.4%, 재현율 13.1%~19.8% 개선.

### RQ3: 컴포넌트 기여도

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/table-3-p12.png)

SRG 제거 시 F1: 0.31→0.27 (테스트), 0.70→0.59 (필터링)
일반화 제거 시 F1: 0.31→0.27 (테스트), 0.70→0.54 (필터링)

### RQ4: 비용 분석

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/table-4-p13.png)

진화 비용: 케이스당 401.55K 토큰 (Trace2Skill 대비 12.28% 증가)
실행 비용: 케이스당 593.21K 토큰 (기준 대비 21.2% 증가, 타 방법 대비는 감소)

### 산업 배포

![](/images/2026-08-10-gse-globalized-skill-evolution-coding-agents/table-5-p14.png)

내부 상용 에이전트: F1 0.43 → 0.71 (61.4% 개선)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고문헌

Yang, C., Tian, J., Wang, Z., Liu, X., Ye, M., & Chen, J. (2026). Learning Globally Reusable Skills for Coding Agents. arXiv:2608.06153.
