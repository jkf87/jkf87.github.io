---
title: "ROBORMBENCH — 같은 로봇 동작, 문장만 바꿨는데 보상 점수가 뒤집힘 (arXiv 2609.05401)"
date: 2026-09-09
draft: false
tags: [VLM, reward-model, robotics, benchmark, arxiv]
description: "VLM을 로봇 학습 보상 함수로 쓸 때 의미 동일 지시문만 바꾸면 점수가 실패/성공으로 뒤집히는 현상을 2,390개 실물 로봇 트라젝토리와 21,673개 검증 패러프레이즈로 측정한 ROBORMBENCH 논문 정리."
---

## 결론 먼저

연세대·CMU·서울대 연구진이 VLM(비전-언어 모델)을 로봇 보상 함수로 쓸 때 치명적인 문제를 잡았습니다. <span style="background-color: #fff59d"><strong>같은 로봇 동작인데 목표 설명 문장만 바꾸면 보상 점수가 크게 달라지고, 실패/성공 판정까지 뒤집힙니다.</strong></span>

이걸 측정하려고 만든 게 ROBORMBENCH입니다. <span style="background-color: #fff59d"><strong>실물 로봇 트라젝토리 2,390개, 검증된 패러프레이즈 21,673개</strong></span>로 구성된 벤치마크구요. 평가 대상은 GPT-5.1, Gemini, Claude 계열부터 Qwen3-VL, Gemma3, Llama4 같은 오픈소스까지 포함합니다.

핵심 발견 3개 정리했습니다.

- <span style="background-color: #fff59d"><strong>패러프레이즈 불안정성은 모델이 커져도 사라지지 않고 오히려 커질 수 있다</strong></span>
- <span style="background-color: #fff59d"><strong>reasoning을 켜면 안정성이 개선되는 경우보다 SCR이 상승하는 경우가 있다</strong></span>
- <span style="background-color: #fff59d"><strong>전용 보상 모델(RR-4B/RR-8B)이 더 큰 범용 VLM보다 훨씬 안정적이다. 트라젝토리 그라운디드 보상 감독이 핵심</strong></span>

기준일: 2026-09-04 arXiv v1 기준입니다.

## 벤치마크 구성

| 항목 | 값 |
|---|---|
| 트라젝토리 | 2,390개 (실물 로봇, GT 진행도 라벨 포함) |
| 검증 패러프레이즈 | 21,673개 |
| 패러프레이즈 전략 | 어휘 치환(LS) / 통사 재구성(SR) / 행동-목표 관점 전환(AGPS) |
| 평가 모델 | GPT-4o, GPT-5.1, Gemini2.5/3-flash, Claude-haiku/sonnet, Qwen3-VL, Gemma3, Llama4, RR-4B/8B |
| 메트릭 | SCR(점수 교차율), FR(판정 뒤집음율), ME(평균 오차) |

의미가 달라지는 재작성은 앙상블 3개 모델(gemini-3-flash, claude-sonnet-4-6, deepseek-v3.2)로 걸러냈고, 사람 주석과의 필터 합치도도 검증했습니다. "slowly" 같은 미묘한 수식어 추가도 의미 차이로 보고 제거하는 보수적 기준이에요.

## 어떤 현상인가

![Figure 1](/images/2026-09-09-robormbench-paraphrase-fragility-vlm-reward/fig-1-p1.png)
*Figure 1: 동일 트라젝토리에 "Pick radish, then place in pink bowl"과 "After picking radish, place in pink bowl"을 넣었더니 보상 점수가 1 vs 5로 갈림. 출처: 논문 Figure 1.*

Figure 1이 논문의 핵심 그림입니다. 무("radish")를 줍고 분홍 그릇에 놓는 과제에서 동작 시퀀스는 완전히 동일합니다. 그런데 "줍고 나서 놓아라"와 "준 다음 놓아라"라는 표현 차이만으로 한쪽은 1점(실패), 다른쪽은 5점(성공)이 나옵니다.

RL 관점에서 이건 학습 신호 자체의 오염이에요. <span style="background-color: #fff59d"><strong>같은 행동에 충돌하는 보상이 들어오면 정책은 과제 목표 대신 문장 표면 쪽으로 최적화됩니다.</strong></span>

