---
title: "Dr. MAS: 멀티에이전트 LLM 강화학습이 터지는 이유와 에이전트별 정규화 해법"
date: 2026-09-11
tags:
  - llm
  - multi-agent
  - reinforcement-learning
  - grpo
  - paper-review
draft: false
description: "GRPO의 전역 어드밴티지 정규화가 멀티에이전트 LLM 학습에서 그래디언트 폭주를 일으키는 원인과, 에이전트별 평균·표준편차 정규화로 수학 +5.6%, 검색 +15.2%를 얻은 Dr. MAS 논문 정리."
---

## 결론 먼저

멀티에이전트 LLM 시스템에 GRPO를 그대로 걸면 학습이 불안정해지는 이유를 이 논문은 수학적으로 짚었습니다. <span style="background-color: #fff59d"><strong>모든 에이전트에게 하나의 전역 평균/표준편차로 어드밴티지를 정규화하면, 역할마다 reward 분포가 다른데 그 차이가 그래디언트 노름 폭주로 이어진다</strong></span>는 겁니다.

해법은 단순합니다. <span style="background-color: #fff59d"><strong>각 에이전트가 자기 데이터의 평균(μk)과 표준편차(σk)로 자기 어드밴티지를 정규화</strong></span>하면 됩니다. 이걸 Dr. MAS라고 부릅니다.

결과(기준일 2026-02 arXiv v1 기준):

| 항목 | vanilla GRPO | Dr. MAS | 차이 |
|---|---|---|---|
| 수학 avg@16 (전체 평균 개선) | 기준 | +5.6% | Qwen3-4B/8B, solver+verifier 2에이전트 |
| 수학 pass@16 | 기준 | +4.6% | 동일 설정 |
| 멀턴 검색 avg@16 | 기준 | +15.2% | Qwen2.5-3B/7B, verifier+search+answer 3에이전트 |
| 검색 pass@16 | 기준 | +13.1% | 동일 설정 |
| 그래디언트 스파이크 | 잦음, NaN까지 | 대부분 제거 | Figure 4, 7 |

