---
title: GABench — 그래프 분석에서 LLM 에이전트는 아직 40%도 안 됩니다
date: 2026-09-02
tags:
  - benchmark
  - llm-agent
  - graph
  - tool-use
draft: false
description: GABench는 그래프 분석용 에이전트 벤치마크로 13개 실데이터셋, 84개 실행 도구, 검증 가능한 태스크 10,400개로 구성됐습니다. 프론티어 모델·하네스 평가 결과 복잡한 그래프 머신러닝과 개방형 QA에서 성공률이 대부분 40% 미만이었고, 하네스가 같은 모델의 성적을 크게 바꿨습니다.
---

## 결론 먼저

GABench([arXiv:2608.01684](https://arxiv.org/abs/2608.01684), 2026-08 공개)는 LLM 에이전트의 그래프 분석 능력을 측정하는 벤치마크다. <span style="background-color: #fff59d"><strong>실세계 데이터셋 13개, 실행 가능한 도구 84개, 검증 가능한 정답을 가진 태스크 10,400개</strong></span>로 구성되며, 그래프 검색(graph retrieval), 그래프 이론(graph theory), 그래프 머신러닝(graph machine learning), 그래프 개방형 질의응답(graph open-ended question answering)의 4개 태스크 범주를 다룬다.

주요 결과는 다음과 같다.

- <span style="background-color: #fff59d"><strong>대부분의 경우 그래프 머신러닝과 그래프 개방형 질의응답에서 성공률(SR)이 40% 미만</strong></span>으로, 구조 이해와 그래프 데이터 위의 추론 능력이 제한적임을 보였다(기준일: 2026-08 공개 논문 기준).
- 동일 모델(GLM-5-turbo)을 사용할 때 하네스에 따라 그래프 머신러닝 평균 성공률이 <span style="background-color: #fff59d"><strong>OpenClaw 34.94%, Hermes 60.22%, Claude Code 87.80%로 차이</strong></span>를 보였다.

## 벤치마크 구성

| 항목 | 값 |
| --- | --- |
| 실세계 데이터셋 | 13개 (6개 도메인) |
| 그래프 유형 | 수치 속성 그래프(NAG), 텍스트 속성 그래프(TAG), 텍스트 쌍 그래프(TPG) 3종 |
| 태스크 범주 | 그래프 검색, 그래프 이론, 그래프 머신러닝, 그래프 개방형 질의응답 |
| 실행 도구 | 84개 |
| 태스크 수 | 10,400개 (검증 가능한 정답 포함) |
| 평가 모델 | Qwen3-235B, GLM-4.5-flash, GLM-5-turbo, DeepSeek-V4-pro, GPT-5-mini, Gemini-3-flash |
| 크로스 하네스 평가 | OpenClaw, Claude Code, Hermes Agent (GLM-5-turbo 고정) |

![GABench 개요](/images/2026-09-02-gabench-graph-analysis-agents/fig-1-p3.png)
*Figure 1. GABench 전체 구조 출처: arXiv:2608.01684 Figure 1*

## 측정 방식

각 태스크는 실행 기반으로 채점된다. 에이전트는 84개 도구를 조합하여 그래프 데이터를 조회하고, 노드 분류, 링크 예측, 그래프 분류 등의 머신러닝 워크플로를 구성하며, 개방형 질문에 대해서는 근거 기반 응답을 생성해야 한다.

평가 지표는 다음 두 가지다.

- SR(task success rate): 최종 결과가 정답과 일치하는 비율
- TSA(tool-selection accuracy): 각 단계에서 필요한 도구를 올바르게 선택했는지의 비율

## 결과 1 — 하네스에 따른 성능 차이

GLM-5-turbo를 3개 하네스에 동일한 도구 스키마·시스템 프롬프트 조건으로 배치한 크로스 하네스 평가 결과(Table 7)는 다음과 같다.

| 하네스 | 그래프 머신러닝 평균 SR(%) | 그래프 개방형 QA 평균 SR(%) |
| --- | --- | --- |
| Claude Code | 87.80 | 16.71 |
| Hermes | 60.22 | 8.17 |
| OpenClaw | 34.94 | 10.28 |

![하네스별 성공률](/images/2026-09-02-gabench-graph-analysis-agents/table-7-p8.png)
*Table 7. GLM-5-turbo의 하네스별 태스크 성공률 출처: arXiv:2608.01684 Table 7*

논문은 Claude Code가 반복적인 코드·도구 실행을 지원하는 특성 때문에 다단계 워크플로가 필요한 그래프 태스크에서 유리하다고 분석한다. 하네스 내에서 툴 스키마와 프롬프트를 일관되게 유지했으므로, 이 차이는 <span style="background-color: #fff59d"><strong>스캐폴드가 모델 행동에 미치는 영향</strong></span>으로 해석할 수 있다.

## 결과 2 — 도구 호출의 질과 수의 관계

평균 도구 호출 수와 성공률의 관계(Figure 3)에서, <span style="background-color: #fff59d"><strong>도구 호출 수보다 도구 호출의 질이 성공률을 결정</strong></span>하는 경향이 관측되었다. 강한 모델은 더 적은 호출로 더 높은 성능을 냈다. 그래프 이론 태스크의 도구 선택 정확도에서는 DeepSeek-V4-pro가 62.26~98.29로 전반적으로 가장 높았다.

![도구 호출 수와 성공률](/images/2026-09-02-gabench-graph-analysis-agents/fig-3-p8.png)
*Figure 3. 평균 도구 호출 수와 SR의 관계 출처: arXiv:2608.01684 Figure 3*

## 결과 3 — 하네스별 토큰 소비

동일 모델 기준 그래프 머신러닝 태스크의 하네스별 평균 토큰 소비는 다음과 같다(Table 8).

| 하네스 | 평균 입력 토큰 | 평균 출력 토큰 |
| --- | --- | --- |
| Claude Code | 15,793 | 4,826 |
| Hermes | 29,795 | 4,044 |
| OpenClaw | 61,431 | 4,201 |

![하네스별 토큰 비용](/images/2026-09-02-gabench-graph-analysis-agents/table-8-p8.png)
*Table 8. GLM-5-turbo의 하네스별 태스크 성공률과 토큰 소비 출처: arXiv:2608.01684 Table 8*

<span style="background-color: #fff59d"><strong>Claude Code가 가장 적은 입력 토큰으로 가장 높은 성공률을 기록</strong></span>했고, OpenClaw는 대부분의 설정에서 입력 토큰 소비가 가장 컸다. 논문은 컴팩트한 중간 상태 표현 등 토큰 효율적인 에이전트 설계를 후속 과제로 제시한다.

## 해석

원문 근거와 본 해석을 구분해 정리한다.

하나. 그래프 데이터를 다루는 도입 검토에서 모델 선택만으로는 불충분하다. 동일 모델에서 <span style="background-color: #fff59d"><strong>약 2.5배의 성공률 차이</strong></span>가 발생했으므로, 하네스 비교를 평가 항목에 포함해야 한다.

둘. 그래프 개방형 질의응답은 하네스를 변경해도 <span style="background-color: #fff59d"><strong>최고 성공률이 16.71%</strong></span>다. 정형 워크플로가 있는 그래프 머신러닝과 달리, 해석·서술이 필요한 영역은 아직 자동화 신뢰가 낮다.

셋. <span style="background-color: #fff59d"><strong>그래프 분류의 도구 선택 정확도(42.09)</strong></span>는 노드 분류(75.57)와 링크 예측(78.32)보다 크게 낮다. 그래프 수준 워크플로 구성이 약하다는 신호로, 그래프 수준 태스크에서는 도구 체인을 사전에 설계하는 접근이 안전하다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**GABench가 기존 그래프 LLM 벤치마크와 다른 점은 무엇인가요?**
실세계 데이터셋 13개를 기반으로 84개 실행 도구를 사용하는 태스크 10,400개를 구축했고, 계획, 도구 사용, 종단 간 성공률을 함께 측정한다는 점에서 답변 생성 중심의 기존 벤치마크와 다릅니다.

**하네스 간 성능 차이는 어느 정도인가요?**
GLM-5-turbo 기준 그래프 머신러닝 평균 성공률이 <span style="background-color: #fff59d"><strong>Claude Code 87.80%, Hermes 60.22%, OpenClaw 34.94%</strong></span>입니다. 동일 모델·동일 도구 스키마 조건의 결과입니다.

**도구 호출 횟수가 많을수록 성능이 좋아지나요?**
아니요. 논문은 도구 호출의 질이 횟수보다 중요하다고 보고하며, 강한 모델이 적은 호출로 더 높은 성능을 내는 경향을 관측했습니다.

**출처는 어디인가요?**
GABench: A Comprehensive Benchmark for Evaluating LLM Agents on Graph Analysis Tasks, arXiv:2608.01684(2026-08 공개, 기준일 2026-09-02). [논문](https://arxiv.org/abs/2608.01684) / [HTML 전문](https://arxiv.org/html/2608.01684v1)
