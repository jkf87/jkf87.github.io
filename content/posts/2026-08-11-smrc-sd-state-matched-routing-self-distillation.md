---
title: "성공 궤적을 그대로 가르치면 학생이 오히려 잘못 배움 — SMRC-SD 상태 매칭 증류"
date: 2026-08-11
tags:
  - agent
  - self-distillation
  - LLM
  - reinforcement-learning
  - multi-turn
  - GRPO
  - harness
  - tool-use
  - loop
  - automation
source: huggingface
source_url: https://arxiv.org/abs/2608.05219
github_url: https://github.com/liujunzhuo/SMRC-SD
description: 참조 궤적과 현재 상태가 어긋나면 teacher가 올바른 행동을 억누름. 상태 매칭 라우팅으로 호환되는 턴에만 증류 신호를 주는 방법을 예시 재사용 설계 관점으로 정리함.
---

멀티턴 에이전트 자기증류에서 성공한 궤적을 매 턴 무조건 teacher에게 보여주는 관행에 구조적 결함이 있었음. SMRC-SD가 그 결함을 측정하고 고쳤음. 원문은 [arXiv:2608.05219](https://arxiv.org/abs/2608.05219).

1. 문제는 state-reference mismatch임. 멀티턴 환경에서 이전 행동이 다음 상태를 바꾸는데, 기존 FullPath-SD는 성공한 전체 궤적을 매 턴 teacher에게 보여줌. 학생이 참조와 다른 행동을 하면 참조에 없는 상태에 도달하는데도 참조를 계속 주입함.

![상태-레퍼런스 불일치 문제](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/fig1-state-reference-mismatch.png)

![](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/gifs/gps-recalculating.gif)

2. 구체 예시가 와닿음. 참조 궤적은 "Product A를 Results A에서 클릭"하라고 가르치는데 학생은 Product B 상세 페이지에 있음. 이 상태에서 올바른 행동은 "Back to Search"인데도 teacher는 여전히 Product A 경로를 평가 기준으로 삼아서 학생의 올바른 행동을 낮게 매김.

![](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/gifs/classroom-exam.gif)

![SMRC-SD 개요](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/fig2-smrc-sd-overview.png)

3. 이걸 실험으로 증명한 게 이 논문의 첫 기여임. 상태·프롬프트·응답을 고정하고 teacher 컨텍스트만 바꿔본 결과, 매칭된 상태에서는 FullPath-SD가 올바른 행동의 로그 확률을 올리지만 비매칭 상태에서는 억누름(+0.070 차이). 무조건적 증류가 해가 된다는 직접 증거임.

4. 해법은 두 단계임. 첫째, 상태 매칭 라우팅. 환경 어댑터가 학생의 현재 상태 서명(작업 ID, 진행도, 인벤토리, 현재 페이지)과 참조 궤적 각 위치의 서명을 비교해서 매칭될 때만 증류를 적용하고 비매칭 시 GRPO만 씀. 둘째, 상태 맞춤 teacher 컨텍스트. 매칭된 턴에서 성공 전체 궤적과 현재 상태 요약, 매칭된 후보 행동을 함께 줘서 teacher가 도달한 상태에 근거해 re-scaring하게 함. 추론 시엔 참조·서명·teacher 컨텍스트를 전부 제거해서 배포 정책은 일반 프롬프트만 받음.

5. 결과. Qwen3-1.7B 기준 ALFWorld(텍스트 가상집에서 일상 과제를 수행하는 벤치마크) Avg@4가 0.746에서 0.865로, WebShop(모의 쇼핑몰에서 상품 검색·구매 과제를 수행하는 벤치마크) Acc가 0.574에서 0.693로 오름. 특히 Skill-SD(0.379)와 SDAR(0.578)는 GRPO(0.717)보다 떨어지는데, 무조건적 증류가 1.7B 같은 작은 모델에서는 학습을 해친다는 뜻임. 같은 참조를 쓰면서 매칭된 턴만 골라내니 문제가 사라짐.

![학습 다이내믹스](/images/2026-08-11-smrc-sd-state-matched-routing-self-distillation/fig3-training-dynamics.png)

6. 부수 효과도 좋음. 응답 길이가 GRPO 수준(78.8 vs 79.5 토큰)으로 유지되는데 FullPath-SD는 142.6, Skill-SD는 255.6 토큰임. 반복 4-gram 비율도 8.8%로 Skill-SD의 38.6%와 대비됨. 잘못된 참조가 낳는 장황함과 반복을 매칭만으로 없앤 것임.

7. 어블레이션의 교훈. 라우팅만 추가해도 0.746에서 0.836으로 오르고 동적 컨텍스트가 +0.029를 더함. 근데 같은 수의 턴을 무작위로 고르면 0.723으로 떨어짐. 어떤 턴을 고르느냐가 턴 수보다 중요하다는 것임. 그리고 상태 요약과 후보 행동 중 하나만 주면 개선이 없어서 "지금 어디인지"와 "다음에 뭘 해야 하는지"를 함께 줘야 함.

8. 내 예시 재사용 설계에 바로 적용한 원칙. 과거 성공 사례를 현재 작업에 참조로 넣을 때 "형태가 비슷하니까"가 아니라 "현재 상태와 맞는가"를 먼저 확인해야 함. 내 자동화에서 실패한 실행에 성공 로그를 무턱대고 붙여주는 패턴이 있었는데, 상태가 어긋난 참조는 없느니만 못하다는 걸 이 논문으로 확인했음. 매칭이 애매하면 참조를 빼는 게 기본값임.

9. 문제제기. 상태 서명이 hand-engineered이고 환경별 어댑터가 필요함. ALFWorld·WebShop은 상태가 정형화돼 있는데 실제 브라우저·터미널 환경에서는 서명 설계가 병목이 될 수 있음. 그래도 replay audit으로 structured-state 매칭이 781/781을 재현하는 등 매칭 품질 자체는 정직하게 검증했음.

10. 결론. 참조 궤적을 conditional plan으로 취급하라는 원칙이 핵심임. 하네스 설계, 메모리 재생, 스킬 재사용까지 같은 질문이 적용됨. "이 참조가 지금 이 상태에서 유효한가"를 먼저 확인하는 것. 코드는 [GitHub](https://github.com/liujunzhuo/SMRC-SD)에 공개돼 있음.
