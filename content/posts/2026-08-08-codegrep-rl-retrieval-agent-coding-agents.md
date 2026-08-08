---
title: "CodeGrep: 코딩 에이전트를 위한 RL 기반 코드 검색 에이전트"
date: 2026-08-08
tags:
  - agent
  - coding-agent
  - reinforcement-learning
  - retrieval
  - SWE-Bench
  - harness
  - LLM
  - tool-use
  - GRPO
  - RL
---

## 개요

CodeGrep은 LLM 코딩 에이전트의 파일 탐색 비용을 절감하기 위해 설계된 14B 검색 에이전트입니다. GRPO 강화학습으로 훈련되어, 다중 턴 grep/glob/read 도구 호출을 수행하고 후보 파일 목록을 반환합니다. SWE-Bench Verified에서 OpenHands 에이전트에 통합 시 라운드 15%, 토큰 19% 절감 및 해결률 +1.2pp 개선을 달성했습니다.

논문: [CodeGrep: An RL-Trained Retrieval Agent for LLM Coding Agents](https://arxiv.org/abs/2608.05886)

## 배경

현대 코딩 에이전트(OpenHands, Claude Code)는 SWE-Bench Verified 이슈 해결 시 상당한 토큰 예산을 파일 탐색에 소모합니다. 30B OpenHands 에이전트 기준 평균 23라운드, 631K 토큰이 소요되며, 이 중 많은 부분이 grep, glob, view_file 호출입니다.

본 연구는 두 가지 가설을 검증합니다:
- H1: 더 나은 파일 검색이 해결률을 향상시키는가
- H2: 동일한 이슈를 더 적은 토큰으로 해결할 수 있는가

## 시스템 구조

![Figure 1: 시스템 개요](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/fig-1-p3.png)

훈련 단계에서는 67K OpenHands 궤적에서 CATM으로 라벨을 마이닝하고 GRPO로 CodeGrep을 훈련합니다. 추론 단계에서는 CodeGrep이 후보 파일을 반환하고, 이를 수정하지 않은 OpenHands 에이전트의 프롬프트에 주입합니다.

## 모델

CodeGrep은 Qwen3-14B-Instruct를 기반으로 하며 세 가지 읽기 전용 도구를 제공합니다.

| 도구 | 기능 |
|---|---|
| grep | 정규식 검색 |
| glob | 경로 패턴 매칭 |
| read | 파일 내용 조회 |

턴당 최대 8개 도구를 병렬 호출하며, 3턴 탐색 + 1턴 답변으로 구성됩니다. 답변은 JSON 스키마로 파일 목록을 반환합니다.

## RL 환경

SWE-Bench Docker 이미지를 사용한 훈련은 디스크 및 시간 비용 측면에서 비현실적입니다 (이미지당 1–3 GB).

![Figure 3: 3계층 RL 환경](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/fig-3-p11.png)

본 연구는 git worktree 기반 샌드박스를 제안합니다. 저장소당 bare clone 한 번, 커밋마다 worktree를 추가하여 롤아웃당 환경 세팅을 밀리초 단위로 단축했습니다. 8×B200 노드 단일 장비에서 훈련이 가능합니다.

## CATM: 훈련 데이터 구성

CATM(Code Agent Trajectory Mining)은 67K OpenHands 궤적에서 행동 기반 라벨을 추출합니다. 패치 파일뿐 아니라 에이전트가 이해를 위해 읽은 파일도 관련 파일로 간주합니다.

![Table 4: CATM vs LRAT 비교](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/table-4-p11.png)

3단계 파이프라인:
1. 파일 읽기 도구 호출 추출
2. LLM judge로 RELEVANT/NOT_RELEVANT 분류
3. 추론 길이 기반 지수 포화 가중치 부여

67,074 궤적에서 31,977개 유효 샘플이 산출되었습니다 (47.7% 유지율).

## 보상 설계

3번의 반복을 통해 보상 함수를 개선했습니다.

![Table 2: 보상 설계 반복 요약](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/table-2-p6.png)

**v1**: Fβ 점수에 도구 호출 페널티를 보상 레이어에서 곱했습니다. 정책 drift가 발생했습니다.

**v2**: 효율 신호를 어드밴티지 레이어로 이동했습니다. KL drift가 0.31에서 0.09로 감소했습니다.

**v3**: 라인 범위 점수를 제거했습니다. 다운스트림 에디터가 라인 범위를 사용하지 않기 때문입니다. 훈련 안정성과 효율이 모두 개선되었습니다.

![Figure 2: 3개 반복의 훈련 곡선](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/fig-2-p6.png)

## 실험 결과

![Table 3: 다운스트림 비교](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/table-3-p6.png)

SWE-Bench Verified 500개 인스턴스 결과:

| 지표 | CodeGrep | 베이스라인 |
|---|---|---|
| 해결률 | 27.0% | 25.8% |
| 라운드 (해결 인스턴스) | -15% | — |
| 토큰 (해결 인스턴스) | -19% | — |

검색기 정밀도에 따른 세 구간이 관찰되었습니다:

| 검색기 | 정밀도 | 다운스트림 효과 |
|---|---|---|
| BM25 | 0.375 | 성능 저하 |
| Jina | 0.445 | 중립 |
| CodeGrep | 0.677 | 효율 개선 |

정밀도 0.677 이상에서 검색이 에이전트 효율에 기여하기 시작합니다.

## 훈련 안정성 분석

![Figure 4: 훈련 안정성 진단](/images/2026-08-08-codegrep-rl-retrieval-agent-coding-agents/fig-4-p14.png)

어드밴티지 레이어에서 효율 신호를 적용할 경우 그룹 내 보상 순위가 보존되며 그라디언트 크기만 조절되어 학습 안정성이 향상됩니다.

## 결론

CodeGrep은 코딩 에이전트의 파일 탐색 병목을 해결하는 14B 검색 에이전트입니다. GRPO 훈련과 보상 설계 개선을 통해 SWE-Bench Verified에서 15-19% 비용 절감을 달성했습니다. 검색 정밀도 임계점의 존재가 확인되었으며, 모델, 훈련 파이프라인, RL 환경, 평가 하네스를 공개합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
