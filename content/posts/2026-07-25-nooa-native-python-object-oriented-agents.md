---
title: "NOOA: 에이전트를 파이썬 객체로 만든다 — NVIDIA가 제안하는 하네스 설계의 정답지"
date: 2026-07-25T13:00:00+09:00
draft: false
tags: ["agent", "harness", "LLM", "NVIDIA", "Python", "automation", "loop", "tool use"]
categories: ["AI Agents", "Agent Harness"]
summary: "NVIDIA의 NOOA(Object-Oriented Agents) 프레임워크는 에이전트를 파이썬 클래스로, 메서드를 액션으로, 타입 애너테이션을 계약으로 만든다. 프롬프트 엔지니어링을 소프트웨어 엔지니어링으로 끌어들이는 설계를 분석한다."
---

에이전트 프레임워크가 너무 많다. LangChain, LangGraph, Claude Agent SDK, OpenAI Codex, OpenHands, smolagents, Google ADK — 각자 고유한 추상화, 고유한 DSL, 고유한 학습 곡선을 가져온다. 그리고 에이전트 소스코드는 프롬프트 템플릿, 툴 스키마, 콜백, 설정 파일, 오케스트레이션 코드로 찢어진다.

NVIDIA가 발표한 **NOOA(NVIDIA Object-Oriented Agents)**는 질문을 바꾼다: "에이전트가 파이썬 객체면 안 되나?"

## 핵심 발상: 에이전트 = 파이썬 클래스

NOOA의 에이전트는 하나의 파이썬 클래스다:

- **메서드** = 모델이 호출할 수 있는 액션
- **필드** = 에이전트의 상태
- **독스트링** = 프롬프트
- **타입 애너테이션** = 입출력 계약
- `...` (말줄임표) 바디 = LLM이 채우는 에이전틱 메서드
- 일반 코드 바디 = 결정론적 파이썬 메서드

![Figure 1: NOOA에서 간단한 에이전트를 구현한 예시. 클래스가 동시에 소스코드, 프롬프트 표면, 타입 계약, 툴 인터페이스, 상태 경계가 된다.](/images/2026-07-25-nooa-native-python-object-oriented-agents/fig-1-p2.png)

`...` 바디를 가진 메서드에 도달하면 하네스가 개입하여 LLM 루프를 실행하고, 일반 메서드는 그냥 파이썬으로 실행된다. 같은 클래스 안에 두 종류가 공존한다.

## 여섯 가지 모델 대면 인터페이스

NOOA가 기존 프레임워크와 구별되는 지점은 여섯 가지 모델 대면(model-facing) 기능을 하나의 표면에 결합했다는 점이다:

### 1. Typed I/O — 타입 입출력
에이전트 메서드 호출은 텍스트 교환이 아니라 타입이 지정된 메서드 호출이다. 인자는 타입이 있고, 반환값도 타입이 있다. 하네스가 렌더링하고 검증한다.

### 2. Pass by Reference — 참조 전달
모델은 직렬화된 텍스트가 아니라 **살아 있는 파이썬 객체**를 다룬다. 100만 행짜리 테이블을 받아도 컨텍스트 창에는 타입, 길이, 앞뒤 샘플만 보인다. 모델은 변수 이름을 보고 코드로 전체 데이터를 조작한다.

```
numbers: list[int] (len=100) = [1, 2, 3, ..., 99, 100]
```

이 짧은 프리뷰만 컨텍스트에 들어가고, 실제 변수는 전체 100개 원소를 가진 채 실행 환경에 존재한다.

### 3. Code as Action — 코드가 곧 액션
모델이 JSON 툴콜을 만드는 대신 파이썬 코드를 작성한다. 루프, 조건분기, 임포트, 라이브러리 호출이 모두 가능하다. LLM이 이미 학습한 파이썬 지식을 그대로 끌어온다.

