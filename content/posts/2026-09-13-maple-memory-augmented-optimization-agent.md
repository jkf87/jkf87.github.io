---
title: "MAPLE: 최적화 에이전트에 상태 메모리를 넣어 연속 변경 요청을 처리하는 방법 (arXiv 2609.11636)"
date: 2026-09-13
tags:
  - agent
  - llm
  - optimization
  - arxiv
draft: false
description: "LLM 최적화 에이전트를 한 번짜리 요청에서 벗어나게 만든 MAPLE 논문 정리. Live State Memory와 타입 기반 TSS 워크벤치로 180개 연속 업데이트를 처리한 구조와 수치를 정리했습니다."
---

## 결론 먼저

MAPLE은 자연어 최적화 요청을 한 번 처리하고 끝내는 기존 LLM 에이전트와 달리, <span style="background-color: #fff59d"><strong>최적화 프로그램·수락된 계획·과거 업데이트·후보 해를 상태로 계속 들고 있으면서 연속 수정 요청을 처리하는 에이전트</strong></span>다.

논문이 직접 만든 NLDO 벤치마크(15 트라젝토리, 180 업데이트)에서 <span style="background-color: #fff59d"><strong>전 트라젝토리 완주, 동적 단일목표 온라인 품질 0.951, 다목표 하이퍼볼륨 비율 0.875</strong></span>를 기록했다. 같은 동적 설정에서 Persistent ReAct는 0.501 / 0.042였다.

핵심은 두 가지다.

- Live State Memory로 이전 결정을 보존하고 참조 해석
- TSS 워크벤치로 LLM이 직접 짜는 코드의 실패 면적을 축소

| 항목 | 값 |
| --- | --- |
| 논문 | MAPLE: Memory-Augmented Planning with Language and Evolution (arXiv 2609.11636) |
| 소속 | Harbin Institute of Technology, Shenzhen |
| 제출일 | 2026-09-10 (v1) |
| 벤치마크 | NLDO: 15 트라젝토리, 180 업데이트 |
| 도메인 | 선택, 스케줄링, 로스터링, 라우팅, 클라우드 자원 배치 |
| 동적 단일목표 품질 | 0.951 (strict) |
| 동적 다목표 HV | 0.875 |
| 비교 Persistent ReAct | 0.501 / 0.042 |
| 트라젝토리당 토큰 | 51.6k (TSS 사용 시) |
| 코드 | github.com/xin8coder/MAPLE |

기준일: 2026-09-13, arXiv v1 기준.

## 문제: 한 번 만들고 끝나는 최적화 에이전트

OptiMUS, ORLM, OR-LLM-Agent 같은 기존 LLM 최적화 에이전트는 자연어를 모델이나 솔버 코드로 바꿔 실행하는 데는 강하다.

근데 현실 운영은 동적이다. 신규 주문이 들어오고, 차량이 빠지고, 우선순위가 바뀐다. 이때 필요한 건 이전 상태와의 연속성이다.

구체적으로는 이 세 가지다.

- 앞서 정한 특정 고객의 차량 배정을 유지
- 과거 탐색에서 나온 유용한 후보 해를 재사용
- 데이터·제약·목적 함수가 바뀌어도 기존 결정과 모순되지 않게 수정

논문 표현으로는 <span style="background-color: #fff59d"><strong>"isolated requests 중심 방법은 이전 결정을 보존하고 탐색 결과를 재사용하는 빠른 적응을 지원하지 못한다"</strong></span>는 것. 매번 처음부터 다시 만드는 방식은 이 세 가지가 안 된다.

## 구조: TSS 워크벤치 + Live State Memory

![MAPLE 전체 구조](/images/2026-09-13-maple-memory-augmented-optimization-agent/fig1-framework.png)

MAPLE의 파이프라인은 이렇게 흘러간다.

1. 자연어 요청 + 공개 테이블 입력
2. LLM이 TSS 워크벤치 함수 작성 (`build_problem()`, `evaluate()`)
3. 고정된 솔버가 실행 (LP/MILP, GA, NSGA-II)
4. 후속 요청이 오면 LPD가 변경 지점을 특정
5. LSM이 과거 이벤트·수락된 계획과 바인딩
6. 재시작 선택기가 Warm/Full 판단, 고정 증거 게이트가 검증

### TSS 워크벤치

