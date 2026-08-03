---
title: "LLM 에이전트 RL 환경 정리: 모델만 보면 절반만 본 겁니다"
date: 2026-08-03
draft: false
tags:
  - reinforcement-learning
  - LLM-agent
  - RL-environments
  - agent-harness
  - verifiers
  - benchmarks
categories:
  - AI
  - Agent
description: "Hanchung Lee의 'A Taxonomy of RL Environments for LLM Agents'를 카톡식 정리 말투로 다시 풀었다. 핵심은 RL 환경을 tasks, harness, verifier, state, configuration 묶음으로 보고, 에이전트 학습의 실제 단위로 다뤄야 한다는 점이다."
aliases:
  - /posts/rl-environments-taxonomy-llm-agents-2026-08-03
---

![LLM 에이전트용 RL 환경을 Tasks, Harness, Verifier, State, Configuration의 다섯 구성요소로 표현한 도식. 이 글의 핵심은 모델 자체보다 모델이 반복 훈련되는 환경이 에이전트의 능력을 결정한다는 주장이다.](/images/rl-environments-taxonomy-llm-agents-2026-08-03/hero.png)

Hanchung Lee의 글 [A Taxonomy of RL Environments for LLM Agents](https://leehanchung.github.io/blogs/2026/03/21/rl-environments-for-llm-agents/) 정리했습니다.

핵심은 이겁니다. LLM 에이전트 성능을 이야기할 때 모델만 보면 반쪽입니다. 모델이 어떤 문제를 풀고, 어떤 도구를 쓰고, 무엇으로 채점받고, 상태를 어떻게 이어받는지가 같이 봐야 할 대상입니다.

요즘은 모델 이름, post-training recipe, reasoning token 이야기는 많이 하는데요. 실제로 에이전트가 반복해서 실패하고 다시 배우는 훈련장, 즉 RL environment 얘기는 상대적으로 덜 합니다. 근데 긴 업무를 하는 agent에서는 이쪽이 꽤 중요합니다.

단일 턴 Q&A만 풀어본 모델한테 50단계짜리 기업 업무를 시키면 흔들립니다. reward 설계가 이상하면 문제를 푸는 게 아니라 점수표를 속이는 법을 배웁니다. 그래서 원문은 RL environment를 agent system의 핵심 구성요소로 봅니다.

## 이 글에서 볼 내용

원문 흐름대로 아래 네 가지를 정리합니다.

1. LLM agent용 RL environment를 어떻게 쪼개서 볼 수 있는지
2. task, harness, verifier, state, configuration이 각각 뭘 통제하는지
3. benchmark와 training environment가 어디까지 같은 구조인지
4. 앞으로 RL environment가 왜 package나 managed API 형태로 갈 가능성이 큰지

## RL 환경은 다섯 개를 묶은 세트입니다

강화학습 기본 구조부터 보면 agent가 environment 안에서 action을 고르고, environment는 state와 reward를 돌려줍니다. 전통적인 표기로는 state 집합 $S$, action space $A$, action $A_t$ 이후 전이된 $S_{t+1}$, 그리고 reward $R_t$가 있죠.

![원문에 포함된 reinforcement learning 기본 루프 도식. Agent가 action을 취하고 environment가 state와 reward를 돌려주는 고전적 RL 구조를 보여준다.](/images/rl-environments-taxonomy-llm-agents-2026-08-03/original-rl-agent.png)

이걸 LLM agent 훈련으로 가져오면 environment는 단순 데이터셋이 아닙니다. task input dataset, model harness, output을 채점하는 reward function, environment state, configuration이 한 묶음으로 움직입니다.

![원문에 포함된 LLM agent용 canonical RL training loop. Task Dataset이 prompt를 Agent Harness로 보내고, harness는 Tools Env와 action/observation을 주고받은 뒤 completion을 Verifier/Rubric에 넘긴다. Verifier는 reward signal을 Trainer로 보내고, Trainer는 다시 policy를 업데이트한다.](/images/rl-environments-taxonomy-llm-agents-2026-08-03/original-rl-environment.png)

원문은 완전한 RL environment를 이렇게 씁니다.

$$
E = \{T, H, V, S, C\}
$$

| 기호 | 의미 | 풀어서 말하면 |
|---|---|---|
| $T$ | Tasks | agent가 풀 문제 묶음 |
| $H$ | Agent harness | 모델이 환경과 상호작용하는 실행 골격 |
| $V$ | Verifier | 결과물을 reward로 바꾸는 채점기 |
| $S$ | State management | 환경의 상태, 기억, 지속성 |
| $C$ | Configuration | 턴 제한, context budget, curriculum 같은 설정 |

여기서 중요한 건 task가 environment에 붙어 있다는 점입니다. coding task는 coding environment와 같이 봐야 하고, research task는 research environment와 같이 봐야 합니다. task만 따로 떼어 놓으면 agent가 실제로 뭘 배웠는지 설명하기 어렵습니다.

## Task는 난이도보다 구조가 중요합니다

Task는 agent가 환경 안에서 풀어야 하는 문제 묶음입니다.

근데 모든 task가 같은 방식으로 어렵진 않습니다. 어떤 건 답 하나 내면 끝나고, 어떤 건 검색을 여러 번 이어야 합니다. 어떤 건 database state를 바꾸고, 어떤 건 repository 전체를 읽고 multi-file patch를 만들어야 합니다.

원문은 task를 이런 구조로 나눕니다.

| Task type | Agent가 하는 일 | 예시 시스템 |
|---|---|---|
| Single-turn Q&A | prompt 하나에 답 하나 | Math benchmarks, SimpleQA |
| Multi-hop search | 검색을 연결하고 source 종합 | BrowseComp, WebWalkerQA |
| Open-ended research | 정답 하나보다 report quality가 중요 | ADR-Bench, ResearchRubrics |
| Agentic tool-use | tool을 올바른 순서로 호출 | tau-bench, function-calling benchmarks |
| Stateful enterprise | persistent DB state 수정, access control 처리 | EnterpriseOps-Gym |
| Code generation | 코드 작성, 실행, output 확인 | SWE-Bench, LiveCodeBench |
| Code review & repair | bug 찾고 patch 검증 | CodeReview-Bench, DebugBench |
| Repository-level coding | 큰 codebase 탐색, multi-file edit | SWE-Bench Verified, RepoBench |
| Productivity workflows | email, calendar, notification 처리 | WorkArena, OSWorld |
| Document authoring | 앱을 넘나들며 문서 생성·편집 | BrowserGym, GAIA |

RL에서 agent가 task를 풀며 만든 state, action, reward sequence를 trajectory라고 합니다. 시작부터 종료까지 한 번의 실행은 episode구요. policy를 돌려 trajectory를 만드는 과정은 rollout입니다.

Agent 쪽에서는 tool call, observation, intermediate output까지 포함한 실행 로그를 trace라고 많이 부릅니다. 대충 정리하면 trajectory는 trainer가 보는 기록이고, trace는 사람이 디버깅할 때 보는 기록에 가깝습니다.

Task distribution을 어떻게 설계하느냐가 꽤 큰 결정입니다. deterministic한 깨끗한 환경에서만 훈련하면 production의 stochastic한 환경에 들어갔을 때 당황합니다. 반대로 항상 positive reward만 받으면 좋은 행동과 나쁜 행동을 구분할 방법이 없습니다.

비용 문제도 있습니다. 가장 싸게 모을 수 있는 건 정답이 딱 있는 single-turn task입니다. 근데 long-horizon behavior를 배우는 데 필요한 task는 만들기 비쌉니다. 이 긴장이 environment 설계의 대부분을 만듭니다.

그래서 curriculum도 중요합니다. 쉬운 task에서 시작해서 점점 복잡한 task로 올리는 방식입니다. 사람이 algebra에서 calculus로 올라가는 것처럼요.

Synthetic task generation도 점점 중요해집니다. 실제 productivity나 research task에는 labeled dataset이 별로 없어서요. 원문은 두 가지 전략을 듭니다.

- Back translation: 원하는 output에서 출발해 그 output을 만들 task input을 거꾸로 구성
- Graph-based synthesis: knowledge graph를 만들고 그 위에서 multi-hop query 생성

## Harness는 모델이 환경과 만나는 방식입니다

Harness는 모델이 environment와 상호작용하게 해주는 실행 골격입니다. 모델이 어떻게 행동할지 통제합니다. 모델의 지식을 직접 늘리는 구성요소는 아닙니다.

원문 정의는 이렇습니다.

```text
H = {
  rollout_protocol, # SingleTurn | MultiTurn | Agentic
  tools,            # rollout 동안 쓸 수 있는 tool
  system_prompt,    # agent instruction
  context_manager,  # context overflow 처리 방식
  turn_limit,       # rollout 최대 상호작용 수
  sandbox,          # code execution sandbox
  state             # turn을 넘나드는 persistent state
}
```

Rollout protocol은 단순한 것부터 복잡한 것까지 이어집니다.

| Harness type | 설명 | 쓰는 곳 |
|---|---|---|
| Single-Turn | prompt 하나, response 하나 | math, factual QA |
| Multi-Turn | back-and-forth dialogue | game, structured task |
| Tool-Use | 모델이 tool을 호출하고 결과를 받음 | agent benchmark |
| Stateful Tool-Use | tool이 persistent state를 수정 | enterprise workflow, SWE-Bench |
| Agentic | Observation→Orient→Decide→Act 전체 루프 | deep research, complex workflow |

Tool도 성격이 다릅니다.

| Category | Tools | Deterministic? | Stateful? |
|---|---|---:|---:|
| Information retrieval | web_search, scholar_search | No | No |
| Content extraction | jina_reader, visit, web_scrape | No | No |
| Code execution | python_interpreter, shell, sandbox | Yes | Yes |
| File operations | file_read, file_write | Yes | Yes |
| Browser automation | playwright, link_click | No | Yes |
| Task management | todo, section_write | Yes | Yes |

Deterministic인지, stateful인지가 reproducibility와 reward assignment에 영향을 줍니다. live web 같은 non-deterministic tool은 같은 trajectory를 다시 실행해도 결과가 달라질 수 있습니다. 그러면 debugging도 어려워지고 verifier도 복잡해집니다.

재밌는 대목은 modern agent harness가 tool 수를 다시 줄이고 있다는 관찰입니다. 초기 agent는 API call, database connection 같은 tool을 계속 붙이는 식이었는데요. 요즘은 read, write, edit, bash, subagent task, MCP resource 연결, skill, askUserQuestions 같은 기본 도구로 수렴하는 경향이 있습니다.

Context management도 핵심입니다. 원문은 harness를 operating system에 비유합니다. OS가 memory와 process management를 대신해주듯, agent harness는 context를 관리해서 user나 skill이 context overflow를 직접 신경 쓰지 않게 합니다.

600-turn research episode는 현실적인 context window를 금방 넘습니다. production에서는 보통 이런 전략을 씁니다.

| Strategy | 설명 | Trade-off |
|---|---|---|
| Recency-based retention | 최근 N turn 유지 | 단순한 대신 초기 context를 잃음 |
| Markovian reconstruction | 매 turn state를 처음부터 재구성 | 원칙적이지만 비쌈 |
| Reference-preserving summarization | 오래된 context를 요약하되 citation 유지 | verifiability 보존 |
| Reference-preserving folding | reference를 잃지 않고 context 압축 | research task에 특히 적합 |

여러 시간 research하는 agent는 열두 번 tool call 전에 왜 그 검색을 시작했는지 기억해야 합니다. 그걸 버리면 같은 검색을 반복하거나 thread를 잃습니다.

## Verifier는 좋음을 reward로 바꿉니다

Verifier는 completion을 reward로 mapping합니다.

$$
V: (\text{task prompt}, \text{completion}, \text{info}) \rightarrow [0, 1]
$$

Atari는 score가 명확합니다. Coding은 test가 통과하면 비교적 쉽습니다. 근데 correct이긴 한데 style이 나쁘거나, 계산 비용이 너무 큰 code는 어떻게 볼까요. Deep research report는 더 어렵습니다. 좋은 답변의 기준이 한 줄로 안 떨어지니까요.

원문은 이걸 generation-verification gap이라고 설명합니다. AI agent로 output을 만드는 비용은 싸졌는데, open-ended task일수록 quality verification은 어려워집니다. Verifier는 크고 stochastic한 input/outcome 공간을 보통 0과 1 사이 reward signal로 줄여야 합니다. 여기서 사고가 많이 납니다.

| Type | Reward signal | 쓰는 곳 |
|---|---|---|
| Exact match | Binary (0/1) | ground truth가 있을 때 |
| Code execution | Binary 또는 partial | programmatic test 가능할 때 |
| LLM-as-judge | Continuous [0,1] | open-ended quality |
| Checklist-style | Continuous | multi-criteria research task |
| Evolving rubric (RLER) | Continuous | reward hacking 방어 |
| Process reward model (PRM) | N-step마다 continuous | long-horizon credit assignment |
| Pairwise comparison | Relative rank | 상대 quality가 중요할 때 |
| Multi-criteria composite | Weighted sum | 여러 quality dimension이 있을 때 |

실무 원칙은 몇 가지입니다.

Verifiable beats judgeable. String match나 code execution 같은 programmatic check가 LLM-as-judge보다 빠르고 싸고 일관적입니다. LLM-as-judge는 다른 방법이 없을 때 쓰는 쪽이 안전합니다.

Reward granularity는 reward type과 별도 결정입니다. Episode 전체에 점수를 줄 수도 있고, turn마다 tool invocation이 유용했는지 볼 수도 있습니다. Nanbeige4.1처럼 최대 600 tool call에 turn-level supervision을 쓰면 credit assignment가 더 정밀해집니다. agent는 전체 실패만 듣는 대신 23번째 search query가 문제였다는 신호를 받을 수 있습니다.

원문은 이걸 project management에 비유합니다. 전구 하나 바꾸는 일은 마지막에 불이 켜졌는지만 보면 됩니다. 주방 전체 리모델링은 중간 inspection과 milestone이 필요하구요.

Static rubric은 게임당합니다. 모델은 문제를 푸는 대신 rubric에서 점수 잘 받는 답변을 쓰는 법을 배웁니다. DR Tulu의 RLER(Rubric-Level Evolving Reward)는 훈련 중 policy와 함께 rubric을 co-evolve합니다. 움직이는 target은 exploit하기 어렵습니다.

Noise injection도 중요합니다. Step-DeepResearch(Hu et al., 2025)는 훈련 중 5–10% tool error를 일부러 넣습니다. 그러면 모델이 production의 flaky API와 예상치 못한 실패를 더 잘 다룹니다.

## State와 Configuration이 현실감을 만듭니다

Agent는 행동할 environment가 필요합니다. Pokémon Ruby agent는 게임과 그 조작 규칙 안에서 움직입니다. Coding agent는 repository와 AGENTS.md 같은 instruction이 있는 VM 안에서 작업하고, code를 실행해 correctness를 확인합니다. Deep research agent는 internet이나 knowledge base에 접근 가능한 VM을 scratch pad처럼 씁니다.

어떤 environment는 stateless입니다. episode가 매번 prior run의 memory 없이 fresh하게 시작됩니다. LeetCode 문제를 푸는 coding agent는 persistent state가 없어도 됩니다.

근데 어떤 environment는 stateful합니다. Database를 조작하는 agent는 action 이후 state를 이어받습니다. Enterprise agent는 episode를 넘어 state가 이어질 수 있습니다. 원문이 예로 드는 EnterpriseOps-Gym(Zhang et al., 2026)은 164개 database table과 512개 tool을 episode 전반에 유지합니다. 한 task의 action이 다음 task에서 보이는 state에 영향을 줍니다. 이러면 agent가 배워야 하는 문제 종류 자체가 바뀝니다.

Automated environment generation도 커지고 있습니다. 사람이 환경을 하나씩 손으로 만드는 대신, LLM coding agent가 새 environment code를 작성하는 방식입니다. AutoEnv(Wang et al., 2025)는 environment 하나당 평균 약 4달러 비용을 보고합니다.

Configuration은 turn limit, context budget, sampling temperature, curriculum scheduling을 포함합니다. 부가 설정처럼 보이지만 아닙니다. turn limit이 5인지 600인지에 따라 agent가 배울 수 있는 skill이 달라집니다. AgentScaler(Pan et al., 2025)는 fundamental capability를 먼저 학습하고 이후 domain-specific task로 가는 two-phase curriculum을 씁니다. Step-DeepResearch는 mid-training 동안 context window를 32K에서 128K로 점진적으로 키웁니다.

Deployment topology도 봐야 합니다. 실제 trainer, model inference server, environment는 보통 별도 process로 돌고 API로 통신합니다. 이렇게 나누면 inference와 environment execution을 따로 scale할 수 있고, environment code를 다시 쓰지 않고 model만 바꿀 수도 있습니다.

## Benchmark는 얼어붙은 RL environment입니다

원문에서 제일 쓸모 있는 비유가 이겁니다. benchmark를 만들어본 적이 있다면 이미 RL environment를 만든 겁니다. 다만 freeze된 버전입니다.

Press(2026)는 benchmark를 4-tuple로 정의합니다.

$$
B = (\text{Request}, \text{Environment}, \text{Stopping Criteria}, \text{Scorer})
$$

이건 RL environment 구성요소와 거의 대응됩니다.

- request는 task prompt입니다. RL environment의 $T$에 대응합니다.
- environment는 model이 작동하는 sandbox입니다. tool, API, file system이 들어가고 $H$와 $S$의 subset입니다.
- stopping criteria는 episode가 언제 끝나는지 정합니다. turn limit, timeout, model의 done 선언 등이 여기에 들어가고 $C$에 대응합니다.
- scorer는 model output을 grade로 mapping합니다. RL environment의 $V$입니다.

차이는 freeze 여부입니다. Benchmark는 reproducibility 때문에 component를 고정합니다. Training environment는 run 중에 parameter가 바뀔 수 있습니다.

좋은 benchmark 설계 원칙은 training environment에도 거의 그대로 갑니다.

Task naturalness. SWE-bench(Jimenez et al., 2024)가 강한 이유는 task가 연구자가 만든 synthetic problem이 아니라 실제 GitHub issue에서 왔기 때문입니다. Press(2026)는 좋은 benchmark가 실제 사람이 자주 수행하고, system이 잘하면 누군가의 시간을 절약해주는 task를 포함해야 한다고 말합니다. Training도 같습니다. 현실에 없는 task로만 훈련하면 eval은 잘 봐도 쓸모를 배우지 못할 수 있습니다.

Automatic, verifiable scoring. Benchmark가 human judge를 요구하면 scale이 안 됩니다. Training environment가 human judge를 요구하면 train이 안 됩니다. training에서는 수백만 개 reward signal이 필요할 수 있어서 더 빡빡합니다.

Difficulty calibration. Press는 benchmark 출시 때 top model accuracy가 0.1%에서 9% 사이가 되도록 권합니다. Training도 비슷합니다. 너무 쉬우면 금방 ceiling에 닿고, 너무 어려우면 reward가 sparse해서 못 배웁니다. 다만 sweet spot은 모델이 좋아질수록 이동합니다. 그래서 training environment에는 curriculum scheduling이라는 자유도가 필요합니다.

Scorer independence. completion을 생성하는 모델 family와 judge 모델 family가 같으면 feedback loop가 생깁니다. agent는 correct한 prose보다 자기 judge에게 좋아 보이는 prose를 쓰는 법을 배울 수 있습니다. LLM-as-judge를 써야 한다면 judge는 policy와 다른 model class가 낫고, 가능하면 training signal이 update할 수 없는 모델이어야 합니다.

정리하면 benchmark는 freeze되고, training environment는 evolve합니다. Task distribution은 curriculum에 따라 바뀌고, verifier rubric은 policy와 같이 바뀔 수 있고, configuration parameter는 training 중 scale up될 수 있습니다. 그래도 underlying component와 설계 원칙은 같습니다.

## 지금 생태계에서 같이 봐야 할 흐름

원문 마지막은 RL environment 생태계가 어디로 가는지 짚습니다.

1) environment diversity는 quality만큼 중요합니다. AgentScaler의 핵심 발견은 environment heterogeneity가 capability breadth를 만든다는 점입니다. 같은 distribution에서 데이터를 더 넣는 것만으로는 부족하고, 더 많은 종류의 environment가 필요합니다.

