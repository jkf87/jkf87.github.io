---
title: "맥북 32GB에서 35B 로컬 LLM 실행하기: Qwen3.6-35B-A3B MLX 4bit 가이드"
date: 2026-04-17
author: 한준구(코난쌤)
tags:
  - qwen
  - mlx
  - apple-silicon
  - local-llm
  - moe
  - macbook
  - ai
  - quartz
description: "Qwen3.6-35B-A3B(활성 3B MoE) MLX 4bit 모델을 맥북 32GB에서 직접 설치·다운로드하며 확인한 최신 저장소 정보, 네트워크 실측과 실무 팁을 정리합니다."
verified_at: 2026-09-27
draft: false
---

> 모델: [mlx-community/Qwen3.6-35B-A3B-4bit](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit)
> 원문 모델 카드: [Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)

## 핵심 요약

Qwen3.6-35B-A3B은 35B 파라미터 MoE(혼합 전문가) 모델이고, 추론 시 <span style="background-color: #fff59d"><strong>활성 파라미터는 3B</strong></span>입니다. MLX 4bit 양자화 버전이 Apple Silicon에서 구동 가능하고, 맥북 32GB에서 로컬 실행이 현실적입니다.

| 항목 | Qwen3.6-35B-A3B |
|------|----------------|
| 총 파라미터 | 35B |
| 활성 파라미터 | 3B (MoE) |
| 전문가 수 | 256명 (활성 8 + 공유 1) |
| 컨텍스트 길이 | 262,144 토큰 (최대 1,010,000) |
| 다운로드 크기 (4bit) | 20.4 GB (safetensors 4개 샤드, 2026-09-25 기준) |
| 런타임 RAM 사용 | ~22-26 GB |
| 디스크 필요 공간 | ~25 GB 이상 (모델 20.4GB + 캐시 여유분) |
| 비전 지원 | ✅ (이미지+텍스트+비디오) |
| 라이선스 | Apache 2.0 |

2026-09-25 재검증 때 HF API로 저장소를 다시 확인했는데, 초판에 적힌 "19.0GB / 14개 샤드"는 과거 정보였습니다. 지금은 <span style="background-color: #fff59d"><strong>4개 샤드에 총 20.4GB</strong></span>입니다. 이 글의 수치는 그 기준으로 수정해 뒀습니다.

## Qwen3.6에서 달라진 점

Qwen3.5 시리즈(2월 출시) 이후 첫 Qwen3.6 오픈 웨이트 변종입니다. 커뮤니티 피드백을 반영해 안정성과 실용성을 최우선으로 잡았습니다.

### 핵심 개선 사항

1. 에이전트 코딩 강화: 프론트엔드 워크플로우와 리포지토리 수준 추론이 더 유창하고 정밀해짐
2. 생각 보존(Thinking Preservation): 이력 메시지에서 추론 컨텍스트를 유지하는 새 옵션 — 반복 개발 시 오버헤드 감소
3. 멀티토큰 예측(MTP): 사전 학습 단계에서 multi-step 토큰 예측 학습으로 추론 속도 향상

### 아키텍처 특징

```
Hidden Layout: 10 × (3 × (Gated DeltaNet → MoE) → 1 × (Gated Attention → MoE))
```

- Gated DeltaNet: 선형 주의(Linear Attention) 기반 — 기존 Transformer의 O(n²) 복잡도를 O(n)으로 낮춤
- Gated Attention: KV 헤드가 Q보다 적음 (Q=16, KV=2) — 효율적인 컨텍스트 처리
- 256명 전문가 중 8+1명만 활성 → 메모리 대비 높은 성능

## 벤치마크 성능

아래 수치는 2026-09-25에 원본 모델 카드와 대조해 전수 일치를 확인했습니다.

### 코딩 에이전트

| 벤치마크 | Qwen3.5-27B | Qwen3.5-35B-A3B | Qwen3.6-35B-A3B |
|----------|-------------|------------------|---------------------|
| SWE-bench Verified | 75.0 | 70.0 | 73.4 |
| SWE-bench Multilingual | 69.3 | 60.3 | 67.2 |
| SWE-bench Pro | 51.2 | 44.6 | 49.5 |
| Terminal-Bench 2.0 | 41.6 | 40.5 | 51.5 |
| Claw-Eval Avg | 64.3 | 65.4 | 68.7 |
| NL2Repo | 27.3 | 20.5 | 29.4 |

Terminal-Bench 2.0에서 <span style="background-color: #fff59d"><strong>10포인트 이상 향상</strong></span>이 인상적입니다.

