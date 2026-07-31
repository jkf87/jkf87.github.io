---
title: "Jeff Dean이 말한 AI 시대의 1% 룰: 모델보다 루프를 설계하는 사람이 이긴다"
date: 2026-07-31
draft: false
tags:
  - AI
  - agents
  - context-engineering
  - hardware
  - startups
  - YC
categories:
  - AI
  - Agent
  - Startup
description: "Y Combinator 인터뷰 ‘Jeff Dean: The 1% Rule for Building in AI’를 뉴스레터 형식으로 발췌·정리했다. 핵심은 더 큰 모델이 아니라 inference hardware, context engineering, skills, multi-agent search, spec, taste, automated experiment loop다."
aliases:
  - /posts/jeff-dean-one-percent-rule-ai-2026-07-31
---

![Y Combinator 무대에서 Jeff Dean이 57분 동안 AI 시스템, 하드웨어, 에이전트, 창업자의 문제 선택을 이야기하는 인터뷰 장면. 이 인터뷰는 “모델이 좋아진다”보다 “무엇을 루프로 만들 것인가”에 가깝다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/opening.jpg)

Jeff Dean 인터뷰는 길다. 그런데 긴 이유가 있다. 한 질문에서 TPU가 나오고, 다음 질문에서 context engineering이 나오고, 다시 agent harness, startup wedge, crisp spec, taste, MapReduce, AlphaEvolve, distillation rejection까지 이어진다. 겉으로는 “AI 시대에 무엇을 만들 것인가”라는 YC식 창업자 인터뷰인데, 실제로는 **AI 시스템을 어디까지 자동 실험 루프로 바꿀 수 있는가**를 묻는 대화다.

