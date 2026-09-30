---
title: "LLM 학습 비용 계산부터 GPU 병렬화까지: ECE7115 강의노트 10편 한 흐름 정리"
date: 2026-09-30
author: 한준구(코난쌤)
description: "ECE7115 강의노트 10편을 비용 계산·아키텍처·스케일링 법칙·GPU 병렬화의 설계 흐름으로 재구성했습니다. LLaMA-1 GPU-시간 역산 MFU 43.4~51.4%, 파라미터당 16바이트 메모리 근사, 2026-09-30 1차 문헌 재검증 포함."
tags:
  - LLM
  - 아키텍처
  - GPU
  - 분산 학습
  - 강의노트
refactor_hub_id: llm-course-notes-01
aliases:
  - ece7115-0-course-introduction
  - ece7115-1-resource-accounting
  - ece7115-2-basics-transformer
  - ece7115-3-basics-llm
  - ece7115-4-modern-llm-architecture
  - ece7115-5-mixture-of-experts
  - ece7115-6-scaling-laws
  - ece7115-7-llm-case-study
  - ece7115-8-understanding-gpus
  - ece7115-9-parallelism
draft: false
sources_read: "ECE7115 슬라이드 원본 10종 PDF를 내려받아 텍스트 추출로 노트 주장과 대조(1강 MFU 8회, 4강 RMSNorm 10회·RoPE 44회, 6강 Kaplan 20회, 8강 FlashAttention 17회, 9강 ZeRO 38회 확인). 인용 수치는 1차 문헌 본문 8편(arXiv PDF)에서 직접 확인: 2302.13971(표2: 6.7~65.2B·1.0~1.4T 토큰, 표15: 82,432~1,022,362 GPU-시·A100-80GB, 65B 380토큰/초/GPU), 2307.09288(문맥 2048→4096, GQA 도입), 2310.06825(표1: 윈도우 4096·문맥 8192·kv헤드 8, 이론 범위 131K), 2401.04088(47B 저장·토큰당 13B 활성, 8중 2 라우팅, 32k, Apache 2.0), 2203.15556(70B/1.4T 토큰으로 Gopher 280B 동일 예산 능가, 70M~16B 400개 모델), 2205.14135(정확 attention, 추가 메모리 선형, GPT-2 3배), 1910.02054(2Ψ+2Ψ+12Ψ=16Ψ 바이트), 2001.08361(C≈6NBS, 파워법칙). 코드·데이터: github.com/meta-llama/llama, github.com/Dao-AILab/flash-attention, github.com/mistralai/mistral-src(mistral-inference로 리다이렉트) 접속 확인, 이 외 논문 5종은 공개 학습 코드를 확인하지 못함"
novelty_vs_paper: "6ND·16바이트/파라미터·동비율 확장·47B/13B 활성 같은 공식과 수치는 각 논문과 강의의 기여입니다. 이 글의 새 기여는 강의 10편을 비용→아키텍처→스케일링→GPU·병렬화 설계 순서로 재배열한 흐름 지도, LLaMA-1 공개 GPU-시간으로 크기별 MFU 43.4~51.4%를 재계산하고 380토큰/초 경로로 교차검증(47.6%)한 것, 16바이트 근사로 80GB HBM 한계선을 모델 크기별로 계산한 차트입니다."
---

## 한눈에 보는 결론

본 문서는 인하대학교 ECE7115 강의노트 10편(0강~9강)을 단일 설계 흐름으로 재구성한 종합 정리문서이다. 검증 기준일은 2026-09-30이며, 강의 슬라이드 원본 10종과 1차 문헌 8편의 본문을 대조하였다.

<span style="background-color: #fff59d"><strong>재구성된 흐름은 다음과 같다. 자원 회계(1강), 아키텍처(2~5강), 규모 결정(6강), 사례 검증(7강), GPU 효율(8강), 병렬화(9강)</strong></span>.

