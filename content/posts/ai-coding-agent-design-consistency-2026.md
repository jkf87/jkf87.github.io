---
title: "AI 코딩 에이전트가 만든 UI가 어딘가 비슷할 때: DESIGN.md·getdesign.md·soul.md 통합 가이드"
date: 2026-09-27
author: 한준구(코난쌤)
description: "코딩 에이전트·디자인 글 8편을 맥락 파일·워크플로·모델·평가 4층으로 합쳤습니다. getdesign 설치와 @google/design.md lint를 직접 실행했고 논문 2편은 본문까지 재검증했습니다(2026-09-27)."
tags:
  - AI 코딩 에이전트
  - 디자인 시스템
  - DESIGN.md
  - Claude Code
  - LLM 에이전트
refactor_hub_id: coding-agents-02
aliases:
  - claude-code-three-signals-2026
  - getdesign-md-design-system-ai-agent-2026-04-28
  - getdesign-md-apple-bmw-starbucks-design-system-2026-04-29
  - anthropic-natural-language-autoencoders-2026-05-25
  - design-md-coding-agent-design-system-2026-06-28
  - posts/ai-first-design-yc-eve-bouffard-2026-07-30
  - posts/motif-3-technical-report-2026-08-12
  - posts/latent-clip-latent-diffusion-control-2026-08-16
sources_read: "논문 2편(arXiv 2608.09119, 2503.08455)은 HTML 본문을 읽고 핵심 수치를 표와 대조했다. Latent-CLIP은 저자 데모 저장소(github.com/jsonBackup/Latent-CLIP-Demo) 공개를 확인했고, Motif 3는 본문에 저자 코드·가중치 공개 저장소가 없음을 확인했다. 나머지 6건은 GitHub API 메타데이터 2건, npm 레지스트리 2건, Anthropic 리서치 페이지, YC 원영상을 이번 실행에서 직접 확인했다."
novelty_vs_paper: "GDLA·MOPD 아키텍처와 latent 직접 평가는 각 논문의 기여다. 이 페이지의 몫은 옛 글 8편의 1차 출처를 2026-09-27에 재검증해 정정 내역(스타 수·npm 버전·ReNO 시간·버튼 토큰)을 남기고, 맥락 파일-워크플로-모델-평가 4층으로 재구성한 표와 getdesign/@google lint 직접 실행, 자체 제작 도표 2장이다."
draft: false
---

## 한눈에 보는 결론

2026-04-18부터 2026-08-16까지 이 블로그에 쌓인 코딩 에이전트·디자인 글 8편을 한 페이지로 합쳤다. 검증일은 2026-09-27이다. 옛 글 주소는 이 페이지로 리디렉션된다.

8편을 다시 읽고 1차 출처를 전부 확인하니 결국 같은 질문이었다. 에이전트가 만든 UI가 왜 매번 평균값처럼 나오는가, 그리고 디자이너의 취향을 어떻게 에이전트에 옮기고 유지하고 검증할 것인가.

정리한 답은 4층 구조다. <span style="background-color: #fff59d"><strong>맥락 파일 → 워크플로 → 모델·실행 → 평가·검증</strong></span>. 파일로 주입하고, 워크플로로 다듬고, 모델이 실행하고, 기계로 검증한다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>취향은 파일·워크플로·평가 장치로 외부화될 때 에이전트에 이식된다</strong></span>.

| 근거 | 수치·결과 | 출처 |
|---|---|---|
| 브랜드 디자인 파일 설치 | npx 한 줄, 562행 DESIGN.md 생성 | getdesign.md (직접 실행) |
| 두 DESIGN.md 생태계 호환 | lint 0 errors, 8 warnings | @google/design.md 0.4.0 (직접 실행) |
| 취향 전달 경로 5가지 | 말·이미지·문서·실제 콘텐츠·파라미터 | YC Design 영상 |
| 이미지 평가 비용 절감 | ReNO 11.59초 → 9.11초(약 21% 감소) | arXiv 2503.08455 본문 |
| 에이전트용 백본 설계 | 총 314B 중 토큰당 13.2B 활성 | arXiv 2608.09119 본문 |
| 모델 내면 감사 | 평가 인식 26% vs 실사용 1% 미만 | Anthropic NLA |

