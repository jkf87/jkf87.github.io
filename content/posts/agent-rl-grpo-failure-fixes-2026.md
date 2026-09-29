---
title: "에이전트 강화학습(GRPO)이 실패하는 다섯 지점과 논문별 해법: 11편 1차 출처 재검증"
date: 2026-09-29
author: 한준구(코난쌤)
description: "에이전트 강화학습 논문 11편을 1차 출처에서 재검증해 보상 오지정, 정규화 결함, 신호 고갈, 세계 모델 부족, 데이터·환경 품질 다섯 실패 지점으로 정리했습니다. 실패 유형별 해법과 재확인된 수치, 그룹 크기 설계식까지 담았습니다."
tags:
  - 강화학습
  - LLM 에이전트
  - GRPO
  - 보상 설계
  - 벤치마크
refactor_hub_id: agent-rl-02
aliases:
  - posts/2026-07-11-sao-single-rollout-asynchronous-agentic-rl
  - posts/2026-07-27-dark-room-reward-collapse-grpo
  - posts/2026-08-04-tapo-transition-aware-policy-optimization
  - posts/2026-08-16-faraday-replica-ai-scientist-replication
  - posts/2026-09-04-grpo-spurious-advantage-signbalance
  - posts/2026-09-04-rwml-reinforcement-world-model-learning
  - posts/2026-09-06-canopy-outcome-only-rl
  - posts/2026-09-08-tree-grpo-agent-rl
  - posts/2026-09-11-dr-mas-stable-multi-agent-llm-rl
  - posts/2026-09-12-t1-terminal-agent-rl
  - posts/2026-09-15-t1-terminal-agent-rl
  - posts/2026-09-21-ai-coding-agent-rl-environments-codemidas
draft: false
sources_read: "11종(2607.07508·2607.21273·2607.27973·2608.13331·2609.04063·2602.05842·2609.01245·2509.21240·2602.08847·2609.11042·2609.22068) 초록을 2026-09-29에 전수 fetch해 HTTP 200과 제목을 확인했고, 본문 HTML 11종을 텍스트로 내려받아 이 글의 표 수치를 grep 대조했습니다(51.6·52.6·55.95·20.6·2.69·5.6·15.2·41.8·31.6·34·81·112·69·16·19.6·6.9·59.30·39.45·24.90·8.84·56.8·66.2·71.7·73.7·77.9·88.4·93.6·59.1·56.5·43.8·49.4·64.0·14.6·47.2·59.9·100.0·88.9·51.7·98.3·97.3·74.8·27.0·29.8·242·73·60·10.0·21.7·4.5·21.5·63.7·72.2·142·65.9 확인). 코드는 github.com/AlibabaResearch/SignalCoverageRL·github.com/AMAP-ML/Tree-GRPO·github.com/langfengQ/DrMAS·github.com/langfengQ/verl-agent·github.com/RobertWangWang/verl-agent 5곳을 직접 불러 HTTP 200을 확인했습니다. SAO·TAPO·Faraday·SignBalance·RWML·T1·CodeMidas는 공식 코드 저장소를 이번 확인에서 찾지 못해 미확인으로 뒀습니다. 재확인 안 된 수치(Faraday 절대 점수 0.856 등·미학습 68과제, TAPO GiGPO 베이스라인 67.4, T1 롤아웃 취소 48/561, Tree-GRPO GAIA +28%·싱글홉 +1~+9%·2롤아웃 조건, 다크 룸 시드 노이즈 ±8.4pt·커버리지 2배→성공 3배, RWML too-easy 30% 필터, CodeMidas IQR 66~305줄)는 뺐습니다."
novelty_vs_paper: "11편 각각의 알고리즘·벤치마크·수치 기여는 전부 논문 것입니다. 다섯 실패 범주 분류, 증상별 대응 가이드, 2026-09-29 재검증 로그, CANOPY 커버리지 재계산(33.66%·80.63%)과 도표 2장은 블로그봇의 비교 결과입니다."
---

## 한눈에 보는 결론

에이전트 강화학습 연구 11편(2026년 7월~9월 대상)을 1차 출처와 대조하여 실패 요인을 다섯 범주로 정리했습니다. <span style="background-color: #fff59d"><strong>보상 오지정, 정규화 결함, 신호 고갈, 세계 모델 부족, 데이터·환경 품질</strong></span>이 그 범주입니다. 각 범주에 대응하는 해법과 재확인된 수치를 아래에 정리합니다.

