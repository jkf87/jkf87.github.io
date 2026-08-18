---
title: "TRCA: 실패 트랙토리의 72%는 버릴 게 아니다"
date: 2026-08-19
tags:
  - reinforcement-learning
  - LLM-agent
  - credit-assignment
  - rubric-reward
  - GRPO
  - long-horizon
  - agent-training
---

긴 호라이즌 LLM 에이전트 학습에서 실패한 롤아웃은 대부분 버려집니다. 근데 이 논문은 그 버린 실패 안에 이미 학습 신호가 들어 있다는 걸 보이고, 그걸 루브릭 기반 전환 단위 보상으로 꺼내는 방법을 제안합니다.

논문: TRCA: Transition-wise Rubric Credit Assignment for Long-horizon LLM Agents (arXiv 2608.16156, 2026-08-17)

## 결론 먼저

GRPO 계열은 성공/실패라는 터미널 아웃컴만으로 트랙토리 전체에 크레딧을 나눕니다. 그래서 성공 트랙토리가 거의 없는 학습 초기에는 스텝 단위 판별이 사실상 불가능합니다.

TRCA의 출발점은 진단 결과입니다. Qwen2.5-1.5B-Instruct 롤아웃을 뽑아 보니 96.5%가 터미널 성공에 실패했고, 태스크 조건별 트레이닝 그룹의 <span style="background-color: #fff59d"><strong>85.6%에는 성공 트랙토리가 하나도 없었습니다</strong></span>.

근데 같은 데이터를 사람 어노테이션 + 프론티어 LLM 판정으로 다시 보니, 실패한 롤아웃의 액션 <span style="background-color: #fff59d"><strong>72.2%는 여전히 진단적으로 유용한 전환 신호</strong></span>를 갖고 있었습니다. 성공 앵커가 없어도 스텝 크레딧을 만들 수 있다는 근거가 이겁니다.

![](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-motivation.png)

## 기존 접근의 비용 구조

스텝 단위 크레딧을 만드는 기존 방법은 두 갈래입니다.

- 프로세스 리워드 모델(PRM): 중간 스텝마다 평가기를 돌립니다. 어노테이션 비용 + 롤아웃마다 추가 추론 비용이 붙습니다.
- 성공 앵커 기반: 성공 트랙토리의 구조에서 스텝 크레딧을 역으로 전파합니다(GiGPO, HCAPO 등). 성공 트랙토리가 확보될 때만 작동합니다.

TRCA는 둘 다 안 씁니다. <span style="background-color: #fff59d"><strong>학습된 평가기도 없고, 성공 앵커도 없습니다</strong></span>. 액션이 일으킨 상태 전환 자체를 규칙 기반 루브릭으로 평가합니다.

## 핵심 설계: 세 개의 루브릭과 두 개의 보상

TRCA는 모든 전환을 세 루브릭으로 판정합니다.

| 루브릭 | 판정 대상 |
| --- | --- |
| Evidence | 환경에서 태스크 관련 정보를 새로 획득했는가 |
| Execution | 환경을 유의미하게 바꾸는 유효한 액션인가 |
| Invalidity | 무효, 중복, 퇴행 행동인가 |

![](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-overview.png)

같은 판정에서 두 개의 보상을 만듭니다.

- Foundational Rubric Reward: 세 카테고리의 부호 있는 점수를 합산한 로컬 전환 품질. "이 스텝 자체는 제대로 했는가"를 봅니다.
- Breakthrough Rubric Reward: 지금까지 커버되지 않았던 Evidence/Execution 조건을 새로 충족했는지 추적. "태스크 진전을 새로 만들었는가"를 봅니다.

두 보상은 하이퍼파라미터 λ로 섞습니다. 퓨전 식은 `(1-λ)·rF + λ·rB`.

여기에 터미널 아웃컴까지 합쳐서 completion-aware return을 만들고, 유사한 결정 컨텍스트끼리 묶은 스텝 레벨 그룹 안에서 정규화해 스텝 상대 어드밴티지를 계산합니다. 그룹핑은 텍스트 정합이 아니라 페이지 타입, 상품 식별, 태스크 술어 같은 환경별 구조 정보로 합니다.

