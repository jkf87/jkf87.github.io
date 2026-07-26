---
title: "Graph Engineering: 네 개의 모델을 네 개의 프롬프트로 바꾸는 Anthropic 플레이북"
date: 2026-07-26
tags:
  - knowledge-graph
  - prompt-engineering
  - structured-outputs
  - entity-resolution
  - graph
  - Claude
  - agent
  - evaluation
summary: "Boris Cherny가 Anthropic 공개 cookbook과 engineering 글을 바탕으로 독립 편집한 Graph Engineering 노트. NER, 관계 분류, 엔티티 해소, 요약 모델을 Claude structured outputs와 Pydantic schema 기반 네 개의 프롬프트로 바꾸는 방법을 원문 흐름에 맞춰 정리한다."
authors:
  - jkf87
---

## 핵심 요약

- 이 문서는 **Boris Cherny**가 2026년 7월 독립적으로 편집한 `Graph Engineering: 4 Models to 4 Prompts: The Anthropic Playbook`이다. Anthropic 공식 문서는 아니고, Anthropic의 공개 cookbook, agent engineering 글, Claude API 문서를 바탕으로 엮은 학습용 노트다.
- 원문의 중심 주장은 지식그래프 구축에 필요하던 네 가지 시스템, 즉 **NER, relation classifier, entity resolution, summarization model**을 **네 개의 Claude prompt + structured outputs + Pydantic schema**로 대체할 수 있다는 것이다.
- 이때 “Graph Engineering”은 새 graph DB나 새 그래프 이론을 뜻하지 않는다. **문서에서 entity와 relation을 뽑고, canonical node로 합치고, hub node를 요약하고, subgraph 위에서 질의하는 운영 파이프라인**을 말한다.
- 원문은 Apollo 6개 문서 코퍼스에서 36개 raw entity, 34개 relation을 추출했고, resolution 후 24개 surface form을 22개 canonical entity로 압축했다고 보고한다.
- 성능은 보수적이다. Apollo 11 / Neil Armstrong 평가에서 precision은 1.00이지만 recall은 0.55 / 0.38이다. 원문도 그래서 evaluation harness, provenance tracking, human sample을 production checklist의 핵심으로 둔다.

---

## Boris Cherny의 독립 노트라는 점부터 분명히 해야 한다

첫 페이지에는 제목과 성격이 꽤 명확하게 적혀 있다. `Full Course From Scratch`, 작성자 **Boris Cherny**, 제목은 `Graph Engineering: 4 Models to 4 Prompts: The Anthropic Playbook`이다. 바로 아래에는 “Based on Anthropic's Knowledge Graph Cookbook, Building Effective AI Agents, and Claude API documentation”이라고 되어 있고, “Independently compiled, July 2026 — not affiliated with Anthropic and not endorsed”라고 못 박는다.

그러니까 이 글은 “Anthropic이 새 논문을 냈다”가 아니다. 더 정확히는 **Anthropic 공개 자료를 바탕으로 Boris Cherny가 knowledge graph construction pipeline을 하나의 course/note 형태로 재구성한 문서**다.

원문이 흥미로운 이유는 이름에 있다. 보통 knowledge graph라고 하면 Neo4j, RDF, ontology, graph DB부터 떠올린다. 그런데 이 노트는 저장소나 그래프 이론보다 앞단의 construction pipeline을 본다. 문서에서 무엇을 node로 볼지, 어떤 relation을 edge로 뽑을지, 같은 entity를 어떻게 합칠지, 그 graph를 agent가 어떻게 읽고 쓸지의 문제다.

![Figure 1: Apollo corpus knowledge graph — Claude API 호출만으로 만든 22 nodes, 34 edges 그래프](/images/2026-07-26-graph-engineering-four-prompts/fig-1-p1.png)
*Figure 1: 원문 PDF의 Apollo corpus knowledge graph. 22 nodes, 34 edges, 1 connected component라고 보고한다. Node 크기는 degree, 색은 entity type을 나타낸다.*

---

## 문제 정의: 네 개의 모델, 네 개의 실패 모드

원문은 classical knowledge graph pipeline을 네 개의 독립 시스템으로 나눈다.

