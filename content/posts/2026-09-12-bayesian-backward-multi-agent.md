---
title: "에이전트 다수결이 틀릴 때: 베이즈 역방향 추론으로 앵커를 만드는 방법 (arXiv 2609.11709)"
date: 2026-09-12
tags:
  - llm-agents
  - multi-agent
  - collective-decision
  - bayesian
  - arxiv
draft: false
description: 명시적 우도 기반 베이즈 역방향 추론으로 역방향 사후분포 앵커를 구성해 LLM 멀티에이전트 집단 의사결정 정확도를 개선한 논문(arXiv 2609.11709) 요약. DDXPlus 5백본 실험 결과 정리.
---

## 핵심 요약

arXiv 2609.11709 (2026-09-10 공개, University of Melbourne, Ken Chen 외)는 여러 LLM 에이전트가 서로 답을 내놓고 의견이 갈릴 때, 기존 투표·LLM 판정관 방식이 같은 오류를 되풀이하기 쉽다는 문제의식에서 출발한다.

둘 다 증거에서 결론으로 가는 <span style="background-color: #fff59d"><strong>순방향 경로 안에서만 판단</strong></span>하기 때문이다.

이 논문은 <span style="background-color: #fff59d"><strong>명시적 우도를 정의하고 사후확률을 한 번 뒤집는 베이즈 역방향 추론으로 "역방향 사후분포 R"을 만들어</strong></span> 이것을 투표·재가중치·융합의 앵커로 쓰는 방법을 제안한다.

주요 결과 (DDXPlus 49질환 진단, 백본 5종, 순방향 에이전트 5종):

- 결과는 DDXPlus 49질환 진단 벤치마크, 5개 백본(Qwen3-30B, Mistral-Small-3.1-24B, Llama-3.1-8B, GLM-4-32B, DeepSeek-V4-Flash) 기준이다. 순방향 에이전트 5개의 top-1 예측이 일치하지 않는 Disagree 구간에서, 제안 방식 LogLin은 <span style="background-color: #fff59d"><strong>최고 성능 순방향 선거 규칙 대비 5개 백본 전체에서 +1.2~+4.7pp 우수</strong></span>하다. LLM 판정관(Informed Dictator, ACH) 두 종류를 모두 상회한다.
- LLM 판정관(Informed Dictator, ACH) 두 종류를 모두 상회
- <span style="background-color: #fff59d"><strong>역방향 사후분포 R은 단독 예측 정확도가 순방향 평균 대비 7.8~26.4pp 낮으나, 앵커로 사용 시 최고 성능 달성</strong></span>
- <span style="background-color: #fff59d"><strong>오류 충돌률 π(다수결과 참조 예측자가 모두 틀렸을 때 동일 오답 선택 확률): R 0.196~0.413</strong></span>, 외부 순방향 에이전트 GenF 0.594~0.765, 풀 내 에이전트 0.680~0.829
- 추가 비용: <span style="background-color: #fff59d"><strong>인스턴스당 역방향 LLM 호출 2회, 테스트 시점 파라미터 갱신 없음</strong></span>

## 주요 수치

| 항목 | 값 |
|---|---|
| 벤치마크 | DDXPlus (49질환, 2,000케이스 테스트 슬라이스) |
| 백본 | Qwen3-30B-A3B, Mistral-Small-3.1-24B, Llama-3.1-8B, GLM-4-32B, DeepSeek-V4-Flash |
| 순방향 에이전트 | ToT, MedPrompt, vanilla CoT, common-bias, rare-bias (5종) |
| 측정 지표 | GTPA@1 (gold pathology top-1 정확도) |
| 역방향 앵커 | R(d) ∝ P(e\|d)·P(d\|a) |
| 집계 전략 | MinJS (하드 선택), FwdJS (τ=5.0 재가중치), LogLin (w_R=0.2 융합) |

## 배경 및 문제 정의

LLM 멀티에이전트 시스템에서 이질적 에이전트의 출력을 집계하는 기존 방법은 다음으로 구분된다.

1. 투표 기반: Plurality, Range, Borda Count, Bucklin, IRV, Minimax, Ranked Pairs.
   단순 합의에 의존하며, 에이전트 간 불일치 해소 기준이 없다.
2. 독재 기반: LLM-as-a-judge.
   외부 판정을 제공하나 평가가 평가 대상과 동일한 순방향 트레이스에서 수행되며 위치 편향, 장황함 편향, 자기강화 편향 등 계통 편향이 보고된다.

저자는 집계 실패의 근본 원인을 <span style="background-color: #fff59d"><strong>알고리즘적이기보다 방향적</strong></span>이라고 진단한다. 순방향 풀 내부 오류는 공선형이며, 다수가 환각할 경우 투표와 판정 모두 동일 오류를 반복한다.

## 제안 방법

베이즈 정리는 동일 사후확률에 대해 두 인수분해를 제공한다.

