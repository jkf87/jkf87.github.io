---
title: "SpatialCLI: VLM이 공간 도구를 배우고, 그 다음 도구 없이도 추론하게 만드는 법"
date: 2026-08-02
tags:
  - agent
  - VLM
  - tool-use
  - RL
  - internalization
  - spatial-reasoning
  - harness
  - automation
  - GRPO
  - embodied-AI
draft: false
---

**8B 모델이 도구를 쓸 때 GPT-5.6을 넘고, 도구를 뺏어도 73.8%를 유지한다.** SpatialCLI는 VLM(시각-언어 모델)이 전문 비전 도구(SAM 3, Depth Anything 3 등)를 에이전트처럼 호출하고, 그 사용 경험을 자기 것으로 만드는 3단계 프레임워크다. 핵심 질문은 단순하다: "도구를 쓰는 능력을 모델 안으로 밀어넣을 수 있는가?"

![SpatialCLI 개념도: 일반 VLM과 SpatialCLI Tools의 비교](/images/2026-08-02-spatialcli-spatial-tool-internalization/fig-1-p2.png)
*그림 1. SpatialCLI Tools 유무에 따른 VLM 추론 경로. 도구가 있으면 segmentation → depth → localization을 순차적으로 호출하며 정답에 도달한다.*

---

## 문제의 핵심: VLM은 추론은 하되 "눈"이 나쁘다

현재 VLM은 "저 이미지에서 가장 먼 곰인형을 찾아라"라는 지시를 이해할 수 있다. 하지만 실제로 정답을 내려면 세 가지 세밀한 지각 능력이 필요하다: (1) 곰인형들을 segmentation으로 식별하고, (2) 각각의 depth를 측정하고, (3) 가장 먼 것을 localization한다.

**일반 VLM은 이 세 단계 중 정확히 0개를 신뢰할 수 있게 수행한다.** 반면 SAM 3 같은 전문 모델은 segmentation은 완벽하지만 "어떤 것을 세그먼트해야 하는가"를 스스로 결정하지 못한다. 이것이 SpatialCLI가 출발하는 능력의 비대칭이다.

---

## Call–Learn–Internalize: 3단계 파이프라인

![SpatialCLI 전체 파이프라인](/images/2026-08-02-spatialcli-spatial-tool-internalization/fig-2-p3.png)
*그림 2. SpatialCLI의 Call → Learn → Internalize 3단계. 각 단계는 전문가 능력을 도구 → 학습 가능한 정책 → 모델 내재 능력으로 변환한다.*

### 1단계: Call — 도구를 에이전트 루프에 노출

SpatialCLI는 네 가지 공간 도구를 VLM에 노출한다:

- **Locate**: 객체의 바운딩 박스 반환 (Grounding DINO, Locate Anything)
- **Segment**: 객체의 폴리곤 경계 반환 (SAM 3)
- **Depth**: 메트릭 깊이 반환 (Depth Anything 3)
- **Pose**: 객체 방향 또는 카메라 모션 반환 (Orient Anything V2, VGGT)

VLM은 ReAct 스타일로推論한 뒤 도구를 호출하고, 결과를 받아 다시推論한다. 남은 도구 호출 예산이 매 턴마다 노출되어 모델이 "추가 도구를 쓸지, 답을 낼지"를 스스로 결정한다. 이 단계만으로 Qwen3-VL-8B의 SpatialCLI-Bench 점수는 35.3%에서 66.5%로 뛴다.

### 2단계: Learn — 에이전트 RL로 도구 사용 정책 학습

Call 단계만으로는 모델이 "언제 어떤 도구를 어떤 인자로 호출할지"를 신뢰성 있게 결정하지 못한다. SpatialCLI는 두 단계로 이를 해결한다.

**Cold-Start SFT**: Qwen3.5-397B-A17B를 교사 모델로 사용해 5,000개 태스크에서 도구 호출 궤적을 수집하고, 약 40%(2,000개)를 필터링하여 SFT 데이터로 사용한다.

**Agentic RL**: GRPO(DAPO 변형)를 사용해 도구 호출 정책을 강화학습한다. 각 태스크에서 그룹 샘플링 → 보상 → 업데이트를 반복하며, 최종 보상은 최종 답안의 정확도로 결정된다.

