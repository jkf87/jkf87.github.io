---
title: "어떤 도구 호출이 성공에 기여했는지 알아내는 법 — TurnSight의 hindsight 크레딧 할당"
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
draft: true
refactor_hub: agent-rl-06
refactor_status: queued
---

도구 호출 에이전트 RL 훈련의 최대 병목은 크레딧 할당임 — 어떤 호출이 성공에 기여했는지 궤적 끝 보상 하나로는 모름. TurnSight는 실행 결과를 hindsight로 활용해 턴 단위로 크레딧을 나눔. 에이전트 궤적 분석에 바로 쓸 수 있는 아이디어라 정리함.

1. 배경. TIR(도구 통합 추론) 에이전트는 하나의 작업에 수십 번 도구를 호출함. 주류인 GRPO(가치 네트워크 없이 같은 프롬프트의 여러 응답을 상대 비교해 학습하는 RL 알고리즘)는 궤적 끝에 보상 하나를 주고 모든 토큰에 동일하게 할당함. 올바른 호출과 잘못된 호출이 같은 크레딧을 받는 것. 턴 단위로 좋았는지 나빴는지 구분이 안 됨.

2. 기존 온폴리시 자기증류(OPSD)의 한계도 명확함. teacher에게 정답이나 참조 궤적을 특권 정보(privileged context, 에이전트는 접근 못 하는 정보)로 주는데, 도구 호출 한 번이 환경을 바꿔버려서 참조 경로와 실제 경로가 금방 갈라짐. 상태 정렬이 깨진다는 것.

3. [TurnSight](https://arxiv.org/abs/2608.04007)의 통찰은 이거임 — 에이전트가 실행한 도구 호출의 결과 자체가 가장 상태 정렬된 privileged 정보다. teacher에게 1~3턴 뒤의 실제 실행 결과를 lookahead context로 주는 것. 정답도 참조 궤적도 필요 없음.

4. 턴 단위 집계가 포인트임. 같은 턴 안엔 포맷 토큰(도구 이름, JSON 괄호)과 실질 인자 토큰이 섞여 있음. 토큰별로 감독하면 포맷 노이즈가 인자 신호를 흐림. 턴 단위로 평균내면 하나의 도구 호출 결정에 대한 일관된 평가가 됨.

5. 다중 lookahead 합의도 눈여겨볼 것. 1, 2, 3턴 teacher 세 개 중 다수표로 방향을 정하고 그 방향에 동의하는 것 중 가장 강한 신호를 선택함. 그리고 GRPO advantage(같은 문제 응답 그룹 안에서의 상대 성과 점수)의 부호는 유지하고 크기만 변조함. 최적화 방향을 안 해치면서 신호를 조율하는 것 — 기존 파이프라인에 drop-in으로 붙는 이유.

6. 결과. Qwen3-4B/8B로 FTRL, BFCL(함수 호출 정확성 리더보드), ToolHop(다단계 도구 호출 추론 벤치마크) 세 벤치마크에서 전부 기존 최고를 넘김. 특히 BFCL의 Long Context와 Miss Parameter에서 큰 폭 개선 — 여러 턴에 걸친 정확한 크레딧 할당이 필요한 문제들에서 효과가 크다는 것.

7. 분석 결과 하나가 흥미로움. hindsight context에 도구 실행 결과만 넣는 게 가장 효과적이고 정답이나 참조 궤적을 추가하면 오히려 상태 정렬이 깨짐. "더 많은 정보 = 더 좋은 teacher"가 아니라는 것. 어떤 정보가 상태와 맞느냐가 중요함.

8. 여기서 실무 전환. 궤적 분석도 같은 구조로 할 수 있음. 어떤 도구 호출이 좋았는지 평가할 때, 그 호출 직후의 실행 결과를 근거로 삼을 것. 최종 성공 여부나 "모범 답안 경로"를 기준으로 삼으면 실제 상태와 안 맞는 평가가 나옴. 턴별로 "이 호출의 결과가 다음 결정에 어떤 정보를 줬나"를 보는 습관.

9. 턴 단위 평가 원칙도 베낄 것. 도구 호출 로그를 분석할 때 토큰 단위나 문장 단위가 아니라 "호출 하나 = 결정 하나"로 묶어서 평가할 것. 그 호출의 reasoning+선택+인자가 하나의 판단이니까. 쪼개서 보면 포맷 노이즈가 판단을 흐림.

10. 합의 방식도 활용 가능함. 궤적의 특정 턴이 좋았는지 나빴는지 판정할 때 판정자를 여러 개 돌려서 다수표로 방향을 정하는 것. 단일 판정자의 실수가 전체 분석을 오염시키는 걸 막는 값싼 안전장치임.

11. 한계. teacher가 필요한 구조라 오픈 궤적 분석에 그대로 쓰긴 어려움. 벤치마크 중심 검증이라 실무 워크로드에서의 이득은 직접 확인해야 함. 그래도 원칙(실행 결과 기반 hindsight, 턴 단위 집계, 부호 보존)은 훈련 없이 분석 관행으로 이식 가능함.

12. 결론. "무엇이 성공에 기여했나"라는 질문의 답은 정답이 아니라 실행 결과 안에 있음. 근데 그 결과를 턴 단위로 묶어 해석해야 신호가 살아남. 토큰 단위로 쪼개거나 모범 경로와 비교하면 오히려 못 보게 된다는 것까지가 교훈임.

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-1-p1.png)

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/github-framework.png)

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-2-p3.png)

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/table-2-p6-1.png)

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-3-p6-2.png)

![](/images/2026-08-05-turnsight-turn-level-hindsight-self-distillation-tir/fig-4-p7.png)
