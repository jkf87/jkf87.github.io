---
title: HarnessEvo 하니스 최적화 이득의 위치와 예산 분할 함정
date: 2026-09-06
tags: [agent, harness, prompt-engineering, credit-assignment, LLM]
draft: false
description: 얼어붙은 LLM 에이전트의 하니스를 4개 슬롯으로 분해해 크레딧을 측정한 arXiv 2609.02889 정리. 이득은 reflection/control 슬롯에 국한됐고 균등 예산 분할은 최적화를 정지시킵니다.
---

기준일: 2026-09-06 기준, 논문 v1. 원문: [arXiv 2609.02889](https://arxiv.org/abs/2609.02889) (Nguyen et al., 2026)

## 결론 먼저

이 논문은 얼어붙은 LLM 에이전트의 하니스를 4개 슬롯으로 분해하고, 슬롯별 크레딧을 leave-one-in / leave-one-out로 측정했습니다. 결과:

- ALFWorld(얼어붙은 7B 백본) 전체 성공률은 기준선과 동점입니다. HarnessEvo 0.657 vs 스톡 0.642 vs 플랫 문자열 진화 0.642 (McNemar p=0.617, p=0.480, 모두 ns).
- 근데 슬롯별 측정에서는 이득 전부가 reflection/control 슬롯 하나에 국한됩니다. leave-one-in 이득 <span style="background-color: #fff59d"><strong>+0.119 (p=0.0046, 불일치 태스크 22 vs 6)</strong></span>. role, task-strategy, format 슬롯은 개별적으로 널.
- 예산 64 rollouts를 4슬롯에 균등 분할하면 슬롯당 16이 되어 <span style="background-color: #fff59d"><strong>수용-재점수 바닥(accept-and-rescore floor) 미달</strong></span>, 전 슬롯이 빈 시드에서 정지합니다. 저자들은 이걸 예산 분할 함정(budget-splitting trap)이라고 명명했습니다.
- 예산을 고신용 슬롯에 집중하면 이득이 회복됩니다. 단일 슬롯 LOI(B/2=32)가 <span style="background-color: #fff59d"><strong>0.761 (+0.119, p=0.0046)</strong></span>, all-to-control(64)은 0.724 (+0.082, p=0.0725, 경계선).
- WebShop은 진짜 널입니다. 전 예산을 control에 투입해도 0.535 vs 0.518 (+0.017, p=0.36, ns).

정리했습니다: 하니스 최적화를 시작하기 전에 크레딧 할당을 먼저 하면 됩니다.

| 항목 | 값 |
| --- | --- |
| 논문 | arXiv 2609.02889 (2026, v1, CC BY 4.0) |
| 방법 | HarnessEvo (4슬롯 분해 + LOI/LOO 크레딧 측정) |
| 환경 | ALFWorld, WebShop |
| 백본 | 얼어붙은 7B 모델 |
| 전체 성공률 (ALFWorld) | 0.657 vs 0.642 vs 0.642 (ns) |
| control 슬롯 LOI 이득 | +0.119 (p=0.0046) |
| 예산 집중 후 | 0.761 (B/2=32 단일 슬롯) |
| WebShop dense | 0.535 vs 0.518 (p=0.36, ns) |
| 예산 | B64 (검증 팔 B120) |

## 하니스를 4개 슬롯으로 분해한 구조

![Figure 1: 슬롯별 이득 분포 — 이득이 reflection/control 슬롯에 집중](/images/2026-09-06-harnessevo-slot-credit-assignment/fig-1-p2.png)

기존 반성적 프롬프트 진화(GEPA 계열)는 하니스를 하나의 플랫 문자열로 취급합니다. HarnessEvo는 의미 범위가 겹치지 않게 4개로 분해합니다.

- c1 role/persona: 에이전트가 누구인지, 신중함·체계성 같은 태도. 액션 템플릿이나 정지 규칙 없음.
- c2 task-strategy: 작업 분해와 풀이 순서라는 상위 접근.
- c3 tool/format-rules: 액션 템플릿과 출력 형식의 하드 규칙. 복사해 바로 쓸 수 있는 수준.
- c4 reflection/control: <span style="background-color: #fff59d"><strong>루프 규율과 자기교정 규칙 (실패한 액션 반복 금지, 종료 전 검증, 되돌림 조건)</strong></span>. 페르소나·전략 없음.

동일한 반성 최적화기가 슬롯별로 튜닝하고, LOI/LOO 프로토콜이 홀드아웃 이득을 슬롯에 귀속시킵니다.

![Figure 2: HarnessEvo 아키텍처 — 4개 명명 슬롯과 반성 최적화 루프](/images/2026-09-06-harnessevo-slot-credit-assignment/fig-2-p9.png)

## 본 실험: 전체 성공률은 동점

iso-budget B64 설정에서 전체 방법은 동점입니다. 저자들은 이 방법을 <span style="background-color: #fff59d"><strong>현미경</strong></span>이라고 부릅니다. 전체 지표가 동점이어도 슬롯 단위로 들여다보면 구조가 보입니다.

## 크레딧 할당: 이득은 control 슬롯에 집중

![Figure 3: 슬롯별 크레딧 지도 — control만 유의미, 나머지는 널](/images/2026-09-06-harnessevo-slot-credit-assignment/fig-3-p13.png)

leave-one-in 측정에서 control 슬롯만 +0.119 이득을 냅니다. 나머지 슬롯은 개별 기여가 전부 널입니다.

전체 방법이 캡처한 이득은 +0.015인데 슬롯 합은 +0.164. 강한 차감 효과(sub-additivity)가 나옵니다.

## 예산 분할 함정의 메커니즘

![Figure 4: 예산 배분 비교 — 균등 분할 대비 집중 배분](/images/2026-09-06-harnessevo-slot-credit-assignment/fig-4-p15.png)

왜 이런 일이 생기는지 저자들은 최적화기 구조에서 설명합니다. 반성 최적화기의 각 반복은 부모/자식 미니배치 비교(2×minibatch rollouts)를 치르고, 수용 시에만 전체 검증 세트 재점수(|V|≈10)를 추가로 지불합니다. 즉 <span style="background-color: #fff59d"><strong>돌연변이 하나를 받아들이려면 최소 16 rollouts 수준의 고정 비용</strong></span>이 듭니다.

64를 4슬롯에 균등 분할하면 슬롯당 16. 바닥과 맞먹는 수준이라 어떤 돌연변이도 수용하지 못하고, 전 슬롯이 빈 시드에서 얼어붙어 하니스가 스톡과 바이트 단위로 동일해집니다. 저자들은 함정의 원인을 하니스 대신 최적화기에서 찾습니다. 균등 분할이 최적화기의 작동점 아래로 예산을 희석시킨다는 설명입니다.

처방은 명확합니다. 균등 분할 대신 고신용 슬롯에 집중하세요.

| 실행 | 예산 | ALFWorld 성공률 | 비고 |
| --- | --- | --- | --- |
| 균등 4분할 | 64 (슬롯당 16) | 전 슬롯 얼어붙음 | 스톡과 동일 |
| 단일 슬롯 LOI | 32 (B/2) | 0.761 (+0.119) | p=0.0046 |
| all-to-control | 64 | 0.724 (+0.082) | p=0.0725, 경계선 |
| B120 검증 팔 | 120 | 방향 유지 | 부록 Table 6 |

## WebShop 널은 태스크 의존성

WebShop에서는 전 슬롯이 빈 채로 정지하고 모든 방법이 동점입니다. "이것도 예산 아사 아니냐"는 반론을 저자들이 직접 확인했습니다. 전 예산을 control 슬롯에 몰아 줘도 0.535 vs 0.518 (+0.017, p=0.36, ns)이고, 컨트롤 슬롯조차 집중 예산 하에서 빈 상태로 정지했습니다. 최적화기는 수용할 규칙을 찾지 못한 겁니다.

해석: <span style="background-color: #fff59d"><strong>ALFWorld에는 반복되고 말로 적을 수 있는 제어 실패가 있는데 WebShop에는 없습니다</strong></span>. 태스크 의존적 결과라는 뜻입니다.

## 이득의 내용: 환경 기반 자기교정

![Figure 5: 태스크 유형별 control 슬롯 이득 분해](/images/2026-09-06-harnessevo-slot-credit-assignment/fig-5-p16.png)

control 슬롯 이득을 ALFWorld 태스크 유형별로 쪼개면 규칙 내용과 정확히 맞물립니다.

| ALFWorld 태스크 | Δ | n |
| --- | --- | --- |
| look_at_obj_in_light | +0.444 | 18 |
| clean_then_place | +0.226 | 31 |
| pick_and_place | +0.042 | 24 |

최대 이득은 조명 확인 태스크에서 나옵니다. 물건을 든 채 포기하거나 책상 램프를 켜지 않는 <span style="background-color: #fff59d"><strong>전형적인 조기 종료 / 루프 실패</strong></span>를 control 규칙이 직접 고칩니다. 이득이 튜닝하지 않은 유형으로도 이전되고, 게임 가능한 dense 보상 환경(WebShop)에서는 최적화기가 슬롯을 채우지 않고 기권합니다. 저자들은 이를 <span style="background-color: #fff59d"><strong>보상 해킹이 아니라 환경 기반 자기교정</strong></span>으로 판단합니다.

## 실무 적용 기준

새 태스크에 하니스 최적화를 도입하기 전에 두 가지만 확인하면 됩니다.

1. 얼어붙은 에이전트의 실패가 인스턴스들 사이에서 반복되는가
2. 그 실패를 일반 제어 휴리스틱 한 줄로 적을 수 있는가

둘 다 예스면 control 슬롯 집중 진화가 효과를 볼 가능성이 높습니다. 아니오면 널이 돌아오는데, 정상 동작하는 최적화기가 과적합 대신 널을 돌려주는 것이 안전한 신호입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

하니스 최적화는 언제 도움이 되나요?
에이전트의 실패가 반복적이고 일반 제어 휴리스틱으로 기술될 때입니다. 논문의 ALFWorld가 그 사례이고, WebShop은 반례입니다.

예산 분할 함정이 정확히 뭔가요?
반성 최적화기의 수용-재점수 바닥(약 16 rollouts)보다 슬롯당 예산이 낮아지면 어떤 돌연변이도 수용하지 못하고 전 슬롯이 빈 시드에서 정지하는 현상입니다.

WebShop에서 왜 이득이 없었나요?
반복적이고 언어화 가능한 제어 실패가 없어서입니다. 전 예산을 control 슬롯에 몰아줘도 널이었습니다 (0.535 vs 0.518, p=0.36).

페르소나나 전략 프롬프트는 버려야 하나요?
이 논문의 측정 범위(태스크 2개, 7B 모델 1종)에서 개별 기여는 널입니다. 저자들도 한계를 명시합니다.

논문의 통계 처리는 어떻게 됐나요?
10,000-리샘플 부트스트랩 95% CI, ALFWorld는 paired McNemar, WebShop은 paired bootstrap입니다. ns 결과를 그대로 보고합니다.
