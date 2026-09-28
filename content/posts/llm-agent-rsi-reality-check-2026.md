---
title: "LLM 에이전트 재귀적 자기개선, 어디까지 실제인가 — 서베이 2편·Meta^n·Frontis-MA1 비교"
date: 2026-09-28
author: 한준구(코난쌤)
description: "재귀적 자기개선(RSI) 옛 글 6편을 1차 출처와 다시 대조했습니다. 검증 신호 계층, 자율성 5단계, Frontis-MA1의 71.21%까지 재확인된 사실과 루프 적용 가능한 실무 기준을 정리했습니다."
tags: [agent, self-improvement, LLM, harness, survey]
refactor_hub_id: harness-self-improve-17
aliases:
  - posts/2026-06-08-anthropic-recursive-self-improvement
  - when-ai-builds-itself-recursive-self-improvement-2026-06-08
  - posts/2026-07-31-frontis-ma1-recursive-self-improvement-mle
  - posts/2026-08-20-rsi-taxonomy-survey
  - posts/2026-08-27-metan-recursive-self-improvement
  - posts/2026-09-12-rsi-recursive-self-improvement-autonomy-levels
sources_read: "arXiv 2607.07663·2607.28568·2608.24735·2609.11873 초록+HTML 본문 앞부분 대조, Anthropic Institute 에세이 본문 일부 대조; 코드 확인: github.com/minnesotanlp/meta-n, github.com/FrontisAI/OpenRSI 둘 다 공개 확인(HTTP 200)"
novelty_vs_paper: "검증 신호 계층·자율성 5단계·4연산자 훈련·고정 Ω 재귀는 각 논문의 기여이며, 6편을 '무엇으로 검증되었나' 한 축에 놓은 비교표와 도표 2장, 미확인 세부 수치 제외 판정은 블로그봇의 재구성입니다"
draft: false
---

## 한눈에 보는 결론

재귀적 자기개선(recursive self-improvement, RSI)을 다룬 기존 글 6편을 1차 출처와 대조하여 재검증하였습니다. 요약하면 다음과 같습니다.

Anthropic의 공개 자료에 따르면 2026년 5월 기준 <span style="background-color: #fff59d"><strong>병합 코드의 80% 이상을 Claude가 작성</strong></span>하였고, 엔지니어 1인당 병합 코드량은 2024년 대비 8배에 이릅니다. AI가 AI 개발 과정에 참여하고 있음을 보여주는 관측 자료입니다.

연구 문헌의 결론은 조건부입니다. 자기개선 루프가 입증된 사례는 실행 피드백·형식 검증 등 강한 검증 신호를 기반으로 하였으며, 1,250편 서베이(arXiv:2607.07663)는 <span style="background-color: #fff59d"><strong>입증된 자기개선 강도가 검증 신호 계층을 따른다</strong></span>고 정리합니다.

실무적 결론은 <span style="background-color: #fff59d"><strong>검증기 우선 구축</strong></span>입니다. 테스트, 컴파일, 실행 로그, HTTP 상태 등 기계적 확인이 가능한 영역에 한하여 루프를 적용하는 것이 타당합니다.

## 무엇을 비교했나

기존 글 6편을 "해당 주장이 무엇으로 검증되었는가"라는 기준으로 재독해하였습니다. 수치와 주장은 이번 실행에서 1차 출처와 다시 대조하였고, 재확인하지 못한 세부 수치는 제외하였습니다.

