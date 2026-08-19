---
title: 지식노동 에이전트의 파일 꼬임 문제와 버전 계약 — StagedWorkspace 정리
tags:
  - agent
  - harness
  - workspace
  - paper-review
---

지식노동 에이전트가 흔히 겪는 실패 하나를 정리했습니다. <span style="background-color: #fff59d"><strong>에이전트가 검색한 파일, 수정한 파일, 제출한 파일이 서로 다른 버전인 경우</strong></span>가 있다는 겁니다. 이 논문은 그걸 막는 방법을 제안합니다.

논문: StagedWorkspace: A Versioned Workspace for Knowledge-Work Agents (arXiv 2608.18050, 2026-08-18)

## 문제가 뭔가

코딩 에이전트는 repo 체크아웃 상태에서 검색·수정·테스트가 하나의 상태를 공유합니다. SWE-bench 스타일 인터페이스죠.

근데 문서 작업 에이전트는 다릅니다. PDF, 스프레드시트, 슬라이드를 다룰 때:

- 검색은 파싱된 인덱스(마크다운 변환본)에서 하고
- 수정은 원본 파일(xlsx, docx)에서 하고
- 검토는 또 다른 시점의 diff로 하고
- 제출은 또 다른 파일 상태로 함

각 단계가 다른 버전의 워크스페이스를 참조할 수 있습니다. 예를 들어 <span style="background-color: #fff59d"><strong>한 통합문서 버전에서 열 정의를 읽어오고, 다른 버전을 수정하고, 사용한 근거와 일치하지 않는 결과물을 내놓는</strong></span> 식이요. 논문은 이걸 <span style="background-color: #fff59d"><strong>명시적 계약 부재</strong></span> 문제로 지목합니다.

## 제안: 워크스페이스 상태 계약

StagedWorkspace는 모든 뷰가 하나의 워크스페이스 상태에 묶이게 합니다. 핵심은 세 가지 뷰입니다.

- Wt: 현재 네이티브 워크스페이스 파일 (제출의 기준이 되는 권한 있는 상태)
- Ct: <span style="background-color: #fff59d"><strong>원본 경로와 콘텐츠 해시로 태깅된 파싱 레코드</strong></span>
- Δt: 시작 상태 W0와 현재 Wt 사이의 변경 diff

파싱 레코드는 원본 파일의 콘텐츠 해시와 함께 저장됩니다. 파일이 바뀌면 해시가 달라지고, 해당 레코드는 `stale`로 표시된 뒤 다시 파싱될 때까지 기다립니다. 이 규칙 하나로 <span style="background-color: #fff59d"><strong>grep이나 벡터 검색이 옛날 버전 증거를 지금 정보처럼 내놓는 걸 막습니다</strong></span>.

동작 순서는 이렇습니다:

1. 각 툴 배치가 끝나면 샌드박스를 워크스페이스로 동기화
2. 해시 스캔으로 바뀐 파일 식별, Wt 갱신
3. 해시가 안 맞는 파싱 레코드만 stale 마킹 후 재파싱 큐에 넣음
4. diff 도구로 Δt를 보고 나서 제출

변경 이력은 저널로 기록되고, 승격/롤백이 가능합니다.

![Figure 2: 워크스페이스 동기화의 세 가지 뷰](/images/2026-08-19-stagedworkspace-versioned-workspace/fig-2-p4-1.png)
*그림 1. Figure 2 — 파싱 캐시, 네이티브 워크스페이스, 리뷰 diff가 해시 스캔으로 동기화되는 구조 (원문 Figure 2)*

## 수치

### 전체 시스템 비교

OfficeQA Pro (<span style="background-color: #fff59d"><strong>미 재무부 게시판 PDF 약 697개</strong></span>, 1939~2025):

| 모델 | 기존 공개 최고치 | SW-AGENT (dual) |
|---|---|---|
| GPT-5.4 | 56.4 | 64.7 (+8.3) |
| Gemini 3.1 Pro | 29.3 | 63.9 (+34.6) |
| Gemini 3 Flash | 33.1 | 57.8 (+24.7) |

<span style="background-color: #fff59d"><strong>Gemini 3.1 Pro가 29.3%에서 63.9%로 뛴 게 눈에 띕니다</strong></span>. 프론티어 밖 모델일수록 워크스페이스 동기화로 복구되는 폭이 크다는 관찰이에요.

