---
title: "Gemma 4를 OpenClaw에 붙이려면, LM Studio부터 해야 하는 이유와 실제 설정 순서"
date: 2026-04-07
tags:
  - gemma4
  - openclaw
  - lm-studio
  - unsloth
  - local-llm
  - ai-assistant
  - macbook-air-m4
  - workflow
description: "Gemma 4를 LM Studio나 Unsloth에서 실행한 뒤 OpenClaw에 연결하는 실전 가이드. LM Studio Headless CLI, OpenAI/Anthropic 호환 엔드포인트, llama-server 경로, M4 32GB 안정성 기준까지 실제 따라할 수 있게 정리했다."
---

# Gemma 4를 OpenClaw에 붙이려면, LM Studio부터 해야 하는 이유와 실제 설정 순서

이 글은 **Gemma 4를 로컬에서 실행하고, 그 모델을 OpenClaw의 백엔드로 붙이는 방법**을 정리한 실전 문서다.

핵심만 먼저 적겠다.

- **첫 실험은 LM Studio로 가는 게 맞다.**
- **Unsloth는 두 번째 실험 경로다.**
- **MacBook Air M4 32GB에서는 26B-A4B 4bit 계열부터 보는 게 안전하다.**
- **이 글은 “될 것 같다”가 아니라 실제로 어디를 확인하고, 어디서 막히는지 중심으로 쓴다.**

## 1. 왜 이 글을 다시 쓰는가

기존에는 “Gemma 4를 OpenClaw에 붙일 수 있나”를 개념적으로 정리하는 수준이었다. 그런데 그걸로는 부족하다.

실제로 필요한 건 이거다.

1. **LM Studio와 OpenClaw가 어떤 API로 붙는지**
2. **Unsloth는 왜 Studio UI가 아니라 llama-server 경로를 봐야 하는지**
3. **M4 Air 32GB에서 어느 모델부터 시작해야 덜 망하는지**
4. **처음에 뭘 확인해야 시간 낭비를 줄일 수 있는지**

이 글은 그 네 가지를 해결하는 문서다.

## 2. 이번에 참고한 추가 자료에서 얻은 핵심

### 자료 1. LM Studio Headless CLI + Gemma 4
GeekNews 정리 글을 보면, LM Studio 0.4.0 이후 `llmster`와 `lms` CLI 덕분에 **GUI 없이도 모델 다운로드, 로드, 서버 실행, API 노출**이 가능해졌다.

여기서 중요한 건 세 가지다.

1. **Gemma 4 26B-A4B는 MoE 구조라 로컬에서 훨씬 현실적이다.**
2. **LM Studio는 OpenAI 호환 `/v1`뿐 아니라 Anthropic 호환 `/v1/messages`도 지원한다.**
3. **Claude Code와 붙이는 예시가 이미 문서화돼 있어서, OpenClaw도 같은 API 관점으로 접근 가능하다.**

즉,

> LM Studio는 단순 로컬 채팅 앱이 아니라, **Gemma 4를 외부 도구에 제공하는 서버 레이어**로 볼 수 있다.

### 자료 2. Mac mini + Gemma 4 운영 요약
두 번째 GeekNews 글은 Ollama 중심이지만, 여기서도 가져갈 포인트가 있었다.

핵심은 이거다.

- 로컬 LLM은 “모델이 돌아가냐”만 보면 안 된다.
- **자동 실행**, **메모리 유지**, **API 엔드포인트 지속성**, **재부팅 후 복구**까지 봐야 한다.

이건 LM Studio나 Unsloth에도 그대로 적용된다.

즉,

> OpenClaw에 붙이는 순간부터는 모델이 “실험용 앱”이 아니라 **상시 백엔드**가 된다.

그래서 이번 글도 단순 설치보다 **운영 가능성** 관점으로 쓴다.

## 3. 결론 먼저, 어떤 경로가 맞나

### 1순위
**LM Studio + Gemma 4 + OpenClaw**

왜냐하면:
- 문서 근거가 가장 많고
- `/v1/models`로 상태 확인이 쉽고
- OpenClaw 공식 문서가 LM Studio 경로를 사실상 권장하고
- OpenAI/Anthropic 호환 API를 둘 다 제공하니까

### 2순위
**Unsloth + llama-server + OpenClaw**

왜냐하면:
- Unsloth는 모델 실험성은 좋지만
- OpenClaw가 직접 보는 건 결국 Unsloth Studio가 아니라 **OpenAI 호환 서버**이기 때문이다

이 두 문장을 기억하면 된다.

> **연결 성공이 목표면 LM Studio**
> **성능/양자화/추론 실험이 목표면 Unsloth**

## 4. 모델 선택부터 잘해야 한다

MacBook Air M4 32GB에서 가장 많이 하는 실수가
**처음부터 너무 무거운 모델/양자화로 들어가는 것**이다.

### 추천 시작점
- **Gemma 4 26B-A4B 4bit 계열**

이유:
- 31B 8bit는 사실상 무리
- 26B-A4B는 MoE 구조라 훨씬 현실적
- 로컬 백엔드 첫 연결 테스트로 적절함

