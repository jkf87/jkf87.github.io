---
title: "IOI 2026에서 AI가 인간 최고점을 넘긴 방법 — SFT·RL·GenCorrect 전체 정리"
date: 2026-09-04
tags:
  - ai
  - llm
  - rl
  - agent
  - post-training
draft: false
description: "NVIDIA 연구팀이 IOI 2026에서 AI 시스템 최초로 인간 최고 득점자(498.27점)를 535.4점으로 넘긴 과정을 정리했습니다. 데이터 큐레이션, SFT, GRPO 강화학습, GenCorrect 테스트타임 컴퓨트 전체 파이프라인 수치를 담았습니다."
---

## 결론 먼저

IOI 2026에서 NVIDIA의 Nemotron-3-Ultra-CC가 <span style="background-color: #fff59d"><strong>535.4/600점</strong></span>으로 인간 최고 득점자(498.27점)를 넘었습니다. <span style="background-color: #fff59d"><strong>인간 참가자와 동일한 시간·인터넷 차단·제출 제한 조건</strong></span>에서 나온 점수구요, 논문 표현을 그대로 옮기면 "IOI 문제 세트에서 AI가 인간 최고 득점자를 넘은 첫 사례"입니다.

논문은 arXiv:2609.02849 (2026-09-02 공개, NVIDIA) — Sean Narenthiran, Mehrzad Samadi, Somshubra Majumdar, Boris Ginsburg입니다.

핵심 구성은 3단계입니다.

| 단계 | 내용 | 결과 |
|---|---|---|
| 데이터 큐레이션 | 16개 대회 출처 22,000문제, 실행형 평가 환경으로 패키징 | 검증 통과 환경만 사용 |
| SFT | DeepSeek-V4-Flash로 120만 개 추론 트레이스 생성 | IOI 2025 21.7% → 47.3% |
| RL (Nano만) | GRPO, 실행 보상(binary), 3,219문제 | 47.3% → 48.5% |
| GenCorrect | 5라운드 생성-평가-수정 루프 | Nano 130→468, Ultra 343.9→502.0 |

## 파이프라인 개요

전체 흐름을 단계별로 정리했습니다.

문제 큐레이션 단계에서는 지난 20년치 지역·국제 대회와 온라인 저지에서 22,000문제를 확보합니다.

각 문제를 <span style="background-color: #fff59d"><strong>문제 설명·제약·테스트케이스·레퍼런스 정답을 포함한 실행형 평가 환경</strong></span>으로 만들고, 레퍼런스 정답과 생성 정답에서 판정이 일관할 때만 남깁니다. IOI 2025/ICPC 2025/LiveCodeBench Pro 평가 문제는 학습 데이터에서 전부 제외·중복 제거했습니다.

SFT는 DeepSeek-V4-Flash로 Nano(30B-A3B)용 120만 트레이스, Ultra(550B-A55B)용 477,642 트레이스를 생성합니다. 어려운 문제에 생성을 더 배분했구요, "이전 풀이를 고치는" 자기개선 트레이스도 포함했습니다. Nano는 3에폭, Ultra는 1에폭, 시퀀스 패킹 최대 262K 토큰입니다.

RL은 Nano에만 적용했습니다. <span style="background-color: #fff59d"><strong>GRPO + 실행 기반 종단 보상(완전 통과 1, 미통과 0)</strong></span> 방식이구요, 스텝당 64프롬프트 × 16롤아웃 = 1,024롤아웃에 참조 정책 KL 페널티는 없습니다.

![전체 파이프라인](/images/2026-09-04-nemotron-ioi-gold-posttraining-rl/fig-2-p3.png)
그림 2. Nano는 SFT+RL, Ultra는 SFT만 거치고 둘 다 추론 시점에 GenCorrect를 사용합니다.

## IOI 2025에서의 각 단계 기여

### SFT가 대부분의 게인을 만든다

Nano 기준으로 IOI 2025 Score@1이 3에폭 SFT 동안 <span style="background-color: #fff59d"><strong>21.7% → 47.3%</strong></span>로 올라갔습니다. 게인 대부분은 첫 에폭에서 나왐구요, ICPC 2025 Pass@1은 16.9% → 46.7%, LCB Pro는 17.6% → 70.7%입니다.

![SFT 진행](/images/2026-09-04-nemotron-ioi-gold-posttraining-rl/fig-6-p7.png)
그림 6. SFT 에폭에 따른 세 벤치마크 성능 변화.

### RL의 기여는 작지만 일관적

