---
title: "Critic-R: 에이전트 검색에서 Retriever를 스스로 진화시키는 폐루프 프레임워크"
date: 2026-06-11
draft: false
tags:
  - AI
  - agentic-search
  - retrieval
  - RAG
  - embedding
  - paper
source: arxiv
source_url: https://arxiv.org/abs/2606.00590
---

Agentic search에서 **검색 품질이 병목**이다. Agent가 아무리 똑똑해도 Retriever가 구리면 답도 구리다. UMass Amherst에서 발표한 **Critic-R**은 이 병목을 두 단계로 공격한다: 추론 시점에 검색 실패를 복구하고, 그 경험으로 임베딩 모델을 파인튜닝한다.

## 핵심 구조: 3개 모델의 협업

![Critic-R Overview](/images/2026-06-11-critic-r-agentic-search-retriever-tuning/fig1-overview.png)

위 Figure 1은 Critic-R의 전체 파이프라인을 보여준다. 위쪽은 **Critic-R-Zero**의 추론 시점 루프, 아래쪽은 **Critic-Embed**의 학습 파이프라인이다.

| 모델 | 역할 |
|------|------|
| **Agent** (Search-R1) | 추론 + 검색 호출. 수정하지 않음 |
| **Critic** (LLM) | Agent의 reasoning trace를 읽고 검색 충분성 판단 |
| **Retriever** (임베딩 모델) | 쿼리 → 문서 검색. Critic-Embed로 학습됨 |

Critic을 Agent 밖에 분리한 이유가 두 가지 있다. 첫째, multi-step 궤적이 길어지면 agent가 검색 실패에 둔감해지는 **overconfidence**를 방지한다. 둘째, 어떤 agent에나 plug-and-play로 붙일 수 있다.

## Critic-R-Zero: 학습 없이 추론 시점에서 검색 복구

Figure 1 위쪽 루프를 따라가면 이렇게 작동한다:

1. **질문** 들어옴 (예: "인셉션 감독이 명예박사 받기 전에 다닌 대학교는?")
2. **Agent**가 thinking trace를 생성하고 검색 쿼리를 뽑음 ("Inception director's university")
3. **Retriever**가 top-k 문서를 반환
4. Agent가 문서를 읽고 **introspective reasoning** 작성 → 여기서 "문서에 감독 이름이 없다"고 쓰면
5. **Critic**이 reasoning trace를 보고 검색 실패 판단 → 쿼리를 재작성 ("Christopher Nolan filmmaker biography")
6. 만족할 때까지 반복, 충분하면 문서를 trajectory에 커밋
7. 최종 정답 도출

gradient 없이 추론 시점에만 작동한다. Critic은 structured prompt로 판단 기준을 명시하고, few-shot examples로 충분/불충분 사례를 보여준다.

## Critic-Embed: 검색 궤적으로 임베딩 모델 파인튜닝

Figure 1 아래쪽 학습 파이프라인은 3단계로 구성된다:

1. **궤적 수집**: Critic-R-Zero를 훈련셋에 돌려서 성공/실패 검색 궤적 축적
2. **학습 데이터 구성**: 성공 = positive, 실패 = hard negative (intra-trajectory)
3. **Contrastive learning**: Stella-400M 백본에 InfoNCE loss로 파인튜닝

핵심은 **사람 라벨링이 불필요**하다는 점이다. 단순 텍스트 유사도가 아니라 **agent 추론에 실제 도움이 된 문서**를 구분하도록 임베딩 공간이 재구성된다.

## Retriever 비교 결과

![Retriever Comparison](/images/2026-06-11-critic-r-agentic-search-retriever-tuning/fig2-results.png)

Figure 2는 Critic-Embed가 기존 retriever 대비 얼마나 나은지 보여준다. Critic 루프 없이 retriever만 비교해도 Stella-400M과 Agentic-R을 모든 top-k에서 압도한다.

| top-k | Stella-400M | Agentic-R | **Critic-Embed** |
|------:|------------:|----------:|----------------:|
| 1 | 0.447 | 0.456 | **0.481** |
| 3 | 0.499 | 0.497 | **0.514** |
| 5 | 0.512 | 0.510 | **0.527** |

## 일반 RAG과의 차이

| | 일반 RAG | Critic-R |
|---|---|---|
| Retriever | 고정 | **학습됨** (자동 라벨) |
| 피드백 | 없음 (일방통행) | **폐루프** |
| 학습 데이터 | 없음 | Critic 궤적으로 자동 생성 |

## 전체 성능 요약

HotpotQA, 2WikiMultihopQA, MuSiQue, Bamboogle에서 평가했다.

- **Critic-R-Zero**: 추론 시 refinement만으로 12.4% 상대 개선
- **Critic-Embed**: 임베딩 모델 파인튜닝만으로 7.5% 상대 개선
- **Critic-R (결합)**: 10.9% 상대 개선

## 한 줄 요약

Agent가 검색 결과를 무조건 받아먹는 일방통행을, Critic을 사이에 둔 **폐루프**로 바꿔서 검색 실패를 복구하고, 그 경험으로 임베딩 모델까지 진화시킨다.

---

**참고문헌**

- Md Zarif Ul Alam, Alireza Saleki, Hamed Zamani. *Critic-R: Improving Agentic Search using Instruction-tuned Retrievers with Natural Language Introspective Feedback*. UMass Amherst, 2026. [arXiv:2606.00590](https://arxiv.org/abs/2606.00590)