### 하지 말 것
- 31B 8bit를 첫 시도로 잡기
- 컨텍스트를 처음부터 과하게 키우기
- LM Studio/Unsloth UI에서 보이는 이름만 믿고 OpenClaw config에 그대로 적기

## 5. LM Studio 경로, 실제 설정 순서

### Step 1. LM Studio에서 모델을 로드한다
Gemma 4를 로드한다.

GUI를 써도 되고, Headless CLI를 써도 된다.

중요한 건 **모델이 메모리에 올라간 상태**여야 한다는 점이다.

### Step 2. Local Server를 켠다
기본 주소는 보통 아래다.

```bash
http://127.0.0.1:1234
```

여기서 가장 먼저 해야 할 건 이 명령이다.

```bash
curl http://127.0.0.1:1234/v1/models
```

#### 이 단계에서 확인할 것
- 서버가 살아 있는가
- 모델 목록이 JSON으로 보이는가
- 모델 ID가 무엇인가

#### 왜 이게 중요하냐
OpenClaw 설정 전에 이걸 확인하지 않으면,
나중에 문제 원인이
- 서버 문제인지
- 모델 문제인지
- config 문제인지
구분이 안 된다.

### Step 3. 모델 ID를 정확히 복사한다
OpenClaw 설정에서 가장 많이 틀리는 지점이다.

문서 예시에는 `my-local-model` 같은 값이 나오지만,
그건 **설명용 placeholder**일 뿐이다.

반드시:
- `/v1/models` 결과에 나오는
- **실제 모델 ID**를
- 그대로 써야 한다

이걸 틀리면 거의 무조건 안 붙는다.

