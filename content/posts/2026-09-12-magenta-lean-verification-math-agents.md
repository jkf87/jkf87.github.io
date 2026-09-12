---
title: "Magenta: Lean 검증을 수학 추론 루프 안에 넣어 7B 모델로 IMO 6문제를 전부 푼 방법 (arXiv 2609.11319)"
date: 2026-09-12
tags: [paper, llm, agents, lean, verification, math, magenta]
draft: false
description: "Magenta는 자연어 문제를 Lean 4 명제로 바꾸고 기계 검증 증명까지 만드는 트레이닝 프리 파이프라인입니다. 7B 리저너로 IMO 2026 6문제 전부 해결, AIME·HMMT는 100%를 기록했습니다."
---

## 결론 먼저

Magenta는 자연어 수학 문제를 받아 답을 내고, 그 답을 Lean 4 명제로 바꾸고, 기계 검증되는 증명까지 만드는 트레이닝 프리 에이전트 파이프라인입니다. 핵심은 이겁니다. 검증 신호가 추론 루프 안으로 들어오면서 <span style="background-color: #fff59d"><strong>K2-HORIZON-7B 하나로 IMO 2026 여섯 문제를 전부 풀었습니다</strong></span>. 논문이 아는 한 이 기록을 낸 가장 작은 리저너입니다.

AIME 2025, AIME 2026, HMMT February 2026에서는 4가지 리저너 조합 모두 <span style="background-color: #fff59d"><strong>정확도 100%</strong></span>를 냈습니다. 93문제 전부라는 뜻입니다.

