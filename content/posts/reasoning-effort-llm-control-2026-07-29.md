---
title: "LLM의 ‘생각 예산’을 조절한다는 것"
date: 2026-07-29
draft: false
tags:
  - LLM
  - reasoning-models
  - inference-scaling
  - RLVR
  - agents
categories:
  - AI
  - Agent
description: "Sebastian Raschka의 Controlling Reasoning Effort in LLMs를 뉴스레터 스타일로 정리했다. reasoning effort는 단순 UI 옵션이 아니라, post-training과 inference-time compute가 만나는 새 조절 노브다."
aliases:
  - /posts/reasoning-effort-llm-control-2026-07-29
---

![Reasoning effort를 Light부터 Ultra까지 조절하는 대시보드. 같은 모델이라도 생각에 쓸 token budget을 바꾸면 비용, 지연시간, 정답률의 균형점이 달라진다.](/images/reasoning-effort-llm-control-2026-07-29/hero.svg)

LLM을 쓰다 보면 이제 이상한 메뉴가 하나씩 보인다. “Reasoning effort: low, medium, high.” 또는 “thinking on/off.” 예전에는 모델을 고르는 일이 전부였다. 작은 모델이냐, 큰 모델이냐. 그런데 이제는 같은 모델 안에서도 **얼마나 오래 생각하게 할 것인가**를 고르는 시대가 됐다.

