---
title: "스킬은 통째로 만들지 말고 한 편집씩 다듬어야 함 — Skill-α의 rollback reward"
date: 2026-08-05
tags:
  - agent
  - skill-generation
  - reinforcement-learning
  - LLM
  - GRPO
  - loop
  - automation
socialImage: /images/2026-08-05-skill-alpha-progressive-agent-skill-rl/fig-1-p4.png
description: 스킬 생성을 증거 하나씩 읽으며 편집하는 의사결정 시퀀스로 쪼개고 각 편집의 가치를 rollback으로 측정함. 스킬 문서 운영에 바로 쓸 편집 액션 설계와 증거 배치 규칙을 정리함.
draft: true
refactor_hub: harness-self-improve-01
refactor_status: queued
---

에이전트 스킬을 자동으로 만들 때의 고민은 "이 스킬이 좋은 스킬인가"를 직접 판정할 수 없다는 것임. CUHK의 Skill-α가 그 문제를 RL로 풀었음. 원문은 [arXiv:2608.01678](https://arxiv.org/abs/2608.01678), 코드는 [GitHub](https://github.com/ejhshen/skill-alpha)에 공개돼 있음.

1. 배경. 스킬은 재사용 가능한 절차 모듈이라 모델 재훈련 없이 에이전트 행동을 바꿀 수 있음. 근데 스킬엔 정답 라벨이 없어서 결국 "에이전트가 그 스킬을 쓰고 잘 동작하는지"로 평가해야 하는데 비용도 크고 신호도 약함. 기존 방법은 문서→스킬(Ctx2Skill, AutoSkill)과 경험→스킬(Trace2Skill, SkillX, SkillPro)이 있었는데 전부 휴리스틱·파이프라인이라 증거 소스마다 설계를 따로 해야 했음.

2. Skill-α의 첫 번째 발상. 스킬을 한 번에 만들지 않고 증거를 순차적으로 읽으며 한 단계씩 편집함. 에디터는 매 단계에서 Create(규칙 추가), Update(수정), Merge(통합), Prune(삭제), Noop(변경 없음) 다섯 행동 중 하나를 고름. 스킬 생성이 의사결정 시퀀스가 되어서 각 편집을 개별 평가할 수 있게 됨.

![Skill-α 순차 편집 개요(논문 Figure 1)](/images/2026-08-05-skill-alpha-progressive-agent-skill-rl/fig-1-p4.png)

3. 두 번째 발상이 핵심인 rollback reward임. 편집 전 스킬과 편집 후 스킬로 같은 anchored query에 답하게 하고 결과 차이를 검증기로 채점함. 편집 하나가 스킬을 실제로 좋게 만들었는지를 워커 자체 능력이나 문제 난이도와 분리해서 측정할 수 있음. 이 보상으로 GRPO(같은 문제의 여러 롤아웃을 그룹으로 묶어 상대 비교로 정책을 갱신하는 강화학습 알고리즘)를 돌려서 에디터를 훈련함.

![되돌림으로 측정하는 편집 가치](/images/2026-08-05-skill-alpha-progressive-agent-skill-rl/gifs/undo.gif)

4. 결과. GPT-4o 기준 문서→스킬에서 CL-Bench 평균 10.38점으로 최강 베이스라인 대비 +3.3점, 경험→스킬에서 tau2-bench(리테일·항공 등 고객 상담 시나리오에서 에이전트의 도구 사용과 정책 준수를 재는 벤치마크) 평균 70.33점으로 SkillX(65.00) 대비 +5.33점임. 두 설정 모두에서 기존 방법을 이겨서 "하나의 학습된 에디터가 문서든 경험이든 동일하게 처리한다"는 주장이 성립함.

5. 워커를 바꿔도 효과가 유지됨. GPT-4o로 만든 스킬을 Claude-Sonnet-4.5에 먹여도 일관된 향상이 나옴. 특정 워커용 프롬프트 핵이 아니라 범용 작업 지식이라는 뜻임.

6. 어블레이션이 실무 교훈의 보고임. 첫째, SFT만 남기면 3.46점으로 급락함. RL이 효과의 본체임. 둘째, rollback을 빼고 직접 검증기 보상만 쓰면 3.68로 사실상 SFT-only 수준임. rollback이 핵심 신호임. 셋째, Merge/Prune을 빼고 Create만 하면 중복·충돌이 쌓여 39.17점으로 무너짐. 스킬 관리에 삭제와 통합이 필수임. 넷째, Noop을 빼고 매 단계 무조건 편집하면 53.33으로 전체(55.83)보다 낮음. "지금 스킬이 충분하면 손대지 않는다"는 판단도 학습 대상임.

![어블레이션별 학습 역학과 행동 분포(논문 Figure 2)](/images/2026-08-05-skill-alpha-progressive-agent-skill-rl/fig-2-p8.png)

![어블레이션 결과(논문 Table 4)](/images/2026-08-05-skill-alpha-progressive-agent-skill-rl/table-4-p8.png)

7. rollback reward를 빼면 에디터가 Noop으로 쏠림. 신호가 약하니 안 바꾸는 게 안전하다고 배우는 것임. 보상 설계가 에디터의 행동 분포를 결정한다는 좋은 사례임.

8. 증거 배치 크기 발견도 챙겨감. 한 번에 증거 1개씩은 시야가 좁아 과적합하고 8개씩은 초점이 흐려짐. 4개씩이 최적이었고 순서를 섞거나 뒤집어도 차이가 크지 않았음. 내가 자동화 로그로 스킬 문서를 갱신할 때 한 번에 몰아넣지 말고 소량 배치로 나눠 반영하라는 근거로 씀.

9. 내 스킬 문서 운영에 적용한 것. 첫째, 스킬 파일 편집을 Create/Update/Merge/Prune/Noop 액션 어휘로 관리함. 특히 Prune(과도하게 구체적인 내용 삭제)과 Merge를 스킬 리뷰 주기에 필수로 넣음. 둘째, 편집 전후로 동일한 기준 쿼리 몇 개를 돌려서 차이로 편집 가치를 판정하는 rollback 패턴을 도입함. 안 좋아지면 되돌림.

10. 문제제기. anchored query와 검증기를 도메인별로 설계해야 하는 부담이 남아있고, 스킬 편집마다 워커를 두 번 돌리는 비용이 있음. 그리고 평가가 벤치마크 중심이라 장기 운영에서 스킬이 계속 자라날 때의 관리 비용은 미측정임.

11. 결론. 스킬 생성을 학습 문제로 프레이밍한 첫 작업이라는 점의 의미가 큼. rollback reward 아이디어는 메모리 편집, 도구 설정 변경, 시스템 프롬프트 수정처럼 "편집 전후로 에이전트 행동을 비교할 수 있는" 모든 설정에 확장 가능함. 내 스킬 파이프라인에도 이 비교 구조가 들어가야 한다는 결론임.

스킬 문서를 다루는 에이전트 루프 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 해볼 수 있음.