### Step 4. OpenClaw에 provider를 추가한다
예시는 이렇게 잡으면 된다.

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "lmstudio/my-local-model" },
      "models": {
        "lmstudio/my-local-model": { "alias": "Local Gemma4" }
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "lmstudio": {
        "baseUrl": "http://127.0.0.1:1234/v1",
        "apiKey": "lmstudio",
        "api": "openai-responses",
        "models": [
          {
            "id": "my-local-model",
            "name": "Gemma 4 Local",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 32768,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

#### 여기서 반드시 바꿔야 하는 것
- `my-local-model` → 실제 모델 ID
- 필요하면 `contextWindow` → 처음엔 32K 전후
- 필요하면 `maxTokens` → 너무 크게 잡지 말 것

### Step 5. 왜 `openai-responses`를 먼저 보나
OpenClaw 문서상 로컬 모델 연결에서 **Responses API**를 먼저 보라고 하는 이유는,
추론 출력과 최종 답변을 더 깔끔하게 다루기 쉽기 때문이다.

특히 Gemma 4처럼 thinking/추론 모드가 얽히면,
이 부분이 채널 출력 품질에 영향을 준다.

그래서 첫 실험은 아래 우선순위가 좋다.

1. `openai-responses`
2. 안 맞으면 `chat/completions` 계열 비교

### Step 6. 왜 `models.mode: "merge"`가 중요하나
이건 빼먹지 말자.

`merge`를 써야
- 로컬 모델과 hosted 모델을 같이 관리할 수 있고
- 실패 시 fallback 설계가 가능하다

즉,
**로컬 모델 실험을 하더라도 탈출구를 남겨두는 설정**이다.

## 6. 처음 테스트는 이렇게 해야 한다

처음부터 긴 대화, 긴 문서 처리, 복잡한 도구 호출을 하지 말자.

### 테스트 1. 한 줄 응답
- 자기소개
- 간단한 번역

### 테스트 2. 한국어 품질
- 블로그 제목 5개
- 초등 수업 아이디어 3개

### 테스트 3. 2~3턴 맥락 유지
- 앞 질문 기억하는지

### 테스트 4. 아주 짧은 실무형 요청
- 메일 초안 5줄
- 회의 요약 5줄

이 단계에서 확인할 건 네 가지다.

1. **응답이 오는가**
2. **한국어가 무너지지 않는가**
3. **시스템이 멈추지 않는가**
4. **thinking 출력이 그대로 새지 않는가**

## 7. Unsloth 경로는 어떻게 이해해야 하나

여기서 가장 중요한 오해 하나를 정리하자.

> **OpenClaw는 Unsloth Studio UI에 붙는 게 아니다.**
> **OpenClaw는 OpenAI 호환 API 서버에 붙는다.**

그래서 실제 구조는 이렇다.

```text
Unsloth 모델
→ llama.cpp / llama-server
→ /v1 API
→ OpenClaw
```

즉, Unsloth를 OpenClaw에 붙이는 핵심은
**Studio가 아니라 llama-server**다.

## 8. Unsloth 경로, 실제 순서

### Step 1. Gemma 4 GGUF 준비
양자화 모델 준비

### Step 2. llama-server 실행
예시:

```bash
./llama-server \
  --model /path/to/gemma4.gguf \
  --alias gemma4-local \
  --port 8001
```

필요하면 thinking 옵션을 같이 준다.

### Step 3. 서버 확인

```bash
curl http://127.0.0.1:8001/v1/models
```

여기서 모델이 보여야 한다.

### Step 4. OpenClaw provider 설정

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "local": {
        "baseUrl": "http://127.0.0.1:8001/v1",
        "apiKey": "sk-local",
        "api": "openai-responses",
        "models": [
          {
            "id": "gemma4-local",
            "name": "Gemma 4 via llama-server",
            "reasoning": false,
            "input": ["text"],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 32768,
            "maxTokens": 4096
          }
        ]
      }
    }
  }
}
```

핵심은:
- 포트 맞추기
- 모델 ID 맞추기
- `/v1/models`로 먼저 검증하기

## 9. 가장 흔한 실패 원인

### 1. 모델 ID 틀림
문서 예시를 그대로 쓰면 안 된다.

### 2. 모델은 안 로드됐는데 서버만 살아 있음
LM Studio에서 자주 생긴다.

### 3. 컨텍스트를 너무 크게 잡음
M4 Air 32GB에서는 KV cache 때문에 금방 무거워질 수 있다.

#### 권장
- 처음엔 **32K 전후**로 시작
- 안정성 확인 후 늘리기

### 4. 31B 8bit 욕심
거의 바로 무너질 가능성이 높다.

### 5. thinking 출력이 그대로 노출됨
채널 응답 품질이 깨질 수 있다.

## 10. 운영 관점에서 꼭 봐야 할 것

GeekNews의 Mac mini + Gemma 4 운영 글이 던지는 핵심은 이거였다.

> 로컬 LLM은 “한 번 돌아간다”로 끝나지 않는다.
> **재부팅 후에도 다시 올라오고, 메모리에 유지되고, API가 안정적으로 살아 있어야 한다.**

이건 OpenClaw에 붙이는 순간 더 중요해진다.

왜냐하면 이제 모델은
- 실험용 채팅 앱이 아니라
- **실제 비서 백엔드**가 되기 때문이다.

그래서 다음 단계에선 반드시 확인해야 한다.

1. 부팅 후 자동 실행
2. 모델 자동 로드
3. 일정 시간 idle 후 언로드 정책
4. API 포트 지속성
5. 장애 시 fallback 동작

이건 다음 글에서 다루면 좋다.

## 11. 이 글 기준으로 진짜 추천하는 실험 순서

1. **LM Studio + Gemma 4 26B-A4B 로드**
2. `curl http://127.0.0.1:1234/v1/models` 확인
3. OpenClaw provider 추가
4. 짧은 한국어 응답 테스트
5. 2~3턴 유지 확인
6. 컨텍스트 32K에서 안정성 확인
7. 그 다음 Unsloth + llama-server 비교

이 순서가 좋은 이유는,
문제 원인을 가장 쉽게 분리할 수 있기 때문이다.

## 12. 아직 더 조사해야 할 부분

있다. 그리고 이건 실제 완성판 글 전에 더 확인해야 한다.

1. Gemma 4 thinking 출력이 OpenClaw 채널 응답에서 얼마나 깔끔하게 정리되는가
2. LM Studio에서 `responses`와 `chat/completions` 중 어느 쪽이 더 안정적인가
3. Unsloth Studio와 llama-server 사이 역할 구분을 더 명확히 할 수 있는가
4. M4 Air 32GB에서 16K / 32K / 48K의 실제 한계가 어디인가
5. 로컬 백엔드를 비서처럼 계속 켜둘 때 idle/unload 전략이 어떻게 잡히는가

즉,
이 글은 지금 기준으로 **가장 현실적인 출발 문서**고,
완성판은 반드시 **실제 연결 로그와 운영 결과**를 붙여야 한다.

## 13. 결론

이 시점에서 결론은 단순하다.

> **Gemma 4를 OpenClaw에 붙여보는 첫 실험은 LM Studio로 해야 한다.**
> **Unsloth는 성능과 양자화 비교 실험으로 두 번째에 배치하는 게 맞다.**

그 이유는:
- 문서 근거가 가장 많고
- 서버 확인이 쉽고
- 연결 실패 원인을 빨리 찾을 수 있기 때문이다.

반대로 Unsloth는 흥미롭지만,
처음부터 붙이기엔 경로가 더 길고 변수도 더 많다.

## 참고 링크

### OpenClaw
- <https://docs.openclaw.ai/gateway/local-models>
- <https://docs.openclaw.ai/concepts/model-providers>

### LM Studio
- <https://lmstudio.ai/docs/developer/openai-compat>
- <https://lmstudio.ai/docs/developer/anthropic-compat>
- <https://lmstudio.ai/blog/claudecode>

### Unsloth
- <https://unsloth.ai/docs/models/gemma-4>
- <https://unsloth.ai/docs/basics/claude-code>
- <https://unsloth.ai/docs/basics/codex>

### GeekNews 참고
- <https://news.hada.io/topic?id=28265>
- <https://news.hada.io/topic?id=28205>
