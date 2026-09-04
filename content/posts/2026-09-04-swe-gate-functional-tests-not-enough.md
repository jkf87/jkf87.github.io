---
title: "SWE-Gate: 코딩 에이전트는 테스트를 통과해도 코드 리뷰에서 떨어진다"
date: 2026-09-04
draft: false
tags: [agent, SWE-bench, benchmark, code-review, evaluation, LLM]
description: "arXiv 2609.04167 SWE-Gate 요약. 기능 테스트 통과 패치 644개 중 221개(34.3%)가 리뷰 제약 위반. 벤치마크 구성, 모델별 성능, 카테고리별 난이도 정리."
---

## 결론 먼저

SWE-Gate(arXiv:2609.04167)는 리포지터리 수준 소프트웨어 엔지니어링 에이전트를 평가하는 벤치마크이다. 기존 벤치마크와 달리 기능 테스트 통과 여부와 리뷰 제약 준수 여부를 분리하여 측정한다. 핵심 결과만 먼저 적으면 다음과 같다.

- 기능 테스트를 통과한 644개 패치 중 <span style="background-color: #fff59d"><strong>221개(34.3%)가 리뷰 제약 위반으로 실패</strong></span>했다(기준일 2026-09-04, v1 논문 보고값).
- 제약 설명을 프롬프트에 넣으면 4개 모델 모두 조인트 성공률이 올라간다. GPT-5.5는 JSR이 41.3%에서 <span style="background-color: #fff59d"><strong>52.8%</strong></span>로 상승.

| 항목 | 값 |
| --- | --- |
| 수리 인스턴스 | 303개 |
| 대상 리포지터리 | Python 오픈소스 75개 |
| 평가 모델 | GPT-5.5, DeepSeek-V4-Flash, GPT-5.4-mini, GPT-4o-mini |
| 기능 테스트 통과 패치 | 644개 |
| 이 중 리뷰 제약 위반 | 221개 (34.3%) |
| GPT-5.5 FSR / CFR / JSR | 74.9% / 70.5% / 52.8% |
| Hidden Failure Rate 범위 | 29.5% ~ 53.6% |

## 벤치마크 구성

- 데이터셋: Python 오픈소스 리포지터리 75개에서 추출한 303개 수리 인스턴스
- 각 인스턴스 구성 요소: 이슈 설명, 기능 테스트 스위트, 제약 테스트 스위트, non-compliant 패치, gold 패치
- 리뷰 제약은 실제 PR 리뷰 코멘트에서 추출하여 실행 가능한 테스트로 변환한다
- 검증 행렬: 원본 리포지터리는 기능 테스트를 통과하고 변이 리포지터리는 실패하는 fail-to-pass 조건을 만족해야 한다

![SWE-Gate 구성 파이프라인](/images/2026-09-04-swe-gate-functional-tests-not-enough/fig-1-p3.png)

![인스턴스 스키마](/images/2026-09-04-swe-gate-functional-tests-not-enough/fig-2-p3.png)

<span style="background-color: #fff59d"><strong>하나의 인스턴스에서 기능 테스트와 제약 테스트가 분리 실행</strong></span>되므로 이슈 해결 능력과 리뷰 제약 준수 능력을 따로 측정할 수 있다.

## 실험 설정

4개 LLM 백엔드(GPT-5.5, DeepSeek-V4-Flash, GPT-5.4-mini, GPT-4o-mini)를 공통 코딩 에이전트 스캐폴드 하에서 평가하였다. 제약 제공(+C)과 제약 생략(-C) 두 조건을 비교했다.

## 결과

GPT-5.5는 227개 패치를 기능 테스트에서 통과시켰고 그중 160개만 제약 검증까지 통과했다. <span style="background-color: #fff59d"><strong>기능 성공 패치의 29.5%가 제약을 위반</strong></span>했다. 약한 모델일수록 심해서 GPT-4o-mini의 HFR은 53.6%이다.

논문은 이런 패치를 hidden failure라고 부른다. 기능 테스트만 보는 평가 프로토콜에서 성공으로 세어지는 실패라서 붙은 이름이다.

제약 설명 제공 시 조인트 성공 수는 <span style="background-color: #fff59d"><strong>360개에서 423개로 증가</strong></span>했다. 다만 일부 모델에서 기능 성공률이 소폭 하락했다. 제약을 챙기느라 수정 폭이 커지면 기능 수정 자체를 놓치는 트레이드오프가 있다는 결과다.

## 카테고리별 난이도

| 제약 카테고리 | CFR 특징 |
| --- | --- |
| Scope Generalization | 46.3~63.0%, 가장 어려움 |
| Lifecycle Cleanup / Resource | 53.8~62.5% |
| Encoding / Escaping / Quoting | 51.1~55.9% (일부 모델) |
| Missing vs Empty / Sentinel | 74.2~81.6%, 상대적으로 쉬움 |
| Ordering / Argument Preservation | 75.0~79.6% |

<span style="background-color: #fff59d"><strong>실패 지점 근처만 고치는 좁은 패치는 범위 일반화나 리소스 라이프사이클 요구를 놓친다</strong></span>. 리뷰어가 전체 호출 경로의 정리를 요구할 때 에이전트는 문제 지점만 손대는 경향이 있다는 해석이다.

## 내 해석과 한계

- 원문 주장: 기능 단독 평가는 리포지터리 수준 수리 능력을 과대평가한다(초록, RQ1).
- 원문 주장: 제약 제공은 전 모델에서 JSR과 CFR을 올린다(RQ2).
- 내 해석: 이건 벤치마크 개선이라기보다 평가 계층 추가에 가깝다. 리뷰 반려 사유를 테스트로 컴파일하는 파이프라인이 이미 존재한다는 점이 핵심이다.
- 내 해석: 에이전트 운영 입장에서는 PR 리뷰 코멘트 히스토리를 하네스 컨텍스트에 넣어줄 근거가 된다. +C 조건에서 성적이 오른다는 건 모델이 제약을 못 지키는 게 아니라 모르고 지키지 못한다는 뜻이다.
- 주의점: 303개 인스턴스는 Python 리포지터리로 한정된다. 다른 언어와 리뷰 문화에서 같은 HFR이 나온다는 보장은 없다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 평가 루프를 직접 다루고 싶다면 아래 두 개를 추천한다.

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### SWE-Gate가 기존 SWE-bench와 다른 점은 무엇인가요?
기능 테스트 통과 여부에 더해, 실제 PR 리뷰 코멘트에서 파생한 제약 테스트를 별도로 실행해서 조인트 판정을 내립니다.

### Hidden Failure Rate(HFR)이 무슨 뜻인가요?
기능 테스트는 통과했지만 제약 검증에 실패한 패치의 비율입니다. 이번 실험에서는 모델별 29.5%~53.6%였습니다.

### 제약을 프롬프트에 넣어주면 무조건 좋아지나요?
조인트 성공률과 제약 준수율은 전 모델에서 올라갔습니다. 대신 일부 모델의 기능 성공률은 소폭 하락했습니다.

### 소스코드와 데이터는 어디서 볼 수 있나요?
GitHub 저장소(https://github.com/DeepSoftwareAnalytics/SWE-Gate)에서 코드, 데이터, 실험 결과를 공개했습니다.

## 출처

- 논문: SWE-Gate: Passing Functional Tests Is Not Enough for Software Engineering Agents (arXiv:2609.04167v1, 2026-09-03)
- 코드: https://github.com/DeepSoftwareAnalytics/SWE-Gate
- 기준일: 2026-09-04. 수치는 모두 v1 논문 보고값이다.
