---
title: "같은 모델인데 코딩 에이전트 결과가 다른 이유: 하네스 설계 1차 자료 10편 통합 정리"
date: 2026-09-28
author: 한준구(코난쌤)
description: "코딩 에이전트 하네스 글 10편을 1차 출처와 대조해 하나로 묶었습니다. Anthropic 비용 실험(9달러 vs 200달러), Raschka 6가지 구성 요소, OpenAI 인간 코드 0% 실험 등 이번에 직접 확인한 것만 정리했습니다."
tags:
  - 코딩 에이전트
  - 하네스
  - LLM 에이전트
  - Claude Code
refactor_hub_id: harness-self-improve-14
aliases:
  - components-of-a-coding-agent-sebastian-raschka
  - geeknews-2026-04-06-coding-agent-components
  - geeknews-2026-04-09-prompt-to-harness-four-years
  - ai-engineer-europe-2026-day1-recap
  - harness-engineering-openai-ryan-lopopolo-2026-04-23
  - code-as-agent-harness-2026-05-20
  - claude-code-dynamic-workflows-harness-2026-06-03
  - anthropic-agent-loop-app-builder-2026-06-22
  - posts/2026-07-27-boris-cherny-claude-code
  - posts/2026-07-28-training-agents-hf-sft
draft: false
sources_read: "arXiv:2605.18747는 초록 페이지와 HTML 본문(저자 목록·서베이 3레이어 구조)을 가져와 대조했습니다. 코드 확인: github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers 접속 HTTP 200. 나머지 9편은 웹 원문(Raschka 매거진, OpenAI·Anthropic 엔지니어링 글, Claude 블로그, 김영민 블로그, Latent Space)과 유튜브 원본 3종 제목·공개 메타데이터를 확인했습니다. 옛 글 인용구 중 원문 미확인 항목(일 1,000달러, 750 패키지, Garbage Collection Day 등)은 이 글에서 제외했습니다."
novelty_vs_paper: "하네스 인터페이스 3레이어와 '코드가 곧 하네스' 프레임은 arXiv:2605.18747 서베이의 기여입니다. 10개 1차 자료를 구성 요소·검증 루프·운영·훈련 4축에 배치한 설계 지도, Anthropic 비용 수치 원문 대조, 도표 2장과 적용 규칙은 블로그봇의 분석입니다."
---

## 한눈에 보는 결론

지난 몇 달 이 블로그에 하네스 얘기가 열 편이나 쌓였더라고요. 이번에 전부 꺼내서 1차 출처와 다시 대조해 보고, 한 페이지로 합쳤습니다. 결론부터 말씀드리면, <span style="background-color: #fff59d"><strong>같은 모델인데 결과가 다르다면</strong></span> 모델 탓보다 하네스 탓일 확률이 높습니다.

하네스가 뭐냐면, 모델을 감싸는 실행 환경이에요. 컨텍스트 수집, 도구·권한 설계, 검증 루프, 운영 규칙이 전부 이 층에서 정해집니다. 열 편이 전부 다른 이야기를 하는 것 같아도 결국 이 네 칸으로 들어옵니다.

| 질문 | 짧은 답 |
|---|---|
| 병목은 어디 | 하네스(컨텍스트·도구·검증·운영)에서 자주 |
| 결정적 증거 | Anthropic: 단일 20분·9달러 vs 풀 하네스 6시간·200달러, 품질은 풀 하네스 승 |
| 구성 | Raschka 기준 6가지 구성 요소 |
| 검증 | 만든 에이전트 말고 별도 평가자 |
| 기준일 | 2026-09-28, 11개 출처 직접 대조 |

![Anthropic 단일 에이전트와 풀 하네스의 비용·시간 비교](../media/coding-agent-harness-design-guide-2026/chart-01-solo-vs-harness.png)

인상적인 건 Anthropic 실험 수치예요. 검증 루프 없이 20분에 9달러로 끝내는 에이전트와, <span style="background-color: #fff59d"><strong>6시간 200달러를 쓰고 끝까지 가는 에이전트</strong></span>. <span style="background-color: #fff59d"><strong>20배 넘게 비싼데 품질 차이가 바로 보였다</strong></span>고 원문에 적혀 있습니다. 어디까지 믿고 언제 돈을 쓸지가 <span style="background-color: #fff59d"><strong>설계의 핵심</strong></span>이 되는 거죠.

비용이 20배인데 품질까지 좋다면 이야기가 간단한데, 현실은 조건이 따라옵니다. 원문도 이 점을 숨기지 않아요. 하네스는 돈을 들여 완성도를 사는 구조예요. 그래서 이 글 뒤쪽에서는 언제 이 비용을 쓸지 조건으로 정리했습니다.

## 무엇을 비교했나

