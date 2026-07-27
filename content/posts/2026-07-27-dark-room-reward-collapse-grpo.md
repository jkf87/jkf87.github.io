---
title: "GRPO의 어두운 방: 밀집 예측 보상이 에이전트를 붕괴시키는 정확한 기전"
date: 2026-07-27T19:05:00+09:00
draft: false
tags:
  - GRPO
  - RLVR
  - reward-design
  - agent
  - reinforcement-learning
  - LLM
  - reward-collapse
  - dark-room
  - shaping
  - auxiliary-loss
categories:
  - AI연구
  - 에이전트
summary: "GRPO에서 potential-based prediction reward가 에이전트를 '다크 룸'으로 몰아넣는 정확한 수학적 기전, 단일 인자 제거로 0%가 51.6%가 되는 실험, 그리고 보상 채널 vs 보조 손실 채널의 20점 차이를 분석한다."
---

## TL;DR

GRPO(Group Relative Policy Optimization)로 훈련한 LLM 에이전트에 "다음 관측을 예측하라"는 밀집 보상을 넣으면, 보상이 아무리 작아도 에이전트가 **예측 가능한 구석에 처박혀서 task를 포기하는 붕괴**가 발생한다. 이 논문은 그 원인이 GRPO의 표준편차 정규화에 있음을 단일 인자 실험으로 증명하고, 보상 채널 대신 **보조 손실(auxiliary loss) 채널**로 동일한 신호를 전달하면 +20점을 얻는다는 것을 보여준다.

---

## 1. 문제: 밀집 보상이 정책을 파괴한다

긴 호라이즌 LLM 에이전트를 희소 성공 보상만으로 훈련하면 학습이 느리다. 자연스러운 해결책은 **단계별 밀집 보상**을 넣는 것이다 — 에이전트에게 매 스텝 다음 관측을 예측하게 하고, 맞추면 보상을 준다.

이 논문은 이 처방이 GRPO 하에서 **역효과**를 낳는다는 것을 보여준다. Qwen3-1.7B/4B/8B를 ALFWorld에서 훈련시킨 결과, potential-based prediction reward를 넣은 모든 실행이 **다크 룸(dark room)** 상태로 빠진다:

- 예측 정확도 → 1.0 (완벽하게 예측)
- 태스크 성공률 → 0%
- 에피소드 길이 → 항상 호라이즌 상한에 고정

즉, 에이전트가 태스크를 수행하는 대신 **가장 예측하기 쉬운 상태**를 찾아 그곳에 머무는 것이다.

![Figure 1: 세 스케일에서 prediction reward가 모든 실행을 붕괴시킨다](/images/2026-07-27-dark-room-reward-collapse-grpo/fig-1-p4.png)

> Figure 1: 1.7B/4B/8B 세 스케일 모두에서 std-normalized prediction reward를 넣으면 허니문 피크 직후 붕괴가 온다. 스케일이 클수록 허니문 피크가 높아진다 — 신호가 실제로 도움이 되다가 해킹 압력이 도달하면 무너진다.

이것은 active inference 문헌에서 오래된 철학적 난제였던 "다크 룸 문제"를 **GRPO 최적화기가 자동으로 만들어내는** 구체적 엔지니어링 결과다.

## 2. 핵심 통찰: 표준편차 정규화가 범인이다

### 2.1 증상

GRPO의 정규화는 그룹 내 반환값을 평균과 표준편차로 나눈다:

$$\hat{A}_i = \frac{R_i - \bar{R}}{\sigma_R + \epsilon}$$

희소 성공 환경에서는 **모든 궤적이 실패하는 그룹(all-fail group)**이 매우 흔하다. 이런 그룹에서 태스크 반환값은 모두 동일(상수 C)하고, 그룹 내 유일한 분산 원천은 ε-스케일의 shaping 보상항 뿐이다.

### 2.2 Proposition 1: λ-불변성

모든 궤적이 실패한 그룹에서, shaping 보상의 계수 λ를 어떻게 줄이든 정규화된 어드밴티지는 **변하지 않는다**:

$$\hat{A}_i = \frac{\lambda(s_i - \bar{s})}{\lambda \sigma_s + \epsilon} \xrightarrow{\lambda \sigma_s \gg \epsilon} \frac{s_i - \bar{s}}{\sigma_s}$$

이것은 λ에 **독립적**이다. 즉, bounded 보상(리턴 수준에서 |Σr| ≤ λ로 유한)이 그룹 정규화를 거치면서 **unbounded 압력**으로 변한다. λ를 줄여도(0.068까지 annealing) 소용이 없다 — λσ_s가 ε(=10⁻⁶)보다 훨씬 큰 영역에서는 언제나 그렇다.

이것이 이 논문의 핵심 수학적 기여다. Ng et al. (1999)의 고전적 shaping 불변성은 potential이 정책에 독립적일 때 성립하지만, 여기서는 potential이 정책 의존적이다 — 그리고 GRPO의 그룹 정규화가 이 차이를 치명적으로 만든다.

