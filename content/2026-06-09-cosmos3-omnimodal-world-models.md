---
title: "NVIDIA Cosmos 3: 물리 AI를 위한 옴니모달 월드 모델"
date: 2026-06-09
draft: false
tags:
  - AI
  - NVIDIA
  - world-model
  - robotics
  - multimodal
  - open-source
source: arxiv
source_url: https://arxiv.org/abs/2606.02800
---

![Cosmos 3](/images/2026-06-09-cosmos3-omnimodal-world-models/cosmos3-overview.png)

NVIDIA가 2026년 5월 31일, COMPUTEX 2026에서 **Cosmos 3**를 발표했다. 언어·이미지·비디오·오디오·액션 시퀀스를 하나의 모델에서 처리·생성하는 **옴니모달(omnimodal) 월드 모델**로, 로봇 공학·자율주행·스마트 인프라 등 물리 AI 전반의 범용 백본을 목표로 한다.

## 핵심 아키텍처: Mixture-of-Transformers

Cosmos 3의 기반은 **Mixture-of-Transformers (MoT)** 구조다. 단일 프레임워크 안에 Reasoner(이해·추론)와 Generator(생성) 컴포넌트가 공존하며, **듀얼 타워 레이어**와 **듀얼 스트림 조인트 어텐션**을 통해 모달리티 간 정보 흐름을 효율적으로 관리한다.

![Architecture](/images/2026-06-09-cosmos3-omnimodal-world-models/cosmos3-architecture.png)

기존에는 비전-언어 모델, 비디오 생성기, 월드 시뮬레이터, 액션 모델이 각각 별도의 시스템이었다. Cosmos 3는 이 네 가지 역할을 **하나의 통합 모델**로 융합한다.

## 모델 라인업

| 모델 | 용도 |
|------|------|
| **Cosmos3-Super** | 최고 성능 범용 모델 |
| **Cosmos3-Nano** | 경량 추론용 |
| **Cosmos3-Super-Text2Image** | 텍스트→이미지 특화 |
| **Cosmos3-Super-Image2Video** | 이미지→비디오 특화 |
| **Cosmos3-Nano-Policy-DROID** | 로봇 정책 학습 특화 |

## 주요 성과

### 이해(Reasoner) 벤치마크
- Cosmos3-Nano(8B급)가 Qwen3-VL 32B, Gemma-4 31B와 동급 또는 상회하는 성능
- 특히 **물리 AI 특화 벤치마크**(ERQA, RoboSpatialHome, Where2Place)에서 압도적 우위

### 생성(Generator) 벤치마크
- **Artificial Analysis Text-to-Image 리더보드** 오픈소스 1위
- **Image-to-Video** 오픈소스 1위, 폐쇄형 Veo-3.1 상회
- **RoboArena** 로봇 정책 평가 최고 성능
- PAIBench-G, Physics-IQ 등 물리 AI 영역에서 SOTA 달성

### 추론 성능
- Cosmos3-Nano T2V 720p: B200에서 약 3초
- Cosmos3-Super도 다중 GPU로 선형적 확장 가능

## 오픈소스 생태계

Linux Foundation의 **OpenMDW-1.1** 라이선스로 전면 공개:

- **코드**: `github.com/nvidia/cosmos`, `github.com/nvidia/cosmos-framework`
- **모델 체크포인트**: Hugging Face에서 다운로드
- **합성 데이터셋**: 물리 시뮬·로봇·자율주행·디지털 휴먼·물류 5종
- **평가 벤치마크**: Cosmos-HUE (HumanEval)

NVIDIA는 Agile Robots, Black Forest Labs, Runway, Skild AI 등과 **Cosmos Coalition**을 결성해 오픈 월드 모델 생태계 확장을 추진 중이다.

## 시사점

1. **모달리티 통합의 시대**: 개별 모델(비전, 언어, 생성)의 경계가 무너지고, 하나의 모델이 모든 것을 처리하는 방향으로 빠르게 전환 중
2. **물리 AI의 기반 모델**: 로봇·자율주행 분야에서 "GPT 모멘트"가 올 수 있는 기반 마련
3. **오픈 vs 폐쇄의 경쟁**: 최고 수준의 성능을 오픈소스로 공개함으로써, 폐쇄형 모델의 존재 이유에 도전

## 한계 및 과제

- 물리 환경에서의 실제 안정성은 시뮬레이션 이상의 검증 필요
- 기업 환경에서의 통합·거버넌스 과제
- 생태계 파편화 리스크

---

**참고문헌**
- 논문: [Cosmos 3: Omnimodal World Models for Physical AI (arXiv:2606.02800)](https://arxiv.org/abs/2606.02800)
- 프로젝트 페이지: [research.nvidia.com/labs/cosmos-lab/cosmos3](https://research.nvidia.com/labs/cosmos-lab/cosmos3)
- NVIDIA 뉴스룸: [NVIDIA Launches Cosmos 3](https://nvidianews.nvidia.com/news/nvidia-launches-cosmos-3-the-open-frontier-foundation-model-for-physical-ai)
