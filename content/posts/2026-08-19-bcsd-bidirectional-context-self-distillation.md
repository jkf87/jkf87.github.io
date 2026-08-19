---
title: "BCSD: 스킬을 잘 쓰는 에이전트를 만드는 양방향 컨텍스트 자기증류"
date: 2026-08-19
tags: [agent, reinforcement-learning, llm, skill, self-distillation]
draft: false
---

## 결론 먼저

에이전트에 스킬 라이브러리를 달아줘도 정작 스킬을 잘 못 쓰는 문제가 있습니다. BCSD(Bidirectional Context Self-Distillation)는 이 문제를 <span style="background-color: #fff59d"><strong>"스킬을 더 잘 쓰도록 정책을 학습시키는 것"</strong></span>으로 접근합니다. 컨텍스트를 늘린 뷰와 줄인 뷰, 두 방향에서 자기증류 신호를 만들어 GRPO 어드밴티지를 리스케일하는 방식이 핵심입니다.

논문: [Bidirectional Context Self-Distillation for Reinforcement Learning of Skill-Based LLM Agents](https://arxiv.org/abs/2608.09555)

## 문제 정의

스킬 기반 에이전트 연구는 크게 두 갈래였습니다.

| 방향 | 접근 | 한계 |
| --- | --- | --- |
| 스킬 품질 개선 | SkillBank 생성/감사/수정 | 좋은 스킬을 줘도 활용을 못함 |
| 스킬 내재화 | 파라미터로 증류 | 명시성·편집성·전이성 상실 |

핵심은 이겁니다. 좋은 스킬을 제공해도 <span style="background-color: #fff59d"><strong>에이전트가 그 스킬을 효과적으로 쓰는 것은 별개의 문제</strong></span>라는 점입니다. 태스크 성공 리워드만으로는 어떤 결정이 스킬에 근거했는지 알 수 없습니다.

![BCSD가 다루는 세 가지 패러다임 비교](/images/2026-08-19-bcsd-bidirectional-context-self-distillation/figure1-paradigms.png)
*그림 1. 스킬 진화, 스킬 내재화, 그리고 BCSD의 스킬 활용 개선. 출처: 논문 Figure 1*

## 방법: 두 개의 컨텍스트 뷰

BCSD는 같은 정책을 서로 다른 컨텍스트에서 다시 스코어링해서 토큰 단위 신호를 만듭니다.

### 1. 증강 뷰 (Augmented) — Meta-Skill 추가

롤아웃 트레이닝에서 성공/실패 궤적을 대조해서 <span style="background-color: #fff59d"><strong>"이 스킬을 어떻게 써야 하는가"에 대한 상위 가이던스(Meta-Skill)를 추출</strong></span>합니다. 이건 현재 정책의 행동에 의존하는 텍스트라서, 학습이 진행될 때마다 검증 윈도우마다 갱신됩니다. 추론 시에는 학생 컨텍스트에 포함되지 않습니다.

### 2. 축소 뷰 (Pruned) — 일반 가이던스 제거

일반 스킬 G에서 군더더기를 잘라낸 Gp를 만듭니다. 태스크 특화 스킬은 그대로 두고 <span style="background-color: #fff59d"><strong>방해가 되는 일반 지침만 제거해서 태스크 스킬 사용 여부에 집중된 참조</strong></span>를 만드는 거구요.

### 3. 갭-가중 어드밴티지 리스케일

각 토큰에 대해 두 컨텍스트에서의 로그확률 갭을 계산합니다.

Δ = α·Δaug + (1−α)·Δpru (α=0.9)

이 갭으로 원래 GRPO 어드밴티지의 크기만 조절합니다.

<span style="background-color: #fff59d"><strong>업데이트 방향은 리워드가 정하고, 크기만 컨텍스트 신호가 조절</strong></span>합니다. 리스케일 계수 λn은 0.1에서 선형 감쇠해서 초반에는 밀도 높은 가이던스를 주고 후반에는 환경 리워드에 반환합니다.

![BCSD 전체 프레임워크](/images/2026-08-19-bcsd-bidirectional-context-self-distillation/figure2-overview.png)
*그림 2. 스킬 조건 롤아웃, 메타스킬 추출, 양방향 자기증류로 토큰별 어드밴티지 리스케일. 출처: 논문 Figure 2*

## 결과

ALFWorld와 WebShop에서 Qwen2.5-3B/7B, Qwen3-1.7B로 평가했습니다.

| 모델 | 벤치마크 | BCSD | 최고 baseline 대비 |
| --- | --- | --- | --- |
| Qwen2.5-7B | ALFWorld 평균 | 83.6% | +3.1pt |
| Qwen2.5-7B | WebShop SR | 78.1% | 최고 |
| Qwen2.5-3B | ALFWorld | — | +5.4pt |
| Qwen2.5-3B | WebShop SR | — | +9.4pt |
| Qwen3-1.7B | ALFWorld | 46.9% | +3.9pt |

학습 곡선에서도 차이가 뚜렷합니다. WebShop에서 <span style="background-color: #fff59d"><strong>스텝 60에 BCSD는 약 45%에 도달, 다른 메서드는 20% 미만</strong></span>이었습니다. 최종적으로 약 66%로 최강 baseline 대비 약 9%p 우위입니다.

### Ablation 결과

- Meta-Skill 뷰 제거: ALFWorld 82.0 → 71.1, WebShop 66.4 → 50.0. 가장 큰 하락이었습니다.
- Pruned 뷰 제거: 82.0 → 75.0.
- λ 고정(감쇠 없음): 76.6 / 52.3. <span style="background-color: #fff59d"><strong>초반 가이던스는 유지하되 후반엔 리워드 학습으로 반환</strong></span>해야 합니다.

### 진짜 스킬을 쓰는 걸까?

태스크 스킬 Sc를 추론 시 제거하면 BCSD는 ALFWorld −2.3pt, WebShop −7.8pt 하락합니다. Skill_GRPO∗(−0.8/−6.2)보다 크게 떨어지는데, 역설적으로 이게 증거입니다. <span style="background-color: #fff59d"><strong>파라미터에 태스크 지식을 외운 게 아니라 외부 스킬을 실제로 읽어서 쓰고 있다</strong></span>는 뜻이거든요. 스킬 사용법만 내재화하고 지식은 외부에 편집 가능한 형태로 남겨둔 겁니다.

## 내 해석

정리했습니다. 이 논문의 실용적 포인트는 두 가지입니다.

1. 온프레미스 스킬 뱅크를 운영 중이라면, 스킬 문서를 더 다듬는 것보다 <span style="background-color: #fff59d"><strong>정책이 스킬을 활용하도록 학습시키는 편이 훨씬 큰 성능 차이</strong></span>를 만듭니다.
2. 자기증류 신호는 단일 특권 컨텍스트에 의존하면 불안정합니다. 늘리기/줄이기 양방향에서 교차 검증하는 구조가 안정적인 크레딧 어사인먼트로 이어졌습니다.

한계도 분명합니다. ALFWorld/WebShop은 텍스트 기반 벤치마크라서 실무 툴 사용 에이전트로의 확장은 추가 검증이 필요합니다. 코드 릴리스가 예고되어 있으니 재현은 가능할 것으로 봅니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