![Figure 2: 단일 인자 구조](/images/2026-07-27-dark-room-reward-collapse-grpo/fig-2-p7.png)

> Figure 2: 붕괴된 실행과 구조된 실행의 **유일한 차이**는 `norm_adv_by_std_in_grpo` 플래그다. Annealing은 구조하지 못한다. 신호가 없는 컨트롤이 구조된 실행과 동일하다 — prediction reward의 순 기여도는 약 0이다.

### 2.3 단일 인자 구조

결정적인 실험: 표준편차 정규화 플래그 **하나만** 끄면 (mean-only normalization), 동일한 보상이 0%에서 51.6%로 바뀐다. 그리고 신호가 없는 베이스라인(52.6%)과 통계적으로 구분되지 않는다 — 즉 prediction reward의 순 기여도는 0에 가깝고, **구조는 normalizer가 제공**한다.

## 3. 왜 Annealing이 실패하는가

λ-invariance가 말하듯, λσ_s ≫ ε 영역에서는 λ를 줄여도 어드밴티지가 변하지 않는다. λ가 충분히 작아져서 λσ_s ~ ε가 되면 바닥(ε)이 다시 활성화되지만, 그 지점에서 보상은 사실상 0이다.

이것은 실무자에게 중요한 교훈이다: **보상 크기를 줄이는 것으로는 GRPO의 shaping 붕괴를 막을 수 없다.** 논문의 용량-반응 곡선은 ±0.01은 무해, ±0.07은 만성 드래그, full-scale은 치명적임을 보여준다.

## 4. 분산 프로파일 기준(Variance-Profile Criterion)

논문의 중심 통찰을 일반화하면:

> GRPO의 z-scoring이 증폭시키는 것은 밀집 신호의 **숙달 시(within-group) 분산**이다. 따라서 숙달(mastery)에 따라 분산이 사라지는 신호는 구조적으로 "증폭기 안전(amplifier-safe)"하다.

이 기준은:
- 이 논문의 붕괴들을 **회고적으로 설명** (prediction accuracy는 mastery에서 분산이 0이 되지만, 그 전에 분산이 너무 크다)
- 아직 실행하지 않은 arm에 대해 **사전 등록된 예측**을 가짐 (SHA256 해시로 공개)
- 기존 reward-channel 성공 사례들과 **양립** (RWML, VAGEN 등)

## 5. 커버리지 × 역학 × 용량: 3축 실패 지도

HiddenRule-Gym(HRG)이라는 합성 POMDP에서 정확히 계산 가능한 feature coverage를 사용해, ALFWorld가 혼재시키는 실패 원인을 분리한다.

![Figure 4: 커버리지 스윕](/images/2026-07-27-dark-room-reward-collapse-grpo/fig-4-p9.png)

> Figure 4: 커버리지를 두 배(0.233 → 0.483) 올리면 성공률이 3배 이상 증가한다. 흥미롭게도 1.7B에 커버리지 있는 신호(24.0%)가 4B 순수 GRPO(26.6%)에 근접한다 — 커버리지 있는 지도가 파라미터 용량을 부분적으로 대체한다.

실패 매트릭스:
- **낮은 커버리지** = 잘못된 믿음 (예측은 정확하지만 태스크와 무관)
- **충분한 커버리지 + 나쁜 역학** = 붕괴 (ALFWorld + std normalization)
- **충분한 커버리지 + 깨끗한 역학 + 부족한 용량** = 바닥 (1.7B에서 한계)
- **세 가지 모두 충족** = 동등 (구조된 arm, 4B ALFWorld)

## 6. 채널 효과: 보상이 아니라 손실로 전달하라

이 논문의 가장 실용적인 발견: **동일한 신호를 reward channel이 아니라 auxiliary loss channel로 전달하면 +20점을 얻는다.**

![Figure 5: 9개 arm의 채널 비교](/images/2026-07-27-dark-room-reward-collapse-grpo/fig-5-p9.png)

> Figure 5: 동일한 prediction 신호, 소비 메커니즘만 변경. 채널이 영역을 가른다.

![Table 2: 신호 전달 매트릭스](/images/2026-07-27-dark-room-reward-collapse-grpo/table-2-p10.png)

> Table 2: loss-channel arm들이 모든 reward-channel variant를 ~20점 차이로 이긴다. shuffled-gold placebo가 true-gold와 매칭되므로, 정확한 content-context pairing이 활성 성분이 아니다.

놀라운 발견: **shuffled-gold placebo**(정답 라벨을 섞어서 content-context pairing을 파괴)가 true-gold arm과 동등하다 (76.0 vs 69.3). 즉, auxiliary-loss 채널의 이득은 정확한 세계 모델 정보 전송이 아니라 **추가 계산/정규화 효과**일 수 있다. 논문은 이 대안적 해석을 공정하게 제시하고, 환경-분리 어휘로 stronger placebo를 사전 등록해놓았다.

