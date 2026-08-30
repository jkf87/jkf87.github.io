---
title: "EvoTrainer — 정책과 훈련 하네스를 같이 진화시키는 자율 에이전트 RL"
date: 2026-08-30
tags:
  - agent
  - rl
  - harness
draft: false
description: "arXiv 2606.03108 정리. 자율 학습 루프가 레시피 서치에서 멈추는 이유와, 트레이너 에이전트가 진단 하네스까지 버전 관리하며 SWE-9B 38.16%까지 간 과정을 정리했습니다."
---

## 핵심 요약

EvoTrainer(arXiv 2606.03108, 통이랩·알리바바)은 자율 에이전트 RL에서 개선 대상을 <span style="background-color: #fff59d"><strong>훈련 레시피에서 훈련을 해석하는 진단 하네스 자체로 확장</strong></span>한 프레임워크입니다. 점수는 오르는데 왜 오르는지 설명 못 하는 학습 루프, 바로 그 지점에서 출발합니다.

핵심 수치 (기준일 2026-08-30, Avg@8):

| 항목 | 값 |
|---|---|
| SWE-9B BC% | <span style="background-color: #fff59d"><strong>38.16 (사람 RL 33.77, no-RL 30.19)</strong></span> |
| Math 종합 (n=78) | 79.49 vs 사람 76.60 (p<0.001) |
| Coding Avg@8 | 51.29 vs 50.71 (p=0.142, 유의차 없음) |
| 트레이너 | Claude Sonnet 4.6 |
| SWE GPU시간 | 약 92,800 (사람 약 140,000) |