Y Combinator가 공개한 [Jeff Dean: The 1% Rule for Building in AI](https://www.youtube.com/watch?v=CxXgV54KzpQ)는 57분짜리 인터뷰다. 제목의 1% 룰은 본문에서 명시적 공식처럼 길게 설명되지는 않지만, 인터뷰 전체에 깔린 기준은 분명하다. **일반 모델이 20%쯤 할 수 있는 문제보다, 아직 0~1%밖에 못 하는 문제를 찾아야 한다.** 그리고 그 문제를 그냥 prompt로 밀어붙이는 것이 아니라, hardware, data movement, skill, evaluator, spec, taste까지 포함한 시스템으로 바꿔야 한다.

저는 이 인터뷰를 보면서, AI 창업자나 agent builder에게 가장 중요한 문장이 이것이라고 봤다. “모델은 전체 시스템의 한 조각일 뿐이다.” Jeff Dean은 더 큰 모델을 부정하지 않는다. 다만 앞으로의 차이는 모델 주변의 루프, 즉 **어떤 정보를 context로 넣고, 어떤 tool을 쓰게 하고, 어떤 evaluator로 되돌리고, 어떤 hardware에서 낮은 latency로 돌릴 것인가**에서 생긴다고 말한다.

## 이번 글이 답하는 질문

이 글은 인터뷰를 순서대로 따라가되, 실무자가 바로 가져갈 수 있게 여섯 질문으로 다시 묶었습니다.

1. 2027년의 AI 진전은 왜 “모델이 똑똑해진다”가 아니라 “ML 시스템 자체가 자동화된다”인가?
2. Jeff Dean은 왜 inference hardware와 energy를 2026년의 핵심 숫자로 보는가?
3. context engineering은 prompt engineering과 무엇이 다른가?
4. agent가 step 30~50에서 무너질 때, skill과 multi-agent search는 어떤 역할을 하는가?
5. Google이 general model을 만들 때, 2~3인 스타트업은 어디서 이길 수 있는가?
6. 코드가 agent에게 넘어간 뒤에도 인간에게 남는 희소 기술은 무엇인가?

## 먼저 전체 흐름부터 잡고 가자

인터뷰는 “AI가 주니어 엔지니어 수준에 도달했나?”라는 질문으로 시작한다. Jeff Dean은 agent 기반 장시간 코딩 작업에서 모델이 “꽤 capable”해졌고, 주니어 엔지니어라는 표현도 정의에 따라 꽤 맞아 들어간다고 답한다. 그가 과소평가한 것은 속도다. 복잡한 작업을 수행하는 능력이 예상보다 빨리 커졌고, 코딩 밖의 도메인에서도 agent-based systems가 빛나기 시작했다.

바로 다음 예측이 중요하다. 2027년에는 **ML 시스템이 자기 자신을 개선하는 자동 실험 루프**가 훨씬 커질 것이라고 한다. 문제를 하위 문제로 쪼개고, 자동으로 실험을 많이 돌리고, 결과를 합쳐 더 나은 시스템을 만드는 흐름이다. 이건 ML에만 국한되지 않는다. Jeff Dean은 “측정 가능한 objective가 있는 과학과 공학”이면 같은 방식으로 진전될 수 있다고 본다.

> “Anything where you can have a measurable objective.” 측정 가능한 목표가 있으면, agent는 실험 루프를 돌릴 수 있다. 이 문장이 이 인터뷰의 바닥에 깔려 있다.

그리고 초반에 나온 “이미 틀린 가정”도 여기와 연결된다. Jeff Dean은 많은 사람이 아직 agent가 며칠, 심지어 몇 주 동안 복잡한 문제를 붙잡고 갈 수 있다는 점을 충분히 내면화하지 못했다고 말한다. 예컨대 기존 software를 더 안전하거나 더 빠른 속성을 가진 다른 programming language로 새로 구현하게 하는 작업처럼, 특정 도메인에서는 agent가 한두 시간짜리 assistant가 아니라 **장기 실행되는 작업자**가 될 수 있다는 것이다.

여기서부터 대화는 과거의 Google 시스템 이야기로 돌아갔다가, 다시 현재의 AI 시스템으로 온다. 2001년 Google 검색이 디스크에서 RAM으로 넘어간 “fits in memory moment”, 2013년 speech recognition과 TPU의 냅킨 계산, AI 시대의 latency numbers, context engineering, skills, multi-agent systems, startup strategy, taste, unreliable transistor thought experiment, MapReduce, AlphaEvolve, distillation rejection까지 이어진다.

![2001년 Google 검색의 “메모리에 들어가는 순간”을 현재 AI에서는 inference hardware 문제로 바꿔 설명하는 인터뷰 장면. agent를 많은 사람에게 쓰게 하려면 latency와 energy가 제품 가능성을 정한다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/inference-hardware.jpg)

## 2026년의 “메모리에 들어가는 순간”은 inference hardware다

인터뷰 진행자는 2001년 Google 검색 이야기를 꺼낸다. 당시 Google 검색은 하드디스크 위에서 돌아갔고, Jeff Dean과 Sanjay Ghemawat은 언젠가 전체 검색 인덱스가 모든 서버의 RAM에 들어갈 수 있다는 계산을 한다. 며칠 만에 RAM 기반 검색 버전을 production에 넣었고, Google 검색이 훨씬 빨라지는 계기가 됐다는 이야기다.

그럼 2026년의 “fits in memory moment”는 무엇인가. Jeff Dean의 답은 메모리가 아니라 **고성능·저전력 inference hardware**다. agent-based systems를 더 많은 사람에게 제공하려면 inference가 핵심이고, latency가 중요하며, specialized hardware가 범용 GPU/TPU보다 더 낮은 latency와 에너지 효율을 만들 수 있다는 설명이다.

그가 던진 상상은 단순하다.

> “Latency가 50배 좋아진다면 무엇을 할 수 있을지 상상해보라.”

이 문장은 제품 질문이다. 지금 우리가 agent를 기다리는 시간은 그냥 UX 문제가 아니다. 어떤 agent workflow는 latency 때문에 애초에 제품이 되지 못한다. 대화가 50배 빨라지면, 지금은 batch job처럼 보이는 일이 실시간 인터랙션이 된다. 코딩 agent도, 연구 agent도, 사무 agent도 마찬가지다. “기다림이 줄어든다”가 아니라, **가능한 제품의 모양이 바뀐다.**

## TPU의 시작은 “모든 사용자가 하루 3분 말하면 서버를 두 배로 늘려야 한다”는 계산이었다

![TPU의 시작을 speech recognition 사용량과 CPU fleet 계산으로 설명하는 인터뷰 장면. 화려한 칩 이야기는 결국 냅킨 계산에서 출발했다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/tpu-linear-algebra.jpg)

TPU의 기원도 같은 방식으로 설명된다. 2013년 무렵 Google의 deep learning 기반 speech recognition은 기존 시스템보다 계산 비용은 비쌌지만 오류율을 절반으로 줄였다. Jeff Dean은 이것을 “몇 달 만에 20년치 speech recognition 발전이 일어난 것”에 가깝게 봤다.

문제는 좋은 기술이 나오면 사람들이 더 많이 쓴다는 점이다. 모든 Google 사용자가 하루 3분만 음성 인식을 쓰면, CPU 서버 fleet을 두 배로 늘려야 할 수 있다는 냅킨 계산이 나왔다. 그래서 CPU로 버티는 대신, low precision dense linear algebra에 특화된 chip을 만들기 시작했다. 그게 TPU의 시작이다.

초기 TPU는 당시 CPU/GPU 대비 30~80배 더 에너지 효율적이었고, latency도 20~30배 낮았다고 한다. 중요한 것은 “과특화”의 정도다. Transformer는 TPU 이후에 나왔다. 그래서 TPU는 특정 모델 하나를 위한 칩이 아니라, **ML 알고리즘이 계속 바뀔 것을 전제로 한 범용 선형대수 시스템**으로 설계됐다. 충분히 특화해 큰 이득을 얻되, 알고리즘 변화에 완전히 갇히지는 않는 지점이다.

여기서 창업자가 가져갈 질문은 “내 아이디어가 TPU급인가?”가 아니다. 훨씬 작고 실용적인 질문이다.

> 오늘 밤 내가 해야 할 냅킨 계산은 무엇인가. 지금 방식이 당연하다고 생각해서 못 보고 있는 병목은 무엇인가. first principles로 다시 보면 한두 자릿수(order of magnitude) 개선이 가능한가.

Jeff Dean은 이렇게 말한다. 현재 문제 풀이 방식에 고정되지 말고, bottleneck을 보고, 완전히 다른 접근으로 10배나 100배 개선할 수 있는지 생각하라. 창업자의 계산은 pitch deck보다 먼저다.

## AI 시대의 latency numbers: 계산보다 데이터 이동이 비싸다

예전 distributed systems 엔지니어에게는 “latency numbers every programmer should know”가 있었다. cache miss, disk seek, network packet이 대략 얼마나 걸리는지 감각적으로 알아야 했다. 진행자는 2026년 AI 버전의 latency numbers를 묻는다.

Jeff Dean의 답은 accelerator 내부 숫자다. main memory에서 on-chip memory로, 다시 multiplier unit으로 가는 bandwidth. 곱셈 한 번에 드는 에너지. 칩 간 interconnect bandwidth. 500개 칩을 연결할 때와 10,000개 칩을 연결할 때 network bandwidth가 어떻게 떨어지는지. 이런 숫자들이 AI 시스템 설계를 바꾼다.

가장 선명한 숫자는 이것이다. **계산 자체는 약 1 picojoule 수준이지만, HBM에서 데이터를 가져오는 비용은 그 1000배쯤 될 수 있다.** 그래서 batching이 생긴다. 데이터를 한 번 가져왔을 때 여러 token, 여러 example을 처리해 data movement 비용을 나눠 먹어야 한다. 그런데 low latency inference에서는 큰 batch가 불리하다. 효율과 지연시간이 서로 당긴다.

이 대목이 흥미로운 이유는, 우리가 종종 “모델 문제”라고 부르는 것이 실제로는 **energy와 data IO 문제**이기 때문이다. batch size, epoch, latency, cost, throughput은 모델 논문에 붙은 부록이 아니라 제품 가능성을 결정하는 시스템 변수다.

## context engineering은 모델 밖에서 모델을 더 똑똑하게 만드는 일이다

![모델을 “전체 시스템의 한 조각”이라고 설명하는 인터뷰 장면. retrieval, memory, tools, context, orchestration이 붙으면서 모델의 능력은 파라미터 안이 아니라 실행 루프 전체에서 나온다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/context-engineering.jpg)

인터뷰 중반부터는 context engineering으로 넘어간다. 진행자는 AI progress가 더 이상 모델 크기와 데이터만의 문제가 아니라 retrieval, tools, memory, agent tools, context engineering으로 옮겨가고 있다고 말한다. Jeff Dean의 답은 명확하다.

모델은 전체 시스템의 한 조각이다. 좋은 시스템은 모델이 도구를 쓰고, 관련 정보를 가져오고, 과거 정보나 작업 history를 context에 넣고, 문제를 tool call sequence로 분해하고, 여러 접근을 시도한 뒤 평가한다. training data는 수조 token이 수천억·수조 parameter의 “soup” 속에 섞인 정보지만, context는 모델이 지금 직접 보는 선명한 정보다.

이건 prompt engineering보다 넓다. prompt는 “어떻게 말할까”에 가깝다. context engineering은 **모델이 일을 잘하게 하기 위해 어떤 외부 구조를 붙일까**에 가깝다. tool, retrieval, memory, skill, evaluator, harness가 모두 포함된다.

Jeff Dean이 든 개인 사례가 좋다. 그와 Sanjay는 Google 내부 low-level library 성능 개선을 할 때 microbenchmark를 자주 돌린다. 현재 성능을 측정하고, 코드 변경을 하고, 다시 benchmark를 돌리고, cache footprint도 보고, 더 넓은 benchmark set으로 확인하는 식이다. 이 사람이 하던 순서를 skill로 써서 모델에게 줬다. 그러자 모델이 benchmark 측정 → 코드 변경 → 성능 재측정 → 반복 개선을 수행할 수 있었다.

![성능 최적화 skill 사례를 설명하는 인터뷰 장면. Jeff Dean처럼 생각하는 모델을 만든 게 아니라, Jeff Dean과 Sanjay가 하던 절차를 모델이 실행할 수 있는 형태로 써준 것이다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/performance-skill.jpg)

여기서 핵심은 “모델이 Jeff Dean처럼 됐다”가 아니다. **사람이 쓰는 접근법을 모델이 사용할 수 있는 형태로 바깥에 적어줬다**는 점이다. 이게 skill이다. 좋은 skill은 모델에게 지식을 주는 문서이면서, 동시에 행동 순서를 주는 실행 레일이다.

여기에 공개 문서 이야기도 붙는다. Jeff Dean은 Sanjay와 함께 쓴 약 30쪽짜리 `Performance Hints` 문서를 언급한다. 사람들이 그 문서를 요약해 모델에 넣었더니 code performance issue를 더 잘 reasoning하게 됐다는 것이다. 이 사례가 중요한 이유는, 조직 안의 암묵지가 꼭 거대한 fine-tuning으로만 전달되는 것이 아니라 **좋은 문서와 skill 형태로도 모델의 작업 능력을 끌어올릴 수 있음**을 보여주기 때문이다.

## agent가 길게 달리려면 “밝게 비춰진 길”과 탐색이 필요하다

진행자는 누구나 경험한 문제를 묻는다. agent가 step 10까지는 괜찮다가, step 30~50쯤 가면 흔들리는 이유는 무엇인가. Jeff Dean은 기계학습 모델 일반의 문제로 답한다. 모델이 훈련 분포에서 조금 벗어나면 성능이 떨어진다. 더 멀어질수록 더 흔들린다.

그래서 skill과 hint가 필요하다. Jeff Dean 표현으로는 모델을 “more brightly lit path”, 더 밝게 비춰진 길 안에 머물게 한다. 모델이 이미 잘 아는 방식, 안전한 절차, 검증 가능한 루틴으로 문제 풀이를 유도한다.

하지만 이것만으로 충분하지 않다. 긴 agent flow에서는 여러 agent가 서로 다른 접근을 시도하고, 다른 모델이나 agent가 그중 유망한 것을 평가하는 방식이 중요해진다. inference-time compute를 써서 가능한 해결 경로의 공간을 탐색하고, promising하지 않은 경로를 버리는 것이다.

![긴 agent flow에서 multi-agent search와 evaluator를 설명하는 인터뷰 장면. 여러 agent가 다른 경로를 시도하고, evaluator가 유망한 경로를 고르면 step 30~50 이후의 안정성이 올라간다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/multi-agent-search.jpg)

이 말은 요즘 agent 제품을 만드는 사람에게 꽤 직접적이다. “우리 agent가 왜 자꾸 이상한 길로 가지?”라고 느낀다면, 문제는 모델 하나가 아니라 harness일 수 있다. skill이 부족하거나, evaluator가 없거나, 실패한 경로를 계속 끌고 가는 구조일 수 있다.

Google 내부에서는 개발환경용 harness와 skill이 있어 agent가 coding tool, code review, performance measurement, log fetching 같은 내부 도구를 쓸 수 있게 한다고 한다. 모델이 Google 내부 도구를 훈련받지 않았더라도, skill definition이 있으면 사용할 수 있다. 이건 agent의 능력이 모델 파라미터뿐 아니라 **조직의 도구 사용법을 얼마나 agent-readable하게 만들었는가**에 달려 있다는 뜻이다.

## 스타트업은 general model이 0~1%만 성공하는 문제를 찾아야 한다

![2~3인 팀의 기회를 이야기하는 인터뷰 장면. general model이 이미 20%쯤 하는 문제라면 6~12개월 안에 따라잡힐 수 있으니, 지금 0~1%만 되는 문제를 찾으라는 조언이 나온다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/startup-domains.jpg)

진행자는 YC다운 질문을 던진다. Google은 processor부터 product까지 co-design한다. 그러면 2~3인 팀은 어디서 이길 수 있는가.

Jeff Dean의 답은 균형 잡혀 있다. Google과 Gemini는 거의 모든 것을 할 수 있는 general model을 만들려 한다. 그렇기 때문에 특정 domain에는 충분한 attention을 주지 못할 수 있다. 그 영역에서 잘 설계된 surface, domain-specific skill set, specialized model이 advantage가 될 수 있다.

단, 조심해야 한다. general model은 계속 넓어진다. 내가 고른 문제가 6개월이나 12개월 안에 frontier model에 흡수될지 판단해야 한다. Jeff Dean의 기준은 꽤 날카롭다.

> 지금 general model이 그 일을 0% 또는 1% 성공한다면 좋은 신호다. 이미 20%쯤 성공한다면, capability가 생기기 시작했다는 뜻이고 곧 좋아질 가능성이 높다.

이게 제목의 1% 룰에 가장 가까운 대목이다. 스타트업은 “모델이 아직 전혀 못 하는 문제”를 찾아야 한다. 특히 personal information처럼 general model이 접근하지 못하는 데이터가 있거나, 특정 domain data로 작고 정확한 niche model을 만들 수 있거나, AlphaFold처럼 매우 구체적인 domain에서 정확도가 압도적으로 중요한 문제라면 기회가 있다. Jeff Dean은 protein folding의 AlphaFold, material science, chip design을 예로 든다.

여기서 중요한 것은 “niche”가 작다는 뜻이 아니라는 점이다. protein folding은 niche지만 세상에 미치는 영향은 작지 않다. chip design도 마찬가지다. 좋은 niche는 시장이 작은 틈새가 아니라, **general model이 아직 학습·접근·평가하기 어려운 고밀도 문제 공간**이다.

## AI-native founder의 기본기는 crisp spec이다

다음 질문은 50~100개의 agent를 관리하는 창업자의 능력이다. Jeff Dean은 crisp design docs/specs를 강조한다. agent에게 원하는 것을 명확히 지정할수록 성공률이 올라간다. 반대로 불명확하면 agent가 의도를 추론해야 하고, 사람의 상상과 다른 해석을 할 수 있다.

![agent 시대의 crisp spec을 설명하는 인터뷰 장면. 사람에게 넘기던 암묵지를 agent가 읽을 수 있는 형태로 적어야 하므로 spec은 더 중요해진다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/crisp-specs.jpg)

그가 든 예시는 언어 변환이다. Python 구현을 Go 구현으로 옮기는 작업은 오늘날 모델이 매우 잘한다. 왜냐하면 기존 Python 코드와 테스트가 매우 상세한 specification 역할을 하기 때문이다. 모델은 테스트를 Go로 옮기고, 동작 차이를 비교하고, 차이가 사라질 때까지 수정할 수 있다.

이 대목은 “AI가 코드를 써주니 기획만 하면 된다”는 말보다 훨씬 엄격하다. 이제 spec은 PM 문서가 아니라 실행 자산이다. 잘 쓴 spec은 agent fleet의 작업 품질을 좌우한다. “대충 이런 느낌”은 인간 동료에게는 회의로 보완될 수 있지만, agent에게는 엉뚱한 추론 공간을 열어준다.

## 코드가 자동화되면 희소해지는 것은 taste다

그렇다면 모두가 수백 개 agent를 돌리고 코드가 자동으로 작성되는 시대에는 무엇이 희소해질까. Jeff Dean은 taste라고 답한다. 무엇을 agent에게 시킬지 고르는 감각이다.

그는 연구자의 예를 든다. 연구자는 도구와 기술을 가질 수 있지만, 싸움의 대부분은 어떤 문제에 시간을 쓸지 고르는 데 있다. 지루한 문제를 아름답게 실행하는 것보다, 중요한 문제를 잘 고르고 해결하는 것이 훨씬 낫다.

Taste를 기르는 방법도 이야기한다. 과거 여러 문제를 풀어본 경험이 미래에 흥미로운 문제를 감지하게 해준다. 또 하나는 앞으로 12개월 동안 중요할 것 같은 것들을 적어두고, 12개월 뒤에 실제로 무엇이 중요했는지 되돌아보는 것이다. 자기 예측의 표본을 늘리는 방식이다.

저는 이 조언이 꽤 실용적이라고 봤다. taste는 타고난 감각처럼 말해지지만, Jeff Dean은 그것을 **예측하고, 기록하고, 나중에 채점하는 루프**로 바꾼다. 좋은 문제 선택도 결국 feedback loop가 있어야 개선된다.

## 가끔은 60년 된 가정을 의심해야 한다

![오류 나는 트랜지스터 thought experiment를 설명하는 인터뷰 장면. 당장 하자는 말이 아니라, 당연한 가정을 흔들어보는 연습이다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/unreliable-transistors.jpg)

진행자가 “crazy thought experiment”를 묻자 Jeff Dean은 반도체 산업의 가정을 건드린다. 지난 60년 동안 chip design과 fabrication은 같은 design의 모든 chip이 동일하고, transistor error rate가 극도로 낮아야 한다는 방향으로 발전해왔다. bit flip은 나쁜 일이다. ECC memory도 그 전제 위에 있다.

그런데 대규모 분산 시스템은 다르게 설계한다. 개별 disk, machine, rack switch는 실패할 수 있다. 그래도 상위 레벨에서 replication, Reed-Solomon coding, checkpointing을 통해 reliable system을 만든다. 그렇다면 transistor level에서도 같은 질문을 할 수 있지 않을까.

하루에 20번 오류가 나는 transistor로 시스템을 만든다면? 신호를 여러 redundant path로 보내야 할 수 있다. 설계 방법이 완전히 달라질 수 있다. Jeff Dean은 “이걸 하자”가 아니라, 이런 식으로 오래된 가정을 가끔 다시 물어야 한다고 말한다. 대부분은 50년 동안 그렇게 한 좋은 이유가 있을 것이다. 그래도 가끔은 다시 의심해야 한다.

실제로 성공한 사례로는 TPU와 MapReduce를 든다. TPU는 당시 아직 그렇게 커 보이지 않았던 niche domain을 위해 hardware를 specialize한 가정 뒤집기였다. MapReduce는 crawling/indexing code에서 parallelization, checkpointing, reliability code가 실제로 하고 싶은 간단한 계산을 가리고 있다는 관찰에서 나왔다. functional language의 map/reduce abstraction을 가져와, 아래에는 reliability를 넣고 위에는 간단한 계산을 쓰게 했다.

## AI가 AI를 만드는 루프: 실험 제안, 구현, 평가, 통합

![AlphaChip, AlphaEvolve와 자동 실험 루프를 설명하는 인터뷰 장면. high-level objective를 subproblem으로 쪼개고, 각 하위 문제에서 빠른 실험 루프를 돌린 뒤, 결과를 다시 통합하는 orchestration framework가 핵심이다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/automated-experiment-loop.jpg)

후반부의 핵심은 automated scientific method다. 과학 방법론은 실험을 제안하고, 구현하고, 평가하고, 결과를 반영하는 루프다. 이 루프를 자동화하고 latency를 낮추면 science, engineering, ML model design, chip design이 모두 빨라진다.

Jeff Dean이 그리는 시스템은 이렇다. high-level objective가 있다. orchestration framework가 그것을 subproblem으로 쪼갠다. 각 subproblem은 자동 실험 루프를 돌려 가장 좋은 해결책을 찾는다. 다시 framework가 subproblem solution을 합쳐 전체 문제의 해법으로 만든다.

여기서 evaluator가 중요하다. 좋은 evaluator가 있는 영역, formal verification에 가까운 영역은 특히 유망하다. 그런데 evaluator 자체가 너무 느리면 루프가 돌지 않는다. 그래서 evaluator를 빠르게 만드는 것도 핵심이다.

그가 든 예가 quantum chemistry다. density functional theory simulator로 한 분자 configuration의 property를 계산하려면 하룻밤이 걸릴 수 있다. 동료들은 expensive simulator의 input/output을 모아 neural approximation을 학습했고, 거의 정확하면서 300,000배 빠른 validator를 만들었다고 한다. 그러면 1,000만 후보를 몇 달 동안 계산하는 대신, 점심시간 동안 screening할 수 있다.

이건 AI 자동화의 본질을 잘 보여준다. agent가 실험을 많이 하려면, 생각만 빨라서는 안 된다. **검증도 빨라야 한다.** 느린 evaluator를 빠른 learned validator로 바꾸면 과학의 탐색 공간 자체가 달라진다.

## reject된 distillation 논문과 “그래도 계속하라”

![distillation 논문 rejection 일화를 말하는 인터뷰 장면. 한때 “impact가 크지 않을 것”이라는 리뷰를 받았지만, 지금은 큰 모델을 작고 빠른 모델로 옮기는 핵심 기술 중 하나가 됐다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/distillation-rejection.jpg)

후반에는 rejection 이야기도 나온다. Jeff Dean, Geoffrey Hinton, Oriol Vinyals가 쓴 distillation 논문은 당시 “significant impact가 없을 것 같다”는 리뷰를 받았다고 한다. 큰 teacher model의 지식을 더 작고 빠른 student model로 옮기는 방법인데, 지금은 업계에서 널리 쓰는 기술이다.

Jeff Dean은 리뷰어를 탓하지 않는다. 리뷰어는 대규모 AI 서비스를 직접 운영하는 관점이 없었을 수 있다. Google 입장에서는 큰 모델을 더 싸고 빠른 모델로 만드는 일이 절실했다. 논문은 arXiv에 올렸고, 사람들은 읽고 사용했다. Gemini Flash도 큰 Pro model에서 distillation을 활용해 크기와 속도 대비 강력해졌다고 말한다.

진행자가 “교훈은 reject되어도 계속 가라는 것”이라고 하자 Jeff Dean은 웃으며 “그게 제가 distill하고 싶은 lesson”이라고 답한다. 농담처럼 지나가지만, 이 인터뷰 전체와도 맞닿아 있다. 중요한 문제를 고르는 taste가 있다면, 외부의 초기 반응 하나로 멈추지 않는다.

## 젊은 Jeff Dean이라면 지금 무엇을 할까

마지막 질문은 개인적이다. 1999년 20명짜리 Google에 합류했던 젊은 Jeff Dean이 지금이라면 frontier lab에 갈까, 창업할까.

Jeff Dean은 정답을 주지 않는다. 대신 세 질문을 던진다.

- 정말 관심 있는 문제인가?
- 좋아하는 동료들과 함께 진전시킬 수 있는가?
- 성공했을 때 세상에 긍정적인 차이를 만드는가?

큰 조직에는 구조, 훌륭한 동료, 큰 플랫폼, 이미 존재하는 impact channel이 있다. 작은 스타트업은 위험이 크지만, 가까운 사람들과 열정 있는 문제를 풀며 매우 보람 있을 수 있다. 다만 최선의 결과가 나와도 세상이 “음, 멋지네, 근데 뭐?”라고 할 문제라면 시간을 쓰지 말라고 한다.

팀에 대해서도 비슷하다. 필요한 기술을 가진 사람을 찾아야 하지만, 함께 있는 것이 즐거운 사람이어야 한다. low ego, team player, complementary skills가 중요하다. 좋은 팀은 혼자 할 수 없는 것을 함께 만들고, 서로의 tool belt를 넓힌다.

![팀과 tool belt를 이야기하는 인터뷰 장면. low ego, complementary skills, 계속 넓어지는 tool belt. 사람이 고르는 문제와 함께 일하는 방식은 아직 자동화되지 않았다.](/images/jeff-dean-one-percent-rule-ai-2026-07-31/toolbelt-team.jpg)

마지막으로 그는 앞으로 누군가 풀었으면 하는 문제들을 나열한다. 새로운 hardware 접근, 훨씬 효율적인 inference hardware, 더 data-efficient한 ML 알고리즘, continual learning, multi-agent interactions, 더 나은 사회적 discourse. 특히 data efficiency 이야기가 인상적이다. 오늘날 frontier model은 18세 인간보다 약 1000배 많은 데이터를 봤을 가능성이 있는데, 인간은 많은 영역에서 여전히 더 낫거나 비슷하다. 그렇다면 훨씬 적은 데이터로 계속 배우는 시스템은 아직 큰 미해결 문제다.

## 이 인터뷰의 실무적 결론: 모델을 기다리지 말고 루프를 만들어라

이 인터뷰를 “Jeff Dean의 위대한 시스템 회고”로만 읽으면 조금 아깝다. 물론 MapReduce, TPU, distillation 이야기는 재미있다. 하지만 지금 실무자에게 더 중요한 메시지는 이쪽이다.

**AI 제품의 차이는 모델 하나가 아니라 루프에서 난다.**

Inference hardware가 빨라지면 제품의 모양이 바뀐다. Data movement 비용을 이해하면 latency와 batching의 trade-off가 보인다. Context engineering을 잘하면 외부에서 모델 파라미터를 바꾸지 않고도 모델의 행동이 좋아진다. Skill은 사람의 작업 절차를 agent-readable하게 만드는 방식이다. Multi-agent search와 evaluator는 긴 agent flow를 안정화한다. Crisp spec은 agent fleet의 입력 품질을 정한다. Taste는 무엇을 시킬지 고르는 인간의 희소 기술로 남는다.

그래서 이 인터뷰를 보고 나서 바로 해볼 일은 거창하지 않다.

1. 내 제품·업무에서 general model이 아직 0~1%만 성공하는 문제를 찾는다.
2. 그 문제를 사람이 어떻게 푸는지 절차를 적어 skill로 만든다.
3. 실패를 빠르게 판정할 evaluator를 만든다.
4. 가능하면 여러 agent가 다른 경로를 시도하게 하고, 좋은 경로만 살린다.
5. 12개월 뒤 중요해질 것 같은 문제를 기록하고, 나중에 내 taste를 채점한다.

이 정도면 충분히 작게 시작할 수 있다. Jeff Dean식으로 말하면, 냅킨 계산은 오늘 밤에도 할 수 있다. 중요한 것은 “AI가 언젠가 더 좋아지면”을 기다리는 것이 아니라, 지금 모델 주변에 어떤 실험 루프를 만들 수 있는지 보는 일이다.

---

편집자 주: 더 실습해보고 싶은 분들을 위한 참고 자료도 남겨둡니다. 에이전트와 자동화 루프를 직접 만들어보고 싶다면 코난쌤의 책 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902), 그리고 [AIFrenz 빌드캠프 · 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184) 강의가 도움이 됩니다. 이 글에서 말한 skill, evaluator, loop를 실제 작업 흐름으로 옮겨보는 쪽에 가깝습니다.


이미지 출처: Y Combinator YouTube 영상 화면 캡처.
