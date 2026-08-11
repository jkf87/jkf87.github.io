---
title: "A2E: 에이전트 하네스를 감사하는 엔드투엔드 평가 엔진"
date: 2026-08-12
tags: [agent, harness, LLM, evaluation, benchmark, auditing, tool-use, Shanghai-AI-Lab]
source: arxiv
paper_url: https://arxiv.org/abs/2608.07346
---

같은 모델인데 하네스가 바뀌면 에이전트 성능이 크게 달라집니다. Shanghai AI Lab이 이 간극을 측정하려고 만든 도구가 A²E(Agent Auditing Engine)입니다. 9개 하네스 × 23개 벤치마크 조합을 하나의 파이프라인에서 실행·감사합니다.

실행 과정을 4단계 라이프사이클(추론→도구 사용→최종 답변→운영 품질)로 쪼개서 평가합니다. 정답만 맞췄는지가 아니라 왜 맞췄는지, 왜 틀렸는지를 진단합니다.

![](/images/2026-08-12-a2e-agent-auditing-engine/fig-1-p1.png)

## 3계층 구조

![](/images/2026-08-12-a2e-agent-auditing-engine/fig-2-p4.png)

Task Layer — Agent Task Protocol(ATP)로 벤치마크와 하네스를 분리합니다. 벤치마크 어댑터가 TaskInput을 만들고, 하네스가 AgentRunner로 실행하고, TaskTrace를 반환합니다. m×n 조합을 m+n 어댑터로 커버합니다.

![](/images/2026-08-12-a2e-agent-auditing-engine/fig-4-p7.png)

Monitor Layer — OpenTelemetry 스팬 모델로 에이전트 실행 궤적을 기록합니다. SDK 레이어가 프레임워크별 호출을 잡고, 시맨틱 레이어가 의미를 부여하고, 스팬 레이어가 시간·계층 관계를 저장합니다.

Evaluation Layer — 라이프사이클 정렬 평가. 각 메트릭이 실행 단계와 차원에 등록됩니다.

![](/images/2026-08-12-a2e-agent-auditing-engine/fig-5-p9.png)

Reasoning(Task/Flow/Logical), Action(Tool/Skill/Memory), Final Answer(Correctness/Task Completion), Runtime Quality(Efficiency/Safety) — 4단계입니다.

## 하네스가 성능과 비용을 좌우한다

같은 GLM-5.2 API 모델을 쓰고도 하네스에 따라 성공률 차이가 GDPVal에서 0.20, MMLU-Pro에서 0.30, τ³-bench에서 0.66까지 벌어집니다.

![](/images/2026-08-12-a2e-agent-auditing-engine/fig-6-p12.png)

855개 실행(19개 비샌드박스 벤치마크)을 13개 메트릭으로 읽으면, 정답률(correctness)은 0.568~0.663으로 좁은 반면 토큰 비용은 3.5배 차이가 납니다. Claude-Agent-SDK는 평균 2,063 토큰, smolagents는 7,319 토큰을 씁니다.

같은 모델이라도 하네스 설계(프롬프트 구성, 도구 인터페이스, 컨텍스트 관리, 실행 루프 정책)가 성능과 비용을 결정합니다.

## 벤치마크마다 다른 순위

9개 하네스를 3개 벤치마크(GDPVal, MMLU-Pro, τ³-bench)에서 비교했습니다.

![](/images/2026-08-12-a2e-agent-auditing-engine/fig-7-p12.png)

모든 벤치마크에서 동일하게 우위를 점하는 하네스는 없었습니다. MMLU-Pro에서는 성공률이 비슷해도 토큰 소모가 크게 다르고, τ³-bench에서는 성공률과 토큰 모두 크게 갈립니다.

openai-agents는 traject-bench에서 1.00을 기록하는데 τ-bench에서는 0.20입니다. llama-index는 대화형 벤치마크에서 리드하는데 traject-bench에서는 0.40입니다. 글로벌 랭킹은 의미가 없습니다.

## 같은 모델, 같은 작업, 다른 결과

LangGraph와 CrewAI가 같은 GLM-5.2로 같은 τ³-bench 작업을 수행한 결과입니다.

| | LangGraph | CrewAI |
|---|---|---|
| 정답 | 1.0 | 0.0 |
| 턴 수 | 3 | 5 |
| LLM 호출 | 4 | 9 |
| 토큰 | 10,122 | 96,704 |

LangGraph는 SIM 카드 상태 확인 → 재장착 → 신호 복구 불가 확인 → 계정 수준 진단(요금 미납)으로 이어지는 짧은 경로로 해결합니다. CrewAI는 APN 리셋, 비행기 모드 토글 등 기기 수준 복구만 반복하다가 종료합니다. 9.6배 더 토큰을 쓰고도 원인을 못 찾습니다.

이 차이가 하네스의 프롬프트 구성, 도구 선택 로직, 컨텍스트 축적 방식에서 옵니다.

## 기존 평가의 세 가지 한계

최종 답변 정확도만 보면 실패 원인을 알 수 없습니다. 메트릭 추가가 어렵습니다. 궤적이 개별 JSON 파일로 남아서 재평가·집계가 안 됩니다.

A²E는 궤적·메트릭·평가 결과를 데이터베이스에 저장합니다. 에이전트를 다시 실행할 필요 없이, 새 메트릭을 기존 궤적에 적용할 수 있습니다.

## 규모

23개 벤치마크, 9개 하네스, DeepSeek-V4-Pro(FP4) 단일 모델로 1,035개 실행을 돌렸습니다. 19개 비샌드박스 벤치마크에서 855개 실행, 23개 메트릭으로 19,665개 평가 레코드가 생성됩니다.

샌드박스 벤치마크 4개를 포함하면 agno가 전체 1위(0.68), 비샌드박스만 보면 llama-index가 1위(0.77)입니다. 근데 이 순위는 벤치마크 구성에 따라 쉽게 바뀝니다.

## 남은 과제

프레임워크별 계측 유지 비용이 있습니다. 하네스 인터페이스가 바뀌면 모니터 어댑터도 업데이트해야 합니다. 자동 계측이 생성 매개변수나 호출 경로를 변경할 수 있어 궤적 충실도에 영향을 줄 수 있습니다.

코드는 공개되어 있으며, 벤치마크-하네스 조합을 확장할 수 있는 어댑터 구조로 되어 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
