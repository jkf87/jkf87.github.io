---
title: "ToolAtlas: 도구가 기억한다 — MCP 시대의 공급자 측 도구 메모리"
date: 2026-07-19
tags:
  - agent
  - MCP
  - tool-use
  - LLM
  - automation
  - memory
draft: false
summary: "ToolAtlas는 LLM 에이전트의 도구 사용 경험을 에이전트가 아닌 도구 공급자 측에 저장하고 공유하는 그래프 기반 프레임워크입니다. MCP 서버 하나가 수많은 에이전트에게 재사용 가능한 도구 지식을 제공합니다."
source_url: "https://arxiv.org/abs/2607.11126"
authors:
  - jkf87
---

MCP(Model Context Protocol)가 표준화되면서, 같은 도구 서버를 수많은 에이전트가 호출하는 세계가 현실이 되었습니다. GitHub MCP 서버, Stripe MCP 서버 하나에 수십 개의 에이전트가 각각 도구를 시도하고, 실패하고, 다시 배웁니다. 같은 실수를 수십 번 반복하는 셈입니다.

ToolAtlas는 이 문제를 발상의 전환으로 해결합니다. 도구 사용 경험을 에이전트가 아닌 **도구 공급자(Tool Provider) 측에 저장**하자는 것입니다.

## 핵심 문제: 에이전트 측 메모리의 두 한계

기존 접근은 에이전트가 도구 사용 경험을 자기 메모리에 축적하는 방식이었습니다. ToolAtlas 연구진은 이 방식의 두 가지 구조적 한계를 지적합니다.

![Figure 1: 에이전트 측 도구 메모리의 두 가지 구조적 한계](/images/2026-07-19-toolatlas-tool-side-memory-mcp/fig-1-p1.png)
*Figure 1: 에이전트 측 도구 메모리는 (A) 일반화 불가 — 한 에이전트가 배운 지식을 다른 에이전트가 재사용할 수 없고, (B) 역량 맹목성 — 과거 태스크가 닿지 않은 도구 경계와 조합을 영원히 놓친다.*

**첫째, 일반화의 딜레마(Generalization Dilemma)입니다.** 에이전트 A가 어떤 도구의 사용법을 학습해도, 그 지식은 에이전트 A의 워크플로우, 액션 포맷, 추론 스타일에 얽혀 있습니다. 에이전트 B는 같은 도구를 쓰면서도 처음부터 다시 배워야 합니다.

**둘째, 역량 맹목성(Capability Blindness)입니다.** 에이전트 메모리는 과거 태스크가 닿은 영역만 기록합니다. 도구가 할 수 있지만 태스크에서触发되지 않은 기능, 경계 조건, 다른 도구와의 조합 가능성은 영원히 빈칸으로 남습니다.

## ToolAtlas: 도구가 기억하는 3단계 프레임워크

ToolAtlas는 도구 공급자가 한 번 구축하면 모든 하위 에이전트가 재사용할 수 있는 **도구 메모리 그래프(Tool Memory Graph)**를 제안합니다.

![Figure 2: ToolAtlas 전체 파이프라인](/images/2026-07-19-toolatlas-tool-side-memory-mcp/fig-2-p4.png)
*Figure 2: Stage 1에서 시드 태스크와 검증된 롤아웃으로 그래프를 부트스트랩하고, Stage 2에서 프론티어 탐색으로 그래프를 확장하며, Stage 3에서 추론 시 적응적으로 그래프를 순회한다.*

### Stage 1: 메모리 부트스트래핑

도구 사양과 웹에서 검색한 사용 예시를 바탕으로 시드 태스크를 생성합니다. 각 태스크는 N회 독립 실행되고, 검증기(verifier)가 성공/실패를 라벨링합니다. 이 결과물에서 에이전트 중립적인 도구-근거 흔적(tool-rationale trace)을 추출해 초기 그래프를 만듭니다.

### Stage 2: 역량 탐색 (Capability Exploration)

여기가 ToolAtlas의 차별점입니다. 수동적 궤적 수집이 아니라, 그래프의 현재 빈칸을 능동적으로 찾아냅니다.

- **외향 탐색(Outward)**: 아직 테스트하지 않은 도구 경계 조건을 찾아 프로브를 생성
- **내향 탐색(Inward)**: 그래프가 아직 포착하지 못한 도구 기능과 도구 간 조합을 발굴

생성된 프로브는 실제 도구에 실행되고, 검증된 결과가 그래프에 다시 기록됩니다. 3개의 그래프 레이어가 상호 연결됩니다:

1. **Tool-Trace Graph**: 과거 실행에서 추출한 에이전트 중립적 흔적
2. **Tool-Capability Graph**: 각 도구의 기능, 경계, 공동 사용 엣지
3. **Tool-Strategy Graph**: 반복되는 오케스트레이션 원칙

