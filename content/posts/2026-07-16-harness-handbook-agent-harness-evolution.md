---
title: "Harness Handbook: AI 에이전트 하네스를 읽고, 감사하고, 수정 가능하게 만드는 행동 중심 지도"
date: 2026-07-16T22:00:00+09:00
draft: false
summary: "Tencent Hunyuan과 Indiana University 등이 제안한 Harness Handbook은 대규모 AI 에이전트 하네스 코드베이스에서 '행동' 단위로 코드를 재구성하여, 개발자와 코딩 에이전트가 수정 위치를 빠르고 정확하게 찾을 수 있게 하는 행동 중심 표현이다. 정적 분석과 LLM 기반 구조화를 결합해 자동 생성되며, 핵심 평가에서 현지화 정확도와 편집 계획 품질을 크게 높이면서도 플래너 토큰 사용량을 줄였다."
tags: ["AI Agent", "Agent Harness", "Behavior Localization", "Code Understanding", "Tencent Hunyuan"]
categories: ["AI Agent", "Software Engineering"]
source_url: "https://arxiv.org/abs/2607.13285"
project_url: "https://ruhan-wang.github.io/Harness-Handbook/"
authors: ["Ruhan Wang", "Yucheng Shi", "Zongxia Li", "Zhongzhi Li", "Yue Yu", "Junyao Yang", "Kishan Panaganti", "Haitao Mi", "Dongruo Zhou", "Leoweiliang"]
affiliations: ["Tencent HY LLM Frontier", "Indiana University", "University of Maryland", "University of Georgia", "National University of Singapore"]
---

## 핵심 요약

현대 AI 에이전트의 능력은 기반 모델만큼이나 **하네스(harness)**—프롬프트 구성, 상태 관리, 도구 호출, 실행 조정을 담당하는 코드 계층—에 달려 있다. 하지만 Codex 같은 프로덕션 하네스는 2,267개 파일, 34,000개 이상의 함수, 약 160,000개의 코드 연결로 이루어져 있어, "파일 삭제 전 사용자 확인" 같은 단일 행동이 어디서 구현되는지 찾기가 극히 어렵다.

**Harness Handbook**은 이 문제를 해결하기 위해 코드를 파일이나 모듈이 아닌 **시스템 행동(behavior)** 단위로 재구성한 탐색 가능한 지도를 제공한다. 정적 프로그램 분석과 LLM 기반 행동 구조화를 결합해 자동 생성되며, 모든 설명은 소스 코드로 검증 가능한 증거에 연결된다.

![Harness Handbook 표현 개요 - L1 시스템 개요부터 L3 소스 수준 세부 정보까지 3단계 계층 구조](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-1-p4.png)

*그림 1: Harness Handbook의 3단계 표현 개요. L1(시스템 개요) → L2(컴포넌트 개요) → L3(소스 수준 세부 정보)로 이어지는 계층 구조와 컴포넌트 및 상태 인덱스를 제공하는 탐색 창.*

---

## 왜 행동 국지화(Behavior Localization)가 핵심 병목인가?

"파일 삭제 전 사용자에게 확인"이라는 규칙은 단일 `confirmBeforeDelete()` 함수로 표현되지 않는다. 프롬프트, 도구 래퍼, 권한 설정, 상태 관리, 샌드박스 실행, 예외 처리 경로 등 여러 모듈에 걸쳐 결정된다. 각 구현 지점은 체인의 일부만 담당하므로, 전체 행동을 이해하려면 모든 관련 코드를 추적해야 한다.

이를 **행동 국지화(behavior localization)**라고 부른다—수정 요청이 설명하는 행동을 구현하는 모든 코드 위치를 식별하는 작업이다. 대규모 하네스에서는 개발자든 코딩 에이전트든 이 작업에 상당한 시간과 토큰을 소모한다.

### 기존 접근의 한계

- **코드 검색 / 저장소 인덱싱**: 개별 코드 조각은 찾을 수 있지만, 행동 체인 전체를 복원하지 못한다
- **긴 컨텍스트 처리**: 입력 한계 때문에 모든 관련 코드를 한 번에 볼 수 없다
- **저장소 지도**: 파일·함수 중심이라 행동-코드 매핑을 사용자가 추론해야 한다

---

## Harness Handbook: 3단계 행동 지도

Harness Handbook은 **행동 중심**의 L1-L3 계층 구조를 사용한다:

### L1 — 시스템 개요
전체 아키텍처, 실행 모델, 주요 단계, 전역 데이터 흐름을 요약한다. "이 하네스는 전체적으로 어떻게 실행되는가?"에 답한다.

### L2 — 컴포넌트(행동 단위) 개요
시스템을 **행동 단위(behavior unit)**로 분해한다. 각 단위는 책임, 입력/출력, 의존성, 핵심 상태를 기록한다. 복잡한 행동이 어떻게 분해되고 다시 연결되는지 보여준다.

### L3 — 행동 단위 세부 정보
특정 행동이 언제 트리거되는지, 어떻게 실행되는지, 상태가 어떻게 변하는지, 예외 경로는 무엇인지, 어떤 파일과 함수가 증거인지를 연결한다. 예를 들어 "파일 삭제 전 확인"은 더 이상 단순한 규칙이 아니라 **검증 가능한 행동 체인**이 된다:

