---
title: "LLM Judge는 평균 취향만 맞춤 — 개인 평가자 시뮬레이션 PersonaJudge 결과"
date: 2026-08-21
tags:
  - LLM-as-Judge
  - preference-learning
  - AI-evaluation
  - personalization
  - human-feedback
  - agent-evaluation
description: "평균 점수를 잘 맞추는 Judge가 특정 평가자의 취향까지 맞추는 건 아님. 판단 라벨과 사후 이유를 함께 넣은 개인화 데모가 클릭 로그보다 셌다는 결과를 평가 시스템 설계 관점으로 정리함."
---

LLM-as-Judge를 쓰면 평가 비용은 내려가지만 하나가 자주 빠짐. 평균 점수를 잘 맞추는 Judge가 특정 평가자의 취향까지 맞춘다는 보장이 없다는 것임. PersonaJudge가 이 문제를 정면으로 다룸. 원문은 [arXiv:2607.05742](https://arxiv.org/abs/2607.05742).

1. 배경. 기존 LLM-as-Judge는 여러 사람의 선호를 합쳐 consensus label을 만드는데 그 과정에서 평가자 사이의 차이는 평균 속으로 사라짐. 근데 disagreement가 항상 노이즈가 아님. 평가자가 서로 다른 기준을 적용했다면 그 차이 자체가 평가 대상임. 어떤 사람은 조심성을, 어떤 사람은 직접성을 높게 보고 어떤 사람은 둘 다 애매하면 Neutral을 자주 고름.

![](/images/2026-08-21-personajudge-individual-preference-eval/gifs/judging-skeptical-man.gif)

2. 설정. 특정 평가자 한 명이 새 pairwise task에서 Prefer A, Neutral, Prefer B 중 무엇을 고를지 맞추는 문제임. 데모에 세 가지 신호가 들어감. Judgment(과거에 고른 라벨), Interface Telemetry(클릭·dwell time·reveal 기록), Retrospective Reasoning(판단 뒤 남긴 사후 이유)임. 새 학습 모델이 아니라 evaluator-specific demonstration을 넣은 in-context learning 실험이라는 점이 실무적임.

![PersonaJudge 워크플로우](/images/2026-08-21-personajudge-individual-preference-eval/personajudge-figure-1-workflow.png)

3. Neutral을 독립된 세 번째 라벨로 보존한 설계가 좋음. 흔한 preference 데이터셋은 A/B 이진으로 밀어붙이는데 실제 평가에서는 "둘 다 비슷하다", "둘 다 문제 있다", "기준상 결정 못 하겠다"가 자주 나옴. 모델 호출도 두 단계로 나눠서 먼저 preference를 낼지 Neutral을 고를지 맞추고, preference가 있다고 판단되면 방향을 다시 맞춤.

4. 데이터. Anthropic HH에서 helpfulness·harmlessness 평가 태스크를 뽑아서 annotator 32명, 데이터셋당 evaluator 21명, evaluator당 100개 판단으로 총 4,200개 preference judgment을 모았음. 라벨만이 아니라 판단 결과·행동 흔적·사후 설명이 같은 평가자 단위로 묶인 게 차별점임.

5. 결과 1. Base Judge 대비 개인화 데모는 Harmlessness +2.8%p, Helpfulness +1.4%p임. 평균 폭은 크지 않은데, 다른 evaluator의 데모를 넣은 컨트롤과 비교하면 차이가 선명함(0.477 vs 0.450, 0.515 vs 0.471). "그 평가자의 과거 판단"이 예시 이상의 신호를 줬다는 뜻임.

6. 결과 2가 실무적으로 제일 중요함. 가장 좋은 조합은 Judgment + Retrospective Reasoning(Harmlessness 0.505, Helpfulness 0.537)이고, Judgment + Interface Telemetry는 판단 라벨만 넣은 것보다 나쁨(0.457). 클릭·dwell time 같은 raw event는 평가 의도와 바로 이어지지 않음. 오래 읽어서 확신한 건지 헷갈려서 오래 본 건지 같은 dwell time이라도 의미가 다르기 때문임. 반면 사후 reasoning은 이 평가자가 어떤 기준을 봤는지가 텍스트로 그대로 들어있음. 비용이 item당 약 5배 들어도 fidelity가 중요한 고위험 평가에서는 낼 이유가 있다는 계산임.

7. 결과 3. 최고 조합(Claude 3.5 Sonnet + 8-shot J+RR)은 Harmlessness 0.581로 Base 대비 +9.9%p, Helpfulness +5.8%p임. 그리고 shot 수는 1에서 4까지 오를 때 좋아지다가 plateau가 나옴. 좋은 reasoning 데모 4개 안팎이면 개인화 Judge 품질이 꽤 오른다는 것임. 모든 사용자에게 긴 설문을 받는 것보다 실제 평가 사례 몇 개에서 "왜 좋았는지/싫었는지"를 짧게 받아 저장하는 게 효율적이라는 뜻임.

8. 어려운 평가자의 특성도 명확함. Neutral을 자주 고르는 평가자일수록 시뮬레이션 정확도가 크게 떨어짐(Helpfulness r=-0.894). consensus에서 자주 벗어나는 평가자일수록 정확도가 낮음(r=-0.463~-0.676). Neutral 사용 성향 자체는 태스크를 바꿔도 안정적(r=0.728)인데 simulatability는 안정적이지 않음. 판단 습관은 남지만 그 습관이 어느 태스크에서 어려움으로 변하는지는 달라진다는 것임.

9. 논문의 정직함이 좋음. consensus와 다른 라벨을 고른 deviation item만 보면 consensus predictor는 원리상 못 맞추는데 PersonaJudge는 0.36 안팎을 맞춤. 대단한 숫자는 아니지만 group average에서 절대 나올 수 없는 신호임. 결론도 대체가 아니라 보완이라고 못박음. 각 개인의 "가장 자주 고르는 라벨" baseline을 안정적으로 넘지 못했다는 것임.

10. 내 에이전트 평가 설계에 적용한 것. 첫째, 사용자 취향을 "간결한 답변 선호함" 같은 프로필 문장으로만 저장하지 않고 좋아한/싫어한 사례 3-5개씩에 이유 한두 문장을 붙여 저장함. 둘째, 평가 라벨에 pass/fail만 두지 않고 "불충분, 애매함, 재확인 필요" 같은 회색 라벨을 둠. 셋째, raw telemetry는 Judge 프롬프트에 바로 안 넣고 행동 요약으로 변환한 뒤 실험함. 넷째, consensus와 다른 판단 사례를 별도 eval set으로 만들어서 개인화의 본게임을 그쪽에서 평가함.

11. 문제제기. HH pairwise preference 한정이라 실제 에이전트 태스크(웹 탐색, 파일 수정, 장기 상태) 검증이 아니고 annotator 32명이라 일반 사용자 대표성이 약함. 사후 reasoning은 그럴듯한 이유 만들기일 수 있어서 "진짜 내면을 읽었다"로 받아들이면 안 되고, telemetry·reasoning 수집의 privacy 문제도 논문이 스스로 명시함.

12. 결론. 좋은 Judge는 평균 인간을 흉내 내는 모델이 아니라 누구의 기준을 평가 기준으로 삼고 있는지 드러내는 시스템임. 에이전트를 실무에 붙이면 사용자는 결국 "정답은 맞는데 내 스타일은 아니야"라고 말함. 그 문장이 개인화 평가의 진짜 문제이고, 시작점은 라벨이 아니라 판단 사례와 이유를 같이 저장하는 것임.

![](/images/2026-08-21-personajudge-individual-preference-eval/gifs/unimpressed-office-skeptic.gif)
