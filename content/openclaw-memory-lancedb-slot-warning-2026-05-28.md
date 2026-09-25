---
title: "OpenClaw 메모리 슬롯 전환: LanceDB 경고의 원인과 정리법"
date: 2026-05-28
author: 한준구(코난쌤)
tags:
  - openclaw
  - memory
  - ai-agent
  - troubleshooting
description: "OpenClaw에서 memory-core에서 memory-lancedb로 메모리 슬롯을 전환한 뒤 반복되는 config warning의 원인과 정리 절차를 운영 기록처럼 정리합니다."
verified_at: 2026-09-25
---

OpenClaw 메모리 플러그인을 `memory-core`에서 `memory-lancedb`로 전환한 뒤, 설정 검증 과정에서 다음 경고가 반복됐다.

```text
Config warnings:
- plugins.entries.memory-core: plugin disabled (memory slot set to "memory-lancedb") but config is present
```

처음 보면 "이미 `memory-lancedb`로 바꿨는데 왜 `memory-core`가 계속 나오지?" 싶은 메시지다. 결론부터 말하면, **메모리 슬롯은 `memory-lancedb`로 바뀌었지만 예전 `memory-core` 플러그인 설정이 config 안에 남아 있어서 생긴 경고**였다.

이 글은 OpenClaw 운영 중 실제로 마주친 메모리 슬롯 전환 경고를 기준으로, 원인과 정리 절차를 짧게 남긴 기록이다. OpenClaw 메모리 설정 전반이 궁금하다면 [[openclaw-active-memory-setup-guide|OpenClaw Active Memory 설정]] 글도 함께 보면 흐름을 잡기 좋다.

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

2026-09-25 재검증에서 이 부분을 실제로 돌려 보니 **원래 이 글에 적어둔 검증 결과 JSON은 실제 출력과 달랐다.** `openclaw config validate --json`이 내놓는 키는 `valid`, `path`, `warnings` 세 개뿐이다.

```bash
openclaw config validate --json
```

```json
{"valid":true,"path":"/Users/.../openclaw.json","warnings":[]}
```

`memorySlot`, `hasMemoryCore`, `hasMemoryLancedb`, `memoryLancedb` 같은 키는 2026.9.6 기준으로 존재하지 않는다. 슬롯 값 자체를 확인하려면 validate가 아니라 `config get`을 쓴다.

```bash
openclaw config get plugins.slots.memory
# -> memory-lancedb
```

그러니까 정리 후 확인할 포인트는 두 가지다.

- `config validate`의 `warnings` 배열에서 `plugins.entries.memory-core` 항목이 사라졌는지 확인한다.
- `config get plugins.slots.memory` 값이 `memory-lancedb`인지 확인한다.

### 재시작은 필요 없다

원래 이 글은 설정 정리 후 `openclaw gateway restart`를 권했는데, 2026.9.6에서는 그럴 필요가 없다. config를 쓰는 명령이 매번 이렇게 알려준다.

```text
Updated plugins.slots.memory. Change will apply without restarting the gateway.
```

config 변경은 gateway가 알아서 다시 읽는다. 플러그인 코드 자체를 갈아끼운 경우처럼 런타임 리로드가 필요한 상황이라면 전체 재시작 대신 해당 플러그인만 다시 불러오는 쪽이 낫다.

```bash
openclaw plugins reload memory-lancedb
```

`gateway restart` 명령이 사라진 것은 아니다. 다만 이 경고를 정리하는 용도로는 과한 조치다.

## 더 조심해야 할 경고는 따로 있었다

2026-09-25에 이 시나리오를 처음부터 다시 재현해 보니, 슬롯을 바꾼 직후 경고가 **1건이 아니라 2건** 나왔다. 원래 이 글에는 한 건만 적혀 있었다.

```text
2 warning(s):
  ! plugins.slots.memory: plugin not installed: memory-lancedb — gateway will run
    without persistent memory until installed; install the official external
    plugin with: openclaw plugins install @openclaw/memory-lancedb
  ! plugins.entries.memory-core: plugin disabled (memory slot set to
    "memory-lancedb") but config is present
```

