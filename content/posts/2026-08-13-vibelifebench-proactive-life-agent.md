---
title: "VibeLifeBench: Can Your Life Agent Be Proactive and Persistent in a Living World?"
date: 2026-08-13
tags:
  - agent
  - benchmark
  - long-horizon
  - proactivity
  - personal-assistant
  - LLM
  - harness
  - evaluation
  - living-world
  - tool-use
---

## 개요

VibeLifeBench는 일상 생활 보조 에이전트의 능동성(proactivity), 세계 적응성(living-world adaptation), 장기 일관성(long-horizon coherence)을 측정하는 벤치마크입니다. 200개 작업, 10개 일상 도메인, 22개 모의 서비스로 구성되며, 작업당 시뮬레이션 호라이즌 중위값은 29일입니다.

## 배경

기존 에이전트 벤치마크(SWE-bench, WebArena, OSWorld 등)는 단발적이고 명시적인 요청을 정적 환경에서 평가합니다. VibeLifeBench는 세 가지 차원에서 기존 평가 패러다임을 보완합니다:

1. 능동성: 에이전트가 사용자의 프롬프트 없이도 세계 상태를 재확인하고 행동을 결정해야 함
2. 살아있는 세계: 환경이 자체 시계에 따라 진행하며, 날씨/가격/재고/알림이 에이전트 행동과 무관하게 변화
3. 긴 호라이즌: 작업이 수주에 걸쳐 진행되며, 초기 제약이 최종 단계까지 유효

![VibeLifeBench 개요](/images/2026-08-13-vibelifebench-proactive-life-agent/fig-1-p2.png)

## 벤치마크 구성

각 작업은 시뮬레이션된 타임라인으로 구현됩니다. 타임라인은 네 가지 이벤트 유형으로 구성됩니다:

| 이벤트 유형 | 설명 | 에이전트 반응 |
|---|---|---|
| 사용자 메시지 | 에이전트에게 직접 전달되는 요청 | 즉시 응답 |
| 자율 세계 이벤트 | 항공편 지연, 예약 변경 등 — 알림 없이 발생 | 능동적 발견 필요 |
| 푸시 알림 | 에이전트에게 전달되지만 무시 가능 | 판단 필요 |
| 조용한 상태 변화 | 여권 만료, 인슐린 통관, 피싱 이메일 등 | 능동적 발견 필요 |

![서비스 사용 분포](/images/2026-08-13-vibelifebench-proactive-life-agent/fig-2-p7.png)

## 평가 방식

에이전트가 남긴 최종 상태만 읽어서 채점합니다. 세 가지 차원을 평가합니다:

- 종료 상태 (end state): 예약 완료, 문서 제출 등
- 시기적절성 (timeliness): 기한 내 수행 여부
- 암묵적 제약 준수 (implicit constraints): 여권 유효기간, 건강 조건, 예산 한도

![도메인별 구성](/images/2026-08-13-vibelifebench-proactive-life-agent/fig-3-p8.png)

## 결과

7개 최첨단 모델(GPT-5.5, Claude 4.6 Sonnet, Gemini 3 Pro 등)을 평가했습니다. 모든 모델이 낮은 점수를 기록했습니다. 주요 실패 패턴:

- 사용자 명시적 요청만 처리하고 세계 변화를 놓침
- 초기 단계에서 확인한 제약을 후반에 잊음
- 조용한 이벤트(여권 만료 등)를 발견하지 못함
- 행동이 필요 없는 시점에 불필요하게 개입

![모델별 성능](/images/2026-08-13-vibelifebench-proactive-life-agent/fig-4-p11.png)

스테이지별 통과율은 작업 진행이 후반으로 갈수록 급격히 하락합니다. 이는 긴 호라이즌에서의 상태 유지와 계획 일관성이 핵심 병목임을 시사합니다.

![모델별 체크 통과율: 스테이지별, 임계값별 세분화된 평가](/images/2026-08-13-vibelifebench-proactive-life-agent/table-7-p11.png)

## 기여

- 일상 생활 도메인에서 에이전트 능동성·지속성을 평가하는 최초의 벤치마크
- 22개 모의 서비스와 상호작용하는 살아있는 세계 시뮬레이터
- 에이전트 행동이 아닌 최종 상태만 읽는 채점 방식 (fine-grained, weighted checks)
- 현재 최첨단 모델들의 근본적 한계를 체계적으로 입증

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

---

- 원문: [VibeLifeBench: Can Your Life Agent Be Proactive and Persistent in a Living World?](https://arxiv.org/abs/2608.10875)
- 코드/환경: 오픈소스 예정
