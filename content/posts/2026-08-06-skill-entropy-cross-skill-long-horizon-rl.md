---
title: "Skill Entropy: LLM이 스킬을 바꾸는 순간 성능이 무너지는 이유"
date: 2026-08-06
tags:
  - agent
  - long-horizon
  - reasoning
  - reinforcement-learning
  - LLM
  - skill-switching
  - benchmark
  - RL
  - loop
  - automation
authors:
  - conanssam
---

수학 풀고 → 그 결과로 일정 짜고 → 그 일정으로 정보 추출하기. 이렇게 스킬이 바뀌는 순간 LLM 정확도가 떨어집니다. Princeton 팀이 이 문제를 "Skill Entropy"로 정량화하고, RL 훈련 신호로 썼습니다.

핵심은 이겁니다: 개별 스킬 점수는 높은데, 스킬을 전환하는 순간 정확도가 −4~−13% 떨어집니다. 그리고 스킬이 멀수록(예: 수학→창작) 전환 비용이 큽니다.

## 스킬 전환 난이도 정의

스킬 전환 난이도를 하나의 숫자로 표현합니다. 기준 모델(Claude-opus-4.7)으로 단일 스킬 정확도와 2-스킬 체인 정확도를 비교합니다.

![](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/fig-2-p5.png)

Figure 2에서 보면, Planning → Information Extraction 전환이 가장 어렵습니다. Science는 단일 도메인에서는 쉬운데 스킬 전환 난이도는 최상위입니다. 도메인 난이도와 스킬 전환 난이도가 다릅니다.

## Skill2-Bench 구성

558개 스킬, 9개 도메인으로 벤치마크를 만들었습니다.

| 도메인 | 시드 데이터 | 검증 가능 | 스킬 수 |
|---|---|---|---|
| Math | OpenR1-Math | ✓ | 186 |
| Science | MMLU-Pro | ✓ | 137 |
| Coding | LiveCodeBench | ✓ | 46 |
| Logic | ZebraLogicBench | ✓ | 14 |
| Information Extraction | WikiTable, WebSRC | ✓ | 92 |
| Planning | NaturalPlan | ✓ | 34 |
| Creative Writing | — | × | 12 |
| Context Retrieval | — | × | 12 |
| Instruction Following | — | × | 25 |

태스크 하나 = 2~10단계 시퀀스. 각 단계가 다른 도메인의 스킬을 요구하고, 앞 단계 정답에 의존합니다. 태스크 난이도는 skill entropy 스칼라값으로 3단계(Low/Medium/High)로 나눕니다.

## 평가 결과: 스킬 전환 격차

![](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/table-2-p7.png)

12개 모델(프론티어 8 + 오픈소스 4)을 평가했습니다.

- skill entropy가 높아질수록 정확도가 거의 단조 감소합니다
- 같은 스킬이어도 cross-skill 태스크 안에서 쓰이면 단독 풀이보다 −4~−13% 떨어집니다
- 주요 실패 모드: 뒷단계에서 앞 단계의 스킬과 답변 양식을 그대로 재사용합니다. 전환을 안 합니다

## Skill-Entropy RL: 전환 난이도를 훈련 신호로

여기서 skill entropy를 벤치마크 점수에서 훈련 보상으로 바꿉니다.

모델이 각 단계의 정답 전에 스킬 라벨을 먼저 예측합니다. 보상은 두 성분의 합입니다:

1. 단계별 정답 정확도
2. 예측 스킬 시퀀스와 정답 스킬 시퀀스의 정렬도 (skill-entropy reward)

![](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/fig-1-p2.png)

Qwen3-4B-Instruct 기준 Skill2-Bench 점수가 34.4% → 68.4%로 올랐습니다. Qwen3-1.7B는 14.6% → 40.1%.

OpenR1-Math 같은 기존 훈련 데이터에도 그대로 적용할 수 있습니다. 스킬 라벨만 있으면 되니까요.

## 에이전트 루프와의 연결

LLM이 각 스킬을 잘한다고 해서 긴 호라이즌 태스크를 잘하는 게 아닙니다. 스킬 사이의 "전환 비용"이 구조적으로 존재하고, 이걸 측정하고 훈련해야 합니다.

에이전트 루프에서 도메인이 바뀌는 순간(검색→코딩→요약)이 같은 문제입니다. skill entropy는 그 전환 지점을 정량화한 첫 프레임워크입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [arXiv:2608.05139](https://arxiv.org/abs/2608.05139)
코드: [github.com/Gen-Verse/Skill-Entropy-RL](https://github.com/Gen-Verse/Skill-Entropy-RL)
데이터: [huggingface.co/datasets/Gen-Verse/Skill2-Bench](https://huggingface.co/datasets/Gen-Verse/Skill2-Bench)