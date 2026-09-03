---
title: "MemoryWalker 정리 — 컨텍스트 압축 하네스에서 RL 학습이 깨지는 이유와 복구법"
date: 2026-09-03
draft: false
tags:
  - agent
  - harness
  - loop
  - RL
  - LLM
  - context-engineering
  - training
description: "Claude Code 같은 하네스는 롤아웃 중 컨텍스트를 압축하는데, 압축된 스트림으로 학습하면 조건부 분포가 트리로 갈라져 성능이 무너집니다. arXiv 2609.00865는 정정법 LogitTree와 SDCC를 제안합니다. 기준일 2026-09-03, arXiv v1 기준."
---

## 결론 먼저

Claude Code, Qwen-Agent 같은 프로덕션 하네스는 롤아웃 중에 <span style="background-color: #fff59d"><strong>컨텍스트를 계속 압축(eviction)합니다</strong></span>. 근데 이 압축된 트랜스크립트를 그대로 RL 학습 데이터로 쓰면 학습-추론 조건부 분포가 어긋납니다. 논문(arXiv:2609.00865, 2026-09-01 v1)은 이 어긋남을 수식으로 정의하고, <span style="background-color: #fff59d"><strong>복구 방법 세 가지를 제안합니다</strong></span>.

핵심 수치(Qwen3-4B, 7개 웹검색 벤치마크 평균 EM):

| 항목 | 값 |
| --- | --- |
| Naive-Compressed 학습 | 28.9 EM |
| Naive-Full(무압축 물리 트레이스) 학습 | 32.1 EM |
| 4D attention mask | 33.4 EM |
| SDCC(단일 백워드 완화법) | 43.1 EM |
| LogitTree(정확 보정) | 45.9 EM |

학습 직렬화 방식만 바꿨는데 평균 EM이 28.9에서 45.9로 갑니다. 롤아웃과 보상은 동일합니다.

## 문제의 정체

하네스가 컨텍스트에서 토큰을 빼내는 시점마다, 그 이후의 "실효 히스토리"는 갈라집니다. <span style="background-color: #fff59d"><strong>학습 대상이 시퀀스에서 트리로 바뀝니다</strong></span>.

기존 선형화는 두 가지 함정에 빠집니다.

- 오른쪽 경로만 남기면 <span style="background-color: #fff59d"><strong>time-travel leakage</strong></span>: 이미 지워진 정보를 알고 있던 시점의 로짓으로 학습하게 됩니다.
- 깊이우선 순회를 재생하면 <span style="background-color: #fff59d"><strong>train-inference mismatch</strong></span>: 실제 배포에서 모델이 본 적 없는 프리픽스로 학습하게 됩니다.

측정값도 있습니다(학습 안 된 Qwen3-4B, 날씨 예보 예제). 압축 스트림 재생은 <span style="background-color: #fff59d"><strong>Δcomp = −22.8 nats</strong></span>, 전체 트레이스 재생은 Δfull = +18.5 nats. 부호가 반대고 크기는 비슷합니다.

![](/images/2026-09-03-memorywalker-context-compression/fig-1-p4.png)

Figure 1에 이 두 함정이 트리 구조로 정리되어 있습니다.

## 복구 방법 셋

| 방법 | 입력 | 비용(기준 대비) | 제약 |
| --- | --- | --- | --- |
| LogitTree | 세그먼트 슬라이스 | 4.20× | K+1번 백워드 |
| 4D attention mask | 전체 물리 트레이스 | 1.35× | 커스텀 커널 + white-box 기록 |
| SDCC | 압축 스트림 | 1.55× | 백워드 1회, O(√ε_KL) 바이어스 |

![](/images/2026-09-03-memorywalker-context-compression/fig-2-p5.png)

LogitTree는 트리를 K+1개의 루트-리프 분기로 쪼개서 정확하게 학습합니다. 4D mask는 같은 목표를 어텐션 마스크 하나로 구현합니다. 둘 다 <span style="background-color: #fff59d"><strong>gradient-equivalent</strong></span>라는 증명이 있습니다.

