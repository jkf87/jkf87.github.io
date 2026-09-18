---
title: "스킬은 각각 잘하는데 스킬이 바뀌는 순간 무너짐 — Skill Entropy 측정과 훈련법"
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
description: 수학→계획→추출처럼 스킬이 바뀌는 순간 정확도가 4-13% 떨어짐. 전환 난이도를 skill entropy로 정량화하고 RL 보상으로 쓴 연구를 에이전트 루프 설계 관점으로 정리함.
---

수학 풀고 → 그 결과로 일정 짜고 → 그 일정에서 정보 추출하기. 이렇게 스킬이 바뀌는 순간 LLM 정확도가 떨어짐. Princeton 팀이 이 현상을 "Skill Entropy"로 정량화하고 훈련 신호로 썼음. 원문은 [arXiv:2608.05139](https://arxiv.org/abs/2608.05139).

1. 핵심 발견. 개별 스킬 점수는 높은데 스킬을 전환하는 순간 정확도가 -4~-13% 떨어짐. 그리고 스킬이 멀수록(수학→창작 같은 경우) 전환 비용이 커짐. 스킬별 성적과 롱호라이즌 성적이 다른 이유를 숫자로 보여준 첫 프레임워크임.

![스킬 전환 시 정확도 하락](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/fig-1-p2.png)

2. 측정 방법. 기준 모델(Claude-opus-4.7)로 단일 스킬 정확도와 2-스킬 체인 정확도를 비교해서 스킬 전환 난이도를 하나의 숫자로 만듦. 흥미로운 점은 Planning → Information Extraction 전환이 가장 어렵고 Science는 단일 도메인에선 쉬운데 전환 난이도는 최상위라는 것임. 도메인 난이도와 스킬 전환 난이도가 다른 축이라는 뜻임.

3. Skill2-Bench 구성. 558개 스킬, 9개 도메인(Math 186, Science 137, Information Extraction 92, Coding 46 등)으로 벤치마크를 만듦. 태스크 하나는 2-10단계 시퀀스인데 각 단계가 다른 도메인 스킬을 요구하고 앞 단계 정답에 의존함. 태스크 난이도는 skill entropy 스칼라로 Low/Medium/High 3단계임.

![Skill2-Bench 구성](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/fig-2-p5.png)

4. 12개 모델(프론티어 8 + 오픈소스 4) 평가 결과. skill entropy가 높아질수록 정확도가 거의 단조 감소함. 주요 실패 모드가 적나라함. 뒷단계에서 앞 단계의 스킬과 답변 양식을 그대로 재사용함. 전환 자체를 안 하는 것임. 내 에이전트 로그에서 "요약하다가 코딩 양식으로 대답하는" 패턴과 정확히 같음.

![](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/gifs/confused-side-eye-chloe.gif)

5. 이걸 훈련 신호로 바꾼 게 두 번째 기여임. 모델이 각 단계 정답 전에 스킬 라벨을 먼저 예측하게 하고, 보상을 단계별 정확도와 예측 스킬 시퀀스-정답 시퀀스 정렬도의 합으로 줌. 스킬 전환을 명시적 예측 문제로 만든 것임.

6. 결과. Qwen3-4B-Instruct 기준 Skill2-Bench가 34.4%에서 68.4%로 오름. Qwen3-1.7B는 14.6%에서 40.1%로 오름. 기존 훈련 데이터(OpenR1-Math 등. OpenR1-Math는 강한 추론 모델이 푼 수학 풀이 과정을 정리해 둔 대규모 수학 훈련 데이터셋임)에도 스킬 라벨만 있으면 그대로 적용 가능함.

![RL 훈련 후 성능 향상](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/fig-4-p10.png)

![](/images/2026-08-06-skill-entropy-cross-skill-long-horizon-rl/gifs/victory-arrested-development.gif)

7. 내 에이전트 루프 설계에 바로 적용한 것. 첫째, 도메인이 바뀌는 단계(검색→코딩→요약)마다 "지금 필요한 스킬이 무엇인지"를 먼저 명시하게 프롬프트를 고정함. 스킬 라벨 예측을 훈련으로 넣은 것과 같은 효과를 추론 시점 컨텍스트로 근사하는 것임. 둘째, 앞 단계의 출력 양식이 뒷단계로 새어들어가는 걸 막으려고 단계별 출력 포맷을 강제로 분리함. 재사용이 아니라 전환을 해야 하니까임.

8. 문제제기. 스킬 라벨이 필요하다는 게 실무 데이터에서의 제약임. 스킬 시퀀스를 손으로 라벨링하기 어려운 복잡한 업무에는 바로 적용이 어려움. 그리고 전환 난이도 기준이 특정 기준 모델(claude-opus-4.7) 종속이라 모델마다 다시 재야 정확함.

9. 결론. "LLM이 각 스킬을 잘한다"와 "긴 호라이즌 태스크를 잘한다"는 다른 문제이고, 그 사이에는 전환 비용이라는 구조적 간극이 있음. 그 간극을 측정하고(벤치마크) 좁히고(RL 보상) 대응하는(루프 설계) 세 가지 도구를 한 번에 준 논문임. 코드는 [GitHub](https://github.com/Gen-Verse/Skill-Entropy-RL), 데이터는 [HuggingFace](https://huggingface.co/datasets/Gen-Verse/Skill2-Bench)에 공개돼 있음.

스킬 전환 지점을 관리하는 루프 설계 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 해볼 수 있음.
