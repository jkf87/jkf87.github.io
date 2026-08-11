---
title: "하네스를 학습 가능한 제어층으로 — 오프라인 RL이 에이전트 실행 흐름을 바꿀 수 있다"
date: 2026-08-11
draft: false
tags:
  - agent
  - harness
  - LLM
  - reinforcement-learning
  - offline-RL
  - advantage-weighted-regression
  - control-policy
  - loop
  - automation
authors:
  - conanssam
---

source: arXiv:2607.05458
paper: "Learning to Control LLM Agent Harnesses with Offline Reinforcement Learning"
authors: Haiwen Yi (University of Toronto), Xinyuan Song (Emory University)
code: https://github.com/Hik289/Agentic-RL-harness

LLM 에이전트를 쓰다 보면 같은 모델인데도 결과가 크게 달라지는 순간이 있습니다. 비밀은 하네스에 있습니다 — 언제 관찰하고, 언제 도구를 부르고, 언제 검증하고, 언제 제출할지를 결정하는 실행 코드입니다. 이 논문은 그 결정들을 학습 가능한 제어 정책으로 만듭니다.

## 에이전트 하네스의 고정성 문제

ReAct, Reflexion, MetaGPT — 다 유명한 하네스 패턴입니다. 근데 이 패턴들은 쉬운 작업이든 어려운 작업이든 똑같은 제어 흐름을 따라갑니다. 항상 체크하는 하네스는 쉬운 문제에서 토큰을 낭비하고, 초안만 쓰고 끝내는 하네스는 어려운 문제에서 실패합니다.

이 논문은 묻습니다: 이 제어 결정 시퀀스를 학습할 수 있을까?

## Harness MDP: 하네스를 정식화하다

핵심 아이디어는 하네스 동작을 MDP 상태-행동 쌍으로 분해하는 것입니다.

상태: 궤적 진행도, 초안 상태, 증거 커버리지, 도구 출력, 검증자 피드백, 최근 실패, 남은 예산

행동 7가지: observe / retrieve / call-tool / draft / check / revise / submit

LLM executor는 얼립니다. 프롬프트, 가중치 전부 고정입니다. 학습은 외부 제어기에만 일어납니다 — 하네스가 곧 정책입니다.

![](/images/2026-08-11-harness-control-offline-rl/fig-2-p4.png)

## 학습 방식: 오프라인 AW

온라인 탐색은 비용이 큽니다. 이 논문은 기존 롤아웃 버퍼에서 advantage-weighted regression으로 학습합니다. 높은 어드밴티지 궤적의 (상태, 행동) 쌍을 더 강하게 따라 배우는 거죠.

이 선택이 결과의 핵심 차이를 만듭니다.

## 결과: 과정은 확실히, 결과는 조건부

![](/images/2026-08-11-harness-control-offline-rl/fig-3-p6.png)

6개 제어 도메인 + τ-bench retail + AgentBench DB-Bench 어댑터에서 테스트했습니다.

가장 일관된 결과는 **제출 전 검증 행동이 모든 설정에서 증가**했다는 것입니다. 이건 꽤 강력합니다 — 어떤 도메인이든 버퍼에 패턴만 있으면 검증 습관을 학습합니다.

결과 품질은 도메인마다 다릅니다. coding, τ-bench, DB-Bench에서 큰 폭으로 개선됐지만, 일부 제어 도메인에서는 과정만 좋아지고 결과는 그대로인 경우도 있습니다.

## 왜 과정과 결과가 분리되는가

이 논문의 이론적 핵심입니다.

과정 행동(검증, 증거 수집)은 고어드밴티지 궤적에서 반복적으로 등장하기만 하면 배웁니다. 버퍼에 패턴만 있으면 됩니다.

결과 품질은 더 까다롭습니다 — 더 나은 결과로 이어지는 궤적이 버퍼에 있어야 합니다. 이것을 **finite-buffer support**라고 부릅니다.

![](/images/2026-08-11-harness-control-offline-rl/fig-5-p10.png)

실무적으로, 이건 "로그를 잘 모아라"는 이야기와 같습니다. 하네스 학습의 재료는 에이전트 실행 궤적이니까요.

## 단순 baseline과의 비교

![](/images/2026-08-11-harness-control-offline-rl/fig-4-p9.png)

- Behavior Cloning보다 일관되게 우세 — 어드밴티지 가중치가 단순 모방보다 낫다
- Forced CHECK(항상 검증)보다 낫다 — "언제 검증할지"를 아는 것이 "항상 검증"보다 낫다

## 한계와 방향

- 버퍼 품질에 대한 의존이 큽니다 — 나쁜 버퍼에서는 결과 향상을 기대하기 어렵습니다
- τ-bench, DB-Bench는 어댑터 평가이고 공식 벤치마크 점수는 아닙니다
- 온라인 수집이나 능동적 데이터 확보로 넘어가야 할 단계입니다

## 왜 이 논문이 중요한가

에이전트 하네스 최적화 연구가 폭발적으로 늘고 있습니다. RHO는 에피소드 사이에 하네스 코드를 개선하고, HarnessOpt-Bench는 LLM이 하네스를 최적화하는 능력을 측정합니다. 이 논문은 다른 축을 엽니다 — 에피소드 안에서 하네스 결정을 내리는 정책을 학습하는 것.

하네스는 더 이상 "고정된 인프라"가 아닙니다. 학습 가능한 제어층입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
