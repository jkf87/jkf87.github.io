---
title: MAD-OPD — 티처 두 명이 토론하니 4B 학생이 14B 선생을 넘었다
date: 2026-08-30
tags:
  - ai
  - llm
  - agents
  - rl
  - distillation
draft: false
description: MAD-OPD(arXiv 2605.01347)는 온폴리시 증류에서 티처를 토론하는 집단으로 바꿔 단일 티처 능력 천장을 깬다. 6개 티처-학생 구성 전체 1위, 14B+8B→4B에서 에이전트 평균 +2.4%, 코드 평균 +3.7%, 4B 학생이 14B 티처를 LCB-v6에서 초과.
---

## 결론 먼저

MAD-OPD(arXiv 2605.01347)는 온폴리시 증류(OPD)에서 <span style="background-color: #fff59d"><strong>선생을 한 명이 아니라 토론하는 집단으로 바꿔 단일 티처 능력 천장을 깬 방법</strong></span>입니다. 학생이 자기 궤적을 진행하는 매 스텝마다 티처 여러 명이 그 상태를 두고 토론하고, 토론 후 자신감으로 가중한 분포가 토큰 단위 감독 신호가 됩니다. 그래디언트는 학생만 업데이트합니다.

핵심 숫자를 먼저 정리하면:

| 항목 | 값 |
| --- | --- |
| 논문 | MAD-OPD: Breaking the Ceiling in On-Policy Distillation via Multi-Agent Debate (arXiv:2605.01347, 2026-05-02) |
| 기본 구성 | 티처 K=2명, 토론 R=2라운드, 신뢰도 가중 감독 |
| 발산 선택 | 에이전트는 JSD(β=0.5), 코드는 reverse KL |
| 평가 구성 | Qwen3/Qwen3.5, 학생 1.7B–14B, 티처 8B–32B, 6개 구성 |
| 벤치마크 | BFCL-v4, τ²-Bench, VitaBench / LCB-v6, MBPP+ |
| 대표 결과(14B+8B→4B) | 에이전트 평균 +2.4%, 코드 평균 +3.7% (단일 티처 OPD 대비) |
| 학생 초과 | 4B 학생이 LCB-v6에서 14B 티처 대비 pass@1 +4.26%, BoN@16 +10.29% |
| 코드 | github.com/chiefovoavicii/MAD-OPD (Apache-2.0) |

기준일: 2026-08-30 기준 arXiv v1 내용입니다.

## 기존 OPD의 한계

온폴리시 증류는 학생 모델이 자기 궤적을 진행하면 그 자리에서 티처가 토큰 단위로 지도하는 학습법입니다. SFT보다 학생 상태 분포에 맞는 학습이 된다는 장점이 있어요.

근데 함정이 두 개 있습니다.

한 가지는 <span style="background-color: #fff59d"><strong>티처가 틀리면 학생이 그 오류를 그대로 물려받습니다</strong></span>. 티처 14B면 학생은 14B를 넘기 어렵다는 뜻이에요.

다른 한 가지는 에이전트 태스크 검증 부족입니다. 다중 스텝 태스크는 스텝마다 오차가 누적되는데, 기존 OPD는 이 누적 앞에서 학습이 불안정해집니다.

논문 Figure 1이 첫 번째 한계를 보여줍니다. 단일 티처의 잘못된 툴 호출이 학생에게 상속되는 장면입니다.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/fig-1-p2.png)

## 작동 방식

파이프라인은 Figure 2 하나로 요약됩니다.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/fig-2-p6.png)

스텝 m에서 일어나는 일을 순서대로 쓰면:

1. 학생 π_θ가 현재 상태 s_m에서 행동을 샘플링합니다.
2. 티처 K명이 s_m을 보고 각자 초기 답을 냅니다.
3. 티처들이 R라운드 토론합니다. 토론록 H_m^R은 티처에게만 보입니다.
4. 각 티처가 토론록을 조건으로 학생의 온폴리시 행동을 force-decode하면서 분포를 냅니다.
5. 토론 후 자신감(post-debate confidence)으로 각 티처 기여를 가중합한 발산 손실을 만듭니다.
6. 그래디언트로 학생만 업데이트합니다.

<span style="background-color: #fff59d"><strong>토론록이 티처 전용 특권 정보(privileged context)라는 설계</strong></span>가 핵심입니다. 학생은 토론 내용을 못 봐요. 티처 집단만 공유하는 이 정보 격차(p-q 갭)가 감독 신호 품질을 끌어올립니다.

### 태스크별 발산 선택

논문은 발산(divergence) 선택을 태스크에 따라 갈라야 한다고 주장합니다. 토큰 단위 그래디언트 안정성과 모드 커버리지 분석에서 유도한 원칙이에요.

| 태스크 | 발산 | 근거 |
| --- | --- | --- |
| 에이전트 (BFCL-v4, τ²-Bench, VitaBench) | JSD (β=0.5) | 다중 스텝 오차 누적 하에서 학습 안정성 |
| 코드 (LCB-v6, MBPP+) | reverse KL | 모드 커버리지, 코드 품질 |

### OPAD: 에이전트용 스텝 샘플링

에이전트 확장인 OPAD(On-Policy Agentic Distillation)는 <span style="background-color: #fff59d"><strong>스텝 레벨 샘플링을 추가해 다중 스텝 오차 누적 상황의 학습을 안정화</strong></span>합니다. Figure 6의 학습 손실 곡선에서 MAD-OPD가 단일 티처 OPD보다 안정적인 걸 확인할 수 있어요.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/fig-6-p19.png)

