---
title: "AMD: 작은 에이전트에게 선생 메모리를 물려주는 계층적 증류"
date: 2026-08-11
draft: false
summary: "4B 학생 에이전트가 GPT-5-mini 선생의 경험을 3단계 메모리로 흡수한다. AppWorld +27.2%p, BFCL V3 +11.2%p. 학습 없이, 메모리 주입만으로."
tags: ["agent", "memory", "LLM", "knowledge-distillation", "tool-use", "small-model", "harness", "KAIST"]
cover: /images/2026-08-11-agent-memory-distillation/fig-1-p1.png
---

작은 LLM 에이전트는 혼자서 성공 궤적을 많이 만들지 못합니다. 성공률이 낮으니까요. 그래서 자기 경험에서 뽑은 메모리도 실패 투성이입니다.

KAIST 연구팀이 제안한 Agent Memory Distillation (AMD)는 선생 에이전트(GPT-5-mini)의 성공 궤적에서 3단계 메모리를 뽑아서 학생 에이전트(4B~8B)에 주입합니다. 학습(파인튜닝)은 없습니다. 메모리 주입만으로 AppWorld에서 +27.2%p, BFCL V3에서 +11.2%p, ToolSandbox에서 +3.4%p 올랐습니다.

논문: *Agent Memory Distillation: Empowering Small LLM Agents with Hierarchical Teacher Memory* (Kim et al., KAIST, 2026) — [arXiv:2608.07169](https://arxiv.org/abs/2608.07169)

## 핵심 문제

![Figure 1: AMD의 동기와 개념](/images/2026-08-11-agent-memory-distillation/fig-1-p1.png)

메모리 전송에는 두 가지 함정이 있습니다.

1. 학생 자신의 메모리는 품질이 낮다 — 4B 모델은 AppWorld에서 15% 정도 성공률이라, 성공 궤적이 거의 없습니다.
2. 선생 메모리를 그대로 줘도 안 된다 — GPT-5-mini의 고수준 전략("먼저 로그인하라")을 4B가 이해 못 합니다. 능력 차이(capability gap)가 걸림돌입니다.

단순 전송으로는 zero-shot과 거의 차이가 없었습니다.

## 3단계 계층 메모리

![Figure 2: AMD의 계층적 메모리 생성과 주입](/images/2026-08-11-agent-memory-distillation/fig-2-p4.png)

AMD는 세 가지 메모리를 다른 시점에 다르게 주입합니다.

| 메모리 종류 | 내용 | 주입 시점 | 형태 |
|---|---|---|---|
| Workflow | 태스크 전략, 관련 앱/도구, 검증 단서 | 시작 시 proactive | 자연어 |
| Subtask | 서브태스크별 구체적 행동 예시 | 시작 시 proactive | 코드 블록 |
| Function | 함수별 호출 규약, 실패 패턴 | 에러 시 reactive | 코드+문서 |

Workflow는 자연어로, Subtask와 Function은 실행 가능한 코드로 줍니다. 이 선택이 중요합니다 — 고수준 계획은 prose가 좋고, 저수준 실행은 코드가 낫습니다.

## 결과

![Table 1: 세 벤치마크 주요 결과](/images/2026-08-11-agent-memory-distillation/table-1-p6.png)

| 학생 모델 | AppWorld | BFCL V3 | ToolSandbox |
|---|---|---|---|
| Qwen3-4B zero-shot → AMD | 14.88 → 49.40 | 29.13 → 40.38 | 52.63 → 55.81 |
| Qwen3-8B zero-shot → AMD | 19.64 → 51.79 | 35.54 → 40.96 | 57.14 → 60.00 |
| Gemma4-E4B zero-shot → AMD | 15.48 → 54.17 | 30.88 → 40.63 | 55.04 → 58.91 |
| GPT-5-mini (선생) | 50.00 | 38.39 | 61.63 |

Gemma4-E4B와 Qwen3-8B는 AppWorld에서 선생(GPT-5-mini, 50.00%)을 넘겼습니다.

## Subtask 메모리가 가장 크다

![Table 2: 메모리 구성 요소별 기여도](/images/2026-08-11-agent-memory-distillation/table-2-p7.png)

Ablation을 돌려보면:

- Workflow만: zero-shot 대비 일관된 향상
- Subtask 추가: AppWorld에서 +25.0%p — 가장 큰 기여
- Function 추가: 추가 이득은 있지만 폭은 작다
- 학생 자신의 메모리: zero-shot과 거의 같음

구체적인 코드 예시가 있어야 4B 모델이 실제로 행동을 바꿉니다. 자연어 설명만으로는 부족합니다.

## 상호작용 효율

![Figure 3: AMD가 학생의 턴 수를 선생 수준으로](/images/2026-08-11-agent-memory-distillation/fig-3-p6.png)

AMD를 쓰면 학생의 턴 수가 선생에 가까워집니다. Qwen3-4B 기준 AppWorld에서 23.8턴 → 14.9턴(선생 10.1턴). 메모리가 "무엇을 할까"뿐 아니라 "얼마나 효율적으로 할까"까지 전달됩니다.

## k=1이 최선이다

검색 수 k를 1에서 5까지 늘려보면, k=1일 때 가장 좋습니다. 특히 Subtask 메모리는 k가 커질수록 정확도가 떨어집니다(49.40% → 33.34%). 작은 모델은 추가 컨텍스트가 노이즈가 됩니다. 정밀한 주입이 다수 주입보다 낫습니다.

## 능력 차이를 메모리 계층으로 좁힌다

단순한 메모리 전송이 안 되는 이유는 선생과 학생 사이의 이해력 차이입니다. AMD는 이 차이를 3단계로 쪼개서 메꿉니다:

- 전략은 자연어로 (Workflow)
- 실행 예시는 코드로 (Subtask)
- 에러 교정은 반응형으로 (Function)

k=1 주입, 코드 중심 Subtask, 반응형 Function — 이 조합이 4B 에이전트를 선생급으로 끌어올립니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
