---
title: "메모리는 추상화와 구체성을 같이 들고 있어야 함 — Memora 조화 기억 구조 정리"
date: 2026-07-06
tags:
  - Memora
  - agent-memory
  - LLM
  - RAG
  - knowledge-graph
  - ICML-2026
  - Microsoft-Research
  - long-horizon-reasoning
draft: false
coverImage: /images/memora-harmonic-memory-2026-07-06/hero.jpg
---

에이전트가 똑똑하다는 건 찰나의 추론을 잘한다는 뜻임. 문제는 그 찰나가 쌓여도 경험이 되지 않는다는 것. 대부분의 LLM 에이전트는 stateless라서 같은 사용자가 어제 무슨 이야기를 나눴는지 매번 처음부터 다시 유추함. Microsoft Research가 ICML 2026에서 발표한 Memora(arXiv:2602.03315)가 이 문제를 정면으로 다룸. 핵심 질문은 "메모리에서 추상화와 구체성을 동시에 가져갈 수 없을까"임.

1. 진짜 어려움은 딜레마임. 추상화하면 디테일이 죽고 디테일을 살리면 파편화됨. 기존 접근은 양극단으로 갈렸음. 한쪽은 원시 로그와 원자적 팩트를 그대로 쌓음. 디테일은 살아있지만 노이즈에 묻힘. Mem0 같은 시스템이 팩트 단위 lifecycle 관리를 시도했고 Nemori는 episodic·semantic 결합을 시도함. 다른 쪽은 요약으로 압축하는데 특정 제약조건, 엣지 케이스, 숫자 같은 실행에 필요한 뉘앙스가 날아감.

2. 논문 표현으로 에이전트는 "관련 없는 팩트의 홍수"와 "실행 불가능한 모호한 요약" 사이에서 선택해야 했다는 것. 고수준 개념과 저수준 디테일을 잇는 구조적 링크가 없어서 자기 history를 탐색 못 한다는 진단임.

![조화 메모리 구조](/images/memora-harmonic-memory-2026-07-06/hero.jpg)

3. Memora의 풀이는 조화 기억(Harmonic Memory)이라는 이층 구조임. 메모리의 내용(content)과 메모리를 찾아가는 경로(navigation)를 분리한 게 핵심임. 구조는 세 단계임.

4. 첫째, 세그먼트 → 에피소드 기억. 원시 데이터를 의미 단위로 쪼개고 각 세그먼트에서 "이 세그먼트가 어디서 왔는지"를 담는 서사적 앵커를 만듦. 참여자, 의도, 시간 범위 요약이거나 원문 보존임.

5. 둘째, 주요 추상화. 각 메모리 엔트리가 "이 메모리가 근본적으로 무엇에 대한 것인가"를 담는 추상화와 구체 내용을 담는 메모리 값으로 구성됨. "Project Memora Timeline"이라는 추상화 아래에 마일스톤, 디자인 반복, 실험 결과가 계속 추가되는 식임. 추상화 임베딩 코사인 유사도로 top-k 후보를 찾고 LLM이 같은 개념인지 판별해서 같으면 Update, 새로우면 Create함.

6. 셋째, 큐 앵커. 주요 추상화는 의도적으로 거칠어서 디테일한 검색 경로가 필요함. 메모리 값에서 부가적 의미 신호를 뽑아 여러 개의 큐 앵커를 만들고 이게 엔트리 간 다대다 연결을 만듦. 명시적 엣지 없이 공유된 큐 앵커를 통해 암시적 메모리 그래프가 형성됨. 고정 스키마를 요구하지 않고 메타데이터 필터 역할까지 겸하는 게 설계의 미덕임.

![아키텍처](/images/memora-harmonic-memory-2026-07-06/fig1-architecture.png)

7. 재밌는 건 "RAG와 KG가 Memora의 특수 케이스"라는 주장임. 큐 앵커를 없애고 메모리 값 자체로만 검색하면 RAG가 되고 주요 추상화를 엔티티로, 큐 앵커를 엣지로 고정하면 KG가 됨. Appendix D에 증명이 들어있음. 기존 방법들을 품는 구조적 상위집합이라는 주장인데, RAG의 단순함과 KG의 연결성을 같이 챙기면서 각각의 약점(파편화, 스키마 경직성)은 회피한다는 실용적 함의가 있음.

8. 검색도 특이함. 수동적 매칭이 아니라 능동적 추론 과정으로 모델링함. Query refinement(쿼리 다듬기), Memory expansion(연결된 메모리 따라가기, multi-hop), Termination(충분하면 멈추기)의 이산 행동 공간을 정의하고 policy retriever를 GRPO로 훈련함.

![GRPO 훈련](/images/memora-harmonic-memory-2026-07-06/fig5-grpo-training.png)

9. 핵심은 정적 임베딩 유사도로 잡을 수 없는 multi-hop 의존성을 잡아낸다는 것. A가 B를 알고 B가 C를 알 때 A의 쿼리에 C가 필요한 상황에서 semantic retriever는 C를 못 찾지만 policy retriever는 expansion 액션으로 도달함.

10. 성능. LoCoMo에서 RAG 0.633, Mem0 0.653, Nemori 0.683에 비해 Memora Semantic Retriever 0.849, Policy Retriever 0.863임. LongMemEval_S(115k 컨텍스트, 500문제)에서 87.4%임.

![LoCoMo 결과](/images/memora-harmonic-memory-2026-07-06/fig2-locomo-results.png)

11. 제일 인상적인 건 full-context inference를 이겼다는 점임. 전체 대화 기록을 컨텍스트 창에 때려넣고 추론하는 것보다 Memora의 추상화 기반 검색이 더 정확함. "적절한 추상화 구조가 있으면 전체 컨텍스트보다 나은 추론이 가능하다"는 뜻임. 그리고 토큰 소비를 최대 98% 줄여서 full-context 대비 1/50 토큰으로 같은 이상의 정답률을 냄.

12. 실무 채점. 우리 에이전트 메모리 설계에 바로 적용할 것 두 개임. 첫째, 메모리 엔트리에 "무엇에 대한 것인가"라는 추상화 헤더와 구체 값을 같이 두고 create-or-update 규칙으로 중복을 막을 것. 둘째, 검색을 한 번의 임베딩 매칭이 아니라 쿼리 다듬기·확장·중단의 반복 액션으로 만들 것. multi-hop이 필요한 질문에 답이 달라짐.

13. 특히 "full-context보다 추상화 검색이 낫다"는 결과는 컨텍스트 창이 커지면 메모리가 불필요해진다는 통념을 뒤집는 것. 길이 싸움이 아니라 구조 싸움이라는 방향을 제시한다는 점에서 이 논문의 의의가 큼.

원문: [arXiv:2602.03315](https://arxiv.org/abs/2602.03315)
