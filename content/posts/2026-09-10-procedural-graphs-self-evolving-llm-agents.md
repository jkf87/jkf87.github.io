---
title: "Procedural Graph: LLM 에이전트를 위한 자가진화 절차 그래프 (arXiv 2609.09153) 논문 정리"
date: 2026-09-10
tags:
  - ai-agent
  - procedural-graph
  - self-evolution
  - knowledge-graph
  - arxiv
draft: false
description: "arXiv 2609.09153 논문 요약. 절차 지식을 (절차, 관계, 절차) 트리플릿 그래프로 표현하고 활성 노드 기반 안내와 검증 게이팅 자가진화를 적용한 Procedural Graph 프레임워크의 구조와 6개 벤치마크 실험 결과 정리."
---

## 결론 먼저

arXiv 2609.09153v1(2026-09-08, Google · Georgia Tech · Peking University, Yuxing Lu 외)는 LLM 에이전트의 절차 지식을 그래프 구조로 명시하고, 이를 자가진화시키는 프레임워크를 제안한다.

6개 벤치마크, 4개 LLM, 7개 베이스라인 비교에서 <span style="background-color: #fff59d"><strong>최강 베이스라인 대비 19승 2무 3패</strong></span>(부호검정 p = 4.3×10⁻⁴)를 기록했다.

## 방법 요약

- 표현: 절차 지식을 (절차, 관계, 절차) 트리플릿 그래프로 표현한다.
- 관계 예: leads_to, requires, enables. 지식그래프가 사실(what-is)을 다루는 것과 대비되어 이쪽은 행동(what-to-do)을 다룬다.
- 실행: 각 결정 스텝에서 에이전트의 활성 노드를 국소화(localize)한다. 안내 모델이 주변 서브그래프를 스텝 수준의 상황 안내로 변환해 솔버의 다음 행동에 치우침을 준다. 행동을 결정하지 않는다.
- 자가진화: LLM refiner가 실패 트레이터리와 성공 트레이터리를 대조하여 그래프의 토폴로지와 속성을 편집한다. 편집은 홀드아웃 검증 성능이 유지 또는 개선될 때만 커밋된다. 거절된 편집도 보존되어 같은 시도의 반복을 억제한다.

![Figure 2 프레임워크 개요](/images/2026-09-10-procedural-graphs-self-evolving-llm-agents/fig-2-p4.png)

## 실험 설정

- 벤치마크: HotpotQA, MultiChallenge, GDPval, ALFWorld, τ-bench, BFCL v3 (7번째 벤치마크 EnterpriseArena는 장기 의사결정 실험에 사용)
- LLM: Claude Sonnet 4.6, Gemini 3.1 Pro, Gemini 3.5 Flash, Grok 4.1 Fast
- 베이스라인: Vanilla ReAct, MemoryBank, RAP, ExpeL, AutoGuide, AWM, KnowAgent

## 주요 결과

| 항목 | 값 |
|---|---|
| 최강 베이스라인 대비 전적 | <span style="background-color: #fff59d"><strong>19승 2무 3패</strong></span> |
| BFCL v3 (Gemini 3.5 Flash) | <span style="background-color: #fff59d"><strong>67.00% vs 58.00% (+9.00p)</strong></span> |
| GDPval (Gemini 3.1 Pro) | 78.78 vs 71.37 (+7.41p) |
| τ-bench (Gemini 3.1 Pro) | 80.00% vs 73.04% (+6.96p) |
| HotpotQA 마진 범위 | −0.90 ~ +1.30p |
| EnterpriseArena 검증 생존율 | <span style="background-color: #fff59d"><strong>베이스라인 0.0% → 진화 그래프 90.0%</strong></span> (테스트 85.0%) |

GDPval, BFCL v3에서는 4개 LLM 전체에서 모든 베이스라인을 상회했다. <span style="background-color: #fff59d"><strong>HotpotQA에서는 유의한 이득이 없었다</strong></span> (마진 −0.90 ~ +1.30p).

### 구성 전략 비교 (Table 2)