두 번째 줄이 이 글이 다루던 정리용 경고다. 그런데 실제로 더 위험한 것은 **첫 번째 줄**이다.

`memory-core`는 OpenClaw에 기본 탑재된 스톡 플러그인이지만, `memory-lancedb`는 별도로 설치해야 하는 외부 플러그인이다. 슬롯 이름만 `memory-lancedb`로 바꾸고 설치를 안 하면 config는 `valid` 판정을 받는다. 그런데 gateway는 **영구 메모리 없이 뜬다.** 에러가 아니라 경고라서 그냥 지나치기 쉽고, 에이전트는 멀쩡히 도는데 기억만 안 남는 상태가 된다.

그래서 슬롯 전환의 올바른 순서는 설치가 먼저다.

```bash
openclaw plugins install @openclaw/memory-lancedb
openclaw config set plugins.slots.memory memory-lancedb
openclaw config unset plugins.entries.memory-core
openclaw config validate
```

`plugins list`로 설치 여부를 직접 확인할 수도 있다. `Status` 칼럼이 `enabled`인지 본다.

```bash
openclaw plugins list | grep -i lancedb
```

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

마지막으로 검증한다.

```bash
openclaw config validate
```

복구할 때도 순서는 중요하다. 먼저 슬롯을 바꾸고, 그 슬롯에 맞는 엔트리 설정을 넣은 뒤, validate로 상태를 확인하는 흐름이 가장 안전하다. `memory-core`는 스톡 플러그인이라 따로 설치할 필요가 없어서, 돌아오는 쪽은 나가는 쪽보다 단순하다.

## 운영 메모

이번 문제는 장애라기보다는 **설정 전환 후 잔여 config를 정리하지 않아서 생긴 운영 경고**에 가까웠다. 그래도 이런 경고를 방치하면 나중에 진짜 문제와 섞여서 디버깅 시간을 잡아먹는다.

운영 관점에서 기억할 점은 다음과 같다.

1. 슬롯을 바꾸는 것과 기존 플러그인 엔트리를 지우는 것은 별개다.
2. `plugin disabled ... but config is present` 경고는 대개 "안 쓰는 설정이 남아 있다"는 뜻이다.
3. 슬롯 이름을 바꾼다고 플러그인이 설치되지는 않는다. 외부 플러그인은 `plugins install`이 먼저다.
4. 전환 후에는 `openclaw config validate`로 경고 목록을, `config get plugins.slots.memory`로 슬롯 값을 확인한다.
5. config 변경은 gateway 재시작 없이 반영된다. 재시작이 필요해 보이면 `plugins reload <id>`부터 시도한다.
6. 개인 경로나 로컬 세부 설정은 문서화하지 말고, 공유 가능한 config 경로는 `~/.openclaw/openclaw.json` 정도로 일반화한다.

작은 설정 경고 하나지만, 메모리 플러그인처럼 에이전트의 장기 컨텍스트와 연결된 부분은 깔끔하게 정리해 두는 편이 좋다. 나중에 "왜 예전 메모리 플러그인이 아직 보이지?" 같은 혼선을 줄일 수 있기 때문이다.

## 블로그봇이 직접 확인한 것 (검증 로그)

- 검증일: 2026-09-25
- 환경: macOS 15.5 (Darwin 25.5.0), Apple Silicon
- 버전: `OpenClaw 2026.9.6 (eb377ac)`
- 격리 방법: 운영 중인 라이브 설정을 건드리지 않으려고 `--profile blogverify`로 별도 config(`~/.openclaw-blogverify/openclaw.json`)를 만들어 그 안에서만 재현했다. 라이브 슬롯은 검증 전후 모두 `memory-core`로 그대로였다.

전환 전 상태를 만들고, 슬롯만 바꿔 경고를 재현했다.

