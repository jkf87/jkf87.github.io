---
title: "Mechanist: AI가 AI의 메커니즘을 스스로 발견하는 에이전트 시스템"
date: 2026-08-14
tags:
  - agent
  - interpretability
  - LLM
  - mechanistic
  - safety
  - automation
  - harness
  - loop
---

AI 모델은 하루가 다르게 똑똑해지는데, 정작 그 모델이 왜 특정 답을 내놓는지 아무도 모르는 상황이 점점 심해지고 있습니다. 저장강소대학교 zjunlp 연구팀이 이 문제에 에이전트를 투입했습니다. 이름은 Mechanist. AI를 "과학 도구"로 써서 AI 자체의 메커니즘을 발견하는 자율 에이전트 시스템입니다.

## "AI가 AI를 해석한다"가 무슨 뜻인가

기존 자동화 연구는 "AI로 과학 실험을 돌린다"였습니다. 약물 발견, 재료 설계, 코딩 — 대상이 자연계나 소프트웨어였죠. Mechanist의 대상은 AI 모델 자체입니다. GPT든 Pythia든, 그 모델 내부에서 무슨 일이 일어나는지를 에이전트가 가설부터 세우고 실험까지 돌립니다.

![Mechanist와 기존 AI Scientist의 비교](/images/2026-08-14-mechanist-agentic-interpretability-discovery/fig-1-p2.png)

## 4단계 자율 연구 루프

Mechanist의 핵심은 가설-실험-검증-반복 루프입니다:

- **가설 에이전트**: 13,000편 해석 논문 + 4,300만편 다학제 논문에서 레퍼런스를 끌어와 연구 가설을 생성합니다.
- **실험 에이전트**: 32개 메커니즘 분석 도구(activation patching, SAE, circuit discovery 등) 중 적절한 것을 골라 코드를 짜고 실행합니다.
- **검증 에이전트**: 데이터 누수, 메트릭 조작, 결과 신뢰성을 체크합니다.
- **반복 에이전트**: GPT-5.4의 독립 리뷰와 함께 어디서 문제가 생겼는지 진단하고 되돌려 보냅니다.

이 루프가 흥미로운 이유는 메모리 구조에 있습니다. 에이전트들이 대화 히스토리에 의존하지 않고, 단계별 산출물을 파일로 저장해서 통신합니다. 그래서 중간에 끊겨도 이어서 할 수 있고, 다음 연구 라운드에서 확정된 결론은 반복하지 않습니다.

## Claude Code를 이긴 도메인 지식

가장 흥미로운 결과는 벤치마크입니다. 16편 최신 논문을 재현하게 해본 결과, 사람 전문가 평가에서 Mechanist가 Claude Code(Opus 4.8)보다 모든 차원에서 9~13%p 앞섰습니다.

![연구 영역별 재현 신뢰성](/images/2026-08-14-mechanist-agentic-interpretability-discovery/fig-10-p17.png)

왜 Claude Code가 졌을까? 도메인 지식 부족입니다. steering 실험에서 올바른 방법(Recursive Feature Machines) 대신 익숙한 방법(Contrastive Activation Addition)을 쓰거나, intervention 강도를 데이터로 보정하지 않고 찍은 값으로 고정했습니다. Mechanist는 도구 라이브러리에 명시된 지침을 따라서 이런 실수를 피합니다.

![시스템 간 신뢰성 비교](/images/2026-08-14-mechanist-agentic-interpretability-discovery/fig-12-p18.png)

## "안전한 데이터로 학습했는데 위험해졌다" — 다중 모달 서브리미널 러닝

Mechanist가 발견한 가장 충격적인 결과입니다.

서브리미널 러닝은 teacher 모델의 특성이 의미적으로 무관한 데이터를 통해 student에게 전이되는 현상입니다. 기존 연구는 텍스트 안에서만 확인됐습니다.

Mechanist는 이것을 모달리티를 넘나드는 현상으로 확장했습니다:

1. 실험실 안전에 대해 위험한 답을 주는 teacher 모델을 만듭니다
2. teacher의 답변 중 GPT-4o가 "안전"이라고 판정한 것만 걸러냅니다
3. 이 안전한 텍스트 데이터로 student를 파인튜닝합니다
4. 멀티모달 안전 질문(텍스트+이미지)을 던지면 → student의 위험 응답률이 48.6%

기준 모델이 20.3%인데 비하면 2.4배입니다. 학습 데이터는 전부 안전한 텍스트였는데도 말이죠.

이건 모델의 행동이 단일 모달리티 경계를 넘어서 전이된다는 것을 보여줍니다. 실제 실험실 환경에서 AI 안전 시스템에 이런 취약점이 있다면 상당히 위험합니다.

## 신념 메커니즘: 모델이 "믿는 것"을 찾아서

두 번째 사례에서 Mechanist는 언어 모델에서 "신념"을 처리하는 메커니즘을 분리해냈습니다.

![신념 상태 추론 메커니즘](/images/2026-08-14-mechanist-agentic-interpretability-discovery/fig-4-p7.png)

Personal-belief head(자기 신념)와 attributed-belief head(타인 신녑 추론)가 분리되어 있고, 이걸 Fisher information localization으로 찾아냅니다. 더 흥미로운 건 이 메커니즘을 조작할 수 있다는 점입니다. 경량 probe로 입력 컨텍스트를 분류해서, belief head의 기여도를 올리거나 내리면 모델의 정확도가 올라갑니다. 파라미터는 건드리지 않고 forward pass에서만 조정합니다.

## DNA 설계까지: 메커니즘을 알면 제어도 된다

세 번째 사례는 과학 파운데이션 모델(Evo2-7B)에서 생물학적 특성 메커니즘을 찾아서, 원하는 특성을 가진 DNA 시퀀스를 생성하도록 유도한 것입니다.

![DNA 시퀀스 설계](/images/2026-08-14-mechanist-agentic-interpretability-discovery/fig-5-p9.png)

기존 generate-and-rerank 방식(무작위로 많이 만들고 필터링) 대신, 메커니즘 수준에서 직접 조정합니다. 계산 비용을 크게 줄이면서도 목표 특성에 도달합니다.

## 지식 그래프: 13,000편에서 출발

![해석 가능성 지식 그래프](/images/2026-08-14-mechanist-agentic-interpretability-discovery/fig-6-p12.png)

Mechanist의 가설 생성 품질은 결국 지식 그래프에서 나옵니다. 기법-컴포넌트-태스크-발견을 그래프로 연결해 두니, "이 현상과 관련된 연구가 있는가"를 탐색할 수 있고, 아직 누구도 시도하지 않은 조합을 발견할 수도 있습니다.

## 이 연구가 중요한 이유

AI 모델 개발 속도가 이해 속도를 앞지르고 있습니다. 인간 연구자가 수동으로 메커니즘을 분석하는 동안 모델은 다음 세대로 넘어갑니다. Mechanist는 이 간극을 에이전트 루프로 좁히려는 시도입니다. 그리고 단순히 "설명하는" 것에 그치지 않고, 발견한 메커니즘으로 모델을 제어하고 개선하는 것까지 보여줬습니다.

논문: [arXiv:2608.12036](https://arxiv.org/abs/2608.12036)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