### Stage 3: 동적 메모리 순회 (Dynamic Memory Traversal)

추론 시점에 가벼운 내비게이터가 그래프를 적응적으로 순회합니다. 정적인 top-k 검색이 아니라, 태스크에 맞게 관련 영역을 단계적으로 확장하며 도구 사용 가이드를 생성합니다.

## 실험 결과: MCPMark와 MCP-Universe에서 일관된 향상

ToolAtlas는 MCPMark와 MCP-Universe 두 벤치마크, 8개 MCP 서비스, 3개 LLM 백본(GPT-5.4, GPT-5.4-mini, Grok-4)에서 평가했습니다.

### 동일 환경 설정 (RQ1)

모든 서비스·모든 백본에서 최강 baseline 대비 pass@1/pass@4 향상을 기록했습니다:

| 백본 | pass@1 향상 | pass@4 향상 |
|------|-----------|-----------|
| GPT-5.4 | +8.15% | +10.48% |
| GPT-5.4-mini | +10.06% | +18.61% |
| Grok-4 | +21.61% | +16.11% |

약한 모델일수록 향상 폭이 큽니다. 도구 지식이 모델 자체 능력을 보완하기 때문입니다.

### 교차 환경 이전 (RQ2)

학습 환경과 다른 환경 인스턴스에서 테스트했을 때, ToolAtlas는 baseline 대비 pass@1/pass@4에서 각각 +24.16%/+16.22% 향상을 보였습니다. 반면 많은 baseline은 환경 특화 패턴에 과적합되어 Vanilla(도구 메모리 없음)보다도 55–77포인트 낮은 성능을 기록했습니다.

### 교차 에이전트 이전 (RQ2)

SwitchAct로 메모리를 구축하고 ReAct와 CodeAct로 이전했을 때도 ToolAtlas는 각각 +16.25%/+14.27%, +17.49%/+14.18%의 pass@1/pass@4 향상을 유지했습니다. 에이전트 중립적 지식 저장이 실제로 작동한다는 증거입니다.

![Figure 3: 추론 토큰 대비 성능 trade-off](/images/2026-07-19-toolatlas-tool-side-memory-mcp/fig-3-p8.png)
*Figure 3: ToolAtlas는 3.55M 토큰으로 Vanilla의 4.44M보다 적은 비용으로 최고 성과를 달성하며 Pareto frontier에 위치한다.*

### 절제 연구 (RQ3)

Tool-Capability Graph를 제거했을 때 가장 큰 성능 저하(-9.18%/-14.19%)가 발생했습니다. 이는 도구 중심 메모리 조직이 ToolAtlas 설계의 핵심임을 확인시킵니다. 기능 탐색(Affordance Exploration)이 경계 탐색(Boundary Exploration)보다 더 큰 기여를 합니다.

![Figure 4: 프론티어 탐색의 효과](/images/2026-07-19-toolatlas-tool-side-memory-mcp/fig-4-p14.png)
*Figure 4: 프론티어 탐색(Frontier Exploration)이 동일 예산의 시드 태스크 샘플링이 도달하는 정체기(plateau)를 넘어서는 것을 보여준다.*

## 왜 중요한가

ToolAtlas는 MCP 생태계가 직면한 현실적 문제에 대한 정답입니다. 도구 서버가 하나이고 에이전트가 여럿인 세계에서, 도구 지식은 도구와 함께 있어야 합니다.

이 접근의 실용적 의미는 명확합니다:

1. **진입 장벽 낮춤**: 새로운 에이전트가 도구를 처음 쓸 때부터 검증된 지식에 접근
2. **비용 절감**: 도구 재탐색 비용 회피, 추론 토큰 20% 절감
3. **생태계 효율**: 공급자 한 번의 오프라인 구축이 모든 하위 에이전트에 전파
4. **약한 모델 보완**: 작은 모델일수록 도구 메모리의 효용이 큼

한계도 있습니다. 8개 서비스로 평가가 제한되어 있고, API 변경 시 재검증 메커니즘이 필요하며, 메모리 오염(poisoning) 방지를 위한 접근 제어가 실 배포에 필수적입니다.

## 더 실습해보고 싶은 분들께

에이전트 도구 사용과 자동화 하네스를 직접 다뤄보고 싶다면, 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 자동화와 도구 활용 실습
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 최적화 실전

---

**참고문헌**: Yue Fang, Zhibang Yang, Fangkai Yang, Xiaoting Qin, Liqun Li, Qingwei Lin, Saravan Rajmohan, Dongmei Zhang. "Learning Once, Reusing Everywhere with Tool-Side Memory." arXiv:2607.11126, 2026. [논문 링크](https://arxiv.org/abs/2607.11126) | [코드 저장소](https://github.com/PuppyKnightUniversity/ToolAtlas)
