---
title: "Harness-G: RL 검색 에이전트의 '검색 등가 붕괴'를 발견하고 액션 인터페이스를 다시 설계하다"
date: 2026-08-01
tags:
  - agent
  - harness
  - RL
  - RAG
  - search-agent
  - retrieval
  - GRPO
  - tool-use
source_url: "https://arxiv.org/abs/2607.27652"
github_url: "https://github.com/7HHHHH/Harness-G"
authors:
  - Yanning Hou
  - Haoyuan Chen
  - Sihang Zhou
  - Xiaoshu Chen
  - Xirui Liu
  - Duanyang Yuan
  - Lingyuan Meng
  - Quan Liu
  - Jian Huang
institution: "CASIA / UC Merced / Adobe Research"
---

# Harness-G: RL 검색 에이전트의 '검색 등가 붕괴'를 발견하고 액션 인터페이스를 다시 설계하다

> **핵심 발견**: Search-R1 학습 중에 롤아웃들이 서로 다른 검색어를 생성하지만, 실제로 검색되는 증거는 점점 같아진다. 이 **"검색 등가 붕괴(retrieval-equivalence collapse)"**가 GRPO의 within-group advantage를 무력화시킨다. Harness-G는 검색 액션 자체를 그래프 기반 유한 선택으로 재설계하여 이 문제를 해결한다.

RL 검색 에이전트(Search-R1, R1-Searcher, DeepResearcher)는 자연어 검색어를 생성하고 최종 답변 보상으로 다중 턴 상호작용을 최적화한다. 학습이 불안정하고, 반복 검색이 발생하며, within-group advantage가 사라지는 문제는 널리 알려져 있다. 기존 연구는 주로 **보상 신호를 조밀하게** 만드는 방향(process reward, information gain, 트리 탐색)으로 접근했다.

Harness-G는 다른 질문을 던진다: **검색 액션 자체가 RL 최적화에 적합한 형태인가?**

## 검색 등가 붕괴: 다양한 검색어, 동일한 결과

![Figure 1: 검색 등가 붕괴 — (a) 검색어 다양성은 높게 유지되지만 검색 결과 다양성은 붕괴한다. (b) 매칭된 전환 조건에서 액션 메뉴가 더 많은 검색-구별 가능한 결과를 보존한다.](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig1-retrieval-collapse.png)

논문의 가장 중요한 관찰은 **검색 등가 붕괴(retrieval-equivalence collapse)** 현상이다. Search-R1 학습 과정에서:

1. **검색어 형태 다양성(query-form diversity)**: 같은 질문에 대해 롤아웃들이 서로 다른 검색어 문자열을 계속 생성한다.
2. **검색 결과 다양성(retrieval-outcome diversity)**: 하지만 이 검색어들이 실제로 검색해오는 증거 집합은 점점 동일해진다.
3. 학습 스텝 30 기준으로, 여러 검색-등가 클래스에 걸쳐 있는 롤아웃 그룹의 비율이 86%에서 10% 미만으로 떨어진다.

이것이 왜 문제인가? GRPO는 같은 입력에 대한 여러 롤아웃 간의 보상 차이로 어떤 행동이 더 나은지 추론한다. 그런데 모든 롤아웃이 같은 증거를 검색해오면, 보상 차이는 검색 품질이 아니라 ** downstream reasoning**에서 발생한다. 검색 행동에 대한 크레딧을 정확하게 할당할 수 없게 된다.

### 두 가지 직접적 결과

- **Advantage 소멸**: 같은 증거 → 같은 답 → 같은 보상 → within-group advantage = 0. 롤아웃이 8개여도 실제로 의미있는 비교 샘플은 1-2개뿐.
- **검색 크레딧 교란**: 같은 증거를 검색했음에도 답이 다르면, 그 차이는 검색 품질이 아니라 답변 생성 능력에서 온 것인데, 이를 검색 행동에 귀인시키면 잘못된 신호가 된다.