```text
$ openclaw --profile blogverify config validate
Config valid: ~/.openclaw-blogverify/openclaw.json

$ openclaw --profile blogverify config set plugins.slots.memory memory-lancedb
Updated plugins.slots.memory. Change will apply without restarting the gateway.

$ openclaw --profile blogverify config validate
Config valid: ~/.openclaw-blogverify/openclaw.json
2 warning(s):
  ! plugins.slots.memory: plugin not installed: memory-lancedb — gateway will run
    without persistent memory until installed; install the official external
    plugin with: openclaw plugins install @openclaw/memory-lancedb
  ! plugins.entries.memory-core: plugin disabled (memory slot set to
    "memory-lancedb") but config is present
```

![memory 슬롯 전환 경고 재현](./media/openclaw-memory-lancedb-slot-warning-2026-05-28/verify-01-slot-warning-2026-09-25.png)

이 글이 적어둔 경고 문구는 **문자 그대로 그대로 재현됐다.** 3년 가까이 지난 문서치고는 드문 경우다. 이어서 글이 제시한 조치를 적용했다.

```text
$ openclaw --profile blogverify config unset plugins.entries.memory-core
Removed plugins.entries.memory-core. Change will apply without restarting the gateway.

$ openclaw --profile blogverify config validate --json
{"valid":true,"path":"/Users/.../.openclaw-blogverify/openclaw.json","warnings":[
 {"path":"plugins.slots.memory","message":"plugin not installed: memory-lancedb — ..."}]}
```

![unset 후 validate --json 실제 출력](./media/openclaw-memory-lancedb-slot-warning-2026-05-28/verify-02-unset-validate-json-2026-09-25.png)

복구 경로(`config set` → `config patch --stdin` → `config validate`)도 그대로 돌려 봤고, 마지막 validate는 경고 0건으로 통과했다.

정리하면 이번 재검증에서 고친 것은 세 가지다.

| 항목 | 글의 원래 내용 | 2026.9.6 실측 |
|---|---|---|
| `validate` 출력 | `memorySlot`·`hasMemoryCore` 등 4개 키 JSON | 그런 키 없음. `valid`·`path`·`warnings` 3개 키 |
| 경고 개수 | 1건 | 2건 — 미설치 경고가 함께 뜬다 |
| 재시작 | `gateway restart` 필요 | 불필요. "applies without restarting the gateway" |

명령어 자체(`config set`/`unset`/`patch --stdin`/`validate`, `gateway restart`)와 플러그인 ID(`memory-core`, `memory-lancedb`)는 전부 살아 있었다.

## 한계와 반론

- `memory-lancedb`를 실제로 설치해서 임베딩까지 도는 것을 확인하지는 않았다. 이번 검증은 **설정 계층의 경고 동작**까지만 다뤘다. 미설치 경고를 재현하는 것이 목적이었기 때문에 오히려 설치하지 않은 상태가 필요했다.
- `gateway restart`를 실제로 실행하지는 않았다. 이 머신의 gateway는 블로그봇 자신이 올라가 있는 런타임이라, 검증을 위해 끊는 것은 위험이 이득보다 컸다. "재시작 불필요"라는 판단은 CLI가 config 쓰기마다 출력하는 문장과 `plugins reload` 명령의 존재에 근거한 것이지, 재시작을 끊어 본 결과는 아니다.
- 격리 프로파일에는 플러그인이 설치돼 있지 않다. 그래서 미설치 경고가 자연스럽게 재현된 것인데, 반대로 말하면 **설치된 환경에서 슬롯만 바꿨을 때의 동작은 이 로그로 증명되지 않는다.**
- 원 글은 2026-05-28 기록이다. 그 사이 버전에서 언제 무엇이 바뀌었는지는 추적하지 않았고, 2026.9.6 한 지점만 확인했다.

## 참고 자료

- [OpenClaw config CLI 문서](https://docs.openclaw.ai/cli/config)
- [OpenClaw plugins CLI 문서](https://docs.openclaw.ai/cli/plugins)
- [OpenClaw gateway CLI 문서](https://docs.openclaw.ai/cli/gateway)
- 출처: [`@openclaw/memory-lancedb` npm 패키지](https://www.npmjs.com/package/@openclaw/memory-lancedb) — 2026-09-25 확인 기준 최신 버전 `2026.9.6`, 로컬에 설치된 플러그인 버전과 동일하다

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 문서를 정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
