---
title: "SMA: 동결 VLM 그대로 두고, 검증된 공간 경험 카드만 쌓아서 점수 올리기"
date: 2026-08-15
tags:
  - LLM
  - agent
  - memory
  - VLM
  - spatial-reasoning
  - self-evolving
  - benchmark
source: arxiv
source_url: https://arxiv.org/abs/2608.12743
paper_url: https://arxiv.org/abs/2608.12743
---

SMA(Spatial Memory Agent, arXiv:2608.12743) 정리했습니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>VLM 파라미터를 하나도 안 건드리고, 검증된 풀이 경험을 교훈 카드로 쌓은 뒤, 각 카드의 이식 신뢰도(TRS) 순으로 꺼내 쓰는 것만으로 공간 추론 정확도를 올렸습니다</strong></span>.

저장대학(ZJU)·상교대 중심 연구진이 만들었구요, 동결 VLM 4종 × 공간 벤치마크 5개 조합으로 평가했습니다.

핵심 수치부터 보시면 됩니다.

| 항목 | 값 |
| --- | --- |
| 기반 모델 | Qwen3.5-9B / 122B-A10B / 27B / 35B-A3B 전부 동결 |
| 벤치마크 | RoboSpatial · ERQA · Omni3D · SAT · EmbSpatial |
| 매크로 평균 | <span style="background-color: #fff59d"><strong>전 모델 블록 1위 (68.8 / 66.7 / 69.8 / 63.5)</strong></span> |
| Qwen3.6-27B RoboSpatial | <span style="background-color: #fff59d"><strong>54.1 → 68.5 (+14.4pt)</strong></span> |
| 학습 기반 SpatialEvo-7B 대비 | <span style="background-color: #fff59d"><strong>평균 47.1 → 63.5 (+16.4pt)</strong></span> |
| 파인튜닝/파라미터 업데이트 | 없음 |

## 동작 방식: 쓰기 1회, 읽기만 계속

![](/images/2026-08-15-sma-spatial-memory-agent/fig-3-p4.png)

전체 파이프라인은 Figure 3 이 한 장입니다. 단계는 3개입니다.

1. 경험 수집 — 검증 가능한 공간 문제 환경에서 동결 VLM이 문제를 풉니다. 검증기(verifier)가 정답 맞춤 여부로 보상 r을 줍니다.
2. 카드 작성 — 리플렉션 모델이 각 풀이를 메모리 카드로 압축합니다. 카드 하나 = (과제, 요약, 이식 가능한 교훈, 방문 수 n, 누적 보상 c, TRS v). 교훈에는 "이 유형에서 빠지기 쉬운 함정"과 "적용할 체크"가 들어가구요, <span style="background-color: #fff59d"><strong>정답 자체를 카드에 적는 건 금지(anti-leakage)</strong></span>입니다.
3. 읽기 전용 배포 — 배포 단계에서는 메모리 뱅크를 얼립니다. 새 문제가 오면 검색만 해서 프롬프트에 끼워 넣습니다. <span style="background-color: #fff59d"><strong>배포 중 쓰기는 없습니다</strong></span>.

메모리 카드는 JSON 두 필드로 나옵니다. summary는 "어떤 문제, 어떤 성공/실패 패턴이었나"이고, lesson은 "비슷한 문제에서 다시 쓸 수 있는 원칙"입니다. 원본 출력이나 정답을 그대로 저장하지 않습니다.

## 검색 구조: 유사도 필터 후 TRS 재랭킹

검색은 2단계입니다.

- 1단계 — 의미 유사도 필터. 과제 임베딩 코사인 유사도가 임계 δ 이하인 카드를 버립니다.
- 2단계 — 남은 카드를 유사도와 TRS를 z-정규화해서 섞은 점수로 재랭킹합니다. <span style="background-color: #fff59d"><strong>S = (1-η)·z(유사도) + η·z(TRS)</strong></span>. 상위 k장을 프롬프트 앞에 붙입니다.

왜 유사도만으로 안 되냐면, 표면적으로 비슷한 문제가 실제로는 다른 절차를 요구하는 경우가 많아서입니다. 논문 측정으로는 <span style="background-color: #fff59d"><strong>SMA가 평균 유사도를 0.792 → 0.698으로 낮추면서도 정확도를 66.8% → 69.8%로 올렸습니다</strong></span>. 가장 가까운 기억이 최선의 기억은 아닙니다.

## TRS 갱신 규칙: 방문 증거 기반 캘리브레이션

TRS(Transfer Reliability Score)가 이 논문의 차별점입니다. 초기값은 전 카드 동일(v₀)로 시작합니다. 카드를 만든 풀이가 맞았는지와 무관하게요.

카드가 검색되어 쓰일 때마다 방문 수와 누적 보상을 갱신합니다.

```
n ← n + 1
c ← c + r        # r ∈ [0,1] 현재 문제의 검증 보상
v ← (λ·v₀ + c) / (λ + n)
```