핵심 통찰: **문제는 보상 신호의 조밀도가 아니라, 액션 인터페이스 자체에 있다.** 자유 형식 검색어는 동일한 검색 의도에 대해 무한히 많은 문자열 변형을 허용하고, 이 다대일 매핑이 GRPO의 전제를 무너뜨린다.

## Harness-G: 그래프 구조화된 검색 환경

![Figure 2: 검색 인터페이스 재설계 — 왼쪽은 자유 검색어 인터페이스, 오른쪽은 Harness-G의 메뉴 인터페이스. 정책은 Select/Lookup/Answer 중 하나를 선택한다.](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig2-interface-redesign.png)

Harness-G의 해결책은 단순하면서도 근본적이다: **자유 형식 검색어 생성을 유한 액션 선택으로 바꾼다.**

### 삼분 그래프(Tripartite Graph)

오프라인 단계에서 Harness-G는 코퍼스를 프로그램적으로 처리하여 **문단-문장-엔티티 삼분 그래프**를 구성한다:

- **문단-문장 엣지**: 각 문장(최소 증거 단위)을 문서 컨텍스트에 연결
- **문장-엔티티 엣지**: 엔티티 멘션을 기록하여 문장/문서 간 브리지 역할
- **문장-문장 엣지**: 인접 문장을 연결하여 로컬 컨텍스트 확장 가능
- **엔티티-엔티티 엣지**: 동일/유사 엔티티를 표면 정규화, 약어 매칭, 임베딩 이웃으로 연결

**중요한 점**: 이 그래프는 생성적 LLM을 사용한 팩트/관계 추출이 아니다. 문장 분할, 엔티티 인식/정규화, 밀집 인코딩만으로 준선형 시간에 구축된다. GraphRAG 시스템과 달리 API 비용이 $0이다.

### 메뉴 환경: 세 가지 액션

온라인에서 정책은 세 가지 유한 액션 중 하나를 선택한다:

| 액션 | 의미 | 환경 동작 |
|------|------|-----------|
| **Select(s)** | 가시적 문장 s를 확정 증거에 추가 | C_{t+1} = C_t ∪ {s} |
| **Lookup(e)** | 엔티티 e 주변 정보 검색 | 환경이 결정론적 쿼리 생성 및 실행 |
| **Answer** | 검색 종료, 확정 증거로 답변 생성 | C_t로부터 ŷ 생성 |

핵심은 **정책은 오직 "어떤 증거/엔티티를 추구할 것인가"라는 의미적 결정만 내리고**, 검색어 문자열 생성은 환경이 결정론적으로 수행한다는 것이다. Lookup의 경우, 식별자는 타겟 엔티티이지 생성된 문자열이 아니므로, 서로 다른 Lookup은 정의상 서로 다른 타겟을 추구한다.

### 세 가지 보장

메뉴 설계로부터 세 가지 속성이 자동으로 따른다:

1. **유한성(Finiteness)**: |M_t|는 가시적 문장 cap K_s와 Lookup 후보 cap K_e로 bounded
2. **검증 가능성(Verifiability)**: 모든 액션은 명시적 타입과 타겟을 가짐. 잘못된 액션은 사후 처벌이 아니라 feasible set에서 차단
3. **미리보기 가능성(Previewability)**: 전환이 결정론적 인덱스 연산이므로, 메뉴의 어떤 후보도 read-only로 확장 가능. 실제 상태를 변경하지 않고 "이 액션을 선택하면 어떤 문장이 추가되는가"를 볼 수 있음

## SNC: 구조화된 비근시적 크레딧

![Figure 3: Harness-G 전체 파이프라인 — 그래프 구축부터 정책 최적화까지. SNC는 동일 상태 대안을 미리보기하고, 확정된 답안 스코어러로 채점하며, 의존성 엣지를 따라 지연 크레딧을 전파한다.](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig3-pipeline.png)

