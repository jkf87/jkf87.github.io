---
title: "검증자 없이 에이전트를 학습시키는 방법 — DRACO 동적 루브릭 크레딧 할당 정리"
date: 2026-09-04
draft: false
tags:
  - LLM-agent
  - reinforcement-learning
  - GRPO
  - credit-assignment
  - rubric-reward
description: "프로그램 검증자가 없는 롱호라이즌 에이전트 학습에서, 궤적별 동적 루브릭 점수를 스텝별 어드밴티지로 재분배하는 DRACO를 정리했습니다. AppWorld TGC 85.3, 검증자 학습 대비 +5.3점, 셀프-저지 판정으로 판정 비용 5.1배 절감까지."
---

## 결론 먼저

<span style="background-color: #fff59d"><strong>RLVR는 유닛테스트 같은 프로그램 검증자가 있을 때만 통하는 레시피입니다</strong></span>. 근데 실제 에이전트 도메인 대부분은 검증자가 없습니다. arXiv 2609.04094의 DRACO는 이 문제를 두 단계로 풉니다.

1. <span style="background-color: #fff59d"><strong>궤적마다 루브릭(평가 기준)을 동적으로 생성하고, 판정 모델이 완성된 궤적을 한 번 채점합니다</strong></span>.
2. 그 채점 결과를 <span style="background-color: #fff59d"><strong>GRPO 어드밴티지에 스텝 단위로 재분배합니다</strong></span>.

핵심 수치(Qwen3.6-27B, AppWorld TN, 기준일 2026-09-04):

| 항목 | 값 |
| --- | --- |
| AppWorld TN TGC (p1) | <span style="background-color: #fff59d"><strong>85.3 (베이스 69.4, +15.9)</strong></span> |
| 검증자 보상 학습 대비 | <span style="background-color: #fff59d"><strong>+5.3 TGC, +11.3 SGC</strong></span> |
| τ-bench 제로샷 전이 SR | 20.4 (베이스 15.8, +4.6) |
| 셀프-저지 판정 비용 | $1607 → $316 (5.1배 절감) |
| 학습 시 검증자 사용 | <span style="background-color: #fff59d"><strong>0회</strong></span> |