1. **Named-entity recognizer**: 문장에서 PERSON, ORGANIZATION, LOCATION 같은 entity span을 찾는다.
2. **Relation classifier**: 두 entity 사이의 관계를 `works_at`, `located_in`, `founded_by` 같은 predicate로 분류한다.
3. **Entity-resolution engine**: “NASA”와 “National Aeronautics and Space Administration”, “Dr. Smith”와 “Jane Smith, PhD”처럼 같은 실체를 가리키는 mention을 합친다.
4. **Summarization model**: 여러 문서에 흩어진 mention을 모아 entity profile을 만든다.

문제는 각 시스템이 따로 논다는 점이다. 각자 labeled dataset이 필요하고, training pipeline이 필요하고, evaluation harness가 필요하다. 뉴스 기사로 학습한 NER는 법률 계약서에서 흔들릴 수 있고, 바이오 문헌용 relation classifier는 금융 공시에서 실패할 수 있다. 이름 문자열에 맞춘 entity-resolution rule은 다른 문자권 이름이나 별칭에서 무너진다.

Boris Cherny 노트의 제안은 이 네 덩어리를 **네 개의 prompt**로 바꾸자는 것이다. 핵심은 structured outputs다. Claude에게 자유 텍스트를 쓰게 두는 게 아니라, Pydantic schema에 맞는 object를 반환하게 한다. 원문 표현을 빌리면 “Pydantic schema is the only training data”다.

물론 엄밀히 말하면 schema가 모델을 훈련시키는 것은 아니다. Claude는 이미 거대한 사전학습과 instruction tuning을 거쳤다. 다만 운영 관점에서는 schema가 “이 파이프라인이 세계를 자르는 방식”을 정의한다. 어떤 entity type을 허용할지, relation을 어떤 shape으로 받을지, query answer가 어떤 citation을 가져야 하는지를 schema가 고정한다.

---

## Prompt 1: Extraction — NER와 relation classifier를 한 번에 대체한다

첫 번째 prompt는 raw document에서 typed entity와 subject-predicate-object triple을 함께 뽑는다. 원문 schema는 대략 이런 모양이다.

```python
EntityType = Literal["PERSON", "ORGANIZATION", "LOCATION", "EVENT", "ARTIFACT"]

class Entity(BaseModel):
    name: str
    type: EntityType
    description: str  # one-line, for disambiguation

class Relation(BaseModel):
    source: str
    predicate: str  # short verb phrase
    target: str

class ExtractedGraph(BaseModel):
    entities: list[Entity]
    relations: list[Relation]
```

여기서 prompt는 네 가지를 요구한다. 문서에서 중심적인 entity만 뽑을 것, 각 entity에 문서 기반 한 문장 설명을 붙일 것, predicate는 짧은 verb phrase로 쓸 것, 모든 relation은 추출된 두 entity를 연결할 것.

이 지시들은 각각 실패 모드를 겨냥한다. 중심 entity만 뽑으라는 지시는 recall을 일부 희생해 noise를 줄인다. 한 문장 설명은 뒤의 entity resolution에 쓰인다. 짧은 predicate는 relation vocabulary가 지나치게 흩어지는 것을 막는다. relation 양끝이 추출 entity인지 확인하는 조건은 orphan edge를 막는다.

구현상 중요한 줄은 `output_format=ExtractedGraph`다. 원문은 이 한 줄이 interface specification 전체라고 설명한다. 반환값은 “파싱해야 하는 텍스트”가 아니라 “검증된 Python object”가 된다.

모델 선택도 원문은 분리한다. extraction은 문서 수만큼 반복되는 high-volume 작업이므로 Haiku를 쓴다. schema가 많은 제약을 걸어주기 때문에, 이 단계에서는 비싼 추론보다 빠르고 저렴한 반복 처리가 중요하다는 판단이다. 원문은 10,000개 문서, 문서당 평균 2,000 tokens라면 Haiku extraction 비용이 single-digit dollars 수준이라고 적는다. 실제 비용은 요율, 캐싱, 입출력 길이에 따라 달라지지만, 설계 의도는 분명하다.

Apollo 예시에서 Haiku는 6개 문서에서 36개 raw entities와 34개 relations를 추출했다. 문서는 Apollo program, Apollo 11, Neil Armstrong, Saturn V, Buzz Aldrin, Kennedy Space Center다.

