---
title: "OneDayAgent: 하루 종일 돌아가는 에이전트를 위한 롱호라이즌 하네스"
date: 2026-08-06
tags:
  - agent
  - harness
  - long-horizon
  - LLM
  - loop
  - automation
  - task-decomposition
  - verification
  - memory
  - MCP
  - tool-use
source: arxiv
source_url: https://arxiv.org/abs/2608.05013
---

OneDayAgent는 긴 시간이 걸리는 일상 작업(web 리서치, 로컬 파일 편집, 최종 결과물 생성)을 처리하기 위한 롱호라이즌 에이전트 하네스입니다. 저장대학(Zhejiang University)과 앤트그룹(Ant Group)이 제안했으며, 핵심 기여는 태스크 분해, 실행 메모리 관리, 전역 검증·수리를 하나의 하네스에서 통합한 점입니다. AgentIF-OneDay 벤치마크에서 GLM-5.2 백엔드 기준 전체 스코어 0.821을 달성했습니다.

## 1. 배경 및 문제 정의

LLM 에이전트가 처리하는 일상 작업은 세 가지 특성을 가집니다:

- Long-horizon: 목표와 제약을 여러 단계에 걸쳐 보존해야 함
- Cross-environment: 웹, 로컬 파일, 코드 실행, 외부 서비스 등 이기종 환경 간 전환
- Multimodal: 텍스트, 문서, 이미지, 표 등 다양한 입력

이로 인해 세 가지 실행 실패가 발생합니다: 목표 이탌(goal drift), 상태 유실(state loss), 컨텍스트 오버플로우. 기존 접근법은 개별 실패 모드만 다루었고, 이들이 복합적으로 작용하는 경우를 다루지 못했습니다.

## 2. OneDayAgent 설계

![](/images/2026-08-06-onedayagent-long-horizon-harness/fig-2-p3.png)

### 2.1 워크플로우

OneDayAgent는 5단계 워크플로우로 구성됩니다:

1. 태스크 분해 (Planner): 원 요청을 순차적 서브태스크 리스트로 변환
2. 서브태스크 실행 (Executor): 각 서브태스크를 ReAct 루프로 실행. 웹/학술/연산/파일/멀티모달 툴을 통합 액션 스페이스로 제공
3. 합성 (Synthesizer): 서브태스크 결과와 산출물을 결합하여 최종 결과물 후보 생성
4. 전역 검증 (Verifier): 후보 결과물을 원 요청 및 서브태스크 답변과 대조
5. 타겟팅 수리 (Repair): 검증 실패 시 문제 부분만 국소 수정

### 2.2 실행 메모리

세 가지 메모리 메커니즘이 동작합니다:

| 메커니즘 | 기능 |
|----------|------|
| 요약 절단 | 검색/웹/파일 관측값을 bounded evidence로 압축 |
| 서브태스크 상태 전달 | 서브태스크 경계에서 low-level trace를 버리고 compact checkpoint만 전달 |
| 자동 컨텍스트 압축 | 컨텍스트가 윈도우의 90% 도달 시 LLM 요약으로 압축, 하드 리밧 시 비상 프루닝 |

### 2.3 도구 인터페이스

![](/images/2026-08-06-onedayagent-long-horizon-harness/table-1-p3.png)

웹 액세스, 학술 검색, 연산, 파일 조작, 멀티모달 처리를 단일 ReAct 액션 스페이스로 통합했습니다. 산출물은 작업공간에 파일로 저장되어 후속 단계에서 참조 가능합니다.

## 3. 실험 결과

### 3.1 AgentIF-OneDay 메인 결과

![](/images/2026-08-06-onedayagent-long-horizon-harness/table-2-p6.png)

104 태스크, 767 인스턴스 채점 포인트로 평가했습니다.

