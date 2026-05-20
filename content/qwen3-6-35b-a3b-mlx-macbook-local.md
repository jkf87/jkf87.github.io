---
title: "Qwen3.6-35B-A3B MLX 4bit, 맥북 M4에서 로컬로 돌려보기"
date: 2026-04-17
tags:
  - qwen
  - mlx
  - apple-silicon
  - local-llm
  - moe
  - macbook
  - ai
  - quartz
description: "Qwen3.6-35B-A3B이 MLX 포맷으로 Apple Silicon에서 구동 가능해졌다. 35B 파라미터 MoE 모델(활성 3B)을 맥북 M4 32GB에서 어떻게 돌리고, 얼마나 빠른지 정리한다."
---

> 모델: [mlx-community/Qwen3.6-35B-A3B-4bit](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit)
> 원문 모델 카드: [Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)

## 핵심 요약

Qwen3.6-35B-A3B은 **35B 파라미터 MoE(혼합 전문가) 모델**로, 추론 시 **활성 파라미터는 단 3B**다. MLX 4bit 양자화 버전이 Apple Silicon에서 구동 가능하며, **맥북 M4 32GB에서 충분히 로컬 실행**할 수 있다.

| 항목 | Qwen3.6-35B-A3B |
|------|----------------|
| 총 파라미터 | 35B |
| 활성 파라미터 | **3B** (MoE) |
| 전문가 수 | 256명 (활성 8 + 공유 1) |
| 컨텍스트 길이 | 262,144 토큰 (최대 1,010,000) |
| **다운로드 크기 (4bit)** | **19.0 GB** |
| **런타임 RAM 사용** | **~22-26 GB** |
| **디스크 필요 공간** | **~25 GB** (모델 + 캐시 여유분) |
| 비전 지원 | ✅ (이미지+텍스트+비디오) |
| 라이선스 | Apache 2.0 |

## Qwen3.6이 뭐가 달라졌나?

Qwen3.5 시리즈(2월 출시) 이후 첫 Qwen3.6 오픈 웨이트 변종이다. 커뮤니티 피드백을 직접 반영하여 **안정성과 실용성**을 최우선으로 삼았다.

### 핵심 개선 사항

1. **에이전트 코딩 강화**: 프론트엔드 워크플로우와 리포지토리 수준 추론이 더 유창하고 정밀해짐
2. **생각 보존(Thinking Preservation)**: 이력 메시지에서 추론 컨텍스트를 유지하는 새 옵션 — 반복 개발 시 오버헤드 감소
3. **멀티토큰 예측(MTP)**: 사전 학습 단계에서 multi-step 토큰 예측 학습으로 추론 속도 향상

### 아키텍처 특징

```
Hidden Layout: 10 × (3 × (Gated DeltaNet → MoE) → 1 × (Gated Attention → MoE))
```

- **Gated DeltaNet**: 선형 주의(Linear Attention) 기반 — 기존 Transformer의 O(n²)가 아닌 O(n) 복잡도
- **Gated Attention**: KV 헤드가 Q보다 적음 (Q=16, KV=2) — 효율적인 컨텍스트 처리
- **256명 전문가 중 8+1명만 활성** → 메모리 대비 높은 성능

## 벤치마크 성능

### 코딩 에이전트

| 벤치마크 | Qwen3.5-27B | Qwen3.5-35B-A3B | **Qwen3.6-35B-A3B** |
|----------|-------------|------------------|---------------------|
| SWE-bench Verified | 75.0 | 70.0 | **73.4** |
| SWE-bench Multilingual | 69.3 | 60.3 | **67.2** |
| SWE-bench Pro | 51.2 | 44.6 | **49.5** |
| Terminal-Bench 2.0 | 41.6 | 40.5 | **51.5** |
| Claw-Eval Avg | 64.3 | 65.4 | **68.7** |
| NL2Repo | 27.3 | 20.5 | **29.4** |

Terminal-Bench 2.0에서 **10포인트 이상 향상**이 인상적이다.

### 지식 & STEM

| 벤치마크 | Qwen3.5-27B | **Qwen3.6-35B-A3B** |
|----------|-------------|---------------------|
| MMLU-Pro | 86.1 | **85.2** |
| MMLU-Redux | 93.2 | **93.3** |
| GPQA | 85.5 | **86.0** |
| AIME 26 | 92.6 | **92.7** |
| LiveCodeBench v6 | 80.7 | **80.4** |

