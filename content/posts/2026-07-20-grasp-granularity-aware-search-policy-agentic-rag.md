---
title: "GRASP: 강화학습으로 에이전트 RAG의 검색 도구를 자유자재로 다루게 만드는 방법"
slug: 2026-07-20-grasp-granularity-aware-search-policy-agentic-rag
publish: true
date: 2026-07-20T07:00:00+09:00
tags:
  - agentic-rag
  - reinforcement-learning
  - retrieval-augmented-generation
  - LLM-agent
  - tool-use
  - multi-hop-reasoning
  - GRPO
  - search-policy
source: arxiv
source_url: https://arxiv.org/abs/2607.10463
authors:
  - Varun Gandhi
  - Jaewook Lee
  - Shantanu Todmal
  - Franck Dernoncourt
  - Ryan Rossi
  - Zichao Wang
  - Andrew Lan
affiliations:
  - University of Massachusetts Amherst
  - Adobe Research
---

## 한 줄 요약

**GRASP**는 에이전트 RAG(Agentic RAG) 시스템이 강화학습을 통해 **의미 검색·키워드 검색·문단 읽기** 세 가지 도구를 상황에 맞게 선택하고 조율하도록 훈련하는 프레임워크입니다. 다중 홉(multi-hop) 추론 벤치마크에서 기존 방법들을 뛰어넘는 성능을 보였으며, 학습된 정책은 인간의 정보 탐색 패턴(스키밍 → 정독 → 키워드 스캔)과 유사한 행동을 자발적으로 발현합니다.

---

## 왜 이 논문이 중요한가

에이전트 RAG는 LLM이 스스로 검색 쿼리를 생성하고, 증거를 수집하며, 이를 바탕으로 답을 도출하는 강력한 패러다임입니다. 하지만 현실에서는 다음 세 가지 난관에 부딪힙니다.

1. **언제 검색할 것인가?** — 필요한 순간에 검색을 시작하는 것
2. **어떤 검색 신호를 쓸 것인가?** — 의미적 유사성(semantic) vs 어휘적 매칭(lexical, BM25)
3. **얼마나 많은 문맥을 가져올 것인가?** — 문장 단위로 정밀하게 가져올지, 문단 전체를 읽을지

기존 방법은 대개 단일 검색 도구만 사용하거나, 고정된 청크(chunk) 크기로 검색했습니다. GRASP는 이 세 가지 문제를 **동시에** 해결합니다.

![GRASP 프레임워크 개요: 쿼리 q가 주어지면 정책 LLM이 여 롤아웃을 생성하고, 각 트랙토리는 보상 모델로 평가된 후 GRPO로 정책이 업데이트됩니다](/images/2026-07-20-grasp-granularity-aware-search-policy-agentic-rag/fig-2-p4.png)
*Figure 2: GRASP 프레임워크 개요. 정책 LLM이 여러 롤아웃(trajectory)을 생성하고, 보상 모델이 각각을 평가하며, GRPO로 정책을 업데이트합니다.*

## 핵심 설계: 세 가지 도구와 보상 구조

### 액션 공간 (Action Space)

GRASP는 에이전트에게 세 가지 증거 수집 도구 + 종료 액션을 제공합니다:

| 도구 | 기호 | 역할 |
|------|------|------|
| 의미 검색 (semantic search) | τₛ | 밀집 표현(dense representation)으로 개념적 유사성 탐색 |
| 키워드 검색 (keyword search) | τₖ | BM25 기반 어휘 매칭으로 엔티티 특정 증거 검색 |
| 문단 읽기 (read paragraph) | τᵣ | 검색된 문장의 원본 문단을 확장하여 문맥 확인 |
| 답변 제출 | τₐ | 최종 답안 생성 후 종료 |

핵심 아이디어는 **문장 수준의 세밀한 증거부터 시작**해서, 필요할 때만 문단 전체를 펼쳐서 확인한다는 것입니다. 이를 통해 불필요한 토큰이 컨텍스트 창을 오염하는 것을 막습니다.

### 보상 설계 (Reward Design)

GRASP의 보상 함수는 네 가지 항목으로 구성됩니다:

$$R = R_A + \alpha \cdot R_R + \beta \cdot R_S + \gamma \cdot R_E$$

