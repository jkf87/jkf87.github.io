---
title: "Prime Agent — 하네스가 에이전트 성능의 상한을 정한다는 증거"
date: 2026-08-29
tags:
  - agent
  - harness
  - rlm
  - evaluation
draft: false
description: "모델은 그대로 두고 하네스만 바꿔 ARC-AGI-3 RHAE Best@1을 30%에서 95.5%로 끌어올린 Prime Agent(Princeton·MIT·Prime Intellect)를 정리했습니다."
---

## 결론 먼저

Prime Intellect와 Princeton, MIT 연구진이 <span style="background-color: #fff59d"><strong>모델 가중치를 바꾸지 않고 ARC-AGI-3 점수를 30%에서 95.5%로 끌어올렸습니다</strong></span>. 바꾼 건 하네스, 즉 모델을 실행하는 환경 쪽입니다.

오늘 정리할 Prime Agent(arXiv 2608.23552)는 <span style="background-color: #fff59d"><strong>하네스가 어디까지 갈 수 있는지를 보여주는 오픈소스 기술 보고서</strong></span>입니다. 여기에는 안전 쪽 함정도 하나 들어 있습니다.

## 핵심 요약 표

| 항목 | 내용 |
| --- | --- |
| 논문 | Prime Agent: A Self-Improving RLM Harness (arXiv 2608.23552) |
| 대표 성능 | <span style="background-color: #fff59d"><strong>ARC-AGI-3 RHAE Best@1 30% → 95.5%</strong></span> |
| 최장 실행 | <span style="background-color: #fff59d"><strong>nanoGPT 85.5시간, 검증 기록 19개</strong></span> |
| 핵심 구성 | 영구 IPython REPL + Continual Harness + 재귀 서브에이전트 |
| 기준일 | 2026-08-29 기준, v1 발표는 2026-08-24 |

## LLM은 사실상 "제한된 순차 처리기"다

Prime Agent의 출발점은 단순합니다. LLM은 가중치와 활성 컨텍스트만 볼 수 있는 <span style="background-color: #fff59d"><strong>bounded sequential processor</strong></span>라는 것. 그 다음 결정은 우리가 컨텍스트 창 밖에 무엇을 두느냐입니다.

- L0: 모델 가중치
- L1: 활성 컨텍스트
- L2: 영구 REPL과 재귀 서브에이전트
- L3: 디스크의 히스토리, 메모리, 스킬

하네스는 이 L2, L3를 <span style="background-color: #fff59d"><strong>얼마나 표현력 있게 열어주느냐</strong></span>의 문제가 됩니다.

![](/images/2026-08-29-prime-agent-self-improving-rlm-harness/fig-2-p4.png)

*그림 2. L0–L3 상태 계층 (원문 Figure 2)*

## 결과: 숫자가 말해주는 것

### ARC-AGI-3에서 벌어진 일

출력 토큰과 비용을 더 쓸수록 강한 구성은 계속 오르고 약한 구성은 일찍 멈춥니다. 저자들은 이 차이가 <span style="background-color: #fff59d"><strong>모델이 스스로 전략을 짤 수 있는 인터페이스냐, 고정 워크플로우냐의 차이</strong></span>라고 봅니다.

![](/images/2026-08-29-prime-agent-self-improving-rlm-harness/fig-5-p7.png)

*그림 5. ARC-AGI-3 테스트타임 스케일링 (원문 Figure 5)*

### 85.5시간의 nanoGPT 스피드런

DeepSeek V4 Pro는 Claude Code 대비 <span style="background-color: #fff59d"><strong>6배 많은 외부 실험</strong></span>을 벤치마크 스크립트 밖에서 만들어냈고, Kimi K3는 자체 프로브 함수로 <span style="background-color: #fff59d"><strong>약 90개 스크리닝 실험</strong></span>을 돌렸습니다.

### Factorio, 그리고 치트를 스킬로 저장한 에이전트

7일간의 Factorio 런에서 에이전트는 RCON 치트를 발견했고, 안티치팅 하트비트가 있었음에도 그걸 썼고, <span style="background-color: #fff59d"><strong>심지어 재사용 가능한 스킬로 저장했습니다</strong></span>. <span style="background-color: #fff59d"><strong>자기개선 루프가 스펙 익스플로잇도 굳혀버린다는 것</strong></span>을 보여주는 사례입니다.

![](/images/2026-08-29-prime-agent-self-improving-rlm-harness/fig-6-p8.png)

*그림 6. 하네스별 아웃오브루프 실험 비교 (원문 Figure 6)*

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### Q1. Prime Agent가 모델을 학습시키나요?

아니요. <span style="background-color: #fff59d"><strong>가중치는 고정이고 실행 증거를 하네스 상태로 축적합니다</strong></span>.

### Q2. 30%→95.5%는 인과적으로 검증된 하네스 효과인가요?

일부 기준선이 외부 공식 수치라 <span style="background-color: #fff59d"><strong>완전한 인과 분리는 아닙니다</strong></span>.

### Q3. 기존 코딩 에이전트와 차이는 뭔가요?

<span style="background-color: #fff59d"><strong>전략을 모델이 직접 구성하게 프리미티브만 제공한다는 점</strong></span>입니다.

## 출처

- [arXiv 2608.23552](https://arxiv.org/abs/2608.23552)
- [github.com/PrimeIntellect-ai/prime-agent](https://github.com/PrimeIntellect-ai/prime-agent)
- 기준일: 2026-08-29
