---
title: "RISE — RLVR 궤적 외삽으로 스스로 증류 선생을 만드는 방법 (arXiv 2609.05295)"
date: 2026-09-08
tags:
  - llm
  - rl
  - post-training
  - distillation
draft: false
description: "RISE 논문 정리. RLVR 학습 궤적의 변위를 β>1로 외삽해 외부 모델 없이 증류 선생을 합성하고 OPD로 토큰 단위 감독을 얻는 방법. OLMo3-7B AIME'24 +16.7, ALFWorld +9.4 등."
---

## 결론 먼저

Yang Li, Semih Yavuz, Shafiq Joty의 논문 <span style="background-color: #fff59d"><strong>RISE: Recursive Improvement via Self-Extrapolating Policy Distillation</strong></span>(arXiv 2609.05295, 2026-09-04 제출)의 내용을 정리했습니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>온폴리시 증류(OPD)의 병목인 선생 모델 품질 문제를, 모델 자신의 RLVR 학습 궤적으로부터 선생을 합성하는 방식으로 해결</strong></span>합니다. 과거 앵커 체크포인트 θ와 현재 체크포인트 θ′(RLVR 갱신 후)의 변위를 표현 공간 φ(로그트 또는 가중치)에서 <span style="background-color: #fff59d"><strong>β>1 배로 외삽하여 합성 선생 θ_future를 구성</strong></span>합니다. 외부 모델도, 특권 컨텍스트도 필요 없고 이전 체크포인트만 있으면 됩니다.

φ(π_future) = φ(π_θ) + β · (φ(π_θ′) − φ(π_θ)), β > 1

## 핵심 요약 표

| 항목 | 내용 |
| --- | --- |
| 논문 | RISE (arXiv 2609.05295, 2026-09-04 제출) |
| 저자 | Yang Li, Semih Yavuz, Shafiq Joty |
| 핵심 아이디어 | RLVR 업데이트 변위를 β>1 외삽해 합성 선생 구성, OPD로 토큰 단위 감독 |
| 외삽 공간 | logit 공간(분포 기하 혼합) / 가중치 공간(task arithmetic) |
| 대표 성적 | OLMo3-7B AIME'24 +16.7, ALFWorld +9.4, WebShop +10.9 |
| 비용 | 추가 샘플링 0, 벽시계 시간 1.3–1.6배 |
| 기준일 | 2026-09-04 (arXiv v1 기준) |

## 배경: 선생이 병목이다

RLVR(GRPO, DAPO 계열)은 결과 보상 하나로 응답 전체를 평가합니다. <span style="background-color: #fff59d"><strong>어떤 토큰이 기여했는지 구분할 수 없는 크레딧 할당 병목</strong></span>이 근본 제약이구요. OPD는 토큰마다 전체 어휘 분포를 주는 밀집 신호인데, 문제는 선생 선택입니다.

- 외부 선생: 학생이 탐색한 낯선 접두사에서 <span style="background-color: #fff59d"><strong>분포 불일치로 신뢰도 하락</strong></span>.
- 특권 조건부 자기증류(OPSD): 정답을 조건으로 주는 식인데 <span style="background-color: #fff59d"><strong>ICL 능력 한계로 토큰 수준 정확도를 보장 못 함</strong></span>. 기존 개선안들(SDPO, SDAR, RLSD)은 이 선생을 그대로 두고 노이즈를 견디는 쪽만 손봤습니다.

## 방법: 궤적 외삽으로 선생 만들기

학습 루프는 이렇습니다. <span style="background-color: #fff59d"><strong>RLVR(GRPO 기반)이 변위의 방향을 검증된 개선으로 결정하고, OPD(Jensen–Shannon 발산)가 외삽 선생의 토큰 수준 분포를 학생 정책에 투영</strong></span>합니다. 선생은 매 반복 갱신되므로 증류는 일회성 압축이 아니라 <span style="background-color: #fff59d"><strong>재귀적 개선 메커니즘</strong></span>이 됩니다.

![Figure 1: RISE 개요 — RLVR 업데이트를 외삽해 θ_future를 만들고 OPD로 되돌리는 루프](/images/2026-09-08-rise-self-extrapolating-policy-distillation/fig-1-p2.png)

이론적 근거는 <span style="background-color: #fff59d"><strong>포스트트레이닝 업데이트가 저차원 부분공간에 국한되어 거의 선형적으로 진행된다는 기존 분석</strong></span>(Cai et al. 2025, Wang et al. 2026)입니다. 저자 확인 기준으로 방향 3개가 분산의 약 87%를 설명했습니다. 모델 병합 문헌의 보간(β≤1)이 강건성을 위해 선형성을 쓴다면, RISE는 능력 향상을 위해 외삽(β>1)으로 같은 구조를 씁니다.

기본 설정은 이렇습니다. <span style="background-color: #fff59d"><strong>β0=1.2에서 선형 감쇠하여 1로</strong></span>, K=100(코드 생성은 20), 앵커는 Qwen 계열 EMA η=0.1 / OLMo 계열 직전 체크포인트.

## 실험 결과: 수학 추론 (Table 1)

| 모델 | GRPO Math Avg | RISE (logit) | RISE (weight) |
| --- | --- | --- | --- |
| Qwen3-8B (DAPOMath) | 60.0 | 62.5 | 62.7 |
| Qwen3-1.7B (DAPOMath) | 45.4 | 50.2 | 49.2 |
| OLMo3-7B (OpenR1-Math-46K) | 47.6 | 56.4 | 53.7 |