메뉴의 미리보기 가능성을 활용하여 **Structured Non-myopic Credit (SNC)** 을 설계한다. SNC는 외부 보상 모델이나 추가 롤아웃 없이, 환경 연산만으로 계산된다.

### Frontier-Relative Advantage

동결된 답안 스코어어(frozen answerer) g를 사용하여, 관찰된 증거가 정답을 얼마나 잘 지원하는지 측정한다:

- pt(a) = g(Ot ∪Ũ(a)) − g(Ot): 액션 a의 한계 이득
- 동일 상태의 대안들 ℱ_t의 평균 이득 p̄_t를 baseline으로 사용
- **Frontier-relative advantage**: rt_fr = pt(at) − p̄_t

이 설계의 의미: 여러 메뉴 항목이 동등한 증거를 추가하면 이득이 비슷해져서 rt_fr ≈ 0이 된다. 정책은 표면적 선택에 대해 보상받지 않는다. **의미 있는 크레딧을 받으려면 동일 상태의 실제 대안들을 능가해야 한다.**

### Enablement Credit

초기 Lookup이 나중에 유용한 브릿지 엔티티를 발견할 수 있다. per-step 한계 이득은 이런 지연 효과를 체계적으로 과소평가한다. SNC는 의존성 엣지(t,u)를 따라 다운스트림 이득을 이전 액션으로 전파한다.

## 실험 결과: 6개 QA 벤치마크에서 압도적

![Figure 4: 6개 QA 벤치마크 메인 결과 — 1.5B와 3B 스케일에서 Harness-G가 일관되게 최고 F1 달성](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig4-results.png)

### 메인 결과 (RQ1)

6개 QA 벤치마크(NQ, TriviaQA, HotpotQA, 2Wiki, MuSiQue, Bamboogle)에서:

| 모델 (1.5B) | 평균 F1 |
|-------------|---------|
| **Harness-G** | **50.08** |
| Graph-R1 | 39.34 |
| Search-R1 | 36.22 |

| 모델 (3B) | 평균 F1 |
|-----------|---------|
| **Harness-G** | **55.33** |
| Graph-R1 | 51.35 |
| Search-R1 | 48.90 |

1.5B에서 Graph-R1 대비 **+10.74점**, 3B에서 **+3.98점** 리드. 작은 모델일수록 구조화된 인터페이스의 이점이 크다.

### 액션 메뉴 vs SNC 기여도 분리 (RQ2)

![Figure 5: 액션 메뉴와 SNC 각각의 기여도를 분리한 제어 실험](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig5-ablation.png)

제어 실험으로 두 혁신의 기여를 분리:

- **액션 메뉴만(SNC 없음)**: free-query → 메뉴 교체만으로도 retrieval-equivalence collapse가 완화되고 F1 상승
- **SNC만(자유 검색어)**: 약간의 개선만 — 미리보기가 가능한 유한 메뉴 없이는 frontier 비교가 무의미
- **둘 다**: 최대 성능. 두 요소가 상호 보완적

핵심 통찰: **액션 인터페이스 설계와 크레딧 할당 설계가 상호 의존적이다.** 메뉴 없이 SNC를 적용하면, 미리볼 수 있는 유한 대안이 없어 frontier 비교가 무의미해진다.

### 학습 안정성 (RQ3)

![Figure 6: 학습 안정성 — 6개 데이터셋에 걸쳐 F1이 지속적 상승, 그래디언트 노름 bounded 유지](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig6-training-stability.png)

- 3B 모델 6개 실행 모두 후반 붕괴 없이 안정적 상승
- Qwen2.5-3B, Qwen3.5-4B, Llama-3.2-3B 모두 동일 GRPO 레시피에서 경쟁력 도달 (백본 비의존적)
- GRPO, PPO, REINFORCE++, DAPO 모두 안정적 상승 (RL 알고리즘 비의존적)

