---
title: "데이터 분석 에이전트를 강화학습으로 훈련하는 방법: 합성 보상 TRACE 논문 정리"
date: 2026-09-13
draft: false
description: 검증 가능한 정답이 없는 데이터 분석·진단 업무에 RLVR을 적용하는 방법을 정리했습니다. 시뮬레이터에 숨은 개입을 넣고 그 라벨로 보상을 만드는 TRACE 논문(arXiv 2609.10315) 핵심과 수치를 정리합니다.
tags:
  - llm-agent
  - reinforcement-learning
  - rlvr
  - data-analysis
  - paper-notes
---

## 결론 먼저

정답 검증이 어려운 진단형 분석 업무에도 RLVR을 쓸 수 있습니다. 방법은 간단합니다. 시뮬레이터에 <span style="background-color: #fff59d"><strong>숨은 개입(intervention)을 주입하고, 그 개입을 그대로 정답 라벨로 써서 보상을 합성</strong></span>하는 거예요. 에이전트는 여전히 노이즈 낀 데이터를 SQL로 조사해야 하구요, 채점은 주입된 라벨로 결정적으로 됩니다.

TRACE 논문(arXiv 2609.10315, 2026-09-09)이 이 접근을 디지털 광고 진단 환경으로 구현했습니다. 핵심 수치를 먼저 정리했습니다.

| 항목 | 값 |
|---|---|
| 논문 | TRACE: Training Reasoning Agents for Causal Exploration with Synthesized Rewards |
| arXiv | 2609.10315 (2026-09-09 제출) |
| 환경 | 디지털 광고 성능 이상 진단, 원인 12종, DuckDB 팩트 테이블 4개 |
| 훈련 대상 | Qwen3.5-35B-A3B (SFT → GRPO) |
| 핵심 지표 | FullAttr@1: 베이스 0.159 → SFT 0.637 → SFT→RL 0.757 |
| 최강 프롬프트 baseline | Claude Opus 5 = 0.686 (즉 35B post-trained 모델이 상회) |
| 툴 호출 수 | 프롬프트 베이스 22.05회 → 학습 후 11.73회 |

핵심은 이겁니다. 이 설정에서 <span style="background-color: #fff59d"><strong>병목은 모델 크기보다 검증 가능한 학습 신호의 유무였다</strong></span>는 것. 122B 프롬프팅(0.283)보다 35B 학습(0.757)이 훨씬 잘합니다.

## TRACE가 푸는 문제

RLVR은 수학·코드에서 잘 통했습니다. 검증이 생성보다 싸니까요. 근데 실무 분석은 다릅니다. 매출이 왜 떨어졌는지 진짜 원인을 확인하려면 전문가 조사가 필요하고, 사후에도 애매한 경우가 남습니다. 검증 비대칭이 없는 거예요.

논문의 질문은 이걸 뒤집습니다. "비대칭이 없으면 만들면 되지 않을까"라는 거예요.

- 원인을 관측해서 맞히는 대신, <span style="background-color: #fff59d"><strong>개입을 먼저 샘플해서 데이터를 생성</strong></span>합니다.
- 숨겨둔 개입이 오라클 라벨이 되구요, 보상은 이 라벨과 최종 답을 비교해서 결정적으로 계산됩니다.
- 에이전트는 여전히 노이즈, 교란 변수, 분산된 증거를 조사해야 해서 태스크는 어렵게 유지됩니다.

문제를 만드는 과정에서 검증자가 같이 나옵니다.

## 동작 방식: 시뮬레이터 – 오라클 – RL

전체 파이프라인은 Figure 1에 정리돼 있습니다.

![TRACE 전체 워크플로우](/images/2026-09-13-trace-synthesized-rewards-diagnostic-agents/trace-figure1-workflow.png)

에피소드 생성은 3단계로 돌아갑니다.

1. 캠페인 인구 구성 — 카테고리, 입찰 전략, 예산, 노출량을 배정합니다.
2. 개입 샘플링 — 12개 원인 중 하나, 드라이버 슬라이스(예: `placement=TOP_OF_SEARCH`), 신호 강도, onset 프로필(즉시/지연/점진)을 뽑습니다.
3. 지표 시뮬레이션 — 일별 노출·CTR·CVR·CPC를 세그먼트 단위로 렌더링합니다.