### 4. Loop Engineering — 프로그래밍 가능한 루프
오케스트레이션을 위한 별도의 워크플로우 언어가 없다. 외부 루프는 일반 파이썬 메서드, 내부 루프는 모델이 작성하는 코드. 개발자와 모델이 같은 제어 흐름을 공유한다.

### 5. Object State — 객체 상태
에이전트의 상태는 대화 기록이 아니라 **객체의 필드**다. 세션 간에 살아있고, 컨텍스트 압축에도 살아남는다. 매 턴마다 라이브 객체에서 렌더링된다.

### 6. Harness APIs — 하네스 API 노출
컨텍스트 블록, 이벤트 히스토리, 동적 컨텍스트가 모두 모델이 호출할 수 있는 파이썬 API로 노출된다. 모델이 자신의 컨텍스트를 직접 관리할 수 있다.

![Figure 3: NOOA의 컨텍스트 렌더링 구조. ContextManager와 EventManager가 정적 컨텍스트, 이벤트 히스토리, 동적 컨텍스트를 각 턴마다 채운다.](/images/2026-07-25-nooa-native-python-object-oriented-agents/fig-3-p6.png)

## CodeAct 전략: 에이전트 루프의 실제

NOOA의 기본 전략인 CodeAct는 파이썬 REPL을 에이전트 루프로 사용한다:

1. **컨텍스트 렌더링**: 정적 블록 + 이벤트 히스토리 + 동적 블록을 조합
2. **LLM 호출**: 모델은 파이썬 코드를 작성하거나 결과를 반환
3. **Python 실행**: 코드를 제한된 REPL 세션에서 실행
4. **상태 업데이트**: 실행 결과로 이벤트와 상태를 갱신
5. **반환 검증**: 타입 애너테이션 against 반환값 검증

![Figure 2: CodeAct 전략 루프. 호출자가 메서드를 호출하면 각 턴은 컨텍스트 렌더링 → LLM 호출 → Python 액션 실행 → 이벤트/상태 업데이트를 거쳐 타입 검증된 값이 반환될 때까지 반복된다.](/images/2026-07-25-nooa-native-python-object-oriented-agents/fig-2-p5.png)

KV-cache 재사용을 극대화하는 구조다: 정적 접두사는 변경되지 않고, 이벤트 히스토리는 메시지를 추가하기만 하고, 휘발성 동적 블록은 꼬리에 배치된다.

## 컨텍스트 엔지니어링 = 파이썬 API

![Figure 4: NOOA의 컨텍스트 엔지니어링. 컨텍스트 블록과 이벤트 히스토리가 개발자와 에이전트 모두에게 파이썬 API로 노출된다.](/images/2026-07-25-nooa-native-python-object-oriented-agents/fig-4-p6.png)

개발자와 모델이 같은 API로 컨텍스트를 다룬다. `self.context.add_block(...)`, `self.events.query(...)` — 프롬프트 빌딩을 위한 외부 스크립트가 아니다.

## 프레임워크 비교: 14개 하네스 평가

NOOA 논문의 가장 흥미로운 부분 중 하나는 14개 주요 에이전트 프레임워크를 위 여섯 가지 기준으로 비교한 표다. LangGraph, Claude Agent SDK, OpenAI Codex, OpenHands, smolagents, Google ADK, OpenClaw 등이 포함된다.

대부분의 프레임워크가 여섯 가지 중 일부만 지원한다. 예를 들어:

| 프레임워크 | Typed I/O | Pass by Ref | Code as Action | Loop Eng. | Object State | Harness APIs |
|---|---|---|---|---|---|---|
| **NOOA** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| LangGraph | 부분 | 부분 | 부분 | 부분 | 부분 | 부분 |
| Claude Agent SDK | 출력만 | 파일 | 셸 | 부분 | 부분 | 부분 |
| OpenHands | 텍스트 | 파일 | 부분 | 부분 | 부분 | ✗ |
| smolagents | 객체 I/O | 네임스페이스 | ✅ | 부분 | 비타입 | ✗ |
| OpenClaw | 텍스트 | 파일 | 부분 | 부분 | 부분 | ✗ |

