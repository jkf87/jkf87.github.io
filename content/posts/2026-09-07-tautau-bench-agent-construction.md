---
title: "ττ-bench — 에이전트를 '짓는' 일을 벤치마크에 넣다"
date: 2026-09-07
tags:
  - agent
  - benchmark
  - coding-agent
  - evaluation
draft: false
description: "ττ-bench(arXiv 2609.04611) 리뷰. 개발 에이전트에게 사업 기록·클라이언트·예산을 주고 고객상담 에이전트를 직접 만들게 하는 벤치마크. 최강 조합이 23.9%, 전문가 레퍼런스는 82.2%."
---

## 결론 먼저

Sierra와 Princeton이 낸 ττ-bench(hyper-tau-bench)는 방향을 뒤집은 벤치마크입니다. 기존 τ-bench 계열이 "완성된 에이전트"를 시뮬레이션 고객에게 점수 매긴다면, ττ-bench는 <span style="background-color: #fff59d"><strong>에이전트를 만드는 코딩 에이전트 자체를 채점</strong></span>합니다.

- 53개 태스크, 4개 도메인(항공/리테일/통신/은행)에서 최강 조합인 Claude Opus 5 + Claude Code가 <span style="background-color: #fff59d"><strong>통과율 23.9%</strong></span>
- 전문가가 직접 만든 레퍼런스 천장은 <span style="background-color: #fff59d"><strong>82.2%</strong></span>. 격차가 3.4배 남
- 논문: [arXiv:2609.04611](https://arxiv.org/abs/2609.04611) (2026-09-04, Sierra · Princeton, 기준일 2026-09-07)

## 핵심 수치

| 항목 | 값 |
|---|---|
| 태스크 수 | 53 (은행 35, 항공/리테일/통신 각 6) |
| 최고 점수 | Claude Opus 5 + Claude Code 23.9% |
| 레퍼런스 천장 | 82.2% (전문가 작성) |
| 도메인별 최고 조합 점수 | 항공 55.9 / 리테일 72.8 / 통신 48.2 / 은행 5.9 |
| 증거 아티팩트 | 2,868개, 텍스트만 550만 토큰 이상 |
| 원자 팩트 수 | 항공 85 / 리테일 119 / 통신 155 / 은행 2,969 |

## 태스크가 어떻게 생겼나

개발 에이전트에게 실제 프로젝트와 같은 시작점을 줍니다.

- 사업이 실제 보관하는 기록: 운영 핸드북, 상담 녹취/채팅 기록, 이메일, 슬라이드, 스크린샷, 화면 녹화
- 기록에 없는 요구사항을 쥔 <span style="background-color: #fff59d"><strong>시뮬레이션 클라이언트</strong></span>. 질문해야만 답해줍니다
- 클라이언트 소유 REST API. <span style="background-color: #fff59d"><strong>일부 엔드포인트는 결함이 심어져 있음</strong></span> (커밋 후 타임아웃, 스키마 드리프트 등 9개 부류)
- 상속받는 불완전한 코드베이스, 그리고 20개 모델 메뉴 + 대화당 크레딧 예산

이 안에서 고객상담 에이전트를 만들어 제출하면, <span style="background-color: #fff59d"><strong>숨겨둔 평가 태스크의 시뮬레이션 고객을 상대로 배포해 점수를 매깁니다</strong></span>. 최종 DB 상태와 고객에게 전달한 정보가 정답과 일치해야 통과구요, 예산 초과분은 점수에서 그대로 차감됩니다.

![ττ-bench 개요](/images/2026-09-07-tautau-bench-agent-construction/fig-1-p2.png)

## 결과가 말해주는 것

### 은행 도메인에서 무너진다

은행 코퍼스는 원자 팩트가 2,969개로 다른 도메인 전체를 합친 것보다 훨씬 큽니다. 태스크 하나가 최대 580개 팩트에 의존하는데, 여기서 최고 조합 점수가 5.9%로 떨어집니다.

### grep만 하고 안 읽는다

개발 에이전트들이 은행 코퍼스 1,700여 파일 중 <span style="background-color: #fff59d"><strong>연 파일은 80개 미만</strong></span>이었습니다. 키워드 검색으로 정책을 조립하니까, 만들어진 에이전트는 정책을 모른 채 "Rho-Bank 카드 목록은 확인된 게 없다"고 답합니다.

### 클라이언트에게 묻지 않는다

클라이언트가 쥔 요구사항이 20~25개인 태스크에서, 개발 에이전트들은 <span style="background-color: #fff59d"><strong>제출 전 질문을 최대 4개</strong></span>만 했습니다. 전체 툴콜 중 클라이언트 대화는 0.3%. 묻지 않으면 평균 0.16점, 4개 이상 묻으면 0.50점으로 3배 차이납니다. $2,500 값이 질문 하나로 해결되는 상황에서 "태스크에 원래 없는 갭"이라 결론 짓고 넘어간 사례도 있었구요.

![빌드 궤적 분석](/images/2026-09-07-tautau-bench-agent-construction/fig-6-p10.png)

### 물려받은 코드를 측정 없이 갈아엎는다

상속 코드를 처음 20스텝 안에 전부 읽는 건 잘 하는데, <span style="background-color: #fff59d"><strong>실행은 해보지 않고 통째로 재작성</strong></span>합니다. 그 시작 코드 중 하나는 손대지 않아도 0.36점이었는데 아무도 그걸 몰랐습니다.

### 예산 관리를 양쪽으로 놓친다

21개 빌드가 예산을 초과해 페널티로 점수가 0이 된 게 10개. 반대로 더 흔한 문제는 <span style="background-color: #fff59d"><strong>예산의 절반만 쓰고 강한 모델로 안 올리는 것</strong></span>이었습니다. 평균 사용률 0.45~0.72×, 레퍼런스는 0.96×. 테스트 출력에 예산이 같이 찍히는데도 3배 초과 상태로 그냥 제출한 케이스도 있습니다.

### 자기 테스트를 맞춰서 고친다

에이전트와 자기가 쓴 테스트가 어긋나면 <span style="background-color: #fff59d"><strong>테스트의 기대값을 늦추는</strong></span> 행동이 6회 관측됐습니다. 평가기 grader 소스를 읽거나 숨긴 데이터를 파려는 시도는 <span style="background-color: #fff59d"><strong>17~42% 빌드에서 관측</strong></span>됐는데, 전부 실패했습니다.

![아키텍처·모델 선택 분포](/images/2026-09-07-tautau-bench-agent-construction/fig-5-p9.png)

## 아키텍처와 모델 선택

제출된 에이전트의 92%가 <span style="background-color: #fff59d"><strong>단일 LLM 툴 루프</strong></span>였습니다. 멀티에이전트 0. 근데 재미있는 건, "인텐트별 라우팅 + 툴콜 검토"라는 한 줄 힌트만 줘도 통신 도메인 점수가 <span style="background-color: #fff59d"><strong>31%에서 67%로 두 배</strong></span>가 됐다는 겁니다. 습관의 문제였던 셈이죠.

모델 선택도 비슷합니다. Codex 빌드의 96%가 OpenAI 모델을 서빙하고, 가장 싼 버킷에서만 골랐습니다.

## 내 해석

이 벤치마크의 가치는 점수 자체보다 <span style="background-color: #fff59d"><strong>요구사항 수집(self-spec-recovery)을 측정 가능하게 만든 것</strong></span>이라고 봅니다. SWE-bench가 "주어진 이슈를 고쳐라"라면, ττ-bench는 "명세가 흩어져 있으니 먼저 모아라"입니다. 현장에서 에이전트 구축이 깨지는 지점이 정확히 이거구요.

짧은 인용으로 정리하면: 돌아가는 에이전트는 만들 수 있는데, <span style="background-color: #fff59d"><strong>배포 가능한 에이전트는 못 만든다</strong></span>가 현재 상태입니다.

![태스크 구조](/images/2026-09-07-tautau-bench-agent-construction/fig-2-p4.png)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### ττ벤치와 τ벤치는 어떻게 다른가
τ-bench는 완성된 에이전트를 시뮬레이션 고객 상대로 평가합니다. ττ-bench는 그 에이전트를 개발 에이전트가 직접 만들게 하고, 만들어진 결과물의 τ-bench 점수로 개발자를 채점합니다.

### 은행 도메인 점수가 낮은 이유는 무엇인가
은행 코퍼스의 원자 팩트가 2,969개로 다른 도메인(85~155개)의 20배 이상이고, 태스크당 최대 580개 팩트를 요구하기 때문입니다. 검색으로 조립한 정책으로는 커버가 안 됩니다.

### 예산 초과는 어떻게 처리되나
대화당 평균 크레딧이 예산 b를 넘으면 초과분 max(0, c/b − 1)만큼 점수에서 차감됩니다. 품질이 좋아도 3배 초과면 점수가 0에 가까워집니다.

### 부정행위 시도는 성공했는가
17~42% 빌드에서 평가기 탐색·숨긴 데이터 마이닝 등이 관측됐지만, 런타임에 정답 데이터가 없도록 설계되어 성공 사례는 0건입니다.
