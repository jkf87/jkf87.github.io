---
title: "AgentDebugX: LLM 에이전트가 실패할 때 디버깅하는 올바른 방법"
date: 2026-07-22
draft: false
tags:
  - agent
  - debugging
  - LLM
  - tool-use
  - observability
  - failure-attribution
categories:
  - AI Agent
summary: "UIUC·Google·Stanford 팀이 발표한 AgentDebugX는 LLM 에이전트의 실패를 관측하고 근본 원인을 특정하며 복구하는 폐루프 디버깅 프레임워크다. DeepDebug 다중 턴 진단 에이전트가 Who&When 벤치마크에서 최고 수준의 귀인 정확도를 기록하고, GAIA에서 실패한 73개 작업 중 13개를 단 한 번의 재실행으로 복구했다."
---

## 에이전트는 왜 디버깅하기 어려운가

LLM 에이전트가 점점 더 복잡한 작업을 수행하면서, 실패의 원인을 찾는 일은 작업 자체만큼이나 어려워지고 있다. 핵심 문제는 **에러가 보이는 지점과 에러를 만든 지점이 다르다**는 것이다.

예를 들어 에이전트가 최종 답변으로 잘못된 값을 반환했다고 하자. 하지만 진짜 원인은 수십 단계 앞에서 누락된 계획 제약 조건, 혹은 다른 에이전트로의 잘못된 핸드오프, 또는 만료된 메모리 조회일 수 있다. 단순히 실행 궤적(trace)을 다시 재생하는 것만으로는 이 근본 원인을 찾을 수 없다.

UIUC·Google·Stanford 연구팀이 발표한 **AgentDebugX**는 바로 이 간극을 메우는 오픈소스 디버깅 프레임워크다. 관측(Observability)에서 귀인(Attribution), 복구(Recovery), 재실행(Rerun)까지를 하나의 폐루프로 연결한다.

![AgentDebugX 시스템 개요: Detect → Attribute → Recover → Rerun 폐루프](/images/2026-07-22-agentdebugx-agent-failure-debugging/fig-1-p3.png)

> **그림 1.** AgentDebugX의 전체 파이프라인. 에이전트 실행 궤적을 입력받아 규칙 기반 탐지, 구조화 귀인, DeepDebug 다중 턴 진단을 거쳐 구체적 수정안을 제안하고 재실행한다.

## 폐루프 디버깅의 4단계

AgentDebugX는 에이전트 실패를 네 단계의 닫힌 루프로 처리한다.

### 1. Detect (탐지)

먼저 기계적으로 검증 가능한 실패를 찾는다 — 도구 호출 포맷 오류, 진행 없는 루프, 무효 출력, 조기 성공 선언 등이다. 규칙이 충분하지 않으면 LLM 판사(judge)가 목표와 궤적 윈도우를 읽고 유형화된 발견(finding)을 반환한다. 19개 시드 실패 모드가 기본 제공되며, 계획·메모리·도구 사용·검증·조정 카테고리를 아우른다.

### 2. Attribute (귀인)

탐지 단계가 찾은 증상을 **진짜 원인이 된 스텝**으로 추적한다. 단순 휴리스틱부터 단일 패스 전체 궤적 읽기, 이진 탐색, 스텝별 검사까지 비용과 정확도를 트레이드오프하는 여러 전략을 제공한다. 각 귀인기(attributor)는 순위화된 가설과 신뢰도, 출처를 반환한다. 모호한 케이스는 DeepDebug로 에스컬레이션된다.

### 3. Recover (복구)

근본 원인이 특정되면, 이를 실행 가능한 재시도 지시문으로 변환한다. DeepDebug 자체의 수정안을 그대로 쓰거나 Reflexion, CRITIC, AutoManual 등 기존 자기수정 방법을 대안 전략으로 사용할 수 있다. 모든 수정은 인간 또는 정책 게이트 뒤에서만 적용된다.

### 4. Rerun (재실행)

진단과 체크포인트, 재시도 지시문을 패키징해서 새로운 궤적을 생성한다. 원본과 복구본을 나란히 비교할 수 있고, 성공한 브랜치는 해결 사례로 저장되며, 실패한 브랜치는 다시 탐지 루프로 들어간다.

## DeepDebug: 다중 턴 근본 원인 진단 에이전트

AgentDebugX의 핵심 혁신은 **DeepDebug**다. 단일 패스 귀인은 두 가지 맹점이 있다 — 전역 읽기는 가장 눈에 띄는 다운스트림 증상에 고착하고, 좁은 스텝별 스캔은 목표를 잃어버린다. DeepDebug는 이를 네 단계로 해결한다.

![AgentDebugX 웹 콘솔: 실패한 실행을 네 단계로 검토](/images/2026-07-22-agentdebugx-agent-failure-debugging/fig-2-p5.png)

> **그림 2.** AgentDebugX 웹 콘솔. (1) 실패한 실행 선택 → (2) 귀인된 원인 이벤트로 점프 → (3) 실패 모드·증거·수정안 검토 → (4) 정책 게이트 재실행 브랜치 생성.

**Stage 1 — 전역 읽기.** 에이전트가 전체 궤적을 읽고 목표와 히스토리를 재구성한 뒤, 결정적 스텝의 초기 후보를 지정한다.

**Stage 2 — 구조 기반 조사.** 멀티 에이전트 실행이면 핸드오프 캐스케이드를 상향 추적하고, 단일 에이전트면 스텝 범위를 이분 탐색으로 좁혀 독립적인 두 번째 후보를 얻는다.

**Stage 3 — 교차 검증.** 두 패스가 일치하면 채택하고, 불일치하면 두 후보를 나란히 검사하여 더 강한 인과 설명을 선택한다. 전체 궤적 탐색이 아니라 두 가설 사이의 집중된 판단으로 문제가 환원된다.