SFT 3에폭 체크포인트에서 시작한 GRPO는 IOI 2025를 46.7% → 48.5%, ICPC를 47.3% → 51.0%, LCB Pro를 70.7% → 71.6%로 올렸습니다.

논문의 설명이 흥미로운데요. <span style="background-color: #fff59d"><strong>바이너리 보상 GRPO는 롤아웃 그룹에 성공·실패가 섞여 있어야 학습 신호가 생겨서, 모델 능력 경계 근처 문제에만 작동</strong></span>한다는 겁니다. 최대 255K 토큰 롤아웃에 종단 보상만 주는 롱호라이즌 크레딧 어사인먼트 문제도 같이 지적했습니다.

![RL 진행](/images/2026-09-04-nemotron-ioi-gold-posttraining-rl/fig-7-p8.png)
그림 7. GRPO 학습 곡선과 SFT 체크포인트별 RL 초기화 비교.

SFT 없이 베이스에서 바로 RL을 돌리면 21.7% → 24.9%로 올라가긴 하는데, SFT 이후에서 시작한 것과 격차가 큽니다. 정리하면 이렇습니다.

- RL은 SFT 없이도 게인을 낸다
- 근데 SFT가 주는 능력까지 대체하진 못한다
- <span style="background-color: #fff59d"><strong>예산이 한정되면 강한 베이스 모델 + 소규모 SFT가 작은 모델의 대규모 포스트트레이닝보다 낫다</strong></span> (4.3절 결론)

### GenCorrect: 테스트타임 컴퓨트로 금메달까지

GenCorrect는 최대 5라운드의 닫힌 루프입니다. 각 라운드마다 이렇게 돌아갑니다.

1. 최대 200개 후보 풀이를 병렬 생성해 로컬 컴파일 (2라운드부터는 이전 풀이+평가 피드백 포함)
2. 행동 기반 클러스터링으로 다양한 대표 후보 10개 선택 — 스코어를 보기 전에 선택
3. 10개 제출, 서브태스크 점수 피드백 수령
4. 서브태스크별 최고 점수를 누적하고 다음 라운드 조건에 반영

결과는 <span style="background-color: #fff59d"><strong>Nano 360.6 → 468.2, Ultra 343.9 → 502.0</strong></span>입니다. Ultra가 1라운드에서는 Nano보다 낮았는데 5라운드 후 33.8점 앞섰구요, 금메달 커트라인(438.3) 기준으로 Ultra는 3라운드, Nano는 4라운드에 넘었습니다.

![GenCorrect 라운드별 성능](/images/2026-09-04-nemotron-ioi-gold-posttraining-rl/fig-8-p9.png)
그림 8. 라운드별 IOI/ICPC 점수 변화와 메달 커트라인.

## IOI 2026 실전: 같은 조건에서 535.4점

대회 특화 시스템에서 눈에 띄는 선택지들입니다.

교사 모델은 IOI 2025에서 GLM-5.2가 66.0%/85,927토큰, DeepSeek-V4-Flash가 55.3%/120,456토큰을 기록해서 <span style="background-color: #fff59d"><strong>점수도 높고 출력이 짧아 고정 추론 시간에 더 많은 후보를 뽑을 수 있는</strong></span> GLM-5.2 데이터를 선택했습니다.

마지막 라운드에는 생성 예산을 <span style="background-color: #fff59d"><strong>1,000개 풀이로 늘리고</strong></span>, 모델에게 테스트 생성기·검증기·스코어링 스크립트를 직접 만들게 해서 실행 기반으로 상위 10개를 골라 제출했습니다.

NVFP4 양자화로는 BF16 대비 Score@1을 6.6포인트 주고 <span style="background-color: #fff59d"><strong>처리량 3.7배</strong></span>를 얻었습니다(199.1 → 736.8 tokens/s/GPU). 대회 시간 안에 큰 후보 배치를 돌리기 위한 트레이드오프구요, 실전 배포에서 <span style="background-color: #fff59d"><strong>최대 760대 GB300 GPU</strong></span>를 사용했습니다.

최종 결과 표입니다.

| 시스템 | 점수 | 메달 |
|---|---|---|
| 인간 최고 득점자 | 498.27 | 금 |
| 금메달 커트라인 | 361.12 | 금 |
| Ultra-CC 실전 라이브 | 535.40 | 금 |
| Ultra-CC 일반 GenCorrect 파이프라인 | 521.72 (495.0–545.8) | 금 |

