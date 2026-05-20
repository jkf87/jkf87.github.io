---
title: "OpenClaw Active Memory: AI가 대화 맥락을 자동으로 기억하는 방법"
date: 2026-04-14
tags:
  - 오픈클로
  - openclaw
  - active memory
  - 액티브 메모리
  - ai 메모리
  - memory search
  - ai 에이전트
  - 설정 가이드
description: "OpenClaw 4.12에 추가된 Active Memory Plugin 설정 방법과 실전 사용법을 정리했다. 매번 '기억해줘'라고 말할 필요 없이, AI가 대화 맥락을 자동으로 검색해서 자연스럽게 대화에 반영한다."
---

OpenClaw를 쓰다 보면 한 가지 아쉬운 점이 있다. AI가 이전 대화를 기억 못 한다는 것이다. "지난번에 말한 거 기억나?"라고 물어보면, 매번 메모리를 검색해야 한다. 아니면 내가 직접 "remember this"라고 명령해야 한다.

**Active Memory**는 이 문제를 근본적으로 해결한다. 매번 명령하지 않아도, AI가 답변하기 전에 **자동으로 관련 메모리를 검색해서 컨텍스트에 주입**한다. 사용자는 그저 대화하면 된다.

이 글에서는 Active Memory가 무엇인지, 어떻게 설정하는지, 그리고 실전에서 어떻게 쓰이는지 정리한다.

## Active Memory란?

Active Memory는 OpenClaw 4.12에 새로 추가된 **플러그인 기반 메모리 서브에이전트**다.

핵심 아이디어는 간단하다:

> 사용자가 메시지를 보내면, **메인 답변을 생성하기 직전에** 메모리 검색 에이전트가 먼저 실행된다. 관련 메모리가 있으면 이를 자동으로 시스템 컨텍스트에 추가한 뒤, 메인 에이전트가 답변을 생성한다.

기존 방식과의 차이를 비교하면 명확하다.

| 항목 | 기존 (수동) | Active Memory (자동) |
|---|---|---|
| 메모리 검색 시점 | 사용자가 "기억해줘"라고 명령할 때 | **매 메시지마다 자동** |
| 컨텍스트 반영 | 에이전트가 판단해서 `memory_search` 호출 | **답변 전에 자동 주입** |
| 사용자 경험 | "이거 기억해"라고 반복해야 함 | **그냥 대화하면 됨** |
| 반응 자연스러움 | 이미 답변을 한 뒤에야 메모리를 찾음 | **답변 자체에 메모리가 녹아있음** |

## 작동 구조

```
사용자 메시지
    ↓
메모리 쿼리 생성 (queryMode에 따라)
    ↓
메모리 서브에이전트 실행 (memory_search + memory_get만 사용)
    ↓
관련 메모리 발견? ── 아니오 ──→ 메인 답변 (평소처럼)
    │
   예
    ↓
숨겨진 시스템 컨텍스트에 메모리 추가
    ↓
메인 답변 (메모리를 반영해서 자연스럽게)
```

중요한 점: 메모리 서브에이전트는 `memory_search`와 `memory_get` **두 가지 도구만** 사용할 수 있다. 외부 API 호출이나 파일 쓰기 등은 할 수 없다. 안전하게 설계되어 있다.

## 설정 방법

### 최소 설정

`~/.openclaw/openclaw.json`에 다음을 추가한다:

```json
{
  "plugins": {
    "entries": {
      "active-memory": {
        "enabled": true,
        "config": {
          "agents": ["main"],
          "allowedChatTypes": ["direct"],
          "modelFallback": "google/gemini-3-flash",
          "queryMode": "recent",
          "promptStyle": "balanced",
          "timeoutMs": 15000,
          "maxSummaryChars": 220,
          "persistTranscripts": false,
          "logging": true
        }
      }
    }
  }
}
```

그리고 게이트웨이를 재시작한다:

```bash
openclaw gateway restart
```

### 설정 항목 설명

| 항목 | 의미 | 추천값 |
|---|---|---|
| `enabled` | 플러그인 활성화 | `true` |
| `agents` | Active Memory를 적용할 에이전트 ID | `["main"]` (본인 에이전트 ID) |
| `allowedChatTypes` | 적용할 채팅 타입 | `["direct"]` (1:1 대화만) |
| `modelFallback` | 메모리 검색에 쓸 폴백 모델 | `"google/gemini-3-flash"` (빠르고 저렴) |
| `queryMode` | 검색 범위 모드 | `"recent"` (균형잡힌 기본값) |
| `promptStyle` | 검색 에이전트의 판단 기준 | `"balanced"` |
| `timeoutMs` | 서브에이전트 실행 타임아웃 | `15000` (15초) |
| `maxSummaryChars` | 주입할 메모리 최대 글자 수 | `220` |
| `logging` | 로그 출력 | `true` (조정 중에는 켜기) |

