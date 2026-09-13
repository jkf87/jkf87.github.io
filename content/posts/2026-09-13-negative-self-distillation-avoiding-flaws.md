---
title: "NSD: 잘못된 추론을 피하도록 학습시키는 네거티브 자기증류 (arXiv 2609.11699)"
date: 2026-09-13
tags: [llm, rl, self-distillation, reasoning]
draft: false
description: "온폴리시 자기증류(OPSD)가 정답을 알고 하는 가르침이라 추론을 망친다는 진단에서 출발해, 모델 스스로 만든 결함 추론을 피하게 학습시키는 네거티브 자기증류(NSD)를 정리했습니다."
---

## 결론 먼저

정답을 보여주며 가르치는 자기증류 대신, <span style="background-color: #fff59d"><strong>모델 스스로 '부정확한 추론자' 역할을 시켜 그 분포를 피하도록 학습</strong></span>시키는 방법이 7개 수학 벤치마크에서 일관되게 더 좋았다는 논문입니다. Qwen3 1.7B/4B/8B에서 <span style="background-color: #fff59d"><strong>평균 +2.3% / +7.5% / +6.0%</strong></span> 개선을 냈고, 라벨도 외부 교사 모델도 필요 없습니다.

핵심 구조를 표로 정리하면 이렇습니다.

| 항목 | 내용 |
| --- | --- |
| 논문 | Negative Self-Distillation: Learning to Reason by Avoiding Flaws (arXiv 2609.11699) |
| 문제 | OPSD가 인위적으로 자신만찬 추론을 흉내 내게 해 탐색·자기교정 행동을 억제 |
| 방법 | 자기 생성 네거티브 컨디션으로 결함 추론 분포를 만들고 그것에서 멀어지게 학습 |
| 핵심 장치 | 토큰 단위 게이팅 + 시그모이드로 bounded한 unlikelihood 페널티 + KL 정규화 |
| 결과 | AIME 24/25/26, HMMT, AMC, OlympiadBench, MATH-500에서 OPSD·Intuitor·TTRL 상회 |
| 비용 | 샘플당 롤아웃 1회, GRPO류(n=8) 대비 롤아웃 시간 약 60% 절감 |

기준일: 2026-09-13 기준, 논문 v1 초록·본문 수치입니다.

## 배경: 정답을 아는 교사의 부작용

RLVR은 롤아웃 비용과 희소한 보상 신호가 병목입니다. 이를 우회하려고 등장한 게 온폴리시 증류(OPD)인데, 강한 외부 교사가 필요하다는 제약이 있습니다. 외부 교사 없이 모델 자신이 교사가 되는 게 온폴리시 자기증류(OPSD)입니다.

OPSD는 학생이 정답 같은 특권 정보를 받아 추론 궤적을 만듭니다. 이 교사는 정답을 이미 알고 있어서 <span style="background-color: #fff59d"><strong>인위적으로 자신이 넘치고 직선적인 추론만 만들어냅니다</strong></span>. 이걸 흉내 내는 학생은 불확실성 표현, 되돌아보기, 자기교정 같은 행동을 잃게 됩니다. 어려운 문제일수록 치명적입니다.

논문의 실험에서 이 부작용이 수치로 드러납니다. Qwen3-4B에서 응답당 반성 토큰("wait", "actually" 등) 빈도가 베이스라인 3.6에서 OPSD는 2.2, Intuitor는 0.8로 떨어집니다.

![](/images/2026-09-13-negative-self-distillation-avoiding-flaws/figure1-framework.png)

Figure 1. 같은 베이스 모델에서 네거티브 컨디션으로 부정 교사를 만들고, 학생 분포를 그 교사에서 멀어지게 최적화하는 전체 구조.

## 방법: 피할 대상을 직접 만든다

NSD(Negative Self-Distillation)는 방향을 반대로 잡습니다. 학습 방향을 결함 쪽으로 잡습니다. <span style="background-color: #fff59d"><strong>결함 있는 추론 패턴에서 분포가 멀어지도록</strong></span> 최적화합니다.