![RL 훈련 다이나믹스](/images/2026-08-02-spatialcli-spatial-tool-internalization/fig-3-p7.png)
*그림 3. RL 훈련 다이나믹스. SFT → RL 파이프라인이 SFT 없이 RL만 하는 것보다 안정적이며, 도구 호출 수도 2.56회로 안정적으로 유지된다.*

핵심 발견: **SFT 없이 RL만 하면 도구 호출 수가 3.36 → 6.74로 폭주**하지만, SFT를 먼저 하면 2.56회로 안정적이다. 그리고 RL 없이 도구만 쓰는 모델은 w/o Tools 성능이 100 스텝 이후 하락하기 시작한다 — 도구 의존성이 모델의 고유 능력을 잠식하는 것이다.

### 3단계: Internalize — 궤적을 증류하여 도구 능력을 모델 안으로

이것이 SpatialCLI의 가장 혁신적인 부분이다. 2단계에서 수집된 **성공적인 도구 호출 궤적**을 텍스트推論 체인으로 "번역"하여, 모델이 도구 없이도 같은推論을 하도록 훈련한다.

**Progressive Evidence-Grounded Trajectory Verbalization**: 전체 궤적을 한 번에 번역하지 않고, 각 도구 호출 턴마다 증거를 정리한 뒤 전역적으로 통합한다. 이는 긴 컨텍스트에서 정보가 묻히는 것을 방지한다.

**Dual-View Capability Internalization**: 두 가지 뷰를 동시에 훈련한다:
- **Capability-Internalization View**: 도구 없이 직접 답하는 프롬프트 + 번역된推論 체인
- **Tool-Use View**: 원래 도구 호출 궤적 (도구 출력은 loss에서 마스킹)

이 dual-view 설계 덕분에 모델은 도구를 쓸 줄도 알면서, 도구 없이도推論할 수 있다.

---

## 결과: 8B가 GPT-5.6을 넘는 순간

![전체 성능 비교](/images/2026-08-02-spatialcli-spatial-tool-internalization/table-1-p7.png)
*표 1. SpatialCLI-Bench 및 공간 추론 벤치마크 전체 결과. model-name 행은 w/o Tools, ++ 행은 w/ Tools.*

SpatialCLI-8B(Qwen3-VL-8B 기반)의 성능:
- **w/ Tools**: SpatialCLI-Bench 91.3% (GPT-5.6 Sol 48.8%의 거의 2배)
- **w/o Tools**: 72.7% (도구 없이도 원래 35.3%에서 37.4점 향상)
- MindCube에서 29.3% → 84.6% (w/ Tools), 73.8% (w/o Tools)

GPT-5.6 Sol에 SpatialCLI Tools를 붙여도 54.9%까지만 향상된다. 8B 모델 + 학습된 도구 정책이 50배 이상 큰 모델 + 도구를 넘는다.

---

## 내재화의 스케일링: 도구 성능은 포화하지만, 내재화는 계속 오른다

![내재화 스케일링 분석](/images/2026-08-02-spatialcli-spatial-tool-internalization/fig-4-p7.png)
*그림 4. (a) 내재화 데이터가 늘어날수록 w/o Tools 점수 상승. (c) 모델 용량이 클수록 CII(Capability Internalization Index) 상승. (d) w/ Tools는 모델 크기에 무관하게 포화하지만, w/o Tools는 계속 스케일한다.*

가장 중요한 발견 중 하나: **w/ Tools 성능은 모델 크기와 무관하게 거의 같다** (8B, 35B-A3B, 27B 모두 ±1점 차이). 도구 호출 정책은 한 번 학습되면 전문가 모델이 나머지를 처리하기 때문이다.

반면 **w/o Tools 성능은 모델 용량에 따라 계속 오른다**. 내재화는 모델이 전문가의 능력을 자기 파라미터에 인코딩하는 과정이므로, 더 큰 모델일수록 더 많이 흡수한다. 이는 "도구 성공 = 문제 해결"이 아니라 "도구 성공 = 학습 기회"라는 패러다임 전환을 시사한다.

---

## 왜 구조화된 도구 반환인가