| 에이전트 | 백엔드 | Overall | Latency(s) |
|----------|--------|---------|------------|
| Minimax-Agent | Gemini-3-Pro | 0.562 | 1416 |
| ChatGPT-Agent | Gemini-3-Pro | 0.626 | 665 |
| Genspark | Gemini-3-Pro | 0.635 | 484 |
| Manus | Gemini-3-Pro | 0.645 | 500 |
| Codex | GPT-5.5 medium | 0.664 | 326 |
| AutoClaw | — | 0.799 | 523 |
| OneDayAgent (GLM-5.2) | GLM-5.2 | 0.821 | 3217 |

모든 슬라이스(태스크 타입 OWE/LII/IR, 도메인 Work/Life/Study, 루브릭 Inst/Fact/Logic, 첨부파일 유무)에서 1위입니다.

### 3.2 에블레이션

| 변형 | Decomp | Verify | Overall | Latency(min) |
|------|--------|--------|---------|--------------|
| DIRECT | ✗ | ✗ | 0.771 | 19.0 |
| VERIFY | ✗ | ✓ | 0.804 | 21.2 |
| DECOMP | ✓ | ✗ | 0.804 | 29.6 |
| FULL | ✓ | ✓ | 0.821 | 34.8 |

검증만 추가해도 +3.3점을 얻고 지연은 2분만 증가합니다. 분해는 같은 점수에 10분이 더 필요합니다. 비용 효율 측면에서 verification-only가 가장 효과적입니다.

### 3.3 백엔드 분석

![](/images/2026-08-06-onedayagent-long-horizon-harness/fig-4-p9.png)

| 백엔드 | Overall | Latency(min) | Tool Calls | Context(KB) |
|--------|---------|--------------|------------|-------------|
| Qwen3.6-27B | 0.613 | 21.3 | 20.7 | 78.5 |
| Qwen3.5-9B | 0.624 | 31.6 | 25.1 | 95.3 |
| Qwen3.5-397B-A17B | 0.708 | 16.1 | 16.9 | 72.2 |
| Gemini-3.1-Pro | 0.743 | 21.4 | 18.7 | 118.1 |
| GLM-5.2 | 0.821 | 53.6 | 51.6 | 585.7 |

파라미터 스케일과 점수는 약한 상관만 보이며, 단조적이지 않습니다. 백엔드마다 실행 스타일(툴콜 수, 컨텍스트 축적, 수리율)이 다릅니다.

### 3.4 실행 행동

![](/images/2026-08-06-onedayagent-long-horizon-harness/fig-3-p8.png)

- 태스크 대부분이 2~4개 서브태스크로 분해됨 (104개 중 16개만 단일)
- 95개 1차 검증 통과, 9개 수리 진입 (6개 복구, 3개 실패)
- 35개 태스크가 컨텍스트 압축 트리거, 최대 350K 토큰 누적
- 압축 횟수와 스코어의 상관관계는 거의 0

### 3.5 케이스 스터디

꽃말 PPT 편집 태스크: 리서치 서브태스크(위키백과 자료 수집)와 PPT 수정 서브태스크로 분해. PPT 수정 중 파일 에러 발생 → 합성 단계에서 실패 보고 → 검증기가 누락된 PPT 식별 → 수리 단계에서 프레젠테이션 생성 → 2차 검증 통과.

## 4. 논의

OneDayAgent의 결과는 하네스 설계가 롱호라이즌 에이전트 성능에 미치는 영향을 보여줍니다. 세 가지 시사점이 있습니다:

1. 통합 하네스의 효과: 분해, 메모리, 검증을 개별적으로 다루는 것보다 하나의 하네스에서 통합할 때 더 높은 스코어 달성
2. 백엔드 무관성: 같은 하네스가 3개 모델 패밀리, 5개 백엔드에서 안정 동작
3. 비용-성능 trade-off: FULL 구성이 최고 스코어지만 평균 53분 소요. verification-only가 비용 효율 최적점

한계로는 AgentIF-OneDay 단일 벤치마크 평가, 워크스페이스 격리 미구현(보안 고려사항)이 있습니다.

코드와 트레젝토리는 zjunlp 깃허브에 공개되어 있습니다.

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