27B 밀집 모델과 거의 동등한 지식/추론 성능을 3B 활성 파라미터로 달성한다.

### 비전·언어

| 벤치마크 | Claude-Sonnet-4.5 | Qwen3.5-35B-A3B | **Qwen3.6-35B-A3B** |
|----------|-------------------|------------------|---------------------|
| MMMU | 79.6 | 81.4 | **81.7** |
| RealWorldQA | 70.3 | 84.1 | **85.3** |
| OmniDocBench | 85.8 | 89.3 | **89.9** |
| VideoMME (sub.) | 81.1 | 86.6 | **86.6** |

비전·문서·비디오 이해에서 Claude Sonnet 4.5를 능가하는 부분도 있다.

## 맥북 M4 32GB 구동 분석

### 하드웨어 요구 사항

| 구분 | 최소 요구 | 권장 | 비고 |
|------|----------|------|------|
| **통합 메모리 (RAM)** | 24GB | **32GB** | 16GB는 불가, 24GB는 타이트 |
| **디스크 여유 공간** | 20GB | **25GB** | 모델 19GB + 캐시/임시 파일 |
| **디스크 타입** | SSD | **SSD** | HDD에서는 로딩 지연 심함 |
| **Apple Silicon** | M1 | **M4** 권장 | M1/M2/M3도 구동 가능 |

### 메모리 요구량 상세

```
4bit 양자화 모델 다운로드:   19.0 GB (safetensors, 14개 샤드)
모델 로딩 (VRAM):           ~18-20 GB
KV 캐시 (8K 컨텍스트 기준): ~1-2 GB
시스템+기타:                  ~4-6 GB
───
총 필요 RAM (8K ctx):       ~22-26 GB

M4 32GB 여유:                ~6-10 GB
```

**32GB 통합 메모리에서 충분히 구동 가능**하다. 여유 메모리로 KV 캐시 확보가 가능하므로 긴 컨텍스트도 어느 정도 처리할 수 있다.

### 예상 속도

| 모드 | 예상 속도 (M4 32GB) |
|------|---------------------|
| 일반 텍스트 생성 | ~15-25 tok/s |
| 생각(Thinking) 모드 | ~8-15 tok/s (생각 토큰 포함) |
| 비전 입력 | ~10-20 tok/s |

MoE 아키텍처 덕분에 활성 파라미터가 3B에 불과하여, 35B 밀집 모델에 비해 **2-3배 빠른 추론**이 가능하다.

MoE 아키텍처 덕분에 활성 파라미터가 3B에 불과하여, 35B 밀집 모델에 비해 **2-3배 빠른 추론**이 가능하다.

### 컨텍스트 길이 vs 메모리

| 컨텍스트 | 총 RAM 예상 | M4 32GB 가능 여부 |
|----------|-------------|-------------------|
| 4K | ~22 GB | ✅ 여유 |
| 8K | ~24 GB | ✅ 여유 |
| 16K | ~26 GB | ✅ 가능 |
| 32K | ~28-30 GB | ⚠️ 여유 적음 |
| 64K | ~30-32 GB | ⚠️ 한계 근접 |
| 128K+ | ~32GB+ | ❌ OOM 위험 |

실무에서는 **4K-16K 컨텍스트**를 유지하면 가장 안정적이다.

### 다른 맥북 스펙별 구동 가능성

| Mac 모델 | RAM | 구동 가능? | 비고 |
|----------|-----|-----------|------|
| MacBook Air M4 | 16GB | ❌ | 모델 로딩 불가 |
| MacBook Air M4 | **24GB** | ⚠️ | 4K ctx만 가능, 여유 없음 |
| **MacBook Air M4** | **32GB** | **✅** | **8-16K ctx 안정, 추천** |
| MacBook Pro M4 Max | 48GB | ✅ | 32K+ ctx 가능 |
| MacBook Pro M4 Max | 64GB+ | ✅ | 64K+ ctx 가능 |
| Mac Studio M4 Ultra | 128GB+ | ✅ | 128K ctx까지 가능 |

## 설치 및 실행

### MLX 설치

```bash
pip install -U mlx-vlm
```

### 기본 실행

