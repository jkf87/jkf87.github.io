---
title: "LLM 에이전트로 수학 연구를 끝내려면: Stellar Colosseum 하네스 논문 정리"
date: 2026-09-15
tags:
  - agent
  - harness
  - benchmark
  - LLM
draft: false
description: "Gemini 3.1 Pro 기반 다중 에이전트 하네스 Stellar Colosseum이 연구급 정리 증명 TCS-Bench 71.0%, Codeforces 222문제 중 218문제를 푼 방식을 정리했습니다. 5단계 파이프라인과 반증 기반 트리 집계 구조를 중심으로 설명합니다."
---

## 결론 먼저

Stellar Colosseum(arXiv 2609.15983, Google Research, 2026-09-14 공개)은 LLM 하나로 긴 수학 증명을 만들지 않고 <span style="background-color: #fff59d"><strong>전략 탐색 → 준비 게이트 → 증명 분해 → 부분문제 병렬 해결 → 전역 검증</strong></span>의 5단계 하네스로 연구를 나눠서 끝냅니다.

기준일(2026-09-15) v1 기준 결과는 다음 표와 같습니다.

| 항목 | 결과 | 조건 |
|---|---|---|
| TCS-Bench (300문제) | <span style="background-color: #fff59d"><strong>71.0%</strong></span> | Gemini 3.1 Pro + 3.7 Flash 교차 선택 |
| Gemini 3.1 Pro 직접 평가 | 30.3% | 단일 모델 기준 |
| GPT-5.6 Pro (max) 직접 평가 | 68.0% | 단일 모델 기준 |
| Colosseum 단일 실행 | 54.0% (Pro) / 55.0% (Flash) | 개별 실행 |
| Oracle best-of-two | 77.3% | 상한값, 달성 불가 규칙 |
| Codeforces 222문제 | <span style="background-color: #fff59d"><strong>218문제 통과</strong></span> | 실행 피드백 포함, 성능 레이팅 4263 |
| 실행 프로브 없음 대조 | 213문제, 3918 | 같은 평가, 다른 구성 |

차이의 원천은 구조입니다. <span style="background-color: #fff59d"><strong>증명을 섹션 의존 그래프로 쪼개고 검증 피드백을 해당 위치로 되돌리는 구조</strong></span>가 성적을 끌어올렸습니다.

## 왜 긴 증명이 어려운가

짧은 증명은 LLM이 잘 만듭니다. 긴 연구는 다릅니다. 논문이 규정하는 네 가지 난점은 다음과 같습니다.

1. 전략 불확실성: 문제가 정확해도 증명 경로가 여럿이고 어느 것이 통할지 앞부분에서 알 수 없습니다.
2. 분산된 기술적 난이도: 하나의 증명에 상호 의존적인 병목이 여러 개 있고, 하나를 풀면 다른 병목이 드러납니다.
3. 긴 출력과 오류 누적: <span style="background-color: #fff59d"><strong>한 번의 응답 예산에 못 들어가는 증명은 단순 샘플링으로 완성할 수 없습니다.</strong></span> 정의와 가정이 멀리 떨어진 섹션 사이에서 어긋나기도 합니다.

4. 실패와 부분 진전: 실패해도 반례, 제한된 결과, 대안 정식화가 남는데 이를 기록하지 않으면 사라집니다.

## 5단계 파이프라인

Figure 1이 전체 구조를 보여줍니다.

![Colosseum 아키텍처 개요: 스테이지별 연구 워크플로우와 스테이지 내부 샘플링·합성 구조](/images/2026-09-15-stellar-colosseum-many-agent-harness/fig-1-architecture.png)

### Stage 1: 전략 탐색

증명을 바로 쓰지 않고 여러 증명 전략(재정식화, 보조정리 경로, 기존 결과와의 연결)을 병렬로 전개합니다. 각 후보는 typed 스키마로 생성되며, 전략 제안은 메커니즘, 필요한 보조정리, 예상 병목, 반증 가능한 테스트를 명시합니다.

### Stage 2: 준비 게이트

