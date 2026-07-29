---
title: "동결된 모델을 그대로 쓰면서 하네스만 학습한다 — 729가지 구성을 돌려본 결과, 정적 기준선이 이겼다"
slug: 2026-07-29-frozen-agent-harness-control-system
publishDate: 2026-07-29T19:05:00+09:00
tags:
  - agent
  - harness
  - LLM
  - reinforcement-learning
  - contextual-bandit
  - DSPy
  - optimization
  - automation
  - loop
  - tool-use
draft: false
---

**프로덕션 LLM 에이전트에서 모델이 아니라 하네스가 성능을 결정한다면, 하네스를 최적화하는 올바른 방법은 무엇일까?** 729가지 구성 공간에 contextual bandit과 REINFORCE를 적용했지만, 예상을 깨고 DSPy 정적 기준선이 모든 도메인에서 승리했다. 이 논문은 그 이유를 추적하고, 실무자를 위한 배포 레시피를 제시한다.

---

## 핵심 질문: 모델이 고정되어 있을 때 무엇을 최적화할 것인가

2026년 프로덕션 환경의 LLM 에이전트는 대부분 **"동결된 모델(frozen model) + 하네스(harness)"** 구조다. 하네스란 프롬프트 템플릿, 도구 세트, 메모리/검색 계층, 계획 전략, 검증 정책을 하나로 묶은 래퍼(wrapper)를 말한다.

Zhang et al. (2026)의 "Binding Constraint Thesis"에 따르면, **롱호라이즌 에이전트 평가에서 모델 선택보다 하네스 구성이 더 큰 성능 분산을 설명한다.** 그렇다면 하네스를 최적화하는 방법은 크게 세 갈래다:

1. **Meta-Harness (Lee et al., 2026)**: Claude Code 기반 에이전트가 소스 코드와 실행 추적을 읽고 새 하네스 코드를 제안하는 루프. 강력하지만 비싸고 감사하기 어렵다.
2. **HyperAgents (Meta AI, 2026)**: 태스크 에이전트와 메타 에이전트를 하나의 자기 참조 프로그램으로 융합. 전체 코드베이스를 읽고 수정하고 재실행한다. Darwin-Gödel-Machine 스타일.
3. **이 논문의 접근**: 하네스를 **작고 고정된, 사람이 읽을 수 있는 이산 행동 공간**으로 정의하고, 그 위에서 고전적인 RL(ε-greedy contextual bandit + REINFORCE)로 정책을 학습한다.

Debjyoti Paul이 작성한 이 논문(arXiv:2607.25415)의 핵심 주장은 단순하다: **모델 API가 블랙박스인 것이 일반적인 프로덕션 환경에서는, 감사 가능하고 저렴하며 모든 chat-completions 엔드포인트에서 작동하는 접근이 필요하다.**

---

## 하네스를 6개 레버로 분해하다

이 논문의 가장 독창적인 설계 결정은 하네스를 **6개의 이산 레버(lever)**로 분해한 것이다:

| 레버 | 선택지 |
|---|---|
| **prompt_style** | direct, structured, reflective |
| **tool_policy** | never, when_needed, always |
| **memory_policy** | none, similar_successes, successes_and_failures |
| **planning_policy** | none, brief_plan, plan_and_revise |
| **verification_policy** | none, final_check, stepwise |
| **max_steps** | 2, 4, 6 |

3⁵ × 3 = **729가지 구성**. 각 구성은 사람이 검토한 이름이 붙어 있으므로, 회귀가 발생하면 정확히 어느 레버 때문인지 즉시 파악할 수 있다. 이것이 임의 코드 생성 방식(Meta-Harness, HyperAgents)과의 근본적 차이다.

DSPy(Khattab et al., 2024)를 컨텍스트 어셈블러로 사용한다. prompt_style에 따라 DSPy Signature의 명령어가 바뀌고, planning_policy에 따라 Predict, ChainOfThought, 또는 2패스 초고-수정 모듈이 선택된다. memory_policy는 과거 궤적의 few-shot 예시 수를 제어하고, verification_policy는 응답 전 자기 검증 호출을 추가한다.

---

## 다목적 보상 함수: 정확도만으로는 부족하다

보상 함수는 설계의 하이라이트다:

$$R = w_s \cdot \text{success} + w_v \cdot \text{verifier\_score} + w_c \cdot \text{compliance} - w_u \cdot \text{unsupported\_claims} - w_\$ \cdot \text{tokens}/1000 - w_\ell \cdot \text{latency}/1000$$

**정확도뿐 아니라 정책 준수(compliance), 근거 없는 주장(unsupported claims), 비용(tokens), 지연 시간(latency)을 1등급 신호로 다룬다.** 이는 단일 메트릭(예: 작업 성공률)만 최적화하는 Meta-Harness나 HyperAgents와의 명시적 차이점이다.

