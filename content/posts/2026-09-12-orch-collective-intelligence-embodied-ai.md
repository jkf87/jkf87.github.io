---
title: "ORCH - 조직론으로 50개 로봇을 움직이는 에이전트 팀 구성법"
date: 2026-09-12
tags:
  - agent
  - multi-agent
  - organization
  - embodied-ai
  - LLM
  - coordination
draft: false
description: ORCH 논문 정리. 인간 조직론의 역할·계층·상호의존성 원리를 코드화해 최대 50대 이형 로봇의 산불 대응 팀을 구성했고, 기존 4개 멀티에이전트 프레임워크 대비 최종 점수 64%, 실행 효율 74% 향상을 확인했습니다.
---

## 결론 먼저

ORCH(Organizing Roles and Coordination Hierarchies)는 산불 대응에 50대의 이형(heterogeneous) 에이전트를 쓸 때, 정찰·구조·운송·진압 각각에 맞는 조직 구조를 LLM이 자동으로 만들어주는 프레임워크입니다. 핵심은 이겁니다.

- <span style="background-color: #fff59d"><strong>사람이 설계한 ORCH 조직이 기존 4개 프레임워크 대비 최종 점수 63.97%, 실행 효율 74.29% 향상</strong></span> (기준일: 2026-09-12, arXiv v1)
- <span style="background-color: #fff59d"><strong>LLM이 자동 생성한 조직도 점수 43.63%, 효율 52.53% 향상</strong></span>
- <span style="background-color: #fff59d"><strong>집단 성능은 모델 스케일이 커진다고 단조 증가하지 않음</strong></span>

<span style="background-color: #fff59d"><strong>25개 산불 대응 미션, 에이전트 최대 50대, 8개 LLM에서 재현된 결과</strong></span>입니다.

## 핵심 수치 요약

| 항목 | 값 |
| --- | --- |
| 태스크 | 25개 CREW-Wildfire 미션 (정찰/구조/운송/자원/봉쇄/진압) |
| 팀 규모 | 최대 50대 이형 에이전트 |
| 평가 LLM | 8개 (모델 공개 논문 표 참조) |
| 인간 설계 ORCH vs 기존 4개 프레임워크 | 점수 +63.97%, 효율 +74.29% |
| LLM 자동 생성 ORCH | 점수 +43.63%, 효율 +52.53% |
| 일관성 | 미션·LLM 변경에도 우위 유지 |