---

## Prompt 2: Entity Resolution — 문자열 유사도 대신 설명을 쓴다

raw extraction 결과를 그대로 graph로 만들면 같은 실체가 여러 node로 갈라진다. “Neil Armstrong”과 “Neil Alden Armstrong”, “Buzz Aldrin”과 “Edwin Aldrin”이 따로 남는 식이다.

전통적인 방법은 edit distance, token overlap, blocking rule에 기대는 경우가 많다. 오타나 약어에는 잘 먹히지만, “Edwin Aldrin”과 “Buzz Aldrin”처럼 글자가 거의 겹치지 않는 별칭에는 약하다.

원문은 두 번째 prompt에서 Sonnet에게 entity type별 clustering을 맡긴다. 이때 중요한 입력은 extraction 단계에서 붙인 한 줄 description이다. “Armstrong, first person to walk on the Moon”과 “Armstrong, jazz trumpeter”는 이름 문자열은 같아도 다른 사람이다. 반대로 “Edwin Aldrin”과 “Buzz Aldrin”은 문자열은 다르지만 설명이 같은 실체를 가리킬 수 있다.

schema는 canonical name과 aliases를 담는 cluster list다.

```python
class Cluster(BaseModel):
    canonical: str  # most complete form
    aliases: list[str]  # all surface forms

class ResolvedClusters(BaseModel):
    clusters: list[Cluster]
```

Apollo corpus에서 resolution은 24개 unique surface form을 22개 canonical entity로 압축했다. 원문은 “Edwin Aldrin”→“Buzz Aldrin”, “Neil Armstrong”→“Neil Alden Armstrong” 같은 케이스를 string similarity가 놓치는 사례로 든다.

다만 원문도 실패 모드를 숨기지 않는다. 어떤 이름도 cluster에 들어가지 않으면 **silent loss**가 생긴다. “Gemini 12”를 더 넓은 “Project Gemini”와 합치면 **over-merge**가 생긴다. 그래서 resolution은 prompt 한 번으로 끝나는 게 아니라 alias map coverage와 human sample로 계속 확인해야 한다.

---

## Prompt 3: Entity Summarization — hub node만 깊게 요약한다

초기 node에는 각 문서에서 온 한 줄 description만 있다. 하지만 여러 문서에 반복 등장하는 hub node는 그 정도로 부족하다. 원문은 이런 node에 대해 mentions와 graph neighborhood를 모아 Sonnet으로 profile을 합성한다.

schema는 summary, key facts, time range를 담는다.

```python
class TimeRange(BaseModel):
    start: str  # YYYY or "unknown"
    end: str    # YYYY or "ongoing"

class EntityProfile(BaseModel):
    summary: str      # 2-3 paragraphs
    key_facts: list[str]  # 3-5 atomic facts
    time_range: TimeRange
```

이 단계의 가치는 cross-document profile에 있다. Apollo program hub node는 6개 문서 전체에 등장하고 degree 9로 보고된다. 원문은 이 node에 대해 1960년부터 1973년까지 이어지는 3문단 profile과 5개 traceable key facts를 만들었다고 설명한다. 단일 문서에는 없던 정보를 graph neighborhood와 mention pool을 통해 합성한 것이다.

하지만 모든 node를 이렇게 요약하면 비용이 커진다. 그래서 원문은 degree 기준을 제안한다. 연결이 많은 top-k node, 또는 degree 3 이상 node만 요약한다. 낮은 degree의 node는 single-document description으로 충분한 경우가 많다.

---

## Prompt 4: Graph-grounded Querying — serialized subgraph 위에서 답한다

네 번째 prompt는 질의다. 중심 entity에서 k-hop subgraph를 뽑고, 그 graph를 `(source) --[predicate]--> (target)` 형태의 triple text로 직렬화한 뒤 Claude가 그 위에서 답하게 한다.

원문 예시는 대략 이런 방식이다.

```python
def serialize_subgraph(center, hops=2):
    nodes = {center}; frontier = {center}
    for _ in range(hops):
        nxt = set()
        for n in frontier:
            nxt |= set(G.successors(n))
            nxt |= set(G.predecessors(n))
        frontier = nxt - nodes; nodes |= frontier
    sub = G.subgraph(nodes)
    return "\n".join(sorted(set(
        f"({s}) --[{d['predicate']}]--> ({t})"
        for s, t, d in sub.edges(data=True)
    )))
```

