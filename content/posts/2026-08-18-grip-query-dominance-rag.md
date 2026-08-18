---
title: "GRIP: RAG가 검색 문서를 무시하는 원인과 4차원 병목 해결책"
date: 2026-08-18
tags:
  - RAG
  - LLM
  - information-bottleneck
  - hallucination
  - query-dominance
  - grounding
source: https://arxiv.org/abs/2608.16776
---

## 결론 먼저

RAG 시스템이 검색해 온 문서를 사실상 무시하고 모델이 원래 알던 지식으로만 답하는 문제를, 논문은 <span style="background-color: #fff59d"><strong>query dominance(질의 지배)</strong></span>라고 이름 붙였습니다. 원인은 프롬프트에 있지 않고 표현(representation) 구조에 있습니다. 질의가 잠재 공간을 차지해 버려서 증거가 기능적으로 무의미해집니다.

GRIP은 여기에 <span style="background-color: #fff59d"><strong>용량 비대칭</strong></span>을 적용합니다. 질의는 디코더에 전 차원으로 그대로 들어가고, 검색 증거는 <span style="background-color: #fff59d"><strong>4차원 확률적 병목</strong></span>만 통과합니다. 그 결과 다섯 개 추론 벤치마크에서 최고 baseline을 모두 앞질렀고, <span style="background-color: #fff59d"><strong>환각(hallucination)은 73% 감소</strong></span>했습니다.

