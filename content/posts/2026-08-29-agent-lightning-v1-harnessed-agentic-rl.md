---
title: Agent Lightning v1.0 — 하네스가 곧 학습 환경이 되는 시대
date: 2026-08-29
tags:
  - ai-agents
  - reinforcement-learning
  - agent-harness
  - post-training
draft: false
description: 마이크로소프트 Agent Lightning v1.0 논문 정리. 하네스가 환경 루프를 소유하고 트레이너는 LLM 요청-응답만 보는 harnessed agentic RL의 구조, 3,500줄 구현, SWE-bench Verified 41.8%→56.4% 결과까지 핵심만 담았습니다.
---

## 결론 먼저

Agent Lightning v1.0(arXiv 2608.17528, Microsoft, 2026-08-18)은 <span style="background-color: #fff59d"><strong>에이전트 하네스가 환경 상호작용 루프를 직접 소유하고, RL 트레이너는 LLM 요청-응답 쌍만 관찰하는</strong></span> 구조를 표준화한 프레임워크입니다. 논문은 이 방식을 <span style="background-color: #fff59d"><strong>harnessed agentic RL</strong></span>.

핵심 수치입니다.

| 항목 | 값 |
| --- | --- |
| 코드 규모 | 약 3,500줄 |
| 학습 데이터 | 6K 예제 |
| SWE-bench Verified | 41.8% → 56.4% (+14.6pt) |
| 대상 모델 | Qwen3.5-9B |
| 학습 속도 | 동기 대비 약 2배(collocated async) |

6K 예제와 적은 컴퓨트만으로 <span style="background-color: #fff59d"><strong>14.6포인트를 올렸다는</strong></span> 점이 이 논문의 실용적 임팩트입니다.

## 기존 agentic RL과 뭐가 다른가

기존 방식에서는 트레이닝 엔진이 환경 루프를 돌렸습니다. 하네스는 <span style="background-color: #fff59d"><strong>배포 시점의 실행 장치</strong></span>였고, 학습과는 분리되어 있었습니다. 하네스는 배포 시점의 실행 장치였고, 학습과는 분리되어 있었습니다.

| 구분 | 기존 agentic RL | harnessed agentic RL |
| --- | --- | --- |
| 상태 | 환경 | 하네스 + 환경 |
| 모델 입력 | 연속 토큰 히스토리 | 호출 단위 프롬프트 |
| 에이전트 구성 | 단일 ReAct 에이전트 | 멀티에이전트, 서브에이전트, 핸드오프 |
| 샘플 단위 | 롤아웃 1개 = 샘플 1개 | 롤아웃이 동적 샘플 여러 개로 확장 |

하나의 롤아웃이 여러 LLM 호출로 나뉘면, 토큰 경계가 어긋나는 <span style="background-color: #fff59d"><strong>retokenization</strong></span>, 호출들을 어떻게 묶을지 <span style="background-color: #fff59d"><strong>sample merging</strong></span>, 이점 계산, loss 정규화, 스케줄링 문제가 전부 새로 생깁니다. 논문은 이 다섯 가지를 하네스형 RL의 실질적 난제로 정리합니다.

원래 Agent Lightning이 제안한 LLM 엔드포인트 프록시 방식은 <span style="background-color: #fff59d"><strong>verl Uni-Agent, AReaL 2.0, slime, Polar</strong></span> 등 후속 프레임워크가 따라갔습니다. v1.0은 그 접근을 정식 명명하고 <span style="background-color: #fff59d"><strong>재현 가능한 파이프라인</strong></span>로 만든 버전입니다.

## 핵심 설계

- API Gateway: 하네스가 그대로 붙는 접점. <span style="background-color: #fff59d"><strong>롤아웃과 가중치 업데이트가 한 GPU 풀을 시분할로 공유</strong></span>하도록 추론 허가를 조율합니다.
- Rollout Controller: Kubernetes 잡/로컬 프로세스로 돌아가는 에이전트 실행 상태를 게이트웨이와 조정합니다.
- Rollout-level Advantage + Rollout-level Norm: 샘플 수가 롤아웃마다 다를 때 <span style="background-color: #fff59d"><strong>롤아웃 단위로 이점을 주고 정규화하는</strong></span> 조합이 검증에서 가장 안정적이었습니다.
- Collocated async RL: 동기식 대비 <span style="background-color: #fff59d"><strong>end-to-end 약 2배 속도</strong></span>를 냈고 GPU도 덜 썼습니다.

## 결과

<span style="background-color: #fff59d"><strong>코딩 에이전트 RL 파이프라인 전체를 공개</strong></span>했고, Qwen3.5-9B 기준 SWE-bench Verified가 <span style="background-color: #fff59d"><strong>41.8%에서 56.4%로 14.6포인트 상승</strong></span>했습니다. <span style="background-color: #fff59d"><strong>명령 이행 에이전트, 검색 에이전트</strong></span> 학습 다이내믹스도 함께 보고합니다.

기준일: 2026-08-29, arXiv v1 기준.

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 출처

- 논문: [Agent Lightning v1.0: Towards Harnessed Agentic RL](https://arxiv.org/abs/2608.17528)
- HTML 전문: https://arxiv.org/html/2608.17528v1
- DOI: https://doi.org/10.48550/arXiv.2608.17528

![기존 agentic RL과 harnessed agentic RL 비교](/images/2026-08-29-agent-lightning-v1-harnessed-agentic-rl/agl-lite-teaser-0814.png)

## 자주 묻는 질문

### harnessed agentic RL이 기존 agentic RL과 다른 점은 무엇인가요?

하네스가 환경 상호작용 루프를 소유하고, 트레이너는 LLM 요청-응답 시퀀스만 관찰합니다. 기존 방식은 트레이닝 엔진이 루프를 직접 돌렸습니다.

### Agent Lightning v1.0의 구현 규모는 어느 정도인가요?

약 3,500줄의 가벼운 프레임워크이고, 임의의 에이전트 하네스를 붙일 수 있습니다.

### SWE-bench 성능은 얼마나 올랐나요?

Qwen3.5-9B 기준 SWE-bench Verified 41.8%에서 56.4%로, 14.6포인트 절대 상승했습니다. 학습에는 6K 예제만 사용했습니다.
