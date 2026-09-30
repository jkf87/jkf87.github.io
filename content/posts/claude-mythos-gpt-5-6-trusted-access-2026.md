---
title: "Claude Mythos는 왜 일반 공개 안 하나: 벤치마크 포화와 GPT-5.6·Opus 5 접근 통제 정리"
date: 2026-09-30
author: 한준구(코난쌤)
description: "2026년 4~9월 Anthropic·OpenAI 출시 6건을 접근 통제와 안전장치 축으로 합친 통합 정리. 시스템카드 PDF 4종을 직접 내려받아 핵심 수치를 대조했습니다."
tags:
  - LLM 에이전트
  - 벤치마크
  - 모델 라인업
  - AI 안전
refactor_hub_id: model-releases-02
aliases:
  - claude-mythos-preview-explained
  - claude-opus-4-8-system-card
  - 2026-06-03-anthropic-expanding-project-glasswing
  - openai-gpt-5-6-preview-system-card-2026-06-27
  - posts/claude-opus-5-system-card-deep-dive-2026-07-25
  - posts/claude-fable-mythos-5-1-2026-09-02
draft: false
sources_read: "논문은 다루지 않음(벤더 시스템카드·공식 발표 6종 단위). 2026-09-30에 Claude Mythos Preview(245쪽)·Claude Opus 4.8(244쪽)·Claude Fable 5.1 & Mythos 5.1(212쪽) 시스템카드 PDF를 직접 내려받아 텍스트를 추출하고 본문에서 수치를 대조했음(SWE-bench 93.9, USAMO 97.6, AECI 155.5/162.1, Terminal-Bench·CursorBench, CB-1/CB-2 판정, Firefox 147 익스플로잇 성공률). Claude Opus 5 System Card PDF와 OpenAI GPT-5.6 배포안전 문서·PDF, Anthropic 글래스윙 확대 공지를 웹에서 직접 확인했음. 이 단위에 해당하는 저자 코드·데이터 저장소는 없음"
novelty_vs_paper: "수치와 위험 판정은 전부 Anthropic·OpenAI 시스템카드와 공식 발표의 것. 이 글이 새로 만든 것은 6개 출시를 '일반 공개 vs 신뢰 접근' 두 트랙으로 묶은 접근 권한 타임라인 차트, Firefox 147 완전 익스플로잇 성공률 비교 차트, 출시 6건 통합 비교표, 2026-09-30 원문 PDF 재검증 로그임"
---
## 한눈에 보는 결론

2026년 4월부터 9월까지 Anthropic과 OpenAI가 낸 모델 6건을 하나로 합쳤습니다. 이 블로그에 나눠 써둔 글 6편을 통합한 허브 글이라 옛 글 URL은 전부 이 글로 넘어옵니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>2026년 모델 출시의 분기점은 접근 권한입니다</strong></span>. 벤치마크 점수표를 펼치기 전에 누가 쓸 수 있는지가 먼저 갈렸어요. 같은 회사가 같은 시기에 일반 공개 트랙과 신뢰 접근(trusted access) 트랙을 함께 돌리고 있습니다.

- Anthropic은 Claude Mythos Preview를 만들고도 <span style="background-color: #fff59d"><strong>일반 공개를 하지 않았습니다</strong></span>. Project Glasswing이라는 방어 전용 프로그램으로만 풀었습니다.
- OpenAI는 GPT-5.6 세 형제(Sol·Terra·Luna) 전부를 생물·화학·사이버 영역에서 <span style="background-color: #fff59d"><strong>High 역량으로 분류</strong></span>하고 제한 프리뷰로 돌렸습니다. 작고 빠른 모델까지 High를 받은 건 이 패밀리가 처음입니다.
- Anthropic은 9월에 <span style="background-color: #fff59d"><strong>같은 기본 모델을 Fable 5.1(일반 공개)과 Mythos 5.1(신뢰 접근)로 쪼개서</strong></span> 내놨습니다. 시스템카드 원문은 <span style="background-color: #fff59d"><strong>"두 모델은 같은 기반 모델을 공유하고 안전장치만 다르다"</strong></span>고 적고 있어요.

기준일은 2026-09-30입니다. 블로그봇이 시스템카드 PDF 4종을 직접 내려받아 수치를 대조했고, 원문에서 재확인된 수치와 멤버 글 기록으로만 남는 수치를 분리해 적었습니다.

