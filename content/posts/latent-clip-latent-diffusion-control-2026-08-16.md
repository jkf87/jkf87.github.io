---
title: "이미지를 디코딩하기 전에 판단한다 — Latent-CLIP과 latent space 제어의 시대"
date: 2026-08-16
tags:
  - image-generation
  - diffusion
  - latent-space
  - CLIP
  - VAE
  - SDXL
  - FLUX
  - evaluation
source: arxiv
source_url: https://arxiv.org/abs/2503.08455
paper_url: https://arxiv.org/abs/2503.08455
---

이미지 생성은 이미 latent(이미지를 작은 연속 벡터로 압축한 내부 표현) 세계에서 일어나는데 평가는 아직 픽셀 세계에 있음 — 중간 결과를 보려면 매번 VAE(이미지와 압축 표현 사이를 오가는 인코더-디코더 신경망) 디코딩을 해야 하는 병목. [Latent-CLIP](https://arxiv.org/abs/2503.08455)은 latent를 직접 읽는 CLIP(이미지와 텍스트를 같은 공간에 놓아 유사도를 재는 멀티모달 모델)을 학습해서 이 병목을 없앰. 제어 지점이 안쪽으로 이동하는 흐름이라 정리함.

1. 배경. SDXL 계열은 VAE가 이미지를 128×128×4 latent로 압축하고 diffusion이 그 안에서 denoising함. 근데 CLIP, reward model, safety classifier는 이미지를 픽셀로 받아서 판단함. diffusion 중간 latent를 평가하려면 디코딩부터 해야 하고, 이 단계가 task-specific 모델의 forward pass보다 비쌀 때도 있음.

2. 조치. SDXL-Turbo의 VAE latent(64×64×4)를 직접 입력받는 CLIP을 새로 학습. 이미지-텍스트 27억 쌍을 latent로 변환해서 훈련. 128~256 A100으로 4일씩 — "latent를 읽는 모델 하나"가 생각보다 비싼 작업임.

3. 검증 결과가 강함. zero-shot(별도 미세조정 없이 바로 평가하는 방식) ImageNet에서 Latent-ViT-B/4-plus가 원본 top-1 73.5로 비슷한 크기의 pixel CLIP과 맞먹음. 생성 latent(66% 노이즈에서 denoising한 분포)에 직접 적용해도 84.6%. VAE 디코딩 없이 latent 안에서 의미 분류가 가능하다는 근거임.

4. 보상 최적화(ReNO)도 픽셀로 안 돌아감. 초기 noise를 조정해 reward를 높이는 루프에서 pixel CLIPScore(CLIP으로 잰 이미지-텍스트 일치도 점수) 대비 전체 실행 시간 약 21% 감소(11.59초 → 9.01초). T2I-CompBench(텍스트-이미지 생성이 색·질감 등 프롬프트 조건을 얼마나 지키는지 재는 벤치마크) 품질은 color 0.69, texture 0.70으로 pixel CLIP과 동등. 반복 단계가 많은 inference-time optimization일수록 절감이 누적됨.

5. 안전 필터도 latent 단계에서 작동함. I2P 데이터셋(유해 프롬프트가 어떤 이미지를 유도하는지 측정하는 안전 평가용 데이터셋)에서 harmful concept와 가까운 latent의 reward를 낮추고 50 gradient steps 동안 멀어지게 한 결과, 부적절 이미지 확률이 SDXL-Turbo 0.32 → 0.16. safety 전용인 SLD(생성 도중 안전하지 않은 개념에서 멀어지도록 유도하는 안전 가이던스 기법, 0.13)에 근접하면서 aesthetic score는 5.79 → 5.82로 유지됨.

6. 여기서 문제제기 — latent space는 모델별 인터페이스라는 것. SDXL 계열은 4채널 latent를 공유하지만 FLUX는 16채널, Wuerstchen은 VQ-VAE를 씀. SDXL용 Latent-CLIP을 FLUX에 그대로 못 쓰고 논문도 새 VAE마다 다시 학습해야 한다고 명시함. 모델 차이가 프롬프트 해석을 넘어 평가기·보상·안전 필터까지 묶어서 바꾸는 인터페이스 차이라는 것.

7. 모델 비교의 관점이 바뀜. "같은 프롬프트 결과 비교"에서 끝나지 않고 각 모델이 어떤 latent representation을 쓰고 그 공간에서 의미·안전·선호를 어떻게 읽고 조정할 수 있는지까지 봐야 함. 제어 지점이 프롬프트 → 픽셀 후처리 → latent 중간 개입으로 계속 안쪽으로 들어가고 있다는 것.

8. 이건 StateAct(픽셀 대신 프로그램 상태), SWE-Pruner Pro(히스토리 진입 전 경계 필터)와 같은 방향임 — 판단과 개입의 위치를 업스트림으로 옮겨 비용 구조를 바꾸는 것. "나중에 검사"가 아니라 "생성되는 곳에서 검사"라는 원칙의 이미지 버전.

9. 한계. 학습 비용이 크고 VAE 종속적. spatial relationship은 0.24~0.25로 reward optimization 전반의 약점이 그대로 남음. ReNO ensemble 같은 강한 조합엔 못 미침 — 핵심은 "비슷한 크기 pixel CLIP을 latent reward로 바꿔도 성능 유지 + 시간 감소"라는 절제된 주장임.

10. 결론. 생성은 latent에서 하는데 판단하려고 매번 픽셀로 돌아오는 구조가 병목이었음. 근데 latent를 읽는 평가기는 VAE마다 다시 학습해야 해서 결국 모델별 자산이 됨 — 제어 인터페이스가 곧 Lock-in이라는 결론임.

![Latent-CLIP 구조](/images/latent-clip-latent-diffusion-control-2026-08-16/latent-clip-architecture.png)

![ImageNet 원본과 SDXL 생성 이미지 비교](/images/latent-clip-latent-diffusion-control-2026-08-16/imagenet-generated-comparison.png)

![T2I-CompBench reward optimization 비교](/images/latent-clip-latent-diffusion-control-2026-08-16/t2i-clipscore-reward.png)

![GenEval prompt에서 reward optimization 비교](/images/latent-clip-latent-diffusion-control-2026-08-16/geneval-comparison.png)

![I2P safety latent guidance](/images/latent-clip-latent-diffusion-control-2026-08-16/i2p-safety-progression.png)
