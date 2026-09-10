---
title: "TRACE: 합성 보상으로 진단 에이전트를 강화학습하는 방법 (arXiv 2609.10315)"
date: 2026-09-11
tags: [ai, llm, rl, agent, rlvr, arxiv]
draft: false
description: "arXiv 2609.10315 TRACE 논문 요약. 시뮬레이터 개입 주입으로 oracle 라벨을 확보하고 GRPO로 Qwen3.5-35B를 학습해 FullAttr@1 0.757을 달성한 방법, 보상 설계, 애블레이션 결과를 정리합니다."
---

## 핵심 요약

TRACE(Sun, Shi, He; Independent Researchers; arXiv 2609.10315)는 검증자가 존재하지 않는 진단 추론 태스크에 RLVR을 적용하는 방법론을 제안한다. 방법은 다음과 같다. <span style="background-color: #fff59d"><strong>시뮬레이터에 개입(intervention)을 샘플링해 주입하고, 해당 개입이 만들어낼 관측 데이터를 생성한다. 주입된 개입은 숨겨진 oracle 라벨이 되어 객관적 보상 계산에 사용된다.</strong></span>

주요 결과 (235 에피소드 홀드아웃, 기준일 2026-09-11):

| 항목 | 값 |
| --- | --- |
| SFT→RL Qwen3.5-35B-A3B FullAttr@1 | 0.757 |
| Claude Opus 5 (프롬프팅) FullAttr@1 | 0.686 |
| Qwen3.5-122B-A10B (프롬프팅) | 0.283 |
| 베이스 35B (프롬프팅) | 0.159 |
| 평균 툴 호출 (학습 정책 vs 프롬프팅) | 11.73 vs 22.05 |