![코딩 에이전트에 디자인 감각을 주는 4개 층](../media/ai-coding-agent-design-consistency-2026/design-context-four-layers.png)

## 무엇을 비교했나

8편의 옛 글이 각각 한 항목에 대응한다. 링크는 이번 실행(2026-09-27)에 다시 확인한 1차 출처이다.

1. [getdesign.md (VoltAgent/awesome-design-md)](https://github.com/VoltAgent/awesome-design-md) — 유명 브랜드 디자인 시스템을 DESIGN.md로 정리한 라이브러리. MIT.
2. [DESIGN.md 스펙 (google-labs-code/design.md)](https://github.com/google-labs-code/design.md) · [포맷 문서](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) — 토큰 YAML과 산문을 함께 쓰는 포맷과 lint·diff·export CLI. Apache-2.0.
3. [YC 영상, YC's Head of Design Shows You How To Design With AI](https://www.youtube.com/watch?v=VbqaL_eHhKY) — Eve Bouffard의 AI-first 디자인 워크플로.
4. [Anthropic, Natural Language Autoencoders](https://www.anthropic.com/research/natural-language-autoencoders) — 모델 활성화를 자연어로 바꿔 읽는 감사 방법.
5. [Motif 3 Technical Report (arXiv 2608.09119)](https://arxiv.org/abs/2608.09119) — 에이전트 작업을 겨냥한 MoE 백본 모델.
6. [Latent-CLIP (arXiv 2503.08455)](https://arxiv.org/abs/2503.08455) · [데모 저장소](https://github.com/jsonBackup/Latent-CLIP-Demo) — 이미지를 디코딩하지 않고 latent에서 바로 평가하는 CLIP.
7. [AI타임즈 클로드 디자인 기사](https://www.aitimes.kr/news/articleView.html?idxno=39607) — 자연어로 디자인하고 코드로 넘기는 흐름의 신호.
8. [오마이뉴스 Mythos 칼럼](https://n.news.naver.com/mnews/article/047/0002512543) · [METR time-horizon 글](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/) — 권한 설계 논쟁과 긴 작업 수행력 측정.

## 방법 비교

| 방법 | 푸는 문제 | 핵심 아이디어 | 확인된 근거(9/27) | 비용·한계 |
|---|---|---|---|---|
| getdesign.md | 브랜드 톤 부재 | 완성된 브랜드 DESIGN.md를 npx 한 줄로 설치 | apple·bmw·starbucks 직접 생성 | 역공학 큐레이션, 비공식 |
| DESIGN.md 스펙+CLI | 세션이 지나며 일관성 붕괴 | 토큰 YAML+산문, lint·diff·export | getdesign 파일이 lint 통과(0 error) | alpha 포맷 |
| YC 워크플로 | 취향 전달 손실 | 말·mood board·soul.md·실제 콘텐츠·파라미터 | 원영상 확인 | 사람이 계속 기록해야 한다 |
| Motif 3 | 에이전트 백본 비용 | expert 384개 중 토큰당 8개, 활성 13.2B | 본문 표 대조, GDLA 9.2% 적은 토큰 | 가중치 비공개 |
| Latent-CLIP | 이미지 평가 비용 | latent를 직접 입력받는 CLIP | ReNO 21% runtime 감소 확인 | VAE마다 재학습 |
| NLA | 블랙박스 감사 | 활성화→텍스트→활성화 왕복으로 설명 품질 측정 | 26% vs 1% 미만 확인 | 추론 비용이 크다 |

같은 버튼 토큰을 놓고 세 브랜드의 답은 이렇게 다르다. 이 차이가 파일 하나로 에이전트에 전달된다.

![세 브랜드의 버튼 토큰 차이](../media/ai-coding-agent-design-consistency-2026/brand-button-radius-chart.png)

<span style="background-color: #fff59d"><strong>디자인 토큰은 값을 고정하고, 산문은 판단을 고정한다</strong></span>. Google Labs의 철학 문서가 강조하는 지점이다. `#B8422E` 같은 값은 색만 알려준다. 그 색을 어디에 쓰고 얼마나 아낄지는 산문이 담당한다.

## 언제 무엇을 쓰나

| 상황 | 먼저 할 것 | 근거 |
|---|---|---|
| 사이드 프로젝트인데 분위기가 급하다 | getdesign으로 유명 브랜드 파일부터 설치 | 3브랜드 직접 생성 확인 |
| 우리 팀 브랜드가 이미 있다 | DESIGN.md 스펙으로 자체 작성 후 lint | WCAG 경고 자동 감지 확인 |
| 채팅에서 같은 디자인 피드백이 반복된다 | 그 피드백을 파일 규칙으로 승격 | DESIGN.md 문서의 권장 사용법 |
| 결과가 늘 뻔하게 나온다 | mood board·실제 콘텐츠·transcript부터 준비 | YC 워크플로의 취향 5경로 |
| 생성 이미지 검수 비용이 아깝다 | latent 단계 평가 도입 검토 | ReNO 21% 감소 |
| 에이전트가 평가를 인식하는지 걱정된다 | NLA류 감사 도구로 활성화 확인 | SWE-bench 26% 사례 |

## 블로그봇이 직접 확인한 것

2026-09-27, macOS 26.5.1(arm64)에서 OpenClaw 에이전트가 직접 실행했다. 검증 방법과 결과를 정리했습니다.

먼저 설치다. <span style="background-color: #fff59d"><strong>npx getdesign@latest add apple 한 줄로 562행짜리 DESIGN.md가 생성됐다</strong></span>. bmw, starbucks도 각각 exit 0으로 생성됐다. apple 파일에는 색 21개, 타이포그래피 스케일 16개, 라운딩 7단계, 컴포넌트 24개가 담겼다.

![getdesign 설치 실행 캡처](../media/ai-coding-agent-design-consistency-2026/getdesign-install-capture.png)

다음은 호환성이다. getdesign 파일을 Google Labs의 linter(`npx @google/design.md lint`)에 넣어봤다. <span style="background-color: #fff59d"><strong>결과는 0 errors, 8 warnings. 두 생태계가 사실상 같은 포맷으로 수렴했다</strong></span>.

![google design.md lint 실행 캡처](../media/ai-coding-agent-design-consistency-2026/getdesign-lint-capture.png)

경고 8개 중 하나는 실제 결함이었다. <span style="background-color: #fff59d"><strong>text-link의 대비가 3.77:1로 WCAG AA 기준 4.5:1에 못 미친다는 것을 기계가 잡아냈다</strong></span>. 나머지 6개는 한 번도 참조되지 않은 고아 토큰 경고다. 사람 눈으로는 놓치기 쉬운 지점이다.

옛 글 주장 네 가지는 이번 검증에서 고쳤다.

- getdesign 저장소 스타 수: 옛 글은 66.9k라고 썼다. 지금 GitHub API는 <span style="background-color: #fff59d"><strong>118,196개</strong></span>다. 5개월 만에 두 배 가까이 늘었다.
- @google/design.md npm 버전: 옛 글은 0.3.0. 지금은 <span style="background-color: #fff59d"><strong>0.4.0</strong></span>이다. getdesign npm은 0.6.25.
- Latent-CLIP의 ReNO 실행 시간: 옛 글은 11.59초 → 9.01초라고 썼다. 논문 표를 다시 읽으니 <span style="background-color: #fff59d"><strong>11.59초 → 9.11초(약 21% 감소)</strong></span>가 맞다.
- Apple 버튼 모양: 옛 글은 라운드 11px 소형 알약형이라고 관찰했다. 지금 생성되는 파일은 <span style="background-color: #fff59d"><strong>버튼에 pill(9999px)을 쓴다</strong></span>. 템플릿이 바뀐 것이다. BMW는 0px, Starbucks는 50px 그대로다.

논문 2편은 초록으로 끝내지 않고 HTML 본문을 읽었다. Motif 3는 314B·13.2B·expert 384개·256K context를 본문 표와 대조했고, <span style="background-color: #fff59d"><strong>한국어 압축이 5.31 bytes/token으로 Qwen3.5(4.03), Gemma-4(3.73)보다 좋다</strong></span>는 표도 확인했다.

다만 <span style="background-color: #fff59d"><strong>저자 코드나 가중치 공개 저장소는 논문에 없다</strong></span>.

Latent-CLIP은 본문의 73.5 top-1, 84.6%, 21% 감소 수치를 대조했고, 저자 데모 저장소가 공개된 것을 확인했다.

Anthropic NLA 페이지도 다시 읽었다. <span style="background-color: #fff59d"><strong>SWE-bench Verified의 26% 사례에서 평가 인식 징후가 나왔고, 실제 claude.ai 사용에서는 1% 미만이었다</strong></span>. 학습 코드와 Neuronpedia 데모가 공개된 것도 확인했다.

## 한계와 반론

- getdesign은 공식 디자인 시스템이 아니다. 사이트 스스로 큐레이션 재현이라고 밝힌다. <span style="background-color: #fff59d"><strong>프로덕션 브랜드에는 자체 파일을 쓰는 게 맞다</strong></span>.
- YC 워크플로는 한 디자이너의 사례다. 취향 5경로가 일반화된 방법론인지는 검증되지 않았다.
- NLA는 환각할 수 있고 비싸다. 활성화 하나 읽는 데 수백 토큰이 나간다고 Anthropic 스스로 밝힌다.
- Latent-CLIP은 VAE 종속이다. SDXL(4채널)용 모델을 FLUX(16채널)에 그대로 못 쓴다. 논문도 재학습이 필요하다고 명시한다.
- Motif 3의 벤치마크 순위는 같은 harness에서 재평가된 게 아니다. <span style="background-color: #fff59d"><strong>숫자는 표 그대로 읽고 순위는 과하게 읽지 않는다</strong></span>.
- lint 통과가 디자인 품질을 보장하지 않는다. 이번 실행도 고아 토큰이나 대비 같은 구조 결함만 잡았다.

## 적용 규칙

- 에이전트에게 UI를 맡기기 전에 프로젝트 루트에 DESIGN.md(또는 soul.md)를 둔다. 이번 실행으로 설치와 lint가 실제로 동작하는 것을 확인했다.
- 파일은 토큰과 산문 두 층으로 쓴다. 값만 적으면 평범한 토큰 파일이 되고, 참조점이 있는 문장이 판단을 전달한다.
- lint를 CI에 넣는다. 깨진 토큰 참조와 낮은 대비는 이번 실행처럼 기계가 잡을 수 있다.
- 채팅에서 한 번 말한 디자인 피드백은 파일 규칙으로 옮긴다. 그래야 다음 세션에서 사라진다.
- <span style="background-color: #fff59d"><strong>빈 프롬프트에서는 평균값이 나온다</strong></span>. mood board와 실제 콘텐츠를 함께 준다.
- 통과 기준은 확인 가능한 조건으로 적는다. 4초 루프를 시작과 끝이 같은 픽셀로 검사하는 식이다.
- 유명 브랜드 파일은 시작점으로만 쓴다. 공식 가이드가 필요한 자리에는 직접 작성한다.

## 참고 자료

- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) · [getdesign npm](https://www.npmjs.com/package/getdesign)
- [google-labs-code/design.md](https://github.com/google-labs-code/design.md) · [DESIGN.md Format](https://github.com/google-labs-code/design.md/blob/main/docs/spec.md) · [@google/design.md npm](https://www.npmjs.com/package/@google/design.md)
- [YC, YC's Head of Design Shows You How To Design With AI](https://www.youtube.com/watch?v=VbqaL_eHhKY) · [Paxel](https://paxel.ycombinator.com) · [SOTA Zine](https://www.sotazine.com)
- [Anthropic, Natural Language Autoencoders](https://www.anthropic.com/research/natural-language-autoencoders)
- [Motif 3: Technical Report (arXiv 2608.09119)](https://arxiv.org/abs/2608.09119)
- [Controlling Latent Diffusion Using Latent CLIP (arXiv 2503.08455)](https://arxiv.org/abs/2503.08455) · [Latent-CLIP-Demo](https://github.com/jsonBackup/Latent-CLIP-Demo)
- [AI타임즈, 클로드 디자인 기사](https://www.aitimes.kr/news/articleView.html?idxno=39607)
- [오마이뉴스, 미토스 칼럼](https://n.news.naver.com/mnews/article/047/0002512543) · [METR, Measuring AI Ability to Complete Long Tasks](https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.