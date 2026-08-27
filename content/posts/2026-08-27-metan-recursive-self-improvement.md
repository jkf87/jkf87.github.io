---
title: "Meta^n — 재귀적 자기개선 에이전트, 깊이 2를 넘는 법"
date: 2026-08-27
tags: [LLM, agent, self-improvement, recursion, ARC-AGI-2, evolution, harness]
draft: false
---

# 논문 요약: Recursive Self-Improvement through Emergent Depth (arXiv 2608.24735)

Minnesota NLP, 2026-08-25 공개. 본 논문은 자기개선 LLM 에이전트의 메타 깊이(meta-depth)가 <span style="background-color: #fff59d"><strong>약 2에 제한되는 문제</strong></span>를 분석하고, 이를 극복하는 프레임워크 Meta^n을 제안한다.

## 기존 연구의 한계

자기수정 시스템은 안정성을 위해 자기 수정 기계의 일부를 불변으로 유지해야 하며, <span style="background-color: #fff59d"><strong>이 불변 부분이 성능 상한을 형성한다</strong></span>. 메타 레벨을 추가하는 접근법도 새 메타 레벨을 고정시키므로 동일한 한계에 직면한다. 기존 자기개선 에이전트는 답(answer)을 개선할 뿐, 답을 만드는 과정 자체를 개선하지는 못한다.

## 제안 방법: 고정된 메타 연산자 Ω

Meta^n은 <span style="background-color: #fff59d"><strong>단일 고정 메타 연산자 Ω</strong></span>를 정의하고 이를 자기 출력에 재귀적으로 적용한다.

1. Ω는 하위 솔버 스택의 실행 트레이스와 <span style="background-color: #fff59d"><strong>해당 트레이스를 만든 코드까지 함께</strong></span> 읽는다.
2. 출력은 다음 층(layer)으로, 각 태스크 앞에 전략적 컨텍스트를 주입하는 짧은 Python 프리프로세스 + 호출 가능한 헬퍼 함수 라이브러리다.
3. <span style="background-color: #fff59d"><strong>Ω는 변경되지 않으므로 시스템이 발산하지 않는다</strong>. 입력은 단조 증가하므로 각 층은 이전 층보다 많은 정보 위에서 추론한다.
4. 깊이는 미리 정하지 않고 <span style="background-color: #fff59d"><strong>수렴 기준으로 결정</strong></span>되며, 진화적 아카이브(evolutionary archive)가 층 체인을 탐색한다.

![Figure 1](/images/2026-08-27-metan-recursive-self-improvement/fig1-overview.png)
*그림 1. Meta^n 전체 구조. 고정된 Ω가 자기 출력 위에 층을 쌓는다.*

![Figure 3](/images/2026-08-27-metan-recursive-self-improvement/fig3-meta-layer.png)
*그림 3. 메타 층 하나의 두 단계. LawBench 사례로 트레이싱.*

## 실험 결과

두 백본(<span style="background-color: #fff59d"><strong>Gemma 4 31B-IT, GPT-5.2</strong></span>), 시드 3개 평균, <span style="background-color: #fff59d"><strong>8개 벤치마크 패밀리 전부</strong></span>에서 선행 자기개선 에이전트(OpenEvolve, Gödel Agent 등)를 능가했다.

Gemma 백본 결과 (일부):

| 벤치마크 | Meta^n | OpenEvolve | Gödel Agent |
|---|---|---|---|
| CO-Bench | 0.851 | 0.814 | 0.451 |
| Symptom2Disease | 0.733 | 0.718 | 0.710 |
| LawBench | 0.815 | 0.745 | 0.775 |
| AlgoTune | ×15.10 | ×10.45 | ×13.22 |

GPT-5.2 백본에서도 순위가 동일하다 (CO-Bench 0.870 vs 0.702, AE Math 0.917 vs 0.726).

가장 주목할 숫자는 ARC-AGI-2다. 스킬 암기에 저항하도록 설계된 벤치마크에서 <span style="background-color: #fff59d"><strong>0.331을 기록, 비교군 중 유일하게 0을 넘었다</strong></span> (OpenEvolve 0.003, Gödel Agent 0.054).

![Figure 5](/images/2026-08-27-metan-recursive-self-improvement/fig5-search-progress.png)
*그림 5. Meta^n agentic가 더 적은 진화 스텝으로 더 높은 점수에 도달한다.*

## 어블레이션 분석

재귀의 성능 향상은 주로 <span style="background-color: #fff59d"><strong>층 간 조건화(conditioning)에서 발생</strong></span>한다. 또한 깊이에 따라 프롬프트에 명시되지 않은 층별 역할이 자발적으로 출현한다(<span style="background-color: #fff59d"><strong>emergent layer roles</strong></span>).

![Figure 6](/images/2026-08-27-metan-recursive-self-improvement/fig6-layer-roles.png)
*그림 6. 깊이별 층 역할 분포.*

## 실무 관점 시사점

- 자기개선 루프 설계에서 첫 결정은 <span style="background-color: #fff59d"><strong>무엇을 불변(invariant)으로 둘 것인가</strong></span>다. Meta^n은 이 불변 영역을 하나의 연산자로 최소화했다.
- 개선 대상을 답이 아니라 <span style="background-color: #fff59d"><strong>코드 + 실행 트레이스</strong></span>로 두면 층이 쌓일 때 정보가 누적된다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고 자료

- 논문: [arXiv:2608.24735](https://arxiv.org/abs/2608.24735)
- 코드: [github.com/minnesotanlp/meta-n](https://github.com/minnesotanlp/meta-n)
