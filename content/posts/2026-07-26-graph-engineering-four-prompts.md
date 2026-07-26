---
title: "그래프 엔지니어링: 네 개의 모델을 네 개의 프롬프트로 줄인다는 말의 진짜 의미"
date: 2026-07-26
tags:
  - knowledge-graph
  - prompt-engineering
  - agent
  - structured-outputs
  - entity-resolution
  - graph
  - Claude
  - automation
  - evaluation
  - harness
draft: false
summary: "Anthropic 공개 cookbook과 agent 패턴을 바탕으로 정리한 독립 문서. NER·관계 분류·엔티티 해소·요약 모델을 네 개의 Claude 프롬프트와 Pydantic schema로 대체하는 접근을, 수치와 한계까지 같이 읽어본다."
authors:
  - jkf87
---

## 핵심 요약

- **주장**: 지식그래프 구축에 필요하던 NER, 관계 분류기, 엔티티 해소기, 요약 모델을 **네 개의 구조화 출력 프롬프트**로 대체할 수 있다는 플레이북이다.
- **핵심 장치**: Claude structured outputs + Pydantic schema. 원문 표현을 빌리면, “유일한 training data는 schema”다.
- **검증 예시**: Apollo 6개 문서 코퍼스에서 36개 raw entity, 34개 relation을 뽑고, resolution 후 24개 surface form을 22개 canonical entity로 압축했다.
- **주의점**: Apollo 11/Neil Armstrong 평가에서 precision은 1.00이지만 recall은 0.55/0.38이다. 즉 “틀린 것을 적게 뽑는” 쪽으로 설계된 데모이지, 모든 중요한 사실을 자동으로 다 잡는 만능 파이프라인은 아니다.

---

## “모델 네 개”가 왜 운영 지옥이었나

전통적인 knowledge graph 파이프라인은 보통 네 덩어리로 나뉜다.

1. 문장에서 사람·조직·장소 같은 entity를 찾는 **NER**
2. 두 entity 사이 관계를 붙이는 **relation classifier**
3. “Buzz Aldrin”과 “Edwin Aldrin”처럼 같은 대상을 합치는 **entity resolution**
4. 여러 문서에 흩어진 정보를 모아 node profile을 만드는 **summarizer**

문제는 각각이 별도 데이터셋, 별도 학습, 별도 평가, 별도 장애 모드를 가진다는 점이다. 뉴스 데이터로 학습한 NER가 계약서에서 흔들리고, 바이오 논문용 관계 분류기가 금융 문서에서 무너지는 식이다. 도메인이 바뀔 때마다 라벨링과 재학습을 다시 해야 한다.

이 PDF의 제안은 꽤 과감하다. **모델을 다시 학습하지 말고, schema와 prompt로 작업 단위를 고정하자.** Claude가 Pydantic schema에 맞는 객체를 반환하게 만들고, 검증 가능한 graph object만 다음 단계로 넘기는 방식이다.

![Figure 1: Apollo corpus knowledge graph — Claude API 호출만으로 만든 22 nodes, 34 edges 그래프](/images/2026-07-26-graph-engineering-four-prompts/fig-1-p1.png)
*Figure 1: 원문 PDF의 Apollo corpus knowledge graph. 22 nodes, 34 edges, 1 connected component라고 보고한다. 장식 이미지가 아니라 원문 figure crop이다.*

---

## Prompt 1: 추출 — NER와 관계 분류를 한 번에 묶는다

첫 번째 프롬프트는 raw document에서 typed entity와 subject-predicate-object triple을 함께 뽑는다. schema는 단순하다. entity type은 PERSON, ORGANIZATION, LOCATION, EVENT, ARTIFACT 정도로 제한하고, relation은 source, predicate, target으로 둔다.

여기서 중요한 건 “Claude에게 잘 부탁한다”가 아니다. **출력 형식을 schema로 잠가버린다**는 점이다. 원문은 `output_format=ExtractedGraph` 하나가 인터페이스 명세 전체라고 설명한다. 반환값은 파싱이 필요한 자유 텍스트가 아니라 검증된 Python object가 된다.