## 결과: 숫자로

벤치마크는 ALFWorld, WebShop, 검색 증강 QA 7종입니다.

ALFWorld (Qwen2.5-7B-Instruct):

| 방법 | 평균 성공률 |
| --- | --- |
| GRPO | 83.3 |
| GiGPO | 90.8 |
| GraphGPO | 93.3 |
| <span style="background-color: #fff59d"><strong>TRCA</strong></span> | <span style="background-color: #fff59d"><strong>94.5</strong></span> |

- WebShop (7B): <span style="background-color: #fff59d"><strong>TRCA 83.8 vs 최강 baseline GraphGPO 80.3</strong></span>. 논문 표현으로 경쟁 baseline 대비 6.0–12.6% 향상.
- SearchQA 평균 (3B): TRCA 45.4%. <span style="background-color: #fff59d"><strong>IGPO 대비 +8.2%, GiGPO 대비 +3.3%</strong></span>. 7개 개별 데이터셋 전부 1위.
- WebShop 서브태스크 Cool (7B): TRCA 100.0 (표준편차 0.0).

![](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-results.png)

샘플 효율도 잡습니다. Pick_two에서 트랙토리 <span style="background-color: #fff59d"><strong>1.92K만 뽑은 시점에 성공률이 11.5% → 34.6%</strong></span>로 오릅니다. 3.84K로 <span style="background-color: #fff59d"><strong>69.2%에 도달하는데, GRPO는 6.40K를 써도 46.7%</strong></span>입니다.

![](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-learning-curves.png)

## 내 해석: 어디서 먹히고 어디서 안 먹히나

루브릭이 코드로 강제된다는 게 이 방법의 실무적 강점입니다. <span style="background-color: #fff59d"><strong>롤아웃마다 PRM을 돌리는 추론 비용도 없고, 성공을 기다릴 필요도 없습니다</strong></span>. Appendix A에 벤치마크별 관측 가능 신호와 연산자 라이브러리가 공개되어 있어서, 자기 환경에 맞춰 루브릭을 다시 바인딩하면 되는 구조입니다.

근데 이식 조건이 분명합니다. Evidence/Execution 판정이 "환경에서 관측 가능한 상태 변화"에 의존하기 때문에, <span style="background-color: #fff59d"><strong>상태 노출이 빈약한 환경에서는 루브릭 신호 자체를 정의하기 어렵습니다</strong></span>. WebShop처럼 페이지/상품/옵션이 구조화된 환경이라 성능이 잘 나온 측면이 있습니다.

애블레이션에서 Breakthrough 보상을 빼면 <span style="background-color: #fff59d"><strong>세 벤치마크 전부 더 크게 하락</strong></span>합니다. 즉 이 시스템의 실질 엔진은 "새로 커버된 조건" 추적이고, Foundational은 넓은 바탕입니다.

λ 민감도도 짚습니다. λ=0.8에서 평균 92.0%인데 <span style="background-color: #fff59d"><strong>λ=1.0(Foundational 제거)에서 88.3%로 떨어집니다</strong></span>. 돌파 크레딧만 남기면 로컬 품질 신호를 잃어서 전체가 흔들립니다. 두 보상이 실제로 상호보완이라는 근거입니다.

![](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-lambda-heatmap.png)

## 같이 읽으면 좋은 흐름

성공 앵커 의존이 이 논문이 지적한 병목이고, 같은 지점을 다른 각도에서 공략하는 흐름이 이미 있습니다. 앵커 기반의 GiGPO/HCAPO와, 앵커 없이 검증기로 크레딧을 묶는 Verifier-Bounded Credit Assignment(arXiv 2608.13179)를 나란히 놓고 보면, "성공이 희소한 초기 학습에서 크레딧을 어디서 끌어오는가"라는 질문의 2026년 답이 정리됩니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

원문: [TRCA: Transition-wise Rubric Credit Assignment for Long-horizon LLM Agents](https://arxiv.org/abs/2608.16156)
