---
title: "NVIDIA OO Agents: 에이전트는 곧 파이썬 객체다"
date: 2026-07-25
tags:
  - agent
  - framework
  - NVIDIA
  - LLM
  - harness
  - code-as-action
draft: false
source_url: https://arxiv.org/abs/2607.20709
source: "arxiv"
github_url: https://github.com/NVIDIA-NeMo/labs-OO-Agents
---

## 핵심 한 줄 요약

NVIDIA가 "에이전트는 하나의 파이썬 객체다"라는 철학으로 만든 **NOOA(NVIDIA Object-Oriented Agents)** 프레임워크. 프롬프트 템플릿, 툴 스키마, 콜백 코드, 워크플로우 그래프를 전부 하나의 클래스로 통합한다. 메서드는 액션, 필드는 상태, docstring은 프롬프트, 타입 어노테이션은 계약(contract)이다.

![Figure 1: NOOA 에이전트 구현 예시](/images/2026-07-25-nvidia-oo-agents/fig-1-p2.png)
> **Figure 1:** NOOA에서 간단한 에이전트를 구현한 예시. 하나의 클래스가 소스 코드이자 프롬프트, 타입 계약, 툴 인터페이스, 상태 경계를 모두 겸한다.

---

## 왜 새 프레임워크인가

기존 에이전트 개발의 고통은 "분할"에 있다. 프롬프트는 템플릿 파일에, 툴 정의는 JSON 스키마에, 콜백은 별도 코드에, 워크플로우는 그래프 설정에 흩어져 있다. 개발자가 새 프레임워크를 배울 때마다 새로운 DSL을 익혀야 하고, 모델 역시 학습 데이터에 없는 낯선 인터페이스를 해석해야 한다.

NOOA의 통찰은 단순하다. **파이썬이 이미 충분히 좋은 추상화를 갖고 있다**는 것이다.

- 클래스 → 에이전트 정의
- 메서드 → 에이전트 기능(capability)
- 타입 어노테이션 → 입출력 계약
- `asyncio` → 동시성
- 필드 → 명시적이고 모델 가시적인 상태
- `...`(ellipsis) 바디 → LLM 구동 에이전트 루프
- 일반 메서드 바디 → 결정론적 파이썬 코드

PyTorch가 "강력한 런타임을 단순한 파이썬 API로 제공한다"는 철학을 에이전트에 적용한 것이다.

## 작동 방식: 두 가지 전략

NOOA는 에이전트 메서드를 두 가지 전략으로 실행한다.

### 1. Predict (싱글샷)

분류나 추출에 적합. 컨텍스트를 렌더링하고 모델에 한 번 호출한 뒤, 반환 타입에 따라 결과를 검증한다. 검증 실패 시 로컬 재시도 루프가 동작한다.

### 2. CodeAct (반복적 REPL)

더 일반적인 형태. 모델이 파이썬 코드를 작성해 실행하고, 결과를 관찰하고, 다시 코드를 작성하는 Jupyter-like 세션이다. `return`으로 타입 검증된 값을 반환할 때까지 반복한다.

![Figure 2: CodeAct 전략 루프](/images/2026-07-25-nvidia-oo-agents/fig-2-p5.png)
> **Figure 2:** CodeAct 전략의 루프. 호출자가 메서드를 호출하면, 매 턴마다 컨텍스트를 렌더링하고 LLM을 호출하며, 파이썬 액션을 실행한 뒤 이벤트와 상태를 업데이트한다.

핵심은 **결정론적 코드와 에이전트 루프의 경계가 소스 코드에 직접 보인다**는 점이다. `...` 바디는 LLM 루프로, 일반 바디는 그냥 파이썬으로 실행된다. 개발자와 모델이 같은 인터페이스를 공유하는 셈이다.

## 컨텍스트 렌더링: 3개 영역

NOOA는 모델 컨텍스트를 세 영역으로 분리한다.

![Figure 3: NOOA 컨텍스트 렌더링](/images/2026-07-25-nvidia-oo-agents/fig-3-p6.png)
> **Figure 3:** NOOA의 컨텍스트 렌더링. ContextManager와 EventManager가 static, event history, dynamic 컨텍스트를 매 턴마다 조합한다.

1. **Static context blocks** — 시스템 프롬프트처럼 턴 간에 불변인 블록. KV-cache 재사용을 극대화한다.
2. **Event history** — 실행 트레이스. 타입화된 이벤트의 append-only 시퀀스로, 에이전트 코드가 과거 이벤트를 쿼리할 수 있다.
3. **Dynamic context blocks** — 매 모델 호출 전에 재평가되는 블록. TODO 리스트나 live state 필드 등.

이 3층 구조는 KV-cache 효율을 극대화하도록 설계되었다. static prefix는 불변이고, event history는 append-only로 성장하며, volatile dynamic 블록은 tail에 배치된다.

## 참조에 의한 전달 (Pass by Reference)

NOOA의 가장 독특한 특성 중 하나. CodeAct 메서드는 인자를 **live 파이썬 객체**로 받는다. 모델은 전체 값을 프롬프트에서 보는 게 아니라, 타입·길이·head/tail 샘플만 보는 "미리보기"를 받는다.

