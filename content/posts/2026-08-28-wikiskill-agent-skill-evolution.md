---
title: WikiSkill — 에이전트 경험을 위키로 컴파일해서 스킬을 계속 진화시키는 방법
date: 2026-08-28
draft: false
tags: [agent, skill-evolution, wiki, llm, paper-review]
description: 구글 리서치 WikiSkill 논문 정리. 실행 트레이스를 위키라는 영구 지식층에 컴파일하고, 그 위에서 스킬을 진화시켜 5개 모델 평균 최대 +23.9pt를 얻은 방법론과 수치를 정리했습니다.
---

## 결론 먼저

핵심은 이겁니다. 에이전트가 실험하면서 얻은 교훈을 통째로 버리지 말고, <span style="background-color: #fff59d"><strong>위키라는 영구 지식층에 컴파일해서 쌓아두면 스킬 진화 성능이 크게 오릅니다</strong></span>.

WikiSkill(구글 리서치, 2026-08-27 arXiv 공개)은 작업공간을 raw 트레이스 / wiki / skills 3층으로 나누고, 매 iteration마다 트레이스를 위키로 정리한 뒤 그 위키를 근거로 스킬을 수정합니다. 검증 점수가 오르면 스킬 업데이트를 받아들이고, 안 오면 롤백합니다. 근데 <span style="background-color: #fff59d"><strong>위키는 롤백하지 않고 계속 쌓입니다</strong></span>.

결과는 Qwen 계열에서 스케일이 클수록 이득이 커져서 <span style="background-color: #fff59d"><strong>4B +12.3pt, 9B +17.5pt, 27B +23.9pt</strong></span>. 그리고 <span style="background-color: #fff59d"><strong>9B+WikiSkill(47.4%)이 스킬 없는 27B(39.4%)를 이겼습니다</strong></span>.

## 핵심 수치 요약

| 항목 | 수치 | 비고 |
|---|---|---|
| Qwen-3.5-4B 평균 향상 | +12.3pt | no skill 대비 |
| Qwen-3.5-9B 평균 향상 | +17.5pt | no skill 대비 |
| Qwen-3.6-27B 평균 향상 | +23.9pt | no skill 대비 |
| 9B+WikiSkill vs 27B no-skill | 47.4% vs 39.4% | 작은 모델이 큰 모델 역전 |
| Gemini-3.5-Flash LiveMath | 33.0% → 72.6% | 같은 모델, 스킬만 다름 |
| Qwen-3.6-27B SpreadSheet | 40.8% → 81.7% | +40.9pt |
| 위키 있음/없음 에블레이션 | 48.7% → 63.7% | Gemini-3.5-Flash 평균 |
| 최고 성능 기준 우위 | +3.3 ~ +12.0pt | 기존 SOTA 대비 5개 모델 전부 |

기준일: 2026-08-28. 모든 수치는 논문 Table 1–3 기준이고, 3회 독립 실행 평균입니다.

## 어떤 문제를 푸나

에이전트 스킬(Anthropic식 SKILL.md 디렉터리)은 파라미터를 건드리지 않고 절차 지식을 재사용하는 가벼운 방법입니다. 최근에는 사람이 직접 안 쓰고, 에이전트를 돌려보고 성공/실패 트레이스를 분석해서 스킬을 자동 수정하는 연구(Trace2Skill, EvoSkill, SkillOpt)가 이어지고 있구요.

문제는 이 방법들이 <span style="background-color: #fff59d"><strong>배운 걸 별도의 지식 표현으로 보존하지 않는다는 겁니다</strong></span>. 교훈이 최적화 히스토리 여기저기에 흩어져 있으니 다음 iteration에서 재사용이 안 됩니다. 저자들은 Karpathy의 LLM Wiki 관점(<span style="background-color: #fff59d"><strong>경험을 복리로 쌓이는 지식으로 컴파일하라</strong></span>)에서 출발했습니다.

## 3층 구조와 진화 루프

![WikiSkill 프레임워크 개요](/images/2026-08-28-wikiskill-agent-skill-evolution/fig-2-p4.png)

작업공간이 세 층입니다.

| 층 | 디렉터리 | 역할 | 성격 |
|---|---|---|---|
| Raw | `raw/` | 실행 트레이스 원본 | 한 번 쓰면 불변 |
| Wiki | `wiki/` | 패턴 문서 + 진화 로그 + 스킬 영향 추적 | 롤백 없이 계속 축적 |
| Skills | `skills/` | 실행 가능한 절차 지식(SKILL.md) | 검증 게이트 통과 시만 교체 |

한 iteration의 흐름은 이렇습니다.