논문: [arXiv 2609.10315](https://arxiv.org/abs/2609.10315)

## 문제 정의

RLVR은 수학(정답 비교)과 코드(테스트 실행)에서 유효하다. 진단 추론은 다르다.

원인 귀속에 전문가 조사가 필요하고, 결과가 사후에도 애매할 수 있으며, 복수 원인·노이즈·유사 신호가 공존한다. LLM-as-judge로도 판정 오류가 남는다. 논문은 이 "검증의 비대칭"을 데이터 생성 쪽에서 해결한다.

## 환경 구성

TRACE는 디지털 광고 진단 환경이다. 에피소드 생성은 3단계: (1) 캠페인 모집단 구축, (2) 개입 샘플링 — <span style="background-color: #fff59d"><strong>12개 원인 유형, 드라이버 슬라이스(1~2차원), 신호 세기, onset 프로파일</strong></span>, (3) 일별 지표 시뮬레이션(노출 Poisson, 세그먼트 Dirichlet-Multinomial, CTR/CVR/CPC율).

원인 유형은 캠페인 전역(입찰가 상승, 예산 상한, 페이지 저하, 품절), 세그먼트 믹스(배치 이동, 타게팅 확장/축소), 세그먼트 특정(크리에이티브 피로, 경쟁 압박, 광고 품질 저하, 오디언스 포화), 신호 없음으로 분류된다.

![TRACE 워크플로](/images/2026-09-11-trace-synthesized-rewards-diagnostic-rl/fig1-workflow.png)
*Figure 1: TRACE 워크플로. 출처: arXiv 2609.10315*

오라클 검증기는 agent-visible 데이터만 읽어 <span style="background-color: #fff59d"><strong>(a) 신호 검출 가능성, (b) 최대 혼동 요인 대비 강도, (c) 경쟁 원인과의 구별 가능성을 확인하고 통과한 에피소드만 사용</strong></span>한다.

에이전트는 Python과 SQL로 멀티테이블 증거를 조사하며, 원인(what)·세그먼트(where)·시점(when)을 모두 맞춰야 정답으로 인정된다. 세그먼트 효과는 캠페인 집계에 희석되므로 올바른 분할을 찾는 것이 핵심 난제다.

## 보상 설계

GRPO 목표함수에 세 보상 항을 가중합한다: r = 0.65·r_attr + 0.30·r_full + 0.05·r_fmt.

- r_attr: 원인 정답 게이팅 + 슬라이스 Jaccard 부분 점수 (α=0.5)
- r_full: 원인·슬라이스 정확 일치 시에만 1
- r_fmt: 파싱 가능 형식

<span style="background-color: #fff59d"><strong>이진 r_full을 넣기 전 FullAttr@1 0.596, 넣은 후 0.757</strong></span>로 16점 상승했다. 부분 점수만으로는 다차원 슬라이스 완전 복원 유인이 부족했다는 것이다.

SFT는 Claude Opus 4.8 궤적 거절 샘플링 1,200예시, RL은 <span style="background-color: #fff59d"><strong>오라클 검증 통과 5,000 에피소드(학습 4,472/검증 528)</strong></span>로 수행한다. 사람 어노테이션과 LLM judge는 사용하지 않는다.

## 실험 결과

| 모델 | Cause@1 | FullAttr@1 |
| --- | --- | --- |
| Qwen3.5-35B (베이스) | 0.184 | 0.159 |
| + SFT | 0.685 | 0.637 |
| + RL (베이스 초기화) | 0.471 | 0.434 |
| + SFT→RL | 0.823 | 0.757 |
| Claude Opus 5 | 0.764 | 0.686 |

애블레이션 결과: 이진 r_full 제거 시 0.596, 베이스 직접 RL 초기화 시 0.434, KL 정규화 제거 시 0.724로 각각 하락.

<span style="background-color: #fff59d"><strong>RL은 SFT warm start 이후 +12.0%p(0.637→0.757)로 additive하게 작용</strong></span>했다.

35B 학습 모델(0.757)이 122B 프롬프팅(0.283)을 크게 앞섰다. 저자들의 결론은 이 태스크의 병목이 모델 스케일보다 <span style="background-color: #fff59d"><strong>유효한 포스트트레이닝 신호 쪽</strong></span>에 있었다는 것이다.

![툴 호출 대비 성능](/images/2026-09-11-trace-synthesized-rewards-diagnostic-rl/fig2-toolcalls.png)
*Figure 2: FullAttr@1 대비 평균 툴 호출 수. 출처: arXiv 2609.10315*

툴 효율 측면에서 학습 정책은 <span style="background-color: #fff59d"><strong>평균 11.73회 호출로 프롬프팅 베이스(22.05회)의 절반 수준</strong></span>에서 더 높은 정확도를 달성했다.

1차원 슬라이스는 SFT 0.71 → RL 0.92로 개선되나 <span style="background-color: #fff59d"><strong>2차원 슬라이스 복원이 주요 오류원으로 남는다</strong></span>.

## 논평

여기부터는 내 해석이다.

제한점: <span style="background-color: #fff59d"><strong>시뮬레이터의 현실 충실도가 결과의 상한을 결정</strong></span>한다. 12개 고정 원인 유형의 닫힌 분류 설정이며, 광고 도메인 외 일반화는 검증되지 않았다. 그럼에도 <span style="background-color: #fff59d"><strong>"개입 주입 → oracle 확보 → RL" 패턴은 SRE 진단, 이상 탐지 후속 분석 등 검증자 부재 도메인에 적용 가능한 일반 레시피</strong></span>로 판단된다. 검증자를 기다릴 게 아니라 검증자가 존재하는 문제를 제조하는 방향이 먼저다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### TRACE의 태스크는 무엇인가?
광고 성과 변화의 원인 12개 유형 중 무엇이, 어느 세그먼트에서, 언제부터 발생했는지 Python/SQL 조사로 귀속하는 과제다.

### 합성 보상은 어떻게 계산되나?
주입 개입이 oracle 라벨이 되며, 에이전트의 최종 귀속(원인+슬라이스)과 비교해 Jaccard 기반 부분 점수와 이진 정확 일치 보상이 계산된다.

### 35B 모델이 프론티어 모델을 능가했나?
TRACE 환경 한정 FullAttr@1 0.757로 Claude Opus 5(0.686)를 능가한다. 범용 능력 비교는 아니다.

### 주요 한계는?
시뮬레이터 충실도 의존, 닫힌 원인 분류, 단일 도메인 평가이다.