k 값은 중요하다. k=1은 빠르고 집중되어 있지만 간접 연결을 놓친다. k=2는 대부분의 multi-hop question에 적당한 sweet spot으로 제시된다. k=3은 context window를 크게 먹기 시작하므로 filtering이 필요하다. Apollo corpus에서는 hub node 기준 k=2가 거의 전체 graph, 즉 22 nodes와 34 edges를 담는다고 한다.

원문이 강조하는 차이는 grounded answer와 ungrounded answer다. graph context 없이 Claude에게 물으면 사전학습 지식으로 포괄적이지만 검증하기 어려운 답을 할 수 있다. graph context를 넣으면 답은 추출된 edge에 묶인다. `(Armstrong) --[walked on]--> (Moon)` 같은 triple을 근거로 답하고, graph에 없는 내용은 없다고 말해야 한다.

private corpus에서는 이 차이가 더 커진다. 모델의 사전지식으로 채울 수 없는 내부 문서라면, 필요한 것은 그럴듯한 답이 아니라 **내 corpus에서 온 edge-level citation**이다.

---

## Schema가 대체하는 것

원문은 classical system과 Claude prompt replacement를 표로 대응시킨다.

| Classical system | Claude prompt | What changes |
|---|---|---|
| Trained NER | Extraction prompt | Schema replaces labels |
| Relation classifier | Extraction prompt | Same call, same schema |
| Edit-distance resolver | Resolution prompt | Descriptions replace rules |
| Fine-tuned summarizer | Summarization prompt | Graph context replaces training |

여기서 “대체”라는 표현은 조심해서 읽어야 한다. 모든 환경에서 기존 trained system을 버리라는 뜻은 아니다. 이 노트의 메시지는 domain shift가 잦고, 빠르게 corpus를 바꾸며, LLM이 읽을 수 있는 문서라면 schema와 prompt로 construction pipeline을 훨씬 빨리 구성할 수 있다는 쪽에 가깝다.

---

## Agent architecture와 만나는 지점

원문은 이 knowledge graph pipeline을 Anthropic의 agent pattern과 연결한다. 여기서도 핵심은 “에이전트의 trajectory graph 이론”이라기보다, **agent가 공유하고 검증할 수 있는 structured state로 knowledge graph를 쓴다**는 점이다.

![Figure 2: Orchestrator-workers에서 graph가 shared memory가 되는 구조](/images/2026-07-26-graph-engineering-four-prompts/fig-2-p4.png)
*Figure 2: 원문 PDF의 orchestrator-workers diagram. worker들이 graph를 직접 읽고 쓰고, orchestrator context를 작게 유지하는 구조다.*

### Orchestrator-workers: shared memory

오케스트레이터가 여러 worker에게 일을 나눠줄 때, 각 worker의 결과를 전부 orchestrator context로 다시 모으면 context window가 빨리 더러워진다. 원문은 graph를 구조적 해결책으로 본다. worker는 관련 subgraph를 읽고 새 entity와 relation을 graph에 쓴다. shared state는 orchestrator의 긴 prompt가 아니라 graph에 남는다.

### Evaluator-optimizer: grounding layer

Evaluator가 “이 답이 맞아 보이는가?”만 판단하면 결국 모델의 추정에 기대게 된다. Knowledge graph가 있으면 evaluator는 generator의 주장이 graph edge에 있는지, predicate가 맞는지, 어느 source document에서 왔는지 확인할 수 있다. feedback이 impression에서 fact-checking으로 이동한다.

### Persistent world model

Self-improving loop에는 context flush를 넘어 살아남는 memory가 필요하다. 원문은 graph를 그 memory로 둔다. 밤새 새 문서가 들어오면 entity를 추출하고, 기존 canonical set에 resolve하고, 새 edge를 추가한다. loop의 state file은 어떤 문서를 처리했는지 기록하고, graph 자체는 run을 넘어 누적된다. 원문 문장 그대로, agent는 잊지만 graph는 잊지 않는다.

원문 표는 agent pattern과 graph role도 함께 정리한다.