![Figure 6: 보조 손실 arm의 세 막](/images/2026-07-27-dark-room-reward-collapse-grpo/fig-6-p10.png)

> Figure 6: auxiliary-loss arm의 세 단계 — 저엔트로피 축적(0.04, false "erosion" 알람), phase transition(65-72 스텝, 28→59%), 고원(59-87%). 간섭 프로브가 0으로 유지 — 보조 그래디언트가 태스크 그래디언트와 깨끗하게 공존한다.

## 7. 실무 가이드

논문이 제시하는 6가지 실용적 권고:

1. **GRPO의 std-normalized reward에 potential-difference self-prediction shaping을 섞지 마라** — 희소 성공 + 작은 그룹 + all-fail 그룹 지배 상황에서.
2. **불가피하면 mean-only normalization을 써라** — per-channel decoupling은 -20pt 만성 드래그, annealing은 완전 실패.
3. **숙달에 따라 분산이 붕괴하는 신호를 선호하라** — progress-style Δacc 보상 (사전 등록된 테스트 진행 중).
4. **보조 손실 채널을 선호하라** — +19.8pt, 그래디언트 간섭 0.
5. **엔트로피 단독으로 모니터링하지 마라** — 엔트로피 감소 + 예측 포화 + 길이 고정의 **결합 전조**를 봐야 한다 (3가지 false-alarm 모드 문서화됨).
6. **예측 포화 형태로 feature-set 난이도를 점검하라** — 즉시 0.99 = 자명한 feature, base-rate plateau = 모델 능력 초과.

## 8. 한계와 공정성

이 논문은 **단일 시드(seed 0)** 결과다. 32게임 validation noise(±8.4pt)를 인정하고, 140게임 통합 평가와 seed 복제(42/96)를 사전 등록해놓았다. 그룹 크기(n=4)가 std 병리와 공선이라는 점도 인정한다.

8B 베이스라인 anomaly(32.8% < 4B의 49.5%)도 미해결 상태다. 모든 cross-arm 비교는 "기술적(descriptive)"으로 한정된다.

이런 투명성이 이 논문의 가치를 높인다. 붕괴 기전의 수학적 분석(Proposition 1-2)은 시드와 무관하게 참이고, 단일 인자 구조(0% → 51.6%)는 시드 노이즈를 넘어서는 효과 크기다.

![Table 3: 사전 등록된 예측과 결과](/images/2026-07-27-dark-room-reward-collapse-grpo/table-3-p14.png)

> Table 3: 사전 등록된 예측과 결과. 논문의 예측이 SHA256 해시로 공개되었다가 실험 결과와 대조된다.

## 필자 코너: 에이전트 RL 실무자에게

이 논문이 특히 가치 있는 이유는 **실패의 기전을 정확히 지역화**한다는 점이다. "보상 설계가 어렵다"는 막연한 통찰이 아니라, "GRPO의 line 47에 있는 `std` 정규화가 all-fail 그룹에서 ε-스케일 shaping을 full-scale 압력으로 변환한다"는 정밀 진단이다.

특히 한국 AI 커뮤니티에서 RLVR/reward shaping을 다루는 연구자와 실무자에게:

- **GRPO를 쓴다면 std normalization을 켜놓고 dense shaping reward를 넣지 마라.** 이 논문의 Proposition 1이 왜 안 되는지 설명한다.
- **동일한 신호를 auxiliary loss로 옮기는 것만으로 +20pt.** 이것은 아키텍처 변경이 아니라 신호 전달 채널 변경이다. 구현 비용이 거의 0이다.
- **shuffled-gold placebo가 true-gold와 동등하다는 결과는 불편하지만 중요하다.** 우리가 "세계 모델을 가르쳐서 에이전트가 더 똑똑해진다"고 믿고 싶을 때, 실제로는 추가 forward pass의 정규화 효과일 수 있다. 논문이 이 대안 해석을 공정하게 제시하는 점이 학술적 성실성의 좋은 본보기다.

## 더 실습해보고 싶은 분들께

에이전트 RL, 보상 설계, GRPO 튜닝을 직접 실험해보고 싶다면 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 루프와 자동화를 실습하며 체감할 수 있는 활용 예제集
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — RL 루프 설계와 보상 공학의 기초부터 실전까지

---

## 참고문헌

- Wang, Y. (2026). *The Dark Room in the Reward Channel: Dense Prediction Rewards Collapse GRPO-Trained LLM Agents—and What Actually Works*. arXiv:2607.21273.
- Shao, Z. et al. (2024). *DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models* (GRPO). arXiv:2402.03300.
- Liu, Y. et al. (2025). *Dr.GRPO* (mean-only normalization variant).
- Ng, A. et al. (1999). *Policy invariance under reward transformations*.
- Setlur, A. et al. (2025). *Process advantage verifiers* (progress principle).
- Bereket, M. & Leskovec, J. (2025). *std removal fixes GRPO overconfidence* (독립적 수렴 증거).
