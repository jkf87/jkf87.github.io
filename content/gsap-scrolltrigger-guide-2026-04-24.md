---
title: "GSAP ScrollTrigger 정리 — 스크롤 기반 애니메이션 제대로 쓰는 법"
date: 2026-04-24
tags:
  - GSAP
  - ScrollTrigger
  - 프론트엔드
  - 웹애니메이션
  - JavaScript
  - 인터랙션
description: "GSAP ScrollTrigger 공식 문서 기반으로 설치, 핵심 옵션, pin / scrub / snap / batch / matchMedia 레시피, 자주 하는 실수까지 한 번에 정리한 실전 가이드."
aliases:
  - gsap-scrolltrigger-guide-2026-04-24/index
---

## ScrollTrigger가 뭔가

GSAP의 플러그인 중 하나로, **스크롤 위치에 애니메이션을 묶어주는 도구**다. 단순히 "보이면 페이드인" 수준이 아니라:

- 스크롤바 움직임에 애니메이션을 직접 매달기 (`scrub`)
- 특정 구간에서 요소 고정 (`pin`)
- 진입/이탈 시 콜백 (`onEnter`, `onLeave`)
- 스크롤 멈추면 특정 위치로 스냅 (`snap`)
- 리사이즈 시 자동 재계산

까지 전부 한 플러그인에서 해결한다. jQuery 시절에 `scroll` 이벤트 붙여서 수동 계산하던 시대는 끝났다.

## 설치

### CDN

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/ScrollTrigger.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger);
</script>
```

### npm

```bash
npm install gsap
```

```javascript
import { gsap } from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);
```

`registerPlugin`은 **반드시 호출**해야 한다. 번들러가 tree-shaking으로 플러그인을 날려버리는 걸 막는 역할도 겸한다.

## 최소 예제

```javascript
gsap.to(".box", {
  scrollTrigger: ".box", // 문자열 단축: trigger로 취급
  x: 500,
  rotation: 360,
  duration: 2,
});
```

`.box`가 뷰포트에 들어오면 애니메이션이 한 번 실행된다.

## 핵심 옵션

| 옵션 | 역할 |
|---|---|
| `trigger` | 애니메이션을 발동시킬 DOM 요소(또는 셀렉터) |
| `start` | 시작 지점. 예: `"top center"` = 트리거 상단이 뷰포트 중앙에 닿는 순간 |
| `end` | 종료 지점. 예: `"bottom top"`, `"+=500"`(시작에서 500px 더) |
| `scrub` | `true` 또는 숫자. 스크롤바에 직접 묶기. 숫자는 catch-up 지연(초) |
| `pin` | 트리거 요소를 구간 동안 고정 |
| `toggleActions` | `onEnter / onLeave / onEnterBack / onLeaveBack` 각각 뭘 할지 |
| `markers` | 개발용 시각 가이드 (운영 배포 전 끄기) |
| `snap` | 스크롤 멈추면 특정 진행률/라벨로 스냅 |
| `once` | 한 번만 실행하고 파괴 |
| `invalidateOnRefresh` | 리사이즈 시 애니메이션 시작값을 다시 읽기 |

### start / end 문자법

기본 문법은 `"트리거기준 뷰포트기준"`이다.

- `"top bottom"` → 트리거 상단이 뷰포트 하단에 닿는 순간
- `"center center"` → 둘 다 중앙
- `"top top+=100"` → 트리거 상단이 뷰포트 상단에서 100px 아래에 닿을 때
- `end: "+=500"` → start에서 스크롤 500px 더 내려간 지점

## 생성 방법 두 가지

### 애니메이션에 내장

```javascript
gsap.to(".card", {
  scrollTrigger: {
    trigger: ".card",
    start: "top 80%",
    end: "bottom 20%",
    scrub: 1,
    markers: true,
  },
  y: -100,
  opacity: 1,
});
```

### 독립 인스턴스 (애니메이션 없이 콜백만)

```javascript
ScrollTrigger.create({
  trigger: "#section-2",
  start: "top top",
  end: "bottom top",
  onEnter: () => console.log("진입"),
  onLeave: () => console.log("이탈"),
  onUpdate: (self) => console.log("progress:", self.progress.toFixed(2)),
});
```

진행 상태에 따라 UI를 직접 조작하고 싶을 때 이 방식을 쓴다.

## 실전 레시피

### 1. 섹션 pin (고정 후 내부 애니메이션)

```javascript
gsap.to(".inner", {
  xPercent: -100,
  scrollTrigger: {
    trigger: ".pin-section",
    pin: true,
    start: "top top",
    end: "+=1000",
    scrub: true,
  },
});
```

트리거 요소 **자신**은 가능하면 직접 애니메이션하지 말고, 내부 자식 요소(`.inner`)를 움직이는 게 안전하다. pin 된 요소에 transform을 같이 걸면 레이아웃이 꼬일 수 있다.

### 2. 가로 스크롤

```javascript
const sections = gsap.utils.toArray(".panel");

gsap.to(sections, {
  xPercent: -100 * (sections.length - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-wrap",
    pin: true,
    scrub: 1,
    snap: 1 / (sections.length - 1),
    end: () => "+=" + document.querySelector(".horizontal-wrap").offsetWidth,
  },
});
```

세로 스크롤을 가로 이동으로 변환하는 고전 패턴. `snap`으로 각 패널 경계에 딱 붙게 만든다.

### 3. batch — 여러 요소 한 번에

```javascript
ScrollTrigger.batch(".item", {
  onEnter: (batch) =>
    gsap.to(batch, { opacity: 1, y: 0, stagger: 0.1, overwrite: true }),
  onLeaveBack: (batch) =>
    gsap.to(batch, { opacity: 0, y: 50, stagger: 0.1, overwrite: true }),
  start: "top 85%",
});
```

리스트 아이템 수십 개를 각각 트리거 만들지 말고 batch 한 번으로 묶는 게 성능/관리 면에서 훨씬 낫다.

### 4. matchMedia — 반응형 분기

```javascript
const mm = gsap.matchMedia();

