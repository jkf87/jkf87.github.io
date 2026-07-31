---
title: "Beacon: 에이전트가 도구를 쓸 때와 쓰지 말아야 할 때를 아는 것이 왜 중요한가"
date: 2026-08-01
tags:
  - agent
  - tool-use
  - visual-reasoning
  - LLM
  - reinforcement-learning
  - RL
  - harness
  - MLLM
  - automation
  - GRPO
  - adaptive
  - evaluation
draft: false
---

**에이전트에게 도구를 쥐여주면 오히려 성능이 떨어진다** — 이 역설적인 결론이 Beacon(베이징대·Kling Team)의 분석에서 드러난다. 도구 사용 RL 훈련 후에도 기존 모델들은 "도구가 필요 없는 쉬운 문제에서 도구를 쓰다가 오히려 틀리는" 패턴을 보였고, 이로 인해 도구가 가져다주는 이득이 거의 상쇄되어 버렸다. Beacon은 이 문제를 **Mode Adaptiveness**(언제 도구를 쓸지 아는 능력)와 **Tool Effect**(도구가 실제로 성능을 높이는지)라는 두 가지 차원에서 정의하고, GRPO 기반의 적응적 보상 설계로 해결한다.

![Figure 1: 에이전트 시각 추론 모델은 도구를 적응적으로, 그리고 효과적으로 사용해야 한다.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-1-p1.png)

---

## 도구 사용의 역설: 왜 도구가 이득이 아닌가

시각 추론 에이전트는 이미지를 자르고(crop), 주석을 달고(annotation), 픽셀 단위 연산을 수행하는 Python 코드를 생성하여 복잡한 시각 문제를 푼다. Thyme, DeepEyesV2, CodeV, Metis 등 최근의 에이전트 시각 추론 모델들은 모두 이런 코드 생성 기반의 도구 사용 패러다임을 채택하고 있다.

그런데 Beacon 팀이 이 모델들을 정밀 분석한 결과, 충격적인 패턴이 드러났다.

![Figure 2: (a) 텍스트 단독 정확도 수준별 도구 호출 비율. (b) 13개 벤치마크 평균 성능. (c) 도구 사용으로 인한 성능 향상과 손해.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-2-p2.png)

기존 모델들은 **도구를 쓸 때와 안 쓸 때의 성능 차이(ΔAcc)**가 거의 없었다. Thyme은 -0.18%에서 +2.06% 사이를 오갔고, Metis는 무려 -2.58%의 마이너스 ΔAcc를 기록하기도 했다. 도구를 쓰면 쓸수록 성능이 떨어지는 상황이 발생한 것이다.

핵심 원인은 두 가지다:

1. **무차별 도구 호출**: 문제의 난이도와 관계없이 항상 도구를 쓰거나, 반대로 항상 안 쓰는 모델이 많았다. 즉, "이 문제는 텍스트만으로 풀 수 있는데도 도구를 호출"하거나 "도구가 꼭 필요한데도 텍스트로만 풀려고 하는" 비적응적 행동.

2. **도구 사용으로 인한 손해 > 이득**: 도구가 어려운 문제를 풀어주는 이득(Tool-Gain)보다, 쉬운 문제에서 도구를 잘못 쓰면서 발생하는 손해(Tool-Harm)가 더 크거나 비슷했다.

---

## Mode Adaptiveness와 Tool Effect: 새로운 평가 프레임워크

Beacon의 가장 큰 기여 중 하나는 에이전트 시각 추론 모델을 평가하는 **새로운 측정 기준**을 제안한 것이다.

### Mode Adaptiveness (MA)

모델이 "이 문제에 도구가 필요한가?"를 올바르게 판단하는 능력이다. Beacon은 각 문제를 텍스트 전용으로 5번 추론하여 "text-easy"(4번 이상 정답)와 "text-hard"(1번 이하 정답)로 분류한 뒤, 도구 사용 프롬프트 하에서 모델이 어떤 모드를 선택하는지 측정한다.

- **MA_text**: text-easy 문제에서 도구를 *사용하지 않은* 비율 (높을수록 좋음)
- **MA_tool**: text-hard 문제에서 도구를 *사용한* 비율 (높을수록 좋음)

기존 모델들의 MA_mean(평균)은 대부분 50% 부근이었다. 이는 "항상 도구를 쓰거나 항상 안 쓰는" 무작위 전략과 다르지 않다는 뜻이다.

### Tool Effect (TE)

