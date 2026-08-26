---
title: "GLM-5.3-Flash: 320B 모델을 18B 활성 파라미터로 쓰는 법"
date: 2026-08-27
tags:
  - LLM
  - GLM
  - agent
  - multimodal
  - coding-agent
  - inference
  - long-context
  - open-weight
draft: false
description: "Z.ai가 공개한 GLM-5.3-Flash를 정리했습니다. 320B 총 파라미터, 18B 활성 파라미터, 1M context, sparse+linear attention, 시각 코딩 루프, 중국산 AI 칩 서빙까지 핵심을 봅니다."
---

## GLM-5.3-Flash 요약

Z.ai가 2026년 8월 26일 `GLM-5.3-Flash`를 공개했습니다. 핵심은 단순합니다. <span style="background-color: #fff59d"><strong>320B 총 파라미터 모델인데, 한 번에 활성화되는 파라미터는 18B</strong></span>입니다.

GLM-5 계열에서 처음으로 native multimodal을 붙였고, coding·agentic benchmark에서는 GLM-5.2를 꽤 크게 앞선다고 발표했습니다.

숫자만 보면 이 모델은 “기본값으로 쓰기 좋은 비용 구조”에 초점이 있습니다. Z.ai는 Artificial Analysis Intelligence Index v4.1.1 기준 점수 57, task당 할인 비용 0.045달러라고 설명합니다. 원문 표현으로는 기존에 약 10배 비싼 비용에서나 가능했던 지능 수준이라는 주장입니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/03-artificial-analysis-pareto.png)
*Artificial Analysis 기준 GLM-5.3-Flash의 비용-성능 위치. 핵심은 비슷한 지능 구간의 task cost를 크게 낮췄다는 점이 포인트입니다. 출처: Z.ai blog.*

## 공개 전 테스트: ox-alpha

흥미로운 대목은 출시 전 테스트 방식입니다. Z.ai는 GLM-5.3-Flash를 `ox-alpha`라는 익명 모델로 OpenCode와 OpenRouter에 먼저 올렸고, 사용자 피드백을 받았다고 밝힙니다. 원문에 따르면 해당 주간 가장 인기 있는 모델이 됐고, 이 트래픽은 중국산 AI 칩에서 서빙됐습니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/01-opencode-openrouter-ox-alpha.png)
*출시 전 `ox-alpha`라는 이름으로 OpenCode·OpenRouter에서 테스트했다는 설명. 새 모델을 논문 발표보다 실제 코딩 트래픽으로 먼저 검증한 셈입니다. 출처: Z.ai blog.*

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/02-weekly-popularity.png)
*익명 테스트 기간의 사용량/인기 지표. 이런 공개 전 실사용 테스트는 요즘 코딩 모델 출시에서 점점 중요해지고 있습니다. 출처: Z.ai blog.*

이 지점이 꽤 중요합니다. 요즘 코딩 모델은 MMLU 몇 점보다, 실제 harness 안에서 얼마나 버티는지가 더 빨리 드러납니다.

Claude Code, OpenCode, SWE harness, browser use, computer use 같은 환경에서 모델은 작업자에 더 가깝습니다. 그래서 GLM-5.3-Flash의 메시지도 “시각 피드백까지 받는 코딩·업무 에이전트”에 맞춰져 있습니다.

## GLM-5.2보다 코딩·에이전트 점수가 크게 올랐습니다

Z.ai가 제시한 대표 비교는 여섯 개 coding/agentic benchmark입니다. DeepSWE v1.1은 GLM-5.2 46.2에서 GLM-5.3-Flash 63.4로 올랐고, AutomationBench v1.0.6은 26.2에서 48.8로 올랐습니다. Toolathlon Verified도 59.9에서 78.4입니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/04-coding-agentic-benchmarks.png)
*Coding·agentic benchmark 비교. GLM-5.3-Flash는 GLM-5.2 대비 DeepSWE와 AutomationBench에서 차이가 크게 납니다. 단, 이 값들은 Z.ai가 공개한 평가 조건과 주석을 같이 봐야 합니다. 출처: Z.ai blog.*

Z.ai Code Bench v1.0도 같이 공개됐습니다. Claude Code 2.1.207에서 돌린 내부 코딩 평가라고 설명되어 있고, max effort에서는 GLM-5.3-Flash 29.0, Claude Opus 4.8 29.5로 거의 붙었다고 합니다. 여기서도 중요한 건 effort level입니다. 같은 모델도 reasoning budget을 얼마나 주느냐에 따라 체감이 크게 갈립니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/05-zai-code-bench-effort.png)
*Z.ai Code Bench v1.0 결과. Effort level을 올릴수록 GLM-5.3-Flash가 GLM-5.2와 벌어지고, max effort에서는 Opus 4.8에 근접한다고 주장합니다. 출처: Z.ai blog.*

요약하면 이렇습니다.

