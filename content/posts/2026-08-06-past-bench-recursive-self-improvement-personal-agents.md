---
title: "PAST-Bench: 에이전트가 경험에서 나아지는지, 처음으로 제대로 측정한 벤치마크"
date: 2026-08-06
tags:
  - agent
  - self-improvement
  - benchmark
  - personal-agent
  - memory
  - harness
  - LLM
  - evaluation
  - persistence
  - recursive-self-improvement
---

에이전트가 이전 세션의 경험을 저장하고 다음 세션에서 더 나은 행동을 하는지, 이걸 통제된 조건에서 처음으로 제대로 측정한 벤치마크입니다.

PAST-Bench(Ding et al., 2026)는 26개 시나리오·204개 에피소드로 구성된 성과 귀속 벤치마크입니다. 구조는 단순한데 의미가 정확합니다. 같은 작업 패밀리 안에서 이전 에피소드가 경험을 저장하는 기회를 주고, 이후 에피소드가 그 경험을 재사용하는지 검사합니다. 이때 persistence(지속성)를 켜고 끄는 매칭 컨트롤을 걸어서, 점수가 올라가면 그것이 경험 재사용 때문인지 아니면 모델 자체 능력 때문인지를 분리합니다.

## 왜 기존 벤치마크로는 안 되는가

기존 에이전트 벤치마크(OSWorld, AgentBench, WorkArena 등)는 fresh session에서 원샷 점수만 냅니다. 메모리 벤치마크(LongMemEval, LoCoMo)는 개별 메모리 컴포넌트만 격리 테스트합니다. 둘 다 "경험을 축적하면 실제로 나아지는가?"라는 질문에 답하지 못합니다.

PAST-Bench는 평가 단위가 작업 하나가 아니라 작업 패밀리 전체 궤적입니다. 그리고 persistence-on/off 컨트롤이 있어서, 나중 에피소드 점수가 올라도 그것이 경험 때문인지 프롬프트 노출 때문인지 구분합니다.

![](/images/2026-08-06-past-bench-recursive-self-improvement-personal-agents/fig-1-p1-1.png)

## 4개 역량과 테스트 구조

PAST-Bench는 에이전트의 자가진화를 4개 역량으로 분해합니다.

| 역량 | 의미 | 에피소드 수 |
|------|------|------------|
| Memory | 사용자 취향·제약·이전 사례를 저장하고 조회 | 41 |
| Procedural Reuse | 다단계 기술 절차를 저장하고 재실행 | 64 |
| Information Gathering | 저장된 정보를 적절한 시점에 능동적으로 검색 | 48 |
| Update | 오래된 정보를 새 정보로 교체, 이전 값 유출 방지 | 51 |

각 패밀리는 cold → learn → evaluation → control 에피소드 순서로 진행됩니다. 세션 사이에 컨텍스트를 완전히 초기화합니다. 그래서 이전 에피소드 점수가 다음 에피소드에 영향을 주려면 persistence layer(메모리 스토어, 스킬 파일, 세션 기록)를 통해서만 가능합니다.

## 결과: 개선은 있지만 불균등

7개 모델(GPT-5.4, Claude Sonnet 4.6, MiniMax-M2.7, GLM-5.1, Kimi K2.6, DeepSeek-V4-Pro, Claude Opus 4.6)과 4개 프레임워크(Hermes, Hermes+, nanobot, ZeroClaw, Agent-Zero)를 테스트했습니다.

전체 Δ(persistence on - persistence off)는 +0.13 ~ +0.24 범위입니다. 경험 저장이 실제로 도움이 됩니다.

여기서 중요한 발견이 있습니다. 같은 Δ 값을 가진 에이전트라도 어떤 역량에서 점수가 올랐는지가 다릅니다.

- GPT-5.4: Memory(38%)과 Update(35%)에 고르게 분포
- GLM-5.1: Update에 46% 집중
- Kimi K2.6: Memory에 49% 집중
- nanobot vs Hermes: 둘 다 Δ=+0.13이지만 nanobot은 Update 한 곳에서만 올리고 메커니즘 근거가 약함(Mech 0.57). Hermes는 4개 역량 모두에서 올림(Mech 0.64)

단일 Δ 숫자는 같아도 내부 동작이 완전히 다릅니다. 그래서 PAST-Bench는 task score와 mechanism-evidence score를 분리해서 보고합니다.

## Hermes+: 5개 메커니즘으로 루프 개선

논문의 진짜 공헌은 진단입니다. Hermes 에이전트의 실패 패턴을 분석하니 5가지로 떨어집니다.

![](/images/2026-08-06-past-bench-recursive-self-improvement-personal-agents/fig-3-p10-1.png)

| 메커니즘 | 위치 | 문제 | 해결 |
|----------|------|------|------|
| E1 Plan | 계획 단계 | 저장된 상태를 안 보고 계획 수립 | 실행 전 필수 조회 |
| E2 Render | 메모리 | stale과 current가 섞임 | typed binding + valid 값만 렌더 |
| E3 Route | 스킬 | 절차가 텍스트로만 남음 | ranked skill로 저장·검색 |
| E4 Gate | 정보 검색 | 저장된 증거를 안 찾아봄 | 회상 의존 행동 전 검색 강제 |
| E5 Close | 업데이트 | 수정이 다음 세션에 안 감 | 에피소드 종료 시 동기 flush |

결과: Overall Δ가 +0.13에서 +0.15로, Mech은 0.64에서 0.73으로 상승합니다. Update 역량에서 가장 큰 개선(Δ +0.12 → +0.24).

이 +0.02 전체 개선은 run-to-run variation(±0.04 ~ ±0.06)보다 작습니다. 논문이 정직하게 이 한계를 밝히고 있습니다. Update에서의 개선은 명확합니다. 전체적으로는 진단 도구로서의 가치가 만능 개선책으로서의 가치보다 큽니다.

![](/images/2026-08-06-past-bench-recursive-self-improvement-personal-agents/fig-4-p20-1.png)

## 왜 중요한가

이 논문이 푸는 문제는 실용적입니다. OpenClaw, Hermes 같은 개인 에이전트가 "경험을 축적한다"고 말할 때, 그 경험이 실제로 다음 세션의 행동을 개선하는지 확인할 방법이 없었습니다. PAST-Bench는 이걸 4개 역량 × 매칭 컨트롤 × 메커니즘 근거로 쪼개서 보여줍니다.

경험을 저장하는 것과 경험으로부터 개선되는 것은 다른 능력입니다. 같은 크기의 개선이라도 어떤 경로를 통해 왔는지가 중요합니다. 이 분리가 재귀적 자기개선(RSI) 연구의 다음 단계를 위한 전제 조건입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

---

**원문**: [PAST-Bench: Benchmarking the Foundations of Recursive Self-Improvement in Personal Agents](https://arxiv.org/abs/2608.04003)

**코드**: [github.com/Gen-Verse/PAST-Bench](https://github.com/Gen-Verse/PAST-Bench)
