---
title: "LLM 에이전트 메모리를 흑백 문서 대신 잠재 공간에서 풀어내는 방법: LGM 논문 정리 (arXiv 2609.18461)"
date: 2026-09-22
tags:
  - LLM 에이전트
  - 메모리
  - 개인화
  - 희소 오토인코더
  - paper-summary
draft: true
description: "LLM 에이전트 장기 메모리를 원문 텍스트 검색 대신 희소 오토인코더로 잠재 그래프를 만들어 쿼리별로 풀어내는 LGM 논문을 정리했습니다. PersonaMem 평균 72.28, MemCoE 대비 +11.20p 수치와 구조를 함께 담았습니다."
refactor_hub: agent-memory-07
refactor_status: queued
---

## 핵심 요약

LLM 에이전트에 장기 메모리를 붙이면 대부분 이렇게 됩니다. 대화 기록을 문장 단위로 잘라 저장하고, 질문이 오면 비슷한 문장을 검색해서 프롬프트에 넣죠. 근데 사용자 취향 같은 건 한 문장에 다 들어있지 않습니다. 여러 세션에 흩어진 행동 흔적을 조합해야 나오는 정보예요.

LGM 논문(arXiv 2609.18461)은 이 문제를 잠재 공간(latent space)으로 옮겨서 풉니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>메모리를 미리 만든 고정 그래프로 저장하지 않고, 질문이 들어올 때마다 희소 오토인코더(SAE)로 잠재 노드를 만들고 쿼리에 맞게 엣지를 새로 계산</strong></span>합니다.

결과는 PersonaMem/PrefEval 기준 Qwen2.5-7B에서 <span style="background-color: #fff59d"><strong>평균 정확도 72.28, 가장 강한 기존 baseline인 MemCoE 대비 +11.20p</strong></span>입니다. 토큰 비용과 응답 지연도 낮은 축에 속합니다.

## 핵심 요약 표

| 항목 | 내용 |
| --- | --- |
| 논문 | Disentangling Long-Term Memory via Latent Neuro-Symbolic Reasoning (arXiv 2609.18461) |
| 핵심 문제 | 텍스트 메모리는 뒤엉켜 있고(noisy/entangled), 고정 그래프는 질문에 따라 달라지는 관계를 못 잡음 |
| 제안 | LGM: SAE 기반 잠재 노드 + 쿼리 조건부 잠재 그래프 + 그래프 인코더 조건 생성 |
| 주요 수치 | PersonaMem/PrefEval 평균 72.28 (Qwen2.5-7B), 66.16 (Gemma3-4B) |
| 기존 최강 대비 | MemCoE 대비 +11.20p / +11.70p |
| 잘 나오는 구간 | 암시적(implicit) 선호, 128K 롱컨텍스트 |
| 백본 | Qwen2.5-7B, Gemma3-4B, Qwen3-4B |
| 기준일 | 2026-09-22 기준, v2(2026-09-18) |

## 기존 메모리 방식이 놓치는 두 가지

### 문장 단위 검색의 한계

Mem0나 Naive RAG처럼 메모리 조각을 독립적으로 점수 매기는 방식은, 답에 필요한 증거가 한 조각에 안 들어 있으면 실패합니다. "이 사용자는 아침에 커피를 안 마신다"는 어디에도 직접 안 나오고, <span style="background-color: #fff59d"><strong>매번 오후에만 커피를 주문한 기록 여러 개</strong></span>에서 추론해야 하는 경우가 그렇습니다.

### 고정 그래프의 한계

LightRAG, Youtu-GraphRAG 같은 구조화 메모리는 미리 그래프를 만들어 둡니다. 근데 관계의 중요도는 질문에 따라 달라져요. 같은 기록이라도 "선호하는 카페인 시간" 질문에서는 커피 주문 엣지가 중요하고, "여행 취향" 질문에서는 항공권 예약 엣지가 중요합니다. <span style="background-color: #fff59d"><strong>쿼리와 무관하게 정적으로 만든 위상 구조는 이걸 못 따라감</strong></span>니다.

## LGM 구조: 세 단계로 보기

![LGM 전체 구조](/images/2026-09-22-llm-agent-latent-memory-disentanglement-lgm/fig2-overview.png)
*그림 2. LGM 개요 — 질문이 들어와야 메모리 그래프를 만드는 on-demand 구조 (원문 Figure 2)*

### 1단계: 희소 오토인코더로 잠재 노드 만들기

과거 상호작용을 그대로 텍스트로 저장하지 않고 임베딩으로 인코딩한 뒤, SAE를 통과시켜 <span style="background-color: #fff59d"><strong>희소한 개념 활성(sparse concept activations)으로 분해</strong></span>합니다. 하나의 메모리가 어떤 개념들의 조합인지 분리되는 거죠. 이게 "disentangling"의 핵심입니다.

### 2단계: 쿼리 조건부 그래프 구성

