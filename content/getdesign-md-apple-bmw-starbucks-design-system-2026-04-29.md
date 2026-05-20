---
title: "getDesign.md — Apple·BMW·Starbucks 디자인 시스템을 AI 코딩 에이전트에게 주는 방법"
date: 2026-04-29
slug: getdesign-md-apple-bmw-starbucks-design-system-2026-04-29
tags:
  - AI코딩
  - 디자인시스템
  - getdesign
  - VoltAgent
  - UI개발
  - 프론트엔드
description: "getDesign.md는 Apple, BMW, Starbucks 등 유명 브랜드 디자인 시스템을 DESIGN.md 파일 한 장으로 추출해, AI 코딩 에이전트에게 넘겨주는 오픈소스 툴. 세 브랜드의 색상·타이포·컴포넌트 시스템을 비교 정리함."
aliases:
  - getdesign-md-apple-bmw-starbucks-design-system-2026-04-29/index
---

AI 코딩 에이전트로 UI를 만들 때 가장 먼저 부딪히는 문제가 있음. 에이전트가 코드는 잘 짜는데, 브랜드 감이 없는 UI를 뱉어낸다는 것. Apple 스타일로 만들어달라고 해도 그게 뭔지 정확히 모르고, 그냥 "깔끔한 흰 배경"으로 때움.

이걸 해결하려고 만들어진 게 **getDesign.md**임. 유명 브랜드 웹사이트의 디자인 언어를 분석해서 `DESIGN.md` 파일 한 장으로 추출해줌. 에이전트한테 이 파일을 레퍼런스로 넘기면, 실제 브랜드 톤을 흉내낸 UI를 만들어줌.

지금 Apple, BMW, Starbucks 세 브랜드가 공개돼 있음. 각각 어떤 시스템인지 뜯어봄.

---

## getDesign.md란

VoltAgent 팀이 만든 오픈소스 프로젝트. 실제 브랜드 사이트를 분석해서 색상 토큰, 타이포그래피 스케일, 컴포넌트 스펙, 레이아웃 원칙을 하나의 YAML+마크다운 파일로 정리해둠.

공식 디자인 시스템이 아님. 사이트를 보고 역공학한 **큐레이션 레퍼런스**임. 그래서 법적으로도 안전하고, 실용적으로도 충분함.

```bash
# 프로젝트 루트에서 실행
npx getdesign@latest add apple
```

이 명령 하나로 `DESIGN.md`가 생성됨. 이걸 Claude, Cursor, GitHub Copilot 같은 AI 코딩 툴에 붙여넣으면 됨.

---

## Apple 디자인 시스템

![getDesign.md Apple 디자인 시스템 페이지](./images/getdesign-md-apple-bmw-starbucks-design-system-2026-04-29/apple-screenshot.png)

**한 줄 요약:** "사진이 박물관 갤러리처럼 보이는 인터페이스"

### 핵심 철학

Apple 디자인의 기본값은 **제품 사진이 주인공, UI 크롬은 배경**임. 장식 그라디언트 없음. 크롬에 그림자 없음. 제품 이미지 아래에만 시그니처 그림자 하나. 밝은 캔버스와 어두운 타일이 번갈아 가며 나와서 각 제품이 독립적인 갤러리 공간처럼 느껴짐.