- **R_A (답안 정확도)**: 예측 답안과 정답 간의 토큰 수준 F1 (0~1)
- **R_R (근거 기반 읽기)**: τᵣ로 읽은 문단이 실제 골드 문서인지 (F1, 가중치 α=0.7)
- **R_S (보완적 검색)**: τₛ와 τₖ 모두가 골드 문서를 검색했는지 (이진, 가중치 β=0.15)
- **R_E (턴 효율성)**: 정답에 도달하는 데 사용한 턴 수의 효율 (가중치 γ=0.15)

보조 보상의 총합이 1.0을 넘지 않도록 설계하여, **답안 정확도가 항상 주 동력**이 되도록 했습니다. 이는 보상 해킹(reward hacking)을 방지하는 핵심 설계입니다.

## 학습 방법: GRPO

GRASP는 **Group-Relative Policy Optimization(GRPO)** 를 사용하여 정책을 학습합니다. 같은 쿼리에 대해 G개의 트랙토리(trajectory)를 샘플링하고, 그룹 내 상대적 보상으로 어드밴티지를 계산합니다. 절대 보상 스케일이 아닌 그룹 내 비교를 통해 업데이트하므로, 보상 설계의 노이즈에 더 강건합니다.

베이스 모델은 **Qwen2.5-3B-Instruct**를 사용했습니다. 3B 크기의 소형 모델로도 강력한 검색 정책을 학습할 수 있다는 점이 이 논문의 중요한 메시지입니다.

## 실험 결과

### 검색 리콜 (Retrieval Recall)

HotpotQA, 2WikiMultiHopQA, MuSiQue 세 개의 다중 홉 QA 벤치마크에서 평가했습니다.

| 방법 | 모델 | HotpotQA | 2Wiki | MuSiQue |
|------|------|----------|-------|---------|
| 단일 검색 (하이브리드) | — | 80.0 | 80.3 | 65.7 |
| IRCoT | GPT-5-mini | 86.7 | 88.0 | 74.3 |
| Search-R1 | Qwen2.5-3B | 82.3 | 81.7 | 67.7 |
| **GRASP** | **Qwen2.5-3B** | **88.7** | **89.7** | **76.3** |

GRASP는 소형 3B 모델을 사용하면서도 GPT-5-mini를 쓰는 IRCoT를 능가했습니다.

### 답안 품질 (QA Metrics)

EM(Exact Match)과 F1 점수에서도 일관되게 최고 성능을 기록했습니다. 특히 **MuSiQue** 같은 어려운 벤치마크에서 기존 방법 대비 큰 격차를 보였는데, 이는 정밀한 문장 단위 검색과 문단 확장의 조합이 복잡한 추론에 효과적이라는 것을 보여줍니다.

![GRASP 학습 곡선: 총 보상 R이 GRPO 스텝에 따라 꾸준히 상승합니다](/images/2026-07-20-grasp-granularity-aware-search-policy-agentic-rag/fig-3-p14.png)
*Figure 3: GRPO 학습 과정에서 총 보상 R의 변화. 훈련이 진행될수록 보상이 안정적으로 상승합니다.*

## 정성 분석: 인간처럼 검색하기

GRASP의 가장 흥미로운 발견은 **학습된 정책이 인간의 정보 탐색 패턴과 유사한 행동을 자발적으로 학습**했다는 점입니다.

![GRASP 에이전트의 행동 전이 그래프: 의미 검색 → 문단 읽기 → 키워드 검색의 순환 패턴](/images/2026-07-20-grasp-granularity-aware-search-policy-agentic-rag/fig-4-p14.png)
*Figure 4: 에이전트 행동의 1차 마르코프 전이 그래프. 의미 검색으로 시작 → 문단 읽기로 확인 → 키워드 검색으로 정제하는 패턴이 dominant합니다.*

관찰된 패턴은 다음과 같습니다:

1. **τₛ (의미 검색)로 시작** — 넓은 영역을 탐색하며 관련 주제/엔티티를 찾습니다.
2. **τᵣ (문단 읽기)로 확인** — 검색된 문장의 원본 문단을 읽어 로컬 문맥을 파악하고 브릿지 엔티티를 추출합니다.
3. **τₖ (키워드 검색)로 정제** — 추출한 엔티티로 정확한 키워드 검색을 수행해 다음 홉의 증거를 찾습니다.

