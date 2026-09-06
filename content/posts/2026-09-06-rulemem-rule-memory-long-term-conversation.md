---
title: "RuleMem: 장기 대화 에이전트 메모리는 규칙을 저장한다"
date: 2026-09-06
tags:
  - ai
  - agent
  - memory
  - llm
draft: false
description: "RuleMem은 장기 대화 이력에서 자연어 Horn 절 규칙을 유도해 검색과 추론을 동시에 guide하는 규칙 메모리 프레임워크입니다. LoCoMo에서 14개 baseline 평균보다 정확도 27.47점 높은 78.05를 기록했습니다."
---

## 결론 먼저

RuleMem(arXiv 2609.03915, 2026-09-03)은 에이전트 메모리를 <span style="background-color: #fff59d"><strong>재사용 가능한 논리 규칙 저장소로 직접 쓰는 프레임워크</strong></span>입니다. 긴 대화 이력에서 자연어 Horn 절 형태의 규칙을 뽑아내고, 검색 단계와 답변 생성 단계 양쪽에 직접 끼워넣습니다.

- LoCoMo benchmark에서 정확도 78.05, 14개 baseline 평균보다 <span style="background-color: #fff59d"><strong>27.47점(상대 +54.3%) 높음</strong></span>
- Multi-hop 질문 정확도 82.43, 최고 baseline 79.79 대비 우위
- 검색 실패·추론 실패를 각각 Guided Recall, Explicit Reasoning으로 분리해서 다룸

기준일: 2026-09-06, 논문 v1 기준입니다.

## 핵심 요약 표

| 항목 | 값 |
|---|---|
| 논문 | RuleMem: Active Rule Memory for Long-Term Conversational Agents (arXiv 2609.03915) |
| 소속 | 중산대 · HKUST(GZ) · SICS · 홍콩폴리U · 칭화 |
| 방식 | 대화 → 시간 사실 4원조 → 추론 경로 마이닝 → 자연어 Horn 절 규칙 유도 |
| 검증 | Rule Perplexity Consistency(RPC)로 규칙 신뢰도 필터 |
| backbone | gpt-4o-mini(규칙 유도·추론), ChromaDB + all-MiniLM-L6-v2 |
| LoCoMo | BLEU 평균 36.90, Accuracy 78.05, Multi-hop 82.43 |
| 데이터 | LoCoMo(대화 5,882턴, 질문 1,986개), LongMemEval_s*(약 182만 토큰, 300문항) |

## 기존 메모리가 실패하는 지점

기존 접근은 두 단계로 정리됩니다.

1. 사실 암기(fact memorization): MemGPT, Mem0, LangMem처럼 대화 조각을 저장하고 유사도로 꺼내 씀. 표면 유사도에 의존해서 <span style="background-color: #fff59d"><strong>질문과 증거가 어휘적으로 멀면 검색 자체가 실패</strong></span>
2. 사실 조직화(fact organization): Zep, A-MEM, Mem0g처럼 지식그래프·Zettelkasten 구조로 연결함. 규모가 커지면 쿼리와 무관한 노이즈가 늘고, LLM이 어떤 사실이 유효한 전제인지 스스로 추론해야 해서 <span style="background-color: #fff59d"><strong>논리 사슬이 끊기거나 환각이 생김</strong></span>

예시가 직관적입니다. "왜 Alice가 회의에 안 왔지?"라는 질문에는 "absent"라는 단어가 없습니다. "Alice가 휴가를 예약했다"는 기록에서 규칙 "여행 계획이 있으면 약속된 일정에 참석 못할 수 있다"를 유도해야 답이 나옵니다.

![](/images/2026-09-06-rulemem-rule-memory-long-term-conversation/figure1-paradigms.png)

Figure 1. 세 가지 메모리 패러다임 비교 — 사실 암기 / 사실 조직화 / 규칙 유도 (원문 Figure 1)

## RuleMem 구조: 귀납 → 검증 → 연역

3단계로 돌아갑니다.

### 1. Bottom-up 규칙 메모리 구축

- 대화에서 (주체, 관계, 객체, 시각) 4원조를 뽑아 사실 메모리 베이스 구성
- 그래프 구조에서 제약 랜덤 워크로 후보 경로 샘플링, LLM이 비논리 경로 제거
- 같은 관계 패턴의 경로들을 묶어 LLM이 공통 규칙으로 유도. 이때 Alice, Bob 같은 고유명사를 [Person], [Event] 같은 <span style="background-color: #fff59d"><strong>타입 placeholder로 치환해 일반화</strong></span>

규칙 형식은 Horn 절입니다. 몸통(전제들의 conjunct)과 머리(결론) 하나:

```
B1 ∧ B2 ∧ ... ∧ Bn  ⟹  H
```

각 atom은 자연어 관계 구문이라 형식 논리의 엄격함과 자연어의 유연함을 같이 씁니다.

### 2. RPC(Rule Perplexity Consistency) 검증

LLM에 규칙을 뽑게 하면 <span style="background-color: #fff59d"><strong>과잉 일반화·환각 규칙이 나오는 게 기본</strong></span>입니다. RuleMem은 두 신호를 결합해 필터링합니다.

- 내부 일관성 Δself: 규칙 몸통을 조건으로 줬을 때 결론의 perplexity가 얼마나 감소하는지 (Llama-3-8B-Instruct로 측정)
- 외부 사실 일관성: 실제 사실 증거가 결론을 지지하는지

RPC admission threshold τ=0.5, 균형 계수 α=0.4가 경험적 기본값입니다.

### 3. Top-down 규칙 기반 QA

