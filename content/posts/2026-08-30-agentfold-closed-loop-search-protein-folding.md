---
title: "AgentFold — 단백질 접힘 모델을 에이전트가 코드로 직접 개선합니다"
date: 2026-08-30T10:00:00+09:00
tags:
  - agent
  - llm
  - protein-folding
  - mcts
  - scientific-ml
draft: false
description: "LLM 멀티 에이전트가 ESMFold 계열 코드베이스를 직접 수정·학습·평가하며 단백질 접힘 예측 모델을 개선한 AgentFold(arXiv:2608.26747) 논문 정리. 5,000 GPU시간, 약 80개 변형 탐색, 최고 lDDT 7.5% 개선 결과와 반복된 설계 패턴을 수치로 정리했습니다."
---

## 결론 먼저

AgentFold는 LLM 멀티 에이전트가 단백질 접힘 예측 모델(ESMFold 기반)의 <span style="background-color: #fff59d"><strong>코드를 직접 고치고, 학습시키고, 평가하는 닫힌 루프</strong></span>를 돌립니다. 약 80개의 코드 변형을 탐색했고, 동일 평가 예산에서 <span style="background-color: #fff59d"><strong>Codex 독립 제안 기준보다 최고 lDDT를 7.5% 더 끌어냈습니다</strong></span>.

- 원문: arXiv:2608.26747 (2026-08-27)
- 코드: https://github.com/lmqfly/AgentFold
- 기준일: 2026-08-30 기준으로 논문 v1 내용 정리

재미있는 지점은 성능 자체보다 증거 쪽입니다. <span style="background-color: #fff59d"><strong>성공/실패 편집을 모두 구조화 메모리에 남긴다</strong></span>는 점, <span style="background-color: #fff59d"><strong>파라미터를 1.1%만 늘리고 로컬 정확도를 개선했다</strong></span>는 점이 하네스 설계에 참고가 됩니다.

## 핵심 수치 요약

| 항목 | 값 |
| --- | --- |
| 기반 모델 | ESMFold 유래 소형 서브스트레이트 (22.61M 파라미터) |
| 코드베이스 규모 | 2,000 LOC 초과 |
| 탐색한 변형 수 | 약 80개 |
| 사용 컴퓨트 | <span style="background-color: #fff59d"><strong>약 5,000 GPU시간</strong></span> |
| LLM 토큰 | <span style="background-color: #fff59d"><strong>약 1억 7천만 토큰</strong></span> |
| 동일 예산 대비 | Codex 제안 대비 최고 lDD트 +7.5%, 랜덤 탐색 대비 우위 |
| 최고 변형 | esmfold_struct_enhanced_v4 (파라미터 22.856M, 약 +1.1%) |

## 시스템 구조와 루프 동작

루프는 이렇게 돌아갑니다.

1. 접힘 모델 동물원과 구조화 메모리에서 증거를 꺼내 가설을 제안합니다.
2. 코드 수정을 구현하고, 실패하면 디버깅합니다.
3. 변형을 학습시키고 구조 지표로 평가합니다.
4. <span style="background-color: #fff59d"><strong>성공과 실패 편집 모두 intervention trace로 저장합니다</strong></span>.
5. MCTS 스타일 트리 컨트롤러가 어느 코드 스냅샷에 컴퓨트를 더 쓸지 정합니다.

각 트리 노드가 곧 <span style="background-color: #fff59d"><strong>"실행 가능한 구현"</strong></span>이라는 점이 핵심이구요. 탐색 대상이 텍스트 가설 대신 코드 스냅샷입니다.

![AgentFold 시스템 개요](/images/2026-08-30-agentfold-closed-loop-search-protein-folding/fig-1-p4.png)

## 결과 상세

CAMEO2022 개발 벤치마크 기준입니다.

| 변형 | NWRS | lDDT 평균/중앙값 | 비고 |
| --- | --- | --- | --- |
| esmfold (베이스) | 0.500 | 0.232/0.220 | 절대값 |
| struct_enhanced_v4 | +0.026 | +0.053/+0.059 | 최고 복합 변형 |
| struct_local_context_v1 | +0.020 | +0.049/+0.044 | 파라미터 +0.015M |
| struct_dist_aware_v1 | +0.018 | +0.027/+0.024 | 전역 지표 유리 |
| struct_enhanced_multiscale_v2 | +0.017 | +0.045/+0.049 | RMSD 대폭 개선 |

해석 포인트 두 가지.

- <span style="background-color: #fff59d"><strong>개선은 로컬 정확도(lDDT, 루프 품질, 콘택트)에 집중되고, 전역 폴드 품질은 "보존" 수준</strong></span>이지 전면 개선은 아닙니다.
- MolProbity(물리적 타당성)는 enhanced_v4에서 <span style="background-color: #fff59d"><strong>-0.157로 가장 크게 줄었습니다</strong></span>.