mm.add("(min-width: 768px)", () => {
  // 데스크톱 전용 pin 애니메이션
  gsap.to(".hero", {
    scrollTrigger: { trigger: ".hero", pin: true, scrub: 1 },
    scale: 1.2,
  });
});

mm.add("(max-width: 767px)", () => {
  // 모바일은 간단한 페이드인만
  gsap.from(".hero", {
    scrollTrigger: { trigger: ".hero", start: "top 80%" },
    opacity: 0,
    y: 40,
  });
});
```

브레이크포인트 벗어나면 해당 블록의 ScrollTrigger가 **자동으로 정리**된다. 직접 `window.matchMedia`로 관리하는 것보다 훨씬 깔끔하다.

### 5. scrub으로 progress 기반 제어

```javascript
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: ".story",
    start: "top top",
    end: "+=3000",
    scrub: 1,
    pin: true,
  },
});

tl.to(".title", { opacity: 0, y: -50 })
  .to(".img", { scale: 1.5 }, 0)
  .to(".text", { opacity: 1 }, 0.5);
```

타임라인에 scrub을 걸면 "스크롤 내린 만큼 타임라인도 앞으로 간다". 영화 스토리보드처럼 단계별 연출에 유리하다.

## 자주 쓰는 메서드

```javascript
// DOM이 바뀐 뒤 위치 재계산
ScrollTrigger.refresh();

// 전체 인스턴스 순회
ScrollTrigger.getAll().forEach((st) => st.kill());

// 특정 id로 조회
const st = ScrollTrigger.getById("hero");

// 임시 비활성화/복구
st.disable();
st.enable();

// 현재 스크롤 속도(px/s)
st.getVelocity();
```

SPA에서 라우트 전환 시 **이전 페이지의 ScrollTrigger를 죽이지 않으면** 새 페이지에서 계산이 꼬인다. `getAll().forEach(st => st.kill())`을 라우트 훅에 달아두는 게 안전하다.

## 자주 하는 실수

1. **registerPlugin 호출 누락**
   개발 환경에선 동작하다가 프로덕션 번들에서만 사라지는 경우가 대부분 이것이다.

2. **트리거 요소 자체에 transform + pin 동시 적용**
   pin은 내부적으로 position/transform을 건드리기 때문에, 같은 요소에 별도 transform을 걸면 깨진다. 자식 요소를 애니메이션하자.

3. **여러 ScrollTrigger를 아래에서 위로 생성**
   ScrollTrigger는 위에서 아래 순서로 생성된다고 가정하고 pin 공간을 계산한다. 반대로 만들면 `refreshPriority`로 순서를 보정해야 한다.

4. **하나의 타임라인에 여러 tween ScrollTrigger를 중첩**
   타임라인의 scrollTrigger는 하나만, 내부 tween에 추가 ScrollTrigger를 또 다는 건 피하자. 계산이 꼬인다.

5. **이미지/폰트 로드 전에 ScrollTrigger 계산**
   높이가 확정되기 전에 계산되면 start/end가 어긋난다. `window.load` 시점이나 이미지 로드 후 `ScrollTrigger.refresh()` 호출을 고려.

6. **모바일 Safari에서 pin이 튐**
   `ScrollTrigger.config({ ignoreMobileResize: true })` 또는 브라우저 주소창 show/hide에 의한 리사이즈 이슈를 별도 처리.

## 성능 팁

- 가능하면 `transform`과 `opacity`만 애니메이션 (레이아웃을 안 건드림)
- 동일 트리거에 여러 tween이 필요하면 **타임라인 하나로 묶기**
- 화면에서 멀리 있는 무거운 애니메이션은 `once: true`로 한 번만 돌리고 파괴
- 리스트는 **batch** 사용
- `scrub` 지연(숫자)을 주면 순간 스크롤에 반응이 부드러워지고 CPU 부하도 줄어듦

## 디버깅 체크리스트

| 증상 | 의심 지점 |
|---|---|
| 아무것도 안 움직임 | `registerPlugin` 호출 여부, 셀렉터 오타 |
| start/end가 엉뚱한 위치 | 이미지/폰트 로드 전 계산, `refresh()` 필요 |
| pin 구간이 겹침 | 위에서 아래 순서 위반, `refreshPriority` |
| 리사이즈 후 깨짐 | `invalidateOnRefresh: true`, 동적 end는 함수로 |
| 모바일에서만 튐 | `ignoreMobileResize`, 주소창 동작 고려 |

개발 중엔 `markers: true`를 항상 켜두자. 시작점과 종료점이 눈에 보이는 것만으로도 디버깅 시간이 절반으로 준다.

## 정리

ScrollTrigger는 옵션이 많아 보여도 실제로 자주 쓰는 건 `trigger / start / end / scrub / pin / toggleActions` 여섯 개 정도다. 이 여섯 개와 **`ScrollTrigger.refresh()` + `matchMedia()` + `batch()`** 세 가지 도구를 익히면 대부분의 요구사항을 커버한다.

공식 문서 원문: [GSAP ScrollTrigger 문서](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
