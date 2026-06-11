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

| 모델 | 역할 |
|------|------|
| **Agent** (Search-R1) | 추론 + 검색 호출. 수정하지 않음 |
| **Critic** (LLM) | Agent의 reasoning trace를 읽고 검색 충분성 판단 |
| **Retriever** (임베딩 모델) | 쿼리 → 문서 검색. Critic-Embed로 학습됨 |

Critic을 Agent 밖에 분리한 이유가 두 가지 있다. 첫째, multi-step 궤적이 길어지면 agent가 검색 실패에 둔감해지는 **overconfidence**를 방지한다. 둘째, 어떤 agent에나 plug-and-play로 붙일 수 있다.

## Critic-R-Zero: 학습 없이 추론 시점에서 검색 복구

```
Agent 질문 → Retriever 검색 → Agent reasoning 작성
                                        ↓
                                Critic이 평가
                          충분 → 다음 단계
                          불충분 → 쿼리 재작성 → 재검색 (반복)
```

gradient 없이 추론 시점에만 작동한다. Critic은 Agent가 자연어로 쓴 reasoning trace를 읽고, "문서에 X 정보가 없다"는 문장을 보면 검색 실패로 판단한다. structured prompt로 판단 기준을 명시하고, few-shot examples로 충분/불충분 사례를 보여준다.

## Critic-Embed: 검색 궤적으로 임베딩 모델 파인튜닝

```
Critic-R-Zero 루프를 돌면서 궤적 축적
  → 성공한 검색 = positive
  → 실패한 검색 = hard negative
        ↓
Intra-trajectory contrastive learning
        ↓
Retriever (임베딩 모델) 파인튜닝
```

핵심은 **사람 라벨링이 불필요**하다는 점이다. Critic-R-Zero 루프를 돌면 성공/실패 궤적이 자동으로 쌓이고, 이걸 학습 데이터로 쓴다. 단순 텍스트 유사도가 아니라 **agent 추론에 실제 도움이 된 문서**를 구분하도록 임베딩 공간이 재구성된다.

## 일반 RAG과의 차이

| | 일반 RAG | Critic-R |
|---|---|---|
| Retriever | 고정 | **학습됨** (자동 라벨) |
| 피드백 | 없음 (일방통행) | **폐루프** |
| 학습 데이터 | 없음 | Critic 궤적으로 자동 생성 |

## 실험 결과

HotpotQA, 2WikiMultihopQA, MuSiQue, Bamboogle에서 평가했다.

- **Critic-R-Zero**: 추론 시 refinement만으로 12.4% 상대 개선
- **Critic-Embed**: 임베딩 모델 파인튜닝만으로 7.5% 상대 개선
- **Critic-R (결합)**: 10.9% 상대 개선

## 한 줄 요약

Agent가 검색 결과를 무조건 받아먹는 일방통행을, Critic을 사이에 둔 **폐루프**로 바꿔서 검색 실패를 복구하고, 그 경험으로 임베딩 모델까지 진화시킨다.

---

**참고문헌**

- Md Zarif Ul Alam, Alireza Saleki, Hamed Zamani. *Critic-R: Improving Agentic Search using Instruction-tuned Retrievers with Natural Language Introspective Feedback*. UMass Amherst, 2026. [arXiv:2606.00590](https://arxiv.org/abs/2606.00590)