![대표 변형 성능 비교](/images/2026-08-30-agentfold-closed-loop-search-protein-folding/table-2-p6.png)

로블러스트니스도 확인했습니다. 반복 실행과 Folding Trunk 8블록 설정에서도 우위가 유지됩니다. 1-layer에서 평균 lDDT <span style="background-color: #fff59d"><strong>0.238→0.274, 8블록에서 0.321→0.355</strong></span>예요.

![로버스트니스 검증](/images/2026-08-30-agentfold-closed-loop-search-protein-folding/fig-4-p8.png)

## 반복된 설계 패턴

약 80개 편집의 성공/실패 흔적에서 나온 사후 패턴입니다. 이론 법칙으로 읽으면 안 되고, 이 탐색 트리에서 반복 관찰된 규칙성으로 읽으면 됩니다.

- P1 (Bias before geometry): <span style="background-color: #fff59d"><strong>좌표가 만들어지기 전에 부드러운 학습 가능 prior를 넣으면 안정적으로 개선</strong></span>됩니다.
- P2 (Multiplicative refinement): 게이트로 업데이트 크기를 조절하면 불확실 영역을 감쇠시켜 학습이 안정됩니다.
- P3 (Avoid geometry-to-attention feedback): <span style="background-color: #fff59d"><strong>기하학 정보를 어텐션·프레임 업데이트에 되먹이면 초기 오차가 증폭되어 붕괴가 자주 옵니다</strong></span>.

실패 사례가 선명합니다. frame-v2/v4/v5, diff-geom 같은 변형은 <span style="background-color: #fff59d"><strong>lDDT 0.002~0.004로 완전히 붕괴</strong></span>했구요, 공통점은 <span style="background-color: #fff59d"><strong>구조 정보가 이미 형성된 뒤 직접 기하 교란을 가했다</strong></span>는 겁니다.

![변형 트리와 붕괴 사례](/images/2026-08-30-agentfold-closed-loop-search-protein-folding/fig-3-p7.png)

## 파라미터 이야기

최고 변형이 22.856M 파라미터로 <span style="background-color: #fff59d"><strong>증가분 약 1.1%</strong></span>입니다. 28.46M(#24, #40), 32.49M(#57), 31.03M(#60)짜리 큰 변형들은 소형 고성능 변형을 이기지 못했고, #60은 파라미터가 많아도 붕괴했습니다. 그래서 <span style="background-color: #fff59d"><strong>개선은 편집 위치에서 왔고 용량 증가와는 무관합니다</strong></span>.

## 내 해석 (하네스 관점)

원문 근거와 제 해석을 구분해 정리합니다.

- 원문이 말하는 것: 닫힌 루프 탐색이 독립 제안보다 낫다, 실패 trace도 자산이다.
- 제 해석: 이건 "에이전트가 연구를 한다"는 선언보다, <span style="background-color: #fff59d"><strong>실패를 구조화해서 저장하는 메모리 설계가 실질 이익</strong></span>이라는 증거에 가깝습니다. 코딩 에이전트 하네스에서 성공 건만 남기는 게 관례인데, 실패 intervention을 타입별로 남겨서 후속 제안이 반복 실수를 피하게 한 설계가 그대로 옮겨질 수 있어요.
- 주의할 점: 개선 폭 자체는 로컬 지표 중심이고 전역 폴드는 보존 수준입니다. "에이전트가 AlphaFold를 뛰어넘었다"는 해석은 과합니다.

![목적별 타겟 평가](/images/2026-08-30-agentfold-closed-loop-search-protein-folding/table-3-p7.png)

## FAQ

**AgentFold는 ESMFold 전체를 다시 학습했나요?**
아니요. 반복 학습·평가가 가능한 소형 ESMFold 유래 서브스트레이트(22.61M)를 기반으로, 구조 모듈의 결합 구조는 유지한 채 코드 편집을 탐색했습니다.

**컴퓨트 비용은 얼마나 들었나요?**
약 80개 변형에 약 5,000 GPU시간, 약 1억 7천만 LLM 토큰을 사용했습니다.

**MCTS는 어디에 쓰였나요?**
각 노드가 실행 가능한 코드 스냅샷인 트리 구조 안에서, 접힘 지표와 정규화 탐색 유틸리티로 확장 우선순위를 정해 컴퓨트를 배분했습니다.

**결론만 요약하면?**
같은 평가 예산에서 Codex 독립 제안 대비 최고 lDD트 7.5% 우위, 파라미터 1.1% 추가로 로컬 정확도 개선, 그리고 "초기 학습 prior + 게이트 정제는 안정, 후반 기하 직접 교란은 붕괴"라는 반복 패턴이 핵심입니다.

## 참고 자료

- 원문: AgentFold: Closed-Loop Agentic Search for Protein Folding Model Design, arXiv:2608.26747
- 코드: https://github.com/lmqfly/AgentFold
- 기반 모델: ESMFold (Lin et al., 2022)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
