---
title: "OpenMythos: Claude Mythos의 비밀을 파헤친 오픈소스 재구현 프로젝트"
date: 2026-04-20
tags:
  - AI
  - OpenMythos
  - Claude Mythos
  - 트랜스포머
  - 오픈소스
  - 사이버보안
  - Anthropic
description: "Anthropic의 비공개 AI 모델 Claude Mythos의 아키텍처를 오픈소스로 재구현한 OpenMythos 프로젝트를 분석합니다."
---

# OpenMythos: Claude Mythos의 비밀을 파헤친 오픈소스 재구현 프로젝트

2026년 4월, AI 업계를 뒤흔든 모델이 하나 있습니다. Anthropic의 **Claude Mythos**입니다. 자율적으로 제로데이 취약점을 발견하고, SWE-bench 93.9%를 달성한 이 모델은 너무 강력해서 일반 공개조차 되지 않았습니다. 그런데 이 모델의 아키텍처를 공개 논문만으로 **이론적으로 재구현**한 오픈소스 프로젝트가 등장했습니다. 바로 **OpenMythos**입니다.

![뉴럴 네트워크 시각화](https://media3.giphy.com/media/YedmoNc3rsqI0/giphy.gif)

---

## Claude Mythos — 너무 강력해서 공개할 수 없는 모델

### 우연히 발견된 존재

Claude Mythos의 존재는 2026년 3월 26일, Anthropic의 CMS 설정 오류로 약 3,000개의 미공개 자산이 노출되면서 세상에 알려졌습니다. 내부 코드명은 **"Capybara"**. Fortune 매체가 이를 최초 보도했고, Anthropic은 4월 7일에 공식 발표했습니다.

### 충격적인 사이버보안 능력

| 항목 | Claude Mythos | Claude Opus 4.6 |
|------|--------------|-----------------|
| SWE-bench | **93.9%** | 80.8% |
| Firefox JS 쉘 익스플로잇 | **181개** | 2개 |
| CTF 전문가 레벨 성공률 | **73%** | 0% |
| 네트워크 침투 시뮬레이션 | 32단계 중 22단계 | 16단계 |

27년 된 OpenBSD TCP/SACK 버그, 16년 된 FFmpeg H.264 코덱 취약점, 17년 된 FreeBSD NFS 원격 코드 실행 결함까지 자율적으로 발견했습니다.

### Project Glasswing — 방어적 사용만 허용

Anthropic은 **Project Glasswing** 컨소시엄을 통해 방어적 사이버보안 목적으로만 배포합니다. 참여 기업: Amazon, Apple, Google, Microsoft, Cisco, CrowdStrike, NVIDIA 등.

![사이버보안 시각화](https://media2.giphy.com/media/FtLZ05FBnC48uYGzuO/giphy.gif)

---

## OpenMythos — 커뮤니티가 해체한 아키텍처의 비밀

| 항목 | 내용 |
|------|------|
| GitHub | [kyegomez/OpenMythos](https://github.com/kyegomez/OpenMythos) |
| 제작자 | Kye Gomez (Swarms Corp) |
| 라이선스 | MIT |
| 설치 | `pip install open-mythos` |

OpenMythos는 Anthropic과 **무관한** 독립 프로젝트입니다. 실제 모델 가중치는 포함되어 있지 않습니다.

### 핵심 가설: Recurrent-Depth Transformer (RDT)

Claude Mythos는 수백 개의 레이어를 쌓은 것이 아니라 **소수의 레이어를 반복 실행**하는 구조라는 것이 핵심 주장입니다.

![반복 루프 시각화](https://media3.giphy.com/media/iwJMmqOiqzss0/giphy.gif)

3단계 구조: **Prelude**(1회) -> **Recurrent Block**(최대 16회 반복) -> **Coda**(1회)

> **비유:** 100층 건물 대신 3층 건물에서 엘리베이터로 16번 왕복하며 일하는 구조입니다.

---

## 5가지 핵심 기술

### 1. LTI-Stable Injection — 발산 방지

행렬 A를 `exp(-exp(x))`로 제한하여 항상 0~1 사이 보장. Parcae 아키텍처 기반.

### 2. Multi-Latent Attention (MLA)

DeepSeek-V2 기반. KV 캐시를 저차원 잠재 벡터로 압축. **10~20배 메모리 절약**.

### 3. Sparse MoE

64개 전문가 중 토큰당 4개만 활성화(6.25%). SwiGLU FFN.

### 4. ACT Halting — 적응형 조기 종료

누적 확률 0.99 도달 시 정지. **2~3배 추론 처리량 향상** 가능.

### 5. Depth-wise LoRA

루프마다 고유 스케일 벡터 적용.

![딥러닝 시각화](https://media1.giphy.com/media/lkdIhnHHnFma6xvICt/giphy.gif)

---

## 실제 사용법

```bash
pip install open-mythos
```

```python
import torch
from open_mythos.main import OpenMythos, MythosConfig

cfg = MythosConfig(vocab_size=1000, dim=256, n_heads=8,
    max_seq_len=128, max_loop_iters=4, n_experts=8, attn_type="mla")
model = OpenMythos(cfg)
input_ids = torch.randint(0, 1000, (2, 16))
logits = model(input_ids, n_loops=4)
output = model.generate(input_ids, max_new_tokens=8, n_loops=8)
```

| 프리셋 | dim | 헤드 | 전문가 | 루프 | 시퀀스 |
|--------|-----|------|--------|------|--------|
| 1B | 2048 | 16 | 16 | 16 | 4K |
| 10B | 4096 | 32 | 64 | 24 | 8K |
| 100B | 8192 | 64 | 160 | 32 | 1M |
| 1T | 16384 | 128 | 512 | 64 | 1M |

---

## 시사점과 의의

### 1. 파라미터보다 추론 연산량
770M RDT가 1.3B 고정깊이 트랜스포머와 동등. 새로운 스케일링 패러다임.

### 2. 추론 시 깊이 조절
쉬운 질문 4루프, 어려운 질문 16루프. 깊이 외삽 가능.

### 3. 오픈소스 커뮤니티의 힘
비공개 모델을 24시간 안에 재구현. 실제 일치 여부는 불명.

### 4. AI 보안의 지정학
백악관 접근 추진, IBM 성명. 기술을 넘어 지정학적 영향력.

---

## FAQ

**Q: OpenMythos로 Claude Mythos를 사용할 수 있나요?**
아닙니다. 아키텍처 코드만 제공되며 가중치가 없습니다.

**Q: RDT 가설이 실제 Mythos와 일치하나요?**
확인 불가. "이론적 추측"이라고 명시합니다.

---

## 참고 자료
- [OpenMythos GitHub](https://github.com/kyegomez/OpenMythos)
- [Claude Mythos Preview](https://red.anthropic.com/2026/mythos-preview/)
- [Project Glasswing](https://www.anthropic.com/glasswing)
- [UK AISI 평가](https://www.aisi.gov.uk/blog/our-evaluation-of-claude-mythos-previews-cyber-capabilities)

## About the Author
OpenMythos GitHub 코드 구조 분석과 Anthropic 공식 발표 자료를 종합한 기술 분석입니다.
