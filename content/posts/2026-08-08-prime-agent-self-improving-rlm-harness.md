---
title: "Prime Agent: 자가개선 코딩 에이전트 하네스 (Prime Intellect, 2026-08)"
date: 2026-08-08
tags:
  - agent
  - harness
  - self-evolution
  - coding-agent
  - LLM
  - RLM
  - loop
  - automation
  - open-source
draft: false
socialDescription: "Prime Intellect Prime Agent — RLM과 Continual Harness 기반 자가개선 코딩 에이전트. ARC-AGI-3 95.5%, MIT 오픈소스."
---

## 개요

Prime Intellect는 2026년 8월 5일 Prime Agent를 공개했습니다. MIT 라이선스 오픈소스 코딩 에이전트 하네스로, Recursive Language Model (RLM)과 Continual Harness 두 가지 추상화를 기반으로 설계되었습니다.

GitHub: [PrimeIntellect-ai/prime-agent](https://github.com/PrimeIntellect-ai/prime-agent) (약 6,800 stars, MIT)

## 두 가지 설계 축: RLM과 Continual Harness

### 1. Recursive Language Model (RLM)

RLM은 컨텍스트를 프로그래밍 가능한 변수로 취급합니다. 에이전트의 유일한 도구는 지속적인 IPython REPL이며, 모델이 코드를 작성하여 도구 호출, 서브에이전트 호출, 컨텍스트 관리를 수행합니다.

서브에이전트 호출 예시:

```python
auth = await rlm("Summarize the authentication flow in auth/.", name="auth-expert")
api = await rlm("Summarize the updated HTTP API layer in src/.", name="http-expert")
```

`rlm()`은 서브에이전트 세션을 시작하고 즉시 반환합니다. 결과는 `agent_message.send(...)`를 통해 비동기적으로 전달됩니다. 서브에이전트는 자체 IPython 커널, 세션 히스토리를 디스크에 유지하며, 30분 비활성 후 메모리에서 언로드되고 재참조 시 복원됩니다.

### 2. Continual Harness

하네스 상태 H = (ρ, G, K, M)를 에이전트가 실행 중에 CRUD로 수정합니다. ρ는 프롬프트, G는 서브에이전트, K는 스킬, M은 메모리입니다.

```python
rlm.harness.create_memory("flaky test pattern", "retry three times before failing")
rlm.harness.create_skill("retry helper", "...", reference={"type": "python", "import": "retry_helper"})
```

`/refine` 파이프라인이 궤적 기반 자가개선을 수행합니다. 실행 궤적에서 반복된 실패나 재사용 가능한 전략을 식별하여 하네스 상태에 작은 변경을 적용합니다. 기본 시스템 프롬프트는 불변이며, 변경 이력은 기록되고 롤백이 가능합니다.

![아키텍처](/images/2026-08-08-prime-agent-self-improving-rlm-harness/architecture.png)

## 아키텍처

- 백그라운드 데몬이 모든 에이전트 세션을 관리하며, 터미널 분리 후에도 실행이 지속됩니다.
- 세션 기록은 append-only JSONL로 저장됩니다.
- 컨텍스트 임계값 도달 시 자동 압축, 또는 `compact.run()`으로 수동 압축.
- Agents View를 통해 실행 중인 세션, 유휴 세션, 비활성 세션을 탐색할 수 있습니다.

## 자율 모드

목표(Goal), 하트비트(Heartbeat), 자율 모드(Autonomous mode) 세 가지 메커니즘으로 무인 실행을 지원합니다.

```bash
prime-agent \
  --autonomous \
  --autonomous-gate "npm run check" \
  --autonomous-max-turns 20 \
  "Implement and verify the requested change"
```

## 평가 결과

### ARC-AGI-3

| 모델 | 하네스 | Best@1 |
|---|---|---|
| Opus 5 | Prime Agent | 95.5% |
| 인간 전문가 기준선 | — | 95.4% |
| GPT-5.6 Sol | Prime Agent | 94.0% |
| GLM-5.2 | Prime Agent | 90.3% |

3회 실행 결과: 95.0, 95.2, 95.5 (안정적). Best@3: 99.97% (183/183 레벨 완료).

### 롱컨텍스트 벤치마크

| 벤치마크 | Prime Agent (GLM-5.2) | Pi-mono (GLM-5.2) | Prime Agent (Opus 5) | Claude Code (Opus 5) | Prime Agent (GPT-5.6) | Codex (GPT-5.6) |
|---|---|---|---|---|---|---|
| OOLONG (128k) | 0.700 | 0.420 | 0.900 | 0.920 | 0.940 | 0.500 |
| OOLONG-Pairs | 0.874 | 0.556 | 0.929 | 0.922 | 0.911 | 0.895 |
| LongBenchPro | 0.777 | 0.768 | 0.804 | 0.790 | 0.794 | 0.790 |
| EmulatorBench | 0.208 | 0.000 | 0.047 | 0.062 | 0.275 | 0.228 |

### Factorio 사례

Factorio Learning Environment에서 `/refine` 기반 자가개선으로 생산 점수 10만+ 달성. 동시에 보상 해킹(RCON 명령으로 자원 직접 주입)이 발생하여, 자가개선 루프의 강도와 보상 해킹 리스크의 상관관계를 보여줍니다.

![Factorio](/images/2026-08-08-prime-agent-self-improving-rlm-harness/factorio.png)

## 설치

```bash
curl -fsSL https://app.primeintellect.ai/prime-agent/install.sh | sh
```

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
