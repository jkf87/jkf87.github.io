---
title: "에이전트 점수는 하네스가 만든다 — AgentCompass가 증명한 평가 인프라의 힘"
date: 2026-07-19
tags:
  - agent
  - evaluation
  - benchmark
  - harness
  - LLM
description: 벤치마크·하네스·환경을 3축으로 분리한 AgentCompass. 같은 모델도 하네스에 따라 점수가 요동친다는 걸 데이터로 보여주며, 에이전트 평가 설계의 기준을 제시함.
aliases:
  - /agentcompass
draft: true
refactor_hub: harness-self-improve-12
refactor_status: queued
---

에이전트 벤치마크 점수를 볼 때마다 드는 의심 하나. "이 점수, 모델 실력인가 하네스(에이전트를 실제로 돌리는 실행틀 — 프롬프트·도구·루프 설계 전체) 실력인가." AgentCompass(모델·하네스·실행 환경을 분리해 에이전트를 평가하는 통합 인프라)가 그 의심을 데이터로 확인해 줬음. 같은 모델인데 하네스를 바꾸면 점수가 유의미하게 움직임.

![](/images/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure/gifs/suspicious-sus-cat.gif)

1. 배경. 각 벤치마크가 자체 실행 환경·데이터 포맷·평가 스크립트를 갖고 있어서 새 벤치마크 추가마다 파이프라인을 처음부터 다시 짜야 했음. 재현성은 무너지고 중복 개발 비용만 쌓임. 나도 에이전트 실험 돌릴 때마다 평가 스크립트를 새로 만드는 게 제일 귀찮았던 부분이라 이 문제가 바로 와닿았음.

2. AgentCompass(OpenCompass 팀, PJLab)의 조치는 구조적 분리임. 평가를 Benchmark·Harness·Environment 세 컴포넌트로 쪼갬. 벤치마크는 데이터를 TaskSpec으로 정규화하고 채점 방식(결정적 매칭·실행 검증·LLM-as-judge, 즉 GPT 같은 모델이 답을 읽고 점수를 매기는 방식)을 고르는 역할, 하네스는 LLM을 대화형 에이전트로 만들어주는 래퍼, 환경은 실행 컨텍스트와 격리 경계임.

![Benchmark·Harness·Environment 3축 분리 구조](/images/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure/x1.png)

3. 이 분리의 실용적 효과. 벤치마크 코드를 수정하지 않고 새 하네스를 끼울 수 있음. Claude Code·Codex 같은 상용 도구와 OpenHands·Mini-SWE-agent 같은 오픈소스 프레임워크를 같은 인터페이스로 돌릴 수 있고, 환경만 로컬→Docker→클러스터로 바꿔서 스케일 테스트도 됨. 나한테는 "모델 비교를 하려면 하네스를 고정해야 한다"는 작업 원칙을 준 도구임.

4. 런타임 설계도 실무 맞춤임. asyncio 기반 비동기 디스패처로 궤적을 병렬 처리하고 부분 결과를 증분 저장해서 중단 후 재개가 됨. 에이전트 태스크 하나가 수십 분 걸리고 API 호출이 중간에 죽는 게 일상이라, 재개 가능성은 필수인데 이걸 기본으로 깔았음.

5. 궤적 분석이 진짜 자산임. 추론 과정·도구 호출·환경 피드백·토큰 소비·지연 시간이 구조화되어 기록되고, 플러거블 분석기가 출력 잘림·지연 스파이크·반복 생성 루프·리워드 해킹(점수만 올리도록 평가 기준의 허점을 이용하는 행동) 패턴을 자동 플래깅함. 실제로 특정 모델이 평가 기준 허점을 이용해 고득점한 패턴을 궤적 분석으로 잡아냈음. 스칼라 메트릭만 봤으면 영영 몰랐을 것임.

6. 규모. 5개 역량 차원(도구 사용·웹 리서치·과학 추론·에이전트 코딩·생산성)에 걸쳐 벤치마크 20개 이상을 기본 지원함. SkillsBench·GAIA(웹 검색·파일 조작 등을 섞은 범용 어시스턴트 과제 벤치마크)·SWE-bench-Pro·Aider 등이 포함됨.

7. 핵심 발견은 하네스 효과임. Qwen3.5-397B, GPT-5.5, Claude-Opus-4.8 등 7개 모델로 8개 벤치마크를 돌렸더니 같은 모델이라도 하네스에 따라 점수가 크게 요동침. SkillsBench에서 OpenClaw와 OpenHands 하네스 사이, SWE-bench 변형에서 Mini-SWE-agent와 OpenHands 사이에 유의미한 차이가 났음. 그래서 "어떤 하네스로 측정했는가"를 명시하지 않은 에이전트 점수는 비교 대상 자체가 안 됨.

![하네스별 점수 요동 예시](/images/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure/x3.png)

![](/images/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure/gifs/confused-bewildered.gif)

8. 그래서 내 평가 워크플로우에 붙인 규칙 세 가지. 첫째, 모델 비교 시 하네스와 환경을 고정하고 선언적으로 기록함. 둘째, 점수와 함께 궤적을 남겨서 실패 모드를 진단 가능하게 함. 궤적은 진단뿐 아니라 학습 데이터 구축에도 재활용됨. 셋째, "코드 공개"와 "재현 가능"은 다른 문제라서 선언적 RunRequest 같은 구조로 실행 자체를 명세화함.

9. 문제제기. 3축 분리가 만능은 아님. 하네스별 특성(프롬프트 포맷, 상태 관리 방식)이 성능에 섞여 들어가는 걸 완전히 통제하진 못함. 그리고 벤치마크 20개를 돌리는 비용 자체가 만만치 않아서 전수 평가는 연구소가 아니면 어려움. 내 용도는 필요한 3-4개 벤치마크 + 하네스 고정 비교가 현실적임.

10. 결론. 평가 인프라도 아키텍처임. 점수만 보지 말고 그 점수를 만든 하네스와 환경을 함께 봐야 함. 코드는 [open-compass/AgentCompass](https://github.com/open-compass/AgentCompass)에서 확인 가능함.

에이전트 하네스 설계를 직접 실습하며 이런 평가 고민을 겪어보고 싶다면 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』가 출발점으로 좋음.
