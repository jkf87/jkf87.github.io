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

## OpenMythos의 의미 — 왜 이 프로젝트가 중요한가

### 가중치 없는 아키텍처 코드가 왜 가치 있는가?

"가중치도 없는 코드가 무슨 의미가 있냐"고 물을 수 있습니다. OpenMythos의 진짜 가치는 **생각의 도구**에 있습니다. 비공개 모델의 동작 원리를 추측하고 검증 가능한 코드로 표현함으로써, AI 연구자와 개발자들이 최신 아키텍처를 **직접 만져보고 실험할 수 있는 출발점**을 제공합니다.

### 구체적으로 어떻게 써볼 수 있나?

**1. 아키텍처 학습 도구로 활용**

트랜스포머 내부를 공부하는 사람에게 1,014줄짜리 단일 파일은 최고의 교재입니다. MLA, MoE, ACT 같은 최신 기법이 실제로 어떻게 결합되는지 코드 레벨에서 따라갈 수 있습니다.

```bash
pip install open-mythos
python3 -c "from open_mythos.main import OpenMythos, MythosConfig; print('OK')"
```

**2. 소규모 실험으로 RDT 가설 검증**

1B 프리셋으로 작은 데이터셋에 학습시켜, 루프 횟수(n_loops)를 바꿔가며 실제로 "깊이 외삽"이 가능한지 직접 실험해볼 수 있습니다.

```python
# 4루프로 학습한 모델을 8루프로 추론하면 성능이 오를까?
logits_4 = model(input_ids, n_loops=4)
logits_8 = model(input_ids, n_loops=8)  # 더 깊은 추론
```

**3. 자체 모델 개발의 참고 아키텍처**

LTI-Stable Injection이나 Depth-wise LoRA 같은 개별 모듈을 떼어다 자신의 프로젝트에 적용할 수 있습니다. MIT 라이선스이므로 상업적 사용도 자유롭습니다.

**4. AI 보안 연구의 맥락 이해**

Claude Mythos가 사이버보안에서 보여준 능력의 **아키텍처적 근거**를 이해하는 데 도움이 됩니다. "왜 루프 트랜스포머가 취약점 발견에 강할 수 있는가?"라는 질문에 대한 하나의 가설을 제공합니다.

### 더 큰 그림 — AI 스케일링의 전환점

OpenMythos가 시사하는 가장 큰 메시지는 이것입니다: **"모델을 더 크게 만드는 것"만이 성능 향상의 길이 아닐 수 있다**는 것입니다.

Parcae 논문에 따르면 770M RDT가 1.3B 고정깊이 트랜스포머와 동등한 성능을 보였습니다. 파라미터를 늘리는 대신 **추론 시간에 연산량을 늘리는**(루프를 더 도는) 접근이 새로운 스케일링 패러다임이 될 수 있습니다. 이는 GPU 메모리가 제한된 환경에서 특히 의미 있는 방향입니다.

또한 백악관의 정부기관 Mythos 접근 추진, IBM의 "Mythos 이후 오픈소스" 성명, EU의 검토 불가 우려 등은 AI 모델이 기술을 넘어 **지정학적 자산**이 되었음을 보여줍니다.

---

## 자주 묻는 질문 (FAQ)

**Q: OpenMythos를 설치하면 Claude Mythos를 사용할 수 있나요?**

아닙니다. OpenMythos는 아키텍처 코드만 제공합니다. 학습된 가중치가 없으므로 실제 추론이나 취약점 탐지는 불가능합니다. 연구와 학습 목적의 구조 분석 도구로 보시면 됩니다.

**Q: RDT 가설이 실제 Mythos와 일치하나요?**

확인할 방법이 없습니다. Anthropic은 Mythos의 아키텍처를 공개하지 않았습니다. OpenMythos도 "이론적 추측"이라고 명시합니다. 공개 논문 바탕의 가장 그럴듯한 가설 정도로 이해하시면 됩니다.

**Q: 코드를 직접 학습시킬 수 있나요?**

가능하지만 별도 학습 스크립트나 데이터셋은 없습니다. 1B 프리셋으로 소규모 실험은 할 수 있으나, 의미 있는 성능을 위해서는 상당한 GPU 자원이 필요합니다.

**Q: 770M으로 1.3B 성능이 정말 가능한가요?**

Parcae 논문(Prairie et al., 2026)의 결과를 인용한 것이며, OpenMythos 자체가 검증한 것은 아닙니다. 루프 트랜스포머의 효율성은 여러 독립 연구에서 보고되고 있습니다.

**Q: Kye Gomez는 누구인가요?**

22세의 오픈소스 AI 개발자로, Swarms 에이전트 프레임워크 창시자입니다. X에서 5,500+좋아요를 받은 프로젝트이지만, 학술 논문으로 발표된 것은 아닙니다.

---

## 참고 자료

- [OpenMythos GitHub](https://github.com/kyegomez/OpenMythos)
- [Claude Mythos Preview 공식 발표](https://red.anthropic.com/2026/mythos-preview/)
- [Project Glasswing](https://www.anthropic.com/glasswing)
- [UK AISI 평가 보고서](https://www.aisi.gov.uk/blog/our-evaluation-of-claude-mythos-previews-cyber-capabilities)
- [Fortune Mythos 최초 보도](https://fortune.com/2026/03/26/anthropic-says-testing-mythos-powerful-new-ai-model-after-data-leak-reveals-its-existence-step-change-in-capabilities/)
- [Kye Gomez X 발표](https://x.com/KyeGomezB/status/2045659150340723107)

---

## About the Author

이 글은 OpenMythos GitHub 리포지토리의 전체 코드 구조 분석(main.py 1,014줄, variants.py, test_main.py)과 Anthropic 공식 발표, UK AISI 평가 보고서를 종합하여 작성되었습니다.