1. Inference Agent가 현재 스킬로 학습 태스크 rollout → 트레이스가 `raw/`에 쌓임
2. Wiki Maintainer가 트레이스에서 실패 원인/성공 전략을 뽑아 `wiki/patterns/` 문서를 만들거나 패치 수정
3. Skill Proposer가 위키 인덱스 + 영향 추적기 + 트레이스를 (ReAct로 필요한 것만 `read_file`해서) 보고 스킬 하나에 대한 원자적 수정 제안
4. 검증 셋에서 점수가 최고치를 갱신하면 수용, 아니면 스킬만 롤백. 위키는 유지

재밌는 디테일이 두 개 있습니다. <span style="background-color: #fff59d"><strong>추론 에이전트는 훈련 rollout 중에 위키 접근이 막혀 있고요</strong></span>(에블레이션에서 오히려 해롭다고 확인), 스킬 영향 추적기(`skill-impact.md`)가 <span style="background-color: #fff59d"><strong>수용/거부 이력과 diff를 자동 기록</strong></span>해서 제안자가 실패한 수정을 반복 제안하지 않게 합니다.

## 성능 — 모델이 클수록, 위키가 있을수록

![모델별 성능 비교](/images/2026-08-28-wikiskill-agent-skill-evolution/fig-1-p1.png)

Table 1 요약입니다. 5개 벤치마크(LiveMath, SealQA, SpreadSheetBench, OfficeQA, ALFWorld), 5개 모델(Qwen 4B/9B/27B, Gemma-4-31B, Gemini-3.5-Flash)에서 WikiSkill이 전 모델 평균 1위입니다. 기존 최강 기법 대비 평균 <span style="background-color: #fff59d"><strong>+3.3(Qwen-4B)부터 +12.0(Gemini-3.5-Flash) 포인트 우위</strong></span>구요.

특징적인 결과들:

- 기존 기법은 불안정합니다. EvoSkill은 Qwen-9B LiveMath를 28.2%→58.1%로 올리면서 Gemma-31B LiveMath는 <span style="background-color: #fff59d"><strong>33.9%→29.8%로 떨어뜨립니다</strong></span>. WikiSkill은 이런 저하 사례가 거의 없습니다.
- LiveMath는 모든 모델에서 +20.6 ~ +39.6pt로 스킬 진화가 잘 먹히는 도메인입니다.
- OfficeQA(긴 문서 QA)는 예외적으로 4B 모델에서 소폭 하락합니다. 다단계 검색 워크플로를 4B가 실행하지 못하고 기본 동작으로 되돌아가서요.

## 스킬 진화와 모델 스케일링의 관계

Qwen 패밀리 내부에서 이득이 4B +12.3 → 9B +17.5 → 27B +23.9로 스케일이 클수록 커집니다. SpreadSheetBench에서는 +6.5 / +9.3 / +40.9로 격차가 벌어지구요. 같은 스킬 메커니즘도 더 강한 모델이 더 잘 활용합니다.

동시에 반대 방향도 성립합니다. Qwen-3.5-9B+WikiSkill이 47.4%로 스킬 없는 Qwen-3.6-27B(39.4%)보다 높습니다. 논문의 해석은 <span style="background-color: #fff59d"><strong>모델 용량과 진화된 절차 지식이 서로 보완적인 성능 원천</strong></span>이라는 것입니다.

## 스킬은 모델 간에 이동한다

Table 2가 또 흥미로운데, 남이 진화한 스킬이 자기가 진화한 스킬보다 나을 때가 있습니다.

| 대상 모델 | 스킬 출처 | SpreadSheet | LiveMath |
|---|---|---|---|
| Qwen-3.5-9B | 없음 | 24.3% | 28.2% |
| Qwen-3.5-9B | 자기 스킬 | 33.6% | 56.3% |
| Qwen-3.5-9B | 27B 스킬 | 50.5% | — |
| Gemma-4-31B | 없음 | 48.3% | 33.9% |
| Gemma-4-31B | 4B 스킬 | — | 73.1% |

ALFWorld에서는 Qwen-3.5-9B가 27B제 스킬로 70.2%, 자기 스킬로는 63.4%입니다. 즉 <span style="background-color: #fff59d"><strong>스킬 발견과 스킬 실행은 별개 능력</strong></span>이고, 작은 모델이 만든 스킬도 큰 모델에 잘 옮겨갑니다.

