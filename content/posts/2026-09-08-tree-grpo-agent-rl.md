---
title: "같은 예산으로 롤아웃 1.5배, 스텝 단위 신호까지 공짜로 — Tree-GRPO 정리"
date: 2026-09-08
draft: false
tags:
  - agent
  - reinforcement-learning
  - tree-search
  - grpo
  - post-training
description: "Tree-GRPO(ICLR 2026, arXiv:2509.21240)는 에이전트 RL 롤아웃을 체인 대신 스텝 단위 트리로 샘플링해서 같은 토큰·툴콜 예산으로 약 1.5배 롤아웃을 얻고, 결과 보상만으로 스텝 단위 선호학습 신호를 만든다. 11개 데이터셋에서 GRPO 대비 최대 69% 상대 개선을 정리했다."
---

## 결론 먼저

Tree-GRPO(Tree-based Group Relative Policy Optimization, arXiv:2509.21240, ICLR 2026, Alibaba AMAP)는 <span style="background-color: #fff59d"><strong>에이전트 RL의 롤아웃을 독립적인 체인 대신 트리 탐색으로 뽑고, 트리 노드를 Thought-Action-Observation 스텝 단위로 잡는 방법</strong></span>이다.

핵심 숫자부터:

| 항목 | 수치 | 조건 |
|---|---|---|
| 같은 예산 롤아웃 수 | 약 1.5배 | 토큰·툴콜 예산 고정, 체인 기반 대비 |
| 멀티홉 QA 상대 개선 | +16% ~ +69% | GRPO 대비, 1.5b~3b 모델 |
| 극저예산 설정 개선 | +112% | 예산 2롤아웃/프롬프트, Qwen2.5-3b 멀티홉 |
| 1/4 예산으로 GRPO 능가 | 달성 | Qwen2.5-3b 기준 |
| 평균 툴콜 수 | 2.4 → 3.0 | 멀티홉 QA, 더 긴 탐색 유도 |
| 웹 에이전트 GAIA 개선 | +28% | GRPO 대비 평균 |
| 이론 결과 | intra-tree GRPO ≡ step-level DPO | 그래디언트 구조 동일 |