### queryMode: 검색 범위 선택

가장 중요한 설정 중 하나다. 세 가지 모드가 있다:

**`message`** — 가장 빠름
- 마지막 사용자 메시지만 검색에 사용
- 지연 시간 최소화
- 안정적인 선호도(취향, 습관) 리콜에 적합
- 타임아웃 추천: 3,000~5,000ms

**`recent`** — 균형잡힌 기본값 ⭐
- 최근 대화 테일 + 현재 메시지를 함께 사용
- "아까 말한 거 관련해서..." 같은 후속 질문에 잘 대응
- 타임아웃 추천: 15,000ms

**`full`** — 가장 정확하지만 느림
- 전체 대화 기록을 검색에 사용
- 스레드 처음 부분의 중요한 맥락까지 포착
- 타임아웃: 15,000ms 이상 필요 (스레드 크기에 따라 더 길게)

### promptStyle: 검색 에이전트의 성격

| 스타일 | 설명 | 언제 쓸까 |
|---|---|---|
| `balanced` | 일반용 기본값 | 대부분의 경우 |
| `strict` | 가장 보수적 | 메모리 노이즈가 많을 때 |
| `contextual` | 대화 맥락을 더 중시 | 연속성이 중요한 대화 |
| `recall-heavy` | 약한 연관성도 수용 | "비슷한 거 다 찾아줘" 같은 느낌 |
| `precision-heavy` | 명확한 매칭만 | 정확도가 최우선일 때 |
| `preference-only` | 취향·습관·루틴 특화 | "내가 좋아하는 것들" 리콜에 최적화 |

### 다중 에이전트 환경에서

에이전트가 여러 개라면 `agents` 배열에 전부 넣으면 된다:

```json
"agents": ["agasa", "agasabot", "obsibot"]
```

그룹 채팅에서도 작동하게 하려면:

```json
"allowedChatTypes": ["direct", "group"]
```

## 실시간 확인하기

설정 후에 Active Memory가 실제로 작동하는지 확인하는 방법:

### /verbose 모드

채팅에서 다음 명령을 입력한다:

```
/verbose on
```

그러면 매 답변 뒤에 이런 상태 줄이 표시된다:

```
🧩 Active Memory: ok 842ms recent 34 chars
```

- `ok`: 정상 실행
- `842ms`: 검색 소요 시간
- `recent`: 사용한 queryMode
- `34 chars`: 주입한 메모리 길이

### /trace 모드

```
/trace on
```

메모리 서브에이전트가 **어떤 내용을 찾았는지** 사람이 읽을 수 있게 보여준다:

```
🔎 Active Memory Debug: Lemon pepper wings with blue cheese.
```

### 세션 토글

설정을 건드리지 않고 현재 세션에서만 끄고 켤 수 있다:

```
/active-memory off
/active-memory on
/active-memory status
```

전체 세션에 적용하려면 `--global` 플래그를 쓴다:

```
/active-memory off --global
```

## 언제 쓰면 좋을까

### 적합한 경우 ✅

- **지속적인 1:1 대화 세션** — 매일 이어지는 대화에서 자연스러운 연속성
- **사용자 취향·선호도 기반 응답** — "커피 좋아하는 것 알아?" 같은 것을 자연스럽게 반영
- **장기 컨텍스트 유지** — 일주일 전에 한 대화의 맥락을 자동으로 가져옴
- **복수 에이전트 환경** — 에이전트마다 각자의 메모리를 자동 검색

### 적합하지 않은 경우 ❌

- **원샷 API 호출** — 단발성 작업에선 오버헤드만 증가
- **자동화 워커** — 백그라운드 작업이나 크론 잡엔 불필요
- **헤드리스 실행** — 비대화형 실행에선 작동하지 않음
- **그룹 채팅에서 개인 메모리 노출** — 프라이버시 주의 필요

## 모델 폴백 정책

`config.model`을 명시하지 않으면, Active Memory는 다음 순서로 모델을 선택한다:

1. 플러그인에 명시된 모델 (`config.model`)
2. 현재 세션 모델 (상속)
3. 에이전트 기본 모델
4. `modelFallback`에 설정된 모델
5. 전부 없으면 **해당 턴은 스킵**

`modelFallback`은 저렴하고 빠른 모델로 설정하는 것이 좋다. 메모리 검색 자체가 복잡한 추론이 필요한 작업이 아니기 때문이다:

```json
"modelFallback": "google/gemini-3-flash"
```

## 임베딩 프로바이더 설정