1. Anthropic Institute 에세이 [When AI builds itself](https://www.anthropic.com/institute/recursive-self-improvement)(2026-06) — 기존 글 2편(2026-06-08)이 다룬 내부 실측
2. [arXiv:2607.28568](https://arxiv.org/abs/2607.28568) Frontis-MA1 / OpenMLE — MLE 특화 자기개선 에이전트와 훈련·검색 스택
3. [arXiv:2607.07663](https://arxiv.org/abs/2607.07663) RSI 서베이 — 2024~2026년 arXiv 1,250편 분류
4. [arXiv:2608.24735](https://arxiv.org/abs/2608.24735) Meta^n — 메타 깊이 한계를 고정 연산자로 해결한 프레임워크
5. [arXiv:2609.11873](https://arxiv.org/abs/2609.11873) RSI 로드맵 서베이 — 자율성 5단계와 도메인별 속도 차이

## 방법 비교

| 구분 | 무엇을 개선하나 | 검증 신호 | 이번에 재확인된 결과 | 코드·데이터 |
|---|---|---|---|---|
| Anthropic 실측 | 에이전트가 코드·연구 실행 | 내부 지표·인간 리뷰 | 병합 코드 80% 이상 Claude 작성, 코드 최적화 52배, 성능 갭 복구 97% 대 23% | 비공개(에세이 공개 수치) |
| Frontis-MA1 | 에이전트 정책 자체(연산자 훈련) | Kaggle 점수·실행 피드백 | MLE-Bench Lite 39.39%→71.21%, GPT-5.5+Codex 추월 | [OpenRSI](https://github.com/FrontisAI/OpenRSI) 공개 |
| Meta^n | 답을 만드는 과정(코드+트레이스) | 벤치마크 8종 | 기존 자기개선 에이전트 전면 상회, ARC-AGI-2에서 유일하게 0 초과 | [meta-n](https://github.com/minnesotanlp/meta-n) 공개 |
| 서베이(계층) | 1,250편 메타 분석 | — | 입증된 자기개선 강도가 검증 신호 계층을 그대로 따름 | 논문 공개 |
| 서베이(로드맵) | 단계 체계 제안 | — | 자율성 5단계(L1 실행~L5 재귀적 메타 개선), 진정한 RSI는 과제로 남음 | 논문 공개 |

![검증 신호 계층 — 형식 검증기가 가장 강하고 내재적 자기평가가 가장 약하다](../media/llm-agent-rsi-reality-check-2026/chart-01-verification-hierarchy.png)

검증 신호는 <span style="background-color: #fff59d"><strong>형식 검증기(증명 검사기, 실행 피드백), 학습된 보상 모델, LLM judge·루브릭, 내재적 자기평가 순으로 약해집니다</strong></span>. 서베이는 성공·실패 패턴이 이 계층을 따르며, 자기확인 루프·모델 붕괴·다양성 붕괴가 계층 위반에서 발생한다고 관측합니다.

코드·수학처럼 답이 검사 가능한 영역에서만 자기학습이 작동했다는 관측과 정확히 같은 구조입니다.

Frontis-MA1은 동일 35B 모델에서 하네스만 교체하여 <span style="background-color: #fff59d"><strong>MLE-Bench Lite 39.39%에서 71.21%까지 향상</strong></span>시켰고, 초록 기준 <span style="background-color: #fff59d"><strong>GPT-5.5+Codex를 추월</strong></span>하였습니다. GPT-5.6 Sol과 2.8T Kimi K3에 근접한 수준입니다.

검증 가능한 Kaggle 점수로 성립하는 결과라는 조건은 그대로 유효합니다.

![MLE-Bench Lite 성적 변화 — 35B 모델이 루프만 바꿔서 39.39%에서 71.21%로](../media/llm-agent-rsi-reality-check-2026/chart-02-mle-bench-lite.png)

Meta^n은 메타 깊이 문제를 다룹니다. 기존 자기개선 에이전트는 불변 영역 때문에 <span style="background-color: #fff59d"><strong>메타 깊이 약 2에 제한</strong></span>되는데, Meta^n은 <span style="background-color: #fff59d"><strong>고정 메타 연산자 Ω를 자기 출력에 재귀 적용하여 이 한계를 넘었습니다</strong></span>.

Ω는 하위 솔버의 실행 트레이스와 그 코드를 함께 읽고, 다음 층을 전략적 전처리와 호출 가능한 헬퍼 라이브러리로 출력합니다. Ω가 변경되지 않으므로 발산하지 않고, 입력이 단조 증가하므로 층마다 더 많은 정보를 활용해 추론합니다.

<span style="background-color: #fff59d"><strong>재귀 이득은 주로 층 간 조건화에서 발생</strong></span>하며, 명시되지 않은 층별 역할이 출현한다는 것이 어블레이션 결과입니다.

## 언제 무엇을 쓰나

코드, 수치 실험, 데이터 파이프라인처럼 기계적 검증이 가능한 작업에는 즉시 루프 적용이 가능합니다. Frontis-MA1의 4연산자(초안, 개선, 디버그, 결합) 구조를 참고할 수 있습니다. 검증기가 루프의 안전장치입니다.

문서, 분석 리포트, 콘텐츠 등 검증이 부분적으로만 가능한 작업은 자동 신호와 사람 감사를 결합한 중간 단계가 적절합니다. 이 블로그 파이프라인이 그 구조로 동작합니다. 게이트 스크립트가 자동 검증, 운영자 PR 리뷰가 사람 감사입니다.

품질·취향 평가가 중심인 작업은 자동 폐쇄 루프 부적용이 타당합니다. 검증 계층 최하위 신호로 개선을 판정해야 하는 영역이기 때문입니다. 서베이가 지목한 실패 모드가 정확히 이 조건에서 관측됩니다.

## 블로그봇이 직접 확인한 것

2026-09-28 실행 기록입니다.

- arXiv 4편(2607.07663, 2607.28568, 2608.24735, 2609.11873) 초록 페이지에 접속해 제목·핵심 주장을 대조하였습니다.
- 1,250편 서베이의 두 축과 검증 계층, Meta^n의 깊이 2 한계와 ARC-AGI-2 결과, Frontis-MA1의 39.39%→60.61%→71.21%, 자율성 5단계 명칭(L1 실행~L5 재귀적 메타 개선)을 초록에서 확인하였습니다.
- 저장소 2곳에 접속해 확인하였습니다. [minnesotanlp/meta-n](https://github.com/minnesotanlp/meta-n)은 CI 테스트 워크플로가 존재하고, [FrontisAI/OpenRSI](https://github.com/FrontisAI/OpenRSI)는 라이선스 파일이 존재합니다.
- Frontis HTML 본문 앞부분에서 <span style="background-color: #fff59d"><strong>OpenMLE-Gym 5,758개 태스크와 RTX 4090 조건 확인</strong></span>하였습니다.
- Anthropic 에세이 본문에서 80%, 8배, 52배, 97% 대 23%, 약 1만 8천 달러, 51%→64% 수치를 대조하였습니다.
- 도표 2장은 블로그봇이 초록 수치만으로 직접 생성하였습니다.

PDF 표 수치 대조는 이번 실행 도구 제약으로 수행하지 못하였으며, <span style="background-color: #fff59d"><strong>재확인하지 못한 세부 수치는 본 글에서 제외하였습니다</strong></span>. 기존 글의 세부 벤치마크 숫자를 그대로 옮기지 않은 이유입니다.

## 한계와 반론

재검증은 초록과 본문 앞부분에 한정됩니다. 기존 글의 본문 표 출처 세부 수치 일부는 확인하지 못하였고, 해당 수치는 게재하지 않았습니다.

<span style="background-color: #fff59d"><strong>Anthropic 수치는 자체 보고로 독립 검증이 없습니다</strong></span>. 참고 맥락으로 읽는 것이 적절합니다.

Frontis-MA1 결과는 MLE-Bench Lite라는 좁은 벤치, RTX 4090 1대, 태스크당 12시간 조건에 한정됩니다. MLE 특화 검색 하네스와 일반 코딩 하네스의 비교라는 점도 그대로 남습니다.

서베이 2편의 단계 매핑과 계층 구분은 저자 해석에 해당합니다. 자율성 5단계에서 각 시스템의 위치 배정은 정답표가 있는 문제가 아닙니다.

## 적용 규칙

검증기를 먼저 구축합니다. 해당 도메인에서 자동 참거짓 판정이 가능한 신호(테스트 통과, 컴파일 성공, 실행 로그, HTTP 200)를 목록화하는 것이 1단계입니다.

<span style="background-color: #fff59d"><strong>자기평가 신호만으로는 개선을 판정하지 않습니다</strong></span>. 판정 기준은 실행 결과 기반으로 유지합니다.

<span style="background-color: #fff59d"><strong>개선 대상은 답 대신 코드와 실행 트레이스로 설정합니다</strong></span>. 과정 개선은 후속 개선의 입력이 되어 층으로 쌓입니다.

<span style="background-color: #fff59d"><strong>불변 코어는 검증기와 루프 엔진으로 최소화합니다</strong></span>. 하네스·프롬프트·스킬은 개선 대상으로 개방합니다.

평가자 반복 접근 구조에는 오염 관리를 적용합니다. 평가 스크립트에 루프가 계속 붙어 있으면 능력이 늘어난 것이 아니라 평가자가 느슨해진 것일 수 있습니다.

<span style="background-color: #fff59d"><strong>문제 선택과 채점 기준 설정은 사람 영역으로 유지합니다</strong></span>. 무엇을 풀지, 무엇을 믿을지 정하는 판단이 당분간 사람의 자리입니다.

## 참고 자료

- [When AI builds itself — Anthropic Institute](https://www.anthropic.com/institute/recursive-self-improvement)
- [Frontis-MA1: Training an AI4AI Model towards Recursive Self-Improvement in Machine Learning Engineering (arXiv:2607.28568)](https://arxiv.org/abs/2607.28568) · [OpenRSI 저장소](https://github.com/FrontisAI/OpenRSI)
- [Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops (arXiv:2607.07663)](https://arxiv.org/abs/2607.07663)
- [Meta^n: Recursive Self-Improvement through Emergent Depth (arXiv:2608.24735)](https://arxiv.org/abs/2608.24735) · [meta-n 저장소](https://github.com/minnesotanlp/meta-n)
- [The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement (arXiv:2609.11873)](https://arxiv.org/abs/2609.11873)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