모델 선택도 현실적이다. extraction은 문서 수만큼 반복되는 고빈도 작업이라 Haiku를 쓴다. 원문은 10,000개 문서, 문서당 2,000 tokens 수준의 extraction 비용이 Haiku 요율 기준 “single-digit dollars” 범위라고 주장한다. 물론 실제 비용은 요율·캐싱·입출력 길이에 따라 달라지지만, 설계 의도는 분명하다. **판단이 덜 필요한 대량 작업은 작은 모델로 밀어붙인다.**

Apollo 예시에서는 6개 문서에서 36개 raw entities와 34개 relations를 추출했다. 여기까지 하면 아직 그래프는 지저분하다. “Neil Armstrong”과 “Neil Alden Armstrong”이 따로 노드가 되고, “Edwin Aldrin”과 “Buzz Aldrin”도 갈라진다.

---

## Prompt 2: 해소 — 문자열 유사도 대신 설명을 쓴다

두 번째 프롬프트는 entity resolution이다. 전통적인 방식은 edit distance, token overlap, blocking rule에 많이 기대지만, “Edwin Aldrin”과 “Buzz Aldrin”은 글자가 거의 겹치지 않는다. 문자열만 보면 놓치기 쉽다.

이 문서의 포인트는 extraction 단계에서 entity마다 붙인 **한 줄 description**이다. 예를 들어 “달을 걸은 우주비행사”라는 설명이 붙으면, 이름 문자열이 달라도 같은 사람으로 묶을 근거가 생긴다. 반대로 “Armstrong, jazz trumpeter” 같은 다른 설명이면 합치면 안 된다.

원문 결과는 24개 unique surface form을 22개 canonical entity로 압축했다고 보고한다. “Edwin Aldrin”→“Buzz Aldrin”, “Neil Armstrong”→“Neil Alden Armstrong” 같은 케이스를 잡았다는 것이다.

다만 여기에는 운영 리스크가 있다.

- 어떤 이름도 cluster에 들어가지 않으면 **silent loss**가 생긴다.
- 설명이 비슷하다는 이유로 “Gemini 12”를 “Project Gemini”에 합치면 **over-merge**가 생긴다.

그래서 resolution은 “모델이 알아서 잘하겠지”로 끝내면 안 된다. alias map coverage, human sample, gold set으로 계속 확인해야 한다.

---

## Prompt 3: 요약 — degree 높은 node에만 비싸게 쓴다

세 번째 프롬프트는 hub entity 요약이다. 모든 entity를 매번 깊게 요약하면 비용이 커진다. 그래서 원문은 degree 기준을 제안한다. 연결이 많은 node, 예를 들어 degree 3 이상 또는 top-k node만 골라 Sonnet으로 profile을 만든다.

Apollo program hub node는 6개 문서 전체에 등장하고 degree 9로 보고된다. 이 node에 대해 원문은 1960년부터 1973년까지 이어지는 3문단 profile과 5개 key facts를 만들었다고 설명한다. 단일 문서에는 없던 cross-document profile이다.

여기서 그래프의 쓸모가 나온다. 단순 RAG는 관련 문단을 찾아 붙인다. 지식그래프는 entity를 기준으로 여러 문서의 관계를 누적하고, hub를 중심으로 요약한다. **검색 결과가 아니라, 축적되는 구조화 기억**에 가깝다.

---

## Prompt 4: 질의 — graph-grounded answer만 믿는다

네 번째 프롬프트는 질의다. 중심 entity에서 k-hop subgraph를 뽑고, `(source) --[predicate]--> (target)` 형태의 triple 문자열로 직렬화한 뒤 Claude에게 답하게 한다.

원문은 k=2를 sweet spot으로 본다. k=1은 빠르지만 간접 연결을 놓치고, k=3은 context window를 과하게 먹을 수 있다. Apollo 코퍼스에서는 hub node 기준 k=2가 거의 전체 그래프(22 nodes, 34 edges)를 담는다고 한다.

