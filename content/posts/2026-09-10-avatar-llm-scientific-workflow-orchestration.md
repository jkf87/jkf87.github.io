---
title: "과학 워크플로 오케스트레이션에 LLM을 끼워넣는 안전한 방법 — Avatar 구조"
date: 2026-09-10
tags:
  - LLM
  - agent
  - workflow
  - orchestration
  - HPC
draft: false
description: "오케스트레이터·실행자·모니터 3-액터에 고정 액션 카탈로그를 얹어 규칙 정책과 LLM 정책을 같은 코어에서 돌리는 Avatar를 정리함. LLM 모드에서 계산 낭비 55%, GPU 시간 40% 절감."
---

과학 연구 워크플로는 이미 자동화돼 있는데 그 자동화를 지배하는 규칙은 여전히 사람이 손으로 튜닝한 고정 룰임. 시시각각 변하는 장애와 리소스 상황 앞에서 이 룰은 둔감할 수밖에 없음. UChicago와 Argonne의 Avatar가 이 간극을 메웠음. 원문은 [arXiv 2609.10509](https://arxiv.org/abs/2609.10509).

1. 구조. 오케스트레이터가 의존성과 스케줄을, 실행자가 기동을, provenance 모니터가 관찰과 진단을 맡는 액터 3개 위에 어댑터가 검증하는 단일 액션 카탈로그를 얹음. 각 액터의 결정 정책은 규칙이나 LLM 둘 중 하나로 플러그 가능함. 핵심은 모든 액션이 고정 카탈로그 안에서만 제안된다는 점임. 어댑터가 카탈로그 밖 제안을 거부하니 LLM의 자율성이 액션 공간 차원에서 묶임.

2. 이 설계가 실무적으로 제일 배울 만함. "LLM을 오케스트레이션에 넣으면 위험하다"가 아니라 "액션 카탈로그로 경계를 그리면 안전하게 넣을 수 있다"는 접근임. 내 자동화에도 LLM 결정 단계가 있는데, 허용 액션 목록을 코드가 소유하고 밖의 제안은 거부하는 구조로 되어 있어서 이 논문의 원칙과 같은 방향임. LLM의 자유도를 프롬프트로 조절하는 게 아니라 액션 공간으로 조절하는 것임.

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/gifs/orchestra-conductor.gif)

![Avatar 오케스트레이션 개요](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-1-p3.png)

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/gifs/train-on-tracks.gif)

3. 재현성 검증이 정직함. 규칙 모드 M0는 TaskVine 네이티브와 retry·완료·영구 실패 카운트가 전 구간 정확히 일치했음. 같은 코어가 TaskVine/Parsl/Colmena 세 워크로드에서 카탈로그의 서로 다른 부분만 쓰면서도 바이트 단위로 동일하게 유지됐다는 것도 확인함. 기존 WMS를 대체하는 게 아니라 같은 코어에서 정책만 갈아끼우는 구조라는 뜻임.

![과학 워크플로 구조](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-2-p4.png)

4. 비교 실험은 M0(규칙-규칙), M1(LLM 진단-규칙 행동), M2(LLM-LLM) 세 변형으로 돌림. LLM 평가는 Argonne Sophia의 openai/gpt-oss-20b를 씀.

![실험 결과](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-3-p6.png)

5. 결과. LLM 모드에서 계산 낭비 55% 감소, GPU-busy 시간 40% 감소임. 에이전트가 이긴 조건이 명확함. retry 예산이 크고 실패 확률이 높을 때, 그리고 캠페인을 멈춰야 할 때임. E3 분자 설계에서 M2는 324개 분자 시점에서 캠페인을 중단해 GPU 시간을 40% 줄였음. "해를 찾은 뒤 이어지는 불필요한 평가"를 끊는 중단 판단이 규칙보다 LLM이 나았다는 것임.

![케이스 스터디](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-5-p7.png)

6. 내 해석. 이 논문의 가치는 절감 숫자보다 "정책 교체 가능한 오케스트레이션 코어"라는 아키텍처 패턴임. 규칙의 예측 가능성과 LLM의 적응성을 같은 시스템에서 A/B로 비교할 수 있다는 게 운영 측면에서 제일 큰 이득임. 내 자동화 배치 작업에도 규칙 정책과 LLM 정책을 같은 액션 카탈로그 위에서 전환할 수 있게 두면, LLM 모드가 안정적이라는 게 확인된 구간만 선택적으로 LLM으로 넘길 수 있음.

7. 문제제기. LLM executor 배치는 단일 노드 테스트베드에서 검증하지 못했고 실패 처리도 단순 retry 수준임. 멀티노드 자원 선택과 오류 유형별 복구는 후속 과제로 남아있음. 그리고 3개 워크로드가 전부 과학 계산 영역이라 일반 업무 자동화로의 일반화는 직접 확인해야 함.

8. 결론. LLM 오케스트레이션 도입의 안전한 경로는 "액션 카탈로그 + 어댑터 검증 + 규칙 폴백"임. 자율성을 액션 공간에서 묶어두면 규칙 시스템의 재현성을 유지하면서 적응성만 얻을 수 있음.

오케스트레이션 루프 설계 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 해볼 수 있음.
