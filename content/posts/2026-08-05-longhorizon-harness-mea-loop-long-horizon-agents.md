---
title: "긴 호라이즌 에이전트의 함정: LongHorizon-Harness가 바꾸는 실행 구조"
date: 2026-08-05
tags:
  - agent
  - harness
  - LLM
  - long-horizon
  - task-state
  - MEA-loop
  - automation
  - tool-use
  - computer-use
  - OpenClaw
---

에이전트가 30분짜리 작업을 시작하고 중간에 길을 잃는 경험, 해보셨을 겁니다. METR의 보고서는 에이전트 작업 호라이즌이 7개월마다 두 배로 늘어난다고 하는데, 호라이즌이 길어진다고 끝까지 안정적으로 실행되는 건 또 다른 문제입니다.

Alibaba DreamX팀이 이 문제를 공격했습니다. 그들의 진단은 명확합니다. 기존 하네스(Claude Code, Codex, OpenClaw 등)는 task execution과 task state management를 같은 컨텍스트에서 처리합니다. 실행 히스토리가 길어지면 상태 추적이 안 되고, 에이전트가 자기 완료 주장을 검증 없이 state로 받아들입니다.

## MEA 루프: 실행과 검증을 분리하다

![MEA 루프 구조도](/images/2026-08-05-longhorizon-harness-mea-loop-long-horizon-agents/mea-overview.png)

LongHorizon-Harness의 핵심 설계는 Manage-Execute-Audit 루프입니다. 세 역할이 라운드별로 돌아갑니다.

**Manager**는 task state를 유지하면서 다음 서브태스크를 정합니다. 환경에는 직접 손을 대지 않습니다. 오직 audit report만 봅니다.

**Executor**는 fresh context에서 서브태스크만 수행합니다. 이전 실행 히스토리는 받지 않고, 계약(목표, 수락 기준)만 받습니다. Claude Code, Codex, OpenClaw 등 기존 하네스를 AgentAdapter로 그대로 연결합니다.

**Auditor**는 실행이 끝난 환경을 읽기 전용으로 검사합니다. 실행기의 보고를 믿지 않고, 환경의 실제 상태를 검증합니다. 파일, 메타데이터, 빌드 결과, 스크린샷을 직접 확인합니다.

검증된 fact만 다음 라운드로 넘어갑니다. 실행 히스토리는 버려집니다.

## 벤치마크: 세 환경에서 일관된 향상

![벤치마크 결과](/images/2026-08-05-longhorizon-harness-mea-loop-long-horizon-agents/benchmark-figure.png)

숫자로 보면:

WeaveBench에서 Qwen 3.7-Plus가 51.8% → 80.7%로 올라갔습니다. Terminal-Bench 2.1에서는 69.7% → 77.2%. OSWorld 2.0에서는 2.8% → 8.3%로, binary completion이 3배 가까이 늘었습니다.

Claude Opus 4.7을 쓰면 OSWorld 2.0 서브셋에서 20.6% → 35.3%로 향상됩니다. 약한 모델이든 강한 모델이든, 하네스 개선이 일관적으로 가져다줍니다.

특히 주목할 점은 시스템 관리 카테고리입니다. Terminal-Bench 2.1에서 0.593 → 0.889로 급등했는데, installation이나 service configuration 같은 상태ful 작업에서 audit이 "대충 끝낸 척"을 정확히 잡아냅니다.

## 비용은 얼마나 들까

Manager는 전체 토큰의 2~8%만 소모합니다. 상태 관리 오버헤드가 거의 없다는 뜻입니다. Auditor가 19~38%를 차지해서, 독립 검증이 주요 추가 비용입니다.

흥미로운 건 모델이 강할수록 전체 토큰이 줄어든다는 점입니다. Claude Opus 4.7은 OSWorld에서 토큰이 16.5M → 11.1M로 감소합니다. 강한 모델은 audit-replan 라운드가 적게 필요하니까요.

## 어디에 잘 맞고 안 맞나

환경 상태가 파일, 바이너리, 메타데이터로 검증 가능하면 효과가 큽니다. 문서 편집(XML 스타일 검증), 빌드(바이너리 존재 + 실행), 시스템 관리(서비스 상태)가 대표적입니다.

반면 숨겨진 성능 임계값이나 비디오 시각적 정밀도가 핵심인 작업에서는 한계가 있습니다. MTEB, data-science, video-processing 태그에서는 오히려 하락이 있습니다.

## 하네스가 모델을 넘는 순간

Qwen 3.7-Plus + LH-Harness의 게임 태스크 점수가 0.733입니다. Claude Opus 4.7 + 기본 Claude Code의 0.680보다 높습니다. 에이전트 능력은 모델만의 속성이 아니라 model-harness 시스템의 속성이라는 걸 보여주는 숫자입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고자료

- 논문: [LongHorizon-Harness: Advancing Long-Horizon Agents for Real-World Tasks](https://arxiv.org/abs/2608.01964)
- 벤치마크: WeaveBench, OSWorld 2.0, Terminal-Bench 2.1