중요한 차이는 grounded vs ungrounded answer다. 그냥 Claude에게 물으면 사전학습 지식으로 그럴듯하게 답한다. graph context를 넣으면 답변이 edge에 묶인다. 예를 들어 `(Armstrong) --[walked on]--> (Moon)` 같은 triple을 근거로 답하고, 그래프에 없는 내용은 없다고 말할 수 있다.

이건 private corpus에서 특히 중요하다. 외부 지식으로 채울 수 없는 내부 문서라면, 모델의 기억보다 **내 그래프의 provenance**가 더 중요하다.

![Figure 2: Orchestrator-workers에서 graph가 shared memory가 되는 구조](/images/2026-07-26-graph-engineering-four-prompts/fig-2-p4.png)
*Figure 2: worker들이 graph를 직접 읽고 쓰는 구조. orchestrator context를 계속 부풀리지 않는다는 점이 핵심이다.*

---

## 에이전트 아키텍처로 보면: 그래프는 “공유 기억”이 된다

이 문서가 재미있는 이유는 knowledge graph 이야기를 agent architecture와 바로 연결한다는 점이다.

오케스트레이터가 worker 5개에게 일을 나눠준다고 해보자. 각 worker의 결과를 전부 orchestrator context에 다시 넣으면 window가 금방 더러워진다. 반대로 worker들이 각자 관련 subgraph를 읽고, 새 entity와 relation을 graph에 쓰면 orchestrator는 작은 상태만 유지해도 된다.

Evaluator-optimizer loop에서도 graph는 평가 기준이 된다. evaluator가 “이 주장 그럴듯한가?”를 보는 대신, 해당 triple이 graph에 있는지, predicate가 맞는지, 어느 source document에서 왔는지 확인한다.

원문에는 evaluator-optimizer loop를 graph grounding으로 연결하는 별도 diagram도 있다. 다만 블로그 본문에는 작은 crop을 억지로 넣지 않았다. 핵심은 간단하다. evaluator가 generator의 주장을 graph edge와 provenance로 점검하면, 평가가 감상이 아니라 근거 확인으로 바뀐다.

overnight loop에도 잘 맞는다. 밤새 새 문서를 ingest하고, 기존 canonical set과 resolution하고, 새 edge만 추가한다. agent의 context는 지워져도 graph는 남는다. 원문 표현처럼, **agent는 잊지만 graph는 잊지 않는다.**

---

## 수치가 말해주는 것: precision 1.00, recall 0.38–0.55

가장 냉정하게 봐야 할 부분은 evaluation이다.

원문은 Apollo 11과 Neil Armstrong 문서에서 gold set 대비 extraction 품질을 보고한다.

| Document | Raw F1 | Precision | Recall |
|---|---:|---:|---:|
| Apollo 11 | 0.71 | 1.00 | 0.55 |
| Neil Armstrong | 0.55 | 1.00 | 0.38 |

겉으로 보면 precision 1.00이 눈에 띈다. Haiku가 뽑은 건 전부 맞았다는 뜻이다. 그런데 recall은 낮다. gold set이 중요하다고 본 entity 중 상당수를 뽑지 않았다.

이건 실패라기보다 설계 선택에 가깝다. extraction prompt가 “central entity만 뽑아라” 쪽으로 보수적으로 조정되어 있기 때문이다. production에서는 틀린 entity 하나가 잘못된 relation을 낳고, 그 relation이 multi-hop reasoning에 퍼진다. 그래서 false positive가 false negative보다 더 위험할 때가 많다.

하지만 독자가 가져가야 할 결론은 이것이다. **이 방식은 평가 harness 없이는 위험하다.** prompt를 바꾸고, scorer를 다시 돌리고, F1을 확인하는 루프가 있어야 한다. 원문도 “demo를 production system으로 바꾸는 것은 evaluation harness”라고 못 박는다.

---

## 어디까지 확장 가능한가

원문은 production scaling도 꽤 구체적으로 적는다.

