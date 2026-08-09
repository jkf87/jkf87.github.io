---
title: "TCPO: 검증자 점수가 있는데도 크레딧을 모르는 문제 — 에이전트 RL의 점수→크레딧 변환"
date: 2026-08-09
tags:
  - agent
  - reinforcement-learning
  - LLM
  - credit-assignment
  - multi-turn-RL
  - GRPO
  - verifier-guided
  - loop
---

에이전트 RL에서 검증자(verifier)가 매 턴 점수를 준다. 그런데 이 점수만 있다고 "어느 턴이 공로가 있는지" 알 수 있을까? Moore Threads AI의 새 논문 TCPO는 이 질문에 대해 단호하게 "아니다"라고 답한다.

## 점수와 크레딧은 다르다

상황을 이렇게 생각해보자. 에이전트가 3턴에 걸쳐 수학 문제를 푼다.

- 1턴: 30점 (시도했지만 틀림)
- 2턴: 30점 (다른 접근, 여전히 틀림)
- 3턴: 100점 (드디어 정답)

여기서 2턴은 쓸모없는 실패일까? 아니면 3턴의 정답을 이끌어낸 중요한 발판일까? 반대로:

- 1턴: 100점 (한 번에 정답)
- 2턴: 100점 (같은 답 유지)
- 3턴: 60점 (답을 바꿔서 틀림)

3턴은 명백한 회귀다. trajectory-level reward는 이 셋을 똑같이 100점으로 취급한다. GRPO의 시퀀스 수준 어드밴티지는 구체적으로 어느 턴이 공로인지 알려주지 않는다.

TCPO가 정의하는 문제가 바로 이것이다. **Score-to-Credit Conversion**: 매 턴 들어오는 점수를, 턴의 실제 기여도로 변환하라.

![TCPO 파이프라인](/images/2026-08-09-tcpo-turn-level-credit-policy-optimization/fig-1-p3.png)

## TCPO의 삼중 렌즈

TCPO는 점수를 세 가지 관점에서 해석한다.

### 렌즈 1: "이전 최고점"과의 비교 (Retrospective)

가장 직관적이다. 턴 k의 점수가 턴 k 이전의 최고점보다 높으면 → 개선 크레딧. 성공 상태를 그대로 유지하면 → 보존 크레딧. 성공 이후 점수가 떨어지면 → 회귀 페널티.

이것만으로도 trajectory-level reward보다 훨씬 정밀하다.

### 렌즈 2: "다른 평행 우주"와의 비교 (Hindsight)

같은 프롬프트에 대해 8개의 궤적을 샘플링한다고 하자. 턴 2에서 점수가 오르지 않았지만, 턴 3에서 100점에 도달한 궤적이 있다. 반면 다른 궤적들은 턴 2에서 비슷한 상태였는데 턴 3에서도 실패했다.

그렇다면 이 궤적의 턴 2는 "보이지 않는 기여"를 한 것이다. TCPO는 같은 턴 인덱스를 가진 다른 궤적들의 future-best 점수 평균과 비교해서 이 값을 계산한다. 추가 검증자 호출이 필요 없다.

### 렌즈 3: "같은 상황에서 다른 선택"과의 비교 (Counterfactual)

가장 모호한 턴에 대해서만 작동한다. 서프라이즈가 높은 턴(모델이 불확실해서 다양한 출력이 나올 수 있는 상황)을 최대 L개 선택한다.

그 턴의 히스토리를 고정하고 M개의 대안 출력을 샘플링한다. 각각을 검증자로 평가한다. 원래 출력이 대안 평균보다 좋았으면 양의 크레딧, 나빴으면 음의 크레딧.

전체 턴에 적용하면 비용이 많이 들지만, high-surprisal 턴만 타겟팅하므로 오버헤드가 3~5%에 그친다.

## 숫자로 보는 결과

![메인 결과](/images/2026-08-09-tcpo-turn-level-credit-policy-optimization/table-1-p6.png)

Qwen3-4B 기준 MATH-500에서 MT-GRPO 대비 +4.4점, DeepSeek-R1-Distill-Llama-8B에서는 +6.2점 개선. 코드 생성(LiveCodeBench)에서도 일관된 이득이 있다.

![AppWorld 결과](/images/2026-08-09-tcpo-turn-level-credit-policy-optimization/table-2-p8.png)

특히 주목할 점은 AppWorld 결과다. 상태가 유지되는 툴 사용 환경에서도 TGC/SGC가 개선된다. 수학나 코드와는 완전히 다른 검증자 구조인데도 효과가 있다.

![크레딧 분해](/images/2026-08-09-tcpo-turn-level-credit-policy-optimization/table-3-p8.png)

각 렌즈의 기여를 분리하면, retrospective를 더할 때 가장 큰 점프가 발생한다. hindsight와 counterfactual은 각각 추가 이득을 가져온다.

![반사실 예산](/images/2026-08-09-tcpo-turn-level-credit-policy-optimization/table-4-p7.png)

반사실 추정의 효율성도 확인할 수 있다. 랜덤 선택은 거의 효과가 없고, high-surprisal 타겟팅이 핵심이다.

## 왜 중요한가

에이전트 RL에서 가장 어려운 문제 중 하나가 "긴 궤적에서 어느 결정이 공로인가"다. TCPO는 이미 매 턴 들어오고 있는 검증자 점수를 재료로 삼아, 이 문제에 대한 실용적인 답을 제시한다.

필요한 건 기존 롤아웃 데이터뿐. 추가 라벨, 학습된 크리틱, 복잡한 인프라가 없다. GRPO 파이프라인에 얹어서 쓸 수 있다.

![분석](/images/2026-08-09-tcpo-turn-level-credit-policy-optimization/fig-2-p8.png)

분석 결과도 흥미롭다. 궤적이 길어질수록(MATH는 3턴, AppWorld는 20턴) 턴별 크레딧의 가치가 커진다. 에이전트가 더 오래 일할수록, 어떤 턴이 진짜 기여했는지 구분하는 게 더 중요해진다.

## 요약

TCPO의 핵심 통찰: 검증자 점수는 관측이지 크레딧이 아니다. 관측을 크레딧으로 바꾸려면 기준이 필요하다. TCPO는 세 가지 기준(이전 최고점, 평행 궤적의 결과, 같은 상황의 대안)을 조합해서 턴별 크레딧을 만든다. 오버헤드는 3~5%, AppWorld 에이전트까지 개선.

논문: [arXiv:2608.01667](https://arxiv.org/abs/2608.01667)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
