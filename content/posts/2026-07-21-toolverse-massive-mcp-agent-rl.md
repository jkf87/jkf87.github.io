---
title: "ToolVerse: 422개 실제 MCP 환경에서 에이전트 RL을 훈련하는 방법"
slug: 2026-07-21-toolverse-massive-mcp-agent-rl
published: 2026-07-21T07:00:00+09:00
tags: [agent, RL, MCP, tool-use, long-horizon, LLM]
source: arxiv
source_url: https://arxiv.org/abs/2607.15660
authors: Shuaiyu Zhou, Fengpeng Yue, Zengjie Hu, Yuanzhe Shen, Chenyang Zhang, Feng Hong, Cao Liu, Ke Zeng
affiliation: Meituan (LongCat Interaction Team), Peking University, Fudan University, Wuhan University
---

## TL;DR

ToolVerse는 **422개의 실제 MCP(Model Context Protocol) 환경**(약 4,438개 도구)에서 에이전트 RL 훈련을 수행하는 프레임워크다. 단순한 검색·코드 실행을 넘어, 도구 의존성 그래프(TDG) 기반으로 긴 호라이즌(long-horizon) 작업을 자동 생성하고, 희소 보상 환경에서도 턴별 크레딧 할당(TARA)을 정교하게 수행한다. BFCL-v3, τ²-Bench, ACEBench-Agent 세 곳의 벤치마크에서 일관된 성능 향상을 확인했다.

---

## 왜 기존 에이전트 RL로는 부족한가

에이전트 RL 연구는 빠르게 발전하고 있지만, Meituan LongCat 팀은 세 가지 병목을 지적한다.

![Table 1: Agentic RL의 세 가지 확장성 한계](/images/2026-07-21-toolverse-massive-mcp-agent-rl/table-1-p2.png)

1. **환경 다양성(Scope)**: 대부분의 기존 연구가 코드 인터프리터나 검색 엔진 한두 개만 다룬다. TORL, rStar2-Agent, ZeroTIR, SimpleTIR, ToolStar 모두 좁은 도구 세트에 머물러 있다.
2. **도구 사용 복잡성(Tool Use Complexity)**: 여러 도구를 연쇄적으로 사용하는 긴 호라이즌 작업을 설계하기 어렵다. 각 단계가 이전 단계의 출력에 의존하기 때문이다.
3. **크레딧 할당(Credit Assignment)**: 다중 턴 궤적에서 sparse terminal reward만으로는 어느 턴의 어떤 행동이 성공에 기여했는지 알기 어렵다. GRPO는 궤적 전체에 단일 스칼라 어드밴티지를 할당해서 이 문제가 특히 심하다.

## ToolVerse의 세 단계 접근

![Figure 1: ToolVerse 프레임워크 개요](/images/2026-07-21-toolverse-massive-mcp-agent-rl/fig-1-p3.png)

### Step 1: 실행 가능한 MCP 환경 자동 구축

원시 도구 정의(JSON 스키마)를 받아서 실행 가능한 MCP 환경으로 변환하는 자동 파이프라인을 만들었다.

- **Schema Refactoring**: 함수 시그니처 정리, 노이즈 제거
- **Mock DB 구축**: 도메인별 딕셔너리 데이터베이스(사용자, 주문, 티켓 등) 생성
- **코드 생성 + 단위 테스트**: 통과한 환경만 유지 (약 20%는 외부 서비스 의존성 등으로 필터링)

결과적으로 422개의 실행 가능한 MCP 환경(각 5–20개 도구 포함, 총 4,438개 도구)을 확보했다.

![Figure 3: 도구의 의미적 범위](/images/2026-07-21-toolverse-massive-mcp-agent-rl/fig-3-p6.png)

8개의 거시적 도메인(e-commerce, 항공, 금융, 헬스케어, 프로젝트 관리 등)에 걸쳐 있다.

### Step 2: 그래프 기반 긴 호라이즌 작업 합성

**도구 의존성 그래프(TDG, Tool Dependency Graph)**를 구성한다. 노드는 도구, 엣지는 의존 관계다.

- 도구 A의 출력이 도구 B의 입력으로 필요하면 엣지 생성
- 논리적 순서가 존재하면 엣지 생성

이 그래프 위에서 **동적 잠금 해제 샘플링(Dynamic Unlocking Sampling, DUS)** 알고리즘을 돌린다. 위상 정렬을 기반으로, 선행 도구가 완료되어야 후행 도구가 "잠금 해제"되는 방식이다. 이렇게 하면 자연스럽게 난이도가 점진적으로 높아지는 커리큘럼이 만들어진다.

GUST(Graph Unlocking Sampling Tasks) 데이터셋은 이렇게 생성된 작업 모음이다. 각 작업은 3–7개의 서브태스크로 구성되며, Pass@8 필터링으로 품질을 보장한다.

### Step 3: 턴 인식 상대적 어드밴티지(TARA)

가장 중요한 알고리즘 기여다. 표준 GRPO가 궤적 전체에 하나의 보상을 할당하는 반면, TARA는 **각 턴마다** 별도의 어드밴티지를 계산한다.

