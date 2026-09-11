---
title: "Training Proactive and Personalized LLM Agents 논문 정리 (arXiv 2511.02208, COLM 2026)"
date: 2026-09-11
tags:
  - ai-agent
  - reinforcement-learning
  - human-agent-interaction
draft: false
description: "COLM 2026 논문 Training Proactive and Personalized LLM Agents 정리. UserVille 환경과 PPP 다목적 강화학습 프레임워크의 구성, SWE-Bench/BrowseComp-Plus 실험 결과(평균 +16.72), 33인 실사용자 연구 결과를 수치 중심으로 요약합니다."
---

## 핵심 요약

- 논문: Training Proactive and Personalized LLM Agents (arXiv 2511.02208, COLM 2026, v2 기준일 2026-09-11)
- 결론: <span style="background-color: #fff59d"><strong>사용자와의 상호작용·적응을 보상에 넣는 다목적 RL로, 36B 모델이 GPT-5 포함 baseline을 평균 +16.72점 앞선다</strong></span>
- 제안: 사용자 시뮬레이션 환경 UserVille, 다목적 강화학습 프레임워크 PPP
- 베이스 모델: Seed-OSS-36B-Instruct
- 핵심 결과: <span style="background-color: #fff59d"><strong>SWE-Bench-Verified (Func-Loc), BrowseComp-Plus에서 평균 +16.72점 개선, GPT-5 포함 baseline 대비 전 차원 우위</strong></span>

| 항목 | 내용 |
| --- | --- |
| 환경 | UserVille (LLM 사용자 시뮬레이터 3단계 파이프라인) |
| 최적화 목표 | Productivity, Proactivity, Personalization |
| 훈련 | Verl, lr 1e-6, batch 64, group 8, 200 steps |
| 평가 | SWE-Bench-Verified Func-Loc N=488, BrowseComp-Plus 450/100 분할 |

## 문제 정의

<span style="background-color: #fff59d"><strong>기존 에이전트 RL은 태스크 완수 중심이다</strong></span>. 논문은 세 가지 협업 차원을 정의한다.

1. Productivity: 태스크 성능
2. Proactivity: 상호작용 품질
3. Personalization: 사용자 선호 준수

프롬프트 통계 (Appendix B):

| 데이터셋 | vague 평균 단어 | 원본 평균 단어 |
| --- | --- | --- |
| SWE-Bench | 11.4 | 193.8 |
| BrowseComp | 17.8 | 97.1 |

## UserVille 구조

세 단계로 구성된다.

1. Prompt Vaguenization: 정밀 프롬프트를 불완전한 버전으로 변환
2. Preference-Aware User Simulation: 선호 파라미터 기반 LLM 사용자 시뮬레이터
3. User-Centric Evaluation: 주도성/개인화 피드백 산출

사용자 선호 20종 중 8종은 unseen으로 평가 전용이다. <span style="background-color: #fff59d"><strong>6종(no_ask, answer_more, only_begin 등)은 규칙 기반 보상, 14종은 LLM-as-a-judge(선호별 루브릭)으로 평가한다</strong></span>.

질문 비용 분류: 저비용/중비용/고비용. 주도성 점수는 세션 user effort가 저비용일 때 1.

![Figure 1: 논문 개요](/images/2026-09-11-ppp-proactive-personalized-llm-agents/fig-1-p2.png)

![Figure 2: UserVille 파이프라인](/images/2026-09-11-ppp-proactive-personalized-llm-agents/fig-2-p3.png)

## PPP 프레임워크

에이전트는 태스크 툴과 사용자 시뮬레이터 양쪽과 상호작용하며 복합 보상을 최대화한다. 보상 구성요소:

| 보상 | 정의 |
| --- | --- |
| Productivity | SWE는 F1, 검색은 EM, 풀태스크는 유닛테스트 성공률 |
| Proactivity | 세션 user effort가 low-effort면 1 |
| Personalization | 질문 1개 이상 세션의 선호 준수율 평균 |

구현 상세: 사용자 시뮬레이터 GPT-5-Nano, 최대 출력 32K(Func-Loc)/65K(Full)/41K(Deep-Research), SWE 스캐폴드 OpenHands 기반, 검색 툴 search/open_page, retriever Qwen3-Embed-8B.

## 실험 결과

RQ1 (상호작용 효과): vague 프롬프트에서 <span style="background-color: #fff59d"><strong>F1 44.11 → 64.50 (상호작용 + PPP 훈련)</strong></span>.

