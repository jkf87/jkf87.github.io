---
title: "GRPO에 숨어 있는 가짜 어드밴티지: 추측으로 맞힌 정답까지 강화하는 문제"
date: 2026-09-04
draft: false
description: "GRPO의 within-group 어드밴티지 추정식이 추측으로 정답을 맞힌 롤아웃에도 높은 크기를 부여한다는 논문(arXiv 2609.04063) 정리. SignBalance는 검증자 부호는 유지하고 크기를 전역 상수로 바꿔 이 문제를 제거한다."
tags:
  - GRPO
  - RLVR
  - advantage-estimation
  - agent-RL
  - benchmark
---

## 결론 먼저

GRPO는 그룹 내 보상 통계로 롤아웃별 어드밴티지 크기를 정합니다. 근데 이 공식은 "추론해서 맞힌 롤아웃"과 "찍어서 맞힌 롤아웃"을 구분하지 못합니다. 찍어서 맞은 롤아웃에도 높은 크기가 붙고, 그대로 그래디언트 가중치에 들어갑니다. 논문은 이 성분을 <span style="background-color: #fff59d"><strong>spurious advantage(가짜 어드밴티지)</strong></span>라고 부릅니다.

핵심 숫자:

| 항목 | 값 |
| --- | --- |
| 논문 | Spurious Advantage Hidden in GRPO (arXiv 2609.04063) |
| 저자/소속 | Jiamian Wang(RIT), Adobe Research |
| 문제 | 정답을 추측으로 맞힌 롤아웃도 그룹 내 정규화로 높은 어드밴티지를 받음 |
| 발생 조건 3가지 | 유한 후보 정답(객관식), 개방형 세트 내 유한 서브케이스, 검색 에이전트의 반복 경로 |
| 제안 | SignBalance: 부호 유지 + 전역 스케일 c + stop-gradient 클래스별 재스케일 |
| 0.5B 결과 | Avg-8 36.61 (GRPO 34.24, DAPO 36.27 대비 우위) |
| 검색 에이전트 | Avg-6 37.80, Search-R1 대비 +1.80 |