2) automated environment generation은 이미 viable해지고 있습니다. environment 하나당 4달러라면 cost는 가장 큰 bottleneck에서 내려옵니다. 더 큰 문제는 verifier quality입니다. reward function이 약한 auto-generated environment는 잘못된 행동을 크게 키워서 가르칠 수 있습니다.

3) environment-as-package 모델이 커지고 managed service로 갑니다. Prime Intellect Environments Hub는 PyPI가 code ecosystem을 만들고 Hugging Face가 model weight ecosystem을 만든 것처럼 RL environment 공유 생태계를 만들려는 시도입니다. OpenReward(General Reasoning, 2026)는 330개 이상의 RL environment를 managed API endpoint로 제공하고, 450만 개 이상의 task와 autoscaled sandbox compute를 붙입니다.

그 아래 protocol인 Open Reward Standard(ORS)는 Anthropic의 MCP를 RL primitive 쪽으로 확장합니다. Episode, reward signal, task split, curriculum management가 들어갑니다. 원문 표현을 빌리면 ORS는 RL environment 쪽에서 MCP가 tool integration에 해준 역할과 비슷합니다. Environment와 trainer를 decouple하는 shared interface입니다.

4) contamination resistance가 설계 요구사항이 됩니다. RL environment가 lab과 open-source effort 전반에서 재사용될수록 data contamination 문제가 커집니다. 모델이 pre-training에서 benchmark answer를 외운 상태라면 training signal validity가 흔들립니다. Held-out task split, dynamic task generation, verifier-side answer withholding을 지원하는 environment가 static dataset보다 오래 살아남을 가능성이 큽니다. SciCode(Tian et al., 2024)는 multi-step scientific problem을 compositional subproblem structure로 설계해 memorization에 저항하는 사례로 언급됩니다.