SpatialCLI는 도구 출력을 이미지(annotation overlay)가 아닌 **구조화된 텍스트**(좌표, 폴리곤, depth 값)로 반환한다. 실험 결과:

| 반환 형식 | SpatialCLI-Bench | BOPASK |
|---|---|---|
| Visual Only | 45.9 | 18.3 |
| Structured + Visual | 66.0 | 20.1 |
| **Structured Only** | **66.5** | **20.6** |

구조화된 출력이 시각적 출력보다 낫다. 이유는 두 가지: (1) VLM이 텍스트 좌표를 직접推論에 활용하기 더 쉽고, (2) 텍스트는 후속 내재화 단계에서 그대로 감독 신호로 변환된다. 이미지 annotation은 내재화하기 어렵다.

---

## 절제 실험: 무엇이 필수적인가

| 변형 | w/o Tools | w/ Tools |
|---|---|---|
| Final Answer Only | 52.7 | 52.1 |
| CoT + Answer | 45.0 | 42.2 |
| Internalization View Only | 71.1 | 62.6 |
| Tool-Use View Only | 42.2 | 89.0 |
| One-Pass Dual-View | 64.5 | 90.2 |
| **Full Dual-View (제안)** | **72.7** | **91.3** |

- Final Answer Only는 간결하지만 도구 능력을 잃는다 (52.1)
- Internalization View Only는 w/o Tools는 강하지만 도구를 잃는다 (62.6)
- Tool-Use View Only는 도구는 강하지만 내재화가 안 된다 (42.2)
- **Full Dual-View만이 두 능력을 동시에 유지**한다 (72.7 / 91.3)

Progressive verbalization도 필수적이다: One-Pass(64.5) vs Full(72.7) = 8.2점 차이. 긴 궤적을 한 번에 처리하면 정보 손실이 발생한다.

---

## SpatialCLI-Bench: 왜 기존 벤치마크가 부족했는가

SpatialCLI는 516개 예제의 **조합적 공간 지각 벤치마크**를 새로 구축했다. 기존 벤치마크들이 localization, depth, pose 등 단일 능력만 측정했다면, SpatialCLI-Bench는 여러 능력의 **조합**을 요구한다.

"가장 먼 곰인형 찾기" = segmentation + depth + localization의 조합이다. GPT-5.6 Sol이 이 벤치마크에서 48.8%에 그치는 것은, 개별 능력이 아니라 **능력 간 조정(orchestration)**이 진짜 병목임을 보여준다.

---

## 의의: 에이전트 도구 사용의 새로운 패러다임

SpatialCLI는 에이전트 도구 사용 연구에 세 가지 중요한 시사점을 던진다.

**1. 도구 사용은 학습 데이터다.** 대부분의 에이전트 시스템은 도구를 런타임 보조 수단으로만 본다. SpatialCLI는 도구 호출 궤적을 **내재화의 원천**으로 활용한다. 도구를 쓴 경험이 모델의 파라미터에 축적되는 것이다.

**2. 구조화된 반환은 내재화의 전제 조건이다.** 도구가 이미지 annotation을 반환하면 VLM이 사용하기도 어렵지만, 더 중요한 것은 그것을 텍스트 감독 신호로 변환할 수 없다는 점이다. 도구 인터페이스 설계는 런타임 성능뿐 아니라 학습 파이프라인 전체에 영향을 미친다.

**3. 도구 성능 포화 ≠ 내재화 포화.** 더 큰 모델은 도구를 쓸 때 더 나은 성능을 내지 않지만, 도구 없이는 확실히 더 낫다. 이는 모델 스케일링의 의미를 바꾼다: 큰 모델의 이점은 도구 성공률이 아니라 흡수 용량(absorption capacity)에 있다.

---

## 더 실습해보고 싶은 분들께

SpatialCLI처럼 에이전트가 도구를 호출하고 그 경험을 학습하는 루프를 직접 만들어보고 싶다면, 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 도구 사용 루프를 실전에서 설계하는 50가지 패턴
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 RL과 도구 호출 정책을 처음부터 끝까지 직접 구축해보는 실습 강의

---

> 📄 **논문**: [SpatialCLI: Learning to Reason With Spatial Tools, Then Without Them](https://arxiv.org/abs/2607.27703) (2026.07.31)