Sebastian Raschka의 글 [Controlling Reasoning Effort in LLMs](https://magazine.sebastianraschka.com/p/controlling-reasoning-effort-in-llms)는 이 메뉴 뒤에 있는 훈련·추론 구조를 차분하게 풀어준다. 글은 길지만, 핵심은 꽤 실무적이다. **reasoning effort는 prompt trick 하나가 아니라, 모델이 비용과 정확도 사이를 움직이도록 학습된 조절 노브**라는 점이다.

저는 이 글을 읽으면서 AI 제품과 에이전트 하네스를 만드는 분들이 바로 가져가야 할 질문이 하나 있다고 봤다. “모델을 똑똑하게 만들 것인가?”가 아니라, **“언제 비싸게 생각하게 하고, 언제 빨리 답하게 할 것인가?”** 이다.

![원문 Figure 1. GPT-5.6 Sol 모델에서 reasoning effort를 바꿨을 때 benchmark 점수가 달라지는 모습. 이 글의 출발점은 “같은 모델이라도 생각 예산을 메뉴로 고른다”는 장면이다. 출처: Sebastian Raschka, Controlling Reasoning Effort in LLMs.](/images/reasoning-effort-llm-control-2026-07-29/fig01-gpt56-effort.png)

## 이번 글이 답하는 질문

이 뉴스레터는 Raschka 글을 따라가되, 실무 관점에서 네 가지 질문으로 다시 묶었습니다.

1. reasoning model은 정말 “생각”하는 모델인가?
2. `<think>` 토큰과 reasoning effort 메뉴는 무엇이 다른가?
3. effort level은 학습 때 어떻게 만들어지는가?
4. 에이전트 시대에는 누가 effort를 골라야 하는가?

## reasoning model은 ‘중간 풀이’를 출력하는 모델이다

먼저 이름을 너무 문자 그대로 받아들이면 안 된다. Raschka도 이 지점에서 시작한다. neural network가 인간 뇌처럼 작동하지 않듯이, reasoning model도 인간처럼 사유한다고 보면 곤란하다.

AI 연구 맥락에서 reasoning model은 보통 **최종 답만 내는 대신, 중간 reasoning trace를 만들어가며 문제를 푸는 모델**을 뜻한다. 수학 문제를 풀 때 풀이 과정을 쓰고, 코딩 문제를 풀 때 조건을 점검하고, 중간에 틀렸다고 판단하면 되돌아가는 식이다. DeepSeek-R1 이후 이 패턴이 대중화됐다.

여기서 중요한 훈련 방식이 RLVR(Reinforcement Learning with Verifiable Rewards)이다. 답이 맞는지 자동으로 확인할 수 있는 영역, 예를 들어 수학과 코딩에서 reward를 준다. 정답이면 1, 오답이면 0에 가깝게. 모델은 여러 번 시도하며 최종 답이 맞는 방향으로 업데이트된다.

![원문 Figure 4. 모델 성능을 올리는 두 축으로 training scaling과 inference scaling을 나눠 보여준다. reasoning effort는 후자, 즉 이미 훈련된 모델이 답변 시점에 더 많은 compute를 쓰게 하는 축이다. 출처: Sebastian Raschka.](/images/reasoning-effort-llm-control-2026-07-29/fig04-training-vs-inference-scaling.png)

흥미로운 점은 DeepSeek-R1 계열 설명에서 자주 나오는 부분이다. **중간 reasoning trace 자체를 직접 채점하지 않아도, 최종 답 보상만으로 모델이 풀이·되돌아가기·자기수정 행동을 배울 수 있었다.** 이른바 “Aha moment”다. 모델이 중간에 “잠깐, 이건 틀렸다”는 식으로 경로를 바꾸는 장면이다.

> 핵심은 모델에게 긴 생각을 쓰라고 가르친 게 아니라, 맞는 답을 찾는 과정에서 긴 생각이 유용해지도록 만든 것이다.

물론 이 말이 reasoning trace를 그대로 믿어도 된다는 뜻은 아니다. trace는 모델 내부의 진짜 마음을 보여주는 창이라기보다, 문제를 풀기 위해 학습된 출력 형식에 가깝다. 하지만 제품 입장에서는 충분히 중요하다. trace가 길어질수록 token, latency, cost가 같이 늘어나기 때문이다.

## `<think>`는 능력이 아니라 경계표시다

많은 reasoning model은 `<think> ... </think>` 같은 토큰을 쓴다. 여기서 오해가 생긴다. 저 태그를 넣으면 모델이 생각을 더 잘하는 것처럼 보이기 때문이다.

Raschka의 설명은 단호하다. **`<think>` 토큰은 reasoning 능력을 만들어내는 장치가 아니다.** 주된 역할은 reasoning trace가 어디서 시작하고 끝나는지 표시하는 것이다. UI나 training pipeline이 중간 풀이와 최종 답을 분리할 수 있게 하는 경계선이다.

DeepSeek-R1 같은 모델에서는 format reward가 붙을 수 있다. 예를 들어 전체 보상을 `R_total = R_accuracy + R_format`처럼 두고, 정답 보상과 함께 `<think>` 블록 형식을 잘 지켰는지 보상한다. 그러면 모델은 reasoning trace를 해당 태그 안에 넣는 법을 배운다.

이건 꽤 현실적인 설계다. 사용자는 중간 풀이를 매번 보고 싶지 않을 수 있다. ChatGPT나 Codex 같은 UI가 “생각 중”은 감추고 최종 답만 보여주는 것도 이 분리 덕분이다. 개발자는 필요하면 trace를 로깅하거나 디버깅에 활용할 수 있다.

하지만 태그는 태그일 뿐이다. 같은 모델을 다른 delimiter로 훈련해도 비슷한 성능에 도달할 수 있다. 중요한 것은 **형식 토큰이 아니라, 그 형식을 따르도록 만든 post-training과 reward 구조**다.

## thinking on/off는 chat template에서 시작될 수 있다

초기 reasoning model은 꽤 불편했다. DeepSeek-R1처럼 reasoning 전용으로 나온 모델은 간단한 질문에도 장황하게 답한다. “2+2는?” 같은 질문에도 불필요하게 긴 reasoning을 만들 수 있다. 비용도 늘고, 사용감도 나빠진다.

그래서 Qwen3 같은 모델은 hybrid 방식을 실험했다. 같은 모델이 필요할 때는 reasoning model처럼, 필요 없을 때는 일반 instruction model처럼 행동한다. 사용자는 `enable_thinking=True/False` 같은 옵션을 고른다.

![원문 Figure 14. Qwen3 0.6B에서 thinking=False와 thinking=True의 응답 차이. 겉으로는 스위치 하나지만, 안쪽에서는 chat template과 prefill이 모드를 가른다. 출처: Sebastian Raschka.](/images/reasoning-effort-llm-control-2026-07-29/fig14-qwen3-thinking-toggle.png)

겉으로 보면 단순한 스위치다. 안쪽은 조금 흥미롭다. Qwen3에서 `enable_thinking=False`는 대체로 assistant 응답 앞에 빈 `<think></think>` 블록을 미리 넣는 방식으로 작동한다. 즉 “생각은 이미 끝났으니 바로 답하라”는 상태에서 모델 생성을 시작하게 한다.

학습 쪽에서는 Thinking Mode Fusion 같은 SFT 단계가 들어간다. 모델은 두 종류의 예시를 본다.

- `/think`: `<think>{reasoning}</think>{answer}`
- `/no_think`: `<think></think>{answer}`

이렇게 thinking/non-thinking 예시를 섞어 학습하면, inference 때 chat template이 어느 모드로 시작할지 정할 수 있다. `/think` 같은 자연어 플래그는 soft switch이고, 빈 `<think></think>`를 prefill하는 것은 hard switch에 가깝다.

여기서 실무 감각 하나가 나온다. **모드 전환은 단순 prompt 지시가 아니라, 그 지시를 따라본 데이터와 훈련 흔적이 있어야 잘 작동한다.** 임의의 모델에 “think less”라고 쓴다고 Qwen3식 on/off가 생기는 것은 아니다.

## reasoning effort는 같은 모델 안의 inference-time scaling이다

이제 핵심인 reasoning effort로 넘어간다. GPT 계열, gpt-oss, Inkling 같은 모델에서 보이는 low/medium/high, Light/Max/Ultra 같은 메뉴다. 모델은 그대로 두고, 답을 만들 때 쓸 reasoning budget을 바꾼다.

Raschka는 이를 training scaling과 inference scaling으로 나눠 설명한다. 더 큰 모델을 고르는 것은 이미 훈련된 다른 scale의 모델을 선택하는 일이다. 반면 reasoning effort를 올리는 것은 **같은 모델이 inference 시점에 더 많은 token과 compute를 쓰도록 허용하는 일**이다.

![원문 Figure 23. 왼쪽의 모델 선택은 서로 다른 모델 scale을 고르는 일이고, 오른쪽의 reasoning effort 선택은 같은 모델의 inference-time compute를 조절하는 일이다. 출처: Sebastian Raschka.](/images/reasoning-effort-llm-control-2026-07-29/fig23-two-scaling-axes.png)

직관적으로는 이렇다.

- 낮은 effort: 짧게 생각한다. 싸고 빠르다. 쉬운 질문에 적합하다.
- 높은 effort: 더 길게 생각한다. 비싸고 느리다. 어려운 코딩·수학·에이전트 작업에 적합하다.
- 너무 높은 effort: 성능은 조금 오르지만 비용 상승 대비 이득이 줄어든다.

Raschka가 인용한 gpt-oss, GPT-5.6, Inkling 관련 그림들은 대체로 같은 방향을 보여준다. effort를 올리면 생성 token이 늘고, benchmark 성능도 오르는 경향이 있다. 다만 높은 구간에서는 diminishing returns가 온다. 돈을 두 배 썼는데 점수는 아주 조금만 오르는 구간이 생긴다.

![원문 Figure 19. reasoning effort를 올리면 coding-agent benchmark 성능도 오르지만 API cost도 함께 증가한다. 고 effort 구간에서 수익 체감이 보이는 것이 핵심이다. 출처: Sebastian Raschka, Artificial Analysis Coding Agent Index v1.1 기반.](/images/reasoning-effort-llm-control-2026-07-29/fig19-cost-performance-effort.png)

이 지점이 제품적으로 중요하다. “최고 성능”만 보면 항상 high나 max를 고르고 싶다. 하지만 서비스에서는 latency, API cost, 사용자 체감, 실패 시 재시도 비용까지 같이 본다. **reasoning effort는 정확도 옵션이 아니라 unit economics 옵션**이다.

## effort level은 학습 때 비용 함수를 달리 주며 만들어진다

그럼 모델은 low와 high를 어떻게 구분할까. 공개된 상용 모델의 내부 구현은 알 수 없다. Raschka도 OpenAI의 세부 구현은 공개되지 않았다고 선을 긋는다. 대신 공개 모델과 technical report에서 몇 가지 패턴을 추정할 수 있다.

첫 번째는 system prompt에 effort label을 넣는 방식이다. gpt-oss chat template에서는 “Reasoning effort: low/medium/high” 같은 문구가 system message에 들어간다. ChatGPT UI의 메뉴도 결국 이런 내부 입력으로 매핑될 가능성이 있다.

두 번째는 그 label을 post-training에서 실제 행동과 연결하는 것이다. 예를 들어 SFT 단계에서 low effort prompt에는 짧은 reasoning target을, high effort prompt에는 긴 reasoning target을 붙인다. 모델은 effort label과 reasoning 길이의 관계를 예시로 배운다.

세 번째는 RLVR 단계에서 token cost를 달리 주는 방식이다. Raschka는 Inkling 사례를 통해 이를 설명한다. 원하는 effort level `e`를 system message에 넣고, reward를 대략 다음처럼 생각할 수 있다.

![원문 Figure 21. effort-conditioned RLVR와 SFT의 가능한 구현. effort label을 프롬프트에 넣고, 그에 맞는 reasoning 길이와 token cost를 학습시키는 구도다. 출처: Sebastian Raschka.](/images/reasoning-effort-llm-control-2026-07-29/fig21-effort-conditioned-training.png)

```text
R(e) = R_task - λ(e) * N_tokens
```

낮은 effort에서는 token penalty `λ(e)`를 크게 둔다. 길게 쓰면 손해다. 높은 effort에서는 penalty를 작게 둔다. 더 오래 생각해도 된다. 그러면 모델은 같은 문제라도 effort 값에 따라 reasoning 길이를 조절하는 법을 배운다.

Inkling은 effort를 0과 1 사이의 연속값으로 다룬다는 점이 흥미롭다. low/medium/high 같은 등급이 아니라 “thinking effort level: 0.8”처럼 줄 수 있다. 이건 UI 관점에서는 슬라이더에 가깝고, 하네스 관점에서는 router가 세밀하게 조절할 수 있는 숫자다.

## 공개 모델들은 서로 다른 방식으로 같은 문제를 푼다

Raschka 글 후반은 꽤 긴 technical report 순례다. DeepSeek V4, Nemotron 3 Ultra, Kimi K2.5/K3, GLM-5, Qwen3, Inkling을 비교한다. 세부는 다르지만, 저는 세 가지 공통 패턴으로 읽었다.

첫째, **chat template과 SFT로 모드의 문법을 만든다.** Qwen3는 thinking/non-thinking 예시를 섞고, GLM-5는 turn-level thinking과 tool-use 상황의 thinking pattern을 다룬다. 모델이 “이런 입력이면 이런 출력 형식”을 배운다.

둘째, **RL 단계에서 길이와 비용을 조정한다.** DeepSeek V4는 모드별 context window와 length penalty가 다르고, Inkling은 effort 값에 따라 token penalty를 조정한다. Nemotron 3 Ultra도 medium-effort를 SFT와 RLVR에서 다룬다.

셋째, **hard budget에 견디는 훈련을 넣는다.** Nemotron은 reasoning trace를 무작위 token budget에서 자른 뒤 답으로 넘어가는 예시를 만든다. Qwen3는 강제로 reasoning span이 멈춘 뒤에도 최종 답을 이어갈 수 있다. Kimi 계열은 budgeted phase와 unconstrained phase를 오가며 token-efficient reasoning을 학습한다.

이 비교가 중요한 이유는 하나다. **비슷한 UI 라벨 뒤에 완전히 다른 훈련 레시피가 숨어 있을 수 있다.** 어떤 모델의 “medium”과 다른 모델의 “medium”은 같은 의미가 아니다. 하나는 SFT로 배운 짧은 답변 모드일 수 있고, 다른 하나는 RL에서 token penalty가 다르게 걸린 모드일 수 있다.

![원문 Figure 32. 공개 technical report 기준으로 reasoning effort 구현 방식을 비교한 표. 같은 “effort”라는 단어 아래에 SFT, chat template, mode-conditioned RL, hard budget 같은 서로 다른 장치가 섞여 있다. 출처: Sebastian Raschka.](/images/reasoning-effort-llm-control-2026-07-29/fig32-open-weight-comparison.png)

그러니 benchmark를 볼 때도 “무슨 모델인가”만 보면 부족하다. 어떤 effort였는지, budget은 얼마였는지, reasoning trace를 강제로 잘랐는지, tool-use 작업에서 같은 설정이었는지까지 봐야 한다.

## 다음 문제는 자동 effort 선택이다

Raschka가 마지막에 던지는 “holy grail”은 자동 effort 선택이다. 사용자가 매번 Light, Medium, Max를 고르는 건 귀찮다. 이상적으로는 싼 router나 agent harness가 요청의 난이도, 남은 시간, token budget, tool state를 보고 알아서 effort를 고른다.

저도 이 방향이 맞다고 본다. 특히 에이전트에서는 더 그렇다. 한 작업 안에서도 단계별로 필요한 생각 깊이가 다르다.

- 파일 목록을 훑는 단계: low effort로 충분하다.
- 실패 원인을 좁히는 단계: medium 이상이 필요하다.
- patch 전략을 세우고 regression risk를 보는 단계: high가 낫다.
- 이미 검증된 명령을 실행하는 단계: 다시 low로 내려도 된다.

이걸 전부 같은 max effort로 돌리면 비용이 터진다. 반대로 전부 low로 돌리면 어려운 순간에 멍청해진다. 그래서 앞으로 좋은 agent harness는 “도구를 잘 부르는가”만이 아니라, **생각 예산을 언제 올리고 내리는가**까지 포함하게 될 가능성이 크다.

여기서 사용자 override도 필요하다. 빨리 대충 보고 싶은 때가 있고, 비용이 들더라도 끝까지 물고 늘어져야 하는 때가 있다. 자동 선택이 기본이 되더라도, “이번 건 high로 가자”는 사람의 의사결정은 남아야 한다.

## 모델 선택보다 예산 배분이 더 중요해지는 순간

이 글이 재미있는 이유는 화려한 신모델 소개가 아니라, 아주 실무적인 비용 구조를 설명하기 때문이다. reasoning effort는 “모델이 생각한다”는 말의 낭만을 걷어내고, token, latency, reward, budget이라는 공학 단위로 바꿔준다.

앞으로 LLM 제품을 만든다는 것은 단순히 더 좋은 모델을 붙이는 일이 아닐 수 있다. 같은 모델이라도 어떤 요청에는 짧게, 어떤 요청에는 길게, 어떤 단계에서는 여러 rollout을, 어떤 단계에서는 바로 답을 쓰게 만드는 일이다.

그러면 질문도 바뀐다.

“이 모델이 제일 똑똑한가?”보다 “이 작업에 얼마만큼의 생각을 사는 게 맞는가?”가 더 중요해진다. reasoning effort 메뉴는 작아 보이지만, 사실은 LLM을 제품 안에 넣을 때 피할 수 없는 경제학의 입구다.

저는 이 흐름이 에이전트 하네스 설계와 바로 맞닿아 있다고 봅니다. 더 실습해보고 싶은 분들은 제가 정리한 오픈클로 책 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)와 [AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)도 참고해보시면 좋습니다. 여기서 말한 effort router, budget, harness 감각을 실제 자동화 루프로 옮겨보는 쪽에 가깝습니다.
