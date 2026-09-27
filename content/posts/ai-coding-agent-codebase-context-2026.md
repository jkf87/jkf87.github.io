---
title: "AI 코딩 에이전트가 큰 레포에서 헤맬 때: 지식 그래프·LSP 플러그인·터미널 8편 통합 가이드"
date: 2026-09-27
author: 한준구(코난쌤)
description: "AI 코딩 에이전트가 큰 레포에서 토큰을 태우는 문제를 지식 그래프 3종(CodeGraph·GitNexus·Understand Anything)과 LSP 플러그인·Chrome DevTools MCP·cmux로 비교 정리했습니다. 라이선스·스타·미니 재현은 2026-09-27 직접 확인했습니다."
tags: [ai-coding-agent, knowledge-graph, claude-code, mcp, devtools]
refactor_hub_id: coding-agents-05
aliases:
  - cmux-yc-s24-terminal-ai-agents-2026-04-26
  - gitnexus-knowledge-graph-code-agents-2026-04-27
  - understand-anything-interactive-knowledge-graph
  - anthropic-nla-natural-language-autoencoders-2026-05-11
  - anthropic-official-claude-code-plugins-directory-2026-05-24
  - chrome-devtools-mcp-coding-agents-2026-05-24
  - codegraph-pre-indexed-code-knowledge-graph-2026-05-24
  - understand-anything-codebase-knowledge-graph-2026-05-26
draft: false
---

## 한눈에 보는 결론

큰 레포에서 AI 코딩 에이전트를 돌리면 비슷한 장면이 반복됩니다. 에이전트가 find → grep → Read를 몇십 번 돌리고, 토큰과 시간을 태우다가 엉뚱한 파일을 손댑니다. 콜체인이나 의존성 같은 <span style="background-color: #fff59d"><strong>관계 정보는 텍스트 유사도 검색으로 안 보이기</strong></span> 때문입니다.

이 글은 그 문제를 다룬 이전 글 8편을 하나로 합친 통합 가이드입니다. 핵심은 이겁니다. 컨텍스트 문제를 모델 업그레이드로 풀기 전에, 파이프라인으로 미리 싸게 풀 수 있는 단계가 있습니다.

검증된 수치부터 보시면 됩니다. 사전 색인 그래프인 CodeGraph를 붙였을 때 같은 질문의 <span style="background-color: #fff59d"><strong>툴 콜이 14~43회에서 1~4회로</strong></span> 줄었습니다(2026-08-05 재측정, Claude Opus 4.8 headless, 4회 실행 중앙값).

<span style="background-color: #fff59d"><strong>처리 토큰은 7개 레포 평균 62% 내려갔습니다</strong></span>. 대신 세션이 끝난 뒤 컨텍스트 창에 남는 검색 컨텍스트는 <span style="background-color: #fff59d"><strong>약 80% 더 큽니다</strong></span>. 공짜가 아닙니다.

| 도구 | 계층 | 한 줄 결론 | 라이선스(2026-09-27 확인) |
|---|---|---|---|
| CodeGraph | 맥락 | 사전 색인 그래프로 툴 콜 1~4회 | MIT |
| GitNexus | 맥락 | MCP 도구+훅으로 그래프 자동 주입 | PolyForm-NC(비상업) |
| Understand Anything | 맥락 | 사람 온보딩용 대시보드 그래프 | MIT |
| Claude Code 공식 플러그인 | 도구 | LSP 중심, 내부 39+외부 14 | Apache-2.0(저장소) |
| Chrome DevTools MCP | 도구 | 에이전트가 실제 Chrome을 검사 | Apache-2.0 |
| cmux | 운영 | 에이전트 수십 개 동시 운영 터미널 | GPL-3.0-or-later |
| NLA(Anthropic) | 검증 | 모델 내면 활성화를 텍스트로 읽기 | 논문·코드 공개 |

