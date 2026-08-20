---
title: "골 드리프트는 두 개였다 — 커밋먼트 드리프트와 바인딩 드리프트를 분리 측정한 구조"
date: 2026-08-20
tags:
  - agent
  - harness
  - evaluation
  - paper-review
draft: false
---

## 결론 먼저

장기 실행 에이전트가 목표에서 벗어나는 <span style="background-color: #fff59d"><strong>"골 드리프트"는 최소 두 개의 서로 다른 실패로 쪼개야 한다</strong></span>는 논문(arXiv:2608.04066)을 읽었습니다. 핵심은 이겁니다.

- 커밋먼트 드리프트(commitment drift): <span style="background-color: #fff59d"><strong>목표가 아예 나중 컨텍스트에서 사라지는 실패</strong></span>. 외부 커밋먼트 스토어가 수리 담당.
- 바인딩 드리프트(binding drift): <span style="background-color: #fff59d"><strong>목표와 대상 사이의 연결이 어텐션에서만 유지되다 끊어지는 실패</strong></span>. 위치 기반 수리가 담당.
- 두 수리를 독립 스위치로 끄고 측정한 결과: <span style="background-color: #fff59d"><strong>커밋먼트 스토어만 제거하면 골 어밴던먼트가 0.00에서 1.00으로 가고, 바인딩 에러는 0.00 그대로</strong></span>입니다. 반대로 바인딩 조인을 꺼도 per-beat 드리프트는 전혀 변하지 않습니다.

<span style="background-color: #fff59d"><strong>검증 방법 자체가 논문의 주 기여</strong></span>입니다. 그리고 <span style="background-color: #fff59d"><strong>태스크 성과는 0</strong></span>이라고 저자가 스스로 먼저 밝힙니다. 이 부분부터 정리했습니다.

