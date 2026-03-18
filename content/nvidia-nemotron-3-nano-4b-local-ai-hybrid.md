---
title: "NVIDIA Nemotron 3 Nano 4B — 로컬 AI를 위한 소형 하이브리드 모델"
date: 2026-03-18
tags:
  - ai
  - nvidia
  - local-llm
  - jetson
  - mamba
description: "NVIDIA가 공개한 4B 파라미터 Mamba-Transformer 하이브리드 모델. Jetson Orin Nano에서 18 tok/s, RTX 4070에서 최저 VRAM 사용량으로 동급 최고 성능을 달성했다."
---

NVIDIA가 **Nemotron 3 Nano 4B**를 공개했다. 파라미터 수 4B에 불과하지만, 엣지 디바이스에서 동작하도록 정교하게 설계된 소형 하이브리드 모델이다. RTX GPU, Jetson, DGX Spark 같은 NVIDIA 플랫폼 어디서든 구동 가능하며, 로컬 대화형 에이전트와 에이전트 AI 시나리오를 타겟으로 한다.

## Mamba-Transformer 하이브리드 아키텍처

이 모델의 핵심은 **Mamba-Transformer 하이브리드 구조**다. 전체 42개 레이어 중 21개가 Mamba(SSM), 4개가 셀프 어텐션, 17개가 MLP로 구성되어 있다.

NVIDIA는 기존 9B 모델(Nemotron Nano 9B v2)을 **Nemotron Elastic** 기술로 압축해서 4B를 만들었다. 라우터(Router)가 종단간 학습되며 최적 압축 방향을 스스로 결정하는 구조.

| 축 | 9B (원본) | 4B (압축) |
|---|---|---|
| Depth (레이어 수) | 56 | 42 |
| Mamba Heads | 128 | 96 |
| FFN 중간 차원 | 15,680 | 12,544 |
| Embedding 차원 | 4,480 | 3,136 |

## 2단계 증류로 정밀도 복원

- **Stage 1**: 63B 토큰, 8K 컨텍스트 (1차 정밀도 회복)
- **Stage 2**: 150B 토큰, 49K 컨텍스트 (복잡한 추론 성능 복구)

이후 SFT 2단계 + 다중 환경 강화학습(RL) 적용.

## 동급 최고 성능 (4개 축)

1. **Instruction Following** (IFBench, IFEval) — 동급 최고
2. **Gaming Agency** (Orak 벤치마크) — 슈퍼마리오, 다크던전, 스타듀밸리 등에서 에이전트 수행 능력 최고
3. **VRAM 효율성** — RTX 4070에서 동급 모델 중 가장 낮은 VRAM 사용량
4. **Tool Use & 환각 방지** — 도구 호출 성능 우수, 환각 억제 경쟁력

## 양자화와 엣지 배포

- **FP8**: DGX Spark/Jetson에서 BF16 대비 **최대 1.8배 지연시간/처리량 개선**, 100% 정밀도 복원
- **Q4_K_M GGUF**: Jetson Orin Nano 8GB에서 **18 tok/s**, 9B 대비 **2배 높은 처리량**

## 실무 시사점

**로컬 LLM 채택의 진입장벽이 다시 한번 낮아졌다.** 4B 모델이 실제 에이전트 과제에서 의미 있는 성능을 낸다는 것은, 로컬에서 "쓸만한" 에이전트를 구성할 수 있는 모델이 구체화되고 있다는 뜻이다.

Jetson Orin Nano 8GB에서 18 tok/s라는 실용적 추론 속도를 확보한 점은 교육·로보틱스·IoT 도메인에서 즉시 실험 가능한 수준.

## 링크

- 모델: [BF16](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16) | [FP8](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-FP8) | [GGUF](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-4B-GGUF)
- 논문: [arXiv 2511.16664](https://arxiv.org/abs/2511.16664)
- 지원 엔진: Transformers, vLLM, TRT-LLM, Llama.cpp

*원문: [HuggingFace Blog](https://huggingface.co/blog/nvidia/nemotron-3-nano-4b)*