## 주요 결과 수치

![Table 2](/images/2026-09-09-robormbench-paraphrase-fragility-vlm-reward/table-2-p6.png)
*Table 2: 세 가지 패러프레이즈 전략에서 모델별 SCR/FR/ME. 낮을수록 좋음. 출처: 논문 Table 2.*

숫자로 보면 이렇습니다.

| 모델 | SCR (LS) | SCR (AGPS) | 비고 |
|---|---|---|---|
| RR-4B | 0.034 | 0.086 | 전용 보상 모델, 최강 |
| Claude-sonnet-4.6 | 0.051 | 0.164 | 범용 VLM 중 최선 (LS) |
| GPT-5.1 | 0.153 | 0.300 | 재작성이 멀수록 악화 |
| Gemini2.5-flash-lite | 0.483 | 0.607 | 절반 이상에서 판정 교차 |
| Llama4-scout | 0.483 | 0.557 | 마찬가지로 절반 이상 |

읽히는 포인트 2개구요.

- <span style="background-color: #fff59d"><strong>Gemini2.5-flash-lite와 Llama4-scout는 AGPS에서 전체 트라젝토리의 절반 이상에서 같은 동작을 실패와 성공 양쪽에 걸쳐 점수매김</strong></span>
- GPT-5.1의 SCR은 어휘 치환 0.153, 통사 재구성 0.204, 관점 전환 0.300. <span style="background-color: #fff59d"><strong>문장이 원문에서 멀어질수록 불안정성이 커집니다.</strong></span>

## 모델 크기와 reasoning 효과

![Figure 3](/images/2026-09-09-robormbench-paraphrase-fragility-vlm-reward/fig-3-p7.png)
*Figure 3: 모델 크기별 SCR. Qwen3-VL과 Gemma3 모두 커질수록 SCR이 상승. 출처: 논문 Figure 3.*

여기가 이 논문에서 제일 흥미로운 대목이에요.

Qwen3-VL(2B→32B)과 Gemma3(4B→27B) 패밀리 내부에서 크기를 키우면 SCR이 내려가지 않고 <span style="background-color: #fff59d"><strong>올라갑니다</strong></span>. 규모 확대만으로는 패러프레이즈 강인성이 확보되지 않고, 문장 표면 민감도가 증폭될 수 있다는 뜻이에요.

reasoning도 비슷합니다.

![Figure 4](/images/2026-09-09-robormbench-paraphrase-fragility-vlm-reward/fig-4-p7.png)
*Figure 4: Qwen3-vl-235B와 Gemini3-flash의 instruct vs. reasoning 비교. reasoning을 켜면 SCR 상승. 출처: 논문 Figure 4.*

Qwen3-vl-235B와 Gemini3-flash 둘 다 reasoning을 켜면 SCR이 올라갑니다. ME는 비슷하니까 평균 정확도는 그대로인데 안정성만 나빠진 거예요. GPT-5.1에서는 개선, Claude-sonnet-4.6에서는 악화라 <span style="background-color: #fff59d"><strong>모델 간 일관된 효과도 없습니다.</strong></span>

## 전용 보상 모델이 앞서는 지점

RR-4B와 RR-8B는 대부분의 범용 VLM보다 작은 모델인데 SCR이 한 자릿수~0.1대 초반 수준으로 낮습니다. ME도 전 구간 최저구요. 저자들의 해석은 이렇습니다. <span style="background-color: #fff59d"><strong>범용 VLM은 지시문의 텍스트 신호에 더 기대는 경향이 있고, 트라젝토리에 직접 그라운딩된 보상 감독을 받은 모델은 그 영향이 작다.</strong></span>

<span style="background-color: #fff59d"><strong>보상 모델링용 데이터로 학습했는지 여부가 승부를 가른다</strong></span>는 결론이에요.

## Best-of-N 트라젝토리 선택 결과

트라젝토리 20개 중 보상 최고인 걸 고르는 offline best-of-N 실험(Table 5)에서 ME가 비슷한 모델끼리 비교하면 이렇습니다.