LLM이 전부 손으로 짜는 대신, 결정 세그먼트에 타입(assignment, permutation, 실수 벡터)을 선언하면 <span style="background-color: #fff59d"><strong>초기화·교차·변이·리페어 연산자가 타입에 맞게 고정 바인딩</strong></span>된다.

솔버 선택도 선언된 공식이 결정한다. 선형이면 LP/MILP, 조합·비선형 스칼라면 GA, 다목표면 NSGA-II.

LLM이 작성하는 건 두 함수뿐이다. 나머지 실행 로직은 고정 절차다.

### LPD: 변경 위치 특정

LPD(Locate Requested Change)는 업데이트 요청을 읽고 데이터 테이블, 결정 선언, 평가 로직 중 어디가 바뀌어야 하는지 찾는다.

가격 변경이면 테이블만, 새 제약이면 `evaluate()` 편집이 필요한 식이다. <span style="background-color: #fff59d"><strong>LPD가 제안한 편집과 실제 저장된 편집은 180개 업데이트 중 170개에서 일치</strong></span>했다.

### LSM: 과거 바인딩

LSM(Live State Memory)은 이벤트, 수락된 결정, 탐색 후보를 저장한다.

"혼잡 노트에서 언급된 고객의 차량 배정을 유지하라" 같은 요청이 오면 이벤트에서 고객을 찾고, 수락된 계획에서 차량을 꺼내 검색 중 강제한다.

<span style="background-color: #fff59d"><strong>참조 3단계를 거쳐야 하는 요청 포함 30/30을 해석했고, 18/18 배정 유지 요청도 정확히 강제</strong></span>됐다.

### 재시작 선택기

![업데이트 처리 흐름](/images/2026-09-13-maple-memory-augmented-optimization-agent/fig3-update-flow.png)

업데이트마다 Warm(이전 개체군 절반까지 그리디 리페어 후 재평가, 나머지는 신규)과 Full(전면 재시작) 중 선택한다.

LLM이 재사용 위험을 평가해 제안하면 <span style="background-color: #fff59d"><strong>고정 증거 게이트가 인용된 변경 사항을 알고리즘으로 검증</strong></span>해서 최종 결정한다.

컴파일·계약·스모크 테스트에 실패하면 유한 횟수(B회)까지 LLM 리페어를 시도한다. 그래도 유효하지 않으면 업데이트를 거부하고 이전 상태를 유지한다.

## NLDO 결과 수치

### 동적 설정이 본 게임

| 방법 | 단일목표 solve rate | strict 품질 | 다목표 solve rate | HV |
| --- | --- | --- | --- | --- |
| MAPLE | 100% | 0.951 | 100% | 0.875 |
| Persistent ReAct* | 51.3% | 0.501 | 11.5% | 0.042 |
| OptiMUS* | 28.2% | 0.281 | 12.8% | 0.084 |
| ORLM* | 12.0% | 0.120 | 0% | 0.000 |
| OptimAI* | 7.7% | 0.077 | 11.5% | 0.051 |
| OR-LLM-Agent* | 11.1% | 0.111 | 12.8% | 0.046 |

*는 논문이 동적 설정용으로 적응시킨 베이스라인.

Persistent ReAct의 0.501이 0.763까지 오르는 계산이 하나 있다. 보조 필드 누락으로 출력 검사에 걸린 7개 스칼라 트라젝토리를 수학적으로 유효하면 수용하는 프로토콜이다. MAPLE은 두 프로토콜에서 점수가 같다.

### 정적 설정에선 만능이 아니다

| 방법 | NLP4LP-hard (Obj.) | BWOR20 (Obj.) | NLDO-SS | NLDO-SM |
| --- | --- | --- | --- | --- |
| MAPLE | 59.3% | 80.0% | 1.000 | 0.832 |
| OptiMUS | 69.5% | 65.0% | 0.889* | 0.417* |
| Persistent ReAct | 62.7% | 70.0% | 0.889* | 0.259* |
| ReAct | 57.6% | 70.0% | 0.889* | 0.300* |

<span style="background-color: #fff59d"><strong>정적 단발 모델링인 NLP4LP-hard에선 OptiMUS(69.5%)가 MAPLE(59.3%)보다 높다</strong></span>. MAPLE의 이득은 연속 갱신 상황에 특화되어 있다는 걸 숫자가 그대로 보여준다.

## 절제 연구: 무엇이 유효성을 지키나

![재시작 전략별 HV 변화](/images/2026-09-13-maple-memory-augmented-optimization-agent/fig5-restart-hv.png)