| Pattern | Graph role | How it helps |
|---|---|---|
| Augmented LLM | Retrieval source | Graph traversal for multi-hop |
| Prompt chaining | Gate signal | Conflict check between steps |
| Routing | Classifier input | Type + degree route queries |
| Orchestrator-workers | Shared memory | Workers read/write the graph |
| Evaluator-optimizer | Grounding layer | Evaluator fact-checks edges |

---

## Evaluation: precision 1.00만 보면 안 된다

원문에서 가장 중요한 production 감각은 evaluation section이다. Knowledge graph quality는 gold set 대비 precision과 recall로 본다. 그리고 원문은 “prompt를 바꾸고, scorer를 다시 돌리고, F1 변화를 본다”는 evaluation harness가 demo를 production system으로 바꾼다고 쓴다.

| Document | Raw F1 | Precision | Recall |
|---|---:|---:|---:|
| Apollo 11 | 0.71 | 1.00 | 0.55 |
| Neil Armstrong | 0.55 | 1.00 | 0.38 |

precision 1.00은 Haiku가 뽑은 entity가 모두 맞았다는 뜻이다. 하지만 recall은 낮다. gold set이 중요하다고 본 entity 중 상당수가 추출되지 않았다. 원문은 이를 extraction prompt가 “central entity” 중심으로 보수적으로 조정된 결과로 설명한다.

production에서는 이 선택이 합리적일 수 있다. wrong entity는 wrong relation을 만들고, wrong relation은 multi-hop reasoning에서 계속 퍼진다. false positive가 false negative보다 더 비싸게 먹힐 때가 있다. 하지만 그 판단도 harness가 있어야 가능하다. recall이 낮아도 되는 task인지, 놓치면 안 되는 entity가 있는 task인지는 corpus와 제품 요구사항에 따라 다르다.

---

## Model selection과 cost

원문은 두 모델 전략을 쓴다.

| Stage | Model | Rationale |
|---|---|---|
| Extraction | Haiku | High volume, schema-constrained; speed and cost |
| Resolution | Sonnet | Weighing conflicting evidence; judgment needed |
| Summarization | Sonnet | Synthesizing across documents; nuance matters |
| Querying | Sonnet | Multi-hop reasoning over serialized triples |

즉 모든 단계를 가장 비싼 모델로 밀어붙이지 않는다. schema가 빡빡하고 반복량이 많은 extraction은 Haiku로 처리한다. 반면 conflict를 따져야 하는 resolution, 여러 문서를 합성하는 summarization, serialized subgraph 위에서 추론하는 querying은 Sonnet이 맡는다.

Scaling section도 꽤 실무적이다. prompt caching은 schema가 고정되어 있을 때 extraction cost를 줄인다. Message Batches API는 최대 24시간 latency를 받아들일 수 있는 작업에 50% 할인을 줄 수 있다고 적는다.

Resolution at scale에서는 10,000개 PERSON entity를 한 prompt에 넣지 말라고 한다. 먼저 same last name, overlapping tokens 같은 cheap signal로 blocking해서 50–100개 단위로 Claude가 판단하게 한다. 이 blocking은 모델 호출 없이 inverted index로 처리한다.

Storage도 처음부터 거창할 필요는 없다. NetworkX는 수십만 edge까지 쓸 수 있고, 그 이상은 `entities(id, name, type, summary)`, `relations(source_id, target_id, predicate)`, `aliases(entity_id, alias)` 세 개의 Postgres table로 옮기면 된다. extraction과 resolution code는 그대로 두고 persistence layer만 바꾸는 식이다.

---

## 언제 knowledge graph를 써야 하나

원문 decision framework는 이 글의 과장을 줄여준다. 모든 문제에 graph가 필요한 것은 아니다.

| Scenario | Right tool | Why |
|---|---|---|
| Single-doc QA | RAG or direct | No chaining needed |
| Multi-doc, single-hop | RAG + reranking | Answer spans docs, no chaining |
| Multi-doc, multi-hop | Knowledge graph | Chaining requires entity linking |
| Multi-agent shared state | Knowledge graph | Workers need shared world model |
| Evaluator needs ground truth | Knowledge graph | Fact-checking needs provenance |
| Overnight persistent loop | Knowledge graph | Memory must survive flushes |