![Figure 2: TARA 개요](/images/2026-07-21-toolverse-massive-mcp-agent-rl/fig-2-p5.png)

세 가지 구성 요소가 있다:

1. **바이너리 턴 보상**: Golden Trace와의 매칭으로 각 턴에 0 또는 1 부여
2. **국소 어드밴티지(Local Advantage)**: 같은 턴의 그룹 내 상대적 성과 정규화
3. **게이트된 미래 어드밴티지(Gated Future Advantage)**: 현재 턴이 정답일 때만 미래 보상을 전파 (Consistency Gate δ = r_{i,t})

일관성 게이트(Consistency Gate)가 핵심이다. 현재 단계가 틀렸는데 운 좋게 뒤에서 맞추는 "디스트랙터(distractor)" 행동을 차단한다. 논문은 수학적으로 TARA의 디스트랙터 억제를 증명했다 — 디스트랙터 행동의 총 어드밴티지는 항상 음수가 된다.

## 실험 결과

### 메인 결과

세 가지 벤치마크에서 ToolVerse를 평가했다:

| 벤치마크 | 특성 |
|---|---|
| BFCL-v3 Multi-Turn | Python API 호출, Missing Param/Func, Long Context |
| τ²-Bench | 항공, 소매, 통신 도메인의 복잡한 대화형 에이전트 |
| ACEBench-Agent | 다중 단계, 다중 턴 동적 환경 추론 |

Qwen3-8B(Thinking) 모델 기준으로:

- **BFCL-v3**: 베이스라인 대비 +7.5%p (GRPO), +8.75%p (TARA)
- **τ²-Bench**: +4.49%p (GRPO), +5.4%p (TARA)
- **ACEBench-Agent**: +10.5%p (GRPO), **+15.15%p** (TARA)

TARA가 GRPO 대비 모든 벤치마크에서 추가 이득을 준다. 특히 ACEBench-Agent의 +4.66%p 추가 향상은 다중 턴·다중 단계 작업에서 턴별 크레딧 할당이 얼마나 중요한지 보여준다.

### 공개 베이스라인과의 비교

ToolRL, agentflow, SimpleTIR 등 공개 재현 가능 베이스라인과 비교해서 Qwen2.5-7B-Instruct-TARA가 일관되게 앞선다.

### 환경 스케일링 효과

![Table 7: 환경 확장 효과](/images/2026-07-21-toolverse-massive-mcp-agent-rl/table-7-p15.png)

환경을 100개에서 422개로 늘리자 BFCL-v3가 35.00% → 37.50%, τ²-Bench가 27.33% → 32.37%로 올랐다. 환경 다양성이 필수적이다.

### TARA 민감도 분석

![Figure 5: TARA λ와 γ에 대한 민감도](/images/2026-07-21-toolverse-massive-mcp-agent-rl/fig-5-p15.png)

λ(미래 어드밴티지 가중치)와 γ(할인 인자) 모두 0.5에서 최적이며, 극단값에서는 성능이 저하된다. 적당한 미래 신호 전파가 균형점이다.

### 컴포넌트 Ablation

![Table 4: TARA 컴포넌트 Ablation](/images/2026-07-21-toolverse-massive-mcp-agent-rl/table-4-p15.png)

- Local-only 어드밴티지만 쓰면 GRPO보다도 못하다 → 미래 신호 없이는 부족
- Consistency Gate 없는 미래 신호도 full TARA보다 못하다 → 노이즈 필터링이 필수
- Local + Gated Future의 조합이 최적

## 의의와 한계

ToolVerse는 MCP가 에이전트 RL의 훈련 환경 표준으로 자리잡고 있음을 보여주는 사례다. 400개 이상의 실제 도구 환경에서 그래프 기반으로 긴 호라이즌 작업을 자동 생성하고, 턴별 크레딧 할당으로 희소 보상 문제를 완화한 점이 핵심 기여다.

GUST 데이터셋 통계를 보면:

![Table 6: GUST 데이터셋 통계](/images/2026-07-21-toolverse-massive-mcp-agent-rl/table-6-p6.png)

한계도 명확하다. 첫째, 사전 정의된 의존성에 의존하므로 자율적 도구 탐색(emergent behavior)이 제한된다. 둘째, 턴별 보상이 여전히 discrete 매칭에 기반하므로, 더 희소하거나 모호한 보상 환경에서는 한계가 있을 수 있다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 MCP 도구 환경에서 RL을 돌리는 실전 감각을 키우고 싶다면, 다음 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 실제 에이전트 자동화 사례 50가지를 통해 하네스 설계와 도구 통합 감각을 익힐 수 있다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 RL 피드백 사이클을 처음부터 끝까지 실습하는 강의다.

---

**Paper**: [ToolVerse: Unlocking Massive Environments and Long-Horizon Tasks for Agentic Reinforcement Learning](https://arxiv.org/abs/2607.15660) (Meituan LongCat Interaction Team, July 2026)