이것은 Grellet(1981)이 기술한 인간의 읽기 전략 — **스키밍(skimming)으로 전체를 파악 → 정독으로 세부사항 확인 → 스캐닝(scanning)으로 특정 정보 검색** — 과 놀랍도록 유사합니다. 아무도 이 패턴을 명시적으로 가르쳐주지 않았습니다. RL 보상 구조만으로 이 패턴이 창발(emerge)했습니다.

### 실제 궤적 예시

Eminem의 곡 "The Monster"가 수록된 앨범을 묻는 질문에 대한 GRASP의 검색 과정:

1. **τₛ**: "Eminem vocals Unapologetic" 의미 검색 → 방해 문서(Encore) 등장
2. **τₖ**: 정확한 키워드 "Eminem vocals Unapologetic" → Unapologetic은 Rihanna의 앨범, The Monster는 Eminem ft. Rihanna 곡
3. **τᵣ**: Unapologetic 문단 읽기 → Rihanna 확인 (1홉 완료)
4. **τₛ**: "Rihanna The Monster album" 의미 검색
5. **τᵣ**: The Marshall Mathers LP 2 문단 확인
6. **τₐ**: 정답 "The Marshall Mathers LP 2" 제출 ✅

반면 Search-R1은 중간 단계에서 환각(hallucination)을 일으켜 "Kelly Clarkson"이라는 존재하지 않는 연결을 만들어냈습니다.

## 제거 실험 (Ablation Study)

| 설정 | EM | F1 |
|------|-----|-----|
| GRASP (전체) | **최고** | **최고** |
| τₖ 없음 (키워드 검색 제거) | ↓ | ↓ |
| τₛ 없음 (의미 검색 제거) | ↓↓↓ | ↓↓↓ |
| τᵣ 없음 (문단 읽기 제거, 문단 단위 검색) | ↓ | ↓ |

흥미로운 점:
- **의미 검색 제거**가 키워드 검색 제거보다 훨씬 더 큰 성능 저하를 일으킵니다. 의미 검색이 "넓은 탐색"의 핵심이기 때문입니다.
- **문단 단위 검색**(문장 단위 + τᵣ 없음)은 중간 쿼리의 질을 떨어뜨립니다. 문단 전체가 한 번에 들어오면 어떤 엔티티가 다음 검색의 단서인지 모호해지기 때문입니다.

## 한계점

논문은 다음 한계를 솔직하게 인정합니다:

1. **골드 주석 의존성**: R_R과 R_S 보상이 정답 문단 라벨을 필요로 합니다. 약한 지도(self-supervised) 대안이 필요합니다.
2. **단일 모델 규모**: 3B 모델에서만 실험했습니다. 7B, 14B 등에서 패턴이 어떻게 변하는지 미지수입니다.
3. **조기 종료 문제**: 가끔 충분한 증거가 모이기 전에 답을 제출하는 경향이 있습니다.

## 더 실습해보고 싶은 분들께

이 논문은 에이전트가 도구를 어떻게 선택하고 조율하는지 배우는 **강화학습 기반 접근**을 보여줍니다. 실제로 에이전트 하네스를 설계하거나 RAG 파이프라인에 강화학습을 적용해보고 싶다면, 다음 자료가 실무에 직접 도움이 됩니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 루프와 도구 사용 패턴을 실무에서 설계하는 방법을 다룹니다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 하네스의 보상 설계와 효율적인 루프 구성을 체계적으로 배울 수 있습니다.

## 마무리

GRASP는 단순한 RAG 개선이 아니라, **에이전트가 스스로 도구를 학습하는 방법**을 제시합니다. 검색이라는 행위 자체를 강화학습의 액션 공간에 넣고, 보상 설계를 통해 정답 정확도뿐 아니라 검색 행동의 품질까지 최적화한 것이 핵심입니다.

3B 모델로도 충분히 강력한 검색 정책을 학습할 수 있다는 점, 그리고 그 정책이 인간의 정보 탐색 패턴과 유사한 행동을 창발적으로 발현한다는 점은, 앞으로 에이전트 RAG 시스템을 설계하는 사람들에게 중요한 방향을 제시합니다.

---

> **Paper**: [GRASP: GRanularity-Aware Search Policy for Agentic RAG](https://arxiv.org/abs/2607.10463)
> **Authors**: Varun Gandhi, Jaewook Lee, Shantanu Todmal, Franck Dernoncourt, Ryan Rossi, Zichao Wang, Andrew Lan
> **Affiliations**: University of Massachusetts Amherst, Adobe Research
> **Code/Data**: 논문 참조
