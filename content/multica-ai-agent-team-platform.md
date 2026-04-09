---
title: "Multica: AI 코딩 에이전트를 팀원으로 만드는 오픈소스 플랫폼"
date: 2026-04-09
tags:
  - ai
  - agents
  - open-source
  - devops
  - automation
description: "코딩 에이전트를 이슈 할당으로 관리하는 오픈소스 플랫폼 Multica. Claude Code와 Codex를 팀원처럼 운용하는 방법과 아키텍처를 정리한다."
---

> "Your next 10 hires won't be human." — Multica

AI 코딩 에이전트(Claude Code, OpenAI Codex 등)를 써본 적이 있다면, 이런 생각을 해봤을 것이다. "이걸 그냥 팀원처럼 이슈 할당하면 알아서 해주면 안 되나?" [Multica](https://github.com/multica-ai/multica)는 정확히 그 문제를 풀고 있다.

Multica는 코딩 에이전트를 **실제 팀원처럼** 관리할 수 있게 해주는 오픈소스 플랫폼이다. 에이전트에게 이슈를 할당하면, 자율적으로 작업을 수행하고, 코멘트를 남기고, 블로커를 보고하고, PR을 만든다. 마치 사람 개발자에게 일을 맡기는 것과 같은 워크플로우를 AI 에이전트와 함께 할 수 있다.

## 왜 이 프로젝트가 눈에 띄었나

지금 AI 코딩 도구는 대부분 "코파일럿" 패러다임이다. 사람이 코드를 쓰면 AI가 옆에서 도와준다. 하지만 Multica는 다른 방향을 택했다. **프로젝트 매니지먼트 시스템에 AI 에이전트가 1급 시민(first-class citizen)으로 참여하는** 구조다. 이슈 트래커에서 사람과 에이전트가 나란히 보이고, 동일한 워크플로우로 관리된다.

이건 하네스 엔지니어링의 실질적인 구현체다. 에이전트를 "채팅 상대"가 아닌 "팀원"으로 다루는 인터페이스를 제공한다는 점에서, 지금까지의 에이전트 도구들과 결이 다르다.

## 핵심 특징

### Agent-as-Teammate

에이전트는 프로필을 갖고, 담당자 드롭다운에 사람과 나란히 표시되며, 이슈에 코멘트를 달고, 블로커를 사전에 보고한다.

```
사람 개발자 → 이슈 할당 → 코드 작성 → PR → 리뷰
AI 에이전트  → 이슈 할당 → 코드 작성 → PR → 리뷰
```

워크플로우가 동일하다. 관리 방식도 동일하다.

### 자율적 태스크 라이프사이클

태스크는 `Enqueue → Claim → Start → Complete/Fail` 단계를 자동으로 거친다. WebSocket을 통한 실시간 진행 상황 스트리밍도 지원하므로, 에이전트가 지금 뭘 하고 있는지 실시간으로 볼 수 있다.

### Skill Compounding (기술 복리효과)

이것이 Multica의 킬러 기능이다. 에이전트가 해결한 솔루션은 재사용 가능한 "스킬 정의"로 패키징된다. 배포 스크립트, 마이그레이션, 코드 리뷰 패턴 등이 조직의 지식으로 축적되어 어떤 에이전트든 활용할 수 있게 된다. **에이전트가 일할수록 팀 전체가 똑똑해진다.**

### 벤더 중립

Claude Code와 OpenAI Codex를 모두 지원한다. PATH에서 사용 가능한 CLI를 자동 감지하며, 특정 벤더에 종속되지 않는다.

## 아키텍처

| 컴포넌트 | 기술 스택 |
|----------|----------|
| Frontend | Next.js 16 (App Router) |
| Backend | Go (Chi router, sqlc, gorilla/websocket) |
| Database | PostgreSQL 17 + pgvector |
| Agent Runtime | 로컬 데몬 (Claude Code / Codex CLI) |

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│  Next.js 16 UI  │◄───►│  Go API 서버  │◄───►│  PostgreSQL 17   │
│  (App Router)   │     │  (Chi + WS)  │     │  + pgvector      │
└─────────────────┘     └──────┬───────┘     └──────────────────┘
                               │
                        ┌──────▼───────┐
                        │ Agent Daemon │
                        │  (로컬 실행)  │
                        └──────┬───────┘
                          ┌────┴────┐
                     ┌────▼──┐  ┌──▼────┐
                     │Claude │  │ Codex │
                     │ Code  │  │  CLI  │
                     └───────┘  └───────┘
```

데몬이 로컬에서 실행되므로 코드가 외부로 나가지 않는다. 셀프호스팅의 큰 장점이다.

## 시작하기

### Docker로 셀프호스팅

```bash
git clone https://github.com/multica-ai/multica.git
cd multica
cp .env.example .env
# .env 파일에서 JWT_SECRET 등 필수 설정 수정
docker compose up -d
cd server && go run ./cmd/migrate up && cd ..
make start
```

### CLI로 에이전트 연결

```bash
brew tap multica-ai/tap
brew install multica
multica login
multica daemon start
```

### 실제 사용 흐름

1. `multica login` — 인증
2. `multica daemon start` — 로컬 데몬 실행
3. 웹 앱에서 Settings → Runtimes에서 런타임 등록 확인
4. Settings → Agents → New Agent에서 에이전트 생성
5. 보드에서 이슈 생성 후 에이전트에 할당
6. 에이전트가 자율적으로 작업 시작

## 기존 도구와의 비교

| | Multica | GitHub Copilot | Cursor | Devin |
|---|---|---|---|---|
| 자율 실행 | O | X | X | O |
| 셀프호스팅 | O | X | X | X |
| 오픈소스 | O (Apache 2.0) | X | X | X |
| 멀티 벤더 | O | X | X | X |
| 태스크 관리 | O (내장) | X | X | O |
| 스킬 축적 | O | X | X | X |

## 실전 시나리오

**버그 트리아지 자동화** — QA팀이 버그를 보고하면, 에이전트가 자동으로 할당받아 원인 분석과 수정 PR을 만든다. 사람 개발자는 리뷰만 하면 된다.

**리팩토링 병렬 처리** — 대규모 리팩토링을 여러 에이전트에 분배해서 병렬로 처리할 수 있다. 각 에이전트가 다른 모듈을 담당하고, 독립적으로 PR을 생성한다.

**문서화 & 테스트 보강** — 사람이 비즈니스 로직에 집중하는 동안, 에이전트가 테스트 코드 작성과 API 문서화를 병행한다.

## 주의할 점

- 초기 설정에 Docker, Go, Node.js 등 개발 환경이 필요하다.
- 에이전트 품질은 기반 모델(Claude Code, Codex)의 성능에 의존한다.
- 복잡한 태스크는 여전히 사람의 감독이 필요하다. 완전 자율이 아닌, 협업 도구로 봐야 한다.

## 정리

Multica는 "AI 에이전트를 어떻게 팀에 통합할 것인가"라는 질문에 대한 실용적인 답을 제시한다. 채팅 인터페이스를 넘어서, 이슈 트래커와 태스크 관리를 통해 에이전트를 관리하는 방식은 실제 팀 환경에 자연스럽게 녹아든다.

Apache 2.0 라이선스의 오픈소스이고 셀프호스팅이 가능하므로, 데이터 주권이 중요한 조직에서도 부담 없이 도입할 수 있다. AI 코딩 에이전트의 다음 단계가 궁금하다면 한번 살펴볼 가치가 있다.

- **GitHub:** [multica-ai/multica](https://github.com/multica-ai/multica)
- **공식 사이트:** [multica.ai](https://multica.ai)
