---
title: "논문 정리: PASTE — LLM 에이전트에서 툴 실행을 미리 돌려서 지연시간 43.5% 줄이기 (arXiv 2603.18897)"
date: 2026-08-25
tags:
  - agent
  - LLM
  - serving
  - tool-use
  - latency
  - systems
draft: false
---

## 결론 먼저

에이전트가 느린 이유 중 하나는 LLM 생성과 툴 실행이 한 줄로 직렬로 묶여 있기 때문입니다. LLM이 툴 콜을 내보내면, 툴이 끝날 때까지 GPU는 기다립니다.

PASTE는 이 직렬 루프를 깨는 서빙 시스템입니다. 과거 에이전트 트레이스에서 반복되는 툴 호출 패턴을 학습해, LLM이 아직 생성 중일 때 다음에 올 툴 호출을 예측해서 미리 실행합니다. 그 결과:

- <span style="background-color: #fff59d"><strong>평균 태스크 완료 시간 43.5% 감소</strong></span>
- <span style="background-color: #fff59d"><strong>관측된 툴 지연시간 1.8배 감소</strong></span>
- p99 테일 지연시간 최대 55.4% 감소

측정 환경은 deep research, 코딩, AI-for-Science 워크로드, Qwen-DeepResearch-30B / Qwen3-30B-A3B, vLLM 서빙 스택입니다. 구현은 에이전트 쪽 TypeScript 5k 줄 + vLLM 훅 Python 2k 줄이고, <span style="background-color: #fff59d"><strong>vLLM 소스코드는 건드리지 않습니다</strong></span>.