### 상호작용 효율성 (RQ4)

![Figure 8: 상호작용 턴 수와 응답 길이 — Harness-G가 더 많은 턴을 사용하지만 응답은 더 짧다](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig8-interaction-efficiency.png)

- **더 많은 턴, 더 짧은 응답**: 학습 후반 Harness-G는 Search-R1보다 더 많은 턴(3.6 vs 2.3)을 사용하지만, 응답 토큰은 더 적음(2.5k vs 4.3k)
- **SNC 오버헤드 제한**: 추가 롤아웃 없이 스텝당 wall-clock 9-11% 증가만
- **저렴한 구축**: 그래프 API 비용 $0 (Graph-R1은 $2.81-$4.14), 코퍼스 1K 토큰당 0.12초

### 크로스 데이터셋 일반화 (RQ5)

![Figure 9: 6개 데이터셋 교차 검증 — Harness-G가 30쌍 중 21쌍 승리, 평균 O.O.D. F1 +3.29](/images/2026-08-01-harness-g-graph-structured-search-agent-retrieval/fig9-cross-dataset.png)

하나의 데이터셋에서 학습하고 나머지 5개에서 평가하는 설정:

- Harness-G는 30개 off-diagonal 쌍 중 **21개 승리**
- 평균 O.O.D. F1: 44.10 → 47.38 (+3.29)
- 특히 multi-hop 타겟에서 더 큰 이득

## 분석: 왜 이것이 중요한가

### 액션 공간 설계 = 보상 설계와 동등한 축

이 논문의 가장 근본적인 기여는 **검색 에이전트 최적화에서 액션 인터페이스 설계가 보상 설계와 동등한 중요성을 가진다**는 점을 실험적으로 입증한 것이다. 기존 연구는 "어떻게 평가할 것인가"에 집중했지만, Harness-G는 "무엇을 선택하게 할 것인가"가 동등하게 중요함을 보여준다.

### 검색 등가 붕괴의 일반성

이 현상은 Search-R1에만 국한되지 않을 수 있다. 자유 형식 출력을 환경 액션으로 사용하는 모든 RL 에이전트(코드 생성 에이전트, 툴 사용 에이전트)에서 유사한 형태의 앨리어싱이 발생할 수 있다. "출력은 다양한데 실제 효과는 같은" 현상은 에이전트 RL의 구조적 문제이다.

### 메뉴 설계의 실용적 매력

Harness-G의 그래프 구축은 LLM 기반 팩트 추출이 필요 없다. API 비용 $0, 준선형 시간. 이는 GraphRAG 시스템들이 LLM으로 코퍼스 전체를 처리해야 하는 병목(수십억 토큰 비용)을 회피한다. 실제 배포 관점에서 매우 매력적이다.

### 한계

- 텍스트 전용: 멀티모달 증거(이미지, 표, 비디오)로의 확장은 향후 과제
- 코퍼스가 사전 구축된 그래프 형태여야 함(스트리밍 웹 검색에는 직접 적용 어려움)
- SNC의 frozen answerer가 학습되는 정책과 정렬되지 않을 경우 크레딧 품질 저하 가능성

## 더 실습해보고 싶은 분들께

에이전트의 액션 인터페이스를 다시 설계하고, 구조화된 크레딧 할당을 실험해보고 싶다면 다음 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 루프와 툴 사용 패턴을 실습하며 체감할 수 있습니다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — RL 에이전트의 보상 설계와 루프 구조를 다루는 강의로, Harness-G의 SNC 설계 원칙과 직접 연결됩니다.

---

> **논문**: [Harness-G: A Graph-Structured Harness for Search Agents](https://arxiv.org/abs/2607.27652)
> **코드**: [github.com/7HHHHH/Harness-G](https://github.com/7HHHHH/Harness-G)
> **저자**: Yanning Hou, Haoyuan Chen, Sihang Zhou et al. (CASIA / UC Merced / Adobe Research)
