---
title: "SMRC-SD: 에이전트 자기증류에서 정답지가 현재 상태와 맞지 않을 때"
date: 2026-08-11
tags:
  - agent
  - self-distillation
  - LLM
  - reinforcement-learning
  - multi-turn
  - GRPO
  - harness
  - tool-use
  - loop
  - automation
source: huggingface
source_url: https://arxiv.org/abs/2608.05219
github_url: https://github.com/liujunzhuo/SMRC-SD
---

## 결론부터

멀티턴 에이전트를 RL로 훈련할 때 성공한 궤적을 참조 삼아 같은 모델이 스스로를 증류(self-distillation)하는 기법이 널리 쓰인다. 기존 방법은 매 턴마다 이 성공 궤적을 무조건 teacher에게 보여준다. 논문은 이 접근에 구조적 문제가 있음을 보여준다. 에이전트가 참조와 다른 행동을 하면 도달한 상태가 달라지고, 그 상태에서 참조 궤적은 더 이상 유효한 지침이 아니다.

SMRC-SD(State-Matched Routing and Contextualized Self-Distillation)는 매 턴마다 현재 상태와 참조 궤적의 호환성을 검사한 뒤, 호환될 때만 증류 신호를 적용한다. ALFWorld에서 Qwen3-1.7B 기준 task success를 0.746에서 0.865로, WebShop에서 0.574에서 0.693로 올렸다.

## 문제: state-reference mismatch

GRPO 같은 trajectory-level RL은 성공/실패 보상만 준다. 어떤 턴의 어떤 행동이 결과를 결정했는지 알기 어렵다. on-policy distillation(OPD)은 같은 모델을 teacher로 쓰되, 성공한 궤적을 training-only 컨텍스트로 주어 학생 응답을 re-scoring하여 턴 단위의 밀집한 학습 신호를 만든다.

기존 FullPath-SD는 성공한 전체 궤적을 매 턴 teacher에게 보여준다. 멀티턴 환경에서 이전 행동이 다음 상태를 바꾼다는 점을 간과한다. 학생이 참조 궤적과 다른 행동을 하거나 다른 순서로 서브골을 완수하면, 참조에 없는 상태에 도달한다.

![](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/fig1-state-reference-mismatch.png)

참조 궤적은 "Product A를 Results A에서 클릭"하라고 가르치는데, 학생은 Product B 상세 페이지에 있다. 이 상황에서 올바른 행동은 "Back to Search"다. FullPath-SD는 여전히 Product A 경로를 teacher에게 보여주며, teacher가 학생의 올바른 행동을 낮게 평가할 수 있다.

논문은 fixed-state teacher intervention으로 이를 직접 측정했다. 상태/프롬프트/응답을 고정하고 teacher 컨텍스트만 바꿔보니, 매칭된 상태에서 FullPath-SD가 올바른 행동의 로그 확률을 올리지만(+), 매칭되지 않은 상태에서는 억누른다(−). A−C 차이는 +0.070 [95% CI: +0.012, +0.153].

## 방법: SMRC-SD

두 단계로 동작한다.

상태 매칭 라우팅에서 환경 어댑터가 학생의 현재 상태 서명과 참조 궤적 각 위치의 서명을 비교한다. 서명은 작업 ID, 실행 진행도, 인벤토리, 현재 페이지 등 환경별 필드로 구성된다. 매칭되면 distillation을 적용하고, 비매칭 시 GRPO만 사용한다.

상태 맞춤형 teacher 컨텍스트에서는 매칭된 턴에서 teacher에게 (1) 성공한 전체 궤적, (2) 현재 상태 요약, (3) 매칭된 후보 행동을 함께 준다. Teacher는 도달한 상태에 근거하여 re-scoring한다.

![](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/fig2-smrc-sd-overview.png)

추론 시에는 참조, 서명, 매칭, teacher 컨텍스트를 전부 제거한다. 배포된 정책은 일반 프롬프트만 받는다.

## 메인 결과