원문: [arXiv:2609.04063](https://arxiv.org/abs/2609.04063) / [HTML 전문](https://arxiv.org/html/2609.04063v1). 기준일 2026-09-03(v1)입니다.

## GRPO 어드밴티지 추정식의 구조적 문제

GRPO는 프롬프트마다 G개 롤아웃을 뽑고, 이진 검증자로 채점한 뒤 <span style="background-color: #fff59d"><strong>그룹 내 통계로 advantage를 만듭니다.</strong></span> 수식으로는 그룹 평균/표준편차로 정규화하거나, 이진 보상에서는 (n+, n−) 조성에 따라 결정되는 폐형 가중치가 됩니다.

논문이 짚는 지점은 이것입니다.

- 정답 롤아웃의 크기는 그룹 내 정답 수 비율의 함수입니다. 희귀할수록 큰 가중치를 받습니다.
- 근데 4지선다에서는 아무 추론 없이 찍어도 1/4 확률로 맞힙니다.
- <span style="background-color: #fff59d"><strong>찍어서 맞은 롤아웃과 추론해서 맞은 롤아웃이 정확히 같은 크기의 어드밴티지를 받습니다.</strong></span>

그래서 정책은 "운 좋은 찍기 궤적"을 강화하는 방향으로 학습 신호가 오염됩니다.

## 어디서 커지는가

논문은 spurious advantage가 커지는 조건을 세 가지로 정리합니다.

- 유한 후보 정답 태스크: 객관식(MMLU-math, SAT-Math, AQuA, AMC)처럼 정답 공간이 작으면 찍기 확률이 커집니다.
- 개방형 세트 안의 유한 서브케이스: <span style="background-color: #fff59d"><strong>MATH-7.5K의 55.95%가 짧은 수치/범주형 답을 가집니다.</strong></span> "개방형 수학 데이터셋"이라 여겨지던 말뭉치가 실제로는 작은 유한 정답 사례들의 혼합입니다.
- 검색 에이전트: 멀티턴 롤아웃은 행동 예산 내 여러 경로로 같은 정답에 도달합니다. 중복/무효 검색을 포함한 경로도 결과 보상만으로 정답 처리됩니다.

그림으로 보는 실험이 직접적입니다. 추론을 전혀 하지 않는 정책이 MATH-7.5K에서 인기 정답 문자열만 출력해도 <span style="background-color: #fff59d"><strong>"2"만 반복 출력해도 2.69%, top-10 문자열 균일 샘플링으로 20.6%</strong></span> 점수가 나옵니다.

![Figure 1: GRPO 어드밴티지 추정식 도식](/images/2026-09-04-grpo-spurious-advantage-signbalance/fig-1-p3.png)
*Figure 1 (원문 p3): GRPO의 어드밴티지 추정식은 그룹 내 조성 (n+, n−)만 본다.*

![Figure 3: 무추론 정책의 찍기 점수](/images/2026-09-04-grpo-spurious-advantage-signbalance/fig-3-p6.png)
*Figure 3 (원문 p6): 추론 없이 인기 정답 문자열만 출력하는 정책의 MATH-7.5K 점수.*

추가로, 난이도가 쉬운 문제일수록 유한 정답 비율이 높습니다(Level 1: 69.2% → Level 5: 45.9%). <span style="background-color: #fff59d"><strong>초기 정책이 가장 잘 푸는 쉬운 문제에서 가짜 어드밴티지가 가장 큽니다.</strong></span>

## SignBalance 방법: 조성 독립 크기와 힘 균형

제안은 단순합니다. advantage 크기가 (n+, n−)에 의존하지 않게 만드는 것. 논문은 세 단계로 유도합니다.

| 단계 | 식 | 효과 |
| --- | --- | --- |
| Step 1 | 정답/오답 클래스별 정규화 | 불균형 그룹 문제 완화. 근데 σ가 여전히 n에 의존 |
| Step 2 | sign(ri)·c 로 붕괴 | 조성 의존 완전 제거. 대신 배치 수준 영평균 깨짐 |
| Step 3 | A+ = c, A− = −c·sg[n+/n−] | <span style="background-color: #fff59d"><strong>롤아웃별 크기는 상수, 힘 균형은 stop-gradient로 복원</strong></span> |

최종 식에서 sg[·]는 stop-gradient입니다. 클래스별 힘의 합이 맞아떨어지도록 n+/n− 비율로 재스케일하되, 그 항은 학습 그래디언트에 영향을 주지 않습니다.

특징:

- 파라미터 없음(전역 스케일 c 제외)
- <span style="background-color: #fff59d"><strong>PPO 스타일 서로게이트 손실은 그대로</strong></span>
- 외부 모델 없음, 추론 비용 추가 없음
- GRPO 손실 안의 드롭인 교체

## 실험 결과: 벤치마크별 등락

### 0.5B 수학 (Qwen2.5-0.5B-Instruct, MATH-7.5K 학습, G=16)

| 방법 | GSM8K | MATH-500 | SAT-M | AQuA | AMC | Avg-8 |
| --- | --- | --- | --- | --- | --- | --- |
| GRPO | 49.89 | 56.60 | 65.62 | 29.53 | 6.02 | 34.24 |
| DAPO | 48.82 | 55.40 | 71.88 | 36.22 | 7.23 | 36.27 |
| SignBalance | 49.66 | 53.60 | 71.88 | 35.43 | 10.84 | 36.61 |

패턴이 분명합니다. <span style="background-color: #fff59d"><strong>객관식 계열(SAT-M, AQuA, AMC)에서 이득이 크고, MATH-500 같은 개방형에서는 소폭 내려갑니다.</strong></span> 페이스트레이드 성질의 신호가 사라진다는 직관과 정확히 일치합니다.

![Table 2: 0.5B 메인 결과](/images/2026-09-04-grpo-spurious-advantage-signbalance/table-2-p6.png)
*Table 2 (원문 p6): 8개 수학 벤치마크, 어드밴티지 구성만 통제변수.*

![Figure 2: 학습 트랙토리 전체에서 유지되는 우위](/images/2026-09-04-grpo-spurious-advantage-signbalance/fig-2-p5.png)
*Figure 2 (원문 p5): Avg-8 우위가 베스트 체크포인트에서만이 아니라 전체 트레이닝 동안 유지됨.*

### 3B 스케일 일반화 (Qwen2.5-3B-Base)

| 방법 | GSM8K | MATH-500 | AIME | AMC | Avg-8 |
| --- | --- | --- | --- | --- | --- |
| GRPO | 85.7 | 64.0 | 7.7 | 36.5 | 42.80 |
| BNPO | 86.0 | 64.4 | 8.0 | 37.0 | 43.18 |
| SignBalance | 86.4 | 64.8 | 8.5 | 38.2 | 43.78 |

![Table 3: 3B 스케일 일반화](/images/2026-09-04-grpo-spurious-advantage-signbalance/table-3-p7.png)
*Table 3 (원문 p7): 3B 스케일 8벤치마크 스위트.*

### 검색 에이전트 (Qwen2.5-7B-Instruct, Search-R1 프로토콜, B=4)

SignBalance는 6개 텍스트 QA 벤치마크 평균 Avg-6 37.80으로 최상위입니다.

- Search-R1(36.00) 대비 +1.80, StepSearch(36.44) 대비 +1.36입니다.
- 가장 큰 단일 벤치 이득은 <span style="background-color: #fff59d"><strong>2WikiMultiHopQA에서 +7.62 (35.20 vs 27.58)</strong></span>입니다.

멀티홥이 많을수록 같은 정답에 도달하는 경로가 많아지고, 그만큼 가짜 어드밴티지가 커진다는 분석과 맞습니다.

## 내 해석과 운영 시사점

원문 근거와 제 해석을 나눠서 정리했습니다.

원문이 보여주는 것:

- GRPO의 크기 공식이 태스크 구조(정답 공간 크기, 경로 수)와 무관하게 동일하게 적용된다는 구조적 문제
- MATH-7.5K 같은 표준 학습 말뭉치 안에 유한 정답 사례가 절반 이상 존재한다는 측정
- 어드밴티지 추정식 하나만 바꿔서(외부 루프 동일) 객관식/검색 에이전트에서 일관된 이득

제 해석:

- RLVR 파이프라인을 운영한다면 "정답률이 올랐다"만 보지 말고 <span style="background-color: #fff59d"><strong>정답 중 찍기로 맞힌 비율을 따로 모니터링할 가치가 있습니다.</strong></span>
  논문 부록에도 정답 롤아웃 중 랜덤 추측 비율 진단이 있습니다.
- 벤치마크 점수가 실사용 신뢰도와 어긋나는 흔한 원인 중 하나가 이런 보상 구조의 허점입니다. 객관식 평가로 학습한 에이전트를 운영 환경에 넣을 때 특히 그렇습니다.
- 개방형 수학에서의 소폭 하락(MATH-500 −3.0)은 트레이드오프입니다. 태스크 믹스에 따라 도입 여부를 판단하면 됩니다.

한계도 적어둡니다. 메인 실험이 0.5B/3B이고 검색 에이전트만 7B입니다. 프론티어 스케일에서의 재현은 아직 없습니다. 저자 소속이 Adobe Research라 코드 공개는 예정으로만 되어 있습니다.

## 더 실습해보고 싶은 분들께

RLVR/에이전트 루프를 직접 굴려보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### GRPO의 spurious advantage가 정확히 무엇인가요?
그룹 내 정규화로 계산되는 롤아웃별 어드밴티지 크기가, 추론이 아니라 추측으로 정답에 도달한 롤아웃에도 동일하게 부여되는 성분입니다. 유한 정답 태스크, 개방형 세트 내 유한 서브케이스, 검색 에이전트의 다중 경로에서 커집니다.

### SignBalance는 GRPO 코드에서 무엇을 바꾸나요?
롤아웃별 크기를 (n+, n−) 조성의 함수에서 전역 상수로 바꾸고, stop-gradient n+/n− 재스케일로 배치 수준 힘 균형만 복원합니다. 손실 함수 구조와 추론 비용은 그대로입니다.

### 실무 벤치마크에서 얼마나 오르나요?
0.5B 8벤치 평균 34.24→36.61 (GRPO 대비 +2.37), 검색 에이전트 6벤치 평균 36.00→37.80 (Search-R1 대비 +1.80)입니다. 객관식 계열에서 이득이 크고 개방형 수학 일부(MATH-500)는 소폭 하락합니다. 기준일: 2026-09-04, arXiv v1 기준.