순방향 추론이 판별적 evidence→label 매핑을 수행한다면, 본 논문은 <span style="background-color: #fff59d"><strong>명시적 우도 P(e|d)와 맥락 사전확률 P(d|a)를 정의하여 인스턴스당 1회 역방향 반전을 수행</strong></span>하고 공유 역방향 사후분포 R(d|x)를 구성한다.

순방향 사후분포와 R 사이의 <span style="background-color: #fff59d"><strong>Jensen-Shannon divergence로 에이전트별 교차 경로 일관성을 측정</strong></span>하며, 이를 세 가지 집계 전략에 활용한다.

![Figure 1: 제안 파이프라인](/images/2026-09-12-bayesian-backward-multi-agent/fig-1-p4.png)

라벨이 있는 경우 2단계 캘리브레이션(서수 맵의 로짓-선형 피팅과 클래스 사전 스칼라 보정)을 적용할 수 있다. 테스트 시점 파라미터 갱신은 없으며, 역방향 반전은 LLM 호출 2회로 구성되고 동일 R을 전 집계 연산자가 재사용한다.

## 실험 결과

### 주 성능

![Table 1: All 구간 GTPA@1](/images/2026-09-12-bayesian-backward-multi-agent/table-1-p8.png)

![Table 2: Disagree 구간 GTPA@1](/images/2026-09-12-bayesian-backward-multi-agent/table-2-p8.png)

All 구간에서 LogLin은 <span style="background-color: #fff59d"><strong>5개 백본 모두 최고 성능</strong></span>을 기록했다. Qwen3-30B 기준 74.25%로 Range 72.69%, ACH 71.84%보다 높다.

Disagree 구간에서 LogLin은 최고 순방향 선거 대비 +1.2~+4.7pp, FwdJS는 +0.4~+3.5pp 우수하다. GLM-4-32B에서는 ACH(44.07%)가 FwdJS(42.60%)를 상회하는 예외가 있으나 LogLin(44.41%)은 최고를 유지했다.

### 앵커 유용성 분석

R은 단독 예측자로는 모든 백본에서 MeanF 대비 7.8~26.4pp 낮으나, 앵커로 사용 시 FwdJS 및 LogLin 성능이 최고다.

MeanF를 LogLin 앵커로 대체하면 최고 순방향 선거 대비 Δ≤0이며, R은 +1.2~+4.7pp를 유지한다. 이는 <span style="background-color: #fff59d"><strong>게인이 역방향 채널에서 발생함을 보여준다</strong></span>.

![Table 8: 단인수 역방향 앵커 비교](/images/2026-09-12-bayesian-backward-multi-agent/table-8-p13.png)

### 오류 충돌 및 랭킹 신호

![Figure 2: JSD 랭크별 정확도](/images/2026-09-12-bayesian-backward-multi-agent/fig-2-p8.png)

Qwen, Llama, GLM에서 랭크-2 에이전트가 최고 정확도를 기록하여, R에 가장 가까운 에이전트가 최정확한 것은 아님이 확인되었다.

## 제한 사항

<span style="background-color: #fff59d"><strong>평가는 폐쇄 레이블 집합(49질환)의 단일 진단 벤치마크로 제한</strong></span>된다. 자유 생성 태스크와 도구 사용 태스크에서의 우도 정의는 향후 과제다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 제안 방법의 핵심
명시적 우도와 맥락 사전확률로 역방향 사후분포 R을 구성하고, JSD 기반 일관성을 하드 선택·재가중치·로그선형 융합의 앵커로 사용하는 것입니다.

### LLM-as-a-judge와 다른 점과 그 이유
LLM 판정관은 평가 대상과 동일한 순방향 트레이스에서 판단하여 상관 오류를 상속합니다. <span style="background-color: #fff59d"><strong>역방향 앵커는 다른 인수분해에서 도출되어 오류 충돌률 π가 0.196~0.413으로 낮습니다</strong></span>.

### 성능이 얼마나 오르는지
Disagree 구간에서 LogLin이 5개 백본 전체에서 최고 순방향 선거 규칙 대비 +1.2~+4.7pp 우수합니다 (기준일 2026-09-12, arXiv 2609.11709v1).

### 추가 비용과 한계
인스턴스당 역방향 LLM 호출 2회와 JSD 계산이며, 미세조정은 필요하지 않습니다.

### 역방향 사후분포를 단독으로 쓰면 안 되는 이유
권장하지 않습니다. <span style="background-color: #fff59d"><strong>R의 단독 정확도는 순방향 평균 대비 7.8~26.4pp 낮으며, 가치는 앵커 사용 시 발휘됩니다</strong></span>.

## 참고

- 논문: [arXiv:2609.11709](https://arxiv.org/abs/2609.11709)
- PDF: [arxiv.org/pdf/2609.11709](https://arxiv.org/pdf/2609.11709)
- 벤치마크: [DDXPlus](https://arxiv.org/abs/2302.05228)
