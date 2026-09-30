---
title: "AI 에이전트와 브라우저·화면 작업을 나눠 쓰는 법: ego lite, macshot, VOID, PolicyGuide 통합 정리"
date: 2026-09-30
author: 한준구(코난쌤)
description: "사람이 쓰는 브라우저·캡처·영상·문서 작업에 AI를 붙이는 도구와 기법을 옛 글 11편에서 다시 정리했습니다. ego lite 브라우저 공유, macshot 캡처, Netflix VOID 영상 편집, PolicyGuide 정책 검증, MobileMoE 온디바이스 기준까지 원문 확인 결과와 함께 묶었습니다."
tags:
  - AI 에이전트
  - GUI 에이전트
  - 브라우저 자동화
  - 오픈소스 도구
refactor_hub_id: web-gui-agents-02
aliases:
  - webtooni-automation-guide
  - macshot-macos-screenshot-tool
  - openclaw-book-preorder-guide-korea
  - netflix-void-video-object-interaction-deletion-guide
  - voice-agent-ecosystem-direction-modupop-guide
  - gsap-scrolltrigger-guide-2026-04-24
  - claude-knowledge-graph-construction-guide-2026-05-07
  - ai-engineering-from-scratch-guide-2026-05-24
  - 2026-06-04-mobilemoe-on-device-moe
  - posts/ego-lite-parallel-agent-browser-2026-07-24
  - posts/2026-08-26-policyguide-workflow-verifier
draft: false
sources_read: "논문 3편(2604.02296, 2608.19861, 2605.27358) 초록과 HTML 본문을 fetch해 핵심 수치를 대조했고, ego lite·macshot·AI Engineering from Scratch는 GitHub 저장소와 README 원문을 확인(README의 2.5배 벤치마크 문구, 스타 3,636, 523레슨·342시간), VOID는 Hugging Face 모델 카드까지 확인, GSAP 문서·Anthropic 쿡북·모두팝 발표 영상 HTTP 200 확인. 웹툰이는 원본 서비스 확인 불가. 저자 코드 실행·재현은 이번 실행 범위 밖"
novelty_vs_paper: "각 논문·저장소의 방법과 수치는 전부 원출처 것이며, 이 글이 새로 만든 것은 흩어진 단일 소개글 11편을 함께 쓰기·문서화·편집·검증·기반의 5역할 축으로 재배치한 비교 구조와 대조 표, 직접 그린 지도·수치 차트 2장, 2026-09-30 원문 재확인 로그(커리큘럼 435→523 레슨 정정, 확인 불가 항목 삭제 포함)임"
---

## 한눈에 보는 결론

본 사이트에 분산되어 있던 단일 소개 글 11편을 통합하여 재구성하였습니다. 주제는 상이하나 공통 주제는 하나입니다. <span style="background-color: #fff59d"><strong>사용자가 사용하는 화면 환경에 AI를 적용하는 방법</strong></span>입니다. 통합 결과는 다음 5개 역할로 분류됩니다.

- 병렬 사용: ego lite — 동일 Chromium 브라우저에서 <span style="background-color: #fff59d"><strong>사람과 에이전트가 각자 격리 작업공간(Space)을 사용</strong></span>
- 문서화: macshot — <span style="background-color: #fff59d"><strong>캡처, 주석, OCR, PII 자동 가림을 무료 오픈소스로 처리</strong></span>
- 영상 편집: Netflix VOID — 객체와 물리적 상호작용을 포함한 영상 인페인팅(<span style="background-color: #fff59d"><strong>GPU 40GB 이상 필요</strong></span>)
- 정책 준수: PolicyGuide — 정책 문서의 워크플로 그래프 컴파일과 외부 검증기 추적
- 실행 기반: MobileMoE(온디바이스 MoE), Claude 지식 그래프, GSAP ScrollTrigger, 음성 실패 복구 설계

![화면 작업에 AI를 붙이는 지도](../media/ai-agent-browser-screen-tools-guide-2026/chart-01-screen-tools-map-2026-09-30.png)