동작 순서는 이렇습니다.

1. 라벨 없는 문제 x가 주어집니다.
2. 학생 모델이 초기 풀이 y_init를 샘플링합니다.
3. 문제와 초기 풀이를 보고 모델이 문제 특화 네거티브 컨디션 n을 생성합니다(예: "부주의한 추론자처럼 풀어라").
4. 같은 가중치의 모델을 일반 컨디션(π_ref)과 네거티브 컨디션(π_neg)으로 각각 돌립니다.
5. 두 분포를 비교해 네거티브 컨디션이 확률을 올린 토큰만 골라 페널티를 줍니다.

### 토큰 게이팅: 언어 능력을 지키는 필터

여기서 난관이 하나 있습니다. 결함 토큰과 일반 언어 토큰이 섞여 있어서 무차별적으로 언러닝하면 기초 언어 능력이 무너집니다.

NSD는 게이트 G_t = max(0, π_neg − π_ref)로 이걸 해결합니다. 네거티브 프롬프트 때문에 확률이 올라간 토큰만 페널티 대상이 되고, 차이가 클수록 페널티도 커집니다. 문법 토큰은 exempt라서 원래 분포가 유지됩니다.

![](/images/2026-09-13-negative-self-distillation-avoiding-flaws/figure2-method.png)

Figure 2. 토큰 분포 비교로 결함 민감 토큰을 분리하고, 걸러진 정상 토큰은 KL로만 정규화하는 과정.

### bounded unlikelihood: 그래디언트 폭발 막기

두 번째 난관은 unlikelihood 손실이 무경계라는 점입니다. 확률이 1에 가까운 토큰에 −log(1−π)를 그대로 먹이면 손실이 발산합니다.

NSD는 시그모이드로 눌러서 <span style="background-color: #fff59d"><strong>L_GU = G_t · 1/(2−π_θ)</strong></span> 형태로 bounded합니다. 구두점 같은 고확률 토큰의 페널티를 낮추고, 저~중확률 토큰에 학습 신호를 재분배합니다.

![](/images/2026-09-13-negative-self-distillation-avoiding-flaws/figure3-gated-unlikelihood.png)

Figure 3. 시그모이드 적용 전후 그래디언트 함수와 실제 4,096 토큰에 대한 손실 분포.

덧붙이면 단일 토큰에 대한 reference-가중 KL 앵커를 더해 전체 언어 사전 지식이 흔들리지 않게 잡아줍니다. 전 어휘 KL을 계산하지 않아 롤아웃 중 비용도 적습니다.

## 결과: 반성 행동을 되살린다

Table 1 요약입니다(Avg@8, non-thinking, 2 에폭 내 최적 체크포인트).

| 모델 | OPSD | Intuitor | TTRL | NSD |
| --- | --- | --- | --- | --- |
| Qwen3-1.7B Δ Avg | +1.1 | −0.5 | +0.3 | <span style="background-color: #fff59d"><strong>+2.3</strong></span> |
| Qwen3-4B Δ Avg | +1.0 | +1.3 | +0.2 | <span style="background-color: #fff59d"><strong>+7.5</strong></span> |
| Qwen3-8B Δ Avg | +0.3 | +1.9 | −0.1 | <span style="background-color: #fff59d"><strong>+6.0</strong></span> |

눈에 띄는 지점 몇 개만 짚습니다.

- 4B에서 AIME 2024 정확도가 베이스 23.8%에서 35.8%로, 8B에서 28.8%에서 <span style="background-color: #fff59d"><strong>39.6%까지 오릅니다</strong></span>.
- 다른 베이스라인 개선은 일부 우연일 수 있지만 NSD의 p-값은 최대 0.001, 4B/8B는 <10⁻⁴로 <span style="background-color: #fff59d"><strong>통계적으로 안정된 향상</strong></span>입니다.
- 클수록 이득이 커집니다. 네거티브 컨디션을 모델 자신이 생성하는 구조라서, 큰 모델일수록 대비 신호의 질이 좋기 때문으로 논문은 설명합니다.
- Intuitor가 1.7B에서 −0.5%인 것과 대비됩니다. 자신감 기반 부트스트랩은 약한 모델에서 신호 자체가 틀릴 수 있습니다.

