---
title: "강한 모델이 작은 모델용 스킬을 뽑아줌 — SKILLER의 executor 특화 원칙"
date: 2026-08-25
tags:
  - agent
  - skills
  - LLM
  - reinforcement-learning
  - small-model
  - harness
  - automation
description: "SKILLER는 강한 모델이 critic과 actor를 맡아 작은 모델을 위한 맞춤 스킬을 자연어 강화학습으로 뽑아주는 프레임워크임. Qwen3.5-9B에서 최대 +20.4%p, 4B가 스킬 하나로 9B를 이기는 결과와 모델 미스매치의 실증을 정리함."
draft: true
refactor_hub: harness-self-improve-01
refactor_status: queued
---

에이전트 하네스에서 스킬은 이제 표준이 됐음. OpenClaw, Codex, Claude Code 모두 숙련자가 쓴 스킬을 재사용해서 반복 작업 품질을 올림. 근데 숨겨진 비용 문제가 있음. 이런 스킬이 제대로 작동하려면 프론티어급 클로즈드 모델이 필요한데 실서비스에서 계속 돌리면 비용이 걷잡을 수 없이 커진다는 것. 상하이AI랩 등이 낸 SKILLER(arXiv:2608.10538, 강한 모델이 critic·actor를 맡아 작은 모델용 스킬을 자연어 강화학습으로 뽑아주는 프레임)가 이 문제의 답을 바꿈. GPT-5.4 같은 강한 모델이 스킬을 쓰는 게 아니라 작은 모델을 위해 맞춤 스킬을 가르쳐주는 것. Qwen3.5-9B에서 최대 +20.4%p, 심지어 4B 모델이 최적화된 스킬 하나로 9B를 이겨버리는 장면도 나옴.

1. 접근이 재밌음. 가중치를 건드리는 RL이 아니라 스킬 자체를 정책으로 보고 소형 모델의 에이전트 루프를 환경으로 삼아 모든 신호를 자연어로만 주고받음. 강한 모델이 critic과 actor를 맡고 벤치마크 검증기가 보상을 줌. 프롬프트 엔지니어링의 자동화이자 검증기 기반 텍스트 탐색으로서의 RL이라는 관점임.

![](/images/skiller-language-level-rl-small-model-skills-2026-08-25/fig-2-overview.png)

2. 제일 instructive한 발견은 모델 미스매치의 실증임. 사람이 쓴 스킬과 Manus(에이전트 제품으로 유명한 스킬 세트를 공개한 업체)가 만든 스킬이 오히려 작은 모델의 성능을 떨어뜨리는 경우가 있음. 거대 모델 전제의 장황한 지시가 작은 모델에게는 과부하로 작용한다는 것. 특히 Manus 스킬이 GAIA(웹 검색·파일 조작 등을 섞은 범용 어시스턴트 과제 벤치마크)에서 스킬 없는 기준선보다도 아래로 떨어짐. 도메인 컨텍스트가 멀티홉 추론에서 과부하와 오류 전파를 일으키는 반면 SKILLER의 간결한 executor 특화 경계는 환각을 일관되게 줄임. "좋은 스킬"은 executor가 누구냐에 따라 달라진다는 뜻. 스킬 시장이 커질수록 executor 특화가 핵심 경쟁력이 될 것이라는 전망에 근거가 생긴 셈임.

3. 수정 방식이 국소적임. 실행 궤적에서 정확히 어디서 이탈했는지 진단한 뒤 그 지점에만 국소적 경계를 삽입함. 전면 재작성이 아니라 이탈 지점 타겟 수정. 하네스 진화 연구에서 반복 확인되는 원칙(국소 수정이 전면 개편을 이김)이 스킬 생성에서도 유지됨.

![](/images/skiller-language-level-rl-small-model-skills-2026-08-25/fig-1-cost-performance.png)

4. 결과. 5개 벤치마크(SkillsBench(에이전트 스킬 활용 능력 벤치마크), SWE-Skills-Bench, SkillLearnBench, GAIA, EarthBench)에서 오픈소스 3종(AutoSkill, EvoSkill, SkillX)과 클로즈드 1종(Manus)을 모두 이김. 제로샷 전이(GAIA, EarthBench)에서도 강함. 비용 구조가 합리적. 스킬 생성 비용은 초기에 집중되지만 실행 토큰은 저렴한 소형 모델로 돌리니 장기적으로 이득임. 비싼 모델은 컴파일러로, 싼 모델은 런타임으로 쓰는 구조.

![](/images/skiller-language-level-rl-small-model-skills-2026-08-25/table-2-zeroshot.png)

5. 내 실무 이식은 이렇게임. 첫째, 프론티어 모델용으로 쓴 스킬을 소형 모델에 그대로 이식하지 말 것. 미스매치가 성능 하락까지 만든다는 실증이 있음. 둘째, 스킬을 쓸 executor를 지정하고 그 모델의 실패 궤적에서 이탈 지점을 진단해 국소 경계를 삽입하는 방식으로 스킬을 작성할 것. 셋째, 비용 구조를 컴파일 타임(강한 모델의 스킬 생성)과 런타임(싼 모델의 실행)으로 나눠 계산할 것. 넷째, 스킬 품질은 스킬 자체가 아니라 executor 성적으로 측정할 것. 결론은 한 줄. 최적화된 자연어 정책 하나가 파라미터 스케일링보다 값싸게 강력할 수 있다는 것.

원문: [arXiv:2608.10538](https://arxiv.org/abs/2608.10538), 코드: [github.com/DANG-ai/SKILLER](https://github.com/DANG-ai/SKILLER).
