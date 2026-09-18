---
title: "모델은 얼려두고 하네스만 진화시켜도 성능이 오름 — HSI 계층 자기개선"
date: 2026-08-13
tags:
  - agent
  - harness
  - LLM
  - self-evolution
  - self-improvement
  - frozen-model
  - BALROG
  - loop
  - automation
source: arxiv
source_url: https://arxiv.org/abs/2608.08466
authors:
  - conanssam
draft: false
description: 동결된 LLM 하나가 태스크 수행, 하네스 수정, 전략 수정 세 역할을 겸하는 계층 구조로 BALROG에서 큰 폭 향상. 하네스 진화가 커버 못 하는 두 경계까지 정리함.
---

모델 가중치를 안 바꾸고 하네스(프롬프트·도구·메모리·검증 로직)만 고쳐서 성능을 올릴 수 있는가. HSI가 그 실험을 했고 결과가 유의미했음. 원문은 [arXiv:2608.08466](https://arxiv.org/abs/2608.08466).

1. 구조는 세 계층임. Task Harness가 환경과 상호작용하며 태스크를 수행하고, Evolver가 평가 기반으로 태스크 하네스를 재작성하고, Meta-Evolver가 Evolver의 전략 코드 자체를 재작성함. 최상단에 동결된 외부 앵커를 둬서 무제한 자기 참조를 막음. 같은 동결 모델이 세 역할을 다 하는 게 포인트임.

![HSI 3계층 프레임워크(논문 Figure 1)](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/fig-1-p5.png)

![이게 피라미드인가](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/gifs/pyramid-scheme.gif)

2. 실험 설계의 디테일이 좋음. 백본은 DeepSeek-V4-Flash-Preview(동결)이고 태스크 수행 시 추론(thinking)을 OFF로 고정함. 성능 변화가 순수하게 하네스 개선에서 오는 걸 보장하는 장치임. 하네스 수정 시에만 thinking을 켬.

3. 결과. BabyAI 42.0→81.3(+39.3), Crafter 11.6→44.6(+33.0), TextWorld 40.0→65.0(+25.0), MiniHack 0.8→15.8임. TextWorld 65.0%는 Grok-4(62.9%)와 Claude-Opus-4.5-Thinking(59.0%)을 넘는 수치임. 같은 모델, 같은 추론 예산에서 하네스만 바꿔서 얻은 결과라는 게 의미임.

![하네스만 바꿔도 좋아짐](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/gifs/self-improvement.gif)

4. 메타 진화를 끄면 전 환경에서 떨어짐. TextWorld 65.0→46.0, MiniHack 15.8→5.8. 진화 전략 자체를 진화시키는 게 유효하다는 뜻임. 하네스 수정도 중요하지만 "어떻게 수정할지"의 원칙을 코드화해 재사용하는 계층이 별도로 필요하다는 것임.

5. 진화 궤적의 패턴이 실무 감각과 맞음. 초기엔 누락된 추상화를 발견함(보상 신호 명시적 노출, 인벤토리 상태 구조화, 행동-상태 정렬 개선). 중기엔 규칙 기반 제안·안전 제약 같은 구조화된 알고리즘 컴포넌트를 도입함. 후기엔 경쟁하는 설계를 다듬거나 가지치기함. 메타 진화기는 이 로컬 발견을 "원시 관찰보다 구조화된 상태 표현을 우선하라" 같은 재사용 가능한 휴리스틱으로 코드화함.

![Crafter 진화 궤적(논문 Figure 2)](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/fig-2-p11.png)

6. 일반화 검증도 정직함. 20% 홀드아웃에서 네비게이션 계열(BreakStop 0.98, GoTo 1.00)은 거의 완벽하게 전달되는데 다단계 제작(Make)은 0.56→0.36으로 떨어짐. 모델 자체 추론 능력이 부족한 태스크는 하네스 개선으로 커버가 안 된다는 경계가 명확히 드러남.

![BabaIsAI-Make 진화 궤적(논문 Figure 3)](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/fig-3-p12.png)

7. 두 가지 한계가 실험적으로 확인됨. 첫째, 피드백 한계. 보상이 희소한 환경(NLE)에선 진화가 작동하지 않음. 수정 방향을 찾을 신호 자체가 없기 때문임. 둘째, 백본 능력 한계. 동결 모델이 기본 역량이 안 되면 하네스 재설계로 못 넘음. 하네스 진화는 기존 능력을 체계적으로 끌어내는 메커니즘이지 강한 모델을 대체하는 게 아님.

8. 내 자동화에 적용할 것 세 가지. 첫째, 하네스 수정 기록을 "재사용 가능한 원칙"으로 별도 저장하는 메타 계층을 둠. 수정 자체는 자주 하지만 원칙을 안 쌓으면 매번 같은 실수를 반복함. 둘째, 태스크 수행과 하네스 수정을 분리된 실행으로 두고 수정 시에만 더 깊은 추론을 씀. 셋째, 보상 신호가 희소한 작업엔 하네스 진화 루프를 돌리지 않고 먼저 피드백 신호를 설계함. 신호가 없으면 진화도 없다는 게 이 논문의 경험칙임.

9. 문제제기. BALROG가 텍스트 게임 6종이라 실무 도메인 검증은 아니고, outer iteration 5회·80스텝 설정의 비용이 환경마다 어떻게 달라지는지도 불투명함. 그래도 "동결 모델 + 하네스 진화"로 프론티어급 점수를 낸 사례 자체가 방향성을 보여줌.

10. 결론. 모델을 바꿀 예산이 없을 때 선택지는 하네스임. 근데 그 하네스 수정도 원칙 축적 계층을 따로 두고, 피드백 신호가 있는 작업에만 돌려야 함. 코드는 [github.com/TailinZhou/hsi](https://github.com/TailinZhou/hsi)에 공개돼 있음.

하네스 진화와 루프 설계 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 시작해볼 수 있음.
