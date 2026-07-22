---
title: "DataFlow-Harness: 에이전트가 코드를 버리지 않고 파이프라인으로 남기는 법"
date: 2026-07-23
tags:
  - agent
  - MCP
  - harness
  - LLM
  - automation
  - DAG
  - code-agent
---

 코딩 에이전트가 데이터 파이프라인을 만들어 달라고 하면 대부분 일회성 파이썬 스크립트를 내놓는다. 실행은 되지만, 플랫폼에서 관리할 수 없고, 시각적으로 검수할 수도 없으며, 재사용이 어렵다. DataFlow-Harness는 이 간극을 **NL2Pipeline gap**이라 부르며, 에이전트가 자유 형태 스크립트 대신 플랫폼 네이티브 DAG를 직접 조립하도록 유도한다.

![DataFlow-Harness architecture](/images/2026-07-23-dataflow-harness-grounded-code-agent-pipelines/fig-1-p4.png)

> **Figure 1:** DataFlow-Harness 아키텍처. 공유 파이프라인 표현이 에이전트 런타임과 DataFlow-WebUI 양쪽에 동기화된다. DataFlow-Skills가 구축을 가이드하고, Validation Engine이 DAG 구조와 스키마 호환성을 검증한다.

## 핵심 문제: NL2Pipeline Gap

LMM 코딩 에이전트(Claude Code, SWE-agent 등)는 코드 생성 정확도가 높아졌지만, 산업 환경에서는 단순히 "돌아가는 스크립트"만으로는 부족하다. 결과물이 **가시적이고, 편집 가능하며, 재사용 가능하고, 플랫폼 거버넌스와 호환되어야** 한다.

DataFlow-Harness 연구진은 이를 다음과 같이 정식화한다:
- **워크플로우** = 의도된 데이터 처리 절차
- **파이프라인 표현** = 플랫폼에 영속되는 객체
- **DAG** = 실행 의존성 그래프

코드 생성 정확도만 높여서는 이 간극을 못 메운다. 구축 과정 자체가 플랫폼 시맨틱에 **접지(grounded)**되어야 한다.

## 세 가지 구성 요소

### 1. DataFlow-Skills (절차적 가이드)

에이전트에게 "어떤 순서로 오퍼레이터를 선택하고 조립해야 하는가"라는 도메인 지식을 주입한다. 스키마 추론, 오퍼레이터 선택, 파라미터 설정, 서빙 검증까지의 권장 시퀀스와 호환성 규칙을 포함한다. MCP가 "무엇이 가능한가"를 알려준다면, Skills는 "어떻게 해야 하는가"를 알려준다.

### 2. MCP Tools Layer (라이브 접지)

![DataFlow-WebUI dual-modality interface](/images/2026-07-23-dataflow-harness-grounded-code-agent-pipelines/fig-2-p5.png)

> **Figure 2:** DataFlow-WebUI의 듀얼 모달리티 인터페이스. 대화형 에이전트와 시각적 DAG 에디터가 실시간 동기화된다.

Model Context Protocol을 통해 에이전트가 **라이브 오퍼레이터 레지스트리**와 **현재 파이프라인 상태**에 접근한다. 모든 변경은 Request-Validate-Commit 프로토콜을 거친다:

1. **State Retrieval**: 매 턴 시작 시 최신 파이프라인 상태를 가져온다 (수동 편집 반영 포함)
2. **Mediated Mutation**: 에이전트가 타입화된 구조적 변이(mutations)로 의도를 표현
3. **Validation**: 결과 그래프가 비순환(DAG)이고 인접 오퍼레이터 간 스키마가 호환되는지 확인
4. **Validated Commit**: 검증 통과 시 백엔드에 커밋, WebSocket으로 클라이언트에 브로드캐스트

핵심은 에이전트가 임의의 Python 코드를 생성하는 것이 아니라, **타입화된 증분 변이(typed incremental mutations)** — 오퍼레이터 추가/제거, 파라미터 업데이트, 엣지 연결 — 만 허용된다는 점이다.

### 3. DataFlow-WebUI (동기화된 듀얼 인터페이스)

대화형 인터페이스와 시각적 DAG 에디터가 하나의 백엔드를 공유한다. 사용자가 에이전트와 대화로 파이프라인을 만들면 실시간으로 시각화되고, 사용자가 직접 에디터에서 노드를 드래그해 수정하면 그 변경이 다음 에이전트 턴에 반영된다.

## 실험 결과: 93.3% 통과율, 72.5% 비용 절감

12개 데이터 엔지니어링 태스크(각 10회 반복, 총 120회)에서 4가지 설정을 비교했다:

