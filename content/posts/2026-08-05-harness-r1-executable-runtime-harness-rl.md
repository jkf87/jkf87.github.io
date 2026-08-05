---
title: "Harness-R1: 에이전트 하네스 코드를 RL로 고치는 9B 모델"
date: 2026-08-05
tags:
  - agent
  - harness
  - LLM
  - reinforcement-learning
  - GRPO
  - self-evolution
  - loop
  - co-evolution
source: arxiv
source_url: https://arxiv.org/abs/2608.02276
paper_url: https://arxiv.org/abs/2608.02276
github_url: https://github.com/DeepExperience/Harness-R1
---

에이전트가 실패하면 모델 가중치를 바꾸는 것만 답이 아닙니다. Harness-R1은 에이전트를 감싸는 실행 코드(하네스)를 고치는 전용 모델을 RL로 훈련합니다. 결과적으로 vanilla Qwen3.5-9B의 평균 성공률을 44.3%에서 53.6%로, +9.3포인트 올립니다.

핵심은 이겁니다: 하네스를 고치는 모델(engineer)과 과제를 푸는 모델(target agent)을 분리하고, engineer만 훈련시킵니다. target은 얼려둔 채로 두는 거죠.

[출처: Harness-R1, Zhang et al., 2026](https://arxiv.org/abs/2608.02276)

## 하네스가 뭔데 왜 고치나

에이전트 하네스는 모델과 환경 사이에 끼어 있는 실행 코드입니다. 컨텍스트를 조립하고, 도구를 중계하고, 액션을 검증하고, 실패에서 복구하는 역할을 합니다.

같은 모델 가중치여도 하네스가 다르면 에이전트 성능이 크게 바뀝니다. 근데 기존 방식의 문제는:

- Self-Refine 같은 고정 룰 → 세 벤치마크 모두에서 보상이 하락
- GPT-5.5, GLM-5.2 같은 대형 모델에게 "하네스 좀 고쳐줘" → 그럴듯해 보이는 패치를 내놓지만 실제 성공률은 불안정하거나 오히려 떨어짐

![Figure 1: 세 벤치마크에서 기존 방식의 보상 변화. 다이아몬드는 가중 평균.](/images/2026-08-05-harness-r1-executable-runtime-harness-rl/fig-1-p2.png)

그래서 "진짜 효과가 있는지"를 패치 적용 후 target을 다시 돌려서 확인해야 합니다. 이걸 학습 신호로 씁니다.

## Harness-R1의 구조

![Figure 2: Harness-R1 개요. 실패 궤적 → engineer가 패치 작성 → target 재실행 → 보상으로 engineer만 훈련](/images/2026-08-05-harness-r1-executable-runtime-harness-rl/fig-2-p3.png)

흐름은 이렇게 됩니다:

1. target agent가 과제를 풀고 실패한 궤적을 모음다
2. failure packet을 engineer에게 준다
3. engineer가 4개 라이프사이클 훅에 대한 실행 가능한 패치를 작성한다
4. 패치를 적용하고 target을 같은 과제에 다시 돌린다
5. 성공률 변화가 engineer의 보상이 된다

4개 훅 위치는 이겁니다:

| 훅 위치 | 역할 |
|---|---|
| episode initialization | 시작 컨텍스트, 에피소드 상태 설정 |
| pre-decision | 모델 결정 전에 컨텍스트 보강, 인터페이스 제약 주입 |
| pre-action | 환경에 전달되기 전 액션 정규화/재작성/거부 |
| post-feedback | 관측 검사, 궤적 정체 시 복구 트리거 |

모델 가중치를 건드리지 않고 이 4곳만 건드립니다.

## 훈련: SFT → GRPO

두 단계로 훈련합니다.

**Cold-start SFT.** GPT-5.5가 failure packet에서 패치를 제안하고, 실행 가능하고 회귀가 없는 것만 남겨서 877개 예제를 만듭니다. Qwen3.5-9B를 이걸로 파인튜닝합니다.

**Online GRPO.** 여기서부터가 핵심입니다. failure packet마다 K=8개의 패치를 샘플링하고, 각각 target에 적용해서 다시 돌려봅니다. 나온 보상 차이로 GRPO 업데이트를 합니다. engineer만 업데이트되고 target은 그대로입니다.

보상 식은 단순합니다:

```
r(B, P) = Δ_B(P) if valid and complete, else 0
```

패치가 유효하지 않거나 불완전하면 보상이 0입니다. 실행 결과만이 판단 기준입니다.

## 결과

| 지표 | vanilla target | + Harness-R1 | 변화 |
|---|---|---|---|
| WebShop Succ. | 50.4% | 57.6% | +7.2 |
| ALFWorld All | 40.6% | 53.2% | +12.6 |
| DBBench Succ. | 42.0% | 50.0% | +8.0 |
| 평균 | 44.3% | 53.6% | +9.3 |

SFT만 한 engineer보다 7.1포인트 높고, 가장 강한 프롬프트 기반 에디터(GLM-5.2, 48.8%)보다도 4.8포인트 위입니다.

더 흥미로운 건 target agent를 직접 파인튜닝한 후에도 효과가 있다는 겁니다. target SFT로 평균이 59.2%까지 오르는데, 여기에 target-specific Harness-R1을 얹으면 64.2%가 됩니다. +5.0포인트 추가 이득입니다.

## 일반화

![Figure 3: 학습에 쓰지 않은 20개 target 모델에 대한 성공률 변화. 전부 양수.](/images/2026-08-05-harness-r1-executable-runtime-harness-rl/fig-3-p8.png)

20개의 안 본 target 모델에 적용해봤습니다. 평균 +7.06포인트, 전부 양수였습니다. 63개 조합 중 56개가 개선, 3개만 미세 하락(≤2.0포인트)이었습니다.

![Figure 4: (a) 희소 실패로부터 일반화, (b) 라이프사이클 위치별 기여도](/images/2026-08-05-harness-r1-executable-runtime-harness-rl/fig-4a-p8.png)

흥미로운 결과: failure 10개만 보고 만든 패치를 1,270개 안 본 과제에 적용해도 +8.9포인트입니다. 같은 설정에서 Qwen3.5-397B는 -4.3, DeepSeek-V4-Pro는 -0.4였습니다. 스케일만으로는 안 되는 능력입니다.

## 어느 위치가 중요한가

라이프사이클 훅을 하나씩 빼보는 ablation입니다:

- pre-action 제거 → -3.9포인트 (가장 큰 영향)
- post-feedback 제거 → -3.3포인트
- episode-start 제거 → -0.9포인트
- pre-decision 제거 → -0.6포인트

근데 환경마다 다릅니다. WebShop은 pre-action이 가장 중요하고, ALFWorld은 post-feedback recovery가 가장 중요합니다. 고정 전략으로는 이걸 선택할 수 없습니다.

## 왜 중요한가

기존 하네스 최적화는 proposer가 고정되어 있었습니다. Meta-Harness, AHE, AutoHarness 모두 에디터를 훈련시키지 않고 탐색이나 선택만 합니다. Harness-R1은 에디터 자체를 outcome 기반으로 훈련시키는 최초의 방법입니다.

9B 모델이 397B 모델보다 하네스를 더 잘 고칩니다. 핵심은 outcome 기반 훈련 루프에 있습니다. 결과를 보고 배운 9B가 그냥 제안만 하는 397B를 이깁니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 한계

- 같은 배치 과제에서 보상을 계산하므로 훈련 신호가 과제 구성에 묶임
- multi-round co-evolution(타겟과 engineer를 번갈아 업데이트)은 후속 연구 과제
- 패치의 inference 비용은 보상에 들어가지 않음

코드와 모델은 공개되어 있습니다: [GitHub](https://github.com/DeepExperience/Harness-R1), [HuggingFace](https://huggingface.co/ShaoShuai0605/Harness-R1)