```bash
python -m mlx_vlm.generate \
  --model mlx-community/Qwen3.6-35B-A3B-4bit \
  --max-tokens 100 \
  --temperature 0.0 \
  --prompt "Describe this image." \
  --image <path_to_image>
```

### 채팅 모드

```python
from mlx_vlm import load, generate
from mlx_vlm.prompt_utils import apply_chat_template
from mlx_vlm.utils import load_image

model, processor = load("mlx-community/Qwen3.6-35B-A3B-4bit")

# 텍스트 전용
messages = [{"role": "user", "content": "한국어로 Qwen3.6의 특징을 설명해줘."}]
prompt = apply_chat_template(processor, messages)
output = generate(model, processor, prompt, max_tokens=2048, temperature=0.7)
print(output)

# 이미지 + 텍스트
image = load_image("screenshot.png")
messages = [{
    "role": "user",
    "content": [
        {"type": "image", "image": image},
        {"type": "text", "text": "이 스크린샷에서 무엇을 하고 있나요?"}
    ]
}]
```

## Qwen3.5 대비 주요 변화

| 항목 | Qwen3.5-35B-A3B | Qwen3.6-35B-A3B |
|------|-----------------|-----------------|
| Terminal-Bench 2.0 | 40.5 | **51.5 (+11)** |
| Claw-Eval Avg | 65.4 | **68.7 (+3.3)** |
| NL2Repo | 20.5 | **29.4 (+8.9)** |
| MCPMark | 27.0 | **37.0 (+10)** |
| MCP-Atlas | 62.4 | **62.8 (+0.4)** |
| AIME 26 | 91.0 | **92.7 (+1.7)** |
| OmniDocBench | 89.3 | **89.9 (+0.6)** |

에이전트 코딩과 MCP(도구 사용) 능력이 특히 크게 향상되었다.

## 추천 샘플링 파라미터

Qwen 공식 추천:

- **생각 모드 (일반)**: `temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5`
- **생각 모드 (코딩)**: `temperature=0.6, top_p=0.95, top_k=20, presence_penalty=0.0`
- **일반 모드 (추론)**: `temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5`
- **일반 모드 (일반)**: `temperature=0.7, top_p=0.8, top_k=20, presence_penalty=1.5`

## 실무 활용 포인트

### 교육 현장에서
- 로컬에서 이미지+텍스트 멀티모달 처리 가능
- 문서 OCR, 수학 문제 풀이, 시각적 추론 등에 활용
- 인터넷 연결 없이도 실행 가능 (오프라인 환경)

### 업무 자동화에서
- MCP 기반 도구 호출 가능 (MCPMark 37.0)
- 터미널 환경에서의 코딩 능력이 크게 향상 (Terminal-Bench 51.5)
- 32GB 맥북에서 완전 로컬로 에이전트 코딩 가능

### 한계
- **긴 컨텍스트(128K+)**에서는 32GB에서 OOM 가능
- **생각 모드** 시 속도가 느려질 수 있음
- **비전 처리** 시 추가 VRAM 소모

## FAQ

### 맥북 M4 16GB에서도 돌아가나요?
불가능합니다. 모델 로딩만 ~19GB이므로 최소 **24GB RAM**, 안정적 사용을 위해 **32GB RAM**이 필요합니다. 디스크 여유 공간도 **25GB 이상** 확보하세요.

### Qwen3.5-35B-A3B에서 업그레이드할 가치가 있나요?
에이전트 코딩과 MCP 능력이 크게 향상되었습니다. 특히 Terminal-Bench +10, MCPMark +10, NL2Repo +8.9 포인트 향상이 실질적입니다. 업그레이드를 권장합니다.

### 클로드 모델보다 나은가요?
특정 벤치마크에서는 Claude Sonnet 4.5와 동급이거나 능가합니다 (RealWorldQA, OmniDocBench 등). 다만, 복잡한 다단계 추론이나 긴 문맥 이해에서는 클로드 모델이 여전히 우위일 수 있습니다.

### 비디오도 처리할 수 있나요?
예. VideoMME, VideoMMMU 등에서 높은 점수를 기록했으며, 비디오 이해 능력이 뛰어납니다. 단, 비디오 처리 시 VRAM 소모가 커질 수 있으니 긴 비디오는 주의가 필요합니다.
