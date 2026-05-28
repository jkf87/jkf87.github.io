---
title: "OpenClaw Obsidian 연동 및 Memory Wiki 설정법"
date: 2026-05-28
tags:
  - openclaw
  - obsidian
  - memory-wiki
  - llm-wiki
  - setup-guide
description: "OpenClaw에서 Obsidian 공식 CLI를 등록하고 memory-wiki를 Obsidian renderMode로 연결하는 방법을 명령어와 설정 예제로 정리합니다."
aliases:
  - openclaw-obsidian-memory-wiki
  - llm-wiki-obsidian-openclaw
draft: false
---

OpenClaw 2026.5.x 기준으로 Obsidian은 독립 기본 플러그인보다 **`memory-wiki` + 공식 `obsidian` CLI** 조합으로 쓰는 쪽이 맞다. `memory-wiki`가 LLM Wiki 역할을 하고, Obsidian은 그 vault를 읽고 편집하는 UI가 된다.

![OpenClaw Memory Wiki와 Obsidian 연동 구조](./images/openclaw-obsidian-memory-wiki/architecture.png)

## 0. 구조

```text
OpenClaw active memory
  -> memory-wiki
  -> Obsidian-friendly Markdown vault
  -> Obsidian app / official obsidian CLI
```

확인할 점:

- `memory-wiki`는 OpenClaw 번들 플러그인
- Obsidian 연동은 `memory-wiki.config.obsidian`에서 켬
- CLI는 third-party `obsidian-cli`가 아니라 공식 `obsidian` CLI
- Obsidian 앱 1.12.7 이상 필요

## 1. 현재 상태 확인

```bash
openclaw --version
openclaw plugins list | grep memory-wiki
openclaw wiki status
openclaw wiki doctor
```

Obsidian CLI 확인:

```bash
obsidian version
obsidian help
```

`obsidian` 명령이 없으면 Obsidian 앱에서 CLI를 켠다.

```text
Obsidian -> Settings -> General -> Command line interface -> Enable
```

macOS에서는 보통 `/usr/local/bin/obsidian`이 등록된다.

## 2. Memory Wiki 활성화

`~/.openclaw/openclaw.json`:

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian"
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true
          },
          search: {
            backend: "shared",
            corpus: "wiki"
          },
          context: {
            includeCompiledDigestPrompt: false
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true
          }
        }
      }
    }
  }
}
```

검증:

```bash
openclaw config validate
openclaw gateway restart
openclaw wiki status
openclaw wiki doctor
```

## 3. Vault 초기화

```bash
openclaw wiki init
openclaw wiki status
openclaw wiki compile
openclaw wiki lint
```

Obsidian에서 열기:

```bash
openclaw wiki obsidian status
openclaw wiki obsidian open index.md
```

Obsidian 앱에서 직접 vault를 추가할 수도 있다.

```text
Open folder as vault:
~/.openclaw/wiki/main
```

## 4. 메모리와 연결하기: bridge 모드

OpenClaw의 active memory 결과를 LLM Wiki에 가져오려면 bridge를 켠다.

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian"
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false
          },
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true
          },
          search: {
            backend: "shared",
            corpus: "all"
          }
        }
      }
    }
  }
}
```

적용:

```bash
openclaw config validate
openclaw gateway restart
openclaw wiki bridge import
openclaw wiki compile
openclaw wiki lint
```

상태 확인:

```bash
openclaw wiki status
openclaw wiki search "google meet"
openclaw wiki search "codex usage limit" --mode source-evidence
```

## 5. 문서 넣기

로컬 Markdown:

```bash
openclaw wiki ingest ./notes/project-alpha.md
openclaw wiki compile
```

URL:

```bash
openclaw wiki ingest https://example.com/article
openclaw wiki compile
```

검색:

```bash
openclaw wiki search "project alpha"
openclaw wiki search "누가 Teams rollout을 잘 알아?" --mode route-question
openclaw wiki search "bgroux" --mode find-person
```

페이지 읽기:

```bash
openclaw wiki get entity.alpha --from 1 --lines 80
```