즉 TRS는 "이 카드를 꽂아줬을 때 실제로 정답률이 올라간 비율"의 추정치구요, 방문 수가 적은 카드는 초기값으로 회귀시킵니다(λ가 그 강도). 검증 결과, <span style="background-color: #fff59d"><strong>TRS 구간별 배포 정확도가 [0.2, 0.3)에서 19.3%, [0.9, 1.0]에서 97.3%</strong></span>입니다. 점수가 실제 이식 품질과 정렬되어 있습니다.

## 주요 결과: 4개 모델 블록 전부 1위

![](/images/2026-08-15-sma-spatial-memory-agent/table-1-p6.png)

Table 1 요약입니다.

- Qwen3.5-122B-A10B: 평균 65.3 → 68.8
- Qwen3.6-35B-A3B: 61.6 → 66.7 (RAG 63.3, MemP 63.7, MemRL-R 63.8 제침)
- Qwen3.6-27B: 63.3 → 69.8 (가장 큰 폭)
- Qwen3.5-9B: 60.6 → 63.5

베이스라인은 No memory / RAG / MemP / MemRL-R / MemRL-GT 5종입니다. RAG는 오히려 122B와 9B에서 성적을 깎는 경우도 있었구요, SMA는 4개 블록 전부에서 최고 평균을 냈습니다.

![](/images/2026-08-15-sma-spatial-memory-agent/table-3-p8.png)

파인튜닝 기반 자기진화(SpatialEvo-7B)와 붙인 Table 3에서는 <span style="background-color: #fff59d"><strong>평균 47.1 vs 63.5로 +16.4pt</strong></span> 차이입니다. SAT에서 +23.6pt까지 벌어졌습니다. 학습 없이 경험 축적만 하는 쪽이 이 설정에선 이겼습니다.

## 절제 실험 결과 (Qwen3.6-27B + RoboSpatial)

| 변형 | 정확도 | 손실 |
| --- | --- | --- |
| SMA 전체 | 68.5 | — |
| − 시맨틱 필터 | 62.7 | <span style="background-color: #fff59d"><strong>−5.8</strong></span> |
| − 보상만 보는 리플렉션 | 63.0 | −5.5 |
| − 원본 모델 출력 추가 | 64.1 | −4.4 |
| − 이식 교훈(lesson) | 65.0 | −3.5 |
| − 요약(summary) | 65.3 | −3.2 |

하이퍼파라미터는 <span style="background-color: #fff59d"><strong>η=0.5, k=3</strong></span>에서 피크입니다.

![](/images/2026-08-15-sma-spatial-memory-agent/fig-4-p8.png)

읽을 점 두 개입니다.

- 유사도 필터를 빼면 가장 크게 무너집니다(−5.8). 걸러주지 않은 기억이 노이즈가 됩니다.
- 리플렉션에 정답(검증 결과)을 알려주는 게 보상만 주는 것보다 5.5pt 낫습니다. 반성 재료로 "왜 틀렸나"가 필요하다는 뜻입니다.

## 메모리 작성 프로토콜: One-Pass vs Continual

메모리를 매 패스마다 계속 쓰면(Continual) 읽을 것 같지만, 실제로는 중복 카드만 늘어납니다. 10패스 비교에서 <span style="background-color: #fff59d"><strong>One-Pass 작성이 카드 수 1/10, 중복률 −21%, TRS 갱신 커버리지 약 2배</strong></span>였습니다. 쓰기를 줄여야 신뢰도 갱신이 카드에 몰아서 들어갑니다.

## 이식성: 모델·벤치마크 간 전이 결과

- 모델 이식: 122B에서 쌓은 기억 뱅크를 27B에 이식해도 <span style="background-color: #fff59d"><strong>RoboSpatial +9.4pt</strong></span>, SAT +5.7pt.
- 벤치마크 이식: EmbSpatial에서 쌓은 카드를 RoboSpatial에 써도 +7.3pt.

기억이 특정 모델·벤치마크에 묶이지 않습니다. 카드가 절차 수준으로 추상화되어 있어서입니다.

## 어떤 분들이 볼 만한가

- 동결 모델로 에이전트를 운영하면서 파인튜닝 예산이 없는 팀 — 검증 가능한 작업 도메인이면 바로 벤치마킹해볼 구조입니다.
- RAG 도입했는데 "비슷한 사례 붙였더니 오히려 성적이 내려가는" 경험 있는 분 — <span style="background-color: #fff59d"><strong>유사도 재랭킹에 신뢰도 항을 섞는 설계</strong></span>가 답이 될 수 있습니다.
- VLM 공간 추론 평가 담당 — RoboSpatial·ERQA·Omni3D·SAT·EmbSpatial 5종 슬라이스 구성과 baseline 재현 세팅이 정리되어 있습니다.

한계도 명확합니다. <span style="background-color: #fff59d"><strong>검증기가 있는(정답 확인 가능한) 환경에서만 경험 수집이 됩니다</strong></span>. 과제 임베딩을 text-embedding-3-large로 뽑는 외부 의존이 있구요, 배포 중 새 경험 축적은 설계상 막아둔 상태입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

원문: [Spatial Memory Agent: Experience-Grounded Procedure Memory for Spatial Intelligence (arXiv:2608.12743)](https://arxiv.org/abs/2608.12743)
