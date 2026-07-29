---
title: "Kernel Forge: LLM 에이전트 하네스가 실제 PyTorch 모델의 CUDA 커널을 최적화하는 법"
date: 2026-07-29T16:00:00+09:00
tags:
  - agent
  - harness
  - LLM
  - CUDA
  - optimization
  - MCTS
  - PyTorch
  - automation
  - loop
  - tool-use
source_url: "https://arxiv.org/abs/2607.24762"
github_url: "https://github.com/TheJoshBrod/KernelForge"
---

**LLM이 생성한 CUDA 커널이 PyTorch eager 실행보다 최대 2.83× 빨라질 수 있다** — Michigan 대학 연구진이 개발한 Kernel Forge는 Monte Carlo Tree Search(MCTS) 기반 에이전트 하네스로, 수정하지 않은 PyTorch 모델에서 실제 실행되는 연산자(op)를 자동 캡처하고, LLM이 생성·검증·프로파일링한 특화 CUDA 커널로 교체한다.

기존 LLM 기반 커널 최적화 도구들이 분리된 벤치마크 커널에만 작동했다면, Kernel Forge는 **실제 모델 실행 컨텍스트**에서 작동한다는 점이 핵심 차이다.

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-1-p3.png)
*Kernel Forge GUI. 프로젝트 런처 → 모델 로드 → 연산자 워크벤치 → 결과 요약 → 커널 리비전 트리까지 전 과정을 시각화한다.*

## 문제: 벤치마크 커널 ≠ 실제 모델 커널

GPU 커널 최적화는 ML 모델의 지연 시간과 비용을 줄이는 가장 직접적인 방법이다. 전통적으로는 전문 엔지니어가 손으로 저수준 CUDA 코드를 작성했고, 최근에는 LLM 기반 에이전트 시스템(AutoComp, GEAK, CudaForge 등)이 등장했다.

하지만 기존 도구들은 4가지 근본적 한계가 있다:

1. **분리된 벤치마크에만 평가**: 랜덤 텐서로 테스트한 커널이 실제 모델 실행에서 같은 성능을 보장하지 않는다. 텐서 shape, 활성화 분포, 인접 연산자, 메모리 동작이 다르기 때문이다.
2. **통합 부재**: 최적화된 CUDA 코드를 스탠드얼론으로 출력해서 개발자가 수동으로 모델에 다시 끼워넣어야 한다.
3. **LLM 중심**: 대부분 LLM 워크로드만 타겟하고, 비전·디퓨전 모델은 다루지 않는다.
4. **탐색 빈약**: 선형 정제(linear refinement)나 빔 서치는 초기 선택에 강하게 의존해서, 일시적으로 느려 보이는 중간 후보를 버린다.

## 해결: End-to-End 에이전트 하네스

Kernel Forge는 2단계 파이프라인으로 동작한다.

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-2-p4.png)
*Kernel Forge 시스템 개요. Model Ingestion Pipeline이 실제 모델 실행에서 연산자를 캡처하고, Forge가 CUDA 후보를 생성·검증·벤치마크·최적화한다.*

### 1단계: Model Ingestion Pipeline

사용자가 **수정하지 않은 PyTorch 모델**과 가중치, 예제 입력을 제공하면:

- 모델을 실제로 실행하면서 `conv2d`, `matmul`, `group_norm`, `softmax` 등의 PyTorch 연산자 호출을 캡처
- 각 호출에서 shape, dtype, stride, 레이아웃, 인자, 출력 메타데이터, 참조 출력, 호출 횟수, eager 지연 시간을 기록
- 동일한 연산자라도 shape/dtype/인자가 다르면 **별도 variant**로 그룹화
- 결과물은 **operator card** — 구체적인 최적화 타겟

이 과정에서 핵심은 "연산자 이름"이 아니라 **실제 실행 컨텍스트**를 캡처한다는 것이다. `conv2d` 하나라도 ResNet-50에서와 Stable Diffusion에서는 완전히 다른 최적화 대상이 된다.

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-2-p4-2.png)
*variant는 구체적인 연산자 호출 케이스다. 같은 연산자라도 shape, dtype, 인자가 다르면 다른 variant가 된다.*

### 2단계: The Forge (최적화 루프)

operator card를 입력받아 MCTS(Monte Carlo Tree Search) 기반으로 CUDA 커널을 생성·개선한다:

1. **Kernel Generator Agent**: LLM(Claude Opus 4.7 사용)이 operator card의 메타데이터를 받아 CUDA 소스 + 런치 래퍼 생성
2. **검증**: PyTorch eager 출력과 수치적 일치 여부 확인
3. **벤치마크**: 실제 워크로드 입력으로 지연 시간 측정
4. **MCTS 탐색**: 선형 정제나 빔 서치 대신, 일시적으로 느려 보이는 경로도 버리지 않고 여러 최적화 경로를 병행 탐색
5. **가드드 디스패치(Guarded Dispatch)**: 최적화된 커널이 측정 결과에서 유효하고 빠를 때만 실행되고, 그렇지 않으면 PyTorch eager로 폴백

## 실험: 4개 모델, 50회 최적화 반복

NVIDIA DGX Spark(GB10 GPU)에서 4개 PyTorch 모델을 평가했다:

| 모델 | 도메인 | 주요 결과 |
|------|--------|-----------|
| ResNet-50 | 비전 | `adaptive_avgpool2d` 1.52× |
| Stable Diffusion 3.5 Medium | 디퓨전 | `group_norm` 1.70× |
| Gemma 4 E2B | LLM | `softmax` 2.83× |
| Qwen 3.5 35B-A3B | LLM | `softmax` 1.54× |

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-3-p7.png)
*ResNet-50 opt50 결과. conv2d가 53% 런타임을 차지하지만 벤더 백엔드라 개선이 어렵고, tensor add나 max pooling 같은 네이티브 op에서 개선이 두드러진다.*