- extraction은 prompt caching과 batch API를 활용한다.
- 10,000개 PERSON entity를 한 프롬프트에 넣지 않는다. 먼저 cheap signal로 blocking해서 50–100개 단위로 Claude가 판단하게 한다.
- 새 문서가 오면 전체 graph를 다시 만들지 않고, 새 entity를 뽑고 기존 canonical set에 resolve한 뒤 edge만 추가한다.
- NetworkX는 수십만 edge까지 쓸 수 있고, 그 이상은 `entities`, `relations`, `aliases` 세 개의 Postgres table로 옮기면 된다.

이 대목은 실무적으로 좋다. “LLM으로 그래프 만들 수 있어요”에서 끝나지 않고, 비용·blocking·incremental update·storage 전환까지 적어놨기 때문이다.

---

## 언제 knowledge graph를 써야 하나

모든 문제에 graph를 붙이면 과하다. 원문 decision framework를 코난쌤식으로 번역하면 이렇다.

- 단일 문서 QA면 그냥 direct QA나 RAG면 된다.
- 여러 문서지만 single-hop이면 RAG + reranking으로 충분할 수 있다.
- 여러 문서의 사실을 entity로 이어야 하고, multi-hop reasoning이 필요하면 knowledge graph가 맞다.
- 여러 agent가 같은 세계 상태를 읽고 써야 하면 graph가 shared memory가 된다.
- evaluator가 provenance 있는 ground truth를 확인해야 하면 graph가 평가 기준이 된다.
- overnight loop처럼 기억이 context flush를 넘어 살아야 하면 graph가 persistent world model이 된다.

즉 graph는 멋있어서 쓰는 게 아니다. **문서 사이의 연결, agent 사이의 공유 상태, 평가의 근거성**이 필요할 때 쓴다.

---

## 더 실습해보고 싶은 분들께

이 글의 주제는 결국 agent가 오래 일하기 위해 필요한 구조입니다. prompt 하나를 잘 쓰는 단계를 지나, schema, graph, evaluator, loop가 서로 물리는 시스템을 만들어야 하니까요.

실제로 OpenClaw 같은 자동화 환경에서 agent loop와 작업 harness를 만져보고 싶다면, 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』를 같이 보면 좋습니다. “에이전트가 도구를 어떻게 쓰게 만들 것인가”를 손으로 확인하는 쪽에 가깝습니다.

그리고 이런 구조를 더 큰 관점에서 loop engineering으로 보고 싶다면, 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」가 잘 맞습니다. 오늘 글의 evaluation harness, overnight loop, graph memory도 결국은 act-observe-learn-repeat 루프의 변형입니다.

---

## 정리: schema는 작은 훈련 데이터다

이 PDF의 가장 좋은 문장은 “Pydantic schema is the only training data”다. 물론 엄밀히 말하면 모델은 이미 거대한 사전학습과 instruction tuning을 거쳤다. 그러니 schema만으로 지능이 생긴다는 뜻은 아니다.

하지만 실무적으로는 맞는 말에 가깝다. 도메인이 바뀔 때 모델을 다시 학습하는 대신, **schema로 세계를 자르고, prompt로 판단 기준을 고정하고, evaluation harness로 품질을 본다.** 그러면 knowledge graph 구축의 단위가 모델 학습에서 운영 가능한 프롬프트 루프로 내려온다.

다만 마지막 안전장치는 사람과 평가다. precision 1.00만 보고 취하면 안 된다. recall이 낮을 수 있고, over-merge와 silent loss가 생길 수 있다. provenance 없이 답하게 두면 다시 환각으로 돌아간다.

그래프 엔지니어링은 “LLM에게 다 맡기자”가 아니다. LLM이 잘하는 판단을 schema 안에 가두고, graph와 harness로 오래 굴릴 수 있게 만드는 일이다. 그 균형이 이 문서의 진짜 메시지다.

---

## Source

- Local PDF: `Graph Engineering: 4 Models to 4 Prompts: The Anthropic Playbook`, Boris Cherny, independently compiled July 2026. The PDF states it is based on Anthropic's Knowledge Graph Cookbook, Building Effective AI Agents, and Claude API documentation, and is not affiliated with or endorsed by Anthropic.