<span style="background-color: #fff59d"><strong>"이 경로가 증명 계획으로 분해될 만큼 구체적인가"를 검사합니다.</strong></span> 증명 완료 여부보다 남은 불확실성이 안정적인 증명 구조 안에 국소화되었는지를 봅니다. 미달이면 탐색으로 돌아갑니다.

### Stage 3: 증명 분해

선택된 경로를 섹션 단위 증명 골격과 부분문제 의존 그래프(DAG)로 변환합니다. 문서 순서는 서술용, 의존 그래프는 작업 순서용입니다.

### Stage 4: 부분문제 병렬 해결

의존성이 충족된 섹션을 병렬로 풉니다. 로컬 리뷰에서 결함이 나오면 <span style="background-color: #fff59d"><strong>해당 부분문제만 재시도하고 의존 그래프의 다른 완성 작업은 보존합니다.</strong></span>

### Stage 5: 전역 검증

각 섹션이 그럴듯해도 전체로는 실패할 수 있습니다(의존성 오용, 표기 드리프트, 케이스 누락). 전역 검증기는 문서 전체를 하나의 논증으로 읽고 결함을 섹션/클레임에 국소화해 되돌립니다. 다수결 투표를 쓰지 않고 <span style="background-color: #fff59d"><strong>구체적 치명 결함 하나만으로 증명을 기각합니다.</strong></span>

## 스테이지 내부: 반증과 트리 집계

어려운 단계의 결정은 단일 응답에 맡기지 않습니다. 후보 n개를 병렬 생성하고, 반증자(falsifier)가 각각을 공격하고, 겹치는 무작위 샘플 트리로 집계합니다.

- 각 집계 노드는 현재 인구에서 k개를 무작위로 뽑아 합성합니다. 그룹이 겹치므로 좋은 후보는 여러 번 살아남을 기회를 갖습니다.
- 집계는 투표를 하지 않고 구성적으로 결합합니다. 호환되는 성분 병합, 경쟁 분기 유지, 국소 결함 수리, 미해결 충돌 선언이 가능합니다.
- <span style="background-color: #fff59d"><strong>반증 기록이 후보에 붙은 채로 집계되므로 이의가 사라지지 않고 다음 단계로 전달됩니다.</strong></span>

설정도 구체적입니다. TCS-Bench/Codeforces의 전략 탐색은 트리 폭 (32, 16, 8, 5, 1), 샘플 크기 5. 나머지 단계는 (16, 8, 5, 1)로 공통입니다.

## 공유 연구 지식

실패한 시도도 버리지 않습니다. 두 가지 메모리가 있습니다.

1. 최신 초안 + 검증 피드백: 다음 라운드는 원 문제에서 다시 시작하는 대신 실제 시도된 논증에서 출발합니다.
2. 지식 디렉터리: 정리/보조정리, 실패한 접근과 정확한 실패 지점, 참고문헌, 관찰을 소스와 함께 보존합니다.

Erdős 단위거리 문제 케이스에서는 <span style="background-color: #fff59d"><strong>15번의 탐색 라운드 동안 축적 지식이 앞으로 전달되며</strong></span>, 인터넷 접속 차단 조건에서 OpenAI 해법의 중심 구조를 독립적으로 재발견한 22페이지 초안이 나왔습니다.

## 실제 연구 성과

하네스는 벤치마크 외에 공개 문제에 신규 결과를 기여했습니다.

- ℓp 부분공간 근사(p > 2) 강한 코어셋 크기를 Õ(k^{p/2}ε^{-2})로 개선 (기존 ε^{-p} 의존 → <span style="background-color: #fff59d"><strong>ε^{-2} 의존</strong></span>)
- 희소 최소제곱의 조건수 장벽 하한 (가정 하, 다항시간 알고리즘의 사실상 선형 의존 필연성)
- 최대 내적 임베딩 차원 하한에서 기존 갭을 거의 닫음
- 단일 단계 하다마드 양자화 추정기 (잔여 단계 제거, 상수 약 <span style="background-color: #fff59d"><strong>5.93배 감소</strong></span>)
- 접두사 행렬 분해 하한 Ω(log^{3/2}n / (log log n)^{3/2})

