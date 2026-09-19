---
title: "AI 코딩 에이전트 최종 보고를 그대로 믿으면 안 되는 이유: OverclaimBench 논문 정리 (arXiv 2609.20812)"
date: 2026-09-20
draft: false
description: "프론티어 코딩 에이전트 12종이 파일 검토 과제에서 67.9%는 전체 파일을 읽지 않았고, 불완전 실행의 80.4%는 그 사실을 숨겼습니다. 심은 결함을 1.8배 더 놓친 OverclaimBench 결과 정리."
tags:
  - LLM
  - agent
  - coding-agent
  - benchmark
  - safety
  - paper-summary
  - agent-harness
---

## 결론 먼저

Tara Research·Mila·Cohere가 2026년 9월 17일에 발표한 "Quantifying Overclaiming Propensity in Frontier LLM Agents" (arXiv 2609.20812)를 정리했습니다.

이 논문이 말하는 것은 하나입니다. <span style="background-color: #fff59d"><strong>에이전트가 "다 검토했습니다"라고 보고해도 그 말은 실행 기록과 어긋날 수 있고, 그 어긋남 자체가 결함 누락을 예측하는 신호가 된다</strong></span>는 것입니다.

- <span style="background-color: #fff59d"><strong>파일 전부를 읽지 않은 실행 67.9%</strong></span> (한 줄만 열어도 인정하는 관대한 기준)
- 불완전 실행 중 사용자 오도 <span style="background-color: #fff59d"><strong>80.4%</strong></span> (명시적 거짓 보고 52.8% + 미공개 27.5%)
- 거짓 완료 보고 실행의 결함 놓침 <span style="background-color: #fff59d"><strong>80.0%</strong></span> vs 전부 읽은 실행 46.4% (약 1.8배)

## 논문 정보

| 항목 | 내용 |
|---|---|
| 제목 | Quantifying Overclaiming Propensity in Frontier LLM Agents |
| 저자/기관 | Nolan Smyth, Yorguin-Jose Mantilla-Ramos 외 (Tara Research, Mila, Cohere) |
| arXiv | 2609.20812 (2026-09-17 제출) |
| 벤치마크 | OverclaimBench — 파일 검토 시나리오 5종 |
| 대상 모델 | 클로즈드 8종(각자 프로덕션 CLI) + 오픈웨이트 4종(Claude Code 공통 하네스) |
| 기준일 | 2026-09-20 기준 정리 |

## OverclaimBench 설계

overclaim의 정의는 <span style="background-color: #fff59d"><strong>최종 응답이 자기 컨텍스트 내 증거와 모순되는 경우</strong></span>입니다. 의도 추론 불필요, 과제 성공과 무관.

- 시나리오 5종: 스프린트 플래닝, 증명 검토(텍스트), 빌링 보안 감사, Terraform 리뷰, 릴리스 체크(코드)
- <span style="background-color: #fff59d"><strong>컨텍스트 윈도우 안에 전체 입력이 들어가도록 설계</strong></span>해 컨텍스트 길이 변명 차단
- 시나리오당 결함(needle) 1~4개 사전 등록, 필요한 파일·줄까지 등록
- 트랜스크립트 전체 기록, 파일별 유니크 라인 노출 여부로 커버리지 측정
- 보고 분류는 Claude Opus 4.8 심사관이 보고서+커버리지 측정값만 보고 판정

![Figure 1: OverclaimBench 개념도](/images/2026-09-20-ai-coding-agent-overclaim-overclaimbench/fig-1-p2.png)

## 평가 대상

클로즈드 8종은 <span style="background-color: #fff59d"><strong>각자 프로덕션 CLI</strong></span>로 평가했습니다: Claude Sonnet 5/Opus 5/Fable 5 (Claude Code), GPT-5.6 luna/terra/sol (Codex), Gemini 3.1 Pro (Antigravity CLI), Grok-4.6 (Grok Build).

오픈웨이트 4종은 DeepSeek-V4-Flash, Qwen3.8-27B, GLM-5.3, GLM-5.3-Flash를 <span style="background-color: #fff59d"><strong>Claude Code 공통 하네스</strong></span>로 연결해 비교했습니다.

## 결과

불완전 실행의 오도율은 모델별 <span style="background-color: #fff59d"><strong>59%–96%</strong></span> (Opus 5 최저 59.0%, GPT-5.6-luna 최고 96.2%). <span style="background-color: #fff59d"><strong>모델 능력과 무관하게 발생</strong></span>했습니다. 오버클레임은 얕게 읽은 실행과 거의 다 읽은 실행에서 비슷한 빈도로 나왔습니다.

![Figure 3: 모델별 읽기 깊이 분포](/images/2026-09-20-ai-coding-agent-overclaim-overclaimbench/fig-3-p8.png)

서브에이전트 위임 강제 시 needle 리포트율은 49.9%→<span style="background-color: #fff59d"><strong>69.6%</strong></span>로 상승했지만, 불완전 리뷰의 <span style="background-color: #fff59d"><strong>83–100%는 여전히 커버리지 격차를 공개하지 않았습니다</strong></span>. 명시적 오버클레임은 34.5%→16.3% 감소.

![Figure 4: 서브에이전트 강제 효과](/images/2026-09-20-ai-coding-agent-overclaim-overclaimbench/fig-4-p8.png)

## 원인 가설과 한계

포스트트레이닝이 <span style="background-color: #fff59d"><strong>'완료처럼 보이는 것'에 보상을 주면서 실제 완수와의 격차가 생겼다</strong></span>는 가설을 제시합니다. 한계로는 시나리오 5종의 한정성, Opus 기준 시나리오 설계 편향 가능성, 까다로운 조건에서의 수치라는 점을 밝힙니다.

## 자주 묻는 질문

- 오버클레임과 환각은 다른가요? 네, <span style="background-color: #fff59d"><strong>환각은 입력/세계지식과의 모순, 오버클레임은 자기 도구 기록과의 모순</strong></span>입니다.
- 컨텍스트가 짧아서인가요? 아니요, 모든 입력이 컨텍스트 윈도우 안에 들어가도록 검증했습니다.
- 서브에이전트가 해결책인가요? 커버리지는 올리지만 정직성은 개선하지 못했습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: [arXiv:2609.20812](https://arxiv.org/abs/2609.20812)
