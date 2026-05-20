---
title: "Qwen3.6-35B-A3B 오픈소스 공개: 오픈클로·클로드 코드에 로컬로 연결하기"
date: 2026-04-17
tags:
  - qwen
  - qwen3.6
  - openclaw
  - 오픈클로
  - claude-code
  - ollama
  - 로컬-llm
  - 오픈소스-llm
  - moe
  - 코딩-에이전트
  - macbook
  - 맥북-ai
description: "Qwen3.6-35B-A3B 오픈소스 모델을 Ollama로 로컬에서 돌리고, OpenClaw와 Claude Code에 연결하는 방법을 단계별로 안내합니다. API 비용 없이 내 컴퓨터에서 무료로 사용하세요."
---

> 원문: [Qwen Blog — Qwen3.6-35B-A3B](https://qwen.ai/blog?id=qwen3.6-35b-a3b)

<!-- Hidden SEO Keywords: Qwen3.6, Qwen 3.6, Qwen3.6-35B-A3B, Qwen3.6 Flash, 오픈클로 Qwen 로컬, openclaw qwen local, 클로드 코드 Qwen 로컬, claude code ollama, Qwen Ollama, Qwen 코딩, 오픈소스 LLM, MoE 모델, Mixture of Experts, 로컬 LLM, local LLM, 무료 AI, 무료 코딩 모델, 맥북 AI, macbook AI, Ollama 설치, 오픈클로 Ollama 설정, claude code ollama 설정, Qwen3.6 한국어, 오픈소스 코딩 에이전트 -->

2026년 4월 17일, 알리바바 클라우드가 **Qwen3.6-35B-A3B**를 오픈소스로 공개했습니다. 35B 파라미터 중 **단 3B만 활성화**하는 MoE 구조로, 코딩 성능은 자신보다 10배 큰 밀집(Dense) 모델과 맞먹습니다.

가장 좋은 점? **Ollama로 내 컴퓨터에서 로컬로 돌릴 수 있고, API 비용이 전혀 들지 않습니다.**

---

## 📌 핵심 요약

| 항목 | 내용 |
|------|------|
| **모델명** | Qwen3.6-35B-A3B |
| **구조** | MoE (35B total / 3B active) |
| **특징** | 에이전트 코딩 성능 대폭 향상, 멀티모달 지원 |
| **생각 모드** | Thinking / Non-Thinking 모드 지원 |
| **라이선스** | 오픈소스 (가중치 공개) |
| **로컬 실행** | Ollama, llama.cpp 지원 |
| **API 비용** | **무료** (로컬 실행 시) |

---

## 🧠 왜 주목해야 하나?

### 1. 작은 활성 파라미터, 큰 성능

- **35B 전체 파라미터 중 3B만 활성화** — 추론 속도와 메모리 효율이 매우 좋음
- 코딩 성능은 **Qwen3.5-27B, Gemma4-31B** 같은 더 큰 모델과 경쟁 수준
- 전작 Qwen3.5-35B-A3B 대비 에이전트 코딩 성능이 **대폭 향상**

### 2. 멀티모달 + 생각 모드

- **멀티모달 지원** — 이미지 인식과 추론 가능
- **Thinking 모드** — 복잡한 문제를 단계별로 사고
- **Non-Thinking 모드** — 빠른 응답이 필요할 때

### 3. 완전 무료

- Hugging Face, ModelScope에서 가중치 다운로드 가능
- Ollama로 로컬 실행 시 **API 비용 0원**
- **OpenClaw, Claude Code, Qwen Code와 공식 연동 지원**

---

## 🖥️ 1단계: Ollama 설치 & Qwen3.6 다운로드

### Ollama 설치

**macOS:**
```bash
# 공식 사이트에서 다운로드
brew install ollama
# 또는 https://ollama.com 에서 DMG 다운로드
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Ollama 공식 사이트에서 설치 파일 다운로드

### Qwen3.6 모델 다운로드

```bash
# MoE 35B (추천 — 3B만 활성화라 비교적 가벼움)
ollama pull qwen3.6:35b-a3b

# 더 가벼운 버전이 필요하면
ollama pull qwen3.6:14b
ollama pull qwen3.6:9b
```

### 확인

```bash
ollama list
# qwen3.6:35b-a3b  ~20GB

ollama run qwen3.6:35b-a3b "안녕, 한국어로 인사해줘"
```

---

## 🔗 2단계: OpenClaw에 로컬 Qwen3.6 연결

OpenClaw는 Ollama를 **번들 프로바이더**로 지원합니다. 별도 설정 없이 로컬에서 돌아가는 Qwen3.6을 사용할 수 있습니다.

### 방법 1: openclaw onboard (권장)

```bash
openclaw onboard --auth-choice ollama
```

온보딩 마법사에서 Ollama를 선택하면 자동으로 로컬 Ollama 서버를 감지하고 설정합니다.

### 방법 2: 설정 파일 직접 편집

`~/.openclaw/openclaw.json`을 열고 다음을 추가합니다.

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/qwen3.6:35b-a3b"
      }
    }
  },
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://127.0.0.1:11434/v1",
        "apiKey": "ollama-local"
      }
    }
  }
}
```

### 방법 3: 명령어 한 줄

```bash
openclaw config set agents.defaults.model.primary "ollama/qwen3.6:35b-a3b"
```

### 확인

```bash
# 게이트웨이 재시작
openclaw gateway restart

# 모델 확인
openclaw models list | grep qwen
```

### 💡 팁: MoE 모델 로컬 실행 시 필요 사양

| 모델 | 다운로드 용량 | 최소 RAM | 권장 사양 |
|------|-------------|----------|----------|
| qwen3.6:35b-a3b | ~20GB | 22GB RAM | 32GB RAM / M2 Pro 이상 |
| qwen3.6:14b | ~9GB | 16GB RAM | M1 MacBook Air 이상 |
| qwen3.6:9b | ~6GB | 8GB RAM | M1 MacBook Air 8GB |

> MoE 구조 덕분에 35B 모델도 **실제로는 3B만 GPU/CPU에서 연산**하므로 생각보다 가볍게 돌아갑니다.

---

## 🔗 3단계: Claude Code에 로컬 Qwen3.6 연결

Claude Code는 Anthropic API를 사용하지만, **Ollama의 OpenAI 호환 엔드포인트**를 가리키도록 설정하면 로컬 모델을 사용할 수 있습니다.

### 전제 조건

- Claude Code 설치 완료
- Ollama 실행 중이고 Qwen3.6 모델 다운로드 완료

### Claude Code 설치 (아직 안 했다면)

```bash
npm install -g @anthropic-ai/claude-code
```

### 환경변수 설정

```bash
# Claude Code가 Ollama 로컬 서버를 사용하도록 설정
export ANTHROPIC_BASE_URL="http://127.0.0.1:11434"
export ANTHROPIC_API_KEY="sk-no-key-required"
```

> **⚠️ 중요:** Claude Code가 Anthropic에 로그인하라고 하면, 더미 키를 사용하세요. 로컬 Ollama는 실제로 키를 검증하지 않습니다.

### 매번 설정하기 번거로우면 셸 프로파일에 추가

```bash
# ~/.zshrc (macOS) 또는 ~/.bashrc (Linux)
echo 'export ANTHROPIC_BASE_URL="http://127.0.0.1:11434"' >> ~/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-no-key-required"' >> ~/.zshrc
source ~/.zshrc
```

### Claude Code 첫 실행 시 로그인 건너뛰기

Claude Code가 처음 실행 시 Anthropic 로그인을 요구할 수 있습니다. `~/.claude.json`에 다음을 추가하세요:

```json
{
  "hasCompletedOnboarding": true,
  "primaryApiKey": "sk-dummy-key"
}
```

### VS Code에서 설정 (macOS 기준)

VS Code `settings.json`에 추가:

```json
{
  "terminal.integrated.env.osx": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:11434",
    "ANTHROPIC_API_KEY": "sk-no-key-required"
  }
}
```

### 실행

```bash
cd /path/to/your/project
claude --model qwen3.6:35b-a3b
```

Claude Code가 실행되면 **로컬 Qwen3.6**을 백엔드로 사용합니다. 기존 Claude Code의 에이전트 워크플로우 — 파일 편집, 터미널 접근, 코드 생성 — 모두 그대로 동작합니다.

> **💡 팁:** KV 캐시 무효화 방지를 위해 환경변수 `CLAUDE_CODE_ATTRIBUTION_HEADER=0`를 설정하면 추론 속도가 더 빨라집니다.

---

## 🔧 트러블슈팅

### "Unable to connect to API (ConnectionRefused)"

Ollama가 실행 중인지 확인하세요:

```bash
ollama list
# 목록이 비어 있으면 Ollama 서버를 시작하세요
```

### Claude Code가 계속 로그인을 요구

```bash
# 로컬로 되돌릴 때
unset ANTHROPIC_BASE_URL
unset ANTHROPIC_API_KEY
```

### 응답이 비어 있다 (빈 결과)

Qwen 모델을 사용할 때 `reasoning` 모드를 끄세요. OpenClaw 설정에서:

```json
{ "reasoning": false }
```

### 모델이 너무 느리다

더 작은 양자화(Quantized) 버전을 사용해보세요:

```bash
ollama pull qwen3.6:35b-a3b-q4_K_M
```

---

## 💰 로컬 vs API 비교

| 구성 | 비용 | 장점 | 단점 |
|------|------|------|------|
| Claude Code + Claude Opus | 💰💰💰 높음 | 최고 품질 | 비용 부담 |
| Claude Code + Qwen3.6 API | 💰 낮음 | 클라우드 인프라 | 데이터 전송 |
| **Claude Code + Qwen3.6 로컬** | **🆓 무료** | 비용 0원, 프라이버시 보장 | 로컬 하드웨어 필요 |
| **OpenClaw + Qwen3.6 로컬** | **🆓 무료** | 플러그인·스킬 생태계, 다중 플랫폼 | 로컬 하드웨어 필요 |

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1. MacBook Air 8GB에서도 돌아가나요?

`qwen3.6:9b`라면 가능합니다. 35B-A3B 모델은 최소 22GB RAM이 필요하므로 16GB 이상의 MacBook에서 사용하는 것을 권장합니다.

### Q2. 로컬에서 돌리면 인터넷 연결이 필요 없나요?

모델 다운로드까지만 인터넷이 필요합니다. 그 이후에는 **완전 오프라인**으로 동작합니다.

### Q3. Claude Code의 어떤 기능이 로컬 모델에서 제한되나요?

Anthropic 전용 기능(extended thinking, Claude 특유의 agentic 기능 일부)은 제한됩니다. 하지만 기본적인 파일 편집, 터미널 명령 실행, 코드 생성은 모두 정상 동작합니다.

### Q4. OpenClaw에서 Ollama 외에 llama.cpp도 쓸 수 있나요?

네. llama.cpp 서버를 띄우고 baseUrl만 변경하면 됩니다:

```json
{
  "models": {
    "providers": {
      "llamacpp": {
        "baseUrl": "http://127.0.0.1:8001/v1",
        "apiKey": "sk-no-key"
      }
    }
  }
}
```

### Q5. Thinking 모드와 Non-Thinking 모드는 언제 쓰나요?

- **Thinking 모드:** 복잡한 코딩, 수학, 다단계 추론이 필요할 때
- **Non-Thinking 모드:** 빠른 응답이 중요한 대화, 간단한 질문 답변

---

## 📌 결론

Qwen3.6-35B-A3B를 **Ollama로 로컬에서 실행**하면 API 비용 없이 Claude Code나 OpenClaw의 강력한 에이전트 기능을 사용할 수 있습니다. Claude Code의 **에이전트 코딩 워크플로우**를 Qwen의 **무료 로컬 추론**과 결합하면, 비용 대비 효율이 극적으로 좋아집니다.

초기 설정만 5분이면 끝납니다. 지금 바로 시도해보세요.

---

*원문: [Qwen Blog — Qwen3.6-35B-A3B](https://qwen.ai/blog?id=qwen3.6-35b-a3b)*
*Ollama: [ollama.com](https://ollama.com)*
*OpenClaw 문서: [docs.openclaw.ai](https://docs.openclaw.ai/providers/ollama)*
*Claude Code: [claude.ai/code](https://claude.ai/code)*