SDCC(Self-Distillation for Conditioning Consistency)가 실용 포인트입니다. 각 eviction 지점에서, 압축된 학생 정책과 압축 전 프리픽스를 복원한 stop-gradient 교사 정책 사이의 <span style="background-color: #fff59d"><strong>forward KL을 최소화합니다</strong></span>. 백워드 1회로 끝나고, 잔여 KL ε_KL에 대해 Pinsker 부등식으로 학습-배포 TV 거리 상한 <span style="background-color: #fff59d"><strong>O(√ε_KL)를 보장합니다</strong></span>. 교사 eviction 로그를 못 받는 블랙박스 하네스에도 적용됩니다.

## 실험 설정

- 편집기 3종 white-box: TC-RAG, AgentFold, MemexRL. 하네스 2종 black-box: Claude Code, OpenCode.
- 학습 코퍼스: RedSearcher + ASearcher 통합 81,638개 복합 QA.
- 평가: 7개 웹검색 벤치마크 총 38,280 문항 — NQ 3,610, TriviaQA 11,313, HotpotQA 7,405, 2WikiMultiHopQA 12,576, MuSiQue 2,417, Bamboogle 125, FRAMES 824. 실제 웹 검색(DashScope + Firecrawl)을 돌리는 에이전트 루프로 평가합니다.
- AgentFold는 3,000 토큰마다 fold, 압축비 0.06–0.15.

![](/images/2026-09-03-memorywalker-context-compression/table-1-p30.png)

## 결과 읽기

Grand matrix(Table 1)에서 정확 보정 두 종류는 무압축 플로어를 그대로 유지합니다. SDCC는 그 격차를 상당히 좁힙니다. Naive-Compressed는 eviction이 많은 배치에서 특히 <span style="background-color: #fff59d"><strong>로짓 드리프트가 커집니다(0.0237 vs LogitTree 0.0133)</strong></span>.

블랙박스 전이도 같은 순서입니다. <span style="background-color: #fff59d"><strong>Claude Code에서 SDCC 37.5 EM(LogitTree 35.9)</strong></span>, OpenCode에서 36.9 vs 35.0. Claude Code와 OpenCode는 내부 eviction 기록을 노출하지 않아 LogitTree/4D를 못 쓰는데, <span style="background-color: #fff59d"><strong>SDCC만 적용 가능합니다</strong></span>.

논문의 주장은 SDCC 우위가 아닙니다. 비용을 감당할 수 있으면 LogitTree와 4D mask가 정답의 기준점이고, 비용이 안 되거나 블랙박스면 SDCC만 쓸 수 있다는 구도입니다.

## 하네스 만드는 사람에게 적용 포인트

- 압축 하네스로 수집한 트랜스크립트를 <span style="background-color: #fff59d"><strong>그대로 SFT/RL에 넣지 마세요</strong></span>. 조건부 불일치가 수치로 측정됩니다.
- eviction 로그를 남겨두면 LogitTree/4D 같은 정확 보정이 열립니다. 로그가 없으면 SDCC로라도 갭을 묶으세요.
- 백워드 횟수가 병목이면 <span style="background-color: #fff59d"><strong>SDCC(1회)가 LogitTree(K+1회)의 현실적 대체입니다</strong></span>.

## 자주 묻는 질문

- 컨텍스트 압축 하에서 무압축 트레이스로 학습하면 안 되나요? 되긴 하는데(32.1 EM) 실제 배포에서 모델이 보는 건 압축 뷰라 여전히 불일치가 남고, 정확 보정(45.9)보다 14포인트 낮습니다.
- SDCC는 어떤 하네스에 쓸 수 있나요? eviction이 일어난다는 것만 알면 되어서 Claude Code, OpenCode 같은 블랙박스도 가능합니다.
- 논문의 근거 URL은 어디인가요? arXiv:2609.00865(abs, PDF). DOI는 10.48550/arXiv.2609.00865.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)』

원문: [MemoryWalker: Stop Training Agents on Contexts They Never Saw](https://arxiv.org/abs/2609.00865) (arXiv:2609.00865v1, 2026-09-01). 본문 수치는 모두 원문 Table 1/본문 기준이며 <span style="background-color: #fff59d"><strong>기준일은 2026-09-03입니다</strong></span>.
