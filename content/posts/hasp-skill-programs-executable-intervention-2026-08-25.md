---
title: "스킬을 텍스트 조언에서 실행 코드로 바꾸니 20.5%→51.0% — HASP가 찾은 진짜 병목"
date: 2026-08-25
tags: [agent, LLM, harness, skill, RL, evaluation]
draft: false
description: "경험에서 뽑은 스킬을 실행 가능한 Program Function으로 감싸 발동 조건과 개입 방식을 코드로 명시한 HASP. 프롬프트 주입 대비 30점 차이가 났고 필터 없는 스킬 진화는 24점을 날렸다."
---

과거 경험에서 뽑은 "스킬"을 프롬프트에 넣는 방식이 실전에서 무시된다는 문제를 정면으로 다룬 논문이 나옴. 결과 차이가 극단적이라 정리함. 원문은 [arXiv:2605.17734](https://arxiv.org/abs/2605.17734).

1. 문제는 이거임. ExpeL, Reflexion, Voyager 계열은 교훈을 자연어로 저장해 프롬프트에 넣는데 이건 권고(advisory)일 뿐임. 모델이 읽어도 다음 액션을 그대로 실행하면 끝임. Qwen2.5-7B 기준 스킬 텍스트만 주입하면 정확도 20.5%에 불과했음.

2. HASP의 해법은 스킬을 두 인터페이스를 가진 함수로 만드는 것임. should_activate(state, action)이 발동 조건을 판단하고 intervene(...)이 다음 액션을 고치거나 교정 맥락을 주입함. "같은 검색어를 반복하지 마라"는 텍스트 대신 반복 검색 상태를 감지하면 검색어를 다시 써주는 PF가 동작하는 식임.

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/gifs/terminal-code-screen.gif)

![HASP 스킬 프로그램 개요](/images/hasp-skill-programs-executable-intervention-2026-08-25/fig-1-p2.png)

3. 결과가 30점 차이임. 같은 스킬을 프롬프트에 넣으면 20.5%, 실행형으로 감싸면 PF-only 51.0%, 보조 티처 선택으로 56.2%, 학습과 스킬 진화까지 더한 HASP-Evolve+RS가 60.3%. 학습 기반 Search-R1(29.9%)도 크게 앞섬. 병목은 스킬 본문 품질이 아니라 발동 조건과 개입 방식을 코드로 명시하는 일이었다는 결론임.

4. 하네스 구조가 외부형이라 적용이 쉬움. 매 스텝 기본 정책이 액션을 제안하면 하네스가 PF 후보를 검색해 활성화를 평가하고 개입함. 개입은 액션 수정과 경고 맥락 주입 두 가지. 그리고 원본 제안-수정 액션 쌍이 기록돼서 그대로 학습 신호가 됨. 이중 구조 — 추론 시점 개입 + 개입 기록의 학습 내재화 — 가 설계의 뼈대임.

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/gifs/tesla-autopilot.gif)

![하네스 구조](/images/hasp-skill-programs-executable-intervention-2026-08-25/fig-2-p4.png)

5. 학습 내재화는 네 신호로 채점함. 개입 시점, 방식, 올바름, 결과에 가중치 (0.15, 0.10, 0.25, 0.50)로 결과에 절반을 둠. SFT, rejection sampling, on-policy distillation 세 경로를 만드는데 고정 라이브러리에서는 OPD가 62.5%로 가장 강했다는 디테일도 있음.

![학습 내재화 결과](/images/hasp-skill-programs-executable-intervention-2026-08-25/table-4-p7.png)

6. 소거 실험이 실무 경고의 핵심임. 스킬 라이브러리 진화에서 실행 필터+티처 필터 둘 다 있으면 60.3%, 필터 없이 진화하면 36.3%로 급락. 검증 안 된 PF가 섞이면 24점이 사라진다는 것. 앞서 정리한 PoisonedEvolution의 출처 다양성 게이트, RuleMem의 RPC 검증과 같은 결론 — 스킬 자기진화 시스템에서 검증 필터는 선택이 아니라 필수임.

![소거 실험](/images/hasp-skill-programs-executable-intervention-2026-08-25/fig-4-p9.png)

7. 도메인별 차이도 정직함. 코딩에서 PF 기반 학습이 69.9%로 vanilla SFT 대비 +12.4%. 수학은 45.4%로 오르긴 하나 AgentFlow(51.5%)가 이 논문 세팅보다 높음. 스킬 개입보다 전체 흐름 RL이 더 맞는 영역이 있다는 대비를 숨기지 않음.

![도메인별 차이](/images/hasp-skill-programs-executable-intervention-2026-08-25/table-6-p9.png)

8. 필자 해석. Skill-Use 벤치마크가 프론티어 모델도 트리거·준수·경계를 다 못 지킨다고 측정했고 HASP가 같은 방향을 보여줌. 두 결과를 합치면 실무 결론은 이거임 — 노트와 교훈을 쌓는 것보다 should_activate/intervene 인터페이스가 있는 실행 스킬 몇 개가 더 싸고 효과적임. 필자의 게이트 스크립트가 사실상 하네스 개입형 스킬이라는 점에서 방향이 맞았다는 확인이 됨.

9. 문제제기. 7B 모델 기준 결과라 큰 모델에서 개입형 스킬의 이득 폭이 얼마나 유지될지 미확인임. 웹검색·코딩 중심 평가라 다른 도메인 일반화도 열려있음. 그리고 OPD와 진화를 동시에 돌리면 56.7%로 역행하는 불안정성이 있어서 구성 선택이 민감함.

10. 남는 결론. 스킬의 가치는 본문이 아니라 인터페이스에 있음. 발동 조건과 개입을 코드로 명시하는 순간 권고가 제어가 되고, 그 차이가 30점이라는 게 이 논문의 실무 교훈임.
