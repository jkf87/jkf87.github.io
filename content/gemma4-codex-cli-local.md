---
title: "Gemma 4를 Codex CLI에서 로컬로 실행하기 — 실제 벤치마크 결과"
date: 2026-04-15
tags:
  - gemma
  - codex-cli
  - local-llm
  - apple-silicon
  - ai-coding
description: "Google Gemma 4의 툴 콜링 성능이 86.4%까지 올라오면서, OpenAI Codex CLI에서 로컬 에이전트 코딩이 처음으로 현실이 되었습니다. Apple Silicon 24GB와 NVIDIA Blackwell 128GB 두 환경에서 직접 테스트한 설정법과 벤치마크를 정리합니다."
---

## 왜 지금인가?

로컬 모델로 에이전트 코딩을 하려면 **툴 콜링(tool calling)**이 필수입니다. Codex CLI가 파일을 읽고, 코드를 쓰고, 테스트를 실행하고, 패치를 적용하려면 모델이 `{"tool": "Read", "args": {"file": "package.json"}}` 같은 구조화된 출력을 **안정적으로** 내야 합니다.

이전 세대인 Gemma 3은 tau2-bench function-calling 벤치마크에서 **6.6%**였습니다. 100번 시도 중 93번이 실패 — 에이전트 코딩의 기초로는 전혀 쓸 수 없는 수준이었습니다.

Gemma 4 31B는 같은 벤치마크에서 **86.4%**를 기록했습니다. 이 한 줄 차이가 "불가능"에서 "현실"로 바꿉니다.

## 테스트 환경

Daniel Vaughan(Google Cloud)이 2026년 4월 12일에 진행한 실측 벤치마크를 기준으로 합니다.

| 항목 | Mac (Apple Silicon) | PC (NVIDIA) | Cloud |
|------|-------------------|-------------|-------|
| 기기 | 24GB M4 Pro MacBook Pro | Dell Pro Max GB10 (128GB) | — |
| GPU/칩 | Apple M4 Pro | NVIDIA Blackwell | — |
| 모델 | Gemma 4 26B MoE | Gemma 4 31B Dense | GPT-5.4 |
| 양자화 | Q4_K_M (GGUF) | Q4_K_M (GGUF) | — |
| 런타임 | llama.cpp | Ollama v0.20.5 | OpenAI API |
| 컨텍스트 | 32,768 | 32,768 | 기본 |

## 설정 방법

### Apple Silicon (Mac)

Mac에서는 **Ollama를 피하고 llama.cpp를 사용**해야 합니다. Ollama에는 Apple Silicon에서 Gemma 4 스트리밍을 깨트리는 버그가 있습니다.

**1. llama.cpp 빌드**

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make
```

**2. GGUF 모델 다운로드**

```bash
# 예: Q4_K_M 양자화 (24GB RAM 기준)
wget https://huggingface.co/google/gemma-4-26B-A4B-it-GGUF/resolve/main/gemma-4-26b-a4b-it-Q4_K_M.gguf
```

**3. 서버 실행**

```bash
./llama-server \
  -m gemma-4-26b-a4b-it-Q4_K_M.gguf \
  -c 32768 \
  --jinja \
  -ctk q8_0 -ctv q8_0