## 6. Synthesis 작성

좁은 주제 요약을 wiki에 직접 만든다.

```bash
openclaw wiki apply synthesis "Google Meet Setup" \
  --body "Google Meet plugin uses transcribe mode for listen-only validation and agent mode for talk-back." \
  --source-id source.google-meet-setup
```

metadata 업데이트:

```bash
openclaw wiki apply metadata entity.google-meet \
  --source-id source.google-meet-setup \
  --status review \
  --question "Chrome-node setup verified on current machine?"
```

컴파일:

```bash
openclaw wiki compile
openclaw wiki lint
```

## 7. Obsidian CLI로 직접 다루기

공식 CLI:

```bash
obsidian vault="OpenClaw Wiki" search query="google meet" format=json
obsidian vault="OpenClaw Wiki" open path="index.md"
obsidian vault="OpenClaw Wiki" daily
```

OpenClaw wrapper:

```bash
openclaw wiki obsidian status
openclaw wiki obsidian search "google meet"
openclaw wiki obsidian open syntheses/google-meet-setup.md
openclaw wiki obsidian command workspace:quick-switcher
openclaw wiki obsidian daily
```

## 8. 에이전트 프롬프트

### Wiki 초기화

```text
OpenClaw memory-wiki를 Obsidian renderMode로 초기화해줘.
vault path는 ~/.openclaw/wiki/main 으로 두고, 공식 obsidian CLI 상태까지 확인해.
명령 실행 후 openclaw wiki status, doctor, obsidian status 결과만 요약해줘.
```

### 메모리 가져오기

```text
현재 OpenClaw memory artifacts를 memory-wiki bridge로 가져와줘.
bridge import -> compile -> lint 순서로 실행하고, 생성된 top pages와 warning만 알려줘.
```

### 문서 정리

```text
이 폴더의 Markdown 문서를 memory-wiki에 ingest하고 Obsidian에서 볼 수 있게 compile해줘.
끝나면 검색 가능한 키워드 5개와 vault 경로를 알려줘.
```

### 근거 있는 답변

```text
memory-wiki에서 "Codex usage limit"을 source-evidence 모드로 검색하고,
근거가 있는 내용만 5줄로 요약해줘.
추측은 빼고 source id를 같이 적어줘.
```

## 9. 문제 해결

### `Obsidian CLI is not available on PATH`

Obsidian 앱에서 CLI를 켠다.

```text
Settings -> General -> Command line interface -> Enable
```

다시 확인:

```bash
which obsidian
obsidian version
openclaw wiki obsidian status
```

### vault가 안 보임

```bash
openclaw wiki status
openclaw wiki init
openclaw wiki compile
```

Obsidian에서 직접 폴더를 연다.

```text
~/.openclaw/wiki/main
```

### bridge import가 비어 있음

```bash
openclaw plugins list | grep -E 'memory|wiki'
openclaw wiki doctor
openclaw memory search "test"
```

확인할 것:

- active memory plugin이 켜져 있는지
- `bridge.enabled`가 `true`인지
- `bridge.readMemoryArtifacts`가 `true`인지
- Gateway 재시작을 했는지

### 검색 결과가 약함

```json5
{
  search: {
    backend: "shared",
    corpus: "all"
  }
}
```

적용 후:

```bash
openclaw gateway restart
openclaw wiki compile
openclaw wiki search "검색어" --mode source-evidence
```

## 10. 최소 성공 루트

처음에는 이 순서만 한다.

```bash
obsidian version
openclaw plugins list | grep memory-wiki
openclaw wiki init
openclaw wiki compile
openclaw wiki obsidian status
openclaw wiki obsidian open index.md
```

그다음 active memory와 연결한다.

```bash
openclaw wiki bridge import
openclaw wiki compile
openclaw wiki search "최근 작업"
```

---

참고: [OpenClaw Memory Wiki docs](https://github.com/openclaw/openclaw/blob/main/docs/plugins/memory-wiki.md), [OpenClaw Wiki CLI docs](https://github.com/openclaw/openclaw/blob/main/docs/cli/wiki.md)
