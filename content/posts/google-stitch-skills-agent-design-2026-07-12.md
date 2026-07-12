---
title: "구글이 디자인 에이전트 생태계를 열었다 — stitch-skills로 코딩 에이전트와 Stitch를 연결하는 법"
date: 2026-07-12
draft: false
tags:
  - google-stitch
  - ai-design
  - agent-skills
  - open-source
  - developer-tools
categories:
  - AI
  - Developer
description: "Google Labs가 stitch-skills 저장소를 공개했다. Stitch MCP 서버와 코딩 에이전트(Claude Code, Cursor, Codex, Gemini CLI, Antigravity)를 잇는 Agent Skills 모음이다. 디자인 생성부터 React 컴포넌트 변환, React Native, Remotion 영상까지 — 실제로 어떤 워크플로우가 만들어지는지 정리했다."
aliases:
  - /posts/google-stitch-skills-agent-design-2026-07-12
---

![Stitch Skills 워크플로우: 프롬프트 → 디자인 → 코드 → 실행 앱, 4컷 만화](/images/google-stitch-skills-agent-design-2026-07-12/stitch-skills-comic.png)

Google I/O 2025에서 Labs 실험으로 시작한 Stitch는, 2026년 3월 대규모 업데이트 이후 "AI 네이티브 디자인 캔버스"라는 포지셔닝을 굳혔다. 텍스트 프롬프트나 이미지만 넣으면 UI 화면을 만들어주고, HTML/CSS 코드를 뱉어낸다. 무료고, 사용량 제한도 없다. Figma 주가가 12% 하락했을 만큼 시장 반응도 컸다 (실제 품질은 "프로토타입용으로는 괜찮지만 클라이언트에게 보여주긴 아직" 수준이라는 20년 차 디자이너의 평도 있다).

그런데 디자인 도구가 아무리 좋아도, 코딩 에이전트와 연결되지 않으면 거기서 끝이다. 만들어진 디자인을 React 컴포넌트로 바꾸고, 디자인 시스템을 동기화하고, 코드를 수정해서 다시 디자인에 반영하는 — 이 "마지막 마일"을 누가接管할 것인가.

