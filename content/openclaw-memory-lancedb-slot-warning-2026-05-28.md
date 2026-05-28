---
title: "OpenClaw 메모리 슬롯 전환: LanceDB 경고의 원인과 정리법"
date: 2026-05-28
tags:
  - openclaw
  - memory
  - ai-agent
  - troubleshooting
description: "OpenClaw에서 memory-core에서 memory-lancedb로 메모리 슬롯을 전환한 뒤 반복되는 config warning의 원인과 정리 절차를 운영 기록처럼 정리합니다."
---

OpenClaw 메모리 플러그인을 `memory-core`에서 `memory-lancedb`로 전환한 뒤, 설정 검증 과정에서 다음 경고가 반복됐다.

```text
Config warnings:
- plugins.entries.memory-core: plugin disabled (memory slot set to "memory-lancedb") but config is present
```

처음 보면 "이미 `memory-lancedb`로 바꿨는데 왜 `memory-core`가 계속 나오지?" 싶은 메시지다. 결론부터 말하면, **메모리 슬롯은 `memory-lancedb`로 바뀌었지만 예전 `memory-core` 플러그인 설정이 config 안에 남아 있어서 생긴 경고**였다.

이 글은 OpenClaw 운영 중 실제로 마주친 메모리 슬롯 전환 경고를 기준으로, 원인과 정리 절차를 짧게 남긴 기록이다. AI 에이전트 메모리 시스템 전반이 궁금하다면 이전 글인 [[agentmemory-ai-coding-agent-persistent-memory-2026-05-10|AI 코딩 에이전트가 기억을 잃는 병]]도 함께 보면 흐름을 잡기 좋다.

## 문제 상황

OpenClaw에는 메모리 기능을 담당하는 슬롯이 있다. 이 슬롯에 어떤 메모리 플러그인을 꽂을지 설정하면, 런타임은 그 플러그인을 기준으로 메모리를 읽고 쓴다.

이번 상황에서는 메모리 슬롯을 `memory-core`에서 `memory-lancedb`로 바꿨다.

설정상 의도는 명확했다.

```text
plugins.slots.memory = "memory-lancedb"
```

그런데 `openclaw config validate`를 실행할 때마다 아래 경고가 계속 보였다.

```text
plugins.entries.memory-core: plugin disabled (memory slot set to "memory-lancedb") but config is present
```

실제 메모리 슬롯은 `memory-lancedb`로 잡혀 있는데, `memory-core` 관련 경고가 반복되는 상태였다.

## 원인 분석

핵심은 OpenClaw 설정 안에서 **슬롯 선택**과 **플러그인 엔트리 설정**이 별도로 존재한다는 점이다.

슬롯은 현재 어떤 플러그인을 대표 메모리로 쓸지 정한다.

```json
{
  "plugins": {
    "slots": {
      "memory": "memory-lancedb"
    }
  }
}
```

반면 `plugins.entries`에는 개별 플러그인의 세부 설정이 남을 수 있다.

문제 상황에서는 슬롯은 이미 `memory-lancedb`였지만, `plugins.entries.memory-core` 설정이 여전히 남아 있었다. 특히 기존에 `memory-core`를 쓰면서 `enabled`나 `dreaming` 같은 설정을 넣어둔 경우, 슬롯에서는 밀려났지만 config에는 엔트리가 남는다.

그래서 OpenClaw 입장에서는 이렇게 해석한다.

- 현재 메모리 슬롯은 `memory-lancedb`다.
- 따라서 `memory-core`는 활성 슬롯 플러그인이 아니다.
- 그런데 `plugins.entries.memory-core` 설정이 아직 존재한다.
- 사용되지 않는 플러그인 설정이 남아 있으니 경고를 낸다.

즉, 이 경고는 `memory-lancedb`가 실패했다는 뜻이 아니다. **전환 후 남은 예전 플러그인 설정을 정리하라는 신호**에 가깝다.

## 해결 절차

해결은 간단했다. 더 이상 `memory-core`를 쓰지 않을 거라면, 남아 있는 `memory-core` 엔트리를 제거하면 된다.

```bash
openclaw config unset plugins.entries.memory-core
openclaw config validate
```

검증 결과는 다음 상태가 되어야 한다.

```json
{
  "memorySlot": "memory-lancedb",
  "hasMemoryCore": false,
  "hasMemoryLancedb": true,
  "memoryLancedb": true
}
```

여기서 확인할 포인트는 네 가지다.

- `memorySlot`이 `memory-lancedb`인지 확인한다.
- `hasMemoryCore`가 `false`인지 확인한다.
- `hasMemoryLancedb`가 `true`인지 확인한다.
- `memoryLancedb`가 `true`인지 확인한다.

설정 정리가 끝났다면 gateway를 재시작한다.

```bash
openclaw gateway restart
```

OpenClaw처럼 백그라운드 gateway가 플러그인 상태를 들고 있는 구조에서는 config만 바꾸고 끝내면 이전 상태가 남아 보일 수 있다. 설정 변경 후 재시작까지 해야 실제 런타임 상태가 깔끔해진다.

## 복구 방법

나중에 다시 `memory-core`로 돌아가고 싶다면, 슬롯을 `memory-core`로 되돌리고 `plugins.entries.memory-core` 설정을 다시 넣으면 된다.

```bash
openclaw config set plugins.slots.memory memory-core
```

이어서 `memory-core` 엔트리를 복구한다.

```bash
openclaw config patch --stdin <<'JSON'
{
  "plugins": {
    "entries": {
      "memory-core": {
        "enabled": true,
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
JSON
```

마지막으로 검증과 재시작을 한다.

```bash
openclaw config validate
openclaw gateway restart
```

복구할 때도 순서는 중요하다. 먼저 슬롯을 바꾸고, 그 슬롯에 맞는 엔트리 설정을 넣은 뒤, validate와 gateway restart로 상태를 확인하는 흐름이 가장 안전하다.

## 운영 메모

이번 문제는 장애라기보다는 **설정 전환 후 잔여 config를 정리하지 않아서 생긴 운영 경고**에 가까웠다. 그래도 이런 경고를 방치하면 나중에 진짜 문제와 섞여서 디버깅 시간을 잡아먹는다.

운영 관점에서 기억할 점은 다음과 같다.

1. 슬롯을 바꾸는 것과 기존 플러그인 엔트리를 지우는 것은 별개다.
2. `plugin disabled ... but config is present` 경고는 대개 "안 쓰는 설정이 남아 있다"는 뜻이다.
3. 전환 후에는 `openclaw config validate`로 실제 슬롯과 엔트리 상태를 확인한다.
4. gateway형 런타임은 설정 변경 후 `openclaw gateway restart`까지 해야 한다.
5. 개인 경로나 로컬 세부 설정은 문서화하지 말고, 공유 가능한 config 경로는 `~/.openclaw/openclaw.json` 정도로 일반화한다.

작은 설정 경고 하나지만, 메모리 플러그인처럼 에이전트의 장기 컨텍스트와 연결된 부분은 깔끔하게 정리해 두는 편이 좋다. 나중에 "왜 예전 메모리 플러그인이 아직 보이지?" 같은 혼선을 줄일 수 있기 때문이다.