| 출시 | 발표 | 접근 트랙 | 위험·안전 분류 | 이번 실행에서 확인된 포인트 |
| --- | --- | --- | --- | --- |
| Claude Mythos Preview | 04-07 | Glasswing 초청 전용 | 일반 공개 보류 | <span style="background-color: #fff59d"><strong>SWE-bench Verified 93.9%, USAMO 97.6%</strong></span> |
| Claude Opus 4.8 | 05-28 | 일반 공개 | ASL-3 유지 | AECI 155.5, Mythos Preview 프런티어 미진입 |
| GPT-5.6 Preview (Sol·Terra·Luna) | 06-25 | 제한 프리뷰 | 생물·화학·사이버 High | <span style="background-color: #fff59d"><strong>자동 레드팀 70만 A100e GPU시간</strong></span> |
| Claude Opus 5 | 07-24 | 일반 공개 | ASL-3 유지, CB-1 | AECI 162.1, Mythos 5와 통계적으로 구분 안 됨 |
| Claude Fable 5.1 | 09-02 | 일반 공개 | CB-1, CB-2 미달 | Terminal-Bench-Science 0.1 52.6% |
| Claude Mythos 5.1 | 09-02 | 신뢰 접근 | CB-1, CB-2 미달 | Terminal-Bench 4.0 60.9% |

![2026년 4월부터 9월까지 모델 출시가 일반 공개 트랙과 신뢰 접근 트랙으로 갈라지는 타임라인](../media/claude-mythos-gpt-5-6-trusted-access-2026/access-timeline-2026.png)

## 무엇을 비교했나

이 글은 2026-04-14 ~ 2026-09-02에 나눠 쓴 글 6편을 합친 허브입니다. 각 멤버 글이 다루던 원문 6종입니다.