### 핵심 발견: "가장 빠른 커널 ≠ 가장 영향력 있는 커널"

이 논문의 가장 중요한 통참은 **지역적 속도 향상과 실제 배포 영향의 괴리**다.

- **Gemma 4 E2B**: softmax에서 2.83× 달성. 하지만 softmax는 전체 연산자 영역의 **5.93%**만 차지. `linear`(90.13%)는 0.246×에 머문다.
- **Stable Diffusion 3.5 Medium**: group_norm에서 1.70× 달성. 하지만 group_norm + layer_norm + SiLU 합쳐도 **10.48%**. `linear`(53.40%)와 SDPA(27.12%)가 80% 이상을 차지하며 여전히 eager보다 느리다.

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-5-p8.png)
*Gemma 4 E2B opt50 결과. softmax 2.83× 달성이 눈에 띄지만, 전체 런타임의 90%를 차지하는 linear는 여전히 eager가 더 빠르다.*

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-4-p8.png)
*Stable Diffusion 3.5 Medium opt50 결과. group_norm 1.70×, SiLU 1.05× 등 소규모 op 개선이 있지만, linear와 SDPA가 대다수 런타임을 차지한다.*

이 패턴은 일관된다: **오픈소스/네이티브 PyTorch 연산자**에서는 LLM이 생성한 CUDA가 eager를 능가하는 경우가 많고 (24개 중 13개), **벤더 백엔드 연산자**(cuDNN, cuBLAS 등)에서는 성숙한 라이브러리 베이스라인을 넘기 어렵다 (9개 중 1개).

### 가드드 디스패치: 안전망

Kernel Forge의 가드드 디스패치는 이 문제를 **엔지니어링적으로 해결**한다. 생성된 커널이 측정 결과 더 빠를 때만 실행되고, 그렇지 않으면 PyTorch eager로 자동 폴백한다. 그래프에서 1.0× 미만의 막대 위에 표시된 반투명 캡이 바로 이 폴백 메커니즘이 회복하는 성능이다.

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-6-p8.png)
*Qwen 3.5 35B-A3B opt50 결과. softmax 1.54×, conv1d 1.29× 달성. grouped matmul(93.62%)은 여전히 eager가 우세.*

### 비용 분석: MCTS 반복당 API 비용

![](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-7-p8.png)
*최적화 단계별 Opus 4.7 API 증분 비용. opt50에서 비용이 급증하지만, 그 비용이 항상 런타임 비중이 높은 연산자 개선으로 이어지지는 않는다.*

비용 분석에서도 같은 패턴이 드러난다. opt50(50회 반복)에서 API 비용이 급증하지만, 추가 비용의 상당수가 런타임 비중이 낮은 연산자에 소모된다. 논문은 **런타임 비중과 베이스라인 강도에 따라 예산을 동적 할당**하는 정책이 필요함을 시사한다.

## 다른 시스템과의 비교

Kernel Forge는 기존 커널 최적화 시스템(Astra, GEAK, CudaForge, AutoComp 등)이 해결하지 못한 4가지 챌린지를 모두 충족한다:

| 챌린지 | 기존 도구 | Kernel Forge |
|--------|-----------|--------------|
| 분리된 벤치마크 입력 | 랜덤 텐서 사용 | 실제 모델 실행 캡처 |
| 통합 부재 | 스탠드얼론 코드 출력 | 모델 실행 경로에 자동 삽입 |
| LLM 중심 | LLM만 지원 | 비전·디퓨전·LLM 모두 지원 |
| 탐색 전략 | 선형 정제/빔 서치 | MCTS 기반 다경로 탐색 |
| 관측 가능성 | 스크립트/프로토타입 수준 | GUI + CLI 제공 |

## 의의와 한계

Kernel Forge는 "에이전트가 생성한 코드를 실제 모델 실행에 안전하게 통합한다"는 목표를 달성한 시스템이다. 가드드 디스패치라는 엔지니어링 장치를 통해, LLM이 생성한 커널이 기존 라이브러리보다 느린 경우 **자동으로 폴백**함으로써 성능 저하를 방지한다.

다만 한계도 명확하다:
- 가장 런타임 비중이 높은 핵심 연산자(`linear`, `conv2d`, `matmul`)는 대부분 벤더 백엔드(cuBLAS, cuDNN)에 의존하며, 이 영역에서 LLM 생성 CUDA가 경쟁하기는 여전히 어렵다.
- 50회 반복당 비용 효율성이 떨어지는 구간이 존재한다.
- 모델-하네스 스택별로 결과가 달라질 수 있다.

이러한 한계에도 불구하고, **에이전트 하네스가 실제 모델 실행 컨텍스트에서 작동하며 안전장치를 갖추었다**는 점은 에이전트 기반 시스템 최적화의 실용성을 보여주는 중요한 사례다.

> 📄 **논문**: [Kernel Forge: An Agent Harness for LLM-based Generation and Optimization of CUDA Kernels](https://arxiv.org/abs/2607.24762)
> 💻 **코드**: [github.com/TheJoshBrod/KernelForge](https://github.com/TheJoshBrod/KernelForge)

## 더 실습해보고 싶은 분들께

에이전트 하네스, 자동화 루프, 도구 사용 최적화에 관심이 있다면 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 실제로 구성하고 활용하는 50가지 사례
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 컨텍스트 엔지니어링의 실전 강의