APEX-AGENTS (컨설팅/IB/법률 33개 월드, <span style="background-color: #fff59d"><strong>480개 과제, 평균 파일 166개</strong></span>):

| 모델 | 공개 Pass@1 / 평점 | SW-AGENT Pass@1 / 평점 |
|---|---|---|
| GPT-5.4 Nano | 16.9 / 25.5 | 25.0 / 42.1 (+8.1 / +16.6) |
| Gemini 3 Flash | 24.0 / 39.5 | 30.9 / 47.8 (+6.9 / +8.3) |
| GPT-5.4 | 36.0 / 52.7 | 37.7 / 53.6 (+1.7 / +0.9) |

GPT-5.4 기준으로 <span style="background-color: #fff59d"><strong>Opus 4.7 레퍼런스(33.9 / 50.6)도 넘습니다</strong></span>.

### 고정 하네스 절제 실험

인과를 확인하려고 모델·프롬프트·파서·검색기·그레이더·툴 예산을 고정하고 뷰만 바꿨습니다.

- dual vs artifact-only (원본만): <span style="background-color: #fff59d"><strong>OfficeQA Pass@1 +8.3~12.1점</strong></span>, 3개 모델 전부 paired bootstrap 유의
- dual vs parsed-only (파싱만): <span style="background-color: #fff59d"><strong>APEX 평균 루브릭 +4.7~9.2점</strong></span>, 3개 모델 전부 유의

태스크 성격에 따라 기여 뷰가 갈립니다. OfficeQA는 증거 탐색이 병목이라 파싱 뷰가, APEX는 원본 파일 실행이 필요해서 네이티브 뷰가 핵심이었어요.

### diff 가시성 실험

APEX 파일 수정 과제 57개에서 <span style="background-color: #fff59d"><strong>제출 전 diff 도구 노출만 바꿨습니다</strong></span> (양쪽 다 파일 추적은 동일):

- Gemini 3 Flash: +2.5
- GPT-5.4 Mini: +8.5
- GPT-5.4 Nano: +3.8

diff가 의미론적 정확성을 보장하지는 않지만, <span style="background-color: #fff59d"><strong>제출 전에 의도와 실제 수정을 비교할 기회를 줍니다</strong></span>. 약한 에디터일수록 효과가 컸어요.

![Figure 4: HarFeast 트레이스 예시](/images/2026-08-19-stagedworkspace-versioned-workspace/fig-4-p10-2.png)
*그림 2. Figure 4 — 파싱 검색으로 설문 컬럼 가이드를 찾고, 채점되는 동일 통합문서에서 실행하는 사례 (원문 Figure 4)*

### 비용

성능 상승이 비용 증가 때문은 아닙니다. OfficeQA에서 dual은 세 모델 중 비용이 가장 낮거나 비슷한 축이고, <span style="background-color: #fff59d"><strong>Reducto parsed-only보다 빨랐습니다 (GPT-5.4: 6.1분 vs 17.3분)</strong></span>.

## 실무자에게 남는 포인트

- <span style="background-color: #fff59d"><strong>에이전트가 검색하는 캐시와 수정하는 파일을 콘텐츠 해시로 묶으면 옛 증거 참조를 막을 수 있습니다</strong></span>
- 파싱 뷰와 네이티브 뷰 중 하나만 주면 성능이 떨어지고, 둘 다 동기화해서 주는 게 최적점입니다
- 제출 전 diff 노출은 파일 수정 과제에서 추가 이득입니다
- <span style="background-color: #fff59d"><strong>코딩 에이전트의 repo 계약을 문서 작업으로 옮긴 것</strong></span>이라고 보면 됩니다

## 한계

세 가지를 논문 스스로 인정합니다. 하나, 그레이더가 최종 결과물만 채점해서 중간 상태 동기화 성공 여부를 직접 검증하지 못합니다. 둘, 공개 비교 로우는 하네스·시도 예산이 달라서 짝비교가 아닙니다. 셋, 동기화가 모든 실패를 못 없앱니다. <span style="background-color: #fff59d"><strong>APEX 452개 과제 중 188개가 모든 암(all-arm)에서 0점</strong></span>이었고, 이건 계획·도메인 추론·루브릭 준수 실패라서 상태 관리로는 안 풀립니다.

## 원문

- arXiv: https://arxiv.org/abs/2608.18050
- 코드/프로젝트 페이지는 논문에 명시된 것 없음 (2026-08-19 기준)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