## 제일 중요한 한 줄

이 글의 핵심은 간단합니다. 에이전트의 절반은 환경입니다.

Task distribution은 agent가 어떤 skill을 개발할지 정합니다. Harness는 agent가 어떻게 상호작용할지 통제합니다. Verifier는 무엇을 좋은 행동으로 볼지 정합니다. State와 configuration은 그 훈련이 얼마나 현실적인지 결정합니다.

이걸 잘 만들면 production으로 옮겨갈 행동을 배웁니다. 잘못 만들면 비싼 demo만 반복해서 훈련합니다.

그래서 agent 논의에서는 모델 이름 다음에 바로 이 질문을 붙여야 합니다.

이 모델을 어떤 환경에서 반복적으로 실패시키고, 무엇을 기준으로 다시 일으킬 건가요.

저는 이 질문이 앞으로 agent product를 가르는 기준이 될 거라고 봅니다. 모델 교체는 점점 쉬워지는데, 좋은 task distribution, harness, verifier, state를 가진 환경은 하루아침에 안 만들어지거든요.

## 더 실습해보고 싶은 분들께

에이전트를 직접 굴려보고 싶은 분들은 코난쌤 책 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)나 [모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)을 같이 보셔도 좋습니다.

이 글의 harness, state, verifier 감각을 실제 작업 흐름으로 연결해보는 쪽입니다. 읽고 끝내는 것보다 한 번 굴려보는 게 훨씬 빨리 잡힙니다.