```
numbers: list[int] (len=100) = [1, 2, 3, ..., 99, 100]
```

모델은 이 변수를 코드에서 `numbers[50:]`처럼 자유롭게 조작할 수 있다. **컨텍스트 윈도우가 아니라 실행 환경의 용량이 처리 한계**가 되는 것이다. 수백만 행의 테이블도 프롬프트에 들어가지 않고 코드로만 다뤄진다.

![Figure 4: NOOA 컨텍스트 엔지니어링 API](/images/2026-07-25-nvidia-oo-agents/fig-4-p6.png)
> **Figure 4:** NOOA의 컨텍스트 엔지니어링. 컨텍스트 블록과 이벤트 히스토리가 개발자와 모델 모두에게 동일한 파이썬 API로 노출된다.

## 메모리 시스템

![Figure 5: NOOA 메모리 시스템](/images/2026-07-25-nvidia-oo-agents/fig-5-p10.png)
> **Figure 5:** NOOA 메모리 시스템. MemoryManager.install(agent)로 메모리를 부착하고, 에이전트가 long-term 기억을 관리한다.

대화 히스토리가 길어지면 압축이 필요한데, NOOA는 객체 스코프의 typed 필드와 named context block을 상태로 유지하며 eviction에서 제외한다. MemGPT의 "working context"와 유사하지만, 파일이나 외부 스토어가 아닌 **객체 필드 자체**가 상태가 된다.

## 벤치마크 성능

![Table 3: SWE-bench Verified 패스유](/images/2026-07-25-nvidia-oo-agents/table-3-p14.png)
> **Table 3:** SWE-bench Verified 패스율. 공개 모델 기준 경쟁력 있는 성능을 보인다.

![Table 4: Terminal-Bench 2.0 결과](/images/2026-07-25-nvidia-oo-agents/table-4-p14.png)
> **Table 4:** Terminal-Bench 2.0 (89 태스크) 결과.

특히 주목할 만한 점은 **ARC-AGI-3** 대화형 추론 벤치마크에서, NOOA 인터페이스가 멀티에이전트 월드 모델 시스템을 단일 에이전트 + 1페이지 스킬로 압축하면서도 score–cost Pareto frontier를 향상시켰다는 것이다.

## 14개 프레임워크 비교

NOOA 논문의 가장 큰 기여 중 하나는 14개 주요 에이전트 프레임워크/하네스를 6가지 인터페이스 역량 기준으로 비교한 표다:

| 역량 | 설명 |
|------|------|
| Typed I/O | 루프 경계에서 타입화된 입출력 |
| Pass by reference | 직렬화가 아닌 live 객체 참조 |
| Code as action | 코드가 액션 모달리티 자체 |
| Loop engineering | 개발자와 모델 모두 오케스트레이션 루프 작성 가능 |
| Object state | 모델 가시적인 typed 내구 상태 |
| Harness APIs | 컨텍스트/이벤트가 모델 호출 가능 API로 노출 |

비교 대상에는 LangGraph, Claude Agent SDK, OpenAI Codex, Google ADK, PydanticAI, smolagents, OpenHands, OpenClaw 등이 포함된다. NOOA는 이 6가지를 **단일 표면에서 모두 지원하는 최초의 프레임워크**임을 주장한다.

## 왜 중요한가

NOOA가 제시하는 비전은 "에이전트 소프트웨어 = 일반 소프트웨어"다. 에이전트 동작을 테스트하고, 추적하고, 리팩토링하고, 버전 관리하는 것이 일반 파이썬 개발과 동일한 워크플로가 된다. 모델이 이미 훈련 데이터에서 학습한 파이썬 지식을 그대로 활용하므로, 별도의 DSL 학습 없이도 에이전트를 "그냥 파이썬 클래스"로 다룰 수 있다.

논문의 결론부가 특히 흥미롭다:

> "진행은 더 큰 모델이나 더 나은 프롬프트뿐만 아니라 **모델과 하네스의 공동 개발**에서 올 것이다. 소프트웨어 인터페이스가 그 공동 개발의 장소가 되어야 한다."

에이전트 최적화가 프롬프트 탐색을 넘어 에이전트 객체 전체(프롬프트, docstring, 타입 시그니처, 헬퍼 코드, 툴 설명, 컨텍스트 정책, 재시도 루프, 분해 구조)의 재작성으로 나아가야 한다는 방향성, 그리고 RL이 단순 텍스트가 아닌 "더 풍부한 액션 공간"에서 에이전트의 귀납적 추론을 학습해야 한다는 가설은 향후 에이전트 연구의 중요한 방향을 제시한다.

---

## 더 실습해보고 싶은 분들께

에이전트 하네스·자동화·루프 엔지니어링에 관심이 있다면, 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 실제 에이전트 하네스를 다양한 시나리오에서 끌어올리는 50가지 활용 패턴
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 컨텍스트 엔지니어링의 실전 강의

NOOA처럼 "에이전트 = 프로그램"이라는 관점에서 자신만의 하네스를 설계해보고 싶다면 두 자료 모두 좋은 출발점이 됩니다.