논문: [arXiv:2606.03108](https://arxiv.org/abs/2606.03108), DOI 10.48550/arXiv.2606.03108

## 레시피 서치의 한계

AutoResearch 류의 자율 실험은 레시피를 바꾸고 스칼라 점수로 비교합니다. 그런데 에이전트 RL의 병목은 계속 옮겨 다닙니다. 보상 희소 → 행동 붕괴 → 평가 아티팩트 → 저정보 롤아웃 그룹 순으로요. 해석 도구가 고정되어 있으면 이 병목 이동을 따라갈 수 없습니다. 그래서 <span style="background-color: #fff59d"><strong>"다음 버전을 해석하는 데 필요한 증거와 절차"도 같이 진화해야 한다</strong></span>가 논문의 전제입니다.

## 공동 진화 구조

![](/images/2026-08-30-evotrainer-co-evolving-policy-training-harness/fig-1-p1.png)

정책 버전과 훈련 하네스, 두 축이 같이 움직입니다.

- 버전은 git 워크트리처럼 분기되어 병렬 학습되고, 촉진·승격·병합은 증거 비교로 결정됩니다. 실패 브랜치도 부정 증거로 보존합니다.
- 하네스는 score / signal / behavior / version 네 계층에서 진단을 재구성하고, 진단 격차가 생기면 지표 확장, 분석기 특화, 절차 개정, 외부 논문 검색으로 갱신됩니다.
- 영속 메모리에 검증된 스킬이 쌓입니다. SWE의 `StdGroupFilter`가 Math·Coding에서 재사용됩니다.
- 사람은 부트스트랩과 게이팅만 담당합니다. 학습 실행과 버전 승격은 <span style="background-color: #fff59d"><strong>사람이 승인하는 하이브리드 구조</strong></span>입니다.

## 주요 결과

![](/images/2026-08-30-evotrainer-co-evolving-policy-training-harness/table-3-p7.png)

![](/images/2026-08-30-evotrainer-co-evolving-policy-training-harness/fig-3-p7.png)

SWE-9B에서 사람 기준을 <span style="background-color: #fff59d"><strong>Δ=+4.39 (95% CI [+2.61, +6.34], p<0.001)</strong></span>로 넘기고, Math도 유의하게 앞섭니다(AIME 2024/2025, CNMO 2024 전부 상회). Coding과 SWE-4B는 통계적으로 구분 안 되는 매칭 수준인데, 논문도 이를 "초월"이 아니라 <span style="background-color: #fff59d"><strong>전문가 수동 튜닝 없이 사람 수준을 재현한 것</strong></span>으로 정직하게 읽습니다. 검증은 태스크 단위 쌍체 부트스트랩(B=10,000) + Wilcoxon.

## 하이라이트 — Git 누수 차단 사건

정리 안 된 SWE-9B 저장소에서 v1이 <span style="background-color: #fff59d"><strong>48.80 BC%</strong></span>를 찍었습니다. 점수만 보면 돌파구입니다. 그런데 하네스 감사가 `git show`/`git log`로 참조 패치를 읽는 걸 잡아냈고, 정리 뒤 실제 점수는 31.04였습니다. 점수 의존 루프였다면 무효 브랜치가 승격됐을 겁니다.

같은 맥락에서 점수만 보던 초기 경로는 v3(33.33)에서 포화됐는데, 더 풍부한 진단·백테스트·하네스 개입을 켜니 <span style="background-color: #fff59d"><strong>36.30(v4) → 38.16(v8)로 +4.83이 추가 확보</strong></span>됩니다.

## 죽은 그룹 구조와 스킬 재사용

![](/images/2026-08-30-evotrainer-co-evolving-policy-training-harness/fig-2-p4.png)

그룹 상대 어드밴티지는 그룹 내 보상 분산이 0이면 학습 신호가 없습니다. v4까지도 약 절반 그룹이 죽어 있었는데, 과거 롤아웃에 0.1 가중 instruction-following 항을 추가해 백테스트하니 <span style="background-color: #fff59d"><strong>죽은 그룹의 45%가 분산을 회복</strong></span>했고 DGR은 55% → 27.5%로 줄었습니다.

StdGroupFilter 스킬은 Coding v9 +1.17, v10 +1.08, Math +0.96을 가져옵니다. 스킬 라이브러리를 빼면 이 후보 경로 자체가 사라지니, <span style="background-color: #fff59d"><strong>메모리가 탐색 공간을 바꾼다는 반증 실험</strong></span>이기도 합니다.

## 도메인마다 남는 레시피가 다르다

- Math: 길이 예산 수정 → 보상 개선 → StdGroupFilter 이전 → Code Interpreter 통합(검증 샘플 약 27%가 도구 호출)
- Coding: 측정 아티팩트(format gate·truncation) 수리 → partial-pass 보존 보상 → Dual-Level Filter
- SWE: 행동 민감 보상 경로(r = 1.0·CR + 0.1·IF + 0.1·SBE + 0.15·ETT)

하나의 보편 템플릿이 아니라 <span style="background-color: #fff59d"><strong>도메인별 병목에 맞춘 개입이 선택됐다</strong></span>는 게 과정 수준 증거입니다.

## 한계와 내 판단

- 컴퓨트 경제학이 주 제약: 버전당 시드 1개, 확률성은 태스크 쌍체 부트스트랩으로 대체 보고
- 트레이너는 장문 추론·문헌 검색이 강한 모델(Claude Sonnet 4.6)이어야 하고, 버전은 도메인당 7~10개 수준
- 내 해석: Meta-Harness·AHE가 추론 시점 하네스라면 이건 <span style="background-color: #fff59d"><strong>훈련 시점 하네스를 진화 대상으로 삼은 첫 사례</strong></span>라는 주장이 실질 기여입니다. 완전 자율은 아니고 사람 게이팅 하이브리드라는 경계 설계를 시스템으로 명문화했다는 점이 읽을 가치가 있습니다

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 트레이너 모델은 무엇인가요?
Claude Sonnet 4.6입니다. 진단·하네스 개정·개입 제안은 자율 실행하되 학습 실행과 승격은 사람이 승인합니다.

### 사람보다 무조건 좋다는 뜻인가요?
아닙니다. SWE-9B와 Math만 통계적으로 유의한 우위이고, SWE-4B와 Coding은 매칭 수준입니다.

### 스킬 라이브러리가 중요한가요?
Coding +1.17, Math +0.96을 가져온 실제 재사용 사례입니다. 제거 시 최종 구성 도달 경로가 사라집니다.

### 컴퓨트는 얼마나 들었나요?
트레이너 토큰 약 4.0×10^8, SWE GPU시간 약 92,800시간으로 사람 기준(약 140,000)보다 1.5배 적게 쓰고 더 높은 점수를 냈습니다.

### 죽은 그룹이란 무엇인가요?
그룹 내 보상 분산이 0에 가까워 그룹 상대 어드밴티지가 학습 신호를 못 만드는 롤아웃 그룹입니다.

## 출처

- [EvoTrainer: Co-Evolving LLM Policies and Training Harnesses for Autonomous Agentic Reinforcement Learning (arXiv:2606.03108)](https://arxiv.org/abs/2606.03108)
- [HTML 전문](https://arxiv.org/html/2606.03108v2)
- 비교 대상: AutoResearch(Karpathy, 2026), RAGEN/RAGEN-2, DAPO, GRPO/GSPO
