---
title: "AI가 AI를 학습시키는 시대, 정작 부족한 건 '전략을 다시 보는 힘'"
date: 2026-08-21
tags: [agent, LLM, post-training, self-improvement, AI-for-AI, strategy]
draft: false
---

에이전트가 코드를 쓰고, 학습을 띄우고, 체크포인트를 평가한다. 마치 스스로 진화하는 기계처럼 보인다. 근데 정말 그럴까?

## 이 논문이 확인한 것

논문 "What is Missing from AI Post-Training AI: An Empirical Analysis"(arXiv:2608.19072)는 이 화려한 그림에 냉정한 질문을 던진다. 에이전트가 부족한 건 경험일까, 가이드일까, 추론 컴퓨트일까?

답은 셋 다 아니었다. <span style="background-color: #fff59d"><strong>실행 중에 전략 자체를 다시 평가하는 메커니즘이 없다</strong></span>는 것이다. 공개된 포스트트레이닝 트레이토리 코퍼스를 분석한 결과, <span style="background-color: #fff59d"><strong>전략은 맨 처음에 고정되고 남은 예산 전부가 그 전략 안의 국소 조정에 쓰인다</strong></span>는 패턴이 태스크와 무관하게 반복되었다. 인접 트레이토리 쌍 <span style="background-color: #fff59d"><strong>3,557개</strong></span>에서 전략 변경으로 인정된 사례는 <span style="background-color: #fff59d"><strong>16건 수준</strong></span>이었다.

![](/images/2026-08-21-strategy-lockin-post-training-agents/fig-1-p2.png)
*Figure 1. 에이전트는 포스트트레이닝 파이프라인을 실행하지만 대부분의 트레이토리는 고정된 전략 안에 머문다. (arXiv:2608.19072 Figure 1)*

## 실험 설계와 숫자

논문은 전략이 못 바뀌는 이유를 세 가지로 가정하고 점점 강도를 높이는 인터벤션으로 테스트한다.

### 1. 경험 스캐폴드

경험 기반 스캐폴드를 얹자 <span style="background-color: #fff59d"><strong>GSM8K +12.6점, HumanEval +40.8점</strong></span>으로 실행 성과는 전반적으로 올라갔다. 근데 전략 지표는 <span style="background-color: #fff59d"><strong>정적 그대로</strong></span>였다.

![](/images/2026-08-21-strategy-lockin-post-training-agents/fig-3-p7.png)
*Figure 3. 경험 기반 프레임워크의 학습 곡선. 성과 개선과 전략 수정은 별개로 움직인다. (arXiv:2608.19072 Figure 3)*

### 2. 인간 가이드

사람이 초기 전략을 직접 지시하면 <span style="background-color: #fff59d"><strong>초기 전략은 실제로 바뀐다</strong></span>. 그런데 학습이 시작되면 에이전트는 <span style="background-color: #fff59d"><strong>다시 국소 조정 루프로 빠진다</strong></span>.

![](/images/2026-08-21-strategy-lockin-post-training-agents/fig-4-p6.png)
*Figure 4. 실행 수준 제안은 수용하면서 전략 수준 반영은 안 되는 비대칭. (arXiv:2608.19072 Figure 4)*

### 3. 추론 컴퓨트

추론 컴퓨트를 늘리면 쉬운 태스크에서는 이득이 있는데, <span style="background-color: #fff59d"><strong>가장 어려운 태스크에서는 이득이 거의 없다</strong></span>는 결과가 나왔다.

## 트레이토리에서 반복되는 패턴

![](/images/2026-08-21-strategy-lockin-post-training-agents/fig-2-p6.png)
*Figure 2. 트레이토리 전 구간의 에이전트 행동 분포. 대부분이 실행 수준 활동이다. (arXiv:2608.19072 Figure 2)*

원문 근거를 정리하면 이렇다.

- 경험 스캐폴드: GSM8K +12.6, HumanEval +40.8, 전략은 정적
- 인간 가이드: 초기 전략 리다이렉션 성공, 학습 시작 후 국소 루프 복귀
- 추론 컴퓨트: 쉬운 태스크 이득, <span style="background-color: #fff59d"><strong>최난도 태스크 이득 거의 0</strong></span>

여기에 내 해석을 붙이면 이건 도구 문제보다 운영 문제에 가깝다. <span style="background-color: #fff59d"><strong>전략 재평가를 담당하는 외부 루프를 누가 언제 도는지 정하지 않으면</strong></span> 에이전트는 계속 실행 모드에 머문다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 남는 정리

세 인터벤션 모두 실행 개선을 보여줬고 전략 수정은 끝내 일어나지 않았다. <span style="background-color: #fff59d"><strong>AI-for-AI의 다음 병목은 메타 판단 루프다</strong></span>. 전략을 다시 보는 장치가 없으면 에이전트는 잘못 고정된 전략을 아주 능숙하게 밀어붙일 뿐이다.
