---
title: "EnvACE: 에이전트가 환경까지 직접 상상하면서 학습하는 RL"
date: 2026-08-14
tags:
  - agent
  - reinforcement-learning
  - world-model
  - LLM
  - harness
  - loop
  - agentic-RL
source: https://arxiv.org/abs/2608.06197
github: https://github.com/Within-yao/EnvACE
authors:
  - Zishan Xu
  - Zhiyuan Yao
  - Yuxin Chen
  - Weinan Zhang
  - Xingshan Zeng
  - Weiwen Liu
affiliation: Shanghai Jiao Tong University, Zhejiang University, Tencent, CUHK, NUS
---

에이전트 RL 훈련에서 가장 비싼 부분은 환경 구축입니다. EnvACE는 그 비용을 없애는 방법입니다. 정책이 행동도 하고, 환경 응답도 상상(world rehearsal)하면서, 외부 환경 없이 훈련합니다.

## 핵심 아이디어: World Rehearsal

기존 에이전트 RL은 정책이 행동을 생성하면 외부 환경이 응답을 돌려줍니다. EnvACE는 정책 하나가 두 역할을 다 합니다.

1. Actor: 도구 호출을 생성
2. Rehearser: 그 도구 호출에 대해 환경이 할 응답을 상상

정책은 행동 → 환경 응답 상상 → 다음 행동 → 또 응답 상상... 이렇게 스스로 궤적을 만듭니다. 두 역할이 같은 파라미터를 공제하면서 end-to-end로 최적화됩니다.

![](/images/2026-08-14-envace-world-rehearsal-agentic-rl/fig-1-p2.png)

세 가지 롤아웃 패러다임 비교입니다. 왼쪽은 실제 환경, 가운데는 외부 시뮬레이터, 오른쪽이 EnvACE의 world rehearsal입니다.

## 왜 작동하는가

정책이 환경 응답을 상상하면서 "이 행동을 하면 환경이 이렇게 반응하겠지"라는 관계를 파라미터 안에 흡수합니다. 이것을 논문에서는 agent world model이라고 부릅니다.

검증 포인트는 역할 분리입니다. 정책을 둘로 나누면(Per-role Policy) τ²-Bench에서 35.5%에 그칩니다. 같은 정책이 두 역할을 다 할 때 36.7%로 올라갑니다. 환경 응답을 상상하는 능력이 행동 개선으로 직결된다는 뜻입니다.

![](/images/2026-08-14-envace-world-rehearsal-agentic-rl/fig-2-p4.png)

EnvACE 전체 구조입니다. 훈련 시 행동-상상 루프가 어떻게 돌아가는지 보여줍니다.

## 결과

4개 벤치마크에서 평가했습니다.

| 벤치마크 | EnvACE-8B | 비교군 최고 |
|---|---|---|
| BFCL V4 (Overall avg) | 46.04 | 47.07 (EnvScaler-8B) |
| τ²-Bench | 36.7 | 31.2 (AWM-14B) |
| VitaBench | 16.0 | 15.0 (ScaleEnv-8B) |
| FinMCP-Bench TF1 | 46.78 | 43.68 (EnvScaler-8B) |

![](/images/2026-08-14-envace-world-rehearsal-agentic-rl/table-1-p7.png)

종합 점수(Overall)에서 EnvACE-8B는 32.91%로 모든 환경 스케일링 baseline을 넘습니다. 환경 응답을 외부에서 가져오지 않고도 정책 내부에서 상상하는 것만으로 transferable한 성능이 나옵니다.

FinMCP-Bench(금융 MCP)에서도 TF1 46.78%로 최고입니다. tool precision 54.04%로 외부 환경 기반 방법들보다 정확한 도구 선택을 합니다.

## 모델 스케일 효과

1.7B → 8B로 스케일업하면:
- BFCL V4: 31.81% → 46.04% (+14.23%)
- τ²-Bench: 15.3% → 36.7% (+21.4%)

스케일이 커질수록 world rehearsal의 효과가 더 큽니다. 작은 모델은 환경을 상상할 용량이 부족한 것으로 보입니다.

## 테스트 타임 스케일링

훈련 후에도 world rehearsal이 쓸모가 있습니다. 실제 환경에 커밋하기 전에 N번 리허설을 하고, 그 결과를 요약해서 최종 실행에 반영합니다.

- N=2 병렬 리허설: Overall 36.7% → 40.9% (+4.2%)
- 순차 리허설도 38.5%로 비TTS 대비 개선

중요한 건 리허설에 EnvACE 훈련 모델을 써야 한다는 점입니다. base model로 리허설하면 효과가 거의 없거나 오히려 떨어집니다. 환경 역할을 내면화한 모델만 리허설 품질이 보장됩니다.

![](/images/2026-08-14-envace-world-rehearsal-agentic-rl/fig-5-p8-5.png)

훈련 스텝이 진행될수록 offline 평가 점수가 우상향합니다. 50스텝 30.0% → 470스텝 36.7%.

## 구조적 의의

에이전트 RL에서 환경은 항상 외부에 있었습니다. 환경을 잘 만들면 성능이 올라가지만, 환경 구축 비용이 선형으로 늘어납니다. EnvACE는 환경 모델링을 정책 안으로 끌어들여서 이 의존성을 끊습니다.

코드는 공개되어 있습니다: https://github.com/Within-yao/EnvACE

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