도구 사용이 실제로 성능에 미치는 영향을 정량화한다.

- **Tool-Gain**: text-hard 문제에서 도구를 사용해 정답을 맞춘 비율
- **Tool-Harm**: text-easy 문제에서 도구를 사용하다가 오답이 된 비율

![Figure 3: (a) 도구 사용 가능 vs 텍스트 전용 정확도. (b) Mode Adaptiveness 지표. (c) Tool-Gain vs Tool-Harm.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-3-p5.png)

결과는 명확했다. 기존 모델들의 ΔTE(Tool-Gain - Tool-Harm)는 거의 0에 가까웠다. 도구를 쓰나 안 쓰나 큰 차이가 없다는 것은, 도구 사용 메커니즘이 제대로 작동하지 않는다는 증거다.

---

## Beacon의 설계: GRPO + 적응적 보상 + 힌트 유도

Beacon은 Qwen3-VL-8B-Instruct를 베이스로 SFT-then-RL 파이프라인으로 훈련된다. 핵심 혁신은 RL 단계의 두 가지 메커니즘에 있다.

![Figure 4: Beacon의 RL 훈련 과정. Necessity-Aware Adaptive Reward와 Hint-Guided Capability Expansion이 적응적 도구 사용과 진정한 성능 향상을 동시에 목표로 한다.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-4-p7.png)

### 1. Necessity-Aware Adaptive Reward (NAAR)

기존 GRPO에서는 정답이면 보상 1, 오답이면 0이다. 하지만 이렇게 하면 모델은 "항상 도구를 쓰는 것"이 안전하다고 학습할 수 있다.

NAAR는 더 정교한 보상 체계를 사용한다:

- **텍스트로 풀 수 있는 문제에서**: 텍스트 전용 정답에 보상 1.0, 코드 사용 정답에 보상 0.25
- **텍스트로 풀 수 없는 문제에서**: 코드 사용 정답에 보상 1.0

이 설계의 핵심은 **"도구를 써서 맞혀도 풀 점수를 주지 않는다"**는 것이다. 텍스트로 충분한 문제에서 도구를 사용하면 75%의 점수를 깎인다. 반대로 텍스트로 못 푸는 문제에서 도구를 쓰면 풀 점수를 받는다. 이렇게 하면 모델이 자연스럽게 "이 문제는 텍스트로 풀 수 있는가?"를 내부적으로 판단하게 된다.

이전의 적응적 도구 사용 접근법들(CodeDance, AdaTooler-V, Metis)과 비교하면, NAAR는 두 가지 이점이 있다:
- **mode-conditioned labeling**: 각 궤적이 실제로 도구를 사용했는지 여부에 기반하여 보상을 차등 지급
- **online labeling**: 교사 모델이 아닌 현재 정책의 성능을 기준으로 문제 난이도를 라벨링 → distribution mismatch 방지

### 2. Hint-Guided Capability Expansion (HCE)

RLVR(강화학습 with 검증 가능한 보상)의 근본적 한계는 **"정책이 처음부터 풀지 못하는 문제는 학습 신호가 없다"**는 것이다. 모든 롤아웃이 틀리면 그룹 내 상대적 어드밴티지가 의미가 없어진다.

HCE는 이 문제를 "전문가의 힌트"로 돌파한다:
1. 정책이 8번 롤아웃해도 전부 틀리면, Gemini 3.1 Pro에게 정답 없는 힌트를 생성
2. 힌트를 프롬프트에 추가해서 다시 8번 롤아웃
3. 힌트가 있는 상태에서 생성된 궤적을 사용하되, **정책 업데이트 시에는 힌트를 제거**한 원래 프롬프트로 importance sampling ratio를 계산

이렇게 하면 힌트에 의존하지 않으면서도, 힌트가 도와준 경험을 통해 모델이 새로운 능력을 획득할 수 있다.

---

## 실험 결과: 13개 벤치마크에서 압도적 1위

Beacon은 13개 벤치마크에서 오픈소스 모델 중 **평균 1위**를 차지했다. 특히 눈에 띄는 것은 도구 사용의 실제 효과다.

