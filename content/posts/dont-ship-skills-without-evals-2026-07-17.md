---
title: "스킬은 코드임 — eval 없이 ship하면 비용과 실패 원인을 동시에 숨김"
date: 2026-07-17
draft: false
tags:
  - agent-skills
  - evaluation
  - ai-agent
  - Google-DeepMind
  - skill-evals
  - agent-engineering
categories:
  - AI
  - Developer
description: "Google DeepMind Philipp Schmid의 'Don't Ship Skills Without Evals' 발표 정리. description 트리거 평가, negative case, on/off ablation, regression eval 없이 배포된 스킬은 성능이 아니라 부채가 된다."
aliases:
  - /posts/dont-ship-skills-without-evals-2026-07-17
---

스킬이 만능 접착제처럼 쓰이는 시절에 정반대 문장을 던진 발표가 있어서 정리함. Google DeepMind의 Philipp Schmid가 AI Engineer 채널에서 한 "Don't ship skills without evals"임. 원본은 [발표 영상](https://www.youtube.com/watch?v=0vphxNt4wyk).

1. 출발 구분이 좋음. 내가 쓰는 코딩 에이전트에서 스킬이 안 불리면 내가 바로 "그 스킬 써서 해"라고 고쳐줌 — 내가 fallback임. 근데 제품 안의 에이전트는 고객이 "환불하고 싶어요"라고만 말하고 모델이 알아서 스킬을 찾아야 함. description 트리거가 실패하면 스킬은 존재하지만 없는 것이 됨. 고객용 에이전트에서는 eval이 fallback이어야 한다는 것.

![Philipp Schmid 발표 영상 썸네일](/images/dont-ship-skills-without-evals-2026-07-17/hero.jpg)

2. 스킬의 첫 비용이 description임. progressive disclosure의 첫 층인 description은 모든 모델 호출 컨텍스트에 항상 들어가서 매번 토큰 비용을 냄. 그래서 에세이가 아니라 지시어여야 함. "chat application을 만들 때 Interactions API를 사용하라"가 "Interactions API는 multi-chat에 권장됩니다"보다 낫다는 것. 배경지식이 아니라 행동을 바꾸는 지시를 줘야 함.

3. capability 스킬과 preference 스킬 구분도 실무적임. 전자는 모델이 아직 못 하는 능력을 보완하는 임시 장치라서 모델이 좋아지면 은퇴시켜야 하고, 후자는 팀의 워크플로와 도메인 규칙을 담아서 더 오래 감. eval의 목적도 달라짐 — capability는 은퇴 시점을 알려주고 preference는 회귀를 막음.

![잠깐, eval 없이 ship?](/images/dont-ship-skills-without-evals-2026-07-17/gifs/hold-on.gif)

4. AI가 만든 스킬은 성능을 떨어뜨릴 수 있다는 경고가 핵심임. SkillsBench 1.1에서 스킬은 평균 약 15% 향상이 있었지만 사람이 쓴 스킬이 가장 좋았고, AI 생성 스킬엔 no-op이 많이 들어감. "명확하고 고품질의 코드를 작성하라" 같은 문장은 틀리지 않았지만 모델이 원래 할 말이라 행동을 바꾸지 않음. 행동을 바꾸지 않는 문장은 비용이라는 것 — 좋은 스킬 문장은 아름다운 문장이 아니라 나쁜 선택지를 줄이는 문장임.

![eval은 TEST부터 작게](/images/dont-ship-skills-without-evals-2026-07-17/gifs/testing.gif)

5. negative test 없이는 과호출을 못 잡음. happy path만 평가하면 React 전용 스킬이 CSS 수정, Angular 마이그레이션에까지 불려서 불필요한 참조 읽기와 잘못된 제약 적용, 비용 증가를 만듦. 시작은 작아도 됨 — 발동되어야 할 프롬프트 5개, 되면 안 되는 프롬프트 5개, 가능하면 실제 트레이스 몇 개. JSON 케이스와 regex 체크면 거창한 judge 없이 시작할 수 있음.

6. 평가는 첫 행동이 아니라 outcome이어야 한다는 것도 중요함. 모델이 첫 턴에 스킬을 읽었는지보다 최종 결과가 맞는지가 본질임. 다만 트리거 품질은 별도 지표로 쪼개야 원인 분리가 됨. should_trigger·did_trigger·final_pass를 나누면 description이 약했는지, 본문이 약했는지, scope가 너무 넓은지가 구분된다는 것.

7. DeepMind 내부 관행이 목표 지점임. 스킬마다 eval을 함께 두고 스킬 diff가 생기면 regression test를 돌리고, 개선하지 못하면 merge하지 않음. 스킬을 문서가 아니라 코드로 취급하는 것 — 코드라면 diff에 test가 돌아야 한다는 당연한 원칙임. 앞서 정리한 Skill-Use 벤치마크의 "SU 0.5 미만 스킬은 없느니만 못함" 결과와 정확히 같은 결론임.

8. 필자가 바로 한 것. 가장 자주 불리는 스킬 하나를 골라 발동 프롬프트 3개, 비발동 프롬프트 2개, regex 체크, on/off ablation 한 번. merche 스킬이 실제로 재작성 품질을 올리는지 아니면 모델이 이미 잘하는 건지 확인하는 게 첫 순서임. 스킬은 자산이지만 동시에 고정비라는 관점을 유지해야 함.

9. 남는 결론. 에이전트 실무의 다음 단계는 멋진 스킬을 많이 만드는 게 아니라 많이 쓰는 스킬에 eval 5개 붙이고 negative case 넣고 ablation 돌리고 no-op 지우는 일임. 검증 없이 붙인 스킬은 지식이 아니라 부채가 된다는 게 이 발표가 주는 제동장치임.