## 결과 정리

### 6개 구성 전부 1위

Qwen3와 Qwen3.5, 학생 1.7B–14B, 티처 8B–32B를 조합한 <span style="background-color: #fff59d"><strong>6개 구성 전체에서 MAD-OPD가 1위</strong></span>입니다. 비교 대상은 단일 티처 OPD, 등가중 다중 티처 OPD(MT-OPD), 오프폴리시 7:3 혼합(MT-SeqKD) 등입니다.

대표 설정(14B+8B→4B)에서 <span style="background-color: #fff59d"><strong>에이전트 평균 +2.4%, 코드 평균 +3.7%</strong></span>을 더 강한 쪽 단일 티처 OPD 대비로 기록했습니다. 벤치마크 수가 다섯 개라 퍼센트 절대값은 조심스럽게 봐야 하는데, 6개 구성 일관성은 강한 신호예요.

### 학생의 티처 초과 결과

가장 눈에 띄는 결과입니다. 4B 학생이 14B+8B 티처 토론으로 학습했을 때 LCB-v6에서 <span style="background-color: #fff59d"><strong>14B 티처보다 pass@1 +4.26%, BoN@16 +10.29% 앞섰습니다</strong></span>. 단일 티처 증류로는 나올 수 없는 결과입니다. 토론이 만드는 집단 지성이 개별 티처 능력을 넘어서고, 학생이 그걸 흡수한 그림이에요.

### 스케일링

Figure 3에서 스케일링 행동을 확인할 수 있습니다. <span style="background-color: #fff59d"><strong>티처·학생 규모가 커질수록 게인도 같이 커지는 경향</strong></span>입니다.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/fig-3-p9.png)

### 발산·컴포넌트 절검

Table 4는 발산 절검입니다. 에이전트 태스크에서는 JSD가, 코드 태스크에서는 reverse KL이 이기는, 주장과 일치하는 패턴이에요.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/table-4-p17.png)

Figure 4의 컴포넌트 절검에서는 <span style="background-color: #fff59d"><strong>신뢰도 가중과 토론 각각의 기여를 분리했고, 둘 다 빼면 성능이 크게 떨어집니다</strong></span>.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/fig-4-p9.png)

## 비용과 한계

매 스텝 티처 토론(K=2, R=2)이 필요하니 <span style="background-color: #fff59d"><strong>티처 추론량이 단일 티처 대비 대략 4배로 늘어납니다</strong></span>. 추가 비용입니다. 논문이 Figure 5의 정확도-효율 트레이드오프 분석을 따로 넣은 이유예요.

![](/images/2026-08-30-mad-opd-debate-on-policy-distillation/fig-5-p17.png)

벤치마크 수도 아직 다섯 개입니다. 퍼센트 게인의 절대값보다 "6개 구성 일관성" 쪽이 더 믿을 만한 신호라고 봅니다.

## 내 해석

원문 근거와 제 해석을 구분해서 정리했습니다.

원문이 말하는 것: 토론 조건화된 티처 분포가 단일 티처 argmax 디코딩보다 낫고(Prop. 1), 그 차이가 학생 성능으로 이어진다. GRPO 계열 RL과 직교해서 조합 가능하다.

제 해석: 이건 <span style="background-color: #fff59d"><strong>증류 티처 신호를 학생의 라이브 상태에 반응하는 런타임 토론으로 만드는 접근</strong></span>입니다. 티처들이 사전 계산이 아니라 학생의 현재 상태를 보고 감독한다는 점이 차별점이에요. 실무 관점에서는:

- 소형 모델(1.7B–4B) 에이전트를 만들어야 하고 강한 티처 접근권이 있다면 시도해볼 가치가 있다.
- 티처 추론 비용 4배는 미리 계산해야 한다.
- RL과의 조합 가능성은 논문 언급 수준이고 검증은 후속 과제다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### MAD-OPD의 핵심 기여는 무엇인가요?
티처를 토론하는 집단으로 바꿔 단일 티처 능력 천장을 깬 것, 에이전트 태스크용 OPAD 스텝 샘플링, 태스크별 발산 선택 원칙(JSD/reverse KL) 세 가지입니다.

### 학생이 티처보다 잘할 수 있나요?
가능한 케이스가 확인됐습니다. 4B 학생이 14B+8B 토론 티처로 학습해 LCB-v6에서 14B 티처보다 pass@1 +4.26%, BoN@16 +10.29% 앞섰습니다.

### 비용은 얼마나 드나요?
매 스텝 티처 토론(K=2, R=2)이 필요하므로 티처 추론량이 대략 4배 늘어납니다. 논문은 Figure 5 정확도-효율 트레이드오프를 함께 제시합니다.

### RL 포스트트레이닝과 어떤 관계인가요?
MAD-OPD는 증류 기반이고 GRPO 같은 RL과 직교하는 방법이라 조합 가능하다고 논문은 서술합니다. 조합 성능 검증은 후속 과제입니다.

## 참고 자료

- arXiv: [MAD-OPD: Breaking the Ceiling in On-Policy Distillation via Multi-Agent Debate](https://arxiv.org/abs/2605.01347) (2605.01347, 2026-05-02)
- GitHub: [chiefovoavicii/MAD-OPD](https://github.com/chiefovoavicii/MAD-OPD) (Apache-2.0)
- Hugging Face: [논문 페이지](https://huggingface.co/papers/2605.01347)
