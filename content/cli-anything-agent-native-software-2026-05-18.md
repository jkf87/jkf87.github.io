---
title: "CLI-Anything — 모든 소프트웨어를 AI 에이전트 네이티브로 만드는 오픈소스"
date: 2026-05-18
tags:
  - AI
  - 에이전트
  - CLI
  - 오픈소스
  - ClaudeCode
  - OpenClaw
  - 자동화
  - HKUDS
description: "HKUDS가 만든 CLI-Anything은 명령 한 줄로 어떤 소프트웨어든 AI 에이전트가 제어할 수 있는 CLI로 변환한다. 38개 앱, 2,280개 테스트 전통과. Claude Code, OpenClaw, Codex 등 다양한 에이전트 플랫폼을 지원한다."
publishDate: 2026-05-18
github: https://github.com/HKUDS/CLI-Anything
---

# CLI-Anything — 모든 소프트웨어를 AI 에이전트 네이티브로

> **오픈소스:** <https://github.com/HKUDS/CLI-Anything>
> **개발:** HKUDS (홍콩대 데이터사이언스 연구실) | **라이선스:** Apache 2.0

![CLI-Anything Teaser](/static/cli-anything-images/teaser.jpg)

---

## 왜 주목해야 하나?

오늘날 대부분의 소프트웨어는 인간이 GUI로 조작하도록 설계되어 있다. 하지만 AI 에이전트 시대가 오면서 상황이 바뀌고 있다 — 에이전트가 소프트웨어를 직접 제어할 수 있어야 한다. CLI-Anything은 이 간극을 메우는 프로젝트다.

**핵심 아이디어:** 소프트웨어의 코드베이스를 분석해서, AI 에이전트가 사용할 수 있는 완전한 CLI 인터페이스를 자동 생성한다.

---

## 왜 CLI인가?

CLI는 인간과 AI 에이전트 모두를 위한 보편적 인터페이스다:

- **구조적 & 조합 가능** — 텍스트 명령은 LLM 포맷과 자연스럽게 맞물리고, 복잡한 워크플로우를 체이닝할 수 있다
- **가볍고 범용적** — 최소 오버헤드, 의존성 없이 모든 시스템에서 동작
- **자기 서술적** — `--help` 플래그가 에이전트가 자동 탐색할 수 있는 문서를 제공
- **검증된 성공** — Claude Code가 매일 수천 개의 실제 워크플로우를 CLI로 실행
- **결정론적 & 안정적** — 일관된 결과로 예측 가능한 에이전트 행동 보장

---

## 작동 원리 — 7단계 자동 파이프라인

![Architecture](/static/cli-anything-images/architecture.jpg)

단 한 줄의 명령으로 전체 파이프라인이 실행된다:

```bash
/cli-anything ./gimp
```

이 한 줄이 다음 7단계를 자동으로 수행한다:

### 1. 🔍 Analyze (분석)
소스 코드를 스캔하고 GUI 액션을 API로 매핑한다.

### 2. 📐 Design (설계)
명령 그룹, 상태 모델, 출력 포맷을 아키텍처링한다.

### 3. 🔨 Implement (구현)
Click 기반 CLI를 REPL, JSON 출력, undo/redo와 함께 빌드한다.

### 4. 📋 Plan Tests (테스트 계획)
단위 + E2E 테스트 계획을 담은 TEST.md를 생성한다.

### 5. 🧪 Write Tests (테스트 작성)
포괄적인 테스트 스위트를 구현한다.

### 6. 📝 Document (문서화)
테스트 결과로 TEST.md를 업데이트한다.

### 7. 📦 Publish (배포)
`setup.py`를 만들고 PATH에 설치한다.

초기 빌드 후에는 `refine` 명령으로 반복적으로 개선할 수 있다:

```bash
# 전체 리파인먼트
/cli-anything:refine ./gimp

# 특정 기능에 집중
/cli-anything:refine ./gimp "이미지 배치 처리와 필터"
```

---

## 실제 데모 — 에이전트가 만드는 실제 산출물

### FreeCAD — 퀴리어시티 로버

![FreeCAD Demo](/static/cli-anything-images/freecad-demo.jpg)

에이전트가 프리뷰, 라이브 프리뷰, 트래젝토리 기록을 사용하면서 퀴리어시티 스타일 로버를 점진적으로 조립한다.

### Blender — 궤도 릴레이 드론

![Blender Demo](/static/cli-anything-images/blender-demo.jpg)

에이전트가 Blender 하네스를 사용해 하드서페이스 궤도 릴레이 드론을 만든다. 각 단계에서 렌더 기반 프리뷰 번들을 푸시하고 트래젝토리로 명령-시각 상태를 연결한다.

### Draw.io — HTTPS 핸드셰이크 다이어그램

![Draw.io Demo](/static/cli-anything-images/drawio-demo.jpg)