- 전문가 그래프 고정 사용(Mode 1)은 MultiChallenge 성공률을 <span style="background-color: #fff59d"><strong>87.50%에서 58.93%로 저하</strong></span>시켰다.
- 1회 오프라인 업데이트(Mode 2)는 53.57%로 추가 저하시켰다.
- 온라인 진화(Mode 3)는 <span style="background-color: #fff59d"><strong>92.86%로 회복</strong></span>했다 (+33.93p).
- 스크래치 + 온라인 진화(Mode 5)는 HotpotQA에서 Ans F1 78.79%, EM 66.30%로 최고 성능을 보였다.

### 사용 방식 절제 (Table 3)

MultiChallenge 정확도: 그래프 없음 80.27% &lt; 전체 그래프 원본 주입 86.60% &lt; 전체 그래프 생성 안내 87.35% &lt; <span style="background-color: #fff59d"><strong>서브그래프 생성 안내(제안 방식) 89.31%</strong></span>.

### 장기 의사결정 (EnterpriseArena)

- 생존율: Claude Sonnet 4.6 <span style="background-color: #fff59d"><strong>44.0%→58.0%</strong></span>, Gemini 3.1 Pro <span style="background-color: #fff59d"><strong>6.0%→34.0%</strong></span>, Grok 4.1 Fast 26.0%→40.0%
- 월평균 툴콜(Gemini 3.5 Flash): <span style="background-color: #fff59d"><strong>18.94회 → 12.53회</strong></span>
- 평균 조달 자본: Flash 베이스라인 <span style="background-color: #fff59d"><strong>$0.00M</strong></span>, PG 안내 Flash $9.39M, PG 안내 Grok 4.1 Fast $30.11M

![Figure 3 현금 트레이터리와 생존곡선](/images/2026-09-10-procedural-graphs-self-evolving-llm-agents/fig-3-p8.png)

## 한계

- HotpotQA 등 절차 의존도가 낮은 태스크에서 이득이 유의미하지 않다.
- EnterpriseArena는 에피소드당 20개 샘플로, 개별 수락/거절 결정의 통계적 해석에 한계가 있다(논문 명시).

## 소스

- 초록: https://arxiv.org/abs/2609.09153
- PDF: https://arxiv.org/pdf/2609.09153
- HTML: https://arxiv.org/html/2609.09153v1

기준일: 2026-09-08 arXiv v1.

## 자주 묻는 질문

### 메모리 기반 에이전트(ExpeL, MemoryBank)와 다른 점은 무엇인가
메모리 방식은 과거 경험을 자유 텍스트로 저장해 검색해 쓰기 때문에, 솔버가 그 기록을 현재 스텝에 어떻게 적용할지 다시 재구성해야 합니다. Procedural Graph는 절차 간 연결과 조건을 그래프 엣지로 명시해 두고, 현재 진행 상태에서 해당 서브그래프만 안내로 받습니다.

### 그래프를 사람이 직접 만들어야 하는지와 그 방법
아니요. 최소 뼈대(skeleton)에서 시작해 LLM refiner가 실패/성공 트레이터리 대조로 수정합니다. HotpotQA에서는 스크래치에서 시작한 자가진화(Mode 5)가 Ans F1 78.79%로 모든 구성 중 최고 성적이었습니다.

### 안내가 모델 행동을 통제하는 범위는 어떻게 되나
안내 모델은 다음 행동을 지시하지 않고 치우침만 줍니다. ablation에서도 원본 그래프 주입보다 서브그래프를 문장 안내로 바꾸는 방식이 성능과 토큰 효율 모두에서 좋았습니다.

### 검증 없이 그래프를 수정하면 어떻게 되나
논문의 1회 오프라인 업데이트(Mode 2)가 MultiChallenge 53.57%로 가장 나쁜 성적을 보인 게 그 사례입니다. 수정은 홀드아웃 성적이 유지·개선될 때만 커밋되어야 합니다.

### 이득이 큰 태스크 유형은 무엇인가
HotpotQA처럼 절차 의존도가 낮은 단순 QA에서는 이득이 거의 없었습니다. 절차가 길고 순서가 중요한 GDPval, BFCL v3, τ-bench 같은 도구 사용·엔터프라이즈 태스크에서 이득이 컸습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