| 실패 범주 | 증상 | 확인된 사례와 수치 |
|---|---|---|
| 보상 오지정 | 쉬운 상태 선호, 가짜 어드밴티지 | 다크 룸 0%→51.6%, MATH 유한 답 55.95% |
| 정규화 결함 | NaN, 그래디언트 폭주 | Dr. MAS 수학 +5.6%, 검색 +15.2% |
| 신호 고갈 | 전원 실패 그룹, 학습 정지 | n=8 34% → n=32 81% |
| 세계 모델 부족 | 무효 툴콜 반복 | 무효 행동 59.30→39.45% |
| 데이터·환경 품질 | 같은 알고리즘의 성적 편차 | 데이터 소거 47.2% vs 64.0% |

다섯 범주를 하나씩 짚습니다.

보상 오지정은 학습 신호 자체가 엉뚱한 대상을 강화하는 경우입니다. 다크 룸 분석(2607.21273)은 예측 정확도 보상이 붙은 GRPO 학습이 태스크 성공률 0%로 떨어지는 과정을 보여줬습니다. SignBalance(2609.04063)는 유한한 정답 후보가 많은 태스크에서 추론 없이 맞힌 답까지 강화되는 구조를 측정했습니다.

정규화 결함은 알고리즘 수식의 한 줄이 학습 전체를 죽이는 경우입니다. Dr. MAS(2602.08847)는 역할마다 다른 보상 분포에 하나의 전역 평균·표준편차를 적용하면 그래디언트 노름이 폭주한다는 것을 짚었고, 역할별 정규화로 수학 +5.6%, 검색 +15.2%를 회복했습니다.

신호 고갈은 그룹 전원이 실패해 학습 신호가 0이 되는 경우입니다. CANOPY(2609.01245)는 이 확률을 그룹 크기와 성공 확률로 계산했습니다. Tree-GRPO(2509.21240)는 같은 예산에서 롤아웃을 트리로 묶어 스텝 단위 신호를 추가로 확보했습니다.

세계 모델 부족은 환경을 이해하지 못해 무효 행동이 반복되는 경우입니다. RWML(2602.05842)은 다음 상태 예측만으로 ALFWorld +19.6pt를 얻었고 무효 행동을 59.30%에서 39.45%로 줄였습니다. TAPO(2607.27973)는 전이 예측을 보조 감독으로 넣어 WebShop 성공률을 56.8%에서 66.2%로 올렸습니다.

데이터·환경 품질은 같은 알고리즘 안에서 태스크 풀이 성적을 가르는 경우입니다. T1(2609.11042)의 소거 실험은 같은 예산에서 데이터 풀만 바꿔 47.2%와 64.0%가 갈리는 것을 보여줬습니다. CodeMidas(2609.22068)는 이슈·커밋 없이 코드만으로 태스크와 실행 기반 테스트를 만드는 파이프라인입니다.

## 무엇을 비교했나

2026년 7월부터 9월까지 다룬 에이전트 RL 논문 11종입니다. 초록 11종을 전수 확인하고 본문 표 수치를 grep으로 대조했습니다.

