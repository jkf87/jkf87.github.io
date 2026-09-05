---
title: "Terminal-Universe: 에이전트 트라젝토리로부터 실행 환경을 재구성하는 프레임워크 논문 요약"
date: 2026-09-05
tags:
  - agent
  - training-data
  - terminal
  - evaluation
  - fine-tuning
draft: false
description: "arXiv 2609.04148 Terminal-Universe 논문 요약. 트라젝토리 재생과 에이전트 완성으로 37,273개의 태스크-충분 환경을 복원하고 Qwen3.5-27B SFT로 Terminal-Bench 2.1 58.1%를 달성한 방법과 어블레이션을 정리합니다."
---

## 결론 먼저

Terminal-Universe(arXiv 2609.04148v1)는 터미널 에이전트의 기록된 트라젝토리로부터 실행 가능한 학습 환경을 재구성하는 프레임워크입니다. <span style="background-color: #fff59d"><strong>결정론적 재생과 에이전트 완성을 거쳐 공개 트라젝토리에서 태스크-충분 환경 37,273개를 복원</strong></span>했으며, 합성 데이터 32.0k 레코드로 Qwen3.5-27B를 SFT하여 <span style="background-color: #fff59d"><strong>Terminal-Bench 2.1에서 46.2%에서 58.1%로 +11.9pt 향상</strong></span>시켰습니다. 기준일: 2026-09-05, 논문 v1 기준입니다.

| 항목 | 값 |
|---|---|
| 복원된 충분 환경 | 37,273 |
| Full Mixture 학습 데이터 | 32.0k records |
| Terminal-Bench 2.0 | 41.6 → 52.8 |
| Terminal-Bench 2.1 | 46.2 → 58.1 |
| EvoCode-Bench v2 MT@4 / Case | 6.3 → 20.1 / 67.8 → 76.1 |

## 문제 정의

터미널 기반 코드 에이전트의 보급으로 트라젝토리는 대량 축적되어 있으나, 에이전트 후학습(post-training)이 요구하는 것은 재쿼리 가능하고 실행 피드백을 제공하는 환경입니다. 트라젝토리의 tool 실행 기록은 실행 환경의 구조와 내용을 노출하므로, <span style="background-color: #fff59d"><strong>트라젝토리로부터 환경을 재구성할 수 있다</strong></span>는 관찰이 출발점입니다.

![](/images/2026-09-05-terminal-universe/fig-1-p2.png)
*그림 1. Terminal-Universe 전체 구성. 트라젝토리와 환경을 같은 대상의 두 관점으로 보고, 단일 워크스페이스·여러 의존 워크스페이스·여러 사용자 라운드로 확장한다. 출처: arXiv 2609.04148 Figure 1.*

## 프레임워크: 2단계 재구성

재구성은 2단계로 수행됩니다. 1단계 <span style="background-color: #fff59d"><strong>결정론적 재생(deterministic replay)</strong></span>은 트라젝토리에 기록된 파일 연산을 역순 재생하여 에이전트 수정 이전 상태의 파일을 복원합니다. 2단계 <span style="background-color: #fff59d"><strong>에이전트 완성(agentic completion)</strong></span>은 completion 에이전트가 누락된 파일과 의존성을 보충합니다.

재생 직후 워크스페이스 충분률은 Terminal 40.2%, SWE 20.1%이며 <span style="background-color: #fff59d"><strong>완성 후 93.5%, 77.1%로 회복</strong></span>합니다.

![](/images/2026-09-05-terminal-universe/table-2-p7.png)
*표 2. 복원된 인텐트 기준 워크스페이스 충분률. 재생 후 vs 완성 후 비교. 출처: arXiv 2609.04148 Table 2.*

![](/images/2026-09-05-terminal-universe/fig-2-p5.png)
*그림 2. 프레임워크 상세. 재생과 완성, 4가지 재쿼리 변형 구조. 출처: arXiv 2609.04148 Figure 2.*

## 재쿼리 3축

복원된 환경에서는 세 축으로 태스크를 합성합니다. Intent Recovery는 원 인텐트 태스크를 재구성·재해결합니다. <span style="background-color: #fff59d"><strong>Cross-WS(breadth)</strong></span>는 환경 간 방향성 의존 관계를 마이닝하여 복수 코드베이스에 걸친 쿼리를 합성합니다. <span style="background-color: #fff59d"><strong>Multi-Round(depth)</strong></span>는 사용자 에이전트를 통해 반복 요구사항 세션으로 확장합니다.

