---
title: "COVE: 에이전트 자가진화에서 메모리와 파라미터를 동시에 쓰는 방법"
date: 2026-08-08
tags:
  - agent
  - self-evolution
  - harness
  - memory
  - LLM
  - reinforcement-learning
  - fine-tuning
  - loop
  - automation
---

source: arXiv 2608.01234

## 요약

에이전트가 배포 후 경험을 축적할 때, 외부 메모리(harness)와 모델 가중치(parameter) 중 어디에 저장할지 자동으로 판단하는 프레임워크다.

## 배경

LLM 에이전트는 API 변경, 새로운 라이브러리, 바뀐 사용자 요구에 직면한다. 기존 자가진화 접근은 두 가지로 나뉜다:

- 하네스 기반: 피드백을 외부 메모리나 스킬로 저장. 빠르지만 모델 역량 부족 시 쓸모없는 경험이 쌓인다.
- 파라미터 기반: 경험을 가중치에 내재화. 깊지만 비싸고, 표면 형식(API 이름 등)이 바뀌면 부서진다.

COVE는 두 채널을 조율한다.

## 분석: 왜 둘 중 하나만으로는 안 되는가

Lean 정리 증명(MiniF2F)에서 하네스 메모리를 늘려도 성공률 변화가 거의 없다. 에피소드 50→250, 검색 메모리 2→8개 — 컴파일 에러가 줄지 않는다. 메모리가 힌트를 주지만 모델이 실행할 역량이 부족하기 때문이다.

반대로 WikiTableQuestions에서 파라미터 학습 후 API 이름을 바꾸면 성공률이 40.5% → 16.5%로 추락한다. API 정답률도 96.5% → 54.0%. 표면 지식을 가중치에 박아넣었기 때문이다.

![](/images/2026-08-08-cove-memory-parameter-coordination-agent-self-evolution/fig-2-p3.png)

그림 2. Lean 하네스 진화: 메모리가 늘어도 성공률이 오르지 않는다.

## COVE 구조

![](/images/2026-08-08-cove-memory-parameter-coordination-agent-self-evolution/fig-5-p5.png)

그림 5. COVE 전체 구조. 태스크 피드백 → 라우터 → 스케줄러 → KnowledgePO.

세 가지 메커니즘이 있다:

1. Task-aware Router — 피드백을 읽고 어느 채널로 보낼지 정한다. 실패 원인이 "추론 역량 부족"이면 파라미터 채널, "표면 지식 부족"이면 하네스 채널. MATH는 이미 추론 능력이 충분해 대부분 하네스로 간다. TableQA는 반복 패턴이 많아 파라미터 비중이 높다.

2. Stage-aware Scheduler — 하네스 탐색이 plateau에 도달하면 파라미터 학습을 트리거한다. 항상 파라미터 학습을 켜는 것보다 plateau에서만 켜는 것이 더 높은 성공률을 보인다.

![](/images/2026-08-08-cove-memory-parameter-coordination-agent-self-evolution/fig-4-p3.png)

그림 4. Plateau 트리거가 always-on과 harness-only보다 낫다.

3. KnowledgePO — 지식을 휘발성/안정성/전략성으로 분류:
- 휘발성(API 이름, 스키마): 메모리에만 저장, 파라미터 학습 시 anti-recitation 페널티로 내재화 차단
- 안정성(알고리즘 패턴, 도메인 추론): 파라미터로 내재화
- 전략성(디버깅 계획): 메모리 유지, 반복 증거 쌓이면 내재화

## 결과

![](/images/2026-08-08-cove-memory-parameter-coordination-agent-self-evolution/table-2-p7.png)

표 2. 메인 결과. COVE는 파라미터 단독 대비 학습 토큰을 86% 줄이면서 전반적으로 더 낫다.

| 방법 | Lean4 | APPS | TableQA | HotpotQA | MATH | 하이브리드 |
|---|---|---|---|---|---|---|
| Base | 0.0 | 23.2 | 34.3 | 45.1 | 75.1 | 15.6 |
| Evo-Memory | 0.0 | 11.5 | 36.2 | 64.5 | 69.0 | 18.2 |
| Self-Challenging | 3.0 | 26.3 | 27.1 | 57.4 | 72.6 | 14.6 |
| Harness-only | 3.0 | 31.6 | 53.5 | 66.2 | 84.0 | 20.8 |
| Parametric-only | 6.2 | 33.1 | 47.0 | 69.4 | 91.6 | 21.3 |
| COVE | 7.0 | 33.4 | 50.0 | 69.6 | 91.7 | 24.1 |

라우터 ablation에서 COVE는 Always-Both 대비 토큰의 16%만 쓰면서 65.0 vs 69.0의 성능을 낸다. 효율(성능/토큰)은 28.83 vs 4.89.

## Anti-recitation 효과

API 이름을 바꿔서 테스트하면:
- 일반 fine-tuning: 성공률 급락, API 오류가 주요 실패 모드
- Anti-recitation 모델: 안정적, 현재 프롬프트의 API를 따라감

![](/images/2026-08-08-cove-memory-parameter-coordination-agent-self-evolution/fig-1-p2.png)

그림 1. 하네스 기반 진화(좌)는 메모리/스킬을 편집 가능하게 두고, 파라미터 기반 진화(우)는 가중치를 업데이트한다.

## 한계

- 베이스 모델 Qwen3-8B로만 실험. 더 큰 모델에서 라우팅 일관성 확인 필요.
- 5개 태스크로 평가. 더 다양한 환경(웹, 터미널, 코딩 에이전트)에서 검증 부족.
- 하네스와 파라미터 채널 사이의 지식 이전을 완전히 통제하는 것은 여전히 어렵다.

## 코드

- 익명 저장소: https://anonymous.4open.science/r/cove-8BCC/

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