1. [SAO — 단일 롤아웃 비동기 RL (arXiv:2607.07508)](https://arxiv.org/abs/2607.07508)
2. [GRPO 밀집 보상 붕괴 분석 (arXiv:2607.21273)](https://arxiv.org/abs/2607.21273)
3. [TAPO — 전이 인식 정책 최적화 (arXiv:2607.27973)](https://arxiv.org/abs/2607.27973)
4. [Faraday / Replica — 논문 재현 에이전트 (arXiv:2608.13331)](https://arxiv.org/abs/2608.13331)
5. [가짜 어드밴티지와 SignBalance (arXiv:2609.04063)](https://arxiv.org/abs/2609.04063)
6. [RWML — 월드 모델 학습 (arXiv:2602.05842)](https://arxiv.org/abs/2602.05842)
7. [CANOPY — 아웃컴 온리 RL (arXiv:2609.01245)](https://arxiv.org/abs/2609.01245)
8. [Tree-GRPO (arXiv:2509.21240)](https://arxiv.org/abs/2509.21240)
9. [Dr. MAS — 멀티에이전트 안정화 (arXiv:2602.08847)](https://arxiv.org/abs/2602.08847)
10. [T1 — 터미널 에이전트 RL (arXiv:2609.11042)](https://arxiv.org/abs/2609.11042)
11. [CodeMidas — RL 환경 자동 구축 (arXiv:2609.22068)](https://arxiv.org/abs/2609.22068)

## 방법 비교

표를 읽는 기준을 먼저 적습니다. 수치는 각 논문이 측정한 자기 벤치마크 기준이고, 블로그봇이 초록과 본문에서 다시 대조한 값입니다. 벤치마크가 다르므로 행 간 직접 비교는 하지 않습니다.

| 방법 | 겨냥한 문제 | 핵심 아이디어 | 재확인된 수치 | 조건·비용 |
|---|---|---|---|---|
| 다크 룸 분석 (2607.21273) | 밀집 보상 붕괴 | std 정규화와 예측 보상의 상호작용 점검 | 0% → mean-only 51.6%(무신호 52.6%) | Qwen3 1.7B/4B/8B, ALFWorld |
| SignBalance (2609.04063) | 가짜 어드밴티지 | 유한 정답 태스크의 어드밴티지 왜곡 측정 | 유한 답 55.95%, 무추론 득점 20.6% | 객관식·짧은 답 태스크 |
| Dr. MAS (2602.08847) | 멀티에이전트 NaN | 역할별 μ·σ 정규화 | 수학 +5.6%, 검색 +15.2%, 비용 -41.8% | 역할별 보상 분포 차이 |
| CANOPY (2609.01245) | 신호 고갈 | 그룹 커버리지 관리 | n=8 34%, n=32 81% | 롤아웃 예산 트레이드오프 |
| Tree-GRPO (2509.21240) | 스텝 크레딧 부족 | 같은 예산 트리 롤아웃 | +16~+69%, 극저예산 +112%, 예산 1/4 동등 | 멀티홉 태스크 |
| RWML (2602.05842) | 검증기 부재 | 다음 상태 예측 학습 | ALFWorld +19.6pt, 무효 행동 59.30→39.45% | 이진 보상 권장 |
| TAPO (2607.27973) | 스텝 감독 부족 | 전이 예측 보조 감독 | WebShop 56.8→66.2%, GiGPO 71.7%, 7B 66.1→73.7% | GSM8K 59.1→56.5 하락 |
| CodeMidas (2609.22068) | 환경 구축 비용 | 코드 기반 태스크·테스트 생성 | DeepSWE 10.0→21.7%, TB v2.1 63.7→72.2% | 실행 기반 테스트 필요 |
| T1 (2609.11042) | 터미널 에이전트 학습 | 실제 셸 300턴, 검증기 밀집 보상 | 43.8→49.4(SFT)→64.0%(RL +14.6pt) | 하네스 민감(6점+ 차이) |
| SAO (2607.07508) | 동기 롤아웃 비용 | 단일 롤아웃 비동기 학습 | AIME2025 97.3, SWE-Bench 27.0→29.8 | 대형 분산 인프라 |
| Faraday/Replica (2608.13331) | 과제 설계 | 코딩 에이전트 지휘 정책 모델 | 학습 분포 내 73%, 미학습 60% 우위 | 루브릭 판정 의존 |

## 언제 무엇을 쓰나

붕괴 증상에 따라 대응 지점을 정합니다. <span style="background-color: #fff59d"><strong>허니문 후 급락은 보상·정규화부터</strong></span>, NaN은 역할별 정규화, 학습 정지는 그룹 크기, 무효 행동은 상태 예측 보조 신호, 성적 편차는 태스크 풀 순으로 점검합니다.

- 밀집 보상 사용 시 <span style="background-color: #fff59d"><strong>std 정규화를 끄고 비교합니다</strong></span>(다크 룸).
- <span style="background-color: #fff59d"><strong>유한 정답 비율을 먼저 측정합니다</strong></span>(SignBalance).
- 역할별 보상 분포가 다르면 역할별 정규화를 적용합니다(Dr. MAS).
- 하드 태스크는 그룹 크기를 늘립니다(CANOPY).
- 멀티홉 태스크는 <span style="background-color: #fff59d"><strong>트리 롤아웃으로 전환합니다</strong></span>(Tree-GRPO).
- 검증기가 없으면 <span style="background-color: #fff59d"><strong>다음 상태 예측·전이 감독을 검토합니다</strong></span>(RWML, TAPO).
- 코딩 에이전트는 <span style="background-color: #fff59d"><strong>환경·태스크 풀 품질을 먼저 바꿉니다</strong></span>(CodeMidas, T1).

## 블로그봇이 직접 확인한 것

확인 방법은 세 단계입니다. 먼저 초록 페이지를 전수 확인하고, 다음으로 본문 HTML을 내려받아 표 수치를 grep으로 대조하고, 마지막으로 코드 저장소 응답과 공식 수치 재계산을 수행했습니다. 날짜는 2026-09-29입니다.

- <span style="background-color: #fff59d"><strong>초록 11종을 2026-09-29에 전수 fetch해 HTTP 200을 확인했습니다</strong></span>(arXiv 2607.07508, 2607.21273, 2607.27973, 2608.13331, 2609.04063, 2602.05842, 2609.01245, 2509.21240, 2602.08847, 2609.11042, 2609.22068).
- 본문 HTML 11종을 내려받아 표 수치를 grep 대조했습니다. 재확인 안 된 수치는 제외했습니다.
- 저장소 5곳(github.com/AlibabaResearch/SignalCoverageRL, github.com/AMAP-ML/Tree-GRPO, github.com/langfengQ/DrMAS, github.com/langfengQ/verl-agent, github.com/RobertWangWang/verl-agent)을 직접 불러 HTTP 200을 확인했습니다.
- SAO·TAPO·Faraday·SignBalance·RWML·T1·CodeMidas는 이번 확인에서 공식 코드 저장소를 찾지 못했습니다.
- CANOPY 커버리지를 1-(1-0.05)^n으로 <span style="background-color: #fff59d"><strong>재계산해 33.66%(n=8), 80.63%(n=32)을 얻었습니다</strong></span>.

![전원 실패 그룹이 되지 않을 확률](../media/agent-rl-grpo-failure-fixes-2026/chart-01-informative-group-coverage.png)

![T1의 Terminal-Bench 2.1 상승 분해](../media/agent-rl-grpo-failure-fixes-2026/chart-02-t1-terminal-bench-progression.png)

두 그림은 블로그봇이 이번 실행에서 직접 생성했습니다.

## 한계와 반론

- 벤치마크가 달라 표의 수치를 상호 직접 비교할 수 없습니다. WebShop 성공률과 Terminal-Bench 해결률은 다른 척도입니다.
- 본문 확인은 HTML 텍스트 추출 기반이라 표 렌더링이 빠지면 수치가 안 보일 수 있습니다. 이번에도 Faraday 절대 점수처럼 재확인 안 된 값은 제외했습니다.
- 다크 룸 분석은 단일 시드 결과입니다.
- T1의 64.0%는 Terminus-2 하네스 기준이며 <span style="background-color: #fff59d"><strong>같은 모델이 하네스에 따라 6점 이상 달라집니다</strong></span>.
- TAPO는 GSM8K 59.1→56.5 하락을 보입니다.
- 다섯 범주 분류는 블로그봇의 임의 구조입니다.

## 적용 규칙

1. 밀집 보상 + std 정규화 조합부터 의심합니다(<span style="background-color: #fff59d"><strong>0%→51.6%</strong></span>).
2. 유한 정답 비율을 먼저 센다(55.95%).
3. 역할별 정규화로 NaN을 잡습니다(+5.6%, +15.2%).
4. 그룹 크기를 <span style="background-color: #fff59d"><strong>1-(1-p)^n으로 설계합니다</strong></span>(n=32에서 81%).
5. 예산보다 롤아웃 구조를 먼저 바꿉니다(예산 1/4 동등).
6. 검증기가 없으면 상태 예측 보조 신호를 씁니다(+19.6pt). 도메인 외 추론 벤치마크를 함께 기록합니다.
7. 알고리즘 전에 <span style="background-color: #fff59d"><strong>태스크 풀을 점검합니다</strong></span>(47.2% vs 64.0%).
8. 벤치마크 표에는 <span style="background-color: #fff59d"><strong>하네스 조건을 함께 확인합니다</strong></span>(6점 이상 차이).

## 참고 자료

1. [SAO (arXiv:2607.07508)](https://arxiv.org/abs/2607.07508)
2. [Dark Room (arXiv:2607.21273)](https://arxiv.org/abs/2607.21273)
3. [TAPO (arXiv:2607.27973)](https://arxiv.org/abs/2607.27973)
4. [Faraday / Replica (arXiv:2608.13331)](https://arxiv.org/abs/2608.13331)
5. [SignBalance (arXiv:2609.04063)](https://arxiv.org/abs/2609.04063)
6. [RWML (arXiv:2602.05842)](https://arxiv.org/abs/2602.05842)
7. [CANOPY (arXiv:2609.01245)](https://arxiv.org/abs/2609.01245) · [코드](https://github.com/AlibabaResearch/SignalCoverageRL)
8. [Tree-GRPO (arXiv:2509.21240)](https://arxiv.org/abs/2509.21240) · [코드](https://github.com/AMAP-ML/Tree-GRPO)
9. [Dr. MAS (arXiv:2602.08847)](https://arxiv.org/abs/2602.08847) · [코드](https://github.com/langfengQ/DrMAS)
10. [T1 (arXiv:2609.11042)](https://arxiv.org/abs/2609.11042)
11. [CodeMidas (arXiv:2609.22068)](https://arxiv.org/abs/2609.22068)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
