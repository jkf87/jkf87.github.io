---
title: "EnvACE: 에이전트가 환경 없이 훈련한다 - 상상만으로 RL을 완성하는 World Rehearsal"
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
authors:
  - conanssam
source: huggingface
source_url: https://arxiv.org/abs/2608.06197
github_url: https://github.com/Within-yao/EnvACE
---

에이전트를 RL로 훈련하려면 환경이 필요하다. 이 문장이 에이전트 RL의 가장 큰 장벽이었다. 환경을 만들고, 검증하고, 유지하는 비용이 훈련 자체보다 큰 경우가 흔하다. Shanghai Jiao Tong University와 Tencent가 함께 발표한 EnvACE는 이 장벽을 정책 안으로 옮겨버린다.

## 핵심 구조: 환경도 정책이 연기한다

EnvACE가 제안하는 건 단순하다. 정책이 에이전트 역할과 환경 역할을 동시에 한다.

궤적이 어떻게 전개되는지 보면 이 아이디어가 왜 파괴적인지 알 수 있다:

1. 정책이 도구를 호출한다 (Act)
2. 정책이 그 도구 호출에 대한 환경의 응답을 생성한다 (Rehearse)
3. 그 응답을 히스토리에 넣고 다음 행동을 결정한다
4. 외부 환경은 한 번도 부르지 않는다

![세 가지 롤아웃 패러다임: 실제 환경 vs 외부 시뮬레이터 vs EnvACE](/images/2026-08-07-envace-world-rehearsal-agentic-rl/paradigm-comparison.png)

이게 왜 되는가? 정책이 행동과 환경 응답을 같은 파라미터로 학습하면, "이 도구를 이렇게 부르면 환경이 이렇게 반응한다"는 관계가 가중치에 묻어난다. 이것이 행동 개선으로 이어진다.

## Role-Wise GRPO: 두 역할을 공정하게 최적화하기

문제는 두 역할의 학습 신호를 어떻게 밸런싱하느냐다. EnvACE는 role-wise GRPO를 설계했다.

같은 트레이젝토리의 모든 토큰은 같은 보상을 받지만, 어드밴티지 계산은 역할별로 다른 베이스라인을 쓴다. Act 그룹 안에서 비교하고, Rehearse 그룹 안에서 비교한다. 파라미터는 공유하므로 리허설로 얻은 환경 지식이 행동에 직접 반영된다.

별도 정책으로 나누면? 1.2% 떨어진다. 같은 파라미터를 공유하는 게 핵심이다.

![EnvACE 프레임워크 구조도](/images/2026-08-07-envace-world-rehearsal-agentic-rl/framework-overview.png)

## 성능: 4개 벤치마크에서 일관되게 앞선다

Qwen3-8B 백본으로 BFCL-v4, τ²-Bench, VitaBench, FinMCP-Bench에서 평가했다.

EnvACE-8B는 Overall 32.91로 환경 스케일링 기법들(EnvScaler-8B, AWM-14B)을 제친다. 특히 눈에 띄는 건 τ²-Bench에서의 36.7% — 이것은 상태를 가지는 멀티턴 상호작용 벤치마크인데, 환경 역학을 내재화한 효과가 가장 크게 나타난다.

FinMCP-Bench에서도 TF1 46.78%로 1위. 금융 도메인 전용 MCP 환경에서도 일반화된다.

![전체 결과 테이블](/images/2026-08-07-envace-world-rehearsal-agentic-rl/main-results-table.png)

## 스케일할수록 더 커지는 효과

1.7B → 8B로 가면 τ²-Bench가 15.3%에서 36.7%로 21.4%나 오른다. 모델이 커질수록 world rehearsal의 수확이 더 크다.

1.7B → 8B로 가면 τ²-Bench가 15.3%에서 36.7%로 21.4%나 오른다. 모델이 커질수록 world rehearsal의 수확이 더 크다.

## 테스트 시점 리허설: 실행 전에 미리 연습하기

여기가 재밌는 부분이다. 훈련이 끝난 후 실제 환경에서 추론할 때, 정책이 "혼자 연습"을 할 수 있다.

N=2개의 가상 궤적을 만들고, 각각에 대해 평가와 수정 제안을 생성한다. 이를 rehearsal memory로 합쳐서 최종 실행에 반영한다.

- Parallel 모드: 독립 리허설 → 합산
- Sequential 모드: 이전 리허설을 다음에 반영

결과: Overall 36.7% → 40.9% (+4.2%). 단, 리허설 정책이 EnvACE여야 한다. Base model으로 리허설하면 효과가 거의 없다 — 환경을 내재화하지 않은 모델이 상상하는 환경 응답은 쓸모가 없다.

![Test-time scaling](/images/2026-08-07-envace-world-rehearsal-agentic-rl/tts-scaling.png)

## 이게 왜 중요한가

에이전트 RL의 가장 큰 병목은 환경 구축이다. 도구를 정의하고, 상태를 관리하고, 검증기를 만드는 일은 반복적이고 비싸다. EnvACE는 이 병목을 정책 안으로 흡수한다.

물론 한계도 있다. 8B까지만 검증했고, 도구 사용 태스크에 집중했다. 그렇지만 방향성은 분명하다 — 환경 모델링을 외부에서 내부로 옮기면, 에이전트 훈련의 확장성이 근본적으로 바뀐다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

코드는 [GitHub](https://github.com/Within-yao/EnvACE)에 공개되어 있다.

---

원문: [EnvACE: Internalizing Environment Dynamics via World Rehearsal for Agentic Reinforcement Learning](https://arxiv.org/abs/2608.06197)