| 카테고리 | 벤치마크 | Qwen3-VL-8B | Beacon-8B | 향상 |
|---|---|---|---|---|
| 고해상도 시각 검색 | V* | 84.85 | 89.00 | +4.15 |
| 고해상도 시각 검색 | HR-Bench 4K | 78.13 | 84.30 | +6.17 |
| 공간 추론 | BLINK | 62.86 | 65.96 | +3.10 |
| 공간 추론 | BabyVision | 12.37 | 18.04 | +5.67 |
| 차트 추론 | ChartQAPro | 41.66 | 58.48 | +16.82 |
| 수식 추론 | MathVision | 53.81 | 54.57 | +0.76 |
| 에이전트 시각 추론 | GameQA | 36.70 | 47.30 | +10.60 |
| 복합 추론 | VisualPuzzles | 36.22 | 42.89 | +6.67 |

차트 이해(ChartQAPro +16.82), 게임 QA(GameQA +10.60)에서의 폭발적 향상은 도구 사용이 진짜로 능력을 확장했음을 보여준다.

![Table 4: Beacon 구성 요소별 제거 실험. NAAR와 HCE 각각이 성능에 기여하며, 두 가지를 모두 사용할 때 최고 성능.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/table-4-p12.png)

### 도구 사용의 실제 효과 검증

Beacon의 ΔTE(Tool-Gain - Tool-Harm)는 +1.96%에서 +5.51%로, 기존 모델들이 0에 머물렀던 것과 극명한 대비를 이룬다. 즉, Beacon은 도구를 사용함으로써 **실제로 순수한 성능 향상**을 얻어낸 것이다.

![Figure 5: RL 훈련 과정의 정확도와 보상 곡선. (a) 평균 훈련 정확도. (b) 보상 추이.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-5-p12.png)

### 도구 사용 패턴의 진화

훈련이 진행됨에 따라 Beacon의 도구 사용 패턴이 어떻게 변하는지도 흥미롭다.

![Figure 6: (a) 훈련 중 텍스트 전용 응답과 코드 사용 응답의 비율 변화. (b) 문제 난이도별 도구 사용 비율.](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-6-p13.png)

초기에는 거의 모든 문제에 도구를 사용하려 하지만, 훈련이 진행되면서 text-easy 문제에서는 도구를 줄이고 text-hard 문제에서는 도구를 유지하는 패턴이 나타난다. 이것이 바로 NAAR가 의도한 "적응적 도구 사용"이다.

---

## 왜 이 연구가 중요한가

Beacon의 발견은 에이전트 연구 전반에 구조적인 시사점을 던진다.

**첫째, "도구를 주면 똑똑해진다"는 가정이 틀렸다.** 도구 사용은 분명히 유용하지만, 도구를 언제 쓸지 모르면 오히려 해가 된다. 이것은 단순히 시각 추론에만 해당하는 이야기가 아니다. 터미널 에이전트, 웹 에이전트, 딥리서치 에이전트 — 모든 도구 사용 에이전트가 같은 문제를 안고 있다.

**둘째, 평가 방법이 중요하다.** 기존 연구들은 "전체 정확도"만 보고 도구 사용이 효과적이라고 주장했다. 하지만 Beacon의 MA/TE 프레임워크로 보면, 그 "향상"의 대부분이 SFT 데이터의 효과이지 도구 사용 자체의 효과가 아니었다. 이것은 에이전트 벤치마크 설계에 대한 근본적 질문이다.

**셋째, RLVR의 한계를 구조적으로 돌파했다.** HCE는 "정책이 풀 수 없는 문제"를 힌트로 연결하여 학습 신호를 만들어낸다. 이 패턴은 시각 추론뿐 아니라 코딩 에이전트, 수학 추론 에이전트 등 모든 RLVR 설정에서 재사용 가능하다.

---

## 더 실습해보고 싶은 분들께

Beacon이 보여주는 것은 에이전트의 도구 사용이 "도구를 많이 쓰는 것"이 아니라 "도구를 **잘** 쓰는 것"이라는 사실이다. 이것은 하네스(harness) 설계, 도구 라우팅, 컨텍스트 엔지니어링의 문제이기도 하다. 이런 주제를 더 깊이 실험해보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 루프와 도구 사용을 실제로 구성하고 테스트하는 방법을 다룬다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 하네스의 최적화, 보상 설계, 도구 라우팅을 루프 관점에서 설계하는 실습 강의.

---

> **논문**: [Beacon: Knowing When and How to Perform Agentic Visual Reasoning](https://arxiv.org/abs/2607.28595) (Qixun Wang, Yang Shi et al., Peking University & Kling Team, 2026)
>
> **코드/모델**: [GitHub](https://github.com/NOVAglow646/Beacon) | [HuggingFace](https://huggingface.co/NOVAglow646/Beacon)
