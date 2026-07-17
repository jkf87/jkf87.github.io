---
title: "스킬도 코드다: eval 없이 ship하지 말라는 DeepMind 엔지니어의 경고"
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
description: "Google DeepMind의 Philipp Schmid가 AI Engineer 영상에서 강조한 메시지. Agent skill은 성능을 올릴 수 있지만, description trigger, negative case, ablation, regression eval 없이 배포하면 비용과 실패 원인을 동시에 숨긴다."
aliases:
  - /posts/dont-ship-skills-without-evals-2026-07-17
---

![Agent skill 폴더가 CI eval gate를 통과해야 배포되는 장면. 스킬은 문서처럼 보이지만 실제로는 제품 동작을 바꾸는 코드에 가깝다.](/images/dont-ship-skills-without-evals-2026-07-17/hero.jpg)

요즘 agent 생태계에서 “skill”은 거의 만능 접착제처럼 쓰인다. Claude Code, Cursor, Codex, Gemini CLI, OpenClaw까지, 모델에게 특정 작업 방식과 도메인 규칙을 알려주는 폴더 하나를 붙이면 갑자기 더 똑똑해지는 것처럼 보인다. 그런데 Google DeepMind의 Philipp Schmid는 AI Engineer 발표에서 정반대의 문장으로 시작한다. **“Don't ship skills without evals.”**

이 말이 중요한 이유는 간단하다. Skill은 프롬프트 조각이 아니라 제품의 행동을 바꾸는 코드에 가깝다. 그런데 코드처럼 테스트하지 않으면, 성능을 올리는지, 비용만 늘리는지, 심지어 성능을 망가뜨리는지 알 방법이 없다.