| 방법 | 산출물 | E2E Pass | 비용 | 지연 |
|---|---|---|---|---|
| Vanilla Claude Code | 일회성 스크립트 | 91.7% | $0.950 | 190.7s |
| Context-Aware CC | 일회성 스크립트 | 94.2% | $0.456 | 115.9s |
| MCP-Only | 네이티브 DAG | 83.3% | $0.321 | 105.5s |
| **DataFlow-Harness** | **네이티브 DAG** | **93.3%** | **$0.261** | **95.5s** |

가장 주목할 점:
- **MCP-Only는 83.3%로 오히려 성능이 하락** — 절차적 가이드 없이 도구 접근만 주면 에이전트가 혼란스러워한다
- **DataFlow-Harness는 Skills를 더하니 93.3%로 회복** — Context-Aware CC(94.2%)와 0.9%p 차이에 불과
- **비용은 Vanilla CC 대비 72.5%, Context-Aware CC 대비 42.8% 절감**
- **지연 시간도 49.9% 단축** (Vanilla 대비)

### 태스크별 분석: Skills는 언제 도움되는가

Skills가 가장 큰 효과를 발휘하는 태스크는 **암묵적 절차적 지식이 필요한 경우**, 즉 문서 파싱 → 품질 필터링 → LLM 채점 → 데이터 증강 같은 복잡한 연쇄가 필요한 작업이다. 반면 단순한 스키마 변환은 Skills 없이도 잘 수행한다.

## 다운스트림 데이터 품질: 파이프라인이 만든 데이터로 학습하면?

가장 흥미로운 결과는 에이전트가 만든 파이프라인의 **출력 데이터 품질**이다. Vanilla CC와 DataFlow-Harness가 각각 합성 데이터를 생성하고, 동일한 레시피로 Qwen2.5-7B-Base를 파인튜닝했다:

- **수학 파이프라인**: AIME24@32에서 25.1 → 35.9 (+10.8), AIME25@32에서 21.6 → 34.5 (+12.9) — DataFlow-Harness가 만든 데이터로 학습한 모델이 더 높은 정확도
- **일반 SFT 파이프라인**: 코드 벤치마크에서 MBPP 64.6 → 75.4 (+10.8), 전체 9-벤치마크 평균 61.5 → 63.8 (+2.3)

이는 단순히 "에이전트가 파이프라인을 잘 만든다"를 넘어, **접지된 파이프라인이 더 깨끗하고 검증된 데이터를 생산한다**는 것을 시사한다.

## 왜 중요한가

이 논문이 던지는 메시지는 현재 에이전트/Harness 연구의 핵심 질문과 직결된다:

1. **코드 생성 ≠ 파이프라인 구축**: 에이전트가 정확한 코드를 쓴다고 해서 프로덕션에서 관리 가능한 워크플로우가 되는 것은 아니다
2. **접지(grounding)가 핵심**: MCP로 라이브 환경에 접근하게 하고, Skills로 절차적 지식을 주입하고, 타입화된 변이만 허용하면 에이전트 출력의 성격이 근본적으로 바뀐다
3. **Skills가 없는 MCP는 독**: 도구에 접근할 수만 있고 어떻게 써야 할지 모르면 오히려 자유도가 성능을 해친다 (83.3% vs 93.3%)
4. **거버넌스와 효율성은 양립 가능**: 영속적이고 편집 가능한 DAG 산출물이 일회성 스크립트보다 비용도 싸고 빠르다

## 한계

연구진 자체도 명시하는 한계:
- 단일 코딩 에이전트(Claude Code)와 단일 모델(Claude Opus 4.7)만 평가
- 12개 태스크, 플랫폼 특화 벤치마크로 일반화 제한
- 스키마 검증은 구조적 유효성만 보장, 시맨틱 정확성은 보장하지 않음
- 다운스트림 품질 결과는 2개 케이스 스터디로, 독립적으로 작성된 여러 파이프라인과 트레이닝 시드를 통한 반복 실험은 아님

## 더 실습해보고 싶은 분들께

에이전트 하네스, MCP 도구 체계, 자동화 파이프라인 설계에 관심이 있다면 다음 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 실제 에이전트 하네스를 구성하고 자동화 루프를 설계하는 50가지 사례
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 컨텍스트 엔지니어링의 실전 가이드

---

**Paper**: [DataFlow-Harness: A Grounded Code-Agent Platform for Constructing Editable LLM Data Pipelines](https://arxiv.org/abs/2607.16617) (Peking University, IAAR Shanghai, Zhongguancun Academy, July 2026)
