---
title: "에이전트 RL에서 스킬은 가르칠 때와 방해할 때를 구분해야 한다 — AUSO 정리"
date: 2026-08-24
tags: [agent, LLM, RL, skill, GRPO, credit-assignment]
draft: false
---

에이전트에 스킬을 넣어 강화학습을 시키는 방식이 몇 갈래로 갈려 있습니다. 스킬을 컨텍스트에 두고 쓰기만 하는 방식, 스킬을 모델 안으로 완전히 내재화하는 방식, 그리고 둘 중 무엇을 할지 태스크 성공률로 고르는 방식이요. 중국과학기술대학·UNSW 공동 팀이 8월 21일에 올린 [AUSO 논문](https://arxiv.org/abs/2608.21292)은 이 흐름에 "액션 단위"라는 축을 하나 추가합니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>스킬이 트레이토리 전체에 균일하게 좋거나 나쁜 게 아니라, 같은 트레이토리 안에서도 어떤 액션은 돕고 어떤 액션은 방해한다</strong></span>는 것.

## 기존 방식의 문제

저자들이 지적하는 문제는 두 가지입니다.

첫 번째는 학습 목표가 쪼개져 있다는 것. Skill0 계열은 스킬을 컨텍스트에 남겨두고, Skill1 계열은 스킬을 가중치에 증류해서 없애버립니다. Skill0.5는 둘 사이를 태스크 성공률로 고르는데, <span style="background-color: #fff59d"><strong>이 성공률이 노이즈가 크다</strong></span>는 게 문제라고 지적합니다. 저자들의 Figure 1 관찰에 따르면 중간 난이도·쉬운 태스크에서 스킬 컨텍스트 유무의 성공률 차이가 애매하게 뒤집히는 구간이 있다고 해요.

두 번째는 트레이토리 안의 모든 액션에 같은 중요도를 준다는 것. 순수 GRPO는 결과 보상을 액션별로 균일하게 분배합니다. 근데 실제로는 <span style="background-color: #fff59d"><strong>스킬 문서가 어떤 스텝에서는 정답으로 이끌고, 어떤 스텝에서는 오히려 시선을 흩트립니다</strong></span>. 이걸 구분하지 않으면 좋은 액션과 나쁜 액션이 같은 크기로 업데이트됩니다.

## AUSO의 3단계 설계

AUSO는 학습 진행에 따라 목표를 바꾸는 단계적 구조입니다. 백본은 GRPO로 고정돼 있고, <span style="background-color: #fff59d"><strong>위에 얹히는 신호가 바뀝니다</strong></span>.

| 단계 | 이름 | 하는 일 |
|---|---|---|
| 초반 | General Skills Internalization | 교사 정책에서 증류(JSD)로 범용 스킬 내재화, 성공한 태스크는 증류 끔 |
| 중반 | Skills Exploration | 순수 GRPO 탐험으로 자립 능력 형성 |
| 후반 | Specific Skill Utilization | 액션별 스킬 기여를 계산해 업데이트 강도 재분배 |

초반 증류는 시간에 따라 ramp-up 후 smooth decay하는 계수로 조절됩니다. <span style="background-color: #fff59d"><strong>이미 성공하는 태스크(성공률 p_q ≠ 0)는 증류에서 빼서, 배울 게 없는 곳에 교사 신호를 쓰지 않게 한 것</strong></span>이 세부 설계 포인트예요.

## 액션 단위 스킬 기여 측정

후반부가 이 논문의 메인 기여입니다. 같은 방문 상태 h_t에서 같은 정책을 두 컨텍스트로 평가합니다.

π_θ(·|h_t, C=Skill) vs π_θ(·|h_t, C=No-skill)

두 분포의 정보량 차이를 액션의 <span style="background-color: #fff59d"><strong>'스킬 민감도'</strong></span>로 씁니다. <span style="background-color: #fff59d"><strong>추가 롤아웃이 필요 없어서 계산 비용이 붙지 않는 것</strong></span>이 장점이에요. <span style="background-color: #fff59d"><strong>인공 보상을 새로 만들지 않</strong></span>습니다. 대신 <span style="background-color: #fff59d"><strong>결과 어드밴티지의 업데이트 강도를 재분배</strong></span>합니다. 성공 트레이토리에서 민감도가 높은 액션은 더 크게 강화하고, 실패 트레이토리에서 민감도가 높은 액션은 더 크게 억제하고, 정보량이 낮은 액션은 업데이트를 줄입니다.

![](/images/2026-08-24-auso-action-level-skill-optimization/fig-2-p5.png)

*Figure 2: AUSO 전체 파이프라인 — 내재화 → 탐험 → 액션 단위 활용 (원문 Figure 2)*

## 성능 수치

백본은 Qwen2.5-7B-Instruct, H200 4장, 롤아웃 그룹 G=8입니다. Skill0.5와 동일한 설정이라 비교가 공정합니다.

ALFWorld에서 결과가 가장 큽니다. <span style="background-color: #fff59d"><strong>ID 평균 94.3, OOD 평균 67.9</strong></span>로, Skill0.5(58.5 OOD)보다 OOD에서 <span style="background-color: #fff59d"><strong>9.4포인트 앞섭니다</strong></span>. WebShop도 <span style="background-color: #fff59d"><strong>ID 49.7 / OOD 51.2</strong></span>로 기존 최고 대비 각각 5.5, 5.3포인트 개선됐습니다.

![](/images/2026-08-24-auso-action-level-skill-optimization/table-2-p7.png)

*Table 2: SearchQA 결과 (원문 Table 2)*

SearchQA는 격차가 작습니다. <span style="background-color: #fff59d"><strong>평균 47.5로 SkillRL(47.1)과 0.4포인트 차이</strong></span>예요. 저자들도 서치 태스크는 스킬 문서가 주는 정보가 상대적으로 균질해서 액션 단위 구분이 벌어질 공간이 적은 걸로 읽히는 것 같습니다. 제 해석이지만, OOD 일반화가 크게 벌어지는 ALFWorld·WebShop이 액션 단위 신호의 이득을 가장 크게 받는다는 결과 흐름은 일관됩니다.

![](/images/2026-08-24-auso-action-level-skill-optimization/table-4-p8.png)

*Table 4: 단계 비율(내재화:탐험:활용)에 대한 소거 실험 (원문 Table 4)*

소거 실험(Table 3)에서는 액션 단위 처리를 빼면 두 단계 모두 성능이 떨어지는데, 특히 활용 단계의 액션 처리를 빼면 <span style="background-color: #fff59d"><strong>ALFWorld OOD가 67.9에서 49.1로 무너집니다</strong></span>. 내재화 감쇠를 제거한 경우도 ID가 94.3에서 83.9로 하락합니다. 단계 비율은 <span style="background-color: #fff59d"><strong>2:5:3이 최적</strong></span>이었고, 균등 분배(3.3:3.3:3.3)는 OOD 41.5로 더 나빴습니다.

![](/images/2026-08-24-auso-action-level-skill-optimization/fig-4-p8.png)

*Figure 4: 액션 선택 후보 K에 따른 ID/OOD 성공률 (원문 Figure 4)*

## 내 해석

제가 이 논문에서 가져갈 점은 두 가지입니다.

'스킬 사용 여부'라는 이진 선택 대신 <span style="background-color: #fff59d"><strong>'이 액션에서 스킬이 정보를 더했나'라는 연속 신호</strong></span>를 썼다는 점. 이건 스킬 크레딧 할당 문제를 태스크 단위에서 액션 단위로 내린 것이라, SkillGate(스킬 선택 토큰에 크레딧을 주는 문제)나 최근 액션 단계 크레딧 연구들과 같은 방향으로 보입니다.

인공 보상을 만들지 않고 기존 GRPO 어드밴티지의 재분배만 한다는 점. <span style="background-color: #fff59d"><strong>보상 해킹 리스크 없이 붙일 수 있는 구조</strong></span>라 실무 하네스에 적용할 여지가 있습니다.

한계도 명확합니다. 7B 단일 백본이고, 스킬 민감도 계산이 두 번의 순방향 패스를 전제로 한다는 점, SearchQA처럼 스킬 기여가 균질한 도메인에서는 이득이 미미하다는 점. 그리고 <span style="background-color: #fff59d"><strong>"교사 스킬 품질이 어느 정도여야 초반 증류가 유효한가"는 본문에서 깊게 다루지 않</strong></span>습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: [AUSO: Action-Level Unified Skill Optimization from Internalization to Utilization](https://arxiv.org/abs/2608.21292) (arXiv:2608.21292, 2026-08-21)
- 비교 대상: Skill0, Skill0.5, Skill1, SkillRL, GRPO, RLOO 등. 스킬 라이프사이클 관점의 후속 연구 흐름.