일반 파이프라인 5회 반복 평균(521.72)보다 실전 점수가 13.68점 높습니다. 관측 범위 안에 들어가서, 대회 특화 적응이 의도대로 작동했다는 해석이네요.

![IOI 2026 결과](/images/2026-09-04-nemotron-ioi-gold-posttraining-rl/fig-1-p2.png)
그림 1. 파이프라인/모델의 IOI 2025·IOI 2026 성능(우측이 실전 라이브 결과).

## 모델 간 비교 (IOI 2025 Score@1 기준)

| 모델 | IOI 2025 | ICPC 2025 | LCB Pro |
|---|---|---|---|
| Nemotron-3-Nano-30B-A3B (베이스) | 21.7% | 16.9% | 17.6% |
| gpt-oss-120b | 40.7% | 45.8% | 66.4% |
| Nemotron-3-Ultra-550B-A55B (베이스) | 45.5% | 54.0% | 72.6% |
| GLM-5.2 | 66.0% | 65.7% | 83.8% |
| Nemotron-3-Nano-CC | 48.5% | 51.0% | 71.6% |
| Nemotron-3-Ultra-CC | 50.7% | 57.4% | 74.5% |

액티브 3B짜리 Nano-CC가 베이스 Ultra(550B)를 Score@1과 Score@200 모두 넘긴 점이 포스트트레이닝 효율을 보여줍니다.

![모델 비교](/images/2026-09-04-nemotron-ioi-gold-posttraining-rl/fig-5-p7.png)
그림 5. IOI 2025 Score@1/Score@200 비교.

## 내 해석: 이 논문에서 가져갈 것

원문 근거와 제 해석을 구분해서 적습니다.

- <span style="background-color: #fff59d"><strong>SFT가 여전히 포스트트레이닝 게인의 대부분</strong></span>이고 RL은 경계 능력 다듬기 수준이라는 측정(근거: 4.3/4.4절 수치)은 에이전트 RL 붐에서 자주 잊히는 사실입니다. 실행 보상 RL을 기획할 때 SFT 데이터 품질이 우선이라는 걸 보여줍니다.
- GenCorrect는 결국 <span style="background-color: #fff59d"><strong>"생성 → 실행 검증 → 피드백 반영" 하네스 루프</strong></span>를 제출 예산 안에 최적화한 설계입니다. 코드 외에도 실행 검증이 가능한 영역이면 적용 여지가 있습니다.
- 인간 최고점을 넘는 데 가장 큰 기여를 한 요소는 모델 자체보다 <span style="background-color: #fff59d"><strong>테스트타임 컴퓨트와 선택 전략</strong></span>입니다. 1라운드 343.9점이던 모델이 루프 5번으로 502점이 됐으니까요.

한계도 명시돼 있습니다. IOI 2026 런은 <span style="background-color: #fff59d"><strong>비공식·무감독 평가</strong></span>라서 순위에 포함되지 않고, 760 GPU 규모 추론 인프라가 전제된 결과입니다.

## 자주 묻는 질문

- IOI 2026에서 AI가 인간을 넘긴 건 사실인가요? 네, NVIDIA Nemotron-3-Ultra-CC가 535.4점으로 인간 최고 득점자(498.27)를 넘었습니다. 다만 비공식·무감독 평가입니다.
- RL보다 SFT가 더 중요한가요? 이 논문 측정 기준으로 SFT가 게인의 대부분을 만들었습니다. Nano에서 SFT는 +25포인트, RL은 +2포인트 수준입니다.
- GenCorrect가 뭔가요? 최대 200개 풀이를 생성하고 다양한 10개를 골라 제출한 뒤, 서브태스크 점수 피드백을 다음 라운드에 반영하는 5회 반복 테스트타임 루프입니다.
- 어떤 모델을 교사로 썼나요? 일반 파이프라인은 DeepSeek-V4-Flash, IOI 2026 실전 시스템은 GLM-5.2입니다.
- 코드는 공개되나요? 경쟁용 Ultra-CC 체크포인트와 실행 가능한 추론·평가 레시피를 NeMo-Skills(https://github.com/NVIDIA-NeMo/Skills)로 공개할 계획이라고 합니다.

## 출처

- 논문: [arXiv:2609.02849](https://arxiv.org/abs/2609.02849) — Post-Training Language Models for Gold-Medal Performance in Coding Competitions
- HTML 전문: https://arxiv.org/html/2609.02849v1
- 코드: https://github.com/NVIDIA-NeMo/Skills (공개 예정)
- 기준일: 2026-09-04 기준 arXiv v1 (2026-09-02 제출)

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
