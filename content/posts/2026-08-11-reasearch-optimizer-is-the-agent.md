---
title: "ReASearch: 최적화 에이전트가 외부 루프 없이 스스로 검색한다"
date: 2026-08-11
tags:
  - agent
  - LLM
  - optimization
  - harness
  - tool-use
  - reasoning
  - loop
  - automation
  - prompt-optimization
  - program-evolution
authors:
  - conanssam
source_url: "https://arxiv.org/abs/2608.06714"
paper_url: "https://arxiv.org/abs/2608.06714"
venue: "COLM 2026"
---

## 요약

ReASearch(LLM 에이전트 기반 통합 최적화 프레임워크)는 프롬프트 최적화, 프로그램 진화, ML 워크플로 최적화 세 영역에서 외부 검색 알고리즘을 제거하고, 단일 에이전트 루프로 검색 정책을 내재화한다. 14개 태스크에서 도메인 특화 시스템과 동등 이상의 성능을 기록했으며, Circle Packing 문제에서는 기존 인간 최고 기록을 초과하는 결과를 달성했다.

논문: [The Optimizer Is the Agent: Reasoning-Driven Search across Prompts, Programs, and ML Workflows](https://arxiv.org/abs/2608.06714) (UT Austin · Snowflake, COLM 2026)

## 문제 정의

텍스트 아티팩트 z(프롬프트, 프로그램, 학습 설정)를 최적화하는 문제는 다음과 같이 정식화된다. 태스크 인스턴스 x ~ D와 아티팩트 z가 주어졌을 때, 출력 Y ~ P(·|x,z)의 기대 보상 r(x,Y)를 최대화하는 z*를 찾는 것.

기존 접근은 LLM을 변이 연산자(mutator)로 사용하고, 외부 알고리즘(진화 연산, 밴딧, 베이지안 최적화, MCTS, 텍스트 그래디언트)이 검색 정책을 담당하는 구조를 취한다. ReASearch는 이 분업 구조를 제거하고, 에이전트가 도구를 통해 검색 정책 전체를 수행하도록 설계되었다.

![Figure 1: ReASearch와 기존 방법의 위치 비교](/images/2026-08-11-reasearch-optimizer-is-the-agent/fig-1-p2.png)

## 방법론

### 에이전트 아키텍처

ReASearch는 파일 I/O, Python/Bash 실행, 컨텍스트 압축, 지속적 메모리(`lessons.md`)를 갖춘 코드 에이전트이다. 태스크별로 도구 세트와 시스템 프롬프트만 변경하여 세 가지 최적화 영역에 동일한 루프를 적용한다.

![Figure 2: 기존 방법 vs ReASearch 아키텍처](/images/2026-08-11-reasearch-optimizer-is-the-agent/fig-2-p3.png)

### 도구 설계

| 범주 | 프롬프트 최적화 | 프로그램 진화 | ML 워크플로 |
|---|---|---|---|
| 평가 | `validate_candidate` | `evaluate` | `run_experiment` |
| 수정 | 프롬프트 재작성 | `edit_code` | `edit_train_file` |
| 분석 | `python_exec` | `python_exec` | `python_exec` |
| 메모리 | `lessons.md` | `lessons.md` | `lessons.md` |

`python_exec`는 에이전트를 텍스트 추론기에서 계산적 추론기로 전환한다. 평가 로그 파싱, 실패 패턴 분류, 통계 계산, 검증 전 가설 테스트가 가능하다.

### 컨텍스트 관리

컨텍스트가 임계치(기본 90,000 토큰)를 초과하면 `compact()`가 호출된다. 전체 기록을 요약하고, `lessons.md` 내용을 보존하여 압축 후에도 핵심 교훈이 유지된다.

### 시스템 프롬프트 재주입

매 턴 시스템 프롬프트에 현재 최고 점수, 최근 20개 실험 결과, 정체 경고(stagnation advisory)를 재주입한다. 이는 Claude Code 등 기존 에이전트 시스템에서 상태를 "사용 가능(available)"하게 두는 것과 "불가피(unavoidable)"하게 만드는 것의 차이다.

![Figure 3: 프롬프트 최적화 에이전트 궤적](/images/2026-08-11-reasearch-optimizer-is-the-agent/fig-3-p4.png)

## 관찰된 검색 행동

에이전트 궤적 분석에서 다음 행동들이 하드코딩 없이 자연스럽게 출현했다:

1. 태스크 구조화 이해 — HotpotQA에서 baseline 실패 126건을 `python_exec`로 범주화 (verbosity 57, wrong-reasoning 68, yes/no 오염 8)하여 수정 방향 결정
2. 사전 검증(double-verification) — 비용이 높은 검증 세트 평가 전, 트레이닝 배치에서 개선의 신뢰성을 먼저 확인
3. 자발적 백트래킹 — Terminal-Bench에서 Candidate #4가 #3 대비 3점 하락하자, 원인 분석 후 #3으로 회귀하여 단일 문장 추가 → 최고점 달성
4. 오버피팅 탐지 및 전략 전환 — AIME에서 트레이닝 정확도 상승(60%→66.7%)이 검증 하락(50.2%)으로 이어지자 "도메인 특화 추가는 검증을 해친다"고 기록하고 방향 전환
5. 전략적 최종 선택 — 검증 최고점 후보 대신 전체 이력 기반 합성 프롬프트를 제출 → 테스트 52.0%로 검증 최고점 49.3%를 초과

## 실험 결과

### 프롬프트 최적화

| 태스크 | 학생 모델 | Baseline | ReASearch |
|---|---|---|---|
| AIME | GPT-4.1 mini | 51.1% | 52.0% |
| HotpotQA | GPT-4.1 mini | 44.6% | 66.0% |
| GSM8K | Llama 3.1 | 84.7% | 88.4% |
| Terminal-Bench 2.0 | GPT-5 | 58.5% | 63.6% |

![Table 1: 프롬프트 최적화 결과](/images/2026-08-11-reasearch-optimizer-is-the-agent/table-1-p7.png)

### 프로그램 진화

Circle Packing(n=23-32)에서 일부 인스턴스의 기존 인간 최고 기록을 초과했다. Heilbronn Triangle, EPLB(MoE 로드밸런싱), Transaction Scheduling, ARC-AGI-2에서도 baseline 대비 일관된 개선을 보였다.

![Table 2: Circle Packing 결과](/images/2026-08-11-reasearch-optimizer-is-the-agent/table-2-p7.png)

![Figure 4: 프로그램 진화와 ML 워크플로 패턴](/images/2026-08-11-reasearch-optimizer-is-the-agent/fig-4-p5.png)

### ML 워크플로 최적화

NanoGPT 학습 스크립트 최적화에서 0.969 bpb를 달성하여 AutoResearch(Claude Code 기반)를 능가했다.

### Claude Code와의 비교

동일한 지시문, 모델(Claude Sonnet 4.6), 예산으로 비교. ReASearch의 우위는 시스템 프롬프트의 매 턴 재주입에서 기인한다:

| 항목 | Claude Code | ReASearch |
|---|---|---|
| 시스템 프롬프트 | 세션 시작 시 고정 | 매 턴 상태 재주입 |
| 실험 이력 | 에이전트가 자발적으로 조회 | 구조화된 테이블로 매 턴 주입 |
| 정체 대응 | 에이전트가 진단 도구 호출 필요 | 3/7회 평가 후 정체 알림 자동 삽입 |

![Figure 5: 도구 호출 빈도 통계](/images/2026-08-11-reasearch-optimizer-is-the-agent/fig-5-p6.png)

### 컴포넌트 제거 실험

메모리(`lessons.md`) 제거는 프롬프트 최적화에서, Python 실행 제거는 프로그램 진화에서 더 큰 영향을 미쳤다. 두 컴포넌트는 서로 다른 검색 측면을 지원한다.

### 오픈소스 백본

GLM-5, Kimi-2.5에서도 ReASearch가 작동한다. AIME/HotpotQA에서는 Claude 결과에 근접하고, Terminal-Bench 2.0에서는 baseline 대비 유의미한 개선을 보였다.

## 더 실습해보고 싶은 분들께

에이전트 루프, 도구 사용, 하네스 최적화에 관심 있다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 결론

ReASearch는 툴을 사용하는 LLM 에이전트의 추론 능력이 수학적 메타휴리스틱을 대체할 수 있음을 체계적으로 입증했다. 검색 정책의 핵심 구성 요소(후보 선택, 예산 배분, 백트래킹, 탐색-활용 트레이드오프)가 외부 알고리즘 없이 에이전트의 추론 과정에서 자연스럽게 출현한다는 것은, 에이전트 기반 최적화의 적용 범위가 기존보다 훨씬 넓을 수 있음을 시사한다.
