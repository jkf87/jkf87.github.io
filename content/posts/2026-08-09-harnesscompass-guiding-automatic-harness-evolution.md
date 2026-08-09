---
title: "HarnessCompass: 제약 진화·주관적 피드백·컴포넌트별 최적화를 통한 하네스 자동 진화 일반화"
tags:
  - agent
  - harness
  - LLM
  - self-evolution
  - SWE-bench
  - benchmark
  - tool-use
  - automation
  - loop
  - generalization
date: 2026-08-09
source: arxiv
paper_url: https://arxiv.org/abs/2608.01918
authors:
  - Luan Zhang
  - Ruochen Zhou
  - Dandan Song
  - Zhengyu Chen
  - Yuhang Tian
  - Jun Yang
  - Huipeng Ma
  - Chenhao Li
  - Guangyuan Feng
  - Xudong Li
  - Yizhou Jin
  - Yan Xu
affiliations:
  - Beijing Institute of Technology
  - City University of Hong Kong
---

## 개요

Zhang et al. (2026)은 자동 하네스 진화(automatic harness evolution)의 세 가지 한계—검색 작업 과적합, 신호 부족, 컴포넌트 간 간섭—를 지적하고, HarnessCompass 프레임워크를 제안합니다. SWE-bench Verified에서 GPT-5.4(non-thinking mode) 기준 Pass@1을 54%에서 66%로 향상시켰으며, 450개의 미지(unseen) 작업에서 60.4%의 일반화 성능을 달성했습니다. 이는 기존 AHE 대비 반복 횟수 1/4로 더 높은 성능을 기록한 것입니다.

## 자동 하네스 진화의 기존 한계

LLM 에이전트의 성능은 기저 모델뿐 아니라 하네스(harness)—프롬프트, 도구, 미들웨어, 메모리, 검증 루틴—에 의해 크게 좌우됩니다. 자동 하네스 진화는 메타 에이전트가 궤적을 분석하여 하네스를 반복적으로 개선하는 방법론입니다.

기존 방법의 한계는 다음과 같습니다:

1. 검색 작업 과적합: 메타 에이전트가 검색에 사용된 작업에 특화된 규칙을 하네스에 포함시킵니다. Wang et al. (2026)은 진화된 하네스가 미지 작업으로 이전될 때 성능이 크게 저하됨을 보였습니다.
2. 궤적 신호만 의존: 궤적 결과(성공/실패)만으로는 실패의 원인이 하네스인지 에이전트의 추론인지 구분할 수 없습니다.
3. 컴포넌트 간 간섭: 프롬프트, 도구, 미들웨어를 동시에 수정하면 각 수정의 효과를 분리할 수 없고, 수정 간 충돌이 발생할 수 있습니다.

## HarnessCompass 프레임워크

![](/images/2026-08-09-harnesscompass-guiding-automatic-harness-evolution/fig-1-p2.png)

Figure 1: HarnessCompass 개요. 하네스를 구조 컴포넌트와 가이드 컴포넌트로 분리하여 독립적으로 진화시킨 뒤 통합합니다.

### 1. 제약 진화 (Constrained Evolution)

일반화 게이트(generalization gate)를 통해 작업无关적(task-agnostic) 수정만 허용합니다. 특정 키워드 매칭, 인스턴스별 하드코딩, 검색 작업에만 유효한 규칙을 차단합니다. 이를 통해 진화 과정에서 학습된 설계 원칙이 미지 작업으로 이전될 수 있습니다.

단독 적용 시: 진화 샘플 54.0% → 62.0%, 미지 작업 51.6% → 58.4%, 진화 횟수 2회.

### 2. 주관적 피드백 (Proactive Feedback)

에이전트에게 하네스 사용 경험을 첫 사람 시점(first-person)으로 보고하도록 요청합니다. 보고된 피드백은 궤적과 대조 검증(hindsight grounding)을 거쳐 진화에 반영됩니다.