원본 영상은 AI Engineer 채널의 [Don't Ship Skills Without Evals](https://www.youtube.com/watch?v=0vphxNt4wyk)다. Philipp은 Gemini API와 agents 쪽에서 일하는 Google DeepMind 엔지니어이고, 발표 전체는 “스킬을 잘 쓰자”보다 한 단계 더 실무적이다. **스킬을 제품에 넣으려면 eval gate를 만들라**는 이야기다.

## 내가 쓰는 agent와 고객이 쓰는 agent는 완전히 다르다

발표 초반에 제일 좋은 구분이 나온다. 우리가 Cursor, Antigravity, Claude Code 같은 coding agent를 쓸 때는 문제가 생겨도 금방 알아차린다. 예를 들어 “Gemini API 기능 만들어줘”라고 했는데 agent가 관련 skill을 안 불렀다. 그러면 개발자는 바로 멈추고 다시 지시한다. “그 skill 써서 해.” 혹은 slash command를 직접 호출한다.

하지만 제품 안에 들어간 agent는 다르다. 고객은 “refund skill을 사용해서 환불 처리해줘”라고 말하지 않는다. 그냥 “환불하고 싶어요”라고 말한다. 그러면 모델이 알아서 적절한 skill을 찾아야 한다. 여기서 description trigger가 실패하면, skill은 존재하지만 없는 것이 된다.

> 내가 쓰는 agent에서는 내가 fallback이다. 고객용 agent에서는 eval이 fallback이어야 한다.

이 차이가 크다. 내부 개발 도구의 skill은 사람이 곁에서 감시한다. 소비자용 agent의 skill은 모델이 스스로 선택한다. 그래서 “언제 불려야 하는가”와 “언제 불리면 안 되는가”를 테스트하지 않으면, 제품 품질은 감으로 운영된다.

## Skill의 첫 번째 비용은 description이다

Skill은 보통 폴더 하나다. `SKILL.md`가 있고, 필요하면 reference 파일과 asset이 붙는다. Philipp은 이것을 progressive disclosure라고 설명한다. 첫 층은 title과 description이다. 이 description은 대부분의 agent harness에서 모델 컨텍스트에 항상 들어간다. 두 번째 층은 `SKILL.md` 본문이고, 세 번째 층은 더 깊은 reference 파일이다.

여기서 실무적으로 중요한 말이 나온다. **description은 모든 model call에서 비용을 낸다.** 길고 멋진 설명을 넣으면 매번 토큰 비용이 나간다. 반대로 너무 약하게 쓰면 모델이 언제 skill을 써야 하는지 모른다. 그래서 description은 에세이가 아니라 directive여야 한다.

예를 들어 “Interactions API는 session state를 처리하므로 multi-chat에 권장됩니다”보다 “chat application을 만들 때 Interactions API를 사용하라”가 낫다. 모델에게 배경지식을 주는 것이 아니라 행동을 바꾸는 지시를 줘야 한다는 뜻이다.

이 대목은 OpenClaw나 Claude Code에서 skill을 직접 만들어본 사람에게 바로 꽂힌다. 우리가 흔히 하는 실수는 두 가지다. 하나는 description을 너무 넓게 쓰는 것. “web development task에 사용” 같은 문장은 React, Angular, CSS, 배포, 문서까지 과하게 trigger될 수 있다. 다른 하나는 본문에 모든 절차를 우겨 넣는 것. AWS, GCP, Azure 배포 절차가 다 다르면 `SKILL.md`에 다 쓰는 게 아니라 reference로 쪼개야 한다.

## Capability skill은 언젠가 은퇴해야 한다

Philipp은 skill을 두 종류로 나눈다. capability skill과 preference skill이다.

Capability skill은 모델이 아직 안정적으로 못 하는 능력을 보완한다. 예를 들어 새 API 사용법, 특정 로그 추적 방식, 낯선 프레임워크 bootstrap 같은 것들이다. 이런 skill은 임시 장치다. 모델이 좋아지면 제거할 수 있어야 한다. 반대로 preference skill은 팀의 workflow, 문체, 도메인 규칙, 회사 내부 선호를 담는다. 이건 더 오래 간다.

이 구분이 좋은 이유는 “스킬을 왜 eval해야 하는가”가 달라지기 때문이다. Capability skill의 eval은 은퇴 시점을 알려준다. skill 없이도 같은 성능이 나오면 지워야 한다. Preference skill의 eval은 회귀를 막는다. 모델이 업데이트되거나 harness가 바뀌어도 팀의 규칙이 깨지지 않는지 본다.

![Skill eval은 단순히 통과/실패를 보는 장치가 아니다. skill을 계속 유지할지, 줄일지, retire할지 판단하는 유지보수 계기판이다.](/images/dont-ship-skills-without-evals-2026-07-17/hero.jpg)

물론 위 이미지는 은유다. 하지만 실제 구조도 크게 다르지 않다. skill을 켠 경우와 끈 경우를 비교하고, positive case와 negative case를 따로 보고, regression이 생기면 merge하지 않는다. 이건 사실상 CI다.

## AI가 만든 skill은 성능을 떨어뜨릴 수도 있다

발표에서 인용된 SkillsBench 1.1 이야기도 흥미롭다. 다양한 open/closed model과 harness에서 skill은 평균적으로 약 15% 성능 향상을 보였다고 한다. 즉 skill은 실제로 효과가 있다. 문제는 “아무 skill이나 효과가 있다”가 아니라는 점이다.

Philipp은 AI가 생성한 skill이 오히려 성능을 떨어뜨릴 수 있다고 말한다. Human-written skill이 가장 좋았고, `SKILL.md`는 500 words 아래가 바람직하다는 이야기도 나온다. 여기서 핵심은 길이가 아니다. 길고 느슨한 skill은 모델의 행동을 바꾸기보다 컨텍스트를 오염시킨다.

특히 AI 생성 skill에는 no-op이 많이 들어간다. “명확하고 고품질의 코드를 작성하라”, “가독성을 유지하라” 같은 문장들이다. 틀린 말은 아니다. 하지만 모델이 원래 해야 하는 말이라면 행동을 바꾸지 않는다. 행동을 바꾸지 않는 문장은 비용이다.

저는 이 대목이 꽤 중요하다고 봅니다. skill은 “좋은 말 모음”이 아니다. 모델의 선택을 바꾸는 좁은 장치다. 그러니 좋은 skill 문장은 아름다운 문장이 아니라, 나쁜 선택지를 줄이는 문장에 가깝다.

## Negative test를 넣지 않으면 과호출을 못 잡는다

대부분 skill eval을 생각하면 happy path부터 떠올린다. “이 prompt가 들어오면 이 skill을 써야 한다.” 맞다. 그런데 Philipp이 더 강조하는 건 negative case다. “이 prompt에서는 이 skill을 쓰면 안 된다.”

예를 들어 React component 전용 skill이 있다고 하자. description에 “web development에 사용”이라고 쓰면 모델은 CSS 수정, Angular migration, Next.js 배포, 단순 HTML 작업에도 skill을 불러올 수 있다. 그러면 불필요한 reference를 읽고, 잘못된 제약을 적용하고, 비용도 늘어난다.

그래서 시작은 작아도 된다. happy path 5개, non-trigger/negative 5개, 가능하면 production trace 몇 개. 총 10~20개 prompt만 있어도 꽤 많은 문제를 잡는다. 완벽한 benchmark가 아니라 “skill이 불릴 때와 안 불릴 때를 구분하는 최소 안전망”이다.

간단한 JSON은 이런 모양이면 충분하다.

```json
{
  "prompt": "React에서 Tailwind 기반 카드 컴포넌트를 만들어줘",
  "should_trigger": true,
  "expected_checks": ["uses_react", "uses_tailwind", "no_inline_css"]
}
```

반대로 negative case도 있어야 한다.

```json
{
  "prompt": "Angular 프로젝트의 routing 설정을 정리해줘",
  "should_trigger": false,
  "expected_checks": ["does_not_load_react_skill"]
}
```

이 정도면 거창한 LLM-as-judge 없이도 시작할 수 있다. Philipp의 Gemini Interactions API 사례도 기본은 JSON test cases와 Python runner, regex checks였다. SDK를 제대로 쓰는지, 최신 model id를 쓰는지, 오래된 method를 쓰지 않는지 같은 것은 regex로 충분히 본다.

## Outcome을 평가해야지, 첫 행동만 평가하면 안 된다

재밌는 포인트가 하나 더 있다. “모델이 첫 턴에 skill을 읽었는가”만 평가하면 안 된다는 것. 진짜 봐야 하는 것은 outcome이다. 모델이 첫 턴에 skill을 읽든, 다섯 번째 턴에 읽든, 혹은 skill 없이도 해결하든, 최종 결과가 맞는지가 더 중요하다.

이 말은 agent eval에서 자주 놓치는 부분이다. 우리는 trace가 예쁘게 생기길 원한다. 하지만 고객은 trace를 사지 않는다. 고객은 결과를 산다. skill eval도 마찬가지다. “정해진 path를 밟았는가”보다 “그 prompt에서 올바른 결과에 도달했는가”를 봐야 한다.

다만 skill 자체의 trigger 품질을 보려면 별도 지표가 필요하다. should_trigger, did_trigger, final_pass를 나눠야 한다. 그래야 실패 원인을 분리할 수 있다.

- should_trigger=true, did_trigger=false, final_pass=false → description이 약했을 가능성
- should_trigger=true, did_trigger=true, final_pass=false → skill 본문이나 reference가 약했을 가능성
- should_trigger=false, did_trigger=true → description이 너무 넓거나 negative scope가 부족
- should_trigger=false, did_trigger=false, final_pass=true → 정상

이렇게 쪼개야 skill을 고칠지, description을 고칠지, 아예 retire할지 판단할 수 있다.

## Skill 변경마다 regression eval을 돌리는 게 이상적이다

Google DeepMind 내부에서는 skill마다 eval을 함께 두고, skill file diff가 생기면 regression test를 돌린다고 한다. 깨끗한 workspace, startup command, script eval, trace 검사, LLM-as-judge expectation을 구성하고, 변경이 test를 개선하지 못하면 merge하지 않는다.

이건 매우 당연한 말처럼 들리지만, 실제 agent 팀에서는 아직 흔하지 않다. 많은 팀이 system prompt와 skill을 “문서”처럼 다룬다. 누군가 좋은 문장을 추가하면 좋아졌다고 믿는다. 하지만 agent는 비결정적이고, harness마다 동작이 다르고, 모델 업데이트마다 trigger 경향이 바뀐다. 문장 하나가 다른 skill 호출을 밀어낼 수도 있다.

그러니 skill은 문서가 아니라 코드로 봐야 한다. 코드라면 diff가 생길 때 test가 돌아야 한다. 실패하면 merge하지 않아야 한다. 적어도 가장 많이 쓰는 skill 몇 개는 그렇게 관리해야 한다.

## 월요일 숙제는 생각보다 작다

발표 마지막 숙제가 좋다. 가장 많이 쓰는 skill 하나를 고르고 test prompt 5개를 쓰라는 것이다. 이 정도면 바로 할 수 있다.

저라면 이렇게 시작하겠습니다.

1. 최근 1~2주 agent trajectory에서 가장 자주 불린 skill 하나를 고른다.
2. “꼭 불려야 하는 prompt” 3개를 쓴다.
3. “불리면 안 되는 prompt” 2개를 쓴다.
4. 결과물에서 regex로 확인 가능한 check를 붙인다.
5. skill on/off ablation을 한 번 돌린다.

여기서 바로 알 수 있다. 이 skill이 정말 성능을 올리는지, 아니면 이미 모델이 skill 없이도 잘하는지. 후자라면 과감히 줄이거나 retire 후보로 올려야 한다. skill은 자산이지만, 동시에 고정비다.

## 에이전트 시대의 실무 감각은 “잘 쓰기”보다 “검증하며 줄이기”다

요즘 agent workflow를 만들다 보면 자꾸 더 붙이고 싶어진다. skill을 붙이고, memory를 붙이고, tool을 붙이고, hook을 붙인다. 처음에는 다 도움이 되는 것처럼 보인다. 하지만 어느 순간부터 시스템은 무거워지고, 실패 원인은 흐려지고, 비용은 조용히 오른다.

Philipp Schmid의 메시지는 그래서 좋은 제동장치다. “skill을 쓰지 말라”가 아니다. 오히려 skill은 평균 성능을 올릴 수 있다고 인정한다. 다만 **검증 없이 붙인 skill은 지식이 아니라 부채가 될 수 있다**는 것이다.

agent engineering의 다음 단계는 멋진 skill을 많이 만드는 일이 아닐지도 모른다. 가장 많이 쓰는 skill에 eval 5개를 붙이고, negative case를 넣고, ablation을 돌리고, no-op을 지우는 일일 가능성이 크다. 조금 덜 화려하지만, 제품은 보통 그런 곳에서 좋아진다.

원문 영상: [Don't Ship Skills Without Evals — Philipp Schmid, Google DeepMind](https://www.youtube.com/watch?v=0vphxNt4wyk)