| 설계 단계 | 강의 | 핵심 질문 | 확인된 기준 |
| --- | --- | --- | --- |
| 비용 계산 | 1강 | 계산·메모리 요구량 | FLOPs = 6ND, 파라미터당 16바이트 |
| 아키텍처 | 2~4강 | 기본 뼈대 | pre-norm + RMSNorm + RoPE + SwiGLU |
| 희소화 | 5강 | 용량 확대와 계산 유지 | 토큰당 2/8 전문가, 활성 13B |
| 규모 결정 | 6강 | 데이터·모델 균형 | 70B / 1.4T 토큰(약 20:1) |
| 사례 검증 | 7강 | 실제 채택 내역 | 문맥 2K→4K→8K→32K, GQA·SWA |
| GPU 효율 | 8강 | 피크 미달 요인 | HBM IO 병목, attention 추가 메모리 선형 |
| 병렬화 | 9강 | 분할 전략 | DP·TP·PP + ZeRO 분할 |

본문에서 확정된 수치는 다음 세 가지이다.

<span style="background-color: #fff59d"><strong>학습 계산량은 6ND로 추정한다</strong></span>. Kaplan 등(2020)의 본문은 <span style="background-color: #fff59d"><strong>C ≈ 6NBS</strong></span>로 표기하며 계수 6이 순전파·역전파를 포함한다고 명시한다.

혼합정밀도 Adam 학습 시 메모리는 <span style="background-color: #fff59d"><strong>파라미터당 16바이트</strong></span>이다(ZeRO, <span style="background-color: #fff59d"><strong>2Ψ+2Ψ+12Ψ=16Ψ</strong></span>). <span style="background-color: #fff59d"><strong>6.7B 모델의 모델 상태는 107GB로 80GB A100 1장의 용량을 초과한다</strong></span>.

LLaMA-1이 공개한 GPU-시간을 역산한 모델별 <span style="background-color: #fff59d"><strong>MFU는 43.4~51.4%이다</strong></span>.

![2023년 레시피 수렴](../media/llm-training-cost-to-parallelism-guide-2026/chart-03-architecture-standard-grid.png)

## 무엇을 비교했나