논문: [GRIP: Grounded Reasoning via Information-Restricted Premises](https://arxiv.org/abs/2608.16776) (2026-08-17)

## 무엇이 고장 나 있는가

RAG는 이론상 P(Y|Q,E), 즉 질의와 증거를 함께 조건으로 답을 만듭니다. 실제 관측은 P(Y|Q)에 가깝습니다. 증거를 바꿔도 출력이 거의 안 바뀌는 거죠.

논문은 이걸 진단 지표로 잡습니다.

| 지표 | 정의 | 의미 |
|---|---|---|
| QL Dependence | I(Q, z_k) 상호정보량 | 증거 표현 z_k가 질의의 복사본이면 높음 |
| Contrastive evidence sensitivity | 정반대 증거를 넣었을 때 출력 변화 | query dominance면 작음 |

기존 RAG 잠재 상태의 QL dependence는 <span style="background-color: #fff59d"><strong>14.8 bits</strong></span>. 증거 채널이 질의 정보로 가득 차 있다는 뜻입니다.

![](/images/2026-08-18-grip-query-dominance-rag/fig-1-p2.png)

위 그림이 핵심 구조입니다. 표준 RAG(A)는 질의와 증거가 같은 잠재 공간에서 섞이고, GRIP(B)은 질의는 bypass로, 증거는 좁은 병목으로 분리합니다.

## GRIP 파이프라인

각 추론 단계는 네 단계로 구성됩니다.

| 단계 | 모듈 | 역할 |
|---|---|---|
| 1. 검색 | dense retriever + 엔트로피 재정렬 | 다음 스텝 예측 엔트로피를 가장 낮추는 문서 선택 |
| 2. 압축 | RoBERTa span 추출기 | 문서를 예측에 필요한 최소 span으로 축소 |
| 3. 검증 | DeBERTa NLI, entailment > 0.75 | 함축되지 않은 span은 폐기 |
| 4. 병목+디코딩 | d_z=4, σ²=1.0 projection + Llama-3 디코더 | 증거는 4차원 노이즈 벡터로만 전달 |

<span style="background-color: #fff59d"><strong>스텝당 전달 용량은 약 2–4 bits</strong></span>입니다. 가우시안 채널 용량 계산 C = (d_z/2)·log(1+P/σ²)에서 나온 값입니다. 질의 경로와 증거 경로의 용량 차이는 약 세 자릿수(1000배)입니다.

왜 이렇게 극단적으로 제한하는가. 용량이 부족하면 질의에서 이미 얻을 수 있는 정보를 복사하는 게 비효율적이 됩니다. 병목은 <span style="background-color: #fff59d"><strong>질의가 못 주는 잔여 정보만 전달</strong></span>하도록 압력을 걸어요.

## 수치

Llama-3-8B 백본, 4×A100 80GB, 20 에포크 학습입니다.

- HotpotQA: 아키텍처 매칭 baseline 대비 <span style="background-color: #fff59d"><strong>+7.2 EM</strong></span> (p<0.01)
- StrategyQA: +4.1 accuracy
- SQuAD 2.0: +3.7 EM (p<0.01)
- 2Wiki, ProofWriter 포함 5개 벤치마크 전부에서 최고 baseline 갱신

환각률 변화가 가장 극적입니다.

| 데이터셋 | baseline → GRIP |
|---|---|
| HotpotQA | 31.7% → <span style="background-color: #fff59d"><strong>8.6%</strong></span> |
| 2Wiki | 31.2% → 9.8% |
| HotpotQA (매칭 컨트롤) | 28.7% → 8.6% |

QL dependence는 <span style="background-color: #fff59d"><strong>14.8 → 0.47 bits, 약 30배 감소</strong></span>했습니다.

## 메커니즘이 맞는지 검증

성능만 오른 걸로는 부족하니, 논문은 세 가지 개입 실험으로 인과를 확인합니다.

1. 병목 제거: QL dependence가 0.47 → 14.20 bits로 복귀, 정확도 -5.3점. 병목이 핵심 부품입니다.
2. z_k 랜덤화: <span style="background-color: #fff59d"><strong>정확도 35.3점 하락</strong></span>. baseline에 같은 개입을 하면 7.5점 하락에 그칩니다. 디코더가 실제로 병목 증거를 쓰고 있다는 증거입니다.
3. 정렬 분석: 병목 출력이 질의 부분공간과의 정렬도 ρ에서 baseline보다 체계적으로 낮음.

![](/images/2026-08-18-grip-query-dominance-rag/fig-3-p6.png)

CDF 그래프에서 GRIP 분포가 모든 구간에서 baseline 아래에 위치합니다. 몇몇 이상치가 아닌 전체 분포의 이동입니다.

## 근데 궁금한 점

스텝별로 추론하면 검증된 span 원문도 컨텍스트에 텍스트로 남습니다. 이러면 병목이 새는 거 아닌가 싶은데, 논문은 두 가지로 답합니다.

- span 원문 경로를 제거하면 오히려 -8.2점. 문장 수준 의미 전달 경로는 의도된 설계입니다.
- 각 스텝에서 디코더는 다음 추론을 먼저 확정하고 그 다음에 span이 컨텍스트에 들어갑니다. 스텝별 증거 신호는 병목이 통제합니다.

환각 측정의 검증기 의존도도 점검했는데, MiniCheck로 재채점하면 원 검증기와 89% 일치(κ=0.77)하고 환각률은 8.6% → 10.1%로 약간 오르나 baseline보다는 여전히 낮습니다.

## 한계

원문이 밝힌 한계입니다. 단일 백본(Llama-3-8B) 검증, QL dependence는 필요조건일 뿐 충분조건은 아님, 정보이론 해석은 메커니즘 수준의 설명이지 형식적 동치가 아님.

내 해석을 하나 덧붙이면, 4 bits라는 극단적 설정이 범용 RAG에 바로 적용될지는 의문입니다. 논문의 작업은 span 추출과 NLI 검증으로 이미 정제된 짧은 증거를 다루기 때문에 가능한 설계고, 수천 토큰 문서를 그대로 넣는 일반 RAG에서는 전처리 단계가 먼저 필요합니다.

## 정리

- RAG의 증거 무시는 본질적으로 <span style="background-color: #fff59d"><strong>용량 배분 문제</strong></span>입니다.
- 증거 채널을 의도적으로 제한하면 모델이 증거를 쓸 수밖에 없게 만들 수 있습니다.
- 결과는 환각 73% 감소, QL dependence 30배 감소, 5개 벤치마크 전면 개선.
- 진단 지표 I(Q; z_k)는 GRIP을 안 써도 <span style="background-color: #fff59d"><strong>내 RAG의 증거 활용도를 점검하는 도구</strong></span>로 쓸 수 있습니다.

## 더 실습해보고 싶은 분들께

검색 증거를 실제로 활용하는 에이전트 루프를 직접 만들어보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

원문: [arXiv:2608.16776](https://arxiv.org/abs/2608.16776)
