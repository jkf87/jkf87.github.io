---
title: "논문 정리: Skill-Use — 에이전트 하네스에서 LLM의 스킬 사용 능력 측정 (arXiv 2608.04828)"
date: 2026-08-24T19:00:00+09:00
tags: [agent, LLM, benchmark, skill, harness, evaluation]
draft: false
---

## 개요

Skill-Use(arXiv 2608.04828)는 LLM 에이전트가 스킬 문서를 실제로 인식하고 준수하는지를 측정하는 벤치마크다. 공개 GitHub 스킬 <span style="background-color: #fff59d"><strong>7,979개</strong></span>와 실행 가능한 과제 <span style="background-color: #fff59d"><strong>17만 7,177개</strong></span>를 9개 도역에서 짝지었고, 각 과제는 Docker 샌드박스에서 실행되어 트레이스 기반 루브릭으로 채점된다. 8개 프론티어 모델을 Claude Code(CC)와 Codex 두 하네스에서 평가했다.

논문: <https://arxiv.org/abs/2608.04828>

## 측정 정의

스킬 문서 전체는 에이전트가 해당 파일을 직접 조회해야만 확인할 수 있는 <span style="background-color: #fff59d"><strong>progressive disclosure</strong></span> 방식으로 제공된다. 에이전트는 이름과 한 줄 설명만 받고 시작한다. 평가 축은 세 가지다.

- Trigger: 대상 스킬을 인식하고 retrieve했는지 여부
- Compliance: 스킬이 규정한 요구 사항의 가중 충족 비율
- Boundary: 금지 행동의 부재 비율

통합 점수는 <span style="background-color: #fff59d"><strong>SU = Trigger × (0.7·Compliance + 0.3·Boundary)</strong></span>이며, 스킬 발동 전에는 실행 점수가 인정되지 않는 게이티드 구조다.

![](/images/2026-08-24-skill-use-trigger-compliance-boundary/fig-1-p1.png)

## 주요 결과

![](/images/2026-08-24-skill-use-trigger-compliance-boundary/table-1-p6.png)

최고 성능 조합은 CC 하네스의 GPT-5.5로 <span style="background-color: #fff59d"><strong>SU 0.613</strong></span>이었다. 신뢰 가능한 수준과는 거리가 있다. CC 하네스 기준 수치는 다음과 같다.

| 모델 | Trigger | Compliance | Boundary | SU |
|---|---|---|---|---|
| GPT-5.5 | 0.972 | 0.611 | 0.718 | 0.613 |
| Claude Opus 4.7 | 0.966 | 0.609 | 0.712 | 0.599 |
| Claude Opus 4.8 | 0.940 | 0.625 | 0.704 | 0.597 |
| MiniMax-M3 | 0.833 | 0.569 | 0.706 | 0.501 |
| Qwen3.6-Max | 0.446 | 0.475 | 0.625 | 0.318 |
| GLM-5.1 | 0.324 | 0.455 | 0.639 | 0.267 |
| DeepSeek-V4-Pro | 0.324 | 0.439 | 0.658 | 0.250 |
| Kimi-K2.6 | 0.337 | 0.447 | 0.580 | 0.190 |

주요 발견은 다음과 같다.

1. <span style="background-color: #fff59d"><strong>Trigger와 Compliance는 독립적 병목이다.</strong></span> 오픈웨이트 중상위 모델(GLM-5.1, DeepSeek-V4-Pro, Kimi-K2.6)은 Trigger가 0.32~0.34에 그치지만 조건부 Compliance†(0.58~0.64)는 선두권과 대등하다.
2. 모든 구성에서 Boundary가 Compliance보다 높다. 모델은 금지 항목을 회피하는 것보다 <span style="background-color: #fff59d"><strong>요구된 절차를 끝까지 완수하는 데 더 자주 실패한다.</strong></span> 예외는 보안/컴플라이언스 도역으로, 이 경우 Boundary가 최저를 기록한다.
3. 하네스 의존성: GPT-5.5는 CC→Codex 이동 시 SU가 0.613→0.503으로 하락하고, GLM-5.1(0.267→0.421)과 Kimi-K2.6(0.190→0.374)은 상승한다. 두 하네스의 모델별 SU 상관은 중간 수준이며 <span style="background-color: #fff59d"><strong>중위권 모델은 순위가 역전된다.</strong></span>

![](/images/2026-08-24-skill-use-trigger-compliance-boundary/fig-3-p7.png)

## 분석 결과

**인젝션 모드(4.4절).** 스킬 전문을 미리 삽입하는 preloaded 모드는 Trigger를 개선하되 조건부 Compliance는 거의 변화시키지 않는다. 개선 효과는 추상적 이름의 스킬에서 크다. <span style="background-color: #fff59d"><strong>병목은 절차 실행이 아니라 검색·인식 단계</strong></span>임을 시사한다.

![](/images/2026-08-24-skill-use-trigger-compliance-boundary/fig-4-p8.png)

**라이브러리 크기(4.5절).** 스킬 수를 1→10으로 늘리면 SU가 하락하며, 손실의 대부분은 오선택이 아닌 미발동(none)에서 발생한다. 10개 이후 감소세는 완만하다.

**범위 밖 절제(4.6절).** 스킬이 불필요한 53개 과제에서 범위 내 SU와 avoidance의 상관은 음수다. <span style="background-color: #fff59d"><strong>스킬을 가장 잘 따르는 모델이 불필요한 발동을 가장 못 막는다.</strong></span> 과잉 발동은 Claude Opus과 GPT-5.5에 집중되며, 주제가 겹치는 문서형 요청에서 유발된다.

![](/images/2026-08-24-skill-use-trigger-compliance-boundary/fig-6-p9.png)

**과제 완수 기여(4.7절).** 동일 과제·모델에서 스킬 on/off 짝 비교 시 순수 이득은 <span style="background-color: #fff59d"><strong>SU≈0.5를 기준으로 부호가 바뀐다.</strong></span> SU 0.5 미만에서는 부분 준수로 인해 스킬이 무제 상태보다 성적을 낮춘다. <span style="background-color: #fff59d"><strong>스킬 라이브러리는 공짜 개선이 아니다.</strong></span>

## 벤치마크 구축 파이프라인

10만 5,586개 후보를 4단계(필터·클러스터링 → 쿼터 기반 수집 → 규칙 점수화 → masked-skill 평가)로 7,979개까지 선별했다. 태스크와 루브릭은 서로 다른 모델 패밀리의 리뷰어가 참여하는 다중 에이전트 대항 심사를 통과했고, 크라우드 인간 감사(<span style="background-color: #fff59d"><strong>Cohen κ=0.65</strong></span>)로 검증되었다. 채점은 정규식·상태 diff 등 결정적 검증을 우선한다.

![](/images/2026-08-24-skill-use-trigger-compliance-boundary/fig-2-p5.png)

## 결론

Skill-Use의 측정에 따르면 스킬 사용 능력은 모델의 고정 속성이 아니라 <span style="background-color: #fff59d"><strong>모델-하네스 구성의 속성</strong></span>이며, 인식과 절차 준수는 분리된 병목이다. 스킬 라이브러리 도입의 실제 손익은 인식률, 조건부 준수율, 범위 밖 절제를 함께 측정해야 판단할 수 있다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
