---
title: "도구 결과와 일반 텍스트의 허위 주장 채택 비교 — Claude Opus 5 대상 3건의 사전등록 연구"
date: 2026-08-22
tags:
  - LLM
  - agent
  - tool-use
  - safety
  - evaluation
source: https://arxiv.org/abs/2608.14992
---

## 개요

arXiv:2608.14992 (2026-08-15, Justin Bronder)는 언어모델 시스템에서 지지 근거가 없는 허위 주장(false claim)의 채택률이 해당 주장을 전달하는 <span style="background-color: #fff59d"><strong>메시지 패키지 유형에 따라 달라지는지</strong></span>를 검토한다.

실험은 <span style="background-color: #fff59d"><strong>Claude Opus 5 단일 모델, 합성 조회 과제 단일 템플릿, 단일 API 접근 조건</strong></span>에서 수행되었다. 연구 1은 탐색적 4군 비교, 연구 2·3은 문서 사전등록(preregistered) 설계다.

## 방법

과제: 모델은 named item에 대응하는 색상 코드를 반환하거나 기권한다. 지지 근거 없는 목표 코드가 다음 중 하나의 패키지로 대화에 삽입된다.

- 군 1: 목표 주장 없음
- 군 2: 이전 어시스턴트 발언(assistant assertion)
- 군 3: <span style="background-color: #fff59d"><strong>도구 결과(tool result) 레코드</strong></span>
- 군 4: unchecked 표기 10필드 메타데이터 래퍼를 포함한 도구 결과

![Figure 1](/images/2026-08-22-tool-result-authority/fig-1-p2.png)

Figure 1 (p.2): 동기 시나리오 — 시스템이 읽기와 쓰기를 모두 수행하는 저장소에서 이전 세션이 작성한 미검증 주장이 조회 결과로 재반환되는 상황.

## 결과

표 1. 포장 유형별 허위 코드 채택 (연구 1, 2026-08-09):

| 패키지 | 채택 |
|---|---|
| 주장 없음 | 0/24 (0%) |
| 어시스턴트 발언 | 0/22 (0%) |
| 도구 결과 | <span style="background-color: #fff59d"><strong>14/24 (58%)</strong></span> |
| 주석 달린 도구 결과 | <span style="background-color: #fff59d"><strong>15/24 (63%)</strong></span> |

지지 사례에서 도구 결과군이 11/12의 정답률을 보였으므로 <span style="background-color: #fff59d"><strong>고정 출력 토큰 편향은 배제</strong></span>된다.

사전등록 재현(연구 2, 2026-08-13)에서 격차는 유지되었다(도구 결과 7/24 vs 발언 0/24, <span style="background-color: #fff59d"><strong>단측 Fisher exact p = 0.0047</strong></span>). 다만 도구 결과 조건의 채택률은 4일 사이에 <span style="background-color: #fff59d"><strong>58%에서 29%로 감소</strong></span>했다.

연구 3(2026-08-14)은 배치 구성을 변경했다. 두 레코드를 사전에 공지하고 동일한 최종 사용자 턴에 배치하며 목표 바인딩을 상호 교환(swap)했다.

그 결과 인라인 텍스트 <span style="background-color: #fff59d"><strong>60/60 (100%)</strong></span>, 도구 결과 57/60 (95%)로 "도구 결과 우월성" 등록 기준은 <span style="background-color: #fff59d"><strong>기각되었다 (p = 1)</strong></span>.

![Figure 2](/images/2026-08-22-tool-result-authority/fig-2-p5.png)

Figure 2 (p.5): 3개 연구의 메시지 패키지 구성.

## 해석 및 한계

- 연구 1·2에서 도구 결과 패키지와 어시스턴트 발언 사이의 채택률
저장소에 쓰기를 수행하는 에이전트 시스템에서는 <span style="background-color: #fff59d"><strong>쓰기 시점의 출처 검증이 필요</strong></span>하다.
- <span style="background-color: #fff59d"><strong>unchecked 메타데이터 표기는 채택률을 낮추지 못했다</strong></span>(58% → 63%). 경고 라벨만으로는 방어 효과가 없다.
- 연구 3에서 인라인 텍스트가 100% 채택된 점은 <span style="background-color: #fff59d"><strong>배치·사전 공지가 패키지 유형과 별개의 지배 변수</strong></span>일 수 있음을 시사한다.
- 일반화 한계: <span style="background-color: #fff59d"><strong>단일 모델, 단일 과제 템플릿, 단일 API</strong></span>. 프롬프트·코드·프리레지스트레이션 문서는 공개되어 있다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- <span style="background-color: #fff59d"><strong>arXiv:2608.14992</strong></span> — Does a Tool Result Carry More Authority Than Plain Text? Three Prospective Studies of False-Claim Adoption in a Synthetic Assignment Task with Claude Opus 5