| 요소 | 내용 |
|------|------|
| **트리거** | 모델이 `delete_file(path)` 호출 |
| **권한 규칙** | 파일 삭제를 고위험으로 분류, 사용자 확인 필요 |
| **상태 변화** | 확인 요청 및 사용자 응답 기록 |
| **실행 경로** | 승인 → 샌드박스 실행 / 거부 → 중단 및 에러 |
| **에지 케이스** | 헤드리스 모드, 자동 승인 정책, 폴백 경로 |
| **증거** | `tools/file_ops.py L32-78`, `tools/wrapper.py L84-128`, `policy/permissions.py L15-66`, `runtime/sandbox.py L40-112`, `state/manager.py L40-61` |

---

## 자동 생성 파이프라인

Harness Handbook은 수동 작성이 아닌 **세 단계 자동 파이프라인**으로 생성된다:

![Harness Handbook 생성 파이프라인 - 정적 분석, 행동 조직, 계층적 합성](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-2-p5.png)

*그림 2: 생성 파이프라인. 정적 분석이 소스 연결 사실을 추출하고, 행동 조직이 소스 단위를 실행 단계에 매핑하며, 계층적 합성이 L1-L3 핸드북을 구축한다.*

### Phase I — 정적 사실 추출 (결정론적)
언어별 어댑터가 저장소를 파싱하여 함수, 시그니처, 호출 그래프를 추출한다. LLM 호출 없이 **결정론적**으로 동작한다.

### Phase II — 행동 조직
소스 단위를 실행 단계 골격에 할당한다. `function-as-leaf` 모드(신뢰할 수 있는 시드 골격이 있을 때)와 `file-as-leaf` 모드(골격을 추론해야 할 때)를 지원한다.

### Phase III — 계층적 합성 및 패키징
L1-L3 문서 트리와 상태 레지스터 뷰를 생성한다. 모든 L3 항목은 정적으로 식별된 소스 위치에 연결되고 현재 저장소와 대조해 검증된다.

---

## Behavior-Guided Progressive Disclosure (BGPD)

**BGPD**는 코딩 에이전트가 하네스 수정 요청을 받았을 때 사용하는 워크플로우다:

1. **국지화**: 요청된 행동을 handbook 탐색을 통해 좁혀간다
2. **계획**: 증거를 편집 계획으로 변환
3. **실행**: 별도 실행기가 편집 적용
4. **재동기화**: 변경이 있으면 handbook를 자동 업데이트

핵심은 **점진적 공개(progressive disclosure)**: 처음부터 모든 코드를 보여주지 않고, L1 → L2 → L3 순으로 필요한 만큼만 드러낸다. 그리고 **행동-구현 정합성**: 모든 L3 위치자(locator)가 현재 저장소에서 여전히 유효한지 재검증한다.

---

## 평가 결과: 정확도 향상 + 토큰 절감

두 개의 오픈소트 에이전트 하네스(Codex, Terminus-2)에서 다양한 수정 요청으로 평가했다.

![계획 품질 및 플래너 토큰 사용량 비교](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-3-p8.png)

*그림 3: Codex와 Terminus-2에서의 계획 품질 및 플래너 토큰 사용량. (a) 전체 승률, (b) 플래너 토큰 사용량 비교.*

![평가 차원별 승률 분해](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-4-p8.png)

*그림 4: 세 가지 평가 차원(현지화, 계획 품질, 실행 가능성)에 대한 판정별 승률.*

### 주요 수치 (Table 1)

![현지화 메트릭 표](/images/2026-07-16-harness-handbook-agent-harness-evolution/table-1-p9.png)

*표 1: 참조 계획 대비 현지화 메트릭(%). Handbook-Assisted가 모든 차원에서 더 높은 정밀도와 재현율을 기록.*

Handbook-Assisted 플래닝은 **현지화 정확도와 편집 계획 품질을 모두 향상**시키면서 **플래너 토큰 사용량을 감소**시켰다. 특히 분산된 구현 지점, 드물게 실행되는 코드 경로, 모듈 간 상호작용이 포함된 변경에서 가장 큰 개선을 보였다.

![수정 요청 유형별 승률](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-5-p9.png)

*그림 5: (a) 수정 요청 유형별, (b) 현지화 난이도별 승률. Q=Query, CF=Cross-File, SH=Scattered/Hard.*

---

## 시사점

이 연구는 에이전트 시스템의 진화가 **편집을 생성하는 능력**뿐 아니라 **어디를 편집해야 하는지 결정하는 능력**에 달려 있음을 보여준다. Harness Handbook은 행동과 구현 사이의 간극을 명시적으로 연결함으로써:

1. **이해(Understand)** — 하네스가 어떻게 실행되는지 전체 흐름 파악
2. **감사(Audit)** — 권한, 확인 로직, 예외 경로가 문서와 일치하는지 검증
3. **적용(Adapt)** — 기존 하네스 위에 자신의 에이전트 구축

이라는 세 가지 목표를 하나의 지도로 지원한다. 복잡한 에이전트 시스템을 안전하게 진화시키려는 개발자와 코딩 에이전트 모두에게 중요한 기여다.

---

## 링크

- 📄 [arXiv 논문](https://arxiv.org/abs/2607.13285)
- 🌐 [프로젝트 페이지](https://ruhan-wang.github.io/Harness-Handbook/)
- 📑 [PDF 다운로드](https://arxiv.org/pdf/2607.13285)