```

핵심 옵션:
- `--jinja`: Gemma 4의 템플릿 렌더링에 필수
- `-c 32768`: Codex CLI 시스템 프롬프트가 최소 27,000 토큰 필요
- `-ctk q8_0 -ctv q8_0`: KV 캐시 양자화로 메모리 절약

### NVIDIA (Windows/Linux)

NVIDIA에서는 Ollama가 잘 동작합니다.

**1. Ollama 설치 및 모델 다운로드**

```bash
# Ollama v0.20.5 이상 필요
ollama pull gemma4:31b
```

**2. 원격 접속 시 SSH 터널링**

Codex CLI의 `--oss` 모드는 localhost만 확인하므로, 원격 GPU 서버를 쓸 때는 터널링이 필요합니다.

```bash
ssh -L 11434:localhost:11434 user@gpu-server
```

**3. Codex CLI 실행**

```bash
codex --oss -m gemma4:31b
```

### Codex CLI 프로필 설정

두 환경 공통으로 `config.toml`에 커스텀 프로바이더를 등록합니다.

```toml
[providers.local]
wire_api = "responses"
# Mac (llama.cpp): localhost:8001
# NVIDIA (Ollama): localhost:11434
```

**⚠️ 반드시 설정해야 할 것:**

```toml
stream_idle_timeout_ms = 1800000
web_search = "disabled"
```

Mac에서 단일 툴 콜 사이클에 **1분 39초**가 걸렸습니다. 기본 타임아웃은 세션을 종료시켜 버리므로 최소 1,800,000ms (30분)로 설정하세요.

## 벤치마크 결과

동일한 태스크를 세 환경에서 실행: `codex exec --full-auto`로 `parse_csv_summary` Python 함수 작성 + 에러 핸들링 + 테스트 작성/실행.

### 토큰 생성 속도

| 환경 | 속도 |
|------|------|
| **Mac (26B MoE)** | **52 tok/s** |
| PC (31B Dense) | 10 tok/s |
| Cloud | — (API) |

Mac이 PC보다 **5.1배 빠릅니다**. 두 기기 모두 273 GB/s LPDDR5X 메모리 대역폭인데 왜 이런 차이가?

**MoE(Mixture of Experts) 아키텍처 때문입니다.** 토큰 생성은 메모리 대역폭에 병목됩니다. 31B Dense는 매 토큰마다 312억 개 파라미터를 전부 읽어야 하고, 26B MoE는 **38억 개**만 활성화합니다. 같은 파이프라인에 넣는 페이로드가 9배 다르니 속도 차이는 당연합니다.

### 코드 품질

| 항목 | Mac (26B MoE) | PC (31B Dense) | Cloud (GPT-5.4) |
|------|--------------|----------------|-----------------|
| 툴 콜 수 | 10회 | 3회 | — |
| 실패한 재시도 | 5회 | 0회 | 0회 |
| 데드 코드 | 있음 | 없음 | 없음 |
| 테스트 통과 | ✅ | ✅ | ✅ |
| 완료 시간 | 가장 느림 | 중간 | **65초** |

**핵심 발견:** 에이전트 코딩에서는 **모델 품질이 토큰 속도보다 중요합니다.** 한 번에 맞히는 모델이 빠르게 반복하며 수정하는 모델보다 낫습니다. 31B Dense는 3번의 툴 콜로 완성했고, 26B MoE는 10번의 시도 끝에 데드 코드까지 남겼습니다.

## 실무 팁

### 버전 고정

llama.cpp 빌드 간 **3.3배 속도 회귀**가 보고된 적이 있습니다. 안정적인 버전을 찾으면 핀(pin)하세요.

### 하이브리드 워크플로

```
codex --profile local  # 반복 작업, 프라이버시 민감 작업
codex                   # 복잡한 작업 (기본 클라우드)
```

Codex CLI의 프로필 시스템을 활용하면 플래그 하나로 전환할 수 있습니다.

### 컨텍스트 길이

Ollama를 쓸 때 기본 컨텍스트가 짧을 수 있습니다. 환경변수로 늘리세요:

```bash
OLLAMA_CONTEXT_LENGTH=64000 ollama serve
```

또는 Ollama 앱 설정에서 직접 조정합니다.

## 결론

> **로컬 Gemma 4는 동작합니다.** 이것이 새로운 것입니다.

| 관점 | 평가 |
|------|------|
| 가능성 | ✅ 양쪽 모두 작동하는 코드 + 통과하는 테스트 생성 |
| 품질 | ⚠️ 클라우드 모델에는 미치지 못함 |
| 속도 | ⚠️ Mac MoE는 빠르지만 재시도가 많음 |
| 비용 | ✅ 토큰 비용 0원, 코드 누출 없음 |
| 추천 | ✅ 프라이버시/반복 작업에 적합 |

Gemma 3→4의 툴 콜링 점프(6.6% → 86.4%)가 "고장"에서 "작동"으로의 간극을 메웠습니다. 클라우드 모델의 대체가 아니라, **프라이버시가 중요하거나 빠른 반복이 필요한 작업**에 현실적인 선택지가 생긴 것입니다.

---

## FAQ

### Q. 24GB Mac에서 Gemma 4를 돌릴 수 있나요?

네. 26B MoE(Mixture of Experts) 변종은 활성 파라미터가 38억 개이므로 Q4 양자화 시 약 1.9GB만 메모리에 올립니다. llama.cpp로 실행하면 52 tok/s로 실용적인 속도가 나옵니다.

### Q. Ollama로 하면 안 되나요?

NVIDIA에서는 Ollama v0.20.5가 잘 동작합니다. 하지만 **Apple Silicon에서는 Ollama에 Gemma 4 스트리밍 버그**가 있어 llama.cpp를 써야 합니다.

### Q. Codex CLI 없이 다른 에이전트에서도 쓸 수 있나요?

네. Claude Code CLI(`ollama launch claude --model gemma4:26b`), LM Studio의 headless CLI, llama.cpp 서버 등 다양한 환경에서 Gemma 4를 로컬로 실행할 수 있습니다. 핵심은 컨텍스트 길이를 충분히 확보(32K 이상)하는 것입니다.

### Q. 언제 클라우드를 쓰고 언제 로컬을 쓰나요?

단순 반복 작업, 프라이버시가 중요한 프로젝트, 인터넷 연결이 불안정한 환경에서는 로컬. 복잡한 아키텍처 설계, 대규모 리팩토링, 정밀한 코드 생성에는 클라우드(GPT-5.4 등)를 추천합니다.

---

**출처:**
- [I ran Gemma 4 as a local model in Codex CLI](https://medium.com/google-cloud/i-ran-gemma-4-as-a-local-model-in-codex-cli-7fda754dc0d4) — Daniel Vaughan, Google Cloud Community, 2026-04
- [Gemma 4 Local Agentic Coding Benchmarks (GitHub Gist)](https://gist.github.com/danielvaughan/9c414ce1b49b1940dfc87bb9d7534a55)
- [Gemma 4: Our most capable open models to date](https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/) — Google Blog