원문: [The LLM Proposes, the Executive Disposes](https://arxiv.org/abs/2608.04066) (Mohsen Arjmandi, 2026-08-04, 개인 연구자)

## 무엇을 측정했나

<span style="background-color: #fff59d"><strong>ARC-AGI-3 인터랙티브 게임에서 52개 실행, 약 1,700만 토큰, 액션 200–400개짜리 호라이즌</strong></span>으로 돌렸습니다. <span style="background-color: #fff59d"><strong>모든 수치는 유효성 게이트를 통과한 실행</strong></span>에서 나왔습니다.

드리프트 측정은 <span style="background-color: #fff59d"><strong>셔도우 레퍼런스</strong></span>라는 장치 위에 정의됩니다. 실험 셀에서 실제 플랜이 없어도, 전체 시스템이 세웠을 플랜을 렌더·실행 없이 컴파일해서 기준 비트로 삼는 겁니다. <span style="background-color: #fff59d"><strong>바이트 동일성 테스트로 이 섀도우가 행동에 새지 않는다</strong></span>는 것도 확인했습니다.

각 기준 비트는 세 가지로 채점됩니다.

| 채점 | 의미 |
|---|---|
| bind | 플랜의 액션은 썼는데 대상이 플랜의 타깃이 아님 |
| aligned | 라이브 스텝을 충실히 수행 |
| abandon | 플랜의 액션도, 타깃도 아님 |

## 메인 결과: 커밋먼트 제거 실험

한 게임에서 셀당 3시드, 전 셀 유효입니다.

![Table 1: 커밋먼트 어블레이션 결과](/images/2026-08-20-commitment-vs-binding-drift/table1-commitment-ablation.png)

Table 1 출처: 논문 §4.1 (arXiv:2608.04066)

- FULL과 J0(조인 제거)는 <span style="background-color: #fff59d"><strong>어밴던먼트 0.00</strong></span>을 유지합니다.
- A0(커밋먼트 스토어 제거)만 <span style="background-color: #fff59d"><strong>어밴던먼트 1.00. 최대 394개의 기준 비트</strong></span>에 대해 사실상 매 비트마다 자기 플랜을 버립니다.
- 바인딩 에러는 <span style="background-color: #fff59d"><strong>어느 셀에서도 0.00</strong></span>.

## 바인딩 제거는 드리프트에 안 나온다

예상과 다르게, 조인(J)을 꺼도 per-beat 바인딩 드리프트가 오르지 않습니다. 두 번째 게임(타깃 액션 비중 높음)에서 짝은 비교로 확인했습니다.

![Table 2: 바인딩 조인 어블레이션 짝은 비교](/images/2026-08-20-commitment-vs-binding-drift/table2-binding-paired.png)

Table 2 출처: 논문 §4.2 (arXiv:2608.04066)

이유는 구조입니다. <span style="background-color: #fff59d"><strong>조준, 컨테인먼트 체크, 영수증 귀속이 전부 코드(Executive) 소유</strong></span>이라서, 착지는 좌표 기하로 결정되고 잘못된 착지는 믿음 상태를 오염시키기 전에 잡힙니다. <span style="background-color: #fff59d"><strong>바인딩 실패 클래스가 "구조적으로 흡수"</strong></span>된 겁니다.

근데 흔적이 아예 없진 않습니다. 효과 연결 가설 형성률을 보면 FULL 3/3 = J0 3/3 > A0 2/3 > J0A0 0/4. 두 메커니즘을 다 끄면 드리프트 이전 단계, 가설 형성 자체가 바닥나서 더블킬 셀은 측정 정의가 없습니다.

## 검증이 구조인 아키텍처

이 논문의 에이전트는 이렇게 돌아갑니다.

- LLM은 Observer, Surveyor, Actuator 세 "기관"으로만 참여하고, <span style="background-color: #fff59d"><strong>타입 제안(typed proposal)만 제출</strong></span>할 수 있습니다.
- <span style="background-color: #fff59d"><strong>결정론적 Executive(diff, matcher, validator, compiler, renderer, test-evaluator)이 모든 상태 전이를 소유</strong></span>합니다.
- <span style="background-color: #fff59d"><strong>주장은 행동 전에 로그로 사전 등록된 예측이 코드로 관측과 대조될 때만</strong></span> 상태에 들어갑니다.
- <span style="background-color: #fff59d"><strong>"LLM이 done이라고 말하는 것은 이벤트가 아니다"</strong></span> — 달성은 로그된 이벤트 위의 서술형 술어입니다.

측정 자체도 자기 검증합니다. 기관별 쓰기 에러율 0.25 초과, 렌더 크기 한도 초과, 솔티드 카나리 에코율 미달이면 <span style="background-color: #fff59d"><strong>그 실행은 무효화</strong></span>됩니다. <span style="background-color: #fff59d"><strong>초반 아키텍처 실행 8개 중 4개가 이 바닥에서 무효화</strong></span>됐고, 각각 실제 결함을 특정했다고 합니다.

컴퓨트 패리티도 적습니다. <span style="background-color: #fff59d"><strong>풀 시스템은 bare backbone 대비 콜 비율 0.15, 토큰 비율 0.38</strong></span>. 추가 추론으로 설명할 수 없다는 근거입니다.

## 성과는 0이라는 공개

<span style="background-color: #fff59d"><strong>52개 실행 전체에서 레벨 완수 0, 점수 0</strong></span>입니다. 저자는 이걸 예외가 아니라 <span style="background-color: #fff59d"><strong>사전 등록된 구조적 결패자(structural defeater)로 명시</strong></span>하고, 효능 주장을 전면 포기합니다. 관찰된 행동은 "자기 지식 결핍을 인식하고 표적 가설을 제출하는 규율 있는 실험자"라고 묘사합니다. 런당 400액션에서 잘못된 이론 약 3개를 영수증과 함께 강등했다고 합니다.

작은 모델 결과도 흥미롭습니다. <span style="background-color: #fff59d"><strong>Haiku급 백본이 쓰기 에러율 0.0으로 전체 루프를 유효하게 돌렸습니다</strong></span>(가설 2개 → 마일스톤 2개 → 조준 실험 비트 448개). 초기 쓰기 에러율 0.55–0.71이었는데, <span style="background-color: #fff59d"><strong>계약에 파오퍼레이션 예시를 넣는 레버 하나로 0.333을 거쳐 0.0까지</strong></span> 떨어졌습니다. 모델 벽이 아니라 계약 문제였다는 얘기구요.

## 정리

- "골 드리프트"라는 집계 점수를 먼저 쪼개고 나서 수리를 설계해야 합니다. 논문의 표현대로 <span style="background-color: #fff59d"><strong>검증은 나중에 붙이는 게 아니라 에이전트에 심어 넣는 속성</strong></span>입니다.
- 커밋먼트는 외부 스토어 + 코드 실행이, 바인딩은 코드 소유 조준으로 각각 수리됩니다. 서로 다른 실패, 서로 다른 수리.
- 태스크 성과 0을 먼저 공개하고도 메커니즘 주장이 성립하는 구조 — 이게 이 논문이 에이전트 평가 방법론에 남기는 지점입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
