---
title: "Σ-Mem: 다중 에이전트 시스템에서 '누구를 믿을 것인가'를 기억하는 방법"
date: 2026-08-02
draft: false
summary: "LLM 멀티에이전트 시스템의 핵심 문제—동료 에이전트의 답변을 신뢰할 수 있는가—를 정확도 기반 '신뢰 메모리'로 해결하는 Σ-Mem. Weyl 부등식으로 보장되는 안정적 온라인 갱신, 5개 Qwen 모델에서 검증된 일반화 성능, 그리고 동적 신뢰 이동에 대한 적응력까지."
tags:
  - agent
  - multi-agent
  - memory
  - LLM
  - reliability
  - coordination
  - harness
authors:
  - conan
---

> **원논문**: [Σ-Mem: An Online Reliability Memory for LLM-based Multi-Agent Systems](https://arxiv.org/abs/2607.27958)
> Peilin Feng, Suorong Yang, Soujanya Poria · DeCLaRe Lab, Nanyang Technological University · 2026년 7월

**다중 에이전트 시스템(MAS)이 실패하는 지점은 모델이 멍청해서가 아니다.** 중앙 모델이 동료 에이전트의 답변을 검증하지 못할 때, "누구를 믿을 것인가"라는 신뢰 결정에서 실패한다. Σ-Mem(시그마-멤)은 이 문제를 **정확도 기반 신뢰 메모리(reliability memory)**로 푼다—동료가 과거에 어떤 작업에서 맞았고 틀렸는지를 추적하고, 현재 작업에서 누구를 믿어야 할지를 스펙트럴하게 안정된 행렬로 기록한다.

## 핵심 통찰: "무슨 일이 있었나"가 아니라 "누가 믿을 만한가"

기존 LLM 에이전트 메모리 연구는 **콘텐츠 메모리(content memory)**에 집중한다—과거 대화, 관찰, 시도를 저장하고 검색한다. 단일 에이전트에서는 이것으로 충분하다. 하지만 다중 에이전트 시스템에서는 다른 차원의 기억이 필요하다.

> *"Content memory answers 'what happened.' Reliability memory answers 'who can be trusted, and when.'"* (원논문)

예를 들어보자. RAG 작업에서 지원 컨텍스트가 중앙 모델에 보이지 않는 상황에서, 세 동료 에이전트가 각각 "Berlin", "Berlin", "Zurich"라고 답했다. 다수결로 보면 Berlin이 이긴다. 하지만 Berlin이라고 답한 두 에이전트가 **상관된 오류(correlated error)**를 공유할 수 있다. 과거에 이 둘이 같이 틀린 적이 많았다면, "Zurich"라고 답한 소수 동료가 더 신뢰할 수 있다.

![Figure 1: Σ-Mem의 동기. 중앙 모델이 직접 검증할 수 없을 때, 동료의 과거 성능과 동료 간 관계가 신뢰 판단의 핵심 증거가 된다.](/images/2026-08-02-sigma-mem-multi-agent-reliability-memory/fig-1-p2.png)

Σ-Mem이 기록하는 두 가지 증거:

1. **역사적 역량 증거(historical competence evidence)**: 각 동료가 과거에 어떤 유형의 작업에서 얼마나 정확했는지
2. **동료 관계 증거(peer relationship evidence)**: 동료들이 서로 독립적으로 맞추는지, 아니면 같이 틀리는지

## 수학적 설계: Weyl 부등식으로 보장되는 안정성

### 기억 행렬의 갱신

각 동료 $p$에 대해 대칭 행렬 $M_p \in \mathbb{R}^{r \times r}$를 유지한다. 작업 $x_t$가 들어오면, 정답 라벨 $c_{p,t} \in \{+1, -1\}$을 받아 다음과 같이 갱신한다:

$$M_p^{(t+1)} = \gamma M_p^{(t)} + \eta \cdot c_{p,t} \cdot \boldsymbol{\phi}(x_t)\boldsymbol{\phi}(x_t)^\top$$

여기서 $\gamma \in (0,1)$은 감쇠 인자(decay factor), $\eta > 0$은 갱신 강도, $\boldsymbol{\phi}(x_t)$는 작업에서 추출된 단위 역량 방향(competence direction)이다. 갱신 항은 랭크-1 대칭 행렬이므로, $M_p$는 항상 대칭 행렬로 유지된다.

동료 관계 행렬 $G$도 비슷하게 갱신된다. 각 이벤트에서 동료들의 정답 여부 벡터를 평균 중심화(centering)한 후 외적으로 누적한다:

$$G^{(t+1)} = \gamma_G G^{(t)} + \eta_G \mathbf{q}_t \mathbf{q}_t^\top, \quad \text{diag}(G^{(t+1)}) = 1$$

$G_{p,q} > 0$이면 동료 $p$와 $q$가 같이 맞추는 경향이 있고, $G_{p,q} < 0$이면 반대 경향이 있음을 뜻한다.

### Weyl 부등식: 단일 이벤트가 기억을 망가뜨리지 못하는 이유

이 설계의 핵심은 **Weyl 부등식(Weyl's inequality)**이다. 실대칭 행렬 $M$에 섭동 $E$가 가해지면:

$$|\lambda_i(M + E) - \lambda_i(M)| \leq \|E\|_2, \quad \forall i$$

즉, 한 번의 이벤트 갱신이 기억 행렬의 스펙트럼(고유값 구조)에 미치는 영향은 섭동의 스펙트럴 노름으로 제한된다. 단일 노이즈가 전체 기억을 뒤집지 못한다는 수학적 보증이다.

동시에, Theorem 1은 **일관된 신호(persistent evidence)는 노이즈를 압도한다**는 것을 보인다. 충분한 시간이 지나면, 행렬의 최대 고유값은 동료의 진짜 역량을 반영한다:

$$\lambda_{\max}(M_p^{(T)}) \geq \eta \mu_p \left(\frac{1 - \gamma^T}{1 - \gamma}\right) - \eta \sqrt{\frac{8\log(2/\delta)}{1 - \gamma^2}}$$

시그널 항은 $T$와 함께 단조 증가하고, 노이즈 항은 $T$와 무관하다. 충분한 피드백이 누적되면 신뢰 판단이 노이즈가 아닌 진짜 역량에 기반하게 된다.

![Figure 2: Σ-Mem 전체 구조. 작업이 들어오면 각 동료의 기억 행렬에서 읽기 → 잔차 조향(residual steering) → 중앙 모델 평가 → 동료 관계 행렬과 결합하여 최종 선택. 사후 정확도 피드백으로 기억 갱신.](/images/2026-08-02-sigma-mem-multi-agent-reliability-memory/fig-2-p5.png)

## 읽기 인터페이스: 같은 기억, 세 가지 결정 방식

Σ-Mem의 강점은 기억 상태를 여러 방식으로 읽을 수 있다는 것이다.

### 1. 잔차 조향 동료 선택 (Steered Peer Selection)

각 동료 $p$에 대해 기억 행렬에서 읽은 벡터를 중앙 모델의 은닉층에 주입한다:

$$\tilde{X}_p^{(\ell)} = X^{(\ell)} + \delta_{p,t}(x_t)$$

이 잔차 조향(residual steering)은 어텐션 연산의 query/key/value를 변경하지만, 모델 파라미터 자체는 건드리지 않는다. 동료별로 다른 조향이 적용되므로, 같은 입력도 동료에 따라 다른 평가를 받는다. 중앙 모델은 "이 동료의 답변을 신뢰하는가?"라는 Yes/No 프롬프트로 평가한다.

### 2. 응답 없는 라우팅 (M-Route)

중앙 모델의 판단조차 필요 없다. 기억 행렬에서 직접 점수를 계산한다:

$$s_{p,t} = \boldsymbol{\phi}(x_t)^\top M_p^{(t)} \boldsymbol{\phi}(x_t)$$

가장 높은 점수의 동료에게 작업을 라우팅한다. 동료의 현재 응답을 아예 보지 않는다—과거 기록만으로 결정한다.

### 3. 신뢰도 가중 투표 (M-Weighted Voting)

같은 정답을 제시한 동료들의 신뢰도 점수를 합산하여 투표한다. 다수결과 달리, 각 동료의 가중치가 다르다.

## 실험 설정

- **중앙 모델**: Qwen3-0.6B, Qwen3-4B, Qwen3-8B, Qwen3.5-4B, Qwen3.5-9B (5개 크기)
- **동료 에이전트**: Gemma-3-4B-it(수학), Phi-4-mini-instruct(RAG), Qwen2.5-Coder-7B-Instruct(코드) — 도메인별 상호 보완적 강점
- **훈련 데이터**: 2,963개 작업 이벤트 (수학 추론 + RAG + 코드 생성)
- **평가 축**: (1) 반사실적(counterfactual) 신뢰 이동, (2) 미지의 동료 추가, (3) 미지의 도메인 일반화, (4) 다양한 선택 메커니즘

## 결과 1: 반사실적 공격—신뢰할 동료가 바뀌었을 때

반사실적 벤치마크는 "원래 수학을 잘하던 동료가 갑자기 틀리기 시작하면?"이라는 시나리오를 테스트한다. CF@ratio가 높을수록 더 극단적인 신뢰 이동이 일어난다.

**가장 극적인 결과**: Qwen3-0.6B에서 CF@90 조건에서 정확도가 46.22% → **71.10%**로 25포인트 폭등 후 회복. Σ-Mem 없는 기본 모델은 항상 같은 동료(p1, Gemma)를 선택하는 경향이 있어서, 신뢰할 동료가 바뀌면 무력해진다. Σ-Mem은 과거 기록을 바탕으로 "지금은 p1이 아니라 p3을 믿어야 한다"는 것을 학습한다.

![Table 3: OOD 도메인 일반화 결과. Σ-Mem은 30개 케이스 중 27개에서 기본 모델을 능가했다. BBH(복합 추론)에서 특히 큰 향상.](/images/2026-08-02-sigma-mem-multi-agent-reliability-memory/table-3-p9.png)

한 가지 흥미로운 예외: CF@50 조건에서는 Σ-Mem이 오히려 정확도를 떨어뜨린다. 이것은 버그가 아니라 **기억의 충실성(faithfulness)**을 보여주는 것이다. CF@50에서는 역사적 증거의 절반이 원래 동료를, 절반이 바뀐 동료를 지지한다—모호한 증거 스트림이 모호한 기억을 만드는 것은 당연하다.

## 결과 2: 더 많은 동료, 미지의 동료—일반화

Σ-Mem은 훈련 때 3명의 동료만 봤지만, 테스트 때 4명, 5명으로 늘려도 작동한다. 새 동료로 Llama-3.2-3B와 BitCPM-CANN-3B를 추가했다. 학습된 선택 메커니즘이 새 동료에게도 잘 이전된다—Σ-Mem의 학습 가능한 컴포넌트가 동료 수에 무관하게 공유되기 때문이다.

![Table 2: 동료 수 일반화. 3명으로 훈련하고 4명/5명으로 테스트. CF@0, CF@70, CF@90에서 일관된 향상.](/images/2026-08-02-sigma-mem-multi-agent-reliability-memory/table-2-p9.png)

## 결과 3: 미지의 도메인으로의 일반화

수학, RAG, 코드에서만 훈련했지만, 6개의 미지의 벤치마크(PIQA, MMLU, OpenBookQA, SciQ, BBH, SuperGLUE)에서 테스트했다.

- **30개 케이스 중 27개에서 기본 모델 능가**
- 특히 **BBH(Big-Bench Hard)**에서 압도적: Qwen3-4B 20.38% → **28.66%** (8.3포인트 향상), Qwen3-8B 19.29% → **28.17%** (8.9포인트 향상)
- MMLU, OpenBookQA, SuperGLUE에서도 일관된 향상

학습된 역량 방향(competence direction) $\boldsymbol{\phi}(x)$가 미지의 작업을 가장 가까운 학습된 방향에 매핑하여, 기억이 새 도메인으로 이전되는 것이다.

## 결과 4: 기억을 읽는 세 가지 방식 모두 효과적

| 선택 메커니즘 | 중앙 모델 사용 | 동료 응답 사용 | 특징 |
|---|---|---|---|
| Steered Selection | O | O | 가장 정확하지만 비용이 높음 |
| M-Route | X | X | 가장 빠름, 응답 생성 전 라우팅 |
| M-Weighted Vote | X | 정규화만 | 동료 응답을 평가하지 않음 |

![Table 4: 선택 메커니즘 비교. M-Route와 M-Vote는 중앙 모델 판단 없이도 다수결과 최고 고정 동료를 능가한다.](/images/2026-08-02-sigma-mem-multi-agent-reliability-memory/table-4-p10.png)

핵심 발견: **M-Route는 중앙 모델을 전혀 사용하지 않고도, 전체 OOD 데이터셋에서 다수결 투표와 최고 고정 동료(best fixed peer)를 능가한다.** 이는 기억 상태 자체가 이미 신뢰 판단에 충분한 정보를 담고 있음을 보여준다.

## 결과 5: 피드백이 많을수록 정확해진다

![Figure 3: 피드백 가용성 비율에 따른 OOD 정확도. Qwen3.5-4B와 Qwen3.5-9B 모두 피드백이 많아질수록 정확도가 일관되게 향상된다.](/images/2026-08-02-sigma-mem-multi-agent-reliability-memory/fig-3-p10.png)

피드백 비율이 20%에서 100%로 증가함에 따라 정확도가 일관되게 향상된다. 이는 Σ-Mem이 **누적적으로 유의미한 신뢰 정보를 축적**한다는 것—단순히 최근 피드백에 반응하는 것이 아니라, 역사 전체에서 패턴을 학습한다는 것을 보여준다.

## 왜 중요한가: 에이전트 코디네이션의 기반층

Σ-Mem이 제안하는 것은 단순한 메모리 모듈이 아니다. 다중 에이전트 시스템에서 **신뢰(trust)를 명시적으로 모델링하고 추적하는 패러다임**이다.

현재 대부분의 MAS 프레임워크(예: LangGraph, CrewAI, AutoGen)는 동료 선택을 프롬프트나 고정된 휴리스틱에 의존한다. "가장 똑똑한 모델에게 물어봐라" 또는 "다수결로 결정하라". 하지만 실제 환경에서는:

1. **동료의 역량이 작업 유형에 따라 다르다**: 수학을 잘하는 에이전트가 RAG에서는 최악일 수 있다
2. **동료 간 상관 오류가 존재한다**: 비슷한 모델들은 비슷한 실수를 한다
3. **역량이 시간에 따라 변한다**: 모델 업데이트, 컨텍스트 변화, 도구 가용성에 따라 신뢰도가 달라진다

Σ-Mem은 이 세 가지 문제를 모두 하나의 수학적으로 안정된 프레임워크에서 다룬다.

## 한계와 향후 방향

논문이 솔직하게 인정하는 한계:

- **CF@50 문제**: 모호한 증거 스트림에서 기억도 모호해진다. 역사적 가이드와 현재 응답 증거를 적응적으로 균형 잡는 읽기 방식이 필요하다.
- **외부 정답 피드백 의존**: 메모리 갱신에 정확도 라벨이 필요하다. 실제 환경에서는 정답을 얻기 어려울 수 있다.
- **동료 수 확장**: 논문은 5명까지 테스트했지만, 수십~수백 개의 에이전트/도구로 확장할 때의 행동은 미탐구다.

## 더 실습해보고 싶은 분들께

다중 에이전트 코디네이션, 동적 신뢰 추론, 그리고 루프 안에서의 자가 개선은 단순한 프롬프트 엔지니어링을 넘어 시스템 설계가 되어야 합니다. 실제 에이전트 하네스를 구성하고 신뢰 메커니즘을 실험해보고 싶다면 아래 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 도구 사용을 실전에서 설계하는 50가지 사례
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 멀티에이전트 루프의 코디네이션과 피드백 구조를 깊이 있게 다루는 강의

---

> 📄 **원논문**: [Σ-Mem: An Online Reliability Memory for LLM-based Multi-Agent Systems](https://arxiv.org/abs/2607.27958) — Peilin Feng, Suorong Yang, Soujanya Poria. DeCLaRe Lab, NTU. 2026년 7월.