원문: [Parallelizing Tool Execution and LLM Generation for Low-Latency Agent Serving (arXiv 2603.18897)](https://arxiv.org/abs/2603.18897)

## 문제: 툴 실행이 임계 경로의 절반 가까이다

![Figure 3. Breakdown of tool execution and LLM generation](/images/2026-08-25-paste-speculative-tool-execution/fig-3-p3.png)

논문이 측정한 워크로드에서 <span style="background-color: #fff59d"><strong>툴 실행은 에이전트 E2E 지연시간의 45%–57%를 차지</strong></span>합니다. 이 비용은 직렬 경로 위에 그대로 노출되어 있어서, LLM 생성을 아무리 빠르게 만들어도 줄지 않습니다.

그래서 이 논문의 목표는 토큰 수준 지연이 아니라 <span style="background-color: #fff59d"><strong>태스크 수준 E2E 지연</strong></span>입니다. 서빙 시스템의 최적화 대상이 여기로 옮겨갔다는 점이 핵심입니다.

## 관찰: 다음 툴 호출은 예측 가능하다

![Figure 2. Recurring tool-call patterns](/images/2026-08-25-paste-speculative-tool-execution/fig-2-p1.png)

실제 에이전트 트레이스에는 반복되는 서브워크플로우가 있습니다. 예를 들어:

- search 다음에 visit
- edit 다음에 run test
- grep 다음에 file_editor

숫자로 보면:

- <span style="background-color: #fff59d"><strong>성공한 file_editor 호출의 55% 뒤에 터미널 실행이 따라온다</strong></span>
- <span style="background-color: #fff59d"><strong>웹 방문의 95%에서 URL이 앞선 search 출력의 부분문자열이다</strong></span>

즉 다음 툴 이름뿐 아니라 인자까지 이전 관찰에서 복사되는 경우가 많아서, LLM이 콜을 내기 전에 이미 실행 가능한 형태로 예측할 수 있습니다.

## 방법: PASTE 세 가지 컴포넌트

![Figure 7. System architecture of PASTE](/images/2026-08-25-paste-speculative-tool-execution/fig-7-p5.png)

PASTE는 LLM 엔진과 툴 실행기 위에 컨트롤 플레인을 얹는 구조입니다. 컴포넌트는 세 개입니다.

1. Pattern Analyzer — 과거 트레이스에서 반복 제어 흐름과 암묵적 데이터 흐름을 마이닝하고, 현재 세션 상태에서 구체적인 미래 툴 호출을 만들어냅니다.
2. Tool Speculation Scheduler — 예측 실행을 승인하고, 확정될 때까지 결과를 격리하며, 정식(authoritative) 호출의 우선순위를 보장합니다.
3. LLM–Tool Co-Scheduler — 툴이 끝난 세션이 LLM 엔진으로 몰려 들어갈 때 진입 속도를 조절해 GPU 과부하를 막습니다.

세 번째가 재미있는 부분입니다. 툴을 아무리 빨리 끝내도, 돌아온 세션들이 한꺼번에 LLM에 몰리면 GPU가 병목이 되어 이득이 사라집니다.

논문은 이걸 실험으로 확인했습니다. 툴 실행만 2배 빠르게 하고 LLM 스케줄러를 그대로 두자, 고부하에서는 툴 쪽 이득이 LLM 감속에 흡수되었고 <span style="background-color: #fff59d"><strong>최악의 경우 베이스라인보다 느려졌습니다</strong></span>.

![Figure 5. Load sensitivity](/images/2026-08-25-paste-speculative-tool-execution/fig-5-p4.png)

<span style="background-color: #fff59d"><strong>동시 세션 1개에서 192개로 늘릴 때 LLM 생성 시간은 17배 이상 늘어나는데 툴 실행 시간은 거의 변하지 않습니다</strong></span>. 그래서 양쪽을 같이 스케줄해야 한다는 게 이 논문의 주장입니다.

## 안전성: 예측이 틀려도 상태를 오염시키지 않는다

![Figure 8. Lossless speculative tool execution](/images/2026-08-25-paste-speculative-tool-execution/fig-8-p7.png)

예측 실행 결과는 격리됩니다. LLM이 실제로 같은 호출을 내보낼 때만 재사용되거나 승격되고, 틀리면 그냥 버려집니다.

예측은 정식 세션 상태에 아무것도 append 하지 않고, 부작용이 있는 툴은 정책과 샌드박싱으로 걸러집니다. <span style="background-color: #fff59d"><strong>틀린 예측이 있어도 외부 관찰 가능한 동작이 바뀌지 않는다</strong></span>는 게 논문의 안전성 주장입니다.

## 숫자 리뷰

| 항목 | 값 |
|---|---|
| 평균 태스크 완료 시간 | 최대 43.5% 감소 |
| p99 테일 지연 | 최대 55.4% 감소 |
| 툴 지연시간 | 1.8배 감소 |
| Top-1 예측 정확도 | 최대 27.8% |
| Top-3 recall | 43.9% |
| 전체 히트율 | 93.8% |
| 스케줄링 오버헤드 | 100ms 미만 |

Top-1 정확도 27.8%는 낮아 보이는데, 여러 후보를 동시에 걸어두면 되기 때문에 <span style="background-color: #fff59d"><strong>전체 히트율은 93.8%까지 올라갑니다</strong></span>. 히트만 하나 하면 노출된 툴 대기 시간이 그만큼 사라지는 구조라, 불완전한 예측으로도 이득이 남습니다.

<span style="background-color: #fff59d"><strong>요청의 97%가 1배 이상 빨라졌고 최악의 경우에도 베이스라인과 비슷한 수준</strong></span>이라, 예측이 빗나갔을 때의 손해가 작습니다.

동시성이 늘어나는 스케일 테스트에서도 PASTE는 vLLM 대비 최소 1.27배, Agentix 대비 1.24배 속도를 유지했습니다. 비교 대상은 vLLM, Agentix, ORION, SpecFaaS입니다.

## 내 해석

근데 이 논문의 예측 부분이 특별히 똑똑한 건 아닙니다. 패턴 매칭에 가깝고 Top-1 정확도도 27.8%밖에 안 됩니다. 그럼에도 이득이 나는 이유는 시스템 설계입니다.

<span style="background-color: #fff59d"><strong>예측이 틀려도 잃을 게 없는 lossless 구조를 만들고, 히트율을 후보 수로 보완하고, 툴 쪽 이득이 GPU 쪽에서 새어나가지 않게 상호 스케줄링한 설계가 43.5%라는 숫자를 만든 겁니다</strong></span>.

에이전트 하네스를 만드는 입장에서 챙길 점 두 가지:

- <span style="background-color: #fff59d"><strong>에이전트 트레이스의 반복 패턴은 메모리·압축 소스이기도 하고 지연시간 최적화의 소스이기도 하다</strong></span>
- <span style="background-color: #fff59d"><strong>툴 병렬화를 넣을 때는 LLM 쪽 재진입 스케줄링을 같이 설계해야 한다. 한쪽만 고치면 고부하에서 이득이 사라진다</strong></span>

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
