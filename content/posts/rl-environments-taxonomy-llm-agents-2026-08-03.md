---
title: "LLM 에이전트를 위한 RL 환경 분류법: 모델보다 훈련장이 먼저다"
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
description: "Hanchung Lee의 'A Taxonomy of RL Environments for LLM Agents'를 원문 흐름에 충실하게 번역·정리했다. 핵심은 RL 환경을 tasks, harness, verifier, state, configuration의 묶음으로 보고, 에이전트 학습의 실제 단위로 다뤄야 한다는 점이다."
aliases:
  - /posts/rl-environments-taxonomy-llm-agents-2026-08-03
---

![LLM 에이전트용 RL 환경을 Tasks, Harness, Verifier, State, Configuration의 다섯 구성요소로 표현한 도식. 이 글의 핵심은 모델 자체보다 모델이 반복 훈련되는 환경이 에이전트의 능력을 결정한다는 주장이다.](/images/rl-environments-taxonomy-llm-agents-2026-08-03/hero.png)

모델 아키텍처는 늘 스포트라이트를 받습니다. 그다음은 post-training recipe가 차지한다. 그런데 정작 **강화학습 환경**, 그러니까 모델이 실제로 무엇을 연습하고, 그 작업이 어떻게 채점되고, 어떤 도구를 쓸 수 있는지는 대화의 중심에 잘 올라오지 않는다.

