---
title: Harness-of-Harness — 코딩 에이전트 하네스를 3중 루프로 감싸니 벤치마크 점수가 최대 82% 올랐습니다
date: 2026-09-02
tags:
  - agent
  - harness
  - coding-agent
  - LLM
  - autonomous-development
  - loop
  - benchmark
draft: false
description: 상하이 AI Lab의 HoH 논문 정리. 코딩 에이전트 하네스를 기획-개발-테스트 루프로 감싸서 3개 벤치마크에서 평균 상대 52.25% 향상, 6일간 70루프로 FPS 게임을 자율 완성한 방법과 수치.
---

## 핵심 요약

2026년 9월 1일 상하이 AI Lab이 낸 논문 Harness-of-Harness(HoH)를 정리했습니다. 하네스를 또다른 하네스로 감싸는 구조인데요, 결과부터 말하면 <span style="background-color: #fff59d"><strong>세 벤치마크에서 평균 상대 향상 52.25%, 최대 82.86%</strong></span>이 나왔고, 같은 구성으로 <span style="background-color: #fff59d"><strong>6일간 70회 넘는 루프로 사람이 플레이 가능한 FPS 게임</strong></span>을 처음부터 완성했습니다.

논문: [arXiv:2609.01481](https://arxiv.org/abs/2609.01481) (Shanghai AI Laboratory, 2026-09-01)
코드: [github.com/Flesymeb/HarnessOfHarness](https://github.com/Flesymeb/HarnessOfHarness)
기준일: 2026-09-02, arXiv v1 기준

핵심 수치를 먼저 표로 정리했습니다.

| 항목 | 내용 |
| --- | --- |
| 프레임워크 | HoH — 기존 하네스 바깥에 3-에이전트 루프 추가 |
| 루프 구성 | Project Planner → Developer → QA Tester, 증거 누적 |
| 벤치마크 | GameCraft-Bench, FrontierSWE, ProgramBench |
| 테스트 구성 | Codex+GPT-5.5(high), OpenCode+DeepSeek-V4-Pro, Pi+MiniMax-M3 |
| 평균 상대 향상 | <span style="background-color: #fff59d"><strong>52.25% (3루프 후, 최대 82.86%)</strong></span> |
| 장기 사례 | 6일 70+ 루프로 FPS 게임 Fusepoint 완성 |

## 문제 정의: 실행 사이의 단절

요즘 코딩 에이전트는 Codex든 Claude Code든 한 번 실행하면 끝입니다. 다음 실행은 이전 실행의 기억을 못 이어받죠. HoH가 노리는 게 이 단절입니다. 사람이 감독하며 돌리는 방식과 자율 개발 방식의 차이는 Figure 2에 잘 나와 있습니다.

![](/images/2026-09-02-harness-of-harness-continual-improvement/fig-2-p3.png)

Figure 2. 사람 감독 개발과 자율 개발의 비교. 자율 개발에서는 관찰·재호출까지 에이전트가 스스로 해야 합니다.

논문이 짚은 문제 세 가지입니다.

- 이전 루프에서 뭘 검증했는지, 뭘 실패했는지가 다음 실행으로 이어지지 않습니다.
- 고수준 스펙만으로는 <span style="background-color: #fff59d"><strong>"다음에 뭘 고쳐야 하는지"가 결정되지 않습니다</strong></span>.
- 시나리오별 동작이라 완성 안 된 아티팩트가 완성된 걸로 받아들여질 수 있습니다.

## 작동 방식: 3-에이전트 루프

HoH의 핵심은 세 역할의 루프입니다. Project Planner가 목표를 정하고, Developer가 구현하고, QA Tester가 독립적으로 평가합니다. 이 사이클이 반복되면서 아티팩트와 "증거(evidence)"가 누적됩니다.

![](/images/2026-09-02-harness-of-harness-continual-improvement/fig-3-p5.png)

Figure 3. HoH 전체 구조. Planner가 PRD와 테스트 증거로 다음 계획을 만들고, Developer가 도구·스킬로 빌드하고, QA Tester가 다차원으로 평가합니다.

핵심 설계 원칙을 꼽으면 이렇습니다.

- 작고 검증 가능한 증분: 한 루프에 목표 하나만 자릅니다.
- 점진적 노출: 도구·스킬·산출물을 루프가 진행되며 조금씩 공개합니다.
- 구현 테스트와 독립 평가를 분리합니다.
- 버전 관리된 이력: 회귀가 생기면 <span style="background-color: #fff59d"><strong>이전 검증 상태로 롤백</strong></span>이 가능합니다.

## 벤치마크 수치

세 가지 하네스-모델 조합에서 Vanilla(단독 하네스)과 HoH@1~3(1~3회 루프)을 비교했습니다. 논문 Table 1 기준입니다.

| 구성 | 지표 | Vanilla | HoH@3 | 증가 |
| --- | --- | --- | --- | --- |
| Codex + GPT-5.5 | GameCraft Overall | 49.58 | 71.52 | +21.93 |
| OpenCode + DeepSeek-V4-Pro | GameCraft Overall | 26.90 | 48.98 | +22.08 |
| Pi + MiniMax-M3 | GameCraft Overall | 42.16 | 58.78 | +16.62 |
| Codex + GPT-5.5 | FrontierSWE Dominance | 44% | 71% | +27pp |
| OpenCode + DeepSeek-V4-Pro | FrontierSWE Dominance | 25% | 44% | +19pp |
| Pi + MiniMax-M3 | FrontierSWE Dominance | 35% | 64% | +29pp |
| Codex + GPT-5.5 | ProgramBench Pass Rate | 60.41 | 66.50 | +6.09 |
| OpenCode + DeepSeek-V4-Pro | ProgramBench Pass Rate | 45.27 | 57.56 | +12.29 |
| Pi + MiniMax-M3 | ProgramBench Pass Rate | 35.83 | 52.68 | +16.85 |

<span style="background-color: #fff59d"><strong>전 구성, 전 태스크 카테고리에서 HoH@3가 Vanilla을 넘었습니다.</strong></span> 시작 성적이 낮은 구성에서도, 높은 구성에서도 다 개선했고, GameCraft-Bench는 HoH@1→@3로 단조 증가했습니다.

![](/images/2026-09-02-harness-of-harness-continual-improvement/fig-4-p12.png)

Figure 4. GameCraft-Bench 4개 평가 축(Mechanics/Content/Functional/Art)별 비교. Codex 구성은 Functional Visuals가 48.67 → 74.23으로 가장 크게 올랐습니다.

### 10루프까지 가면

FrontierSWE에서 Codex 구성을 10루프까지 돌렸습니다. Dominance가 HoH@3의 39.33%에서 <span style="background-color: #fff59d"><strong>HoH@9의 76.00%</strong></span>까지 올라갑니다. Vanilla은 27.33%입니다. 루프를 더 돌릴수록 계속 좋아진다는 게 핵심 관찰입니다.

## 동일 패스 예산 비교(반복 실행 대비)

같은 개발 패스 수에서 HoH와 Vanilla Continuation(같은 세션에서 이어서 돌리기)을 비교한 게 Table 2입니다. GameCraft-Bench, Codex 구성.

| 방법 | 패스 | 점수 | 토큰 (M) |
| --- | --- | --- | --- |
| Vanilla | 1 | 49.58 | 2.59 |
| Vanilla Continuation | 3 | 58.24 | 6.33 |
| HoH | 1 | 59.71 | 2.88 |
| HoH | 2 | 64.84 | 5.67 |
| HoH | 3 | 71.52 | 8.41 |

<span style="background-color: #fff59d"><strong>HoH 2패스(5.67M 토큰)가 Vanilla 3패스(6.33M 토큰)보다 적은 비용으로 더 높은 점수</strong></span>를 냈습니다. 단순 반복이 아니라 루프 구조가 하는 일이 있다는 뜻입니다.

![](/images/2026-09-02-harness-of-harness-continual-improvement/table-2-p12.png)

Table 2. 동일 패스 수 비교 원표.

### 절제 실험에서 뭘 빼면 점수가 떨어지나

GameCraft-Bench(Codex 구성)에서 세 메커니즘을 하나씩 뺀 결과입니다.

| 제거 항목 | 점수 변화 | 토큰 변화 |
| --- | --- | --- |
| 계획 갱신 (Plan Update) | −8.13 | 7.56M |
| 증거 피드백 (Evidence Feedback) | −6.28 | 7.46M |
| 웜스타트 (Warm-Start) | −7.85 | <span style="background-color: #fff59d"><strong>8.41M → 11.12M (+32%)</strong></span> |

세 축 다 유의미하고, 특히 웜스타트가 없으면 이전 구현을 반복 재구축하느라 토큰이 32% 늘어납니다.

## 6일 70루프 FPS 게임 Fusepoint 사례

가장 인상적인 건 열린 설정 실험입니다. 빈 워크스페이스에 PRD(제품 요구사항 문서) 하나만 넣고 자율 개발을 시켰습니다.

![](/images/2026-09-02-harness-of-harness-continual-improvement/fig-1-p1.png)

Figure 1. 6일간 루프에 따른 게임 발전. Day 1 그레이박스부터 최종 Polish까지.

- 결과물: Fusepoint — 5분짜리 1인칭 폭탄 해체 미션 게임
- 요구: 통제 지점 2곳 순차 점령, 최종 목표 3단계 해체, 적 18명 고정 배치
- 산출: 일관된 스토리라인, 전투·무기·적 상호작용, HUD·메뉴, 시네마틱 애니메이션, 통합 오디오까지 갖춘 <span style="background-color: #fff59d"><strong>사람이 플레이 가능한 빌드</strong></span>
- 과정: 매 에이전트 스테이지마다 GitHub에 커밋되어 <span style="background-color: #fff59d"><strong>전체 개발 궤적이 공개 추적 가능</strong></span>

여기서는 HoH에 역할별 도구와 스킬(Godot MCP, 에셋 제너레이터, 이슈 레저 등)을 추가로 붙였습니다. 검증됐던 동작이 나중 변경으로 다시 깨지면 reopened 레코드로 <span style="background-color: #fff59d"><strong>회귀 수리가 명시적 작업</strong></span>이 됩니다.

![](/images/2026-09-02-harness-of-harness-continual-improvement/fig-6-p13.png)

Figure 6. Vanilla과 HoH@3의 최종 게임 프레임 비교. 대표 3개 태스크에서 Overall 점수가 34.05→70.61, 42.63→73.38, 65.52→87.88로 올랐습니다.

## 제 해석과 남는 질문

논문 수치와 제 판단을 나눠 정리했습니다.

- 실질 기여는 <span style="background-color: #fff59d"><strong>실행 간 상태 전달 구조</strong></span>입니다. 에이전트 자체를 개선한 건 아니고, 하네스 수정 없이 바깥 루프만 추가한 게 실용적입니다.
- 동일 패스 예산 비교(Table 2)가 가장 설득력 있는 근거입니다.
- 벤치마크는 3루프, 사례는 70루프입니다. 중간 구간(10~30루프)의 비용-편익은 열린 문제로 보입니다.
- 제한점: 게임 개발 중심 벤치마크 비중이 크고, 일반 소프트웨어·레거시 적용은 future work로 남아 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)』

## 자주 묻는 질문

**Q. HoH는 Codex나 OpenCode 같은 하네스를 직접 수정하나요?**
아니요. 기존 하네스 구현은 그대로 두고, 그 실행을 Planner/Developer/QA 루프로 조직하는 바깥 구조만 추가합니다.

**Q. 그냥 같은 세션으로 여러 번 돌리는 것과 뭐가 다른가요?**
같은 패스 수 비교에서 3패스 기준 HoH 71.52 vs 반복 Vanilla 58.24입니다. 매 루프가 독립 평가를 받고 증거가 다음 계획에 반영됩니다.

**Q. 몇 루프까지 돌려야 하나요?**
벤치마크에서는 3루프에서 이미 최대 +22점이 나왔고, FrontierSWE는 9~10루프까지 상승했습니다. 다만 토큰은 루프마다 누적되니(HoH@3에서 태스크당 8.41M) 목표 점수 대비 비용을 보고 끊는 게 좋습니다.

**Q. 코드는 공개되어 있나요?**
네. [github.com/Flesymeb/HarnessOfHarness](https://github.com/Flesymeb/HarnessOfHarness)에서 확인할 수 있고, FPS 게임 개발 궤적 전체가 커밋 이력으로 공개되어 있습니다.

## 참고 자료

- 논문: [Harness-of-Harness: Multi-Day Autonomous Software Development with Continual Improvement (arXiv:2609.01481)](https://arxiv.org/abs/2609.01481)
- GitHub: [Flesymeb/HarnessOfHarness](https://github.com/Flesymeb/HarnessOfHarness)
- 벤치마크: GameCraft-Bench, FrontierSWE, ProgramBench
