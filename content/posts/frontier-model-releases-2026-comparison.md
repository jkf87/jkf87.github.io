---
title: "2026년 프론티어 모델 출시 6종 비교: Claude Opus·GPT-5.5 가격과 벤치마크 흐름 정리"
date: 2026-09-30
author: 한준구(코난쌤)
description: "2026년 3~7월 프론티어 모델 6종(Claude Opus 4.6·4.7·4.8·Sonnet 5·Opus 5, GPT-5.5)을 가격·컨텍스트·에포트·검증 축으로 합쳐 정리했습니다. 2026-09-30 기준 공식 페이지를 직접 확인한 수치만 표로 담았습니다."
tags:
  - LLM 에이전트
  - 벤치마크
  - AI 코딩 에이전트
  - 모델 라우팅
refactor_hub_id: model-releases-01
aliases:
  - claude-opus-sonnet-4-6-1m-context-ga
  - claude-opus-4-7-review
  - gpt-5-5-deep-dive-2026-04-24
  - gpt-5-5-introducing-2026-04-24
  - 2026-05-29-claude-opus-4-8
  - claude-sonnet-5-agentic-sonnet-2026-07-01
  - posts/claude-opus-5-agentic-work-2026-07-25
draft: false
sources_read: "논문은 다루지 않음(벤더 발표 6종 단위). 2026-09-30에 공식 발표 페이지 6종(1M GA·Opus 4.7·GPT-5.5·Opus 4.8·Sonnet 5·Opus 5)과 Claude 가격 문서를 직접 fetch해 본문 텍스트와 수치를 대조했고, Opus 4.7 마이그레이션 가이드는 문서 셸만 받혀져 내용 확인 불가로 기록. GPT-5.5 API 가격·ARC-AGI-2·MRCR 세부와 Sonnet 5 토크나이저 배율은 오늘 원문에서 재확인되지 않아 멤버 글 기록으로 분리 표기. 이 단위에 저자 코드·데이터 저장소는 없음"
novelty_vs_paper: "벤치마크 수치·가격·기능은 전부 Anthropic·OpenAI 발표문의 것. 이 긘이 새로 만든 것은 6개 출시를 가격·컨텍스트·에포트·검증 4축으로 묶은 통합 비교표, 출시 타임라인·같은 하네스 비교 차트 2장, 하네스 혼용 금지 원칙 정리, 2026-09-30 원문 재검증 로그(Sonnet 5 $2/$10 영구화 확인 포함)임"
---
## 한눈에 보는 결론

2026년 3월 13일부터 7월까지 프론티어 모델이 6번 나왔습니다. Opus 4.6 1M GA, Opus 4.7, GPT-5.5, Opus 4.8, Sonnet 5, Opus 5 순입니다. 이 블로그에 나눠 써둔 글 7편을 하나로 합쳐 다시 정리했습니다.

결론부터 말하면 <span style="background-color: #fff59d"><strong>프론티어 모델 경쟁의 축이 벤치마크 정점 점수에서 비용-성능 곡선으로 넘어갔습니다</strong></span>. 여섯 출시가 같은 방향을 가리킵니다.

- 단가: Sonnet 5는 $2/$10(입력/출력, 100만 토큰당)으로 나왔고, 2026-09-30 원문 확인 결과 <span style="background-color: #fff59d"><strong>이 가격이 영구화됐습니다</strong></span>.
- 사고 예산: Opus 4.7부터 확산된 <span style="background-color: #fff59d"><strong>에포트(추론 노력) 레벨</strong></span>이 이후 출시 전체의 기본 문법이 됐습니다.
- 컨텍스트: Opus 4.6에서 <span style="background-color: #fff59d"><strong>1M 윈도우의 롱컨텍스트 프리미엄이 사라졌습니다</strong></span>.
- 검증: Opus 4.8은 자기 코드 결함을 약 4배 더 잘 잡는다고 발표했습니다.

기준일 2026-09-30. 블로그봇이 여섯 공식 발표 페이지를 직접 fetch해 수치를 대조했습니다. 원문에서 재확인한 수치와 멤버 글 기록으로만 남는 수치를 분리해서 적었습니다.

| 출시 | 발표 | 표준 입/출력($/M토큰) | 이번 실행에서 확인된 포인트 |
| --- | --- | --- | --- |
| Opus 4.6 · Sonnet 4.6 1M GA | 03-13 | 5/25 · 3/15 | 1M GA·프리미엄 없음, MRCR v2 78.3% |
| Opus 4.7 | 04-16 | 5/25 | XBOW 54.5→98.5%, 2,576px, 파괴적 API 변경 |
| GPT-5.5 | 04-23 | 5/30(기록) | TB 2.0 82.7%, OSWorld 78.7% |
| Opus 4.8 | 05-28 | 5/25(패스트 10/50) | 결함 자각 약 4배, Online-Mind2Web 84% |
| Sonnet 5 | 06-30 | 2/10(영구화) | 익스플로잇 성공률 0.0%, 에포트 곡선 |
| Opus 5 | 07-24(기록) | 5/25(패스트 2배) | Fable 5급 지능의 절반 가격, 오정렬 2.3 |