논문: [arXiv:2609.11737](https://arxiv.org/abs/2609.11737) · 저자: Zhengran Ji, Jonathan Hyun, Boyuan Chen (Duke University) · 2026-09-12 v1

## 방법 전체 구조

Figure 1이 프레임워크 전체를 보여줍니다. 태스크 설명을 받으면 팀 계층과 역할을 구성하고, 미션 단계별로 조정합니다.

![Figure 1: Method Overall](/images/2026-09-12-orch-collective-intelligence-embodied-ai/fig-1-p3.png)
*Figure 1. 태스크 기반 계층 설계와 조정 구조 전체 그림 (논문 p.3)*

## 핵심 개념 두 가지

### 상호의존성(interdependence)을 타입으로 나눔

ORCH는 인간 조직론의 상호의존성 개념을 그대로 가져옵니다.

- <span style="background-color: #fff59d"><strong>pooled interdependence(집합적): 순서 제약 없이 병렬로 진행 가능한 작업. 정찰 여러 구역 동시 수사 같은 것.</strong></span>
- <span style="background-color: #fff59d"><strong>sequential interdependence(순차적): 선행 작업이 끝나야 다음 작업이 가능. 정찰 결과가 있어야 구조 계획을 세우는 것.</strong></span>

병렬로 될 일은 병렬로 돌리고, 순서가 필요한 일만 계층으로 묶어 조정합니다. 이게 성능 차이의 뼈대입니다.

### 역할(role)과 계층(hierarchy)을 태스크에 맞춰 생성

역할은 태스크 요구사항에서 도출되고, 계층은 상호의존성 구조에서 나옵니다. 사람이 직접 설계할 수도 있고, <span style="background-color: #fff59d"><strong>LLM에 태스크 설명을 주고 조직을 생성하게 할 수도 있습니다</strong></span>. 자동 생성 조직이 인간 설계보다는 낮지만 기존 프레임워크보다는 크게 앞섭니다.

## 결과

![Figure 2: Aggregated Performance](/images/2026-09-12-orch-collective-intelligence-embodied-ai/fig-2-p13.png)
*Figure 2. 25개 태스크에서 프레임워크별 통합 성능 (논문 p.13)*

![Figure 3: Performance by LLM](/images/2026-09-12-orch-collective-intelligence-embodied-ai/fig-3-p16.png)
*Figure 3. LLM별로 나눈 통합 성능 (논문 p.16)*

Figure 3이 흥미로운 지점입니다. <span style="background-color: #fff59d"><strong>어느 LLM을 쓰든 ORCH가 우위를 유지</strong></span>하면서, 동시에 <span style="background-color: #fff59d"><strong>모델 스케일을 키워도 팀 성능이 항상 오르지는 않는다</strong></span>는 게 드러납니다. 병목이 개별 에이전트 능력에 있지 않고 조직 구조에 있는 구간이 존재한다는 뜻입니다.

![Figure 5: Ablation](/images/2026-09-12-orch-collective-intelligence-embodied-ai/fig-5-p20.png)
*Figure 5. 조직 설계·계층 분석 어블레이션 (논문 p.20)*

어블레이션에서 조직 설계 요소를 빼면 성능이 떨어집니다. 우연이 아니라 조직 구조 자체의 기여입니다.

![Figure 6: Team Hierarchy Generation](/images/2026-09-12-orch-collective-intelligence-embodied-ai/fig-6-p21.png)
*Figure 6. 인간 전문가 계층과 LLM 생성 계층 비교 (논문 p.21)*

## 왜 이 결과가 나오나: 장기 미션 분석

긴 미션에서 ORCH 조직은 <span style="background-color: #fff59d"><strong>전문 그룹 내부의 병렬 활동을 유지하면서도 미션 단계 전환 시 순서 있는 조정을 수행</strong></span>합니다. <span style="background-color: #fff59d"><strong>그룹 안에서는 자율적으로 돌고, 단계가 바뀔 때만 상위 계층이 개입하는 구조</strong></span>입니다. 이게 효율 차이(+74%)의 직접 원인으로 분석됩니다.

## 나의 해석 (원문 근거와 구분)

- 원문 주장: <span style="background-color: #fff59d"><strong>조직 원리를 코드화하면 이형 로봇 50대 규모에서도 일관된 성능 향상이 있다</strong></span>.
- 내 해석: "멀티에이전트 시스템의 상한을 정하는 요소가 조직 구조 쪽에 있다"는 방향성 증거로 읽을 수 있습니다. 다만 <span style="background-color: #fff59d"><strong>25개 미션이 모두 산불 대응 도메인(CREW-Wildfire)이라는 점은 한계</strong></span>입니다. 다른 도메인에서 상호의존성 타입 분류가 같은 효과를 낼지는 후속 검증이 필요합니다.

## 코드와 재현

논문 페이지에 코드 공개 여부는 v1 기준 확인이 필요합니다. 재현하려면 CREW-Wildfire 환경과 8개 LLM 접근이 전제입니다.

## 더 실습해보고 싶은 분들께

멀티에이전트 조직 설계를 실습하려면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### ORCH가 자동으로 하는 일은 무엇인가
사람이 팀 계층을 설계하는 대신, 태스크 설명을 넣으면 LLM이 역할·계층·조정 구조를 생성합니다. 사람이 설계하면 더 좋지만 자동 생성도 기존 프레임워크보다 낫습니다.

### 기존 프레임워크 대비 얼마나 좋아지는지
25개 산불 미션 기준으로 사람 설계 ORCH는 점수 63.97%, 실행 효율 74.29% 향상입니다. LLM 자동 생성은 43.63% / 52.53% 향상입니다.

### 왜 모델 스케일만 키우면 팀 성능이 오르지 않는지
아니요. 논문은 집단 성능이 모델 스케일에 단조 증가하지 않는다는 걸 관찰했습니다. 조직 구조가 더 중요한 경우가 있습니다.

### 평가 도메인의 한계와 그 이유
평가는 CREW-Wildfire 25개 미션으로 한정됩니다. 방법 자체는 도메인 독립을 목표로 하고, 타 도메인 검증은 후속 과제입니다.

### pooled와 sequential interdependence 차이는 무엇인가
pooled는 순서 제약 없이 병렬 실행 가능한 작업 묶음이고, sequential은 선행 결과가 필요한 작업 묶음입니다. ORCH는 병렬은 그대로 두고 순차만 계층으로 조정합니다.