## 주요 결과

Terminus2-XML 스캐폴드 기준으로 Full Mixture 학습 결과는 Terminal-Bench 2.0 52.8%, 2.1 58.1%입니다. <span style="background-color: #fff59d"><strong>Claude Code 스캐폴드에서도 58.2%(+10.4)로 게인이 유지</strong></span>됩니다. 동일 규모 비교에서 유사 방법들을 상회합니다.

| 모델 | Base | 데이터 | TB2.1 | MT@4 |
|---|---|---|---|---|
| Qwen3.5-27B (base) | – | – | 46.2 | 6.3 |
| TerminalTraj-32B | Qwen2.5-Coder-32B | 50.7k | 28.5 | 0.0 |
| RST-27B | Qwen3.5-27B | 37.5k | 49.4 | – |
| FACET-Terminal-27B | Qwen3.5-27B | 1.2k | 47.6 | – |
| Terminal-Universe-27B | Qwen3.5-27B | 32.0k | 58.1 | 20.1 |

![](/images/2026-09-05-terminal-universe/fig-5-p7.png)
*그림 5. 복원된 터미널 풀의 다양성. Python 84.7%가 주력이고 데이터 처리·DevOps·보안이 기술 도메인의 80% 이상. 출처: arXiv 2609.04148 Figure 5.*

## 어블레이션

- 재해결 vs 원본 SFT(35.8k 동일): <span style="background-color: #fff59d"><strong>52.1 vs 36.7</strong></span> (TB2.1, 두 스캐폴드 평균). 재구성한 환경을 다시 푸는 것이 원본 모방보다 우위입니다.
- 완성 단계 제거: 52.9 → 48.7, 런 간 편차 ±1.4 → ±3.5.
- Verifier 필터: Cross-WS에서 데이터 감소에도 <span style="background-color: #fff59d"><strong>53.2 → 55.4</strong></span>.
- Cross-WS 혼합: 56.4 → 58.4. 티처 pass@1은 72.3% → 49.2%로 하락(난이도 상승).
- Multi-Round: MT@4 18.4 → 21.0, Case 71.9 → 76.9. 라운드별 verifier 제거 시 MT@4 -2.2.
- 예산 배분: <span style="background-color: #fff59d"><strong>환경 확장(53.2 → 56.0)이 쿼리 확장(53.8)·솔루션 확장(53.9)보다 효과적</strong></span>. 환경 하나가 곧 새 실행 컨텍스트입니다.
- 도메인 이전: SWE 저장소 1,900개 중 1,464개 충분, 10.3k 학습으로 TB2.1 평균 47.0 → 50.0.

![](/images/2026-09-05-terminal-universe/fig-3-p6.png)
*그림 3. Multi-Round 세션의 통과/실패 패턴. 출처: arXiv 2609.04148 Figure 3.*

## 한계 (논문 명시)

- 모든 워크스페이스에 <span style="background-color: #fff59d"><strong>표준 Ubuntu 24.04 컨테이너를 사용</strong></span>하여 특수 시스템 의존성이 필요한 사례의 충실도가 제한됩니다.
- 도메인·언어·툴체인 분포는 수집 트라젝토리 커버리지에 종속됩니다.
- <span style="background-color: #fff59d"><strong>태스크·솔루션·verifier를 단일 티처가 생성</strong></span>하므로 티처 오류가 검증을 우회할 수 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)』

## 자주 묻는 질문

**Terminal-Universe의 핵심 기여는 무엇인가요?**
기존 트라젝토리로부터 재생·완성을 통해 재사용 가능한 실행 환경을 복원하고, 그 환경에서 폭·깊이 축으로 태스크를 합성하는 프레임워크입니다.

**재생만으로 환경 복원이 충분한가요?**
불충분합니다. 재생 후 충분률은 Terminal 40.2%이며 완성 후 93.5%입니다.

**학습 데이터 규모와 성능은 어느 정도인가요?**
32.0k 레코드로 Qwen3.5-27B를 SFT하여 Terminal-Bench 2.1 58.1%, EvoCode-Bench v2 MT@4 20.1을 달성했습니다.

**결과가 특정 스캐폴드에만 유효한가요?**
Terminus2-XML과 Claude Code 모두에서 유사한 게인(+11.9 / +10.4)이 확인되었습니다.

**원문은 어디서 확인할 수 있나요?**
[arXiv:2609.04148](https://arxiv.org/abs/2609.04148)에서 확인할 수 있습니다. 기준일 2026-09-05.
