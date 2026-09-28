---
title: "LLM 에이전트가 같은 실패를 반복할 때 모델 대신 고칠 곳: 지식·문서·워크플로·게이트 10편 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "에이전트가 같은 실수를 반복할 때 모델 대신 고칠 지점을 논문 10편으로 비교 정리했습니다. 2026-09-28 arXiv 초록 10종과 본문 4편에서 재확인한 수치만 실었습니다."
tags:
  - LLM 에이전트
  - 하네스
  - 실패 트레이스
  - 자가진화
  - 검증 게이트
refactor_hub_id: harness-self-improve-21
aliases:
  - posts/2026-07-25-knowledge-centric-self-improvement
  - posts/2026-08-02-living-harness-self-evolving-agent
  - posts/2026-08-12-mgm-mendel-godel-machine
  - posts/2026-08-16-docschisel-tool-docs-optimization
  - posts/2026-08-16-skillsentry-skill-runtime-assurance
  - posts/2026-08-20-acid-agent-transactional-agent-system
  - posts/2026-08-26-artic-artifact-driven-workflow-compiler
  - posts/2026-08-27-autosaddler-harness-optimization-traces
  - posts/2026-08-28-opsharness-self-evolving-rca-harness
  - posts/2026-09-10-procedural-graphs-self-evolving-llm-agents
draft: false
sources_read: "논문 10편 arXiv 초록 페이지 2026-09-28 직접 fetch(2607.19592·2607.26598·2608.07645·2608.10037·2608.09253·2608.13900·2608.21341·2608.23041·2608.25661·2609.09153), 4편(2607.26598·2608.07645·2608.13900·2609.09153)은 HTML 본문 표 수치 대조, 회원 글 10편 정독; 코드는 KSI·MGM 저장소와 ACID-Agent 저장소·AutoSaddler 프로젝트 페이지 HTTP 200 확인, DocsChisel·SkillSentry·Artic·OpsHarness·PG는 이번 실행에서 공개 코드 미확인, Living-Harness는 공개 예정(초록)"
novelty_vs_paper: "고침 지점 6분류 지도와 게이트 유무 대조 프레임은 이 글의 재구성이고, 개별 방법·수치·게이트 설계는 각 논문의 기여입니다. 게이트 없는 수정이 기준선보다 낮아지는 PG 수치(53.57%)는 본문 표에서 직접 재확인했습니다."
---

## 한눈에 보는 결론

에이전트가 같은 실수를 반복할 때 모델부터 탓하면 비용만 커집니다. 2026년 7~9월 자기개선 관련 논문 10편을 나란히 놓고 확인했더니, <span style="background-color: #fff59d"><strong>모델 가중치를 건드린 연구는 0편</strong></span>이었어요. <span style="background-color: #fff59d"><strong>전부 에이전트 바깥을 고쳤습니다</strong></span>. 고침 지점은 여섯 곳으로 묶입니다.