NOOA는 여섯 가지를 **모두** 하나의 표면에 결합한 최초의 프레임워크임을 주장한다.

## 벤치마크 성능

### SWE-bench Verified

![Table 3: SWE-bench Verified 패스율. NOOA 인터페이스로 여러 모델을 테스트한 결과.](/images/2026-07-25-nooa-native-python-object-oriented-agents/table-3-p14.png)

### Terminal-Bench 2.0

![Table 4: Terminal-Bench 2.0 (89개 태스크) 결과.](/images/2026-07-25-nooa-native-python-object-oriented-agents/table-4-p14.png)

### ARC-AGI-3

ARC-AGI-3 인터랙티브 추론 벤치마크에서는 멀티에이전트 월드모델 시스템을 단일 에이전트 + 1페이지 스킬로 압축하면서 스코어-비용 파레토 프론티어를 advance시켰다.

현재 모델들이 NOOA 인터페이스를 **학습한 적 없음에도** 효과적으로 사용한다는 점이 중요하다. 파이썬 클래스, 메서드, 타입 애너테이션이 모델 학습 데이터에 이미 풍부하게 존재하기 때문이다.

## 메모리 시스템

![Figure 5: NOOA의 메모리 시스템. MemoryManager.install(agent)가 에이전트에 메모리를 부착한다.](/images/2026-07-25-nooa-native-python-object-oriented-agents/fig-5-p10.png)

메모리도 객체 모델의 일부다. 별도의 벡터 DB나 외부 스토어가 아니라, 에이전트 객체에 부착되는 MemoryManager를 통해 add/update/delete 연산을 수행한다.

## 왜 중요한가

NOOA의 의미는 "또 하나의 프레임워크"가 아니라 **에이전트 설계의 수렴점**을 보여준다는 데 있다.

1. **프롬프트 엔지니어링 → 소프트웨어 엔지니어링**: 에이전트 행동을 일반 소프트웨어처럼 테스트, 디버그, 리팩터, 버전 관리할 수 있다.

2. **학습 곡선 제거**: 파이썬 개발자가 추가로 배울 것이 없다. 에이전트 = 클래스, 액션 = 메서드, 상태 = 필드.

3. **모델 친화적**: LLM이 이미 아는 파이썬을 그대로 사용. 새로운 DSL이나 툴 스키마를 배울 필요가 없다.

4. **확장 가능한 하네스**: 컨텍스트, 이벤트, 메모리가 모두 파이썬 API로 노출되므로, 에이전트가 자기 자신을 개선하는 루프를 만들 수 있다.

논문이 제시하는 미래 방향도 흥미롭다: 에이전트 최적화를 프롬프트 탐색이 아니라 **에이전트 객체 전체 재작성**(docstring, 타입 시그니처, 헬퍼 코드, 컨텍스트 정책 포함)으로 확장하고, RL을 통해 하네스 API 활용 자체를 학습하는 방향이다.

> "진전은 더 큰 모델이나 더 좋은 프롬프트뿐만 아니라, 모델과 하네스의 공동 개발에서 올 것이다. 소프트웨어 인터페이스가 그 공동 개발의 장소다."

## 더 실습해보고 싶은 분들께

에이전트 하네스 설계와 파이썬 네이티브 에이전트 루프에 관심이 생겼다면, 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스를 실제로 구성하고 자동화 루프를 설계하는 실전 활용법
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프와 컨텍스트 엔지니어링을 체계적으로 배우는 강의

---

**Paper**: [NVIDIA Object-Oriented Agents (NOOA)](https://arxiv.org/abs/2607.20709) — Paul Furgale et al., NVIDIA Labs, 2026
**Code**: [github.com/NVIDIA-NeMo/labs-OO-Agents](https://github.com/NVIDIA-NeMo/labs-OO-Agents)