이 중 2편은 이번 실행에서 원본 확인에 실패했습니다. 웹툰이라는 캐릭터 생성 서비스는 원본을 찾지 못해 세부 정보를 싣지 않았고, 오픈클로 책 예판 안내는 기한이 지난 공지라 링크 정보만 유지합니다.

## 무엇을 비교했나

1. [ego lite](https://github.com/citrolabs/ego-lite): 사람·에이전트 병렬 브라우저. 저장소 MIT, 브라우저는 별도 무료 배포, 2026-09-30 기준 macOS 전용.
2. [macshot](https://github.com/sw33tLie/macshot): macOS 캡처·녹화 도구. 확인 시점 스타 3,636개.
3. [Netflix VOID](https://arxiv.org/abs/2604.02296): quadmask 4값 조건부 비디오 인페인팅. [Hugging Face 모델 카드](https://huggingface.co/netflix/void-model) 공개.
4. [PolicyGuide](https://arxiv.org/abs/2608.19861): τ²-bench 3개 도메인 <span style="background-color: #fff59d"><strong>mean Pass⁴ 0.42→0.62</strong></span>, <span style="background-color: #fff59d"><strong>telecom 0.19→0.61</strong></span>.
5. [MobileMoE](https://arxiv.org/abs/2605.27358): <span style="background-color: #fff59d"><strong>활성 0.3~0.9B/총 1.3~5.3B</strong></span> 온디바이스 MoE. <span style="background-color: #fff59d"><strong>prefill 1.8~3.8배, decode 2.2~3.4배</strong></span> 빠름.
6. [모두팝 음성 에이전트 발표](https://www.youtube.com/watch?v=e3TWqrBxLVc): 인식 실패 복구 UX 관점.
7. [GSAP ScrollTrigger 공식 문서](https://gsap.com/docs/v3/Plugins/ScrollTrigger/): 스크롤 애니메이션 표준 플러그인.
8. [Claude 지식 그래프 쿡북](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide): 엔티티 추출·해석·다중 홉 질의.
9. [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch): MIT 커리큘럼, <span style="background-color: #fff59d"><strong>현재 523 레슨·20 페이즈·342시간</strong></span>(구 글의 <span style="background-color: #fff59d"><strong>435/320은 오류로 정정</strong></span>).
10. 웹툰이(Webtooni): 원본 서비스 확인 불가(2026-09-30), 세부 정보 제외.
11. 오픈클로 책 예판 안내: 기한 종료 공지, 링크 정보만 유지.

## 방법 비교

| 도구·기법 | 문제 | 방식 | 실행 조건 | 확인 결과(2026-09-30) |
| --- | --- | --- | --- | --- |
| ego lite | 웹 업무 자동화 시 세션·탭 충돌 | 격리 Space 병렬 사용, Chrome 데이터 이동 | macOS, 무료 | 저장소 HTTP 200, 2.5배 문구 확인 |
| macshot | 유료 캡처 앱 부담 | 캡처·주석·OCR·PII 가림 통합 | macOS, 무료 오픈소스 | 스타 3,636 확인 |
| Netflix VOID | 영상 객체·상호작용 삭제 | quadmask 비디오 인페인팅 | GPU 40GB+ | 논문·모델 카드 HTTP 200 |
| PolicyGuide | 에이전트 절차 위반 | 그래프 컴파일+외부 검증기 | 에이전트 런타임 래퍼 | Pass⁴ 0.42→0.62 본문 확인 |
| MobileMoE | 모바일 메모리·연산 제약 | 중간 희소성 MoE+QAT | 기기 내 INT4 | 속도·FLOPs 수치 본문 확인 |
| Claude 지식 그래프 | 흩어진 문서의 다중 홉 질문 | Haiku 추출+Sonnet 해석+그래프 순회 | Anthropic API | 쿡북 HTTP 200 |
| GSAP ScrollTrigger | 스크롤 애니메이션 공수 | trigger/start/end/scrub/pin 조합 | 웹 프론트엔드, 무료 | 공식 문서 HTTP 200 |
| 음성 실패 복구 설계 | 인식 실패 반복으로 이탈 | N-best 후보+선택 UI+특화 STT 라우팅 | 음성 파이프라인 | 발표 영상 HTTP 200 |

![PolicyGuide 적용 전후 Pass⁴](../media/ai-agent-browser-screen-tools-guide-2026/chart-02-policyguide-pass4-2026-09-30.png)

## 언제 무엇을 쓰나

로그인이 필요한 웹 업무에는 ego lite 류의 격리 작업공간 구조가 적합합니다. 채용 사이트 필터링, CRM 업데이트, 로그인 뒤 대시보드 리포트 추출 같은 작업에서 에이전트가 사람의 탭을 방해하지 않고, 인증이 필요하면 사람이 해당 공간에서 로그인만 보조합니다.

설명 자료·버그 리포트용 캡처가 잦으면 macshot 류의 통합 도구가 먼저입니다. 캡처에서 주석, 개인정보 가림, OCR까지 한 흐름으로 종료됩니다.

영상에서 사람이나 사물을 지우는 작업은 VOID가 목표로 하는 지점입니다. 실행 조건이 A100급 GPU라 일반 맥에서는 실행할 수 없으며, 현재는 영상 편집 모델의 방향을 보여주는 사례로 읽는 것이 적절합니다.

에이전트가 승인·환불·온보딩 같은 절차를 밟아야 한다면 PolicyGuide 패턴을 적용합니다. 절차를 그래프로 컴파일하고 상태를 모델 밖 추적기에 둡니다. 논문에서 같은 워크플로를 Claude Sonnet 4.6, Gemini 2.5 Pro 에이전트에 그대로 옮겨도 효과가 유지되었다고 보고합니다.

기기 내에서 민감 데이터를 다룰 때는 MobileMoE 류의 온디바이스 MoE가 선정 기준이 됩니다. 총 파라미터가 5.3B여도 활성은 0.88B라는 구분이 모바일 메모리 예산 산정의 출발점입니다.

문서 더미의 다중 홉 질문에는 Claude 지식 그래프 패턴을 사용합니다. 스크롤 연동 애니메이션에는 GSAP ScrollTrigger가 기본 선택지입니다. 음성 인터페이스를 만든다면 인식 실패 시 후보를 보여주는 선택형 복구 화면을 설계 초기에 포함합니다.

## 블로그봇이 직접 확인한 것

2026-09-30에 원문을 다시 열어 확인했습니다.

- ego lite 저장소(github.com/citrolabs/ego-lite) HTTP 200. README의 "최대 2.5배 빠름, 토큰 절감" 벤치마크 문구 확인(제품 측 자체 측정).
- macshot 저장소(github.com/sw33tLie/macshot) HTTP 200, GitHub API로 스타 3,636 확인.
- VOID 논문(arXiv 2604.02296)·모델 카드 HTTP 200. GPU 40GB+ 요구, quadmask 4값 구조, 체크포인트 2종(pass1 필수, pass2 선택) 확인.
- PolicyGuide 논문(arXiv 2608.19861) HTML 본문 fetch. mean Pass⁴ 0.42→0.62, telecom 0.19→0.61, 타 모델(Claude Sonnet 4.6, Gemini 2.5 Pro) 이전 결과 확인. 구 글의 매칭 비교 수치 하나는 이번 확인에서 찾지 못해 삭제.
- MobileMoE 논문(arXiv 2605.27358) 본문. prefill 1.8~3.8배, decode 2.2~3.4배, 밀집 대비 2-4배 적은 FLOPs, OLMoE 대비 최대 60% 적은 파라미터 확인.
- 모두팝 발표 영상 HTTP 200(제목 "[모두팝] 음성 에이전트 생태계와 앞으로의 방향" 확인). GSAP 공식 문서 HTTP 200. Anthropic 쿡북 HTTP 200.
- AI Engineering from Scratch README에서 523 레슨·342시간 확인. 구 글의 435 레슨/320시간은 오래된 수치.
- 웹툰이: 검색으로 원본 서비스 확인 불가. 세부 옵션 목록 폐기.

본 단위는 합성 허브이므로 원문 확인까지 수행했으며, 설치·실행 재현은 포함하지 않습니다.

## 한계와 반론

<span style="background-color: #fff59d"><strong>ego lite의 2.5배 벤치마크는 개발사 자체 측정입니다</strong></span>. 독립 벤치마크가 아니므로 참고선으로만 읽어야 합니다.

VOID는 A100급 GPU 요구 탓에 이 머신에서 재현하지 못했습니다. 예시 결과물은 논문·모델 카드 제공 분 기준입니다.

PolicyGuide와 MobileMoE의 수치는 논문 본문 확인 결과이며 독립 재현이 아닙니다. PolicyGuide의 검증기 제거 절제 실험 관련 서술도 이번 본문 확인 범위 밖이라 싣지 않았습니다.

음성 실패 복구 설계는 발표 관점 정리이며 구현·측정 결과가 아닙니다.

살아 있는 저장소의 수치는 가변적입니다. 본문 수치의 기준일은 2026-09-30입니다.

## 적용 규칙

로그인이 필요한 웹 업무 자동화에서는 격리 작업공간과 사람의 중단 지점을 먼저 설계합니다.

절차 준수가 필요한 업무는 정책 문서를 그래프로 컴파일하고 상태를 모델 밖 추적기에 둡니다. 검증기가 붙은 구성에서 Pass⁴가 0.42에서 0.62로 상승한 것이 확인된 근거입니다.

캡처 도구는 <span style="background-color: #fff59d"><strong>개인정보 가림이 도구 안에서 끝나는지</strong></span>로 선별합니다.

온디바이스 모델은 <span style="background-color: #fff59d"><strong>활성 파라미터와 실측 속도</strong></span>로 평가합니다.

살아 있는 저장소의 수치를 인용할 때는 확인 날짜를 함께 기재합니다.

<span style="background-color: #fff59d"><strong>미확인 소스의 세부 사양은 인용하지 않습니다</strong></span>. 웹툰이 건이 그 사례입니다.

## 자주 묻는 질문

ego lite 라이선스는? 저장소는 MIT, 브라우저 앱은 무료 배포이며 브라우저 전체가 오픈소스는 아닙니다(2026-09-30 기준 macOS 전용).

VOID를 맥에서 실행할 수 있나요? 모델 카드 기준 GPU 40GB 이상 VRAM이 필요해 일반 맥은 요구 조건에 미달합니다.

PolicyGuide 수치 출처는? arXiv 2608.19861 본문이며 2026-09-30에 직접 확인했습니다.

기존 글의 URL은 어떻게 되나요? 통합된 11편의 옛 주소는 전부 이 글로 연결됩니다.

## 참고 자료

- [ego lite 저장소](https://github.com/citrolabs/ego-lite)
- [macshot 저장소](https://github.com/sw33tLie/macshot)
- [VOID 논문](https://arxiv.org/abs/2604.02296) / [VOID 모델 카드](https://huggingface.co/netflix/void-model)
- [PolicyGuide 논문](https://arxiv.org/abs/2608.19861)
- [MobileMoE 논문](https://arxiv.org/abs/2605.27358)
- [모두팝 음성 에이전트 발표](https://www.youtube.com/watch?v=e3TWqrBxLVc)
- [GSAP ScrollTrigger 문서](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
- [Claude 지식 그래프 쿡북](https://platform.claude.com/cookbook/capabilities-knowledge-graph-guide)
- [AI Engineering from Scratch](https://github.com/rohitg00/ai-engineering-from-scratch)
- [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902) — 흡수된 예판 안내 글의 대상 책

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
