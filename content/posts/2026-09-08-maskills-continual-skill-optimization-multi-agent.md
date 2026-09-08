---
title: "MASkills — 멀티에이전트도 스킬로 최적화한다, EMNLP 2026 Findings 논문 정리 (arXiv 2609.02094)"
date: 2026-09-08
tags: [multi-agent, skill, credit-assignment, emnlp2026]
draft: false
description: "EMNLP 2026 Findings MASkills(arXiv 2609.02094) 정리. 멀티에이전트 LLM의 스킬 라이브러리를 검증 롤백과 함께 계속 최적화해 HotpotQA F1 76.3, LoCoMo 멀티홉 F1 17.22, GAIA 23.3%를 달성한 방법과 절제 실험을 수치로 정리했습니다."
---

## 결론 먼저

LLM 에이전트 팀에 <span style="background-color: #fff59d"><strong>'경험 메모리' 대신 '스킬 라이브러리'를 달아주고 그걸 계속 최적화</strong></span>하면 어떻게 되는가. EMNLP 2026 Findings에 실린 MASkills 논문의 답은 이렇다. <span style="background-color: #fff59d"><strong>HotpotQA F1 69.2 → 76.3, LoCoMo 멀티홉 F1 12.04 → 17.22, GAIA 평균 20.4% → 23.3%</strong></span>.