기준일: 2026-09-08, 논문 v3(2026-03-18) 기준. 코드는 [github.com/AMAP-ML/Tree-GRPO](https://github.com/AMAP-ML/Tree-GRPO)에 공개돼 있다.

## 문제: 롤아웃 비용과 희소한 보상

에이전트 RL에는 두 가지 고비용이 걸려 있다.

첫 번째는 롤아웃 예산이다. 멀티턴 에이전트 트랙토리는 수천 토큰에 툴콜 여러 개다. 그룹 기반 RL(GRPO 계열)은 프롬프트마다 독립적인 완전 트랙토리를 N개 뽑는데, 앞부분이 거의 겹치는 샘플을 매번 처음부터 다시 생성한다. 검색 API 같은 유료 툴이 붙으면 비용이 더 아프다.

두 번째는 희소한 감독 신호다. 보상은 결과(outcome) 하나로만 들어오는데, 트랙토리 안의 어떤 스텝이 성공·실패에 기여했는지 알 수 없다. 롤아웃을 아무리 늘려도 학습 신호의 총량은 그대로라서 학습이 불균형해지고 붕괴되기도 한다.

Tree-GRPO의 출발점은 이거다. <span style="background-color: #fff59d"><strong>트랙토리를 공통 접두사를 공유하는 트리로 뽑으면 같은 예산으로 샘플이 늘고, 분기점마다 형제 서브트리 간 보상 차이가 스텝 단위 신호가 된다</strong></span>.

## 방법: 스텝 단위 노드의 트리 롤아웃

![](/images/2026-09-08-tree-grpo-agent-rl/fig-1-p1.png)

Figure 1: 체인 기반 롤아웃(좌)과 스텝 단위 트리 롤아웃(우) 비교 — 트리는 롤아웃 예산을 아끼면서 과정/선호 신호를 함께 제공한다 (논문 Figure 1)

기존 트리 기반 RL은 노드를 토큰이나 문장 단위로 잘랐다. Tree-GRPO는 노드를 <span style="background-color: #fff59d"><strong>하나의 완전한 에이전트 스텝(τ, α, o) — 생각, 행동, 관찰 쌍</strong></span>으로 잡는다. ReAct 구조처럼 스텝 경계가 명확한 에이전트 태스크에 맞는 단위다.

샘플링은 세 단계다.

1. 초기화: 프롬프트마다 M개의 독립 체인 트랙토리를 먼저 뽑아 M개 트리의 씨앗으로 쓴다.
2. 샘플링: 각 트리에서 최종 답 리프를 제외한 노드 N개를 무작위로 고른다.
3. 확장: 고른 노드까지의 전체 컨텍스트를 입력으로 나머지 응답을 이어 생성하고, 원 트리에 새 가지로 삽입한다.

이걸 L번 반복하면 프롬프트당 G = M×(L×N+1)개 롤아웃이 나온다. 트리 확장은 평균적으로 최대 깊이의 절반 지점에서 시작한다.

그래서 <span style="background-color: #fff59d"><strong>한 번 확장의 기대 비용은 완전 트랙토리의 절반(B/2)</strong></span>이고, 총 예산은 E[B_tree] = M·B + L·N·B/2다. 같은 예산에서 체인 방식 대비 약 1.5배 샘플을 확보한다.

## 어드밴티지 계산: 트리 안에서, 트리 사이에서

![](/images/2026-09-08-tree-grpo-agent-rl/fig-3-p4.png)

Figure 3: Tree-GRPO 학습 파이프라인 — 트리 탐색 롤아웃과 intra-tree/inter-tree 그룹 상대 어드밴티지 (논문 Figure 3)

보상은 여전히 결과 보상 하나다. 근데 트리 구조가 바뀌면 감독 신호의 성격이 달라진다.

각 분기점에서 형제 서브트리들의 역전파된 결과 보상 차이는 그대로 선호학습 목적함수가 된다. 서브트리 깊이에 따라 신호의 세분화 단위가 달라져서, <span style="background-color: #fff59d"><strong>추가 감독 없이 결과 보상만으로 스텝 단위 과정(process) 신호가 자동으로 만들어진다</strong></span>.

구체적으로 어드밴티지는 두 층위로 잡는다.

- intra-tree: 같은 트리 안 롤아웃끼리 그룹을 만들어 상대 어드밴티지를 계산한다. 스텝 단위 선호학습 목적이 들어있지만, 가지 수가 적으면 베이스라인 추정이 불안정하다.
- inter-tree: 전체 트리의 롤아웃을 묶어 그룹화한다. 베이스라인은 안정적이지만 과정 신호가 없다.

최종 어드밴티지는 두 개의 합 Â_tree = Â_intra + Â_inter다. 저자들의 소거 실험에서 <span style="background-color: #fff59d"><strong>intra-tree만 쓰면 가지 수가 적을 때(M=2, N=2, L=1) 학습이 붕괴하는데, inter-tree를 더하면 회복돼서 +16% 개선이 유지</strong></span>된다.

이론적으로도 정리했다. 이진 선호 가정 하에서 <span style="background-color: #fff59d"><strong>intra-tree GRPO의 그래디언트 구조는 step-level DPO와 동일하고, 차이는 가중치 항뿐</strong></span>이다. 트리 구조가 온라인 RL 안에 암묵적 스텝 단위 선호학습을 끼워 넣는 셈이다.

## 결과: 모델 크기와 예산에 따른 개선 폭

![](/images/2026-09-08-tree-grpo-agent-rl/fig-5-p9.png)

Figure 5: 트리 기반 vs 체인 기반 RL의 보상·액션 수 비교 (논문 Figure 5)

실험은 11개 데이터셋, 3종 QA(싱글홉, 멀티홉, 웹 에이전트)에서 Qwen2.5와 Llama3.2의 1.5b~14b로 돌렸다.

멀티홉 QA(EM)에서 Tree-GRPO는 체인 기반 GRPO 대비 3b 이하 모델에서 +16% ~ +69% 상대 개선을 보인다. Qwen2.5-1.5b에서는 <span style="background-color: #fff59d"><strong>체인 기반이 멀티턴 툴 사용을 거의 학습하지 못하는 반면 Tree-GRPO는 SFT 없이도 ReAct 패러다임을 습득</strong></span>한다.

예산 실험에서는 롤아웃 2개 분량 예산에서 멀티홉 평균 +112%까지 벌어진다. 반대로 <span style="background-color: #fff59d"><strong>Qwen2.5-3b 기준 체인 GRPO와 동등한 성적을 예산 1/4로 달성</strong></span>했다.

싱글홉 QA는 개선폭이 +1% ~ +9%로 작다. 한두 번의 검색으로 끝나는 태스크라 트리 깊이가 2 정도로 얕아서 과정 신호의 이득이 제한적이기 때문이다.

웹 에이전트 QA(F1)에서는 GAIA에서 평균 +28% 개선, SimpleQA 7b에서 61.5 → 62.4, 14b에서 65.4 → 67.8 등 네 테스트셋 전반에서 GRPO를 앞선다.

BrowseComp처럼 수십 회 웹 상호작용이 필요한 벤치마크는 학습 데이터가 못 미쳐 개선이 미미했다는 게 논문의 한계 인정이다.

성능 외 효과도 있다. 희소 보상에 노출된 체인 기반 모델은 짧은 지름길로 수렴하는 경향이 있는데, 트리 기반은 <span style="background-color: #fff59d"><strong>평균 툴콜 수가 2.4에서 3.0으로 늘며 더 긴 탐색을 하도록 유도</strong></span>된다.

3b 이하 소형 모델은 LR 워밍업 비율에 민감한데, 모든 설정에서 트리 기반이 체인 기반보다 안정적이었다는 것도 Figure 6 소거 결과다.

## 실무 관점에서 가져갈 것

토큰·툴콜 예산이 실제 병목인 멀티턴 에이전트 RL에서 <span style="background-color: #fff59d"><strong>트리 샘플링은 예산 효율과 크레딧 어사인먼트를 동시에 개선하는 구조적 선택지</strong></span>다. 대가는 있다.

트리 수 M을 줄이고 확장을 늘리면 같은 예산에 롤아웃은 많아지지만 탐색 범위가 좁아진다. 병렬 추론 엔진에 순차적 멀티턴 롤아웃이 붙는 트리 탐색은 구현이 성가시다. 논문은 initialize-then-expand 방식으로 풀었다.

작은 모델 + 빠듯한 예산 + 긴 호라이즌 조합일수록 이 방법의 이득이 크다. 큰 모델의 싱글홉성 태스크에는 기대할 게 별로 없다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Tree-GRPO는 GRPO와 무엇이 다른가요?** 롤아웃 샘플 방식(독립 체인 → 공유 접두사 트리), 트리 노드 정의(에이전트 스텝 단위), 어드밴티지 계산(intra-tree + inter-tree 두 층위 합)이 다릅니다.

**결과 보상 외에 추가 감독 신호가 필요한가요?** 아니요. 트리 구조에서 형제 서브트리 간 결과 보상 차이가 스텝 단위 선호 신호로 작동하므로, PRM 같은 추가 주석이나 모델이 필요 없습니다.

**예산이 넉넉하면 트리 방식의 이득이 커지나요?** 싱글홉에서는 예산이 커질수록 이득이 줄어듭니다.

**어떤 상황에서 가장 효과가 큰가요?** 3b 이하 소형 모델, 롤아웃 예산이 프롬프트당 2~4개 수준으로 빠듯한 경우에 큽니다.

**Tree-GRPO는 스텝 단위 DPO와 같은 건가요?** 이진 선호 가정 하에서 intra-tree GRPO 목적함수의 그래디언트가 step-level DPO와 동일 구조임을 이론적으로 보였습니다. 차이는 가중치 항에 있고, 온라인 RL 안에서 동작한다는 점이 실용적 차이입니다.

## 출처

- 논문: [Tree Search for LLM Agent Reinforcement Learning (arXiv:2509.21240)](https://arxiv.org/abs/2509.21240) — ICLR 2026, Alibaba AMAP · Xiamen University · SUSTech
- 코드: [github.com/AMAP-ML/Tree-GRPO](https://github.com/AMAP-ML/Tree-GRPO)
- 수치 인용: 논문 v3 Table 1~4, Figure 5~6 (기준일 2026-09-08)