## References

- [Sutton, R. S., & Barto, A. G. (2018). Reinforcement learning: An introduction (2nd ed.). MIT Press.](http://www.incompleteideas.net/book/the-book-2nd.html)
- [Lee, H. (2026). It’s-a Me, Agentic AI. Han, Not Solo.](https://leehanchung.github.io/blogs/2026/02/18/mario-agentic-ai/)
- [Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. (2024). SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)
- [Tian, M., et al. (2024). SciCode: A Research Coding Benchmark Curated by Scientists.](https://arxiv.org/abs/2407.13168)
- [Anthropic. (2024). Model Context Protocol.](https://modelcontextprotocol.io/)
- [Pan, J., et al. (2025). AgentScaler: Scaling LLM Agent Training with Automatically Constructed Environments.](https://arxiv.org/abs/2509.13311)
- [Wang, Y., et al. (2025). AutoEnv: Towards Automated Reinforcement Learning Environment Design.](https://arxiv.org/abs/2511.19304)
- [PrimeIntellect. (2025). Prime RL Environments Hub.](https://github.com/PrimeIntellect-ai/prime-rl)
- [Press, O. (2026). How to Build Good Language Modeling Benchmarks.](https://ofir.io/How-to-Build-Good-Language-Modeling-Benchmarks/)
- [Zhang, K., et al. (2026). EnterpriseOps-Gym: A Benchmark for Enterprise Operations Agents.](https://arxiv.org/abs/2603.13594)
- [General Reasoning. (2026). OpenReward: Managed RL Environments API.](https://docs.openreward.ai/)
- [Open Reward Standard. (2026). ORS Protocol Specification.](https://openrewardstandard.io/)

원문: Hanchung Lee, [A Taxonomy of RL Environments for LLM Agents](https://leehanchung.github.io/blogs/2026/03/21/rl-environments-for-llm-agents/)