| Benchmark | GLM-5.3-Flash | GLM-5.2 | 원문상 포인트 |
|---|---:|---:|---|
| Terminal Bench 2.1 | 84.3 | 81.0 | 이미 높은 영역에서 소폭 개선 |
| DeepSWE v1.1 | 63.4 | 46.2 | SWE류 작업에서 큰 상승 |
| Toolathlon Verified | 78.4 | 59.9 | 도구 사용 검증 태스크 개선 |
| AutomationBench v1.0.6 | 48.8 | 26.2 | 자동화 워크플로우에서 큰 상승 |
| Agents' Last Exam | 26.3 | 20.4 | 에이전트 종합 시험 소폭 개선 |
| GDPval-AA v2 | 1773 | 1504 | 업무형 평가에서도 상승 |

## 구조: 320B 총량에 18B 활성 파라미터

GLM-5.3-Flash의 설계 포인트는 효율입니다. GLM-4.5 계열과 비교하면 총 파라미터는 320B 대 355B로 비슷합니다.

반면 활성 파라미터는 18B 대 32B, 레이어 수는 45 대 92로 줄었습니다. 즉 모델 전체 용량은 크게 유지하면서, 추론 시 실제로 쓰는 계산량을 낮추는 방향입니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/06-glm-53-flash-architecture.png)
*GLM-5.3-Flash 구조 요약. 45 layers, 18B activated parameters, sparse+linear attention 조합이 핵심입니다. 출처: Z.ai blog.*

긴 컨텍스트 비용을 줄이기 위해 sparse attention과 linear attention을 섞었습니다. linear attention은 local dependency를 state modeling으로 처리하고, sparse attention은 lightweight indexer로 관련 global context를 찾습니다. 여기에 1M token context에서 indexer의 latency와 memory overhead를 줄이기 위해 `IndexPool`을 넣었습니다. 네 개의 indexer key vector를 weighted pooling으로 하나로 압축하는 방식입니다.

Z.ai 문서 기준으로 GLM-5.3 대비 attention compute는 3.01배, KV cache size는 4.44배 줄었다고 합니다. 이 수치는 모델 공개 글과 API 문서가 같은 방향으로 말하고 있습니다.

다만 원문도 인정하듯 KV cache는 Kimi-K3와 DeepSeek-V4-Flash보다 아직 약간 큽니다. 완전히 끝난 설계라기보다, 비용을 크게 낮춘 첫 버전에 가깝습니다.

| 항목 | GLM-4.5-Base | GLM-5-Base | DeepSeek-V4-Flash-Base | GLM-5.3-Flash-Base |
|---|---:|---:|---:|---:|
| Activated Params | 32B | 40B | 13B | 18B |
| Total Params | 355B | 744B | 284B | 320B |
| MMLU | 86.1 | 88.3 | 88.5 | 88.1 |
| BBH | 86.2 | 87.4 | 84.9 | 86.6 |
| LiveCodeBench-Base | 28.1 | 34.4 | 29.9 | 37.6 |
| SimpleQA | 30.0 | 36.0 | 31.2 | 33.5 |

Base model 표를 보면 GLM-5.3-Flash-Base는 MMLU 같은 일반 지식 점수에서 GLM-5-Base를 압도하진 않습니다. 대신 LiveCodeBench-Base에서는 37.6으로 가장 높습니다. 이번 모델의 방향이 어디에 맞춰져 있는지 꽤 분명합니다. 코딩과 에이전트 실행입니다.

## 멀티모달은 이미지를 받고, 화면을 보며 고치는 모델입니다

GLM-5.3-Flash에서 제일 실무적인 부분은 visual coding입니다. Z.ai는 frontend, game development, 3D simulation 같은 작업에서는 최종 산출물이 interface, interaction, world라고 말합니다. 실패는 렌더링 화면, 클릭 흐름, 플레이테스트에서 드러납니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/07-visual-self-verification-before-after.jpg)
*Visual self-verification 예시. 처음에는 레이아웃 문제가 있고, 모델이 화면을 보고 다시 고치는 흐름을 보여줍니다. 출처: Z.ai blog.*

이건 꽤 맞는 이야기입니다. 코딩 에이전트가 브라우저 screenshot을 보고, 다시 CSS를 고치는 루프는 이미 실무에서 많이 씁니다. 모델이 이미지를 “설명”하는 수준에 머물면 루프가 약합니다. 필요한 건 <span style="background-color: #fff59d"><strong>자기 산출물을 보고, 의도와 다른 부분을 판단하고, 다음 액션을 고르는 능력</strong></span>입니다.

Z.ai는 이 능력을 만들기 위해 visual coding data synthesis pipeline을 만들었고, self-visual judgment와 test-time improvement에 초점을 뒀다고 설명합니다. frontend coding에서는 environment feedback 기반 reinforcement learning과, 실제 user flow에 기반한 agent verification도 탐색했다고 합니다. 기능 테스트를 넘어서 rendered product의 품질까지 평가하려는 방향입니다.

## 업무 에이전트는 문서·표·PPT 화면까지 읽어야 합니다

Z.ai가 GLM-5.3-Flash를 코딩 모델로만 포장하지 않는 이유도 여기 있습니다. 실제 업무는 텍스트만으로 처리되지 않습니다. 문서, 스프레드시트, 프레젠테이션, 대시보드, 회의 자료, 브라우저 화면이 섞여 있습니다. 사용자가 이걸 매번 텍스트로 풀어 설명해야 하면, 에이전트의 효율은 크게 떨어집니다.

