---
title: "GRPO의 균등 보상을 턴별로 재분배하기 — AgentOPSD의 재귀적 자기증류"
date: 2026-08-07
tags:
  - agent
  - reinforcement-learning
  - LLM
  - credit-assignment
  - self-distillation
  - GRPO
  - Bayesian
  - turn-level
  - agentic-RL
  - loop
authors:
  - conanssam
source: https://arxiv.org/abs/2608.05987
github: https://github.com/ZethWang/AgentOPSD
description: "AgentOPSD는 teacher-student log-prob 격차를 턴별 증거로 집계하고 Bayesian belief를 재귀 갱신해 궤적 어드밴티지를 턴별로 재분배함. 크리틱·추가 롤아웃 없이 세 환경에서 GRPO를 꾸준히 앞짬. 크레딧 설계의 실무 교훈을 정리함."
draft: true
refactor_hub: agent-rl-06
refactor_status: queued
---

agentic RL에서 GRPO(같은 문제의 여러 롤아웃을 비교해 상대적으로 나은 행동을 강화하는 강화학습 알고리즘)가 널리 쓰이는 이유는 크리틱이 필요 없다는 점임. 근데 대가가 있음. 궤적 단위 어드밴티지(어떤 행동이 평균보다 얼마나 나은지 나타내는 학습 신호)를 모든 토큰에 균등하게 나누는 것. 그래서 성공 궤적의 무의미한 행동도 보상을 받고, 긴 호라이즌에서 비효율이 커짐. AgentOPSD는 이 균등 할당을 크리틱 없이 턴별로 재분배함. 방법이 재밌음. 자기 자신을 증류 교사로 쓰는 것.

1. 증거 계산이 출발점임. privileged self-distillation이라 부르는데, 같은 모델 파라미터를 쓰되 teacher branch에 추가 컨텍스트(스킬 c+)를 줌. 그리고 각 턴에서 "컨텍스트가 있을 때의 log-prob"와 "없을 때의 log-prob"(모델이 해당 출력에 부여하는 로그 확률)의 격차를 토큰 전체에 걸쳐 합산함. 이 격차가 큰 턴이 스킬을 활용해 성공에 기여한 턴이라는 논리. 추가 롤아웃도 외부 크리틱도 필요 없이 기존 궤적에서 계산되는 신호임.

2. 그다음이 재귀적 벨리프 갱신임. 그룹 성공률로 초기 믿음 B_0를 잡고, 턴마다 증거 e_k를 감쇠 누적해서 log-odds(승산의 로그, 확률을 더하고 빼기 쉽게 바꾼 표현) 공간에서 Bayesian 갱신을 함. 각 턴의 ΔB_k, 즉 그 턴이 성공 확률에 대한 믿음을 얼마나 수정했는지가 그 턴의 기여도가 됨. 이렇게 하면 "어느 턴에서 국면이 바뀌었는가"가 자동으로 부각됨. 마지막으로 bounded advantage reshaping. 궤적 어드밴티지에 ΔB 기반 가중치를 곱하는데 [1-b, 1+b]로 클리핑해서 GRPO의 안정성을 해치지 않음. 보상을 갈아엎는 게 아니라 재조정하는 설계임.

![Figure 1: 훈련 역학 및 호라이즌 robustness](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x1.png)

3. 결과가 일관됨. Qwen2.5-7B 기준 ALFWorld 85.7% → 89.1%(+3.4pp), Search-QA 42.8% → 46.9%(+4.1pp), WebShop도 점수와 정확도 모두 상승. 3B에서도 개선이 확인됨. 화려한 폭발은 아니지만 크리틱도 롤아웃도 없이 공짜로 얻는 이득이라는 점이 실무적 가치임.

![Figure 2: 방법론 개요](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x2.png)

4. 호라이즌 효과가 방법의 정체를 보여줌. 평균 5~6턴인 ALFWorld에서 개선이 크고 4턴짜리 Search-QA에서는 작음. 재귀 벨리프 갱신이 긴 궤적에서 더 큰 효과를 발휘한다는 것. ablation에서도 턴 경계 집계와 재귀 벨리프가 각각 기여하는데 특히 재귀 벨리프가 호라이즌 robustness의 핵심이었음. 긴 과제를 다루는 팀일수록 쓸모가 커지는 방법임.

5. 기존 방법 지도가 깔끔함. PPO(가장 널리 쓰는 정책 경사 RL 알고리즘)/GAE(시간차 오차를 누적해 어드밴티지를 추정하는 기법)는 크리틱 필요, VinePPO는 크리틱에 추가 롤아웃까지 필요, GRPO는 둘 다 없지만 크레딧이 궤적 전체 단위, StepOPSD는 스텝 단위지만 로컬 신호, AgentOPSD는 둘 다 없이 턴 단위 재귀 신호. 그리고 GiGPO가 환경 보상으로 스텝 어드밴티지를 추정하는 방식이라 상호보완적이라는 정리도 유익함. 자기 상황에서 무엇이 제약인지(크리틱 GPU 비용? 롤아웃 비용?)에 따라 선택지가 좁혀지는 표임.

![Figure 3: 하이퍼파라미터 민감도 분석](/images/2026-08-07-agentopsd-recursive-turn-level-credit-agentic-rl/x3.png)

6. 내 실무 결론은 이렇게임. 첫째, GRPO로 긴 호라이즌 에이전트를 훈련 중이라면 턴별 크레딧 실험을 해볼 것. 코드가 공개되어 있어서 도입 장벽이 낮음. 둘째, 크레딧 재조정은 "가중치를 흔들되 경계로 클리핑"하는 방식이 안전함. 학습 안정성을 해치는 크레딧 개조는 실험 전체를 망침. 셋째, 기여도 신호를 외부 크리틱 말고 모델 자체의 정보격차(컨텍스트 유무 log-prob 차이)에서 뽑는 아이디어는 다른 용도에도 이식 가능함. 중요한 스킬·지식이 어느 턴에서 실제로 활용됐는지 측정하는 프로브로 쓸 수 있음.

원문: [arXiv:2608.05987](https://arxiv.org/abs/2608.05987).