새 질문이 오면 순서를 뒤집습니다.

- 규칙 활성화: 질문을 추상 결론 공간에 매핑해 관련 규칙 선택
- Guided Recall: <span style="background-color: #fff59d"><strong>활성화된 규칙의 몸통(전제)을 검색 쿼리로 써서</strong></span> 의미상 멀어도 논리적으로 관련된 사실을 회수. LLM이 타입 제약으로 변수 바인딩 오매칭을 걸러냄(의미적 unification)
- Explicit Reasoning: 질문 + 활성화 규칙 + 회수된 증거를 구조화된 프롬프트로 생성. 규칙이 대전제, 사실이 소전제 역할

![](/images/2026-09-06-rulemem-rule-memory-long-term-conversation/figure2-framework.png)

Figure 2. RuleMem 프레임워크 전체 구조 (원문 Figure 2)

## 성능: LoCoMo에서 baseline 최고치

LoCoMo 4개 질문 유형(Single-hop, Multi-hop, Open-domain, Temporal)에서 평가했습니다.

![](/images/2026-09-06-rulemem-rule-memory-long-term-conversation/table1-locomo.png)

Table 1. LoCoMo 성능 비교 (원문 Table 1)

- <span style="background-color: #fff59d"><strong>Accuracy 78.05, BLEU 평균 36.90</strong></span>로 14개 baseline 전반 최고
- Multi-hop 정확도 82.43 (최고 baseline 79.79)
- Single-hop에서 BLEU 42.12로 생성 품질 1위. Guided Recall이 규칙을 정확한 단서로 써서 구체적 디테일 손실이 적음

baseline은 세 그룹입니다. 사실 암기(Mem0, LangMem, Letta), 사실 조직화(A-MEM, Mem0g, MemoryBank, MemInsight, Zep, SCM), RAG(BM25, ReAct, MetaKGRAG, LightRAG, GraphRAG). 평가 스크립트·메트릭은 Mem0 저장소와 동일하게 맞췄습니다.

## 성능 이득의 출처

![](/images/2026-09-06-rulemem-rule-memory-long-term-conversation/figure3-analysis.png)

Figure 3. 검색 실패·추론 실패 분석과 RPC 하이퍼파라미터 민감도 (원문 Figure 3)

- Guided Recall을 붙이면 모든 프레임워크에서 검색률이 0.56 → 0.79로 상승(+41.1%). LoCoMo의 수동 주석 supporting facts 기준
- Explicit Reasoning은 baseline별 추론 실패 수를 일관되게 줄임
- Ablation: 규칙 추상화를 빼면(w/o Rule+RPC) <span style="background-color: #fff59d"><strong>성능이 baseline 수준으로 떨어짐</strong></span>. RPC 필터를 빼면(w/o RPC) 걸러지지 않은 오류 규칙이 연역을 방해해 성능 저하. 규칙 추상화와 RPC 검증 둘 다 필요

## 적용 지점과 한계

- RAG가 "소전제(사실)"만 공급한다는 지적이 이 논문의 핵심 프레임입니다. GraphRAG 계열이 구조를 늘려도 대전제 없이는 추론 부담이 전부 생성 모델에 남습니다. 규칙 뱅크를 따로 두는 설계는 <span style="background-color: #fff59d"><strong>긴 대화형 제품(친구·비서·CS 봇)에 바로 적용할 수 있는 구조</strong></span>입니다.
- 규칙 유도는 gpt-4o-mini급 소형 모델로도 돌리므로, 메모리 구축 비용이 매 쿼리마다 LLM 감독하는 구조보다 저렴합니다. 규칙은 amortized 자산이라는 관점이 MIRA류 메모리-증폭 RL과도 통합니다.
- 한계도 분명합니다. 자연어 Horn 절에 형식적 변수 통일이 없어 오매칭 위험을 LLM 필터로만 막고, LoCoMo가 일상 대화 중심이라 도메인 지식 QA에서의 규칙 유도 품질은 미검증입니다. RPC threshold도 경험적 튜닝이 필요합니다.

## 원문

- arXiv: https://arxiv.org/abs/2609.03915
- HTML: https://arxiv.org/html/2609.03915v1
- PDF: https://arxiv.org/pdf/2609.03915

## 자주 묻는 질문

### RuleMem이 기존 Mem0·Zep과 다른 점은?

Mem0·Zep은 사실을 저장하거나 그래프로 조직화하는 수준입니다. RuleMem은 사실에서 규칙(자연어 Horn 절)을 유도해 검색 쿼리와 추론 대전제로 능동적으로 사용합니다.

### RPC는 무엇을 측정하나?

규칙 몸통(전제)을 조건으로 줬을 때 결론의 perplexity 감소량을 내부 일관성 신호로 쓰고, 실제 사실 증거와의 일관성을 합쳐 규칙의 신뢰도를 점수화합니다. threshold τ=0.5가 기본값입니다.

### LoCoMo 성능은?

Accuracy 78.05로 14개 baseline 평균보다 27.47점 높고, Multi-hop 정확도는 82.43입니다. BLEU 평균은 36.90입니다.

### 구현에 어떤 모델을 썼나?

규칙 유도와 명시적 추론에는 gpt-4o-mini, RPC 측정에는 Llama-3-8B-Instruct, 벡터 저장은 ChromaDB(all-MiniLM-L6-v2)를 썼습니다.

### 규칙을 전부 다 믿으면 안 되는 이유는?

LLM 규칙 유도는 과잉 일반화·환각을 동반합니다. Ablation에서 RPC 필터를 제거하면 오류 규칙이 추론을 방해해 성능이 떨어집니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
