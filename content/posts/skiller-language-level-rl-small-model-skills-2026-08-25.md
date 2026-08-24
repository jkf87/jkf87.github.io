---
title: "SKILLER: 강한 모델이 작은 모델용 스킬을 RL로 뽑아주는 프레임워크"
date: 2026-08-25
tags:
  - agent
  - skills
  - LLM
  - reinforcement-learning
  - small-model
  - harness
  - automation
draft: false
---

## 작은 모델에게도 스킬이 필요한 시대

에이전트 하네스의 세계에서 '스킬(skill)'은 이제 하나의 표준이 되었습니다. OpenClaw, Codex, Claude Code 같은 하네스들은 숙련된 사용자가 작성한 스킬을 재사용하며 반복 작업의 품질을 끌어올리죠. 그런데 여기에 숨겨진 비용 문제가 있습니다. 이런 스킬이 제대로 작동하려면 <span style="background-color: #fff59d"><strong>프론티어급 클로즈드소스 모델이 필요한데, 실서비스에서 이 모델들을 계속 돌리자면 비용이 걷잡을 수 없이 커진다</strong></span>는 겁니다.

2026년 8월, 상하이AI랩을 중심으로 한 연구진이 흥미로운 답을 내놨습니다. arXiv:2608.10538, 바로 SKILLER입니다. GPT-5.4 같은 강한 모델이 배우(skills)를 쓰는 게 아니라, <span style="background-color: #fff59d"><strong>작은 모델을 위해 맞춤 스킬을 '가르쳐주는' 프레임워크</strong></span>죠. Qwen3.5-9B에서 <span style="background-color: #fff59d"><strong>최대 +20.4%p</strong></span>, 심지어 <span style="background-color: #fff59d"><strong>4B 모델이 최적화된 스킬 하나로 9B를 이겨버리는</strong></span> 장면도 나옵니다.

## 접근: 스킬을 정책으로 보는 자연어 강화학습

SKILLER가 강화학습이라고 하면 가중치를 건드리는 걸 떠올리기 쉬운데, 전혀 아닙니다. <span style="background-color: #fff59d"><strong>스킬 자체를 정책으로 보고, 소형 모델의 에이전트 루프를 환경으로 삼아, 모든 신호를 자연어로만 주고받습니다</strong></span>. 강한 모델이 critic과 actor를 맡고, 벤치마크 검증기가 보상을 줍니다.

![](/images/skiller-language-level-rl-small-model-skills-2026-08-25/fig-2-overview.png)
*Figure 2. SKILLER 프레임워크 개요. 출처: arXiv:2608.10538*

재밌는 건 <span style="background-color: #fff59d"><strong>사람이 쓴 스킬과 Manus가 만든 스킬이 오히려 성능을 떨어뜨리는 경우가 있다</strong></span>는 점입니다. 거대 모델 전제의 지시가 작은 모델에게는 과부하로 작용한다는, 이른바 <span style="background-color: #fff59d"><strong>모델 미스매치의 실증</strong></span>이죠. SKILLER는 실행 궤적에서 <span style="background-color: #fff59d"><strong>정확히 어디서 이탈했는지 진단한 뒤 그 지점에만 국소적 경계를 삽입</strong></span>합니다.

![](/images/skiller-language-level-rl-small-model-skills-2026-08-25/fig-1-cost-performance.png)
*Figure 1. SkillsBench 단일 스킬 태스크의 비용-성능. 출처: arXiv:2608.10538*

## 결과와 시사점

5개 벤치마크(SkillsBench, SWE-Skills-Bench, SkillLearnBench, GAIA, EarthBench)에서 <span style="background-color: #fff59d"><strong>오픈소스 3종(AutoSkill, EvoSkill, SkillX)과 클로즈드소스 1종(Manus)을 모두 이겼고</strong></span>, 제로샷 전이에서도 강했습니다. 스킬 생성 비용은 초기에 집중되지만, <span style="background-color: #fff59d"><strong>실행 토큰은 저렴한 소형 모델로 돌리니 장기적으로 이득</strong></span>입니다.

![](/images/skiller-language-level-rl-small-model-skills-2026-08-25/table-2-zeroshot.png)
*Table 2. GAIA·EarthBench 제로샷 결과. 출처: arXiv:2608.10538*

참고로 Manus 스킬은 GAIA에서 <span style="background-color: #fff59d"><strong>스킬 없는 기준선보다도 아래로 떨어집니다</strong></span>. 장황한 도메인 컨텍스트가 멀티홉 추론에서 과부하와 오류 전파를 일으키는 반면, SKILLER의 간결한 executor 특화 경계는 환각을 일관되게 줄입니다.

이 논문이 남기는 메시지는 결국 이것입니다: <span style="background-color: #fff59d"><strong>최적화된 자연어 정책 하나가 파라미터 스케일링보다 값싸게 강력하다</strong></span>. 프롬프트 엔지니어링의 자동화이자, 검증기 기반 텍스트 탐색으로서의 RL. 앞으로 스킬 시장이 커질수록 <span style="background-color: #fff59d"><strong>executor 특화가 핵심 경쟁력</strong></span>이 될 겁니다.

- [arXiv:2608.10538](https://arxiv.org/abs/2608.10538)
- [GitHub: DANG-ai/SKILLER](https://github.com/DANG-ai/SKILLER)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