![Figure 3: SWE-Bench Func-Loc F1](/images/2026-09-11-ppp-proactive-personalized-llm-agents/fig-3-p6.png)

RQ2 (Table 1, vague 프롬프트 + 20 선호 평균):

| 방법 | 평균 | Productivity | Proactivity | Personalization |
| --- | --- | --- | --- | --- |
| GPT-5 | 40.40 | 55.83 | 36.60 | 12.96 |
| GPT-5-Mini | 35.82 | 35.00 | 15.90 | 24.82 |
| GPT-5-Nano | 30.09 | 24.30 | 11.10 | 16.92 |
| GPT-4.1 | 38.86 | 25.08 | 11.35 | 53.04 |
| Seed-OSS-36B | 45.32 | 38.59 | 43.70 | 69.07 |
| PPP | <span style="background-color: #fff59d"><strong>62.04</strong></span> | <span style="background-color: #fff59d"><strong>56.26</strong></span> | <span style="background-color: #fff59d"><strong>75.55</strong></span> | <span style="background-color: #fff59d"><strong>89.26</strong></span> |

RQ3 (질문 전략 학습): <span style="background-color: #fff59d"><strong>질문 수 0.5 → 1.2. 저비용 질문 중심 증가, 중비용 질문은 증가 후 감소, 고비용 질문은 미미</strong></span>. 주도성 보상 제거 시 중·고비용 질문 증가.

![Figure 7: 세션당 평균 상호작용](/images/2026-09-11-ppp-proactive-personalized-llm-agents/fig-7-p8.png)

RQ4 (일반화): unseen 선호 8종에서 일관된 개선. 개인화 보상 제거 시 <span style="background-color: #fff59d"><strong>JSON_Format 선호 점수 1.00 → 0.30 붕괴</strong></span>. <span style="background-color: #fff59d"><strong>Func-Loc → SWE-Full 전이 시 성공률 0.29 → 약 0.36, 상호작용 0.10 → 1.8</strong></span>. <span style="background-color: #fff59d"><strong>정밀 프롬프트에서는 0.558 → 약 0.530으로 소폭 감소</strong></span> — 상호작용 훈련의 이득은 애매한 지시에서 집중되고 정밀한 지시에서는 미세 비용이 있다.

시뮬레이터 강건성 (Table 3): GPT-5/GPT-5-Mini/GPT-4.1/GPT-4o 시뮬레이터로 평가해도 성능 변동 소폭.

## 실사용자 연구 (Section 8)

- 참가자: Prolific, 프로그래밍 경험자 33명, SWE-Bench Verified 첫 100 인스턴스
- 비교: GPT-5, Seed-36B, PPP-36B 익명 배정
- 결과: 전체 점수 <span style="background-color: #fff59d"><strong>PPP-36B 3.75, GPT-5 3.79, Seed-36B 3.45</strong></span>. 선호 준수 "Yes" <span style="background-color: #fff59d"><strong>PPP-36B 67.7%로 최고</strong></span>. 문제 해결률 PPP-36B 71.0%, Seed-36B 70.0%, GPT-5 85%. <span style="background-color: #fff59d"><strong>만족도는 코딩 실력이 아니라 상호작용 기술이 좌우한다</strong></span>는 해석이 가능하다.

## 부록: 질문 설계 실험

| 설정 | 질문 수 | 좋은 질문 수 | 비율 |
| --- | --- | --- | --- |
| 페널티/보너스 없음 | 4.65 | 2.39 | 51.39% |
| 페널티 추가 | 0.806 | 0.722 | 89.57% |
| 페널티 + 보너스 | 1.10 | 1.02 | <span style="background-color: #fff59d"><strong>92.72%</strong></span> |

## 관련 URL

- arXiv abstract: https://arxiv.org/abs/2511.02208
- PDF: https://arxiv.org/pdf/2511.02208
- HTML (v2): https://arxiv.org/html/2511.02208v2

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 세 가지 평가 지표는 무엇인가?

Productivity(태스크 성공), Proactivity(저비용 질문 기반 세션 비율), Personalization(선호 준수율)이다.

### 실사용자 연구 규모와 결과는?

33명, PPP-36B 3.75점으로 GPT-5(3.79)와 대등, Seed-36B(3.45)보다 우수.

### 프론티어 모델의 한계는?

GPT-5의 Personalization 점수가 12.96으로 낮고, GPT-4.1(53.04)보다도 낮다.