![AI 코딩 에이전트 작업 환경의 4개 계층](../media/ai-coding-agent-codebase-context-2026/chart-01-context-stack-2026-09-27.png)

## 무엇을 비교했나

2026년 4~5월에 따로 썼던 글 8편을 합쳤습니다. 이번 통합 작업에서 원문을 1차 출처로 다시 확인했고, 스타 수와 라이선스가 달라진 부분은 2026-09-27 기준으로 바로잡았습니다.

1. [cmux](https://github.com/manaflow-ai/cmux) — 에이전트 수십 개를 띄우는 macOS 터미널. <span style="background-color: #fff59d"><strong>알림 링</strong></span>과 사이드바(브랜치·PR·포트)로 "어느 에이전트가 멈췄는지"를 보여줍니다.
2. [GitNexus](https://github.com/abhigyanpatwari/GitNexus) — 레포 전체를 지식 그래프로 색인해 MCP 서버로 돌려주는 엔진. 변경 영향 분석(impact)이 중심입니다.
3. [Understand Anything](https://github.com/Egonex-AI/Understand-Anything) — <span style="background-color: #fff59d"><strong>Tree-sitter+LLM 하이브리드</strong></span>로 코드베이스를 대화형 그래프로 바꾸는 플러그인. 사람 온보딩·문서화 용도입니다.
4. [Natural Language Autoencoders](https://www.anthropic.com/research/natural-language-autoencoders) — Anthropic의 해석 기술. 모델 활성화를 텍스트로 바꿔 읽습니다. 에이전트 출력을 어디까지 믿을지 판단하는 계층입니다.
5. [Claude Code 공식 플러스인 디렉토리](https://github.com/anthropics/claude-plugins-official) — Anthropic이 직접 관리. <span style="background-color: #fff59d"><strong>내부 39 + 외부 14</strong></span>(2026-09-27 실측).
6. [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) — 에이전트가 실제 Chrome을 검사·제어합니다. 프론트엔드 디버깅용입니다.
7. [CodeGraph](https://github.com/colbymchenry/codegraph) — 사전 색인 코드 지식 그래프. 파일 변경을 <span style="background-color: #fff59d"><strong>자동 동기화</strong></span>합니다.
8. Understand Anything 파이프라인 분석 — 3번과 같은 도구의 설계 분석 글. 결정론적 구조(Tree-sitter)와 시맨틱(LLM)의 역할 분리를 다룹니다.

4개 계층으로 읽으면 정리가 됩니다. 맥락 계층(무엇을 보여줄까), 도구 계층(에이전트의 손과 눈), 운영 계층(동시에 몇 개를 돌릴까), 검증 계층(무엇을 믿을까). 위 차트가 그 구조입니다.

## 방법 비교

| 도구 | 해결하는 문제 | 핵심 방법 | 근거·데이터 | 비용·라이선스 | 확인된 한계 |
|---|---|---|---|---|---|
| CodeGraph | 탐색에 토큰 태움 | .codegraph SQLite 색인+파일 와처 | 7레포 벤치마크(토큰 62%↓) | MIT, 100% 로컬 | 잔류 컨텍스트 +80% |
| GitNexus | 변경 영향 놓침 | 17개 MCP 도구+PreToolUse 훅 | README 설계 문서 | PolyForm-NC | 상업 사용 별도 계약 |
| Understand Anything | 사람이 구조 파악 못 함 | Tree-sitter 구조+LLM 요약 | README+라이브 데모 | MIT | 그래프 10MB 이상 git-lfs 권장 |
| 공식 플러그인 | 타입 정보 부재 | LSP 서버 연결 | 디렉토리 실측 39+14 | 무료 | 플러그인별 완성도 편차 |
| Chrome DevTools MCP | 실행 결과 미관측 | 실제 Chrome 제어(CDP) | 공식 문서 | Apache-2.0 | Chrome 계열 브라우저만 |
| cmux | 동시 운영 혼란 | 알림 링+워크스페이스 사이드바 | README | GPL-3.0+, 무료 | macOS 전용 |
| NLA | 모델 내면 불투명 | 활성화→텍스트→재구성 왕복 학습 | 논문 본문 | 코드·모델 공개 | 환각(confabulation), 비용 |

맥락 계층 셋을 같은 축으로 보면 차이가 보입니다. CodeGraph는 "탐색 토큰을 줄인다", GitNexus는 "변경 전에 영향을 본다", Understand Anything은 "사람이 구조를 읽게 한다"입니다. 같은 그래프라도 <span style="background-color: #fff59d"><strong>소비자가 에이전트냐 사람이냐</strong></span>에 따라 설계가 갈립니다.

도구 계층 둘은 보완 관계입니다. LSP 플러그인은 정적 타입 정보를, Chrome DevTools MCP는 실행 중인 브라우저를 관측합니다. 운영 계층(cmux)과 검증 계층(NLA)은 앞의 세 계층이 커질수록 필요해지는 인프라입니다.

## 언제 무엇을 쓰나

- 에이전트가 큰 레포에서 헤매면: <span style="background-color: #fff59d"><strong>주 언어 LSP 플러그인 먼저</strong></span>, 그다음 CodeGraph init(MIT, 로컬). 설치가 간단한 순서대로입니다.
- 회사 상용 코드면: GitNexus는 PolyForm-NC라 개인 학습·사이드 프로젝트만 가능. 회사 코드엔 CodeGraph(MIT)를 쓰면 됩니다.
- 새 팀원 온보딩 자료나 아키텍처 문서가 목적이면: Understand Anything에 --language ko.
- 프론트엔드 "버튼 눌러도 반응 없음"류 디버깅: chrome-devtools-mcp. 민감한 환경이면 --no-performance-crux.
- 에이전트 5개 이상을 동시에 돌리는 단계: cmux(macOS).
- 벤치마크 점수를 근거로 에이전트를 골라야 하는 자리: NLA류 내면 관측 결과가 있다면 참고 자료로. 아직 연구 도구입니다.

## 블로그봇이 직접 확인한 것

검증일 2026-09-27, macOS 26.5.1(M2 Max 32GB). GitHub API, npm registry, sqlite3, raw README를 curl로 직접 확인했습니다.

#### 저장소·라이선스 실측(GitHub API)

```text
$ curl -s https://api.github.com/repos/<owner>/<repo>
manaflow-ai/cmux              27,427★  GPL-3.0-or-later
abhigyanpatwari/GitNexus      47,606★  PolyForm-NC
Egonex-AI/Understand-Anything 84,300★  MIT
```

지식 그래프 계열 셋의 규모가 이렇습니다. 관측·운영 쪽도 같은 방식으로 확인했습니다.

```text
ChromeDevTools/chrome-devtools-mcp   52,648★  Apache-2.0
colbymchenry/codegraph               72,150★  MIT
anthropics/claude-plugins-official   37,067★  Apache-2.0
```

원문 발행 뒤 달라진 것들입니다. <span style="background-color: #fff59d"><strong>Understand Anything 저장소가 Lum1104에서 Egonex-AI로 이동</strong></span>했습니다(301 리다이렉트 확인).

GitNexus는 한 달 만에 30k★였던 스타가 47.6k★로, MCP 도구도 16개에서 <span style="background-color: #fff59d"><strong>17개(15 per-repo + 2 group)</strong></span>로 늘었습니다. 공식 플러그인 디렉토리는 내부 37개였던 게 39개로 늘었고 외부 14개는 그대로입니다(contents API로 직접 카운트).

#### npm 패키지 실측

```text
chrome-devtools-mcp@1.10.1        Apache-2.0
gitnexus@1.6.12                   PolyForm-Noncommercial-1.0.0
@colbymchenry/codegraph@1.6.0     MIT
```


#### CodeGraph 미니 재현

auth.py·orders.py·payments.py 세 파일짜리 토이 레포를 만들고 init을 돌렸습니다.

```text
$ npx -y @colbymchenry/codegraph@latest init
◆  Initialized in .../cg-test
Scanning files...  Parsing code...  Resolving refs...
◆  Indexed 3 files
●  10 nodes, 12 edges in 1.0s
```


색인 결과물은 SQLite 파일(.codegraph/codegraph.db)입니다. 노드 테이블을 조회하니 function 5개, file 3개, import 2개가 잡혀 있었습니다.

login→token_for→create_order 같은 호출 관계가 엣지로 들어가 있었습니다. <span style="background-color: #fff59d"><strong>3파일 기준 색인 1.0초</strong></span>, 로컬에서만 동작합니다. 대형 레포 재현은 이번 실행 범위 밖입니다.

#### NLA 논문 본문 확인

Anthropic 연구 페이지와 transformer-circuits 논문 본문을 직접 읽었습니다. 확인된 서술은 이렇습니다.

Opus 4.6 사전 배포 감사에서 <span style="background-color: #fff59d"><strong>드러내지 않으면서 평가라고 의심하는 내면 상태(unverbalized evaluation awareness)</strong></span>가 관측됐습니다. 의도적으로 잘못 정렬시킨 모델의 원인을 찾는 오디팅 과제에서 NLA 장착 에이전트가 베이스라인보다 잘했고, 훈련 데이터 접근 없이도 가능했다는 서술도 확인했습니다.

이전 글에 있던 세부 백분율은 이번 재확인 범위 밖이라 이 통합본에서는 뺐습니다.

![CodeGraph README 벤치마크(2026-08-05 재측정)를 도식화한 차트](../media/ai-coding-agent-codebase-context-2026/chart-02-codegraph-benchmark-2026-09-27.png)

## 한계와 반론

- 잔류 컨텍스트: CodeGraph는 처리 토큰은 줄이지만 세션 뒤 창에 남는 컨텍스트가 약 80% 더 큽니다(VS Code 기준 67k vs 18k 토큰). 긴 세션·작은 창이면 이 비용이 이득을 넘을 수 있습니다. 출처는 README 자체 실험입니다.
- 직접 질문할 때만 효과: README에 <span style="background-color: #fff59d"><strong>CodeGraph only helps when queried directly</strong></span>라고 명시돼 있습니다. 서브에이전트가 알아서 파일을 읽게 두면 그래프는 오버헤드가 됩니다.
- 벤치마크 독립성: CodeGraph 수치는 자체 측정입니다(오염 확인 0/28은 보고됨). 제3자 재현은 이번에 찾지 못했습니다.
- GitNexus 라이선스: PolyForm Noncommercial는 회사 사용 금지 조건입니다. 기업 환경 도입 시 별도 상용 계약이 필요합니다.
- NLA 한계: 논문 스스로 <span style="background-color: #fff59d"><strong>confabulation</strong></span>(그럴듯한 지어내기)을 한계로 적습니다. 단일 주장을 그대로 믿지 말고 테마로 읽으라고 권합니다.
- cmux는 macOS 전용입니다. 이 머신이 macOS라 설치·문서 확인은 가능했지만 Linux/Windows 운영은 검증하지 못했습니다.
- 제 재현은 3파일 토이입니다. 10k 파일급 레포의 색인 시간·메모리는 측정하지 않았습니다.

## 적용 규칙

1. 도입 순서를 지키세요. LSP 플러그인 → 사전 색인 그래프 → 관측 도구 → 운영 도구 순이 저비용·고천력 순입니다.
2. 큰 레포라면 CodeGraph init을 먼저 돌려보면 됩니다(MIT, 100% 로컬). 텔레메트리가 걱정이면 `codegraph telemetry off`.
3. 긴 멀티턴 세션이거나 컨텍스트 창이 작으면 잔류 컨텍스트(+80%)를 예산에 넣으세요.
4. 회사 코드에는 GitNexus를 쓰지 마세요(PolyForm-NC). 개인 학습용입니다.
5. GitNexus로 큰 레포를 색인할 때는 --skip-embeddings로 시작하세요. 임베딩은 옵트인입니다.
6. 온보딩 문서가 목적이면 Understand Anything --language ko로 생성하고 그래프 JSON을 깃에 커밋해 팀과 공유하세요. 10MB를 넘으면 git-lfs.
7. 민감한 환경에서 chrome-devtools-mcp를 쓸 때는 <span style="background-color: #fff59d"><strong>--no-performance-crux</strong></span>와 Chrome for Testing 프로필을 같이 쓰세요.
8. 에이전트를 여러 개 돌리기 시작하면 알림 흐름부터 정리하세요. cmux의 알림 링·사이드바가 그 문제를 직접 겨냥합니다(macOS).

## 자주 묻는 질문

### 큰 레포에서 에이전트가 헤맬 때 먼저 까는 조합

Q. Claude Code가 몇천 파일짜리 레포에서 금방 토큰을 태웁니다. 뭘 먼저 깔아야 하나요?

주 언어의 LSP 플러그인 먼저, 그다음 CodeGraph init입니다. 둘 다 설치 한 줄이고 로컬에서 돕니다. 벤치마크에서 툴 콜이 1~4회로 줄어든 게 확인된 조합입니다.

### CodeGraph와 GitNexus 고르는 기준

Q. 둘 다 코드 지식 그래프라고 하던데요. 어떤 기준으로 고르나요?

라이선스가 갈립니다. CodeGraph는 MIT라 상업 프로젝트에도 쓸 수 있고, GitNexus는 PolyForm-NC라 개인 학습 전용입니다. 파일 변경 자동 동기화가 기본인 쪽은 CodeGraph, MCP 훅으로 그래프를 강제 주입하는 쪽은 GitNexus입니다.

### 지식 그래프 도입의 단점

Q. 토큰 62% 절감이라고 하던데요. 단점은 없나요?

잔류 컨텍스트가 약 80% 더 큽니다. 처리량은 줄어도 창에 남는 양은 늘어납니다. 짧은 세션이거나 창이 크면 체감이 작고, 긴 멀티턴 세션이면 컨텍스트 예산을 짜야 합니다.

### 에이전트 여러 개 알림 관리

Q. Claude Code 5개를 띄워놨는데 멈춘 걸 못 찾겠습니다. 어떻게 관리하나요?

macOS라면 cmux입니다. 알림 링과 사이드바(브랜치·PR·포트)가 그 문제를 직접 겨냥합니다. 다른 OS면 tmux와 알림 스크립트 조합이 대안입니다.

## 참고 자료

- [manaflow-ai/cmux (GitHub)](https://github.com/manaflow-ai/cmux) · [cmux.com](https://cmux.com)
- [abhigyanpatwari/GitNexus (GitHub)](https://github.com/abhigyanpatwari/GitNexus)
- [Egonex-AI/Understand-Anything (GitHub)](https://github.com/Egonex-AI/Understand-Anything) · [라이브 데모](https://understand-anything.com/demo/)
- [colbymchenry/codegraph (GitHub)](https://github.com/colbymchenry/codegraph)
- [anthropics/claude-plugins-official (GitHub)](https://github.com/anthropics/claude-plugins-official)
- [ChromeDevTools/chrome-devtools-mcp (GitHub)](https://github.com/ChromeDevTools/chrome-devtools-mcp) · [npm](https://www.npmjs.com/package/chrome-devtools-mcp)
- [Natural Language Autoencoders (Anthropic)](https://www.anthropic.com/research/natural-language-autoencoders) · [논문](https://transformer-circuits.pub/2026/nla/index.html) · [학습 코드](https://github.com/kitft/natural_language_autoencoders)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