논문: [arXiv:2609.04094](https://arxiv.org/abs/2609.04094), 코드: [github.com/IBM/draco](https://github.com/IBM/draco)

## 배경: 두 개의 벽

긴 궤적 에이전트 RL에는 벽이 두 개 있습니다.

첫 번째 벽은 보상의 출처입니다. 수학은 정답 매칭, 코딩은 유닛테스트로 검증할 수 있습니다. <span style="background-color: #fff59d"><strong>고객지원 에이전트나 개방형 리서치 에이전트는 이런 오라클이 없고요</strong></span>, 만들려면 문제 자체를 푸는 수준의 비용이 듭니다.

두 번째 벽은 크레딧 할당입니다. AppWorld 궤적은 수십 개의 툴 호출 스텝으로 이루어집니다. <span style="background-color: #fff59d"><strong>GRPO는 궤적 하나에 스칼라 보상을 하나 주고, 그 스칼라를 궤적의 모든 토큰에 똑같이 곱합니다</strong></span>. 성공한 궤적에도 운 좋은 스텝과 불필요한 스텝이 섞여 있고, 실패한 궤적에도 대부분 옳았던 스텝이 있죠. 전체에 같은 신호를 주는 건 통계적으로 낭비이고 학습을 해칠 수도 있습니다.

DRACO의 설정은 이 둘을 합친 outcome-blind 체제입니다. 학습 전 과정에서 <span style="background-color: #fff59d"><strong>정답 신호, 검증자, 골드 앤서에 단 한 번도 접근하지 않습니다</strong></span>.

## 방법 1: 궤적마다 바뀌는 동적 루브릭

미리 짜둔 고정 루브릭은 긴 궤적이 실패하는 다양한 방식을 예측하지 못합니다. DRACO는 태스크마다 루브릭을 만들고 궤적마다 채점합니다.

절차는 이렇습니다.

1. 판정 모델(judge)이 태스크 지시문만 보고 초기 기준을 제안합니다.
2. 샘플링된 롤아웃마다 한 번씩 기준을 확장합니다. 그 롤아웃이 드러낸 서브골과 실제 실패 방식을 추가합니다.
3. 그룹 내 모든 제안을 병합·중복 제거해 하나의 기준 집합 R을 만듭니다. 기준은 상호배타·전체포괄(MECE)을 지키도록 지시하는데, 보상이 비율이라 기준이 겹치면 실수가 이중으로 카운트되기 때문입니다.
4. discriminative dropout: 그룹 내 누구도 통과하지 못한 기준은 유지하고, 모두가 통과한 기준은 버립니다.
5. 동결된(frozen) 판정 모델이 각 궤적을 기준별로 채점합니다. 판정은 <span style="background-color: #fff59d"><strong>pass / fail / not applicable 3값</strong></span>에, 근거와 해당 스텝 번호를 함께 반환합니다.

보상은 적용된 기준 안에서 계산합니다. pi, fi를 적용된 통과·실패 수라 하면 R_i = (p_i − f_i)/(p_i + f_i). 적용 안 된 기준으로 나누지 않으므로 기준 수가 다른 궤적끼리도 그룹 내 비교가 가능합니다.

## 방법 2: 루브릭 판정을 스텝 어드밴티지로 재분배

여기가 논문의 핵심 기여입니다. GRPO의 궤적 어드밴티지 A_i를 스텝별 a_j로 쪼개는 규칙이 <span style="background-color: #fff59d"><strong>닫힌 형태(closed-form)로 주어집니다. 학습된 어트리뷰션 모듈이 없습니다</strong></span>.

스텝 j의 품질은 그 스텝을 인용한 기준의 통과율입니다. Q_j = p_j/(p_j + f_j). 아무 기준도 인용하지 않은 스텝은 인용된 스텝의 평균 Q를 물려받습니다.

가중치는 궤적의 부호를 따릅니다. A_i ≥ 0(승자 궤적)이면 w_j = Q_j로 좋은 스텝을 강화하고, A_i < 0(패자 궤적)이면 w_j = 1 − Q_j로 나쁜 스텝을 억제합니다. 스텝을 인용한 기준이 전부 같은 방향이면 w_j = 0이 되어 업데이트에서 빠지는데, 이게 의도된 동작입니다. 승자 궤적에서 전 기준이 실패한 스텝은 강화하면 안 되니까요.

스텝 어드밴티지는 a_j = A_i · N·w_j / (n_j · Σw_k). n_j는 스텝 j의 토큰 수입니다. 1/n_j 때문에 스텝의 총 기여 n_j·a_j는 길이와 무관해지고, 품질이 곧 영향력이 됩니다. 말이 길다고 점수를 받는 구조가 아닙니다.

이 규칙은 합을 보존합니다. Σ n_j·a_j = A_i·N으로, 재분배가 <span style="background-color: #fff59d"><strong>궤적의 총 푸시를 부풀리거나 깎지 않습니다</strong></span>. 부호도 보존됩니다. a_j가 A_i와 반대 방향이 되는 경우가 없으므로 크레딧이 뒤집히지 않습니다. 저지가 아무 스텝도 인용하지 않으면 베이스라인 GRPO로 폴백합니다.

전체 파이프라인은 논문 Figure 1에 잘 나와 있습니다.

![](/images/2026-09-04-draco-dynamic-rubric-credit-assignment/fig-1-p2.png)

## 실험 설정

- 학습: AppWorld 학습 스플릿 90 태스크, GRPO + LoRA, 그룹 크기 G=6, 8×H100. 베이스 정책은 Qwen3.6-27B(모든 어블레이션)와 Qwen2.5-32B-Instruct.
- 저지: GPT-5.4, temperature 0.1, 동결. 루브릭 생성·병합·채점·재분배 전 단계에서 동일 모델 사용.
- 평가: AppWorld TN(168 태스크) / TC(417 태스크) + τ-bench Banking(97 태스크). τ-bench는 학습에 전혀 쓰지 않은 제로샷 전이입니다. 정답 신호는 평가에만 사용합니다.
- 일관성 지표 p_k: n=3 실행 전부 성공. AppWorld 기존 RL 결과(PPO, GRPO, RLOO, DPO, LOOP 등)는 전부 유닛테스트 보상으로 학습했고, 저자들 주장 기준으로 검증자 없이 AppWorld를 학습한 첫 RL입니다.

## 결과: 숫자로 보기

| 설정 | AppWorld TN TGC p1 | TN SGC p1 | TC TGC p1 | τB SR p1 | 평균 p1 |
| --- | --- | --- | --- | --- | --- |
| Qwen3.6-27B 베이스 | 69.4 | 41.1 | 49.7 | 15.8 | 41.2 |
| Outcome reward(유닛테스트 학습) | 80.0 | 59.3 | 59.9 | 17.6 | 51.0 |
| DRACO w/o Dyn. & Cred. | 81.1 | 59.9 | 60.5 | 19.4 | 52.7 |
| DRACO w/o Cred. | 82.1 | 64.9 | 59.3 | 19.7 | 53.3 |
| DRACO | 85.3 | 70.6 | 61.5 | 20.4 | 55.7 |
| DRACO (셀프-저지) | 81.1 | 62.7 | 61.0 | 21.1 | 52.1 |

![](/images/2026-09-04-draco-dynamic-rubric-credit-assignment/table-2-p6.png)

읽을 포인트 세 가지입니다.

<span style="background-color: #fff59d"><strong>검증자 없이 검증자 학습을 이겼습니다</strong></span>. AppWorld TN에서 DRACO 85.3 vs outcome reward 80.0. 일관성 p3에서는 격차가 더 벌어집니다(<span style="background-color: #fff59d"><strong>TGC +9.5, SGC +13.7</strong></span>).

일관성 향상이 발견(discovery) 향상보다 큽니다. TN TGC pass@3는 +3.9인데 p3는 +25.2입니다. <span style="background-color: #fff59d"><strong>베이스 모델도 한 번은 풀던 태스크를 매번 풀도록 만든 게 학습의 실체라는 뜻입니다</strong></span>.

제로샷 전이도 됩니다. AppWorld만으로 학습했는데 <span style="background-color: #fff59d"><strong>τ-bench에서 15.8 → 20.4</strong></span>. 검증자·골드 앤서·참조 궤적 없이 달성했습니다.

![](/images/2026-09-04-draco-dynamic-rubric-credit-assignment/fig-2-p6.png)

비용도 낮아졌습니다. TN 전체 평가 한 바퀴 기준 DRACO $8.27 vs 베이스 $10.77. 에피소드당 평균 턴 수도 18.7 → 14.7로 짧아졌습니다. 학습이 정확도와 효율을 같이 올린 셈입니다.

## 어블레이션: 두 부품은 <span style="background-color: #fff59d"><strong>같이 써야 합니다</strong></span>

DRACO는 동적 루브릭과 스텝 크레딧 두 부품으로 구성됩니다. 어블레이션의 결론은 두 부품의 상호작용입니다.

TN에서 동적 루브릭에 스텝 크레딧을 얹으면 +3.2 TGC, 둘 다 합치면 고정 루브릭 단독 대비 +4.2 TGC / +10.7 SGC. p3에서는 +8.1 / +14.3으로 벌어집니다. 각 부품 단독 효과는 +0.8, +1.0에 그칩니다.

TC에서는 부호가 뒤집히는 구간도 나옵니다. 고정 루브릭에 스텝 크레딧을 얹으면 p3 TGC가 오히려 −3.7인데, 궤적별 루브릭에서는 +1.4입니다. 이유는 명확합니다. 스텝 크레딧은 특정 스텝을 지목할 만큼 구체적인 기준이 필요한데, 태스크 분포 전체를 향해 쓴 고정 루브릭은 지목할 게 없기 때문입니다.

## 셀프-저지: 프론티어 모델 없이도 됩니다

판정 비용은 파이프라인에서 가장 큰 지출입니다. 저자들은 프론티어 저지를 정책 모델 자체로 바꿔봤습니다. 채점은 k=3회 반복해 세 번 전부 pass여야 pass로 인정하는 방식으로 관대한 판정을 막았습니다.

결과: 100 학습 스텝의 저지 비용이 <span style="background-color: #fff59d"><strong>$1607 → $316, 5.1배 절감</strong></span>. TN에서 81.1/62.7로 outcome-aware 참조(80.0/59.3)를 넘고, τ-bench에서는 전 설정 중 최고 SR 21.1을 기록합니다. 저지 성능 검증도 했는데, 60,689개 기준 판정의 <span style="background-color: #fff59d"><strong>89.4%가 프론티어 저지와 일치</strong></span>했고 불일치는 관대한 방향(30.4% 추가 pass vs 1.3% 추가 fail)이었습니다.

![](/images/2026-09-04-draco-dynamic-rubric-credit-assignment/fig-4-p8.png)

학습 중 루브릭 통과율과 보상이 어떻게 올라가는지는 Figure 4에서 확인할 수 있습니다.

## 내 해석: 어디에 쓸 수 있나

원문 근거와 제 해석을 나눠 정리합니다.

- 원문이 보여준 것: 검증자 없는 설정에서 동적 루브릭 + 닫힌 형태 크레딧 재분배가 검증자 학습보다 나은 결과를 냈고, 그 이유를 어블레이션으로 분해했다.
- 내 해석 1: 실무에서 쓸 수 있는 지점은 보상 설계입니다. "정답 체커가 없어서 RL을 못 한다"가 이제 변명이 아닙니다. <span style="background-color: #fff59d"><strong>기준 문서 + LLM 채점 + 합 보존 재분배만으로 학습 신호가 나옵니다</strong></span>..
- 내 해석 2: 저지 프롬프트 전문이 부록 F에 공개되어 있고 코드가 IBM 오픈소스로 나와 있어서 재현 장벽이 낮습니다. AppWorld 공식 하니스 기준 평가라 비교 가능성도 있습니다.
- 내 해석 3: 한계도 분명합니다. 저지 비용이 여전히 존재하고(셀프-저지로 $316), 채점이 굵은 3값 판정이라 <span style="background-color: #fff59d"><strong>기준 설계 품질이 결과를 좌우합니다</strong></span>. 도메인이 바뀌면 루브릭 템플릿을 다시 다듬어야 합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

DRACO는 학습 중에 정답이나 검증자를 전혀 안 쓰나요? 네, 안 씁니다. 학습 신호는 루브릭 채점만으로 만들고 정답 신호는 평가에서만 사용합니다. 논문은 이를 outcome-blind 체제라고 부르고, AppWorld에서 검증자 없이 학습한 첫 RL이라고 주장합니다.
기존 GRPO와 무엇이 다른가요?** GRPO는 궤적 하나의 스칼라 어드밴티지를 모든 토큰에 똑같이 곱합니다. DRACO는 저지의 기준별 판정을 근거로 그 어드밴티지를 스텝별로 재분배합니다. 총합은 그대로 보존되고 부호도 뒤집히지 않습니다.
스텝 크레딧은 고정 루브릭에서도 효과가 있나요?** AppWorld TC에서는 오히려 p3 TGC가 −3.7 떨어졌습니다. 궤적별 동적 루브릭에서는 +1.4 올랐고요. <span style="background-color: #fff59d"><strong>스텝 크레딧은 기준이 스텝을 지목할 만큼 구체적일 때만 작동합니다</strong></span>..
판정 모델은 꼭 프론티어 모델이어야 하나요?** 아니요. 정책 모델 자기 저지로 k=3 다수결 채점하면 비용이 5.1배 줄고 TN에서 outcome-aware 참조를 넘었습니다. 다만 판정이 프론티어 저지보다 관대한 방향으로 치우칩니다.
주요 숫자는 무엇인가요?** AppWorld TN TGC 85.3(+15.9 vs 베이스, +5.3 vs 검증자 학습), SGC 70.6(+29.5), τ-bench 제로샷 SR 20.4(+4.6), 셀프-저지 저지 비용 $316/100스텝. 기준일 2026-09-04, Qwen3.6-27B 기준입니다.