Active Memory는 내부적으로 `memory_search`를 사용하므로, **임베딩 프로바이더 설정**이 중요하다.

### 자동 감지

OpenAI, Gemini, Voyage, Mistral 중 API 키가 하나라도 설정되어 있으면 자동으로 감지된다. 별도 설정 없이도 동작한다.

### 명시적 설정 (추천)

자동 감지는 편하지만, API 키가 여러 개 있으면 어떤 게 선택될지 예측하기 어렵다. **명시적으로 지정하는 것이 안전하다**:

**OpenAI:**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "model": "text-embedding-3-small"
      }
    }
  }
}
```

**Gemini:**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "gemini",
        "model": "gemini-embedding-001"
      }
    }
  }
}
```

**Gemini Embedding 2 (이미지·오디오 인덱싱 지원):**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "gemini",
        "model": "gemini-embedding-2-preview",
        "outputDimensionality": 1536
      }
    }
  }
}
```

**Ollama (로컬, API 키 불필요):**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "ollama",
        "model": "nomic-embed-text"
      }
    }
  }
}
```

### 폴백 설정

프로바이더 장애 시 자동 전환을 원하면 `fallback`을 설정한다:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "provider": "openai",
        "fallback": "gemini"
      }
    }
  }
}
```

### 메모리 상태 확인

```bash
# 인덱스와 프로바이더 상태 확인
openclaw memory status --deep

# 인덱스 강제 재구축
openclaw memory index --force

# 커맨드라인에서 검색 테스트
openclaw memory search "테스트 쿼리"
```

## 검색 품질 튜닝

메모리가 쌓이다 보면 검색 결과의 품질이 떨어질 수 있다. `memorySearch.query.hybrid` 설정으로 개선할 수 있다.

### 시간적 감쇠 (Temporal Decay)

오래된 메모리는 점점 점수가 낮아지게 한다. 기본 반감기는 30일:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "query": {
          "hybrid": {
            "temporalDecay": {
              "enabled": true,
              "halfLifeDays": 30
            }
          }
        }
      }
    }
  }
}
```

`MEMORY.md` 같은 영구 파일은 감쇠 대상이 아니다.

### MMR (다양성)

비슷한 내용의 메모리가 여러 개 반환되는 것을 방지한다:

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "query": {
          "hybrid": {
            "mmr": {
              "enabled": true,
              "lambda": 0.7
            }
          }
        }
      }
    }
  }
}
```

`lambda` 값: 0이면 최대 다양성, 1이면 최대 관련성.

### 하이브리드 검색 가중치

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "query": {
          "hybrid": {
            "vectorWeight": 0.7,
            "textWeight": 0.3
          }
        }
      }
    }
  }
}
```

- 벡터 검색: 의미 기반 (비슷한 뜻의 문장을 찾음)
- BM25 키워드 검색: 정확한 단어 매칭 (ID, 에러 코드, 설정 키 등)

## 트러블슈팅

### Active Memory가 작동하지 않을 때

체크리스트:

1. **플러그인 활성화 확인** — `plugins.entries.active-memory.enabled: true`
2. **에이전트 ID 확인** — `config.agents`에 현재 에이전트 ID가 있는지
3. **세션 타입 확인** — 대화형 지속 세션이어야 함 (원샷 실행, 크론 잡에서는 작동 안 함)
4. **로깅 켜기** — `logging: true`로 게이트웨이 로그 확인
5. **메모리 인덱스 확인** — `openclaw memory status --deep`

### 임베딩 프로바이더가 바뀐 것 같을 때

`memorySearch.provider`를 명시적으로 고정하면 예측 가능해진다:

```bash
openclaw config set agents.defaults.memorySearch.provider gemini
openclaw gateway restart
openclaw memory index --force
```

### Active Memory가 느릴 때

- `queryMode`를 `recent`에서 `message`로 낮추기
- `timeoutMs` 줄이기
- `maxSummaryChars` 줄이기
- `recentUserTurns`, `recentAssistantTurns` 줄이기

### 검색 결과가 노이즈가 많을 때

- `maxSummaryChars` 줄이기
- `promptStyle`을 `strict` 또는 `precision-heavy`로 변경
- `temporalDecay` 활성화

## 한 줄 요약

> Active Memory는 **"기억해줘"라고 매번 말할 필요 없이**, AI가 매 대화마다 자동으로 관련 메모리를 찾아서 자연스럽게 반영해주는 기능이다. `openclaw.json`에 몇 줄 추가하고 게이트웨이를 재시작하면 끝.

---

- OpenClaw 공식 문서: <https://docs.openclaw.ai>
- Active Memory 문서: <https://docs.openclaw.ai/concepts/active-memory>
- Memory Search 문서: <https://docs.openclaw.ai/concepts/memory-search>