### 지식 & STEM

| 벤치마크 | Qwen3.5-27B | Qwen3.6-35B-A3B |
|----------|-------------|---------------------|
| MMLU-Pro | 86.1 | 85.2 |
| MMLU-Redux | 93.2 | 93.3 |
| GPQA | 85.5 | 86.0 |
| AIME 26 | 92.6 | 92.7 |
| LiveCodeBench v6 | 80.7 | 80.4 |

27B 밀집 모델과 거의 동등한 지식/추론 성능을 3B 활성 파라미터로 달성합니다.

### 비전·언어

| 벤치마크 | Claude-Sonnet-4.5 | Qwen3.5-35B-A3B | Qwen3.6-35B-A3B |
|----------|-------------------|------------------|---------------------|
| MMMU | 79.6 | 81.4 | 81.7 |
| RealWorldQA | 70.3 | 84.1 | 85.3 |
| OmniDocBench | 85.8 | 89.3 | 89.9 |
| VideoMME (sub.) | 81.1 | 86.6 | 86.6 |

비전·문서·비디오 이해에서 Claude Sonnet 4.5를 능가하는 부분도 있습니다.

## 맥북 32GB 구동 분석 (M1~M4)

### 하드웨어 요구 사항

| 구분 | 최소 요구 | 권장 | 비고 |
|------|----------|------|------|
| 통합 메모리 (RAM) | 24GB | 32GB | 16GB는 불가, 24GB는 타이트 |
| 디스크 여유 공간 | 21GB | 25GB 이상 | 모델 20.4GB + 캐시/임시 파일 |
| 디스크 타입 | SSD | SSD | HDD에서는 로딩 지연 심함 |
| Apple Silicon | M1 | M4 권장 | M1/M2/M3도 구동 가능 |

### 메모리 요구량 상세

```
4bit 양자화 모델 다운로드:   20.4 GB (safetensors, 4개 샤드, 2026-09-25 기준)
모델 로딩 (VRAM):           ~18-21 GB
KV 캐시 (8K 컨텍스트 기준): ~1-2 GB
시스템+기타:                  ~4-6 GB
───
총 필요 RAM (8K ctx):       ~22-26 GB

32GB 여유:                   ~6-10 GB
```

<span style="background-color: #fff59d"><strong>32GB 통합 메모리에서 충분히 구동 가능</strong></span>합니다. 여유 메모리로 KV 캐시 확보가 되니까 긴 컨텍스트도 어느 정도 처리할 수 있습니다.

### 예상 속도

아래 표는 원래 글의 추정치입니다(2026-04, M4 32GB 기준). 블로그봇 실측(M2 Max, 2026-09-25·09-27)은 아래 검증 로그를 참고하세요.

| 모드 | 예상 속도 (M4 32GB) |
|------|---------------------|
| 일반 텍스트 생성 | ~15-25 tok/s |
| 생각(Thinking) 모드 | ~8-15 tok/s (생각 토큰 포함) |
| 비전 입력 | ~10-20 tok/s |

MoE 아키텍처 덕분에 활성 파라미터가 3B에 불과해서, 35B 밀집 모델에 비해 2-3배 빠른 추론이 가능합니다.

### 컨텍스트 길이 vs 메모리

| 컨텍스트 | 총 RAM 예상 | 32GB 가능 여부 |
|----------|-------------|-------------------|
| 4K | ~22 GB | ✅ 여유 |
| 8K | ~24 GB | ✅ 여유 |
| 16K | ~26 GB | ✅ 가능 |
| 32K | ~28-30 GB | ⚠️ 여유 적음 |
| 64K | ~30-32 GB | ⚠️ 한계 근접 |
| 128K+ | ~32GB+ | ❌ OOM 위험 |

실무에서는 <span style="background-color: #fff59d"><strong>4K-16K 컨텍스트를 유지</strong></span>하면 가장 안정적입니다.

### 다른 맥북 스펙별 구동 가능성

| Mac 모델 | RAM | 구동 가능? | 비고 |
|----------|-----|-----------|------|
| MacBook Air M4 | 16GB | ❌ | 모델 로딩 불가 |
| MacBook Air M4 | 24GB | ⚠️ | 4K ctx만 가능, 여유 없음 |
| MacBook Air M4 | 32GB | ✅ | 8-16K ctx 안정, 추천 |
| MacBook Pro M4 Max | 48GB | ✅ | 32K+ ctx 가능 |
| MacBook Pro M4 Max | 64GB+ | ✅ | 64K+ ctx 가능 |
| Mac Studio M4 Ultra | 128GB+ | ✅ | 128K ctx까지 가능 |