| 모델 | 방법 | ALFWorld Avg@4 | ALFWorld Pass@4 | WebShop Score | WebShop Acc |
|---|---|---|---|---|---|
| Qwen3-1.7B | GRPO | 0.717 | 0.812 | 0.673 | 0.383 |
| Qwen3-1.7B | Skill-SD | 0.379 | 0.453 | 0.818 | 0.539 |
| Qwen3-1.7B | SDAR | 0.578 | 0.615 | 0.768 | 0.586 |
| Qwen3-1.7B | FullPath-SD | 0.746 | 0.836 | 0.694 | 0.574 |
| Qwen3-1.7B | SMRC-SD | 0.865 | 0.914 | 0.825 | 0.693 |
| Qwen2.5-3B | FullPath-SD | 0.766 | 0.852 | 0.842 | 0.734 |
| Qwen2.5-3B | SMRC-SD | 0.883 | 0.938 | 0.863 | 0.736 |

Qwen3-1.7B에서 Skill-SD와 SDAR이 GRPO보다 성능이 떨어진다. 무조건적인 distillation이 1.7B 같은 작은 모델에서는 학습을 해친다는 뜻이다. SMRC-SD는 동일한 참조 궤적을 쓰면서도 매칭된 턴만 골라내어 이 문제를 회피한다.

![](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/fig3-training-dynamics.png)

응답 길이도 GRPO 수준으로 유지된다. SMRC-SD 평균 78.8 토큰, GRPO 79.5, FullPath-SD 142.6, Skill-SD 255.6. 반복 4-gram 비율도 8.8%로 Skill-SD의 38.6%와 대비된다.

## Ablation: 라우팅과 컨텍스트가 각각 기여한다

| 구성 | ALFWorld Avg@4 |
|---|---|
| FullPath-SD (기준) | 0.746 |
| + 매칭 라우팅만 | 0.836 |
| + 동적 컨텍스트만 | 0.695 |
| SMRC-SD (둘 다) | 0.865 |

라우팅이 주된 기여지만, 매칭된 턴에서 동적 컨텍스트가 추가로 +0.029를 더한다. 같은 수의 턴을 무작위로 선택한 대조군은 0.723으로, 어떤 턴을 고르는가가 턴 수보다 중요하다.

컨텍스트 구성 요소를 분리하면 후보 행동만 주거나 상태 요약만 주는 것은 FullPath-SD + 라우팅보다 나아지지 않는다. 상태 요약이 "지금 어디인지"를, 후보 행동이 "다음에 뭘 해야 하는지"를 함께 알려줘야 teacher가 정확한 re-scoring을 한다.

## 매칭 품질 검증: replay audit

매칭이 실제로 실행 가능한 continuation을 반환하는지 확인하기 위해, 논문은 두 가지 매칭 방식(structured-state vs history-only)을 비교했다.

35,712개의 동일한 archived turn에서 structured-state 매칭은 20.2% 커버리지를 보이고, history 매칭의 98.8%를 재현한다. History 매칭은 structured-state 매칭의 75.4%만 재현한다. 공통 매칭 5,428건 중 99.4%에서 동일한 후보를 선택한다.

Replay audit에서는 학생의 실제 action prefix를 실행하여 도달한 환경 상태를 복원한 뒤, 매칭된 후보와 나머지 canonical suffix를 실행한다. Structured-state 매칭은 781/781(100%), history 매칭은 792/800(99.0%)이 성공적으로 replay된다.

## 한계 및 확장 가능성

참조 궤적을 conditional plan으로 취급하는 방식은 하네스 설계, 메모리 재생, 스킬 재사용까지 확장할 수 있는 원칙이다. 기존 self-distillation 연구가 teacher 신호의 가중과 마스킹에 집중했다면, SMRC-SD는 참조가 현재 상태에서 유효한지를 먼저 확인한다.

상태 서명이 hand-engineered이고 환경별 어댑터가 필요하다는 한계가 있다. ALFWorld와 WebShop은 상태 공간이 정형화되어 있어서, 실제 웹 브라우저나 터미널 환경에서는 서명 설계가 병목이 될 수 있다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참조

- Liu, J. et al. "When Privileged Guidance Misaligns: State-Matched Routing and Contextualized Self-Distillation for Multi-Turn Agents." arXiv:2608.05219, 2026.
- 코드: https://github.com/liujunzhuo/SMRC-SD