검증기(verifier)는 도메인별로 결정된다:
- **코딩**: HumanEval 유닛 테스트 실행
- **도구 사용**: mock 백엔드 상태 diff
- **검색 QA**: HotpotQA 정답 정확 매칭 + token-F1

---

## 예상치 못한 결과: 정적 기준선이 모든 곳에서 이겼다

![Figure 1: 최적화 방식별 신뢰도와 비용(토큰당) 비교. DSPy-static이 모든 도메인에서 가장 높은 성공률과 가장 낮은 토큰 비용을 동시에 달성한다.](/images/2026-07-29-frozen-agent-harness-control-system/results-comparison.png)

실험 매트릭스: 4개 최적화기(random, DSPy-static, bandit, REINFORCE) × 3개 도메인 × 2개 모델(Ollama qwen2.5:7b, AWS Bedrock Haiku). 총 2,460 에피소드 + Bedrock Sonnet 스팟 체크 960 에피소드. 전체 연구 비용 **$7.62**.

헤드라인 결과는 저자 자신도 예상하지 못한 것이다:

> **모든 도메인, 모든 모델에서 DSPy 정적 기준선이 온라인 적응형 컨트롤러(bandit, REINFORCE)와 일치하거나 능가했다.** 그것도 대부분 훨씬 적은 토큰 비용으로.

구체적으로, Bedrock Haiku에서 도구 사용 도메인의 경우:
- **DSPy-static**: 96% 성공률, 에피소드당 285 토큰
- **REINFORCE**: 62% 성공률, 에피소드당 680 토큰

이것은 일반적인 결과가 아니다. 논문은 이를 숨기지 않고 직접 보고한다.

---

## 왜 정적 기준선이 이겼는가: 샘플 효율성의 함정

원인을 추적하기 위해 저자는 도구 사용 / Bedrock Haiku에서 **300 에피소드**(원래 예산의 5-12배)를 추가로 실행했다. 결과:

| 구간(50에피소드) | bandit | REINFORCE |
|---|---|---|
| 1-50 | 0.62 | 0.60 |
| 51-100 | 0.58 | 0.60 |
| 101-150 | 0.66 | 0.70 |
| 151-200 | 0.60 | 0.62 |
| 201-250 | 0.62 | 0.66 |
| 251-300 | 0.68 | 0.74 |

300 에피소드 후에도 두 컨트롤러는 0.61-0.65(bandit), 최대 0.74(REINFORCE)에 머문다. 같은 설정에서 DSPy-static은 0.96이다.

**핵심 통찰**: Majumdar (2026)의 이론적 결과와 일치한다 — 729차원의 이산 행동 공간에서 밀집 정책(dense policy)이 샘픔 효율적이 되려면 Ω(M), 즉 729 에피소드 이상이 필요하다. 실제 예산(25-60 에피소드)은 이보다 한참 부족하다.

반면 DSPy BootstrapFewShot은 **지표 가이드 검색(metric-guided search)**으로, 처음부터 그럴듯한 예시 세트만 제안한다. 균등 사전 확률에서 출발하는 온라인 컨트롤러가 도달하기 어려운 영역에 이미 위치해 있는 것이다.

---

## 발견하고 고친 3가지 함정

이 논문의 솔직함이 돋보이는 부분이다. 저자는 세 가지 실제 함정을 보고하고, 각각을 어떻게 고쳤는지 설명한다.

### 1. 콜드스타트 함정: bandit이 0%에서 시작했다

모든 Q값을 0으로 초기화하자, numpy.argmax가 동점을 action index 0으로 결정론적으로 처리했다. 우연히 index 0은 `tool_policy=never` 설정이었고, 도구가 없으면 도구 사용 작업을 풀 수 없다. ε=0.1에서 5 에피소드로는 이 함정을 빠져나올 수 없었다.

**해결**: 낙관적 초기화(optimistic initialization) + 무작위 동점 처리. 둘 다 Sutton & Barto (2018)의 표준 기법이다.

### 2. 크래시 격리: 하나의 malformed 응답이 39개를 죽였다

Bedrock Sonnet에서 `plan_and_revise`를 사용할 때, 모델이 너무 장황하게 reasoning 필드를 채워서 code 필드가 예산을 넘겨버렸다. DSPy 구조화 출력 어댑터가 예외를 발생시키고, **한 에피소드의 크래시가 같은 잡의 나머지 39개 에피소드를 모두 죽였다.**

**해결**: 각 에피소드를 try/except로 격리하고, 파싱 실패를 보상 0의 정상 실패 에피소드로 처리.

### 3. 측정 함정: DSPy 캐시가 비용을 0으로 보고했다