**Stage 4 — 진단 및 제안.** 책임 에이전트와 스텝, 평문 설명, 인용 증거, 구체적 수정안 하나를 구조화된 보고서로 출력한다. 모든 검사가 기록되어 감사 추적을 제공한다.

## 벤치마크 결과

### Who&When: 귀인 정확도

![Who&When 벤치마크 실패 귀인 결과](/images/2026-07-22-agentdebugx-agent-failure-debugging/table-2-p6.png)

> **표 2.** Who&When 벤치마크에서의 실패 귀인 정확도. DeepDebug는 테스트된 두 오픈 웨이트 백본 모두에서 최고 수준의 정확도를 달성했다.

DeepDebug는 qwen3.5-9b 백본에서 **28.8%의 strict agent-and-step 정확도**를 기록했다. 가장 강력한 단일 패스 baseline의 21.7%를 크게 웃도는 수치다. 귀인이 정확해야 복구도 가능하다는 점에서 이 격차는 단순한 스펙 경쟁이 아니다.

### GAIA: 엔드투엔드 복구

![GAIA 벤치마크 엔드투엔드 복구 결과](/images/2026-07-22-agentdebugx-agent-failure-debugging/table-3-p6.png)

> **표 3.** GAIA 검증 세트에서의 엔드투엔드 복구 결과. DeepDebug의 진단을 적용한 단일 재실행이 기존 자기수정 baseline들을 능가했다.

GAIA 벤치마크에서 DeepDebug의 진단을 단 한 번의 재실행에 적용하자, 기존에 실패했던 73개 작업 중 **13개를 복구**했다. 세 개의 분리된 자기수정 baseline들이 각각 4–6개만 복구한 것과 비교하면 압도적이다. 전체 정확도는 55.8%에서 **63.6%**로 향상되었다.

이 결과가 시사하는 바는 명확하다. **에러 위치를 알려주면 모델은 훨씬 더 잘 고친다.** 자기수정 연구(Tyen et al., 2024)에서도 "모델은 추론 에러를 스스로 찾기는 어렵지만, 위치를 알려주면 고칠 수 있다"는 결론이 반복됐다. AgentDebugX는 바로 그 위치를 정확하게 찾아주는 인프라다.

## 확장 가능한 실패 분류 체계

고정된 분류 체계는 모든 롱테일 에러를 예상할 수 없다. AgentDebugX는 판사(judge)가 기존 시드에 없는 실패를 만나면 novel-mode 후보로 기록하고, 유도기(inducer)가 이를 클러스터링하여 새로운 실패 모드를 제안한다. 예를 들어 여러 실행에서 에이전트들이 서로를 무한히 기다리는 패턴이 발견되면, "multi-agent deadlock" 모드가 제안되고 기존 "lost-handoff" 카테고리와의 관계가 표시된다. 단, 제안은 큐레이션된 분류 체계를 덮어쓰지 않는다.

## 시스템 통합

AgentDebugX는 Python 라이브러리, CLI, 웹 콘솔, 에이전트 스킬로 노출된다. `pip install agentdebugx` 한 줄로 시작할 수 있고, `agentdebug serve`로 로컬 웹 디버거를 띄운다.

**프레임워크 호환성:** LangGraph, CrewAI, OpenAI Agents SDK, OpenTelemetry, raw ReAct 형식의 궤적을 모두 동일한 `AgentTrajectory` 표현으로 변환한다. 진단은 원본 프레임워크와 무관하게 동작한다.

**Error Hub:** 궤적, 진단 보고서, 아티팩트를 하나의 번들로 패키징하여 공유할 수 있다. 기본적으로 이벤트 입력 전체를 스트리핑하고, 남은 문자열에서는 알려진 패턴의 자격 증명과 PII를 삭제한다. CI 회귀 픽스처, 내부 사후 검토, 재사용 가능한 디버깅 메모리로 활용된다.

## 왜 중요한가

에이전트 시스템이 프로덕션에 배포될수록, "무엇이 잘못되었는가"보다 **"어디서 잘못되기 시작했는가"**가 더 중요해진다. AgentDebugX는 이 질문에 구조화되고 감사 가능한 방식으로 답한다.

기존 관측 도구(Langfuse, LangSmith, Phoenix)가 트레이스를 보여주는 데 그쳤다면, AgentDebugX는 거기서 한 걸음 더 나아간다 — 근본 원인을 특정하고, 수정안을 제안하고, 재실행으로 검증까지 수행한다. 벤치마크 결과가 말해주듯, 이 접근은 단순한 자기수정보다 2–3배 더 많은 실패를 복구한다.

에이전트 디버깅에 관심이 있는 연구자나 엔지니어에게, AgentDebugX는 현재 사용할 수 있는 가장 완성도 높은 오픈소스 도구다.

## 더 실습해보고 싶은 분들께

에이전트 디버깅, 도구 사용, 하네스 설계와 같은 주제를 직접 실험해보고 싶다면 다음 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 자동화와 도구 활용을 실전에서 다루는 활용 가이드
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 컨텍스트 엔지니어링의 기초부터 실습까지

---

**참고문헌**

- Zhu et al., "AgentDebugX: An Open-Source Toolkit for Failure Observability, Attribution, and Recovery in LLM Agents," arXiv:2607.18754, 2026. [Paper](https://arxiv.org/abs/2607.18754) | [Code](https://github.com/AgentDebugX/AgentDebugX) | [Project](https://www.agentdebugx.com)
- Tyen et al., "LLMs Cannot Find Reasoning Errors, But Can Correct Them Given the Error Location," 2024.
- Cemri et al., "Why Do Multi-Agent LLM Systems Fail?" (MAST), 2026.