논문: [arXiv:2602.08847](https://arxiv.org/abs/2602.08847) (2026-02-09, NTU, Lang Feng 외, Bo An 교수 그룹)
코드: [github.com/langfengQ/DrMAS](https://github.com/langfengQ/DrMAS)

## 문제 정의: 왜 멀티에이전트에서 GRPO가 흔들리나

GRPO는 그룹 단위로 rollout을 모아 그룹 평균을 baseline으로 씁니다. 단일 에이전트에서는 잘 작동하는 구조구요.

근데 멀티에이전트로 오면 상황이 달라집니다.

- 에이전트마다 호출 빈도가 다릅니다. verifier는 매 턴 도는데 search agent는 조건부로 도는 식이에요.
- 역할이 다르니 reward 분포 자체가 다릅니다.
- 그런데도 <span style="background-color: #fff59d"><strong>전역 baseline 하나로 모든 에이전트의 어드밴티지를 정규화하면, 실제 분포와 baseline이 어긋난 에이전트의 그래디언트가 비정상적으로 커집니다</strong></span>.

논문은 이 어긋남이 그래디언트 이차 모먼트를 키워서 그래디언트 노름 폭발로 이어진다고 수학적으로 보여줍니다. 실측에서도 vanilla GRPO는 search agent의 그래디언트 노름이 80을 넘긴 뒤 NaN으로 죽는 걸 확인했습니다 (Appendix E.2, Figure 7).

![](/images/2026-09-11-dr-mas-stable-multi-agent-llm-rl/fig-4-p9.png)
*Figure 4: GRPO(위)와 Dr. MAS(아래)의 학습 정확도·그래디언트 노름 비교. 3에이전트 검색 오케스트레이션, Qwen2.5-3B 비공유 설정. GRPO는 스파이크가 계속 나오는데 Dr. MAS는 평탄합니다. 출처: arXiv:2602.08847 Figure 4.*

## Dr. MAS의 수정: 에이전트별 (μk, σk) 정규화

레시피 자체는 한 줄입니다.

```text
어드밴티지 계산 시:
- 경험을 에이전트별로 그룹핑
- 각 에이전트 k는 자기 그룹의 평균 μk, 표준편차 σk로 정규화
A_k = (r - μk) / σk
```

<span style="background-color: #fff59d"><strong>전역 통계 대신 에이전트 자기 통계를 쓰는 것만으로 그래디언트 스케일이 보정</strong></span>되고, 학습이 안정화됩니다.

### 어블레이션: 어떤 통계를 에이전트별로 바꿔야 하나

Qwen2.5-7B 검색 태스크, 비공유 설정에서 4가지 구성을 비교했습니다.

| 정규화 구성 | avg@16 | pass@16 |
|---|---|---|
| (μ, σ) 전역 — vanilla GRPO | 28.0 | 40.5 |
| (μk, σ) 에이전트별 평균만 | 39.1 (+11.1) | 53.5 (+13.0) |
| (μ, σk) 에이전트별 표준편차만 | 42.9 (+14.9) | 57.6 (+17.1) |
| (μk, σk) 둘 다 — Dr. MAS | 43.8 (+15.8) | 58.3 (+17.8) |

표준편차 쪽 기여가 더 큽니다. 에이전트 간에 어드밴티지 평균 차이보다 퍼짐(스케일) 차이가 더 크다는 뜻이에요.

## 실험 설정 1: 수학 — solver/verifier 2에이전트

solver가 풀이를 제안하고, verifier가 검토해서 통과시키거나 수정을 요청하는 루프입니다. 최대 2회 루프, 그룹 크기 8, binary reward(성공 1/실패 0), 학습률 1e-6.

Qwen3-4B/8B로 공유(모델 하나를 역할마다 공동학습)와 비공유(역할마다 별도 파라미터) 설정을 둘 다 돌렸습니다.

- Qwen3-4B 공유: 56.8/70.7 → 59.0/73.2
- Qwen3-4B 비공유: 57.5/74.4 → 61.1/77.7
- Qwen3-8B AIME'24: <span style="background-color: #fff59d"><strong>42.7/66.7 → 54.8/80.0</strong></span>

<span style="background-color: #fff59d"><strong>비공유 설정에서 개선이 더 큽니다. 파라미터가 독립일수록 행동 분포가 더 벌어지니, 에이전트별 보정이 더 중요해지는 거죠.</strong></span>

![](/images/2026-09-11-dr-mas-stable-multi-agent-llm-rl/table-1-p7.png)
*Table 1: 수학 태스크 전체 결과. Qwen3-4B/8B, avg@16/pass@16. 출처: arXiv:2602.08847 Table 1.*

## 실험 설정 2: 멀턴 검색 — verifier/search/answer 3에이전트

verifier가 정보 충분 여부를 판단하고, 부족하면 search agent에게 외부 검색을, 충분하면 answer agent에게 최종 답 합성을 맡깁니다. 최대 4턴, 그룹 크기 5, Qwen2.5-3B/7B.

여기서 vanilla GRPO의 실패가 극명하게 드러납니다.

<span style="background-color: #fff59d"><strong>Qwen2.5-7B 비공유에서 vanilla GRPO는 그래디언트 노름이 커지면서 검색 호출 자체를 회피하도록 학습되어 28.0/40.5로 추락했습니다.</strong></span> Dr. MAS는 같은 설정을 43.8/58.3로 복원했고, 이는 단일 에이전트 baseline과 공유 설정보다도 높습니다.

![](/images/2026-09-11-dr-mas-stable-multi-agent-llm-rl/table-2-p8.png)
*Table 2: 멀턴 검색 QA 결과. Qwen2.5-3B/7B. 출처: arXiv:2602.08847 Table 2.*

## 시스템 프레임워크: 오케스트레이션부터 코트레이닝까지

알고리즘 외에 프레임워크 기여도 있습니다.

![](/images/2026-09-11-dr-mas-stable-multi-agent-llm-rl/fig-2-p5.png)
*Figure 2: 멀티에이전트 LLM RL 프레임워크 개요. 출처: arXiv:2602.08847 Figure 2.*

- 논리 에이전트 K개를 물리적 LLM 워커 그룹으로 매핑합니다. 비공유면 역할마다 별도 워커(예: 7B + 3B), 공유면 같은 모델끼리 하나의 워커 그룹으로 묶어 공동학습합니다.
- <span style="background-color: #fff59d"><strong>에이전트별 학습 설정(최적화 하이퍼파라미터)을 따로 둘 수 있고, 액터 백엔드 자원을 공유 스케줄링</strong></span>합니다.
- 기존 veTRL/ROLL/AReaL류 대규모 RL 프레임워크는 단일 액터 최적화 중심이라 이런 멀티에이전트 오케스트레이션이나 여러 LLM 코트레이닝이 자연스럽지 않았다는 게 저자들의 지적입니다.

## 이질 모델 배치: 상위에 큰 모델, 하위에 작은 모델

실무적으로 가장 와닿는 결과입니다.

verifier에만 Qwen2.5-7B를 두고 search/answer에 Llama-3.2-3B-Instruct를 쓰는 이질 구성을 전체 7B 동질 구성과 비교했습니다.

- 성능: 거의 동일
- 비용: <span style="background-color: #fff59d"><strong>API 비용 41.8% 절감, 지연 31.6% 절감</strong></span> (OpenRouter 기준 시가로 추정, 7B $0.30/M, 3B $0.06/M 토큰)

<span style="background-color: #fff59d"><strong>계층형 멀티에이전트에서는 최상위 판단자(verifier)만 강하면 전체 품질이 유지되고, 하위 실행 에이전트는 작은 모델로 바꿔도 된다</strong></span>는 결론입니다. 배포 설계에 바로 쓸 수 있는 가이드라인이에요.

![](/images/2026-09-11-dr-mas-stable-multi-agent-llm-rl/fig-5-p9.png)
*Figure 5: 동질(전체 7B) 대 이질(verifier 7B, 나머지 3B) 구성의 성능·효율 비교. 출처: arXiv:2602.08847 Figure 5.*

## 내 해석: 어디까지 믿을 것인가

원문 근거와 제 해석을 구분해서 적습니다.

원문이 명확히 보여준 것:

- 전역 정규화 → 그래디언트 불안정의 인과관계 (이론 + 실측)
- (μk, σk) 정규화로 수학/검색 양쪽 일관된 개선
- NaN 사례 재현 (Appendix E.2)

제 해석 / 주의 포인트:

- 실험이 role-specialized 오케스트레이션 2종(2에이전트 수학, 3에이전트 검색)으로 한정됩니다. 자유로운 대화형 멀티에이전트나 코드 에이전트 같은 더 복잡한 위상에 그대로 일반화하긴 이릅니다.
- binary reward(성공/실패) 기준입니다. 연속 reward나 보상 셰이핑이 섞이면 에이전트별 분포 차이도 다른 양상을 보일 수 있어요.
- 그래도 수정 자체가 어드밴티지 정규화 한 줄이라 도입 비용이 거의 없습니다. 멀티에이전트 RL을 돌리고 있다면 가장 먼저 시도해볼 후보입니다.

## 요약 체크리스트

- GRPO를 멀티에이전트에 그대로 쓰면 전역 baseline과 에이전트별 reward 분포가 어긋나며 그래디언트가 폭주한다.
- 해법은 에이전트별 (μk, σk) 어드밴티지 정규화. 수학 +5.6% avg@16, 검색 +15.2% avg@16, 스파이크 대부분 제거.
- 표준편차(σk)를 에이전트별로 두는 것이 평균(μk)보다 기여가 크다.
- 상위 verifier만 7B, 하위를 3B로: 성능 유지 + 비용 41.8% 절감 + 지연 31.6% 절감.
- 프레임워크는 공유/비공유 코트레이닝, 에이전트별 최적화 설정, 자원 공유 스케줄링을 지원한다.

## 자주 묻는 질문

### Dr. MAS가 GRPO에서 바꾸는 부분은 정확히 무엇인가요?

어드밴티지 정규화 통계를 전역 (μ, σ)에서 에이전트별 (μk, σk)로 바꾸는 것입니다. rollout을 에이전트별로 그룹핑하고 각자 자기 평균/표준편차로 나눕니다. 다른 학습 절차는 그대로입니다.

### 단일 에이전트 GRPO에서도 써야 하나요?

아니요. 단일 에이전트에서는 그룹 내 분포가 하나라 전역 정규화가 이미 자기 통계와 같습니다. 논문도 단일 에이전트 GRPO이 baseline로 정상 작동함을 보여줍니다.

### NaN이 실제로 재현되나요?

네. Appendix E.2의 Figure 7에서 Qwen2.5-7B 비공유 검색 태스크에서 vanilla GRPO의 search agent 그래디언트 노름이 80 이상으로 치솟은 뒤 NaN이 되었습니다. Dr. MAS는 같은 설정에서 낮은 그래디언트 노름을 유지합니다.

### 비용 절감 수치는 어떻게 나온 건가요?

51.7k 샘플 테스트셋 전체 추론 비용을 OpenRouter 시가(7B $0.30/M, 3B $0.06/M 토큰)로 환산한 추정치입니다. 실제 배포 단가에 따라 달라질 수 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 출처

- 논문: Dr. MAS: Stable Reinforcement Learning for Multi-Agent LLM Systems — [arXiv:2602.08847](https://arxiv.org/abs/2602.08847) (2026-02-09 v1, 기준일 2026-09-11 열람)
- 코드: [https://github.com/langfengQ/DrMAS](https://github.com/langfengQ/DrMAS)
- 저자: Lang Feng, Longtao Zheng, Shuo He, Fuxiang Zhang, Bo An (Nanyang Technological University)
