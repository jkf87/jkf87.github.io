---
title: "Qwen3.6-35B-A3B 오픈소스 공개: 오픈클로·클로드 코드 연결 방법까지"
date: 2026-04-17
tags:
  - qwen
  - qwen3.6
  - openclaw
  - 오픈클로
  - claude-code
  - 오픈소스-llm
  - moe
  - alibaba
  - 코딩-에이전트
  - 업무자동화
  - ai-모델
description: "Qwen3.6-35B-A3B 오픈소스 모델 핵심 정리. 35B 파라미터 중 3B만 활성화하는 MoE 구조로 코딩 성능이 대형 모델 맞먹는다. OpenClaw와 Claude Code에 연결하는 방법을 단계별로 안내합니다."
---

> 원문: [Qwen Blog — Qwen3.6-35B-A3B](https://qwen.ai/blog?id=qwen3.6-35b-a3b)

<!-- Hidden SEO Keywords: Qwen3.6, Qwen 3.6, Qwen3.6-35B-A3B, Qwen3.6 Flash, 오픈클로 Qwen, openclaw qwen, 클로드 코드 Qwen, claude code qwen, Qwen 코딩, Qwen coding, 오픈소스 LLM, MoE 모델, Mixture of Experts, 알리바바 AI, Alibaba Cloud, DashScope, Qwen Studio, 오픈클로 설정, openclaw setup, Claude Code 설정, Qwen API, 무료 코딩 모델, Qwen3.6 한국어, openclaw qwen 연결, claude code qwen 연결 -->

2026년 4월 17일, 알리바바 클라우드가 **Qwen3.6-35B-A3B**를 오픈소스로 공개했습니다. 35B 파라미터 중 **단 3B만 활성화**하는 희소 Mixture-of-Experts (MoE) 구조로, 코딩 성능은 자신보다 10배 큰 밀집(Dense) 모델과 맞먹는다고 합니다.

---

## 📌 핵심 요약

| 항목 | 내용 |
|------|------|
| **모델명** | Qwen3.6-35B-A3B |
| **구조** | MoE (35B total / 3B active) |
| **특징** | 에이전트 코딩 성능 대폭 향상, 멀티모달 지원 |
| **생각 모드** | Thinking / Non-Thinking 모드 지원 |
| **라이선스** | 오픈소스 (가중치 공개) |
| **API** | Alibaba Cloud Model Studio (`qwen3.6-flash`) |

---

## 🧠 왜 주목해야 하나?

### 1. 작은 활성 파라미터, 큰 성능

- **35B 전체 파라미터 중 3B만 활성화** — 추론 속도와 메모리 효율이 매우 좋음
- 코딩 성능은 **Qwen3.5-27B, Gemma4-31B** 같은 더 큰 모델과 경쟁 수준
- 전작 Qwen3.5-35B-A3B 대비 에이전트 코딩 성능이 **대폭 향상**

### 2. 멀티모달 + 생각 모드

- **멀티모달 지원** — 이미지 인식과 추론 가능
- **Thinking 모드** — 복잡한 문제를 단계별로 사고하는 모드
- **Non-Thinking 모드** — 빠른 응답이 필요할 때 사용

### 3. 오픈소스 + API 병행

- Hugging Face, ModelScope에서 가중치 다운로드 가능
- Alibaba Cloud Model Studio에서 API로도 사용 가능 (`qwen3.6-flash`)
- **OpenClaw, Claude Code, Qwen Code와 공식 연동 지원**

---

## 🔗 OpenClaw에 Qwen3.6 연결하기

OpenClaw는 Qwen Cloud를 **번들 프로바이더**로 지원합니다. Alibaba Cloud Model Studio API를 통해 연결할 수 있습니다.

### 전제 조건

- OpenClaw 설치 완료
- Alibaba Cloud Model Studio 계정 + API 키 발급

### 방법 1: `openclaw onboard` 사용

```bash
openclaw onboard
```

온보딩 마법사에서 **Qwen Cloud**를 제공자로 선택하고, 발급받은 API 키를 입력합니다.

### 방법 2: 설정 파일 직접 편집

`~/.openclaw/openclaw.json`을 열고 다음을 추가합니다.

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "qwen/qwen3.6-flash"
      }
    }
  },
  "models": {
    "providers": {
      "qwen": {
        "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "apiKey": "sk-본인의_DASHSCOPE_API_키"
      }
    }
  }
}
```

> **⚠️ 중요:** Qwen 모델 사용 시 `"reasoning": false`로 설정하세요. `true`로 두면 응답이 비어 있습니다.

### 리전별 Base URL

| 리전 | Base URL |
|------|----------|
| 중국 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 싱가포르 | `https://dashscope-intl.aliyuncs.com/api/v2/apps/claude-code-proxy` |
| 기타 | [Alibaba Cloud 문서](https://www.alibabacloud.com/help/en/model-studio/openclaw) 참고 |

### 모델 확인

```bash
# 게이트웨이 재시작
openclaw gateway restart

# 모델 확인
openclaw models list | grep qwen
```

---

## 🔗 Claude Code에 Qwen3.6 연결하기

Claude Code는 Anthropic API 인터페이스를 사용하는데, Qwen은 **Claude Code Proxy**를 통해 Anthropic 호환 API를 제공합니다. 이를 이용하면 Claude Code UI로 Qwen 모델을 사용할 수 있습니다.

### 전제 조건

- Claude Code 설치 완료
- Alibaba Cloud DashScope API 키 발급

### 설정 방법

터미널에서 환경변수를 설정합니다:

```bash
# Claude Code가 Qwen 프록시를 사용하도록 설정
export ANTHROPIC_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v2/apps/claude-code-proxy"
export ANTHROPIC_AUTH_TOKEN="sk-본인의_DASHSCOPE_API_키"
```

매번 입력하기 번거로우면 셸 프로파일에 추가하세요:

```bash
# ~/.zshrc (macOS) 또는 ~/.bashrc (Linux)
echo 'export ANTHROPIC_BASE_URL="https://dashscope-intl.aliyuncs.com/api/v2/apps/claude-code-proxy"' >> ~/.zshrc
echo 'export ANTHROPIC_AUTH_TOKEN="sk-본인의_DASHSCOPE_API_키"' >> ~/.zshrc
source ~/.zshrc
```

### 실행

```bash
claude
```

Claude Code가 실행되면 **Qwen3.6-Flash**를 백엔드 모델로 사용합니다. 기존 Claude Code의 에이전트 워크플로우, 파일 편집, 터미널 접근 등 모든 기능을 그대로 사용할 수 있습니다.

### VS Code에서 설정 (macOS 기준)

VS Code `settings.json`에 추가:

```json
{
  "terminal.integrated.env.osx": {
    "ANTHROPIC_BASE_URL": "https://dashscope-intl.aliyuncs.com/api/v2/apps/claude-code-proxy",
    "ANTHROPIC_AUTH_TOKEN": "sk-본인의_DASHSCOPE_API_키"
  }
}
```

---

## 💰 비용 비교

| 구성 | 비용 | 장점 |
|------|------|------|
| Claude Code + Claude Sonnet | 높음 | 최고 품질, 공식 지원 |
| Claude Code + Qwen3.6 Flash | 매우 낮음 (무료 크레딧 활용 가능) | 90% 성능, 최소 비용 |
| OpenClaw + Qwen3.6 Flash | 매우 낮음 | 다양한 플랫폼 연동, 스킬 생태계 |

Claude Code의 강력한 **에이전트 코딩 워크플로우**를 Qwen의 **저렴한 추론 비용**과 결합하면, 비용 대비 효율이 극적으로 좋아집니다.

---

## 📥 자체 호스팅 (Ollama)

GPU가 있다면 Ollama로 자체 호스팅도 가능합니다:

```bash
# Ollama 설치 후
ollama pull qwen3.6:35b-a3b

# OpenClaw에서 Ollama 모델 사용
openclaw onboard --auth-choice ollama
```

자체 호스팅 시 API 비용이 전혀 발생하지 않지만, MoE 모델 구조상 **35B 전체 파라미터를 메모리에 올려야 하므로** 최소 24GB VRAM이 권장됩니다.

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1. Qwen3.6-35B-A3B은 어떤 언어를 지원하나요?

한국어를 포함한 다국어를 지원합니다. 특히 코딩과 멀티모달 추론에 강점이 있습니다.

### Q2. API 비용은 얼마나 하나요?

Alibaba Cloud Model Studio에서 신규 가입 시 무료 크레딧이 제공됩니다. 이후 종량과금 체계로 매우 저렴하게 사용할 수 있습니다.

### Q3. Claude Code에서 Qwen을 쓰면 기능 제한이 있나요?

Claude Code의 UI와 워크플로우는 그대로 사용할 수 있습니다. 다만 Anthropic 전용 기능(extended thinking 등)은 사용할 수 없습니다.

### Q4. OpenClaw에서 여러 모델을 동시에 사용할 수 있나요?

네. `qwen/qwen3.6-flash`, `anthropic/opus`, `google/gemini` 등 여러 프로바이더를 동시에 설정하고 상황에 맞게 전환할 수 있습니다.

### Q5. Thinking 모드와 Non-Thinking 모드는 언제 쓰나요?

- **Thinking 모드:** 복잡한 코딩, 수학, 다단계 추론이 필요할 때
- **Non-Thinking 모드:** 빠른 응답이 중요한 대화, 간단한 질문 답변

---

## 📌 결론

Qwen3.6-35B-A3B는 **효율성과 성능의 균형**을 잘 잡은 오픈소스 모델입니다. 3B 활성 파라미터로 대형 모델급 성능을 내면서도, OpenClaw와 Claude Code 같은 강력한 에이전트 도구와 공식 연동됩니다.

Claude Code의 에이전트 코딩 워크플로우를 무료에 가까운 비용으로 경험하고 싶다면, Qwen3.6 + Claude Code 조합을 강력히 추천합니다.

---

*원문: [Qwen Blog — Qwen3.6-35B-A3B](https://qwen.ai/blog?id=qwen3.6-35b-a3b)*
*Hugging Face: [Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B)*
*Alibaba Cloud Model Studio: [모델 스튜디오](https://www.alibabacloud.com/help/en/model-studio/openclaw)*
