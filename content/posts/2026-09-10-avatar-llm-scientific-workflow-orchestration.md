---
title: "Avatar: LLM으로 과학 워크플로 오케스트레이션 자동화 (arXiv 2609.10509)"
date: 2026-09-10
tags:
  - LLM
  - agent
  - workflow
  - orchestration
  - HPC
draft: false
description: "UChicago/Argonne의 Avatar는 오케스트레이터·실행자·모니터 3-액터 구조로 기존 WMS 규칙과 LLM 추론을 같은 코어에서 돌리게 만들어, LLM 모드에서 계산 낭비 55%·GPU 사용 시간 40%를 줄였습니다."
---

과학 연구의 워크플로는 이미 자동화되어 있습니다. 그런데 그 자동화를 지배하는 규칙은 여전히 사람이 손으로 튜닝한 고정 룰입니다. 시시각각 변하는 장애와 리소스 상황 앞에서 이 룰은 어딘가 둔감할 수밖에 없죠. 최근 UChicago와 Argonne팀이 이 간극을 메우는 흥미로운 구조를 내놨습니다.

## 결론 먼저

Avatar(arXiv 2609.10509)는 오케스트레이터, 실행자, provenance 모니터라는 액터 3개 위에 어댑터가 검증하는 단일 액션 카탈로그를 얹어, 규칙 기반 정책과 LLM 기반 정책이 같은 코어에서 돌아가게 만듭니다. 결과는 이렇습니다: <span style="background-color: #fff59d"><strong>LLM 모드에서 계산 낭비 55% 감소, GPU-busy 시간 40% 감소</strong></span>. 그리고 <span style="background-color: #fff59d"><strong>규칙 모드는 기존 WMS의 실행을 그대로 재현합니다</strong></span>. 기준일은 2026-09-10, arXiv v1 기준입니다.

| 항목 | 내용 |
|---|---|
| arXiv | 2609.10509 (2026-09-09) |
| 소속 | UChicago, Argonne National Laboratory |
| 구조 | 액터 3개 + 단일 액션 카탈로그 |
| 구현 | Academy 프레임워크 |
| 평가 | TaskVine/Parsl/Colmena 3개 워크로드 |
| LLM | openai/gpt-oss-20b (Argonne Sophia) |
| 수치 | 계산 낭비 55%↓, GPU-busy 40%↓ |

원문: <span style="background-color: #fff59d"><strong>https://arxiv.org/abs/2609.10509</strong></span>

## 시스템 구조

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-1-p3.png)
*Fig. 1: Avatar 아키텍처*

오케스트레이터가 의존성과 스케줄을, 실행자가 기동을, provenance 모니터가 관찰과 진단을 맡습니다. 각 액터의 결정 정책은 <span style="background-color: #fff59d"><strong>규칙이나 LLM 둘 중 하나로 플러그 가능합니다</strong></span>. 핵심은 <span style="background-color: #fff59d"><strong>모든 액션이 고정 카탈로그 안에서만 제안된다는 점</strong></span>입니다. <span style="background-color: #fff59d"><strong>어댑터가 카탈로그 밖 제안을 거부하니 LLM의 자율성이 액션 공간 차원에서 묶입니다</strong></span>. 어댑터가 카탈로그 밖 제안을 거부하니 LLM의 자율성이 액션 공간 차원에서 묶입니다.

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-2-p4.png)
*Fig. 2: 액터·어댑터·액션 카탈로그*

<span style="background-color: #fff59d"><strong>M0(규칙-규칙), M1(LLM 진단-규칙 행동), M2(LLM-LLM)</strong></span> 세 변형으로 비교 실험을 돌립니다.

## 무엇을 보여줬나

규칙 모드 M0는 TaskVine 네이티브와 <span style="background-color: #fff59d"><strong>retry·완료·영구 실패 카운트가 전 구간 정확히 일치했습니다</strong></span>. 같은 코어가 <span style="background-color: #fff59d"><strong>세 워크로드에서 액션 카탈로그의 서로 다른 부분만 쓰면서도 바이트 단위로 동일하게 유지</strong></span>된 점도 확인했습니다.

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-3-p6.png)
*Fig. 3: 재현성 검증*

에이전트가 이긴 조건은 명확했습니다. <span style="background-color: #fff59d"><strong>retry 예산이 크고 실패 확률이 높을 때, 그리고 캠페인을 멈춰야 할 때입니다</strong></span>. E3 분자 설계에서 M2는 <span style="background-color: #fff59d"><strong>324개 분자 시점에서 캠페인을 중단해 GPU 시간을 40% 줄였습니다</strong></span>.

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-5-p7.png)
*Fig. 5: 조건별 낭비 시간 비교*

![](/images/2026-09-10-avatar-llm-scientific-workflow-orchestration/fig-6-p7.png)
*Fig. 6: E2/E3 결과*

## 한계와 전망

<span style="background-color: #fff59d"><strong>LLM executor 배치는 단일 노드 테스트베드에서 검증하지 못했</strong></span>고, 실패 처리도 단순 retry 수준입니다. 실패 처리도 단순 retry 수준입니다. 저자들은 멀티노드 자원 선택과 오류 유형별 복구를 후속으로 남겼습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Avatar에서 LLM이 하는 일이 뭔가요?** M2에서 진단과 오케스트레이터 결정을 맡고, 결정은 고정 액션 카탈로그 안의 제안으로만 나옵니다.

**55% 절감은 어디서 나오나요?** LLM 모드가 규칙 대비 계산 낭비를 줄인 비율로, retry 예산·실패 확률이 높은 조건에서 격차가 커졌습니다.

**기존 WMS를 바꿔야 하나요?** 아니요. `_execute` 인터페이스 하나로 연결되는 참조 구현에 가깝습니다.

**GPU 40% 절감 원리는요?** 해를 찾은 뒤 이어지는 불필요한 평가를 stop-campaign으로 끊어서입니다.

**관련 소스는요?** https://arxiv.org/abs/2609.10509, 평가 LLM은 Argonne Sophia의 openai/gpt-oss-20b입니다.