## 무엇을 비교했나

이 글은 2026-03-15 ~ 2026-07-25에 나눠 쓴 글 7편을 합친 허브입니다. 옛 글 URL은 이 글로 연결됩니다.

1. [1M 컨텍스트 GA](https://claude.com/blog/1m-context-ga) — Opus/Sonnet 4.6, 프리미엄 제거와 미디어 한도 6배.
2. [Claude Opus 4.7 발표](https://www.anthropic.com/news/claude-opus-4-7) — 코딩 자율성, 시각 해상도, 파괴적 API 변경.
3. [GPT-5.5 소개](https://openai.com/index/introducing-gpt-5-5/) — 토큰 효율과 코딩 벤치.
4. [GPT-5.5 배포 안전 문서](https://deploymentsafety.openai.com/gpt-5-5) — 사이버보안 분류(기록).
5. [Claude Opus 4.8 발표](https://www.anthropic.com/news/claude-opus-4-8) — 에이전트 안정성과 패스트 모드.
6. [Claude Sonnet 5 발표](https://www.anthropic.com/news/claude-sonnet-5) — 미드티어 에이전트 실행층.
7. [Claude Opus 5 발표](https://www.anthropic.com/news/claude-opus-5) — 비용-성능 곡선과 안전 fallback.

보조로 [TechCrunch의 Sonnet 5 보도](https://techcrunch.com/2026/06/30/anthropic-launches-claude-sonnet-5-as-a-cheaper-way-to-run-agents/)와 [Claude 가격 문서](https://platform.claude.com/docs/en/about-claude/pricing)를 확인했습니다.

## 방법 비교

여섯 출시를 같은 축으로 놓고 비교했습니다. 가격은 100만 토큰당 입력/출력 달러입니다.

| 출시 | 가격 | 컨텍스트 | 강조 축 | 재확인된 대표 수치 | 주의점 |
| --- | --- | --- | --- | --- | --- |
| Opus 4.6 1M GA | 5/25(Sonnet 3/15) | 1M | 롱컨텍스트 평준화 | MRCR v2 78.3%, 이미지·PDF 600페이지 | 없음(베타 헤더 자동 무시) |
| Opus 4.7 | 5/25 동결 | 1M | 코딩 자율성·시각 | XBOW 54.5→98.5%, 3.75MP, 토큰 최대 1.35배 | thinking·샘플링·프리필 파괴적 변경(기록) |
| GPT-5.5 | 5/30(기록) | API 1M·Codex 400K(기록) | 토큰 효율·경제성 | TB 2.0 82.7%, OSWorld 78.7%, Tau2 98% | 사이버 상향 분류(기록) |
| Opus 4.8 | 5/25·패스트 10/50 | 1M | 안정성·정직성 | 결함 자각 약 4배, Online-Mind2Web 84% | 에포트 기본 high |
| Sonnet 5 | 2/10 영구화 | 표기 없음 | 실행층 단가 | 익스플로잇 0.0%, 에포트별 비용 곡선 | 토크나이저 배율(미재확인) |
| Opus 5 | 5/25·패스트 2배 | 발표 표기 확인 못함 | 비용-성능·판단력 | 오정렬 2.3, 패스트 2.5배속·2배가 | 안전 분류기 fallback |

![출시 타임라인과 출력 단가 흐름](../media/frontier-model-releases-2026-comparison/chart-01-release-price-timeline.png)
*그림 1. 블로그봇이 공식 페이지 6종 fetch 결과로 직접 그린 출시 타임라인. 파란 점은 2026-09-30 원문에서 단가 재확인, 주황 점은 발표문 기록 기준.*

가격 흐름이 먼저 보입니다. Opus 계열 표준 출력 단가는 4.6에서 5까지 <span style="background-color: #fff59d"><strong>$25로 얼어 있고</strong></span>, GPT-5.5가 $30(기록), Sonnet 5가 $10으로 갈라섭니다. 같은 기간 패스트 모드는 속도를 사는 별도 단가표가 됐습니다. Opus 4.8 패스트 $50, Opus 5 패스트 기본가의 2배 — 둘 다 원문에서 확인했습니다.

근데 벤치마크 숫자는 조건이 까다롭습니다. 벤더 발표 표는 자기 하네스 안에서 만든 숫자라서, 벤치가 같아야 직접 비교가 됩니다. 그래서 GPT-5.5 발표문이 같은 표에 담은 네 모델만 따로 뽑아봤습니다.

![같은 하네스 안 비교](../media/frontier-model-releases-2026-comparison/chart-02-same-bench-comparison.png)
*그림 2. GPT-5.5 발표문(2026-04-23)이 같은 표에 기록한 수치. TB 2.0 82.7%와 OSWorld 78.7%는 2026-09-30 원문에서 재확인했고, 나머지는 발표문 기록값입니다.*

여기서 <span style="background-color: #fff59d"><strong>Terminal-Bench 2.0에서는 GPT-5.5가 82.7%로 앞서는데</strong></span>, 같은 발표문의 SWE-Bench Pro 표에서는 Opus 4.7이 64.3%로 GPT-5.5(58.6%)보다 높습니다(기록).

<span style="background-color: #fff59d"><strong>벤치가 바뀌면 순서가 바뀝니다</strong></span>. 하네스를 섞어서 요약한 랭킹은 믿지 않는 편이 맞습니다.

## 언제 무엇을 쓰나

- 대량 실행형 에이전트(분류, 정리, 반복 업무): Sonnet 5. $2/$10 영구화를 원문에서 확인했습니다. 에포트를 낮게 잡아 돌리면 되구요, 품질 하한은 실제 과제로 잡아야 합니다.
- 코딩 에이전트 기본 실행: GPT-5.5 또는 Opus 5. 토큰 효율 주장(GPT-5.5)과 비용-성능 곡선 주장(Opus 5)이 방향이 다르니, 자기 코드베이스로 A/B를 돌려 정하면 됩니다.
- 고난도 판단과 최종 검토: Opus 4.8/5. 결함 자각 약 4배, 오정렬 2.3처럼 검증·정직성 지표가 강조 축입니다.
- 초장문 입력(계약서 묶음, 코드베이스 전체): 1M 윈도우. Opus 4.6부터 추가 요금이 없고, <span style="background-color: #fff59d"><strong>MRCR v2 78.3%(원문 확인)</strong></span>로 회상 정확도도 실용권에 들어왔습니다.
- 지연 시간 민감 작업: Opus 4.8/Opus 5 패스트 모드. 속도 2.5배, 단가 2배(4.8은 $10/$50)라 비용 곱셈부터 계산하세요.

## 블로그봇이 직접 확인한 것

2026-09-30에 공식 페이지를 직접 fetch해 멤버 글의 수치와 대조했습니다.

| 확인 대상 | 결과 | 원문에서 확인된 것 |
| --- | --- | --- |
| claude.com 1M GA 글 | HTTP 200 | $5/$25·$3/$15, 승수 없음, 600페이지, MRCR v2 78.3% |
| Opus 4.7 발표 | HTTP 200 | 98.5/54.5, 2,576px·3.75MP, 13%, xhigh, 1.35배 |
| GPT-5.5 발표 | HTTP 200 | TB 2.0 82.7%, OSWorld 78.7%, Tau2 98, GB200, 20%, K-1 24,771건, 주간 Codex 사용 85% |
| Opus 4.8 발표 | HTTP 200 | $5/$25·패스트 $10/$50, Online-Mind2Web 84%, 결함 자각 four times, dynamic workflows |
| Sonnet 5 발표 | HTTP 200 | $2/$10 영구화 문구, Firefox 147 익스플로잇 0.0% |
| Opus 5 발표 | HTTP 200 | $5/$25, 패스트 2.5배속·2배가, Fable 절반, 오정렬 2.3, 22% |
| Claude 가격 문서 | HTTP 200 | 단가 표기 정합 |

가장 큰 수확은 Sonnet 5 가격입니다. 멤버 글은 8월 31일까지 $2/$10 뒤 표준가 $3/$15로 바뀐다고 기록했는데, 오늘 원문에는 introductory pricing이 now permanent라는 문구가 있습니다. <span style="background-color: #fff59d"><strong>할인가가 표준가로 확정된 겁니다</strong></span>. 이 허브의 표는 이 값을 따랐습니다.

Opus 4.7 마이그레이션 가이드는 fetch해도 문서 셸(1,934자)만 돌아와서 내용 확인은 못 했습니다. 파괴적 변경 목록은 멤버 글 기록으로만 싣습니다. 차트 2장은 이 대조 결과에서 블로그봇이 직접 만들었고, 생성 스크립트는 검증 로그와 함께 보관했습니다.

## 한계와 반론

- <span style="background-color: #fff59d"><strong>모든 벤치마크 수치는 벤더 자체 보고입니다</strong></span>. 독립 기관 평가가 아닙니다.
- GPT-5.5의 API 가격 $5/$30, ARC-AGI-2 85.0%, MRCR 512K~1M 74.0%(GPT-5.4는 36.6%), 사이버보안 High 분류는 오늘 원문 텍스트에서 재확인되지 않았습니다. 멤버 글의 발표문 기록으로만 싣습니다.
- Sonnet 5 토크나이저 1.0~1.35배 주장도 재확인되지 않았습니다. 도입 전에 실제 워크로드로 토큰 수를 다시 재야 합니다.
- Opus 4.7의 SWE-Bench Pro 64.3%에는 발표문 자체가 메모리제이션 증거 각주를 달았다고 멤버 글이 기록합니다.
- <span style="background-color: #fff59d"><strong>OSWorld-Verified는 Opus 4.8 발표에서 Opus 4.7 점수가 82.3%로 재조정됐습니다</strong></span>. 같은 벤치 이름도 하네스 개정으로 점수가 바뀝니다.
- 가격과 정책은 계속 바뀝니다. 이 글의 모든 판단은 기준일 2026-09-30의 스냅샷입니다.

## 적용 규칙

1. 라우팅 표를 분기마다 다시 확인한다. 이번 실행에서도 멤버 글 기록($3/$15 전환 예고)과 현재 원문($2/$10 영구화)이 달랐습니다.
2. 벤치마크 숫자는 하네스가 같은 것끼리만 비교한다. Terminal-Bench 2.0과 2.1, OSWorld-Verified 재조정을 근거로 둡니다.
3. 모델 교체 전에 파괴적 API 변경 목록을 먼저 본다. Opus 4.7은 thinking·샘플링 파라미터·프리필을 막았다는 기록이 있습니다(가이드 원문은 오늘 확인 불가).
4. 패스트 모드는 단가 배수를 설계에 반영한다. Opus 4.8 패스트 $10/$50와 Opus 5 패스트 2배가는 둘 다 원문 확인값입니다.
5. 벤더 수치를 인용할 때는 확인 날짜를 남긴다. 이 글의 fetch 로그처럼 <span style="background-color: #fff59d"><strong>재현 가능한 기록이 나중에 차이를 잡아줍니다</strong></span>.

## 자주 묻는 질문

- 지금 에이전트 실행 모델 중 단가가 가장 낮은 선택은 무엇인가요? Sonnet 5입니다. <span style="background-color: #fff59d"><strong>$2/$10가 2026-09-30 원문에서 영구 가격으로 확정됐습니다</strong></span>.
- GPT-5.5와 Opus 4.7 중 코딩에는 뭘 쓰면 되나요? 같은 하네스 기록인 Terminal-Bench 2.0에서는 GPT-5.5 82.7% 대 Opus 4.7 69.4%, SWE-Bench Pro 기록에서는 Opus 4.7 64.3%가 앞섭니다. 벤치마다 순서가 다르니 실제 워크로드로 A/B 테스트하면 됩니다.
- 1M 컨텍스트는 실무에서 의미가 있나요? Opus 4.6부터 추가 요금 없이 표준가입니다. MRCR v2 78.3%(원문 확인)이라 긴 문서 회상도 실용권에 들어왔습니다.
- Opus 4.7로 올라갈 때 코드에서 고칠 부분은 무엇인가요? 멤버 글 기록 기준으로 thinking enabled를 adaptive로 바꾸고, temperature·top_p·top_k와 프리필을 제거하는 것입니다. 마이그레이션 가이드 원문 확인은 오늘 실패했으니 적용 전 공식 문서를 다시 보세요.

## 참고 자료

- Anthropic, [Claude Opus 4.6 / Sonnet 4.6 1M context GA](https://claude.com/blog/1m-context-ga)
- Anthropic, [Introducing Claude Opus 4.7](https://www.anthropic.com/news/claude-opus-4-7)
- OpenAI, [Introducing GPT-5.5](https://openai.com/index/introducing-gpt-5-5/)
- OpenAI, [GPT-5.5 배포 안전 문서(기록)](https://deploymentsafety.openai.com/gpt-5-5)
- Anthropic, [Introducing Claude Opus 4.8](https://www.anthropic.com/news/claude-opus-4-8)
- Anthropic, [Introducing Claude Sonnet 5](https://www.anthropic.com/news/claude-sonnet-5)
- Anthropic, [Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)
- TechCrunch, [Anthropic launches Claude Sonnet 5 as a cheaper way to run agents](https://techcrunch.com/2026/06/30/anthropic-launches-claude-sonnet-5-as-a-cheaper-way-to-run-agents/)
- Anthropic, [Claude 가격 문서](https://platform.claude.com/docs/en/about-claude/pricing)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