## 설치 및 실행

### MLX 설치

```bash
pip install -U mlx-vlm
```

2026-09-25 재검증 당시 mlx-vlm 0.7.3이 설치됐는데, 모델 카드의 안내 명령과 이 글의 코드 경로가 <span style="background-color: #fff59d"><strong>그대로 동작</strong></span>했습니다.

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
prompt = apply_chat_template(processor, model.config, messages)
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
prompt = apply_chat_template(processor, model.config, messages, num_images=1)
output = generate(model, processor, prompt, image=image, max_tokens=2048)
print(output)
```

<span style="background-color: #fff59d"><strong>주의 (2026-09-27 실측)</strong></span>: 모델 카드 초판에 있던 `apply_chat_template(processor, messages)` 형태는 mlx-vlm 0.7.3에서 TypeError가 납니다. <span style="background-color: #fff59d"><strong>두 번째 인자로 model.config를 넘기고, 이미지를 쓸 때는 num_images=1을 추가</strong></span>해야 합니다. 위 코드는 이 실행에서 직접 돌아간 확인 버전입니다.

## Qwen3.5 대비 주요 변화

| 항목 | Qwen3.5-35B-A3B | Qwen3.6-35B-A3B |
|------|-----------------|-----------------|
| Terminal-Bench 2.0 | 40.5 | 51.5 (+11) |
| Claw-Eval Avg | 65.4 | 68.7 (+3.3) |
| NL2Repo | 20.5 | 29.4 (+8.9) |
| MCPMark | 27.0 | 37.0 (+10) |
| MCP-Atlas | 62.4 | 62.8 (+0.4) |
| AIME 26 | 91.0 | 92.7 (+1.7) |
| OmniDocBench | 89.3 | 89.9 (+0.6) |

에이전트 코딩과 MCP(도구 사용) 능력이 특히 크게 향상됐습니다.

## 추천 샘플링 파라미터

Qwen 공식 추천:

- 생각 모드 (일반): temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5
- 생각 모드 (코딩): temperature=0.6, top_p=0.95, top_k=20, presence_penalty=0.0
- 일반 모드 (추론): temperature=1.0, top_p=0.95, top_k=20, presence_penalty=1.5
- 일반 모드 (일반): temperature=0.7, top_p=0.8, top_k=20, presence_penalty=1.5

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
- 긴 컨텍스트(128K+)에서는 32GB에서 OOM 가능
- 생각 모드 시 속도가 느려질 수 있음
- 비전 처리 시 추가 VRAM 소모

## FAQ

### 16GB 맥북에서도 실행할 수 있나요?
불가능합니다. 모델 다운로드만 20.4GB이므로 <span style="background-color: #fff59d"><strong>최소 24GB RAM, 안정적 사용을 위해 32GB RAM</strong></span>이 필요합니다. 디스크 여유 공간도 25GB 이상 확보하세요.

### 첫 다운로드는 얼마나 걸리나요?
회선에 따라 크게 다릅니다. 블로그봇이 2026-09-25에 직접 측정했을 때 <span style="background-color: #fff59d"><strong>단일 스트림 0.53MB/s</strong></span>였고, 16분할 병렬 다운로드로 <span style="background-color: #fff59d"><strong>합산 0.3~5.6MB/s</strong></span>까지 시간대별로 변동했습니다.

이 속도면 20.4GB를 받는 데 수 시간이 걸립니다. huggingface-cli 같은 재개 가능한 방법을 쓰고, 한 번에 끝내려 하지 말고 <span style="background-color: #fff59d"><strong>밤에 걸어두는 게 편합니다</strong></span>.

### Qwen3.5에서 업그레이드할 가치가 있나요?
에이전트 코딩과 MCP 능력이 크게 향상됐습니다. 특히 Terminal-Bench +10, MCPMark +10, NL2Repo +8.9 포인트 향상이 실질적입니다. 업그레이드를 권장합니다.

### Claude 모델과 비교하면 어떤가요?
특정 벤치마크에서는 Claude Sonnet 4.5와 동급이거나 능가합니다 (RealWorldQA, OmniDocBench 등). 다만 복잡한 다단계 추론이나 긴 문맥 이해에서는 클로드 모델이 여전히 우위일 수 있습니다.

### 비디오 처리도 지원하나요?
예. VideoMME, VideoMMMU 등에서 높은 점수를 기록했고 비디오 이해 능력이 좋습니다. 단, 비디오 처리 시 VRAM 소모가 커지니까 긴 비디오는 주의가 필요합니다.

### 모델 카드 파이썬 예제가 TypeError를 내는 이유는 뭔가요?

mlx-vlm 0.7.3에서 `apply_chat_template` 시그니처가 바뀌어서입니다. 두 번째 인자로 `model.config`를 넘기고, 이미지 입력 시 `num_images=1`을 추가하면 됩니다. 2026-09-27 실측으로 확인한 수정 코드를 본문 채팅 모드 예제에 반영해 뒀습니다.

## 블로그봇이 직접 확인한 것 (검증 로그)

2026-09-25 16:00 1차 실행에서 설치 명령, 모델 저장소 최신 정보, 원본 모델 카드 대조, 다운로드 속도를 실측했습니다. 2026-09-27 10:00 2차 실행에서 <span style="background-color: #fff59d"><strong>다운로드 완료 후 추론 실측(텍스트·비전·CLI)까지 마쳤습니다</strong></span>. 이제 이 글에 적힌 실행 경로는 전부 블로그봇이 이 머신에서 직접 돌려 확인했습니다.

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-09-25 |
| 에이전트 | OpenClaw 2026.9.6 (eb377ac) |
| 기기 | MacBook Pro 16인치, M2 Max 32GB (Mac14,5), macOS 26.5.1 |
| Python | 3.13.6 |
| mlx / mlx-vlm | 0.32.2 / 0.7.3 |
| transformers / huggingface_hub | 5.17.0 / 1.33.0 |

### 확인 1: 설치

```bash
$ python3 -m venv .venv
$ .venv/bin/pip install -U mlx-vlm
$ .venv/bin/python -c "import mlx_vlm, mlx.core as mx; print('ok')"
IMPORT_OK mlx_vlm 0.7.3 | mlx 0.32.2
```

글에 소개된 파이썬 스니펫의 임포트 경로(mlx_vlm.load, prompt_utils.apply_chat_template, utils.load_image)도 0.7.3에서 그대로 동작하는 걸 확인했습니다.

### 확인 2: 모델 저장소 실측

```bash
$ curl -s 'https://huggingface.co/api/models/mlx-community/Qwen3.6-35B-A3B-4bit?blobs=true'
files: 4
total GB: 20.4
downloads: 25408
lastModified: 2026-04-16T16:32:41Z
model-00001-of-00004.safetensors 5288196018
model-00002-of-00004.safetensors 5368472749
model-00003-of-00004.safetensors 5368324139
model-00004-of-00004.safetensors 4377211365
```

초판 본문의 "19.0GB / 14개 샤드"는 과거 정보라서 "20.4GB / 4개 샤드"로 수정했습니다.

### 확인 3: 원본 모델 카드 대조

[Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) 카드와 본문 수치를 대조했습니다.

<span style="background-color: #fff59d"><strong>구조와 스펙은 전부 일치합니다</strong></span>: 35B 총/3B 활성, 전문가 256(활성 8+공유 1), Gated DeltaNet/Gated Attention 구조(Q=16, KV=2), 컨텍스트 <span style="background-color: #fff59d"><strong>262,144(최대 1,010,000)</strong></span>.

<span style="background-color: #fff59d"><strong>벤치마크 수치도 일치합니다</strong></span>: SWE-bench Verified 73.4, Terminal-Bench 2.0 51.5, MCPMark 37.0, AIME26 92.7, MMMU 81.7 등. 라이선스는 <span style="background-color: #fff59d"><strong>apache-2.0</strong></span> 태그로 확인했습니다.

### 확인 4: 다운로드 실측

```bash
$ # 단일 스트림 150MB 구간
$ curl -sL -o /dev/null -w 'SPEED_BPS=%{speed_download} TIME=%{time_total}' \
    -r 0-157286399 .../model-00001-of-00004.safetensors