![](/images/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27/08-professional-workflow-example.jpg)
*전문 업무 워크플로우 예시. 문서·표·프레젠테이션 같은 구조화된 시각 자료를 읽고 산출물을 점검하는 방향을 보여줍니다. 출처: Z.ai blog.*

API 문서도 같은 메시지입니다. GLM-5.3-Flash는 1M-token context를 지원하고, `messages[].content[]`에 `type: image_url` content block을 여러 개 넣는 방식으로 이미지를 받을 수 있습니다. 권장 설정은 `temperature: 1`, `top_p: 0.95`, `reasoning_effort: max`입니다. streaming에서는 `stream: true`와 `tool_stream: true`를 함께 켜는 것을 권장합니다.

로컬 배포 경로도 공개했습니다. Hugging Face 모델 카드 기준 지원 프레임워크는 SGLang, vLLM, TokenSpeed, KTransformers입니다. 원문 블로그에는 SGLang, vLLM, TokenSpeed가 언급되어 있고, Hugging Face 쪽에는 KTransformers 튜토리얼도 붙어 있습니다.

## 중국산 AI 칩에서 대규모 서빙까지 테스트했습니다

마지막 섹션은 모델보다 인프라 이야기입니다. Z.ai는 지난 한 주 동안 GLM-5.3-Flash를 대규모 중국산 AI 칩 클러스터에서 서빙했다고 밝힙니다.

고대역폭 interconnect와 해당 하드웨어에 최적화된 serving stack을 썼고, SGLang 위에 dedicated inference engine을 만들었다고 합니다.

여기서 재밌는 문장이 나옵니다. GLM-5.3 기반 infrastructure agent가 kernel 최적화, bottleneck 진단, serving stack 개선을 도왔다는 겁니다. 즉 <span style="background-color: #fff59d"><strong>모델이 자기 자신을 서빙하는 시스템을 최적화하는 피드백 루프</strong></span>가 생겼다는 설명입니다.

기술적으로는 memory capacity와 bandwidth 제약을 다룹니다. 1M context를 지원하려면 메모리와 대역폭이 병목이 됩니다. Z.ai가 언급한 구성은 intra-node tensor parallelism, ReplaySSM, W8A8 quantization, hybrid INT8/FP8/BF16 cache quantization, Layer Split, 그리고 Encode-Prefill-Decode(EPD) disaggregated architecture입니다.

초기 baseline 대비 end-to-end serving performance를 3배 개선했고, per-token cost가 mainstream NVIDIA GPU와 비슷한 수준에 도달했다고 주장합니다. 이건 단순히 “중국 칩도 됩니다”가 아닙니다. <span style="background-color: #fff59d"><strong>모델 구조, 컨텍스트 정책, quantization, serving architecture를 같이 설계해야 flash cost가 나온다</strong></span>는 이야기입니다.

## 사용처: 긴 코딩 루프와 시각 검증

GLM-5.3-Flash는 “모든 벤치마크 1등 모델”로 읽으면 애매합니다. 표 안에는 GPT-5.6 Terra, Gemini 3.7 Flash, Opus 4.8 같은 강한 비교 대상이 있고, vision benchmark 일부에서는 GLM-5.3-Flash가 항상 최고는 아닙니다. BabyVision, MVBench, MMVU에서는 Gemini 3.7 Flash가 더 높게 제시됩니다.

대신 이 모델의 포지션은 선명합니다.

- 긴 컨텍스트를 많이 쓰는 코딩·에이전트 작업
- 브라우저/GUI를 보고 고치는 visual coding loop
- 비용 때문에 프론티어 모델을 자주 쓰기 어려운 자동화 워크플로우
- open-weight를 직접 서빙하거나 튜닝된 serving stack에 얹고 싶은 팀

특히 에이전트 하네스를 운영하는 입장에서는 “정답률”보다 “한 작업당 비용”이 더 무섭습니다. agentic workflow는 관찰, 계획, 도구 호출, 검증, 재시도까지 포함합니다. 여기서 10배 비용 차이는 제품 가능 여부를 가르는 숫자입니다.

GLM-5.3-Flash가 흥미로운 이유는 이 지점입니다. 모델 지능과 장기 운영 비용이 같은 설계 문제로 묶였습니다. 320B를 만들고 18B만 켜는 설계, sparse+linear attention, 1M context serving, visual self-verification, EPD serving까지 전부 같은 질문을 향합니다.

<mark>에이전트 시대의 기본 모델은 긴 루프를 끝까지 돌릴 수 있어야 합니다.</mark>

## 참고 링크

- [Z.ai blog: GLM-5.3-Flash](https://z.ai/blog/glm-5.3-flash)
- [Z.ai docs: GLM-5.3-Flash](https://docs.z.ai/guides/llm/glm-5.3-flash)
- [Hugging Face: zai-org/GLM-5.3-Flash](https://huggingface.co/zai-org/GLM-5.3-Flash)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