부정 전이도 있습니다. Qwen-3.5-4B 스킬을 Gemini-3.5-Flash에 넣으면 SpreadSheet가 <span style="background-color: #fff59d"><strong>50.5%→18.1%로 추락</strong></span>합니다. 원인 분석은 이렇습니다. 4B용 스킬에 "한 줄짜리 파이썬 커맨드" 같은 저수단 워크어라운드가 박혀 있어서, 강한 모델이 엔드투엔드 스크립트를 쓰는 걸 막아버리는 겁니다. 스킬이 일반 절차인지 모델 특화 우회책인지에 따라 이동성이 갈립니다.

## 에블레이션 — 위키 지속성의 효과

![ALFWorld 사례 연구](/images/2026-08-28-wikiskill-agent-skill-evolution/fig-3-p12.png)

Table 3 에블레이션(Gemini-3.5-Flash)이 구조의 가치를 직접 보여줍니다.

| 구성 | 평균 |
|---|---|
| 스킬 제안자 위키 접근 없음(=지식 축적 없음) | 48.7% |
| 제안자만 위키 접근(기본 구성) | 63.7% |
| 제안자 + 추론 에이전트 둘 다 위키 접근 | 60.9% |

<span style="background-color: #fff59d"><strong>위키 유무만으로 +15.0pt입니다</strong></span>. LiveMath는 51.3%→72.6%, SpreadSheet는 49.9%→76.6%로 뜁니다.

추론 에이전트에게도 위키 접근을 주면 오히려 63.7%→60.9%로 떨어집니다. 훈련 rollout에서 위키를 직접 보면 스킬 대신 위키에서 지식을 가져와버려서, 트레이스가 스킬 개발에 주는 신호가 흐려지기 때문이라고 저자들은 추정합니다.

## 내 해석 — 하네스에 적용할 점

원문 근거와 제 해석을 나눠서 정리하면:

- 원문이 보여주는 건 <span style="background-color: #fff59d"><strong>"지식 축적 층의 존재 유무"가 성능을 좌우한다는 사실</strong></span>입니다. 스킬 제안 로직은 기존 기법과 크게 다르지 않습니다.
- 제 해석: 이건 사실상 에이전트 하네스에 메모리 계층 설계를 넣으라는 얘기입니다. rejected 제안 + diff + 점수를 자동 기록하는 `skill-impact.md` 같은 감사 로그가 "같은 실패를 반복하지 않는" 핵심 메커니즘이라, 에이전트 루프 설계에 바로 베낄 만합니다.
- 주의점: 위키 접근 권한을 누구에게 줄지가 성능을 3pt 흔듭니다. 지식 노출 범위 자체가 설계 변수입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### WikiSkill이 뭐하는 프레임워크인가요?

에이전트 실행 트레이스를 위키(영구 지식 베이스)로 컴파일하고, 그 위키를 근거로 스킬을 반복 수정·게이트하는 스킬 진화 프레임워크입니다. 구글 리서치가 2026-08-27에 arXiv에 공개했습니다.

### 위키가 없으면 왜 성능이 떨어지나요?

매 iteration의 교훈이 보존되지 않아서 스킬 제안자가 같은 실패를 반복 분석합니다. 에블레이션에서 제안자의 위키 접근을 끊자 Gemini-3.5-Flash 평균이 63.7%→48.7%로 떨어졌습니다.

### 작은 모델도 스킬 진화로 이득을 보나요?

봅니다. Qwen-3.5-4B도 평균 +12.3pt 올랐고, 9B+WikiSkill은 스킬 없는 27B를 역전했습니다. 다만 이득 크기는 큰 모델일수록 커지는 추세입니다.

### 다른 모델이 만든 스킬도 쓸 수 있나요?

네. Qwen 스킬이 Gemma, Gemini로 잘 옮겨갔고, 남이 만든 스킬이 자기 스킬보다 나은 경우도 있었습니다. 단, 모델 특화 우회책이 섞인 스킬은 부정 전이(50.5%→18.1%)를 일으킬 수 있습니다.

### 한계는 뭔가요?

OfficeQA처럼 긴 컨텍스트 다단계 검색에서는 4B급 모델이 스킬을 실행하지 못해 성능이 소폭 하락했고, SpreadSheet 스킬은 출처 모델에 따라 이동성 편차가 큽니다. 스킬 발견과 실행이 별개 능력이라는 점 자체가 배포 시 고려사항입니다.

## 출처

- 논문: [WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution](https://arxiv.org/abs/2608.27454) (arXiv 2608.27454, 2026-08-27)
- PDF: https://arxiv.org/pdf/2608.27454v1
- 인용 기법: Trace2Skill, EvoSkill, SkillOpt, Karpathy의 LLM Wiki 관점
- 본문 그림은 논문 Figure 1, 2, 3 캡션 크롭입니다.
