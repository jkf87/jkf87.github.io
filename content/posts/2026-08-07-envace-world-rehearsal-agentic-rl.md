---
title: "환경 없이 에이전트 RL을 돌린다 — 정책이 환경 역할까지 연기하는 EnvACE 리허설"
date: 2026-08-07
tags:
  - agent
  - reinforcement-learning
  - LLM
  - world-model
  - tool-use
  - GRPO
  - harness
  - self-evolution
  - loop
  - automation
source: huggingface
source_url: https://arxiv.org/abs/2608.06197
description: "에이전트 RL의 최대 병목인 환경 구축을 정책 안으로 흡수한 EnvACE. 정책이 도구 호출과 환경 응답을 같은 파라미터로 생성·학습해 4개 벤치마크에서 환경 스케일링 기법을 앞선 결과를 정리했다."
---

에이전트 RL의 진짜 병목은 환경 구축임. 환경을 만들고 검증하고 유지하는 비용이 훈련보다 큰 경우가 흔했는데, 이걸 정책 안으로 흡수해버린 논문이 나옴. 원문은 [arXiv:2608.06197](https://arxiv.org/abs/2608.06197).

1. 발상이 과감함. 정책이 에이전트 역할과 환경 역할을 동시에 함. 도구를 호출하고(Act), 그 호출에 대한 환경의 응답을 자기가 생성하고(Rehearse), 그 응답을 히스토리에 넣고 다음 행동을 결정함. 외부 환경을 한 번도 안 부름.

![EnvACE 프레임워크 개요](/images/2026-08-07-envace-world-rehearsal-agentic-rl/framework-overview.png)

![환경을 상상으로 리허설](/images/2026-08-07-envace-world-rehearsal-agentic-rl/gifs/imagination.gif)

2. 왜 되는가. 행동과 환경 응답을 같은 파라미터로 학습하면 "이 도구를 이렇게 부르면 환경이 이렇게 반응한다"는 관계가 가중치에 묻어남. 이 환경 지식이 행동 개선으로 직결됨. 실제로 별도 정책으로 역할을 나누면 1.2% 떨어짐. 파라미터 공유가 핵심이라는 게 실험으로 확인된 것임.

![기존 패러다임과의 비교](/images/2026-08-07-envace-world-rehearsal-agentic-rl/paradigm-comparison.png)

3. 최적화 설계는 role-wise GRPO임. 같은 궤적의 토큰은 같은 보상을 받되 어드밴티지 계산은 Act 그룹 안에서, Rehearse 그룹 안에서 각각 비교함. 역할별 베이스라인을 나눠서 두 역할의 학습 신호를 공정하게 밸런싱하는 것임.

4. 성능은 Qwen3-8B 기준 BFCL-v4, τ²-Bench, VitaBench, FinMCP-Bench 4개에서 일관 우위. 특히 상태를 가지는 멀티턴 상호작용인 τ²-Bench에서 36.7%로 환경 스케일링 기법들을 제침. 환경 역학을 내재화한 효과가 상호작용이 길어질수록 커진다는 증거임. 1.7B→8B로 스케일업하면 τ²가 15.3%→36.7%로 21.4%p 상승. 모델이 클수록 리허설의 수확이 커지는 구조임.

![4개 벤치마크 주요 결과](/images/2026-08-07-envace-world-rehearsal-agentic-rl/main-results-table.png)

![테스트 타임 스케일링 효과](/images/2026-08-07-envace-world-rehearsal-agentic-rl/tts-scaling.png)

5. 테스트 시점 리허설도 재밌음. 훈련 끝난 뒤 실제 실행 전에 가상 궤적 2개를 만들고 평가·수정 제안을 생성해서 rehearsal memory로 합쳐 반영하면 Overall 36.7→40.9%임. 단 리허설 정책이 EnvACE여야 함. 환경을 내재화 안 한 base 모델의 상상은 쓸모가 없다는 결과 — "그럴듯한 환각"과 "내재화된 역학"의 차이를 보여주는 부분임.

6. 필자 관점에서 쓸모 있는 지점. 이 논문을 직접 쓸 일은 없지만 발상은 빌릴 수 있음. 자동화 파이프라인에서 실제 실행 전에 "이 도구 호출을 하면 응답이 이렇게 올 텐데"를 먼저 적어보게 하고 실제 응답과 비교하는 dry-run 검증을 달면, 예상과 실제의 갭이 커지는 지점을 조기에 잡을 수 있음. 이 갭 감시는 예산 낭비 호출을 줄이는 실용 게이트가 됨.

7. 문제제기. 검증이 8B까지고 도구 사용 태스크에 집중됨. 리허설된 환경이 실제 환경과 어긋나면 훈련 신호 자체가 오염되는데, 이 어긋남을 측정하는 방법이 논문에서 충분히 정립되지 않았음. 실서비스 도메인에 적용하려면 리허SCALL 품질 검증이 먼저임.

8. 남는 결론. 환경 모델링을 외부 인프라에서 모델 내부로 옮기면 에이전트 훈련의 확장성이 근본적으로 바뀜. 환경 구축 비용 때문에 에이전트 RL을 포기했던 팀들에게 열리는 방향이라는 게 이 논문의 실무적 의미임.
