---
title: "ECE7115 6강: Scaling Laws"
date: 2026-04-26
tags:
  - ai
  - llm
  - lecture-notes
  - ece7115
  - scaling-laws
  - chinchilla
  - kaplan
description: "ECE7115 6강 Scaling Laws 정리. Kaplan과 Chinchilla 법칙, compute-optimal 학습, 모델·데이터·연산량 사이의 거듭제곱 관계, 그리고 over-training 트렌드까지 짧게 정리함."
---

# ECE7115 6강: Scaling Laws

![Scaling laws cover](./images/ece7115-6-scaling-laws/cover.png)

## 한줄 정리
Scaling law는 작은 모델 몇 개로 큰 모델의 손실을 예측하는 거듭제곱(power-law) 규칙으로, 하이퍼파라미터 선택과 compute 분배를 데이터 기반으로 결정하게 해줌.

## 핵심 포인트
- Kaplan(2020)은 데이터·모델 크기와 test loss가 log-log 공간에서 선형(거듭제곱) 관계를 가지며, 데이터 구성은 기울기가 아니라 offset만 바꾼다는 점을 보였음. 모델 모양(aspect ratio, depth/width)은 성능에 약하게만 영향을 줌.
- 작은 모델로 scaling law를 먼저 fit한 뒤 큰 모델로 외삽하면, optimizer·architecture(Transformer vs LSTM)·MoE 같은 설계 선택을 큰 학습 비용 없이 비교할 수 있음. critical batch size는 목표 loss가 낮아질수록 커진다는 점도 같은 방식으로 예측됨.
- Kaplan 법칙은 "데이터보다 모델 키우기"를 권했지만, Chinchilla(Hoffmann+ 2022)는 cosine LR scheduler의 T_max 설정 오류를 지적하며 모델 크기를 과대평가했다고 반박함.
- Chinchilla는 IsoFLOPs 등 3가지 방법으로 fit한 결과, compute-optimal 비율로 파라미터당 약 20 토큰(20:1)을 학습해야 한다고 제안함. 즉, 같은 compute라면 모델은 더 작고 데이터는 더 많아야 함.
- 다만 실제 배포에서는 inference 비용이 지배적이라 일부러 over-train함. GPT-3는 2 tokens/param, Chinchilla는 20, LLaMA 2 70B는 29, LLaMA 3 70B는 215 tokens/param까지 늘어났고, downstream 성능 scaling은 upstream loss만큼 깔끔하게 예측되지 않는다는 점도 주의해야 함.

## Source
- 원본 PDF: [6_scaling_laws.pdf](https://gcl-inha.github.io/ece7115/slides/6_scaling_laws.pdf)
- 강의 페이지: [ECE7115](https://gcl-inha.github.io/ece7115/)