Hanchung Lee의 글 [A Taxonomy of RL Environments for LLM Agents](https://leehanchung.github.io/blogs/2026/03/21/rl-environments-for-llm-agents/)는 이 빠진 조각을 정면으로 다룬다. 원문의 주장은 단순하다. **에이전트가 무엇을 배울 수 있는지는 모델만이 아니라, 모델이 굴러가는 훈련장이 결정한다.**

단일 턴 Q&A만으로 훈련된 모델은 50단계짜리 기업 업무 흐름에서 상태를 유지하라는 순간 흔들린다. reward function이 잘못 설계된 모델은 문제를 푸는 대신 metric을 게임한다. 그래서 원문은 이렇게 말한다. RL environment는 시스템의 절반이다.

## 이 글이 답하는 질문

원문을 따라가며 네 가지 질문을 중심으로 번역·정리합니다.

1. LLM 에이전트용 RL 환경은 어떤 구성요소로 볼 수 있는가?
2. task, harness, verifier, state, configuration은 각각 무엇을 통제하는가?
3. benchmark와 training environment는 어디까지 같고, 어디서 달라지는가?
4. 앞으로 RL 환경은 왜 패키지이자 관리형 서비스가 될 가능성이 큰가?

## 정식 루프: 환경은 다섯 가지를 묶은 세트다

강화학습은 동적인 환경 안에서 지능형 agent가 reward signal을 최대화하도록 행동을 선택하는 문제다. 전통적인 표현으로는 agent와 environment의 state 집합 $S$, agent가 선택할 수 있는 action space $A$, 그리고 action $A_t$에 의해 $S_t$에서 $S_{t+1}$로 전이한 뒤 받는 즉시 reward $R_t$가 있다.

![원문에 포함된 reinforcement learning 기본 루프 도식. Agent가 action을 취하고 environment가 state와 reward를 돌려주는 고전적 RL 구조를 보여준다.](/images/rl-environments-taxonomy-llm-agents-2026-08-03/original-rl-agent.png)

이 틀을 LLM agent 훈련으로 가져오면, RL 환경은 단순한 데이터셋이 아니라 다음 객체들을 묶은 단위가 된다. task input dataset, model harness, output을 채점하는 reward function, environment state, 그리고 environment configuration이다.

![원문에 포함된 LLM agent용 canonical RL training loop. Task Dataset이 prompt를 Agent Harness로 보내고, harness는 Tools Env와 action/observation을 주고받은 뒤 completion을 Verifier/Rubric에 넘긴다. Verifier는 reward signal을 Trainer로 보내고, Trainer는 다시 policy를 업데이트한다.](/images/rl-environments-taxonomy-llm-agents-2026-08-03/original-rl-environment.png)

원문은 완전한 RL environment를 다음처럼 정의한다.

$$
E = \{T, H, V, S, C\}
$$

여기서 각 기호는 다음을 뜻한다.

| 기호 | 의미 | 한국어로 풀면 |
|---|---|---|
| $T$ | Tasks | agent가 풀어야 할 문제 묶음 |
| $H$ | Agent harness | 모델이 환경과 상호작용하게 만드는 실행 골격 |
| $V$ | Verifier | 결과를 reward로 바꾸는 채점기 |
| $S$ | State management | 환경의 상태, 기억, 지속성 |
| $C$ | Configuration | 턴 제한, context budget, curriculum 같은 설정 |

중요한 점은 task가 environment에 묶인다는 것이다. coding task는 coding environment와 묶이지, research environment와 묶이지 않는다. task와 environment를 분리된 파일처럼 보면 에이전트 학습을 제대로 설명하기 어렵다.

## $T$: Task는 난이도만이 아니라 구조가 다르다

Task는 agent가 해당 환경 안에서 풀어야 하는 문제들의 집합이다. 모든 task가 같은 방식으로 어렵지는 않다. 어떤 task는 한 번 답하면 끝나고, 어떤 task는 여러 검색을 연결해야 하며, 어떤 task는 persistent database state를 바꾼다.

원문은 task를 다음과 같은 구조적 분포로 본다.

| Task type | Agent가 해야 하는 일 | 예시 시스템 |
|---|---|---|
| Single-turn Q&A | prompt 하나 → response 하나, 답 확인 | Math benchmarks, SimpleQA |
| Multi-hop search | 검색을 연결하고 source를 종합 | BrowseComp, WebWalkerQA |
| Open-ended research | 단일 정답 없음, report quality가 중요 | ADR-Bench, ResearchRubrics |
| Agentic tool-use | tool을 올바른 순서로 호출 | tau-bench, function-calling benchmarks |
| Stateful enterprise | persistent DB state 수정, access control 안에서 작업 | EnterpriseOps-Gym |
| Code generation | 코드 작성, 실행, output 확인 | SWE-Bench, LiveCodeBench |
| Code review & repair | bug 탐지, fix 제안, patch 검증 | CodeReview-Bench, DebugBench |
| Repository-level coding | 큰 codebase 탐색, multi-file edit, issue 해결 | SWE-Bench Verified, RepoBench |
| Productivity workflows | email draft, calendar 관리, notification triage | WorkArena, OSWorld |
| Document authoring | app을 넘나들며 문서 생성·편집·요약 | BrowserGym, GAIA |

RL에서 agent가 task를 풀며 만들어내는 state, action, reward의 sequence를 trajectory라고 부른다. 시작부터 종료까지의 한 번의 실행은 episode다. policy를 실행해 trajectory를 만드는 과정은 rollout이다. agent 세계에서는 tool call, observation, intermediate output을 포함한 실행 로그를 trace라고 부른다.

조금 다르게 말하면, **trajectory는 trainer가 보는 기록이고, trace는 observability system이 보는 기록**이다. 전자는 state-action-reward tuple이고, 후자는 사람이 디버깅하고 관찰할 수 있는 구조화된 실행 로그에 가깝다.

Task distribution을 설계하는 일은 중요한 data design decision이다. agentic model은 환경을 탐색하면서 배워야 한다. 깨끗하고 deterministic한 환경에서만 훈련되면, stochastic한 production environment에 들어갔을 때 어떻게 대응해야 할지 모를 가능성이 크다. 반대로 항상 positive reward만 받는다면, 좋은 행동과 나쁜 행동을 구분할 방법이 없다.

비용 측면의 긴장도 있다. 가장 싸게 수집할 수 있는 task는 verifiable answer가 있는 single-turn task다. 하지만 long-horizon behavior를 학습시키는 데 가장 가치 있는 task는 만들기 비싸다. 이 긴장이 대부분의 environment design decision을 만든다.

그래서 curriculum도 중요해진다. 사람이 9학년 algebra에서 12학년 calculus로 가듯, task를 난이도에 따라 정렬하고 훈련 중 복잡도를 높일 수 있다.

Synthetic task generation 역시 점점 일급 문제가 되고 있다. 실제 productivity나 research task에는 대규모 labeled dataset이 드물기 때문이다. 원문은 두 가지 전략을 예로 든다.

- **Back translation**: 원하는 output에서 시작해, 그 output을 만들 task input을 역으로 구성한다.
- **Graph-based synthesis**: knowledge graph를 만들고, 그 위에서 multi-hop query를 생성한다.

## $H$: Harness는 모델이 환경과 만나는 방식이다

Harness는 모델이 environment와 상호작용하게 해주는 scaffolding이다. 모델이 어떻게 행동할지 통제하지만, 모델이 무엇을 아는지를 직접 늘리지는 않는다.

원문은 harness를 다음처럼 정의한다.

```text
H = {
  rollout_protocol, # SingleTurn | MultiTurn | Agentic
  tools,            # environment에서 rollout 동안 쓸 수 있는 tool
  system_prompt,    # agent instruction
  context_manager,  # context overflow 처리 방식
  turn_limit,       # rollout 최대 상호작용 수
  sandbox,          # code execution sandbox
  state             # turn을 넘나드는 persistent state
}
```

Rollout protocol은 단순한 것부터 복잡한 것까지 이어진다.

| Harness type | 설명 | 언제 쓰는가 |
|---|---|---|
| Single-Turn | prompt 하나, response 하나 | math, factual QA |
| Multi-Turn | back-and-forth dialogue | game, structured task |
| Tool-Use | 모델이 tool을 호출하고 결과를 받음 | agent benchmark |
| Stateful Tool-Use | tool이 persistent state를 수정 | enterprise workflow, SWE-Bench |
| Agentic | Observation→Orient→Decide→Act, 즉 OODA loop 전체 | deep research, complex workflow |

Tool 역시 여러 축으로 나뉜다.

| Category | Tools | Deterministic? | Stateful? |
|---|---|---:|---:|
| Information retrieval | web_search, scholar_search | No (live web) | No |
| Content extraction | jina_reader, visit, web_scrape | No | No |
| Code execution | python_interpreter, shell, sandbox | Yes (같은 code라면) | Yes |
| File operations | file_read, file_write | Yes | Yes |
| Browser automation | playwright, link_click | No | Yes |
| Task management | todo, section_write | Yes | Yes |

Deterministic/non-deterministic, stateful/stateless의 조합은 reproducibility와 reward assignment에 영향을 준다. non-deterministic tool은 같은 trajectory를 두 번 실행해도 결과가 달라질 수 있다는 뜻이다. debugging도 어려워지고 verifier 설계도 복잡해진다.

원문에서 흥미로운 대목은 modern agent harness가 tool 수를 다시 줄이고 있다는 지적이다. 초기 LLM agent는 API call, database connection 같은 개별 tool을 수동으로 계속 붙이는 방식이었다. 반면 최근 설계는 read, write, edit, bash, subagent task, MCP resource 연결, skill, human-agent interface를 위한 askUserQuestions 같은 원자적 기본 도구로 수렴하는 경향이 있다.

Context management는 long-horizon task에서 특히 중요하다. 원문은 harness의 역할을 operating system에 비유한다. OS가 memory와 process management를 추상화해 application이 직접 신경 쓰지 않게 하듯, agent harness는 context를 관리해 skill과 user가 context overflow를 직접 다루지 않아도 되게 한다.

600-turn research episode는 현실적인 context window를 쉽게 넘어간다. production에서 쓰는 전략은 대략 다음과 같다.

| Strategy | 설명 | Trade-off |
|---|---|---|
| Recency-based retention | 최근 N turn 유지 | 단순하지만 초기 context를 잃음 |
| Markovian reconstruction | 매 turn state를 처음부터 재구성 | 원칙적이지만 비쌈 |
| Reference-preserving summarization | 오래된 context를 요약하되 citation 유지 | verifiability 보존 |
| Reference-preserving folding | reference를 잃지 않고 context 압축 | research task에 특히 적합 |

여러 시간 research를 하는 agent는 열두 번의 tool call 전에 왜 특정 방향으로 검색을 시작했는지 기억해야 한다. 그 context를 버리면 반복 작업과 thread loss가 생긴다.

## $V$: Verifier는 “좋음”을 reward로 바꾸는 장치다

Verifier는 completion을 reward로 mapping한다.

$$
V: (\text{task prompt}, \text{completion}, \text{info}) \rightarrow [0, 1]
$$

Atari에서는 score가 명확하다. Coding에서는 test가 통과하면 검증이 비교적 쉽다. 하지만 correct이긴 해도 style이 나쁘거나 computationally expensive한 code는 어떻게 볼 것인가? Deep research에서는 좋은 답변의 기준이 훨씬 모호하다.

원문은 이를 generation-verification gap으로 설명한다. AI agent로 output을 생성하는 비용은 싸지만, task가 open-ended해질수록 quality verification은 더 어려워진다. Verifier의 목표는 크고 stochastic한 input/outcome 공간을 보통 0과 1 사이의 좁은 reward signal로 mapping하는 것이다. 이 mapping을 설계하는 일이 RL environment의 핵심 난제다.

| Type | Reward signal | 언제 쓰는가 |
|---|---|---|
| Exact match | Binary (0/1) | ground truth가 있을 때 |
| Code execution | Binary 또는 partial | output을 programmatically test할 수 있을 때 |
| LLM-as-judge | Continuous [0,1] | open-ended quality, 다른 선택지가 없을 때 |
| Checklist-style | Continuous | multi-criteria research task |
| Evolving rubric (RLER) | Continuous | reward hacking에 강하게 만들 때 |
| Process reward model (PRM) | N-step마다 continuous | long-horizon credit assignment |
| Pairwise comparison | Relative rank | absolute score보다 상대 quality가 중요할 때 |
| Multi-criteria composite | Weighted sum | 여러 quality dimension이 있을 때 |

실무에서 중요한 원칙은 몇 가지다.

**Verifiable beats judgeable.** String match나 code execution 같은 programmatic check는 LLM-as-judge보다 빠르고, 싸고, 일관적이다. LLM-as-judge는 다른 방법이 없을 때 쓰는 것이지 default가 아니다.

**Reward granularity는 reward type과 별개의 결정이다.** Trajectory level에서 점수를 줄 수도 있고, turn level에서 각 tool invocation이 유용했는지 볼 수도 있고, process reward처럼 step별로 줄 수도 있다. Nanbeige4.1처럼 최대 600 tool call에 걸쳐 turn-level supervision을 쓰면 credit assignment가 더 정밀해진다. 모델은 전체 episode가 실패했다는 신호만 받는 대신, 23번째 turn의 search query가 문제였다는 신호를 배울 수 있다.

원문은 이를 project management에 비유한다. 전구 하나를 바꾸는 일이라면 마지막에 불이 켜졌는지만 보면 된다. 하지만 주방 전체를 리모델링한다면 중간 inspection과 milestone이 필요하다.

**Static rubric은 게임당한다.** 모델은 문제를 푸는 대신 rubric에서 점수 잘 받는 답변을 쓰도록 배운다. DR Tulu의 RLER(Rubric-Level Evolving Reward)는 훈련 중 policy와 함께 rubric을 co-evolve한다. 움직이는 target은 exploit하기 어렵다.

**Noise injection은 과소평가되어 있다.** Step-DeepResearch(Hu et al., 2025)는 훈련 중 5–10% tool error를 의도적으로 주입한다. 그 결과 모델은 production의 flaky API와 예상치 못한 실패를 더 잘 다룬다.

## $S$와 $C$: 상태와 설정은 realism을 결정한다

모든 agent는 행동할 environment가 필요하고, environment는 아주 다양하다. Pokémon Ruby agent는 게임 자체와 그 조작·규칙 안에서 움직인다. Coding agent는 보통 code repository와 AGENTS.md 같은 instruction이 있는 virtual machine 안에서 작업하고, VM 안에서 code를 실행해 correctness를 검증한다. Deep research agent는 internet이나 knowledge base에 접근 가능한 VM을 scratch pad로 써서 research report를 만든다.

어떤 environment는 stateless다. episode가 매번 prior run의 memory 없이 fresh하게 시작된다. LeetCode 문제를 푸는 coding agent에는 persistent state가 필요 없다.

하지만 어떤 environment는 stateful하다. Database를 조작해야 하는 coding agent는 action을 넘어 state를 이어간다. Enterprise agent는 episode를 넘어 state를 이어간다. 원문이 예로 드는 EnterpriseOps-Gym(Zhang et al., 2026)은 164개 database table과 512개 tool을 episode 전반에 유지한다. 한 task의 action이 다음 task에서 보이는 state에 영향을 준다. 이것은 agent가 배워야 하는 문제의 종류 자체를 바꾼다.

Automated environment generation도 환경 다양성을 scaling하는 emerging approach다. 사람이 환경을 하나하나 손으로 쓰는 대신, LLM coding agent가 새 environment code를 작성한다. AutoEnv(Wang et al., 2025)는 environment 하나당 평균 약 4달러 비용을 보고한다.

Configuration은 turn limit, context budget, sampling temperature, curriculum scheduling을 포함한다. 이것들은 사소한 부가 설정이 아니다. **turn limit이 5인가 600인가에 따라 agent가 개발할 수 있는 skill이 달라진다.** AgentScaler(Pan et al., 2025)는 fundamental capability를 먼저 학습하고, 이후 domain-specific task로 가는 two-phase curriculum을 쓴다. Step-DeepResearch는 mid-training 동안 context window를 32K에서 128K로 점진적으로 키운다.

Deployment topology도 중요하다. 실제로 trainer, model inference server, environment는 보통 별도 process로 돌고 API로 통신한다. 이 분리는 inference와 environment execution을 독립적으로 scale하고, environment code를 다시 쓰지 않고도 model을 바꿀 수 있게 한다.

## Benchmark는 얼어붙은 RL 환경이다

원문에서 가장 좋은 비유 중 하나는 이것이다. Benchmark를 만들어본 적이 있다면, 이미 RL environment를 만든 것이다. 다만 얼어붙은 environment다.

Press(2026)는 benchmark를 4-tuple로 정의한다.

$$
B = (\text{Request}, \text{Environment}, \text{Stopping Criteria}, \text{Scorer})
$$

이것은 RL environment의 구성요소와 거의 대응된다.

- request는 task prompt이며, RL environment의 $T$(tasks)에 대응한다.
- environment는 model이 작동하는 sandbox다. tool, API, file system을 포함하며, RL environment의 $H$(harness)와 $S$(state)의 subset이다.
- stopping criteria는 episode가 언제 끝나는지를 정의한다. turn limit, timeout, model의 done 선언 등이 여기에 해당하고, $C$(configuration)에 대응한다.
- scorer는 model output을 grade로 mapping하며, RL environment의 $V$(verifier)다.

차이는 benchmark가 reproducibility를 위해 모든 component를 freeze한다는 점이다.

Benchmark와 training environment는 같은 component를 공유하므로, 좋은 benchmark를 만드는 설계 원칙은 training environment에도 직접 적용된다. 다만 한 가지 핵심 차이가 있다. Training environment는 run 중 parameter를 evolve할 수 있다.

**Task naturalness.** SWE-bench(Jimenez et al., 2024)가 작동하는 이유는 task가 연구자가 발명한 synthetic problem이 아니라, 실제 developer가 올린 real GitHub issue이기 때문이다. Press(2026)는 유용한 benchmark가 실제 사람이 자주 수행하고, system이 잘하면 누군가의 시간을 절약해줄 task를 포함해야 한다고 말한다. Training도 마찬가지다. 실제 사람이 마주치지 않을 task로 훈련된 agent는 eval은 잘 볼 수 있어도 유용성을 배우지 못할 수 있다.

**Automatic, verifiable scoring.** Benchmark가 human judge를 요구하면 scale할 수 없다. Training environment가 human judge를 요구하면 train할 수 없다. 원리는 같지만 training에서는 stakes가 더 높다. 몇백 개가 아니라 수백만 개 reward signal이 필요할 수 있기 때문이다.

**Difficulty calibration.** Press는 benchmark를 출시할 때 top model accuracy가 0.1%에서 9% 사이가 되도록 권한다. Training analog도 같다. Task distribution이 너무 쉬우면 agent는 곧 ceiling에 닿고 더 개선되지 않는다. 너무 어려우면 reward signal이 너무 sparse해 배울 수 없다. 다만 sweet spot은 모델이 좋아질수록 이동한다. 그래서 training environment는 benchmark와 달리 curriculum scheduling이라는 추가 자유도를 가진다.

**Scorer independence.** Completion을 생성하는 모델 family와 judge 모델 family가 같으면 feedback loop가 생긴다. Agent는 correct한 prose가 아니라 자기 judge에게 좋아 보이는 prose를 쓰는 법을 배운다. Benchmark에서는 score inflation이 생기고, training에서는 더 나쁘게도 wrong behavior를 적극적으로 가르친다. LLM-as-judge를 써야 한다면, judge는 policy와 다른 model class여야 하고, 가능하면 training signal이 update할 수 없는 모델이어야 한다.

Benchmark와 training environment의 차이는 이 문장으로 정리된다. **Benchmark는 freeze되고, training environment는 evolve한다.** Task distribution은 curriculum에 따라 바뀐다. Verifier rubric은 policy와 함께 co-evolve할 수 있다. Configuration parameter는 training 중 scale up될 수 있다. 하지만 underlying component와 좋은 설계 원칙은 같다.

## 추가로 봐야 할 흐름들

원문 마지막 부분은 RL environment 생태계가 어디로 가고 있는지 짚는다.

첫째, **environment diversity는 environment quality만큼 중요하다.** AgentScaler의 핵심 발견은 environment heterogeneity가 capability breadth를 만든다는 점이다. 같은 distribution에서 데이터를 더 넣는 것만으로는 안 된다. 더 많은 environment가 아니라, 더 많은 종류의 environment가 필요하다.

둘째, **automated environment generation은 이미 viable해지고 있다.** environment 하나당 4달러라면 cost는 더 이상 가장 큰 bottleneck이 아니다. bottleneck은 verifier quality다. reward function이 약한 auto-generated environment는 잘못된 행동을 scale해서 가르친다.

셋째, **environment-as-package 모델이 이기고 있으며, managed service가 되고 있다.** Prime Intellect Environments Hub는 PyPI가 code ecosystem을 만들고 Hugging Face가 model weight ecosystem을 만든 것처럼, RL environment 공유 생태계를 만들고 있다. OpenReward(General Reasoning, 2026)는 이를 더 밀어붙여 330개 이상의 RL environment를 managed API endpoint로 제공하고, 450만 개 이상의 task와 autoscaled sandbox compute를 붙인다.

그 아래 protocol인 Open Reward Standard(ORS)는 Anthropic의 MCP를 RL primitive로 확장한다. Episode, reward signal, task split, curriculum management가 들어간다. 원문 표현을 빌리면, **ORS는 RL environment에 대해 MCP가 tool integration에 대해 하는 일과 비슷하다.** Environment와 trainer를 decouple하는 shared interface다. 한 번 publish한 environment를 어떤 trainer든 hosted 또는 self-served 방식으로 consume할 수 있다.

넷째, **contamination resistance는 설계 요구사항이 될 것이다.** RL environment가 lab과 open-source effort 전반에서 재사용될수록 data contamination, 즉 model이 pre-training에서 benchmark answer를 외우는 문제가 training signal validity를 위협한다. Held-out task split, dynamic task generation, verifier-side answer withholding을 지원하는 environment가 static dataset보다 오래 살아남을 가능성이 크다. SciCode(Tian et al., 2024)는 multi-step scientific problem을 compositional subproblem structure로 설계해 memorization에 저항하는 사례로 언급된다.

## 그래서, 에이전트의 절반은 환경이다

원문의 결론은 명확하다. RL environment는 agent가 무엇을 할 수 있는지를 형성하는 training ground다. Task distribution은 agent가 어떤 skill을 개발할지 정한다. Harness는 agent가 어떻게 상호작용할지 통제한다. Verifier는 무엇이 “좋음”인지를 정의한다. State와 configuration은 훈련이 얼마나 현실적인지를 결정한다.

이것들을 제대로 만들면 agent는 production으로 transfer되는 behavior를 배운다. 잘못 만들면 비싼 demo를 훈련한 셈이 된다.

저는 이 글이 요즘 agent 논의의 무게중심을 잘 옮긴다고 봅니다. “어떤 모델을 쓸까?”도 중요하지만, 에이전트에서는 곧바로 다음 질문이 붙어야 한다. **그 모델을 어떤 환경에서 반복적으로 실패시키고, 무엇을 기준으로 다시 일으킬 것인가?**

## 더 실습해보고 싶은 분들께

에이전트를 더 실전적으로 실험해보고 싶은 분들을 위한 참고 자료도 남겨둡니다. 코난쌤의 책 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)는 OpenClaw를 손으로 굴려보는 예제 중심이고, [모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)은 agent loop와 자동화 실습 쪽에 더 가깝습니다. 이 글에서 말한 harness, state, verifier 감각을 실제 작업 흐름으로 연결해보고 싶다면 같이 보면 좋겠습니다.

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