DSPy의 LM 디스크 캐시(기본 활성화)는 캐시 히트 시 빈 usage 딕셔너리를 반환한다. 첫 번째 비용 계산은 이를 0 토큰으로 해석했다 — 특히 같은 컨텍스트를 반복하는 DSPy-static의 비용을 과소 계산했다.

**해결**: usage가 비어 있으면 문자열 길이로 토큰을 추정하는 폴백(fallback)을 추가하고 전체 매트릭스를 재실행.

---

## 10단계 배포 레시피

이 논문의 실용적 가치는 `RECIPE.md`라는 10단계 배포 플레이북에 있다:

1. 작업 분포와 특징 벡터를 정의하라
2. 모델에 손대기 전에 **결정론적 검증기를 먼저 만들어라**
3. 작고 열거 가능한 하네스 행동 공간을 정의하라
4. 프로바이더 중립적 LLM 어댑터를 연결하라
5. **0일 차에 DSPy 최적화 정적 기준선으로 부트스트랩하라**
6. 전체 궤적 로깅과 함께 온라인 컨트롤러를 배포하라
7. 컨트롤러 신뢰도가 낮을 때 **인간에게 에스컬레이션하라** (agentic-RPA 루프)
8. 작업 성공률이 아니라 **보상 분해 전체를 모니터링하라** — 이것이 감사 추적(audit trail)이다
9. 주기적으로 오프라인 재생(replay)하여 드리프트를 점검하라
10. 안전 제약(정책 위반률에 대한 하드 필터 또는 라그랑지안 패널티)을 추가한 후 확장하라

핵심 교훈은 5단계에 있다: **온라인 컨트롤러를 처음부터 시작하지 말고 정적 기준선으로 부트스트랩하라.** 논문의 실험 결과가 이 순서가 "있으면 좋은 것"이 아니라 "실용적 에피소드 예산에서는 필수적(load-bearing)"이라는 것을 증명한다.

---

## 데이터셋: 120개 검증 가능한 작업 + 4,620개 궤적 로그

논문은 3개 도메인에 걸쳐 120개 작업(96 훈련 / 24 테스트)을 공개한다:

- **도구 사용**: 40개 가상 CRM 워크플로 (create/update/delete/merge, 상태 diff로 채점)
- **코딩**: 40개 HumanEval 문제 (공식 유닛 테스트로 채점)
- **검색 QA**: 40개 HotpotQA 디스트랙터 설정 문제 (정확 매칭, 외부 검색 API 없이 로컬 말뭉치 사용)

여기에 SQLite 형식의 전체 궤적 로그 — 시도한 모든 구성, 모든 보상 분해, 모든 원시 모델 출력 — 4,620개 에피소드를 공개한다. 코드는 [github.com/dpaul0501/context-optimization-rl](https://github.com/dpaul0501/context-optimization-rl)에서 확인할 수 있다.

---

## 의미: 언제 온라인 하네스 학습을 쓰고, 언제 쓰지 말아야 하는가

이 논문의 가장 큰 기여는 부정적 결과의 **솔직한 보고와 그에 대한 정확한 진단**이다. 실무자에게 주는 시사점은 구체적이다:

**온라인 하네스 제어를 쓸 때:**
- 정적 기준선으로 부트스트랩한 후
- 작업 분포가 충분히 이동하여 정적 프롬프트가 낡았을 때
- 충분한 에피소드 예산(729 이상)이 확보될 때

**쓰지 말아야 할 때:**
- 콜드스타트, 작은 작업 풀, 타이트한 에피소드 예산
- 모델 API가 블랙박스이고 코드 실행 권한이 없을 때 (이 경우 정적 최적화가 더 나은 선택이다)

궁극적으로 이 논문이 말하는 것은: **하네스 최적화는 모델을 고칠 수 없는 환경에서 가장 가성비 높은 레버지만, "어떻게" 최적화하느냐가 "무엇을" 최적화하느냐만큼이나 중요하다.** 729개 레버를 균등 확률로 탐색하는 것보다, DSPy처럼 지표 가이드로 좁은 영역을 집중적으로 파는 것이 실용적 예산에서는 압도적으로 효율적이다.

> 원문: [A Control System, a Dataset, and a Recipe for Making Frozen LLM Agents Learn a Domain](https://arxiv.org/abs/2607.25415) — Debjyoti Paul, 2026

---

## 더 실습해보고 싶은 분들께

에이전트 하네스 최적화, 컨텍스트 엔지니어링, 그리고 RL 기반 자동화 루프를 직접 실험해보고 싶다면 다음 두 가지를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 실제로 구성하고 활용하는 50가지 사례
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 하네스 설계부터 보상 함수 정의까지, 에이전트 RL 루프를 처음부터 끝까지 실습하는 강의