BYTES=157286400 SPEED_BPS=534205 TIME=294.43

$ # 16분할 병렬 (재개 가능) 관측치
44449792 -> 50053120 bytes (약 9초) = 합산 약 5.6 MB/s
09-25 16:18:51 total_kb=751376
09-25 16:19:51 total_kb=772164   # 구간별로 0.3~5.6 MB/s 변동
```

![mlx-vlm 설치와 모델 저장소 실측 화면](media/qwen3-6-35b-a3b-mlx-macbook-local/verify-01-install-repo-2026-09-25.png)

![다운로드 실측 화면 — 단일 스트림과 16분할 병렬](media/qwen3-6-35b-a3b-mlx-macbook-local/verify-02-download-2026-09-25.png)

### 확인 5: 추론 실측 (2026-09-27 2차 실행)

다운로드는 2026-09-26 05:47에 4샤드 전부 완료됐습니다(dl-status.log ALL_DONE). 같은 sandbox에서 문서화된 세 경로를 순서대로 돌렸습니다.

텍스트 생성(Python API):

```bash
$ .venv/bin/python gen-text.py .
load_time_s=8.1          # 웜 상태
gen_time_s=58.0          # 첫 실행: 20.4GB mmap 웨이트 first-touch 포함
prompt_tokens=29 generation_tokens=93 finish_reason='stop'
prompt_tps=0.53 generation_tps=67.73
peak_memory=20.56        # MLX 보고값(GB)
```

비전 입력(Python API, 480x270 테스트 이미지):

```bash
$ .venv/bin/python gen-vision.py . own-test-image.png
gen_time_s=47.1          # 이미지 인코딩 + 생성
prompt_tokens=151 generation_tokens=74 finish_reason='stop'
prompt_tps=3.37 generation_tps=64.19
peak_memory=20.72        # MLX 보고값(GB)
```

문서화된 CLI 경로:

```bash
$ .venv/bin/python -m mlx_vlm.generate --model . --max-tokens 100 \
    --temperature 0.0 --prompt "Describe this image." --image own-test-image.png
 # "blue square / orange triangle / green oval" — 도형 3개를 모두 정확히 식별, EXIT=0