세 설정 모두에서 <span style="background-color: #fff59d"><strong>RISE 두 변형이 모든 베이스라인을 상회</strong></span>했습니다. 가장 큰 이득은 경쟁 수학에서 나왔습니다. <span style="background-color: #fff59d"><strong>OLMo3-7B AIME'24 30.2 → 46.9 (+16.7), Math Avg 47.6 → 56.4 (+8.8)</strong></span>. 시드 3회 반복으로 재현성도 확인됐습니다(RISE weight 62.4±0.2 vs GRPO 60.1±0.2, Qwen3-8B).

![Table 1: 수학 추론 결과, 모델 3종 × 베이스라인 5종 정확도](/images/2026-09-08-rise-self-extrapolating-policy-distillation/table-1-p9.png)

특권 조건부 베이스라인은 부진했습니다. Qwen3-8B에서 GRPO+SDPO 55.9, SDAR 59.7, RLSD 59.8로 GRPO 단독(60.0)을 넘지 못하거나 근접 수준이었구요. 선생 품질이 병목이면 적분 방식을 바꿔봐야 한계가 있다는 논문 주장의 방증입니다.

OOD(GPQA, IFEval, MMLU-Pro)는 유지 내지 개선. <span style="background-color: #fff59d"><strong>Qwen3-8B OOD 평균 70.6 → 72.0</strong></span>으로 토큰 단위 조정이 일반 능력을 해치지 않았습니다.

![Figure 2: 세 모델 스케일에서 RISE가 더 적은 스텝에 더 높은 정확도 도달](/images/2026-09-08-rise-self-extrapolating-policy-distillation/fig-2-p9.png)

샘플 효율도 개선됐습니다. 학습 초반, RL 어드밴티지 추정이 불안정한 구간에서 외삽 선생이 밀집 신호를 먼저 공급해 초반 격차가 가장 크게 벌어집니다.

## 확장: 멀티도메인, 코드, 에이전트

- Qwen3-4B-Base 혼합(math+STEM): <span style="background-color: #fff59d"><strong>Math Avg 40.2 → 44.8, STEM Avg 45.5 → 47.5</strong></span>. 이질적 도메인의 변위를 합쳐 외삽해도 희석이 없었습니다.
- Qwen3-8B-Base 코드(Skywork-OR1-Code): 최종 정확도는 GRPO와 유사하나 <span style="background-color: #fff59d"><strong>HumanEval+ 도달 스텝 90 → 50</strong></span>으로 수렴이 빨랐습니다.
- Qwen2.5-3B-Instruct 에이전트(GIGPO 설정): <span style="background-color: #fff59d"><strong>ALFWorld +9.4, WebShop Acc +10.9</strong></span>. 희소·지연 보상의 순차 의사결정에서도 원리가 통했습니다.

## 절개 실험: 외삽의 안전 조건

두 절개 실험이 방법의 존재 이유를 보여줍니다.

- RLVR 제거: 자기증류 변위만 외삽하면 <span style="background-color: #fff59d"><strong>60스텝 내 붕괴. MATH-500 2.4%, 응답 길이 8K 컨텍스트 한도 폭주</strong></span>. 검증 보상이 방향을 못 잡으면 외삽은 자기참조적 진폭 증폭일 뿐입니다.
- OPD 제거: 외삽 체크포인트를 그냥 다음 정책으로 쓰면 안정적이지만 <span style="background-color: #fff59d"><strong>Math Avg 60.3 (GRPO 60.0)로 유의미한 이득 없음</strong></span>. 토큰 단위 투영이 이득을 만듭니다.
- β 안전 범위는 학습 진행에 따라 축소됩니다. <span style="background-color: #fff59d"><strong>RISE 운용 범위(β≤1.2)에서는 전 구간 성능 저하 없음</strong></span>.

## 실무 관점 정리

GRPO류 파이프라인을 이미 돌리고 있다면 이전 체크포인트 두 개로 시도해볼 수 있는 방법입니다. <span style="background-color: #fff59d"><strong>추가 샘플링 비용 0, 벽시계 오버헤드 1.3–1.6배</strong></span>라는 조건에서 선택지로 괜찮은 편이에요. β 감쇠 스케줄 유지와 RLVR 앵커 유지가 필수라는 점, 후반 학습으로 갈수록 외삽 민감도가 커진다는 점은 운영 리스크로 기억해두면 됩니다.

원문 근거는 전부 arXiv 2609.05295 v1(2026-09-04 제출)에서 가져왔고, 실무 관점 문단은 제 해석임을 밝힙니다. 원문: https://arxiv.org/abs/2609.05295

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### RISE에 외부 선생 모델이 필요한가?

필요 없습니다. 자기 RLVR 궤적의 체크포인트 두 개(앵커와 현재)만 사용합니다.

### GRPO 대비 학습 비용은 얼마나 되나?

추가 샘플링은 없으며 벽시계 기준 1.3–1.6배입니다.

### β는 어떻게 설정하나?

논문 기본값은 β0=1.2에서 1까지 선형 감쇠이며, 안전 범위가 학습 후반에 좁아지므로 큰 β 고정은 위험합니다.

### 에이전트 과제에서도 효과가 있나?

ALFWorld +9.4, WebShop Acc +10.9로 GRPO를 상회했습니다(Qwen2.5-3B, GIGPO 설정).