에이전트가 TCP 3-way 핸드셰이크, TLS 협상, 암호화 데이터 교환, TCP 4-way 종료까지 전체 HTTPS 연결 수명주기 다이어그램을 CLI 명령만으로 생성한다.

### Slay the Spire II — 게임 자동화

![Slay the Spire Demo](/static/cli-anything-images/slay-the-spire-demo.jpg)

에이전트가 CLI 하네스를 통해 게임 상태를 읽고, 카드를 선택하고, 경로를 선택하며 실시간 전략적 결정을 내린다.

### VideoCaptioner — 자동 자막 생성

![VideoCaptioner Before](/static/cli-anything-images/videocaptioner-before.jpg)
![VideoCaptioner After](/static/cli-anything-images/videocaptioner-after.jpg)

에이전트가 비디오에 이중언어 자막을 자동 생성하고 오버레이한다.

---

## 지원 소프트웨어 — 38개 앱, 2,280개 테스트

### 창작 도구

| 소프트웨어 | 분야 | CLI 명령 | 테스트 |
|-----------|------|---------|--------|
| 🎨 GIMP | 이미지 편집 | `cli-anything-gimp` | 107 |
| 🧊 Blender | 3D 모델링 & 렌더링 | `cli-anything-blender` | 208 |
| ✏️ Inkscape | 벡터 그래픽 | `cli-anything-inkscape` | 202 |
| 🎵 Audacity | 오디오 프로덕션 | `cli-anything-audacity` | 161 |
| 📐 Draw.io | 다이어그램 | `cli-anything-drawio` | 138 |
| 🎵 MuseScore | 악보 | `cli-anything-musescore` | 56 |
| 🎨 Sketch | UI 디자인 | `sketch-cli` | 19 |
| 🖼️ ComfyUI | AI 이미지 생성 | `cli-anything-comfyui` | 70 |

### 생산성 & 오피스

| 소프트웨어 | 분야 | CLI 명령 | 테스트 |
|-----------|------|---------|--------|
| 📄 LibreOffice | 오피스 스위트 | `cli-anything-libreoffice` | 158 |
| 📚 Zotero | 참고문헌 관리 | `cli-anything-zotero` | New |
| 📝 Mubu | 지식 관리 | `cli-anything-mubu` | 96 |
| 📓 Obsidian | 지식 관리 | `cli-anything-obsidian` | 48+7 |

### 비디오 & 스트리밍

| 소프트웨어 | 분야 | CLI 명령 | 테스트 |
|-----------|------|---------|--------|
| 📹 OBS Studio | 라이브 스트리밍 | `cli-anything-obs-studio` | 153 |
| 🎞️ Kdenlive | 비디오 편집 | `cli-anything-kdenlive` | 155 |
| 🎬 Shotcut | 비디오 편집 | `cli-anything-shotcut` | 154 |
| 🎬 Openscreen | 화면 녹화 편집 | `cli-anything-openscreen` | 101 |
| 🎬 VideoCaptioner | AI 비디오 자막 | `cli-anything-videocaptioner` | 26 |

### 개발 & AI

| 소프트웨어 | 분야 | CLI 명령 | 테스트 |
|-----------|------|---------|--------|
| 🦙 Ollama | 로컬 LLM 추론 | `cli-anything-ollama` | 98 |
| 🐞 LLDB | 네이티브 디버깅 | `cli-anything-lldb` | 27 |
| 🟩 Nsight Graphics | GPU 디버깅 | `cli-anything-nsight-graphics` | 51 |
| 📈 Unreal Insights | 퍼포먼스 프로파일링 | `cli-anything-unrealinsights` | 50 |
| 🔍 Exa | AI 웹 검색 | `cli-anything-exa` | 40 |
| 🧬 Uni-Mol Tools | 분자 모델링 | `cli-anything-unimol-tools` | 67 |

### 게임 & 기타

| 소프트웨어 | 분야 | CLI 명령 | 테스트 |
|-----------|------|---------|--------|
| 🎮 Godot | 게임 개발 | `cli-anything-godot` | 24 |
| 📦 s&box | 게임 개발 (Source 2) | `cli-anything-sbox` | 244 |
| ⚔️ Slay the Spire II | 게임 자동화 | `cli-anything-slay-the-spire-ii` | - |
| 🗺️ QGIS | 지리공간 분석 | `cli-anything-qgis` | 22 |
| 🏭 FreeCAD | CAD | `cli-anything-freecad` | 258 |
| 🎮 RenderDoc | GPU 프레임 캡처 | `cli-anything-renderdoc` | 59 |

> **100% 통과율** — 2,280개 테스트 전통과 (단위 1,682 + E2E 579 + Node.js 19)

---

## CLI-Hub — 커뮤니티 CLI 패키지 매니저

