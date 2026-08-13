---
title: "SkillZip: 에이전트 스킬이 늘어만 가면 망한다 - 평가 없이 구조를 찾아 압축하는 법"
date: 2026-08-13
tags:
  - agent
  - skill-evolution
  - self-evolving
  - LLM
  - harness
  - compression
  - MDL
  - loop
  - automation
draft: false
---

## 개요

Self-evolving agent는 경험을 재사용 가능한 스킬로 축적하면서 성능을 개선한다. 그러나 스킬이 append-only 방식으로 관리되면, 동일한 제약이 여러 브랜치에 반복되고 유사한 워크플로우가 복사되는 문제가 발생한다. Alibaba·절강대학·Duke 대학 공동 연구진이 2026년 8월에 발표한 SkillZip은 이러한 구조적 중복을 평가 롤아웃 없이 제거하는 방법을 제안한다.

## 문제: 스킬 길이는 자라는데 새 절차는 없다

![](/images/2026-08-13-skillzip-evaluation-free-skill-compression/fig-1-p1-2.png)

Figure 1은 CodeX Agent 기반 self-evolving 과정에서 스킬 길이가 단조 증가하는 현상을 보여준다. 반면 실제 새로운 절차적 내용은 일찍 포화에 도달한다. 스킬은 매 호출 시 컨텍스트에 로드되므로, 텍스트 길이 증가는 곧 prefill 비용 증가로 이어진다.

기존 접근의 한계:

| 방법 | 한계 |
|---|---|
| 프롬프트 압축 (LLMLingua 등) | query-dependent 중요도 기반이라 미래 작업을 알 수 없는 스킬 압축에 부적합 |
| SkillReducer | 검증을 위해 40–80회 롤아웃 필요, evaluation set 의존적 |

## SkillZip의 구조적 접근

![](/images/2026-08-13-skillzip-evaluation-free-skill-compression/fig-2-p3-1.png)

SkillZip은 스킬을 6개 타입의 계약(contract)으로 분해한다:

| 타입 | 구성 요소 |
|---|---|
| Interface (I) | 이름, 목적, 트리거, 제외 조건 |
| Workflow (G) | 액션 순서, 결정점, 루프, 폴백, 중지 조건 |
| Tool protocol (T) | 도구 이름, 필수 인자, 전제조건, 예상 관측 |
| Scoped rules (C) | 의무/금지/권장 규칙 + 적용 범위 및 가드 |
| Output contract (O) | 응답 타입, 필수 필드, 순서, 검증, 완료 조건 |
| Evidence (E) | 예시, 템플릿, 근거 |

압축의 안전 기준은 토큰 중요도가 아닌 타입별 커버리지이다. 두 문장이 동일한 도구를 다루더라도 인자가 다르면 병합할 수 없고, 모든 브랜치에 반복되는 규칙은 상위 스코프로 이동할 수 있다.

## 방법론

![](/images/2026-08-13-skillzip-evaluation-free-skill-compression/fig-3-p6-1.png)

### 목표 함수

SkillZip은 최단 충실 설명(shortest faithful explanation) 목표를 최소화한다:

- 공유 라이브러리 K와 잔차 R에 대해 L(K) + L(R|K)를 최소화
- 모든 필수 계약 유닛에 대한 hard coverage constraint

이 목표에서 4가지 구조적 결정이 도출된다:

1. 동등 요건 통합: 중복 규칙을 한 번만 서술하고 참조
2. 스코프 상향: 모든 경로에 적용되는 규칙을 공통 상위로 이동
3. 워크플로우 재사용: 반복 액션 시퀀스를 공유 프로시저로 추출
4. 가드 예외 분해: 공통 규칙 + 가드 차분으로 표현

### 두 가지 모드

- **원샷 SkillZip**: 기존 스킬 체크포인트를 1회 구조화 추출 + deterministic optimization으로 압축. 태스크 롤아웃 불필요.
- **Zip-on-Write**: self-evolution 루프 내에서 동작. 패치 도착 시 컨트랙트와 비교하여 흡수/정제/추가/리팩토링 수행. 주기적 repack으로 누적 패턴 처리.

## 실험 결과

3개 벤치마크(LiveMath, Spreadsheet, BFCL-V4), 3개 모델(Qwen3.6-Plus, Kimi K2.6, Qwen3.7-Max)에서 평가했다.

### 압축 성능 및 태스크 유지

| 지표 | SkillZip | SkillReducer |
|---|---|---|
| 평균 압축률 | 31.2% | 9.2% |
| 태스크 성능 | 0.577 | 0.544 |

### 압축 비용

| 지표 | SkillZip | SkillReducer |
|---|---|---|
| 평균 시간 | 286초 | 1006초 |
| 롤아웃 | 0회 | 40–80회 |

### 크로스 모델 일반화

한 모델에서 압축한 스킬을 다른 모델에서 실행했을 때 retention: SkillZip 0.97, SkillReducer 0.91.

### Zip-on-Write 지속 압축

![](/images/2026-08-13-skillzip-evaluation-free-skill-compression/fig-5-p8.png)

16라운드 self-evolution에서 무압축 시 스킬이 2.5–3.7배 증가한 반면, round 1부터 Zip-on-Write 적용 시 1.6–1.9배로 억제되었다. round 8부터 적용하면 부분 회복되나 round 1 트랙에는 미치지 못한다. 압축 적용 시 정확도 저하 없음.

## 실무 적용 가이드

- self-evolution 루프 초기(round 1)부터 Zip-on-Write를 통합하면 중복 누적을 예방할 수 있다
- hard coverage constraint로 인해 드문 규칙이 삭제되지 않는다
- 평가 셋이나 롤아웃 환경 없이도 압축이 가능하다
- 압축된 스킬은 다른 모델에서도 사용 가능하다

논문: [SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure](https://arxiv.org/abs/2608.11079)

## 더 실습해보고 싶은 분들께

에이전트 스킬 진화와 하네스 최적화에 관심 있다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