논문: [arXiv:2609.11319](https://arxiv.org/abs/2609.11319)

## 핵심 숫자 정리

| 항목 | 값 |
| --- | --- |
| K2-HORIZON-7B 단독 (93문제 평균) | 74.19% |
| K2-HORIZON-7B + Magenta | 100% (↑25.81pp) |
| 가장 작은 상승폭 (Qwen3.8-27B) | +8.60pp |
| IMO 2026 | 7B 리저너로 6/6 |
| 증명 검증 | Lean v4.29.1 + MATHLIB (SafeVerify) |
| 기준일 | 2026-09-12 기준, arXiv v1 (2026-09-10 게시) |

## 문제 설정: 증명은 통과했는데 뭘 증명했는지 모르는 상태

Lean 같은 증명 보조기는 컴파일이 통과하면 증명이 맞다는 이산 검증을 줍니다. 근데 함정이 하나 있습니다.

Lean 커널은 이 증명이 이 명제를 증명한다는 사실만 확인할 수 있습니다. <span style="background-color: #fff59d"><strong>그 명제가 원래 자연어 문제를 충실히 옮겼는지는 확인해주지 않습니다</strong></span>.

예를 들어 문제의 조건 하나를 슬쩍 빼거나, 답을 아는 상태에서 명제가 그 답을 가리키도록 만들면 증명은 통과하는데 원래 문제를 푼 게 아닙니다. 논문은 이 간극을 autoformalisation gap이라 부르고, 여기서 나오는 잘못된 통과를 false certificate로 부릅니다.

기존 벤치마크 대부분은 사람이 쓴 formal statement를 주고 증명만 시킵니다. 그래서 이 문제를 애초에 피해갑니다. Magenta는 자연어 문제에서 시작하니 이 간극을 정면으로 다룹니다.

## 파이프라인 구조

![](/images/2026-09-12-magenta-lean-verification-math-agents/fig1-overview.png)
*그림 1. Magenta 전체 파이프라인 (원문 Figure 1)*

역할을 넷으로 나눕니다. 정리했습니다.

| 역할 | 하는 일 | 기본 모델 |
| --- | --- | --- |
| 리저너 | 자연어 풀이 도출, 답 확정 | K2-HORIZON-7B/375B, Qwen3.8-27B, GPT-5.6-Sol |
| 포멀라이저 | 문제와 답을 Lean 4 명제로 변환 | Goedel-Formaliser-32B |
| 스테이트먼트 저지 | 명제가 원래 문제를 보존하는지 검사 | DeepSeek-V4-Flash |
| 프로버 | Lean 증명 스크립트 작성 | Leanstral-1.5 |

스테이트먼트 저지가 검사하는 건 구체적입니다. 가설 누락, 상수 변경, 자명해지는 가정을 기각합니다. <span style="background-color: #fff59d"><strong>무엇을 증명할지 결정하는 저지가 Lean 보증과 원래 문제를 잇는 다리입니다</strong></span>.

여기에 실패 처리를 담당하는 error-attribution 저지가 붙습니다. 증명이 실패하면 원인을 SYNTAX/Math로 분류합니다. 코드 문제면 지역 Lean 수리로, 수학 문제면 새 추론 체인으로 되돌립니다. <span style="background-color: #fff59d"><strong>실패를 무작정 리샘플하지 않고 원인별로 라우팅하는 게 기존 재시도 루프와 다른 점입니다</strong></span>.

기본 구성은 전부 오픈웨이트입니다. 리저너만 바꿔가며 테스트했습니다.

## 결과: 리저너를 바꿔도 전부 100%

![](/images/2026-09-12-magenta-lean-verification-math-agents/table1-accuracy.png)
*표 1. 경시대회 벤치마크 정확도, 93문제 (원문 Table 1)*

주요 결과만 옮기면 이렇습니다.

| 모델 | AIME 2025 | AIME 2026 | HMMT Feb | 전체 |
| --- | --- | --- | --- | --- |
| Claude Opus 5 | 100.00 | 100.00 | 96.97 | 98.92 |
| Gemini 3.7 Flash | 100.00 | 100.00 | 90.91 | 96.77 |
| Kimi K3 | 93.33 | 90.00 | 78.79 | 87.10 |
| K2-Horizon-7B 단독 | 83.33 | 80.00 | 60.61 | 74.19 |
| K2-Horizon-7B + Magenta | 100.00 | 100.00 | 100.00 | 100.00 |
| GPT-5.6-Sol 단독 | 90.00 | 86.67 | 78.79 | 84.95 |
| GPT-5.6-Sol + Magenta | 100.00 | 100.00 | 100.00 | 100.00 |

리저너 교체에도 전부 100%가 나왔습니다. 포멀라이저와 프로버를 GPT-5.6-Sol로 통째로 바꿔도 역시 만점이었습니다.

논문은 이걸 근거로 성능 향상이 특정 모델이 아니라 <span style="background-color: #fff59d"><strong>검증이 포함된 파이프라인 구조 자체에서 나온다</strong></span>고 해석합니다. 리저너별 상승폭은 Qwen3.8-27B의 +8.6점부터 K2-HORIZON-7B의 +25.8점까지입니다.

## 스테이트먼트 저지를 빼면 생기는 일

저지 없이 돌리면 문제가 자명해지는 명제나 조건이 빠진 명제의 증명이 통과합니다. 증명은 성공했는데 푼 건 다른 문제인 상태가 됩니다.

한계도 논문이 솔직하게 밝힙니다. 최종 출력은 Lean 커널이 아니라 학습된 저지의 승인을 거치므로 <span style="background-color: #fff59d"><strong>소프트 인증서(soft certificate)</strong></span>입니다. autoformalisation gap의 완전한 제거는 현재 기술로 불가능하다고 못 박습니다.

## 비용 분포

![](/images/2026-09-12-magenta-lean-verification-math-agents/fig3-pass-rate.png)
*그림 3. formal statement 생성 호출 수에 따른 누적 통과율, AIME 2026 (원문 Figure 3)*

포멀라이저 선택이 비용을 크게 갈랐습니다.

- Codex: AIME 2026에서 <span style="background-color: #fff59d"><strong>첫 호출에 약 66% 문제의 명제 통과</strong></span>, 6호 안에 커버 완료
- Goedel: 첫 통과율 42%, 풀 커버에 약 120호 필요, 6호 예산에서 커버율 약 68%

![](/images/2026-09-12-magenta-lean-verification-math-agents/fig2-self-corrections.png)
*그림 2. K2 리저너가 필요로 한 자기수정 횟수 분포 (원문 Figure 2)*

어려운 문제에서는 피드백을 받아 고치는 방식이 독립 리샘플링보다 효율이 좋았습니다. 실패 진단 정보가 다음 시도의 탐색 폭을 줄여주기 때문입니다.

## 오염 가능성 점검

만점이 나오면 오염 의심이 먼저 듭니다. 저자들도 점검했습니다.

기준일 기준 <span style="background-color: #fff59d"><strong>AIME/HMMT 문제 다수가 퍼블릭 웹에 공개되지 않은 상태</strong></span>라 원샷 리콜로 결과를 설명하기 어렵다고 봅니다. 패러프레이즈 버전 테스트(Table 2)에서도 성능이 유지됐습니다.

## 내 해석: 검증 신호의 위치가 핵심

제가 주목하는 건 7B의 IMO 기록 자체보다 구조입니다. <span style="background-color: #fff59d"><strong>검증기가 정답 라벨 없이도 역할 분리로 추론 루프 안에 배치됐다는 점</strong></span>입니다.

LLM 저지는 학습된 프록시라 완전하지 않습니다. 근데 명제 정합성 검사는 명제 생성보다 쉬운 과제라는 가정 위에 역할을 나눠두면, Lean 커널의 이산 검증을 답의 신뢰도에 실제로 묶어낼 수 있습니다.

수학 밖의 도메인에서 같은 구조가 통할지 여부는 검증기의 이산성이 얼마나 강한가에 달려 있습니다. 저지가 다루는 간극이 어느 도메인에서나 남는다는 점이 이 접근의 경계입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### Magenta가 모델을 학습하는 방식
학습시키지 않습니다. 트레이닝 프리 파이프라인이고, 기존 모델을 역할별로 오케스트레이션합니다.

### Lean 증명이 통과하면 정답이 보장되는 이유와 한계
Lean은 해당 명제의 증명만 검증합니다. 명제가 원래 문제를 충실히 옮겼는지는 스테이트먼트 저지가 검사하며, 학습된 저지라 완전하지 않습니다.

### 오픈웨이트만으로 구동하는 방법
가능합니다. 기본 구성(Goedel-Formaliser-32B, DeepSeek-V4-Flash, Leanstral-1.5)은 전부 오픈웨이트입니다.

### 운영 비용을 줄이는 방법
포멀라이저 선택이 가장 큽니다. Codex는 명제 생성 6호 안에 벤치마크를 커버했고 Goedel은 약 120호가 필요했습니다. 저지가 불성실 명제를 증명 시도 전에 걸러서 비용 폭증을 막습니다.
