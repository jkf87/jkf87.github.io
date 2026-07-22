---
title: "SWE-Pruner Pro: 코딩 에이전트가 스스로 컨텍스트를 가지치기한다 — 외부 모델 없이 내부 표현만으로"
date: 2026-07-22T10:00:00+09:00
draft: false
tags: ["agent", "coding-agent", "context-engineering", "LLM", "harness", "tool-use"]
categories: ["AI Agents", "LLM"]
source_url: "https://arxiv.org/abs/2607.18213"
github_url: "https://github.com/Ayanami1314/swe-pruner-pro"
---

> **한 줄 요약**: 코딩 에이전트가 도구 출력을 읽을 때 이미 내부 표현(hidden state)에 "어떤 줄이 중요하고 어떤 줄이 불필요한지"를 인코딩하고 있다. SWE-Pruner Pro는 이 신호를 가벼운 헤드로 직접 읽어내어, 별도의 외부 모델 없이 최대 39% 토큰을 절약하면서도 작업 품질을 유지한다.

## 배경: 코딩 에이전트의 토큰 폭식 문제

SWE-Bench 같은 코드 수정 벤치마크에서 에이전트 한 궤적(trajectory)의 토큰 예산 중 **70% 이상**이 도구 출력(`cat`, `grep`, `ls`, `python` 등)에 소비된다. 파일을 읽고, 검색하고, 실행 결과를 보는 과정에서 컨텍스트 창이 빠르게 채워지고, 이는 단순한 비용 문제가 아니라 긴 컨텍스트 성능 저하(long-context degradation)로 이어진다.

기존 해결책은 크게 두 갈래였다:

1. **범용 압축**: perplexity나 구문 구조로 토큰을 점수 매겨 잘라내는 방식 (LLMLingua, LongCodeZip 등). 에이전트의 현재 의도를 반영하지 못한다.
2. **작업 특화 가지치기**: SWE-Pruner가 대표적. 별도의 점수 매기는 모델을 달고, 에이전트가 매 턴마다 "목표 힌트(goal-hint)"를 명시적으로 작성해야 한다. 즉, 가지치기 신호를 **에이전트 바깥**에서 구한다.

![Figure 1: 기존 방식 vs SWE-Pruner Pro](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-1-p2.png)

## 핵심 발견: 에이전트가 이미 알고 있다

저자들의 출발점은 단순한 질문이었다: "도구 출력을 읽는 과정은 어텐션 가중치가 적용된 forward pass다. 그렇다면 백본 모델의 은닉 상태(hidden state)에 이미 어떤 줄이 중요한지 인코딩되어 있지 않을까?"

이를 검증하기 위해 Qwen3-Coder-Next의 마지막 층 hidden state에 선형 프로브(linear probe)를 적용해 보았다.

![Figure 2: 선형 프로브 결과 — hidden state 공간에서 keep/prune이 구분된다](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-2-p3.png)

결과는 명확했다. **AUC 0.83, F1 0.63** — 단순한 로지스틱 회귀만으로도 보존할 줄과 가지치기할 줄이 구분된다. 다수 클래스의 F1 상한이 0.46인 점을 고려하면 충분한 분리 신호다. 가지치기에 필요한 정보가 이미 백본 내부에 존재한다.

## SWE-Pruner Pro의 구조

SWE-Pruner Pro는 이 발견을 실제 시스템으로 구현한다. 핵심은 **에이전트 백본의 prefill을 공유하는 가벼운 헤드**다.

![Figure 3: 전체 파이프라인 개요](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-3-p4.png)

동작 방식은 다음과 같다:

1. **각 턴 t**: 에이전트가 도구 호출 $c_t$를 발행하고 환경이 응답 $r_t$를 반환한다.
2. **Prefill 공유**: 백본은 $[H_{t-1}, c_t, r_t]$를 prefill하는데, 이때 $r_t$ 토큰들의 hidden state $h_i$가 자연스럽게 생성된다. SWE-Pruner Pro는 이 hidden state를 "무료로" 읽어낸다.
3. **헤드 예측**: 가벼운 헤드가 각 토큰의 hidden state를 keep-or-prune 로짓으로 변환하고, 줄 단위 다수결로 최종 결정을 내린다.
4. **압축 적용**: 가지치기된 $\tilde{r}_t$가 다음 턴의 컨텍스트에 들어간다.

![Figure 4: 헤드 아키텍처 상세](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/fig-4-p5.png)

### 두 가지 핵심 설계 선택

**길이 인지 임베딩 (Length-Aware Embedding)**: 도구 응답이 5줄일 때와 300줄일 때 가지치기 비용이 다르다. 5줄에서 몇 줄을 잘못 지우면 치명적이지만, 300줄에서는 무방하다. 헤드에 줄 수 $N$에 대한 학습된 임베딩 $\mathbf{e}(N)$을 더해주어, 길이에 따라 다르게 결정하도록 만든다.

