---
title: "TurnSight: 도구 호출 에이전트의 크레딧 할당 문제를 hindsight로 푼다"
date: 2026-08-05
tags:
  - agent
  - reinforcement-learning
  - LLM
  - tool-integrated-reasoning
  - self-distillation
  - hindsight
  - credit-assignment
  - GRPO
  - loop
---

에이전트가 도구를 호출하면서 추론할 때 RL 훈련의 가장 큰 병목은 크레딧 할당이다. 어떤 도구 호출이 성공에 기여했는지 궤적 끝의 보상 하나로는 알 수 없다. TurnSight는 이 문제를 실행 결과를 hindsight로 활용해서 푼다. 감독 신호를 정답이나 참조 궤적이 아니라 에이전트 자신의 실행 결과에서 끌어낸다.

## 배경: 왜 트라젝토리 보상으로는 부족한가

Tool-Integrated Reasoning(TIR) 에이전트는 하나의 task를 해결하기 위해 수십 번의 도구 호출을 수행한다. 현재的主流인 GRPO는 궤적 끝에 하나의 보상을 주고, 이를 궤적의 모든 토큰에 동일하게 할당한다.

이 방식의 한계는 명확하다. 올바른 도구 호출과 잘못된 도구 호출이 같은 크레딧을 받는다. 실행 결과가 좋았는지 나빴는지 턴 단위로 구분할 수 없다.

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-1-p1.png)

기존 on-policy self-distillation(OPSD)도 한계가 있다. teacher에게 정답이나 참조 궤적을 privileged context로 주지만, 에이전트가 실제 방문한 상태와 맞지 않을 수 있다. 도구 호출 한 번이 환경을 바꿔버리기 때문에 참조 경로와 실제 경로가 금방 갈라진다.

## TurnSight의 접근: 실행 결과가 곧 hindsight

TurnSight의 핵심 통찰은 "에이전트가 실행한 도구 호출의 결과 자체가 가장 state-aligned된 privileged 정보다"라는 점이다.

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/github-framework.png)

### 작동 방식

1. **실행 기반 hindsight 구성**: 학생 에이전트가 턴 k에서 도구를 호출하고 결과를 받는다. 이 결과를 frozen reference policy(teacher)에게 lookahead context로 제공한다. teacher는 1턴, 2턴, 3턴 뒤의 실행 결과까지 볼 수 있다.

2. **턴 단위 집계**: token-level log-prob gap을 계산한 뒤, 같은 턴의 모든 토큰에 대해 평균낸다. 도구 호출 하나(reasoning + tool selection + arguments)를 하나의 결정 단위로 취급하는 것이다.

3. **다중 lookahead 선택**: 세 개의 lookahead teacher(1, 2, 3) 중 다수표로 합의 방향을 정하고, 그 방향에 동의하는 teacher 중 가장 강한 신호를 선택한다.

4. **부호 보존 변조**: 선택된 hindsight 신호로 GRPO advantage의 크기를 조절한다. 부호는 유지하고 크기만 변조하므로 RL 최적화 방향을 해치지 않는다.

## 토큰 단위 vs 턴 단위

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-2-p3.png)

같은 턴 안에서 포맷 토큰(tool name, JSON braces)과 실질적 인자 토큰이 섞여 있다. 토큰마다 개별적으로 감독하면 포맷 토큰의 noise가 인자 결정의 신호를 흐린다. 턴 단위로 평균내면 하나의 도구 호출 결정에 대한 coherent한 평가가 된다.

## 실험 결과: 세 벤치마크에서 일관된 향상

Qwen3-4B와 Qwen3-8B로 FTRL, BFCL, ToolHop 세 벤치마크에서 평가했다.

TurnSight는 모든 벤치마크에서 기존 최고 방법론을 넘어섰다. 특히 BFCL의 Long Context와 Miss Parameter 하위 태스크에서 큰 폭으로 개선됐는데, 이는 다중 턴에 걸쳐 정확한 크레딧 할당이 필요한 문제들이다.

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/table-2-p6-1.png)

Ablation study에서 핵심 컴포넌트들(실행 기반 hindsight, 다중 lookahead, 턴 단위 집계)을 하나씩 제거할 때마다 성능이 떨어진다.

## 분석: 어떤 hindsight 구성이 좋은가

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-3-p6-2.png)

hindsight context에 도구 실행 결과만 넣는 것이 가장 효과적이다. 정답이나 참조 궤적을 추가하면 오히려 상태 정렬이 깨진다.

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-4-p7.png)

고정 lookahead vs 가변 lookahead를 비교하면, 단일 lookahead보다 다중 lookahead 합의 방식이 안정적으로 높은 성능을 보인다.

## 의의

TurnSight는 hindsight 감독을 실행 결과에서 도출하고, 턴 단위로 크레딧을 할당한다. RL advantage의 부호를 바꾸지 않고 크기만 조절하기 때문에 기존 RL 파이프라인에 drop-in으로 붙일 수 있다.

## 더 실습해보고 싶은 분들께

에이전트 RL 루프와 도구 호출 크레딧 할당을 직접 실험해보고 싶다면 다음 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

코드와 모델 체크포인트가 모두 공개되어 있다:

- 코드: [github.com/quchangle1/TurnSight](https://github.com/quchangle1/TurnSight)
- 모델: [huggingface.co/ChangleQu/Qwen3-8B-TurnSight](https://huggingface.co/ChangleQu/Qwen3-8B-TurnSight)
- 논문: [arxiv.org/abs/2608.04007](https://arxiv.org/abs/2608.04007)