인터랙션 색은 단 하나, **Action Blue (#0066cc)**. 이 파란색 말고는 어디에도 색을 쓰지 않음.

### 색상 팔레트

| 역할 | 색상명 | 헥스코드 |
|------|--------|---------|
| 주요 액션 | Action Blue | `#0066cc` |
| 다크모드 액션 | Action Blue On Dark | `#2997ff` |
| 기본 텍스트 | Ink | `#1d1d1f` |
| 기본 배경 | Canvas | `#ffffff` |
| 크림 배경 | Canvas Parchment | `#f5f5f7` |
| 다크 타일 1 | Surface Tile 1 | `#272729` |
| 다크 타일 2 | Surface Tile 2 | `#2a2a2c` |
| 완전한 검정 | Surface Black | `#000000` |

### 타이포그래피

폰트: **SF Pro Display** (헤더) / **SF Pro Text** (본문). 시스템 폰트이므로 Apple 기기에서는 자동 적용됨.

| 토큰 | 크기 | 굵기 | 자간 | 용도 |
|------|------|------|------|------|
| hero-display | 56px | 600 | -0.28px | 메인 히어로 헤드라인 |
| display-lg | 40px | 600 | 0 | 섹션 타이틀 |
| display-md | 34px | 600 | -0.374px | 서브섹션 헤드 |
| body | 17px | 400 | -0.374px | 기본 본문 |
| caption | 14px | 400 | -0.224px | 캡션 |

자간이 **음수**임. -0.374px 이 미세한 당김이 SF Pro 특유의 밀도감을 만들어냄.

### 버튼 & 컴포넌트

- **Primary Button:** Action Blue 배경, 흰 텍스트, 라운드 `md(11px)` — 작은 알약형
- **Button On Dark:** 다크 배경에서는 반투명 처리, 텍스트만 강조
- **Product Tile:** 어두운 타일 위에 제품 사진 + 아래에 헤드라인 + Action Blue CTA
- **Nav:** 흰 배경, 12px nav-link, 유리 블러 효과(다크모드 시)

```bash
npx getdesign@latest add apple
```

---

## BMW 디자인 시스템

![getDesign.md BMW 디자인 시스템 페이지](./images/getdesign-md-apple-bmw-starbucks-design-system-2026-04-29/bmw-screenshot.png)

**한 줄 요약:** "독일 엔지니어링 정밀도 — 직사각형과 두 가지 굵기만으로"

### 핵심 철학

BMW 코퍼레이트 사이트(BMW M 서킷 버전이 아닌)는 **절제된 자동차 브랜드 UI**임. 흰 캔버스가 기본, 다크 네이비 히어로 밴드가 모델 사진을 품음. 버튼은 예외 없이 **직사각형(0px 라운드)**. 이게 브랜드 언어임.

BMW Type Next Latin 폰트를 700(헤드라인)과 300(본문) 두 굵기만 씀. 중간인 500은 없음. 이 극단적 대비가 "유럽 정밀 엔지니어링" 느낌을 만듦.

### 색상 팔레트

| 역할 | 색상명 | 헥스코드 |
|------|--------|---------|
| 주요 액션 | BMW Blue | `#1c69d4` |
| 액션 눌렸을 때 | Primary Active | `#0653b6` |
| 기본 텍스트 | Ink | `#262626` |
| 본문 텍스트 | Body | `#3c3c3c` |
| 기본 배경 | Canvas | `#ffffff` |
| 소프트 배경 | Surface Soft | `#f7f7f7` |
| 다크 히어로 | Surface Dark | `#1a2129` |
| M 빨강 (M모델 전용) | M Red | `#e22718` |

다크 히어로 `#1a2129`는 순수 검정이 아님. 따뜻한 언더톤을 품은 네이비임. 이 미묘함이 고급 차량 조명처럼 보이게 함.

### 타이포그래피

| 토큰 | 크기 | 굵기 | 용도 |
|------|------|------|------|
| display-xl | 64px | 700 | 히어로 모델명 ("iX3") |
| display-lg | 48px | 700 | 섹션 헤드 |
| display-md | 32px | 700 | 서브섹션 헤드 |
| body-md | 16px | **300** | 기본 본문 (Light!) |
| label-uppercase | 13px | 700 | "LEARN MORE" 형식 링크 |
| button | 14px | 700 | 버튼 레이블 |

주의: 본문이 weight **300(Light)**임. 헤드 700 대 본문 300. 이 극단 대비가 브랜드 시그니처임.

### 버튼 & 컴포넌트

- **Primary Button:** BMW Blue, 흰 텍스트, **0px 직사각형**, 높이 48px
- **Secondary Button:** 흰 배경, 잉크 텍스트, hairline 테두리, 마찬가지로 0px 직사각형
- **Button Text Link:** "LEARN MORE ›" 형식, 대문자, 1.5px 트래킹
- **Model Card:** 4-up 그리드, 소프트 카드 배경, 모델 사진 + 이름 + Learn More 링크
- **M Stripe:** M모델 전용 빨파파 트리컬러 4px 가로선 — 코퍼레이트 사이트 메인 플로우에는 쓰지 않음

```bash
npx getdesign@latest add bmw
```

---

## Starbucks 디자인 시스템

![getDesign.md Starbucks 디자인 시스템 페이지](./images/getdesign-md-apple-bmw-starbucks-design-system-2026-04-29/starbucks-screenshot.png)

**한 줄 요약:** "카페 앞치마 초록을 4단 그린 시스템으로 — 따뜻한 크림 캔버스 위에"

### 핵심 철학

Starbucks 디자인은 **따뜻한 소매 플래그십**임. 배경이 차가운 흰색이 아님. 크림 베이지(`#f2f0eb`)와 세라믹 오프화이트(`#edebe9`) — 카페 냅킨, 나무 테이블, 도자기 컵 질감을 디지털로 재현한 색임.

초록이 한 가지가 아니라 **4단계 그린 시스템**임:
- Starbucks Green (브랜드 신호)
- Green Accent (CTA 색)
- House Green (히어로·푸터 배경)
- Green Uplift (장식 액센트)

골드(`#cba258`)는 리워즈 티어 전용. 일반 액센트로 절대 쓰지 않음.

### 색상 팔레트

| 역할 | 색상명 | 헥스코드 |
|------|--------|---------|
| 브랜드 그린 | Starbucks Green | `#006241` |
| CTA 그린 | Green Accent | `#00754A` |
| 히어로/푸터 | House Green | `#1E3932` |
| 장식 그린 | Green Uplift | `#2b5148` |
| 연한 민트 | Green Light | `#d4e9e2` |
| 리워즈 골드 | Gold | `#cba258` |
| 크림 캔버스 | Neutral Warm | `#f2f0eb` |
| 세라믹 오프화이트 | Ceramic | `#edebe9` |
| 기본 흰색 | White | `#ffffff` |

### 타이포그래피

**SoDoSans** — Starbucks 전용 독점 서체. `-0.16px` 자간이 자신감 있고 친근한 톤을 만들어냄.

특이한 점: 페이지별로 폰트가 다름.
- **SoDoSans**: 전체 기본 서체
- **Lander Tall / Iowan Old Style (세리프)**: 리워즈 페이지 헤드라인 — 카페 칠판 감성
- **Kalam / Comic Sans (필기체)**: 커리어 페이지 컵 이름 터치

| 역할 | 크기 | 굵기 | 자간 |
|------|------|------|------|
| Display | 80px | 400–600 | -0.16px |
| Hero Large | 45px | 400–600 | -0.16px |
| H1 | 24px | 600 | -0.16px |
| Body | 16px | 400 | -0.01em |
| Button Label | 14–16px | 400–600 | -0.01em |

### 버튼 & 컴포넌트 (시그니처 포인트)

- **모든 버튼:** **50px 풀 필 (pill)**. 예외 없음.
- **Frap 플로팅 CTA:** 56px 원형 버튼, Green Accent 배경, 오른쪽 하단 플로팅. 레이어드 그림자 스택(`0 0 6px rgba(0,0,0,0.24)` + `0 8px 12px rgba(0,0,0,0.14)`). 누르면 `scale(0.95)` 수축 — 이게 Starbucks UI의 시그니처 인터랙션임.
- **Gift Card 타일:** 실제 카드 사진 — 생성 그래픽이 아니라 촬영된 실물 카드.
- **카드 라운드:** 12px 라운드 직사각형 + 속삭임 수준 그림자

```bash
npx getdesign@latest add starbucks
```

---

## 세 브랜드 비교

| 항목 | Apple | BMW | Starbucks |
|------|-------|-----|-----------|
| 메인 배경 | 흰색/크림 교차 | 흰색 | 따뜻한 크림 |
| 액션 색 | Action Blue `#0066cc` | BMW Blue `#1c69d4` | Green Accent `#00754A` |
| 버튼 모양 | 소형 알약형 (11px) | **0px 직사각형** | **50px 풀 필** |
| 폰트 | SF Pro Display/Text | BMW Type Next Latin | SoDoSans (전용) |
| 그라디언트 | 없음 | 없음 | 없음 |
| 그림자 | 제품 사진에만 | 없음 (색 블록으로 깊이) | 카드에 소프트 그림자 |
| 다크 서페이스 | 다크 타일 `#272729` | 히어로 밴드 `#1a2129` | 히어로/푸터 `#1E3932` |

셋 다 공통점이 있음. **그라디언트 없음, 장식 최소화, 사진/제품이 주인공**. 대신 색과 타이포그래피의 시스템적 일관성으로 브랜드를 만들어냄.

---

## 설치 및 사용법

```bash
# Apple 스타일
npx getdesign@latest add apple

# BMW 스타일
npx getdesign@latest add bmw

# Starbucks 스타일
npx getdesign@latest add starbucks
```

프로젝트 루트에 `DESIGN.md`가 생성됨. 그 다음 AI 에이전트에게:

```
DESIGN.md를 참고해서 제품 카드 컴포넌트를 만들어줘.
```

이렇게 하면 됨.

**Claude Project**나 **Cursor Rules**에 DESIGN.md를 시스템 컨텍스트로 등록해두면, 매번 붙여넣지 않아도 자동으로 반영됨.

---

## 더 많은 브랜드

getDesign.md는 계속 확장 중임. GitHub 저장소(VoltAgent/awesome-design-md)에서 사용 가능한 전체 브랜드 목록 확인 가능.

공식 디자인 시스템이 아니기 때문에 실제 브랜드 가이드라인과 100% 일치하지 않을 수 있음. 프로덕션 공식 제품보다는 AI 코딩 시 레퍼런스로 쓰는 용도임.

브랜드 디자인을 흉내내야 하는 사이드 프로젝트, 프로토타입, 교육용 UI 개발에는 충분히 실용적임.
