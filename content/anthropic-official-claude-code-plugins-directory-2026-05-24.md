---
title: "Anthropic이 직접 관리하는 Claude Code 공식 플러그인 디렉토리 완전 정복"
date: 2026-05-24
tags: [claude-code, plugin, anthropic, ai-coding, devtools]
---

Claude Code의 플러그인 생태계가 어느덧 꽤 흥미로운 수준에 도달했습니다. Anthropic이 직접 운영하는 **claude-plugins-official** 리포지토리가 2,000스타를 돌파했고, 내부 플러그인 37개와 외부 파트너 플러그인 14개가 등록된 정식 디렉토리가 됐습니다. 이걸 어디서부터 어떻게 써야 할지, 인터뷰 형식으로 정리해봤습니다.

---

## Q1. Claude Code 플러그인이 뭔가요?

**A1.** Claude Code에 "능력"을 추가하는 모듈입니다. VS Code 확장과 비슷한 개념인데, 차이점은 플러그인이 명령어, 에이전트, MCP 서버, 스킬을 하나의 패키지로 묶어서 제공한다는 겁니다. 예를 들어 `code-review` 플러그인을 설치하면 코드 리뷰 전용 명령어와 프롬프트가 Claude Code에 통합됩니다.

구조는 간단합니다. `.claude-plugin/plugin.json`이 메타데이터고, 여기에 명령어는 `commands/`, 자율 에이전트는 `agents/`, 학습 가능한 지식은 `skills/`, MCP 서버 설정은 `.mcp.json`에 각각 들어갑니다.

---

## Q2. 내부 플러그인 37개가 있다는데, 어떤 게 있나요?

**A2.** 크게 몇 가지 카테고리로 나눌 수 있습니다.

**언어 서버(LSP) 플러그인** — 가장 많은 그룹입니다. `typescript-lsp`, `pyright-lsp`, `rust-analyzer-lsp`, `gopls-lsp`, `swift-lsp`, `kotlin-lsp`, `lua-lsp`, `php-lsp`, `ruby-lsp`, `csharp-lsp`, `clangd-lsp`, `jdtls-lsp`까지 12개 언어를 지원합니다. 설치하면 Claude Code가 해당 언어의 타입 정보, 정의로 이동, 참조 찾기를 실시간으로 활용할 수 있습니다.

**개발 워크플로우 플러그인** — `code-review`, `pr-review-toolkit`, `feature-dev`, `commit-commands`, `code-modernization`, `code-simplifier` 같은 실전 개발용 플러그인들입니다. 코드 리뷰부터 기능 개발, 리팩토링, 커밋 메시지 작성까지 개발 사이클 전체를 커버합니다.

**출력 스타일 플러그인** — `explanatory-output-style`과 `learning-output-style`이 있습니다. Claude Code의 응답을 교육적이거나 설명적인 톤으로 조정합니다. 튜토리얼을 쓰거나 팀원에게 설명할 때 유용합니다.

**MCP 관련 플러그인** — `mcp-server-dev`는 MCP 서버를 직접 개발할 때 쓰고, `mcp-tunnels`는 원격 MCP 서버에 터널링 연결을 만듭니다.

**보안 및 유틸리티** — `security-guidance`는 보안 모범 사례를 적용하고, `session-report`는 세션 활동 리포트를 생성합니다. `hookify`는 Claude Code 훅을 쉽게 관리합니다.

**개발자 도구** — `plugin-dev`, `example-plugin`, `playground`는 플러그인 자체를 만들 때 사용합니다. `agent-sdk-dev`는 Agent SDK 기반 커스텀 에이전트 개발용입니다.

---

## Q3. 외부 파트너 플러그인은요?

**A3.** 14개 외부 플러그인이 공식 디렉토리에 등록되어 있습니다. 눈에 띄는 것들만 꼽으면:

- **GitHub / GitLab** — PR, 이슈, 코드 리뷰를 Claude Code 안에서 직접
- **Playwright** — 브라우저 자동화 테스트를 자연어로
- **Asana / Linear** — 프로젝트 관리 도구와 연동
- **Discord / Telegram / iMessage** — 메시징 플랫폼 연동
- **Firebase** — Firebase 프로젝트 관리
- **Terraform** — 인프라스트럭처 as Code 워크플로우
- **Context7** — 컨텍스트 관리 최적화

외부 플러그인을 디렉토리에 등록하려면 [clau.de/plugin-directory-submission](https://clau.de/plugin-directory-submission)에서 제출하면 됩니다.

---

## Q4. 설치는 어떻게 하나요?

**A4.** 두 가지 방법이 있습니다.

방법 1 — 명령어로 직접 설치:
```
/plugin install code-review@claude-plugins-official
```

방법 2 — UI에서 검색:
```
/plugin > Discover
```
`Discover` 메뉴에서 전체 디렉토리를 브라우징하고 원하는 플러그인을 선택할 수 있습니다.

설치 후에는 플러그인이 제공하는 명령어가 자동으로 `/` 명령어 목록에 나타납니다.

---

## Q5. 직접 플러그인을 만들 수도 있나요?

**A5.** 네, 가능합니다. 최소 구조는 다음과 같습니다:

```
my-plugin/
  .claude-plugin/
    plugin.json    # 이름, 버전, 설명
  .mcp.json        # MCP 서버 설정 (선택)
  commands/        # 커스텀 명령어
  agents/          # 자율 에이전트
  skills/          # 학습 가능한 지식
```

`plugin-dev` 플러그인을 설치하면 플러그인 개발용 템플릿과 가이드가 제공됩니다. `example-plugin`도 참고하기 좋습니다. 만들고 나서 공식 디렉토리에 등록까지 노려볼 만합니다.

---

## Q6. 실전 팁이 있나요?

**A6.** 몇 가지 정리해봅니다.

**먼저 LSP 플러그인부터.** 본인이 주로 쓰는 언어의 LSP 플러그인은 무조건 설치하세요. 타입 추론과 코드 네비게이션이 활성화되면 Claude Code의 정확도가 체감 수준으로 올라갑니다.

**프로젝트에 맞춰 조합.** 웹 개발이면 `typescript-lsp` + `code-review` + `commit-commands` 조합이 기본이고, 여기에 `frontend-design`을 추가할 수도 있습니다. 인프라 담당이면 `rust-analyzer-lsp` + `terraform` + `security-guidance`를 고려해보세요.

**출력 스타일은 상황에 따라.** 평소 코딩할 때는 기본 출력이 낫고, 문서를 쓰거나 코드베이스를 학습할 때는 `explanatory-output-style`이나 `learning-output-style`을 켜두면 좋습니다.

**플러그인은 가볍게 시작.** 처음부터 다 설치할 필요 없습니다. 하나씩 추가하면서 어떤 변화가 있는지 체감해보세요. Claude Code의 `/plugin` 명령어로 설치와 제거가 모두 간단합니다.

---

## 마무리

Claude Code 플러그인 시스템은 "확장 가능한 AI 코딩 환경"을 향한 Anthropic의 분명한 방향성을 보여줍니다. 특히 공식 리포지토리를 중앙 디렉토리로 운영하면서 품질 관리와 커뮤니티 생태계를 동시에 잡는 접근이 흥미롭습니다. 아직 초기라 모든 플러그인이 완성도가 높지는 않지만, 생태계가 성숙해지는 속도가 빠릅니다. 지금이 탐색하기 좋은 타이밍입니다.