1. [Claude Mythos Preview 시스템카드 PDF](https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf) — 미공개 최상위 모델의 능력과 배포 보류 사유.
2. [Claude Opus 4.8 System Card PDF](https://cdn.sanity.io/files/4zrzovbb/website/c886650a2e96fc0925c805a1a7ca77314ccbf4a6.pdf) — RSP 위협모델별 판정과 안전장치 효과.
3. [Expanding Project Glasswing (Anthropic)](https://www.anthropic.com/research/expanding-project-glasswing) — 150개 조직 확대와 방어자 지원 전략.
4. [GPT-5.6 Preview System Card (OpenAI)](https://deploymentsafety.openai.com/gpt-5-6-preview) — 세 형제 전원 High 판정과 배포 운영.
5. [Claude Opus 5 System Card PDF](https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf) — ASL-3 유지 판단의 근거 수치.
6. [Claude Fable 5.1 & Claude Mythos 5.1 System Card PDF](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf) — 같은 모델 두 구성의 안전장치 차등.

보조로 [GPT-5.6 PDF 원문](https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf)도 직접 내려받아 대조했습니다.

## 방법 비교

여섯 출시를 같은 축(왜 통제하나, 무엇을 쟀나, 무엇으로 막나)에 올리면 아래 표와 같습니다.

| 출시 | 통제 이유 | 핵심 근거 수치 | 안전장치·배포 방식 |
| --- | --- | --- | --- |
| Mythos Preview | 사이버 역량 과잉 | 주요 OS·브라우저 제로데이 자율 탐지 능력(카드 명시), SWE-bench 93.9% | Glasswing 초청, 방어 목적만, 참여사에 크레딧 지원 |
| Opus 4.8 | RSP 임계 확인 | AECI 155.5로 프런티어 미진입, CyberGym 78.8% | Tier-3 분류기로 CyberGym 1.0%까지 차단 |
| GPT-5.6 | 생물·화학·사이버 High | 70만 A100e GPU시간 자동 레드팀, universal jailbreak 추가 완화 후 0% | activation classifier + safety reasoner, 신뢰 접근 |
| Opus 5 | CB-1 도달, CB-2 미달 | AECI 162.1(Mythos 5 161.3과 통계적 동급) | 소스코드 취약점 탐색 허용, 바이너리는 차단 |
| Fable 5.1 / Mythos 5.1 | CB-1, CB-2 미달 | Terminal-Bench 4.0 55.8% / 60.9%, CursorBench max 73.4% | 같은 기반 모델, 안전장치만 다른 두 구성 |

능력은 계속 일반 모델 쪽으로 넘어오고 있습니다. Opus 4.8 시스템카드에서 Opus 4.8의 Firefox 147 완전 익스플로잇 성공률은 8.8%(22/250)였는데, Opus 5는 52.4%(131/250)까지 올라왔어요. 같은 평가에서 신뢰 접근 트랙의 Mythos 5는 88.4%(221/250)입니다. <span style="background-color: #fff59d"><strong>일반 공개 모델이 신뢰 접근 모델 수준에 가까워지는 속도</strong></span>가 핵심이에요.

![Firefox 147 완전 익스플로잇 성공률을 모델별로 비교한 막대 차트](../media/claude-mythos-gpt-5-6-trusted-access-2026/firefox147-exploit-gap.png)

안전장치는 켜면 결과가 달라집니다. Opus 4.8은 안전장치 없이 CyberGym 표적 취약점을 78.8% 재현했는데 <span style="background-color: #fff59d"><strong>Tier-3 안전장치를 켜면 1.0%로 떨어집니다</strong></span>. Firefox 평가에서도 <span style="background-color: #fff59d"><strong>안전장치 on 조건에선 Opus 4.7·4.8 모두 0점</strong></span>이었습니다. 같은 모델의 수치가 조건에 따라 78.8%와 1.0%로 갈리니, 조건 표기 없이 인용하면 오독이 생깁니다.

벤치마크가 먼저 포화됩니다. Mythos Preview 카드는 Cybench에 대해 <span style="background-color: #fff59d"><strong>"현 프런티어 모델의 역량을 더 이상 유의미하게 측정하지 못한다"</strong></span>고 적고 35문제 서브셋만 돌렸습니다. 그래서 이후 카드들은 ExploitBench 같은 개방형 과제로 갈아탔어요. 벤치마크를 비교할 때는 그 벤치마크의 수명부터 확인하면 됩니다.

가격 경쟁은 일반 트랙에서만 붙습니다. Fable 5.1은 CursorBench 미디엄에서 68.0%를 과제당 $3.53로 냈고, GPT-5.6 Sol 맥스가 67.2%에 $5.69인 것과 비교됩니다. 신뢰 접근 트랙은 심사와 용도 제한이 가격보다 앞에 와요.

## 언제 무엇을 쓰나

- 일반 API로 코딩·지식 작업을 돌린다면: Fable 5.1 같은 일반 공개 모델이 기본값입니다. 벤치마크 중간 지점(미디엄)의 비용 효율이 실무 지표로 더 유용해요.
- 보안 연구·방어 목적이라면: Claude Security(엔터프라이즈) 또는 Glasswing 파트너십 경로만 Mythos급 역량에 닿습니다. 신뢰 접근 심사를 전제로 계획을 세우면 됩니다.
- 모델 간 비교 자료를 만든다면: 포화 벤치마크(Cybench)는 빼고, 안전장치 조건을 명시한 최신 벤치(ExploitBench, Terminal-Bench)를 쓰세요.
- 벤더 발표 수치를 인용한다면: 자체 보고라는 한계를 함께 달고, 시스템카드 원문의 조건(안전장치 on/off, 시행 횟수)까지 확인하는 순서로 읽으면 됩니다.

## 블로그봇이 직접 확인한 것

이 실행에서 블로그봇이 직접 한 일입니다.

- 시스템카드 PDF 4종(Mythos Preview 245쪽, Opus 4.8 244쪽, Fable/Mythos 5.1 212쪽, Opus 5)을 내려받아 텍스트를 추출하고 핵심 수치를 원문에서 대조했습니다. SWE-bench 93.9%, USAMO 97.6%, AECI 155.5/162.1, Firefox 147 관련 수치, "같은 기반 모델" 문장 전부 원문에 있음을 확인했어요.
- Glasswing 확대 공지와 GPT-5.6 배포안전 문서를 웹에서 직접 받아 150개 조직·10,000건 취약점, Sol·Terra·Luna 전원 High, 70만 A100e GPU시간을 확인했습니다.
- Opus 4.8 카드 URL은 HTTP 200과 파일명(Claude Opus 4.8 System Card.pdf)까지 확인했고, 다운로드·추출 스크립트와 로그는 sandbox-lane-d/<slug>/에 남겨뒀습니다.

## 한계와 반론

- <span style="background-color: #fff59d"><strong>여섯 문서 전부 벤더 자체 보고입니다.</strong></span> 외부 기관 검증은 일부(UK AISI 등)에 그치고, 이 글도 자체 보고를 그대로 옮기는 한계가 있습니다.
- Mythos의 "Cybench 100%"라는 표현은 언론 보도 기반이고 카드 원문에는 없어서, 카드 문구대로 '포화'로만 적었습니다. OpenBSD 27년 버그 같은 세부도 같은 이유로 뺐어요.
- GPT-5.6 내부 CTF 96.7% 등 일부 수치는 멤버 글 기록으로만 남아 본문에서 빼두었습니다.
- 가격·크레딧 정책은 발표문 기준이라 시스템카드 수치보다 변동 가능성이 큽니다.
- 이 글은 2026-09-30 기준입니다. 접근 정책과 안전장치 구성은 이후 계속 바뀔 수 있어요.

## 적용 규칙

- 모델 비교표를 볼 때 <span style="background-color: #fff59d"><strong>접근 트랙(일반 공개인지, 신뢰 접근인지) 열을 성능 열보다 먼저</strong></span> 확인할 것. 이 실행에서 같은 회사가 두 트랙을 병행한 사례가 3건 확인됐습니다.
- 사이버 능력 수치는 안전장치 조건을 붙여 인용할 것. Opus 4.8 기준 78.8%와 1.0%는 같은 모델의 다른 조건입니다.
- 포화 벤치마크 점수는 비교 근거에서 제외할 것. 벤더 스스로 측정 가치가 없다고 밝힌 벤치입니다.
- 벤더 자체 평가를 인용할 때는 '자체 보고'임을 표시하고 가능하면 원문 조건(시행 수, 안전장치 on/off)까지 확인할 것.
- 수치에는 기준일을 남길 것. 이 글의 기준일은 <span style="background-color: #fff59d"><strong>2026-09-30</strong></span>입니다.

## 자주 묻는 질문

Q. Claude Mythos는 일반 사용자도 쓸 수 있나요?
지금은 아니에요. Mythos 5.1은 심사를 통과한 개인·조직 대상 신뢰 접근 프로그램으로만 제공되고, 그 역량 일부는 Claude Security(엔터프라이즈)로만 간접 제공됩니다.

Q. Fable 5.1과 Mythos 5.1은 다른 모델인가요?
시스템카드 기준으로 같은 기반 모델이고 안전장치 구성만 다릅니다. Terminal-Bench 4.0 격차(55.8% vs 60.9%)에 대해 Anthropic은 안전장치가 개입한 과제 차이로 설명해요.

Q. GPT-5.6은 왜 세 모델 전부 High인가요?
생물·화학과 사이버 영역에서 novice 행위자에게 의미 있는 지원을 줄 수 있는지가 High 기준인데, 가장 작고 빠른 Luna까지 그 기준을 넘었다고 OpenAI가 판단했기 때문입니다.

Q. 옛 글 URL은 어떻게 되나요?
이 허브가 6편의 멤버 글을 통합했습니다. 옛 URL 6개는 aliases로 전부 이 글로 리디렉트됩니다.

## 참고 자료

- [Claude Mythos Preview System Card (PDF)](https://www-cdn.anthropic.com/08ab9158070959f88f296514c21b7facce6f52bc.pdf)
- [Claude Opus 4.8 System Card (PDF)](https://cdn.sanity.io/files/4zrzovbb/website/c886650a2e96fc0925c805a1a7ca77314ccbf4a6.pdf)
- [Expanding Project Glasswing — Anthropic](https://www.anthropic.com/research/expanding-project-glasswing)
- [GPT-5.6 Preview System Card — OpenAI Deployment Safety](https://deploymentsafety.openai.com/gpt-5-6-preview)
- [GPT-5.6 Preview System Card (PDF)](https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf)
- [Claude Opus 5 System Card (PDF)](https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf)
- [Claude Fable 5.1 & Claude Mythos 5.1 System Card (PDF)](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20&%20Claude%20Mythos%205.1%20System%20Card.pdf)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
