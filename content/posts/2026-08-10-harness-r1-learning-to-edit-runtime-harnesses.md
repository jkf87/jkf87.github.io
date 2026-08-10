---
title: "Harness-R1: 실행 가능한 런타임 하네스 편집을 RL로 학습하는 방법"
date: 2026-08-10
tags:
  - agent
  - harness
  - LLM
  - reinforcement-learning
  - GRPO
  - self-evolution
  - co-evolution
  - loop
  - automation
authors:
  - name: conanssam
    url: https://github.com/conanssam
    original: https://arxiv.org/abs/2608.02276
---

## 개요

Harness-R1은 LLM 에이전트의 런타임 하네스를 실패 궤적으로부터 편집하는 전용 엔지니어 모델을 온라인 강화학습으로 학습하는 방법입니다. 상하이 자오퉁대학과 샤오홍슈의 연구로, arXiv:2608.02276에 게시되었습니다.

핵심 아이디어는 에이전트 모델 자체는 동결한 채, 별도의 하네스 엔지니어(9B 모델)가 타겟 에이전트의 실패 배치를 조건으로 실행 가능한 패치를 생성하고, 패치 적용 후 타겟을 재실행하여 얻은 성공률 변화를 보상으로 학습하는 것입니다.

## 방법론

### 문제 정식화

동결된 타겟 에이전트 A와 태스크 배치 B가 주어집니다. 타겟을 수정하지 않은 기준 궤적에서 실패한 에피소드만 추출하여 실패 패킷 s_B를 구성합니다. 하네스 엔지니어 H_θ는 s_B를 입력으로 받아 실행 가능한 오버레이 P를 생성합니다.

오버레이는 에이전트 라이프사이클 4개 지점에 훅으로 설치됩니다:

1. 에피소드 초기화 — 시작 컨텍스트 및 에피소드 상태 설정
2. 의사결정 직전 — 컨텍스트에 가이드 및 인터페이스 제약 추가
3. 액션 직전 — 환경 도달 전 액션 정규화, 재작성, 또는 거부
4. 피드백 이후 — 관찰 검사 및 궤적 정체 시 복구 트리거

패치 검증 후 타겟을 동일 배치에 재실행하고, 보상 차이 Δ_B(P)를 계산합니다.

### 학습 과정

콜드스타트 SFT: GPT-5.5 교사 모델이 약 1,000개의 실패 패킷에서 편집 응답을 생성합니다. 타겟에 적용하여 검증하고, 실행 가능하며 회귀가 없는 응답만으로 SFT 데이터셋을 구성합니다.

온라인 GRPO: 분리된 약 1,500개 실패 패킷으로 온라인 RL을 수행합니다. 엔지니어가 패치 후보 K=8개를 샘플링하고, 각각을 검증 후 타겟에 적용하여 재실행합니다. 그룹 내 보상을 정규화하여 어드밴티지를 계산하고, clipped surrogate 목적으로 엔지니어 파라미터만 업데이트합니다.

![](/images/2026-08-10-harness-r1-learning-to-edit-runtime-harnesses/fig-2-p3.png)

## 실험 결과

### 메인 결과

3개 환경 (WebShop, ALFWorld, DBBench)에서 Qwen3.5-9B 타겟의 성공률 변화:

| 환경 | 베이스라인 | Harness-R1 | 변화 |
|---|---|---|---|
| WebShop | 50.6% | 57.2% | +6.6 |
| ALFWorld | 40.6% | 53.2% | +12.6 |
| DBBench | 41.8% | 50.3% | +8.5 |
| 평균 | 44.3% | 53.6% | +9.3 |

![](/images/2026-08-10-harness-r1-learning-to-edit-runtime-harnesses/fig-1-p2.png)

프론티어 모델(GLM-5.2, GPT-5.5, DeepSeek-V4 등)에게 하네스 편집을 프롬프트로 지시한 경우, 가장 좋은 GLM-5.2가 48.8%로 Harness-R1(53.6%)에 못 미쳤습니다. 고정된 Self-Refine 규칙은 세 환경 모두에서 보상을 감소시켰습니다.

### 타겟 일반화

학습에 사용하지 않은 20개 타겟 모델에 동일한 엔지니어를 적용했습니다. 모든 타겟에서 양수 이득이 관측되었으며, 평균 7.06포인트 상승이었습니다. 63개 타겟-벤치마크 조합 중 56개 개선, 4개 변화 없음, 3개 미세 회귀(≤2.0포인트)였습니다.

![](/images/2026-08-10-harness-r1-learning-to-edit-runtime-harnesses/fig-3-p8.png)

### 홀드아웃 태스크 일반화

1,270개 홀드아웃 태스크에서 +8.9±1.5포인트를 기록했습니다. 동일 조건에서 Qwen3.5-397B는 -4.3±2.5, DeepSeek-V4-Pro는 -0.4±3.6이었습니다.

![](/images/2026-08-10-harness-r1-learning-to-edit-runtime-harnesses/fig-4a-p8.png)

### 라이프사이클 위치별 기여도

pre-action mediation 제거 시 -3.9포인트, post-feedback recovery 제거 시 -3.3포인트. 환경별로 중요한 훅이 달랐습니다 (WebShop은 pre-action, ALFWorld는 post-feedback).

### 공동 진화

타겟 에이전트를 직접 SFT로 59.2%까지 개선한 후, 타겟 전용 엔지니어를 재학습하여 64.2%까지 추가 상승(+5.0포인트)을 확인했습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 리소스

- 코드: [github.com/DeepExperience/Harness-R1](https://github.com/DeepExperience/Harness-R1)
- 모델: [huggingface.co/ShaoShuai0605/Harness-R1](https://huggingface.co/ShaoShuai0605/Harness-R1)
- 원문: [arxiv.org/abs/2608.02276](https://arxiv.org/abs/2608.02276)