| 구성 | Feasible | HV | IGD |
| --- | --- | --- | --- |
| MAPLE | 100.0% | 0.879 | 0.079 |
| Always Warm | 100.0% | 0.868 | 0.091 |
| Always Full | 100.0% | 0.824 | 0.111 |
| TSS 제거 | 80.6% | 0.665 | 0.143 |

TSS를 빼면 LLM이 직접 짠 코드에서 사고가 난다. 720개 결과 중 140개가 무효가 됐다.

원인도 구체적이다. <span style="background-color: #fff59d"><strong>"차량이 경로 하나만 담당한다"는 검사가 빠지고, GPU 비호환 배치를 걸러내지 못했다</strong></span>. 스캐폴딩이 유효성의 핵심이라는 근거다.

재시작 선택도 의미가 있다. 앞선 10개 업데이트에선 MAPLE과 Always Warm이 동점(0.915)인데, 과제 대부분이 바뀌는 마지막 2개 업데이트에서 MAPLE은 Full을 골라 0.696, Always Warm은 0.636.

<span style="background-color: #fff59d"><strong>파괴적 변경 직전엔 재사용, 이후엔 재시작</strong></span>이라는 타이밍 판단이 게인을 만든다. 다만 에피소드 평균 게인은 0.010, 95% 신뢰구간 [0.001, 0.021], 부호검정 p=0.219라서 통계적 유의성은 약하다.

## 토큰 비용과 다른 모델

프로그램 생성·편집·리페어 토큰을 세면 <span style="background-color: #fff59d"><strong>트라젝토리당 51.6k</strong></span>. TSS 없이 전부 LLM이 짜면 72.8k로 늘어난다. 스캐폴딩이 품질과 비용을 동시에 잡는 셈.

다른 모델로 Kimi k2.7을 돌린 풀 벤치마크에서는 스칼라 solve rate 100% / 품질 0.937, 파레토 92.3% / HV 0.766. 메인 모델 대비 소폭 하락했다. 그래도 구조 자체는 모델을 갈아끼워도 유지된다.

## 한계와 내 해석

원문 근거로 확인되는 한계:

- 정적 단발 벤치마크(NLP4LP-hard)에선 베이스라인 OptiMUS에 뒤진다
- NLDO가 합성 데이터 기반 벤치마크다 (논문 Ethics 항목에 명시)
- 재시작 선택의 평균 게인은 유의수준에서 애매하다 (p=0.219)

내 해석은 이렇다. 이 논문의 기여는 <span style="background-color: #fff59d"><strong>상태를 유지하는 실행 구조 + 코드 생성 면적을 줄이는 타입 시스템</strong></span> 조합이다. "더 똑똑한 LLM"은 이 논문의 핵심이 아니다.

하네스·루프 설계 관점에서 그대로 벤치마킹할 만한 패턴이 여럿 있다. 고정 증거 게이트로 LLM 제안을 검증한다는 설계, 무효 출력엔 상태 롤백한다는 규칙이 특히 그렇다.

## 더 실습해보고 싶은 분들께

LLM 에이전트 하네스·루프 설계가 궁금하다면:

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### MAPLE과 기존 OR-LLM-Agent는 어떻게 다른가

기존 방식은 요청 하나를 모델로 바꿔 실행하고 끝냅니다. MAPLE은 프로그램·수락 계획·이벤트·후보 해를 상태로 유지해서, "그 고객 차량 유지" 같은 과거 참조 요청과 후보 해 재사용이 가능합니다.

### NLDO 벤치마크는 어떻게 구성되어 있나

선택, 스케줄링, 로스터링, 라우팅, 클라우드 자원 배치 5개 도메인에서 15개 트라젝토리, 총 180개 업데이트로 구성된 합성 벤치마크입니다.

### Warm과 Full 재시작을 고르는 방법

LLM이 변경 요약과 히스토리로 재사용 위험을 평가해 제안하면, 고정 증거 게이트가 인용된 변경을 검증해 최종 결정합니다. 파괴적 변경 땐 Full, 그 외엔 Warm이 유리했습니다.

### TSS를 빼면 어떻게 되나

Pareto 업데이트에서 실행 가능률이 100%에서 80.6%로 떨어지고, 평균 HV가 0.879에서 0.665로 하락합니다. 누락된 제약 검사로 720개 중 140개가 무효 출력이 됩니다.