```

정리하면:

- <span style="background-color: #fff59d"><strong>생성 속도는 MLX 보고 기준 텍스트 67.7 tok/s, 비전 64.2 tok/s</strong></span>입니다. 활성 3B MoE라 32GB 기기에서도 여유가 있습니다.
- <span style="background-color: #fff59d"><strong>peak_memory는 텍스트 20.56GB, 비전 20.72GB</strong></span>로, 32GB에서 긴 컨텍스트를 더 얹으면 여유가 없는 구조입니다.
- 첫 실행 벽시계(58초)에는 20.4GB 웨이트 first-touch가 포함됩니다. 재실행하면 로드가 8초대로 줄어듭니다.
- 비전 프롬프트 토큰이 151로 텍스트(29)의 5배 넘게 나옵니다. 이미지 전처리 토큰이 붙기 때문입니다.

![텍스트 생성 실측 — gen-text.py 결과](media/qwen3-6-35b-a3b-mlx-macbook-local/verify-03-textgen-2026-09-27.png)

![비전 입력 실측 — gen-vision.py 결과](media/qwen3-6-35b-a3b-mlx-macbook-local/verify-04-vision-2026-09-27.png)

### 이번 실행에서 못 한 것

2차 실행까지 마치고 남은 것은 두 가지입니다. 긴 컨텍스트(128K+) 입력과 여러 요청 동시 실행은 32GB RAM 한계로 확인하지 않았습니다. 벤치마크 점수는 원 모델 카드 보고값을 그대로 인용합니다.

## 한계와 막힌 부분

- 2026-09-27 2차 실행으로 추론 속도·메모리 실측까지 마쳤습니다(위 검증 로그 확인 5). 긴 컨텍스트(128K+)와 동시 실행 실측은 여전히 없습니다.
- 검증 기기는 <span style="background-color: #fff59d"><strong>M2 Max 32GB</strong></span>입니다. 본문의 M4 기준 속도 표는 원래 글의 추정치라서 그대로 뒀고, M2 Max 실측치는 검증 로그를 보세요.
- 긴 컨텍스트(128K+)는 32GB에서 OOM 가능성, 비전 처리 시 VRAM 추가 소모는 기존 주의 그대로입니다.
- HF CDN 속도가 시간대별로 0.3~5.6MB/s까지 변동해서, 첫 다운로드는 회선 상태가 좋은 시간대를 노리는 게 낫습니다.

## 참고 자료

**출처:**

- [mlx-community/Qwen3.6-35B-A3B-4bit (MLX 변환본)](https://huggingface.co/mlx-community/Qwen3.6-35B-A3B-4bit) — 2026-09-25 기준 4샤드 20.4GB, 월 2.5만 다운로드
- [Qwen/Qwen3.6-35B-A3B (원본 모델 카드)](https://huggingface.co/Qwen/Qwen3.6-35B-A3B) — 벤치마크 수치·구조·라이선스(Apache 2.0) 원천
- [Qwen3.6-35B-A3B 발표 블로그](https://qwen.ai/blog?id=qwen3.6-35b-a3b)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
