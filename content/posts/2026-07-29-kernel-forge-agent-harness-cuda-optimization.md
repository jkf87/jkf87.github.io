---
title: "에이전트가 짠 CUDA 커널, 가장 빨라도 소용없는 이유 — Kernel Forge가 보여준 것"
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
description: "Kernel Forge 분석. 실제 모델 실행을 캡처해 LLM이 CUDA 커널을 생성·검증·교체하는 하네스. 지역 속도 2.83배와 실제 배포 영향이 다르다는 통찰과, 가드드 디스패치의 실무 교훈."
---

LLM이 생성한 CUDA 커널이 PyTorch eager보다 최대 2.83배 빨라질 수 있다는 [연구](https://arxiv.org/abs/2607.24762)가 나옴. PyTorch eager는 연산을 그래프 컴파일 없이 하나씩 즉시 실행하는 기본 모드임. Michigan 대학의 Kernel Forge는 MCTS 기반 하네스로, MCTS는 몬테카를로 트리 탐색을 뜻하는데 선택지를 트리로 펼치고 시뮬레이션 결과를 반영해 유망한 경로를 집중 탐색하는 기법임. 수정하지 않은 PyTorch 모델에서 실제 실행되는 연산자를 자동 캡처해서 LLM이 만든 특화 커널로 교체함. 근데 이 논문의 진짜 가치는 커널 속도가 아니라 **"가장 빨라진 커널이 가장 영향력 있는 커널은 아니었다"**는 발견임. GPU 최적화를 안 하더라도 에이전트 시스템의 우선순위 설계에 적용되는 교훈이라 정리함.

1. 배경. 기존 LLM 기반 커널 최적화 도구(AutoComp, GEAK, CudaForge)는 네 가지 한계가 있었음. 랜덤 텐서로 테스트한 분리된 벤치마크에서만 평가했다는 것, 최적화된 코드를 스탠드얼론으로 뽑아줘서 개발자가 수동으로 다시 끼워야 한다는 것, LLM 워크로드만 봤다는 것, 선형 정제나 빔 서치로 탐색해서 초기 선택에 묶인다는 것. 랜덤 텐서로 빨랐던 커널이 실제 모델에서 같은 성능이 안 나오는 건 shape, 활성화 분포, 인접 연산자, 메모리 동작이 전부 다르기 때문.

2. Kernel Forge의 접근은 두 단계임. 첫 단계, Model Ingestion. 수정하지 않은 PyTorch 모델을 실제로 돌리면서 연산자 호출을 캡처하고 shape, dtype, stride, 인자, 참조 출력, 호출 횟수, eager 지연 시간을 기록함. 같은 연산자라도 shape이나 인자가 다르면 별도 variant로 그룹화해서 operator card를 만듦. `conv2d` 하나가 ResNet-50에서와 Stable Diffusion에서는 전혀 다른 최적화 대상이 되니까, 연산자 이름이 아니라 실제 실행 컨텍스트를 잡는 것. 두 번째 단계, Forge. LLM이 operator card를 보고 CUDA 후보를 생성하고, eager 출력과 수치 일치를 검증하고, 실제 워크로드로 벤치마크하고, MCTS로 여러 최적화 경로를 병행 탐색함.

![Kernel Forge 시스템 개요](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-2-p4.png)

3. 이 "실제 실행을 캡처해서 타겟을 만든다"는 설계는 그대로 내 자동화에 이식됨. 에이전트로 뭔가를 최적화할 때 감으로 대상을 고르지 말고, 실제 프로덕션 로그에서 호출·실행 컨텍스트를 캡처해서 우선순위를 매기는 것. 그리고 같은 기능이라도 호출 맥락이 다르면 다른 케이스로 분리해서 관리하는 것. 벤치마크용 가상 데이터가 아니라 실제 워크로드로 검증해야 한다는 원칙임.

4. 결과가 재밌음. DGX Spark에서 네 모델을 돌려서 ResNet-50의 adaptive_avgpool2d 1.52배, Stable Diffusion의 group_norm 1.70배, Gemma 4 E2B의 softmax 2.83배, Qwen 3.5의 softmax 1.54배를 달성함. 근데 Gemma의 softmax는 전체 연산자 런타임의 5.93%만 차지하고, 90.13%를 차지하는 linear는 0.246배, 즉 커스텀 커널이 더 느려서 쓸 수 없었음. Stable Diffusion도 group_norm을 1.70배로 만들어봤자 group_norm + layer_norm + SiLU 합쳐 10.48%이고, linear와 SDPA가 80% 이상을 차지하는데, SDPA는 스케일드 닷-프로덕트 어텐션 연산을 뜻하며 여기는 여전히 eager가 빠름.

![Gemma 4 E2B 결과 — softmax 2.83배지만 런타임 5.93%](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-5-p8.png)

5. 이게 이 논문의 핵심 통찰임. 지역적 속도 향상과 실제 배포 영향은 다름. 그리고 패턴도 일관됨. 오픈소스/네이티브 PyTorch 연산자에서는 LLM 생성 CUDA가 24개 중 13개에서 eager를 이기는데, cuDNN·cuBLAS 같은 벤더 백엔드 연산자에서는 9개 중 1개만 이김. 성숙한 라이브러리가 지배하는 영역에서 LLM이 경쟁하기는 아직 어려움. 이건 GPU만의 이야기가 아님. 내 업무 자동화에서도 "에이전트가 개선할 수 있는 영역"과 "이미 잘 짜인 시스템이 지배하는 영역"을 구분해야 예산이 새지 않는다는 것과 같은 구조임.

6. 그래서 이 논문이 준 엔지니어링 답이 가드드 디스패치임. 생성된 커널이 실측에서 유효하고 빠를 때만 실행하고, 아니면 자동으로 eager로 폴백함. 덕분에 LLM이 만든 게 느려도 성능 저하가 발생하지 않음. 이 패턴은 모든 에이전트 생성물에 적용할 수 있음. 에이전트가 짠 코드, 프롬프트, 워크플로우를 "생성 즉시 교체"가 아니라 "측정해서 기존보다 나을 때만 교체"하는 게이트를 두는 것. 회귀 없는 개선의 기본형임.

7. 비용 분석도 뼈아픔. 50회 반복(opt50)에서 API 비용이 급증하는데, 추가 비용의 상당수가 런타임 비중이 낮은 연산자에 소모됨. 논문은 런타임 비중과 베이스라인 강도에 따라 예산을 동적 할당하는 정책이 필요하다고 마무리함. 이건 에이전트 최적화 작업 전반의 교훈임. 비중이 크고 베이스라인이 약한 곳에 탐색 예산을 몰아주는 것. 반복 횟수를 균등하게 나누는 건 비용 낭비의 처방임.

![ResNet-50 결과 — 벤더 백엔드 conv2d는 개선 어려움](/images/2026-07-29-kernel-forge-agent-harness-cuda-optimization/fig-3-p7.png)

8. 요약하면 Kernel Forge는 4가지 과제를 전부 해결한 시스템임. 실제 모델 실행 캡처, 모델 실행 경로에 자동 삽입, 비전·디퓨전·LLM 전 도메인 지원, MCTS 다경로 탐색에 GUI까지. 한계도 명확함. 핵심 고비중 연산자는 벤더 백엔드가 지배해서 당분간 안 뚫리고, 반복당 비용 효율이 떨어지는 구간이 있음.

9. 내가 가져갈 것 세 개. 첫째, 최적화 대상은 실제 실행 로그에서 비중 기반으로 선정할 것. 둘째, 에이전트 생성물 교체엔 실측 게이트와 폴백을 붙일 것. 셋째, 탐색 예산은 대상별 비중과 난이도에 따라 동적으로 배분할 것. 화려한 배수와 실제 이득은 다르다는 게 이 논문이 남긴 한 줄임.

에이전트 하네스와 자동화 루프 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』와 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 강의를 참고.

> 📄 **논문**: [arXiv:2607.24762](https://arxiv.org/abs/2607.24762) · 💻 **코드**: [github.com/TheJoshBrod/KernelForge](https://github.com/TheJoshBrod/KernelForge)