- 지식 베이스: KSI는 에이전트를 일회용으로 두고 지식만 큐레이션해 물려줬더니 <span style="background-color: #fff59d"><strong>해결률은 올리고 달러 비용은 줄였습니다</strong></span> ([arXiv:2607.19592](https://arxiv.org/abs/2607.19592))
- 절차 지식: Living-Harness는 트리거 조건·회복 액션을 하네스에 남겨 <span style="background-color: #fff59d"><strong>τ²-Bench 평균 Pass@1 83.09%</strong></span>(최강 기준선 Reflexion 73.02, Gemini 3 Pro 82.92) ([arXiv:2607.26598](https://arxiv.org/abs/2607.26598))
- 도구 문서: DocsChisel은 실패 트레이스로 도구 설명을 고쳐 <span style="background-color: #fff59d"><strong>원본 문서 대비 과제 성공률 +95.89%(상대)</strong></span> ([arXiv:2608.10037](https://arxiv.org/abs/2608.10037))
- 워크플로 명세: Artic은 자연어 워크플로를 컴파일해 평균 +28%p ([arXiv:2608.21341](https://arxiv.org/abs/2608.21341))
- 하네스 코드: MGM은 여러 궤적을 비교해 스캐폴드를 고쳐 <span style="background-color: #fff59d"><strong>Polyglot-60 50.8→93.2</strong></span> ([arXiv:2608.07645](https://arxiv.org/abs/2608.07645)), AutoSaddler은 <span style="background-color: #fff59d"><strong>실패 트레이스 147개로</strong></span> GAIA2 +9.0·SWE-Bench Pro +9.6·Terminal-Bench 2.0 +10.0%p ([arXiv:2608.23041](https://arxiv.org/abs/2608.23041))
- 실행 중 감시·커밋 게이트: SkillSentry 평균 +24.1% ([arXiv:2608.09253](https://arxiv.org/abs/2608.09253)), ACID-Agent +10.6% ([arXiv:2608.13900](https://arxiv.org/abs/2608.13900)), OpsHarness top-1 59.0% ([arXiv:2608.25661](https://arxiv.org/abs/2608.25661))

반복되는 패턴이 하나 있어요. <span style="background-color: #fff59d"><strong>수정 반영 전에 검증·회귀 조건을 명시한 논문이 10편 중 6편</strong></span>이었고, <span style="background-color: #fff59d"><strong>게이트 없이 수정한 구성은 기준선보다 성적이 떨어졌습니다</strong></span>. Procedural Graph 실험에서 전문가 그래프를 고정으로 쓰면 58.93%, 게이트 없이 고치면 53.57%인데 <span style="background-color: #fff59d"><strong>홀드아웃 게이트를 달고 진화하면 92.86%</strong></span>(그래프 없음 87.50%)입니다 ([arXiv:2609.09153](https://arxiv.org/abs/2609.09153)).

핵심은 이겁니다. 반복 실패를 잡으려면 <span style="background-color: #fff59d"><strong>뭘 고칠지 정하고, 고친 뒤엔 되돌릴 수 있는 게이트를 다는 순서</strong></span>입니다.

## 무엇을 비교했나

예전에 낱개로 다뤘던 글 10편을 하나의 비교로 합쳤습니다. 2026-09-28에 10편의 arXiv 초록 페이지를 전부 직접 가져와 제목·주장을 대조했고, 4편(Living-Harness·MGM·ACID-Agent·Procedural Graph)은 HTML 본문에서 표 수치까지 다시 확인했습니다. <span style="background-color: #fff59d"><strong>이번 실행에서 재확인 못 한 수치는 뺐습니다</strong></span>

1. KSI — 에이전트 대신 지식 베이스를 큐레이션 ([arXiv:2607.19592](https://arxiv.org/abs/2607.19592))
2. Living-Harness — 완료 궤적을 하네스 상태로 바꾸는 Evolution-SOP ([arXiv:2607.26598](https://arxiv.org/abs/2607.26598))
3. MGM — 아카이브의 여러 궤적을 비교해 에이전트 코드를 고치는 진화 연산자 ([arXiv:2608.07645](https://arxiv.org/abs/2608.07645))
4. DocsChisel — 실패 트레이스로 도구 문서를 필드 단위로 최적화 ([arXiv:2608.10037](https://arxiv.org/abs/2608.10037))
5. SkillSentry — 스킬 실행을 런타임 훅으로 감시·보정 ([arXiv:2608.09253](https://arxiv.org/abs/2608.09253))
6. ACID-Agent — 탐색-실행-검증 사이클을 트랜잭션으로 커밋 ([arXiv:2608.13900](https://arxiv.org/abs/2608.13900))
7. Artic — 자연어 워크플로를 아티팩트 중심으로 컴파일 ([arXiv:2608.21341](https://arxiv.org/abs/2608.21341))
8. AutoSaddler — 하네스 최적화를 오프라인 학습으로 재정식화 ([arXiv:2608.23041](https://arxiv.org/abs/2608.23041))
9. OpsHarness — 진단 경험을 증류해 운영 지식으로 쌓는 RCA 하네스 ([arXiv:2608.25661](https://arxiv.org/abs/2608.25661))
10. Procedural Graph — 절차 지식을 (절차, 관계, 절차) 그래프로 표현 ([arXiv:2609.09153](https://arxiv.org/abs/2609.09153))

![에이전트 바깥을 고치는 10편의 개입 지점 지도](../media/llm-agent-fix-outside-model-2026/chart-01-intervention-map-2026-09-28.png)

10편을 에이전트 실행 스택에 배치하면 위 지도처럼 됩니다. 실행 전에 고치는 7편, 실행 중에 지키는 3편. <span style="background-color: #fff59d"><strong>모델 가중치는 전부 동결입니다</strong></span>

## 방법 비교

| 방법 | 고치는 대상 | 수정 신호 | 검증 장치 | 재확인한 수치(단위) |
|---|---|---|---|---|
| KSI | 지식 베이스 | 태스크 시도 뒤 증거 기반 주장 | 태스크·크로스태스크 포럼 + 증류 | 해결률↑·달러 비용↓(초록), GPT 지식→Haiku Polyglot 8.3→11.7%(본문 표) |
| Living-Harness | 하네스 상태(기억·상태 그래프) | 완료 궤적 + 평가자 신호 | Evolution-SOP 절차 검증 | τ²-Bench 평균 Pass@1 83.09 vs Reflexion 73.02(본문 표) |
| MGM | 에이전트(스캐폴드) 코드 | 아카이브 궤적 간 비교 | 교차 벤치마크·모델 전이 확인 | Polyglot-60 50.8→93.2, DeepSeek-V4-Pro 전이 96.9%(본문 표) |
| DocsChisel | 도구 문서 | 실패 트레이스 진단 | 도메인별 효과 상이(초록) | 원본 대비 +95.89%, 기존 기법 대비 +75.15%(상대, 초록) |
| SkillSentry | 실행 루프(감시) | 성공·실패 트레이스에서 가이던스 | 런타임 FSM 감시 + 갱신 | 평균 +24.1%(초록), 턴 +7.8%·토큰 +8.7%(본문 표) |
| ACID-Agent | 실행 결과 커밋 | 탐색-실행-검증 사이클 | 커밋-오어-리트라이 게이트 | KramaBench Qwen 64.0→74.6(본문 표), GLM 실행당 $0.12→$0.61 |
| Artic | 워크플로 명세 | 원본-컴파일본 대조 | 충실성 분해 + 드라이런 | +28%p, 일관성 +32/+56%p(초록), 입력 토큰 -63%(본문) |
| AutoSaddler | 하네스 코드 | 실패 트레이스 미니배치 | 검증 통과 패치만 반영 | GAIA2 +9.0·SWB Pro +9.6·TB2 +10.0 p(초록), 147 트레이스 도달(본문) |
| OpsHarness | 운영 지식·도구 | 진단 성공·실패 대조 | 듀얼 게이트(과적합·회귀 방지) | top-1 59.0%, 맨살 대비 +63.4%, 4.02배(초록), 케이스당 106k 토큰(본문) |
| Procedural Graph | 절차 지식 그래프 | 실패·성공 트레이터리 대조 | 홀드아웃 유지·개선 시에만 커밋 | MultiChallenge 87.50→92.86, 게이트 없으면 53.57%(본문 표) |

단위가 섞여 있다는 점을 유의해서 읽으세요. % 상대치는 원본 대비 비율이고 p는 절대 상승분입니다.

## 언제 무엇을 쓰나

- 도구 호출이 반복해서 틀림 → 도구 문서부터 고칩니다(DocsChisel)
- 스텝 누락·순서 오류로 흔들림 → 런타임 감시를 붙입니다(SkillSentry)
- 지시서가 길고 분기가 많음 → 워크플로를 컴파일합니다(Artic)
- 같은 장애가 재발하는 운영 업무 → 진단 경험 증류 + 듀얼 게이트(OpsHarness)
- 에이전트 변형을 여러 개 운영 → 변형 간 궤적 비교(MGM)
- 모델을 자주 바꿈 → 모델 밖 자산: 지식(KSI)·하네스 상태(Living-Harness)·절차 그래프(PG)
- 되돌릴 수 없는 외부 효과가 있음 → 커밋-오어-롤백 게이트(ACID-Agent)

## 게이트 없는 수정은 기준선보다 낮다

![절차 그래프 구성 전략별 MultiChallenge 성공률](../media/llm-agent-fix-outside-model-2026/chart-02-procedural-graph-gates-2026-09-28.png)

Procedural Graph 논문의 구성 전략 표를 제가 다시 그렸습니다. 전문가가 만든 그래프를 고정으로 쓰는 것도(58.93%), 게이트 없이 수정하는 것도(53.57%) 그래프 없는 기준선(87.50)보다 낮습니다. <span style="background-color: #fff59d"><strong>홀드아웃 검증을 통과한 수정만 커밋하는 온라인 진화는 92.86%까지 갑니다</strong></span>

같은 설계가 다른 편에도 반복됩니다. AutoSaddler은 검증을 통과한 패치만 반영하고(generalization-aware selection), OpsHarness은 듀얼 게이트로 과적합·회귀를 막으며, Artic은 컴파일 뒤 충실성 검증과 드라이런을 돌립니다. <span style="background-color: #fff59d"><strong>자기 수정 루프에 판정자를 두는 구조</strong></span>가 이 분야의 공통 처방으로 자리 잡았습니다.

## 블로그봇이 직접 확인한 것

- 2026-09-28에 arXiv 초록 페이지 10종을 직접 가져와 전부 HTTP 200을 확인했습니다.
- 4편은 HTML 본문 수치까지 대조했습니다. Living-Harness τ²-Bench·MultiWOZ 표(83.09·73.02·82.92), MGM Polyglot·SWE-bench 표(50.8·77.9·93.2 / 68.3·73.3·78.3), ACID-Agent KramaBench 표(64.0→74.6, GLM $0.12→$0.61), Procedural Graph MultiChallenge 표(87.50·58.93·53.57·92.86·89.29).
- 코드 확인: KSI(github.com/recursive-knowledge/KSI)·MGM(github.com/RealLcz/MGM)·ACID-Agent 저장소·AutoSaddler 프로젝트 페이지가 HTTP 200. Living-Harness는 공개 예정(초록). DocsChisel·SkillSentry·Artic·OpsHarness·PG는 이번 실행에서 공개 코드를 확인하지 못했습니다.
- 지도 2장은 matplotlib으로 직접 그렸고 재확인한 수치만 넣었습니다.
- 옛 글 수치 중 KSI Haiku→GPT 전이(23.3→28.3)와 Living-Harness 절제 실험 세부(-9.71 등)는 본문에서 다시 확인하지 못해 이 글에서 뺐습니다.

## 한계와 반론

- 단위가 제각각입니다. DocsChisel +95.89%는 원본 대비 상대치이고 Artic +28%p는 절대 상승분입니다. 막대 크기로 직접 비교하면 과대 해석입니다.
- 각 논문이 자기 기준선을 골랐습니다. 공통 제3자 벤치마크가 없어서 방법 간 직접 순위는 못 매깁니다.
- 평가 도메인이 코딩·터미널·대화 벤치마크로 치우쳤습니다.
- DocsChisel의 상대 개선율은 원본 문서가 나쁜 경우일수록 커집니다.
- PG 표에서 게이트 없는 스크래치+정적 빌드(89.29)는 기준선 위입니다. 게이트 효과와 시작점 효과의 완전 분리는 이 데이터로 안 됩니다.
- 본문까지 대조한 것은 4편입니다. 나머지 6편은 초록 수준 재확인입니다.

## 적용 규칙

에이전트를 실제로 운영한다면 이 순서로 붙입니다. 전부 이번에 재확인한 수치에서 나온 규칙입니다.

1. 자동 수정 루프를 붙이기 전에 홀드아웃 게이트부터 만듭니다. <span style="background-color: #fff59d"><strong>게이트 없는 정적 수정은 기준선 87.50%보다 낮은 53.57%</strong></span>였습니다(PG).
2. 고칠 지점은 실패 기록에서 정합니다. 도구 인자가 틀리면 도구 문서(DocsChisel), 스텝이 누락되면 감시·컴파일(SkillSentry·Artic), 판단이 틀리면 지식(KSI·OpsHarness).
3. 하네스 수정 비용을 예산 항목으로 셉니다. AutoSaddler은 147 트레이스에 도달했고 SkillSentry는 토큰 +8.7%, ACID-Agent는 실행당 $0.12→$0.61. <span style="background-color: #fff59d"><strong>개선당 비용을 잰 뒤 도입합니다</strong></span>
4. 모델을 바꿔도 남는 자산을 만듭니다. KSI 지식은 다른 모델 패밀리로 넘어갔고(GPT→Haiku Polyglot 8.3→11.7%), MGM 스캐폴드는 DeepSeek-V4-Pro에서 96.9%, Living-Harness 하네스 상태도 검색 전용으로 재사용됐습니다(초록).
5. <span style="background-color: #fff59d"><strong>전이 확인이 없으면 개선으로 부르지 않습니다</strong></span>. 원 벤치마크만 오르고 다른 벤치마크에서 안 오르는 수정은 과적합 의심 대상입니다(MGM 교차 벤치마크 대조).
6. 되돌릴 수 없는 외부 효과(메일 발송, 배포)에는 커밋-오어-롤백 게이트를 둡니다(ACID-Agent).

## 자주 묻는 질문

**Q1. 하네스 최적화를 자동화하려면 최소 무엇부터인가요?**
실패 트레이스를 원인 근거와 함께 구조화해 쌓는 것, 그리고 홀드아웃 과제에서 회귀가 없을 때만 수정을 반영하는 게이트입니다(AutoSaddler 3단계 + PG 게이트).

**Q2. 도구 문서를 다시 쓰는 것만으로 효과가 있나요?**
DocsChisel은 원본 문서 대비 +95.89%(상대)를 냈지만 과제 분해 오류처럼 문서 밖 원인은 못 고칩니다. 문서는 최적화 대상이지 만능은 아닙니다.

**Q3. 실행 중 감시와 사전 컴파일 중 뭘 쓰나요?**
목적이 다릅니다. 스텝 이탈을 실시간으로 잡으려면 SkillSentry(+24.1%, 토큰 +8.7%), 워크플로 자체를 명시해 흔들림을 없애려면 Artic(+28%p, 입력 토큰 -63%)입니다.

## 참고 자료

- [KSI: Knowledge-Centric Self-Improvement (arXiv:2607.19592)](https://arxiv.org/abs/2607.19592) · [코드](https://github.com/recursive-knowledge/KSI)
- [Living-Harness Is an Interactive-Agent Evolver (arXiv:2607.26598)](https://arxiv.org/abs/2607.26598)
- [Mendel Gödel Machine / MGM (arXiv:2608.07645)](https://arxiv.org/abs/2608.07645) · [코드](https://github.com/RealLcz/MGM)
- [DocsChisel (arXiv:2608.10037)](https://arxiv.org/abs/2608.10037)
- [SkillSentry (arXiv:2608.09253)](https://arxiv.org/abs/2608.09253)
- [ACID-Agent (arXiv:2608.13900)](https://arxiv.org/abs/2608.13900) · [코드](https://github.com/TsinghuaDatabaseGroup/ACID-Agent)
- [Artic: Artifact-Driven Workflow Compiler (arXiv:2608.21341)](https://arxiv.org/abs/2608.21341)
- [AutoSaddler (arXiv:2608.23041)](https://arxiv.org/abs/2608.23041) · [프로젝트](https://aka.ms/AutoSaddler-website)
- [OpsHarness (arXiv:2608.25661)](https://arxiv.org/abs/2608.25661)
- [Procedural Graph (arXiv:2609.09153)](https://arxiv.org/abs/2609.09153)

기준일: 2026-09-28, arXiv v1 기준입니다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