질문 임베딩을 조건으로 삼아 잠재 노드 사이 엣지 가중치를 동적으로 계산합니다. 같은 메모리라도 질문이 다르면 다른 서브그래프가 만들어집니다. 미리 그래프를 다 만들어 두는 게 아니라는 점이 기존 GraphRAG와 다른 지점입니다.

### 3단계: 그래프 인코더로 메시지 패싱

쿼리 임베딩이 선호 조건으로 작동하면서 서브그래프 위에 비선형 메시지 패싱을 돌립니다. 나온 압축 표현이 생성 모델을 조건화합니다. 이때 <span style="background-color: #fff59d"><strong>증거 복원(evidence-reconstruction) 목적함수</strong></span>를 붙여서 잠재 표현이 원래 정보를 잃지 않게 잡아줍니다.

## 수치: 얼마나 좋아지나

![Table 1 결과](/images/2026-09-22-llm-agent-latent-memory-disentanglement-lgm/table1-results.png)
*표 1. PersonaMem/PrefEval 정확도 (원문 Table 1)*

Qwen2.5-7B 기준 주요 숫자만 뽑으면:

| 방법 | 계열 | 평균 | 대비 |
| --- | --- | --- | --- |
| Long Context / Naive RAG | 평면 검색 | 하위권 | – |
| Mem0 | 에이전트 메모리 | 48.05 | +24.23 |
| A-Mem | 에이전트 메모리 | 50.40 | +21.88 |
| Memory-R1 | RL 메모리 | 56.23 | +16.05 |
| MemCoE | 통합 정책 | 61.08 | +11.20 |
| LGM (본 논문) | 잠재 심볼릭 | 72.28 | – |

Gemma3-4B에서도 66.16으로 1위, MemCoE 대비 +11.70p입니다. 백본을 바꿔도 격차가 유지되는 걸 구조 효과로 보고 있어요.

특히 눈에 띄는 두 구간:

- <span style="background-color: #fff59d"><strong>암시적 선호(implicit) 분할</strong></span>: 명시적으로 말한 취향이 아니라 행동에서 추론해야 하는 구간에서 격차가 가장 큼
- <span style="background-color: #fff59d"><strong>128K 롱컨텍스트</strong></span>: 증거가 여러 세션에 흩어진 설정에서도 유리

![효율 비교](/images/2026-09-22-llm-agent-latent-memory-disentanglement-lgm/fig3-efficiency.png)
*그림 3. LLM 호출/토큰/지연 효율 비교 (원문 Figure 3)*

원문 히스토리를 매번 리플레이하지 않기 때문에 <span style="background-color: #fff59d"><strong>LLM 호출 수, 토큰 소비, 첫 토큰까지 시간 모두 낮은 비용 프론티어</strong></span>에 위치한다고 합니다. 정확도만 올린 게 아니라 비용도 같이 잡았다는 점이 실용적입니다.

## 흥미로운 지점: RL 메모리와의 비교

테이블에 Memory-R1, Mem-α, MemAgent 같은 <span style="background-color: #fff59d"><strong">RL로 읽기/쓰기 정책을 학습하는 계열</strong></span>이 같이 있습니다. 이 논문은 그 대신 "읽기/쓰기를 학습하는 게 아니라 <span style="background-color: #fff59d"><strong>메모리 표현 자체를 미분 가능하게</strong></span> 만든다"는 방향을 택했습니다. 어느 쪽이 맞다기보다, 문제를 토큰 공간에서 싸우느냐 잠재 공간으로 옮기느냐의 선택 차이로 읽힙니다. 개인적으로는 어느 쪽이든 결국 증거 결합 문제가 관건이라는 진단이 공유된다는 점이 흥미로웠습니다.

## 자주 묻는 질문

### LGM은 Mem0 같은 기존 메모리 시스템을 바로 대체하나요?

아니요. LGM은 연구 프레임워크이고, 원문 텍스트 메모리를 잠재 표현으로 바꾸는 구조라 기존 시스템과 통합하려면 SAE 학습과 그래프 인코더 추가가 필요합니다. 결론은 "텍스트 리플레이 대신 잠재 공간 정리가 가능하다"는 것입니다.

### 검색(retrieval) 대비 성능 향상 폭은 어느 정도인가요?

논문 기준 Qwen2.5-7B에서 Naive RAG 계열은 평균 50 이하, LGM은 72.28입니다. 다만 벤치마크는 개인화 평가(PersonaMem/PrefEval)이고, 일반 QA에서의 수치는 별도로 확인이 필요합니다.

### 오픈소스로 공개되었나요?

이 글 작성 시점(2026-09-22, v2 기준)에는 논문에 명시된 코드 공개 링크를 확인하지 못했습니다. arXiv 페이지에서 후속 확인이 필요합니다.

## 더 실습해보고 싶은 분들께

에이전트 메모리를 직접 다뤄보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고 자료

- 논문: Disentangling Long-Term Memory via Latent Neuro-Symbolic Reasoning (arXiv 2609.18461, v2 2026-09-18)
- arXiv: https://arxiv.org/abs/2609.18461
- HTML: https://arxiv.org/html/2609.18461v2