정리 대상 강의는 인하대 GCL의 [ECE7115](https://gcl-inha.github.io/ece7115/) 슬라이드 10종이다.

1. [0강 Course Introduction](https://gcl-inha.github.io/ece7115/slides/0_course_introduction.pdf)
2. [1강 Resource Accounting](https://gcl-inha.github.io/ece7115/slides/1_resource_accounting.pdf)
3. [2강 Transformer Basics](https://gcl-inha.github.io/ece7115/slides/2_basics_transformer.pdf)
4. [3강 LLM Basics](https://gcl-inha.github.io/ece7115/slides/3_basics_llm.pdf)
5. [4강 Modern LLM Architecture](https://gcl-inha.github.io/ece7115/slides/4_modern_llm_architecture.pdf)
6. [5강 Mixture of Experts](https://gcl-inha.github.io/ece7115/slides/5_moe.pdf)
7. [6강 Scaling Laws](https://gcl-inha.github.io/ece7115/slides/6_scaling_laws.pdf)
8. [7강 LLM Case Study](https://gcl-inha.github.io/ece7115/slides/7_llm_case_study.pdf)
9. [8강 Understanding GPUs](https://gcl-inha.github.io/ece7115/slides/8_understanding_gpus.pdf)
10. [9강 Parallelism](https://gcl-inha.github.io/ece7115/slides/9_parallelism.pdf)

검증 문헌은 다음 8편이다.

11. [Kaplan et al., arXiv:2001.08361](https://arxiv.org/abs/2001.08361)
12. [Hoffmann et al.(Chinchilla), arXiv:2203.15556](https://arxiv.org/abs/2203.15556)
13. [Touvron et al.(LLaMA), arXiv:2302.13971](https://arxiv.org/abs/2302.13971)
14. [Touvron et al.(Llama 2), arXiv:2307.09288](https://arxiv.org/abs/2307.09288)
15. [Jiang et al.(Mistral 7B), arXiv:2310.06825](https://arxiv.org/abs/2310.06825)
16. [Jiang et al.(Mixtral), arXiv:2401.04088](https://arxiv.org/abs/2401.04088)
17. [Dao et al.(FlashAttention), arXiv:2205.14135](https://arxiv.org/abs/2205.14135)
18. [Rajbhandari et al.(ZeRO), arXiv:1910.02054](https://arxiv.org/abs/1910.02054)

하드웨어 규격은 [NVIDIA A100 데이터시트](https://www.nvidia.com/en-us/data-center/a100/)(80GB HBM2e, 2,039GB/s, BF16 312 TFLOPS)를 따랐다.

<span style="background-color: #fff59d"><strong>기존 강의노트 10개의 주소는 본 문서로 리디렉션된다</strong></span>.

## 방법 비교

| 강의(주제) | 핵심 개념 | 강의 주장 | 문헌 확인 |
| --- | --- | --- | --- |
| 1강 자원 회계 | FLOPs·메모리·MFU | 6ND 근사 | Kaplan C≈6NBS, ZeRO 16바이트 확인 |
| 2~3강 기초 | attention·학습 파이프라인 | 사전학습 중심 전환 | 후속 모델의 공통 기반으로 확인 |
| 4강 현대 아키텍처 | pre-norm·RMSNorm·RoPE·SwiGLU | 표준 조합 | LLaMA 본문 명시 확인 |
| 5강 MoE | expert·router·활성 파라미터 | 희소 활성화 | Mixtral 47B/13B, 2-of-8 확인 |
| 6강 스케일링 | power law·compute 배분 | 소규모 예측 | Chinchilla 70B/1.4T 확인 |
| 7강 케이스 | 레시피 수렴 | 문맥·attention 진화 | 2048→4096→8192→32k, SWA 4096 확인 |
| 8강 GPU | 메모리 계층·타일링 | 데이터 이동 병목 | FlashAttention 선형 메모리 확인 |
| 9강 병렬화 | DP·TP·PP·집단통신 | 통신 비용 균형 | 6.7B도 80GB 초과 확인 |

1강의 자원 회계는 dtype별 바이트 수에서 출발한다. fp32는 4바이트, fp16·bf16은 2바이트, fp8은 1바이트이다. 계산량 추정은 선형층 기준 순전파 2ND, 역전파 포함 총 6ND로 정리된다.

LLaMA-1 65B의 학습 규모는 논문 본문에 수치로 남아 있다. 2,048장의 A100-80GB에서 GPU당 초당 약 380토큰을 처리하였고, 1.4T 토큰 학습에 약 21일이 소요되었다.

ZeRO의 분석은 메모리 문제를 수치로 보여준다. GPT-2 1.5B의 모델 상태만 최소 24GB이다. 저장소 분할이 도입되기 전에는 데이터 병렬만으로 이를 나눌 수 없었다.

FlashAttention의 보고 수치는 학습 전체 기준 BERT-large 15% 단축, GPT-2 3배, GPT-NeoX 2.4배 가속이다. 근사가 아닌 정확 attention이라는 점이 채택 배경이다.

Chinchilla는 70M~16B 파라미터 400여 개 모델을 5B~500B 토큰으로 학습해 규칙을 도출하였다. Gopher와 동일한 예산에서 크기는 4분의 1(70B 대 280B), 토큰은 4배를 사용하였다.

Mistral 7B는 어텐션 창 4096, 문맥 8192로 학습되었다. 캐시는 창 크기 W로 고정되는 롤링 버퍼로 제한된다.

## 언제 무엇을 쓰나

- 학습 예산 산정: 6ND로 FLOPs를 구하고 <span style="background-color: #fff59d"><strong>312 TFLOPS × MFU 0.45</strong></span>로 GPU-시간을 환산한다.
- 필요 GPU 수 산정: <span style="background-color: #fff59d"><strong>파라미터 × 16바이트</strong></span>를 GPU 메모리로 나눈다(6.7B 최소 2장, 65.2B 최소 13장).
- 데이터 규모 결정: <span style="background-color: #fff59d"><strong>모델 크기와 토큰 수를 동비율로 확장한다</strong></span>. 추론 비용이 제약이면 토큰을 추가 투입한다(LLaMA 7B/1T).
- 장문맥 대응: <span style="background-color: #fff59d"><strong>GQA와 슬라이딩 윈도우(4096)를 적용한다</strong></span>(Mistral 7B, 이론 최대 131K).
- 용량 확대: MoE로 토큰당 활성 파라미터를 유지한다(<span style="background-color: #fff59d"><strong>Mixtral 47B/13B</strong></span>).
- 대역폭 병목: IO-aware 정확 attention 커널을 적용한다.
- 증설 후 정체: 집단 통신(all-reduce 등)을 점검한다.

## 블로그봇이 직접 확인한 것

- 슬라이드 10종의 텍스트를 추출하여 노트 주장과 대조하였다(1강 MFU 8회, 4강 RMSNorm 10회·RoPE 44회, 6강 Kaplan 20회, 8강 FlashAttention 17회, 9강 ZeRO 38회).
- 논문 8편의 PDF 본문에서 수치를 직접 확인하였다(LLaMA-1 표 2·표 15 포함).
- <span style="background-color: #fff59d"><strong>MFU 재계산 결과는 43.4/51.4/45.8/47.7%이며, 65.2B는 380토큰/초/GPU 경로로 47.6%로 교차 확인되었다</strong></span>.
- 환산 GPU-시간 <span style="background-color: #fff59d"><strong>약 102만 시간은 표 15의 1,022,362와 일치</strong></span>한다.
- 재계산식은 FLOPs(6ND) ÷ (GPU-시 × 3600초 × 312 TFLOPS)이다. 계산 스크립트와 근거 파일은 sandbox-lane-c/llm-training-cost-to-parallelism-guide-2026/에 보관하였다.
- 저장소 실재를 확인하였다([meta-llama/llama](https://github.com/meta-llama/llama), [Dao-AILab/flash-attention](https://github.com/Dao-AILab/flash-attention), [mistralai/mistral-src](https://github.com/mistralai/mistral-src)).

![메모리 요구량](../media/llm-training-cost-to-parallelism-guide-2026/chart-01-training-memory-vs-80gb-hbm.png)

![MFU 재계산](../media/llm-training-cost-to-parallelism-guide-2026/chart-02-llama1-mfu-recompute.png)

## 한계와 반론

- MFU 산출은 312 TFLOPS 밀도 가정에 근거한다. 실제 동작 클록은 미공개이다.
- 슬라이드 일부 도형·수식은 텍스트 추출에서 누락되었다(OCR 미실시). 수치 주장은 문헌 대조로 갈음하였다.
- 20토큰/파라미터는 Chinchilla 수치에서 유도한 비율이다.
- 대상 모델은 2023~2024년 초 기준이며 2026년 설계 관행은 범위 외이다.
- Kaplan과 Chinchilla 간 방법론 논쟁은 다루지 않았다.

## 적용 규칙

1. 견적은 6ND에서 시작하며 <span style="background-color: #fff59d"><strong>MFU 45~50%를 적용</strong></span>한다.
2. GPU 수는 파라미터당 16바이트 기준으로 산정한다.
3. 표준 조합(pre-norm·RMSNorm·RoPE·SwiGLU)에서 출발하여 GQA·SWA·MoE를 조건부 적용한다.
4. 모델 비교는 <span style="background-color: #fff59d"><strong>활성 파라미터 기준</strong></span>으로 수행한다.
5. 데이터와 모델 크기를 동비율로 확장한다.
6. 학습 순서는 1→4→5→6→7→8→9강을 권장한다.

## 자주 묻는 질문

**LLM 학습 비용은 어떻게 계산하나요?**
6 × 파라미터 수 × 토큰 수로 추정하며, 65.2B/1.4T 기준 약 102만 A100 GPU-시간이다.

**7B 모델이 다수 장비를 요구하는 이유는?**
파라미터당 16바이트 요구로 모델 상태만 107GB이다.

**MFU가 절반 수준인 이유는?**
집단 통신과 HBM 전송이 병목이다.

**MoE의 적용 조건은?**
토큰당 계산 유지 조건에서 저장 용량 확대가 필요한 경우이다.

## 참고 자료

- [ECE7115 강의 페이지](https://gcl-inha.github.io/ece7115/)
- [arXiv:2001.08361](https://arxiv.org/abs/2001.08361) · [arXiv:2203.15556](https://arxiv.org/abs/2203.15556) · [arXiv:2302.13971](https://arxiv.org/abs/2302.13971) · [arXiv:2307.09288](https://arxiv.org/abs/2307.09288)
- [arXiv:2310.06825](https://arxiv.org/abs/2310.06825) · [arXiv:2401.04088](https://arxiv.org/abs/2401.04088) · [arXiv:2205.14135](https://arxiv.org/abs/2205.14135) · [arXiv:1910.02054](https://arxiv.org/abs/1910.02054)
- [NVIDIA A100 데이터시트](https://www.nvidia.com/en-us/data-center/a100/)

기준일: 2026-09-30.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
