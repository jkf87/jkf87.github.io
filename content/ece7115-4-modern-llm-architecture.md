---
title: "ECE7115 4강 정리: Modern LLM Architecture"
date: 2026-04-26
slug: ece7115-4-modern-llm-architecture
tags:
  - ece7115
  - llm
  - architecture
  - lecture-note
description: "ECE7115 4강 Modern LLM Architecture를 Pre-Norm, RMSNorm, RoPE, SwiGLU 중심으로 정리한 짧은 강의노트."
aliases:
  - ece7115-4-modern-llm-architecture/index
---

ECE7115 4강은 vanilla Transformer를 요즘 LLM 스타일로 바꾸는 핵심 선택지를 압축해서 보여준다. Pre-Norm, RMSNorm, RoPE, SwiGLU가 사실상 표준 조합에 가깝다는 점이 핵심이다.

![](./images/ece7115-4-modern-llm-architecture/cover.png)

- 기본축은 transformer지만, 실전 LLM은 LLaMA-style 변형이 많다.
- Pre-Norm은 residual 경로를 덜 건드려서 학습 안정성이 좋고 큰 LR을 쓰기 쉽다.
- RMSNorm은 mean subtraction과 bias가 없어 단순하고 빠른 편이다.
- RoPE는 positional encoding 대신 많이 쓰이는 위치 정보 방식이다.
- FFN은 ReLU보다 SwiGLU가 더 자주 보이고, bias를 빼는 설계도 흔하다.
- FLOPs가 줄었다고 runtime이 자동으로 줄지는 않으니, 계산량과 실제 속도를 분리해서 봐야 한다.

## Source
- 원문 PDF: [4_modern_llm_architecture.pdf](https://gcl-inha.github.io/ece7115/slides/4_modern_llm_architecture.pdf)
- 강의 페이지: [ECE7115](https://gcl-inha.github.io/ece7115/)


---

**시리즈 네비**

[← 이전 편: ECE7115 3강 — LLM Basics](./ece7115-3-basics-llm)  |  [ECE7115 5강 — Mixture of Experts 다음 편 →](./ece7115-5-mixture-of-experts)
