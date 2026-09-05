---
title: "Speculative Macro Commit: 도구 에이전트 지연시간을 19% 줄이는 멀티스텝 투기 실행 (arXiv 2609.03236)"
date: 2026-09-05
tags:
  - agent
  - inference
  - latency
  - speculative-execution
  - tool-use
draft: false
description: "SMC는 큰 모델(actor)과 작은 모델(drafter)을 병렬로 돌리고, 드래프터가 미리 실행해둔 반복적 다중 액션 체인을 앵커 검증 한 번으로 커밋해 툴 에이전트 지연시간을 18.59% 줄입니다."
---

## 결론 먼저

<span style="background-color: #fff59d"><strong>SMC는 τ² Telecom(SA 대비 10.23%, 순차 실행 대비 18.59% 절감, 정확도 유지)에서 검증됐습니다.</strong> 핵심 아이디어는 두 가지입니다.

- 작은 드래프터 모델(Qwen3.5-4B)이 격리된 환경 스냅샷에서 미래 액션 체인을 미리 실행한다.
- 큰 액터 모델(Qwen3.5-27B INT4)의 다음 툴 호출이 드래프트 첫 액션과 일치하면, <span style="background-color: #fff59d"><strong>나머지 스텝들을 액터 재검증 없이 통째로 공식 트라젝토리에 커밋한다.</strong></span>

기준일: 2026-09-05 기준, arXiv 2609.03236v1 (USC + Intel Labs, Zeyu Liu, Souvik Kundu, Peter A. Beerel).

## 핵심 요약 표

| 항목 | 값 |
| --- | --- |
| 논문 | Speculative Macro Commit for Faster Tool-Using Agents (arXiv 2609.03236) |
| 액터 / 드래프터 | Qwen3.5-27B INT4 / Qwen3.5-4B, greedy 디코딩 |
| 벤치마크 | τ² Telecom (전체), AppWorld (168 태스크) |
| τ² Telecom | <span style="background-color: #fff59d"><strong>정확도 99.52 유지, 27.60s → 22.47s (-18.59%)</strong></span> |
| vs 단일스텝 투기(SA) | -10.23% 추가 절감 (25.03s → 22.47s) |
| AppWorld | 355.7s → 195.9s (-44.93%), TGC 70/168 → 68/168로 소폭 하락 |
| 커밋 정밀도 | 실제 발동 커밋 158/158 = 100% 아웃컴 보존 (100개 홀드아웃 감사) |
| 코드 | github.com/zeyuliu1037/speculative-macro-commit |

## 배경: 툴 에이전트 지연시간의 구조

툴 에이전트의 wall-clock 지연시간은 모델 추론만으로 설명되지 않습니다. PASTE(인용 문헌)의 측정에 따르면 <span style="background-color: #fff59d"><strong>툴 실행이 총 지연시간의 35~61%</strong></span>를 차지하는 사례가 있습니다. 토큰 단위 speculative decoding은 한 번의 모델 호출 내부만 가속합니다. 액션 단위로 올라와도 기존 SA(Speculative Actions, ICLR 2026)는 인접 한 스텝씩만 재사용합니다. 반복되는 다중 액션 패턴을 메타툴(AWO 방식)로 노출하면, Qwen3.5-27B 같은 오픈 모델은 <span style="background-color: #fff59d"><strong>채굴된 매크로를 거의 선택하지 않는다</strong></span>는 것이 저자들의 실험적 관찰입니다. 논문의 중심 질문은 이것입니다. 모델이 새 메타툴을 선택하도록 만들지 않고, 반복 액션 패턴으로 지연시간을 줄일 수 있는가.

## 방법

### 실행 구조

SMC는 에이전트 익스큐터(툴 루프를 도는 프로그램)에 두 모델을 병렬로 둡니다.

- 액터(actor): 큰 모델. 공식 트라젝토리 H의 다음 툴 호출을 결정.
- 드래프터(drafter): 작은 모델. H로부터 미래 액션 체인 Q=(q1..qD)를 예측하고, 격리된 드래프트 상태에서 미리 실행해 결과까지 확보.

드래프터의 호출은 격리 상태에서 실행되므로 라이브 태스크 상태를 오염시키지 않습니다.

### 매크로 채굴