Google Labs의 대답은 [stitch-skills](https://github.com/google-labs-code/stitch-skills)다.

## 에이전트에게 디자인 감각을 가르치는 스킬 라이브러리

stitch-skills는 한마디로 **"코딩 에이전트가 Stitch와 대화하는 법을 가르쳐주는 스킬 팩"**이다. [Agent Skills](https://agentskills.io) 오픈 스탠다드를 따르며, Codex, Claude Code, Cursor, Gemini CLI, Antigravity와 호환된다. Stitch MCP 서버가 실행 중인 환경에서 동작한다.

스킬 구조는 깔끔하다. 각 스킬 디렉토리에 `SKILL.md`(미션 컨트롤), `scripts/`(검증·네트워킹 실행기), `resources/`(체크리스트·스타일 가이드), `examples/`(정답 예시)가 들어간. 에이전트가 이 디렉토리를 읽고, 문맥을 잡고, 실제로 스크립트를 실행하는 구조다.

세 개의 플러그인 카테고리로 나뉜다: **Design**, **Build**, **Utilities**. 하나씩 파보자.

## Design — 코드를 디자인으로, 프롬프트를 화면으로

`stitch-design` 플러그인은 핵심 디자인 워크플로우를 담당한다. 6개 스킬이 들어있다.

**`stitch::code-to-design`** 가 가장 흥미롭다. React나 Vue 같은 프론트엔드 코드를 Stitch 디자인으로 역변환한다 — HTML 추출, 디자인 시스템 분석, Stitch 프로젝트 업로드까지 한 번에 처리한다. 기존 코드베이스를 Stitch로 가져와서 리디자인하고 싶을 때 쓴다.

> "Upload the frontend code at /path/to/dashboard into a Stitch project named 'Dashboard-Migration-2026'."

이렇게 말하면 된다. 에이전트가 알아서 코드를 분석하고, 디자인 토큰을 뽑아내고, Stitch에 프로젝트를 만든다.

**`stitch::generate-design`** 는 텍스트나 이미지에서 새 화면을 생성하고, 기존 화면을 편집하고, 디자인 변형을 만든다. 다크모드 3종 변형을 한 번에 뽑는다거나, 로그인 화면에 "Remember Me" 체크박스를 추가한다거나 — 자연어로 디자인을 조작한다.

나머지 4개 스킬은 지원 역할이다:

- **`stitch::manage-design-system`**: `DESIGN.md`를 업로드하고 모든 화면에 테마를 적용
- **`stitch::extract-design-md`**: 프론트엔드 소스 코드에서 디자인 시스템을 자동 추출
- **`stitch::extract-static-html`**: 실행 중인 웹앱에서 CSS·이미지를 인라인한 정적 HTML 스냅샷을 추출
- **`stitch::upload-to-stitch`**: 로컬 에셋(이미지, 목업, HTML)을 Stitch 프로젝트에 업로드

## Build — 디자인을 프로덕션 코드로

`stitch-build` 플러그인은 디자인을 실제 코드로 바꾼다. 여기가 진짜 "마지막 마일"이다.

**`stitch::react-components`** 는 Stitch 화면을 React 컴포넌트 시스템으로 변환한다. 디자인 토큰 일관성 검증과 자동 validation이 붙어 있다. Stitch 프로젝트 ID만 주면, 최신 업데이트까지 동기화(sync)한다.

> "Sync the app to the last updates of the Stitch project 13039335308618232534."

**`stitch::react-native`** 는 같은 일을 React Native로 한다. StyleSheet와 플랫폼별 코드까지 생성한다. 모바일 앱 워크플로우에 바로 투입할 수 있다.

두 개 더:

- **`remotion`**: Stitch 프로젝트에서 walkthrough 영상을 만든다. Remotion으로 부드러운 전환과 줌 효과를 넣어 — 프로젝트 데모 영상이 필요할 때 유용하다.
- **`shadcn-ui`**: shadcn/ui 컴포넌트 통합에 특화된 가이드. 정렬·필터가 있는 데이터 테이블을 만들어야 할 때.

## Utilities — 프롬프트를 더 똑똑하게

`stitch-utilities`는 디자인 품질을 끌어올리는 보조 도구다.

- **`design-md`**: Stitch 프로젝트를 분석해서 종합 `DESIGN.md`를 생성
- **`enhance-prompt`**: "설정 페이지 만들어줘" 같은 모호한 프롬프트를 Stitch에 최적화된 프롬프트로 변환 — UI/UX 키워드를 보강한다
- **`stitch-loop`**: 단일 프롬프트에서 완성된 다중 페이지 웹사이트를 자동 생성. validation까지 포함
- **`taste-design`**: "프리미엄, 제네릭하지 않은" UI 기준을 강제하는 `DESIGN.md`를 생성. 타이포그래피 규칙과 보정된 색상까지

`enhance-prompt`와 `taste-design`은 조합해서 쓰면 좋다. 프롬프트를 다듬고, 디자인 기준을 세팅한 뒤에 생성을 돌리는 식이다.

## 실제 워크플로우: 프롬프트 하나로 앱을 만들 수 있는가

이 스킬들이 실제로 어떻게 연결되는지, 가상 시나리오를 만들어봤다.

**1단계 — 디자인 생성**: `stitch::generate-design`로 "로맨스 데이트 앱의 브라우즈 탭"을 만든다. Stitch가 화면을 생성한다.

**2단계 — 디자인 시스템 정의**: `taste-design`로 프리미엄 기준의 `DESIGN.md`를 생성하고, `stitch::manage-design-system`로 모든 화면에 적용한다.

**3단계 — 코드 변환**: `stitch::react-components`로 React 컴포넌트로 변환한다. 디자인 토큰이 코드의 theme 객체가 된다.

**4단계 — 영상 제작(선택)**: `remotion`으로 프로젝트 walkthrough 영상을 만든다. 투자자 피치나 팀 공유용이다.

물론 각 단계마다 에이전트가 Stitch MCP 서버와 통신해야 하므로, Stitch 계정과 MCP 설정이 전제다. [Stitch MCP Setup 문서](https://stitch.withgoogle.com/docs/mcp/setup/)를 따라 환경변수와 인증을 먼저 세팅해야 한다.

## 설치는 30초면 충분하다

가장 빠른 방법은 CLI 한 줄이다:

```bash
codex plugin marketplace add google-labs-code/stitch-skills --ref main \
  --sparse .agents/plugins \
  --sparse plugins/stitch-design \
  --sparse plugins/stitch-build \
  --sparse plugins/stitch-utilities
```

`--sparse` 플래그는 체크아웃 범위를 좁혀서 속도를 높인다. Claude Code나 Cursor를 쓴다면:

```bash
# Claude Code — 프로젝트 단위 설치
npx plugins add google-labs-code/stitch-skills --scope project --target claude-code

# Cursor — 워크스페이스 단위 설치
npx plugins add google-labs-code/stitch-skills --scope workspace --target cursor
```

개별 스킬만 골라서 설치할 수도 있다:

```bash
npx skills add google-labs-code/stitch-skills
```

주의할 점: Design 스킬들은 서로 의존성이 있다. 선택적으로 설치할 때는 의존 스킬까지 함께 넣어야 한다.

## Agent Skills 오픈 스탠다드가 의미하는 것

stitch-skills가 단순한 플러그인 모음 이상인 이유는, [Agent Skills](https://agentskills.io) 오픈 스탠다드를 따르고 있기 때문이다. 이 표준의 핵심 구조는:

```
skills/<skill-name>/
├── SKILL.md      — 에이전트의 "미션 컨트롤"
├── scripts/      — 검증·네트워킹 실행기
├── resources/    — 체크리스트·스타일 가이드
└── examples/     — 정답 예시
```

이 구조가 좋은 점은, 에이전트가 **문서를 읽고 맥락을 잡은 뒤 실제로 스크립트를 실행**한다는 거다. 단순히 API를 호출하는 게 아니라, 가이드라인을 이해하고 검증 단계를 거친다. 다른 도구에서도 같은 패턴으로 스킬을 만들 수 있다 — Agent Skills는 Google 독자 표준이 아니라 범용 오픈 스탠다드다.

## 그래서, 누가 써야 하나

stitch-skills는 이런 분에게 당장 유용하다:

- **프론트엔드 개발자**가 디자인 없이 프로토타입을 빠르게 만들어야 할 때 — Stitch에서 디자인을 생성하고, `react-components` 스킬로 바로 컴포넌트를 뽑는다
- **디자이너가 코드를 모를 때** — Stitch에서 디자인을 다듬고, 에이전트가 코드를 생성하게 둔다
- **에이전트 기반 워크플로우를 구축 중인 팀** — Agent Skills 표준을 따르는 레퍼런스 구현체로 활용할 수 있다

Google이 "디자인 도구"에서 끝나지 않고, 코딩 에이전트 생태계까지 스킬을 열었다는 것 자체가 방향성을 보여준다. 디자인과 코드의 경계가 MCP 한 단위로 녹아내리고 있다. Stitch 자체는 아직 베타이고 품질이 완벽하지 않지만, 이 스킬 라이브러리는 성숙하다 — 구조, 검증, 문서가 다 갖춰져 있다.

다음 단계는 직접 설치해보는 거다. Stitch 계정 만들고, MCP 설정하고, 코딩 에이전트에 스킬을 넣어보면 — "프롬프트에서 앱까지"가 얼마나 가까워졌는지 체감할 수 있다.