| 선택자 | ME↓ | SCR↓ | 선택된 GT↑ | Regret↓ |
|---|---|---|---|---|
| Random | – | – | 3.158 | 1.398 |
| Gemini2.5-Flash-Lite | 0.970 | 0.607 | 3.222 | 1.333 |
| GPT-5.1 | 1.015 | 0.300 | 3.737 | 0.818 |
| Claude-Sonnet-4.6 | 0.970 | 0.164 | 3.980 | 0.576 |
| Oracle | – | – | 4.556 | 0.000 |

ME가 거의 같은 두 모델(Gemini2.5-Flash-Lite vs Claude-Sonnet-4.6)의 성적 차이가 큽니다. <span style="background-color: #fff59d"><strong>평균 예측 오차가 비슷해도 SCR이 낮은 모델이 더 좋은 트라젝토리를 고르고 regret이 절반 이하</strong></span>입니다. 11개 모델에서 SCR-Regret 상관은 Pearson r=0.882.

Pairwise 선호 판정(Table 6)에서도 같은 순서고, RR-8B가 정확도 0.855로 최상위구요.

패러프레이즈 앙상블로 점수를 평균 내는 방법(Figure 6)도 SCR과 예측 오차를 일관되게 낮춥니다. 예산이 있으면 현장에서 바로 쓸 수 있는 완화책이에요.

## 원문 근거

- arXiv: [2609.05401](https://arxiv.org/abs/2609.05401) (Same Trajectory, Contradictory Rewards (ROBORMBENCH): Paraphrase Fragility in Vision Language Reward Models, 2026-09-04, v1)
- 저자: Wonje Jeung 외, 연세대학교 / Carnegie Mellon University / Seoul National University
- 위 수치는 모두 논문 v1의 Table 2, 3, 5, 6과 Figure 3, 4, 6 기준. 내 해석이 섞인 곳은 "Best-of-N 트라젝토리 선택 결과" 섹션의 서술입니다.

## 자주 묻는 질문

### SCR 점수 교차율의 뜻과 계산 방법
같은 트라젝토리에 대해 의미 동일 지시문들 중 실패 수준 점수와 성공 수준 점수가 둘 다 나온 비율입니다. 0.5면 절반의 트라젝토리에서 판정이 문장에 따라 갈린다는 뜻이에요.

### 패러프레이즈 불변성이 중요한 이유
VLM 보상 함수는 RL에서 어떤 행동을 강화할지 결정합니다. 동일 행동에 충돌 보상이 나오면 학습 신호가 오염되고, 정책이 과제 대신 표현에 맞춰 최적화될 수 있기 때문입니다.

### 큰 VLM을 쓰면 되는지 여부와 한계
논문 Figure 3에서 Qwen3-VL·Gemma3 패밀리 모두 크기가 커질수록 SCR이 상승했습니다. 전용 보상 모델(RR-4B/8B)처럼 트라젝토리 그라운디드 보상 감독을 받은 쪽이 유리합니다.

### reasoning 모드의 효과와 한계
Qwen3-vl-235B와 Gemini3-flash에서는 SCR이 오히려 올라갔고, 모델별로 방향이 갈렸습니다. reasoning은 이 문제의 신뢰할 만한 해법이 못 됩니다.

### 현장에서 바로 쓸 수 있는 완화 방법
논문이 제시하는 건 두 가지: 의미 동일 지시문 여러 개에 대한 점수 앙상블(평균)과 전용 보상 모델 사용. 앙상블은 SCR과 예측 오차를 모두 낮췄습니다.

## 정리

VLM 보상 모델은 과제를 이해하는 능력과 문장 표면에 과적합하는 경향 사이 어딘가에 있었습니다. 이 논문은 그 경계를 검증된 문장 21,673개로 측정한 첫 체계적 시도구요. 로봇 RL에 VLM 보상을 쓰는 팀이라면 <span style="background-color: #fff59d"><strong>스케일업이나 reasoning 대신 패러프레이즈 안정성(SCR)을 보상 모델 선정 기준에 넣어야 한다</strong></span>는 게 실무적 결론입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