이 표를 보면 원문이 말하는 graph engineering의 자리가 선명해진다. 단일 문서 질의에는 과하다. 여러 문서에 답이 걸쳐 있어도 single-hop이면 RAG와 reranking으로 충분할 수 있다. 하지만 문서 사이의 entity를 연결해야 하고, agent들이 같은 world state를 읽고 써야 하며, evaluator가 provenance 있는 ground truth를 확인해야 한다면 knowledge graph가 맞다.

---

## Production readiness checklist

원문 마지막 체크리스트는 꽤 좋다. “LLM으로 graph 만들었다”에서 끝나면 demo다. production으로 가려면 다음 실패 모드를 막아야 한다.

| Element | Failure if missing |
|---|---|
| Gold set | No feedback loop; prompt changes are blind |
| Alias map coverage | Scoring artifacts: recall looks worse than it is |
| Schema version | Incompatible entities from different prompt versions |
| Extraction cap | Unbounded cost from corpus ingestion errors |
| Resolution fallback | Silent entity loss: nodes disappear |
| Provenance tracking | Ungrounded answers; evaluator cannot fact-check |
| Connectivity monitor | Fragmented graph: missed cross-doc links |
| Human sample | Comprehension rot: graph outgrows understanding |

특히 provenance tracking과 human sample은 중요하다. graph가 커질수록 사람이 전체를 이해하기 어려워지고, 그 순간부터 graph는 “검증 가능한 구조”가 아니라 “또 다른 블랙박스”가 될 수 있다. 원문은 그래서 마지막에 pipeline은 실행될 때 끝나는 게 아니라, 어느 아침에든 밤새 만들어진 결과가 실제로 맞았는지 말할 수 있을 때 끝난다고 쓴다.

---

## 정리: schema, graph, harness가 한 묶음이다

Boris Cherny의 이 노트는 새 graph DB를 제안하지 않는다. 또 “그래프”라는 이름으로 agent trajectory 이론을 새로 세우는 문서도 아니다. 원문에 충실하게 읽으면, 이 글은 **knowledge graph construction pipeline을 Claude structured outputs 중심으로 재배치하는 플레이북**이다.

네 개의 trained system이 하던 일을 네 개의 prompt로 나눈다. Extraction prompt는 NER와 relation classifier를 한 번에 맡는다. Resolution prompt는 description을 근거로 surface form을 canonical node로 합친다. Summarization prompt는 hub node의 cross-document profile을 만든다. Query prompt는 serialized subgraph 위에서 edge-level citation으로 답한다.

그리고 이 graph는 agent architecture 안에서 retrieval source, shared memory, evaluator grounding layer, persistent world model로 쓰일 수 있다. 여기서 중요한 것은 멋진 은유가 아니라 운영 조건이다. schema version을 관리하고, gold set으로 prompt 변경을 평가하고, provenance를 남기고, 사람이 샘플을 본다.

원문 문장을 조금 풀면 이렇게 정리할 수 있다. **schema는 세계를 자르는 작은 명세이고, graph는 그 명세로 누적된 기억이며, harness는 그 기억이 맞는지 매일 확인하는 장치다.** 이 셋이 같이 있을 때, “LLM으로 지식그래프를 만든다”는 말이 데모를 넘어 운영 가능한 파이프라인이 된다.

---

## 더 실습해보고 싶은 분들께

원문이 마지막에 agent pattern, evaluator-optimizer, overnight loop까지 연결하는 이유는 결국 이 파이프라인이 단발성 추출기가 아니라 반복 실행되는 시스템으로 들어가기 때문이다. schema를 고정하고, graph를 누적하고, harness로 매일 확인하는 구조를 직접 만져보고 싶은 분들에게는 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』와 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」가 참고가 될 수 있다. 이 글의 주제를 과하게 확장하기보다는, 원문이 말한 shared memory와 evaluation harness를 실제 agent loop 안에서 어떻게 다루는지 보는 용도에 가깝다.

---

## Source

- Local PDF: `Graph Engineering: 4 Models to 4 Prompts: The Anthropic Playbook`, Boris Cherny, independently compiled July 2026. The PDF states it is based on Anthropic's Knowledge Graph Cookbook, Building Effective AI Agents, and Claude API documentation, and is not affiliated with or endorsed by Anthropic.
