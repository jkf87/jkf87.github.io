---
title: "n8n-MCP: AI가 n8n 워크플로우를 대신 짜주는 시대가 왔다"
slug: "n8n-mcp-ai-workflow-automation-2026-05-05"
date: 2026-05-05
tags:
  - n8n
  - MCP
  - AI자동화
  - 워크플로우
  - Claude
  - 업무자동화
  - ModelContextProtocol
description: "n8n의 1,650개 노드를 AI가 이해하고 대신 워크플로우를 짜준다면? n8n-MCP가 그 다리 역할을 한다. 설치부터 실전 활용까지 정리했다."
aliases:
  - n8n-mcp-ai-workflow-automation-2026-05-05/index
draft: false
cover: images/n8n-mcp-ai-workflow-automation-2026-05-05/thumbnail.jpg
---

![n8n-MCP 4컷 요약 — AI가 n8n 워크플로우를 대신 짜주는 시대](images/n8n-mcp-ai-workflow-automation-2026-05-05/thumbnail.jpg)

## 1,650개 노드, 어디서 시작해야 할까

[n8n](https://github.com/n8n-io/n8n)은 오픈소스 워크플로우 자동화 도구다. Slack 메시지를 받아 Google Sheets에 기록하고, webhook으로 외부 API를 호출하고, AI 에이전트를 돌려 이메일을 자동 분류한다. 할 수 있는 일은 무한한데, 문제는 하나다.

**노드가 너무 많다.**

핵심 노드 820개, 커뮤니티 노드 830개. 합치면 1,650개다. 각 노드마다 속성이 있고, 오퍼레이션이 있고, 필수 파라미터가 있다. "Slack에 메시지 보내기" 하나만 해도 `resource`, `operation`, `select`, `channelId`, `text`를 다 설정해야 한다. 디폴트 값을 믿었다간 런타임 에러가 터진다.

그래서 등장한 게 **n8n-MCP**다.

## n8n-MCP가 뭔가

[n8n-MCP](https://github.com/czlonkowski/n8n-mcp)는 **Model Context Protocol(MCP) 서버**다. AI 모델(Claude, Cursor, Windsurf 등)이 n8n의 모든 노드 문서, 속성, 오퍼레이션, 템플릿을 실시간으로 조회할 수 있게 해준다.

간단히 말해:

> AI에게 "n8n으로 Slack→Google Sheets 워크플로우 만들어줘"라고 말하면, AI가 n8n-MCP를 통해 정확한 노드 설정값을 찾아서, 검증까지 거쳐서 완성된 워크플로우 JSON을 내어준다.

### 숫자로 보는 규모

| 항목 | 수치 |
|------|------|
| n8n 노드 | 1,650개 (코어 820 + 커뮤니티 830) |
| 노드 속성 커버리지 | 99% |
| 오퍼레이션 커버리지 | 63.6% |
| 공식 문서 커버리지 | 87% |
| AI 툴 변형 | 265개 |
| 실전 예시 | 156개 (템플릿에서 추출) |
| 워크플로우 템플릿 | 2,352개 |
| 테스트 | 5,418개 통과 |

## 어떻게 작동하나

### 핵심 도구 7개

1. **`search_nodes`** — 노드 전문 검색. `includeExamples: true`로 실제 설정값까지 가져온다
2. **`get_node`** — 특정 노드의 상세 정보. 문서 모드, 속성 검색 모드, 버전 비교 모드 지원
3. **`validate_node`** — 노드 설정값 검증. 최소 검사(<100ms)와 전체 검사 지원
4. **`validate_workflow`** — 워크플로우 전체 검증. 연결, 표현식, AI 에이전트까지
5. **`search_templates`** — 2,352개 템플릿 검색. 키워드, 노드 타입, 태스크, 메타데이터 필터
6. **`get_template`** — 템플릿 전체 JSON 가져오기
7. **`tools_documentation`** — 각 MCP 툴의 사용법 문서

### n8n 관리 도구 13개 (API 연동 시)

n8n 인스턴스의 API 키를 설정하면 더 강력해진다:

- **워크플로우 관리**: 생성, 조회, 업데이트, 삭제, 부분 업데이트(diff 방식)
- **실행 관리**: 테스트 실행, 실행 이력 조회
- **자격증명 관리**: CRUD + 스키마 조회
- **보안 감사**: n8n 내장 감사 API + 워크플로우 심층 스캔
- **자동 수정**: `n8n_autofix_workflow`로 일반적인 에러 자동 교정

## Q: 그냥 AI한테 물어보면 안 되나?

안 된다. n8n 노드의 필수 파라미터는 버전마다 바뀐다. Claude가 학습한 시점의 n8n 지식과 현재 버전의 n8n은 다르다. 예를 들어보자.

**AI가 디폴트를 믿고 짠 설정:**
```json
{
  "resource": "message",
  "operation": "post",
  "text": "Hello"
}
```

**실제로 작동하는 설정:**
```json
{
  "resource": "message",
  "operation": "post",
  "select": "channel",
  "channelId": "C123",
  "text": "Hello"
}
```

`select`와 `channelId`가 빠지면 런타임에 에러가 난다. n8n-MCP는 **현재 버전의 스키마**를 실시간으로 제공하기 때문에 이런 문제가 안 생긴다.

## Q: 어떤 IDE에서 쓸 수 있나?

거의 다 된다:

- **Claude Code** — CLI 환경에서 바로 연동
- **VS Code** — GitHub Copilot과 함께 사용
- **Cursor** — 별도 설정 가이드 제공
- **Windsurf** — 프로젝트 룰과 연동
- **Codex** — 전용 설정 가이드
- **Antigravity** — 연동 가이드 제공

가장 빠른 시작은 **dashboard.n8n-mcp.com**이다. 가입하고 API 키 받으면 끝. 무료 티어는 하루 100회 툴 콜이다. 설치 없이 바로 시작할 수 있다.

셀프 호스팅을 원하면 `npx`, Docker, Railway 등으로 직접 띄울 수도 있다.

## Q: 실제 워크플로우 작성 흐름은?

n8n-MCP가 권장하는 워크플로우를 따라가보자.

### 1단계: 템플릿 먼저 찾는다

2,352개 템플릿에서 먼저 찾는다. 바닥부터 짜는 건 최후의 수단이다.

```
search_templates({searchMode: 'by_task', task: 'webhook_processing'})
```

### 2단계: 노드를 찾는다

적합한 템플릿이 없으면 노드를 검색한다.

```
search_nodes({query: 'slack notification', includeExamples: true})
```

### 3단계: 설정값을 확인한다

```
get_node({nodeType: 'n8n-nodes-base.slack', detail: 'standard', includeExamples: true})
```

### 4단계: 검증한다

2단계 검증을 거친다:

```
validate_node({nodeType, config, mode: 'minimal'})  // 필수 필드만 빠르게
validate_node({nodeType, config, mode: 'full', profile: 'runtime'})  // 전체 검증
```

### 5단계: 워크플로우를 완성한다

모든 노드가 검증을 통과하면 조립하고, 전체 워크플로우를 한 번 더 검증한다:

```
validate_workflow(workflow)
```

### 6단계: 배포한다 (선택)

n8n API가 연동되어 있으면 바로 배포까지:

```
n8n_create_workflow(workflow)
n8n_test_workflow({workflowId})
```

## Q: 주의할 점은?

**프로덕션 워크플로우를 AI로 직접 편집하지 마라.** n8n-MCP README에도 경고가 있다. 반드시:

1. 워크플로우 복사본을 먼저 만든다
2. 개발 환경에서 테스트한다
3. 중요 워크플로우는 백업을 export 해둔다
4. 프로덕션 배포 전에 변경사항을 검증한다

AI 결과는 예측 불가능할 수 있다. 보호는 기본이다.

## 누가 만들었나

[Cole Zlonkowksi](https://github.com/czlonkowksi)가 개인 프로젝트로 시작했다. 지금은 수만 명의 개발자가 사용하는 오픈소스 도구가 됐다. MIT 라이선스로 공개되어 있고, [npm 패키지](https://www.npmjs.com/package/n8n-mcp)와 [Docker 이미지](https://github.com/czlonkowksi/n8n-mcp/pkgs/container/n8n-mcp) 모두 제공한다.

## 왜 주목해야 하나

n8n-MCP는 **"AI가 도구를 이해하는 방식"**을 표준화한 사례다. MCP(Model Context Protocol)는 Anthropic이 제안한 프로토콜로, AI 모델이 외부 도구의 컨텍스트를 구조적으로 이해할 수 있게 한다. n8n-MCP는 이 프로토콜을 n8n이라는 구체적인 도구에 적용한 것이다.

앞으로는 More tools, more integrations가 MCP 서버 형태로 계속 나올 것이다. n8n-MCP는 그 선두주자 중 하나다.

**핵심은 이거다:** AI에게 "이렇게 해줘"라고 말하는 시대에서, AI가 "이 도구의 문서를 읽고, 검증하고, 안전하게 만들어줄게"라고 하는 시대로 넘어가고 있다. n8n-MCP가 그 전환을 실제로 보여주고 있다.

---

**관련 링크**
- GitHub: <https://github.com/czlonkowksi/n8n-mcp>
- 대시보드: <https://dashboard.n8n-mcp.com>
- npm: <https://www.npmjs.com/package/n8n-mcp>
- n8n 공식: <https://github.com/n8n-io/n8n>