성공한 학습 트레이스에서 반복 다중 액션 패턴을 뽑고, 사용자 ID·문서 ID·타임스탬프 같은 태스크별 값을 슬롯으로 정규화합니다. 후보마다 샘플링된 상태에서 드래프터가 실제로 그 패턴을 재현하는지 라벨링하고, <span style="background-color: #fff59d">Beta 사후분포 하위 δ-분위수로 보수적 신뢰도를 계산합니다. <strong>n≥nmin이고 p̄≥τ인 후보만 라이브러리에 남깁니다.</strong></span> 채굴은 어디까지나 필터이고, 실제 커밋 여부는 런타임 규칙이 따로 결정합니다.

### 커밋 규칙

런타임 정렬이 매크로의 앞부분 u1..uj를 H의 접미사에, 나머지를 드래프트 체인 접두 q1..qℓ에 대응시킵니다. 액터의 다음 호출이 q1과 일치하면 q1이 앵커가 되고, 커밋은 이렇게 진행됩니다.

1. 앵커 q1은 이미 실행된 결과와 함께 커밋.
2. <span style="background-color: #fff59d"><strong>q2..qℓ는 액터 개별 확인 없이 통째로 커밋 — 이때 ℓ-1개의 액터 호출과 툴 대기를 건너뜁니다.</strong></span>
3. 최소 스킵 깊이 ℓ-1≥Lmin 미달이거나 온라인 체크에 걸리면 앵커만 커밋하고 SA 기준으로 동작.

액터가 q1과 불일치하면 드래프트를 폐기하고 재시작합니다. AppWorld에서는 되돌릴 수 없는/미지의 API를 거부하는 규칙과 포크 가능한 뮤테이션의 라이브 상태 재실행 체크가 추가됩니다.

![Algorithm 1. Speculative Macro Commit executor pseudocode.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/algorithm1-executor.png)

## 결과

τ² Telecom(2,285 태스크)에서 SMC는 <span style="background-color: #fff59d"><strong>모든 태스크에서 순차 기준과 동일한 정합 아웃컴(2,274 정답 / 11 오답)</strong></span>을 냈습니다. SA 대비로는 1개를 회복하고 0개를 잃었습니다.

![Table 1. Full benchmark results.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/table1-main-results.png)

AppWorld는 더 어려운 영역입니다. SA가 이미 40.37%를 절감한 상태에서 SMC는 추가로 7.64%를 줄여 기준 대비 -44.93%(355.7s → 195.9s)에 도달합니다. 대신 TGC가 70/168 → 68/168로 2태스크 하락합니다. 저자들의 분석:

- <span style="background-color: #fff59d"><strong>동일 정확도 슬라이스(143 태스크)에서는 SA 대비 -13.5%</strong></span>, NTC-free 슬라이스(85 태스크)에서는 -10.7%로, 전체 평균 -7.64%보다 큽니다.
- 스킵 밀도는 AppWorld 3.81% vs τ² 3.91%로 비슷합니다. 두 벤치마크 모두 비슷한 양의 스킵이 일어난다는 뜻이고, 아웃컴 변화와 유휴/복구 트라젝토리가 평균을 희석합니다.

![Table 3. AppWorld controlled wall-time slices.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/table3-appworld-slices.png)

![Table 2. Macro-step coverage.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/table2-macro-coverage.png)

### 절제 실험 3가지

#### 인터페이스

채굴 패턴을 등록 메타툴로 노출하면(+1.05%, 정확도 하락) 오히려 느려집니다. 온라인 체크 없이 수동 커밋만 하면 -11.34%까지 빨라지지만 정확도가 99.52% → 96.48%로 무너집니다. <span style="background-color: #fff59d"><strong>숨은 런타임 상태 + 앵커 검증의 조합만이 속도와 정확도를 동시에 잡습니다.</strong></span>

![Table 4. Interface ablation.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/table4-interface-ablation.png)

#### 커밋 정밀도

100개 홀드아웃 τ² 태스크의 단계별 감사에서, 라이브러리 매치만으로는 정밀도가 34.6%에 그칩니다. 드래프터 실행(70.6%) → 앵커 검증(87.9%) → 깊이 가드 Lmin=1(90.4%)을 거치면, 실제 발동한 158개 커밋은 <span style="background-color: #fff59d"><strong>158/158 전부 아웃컴을 보존했습니다.</strong></span>

