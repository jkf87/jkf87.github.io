---
title: "하네스를 자연선택으로 진화시키면 모델 안 바꿔도 성적이 오른다 — DarwinX 레시피"
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
description: "Salesforce DarwinX 분석. 단일 계통 keep-best 방식의 경로 의존성과 교차 작업 간섭을 집단 선택과 재조합으로 해결. 모델 가중치 동결 상태로 Terminal-Bench 2.1 84.7%, 진화한 하네스의 교차 벤치마크 전이까지 확인."
---

모델 가중치를 얼린 채 하네스만 진화시켜서 Terminal-Bench 2.1 avg@5 84.7%, WebArena-Infinity 실제 작업 pass@1 93.0%를 달성한 [연구](https://arxiv.org/abs/2608.07545)가 Salesforce에서 나옴. 하네스 자가진화의 두 고질병을 집단 수준의 자연선택으로 푸는 레시피가 인상적이라 정리함. 앞서 정리한 여러 하네스 진화 연구들의 문제의식이 여기서 한 덩어리로 합쳐지는 느낌임.

1. 기존 자가진화의 실패 모드 두 개가 출발점임. SICA, DGM 같은 방식은 단일 계통에서 keep-best로 동작하는데, 여기서 경로 의존성이 생김. 초반 편집이 이후 검색 방향을 고정시켜서 성능이 정체기에 빠지는 것. 그리고 교차 작업 간섭. 한 작업군을 개선하는 편집이 다른 작업군에서 조용히 회귀를 유발함. 작업 분포가 넓을수록 심해짐. 앞서 본 Regression Tax와 누적 개선 연구가 지적한 것과 같은 문제들이 단일 계정 구조의 한계로 정리돼 있음.

![4개 벤치마크 성능](/images/2026-08-13-winx-darwinx-harness-natural-selection/fig-1-p2.png)

2. 핵심 선택 규칙은 preserve-and-extend 계약임. 자식 변종이 부모가 풀던 작업을 잃지 않으면서(회귀 ≤ δ) 새로운 작업을 추가로 풀어야(순이득 > 0) 다음 세대의 부모가 됨. 측정은 avg@k 기반이고 벤치마크 자체의 검증기를 써서 gold solution이나 수동 선정이 없음. 회귀 제어를 세대 선택의 계약으로 승격시킨 것. 이건 내 스킬 개선 루프에도 그대로 적용되는 규칙임. 새 작업을 풀게 하는 수정은 많은데 기존 작업을 지키는 조건을 같이 못 박아야 간섭이 안 생김.

![선택 루프](/images/2026-08-13-winx-darwinx-harness-natural-selection/fig-2-p5.png)

3. 학습 신호는 세 종류를 하네스 편집으로 변환함. 실패한 궤적에서 누락된 능력을 진단하는 실패 유도, 참조 솔버의 성공 궤적을 접근법으로 증류하는 교사 유도(성공 롤아웃이 없는 작업용), 에이전트 자신의 성공/실패 궤적을 비교하는 자기 유도(성공/실패 혼재 작업용). 상황에 따라 신호를 고르는 게 아니라 세 가지를 갖춰두는 게 포인트임.

4. 집단 아카이브와 재조합이 두 번째 축임. 모든 변종을 아카이브에 보관하고, 개선자, 중립, 스테핑 스톤(진부분집합이지만 고유한 해 보유), 보관 노드로 분류함. 서로 다른 계통에서 보완적인 작업을 푸는 전문가 변종들이 발견되면 additive edit을 병합해서, 병합된 자식이 부모들의 해집합 합집합을 커버하면 유지함. 앞서 본 EvolveNet의 합병이 이기는 논리와 같은 결론이 다른 구조로 도출된 것. 단일 최강자를 뽑는 게 아니라 전문가를 합치는 게 이김.

![세대별 연산자](/images/2026-08-13-winx-darwinx-harness-natural-selection/fig-3-p7.png)

5. 결과. Terminal-Bench 2.1에서 베이스 77.0%가 DarwinX로 83.2%, 더 강한 베이스에서 84.7%. 스킬 번들 분석에서 검증/계약 스킬이 주요 기여를 했다는 게 앞선 보상 신호 신뢰성 논의와 연결됨. 클러스터별로도 numerical ML, low-level systems, bio/assembly, parsing/text tools, database 전반에 걸쳐 상승해서 특정 영역 오버핏이 아님.

6. 일반화 검증이 세 방향으로 돼 있어서 신뢰가 감. 진화에 안 쓴 held-out 작업(TerminalWorld)에서 68.3%로 모든 오프더셸프 에이전트를 앞섬. 합성 intent로만 진화하고 실제 작업에서 평가하니 WebArena-Infinity가 43.5%에서 93.0%로 오름. 그리고 Terminal-Bench에서 진화한 하네스를 SWE-bench Verified에 그대로 옮겨도 유효함. 인도메인 피드백 없이 교차 벤치마크 전이가 된 건 벤치마크 특화 튜닝이 아니라 일반 에이전트 능력이 진화했다는 뜻임.

7. 내 적용 결론. 첫째, 하네스·스킬 변형을 하나만 유지하지 말고 여러 변종을 아카이브로 보관하고 역할을 분류할 것. 둘째, 선택 기준은 preserve-and-extend, 순이득만 보지 말 것. 셋째, 보완적인 전문가 변형을 발견하면 병합을 시도할 것. 하네스가 진화의 단위라면 평가 컴퓨팅이 곧 에이전트 능력이라는 명제가 이 논문의 남기는 한 줄임. 모델 예산을 못 늘리는 상황에서 진화 예산은 늘릴 수 있다는 것.

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』와 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 강의에서 하네스와 진화 루프 설계를 다룸.
