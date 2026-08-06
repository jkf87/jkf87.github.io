---
title: "TCPO: 검증자 점수를 크레딧으로 바꾸는 방법 — 멀티턴 에이전트 RL의 핵심 문제"
date: 2026-08-06
tags:
  - agent
  - reinforcement-learning
  - LLM
  - credit-assignment
  - verifier-guided-RL
  - GRPO
  - multi-turn
  - loop
  - automation
source: arxiv
source_url: https://arxiv.org/abs/2608.01667
---

멀티턴 RL에서 검증자(verifier)가 매 턴마다 점수를 준다. 근데 그 점수가 곧 크레딧은 아니다. 이 차이를 못 잡으면, 실패한 행동에 보상을 주고 올바른 수리에 벌점을 물린다.

TCPO(Turn-Level Credit Policy Optimization)는 이 "score-to-credit conversion" 문제를 정면으로 다룬다. Moore Threads AI에서 제안했고, 수학·코드·AppWorld 에이전트 벤치마크에서 기존 GRPO 계열 기법들을 다시 이겼다.

## 핵심 문제: 점수 vs 크레딧

검증자가 턴마다 점수를 주는 환경을 생각해보자. 수학 문제를 풀면 정답 여부로 0 또는 1, 코드면 테스트 통과율이 점수가 된다.

문제는 이 점수가 "이 턴의 기여"를 측정하지 않는다는 거다.

| 상황 | 점수 | 실제 크레딧 |
|------|------|------------|
| 이미 풀린 상태 유지 | 1 (높음) | 유지 보상 필요 |
| 안 고쳤지만 다음 턴의 수리에 기여 | 0 (낮음) | 지연 크레딧 필요 |
| 정답 후 잘못 건드려서 틀림 | 낮아짐 | 회귀 벌점 필요 |

궤적 전체에 최종 점수를 뿌리면(GRPO 방식) 이 셋이 섞인다. 인접 점수 차이(이전 턴과의 diff)도 한계가 있다 — 최고점 갱신인지 단순 요동인지 구분을 못 한다.

## TCPO의 세 가지 참조 비교

TCPO는 기존 롤아웃을 그대로 두고, 검증자 점수 기록을 세 방식으로 변환한다.

### 1. 후향적 크레딧 (Retrospective Credit)

각 턴을 "그 이전의 최고 점수"와 비교한다.

- 최고점 갱신 → 개선 크레딧 (양수)
- 성공 상태 유지 → 유지 크레딧 (양수, 작음)
- 성공 후 하락 → 회귀 벌점 (음수)

수식으로 쓰면:

```
m_{i,k} = max_{t<k} r_{i,t}        # 이전 최고 점수
Δ_{i,k} = [r_{i,k} - m_{i,k}]_+    # 개선분
```

성공 임계값 τ 넘은 뒤 점수가 유지되면 유지 보상, 떨어지면 회귀 벌점.

### 2. 사후 지연 크레딧 (Hindsight Delayed Credit)

점수가 오르지 않았지만 나중에 수리로 이어지는 턴이 있다. 이걸 잡기 위해, 완료된 롤아웃에서 그 턴 이후의 최고 점수를 돌아본다.

같은 프롬프트, 같은 턴 위치를 가진 다른 궤적들과 비교해서 지연 보상을 준다.

### 3. 고정 이력 반사실 추정 (Fixed-History Counterfactual)

크레딧이 가장 불확실한 턴(높은 surprisal)을 골라서, 같은 이력에서 대안 출력을 샘플링한다. 검증자로 점수를 비교하면 "이 턴이 정말 기여했는지"를 더 정확히 잴 수 있다.

비용 효율을 위해 surprisal 상위 L개 턴만 선택한다 (수학 L=5, 코드·AppWorld L=10). 전체를 다 하면 1.11–1.16배 비용이지만, 선택적으로 하면 1.03–1.05倍 overhead로 끝난다.

![](/images/2026-08-06-tcpo-turn-level-credit-policy-optimization/fig-1-p3.png)

## 실험 결과

### 수학·코드

![](/images/2026-08-06-tcpo-turn-level-credit-policy-optimization/table-1-p6.png)

Qwen3-4B 기준 MT-GRPO 대비 MATH-500 +4.4점, AIME +2.2점, LiveCodeBench +1.6점. DeepSeek-R1-Distill-Llama-8B에서는 격차가 더 벌어진다 — 초기 모델이 약할수록 궤적에 실패와 수리가 섞여 있어서 크레딧 분리의 효과가 크다.

성공까지 걸리는 평균 턴 수도 줄어든다. MATH-500 기준 GRPO 1.84턴 → TCPO 1.59턴.

### AppWorld 에이전트

![](/images/2026-08-06-tcpo-turn-level-credit-policy-optimization/table-2-p8.png)

Qwen2.5-32B-Instruct로 AppWorld를 돌렸다. Dev TGC 84.2 → 88.3, Test-N TGC 72.6 → 74.4. 상태를 유지하고 갱신해야 하는 긴 호라이즌 에이전트에서도 유효하다.

### 크레딧 신호 분해

![](/images/2026-08-06-tcpo-turn-level-credit-policy-optimization/table-3-p8.png)

궤적 보상 → 턴 보상 → 점수 차이 → 후향 → 후향+사후 → TCPO 순으로 하나씩 추가할 때마다 점수가 오른다. 점수를 더 조밀하게 주는 게 아니라, 같은 점수을 더 올바른 참조로 변환하는 게 핵심이라는 걸 보여준다.

### 반사실 예산

![](/images/2026-08-06-tcpo-turn-level-credit-policy-optimization/table-4-p8.png)

반사실 추정을 모든 턴에 적용하면 성능은 더 높아지지만(66.8% MATH-500), 훈련 비용이 1.11–1.16배로 오른다. surprisal 상위만 선택하면 1.03–1.05倍 비용으로 65.2%를 달성한다. 무작위 선택은 효과가 없다 — 어디에 예산을 쓰느냐가 중요하다.

## 분석

![](/images/2026-08-06-tcpo-turn-level-credit-policy-optimization/fig-2-p8.png)

TCPO가 부여하는 크레딧을 턴 유형별로 보면: 개선·유지에는 양수, 회귀에는 음수가 할당된다. 턴 인덱스별로는 초기 턴이 더 큰 크레딧을 받는다 — 빠른 수리를 장려하는 설계다.

터수가 늘어남에 따른 성능 포화도 과제마다 다르다. MATH-500은 3턴이면 충분하고, LiveCodeBench는 5턴, AppWorld는 20턴까지 오른다. 궤적이 길어질수록 궤적 수준 보상이 더 혼란스러워진다.

## 정리

TCPO가 말하는 핵심은 단순하다. 검증자 점수가 이미 매 턴 있다면, 더 조밀한 보상을 만드는 게 아니라 그 점수을 올바른 턴 크레딧으로 변환하는 게 문제다. 세 가지 참조(후향·사후·반사실)로 이 변환을 하면 수학·코드·에이전트에서 일관되게 개선된다.

코드는 공개 예정이며, GRPO 스타일 목적에 바로 끼워넣을 수 있다.

## 더 실습해보고 싶은 분들께

에이전트 RL 루프와 크레딧 할당은 직접 구현해봐야 감이 잡힙니다. 두 가지 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 도구 사용 루프를 실험하는 50가지 사례
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 훈련 루프의 설계와 최적화를 다루는 실무 강의