![Table 5. Commit precision stages.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/table5-commit-precision.png)

#### 임계경로 깊이

커밋을 거의 두 배로 많이 하는 레거시 런타임(히트 6,410, 스킵 10,528)은 오히려 SA보다 1.64% 느립니다. 최종 런타임은 깊이-1 기회 6,281개를 억제하고 임계경로상 충분히 깊은 커밋만 남겨 -10.23%를 달성합니다. <span style="background-color: #fff59d"><strong>유용한 단위는 임계경로의 액터 호출을 실제로 건너뛰는 가드된 커밋입니다.</strong></span>

![Table 6. Raw macro count vs critical-path commits.](/images/2026-09-05-speculative-macro-commit-faster-tool-agents/table6-critical-path.png)

### 내 해석: 어디에 쓸 수 있나

- 적용 조건이 명확합니다. 드래프터가 반복 패턴을 재현할 수 있어야 하고, 앵커 검증·깊이 가드·온라인 체크가 있어야 합니다. 세 가지 중 하나라도 빠지면 Table 4·5에서 보듯 정확도나 속도가 무너집니다.
- 근사 최적화라는 점을 알아야 합니다. SA는 한 스텝 검증으로 무손실을 보장하는 반면, SMC는 스킵한 스텝을 액터가 재검증하지 않습니다. τ²에서는 아웃컴 변화가 없었고 AppWorld에서는 2태스크 하락이 있었습니다. 되돌릴 수 없는 툴이 있는 도메인에서는 AppWorld식 안전 규칙이 필수입니다.
- 하드웨어 코스트가 있습니다. 베이스라인은 GPU 1장, SA/SMC는 액터+액터급 복제본+드래프터로 3장을 씁니다. 대기 시간이 비싸고 GPU가 남는 서빙 환경에 맞는 트레이드오프입니다.
- 원문 근거를 구분해두면, "35~61% 툴 지연"은 SMC 논문이 인용한 PASTE의 측정이고, "Qwen3.5-27B가 채굴 매크로를 거의 선택 안 한다"는 저자들의 자체 관찰입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

Q. SMC는 speculative decoding과 무엇이 다른가요?
speculative decoding은 한 번의 모델 호출 안에서 토큰을 드래프트·검증합니다. SMC는 모델 호출과 툴 실행이 반복되는 에이전트 루프 전체에서, 액션 단위로 여러 스텝을 미리 실행해 커밋합니다.

Q. 정확도 손실이 없나요?
τ² Telecom에서는 순차 기준과 태스크별 아웃컴이 완전히 동일했습니다. AppWorld에서는 태스크 완수가 168개 중 2개 하락했습니다. 근사 최적화이므로 도메인별 안전 체크가 필요합니다.

Q. 왜 채굴한 매크로를 메타툴로 주지 않나요?
실험 결과 오픈 모델이 그런 메타툴을 거의 선택하지 않아 효과가 없었고, 오히려 툴 선택 문제만 늘어 지연시간과 정확도가 모두 나빴기 때문입니다. SMC는 모델이 보는 인터페이스를 그대로 두고 익스큐터가 검증해 커밋합니다.

Q. AppWorld에서 절감이 44.9%나 되는데 왜 SA 대비 추가 이득은 7.6%인가요?
SA가 이미 40.37%를 절감한 상태이고, 남은 이득이 아웃컴 변화·유휴 복구 트라젝토리에 희석되기 때문입니다. 동일 정확도 슬라이스에서는 SA 대비 -13.5%까지 올라갑니다.

Q. 필요한 하드웨어는요?
논문 설정에서 액터(Qwen3.5-27B INT4) 1장, 투기 요청용 액터급 복제본 1장, 드래프터(Qwen3.5-4B) 1장 총 3 GPU입니다.

## 출처

- 논문: [arXiv:2609.03236 — Speculative Macro Commit for Faster Tool-Using Agents](https://arxiv.org/abs/2609.03236)
- 코드: [github.com/zeyuliu1037/speculative-macro-commit](https://github.com/zeyuliu1037/speculative-macro-commit)
- 비교 대상: Speculative Actions (ICLR 2026, OpenReview P0GOk5wslg), AWO (arXiv 2601.22037), PASTE (arXiv 2603.18897), τ²-Bench (arXiv 2506.07982), AppWorld (ACL 2024)