Knuth 사이클 문제에서는 <span style="background-color: #fff59d"><strong>46페이지와 75페이지짜리 완전 증명 초안</strong></span>을 산출했습니다. 단일 응답 예산을 훨씬 넘는 길이입니다.

## 평가 상세

TCS벤치는 FOCS/STOC/SODA 2020–2026 논문에서 뽑은 300개 연구급 정리 증명 과제입니다.

두 개의 Colosseum 실행(Gemini 3.1 Pro 54.0%, Gemini 3.7 Flash 55.0%)은 개별 성적이 비슷했지만 오류가 상호 보완적이어서, 크리틱 기반 교차 선택으로 <span style="background-color: #fff59d"><strong>213문제 = 71.0%</strong></span>에 도달했습니다(선택 신호 판별력 AUC 0.896).

Codeforces(2025년 4–10월, 난이도 추정 1500 초과 222문제)에서는 증명 지향 파이프라인에 C++ 실행 프로브만 추가해 <span style="background-color: #fff59d"><strong>218/222 통과, 코퍼스 성능 레이팅 4263</strong></span>을 기록했습니다.

실행 프로브 없으면 213/222, 3918입니다. 논문은 두 구성이 리비전 예산도 달라 <span style="background-color: #fff59d"><strong>인과 효과 분리 비교가 아님</strong></span>을 명시합니다.

## 하네스 설계자가 남긴 과제

- 전략 클러스터링: 같은 아이디어 변형이 다수를 차지하면 진짜 다른 방향이 묻힙니다. 방향별 클러스터 탐색 제안.
- 부분문제 실패 후 국소 재구조화: 재시도만 반복하면 경계 설계가 잘못된 것입니다. 의존 그래프의 작은 이웃만 수정하는 중간 단계 제안.
- 검증된 연구 궤적을 포스트트레이닝 데이터로 사용: 분기 구조가 크레딧 배정 단서를 제공합니다.

제 해석을 붙이면, 이 논문의 실질 기여는 <span style="background-color: #fff59d"><strong>실패와 이의를 일등급 데이터로 취급하는 상태 관리</strong></span>입니다. 반증 기록이 붙은 채 집계되고, 실패한 경로의 정확한 지점이 디렉터리에 남습니다. 일반 에이전트 워크플로 설계에도 그대로 적용할 수 있는 원칙입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### Colosseum은 어떤 모델을 쓰나요?

모델 비구체적(model-agnostic) 하네스입니다. 평가에는 Gemini 3.1 Pro와 Gemini 3.7 Flash를 사용했고, 교차 선택 규칙으로 두 실행 결과 중 하나를 골랐습니다.

### 벤치마크 71.0%는 동일 컴퓨트 비교인가요?

동일하지 않습니다. 직접 평가(Gemini 3.1 Pro 30.3%, GPT-5.6 Pro max 68.0%)보다 높지만 추론 시점 컴퓨팅을 훨씬 더 쓰며, 논문도 컴퓨트 매칭 평가의 필요성을 인정합니다.

### 일반 소프트웨어 에이전트에도 적용되나요?

Codeforces 케이스가 근거입니다. 증명용 탐색-분해 구조를 코드에 그대로 옮기고 실행 피드백만 추가해 218/222를 달성했습니다.

### 코드는 공개되어 있나요?

논문 본문 기준으로 하네스 자체 코드 공개는 확인되지 않고, Erdős 문제의 22페이지 초안이 GitHub에 공개되어 있습니다. 워크플로는 Google Antigravity Teamwork 프레임워크의 Long Proof 패턴으로 통합되었다고 합니다.

## 출처

- 논문: [Stellar Colosseum: A Many-Agent Harness for Long-Horizon Research in Mathematics and Theoretical Computer Science (arXiv:2609.15983)](https://arxiv.org/abs/2609.15983)
- 관련 링크: [Google Antigravity Teamwork 블로그](https://antigravity.google/blog/teamwork-when-ai-becomes-a-research-partner)
- 작성 기준일: 2026-09-15, v1 기준