오라클 검증기가 여기서 중요합니다. 정답을 아는 상태로 <span style="background-color: #fff59d"><strong>에이전트에게 보이는 데이터만 읽어서</strong></span> <span style="background-color: #fff59d"><strong>신호가 감지 가능한지(SNR 1 이상), 교란 변수보다 강한지, 경합 원인과 구분되는지</strong></span> 확인하고 통과 못 하면 에피소드를 버립니다. 난이도와 풀 수 있음을 동시에 잡는 장치예요.

## 12가지 원인 구조

원인은 신호가 어디에 나타나는지 기준으로 4그룹으로 나뉩니다.

| 그룹 | 예시 원인 | 진단 포인트 |
|---|---|---|
| 캠페인 전체 (4종) | BID INCREASE, BUDGET CAP, PAGE DEGRADATION, OUT OF STOCK | 집계 지표에 바로 보임 |
| 세그먼트 믹스 (3종) | PLACEMENT SHIFT, TARGETING BROADENING/NARROWING | 총량은 비슷, 트래픽 구성 변화 |
| 세그먼트 특정 (4종) | CREATIVE FATIGUE, COMPETITIVE PRESSURE, AD QUALITY DROP, AUDIENCE SATURATION | 올바른 분할에서만 신호가 나옴 |
| 신호 없음 (1종) | NO SIGNAL | 증거 부족 시 판단 보류해야 함 |

에이전트는 Python/SQL 툴로 DuckDB 팩트 테이블 4개를 조사하고, 최종 답으로 원인 + 영향 슬라이스(2차원이면 `placement=TOP_OF_SEARCH, geo=US` 같은 교집합)를 제출합니다.

## 보상 설계

GRPO로 학습합니다. 보상은 세 항의 가중합이구요, 논문 세팅은 이렇습니다.

| 구성 | 가중치 | 내용 |
|---|---|---|
| r_attr (graded) | 0.65 | 원인 정답 + 슬라이스 Jaccard 부분 점수 |
| r_full (binary) | 0.30 | 원인과 슬라이스가 정확히 일치할 때만 1 |
| r_fmt | 0.05 | 파싱 가능한 최종 답 형식 |

<span style="background-color: #fff59d"><strong>이진 full-attribution 항이 성패를 갈랐습니다.</strong></span> graded만 쓰면 0.596인데 r_full을 넣으니 0.757까지 올라갑니다. 슬라이스를 완전히 복원해야 점수를 주는 압력이 다차원 귀속에서 결정적이었던 거예요.

훈련 인프라는 slime 포크 + Megatron-LM + SGLang + Ray 비동기 파이프라인, 300 스텝, 스텝당 32 프롬프트 × 8 트랙토리입니다.

## 결과: 35B로 프론티어 넘기

235 에피소드 홀드아웃 테스트 결과입니다.

| 모델 | Cause@1 | FullAttr@1 | No-Signal 정확도 |
|---|---|---|---|
| Qwen3.5-35B (베이스) | 0.184 | 0.159 | 0.41 |
| + SFT | 0.685 | 0.637 | 0.76 |
| + RL (베이스부터) | 0.471 | 0.434 | 0.28 |
| SFT→RL | 0.823 | 0.757 | 0.49 |
| Qwen3.5-122B (프롬프팅) | 0.296 | 0.283 | 0.78 |
| Claude Opus 5 | 0.764 | 0.686 | 0.87 |
| GPT-5.6 Sol | 0.635 | 0.565 | 0.30 |
| GPT-5.5 | 0.581 | 0.524 | 0.61 |
| Claude Sonnet 5 | 0.472 | 0.438 | 0.85 |

읽을 포인트 세 가지입니다.

- <span style="background-color: #fff59d"><strong>SFT 다음에 RL을 얹으니 +12.0pp가 추가</strong></span>됐습니다(0.637 → 0.757). 합성 보상이 SFT에 더해지는 효과란 뜻이에요.
- 학습된 35B가 프롬프팅한 122B(0.283)를 크게 앞섭니다. 스케일만으론 안 되는 영역이라는 근거입니다.
- 툴 호출은 오히려 줄었습니다. 프롬프트 베이스 평균 22.05회 → 학습 후 11.73회. <span style="background-color: #fff59d"><strong>성적 향상은 '더 많이 조사'에서 온 게 아니라 '더 잘 조사하고 멈추기'에서 왔다</strong></span>는 게 Figure 2의 메시지입니다.

![FullAttr@1 대비 툴 호출 수](/images/2026-09-13-trace-synthesized-rewards-diagnostic-agents/trace-figure2-toolcalls.png)

