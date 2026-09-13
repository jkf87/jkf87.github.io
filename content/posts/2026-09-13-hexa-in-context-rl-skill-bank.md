---
title: "LLM 에이전트를 학습 없이 강화학습처럼 만드는 방법: HExA 논문 정리"
date: 2026-09-13
tags:
  - llm
  - agent
  - reinforcement-learning
  - in-context-learning
  - skill-library
  - arxiv
draft: false
description: "가중치 업데이트 없이 에이전트 경험을 스킬 뱅크로 증류해 재사용하는 인컨텍스트 강화학습 프레임워크 HExA(arXiv 2606.29315)를 정리했습니다."
---

에이전트가 어떤 일을 하다가 실패합니다. 보통은 그 실패가 그 에피소드와 함께 사라지죠. 그런데 어떤 팀은 그 실패를 모아서 다음 에피소드에 도구로 쓰는 겁니다. 이게 HExA의 출발점입니다.

## 결론 먼저

HExA는 <span style="background-color: #fff59d"><strong>가중치 업데이트 없이 에이전트 경험을 스킬 뱅크로 증류해 재주입하는 인컨텍스트 강화학습 프레임워크</strong></span>입니다. 논문 실험에서 Qwen-2.5-3B의 catapult 해결률이 사실상 0%에서 54%로 올랐고, 동일 샘플 예산에서 GRPO 파인튜닝보다 sample efficiency가 좋았습니다.

| 항목 | 내용 |
| --- | --- |
| 프레임워크 | HExA (Hierarchical Experimentalist Agents) |
| 방식 | training-free 인컨텍스트 RL (파라미터 업데이트 없음) |
| 구성 | actor(실험) + evolver(스킬 증류) + retriever(재주입) |
| 검증 환경 | InterPhyre 물리 퍼즐 8레벨, 레벨당 50 seed |
| 대표 수치 | catapult 67.3±9.3% vs ReAct 8.0% (Claude Sonnet) |
| GRPO 비교 | 50 seed에서 down_to_earth 24% vs 20%, two_body 14% vs 6% |
| 소스 | arXiv 2606.29315 |

기준일: 2026-09-13, 논문 v1 기준입니다.

## 무슨 일이 벌어지나

actor가 환경을 실험합니다. evolver가 성공/실패 궤적을 대조해서 스킬을 뽑아냅니다. retriever가 다음 에피소드에 그 스킬을 넣어줍니다. 이 루프가 돌면서 에이전트가 경험을 쌓는 구조입니다.

![HExA 프레임워크 개요](/images/2026-09-13-hexa-in-context-rl-skill-bank/fig-1-p2.png)

Figure 1. HExA 프레임워크 개요. 출처: arXiv 2606.29315 Figure 1.

증류는 <span style="background-color: #fff59d"><strong>2단계 대비 분석과 실패 분석</strong></span>으로 수행됩니다. 고보상 에피소드와 저보상 에피소드를 나란히 놓고 차이를 뽑아내는 방식이에요.

![actor–evolver–retriever 루프](/images/2026-09-13-hexa-in-context-rl-skill-bank/fig-2-p4.png)

Figure 2. 스킬 뱅크 학습 루프. 출처: arXiv 2606.29315 Figure 2.

## 숫자로 보는 성장

Qwen-2.5-3B가 catapult에서 <span style="background-color: #fff59d"><strong>0%에서 54%로</strong></span> 올라갑니다. Claude Sonnet은 catapult에서 67.3±9.3%를 기록합니다. ReAct는 8.0%였죠.

| 모델 | 레벨 | ReAct | HExA |
| --- | --- | --- | --- |
| Qwen-2.5-3B | down_to_earth | 8.0% | 24.0% |
| Qwen-2.5-3B | two_body_problem | 6.0% | 14.0% |
| Qwen-2.5-7B | down_to_earth | 62.0% | 72.0% |
| Qwen-2.5-7B | two_body_problem | 18.0% | 34.0% |
| GPT-OSS-120B | catapult | 0.0% | 54.0% |

즉 <span style="background-color: #fff59d"><strong>강한 모델 전용이 아니라 약한 에이전트를 끌어올리는 데도 유효</strong></span>합니다.

![catapult 성능 비교](/images/2026-09-13-hexa-in-context-rl-skill-bank/fig-5-p10.png)

Figure 5. 보상 가이드 스킬 축적 효과. 출처: arXiv 2606.29315 Figure 5.

GRPO와 50 seed 예산을 맞춰 비교하면 down_to_earth 24% vs 20%, two_body_problem 14% vs 6%로 HExA가 앞섭니다. 논문은 이 차이를 <span style="background-color: #fff59d"><strong>스킬이 컨텍스트로 즉시 재사용되는 구조</strong></span> 때문이라고 설명합니다. 그래디언트 기반은 롤아웃을 쌓아야 같은 지식이 가중치에 반영되니까요. 롤아웃을 충분히 확보한 GRPO는 결국 따라잡는다고 논문이 명시합니다.

## 어디에 쓸 수 있나

파인튜닝 예산이 없는 팀에 유용합니다. 스킬 뱅크가 <span style="background-color: #fff59d"><strong>자연어라 읽고 편집할 수 있고, 모델을 바꿔도 가져갈 수 있다</strong></span>는 게 실무적 이점입니다. 다만 실험이 물리 퍼즐로 좁다는 점은 감안해야 합니다. 논문도 <span style="background-color: #fff59d"><strong>초기 부트스트랩은 인컨텍스트, 후속 최적화는 그래디언트 RL로 이어붙이는 조합</strong></span>을 권장합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### HExA는 모델 파인튜닝을 하나요?

아니요. 가중치 업데이트가 전혀 없는 training-free 방식입니다.

### GRPO보다 무조건 낫나요?

아니요. 동일 샘플 예산에서 우위이나, 충분한 롤아웃을 확보한 GRPO가 환경 보상 직접 최적화로 따라잡을 수 있습니다.

### 스킬 뱅크는 어떤 형태인가요?

자연어 전략과 실수 목록의 구조화된 모음입니다.

### 검증 환경은 무엇인가요?

InterPhyre 물리 퍼즐 8레벨, 레벨당 50 seed입니다. Claude Sonnet, Qwen-2.5-3B/7B, GPT-OSS-120B로 테스트했습니다.

## 참고

- 논문: [arXiv:2606.29315](https://arxiv.org/abs/2606.29315)
- HTML 버전: [arxiv.org/html/2606.29315v1](https://arxiv.org/html/2606.29315v1)
