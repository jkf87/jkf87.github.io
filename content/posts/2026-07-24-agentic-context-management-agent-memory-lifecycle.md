---
title: "에이전트가 자기 컨텍스트를 관리하지 못하면 망한다 — Agentic Context Management의 5원시 프레임워크"
date: 2026-07-24T22:00:00+09:00
draft: false
summary: "프로덕션 AI 에이전트의 실패 원인은 추론 능력 부족이 아니라 '컨텍스트 관리' 부재다. 본 논문은 메모리를 단순한 저장소가 아닌 라이프사이클로 재정의하고, 5개 원시 연산(architecting, ingesting, scoping, anticipating, compacting)과 조직 스코프 위계를 제안한다. 토큰 비용은 O(n²)에서 O(n)으로, 정확도는 검증된 압축으로 유지한다."
tags:
  - agent
  - context-engineering
  - memory
  - LLM
  - harness
  - production
  - long-context
categories:
  - AI Agents
  - LLM Research
source_url: "https://arxiv.org/abs/2607.21503"
---

> **원논문**: [Agentic Context Management: Solving Agent Memory and Cost by Treating Them as Lifecycle and Architecture Problems](https://arxiv.org/abs/2607.21503) (Dadhich, 2026, arXiv:2607.21503)

## 한 줄 요약

프로덕션 AI 에이전트가 실패하는 진짜 이유는 추론을 못해서가 아니라 **자기 컨텍스트를 관리하지 못해서**다. 이 논문은 "메모리 = 저장소"라는 프레임을 버리고, 컨텍스트를 하나의 **라이프사이클**로 관리해야 한다고 주장한다. 다섯 개의 원시 연산과 조직 스코프 위계로 비용을 O(n²)에서 O(n)으로 줄이면서 정확도는 유지하는 설계를 보여준다.

---

## 문제: 에이전트는 자기 역사에 빠져 죽는다

2025년 기준 대다수 기업이 AI 에이전트를 실험하고 있지만, 실제 프로덕션까지 가는 건 10%도 안 된다 (McKinsey, 2025). 원인은 모델의 추론 능력이 부족해서가 아니다. 프론티어 모델은 충분히 잘 추론한다. 문제는 **컨텍스트 윈도우 안에 무엇을 담을지 결정하는 체계가 없을 때** 벌어진다:

- 긴 대화에서 이전 발화를 부분적으로 잊어버린다
- 도구 호출 결과가 누적되면서 컨텍스트가 부풀어지고, 할루시네이션이 시작된다
- 멀티 에이전트 핸드오프에서 모순이 발생한다
- 턴이 길어질수록 비용이 기하급수적으로 증가한다

기존 접근은 이걸 "메모리 문제", 즉 **저장소 문제**로 본다. 벡터 DB에 넣고, 검색하고, 끝. 이 논문은 그 프레임이 근본적으로 좁다고 반박한다.

## 재정의: 메모리에서 컨텍스트 매니지먼트로

저자(Gaurav Dadhich, Maximem AI)가 제안하는 새로운 이름은 **Agentic Context Management (ACM)**이다. 핵심 주장은 이렇다:

> "에이전트가 머릿속에 담고 있는 것을 능동적으로 관리하는 것은 **저장(save)**이 아니라 **라이프사이클**이다."

이 라이프사이클은 5개의 원시 연산(primitive)으로 쪼개진다. 아래 그림은 이 다섯 단계가 중앙의 에이전트를 어떻게 둘러싸는지 보여준다:

![Figure 1: 5원시 컨텍스트 라이프사이클 — architecting → ingesting → scoping → anticipating → compacting & consolidation](/images/2026-07-24-agentic-context-management/fig-1-p4.png)

### 1. Architecting (설계)

메모리를 저장하기도 전에, 이 에이전트에게 어떤 종류의 메모리가 필요한지 결정해야 한다. 코딩 에이전트와 고객 지원 에이전트는 다른 메모리 구조를 가져야 한다. 저자는 고정된 유니버셜 스키마가 아니라 **에이전트의 목적에서 자동 생성되는 맞춤형 메모리 아키텍처**를 주장한다.

### 2. Ingesting (수용)

대화 턴, 도구 호출 결과, 멀티모달 문서 등 원시 신호를 구조화된 검색 가능한 메모리로 변환한다. 핵심 관찰: **검색 품질은 수용(ingestion) 품질의 상한선이다.** "사용자가 요금제를 언급했다"를 저장하면 나중에 "4월 3일 Starter에서 Pro로 업그레이드했다"를 검색할 수 없다.

### 3. Scoping (범위 지정)

수용 시점과 검색 시점 모두에서, 전체 지식 중 어느 부분이 현재 맥락에 relevant한지 결정한다. 이것은 단순히 per-user가 아니라 **조직 위계(user → customer → client)**를 따른다:

- **User**: 개인 사용자의 컨텍스트
- **Customer**: 조직 단위의 컨텍스트 (팀의 플랜 히스토리 등)
- **Client**: 플랫폼 운영자 단위의 패턴

각 스코프는 strict isolation을 유지한다. 한 사용자의 데이터가 다른 사용자의 세션에 노출되지 않는다.

### 4. Anticipating (예측적 사전 로드)

에이전트가 **모르는 것을 모르기 때문에**, 명시적 요청이 오기 전에 필요할 컨텍스트를 미리 준비한다. CPU의 speculative prefetch와 같은 원리다. 저자의 참조 구현(Maximem Synap)은 60% 이상의 히트율을 일관되게 달성한다고 보고한다.

이것은 단순한 캐시가 아니다. 캐시는 반복된 쿼리에 같은 답을 반환한다. 반면 anticipation은 에이전트의 행동 패턴에서 **아직 요청되지 않은 컨텍스트**를 예측하여 미리 가져온다.

### 5. Compacting & Consolidation (압축과 통합)

관련 컨텍스트가 모델이 처리할 수 있는 예산을 초과할 때, 손실 없이 줄여야 한다. 핵심은 **검증된(validated) 압축**이다:

- 정보 손실을 자동 체크하는 validation score 반환
- 압축이 실패하면 덜 공격적인 압축으로 자동 재시도
- 카테고리별로 차등 적용 (계정 정보는 verbatim, 일반 잡담은 추상화 가능)

## 왜 저장소 접근이 충분하지 않은가: 경제학

### 비용은 이차함수로 증가한다

매 턴마다 전체 히스토리를 재전송하는 naïve 패턴(대부분의 hand-rolled 에이전트가 이렇게 동작한다)에서, n번째 턴의 누적 입력 토큰은:

$$C_{\text{append}} = \sum_{k=1}^{n} k \cdot t = t \cdot \frac{n(n+1)}{2} \approx \frac{t}{2} n^2 = O(n^2)$$

반면 컨텍스트를 고정 예산 W로 유지하면:

$$C_{\text{bounded}} = n \cdot W = O(n)$$

t=500, W=4,000을 가정하면, 100턴에서 약 6배, 200턴에서 약 13배의 비용 차이가 난다. 대화가 길어질수록 full-append 패턴은 감당할 수 없어진다.

### 하지만 무식하게 줄이면 정확도가 무너진다

단순 요약(summarization)은 토큰을 선형으로 줄이지만, **정확도 절벽**을 만든다. 인용된 사례: 18,282토큰을 122토큰으로 한 번에 압축했더니 정확도가 66.7% → 57.1%로 떨어졌다. 컨텍스트를 아예 안 준 것보다 못한 결과다.

**검증된 압축(validated compaction)**만이 선형 비용 + 정확도 유지를 달성한다. 이것이 이 논문이 말하는 "efficient frontier"다.

### 검색: 벡터만으로는 부족하다

저자의 검색 실험(5개 도메인, 각 10,000문서 / 1,000쿼리)에서 흥미로운 발견:

![Figure 4: 도메인별 키워드 vs 벡터 검색 MRR 비교 및 벡터 인덱싱 지연](/images/2026-07-24-agentic-context-management/fig-4-p9.png)

- **코드 검색**(CodeXGLUE): 벡터 0.91 vs 키워드 0.29 — "sort a list"가 bubble_sort를 찾는 건 의미 매칭이 필요하다
- **과학 QA**(SciQ): 키워드 0.81 vs 벡터 0.61 — "mitochondria"는 키워드지 비슷한 개념이 아니다
- **멀티홉**(HotpotQA): 단일 타겟 스코어링의 한계로 reasoning sufficiency를 측정하지 못한다

결론: **하이브리드(키워드 + 벡터 + 그래프)**가 필수다. 하지만 이것만으로는 충분하지 않다. 구조화된 수용과 스코프 인식 조립이 결합되어야 reasoning sufficiency가 닫힌다.

## 참조 구현: Maximem Synap

![Figure 5: Maximem Synap 참조 아키텍처 — SDK → API → managers/pipelines → polyglot storage](/images/2026-07-24-agentic-context-management/fig-5-p10.png)

Maximem Synap은 5개 원시 연산을 멀티테넌트 서비스로 구현한 참조 시스템이다:

- **비동기 수용**: 메모리 쓰기는 즉시 ingestion ID를 반환하고, 무거운 처리는 백그라운드에서
- **폴리글랏 저장소**: 벡터 스토어(의미 검색) + 그래프 스토어(관계) + 관계형 DB(source of truth) + 오브젝트 스토어
- **엔티티 해석**: "Sarah", "Sarah Chen", "SC"를 동일 인물로 정규화. 조직 스코프에서 "PR FAQ"과 "6-pager"를 동일 문서로 매핑
- **그래프 인식 검색**: 벡터 유사도로 그래프 진입점을 찾고, 관계를 따라 bridge document를 발견
- **검증된 압축**: 압축마다 validation score와 compression ratio를 반환, 실패 시 자동으로 덜 공격적으로 재시도

프로덕션 통합 패턴은 각 모델 호출마다 3번의 호출로 요약된다:

```
retrieved ← FETCH(query=user_message, scope={user, customer})
compacted ← COMPACT(current_conversation)
reply     ← MODEL(assemble(retrieved, compacted, recent_turns))
INGEST(turn, scope)   # 비동기; 즉시 ID 반환
```

이 패턴에서 에이전트 개발자가 다룰 것이 없는 부분이 핵심이다: 스키마 설계, 임베딩 모델 선택, 인덱스 관리, isolation 로직 — 모두 라이프사이클의 책임이다.

## 평가 결과

![Figure 6: LongMemEval 6개 카테고리별 결과 (전체 92.0%) 및 LoCoMo 카테고리 1-4 (93.2%)](/images/2026-07-24-agentic-context-management/fig-6-p15.png)

두 개의 공인 서드파티 벤치마크에서:

| 벤치마크 | 점수 | 비고 |
|----------|-------|------|
| LongMemEval | **92.0%** (460/500) | gpt-5-mini를 답변 모델로 사용 |
| LoCoMo (cat 1-4) | **93.2%** | 카테고리 5(적대적)는 제외 |

주목할 점: 답변 모델로 **gpt-5-mini**(더 작은 모델)를 사용했음에도 경쟁 시스템보다 높은 점수를 기록했다. 이는 점수 향상이 모델이 아니라 **컨텍스트 레이어**에서 왔다는 증거다.

약점도 솔직하게 보고한다: LongMemEval의 multi-session 카테고리(75.2%)에서 오류가 집중된다. 여러 세션에 걸친 정보를 결합하는 reasoning이 여전히 가장 어렵다.

## 기존 시스템과의 비교

논문의 Table 4는 주요 메모리 시스템을 5개 원시 연산 기준으로 매핑한다:

| 시스템 | Architecting | Ingesting | Scoping | Anticipating | Compacting |
|--------|:---:|:---:|:---:|:---:|:---:|
| MemGPT/Letta | — | ◐ | ◐ | ◐<sup>c</sup> | ● |
| Mem0 | — | ● | ◐ | — | — |
| Zep/Graphiti | — | ● | ◐ | — | — |
| SuperMemory | — | ● | ◐ | ◐<sup>f</sup> | — |
| ACE/Dyn. Cheatsheet | — | ● | — | — | ◐ |
| **Maximem Synap** | **●** | **●** | **●** | **●** | **●** |

대부분의 시스템이 ingesting에 집중하고 있으며, **generative per-agent memory architecting**이나 **query-predictive pre-fetch**를 주장하는 시스템은 거의 없다.

## 왜 이 논문이 중요한가

1. **프레임 전환**: "메모리"에서 "컨텍스트 매니지먼트"로. 저장이 아니라 라이프사이클이라는 관점이 에이전트 설계의 언어를 바꾼다.
2. **경제적 증명**: 단순한 효율 개선이 아니라, O(n²) 비용 구조를 O(n)으로 바꾸는 것은 프로덕션에서 존속 가능성의 문제다.
3. **검증된 압축**: "요약하면 된다"가 아니라 "검증 없는 압축은 독이다"라는 메시지는 실무적으로 중요하다.
4. **조직 스코프**: per-user 메모리에서 조직 단위의 context 위계로 가는 방향을 명확히 한다. 이것이 B2B 에이전트가 풀어야 할 다음 문제다.

## 한계와 과제

- 벤치마크가 대화 회상에 집중되어 있고, 프로덕션 부하下的 지연(latency)이나 토큰 효율성은 측정하지 않는다
- 참조 구현의 내부 메커니즘이 공개되지 않았다(proprietary)
- 결정 수준의 컨텍스트(decision-level context) — "왜 그렇게 결정했는가" — 는 미해결 영역이다
- 5개 원시 연산의 경계가 실제 구현에서는 다소 인위적일 수 있다

## 더 실습해보고 싶은 분들께

에이전트 컨텍스트 관리와 루프 엔지니어링은 말로 이해하는 것과 직접 구축해보는 것이 완전히 다른 영역입니다. 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 직접 만들어보면서 체득하는 활용 사례 50선
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 컨텍스트 설계부터 검증 루프까지, 에이전트 시스템을 견고하게 만드는 엔지니어링 실습

이 논문의 5원시 프레임워크(architecting, ingesting, scoping, anticipating, compacting)를 자기 에이전트에 적용해보려면, 위 실습 자료에서 다루는 루프 설계와 컨텍스트 엔지니어링 기초가 큰 도움이 된다.