![툴 효율 상세](/images/2026-09-13-trace-synthesized-rewards-diagnostic-agents/trace-figure2-toolcalls-detail.png)

## 어블레이션에서 배울 것

| 학습 조건 | Overall | 1D 슬라이스 | 2D 슬라이스 | No Signal |
|---|---|---|---|---|
| SFT만 | 0.637 | 0.71 | 0.04 | 0.76 |
| SFT→RL, graded만 | 0.596 | 0.67 | 0.00 | 0.64 |
| + full-attribution 항 | 0.757 | 0.92 | 0.27 | 0.49 |
| + KL 정규화 | 0.724 | 0.92 | 0.16 | 0.30 |
| 베이스부터 RL | 0.434 | 0.51 | 0.03 | 0.28 |

- SFT 초기화가 필수입니다. 같은 보상으로 베이스부터 RL하면 0.434에 그칩니다.
- KL 페널티는 여기서 도움이 안 됐습니다(0.757 → 0.724).
- <span style="background-color: #fff59d"><strong>2차원 슬라이스가 남은 과제</strong></span>입니다. SFT→RL도 0.27로 Opus 5(0.33)보다 낮아요. 원인 종류는 맞혀도 슬라이스를 완전히 복원하지 못하는 경우가 많습니다.
- No-signal 구간은 학습 모델(0.49)이 Opus(0.87)보다 약합니다. <span style="background-color: #fff59d"><strong>"증거 부족 시 답하지 않기"가 학습 정책에서 오히려 약해졌다</strong></span>는 점은 실무 적용 시 주의할 부분이에요.

## 실무에 가져갈 것

- 검증 보상이 없는 도메인에 RL을 쓰고 싶으면, <span style="background-color: #fff59d"><strong>"개입을 샘플해서 데이터를 만들 수 있는가"를 먼저 확인</strong></span>하세요. 시뮬레이터가 있으면 보상은 저절로 따라옵니다.
- 부분 점수(graded)만 주면 다차원 귀속에서 실패합니다. <span style="background-color: #fff59d"><strong>완전 귀속 보상을 명시적으로 넣는 게 설계 포인트</strong></span>예요.
- 오라클 검증기로 "풀 수 있는 에피소드"만 남기는 필터를 꼭 두세요. 그래야 노이즈 속 학습이 안정됩니다.

기준일: 2026-09-13, arXiv v1 기준입니다.

## 더 실습해보고 싶은 분들께

에이전트 훈련 루프와 하네스를 직접 다뤄보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Q. RLVR을 쓸 수 없는 업무에 RL을 적용하려면?**
시뮬레이터로 태스크를 생성하고 숨은 개입을 정답 라벨로 쓰면 됩니다. TRACE가 디지털 광고 진단에서 보여준 방식이구요, 제어 가능한 생성 모델이 있는 도메인이면 같은 구조가 적용됩니다.

**Q. 학습된 35B 모델이 정말 프론티어 모델을 이겼나요?**
FullAttr@1 기준 0.757으로 Claude Opus 5(0.686)를 포함한 전체 프롬프팅 baseline을 넘었습니다. 근데 이차원 슬라이스(0.27 vs 0.33)와 no-signal 판단(0.49 vs 0.87)에서는 아직 뒤집힙니다.

**Q. 왜 SFT를 먼저 해야 하나요?**
같은 보상으로 베이스부터 RL하면 0.434에 그칩니다. 감독 웜스타트가 조사 절차와 중단 시점을 먼저 가르쳐주고, RL이 그 뒤에 귀속 정확도를 끌어올리는 구조예요.

**Q. 합성 보상의 위험은 없나요?**
보상 게이밍 가능성은 논문도 인지하고 있습니다(스칼스 등의 reward gaming 인용). 여기서는 오라클 검증기가 신호 감지 가능성과 경합 원인 구분성을 에이전트 가시 데이터로 확인해서 완화합니다.

**Q. 툴 호출이 많아진 걸까요?**
아니요. 22.05회에서 11.73회로 줄었습니다. 성능 향상은 탐색량이 아니라 탐색 효율에서 왔습니다.

## 참고 자료

- TRACE: Training Reasoning Agents for Causal Exploration with Synthesized Rewards — https://arxiv.org/abs/2609.10315
- HTML 버전 — https://arxiv.org/html/2609.10315v1
- GRPO 원논문(DeepSeekMath) — https://arxiv.org/abs/2402.03300