반성 토큰 빈도(Table 2, Qwen3-4B)도 방향이 확실히 다릅니다.

| 방법 | AIME 2024 | AIME 2025 | HMMT 2025 | 평균 |
| --- | --- | --- | --- | --- |
| Baseline | 6.8 | 2.2 | 1.7 | 3.6 |
| OPSD | 2.6 | 2.1 | 1.8 | 2.2 |
| Intuitor | 0.6 | 1.0 | 0.7 | 0.8 |
| NSD | 6.9 | 7.5 | 8.1 | <span style="background-color: #fff59d"><strong>7.5</strong></span> |

<span style="background-color: #fff59d"><strong>NSD는 반성 빈도를 베이스라인보다도 높게 유지·증가</strong></span>시킵니다. 결함 경로를 피하도록만 학습했을 뿐인데 자기검증 행동이 살아난 게 이 논문의 가장 흥미로운 관찰입니다.

## 비용 구조

GRPO류(Intuitor, TTRL)는 프롬프트당 8개 샘플이 필요한 데 비해 NSD와 OPSD는 1개면 됩니다. <span style="background-color: #fff59d"><strong>롤아웃 시간 약 60% 절감</strong></span>이고, 오프라인 정적 컨디션(wiki-irr)을 쓰면 전체 지연이 68초에서 54초로 줄어듭니다. 흥미롭게도 무관 위키 문서를 넣는 단순 노이즈 전략으로도 비슷한 효과가 나옵니다.

![](/images/2026-09-13-negative-self-distillation-avoiding-flaws/figure4-punct-distribution.png)

## 내 해석과 한계

여기부터는 논문 내용이 아니라 내 판단입니다.

좋은 점부터. "무엇을 피할지"는 "무엇을 흉내 낼지"보다 정의가 쉬운 경우가 많습니다.

NSD는 그 비대칭을 학습 신호로 바꾼 설계라 개념적으로 깔끔합니다. 게이팅으로 언어 능력을 보존하는 것도 실용적인 선택입니다.

한계도 있습니다.

- 평가가 수학 추론에 집중돼 있습니다. 코드, 에이전트 과제에서 네거티브 컨디션 품질이 유지될지는 열린 질문입니다.
- "부주의한 추론자" 프롬프트가 특정 언어·도메인에 편향될 수 있습니다.
- 네거티브 컨디션 생성 자체가 롤아웃 비용을 만듭니다. 오프라인 전략으로 상쇄는 되지만 완전히 공짜는 아닙니다.

관련 링크:

- 논문: <https://arxiv.org/abs/2609.11699>
- HTML 버전: <https://arxiv.org/html/2609.11699v1>

## 더 실습해보고 싶은 분들께

에이전트·루프 학습 파이프라인에 관심 있다면 아래 두 개를 먼저 보시길 권합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Q. NSD는 정답 라벨이 꼭 필요한가요?**
아니요. 문제 문장만 있고 정답·외부 교사 없이 자기 생성 네거티브 컨디션으로 학습합니다.

**Q. OPSD와 결과 차이의 원인은 뭔가요?**
OPSD 교사가 정답을 알아서 과하게 직선적인 추론을 만들고, 이를 흉내 낸 학생이 자기교정·탐색 행동을 잃기 때문입니다.

**Q. 반성 행동은 어떻게 측정했나요?**
응답당 "wait", "actually" 같은 반성 토큰의 평균 빈도로 측정했고, NSD에서 7.5로 가장 높았습니다.

**Q. 계산 비용은 어떻게 되나요?**
샘플당 롤아웃 1회면 충분해 GRPO류 대비 롤아웃 시간 약 60%를 줄일 수 있습니다.