9월 2일 arXiv에 올라온 논문입니다 — [arXiv 2609.02094](https://arxiv.org/abs/2609.02094), 코드는 [GitHub](https://github.com/DaRL-GenAI/MASkills)에 공개됐습니다.

## 핵심 요약 표

| 항목 | 값 |
| --- | --- |
| HotpotQA F1 | MultiPersona 69.2 → MASkills 76.3 |
| LoCoMo 멀티홉 F1 | 베이스 12.04 → 17.22 |
| GAIA 평균 | R1-Searcher 20.4% → MASkills 23.3% |
| 최대 기여 모듈 | <span style="background-color: #fff59d"><strong>검증 롤백 (validation rollback)</strong></span> |
| 옵티마이저 / 액터 | <span style="background-color: #fff59d"><strong>GPT-5.1 / GPT-4o-mini, Qwen2.5-7B</strong></span> |

기준일: 2026-09-08 기준 arXiv v1 수치입니다.

## 스킬을 최적화 단위로 쓰는 이유

기존 자기반성 방식의 문제는 명확하다. 쌓아둔 메모리는 호출이 어렵고, 정제되지 않고, 스케일도 안 된다. <span style="background-color: #fff59d"><strong>MASkills는 다른 단위를 고른다</strong></span> — <span style="background-color: #fff59d"><strong>언제, 어떻게, 무엇으로 행동할지 명세한 구조화된 절차 지식, 즉 스킬</strong></span>.

## 파이프라인 구조

![MASkills 파이프라인](/images/2026-09-08-maskills-continual-skill-optimization-multi-agent/fig-1-p4.png)

Figure 1. 스킬 공간 정책 최적화. (출처: arXiv 2609.02094 Figure 1)

액터들이 스킬을 실행해 트라젝토리를 만든다. 어느 스킬이 공헌했는지 <span style="background-color: #fff59d"><strong>언어 크레딧이 매겨지고 모멘텀로 평활화</strong></span>된다. 그리고 스킬 라이브러리가 다듬어진다 — <span style="background-color: #fff59d"><strong>refinement, induction, consolidation, pruning</strong></span>.

## 벤치마크별 결과

![주요 결과](/images/2026-09-08-maskills-continual-skill-optimization-multi-agent/table-1-p9.png)

Table 1. 3개 벤치마크 주요 결과. (출처: arXiv 2609.02094 Table 1)

셋 다 이겼다. 특히 <span style="background-color: #fff59d"><strong>LoCoMo 멀티홉은 상대 개선 43%</strong></span>. 반면 GAIA L3(최상위 난이도)에서는 여전히 0%라는 점이 정직하다.

![학습 곡선](/images/2026-09-08-maskills-continual-skill-optimization-multi-agent/fig-2-p8.png)

Figure 2. 검증 기반 스킬 갱신 곡선. (출처: arXiv 2609.02094 Figure 2)

## 절제 실험 결과

검증 롤백을 빼면 <span style="background-color: #fff59d"><strong>LoCoMo-MH가 17.2 → 6.6으로 무너진다</strong></span>. LLM 비평 기반 자기수정은 되돌림 장치 없이는 붕괴한다 — 하네스 설계자가 아려야 할 문장이다. <span style="background-color: #fff59d"><strong>스킬 크레딧 어사인먼트 제거도 GAIA에서 6.2%p 하락</strong></span>을 만든다.

| 구성 | LoCoMo-MH | GAIA |
| --- | --- | --- |
| MASkills (Full) | 17.2 | 23.3 |
| w/o 스킬 크레딧 어사인먼트 | 14.2 | 17.1 |
| w/o 모멘텀 평활화 | 16.4 | 21.9 |
| w/o 검증 롤백 | 6.6 | 13.5 |
| w/o 통합/가지치기 | 13.9 | 13.0 |

![절제 실험 표](/images/2026-09-08-maskills-continual-skill-optimization-multi-agent/table-2-p10.png)

Table 2. 절제 실험. (출처: arXiv 2609.02094 Table 2)

## 스킬 전이 결과

![스킬 품질과 전이](/images/2026-09-08-maskills-continual-skill-optimization-multi-agent/fig-3-p9.png)

Figure 3. 스킬 품질 비교와 크로스태스크 전이. (출처: arXiv 2609.02094 Figure 3)

<span style="background-color: #fff59d"><strong>프롬프트로 한 번 뽑은 스킬은 노스킬과 별 차이가 없다</strong></span>. 계속 최적화된 스킬만 격차를 벌린다. 게다가 <span style="background-color: #fff59d"><strong>GAIA에서 배운 스킬을 HotpotQA에 그대로 옮겨도 CoT보다 높다</strong></span>. <span style="background-color: #fff59d"><strong>추가 최적화 없는 제로샷 이식으로도 전이 효과가 확인됐다</strong></span>는 게 핵심 관찰이다.

## 토폴로지와 백본 범위

중앙집중·분산·계층 어느 구조에서나 경쟁력을 유지한다. 최적 토폴로지는 태스크 따라 다르다 — <span style="background-color: #fff59d"><strong>탐색 다양성이 필요하면 분산, 전역 메모리 일관성이 필요하면 중앙집중</strong></span>. <span style="background-color: #fff59d"><strong>액터가 GPT-4o-mini와 Qwen2.5-7B</strong></span>라는 점도 주목할 만하다. 프론티어 모델이 아닌 액터로도 스킬 최적화 이득이 살아난다.

![백본 비교](/images/2026-09-08-maskills-continual-skill-optimization-multi-agent/fig-4-p10.png)

Figure 4. 백본별 비교. (출처: arXiv 2609.02094 Figure 4)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### MASkills는 어떻게 멀티에이전트를 최적화하나요?
각 에이전트의 자연어 스킬 라이브러리를 refinement/induction/consolidation/pruning으로 갱신합니다. 수정 후보는 검증 셋 통과 시에만 커밋됩니다.

### 대표 성능 수치는?
HotpotQA F1 76.3, LoCoMo 멀티홉 F1 17.22, GAIA 평균 23.3%입니다.

### 가장 중요한 구성요소는?
<span style="background-color: #fff59d"><strong>검증 롤백입니다. 제거 시 LoCoMo 멀티홉 F1이 17.2 → 6.6으로 붕괴합니다.</strong></span>

### 어떤 모델로 실험했나요?
옵티마이저 GPT-5.1, 액터 GPT-4o-mini와 Qwen2.5-7B입니다.

## 출처

- [arXiv 2609.02094](https://arxiv.org/abs/2609.02094) (EMNLP 2026 Findings) — [PDF](https://arxiv.org/pdf/2609.02094) / [HTML](https://arxiv.org/html/2609.02094v1) / [DOI](https://doi.org/10.48550/arXiv.2609.02094)
- 코드: [github.com/DaRL-GenAI/MASkills](https://github.com/DaRL-GenAI/MASkills)
- Figure 1–4, Table 1–2는 원문 caption crop.