CLI-Anything은 [CLI-Hub](https://hkuds.github.io/CLI-Anything/)라는 중앙 레지스트리를 운영한다:

```bash
# 허브 설치
pip install cli-anything-hub

# CLI 검색 및 설치
cli-hub install blender
cli-hub install gimp
```

에이전트가 자율적으로 CLI를 발견하고 설치할 수 있는 **메타 스킬**도 제공한다.

---

## 지원 에이전트 플랫폼

CLI-Anything은 주요 AI 코딩 에이전트 플랫폼을 모두 지원한다:

### Claude Code

```bash
# 마켓플레이스 추가
/plugin marketplace add HKUDS/CLI-Anything

# 플러그인 설치
/plugin install cli-anything

# CLI 생성
/cli-anything ./gimp
```

### OpenClaw

```bash
# 스킬 설치
mkdir -p ~/.openclaw/skills/cli-anything
cp CLI-Anything/openclaw-skill/SKILL.md ~/.openclaw/skills/cli-anything/

# 사용
@cli-anything build a CLI for ./gimp
```

### Pi Coding Agent

```bash
bash .pi-extension/cli-anything/install.sh
/cli-anything ./gimp
```

### Codex

```bash
bash CLI-Anything/codex-skill/scripts/install.sh
# 자연어로 지시
# "Use CLI-Anything to build a harness for ./gimp"
```

그 외에도 **OpenCode, Goose, Qodercli, GitHub Copilot CLI** 등을 지원한다.

---

## 핵심 설계 원칙

### 진정한 소프트웨어 통합
CLI가 유효한 프로젝트 파일(ODF, MLT XML, SVG 등)을 생성하고 실제 애플리케이션에 렌더링을 위임한다. 소프트웨어를 대체하는 게 아니라 **구조적 인터페이스를 구축**하는 것이다.

### 이중 인터랙션 모델
모든 CLI는 두 가지 모드로 동작한다:
- **REPL 모드** — 대화형 에이전트 세션용
- **서브커맨드 모드** — 스크립팅/파이프라인용

### 에이전트 네이티브 설계
모든 명령에 `--json` 플래그가 내장되어 기계가 소비할 수 있는 구조화된 데이터를 제공한다. 에이전트는 `--help`와 `which` 명령으로 능력을 자동 탐색한다.

### 타협 없는 의존성
실제 소프트웨어가 필수 요구사항이다. 대체나 우아한 저하 없이 백엔드가 없으면 테스트가 실패한다.

---

## 테스트 결과 — 100% 통과율

```
gimp          107 passed  ✅   (64 unit + 43 e2e)
blender       208 passed  ✅   (150 unit + 58 e2e)
inkscape      202 passed  ✅   (148 unit + 54 e2e)
freecad       258 passed  ✅   (full coverage)
sbox          244 passed  ✅   (157 unit + 87 e2e)
libreoffice   158 passed  ✅   (89 unit + 69 e2e)
audacity      161 passed  ✅   (107 unit + 54 e2e)
obs-studio    153 passed  ✅   (116 unit + 37 e2e)
kdenlive      155 passed  ✅   (111 unit + 44 e2e)
shotcut       154 passed  ✅   (110 unit + 44 e2e)
drawio        138 passed  ✅   (116 unit + 22 e2e)
ollama         98 passed  ✅   (87 unit + 11 e2e)
───────────────────────────────────────────────────
TOTAL        2,280 passed  ✅   100% pass rate
```

다계층 테스트:
- **단위 테스트** — 합성 데이터로 모든 핵심 함수를 격리 테스트
- **E2E 테스트 (네이티브)** — 프로젝트 파일 생성 파이프라인 검증
- **E2E 테스트 (실제 백엔드)** — 실제 소프트웨어 호출 + 출력 검증
- **CLI 서브프로세스 테스트** — 설치된 명령의 JSON 출력 검증

---

## 실무 적용 시나리오

- **에이전트 기반 자동화** — AI 에이전트가 GIMP, Blender 등을 CLI로 제어하여 창작 워크플로우 자동화
- **CI/CD 파이프라인** — 생성된 CLI를 빌드 파이프라인에 통합
- **게임 개발** — Godot, s&box 엔진을 에이전트가 제어
- **CAD/3D 모델링** — FreeCAD, Blender를 프로그래밍 방식으로 제어
- **비디오 프로덕션** — Kdenlive, Shotcut으로 자동 편집
- **연구 & 데이터 분석** — QGIS, Uni-Mol Tools 등 전문 도구를 에이전트가 활용

---

## 리소스

- **GitHub:** <https://github.com/HKUDS/CLI-Anything>
- **CLI-Hub:** <https://hkuds.github.io/CLI-Anything/>
- **기여 가이드:** <https://github.com/HKUDS/CLI-Anything/blob/main/CONTRIBUTING.md>
- **위시리스트:** <https://github.com/HKUDS/CLI-Anything/issues/new?template=cli-wishlist.yml>
- **PyPI:** `pip install cli-anything-hub`

---

이 글은 [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) 리포지토리를 기반으로 작성되었습니다.