**샘플 단위 균형 focal loss (Per-Sample Balanced Focal Loss)**: 전체 코퍼스의 보존 비율은 약 30%다. 하지만 샘플마다 다르다 — 100줄 중 3줄만 보존하는 샘플의 그 3줄은 강한 신호를 담고 있고, 100줄 중 90줄을 보존하는 샘플의 10줄은 안전하게 지울 수 있다. 일반적인 교차 엔트로피는 전역 보존 비율에 편향되어 극단적 비율의 샘플에서 학습 신호가 희석된다. 저자들은 keep 토큰과 prune 토큰의 loss를 샘플 내에서 따로 평균내어 동일 가중치로 결합한다.

## 실험 결과: 일관된 절약, 미미한 품질 저하

4개 멀티턴 벤치마크 (SWE-QA, SWE-QA-Pro, Oolong, SWE-Bench Verified)에서 2개 오픈웨이트 백본 (Qwen3-Coder-Next, MiMo-V2-Flash)으로 평가했다.

![Table 1: 읽기 전용 멀티턴 벤치마크 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/table-1-p6.png)

**SWE-QA-Pro (Qwen3-Coder-Next)**: 토큰 39% 절약, 점수 +0.24 상승 — 품질 저하 없이 오히려 개선.
**Oolong (MiMo-V2-Flash)**: 토큰 30% 절약, 정확도 +2.2점 상승.
**SWE-Bench Verified (MiMo-V2-Flash)**: resolve rate +3.8% 상승.

![Table 2: SWE-Bench Verified 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/table-2-p8.png)

모든 벤치마크에서 품질 저하 없이 토큰을 절약한 유일한 방법론이었다. 반면 LLMLingua2는 품질이 크게 떨어지고, RAG는 절약률이 미미하다.

### 소거 실험

![Table 3: 소거 실험 결과](/images/2026-07-22-swe-pruner-pro-agent-self-pruning/table-3-p8.png)

Per-sample balanced focal loss가 판정자 점수 7.08로 가장 높았고, 길이 인지 임베딩은 F1은 동일하지만 판정자 점수를 6.86에서 7.08로 올렸다. F1만 보면 차이가 없어도, 실제로 유용한 결과인지는 판정자가 더 잘 포착한다.

### 지연 분석

프루닝 헤드가 추가하는 wall time은 전체 생성 시간의 **15.0%** (p50=14.7%, p95=34.8%)다. 백본의 prefill을 재사용하므로 추가 forward pass가 필요 없고, 헤드 자체는 매우 가볍다. 이 비용은 토큰 절약으로 인한 후속 턴들의 감소로 상쇄된다.

## 왜 중요한가: 에이전트-환경 경계에서의 압축

기존 컨텍스트 관리 방법들은 대부분 에이전트의 **상호작용 이력**을 요약하거나 잘라내는 방식이었다 — 트라젝토리 오버플로우 시 요약, 하드 트렁케이션, 마스킹 등. 이들은 모두 이미 컨텍스트에 들어온 정보를 사후에 처리한다.

SWE-Pruner Pro는 한 단계 **업스트림**에서 작동한다 — 도구 출력이 히스토리에 들어가기 전에, 에이전트-환경 경계에서 압축한다. 그리고 그 압축 신호를 외부에서 끌어오지 않고, 에이전트가 이미 수행한 연산의 부산물에서 읽어낸다.

> 백본이 관찰을 읽으면서 수동적으로 형성한 표현이, 이미 이전 접근법들이 추가 모델 호출로 복구하려 했던 관련성 판단을 인코딩하고 있다. (논문 결론부)

이는 에이전트 하네스 설계에 대한 더 넓은 시사점을 갖는다: 에이전트 주변에 부가 장치를 쌓는 대신, 에이전트가 이미 형성한 내부 표현을 읽어내는 것만으로 충분할 수 있다.

## 한계

- **오픈웨이트 전용**: hidden state에 접근해야 하므로 현재는 오픈웨이트 모델만 지원한다. 클로즈드 모델(GPT, Claude 등)에는 적용할 수 없다.
- **백본별 헤드 재학습**: 새로운 백본마다 헤드를 다시 학습해야 하지만, 백본 자체는 완전히 동결되므로 파인튜닝이 필요 없다.
- **Python 중심**: 벤치마크가 Python에 집중되어 있으나, Oolong(자연어)에서도 품질 유지가 확인되어 언어 무관 가능성이 있다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 컨텍스트 엔지니어링을 더 깊이 다룬 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고문헌

- Shi et al., "SWE-Pruner Pro: The Coder LLM Already Knows What to Prune," arXiv:2607.18213, 2026.
- Wang et al., "SWE-Pruner: Context Pruning for Coding Agents," 2026.
- 프로젝트 저장소: https://github.com/Ayanami1314/swe-pruner-pro