이번에 합친 열 편과 확인한 출처입니다. 열 편을 하나로 묶은 이유는 단순해요. 전부 '왜 내 에이전트는 기대보다 못한가'라는 질문에 답한 글인데, 다루는 층이 달라서 합치면 설계 가이드 한 편이 나온다고 판단했습니다.

1. Sebastian Raschka, Components of A Coding Agent — [원문](https://magazine.sebastianraschka.com/p/components-of-a-coding-agent)
2. 김영민, 프롬프트에서 하네스까지 — [원문](https://bits-bytes-nn.github.io/insights/agentic-ai/2026/04/05/evolution-of-ai-agentic-patterns.html)
3. OpenAI, Harness Engineering — [엔지니어링 글](https://openai.com/index/harness-engineering/)
4. Ryan Lopopolo 하네스 운영 — [Latent Space](https://www.latent.space/p/harness-eng), [키노트 영상](https://www.youtube.com/watch?v=am_oeAoUhew)
5. Code as Agent Harness 서베이 arXiv:2605.18747 — [초록](https://arxiv.org/abs/2605.18747), [저장소](https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers)
6. Anthropic, Harness design for long-running apps — [원문](https://www.anthropic.com/engineering/harness-design-long-running-apps)
7. Claude Code 동적 워크플로 — [블로그](https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code)
8. Boris Cherny 인터뷰 — [YC](https://www.ycombinator.com/library/UN-boris-cherny-building-claude-code), [80% 삭제 발표](https://www.youtube.com/watch?v=qyPCVqFUyDo)
9. Hugging Face, Training Agents — [영상](https://www.youtube.com/live/rNgUoH7Wbv8)
10. AI Engineer Europe 2026 — [영상](https://www.youtube.com/live/O_IMsEg91g8)

## 방법 비교

| 자료 | 핵심 주장 | 확인 수준 |
|---|---|---|
| Raschka | 하네스 6요소(리포 컨텍스트·프롬프트 캐시·도구 검증·컨텍스트 압축·메모리 분리·위임) | 원문 나열 대조 |
| 김영민 | 프롬프트→컨텍스트→하네스 3기 전환 | TL;DR 대조 |
| OpenAI | 5개월간 수동 코드 0줄 내부 베타, 스킬·DevTools 검증 | 원문 확인 |
| Lopopolo | 100만 줄·일 10억 토큰·인간 코드 0% | 글 제목 기준 |
| arXiv 서베이 | 코드가 곧 하네스, 3레이어 | 초록·본문 구조 확인 |
| Anthropic | Planner-Generator-Evaluator 분리 | 비용 표 대조 |
| Claude Code | 작업마다 하네스를 즉석 작성 | 릴리스 문 확인 |
| Cherny | 시스템 프롬프트 80% 삭제 | 발표 제목 확인 |
| HF | 트레이스 SFT·스킬 | 영상 확인 |
| AIE Europe | 병목은 하네스·운영 | 영상 확인 |

![10개 자료를 하네스 4층에 배치한 설계 지도](../media/coding-agent-harness-design-guide-2026/chart-02-design-map.png)

네 칸으로 정리하면 <span style="background-color: #fff59d"><strong>① 구성 요소 ② 검증 루프 ③ 운영 ④ 훈련·개선</strong></span>이에요. 이 지도는 블로그봇이 그린 거고, 각 자료가 어디에 답하는지 한눈에 보입니다.

각 칸을 조금 풀어볼게요. 구성 요소는 하네스의 재료 얘기입니다. Raschka가 원문에서 나열한 여섯 개는 리포 컨텍스트, 프롬프트 접두사 캐시, 구조화된 도구와 권한, 컨텍스트 압축, 트랜스크립트와 작업 메모리 분리, 경계가 있는 위임이에요. arXiv 서베이는 이런 부품들을 코드를 중심으로 다시 묶습니다.

검증 루프는 끝까지 가게 만드는 장치구요. Anthropic 구조에서 Planner는 스펙을 정리하고, Generator가 구현하고, Evaluator가 실제 실행으로 검증합니다. Claude Code 동적 워크플로는 이 역할 분리를 작업마다 즉석에서 만드는 쪽이에요.

운영은 팀 단위 이야기입니다. OpenAI 실험 글은 5개월간 에이전트가 전부 작성한 내부 베타를 배포했다고 적고요. 맥락은 스킬과 저장소 내장 도구로 줬다고 합니다. 리뷰 부담도 1분 미만 리뷰 후 자동 머지로 낮췄구요.

훈련·개선은 다음 모델을 키우는 쪽이에요. HF 튜토리얼이 에이전트 트레이스로 SFT하고 스킬을 갱신하는 루프를 다루고, 김영민 글은 프롬프트에서 하네스로 관심이 이동한 과정을 정리합니다.

## 언제 무엇을 쓰나

- 모델을 바꾸고 싶을 때: 6요소 점검 먼저. 빠진 게 있으면 새 모델도 같은 자리에서 막힙니다.
- 중간에 멈추는 에이전트: <span style="background-color: #fff59d"><strong>만드는 역할과 평가하는 역할 분리</strong></span>. <span style="background-color: #fff59d"><strong>평가자는 브라우저·테스트를 실제로 돌립니다</strong></span>.
- continue를 자꾸 누를 때: <span style="background-color: #fff59d"><strong>완료 조건을 문서로</strong></span>. 이 인용구는 원문 확인이 안 돼서 뺐지만 방향은 OpenAI 문서와 같습니다.
- 새 모델이 나왔을 때: <span style="background-color: #fff59d"><strong>프롬프트 삭제 실험</strong></span>. Cherny 발표 제목 자체가 <span style="background-color: #fff59d"><strong>80% 삭제</strong></span>예요.
- 같은 실수가 반복될 때: 린트 메시지·스킬 문서로 고정.
- 공개 입력을 읽을 때: <span style="background-color: #fff59d"><strong>권한 최소화</strong></span>. 입력 읽기+데이터 접근+외부 통신이 겹치면 공격면이 됩니다.
- 비용을 줄이고 싶을 때: <span style="background-color: #fff59d"><strong>트레이스 수집부터</strong></span>. SFT 마스킹(-100)은 <span style="background-color: #fff59d"><strong>어시스턴트 토큰만 학습하는 표준</strong></span>입니다.

## 블로그봇이 직접 확인한 것

- <span style="background-color: #fff59d"><strong>11개 URL 전부 HTTP 200 확인</strong></span>(유튜브 3종 포함, Lopopolo 키노트 제목에 이름 명기).
- Anthropic 원문 비용 표 대조: 20분·9달러 / 6시간·200달러 / 20배 이상. 레트로 게임 메이커 예시와 Planner·Evaluator 페르소나 문단도 원문에서 확인.
- OpenAI 실험 글에서 스킬·gh·저장소 내장 도구 언급과 1분 미만 리뷰 후 자동 머지 서술을 확인.
- Raschka 6요소 나열 원문 대조, 김영민 3기 전환 TL;DR 대조.
- arXiv 저자(UIUC·Meta·Stanford)·서베이 3레이어 확인, 저장소 접속 확인.
- 옛 글 인용구 중 <span style="background-color: #fff59d"><strong>원문 미확인</strong></span>(일 1,000달러, 750 패키지, Garbage Collection Day 등)은 제외.
- 도표 2장 matplotlib 직접 생성.

## 한계와 반론

- 유튜브 인용은 제목·공개 자료 대조 수준이라 화면 속 수치는 다루지 않았습니다.
- Lopopolo 수치는 Latent Space 글 제목 기준이고 <span style="background-color: #fff59d"><strong>OpenAI 공식 문서엔 없습니다</strong></span>.
- Anthropic 비교는 단일 데모 기준이라 일반화에 한계가 있습니다.
- 하네스 개선 효과의 정량 측정은 이번 범위 밖입니다.
- 4축 분류는 블로그봇 해석이라 다른 축도 가능합니다.

## 적용 규칙

1. 모델 교체 전에 6요소부터 점검합니다.
2. <span style="background-color: #fff59d"><strong>자기 검증 금지</strong></span>. 평가자 분리, 실행 기반 검증.
3. continue 반복 구간이 하네스 수정 지점입니다. 완료 조건을 문서화합니다.
4. 새 모델마다 삭제 실험으로 프롬프트를 재점검합니다.
5. 반복 실수는 린트·스킬로 고정합니다.
6. 신뢰할 수 없는 입력을 읽는 에이전트는 권한·네트워크를 최소화합니다.

## 참고 자료

- Raschka: https://magazine.sebastianraschka.com/p/components-of-a-coding-agent
- 김영민: https://bits-bytes-nn.github.io/insights/agentic-ai/2026/04/05/evolution-of-ai-agentic-patterns.html
- OpenAI: https://openai.com/index/harness-engineering/
- Latent Space: https://www.latent.space/p/harness-eng
- arXiv:2605.18747: https://arxiv.org/abs/2605.18747
- 저장소: https://github.com/YennNing/Awesome-Code-as-Agent-Harness-Papers
- Anthropic: https://www.anthropic.com/engineering/harness-design-long-running-apps
- Claude 블로그: https://claude.com/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code
- YC: https://www.ycombinator.com/library/UN-boris-cherny-building-claude-code
- HF: https://www.youtube.com/live/rNgUoH7Wbv8
- AIE Europe: https://www.youtube.com/live/O_IMsEg91g8

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