- 맹목 보고(blind): 검증 없이 피드백만 사용 → 진화 샘플 66.0%, 미지 작업 55.8% (과적합 발생)
- 후견 보고(hindsight): 궤적 검증 후 피드백 사용 → 진화 샘플 66.0%, 미지 작업 개선

### 3. 컴포넌트별 최적화 및 R³ 통합

하네스를 두 트랙으로 분리합니다:
- 구조 트랙: 도구 구현, 미들웨어, 서브에이전트 설정
- 가이드 트랙: 시스템 프롬프트, 도구 설명, 스킬, 장기 메모리

각 트랙을 독립적으로 진화시킨 뒤, R³(Retrieve, Review, Refine) 통합으로 상호 보완적인 수정을 병합합니다.

R³ 통합 추가 시: 미지 작업 60.4%, 전체 61.0%.

## 실험 결과

### 메인 비교 (SWE-bench Verified, GPT-5.4)

| 방법 | 진화 샘플 (50개) | 미지 작업 (450개) | 전체 (500개) | 진화 횟수 |
|---|---|---|---|---|
| 시드 H₀ | 54.0% | 51.6% | 51.8% | 0 |
| AHE | 63.0% | 54.7% | 55.5% | 20 |
| HarnessCompass | 66.0% | 60.4% | 61.0% | 5 |

Table 1: 메인 결과. HarnessCompass가 미지 작업에서 AHE 대비 5.7%p 우위.

![](/images/2026-08-09-harnesscompass-guiding-automatic-harness-evolution/fig-2-p6.png)

Figure 2: 반복별 Pass@1. HarnessCompass는 5회에서 66%에 도달, AHE는 20회에서 낮은 수렴.

### 누적 어블레이션

| 구성 | 진화 샘플 | 미지 작업 | 전체 | 횟수 |
|---|---|---|---|---|
| 시드 | 54.0% | 51.6% | 51.8% | 0 |
| + 일반화 게이트 | 62.0% | 58.4% | 58.8% | 2 |
| + 주관적 피드백 | 66.0% | 55.8% | 56.8% | 12 |
| + R³ 통합 | 66.0% | 60.4% | 61.0% | 5 |

Table 2: 누적 어블레이션. 주관적 피드백 단계에서 미지 작업이 55.8%로 저하되는 현상을 R³ 통합이 보정합니다.

### 교차 모델 이전

| 모델 | 하네스 | 진화 샘플 | 미지 작업 | 전체 |
|---|---|---|---|---|
| GPT-5.4 | 시드 | 54.0% | 51.6% | 51.8% |
| GPT-5.4 | HarnessCompass | 66.0% | 60.4% | 61.0% |
| Claude-Sonnet-4.6 | 시드 | 68.0% | 70.2% | 70.0% |
| Claude-Sonnet-4.6 | HarnessCompass | 76.0% | 73.6% | 73.8% |

Table 3: GPT-5.4로 진화한 하네스를 Claude-Sonnet-4.6에 적용. 3.8%p (전체 기준) 개선이 유지됩니다.

![](/images/2026-08-09-harnesscompass-guiding-automatic-harness-evolution/fig-3-p7.png)

Figure 3: 저장소별 Pass@1. 일관된 개선 패턴.

## 분석

본 연구의 핵심 발견은 다음과 같습니다:

1. 하네스 진화에서 가장 중요한 제약은 수정의 일반성입니다. 일반화 게이트만으로도 과적합이 상당 부분 해소됩니다.
2. 에이전트의 주관적 피드백은 진화 샘플 성능을 향상시키지만, 검증 없이 사용할 경우 미지 작업에서 과적합을 유발합니다. 궤적 기반 검증이 필수적입니다.
3. 컴포넌트를 분리하여 진화하고 후속 통합하는 방식이 동시 진화보다 더 적은 반복으로 더 높은 성능을 달성합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [HarnessCompass: Guiding Automatic Harness Evolution toward Generalizable and Effective Agent Harnesses](https://arxiv.org/abs/2608.01918)
