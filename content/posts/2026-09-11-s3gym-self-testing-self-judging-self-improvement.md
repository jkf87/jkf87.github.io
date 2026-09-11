---
title: "S3Gym: LLM이 자기 테스트·자기 판정으로 스스로 좋아지는지 측정하는 벤치마크 (arXiv 2608.31100)"
date: 2026-09-11
tags: [ai, llm, agent, rl, self-improvement, benchmark, arxiv]
draft: false
description: "arXiv 2608.31100 S3Gym 논문 정리. Self-Testing·Self-Judging·Self-Improvement 세 능력을 7개 텍스트 게임에서 평가하고 History ICL, Summary Memory, 파라미터 트레이닝 세 경로를 통일된 프로토콜로 비교한 결과와 실패 지점을 정리했습니다."
---

## 스스로 좋아지는 에이전트는 진짜 존재할까

테스트 게임 7종에서 LLM 에이전트 30 에피소드씩 놀아보게 하고, 그 경험으로 점수가 오르는지 지켜본 벤치마크가 나왔다. S3Gym(ByteDance Seed 외, arXiv 2608.31100)이다. 결론부터 말하면, <span style="background-color: #fff59d"><strong>스스로 좋아지는 일은 일어나기는 하는데 절대 자동이 아니다</strong></span>.

이 벤치마크가 특별한 이유는 하나다. <span style="background-color: #fff59d"><strong>에이전트가 스스로 매긴 점수와 환경 검증기가 매긴 점수를 따로 기록한다.</strong></span> 그래서 "내가 잘했다고 믿은 것"과 "실제로 잘된 것"의 간극이 그대로 숫자로 나온다.

주요 결과 (기준일 2026-09-11, 논문 Table 4·5·7):

| 항목 | 값 |
| --- | --- |
| 게임 | Chess, Minesweeper, Nullify, Tetris, Snake, PvZ, Trust Evolution |
| 자기 판정-환경 보상 동의율 | <span style="background-color: #fff59d"><strong>0.496(Chess) ~ 0.881(PvZ)</strong></span> |
| 판정 정확도와 다음 점수 상승 상관 | <span style="background-color: #fff59d"><strong>ρ ≈ -0.01</strong></span> |
| Qwen3-8B 트레이닝 | Trust 0→30, PvZ <span style="background-color: #fff59d"><strong>23→6(악화)</strong></span> |

논문: [arXiv 2608.31100](https://arxiv.org/abs/2608.31100)

## 자기 개선을 세 단계로 측정한다

S3Gym은 자기 개선을 Self-Testing(전략 시도), Self-Judging(자기 평가), Self-Improvement(반영) 세 단계로 분해한다. <span style="background-color: #fff59d"><strong>탐험 중에는 환경 점수를 숨겨서 자기 판정의 정확도를 따로 측정한다.</strong></span>

![S3Gym 개요](/images/2026-09-11-s3gym-self-testing-self-judging-self-improvement/fig2-overview.png)
*Figure 2: S3Gym 구조. 출처: arXiv 2608.31100*

## 요약 메모리가 원본 히스토리를 이기지 못하는 게임들

경험을 요약해서 넣느냐, 원본 히스토리를 통째로 넣느냐. 결과는 게임 구조에 따라 완전히 갈린다.

| 게임 | 평균 ΔNABA | 유리한 경로 |
| --- | --- | --- |
| Tetris | +6.20 | 요약 |
| Trust Evolution | +8.43 | 요약 |
| Nullify | +2.79 | 요약 |
| Chess | +3.37 | 요약 |
| Minesweeper | -1.12 | 원본 히스토리 |
| Snake | -0.81 | 원본 히스토리 |
| PvZ | -2.11 | 원본 히스토리 |

- 요약이 이긴 게임: <span style="background-color: #fff59d"><strong>Tetris(+6.20), Trust(+8.43), Nullify(+2.79)</strong></span>
- 원본이 이긴 게임: <span style="background-color: #fff59d"><strong>Minesweeper(-1.12), Snake(-0.81), PvZ(-2.11)</strong></span>

GPT-5.5는 PvZ에서 요약으로 바꾸는 순간 <span style="background-color: #fff59d"><strong>AUC+가 548에서 33으로 무너졌다</strong></span>. 규칙으로 압축되는 경험과, 현재 상태를 정확히 복원해야 하는 경험은 다른 종류라는 뜻이다.

![학습 곡선](/images/2026-09-11-s3gym-self-testing-self-judging-self-improvement/fig3-trajectories.png)
*Figure 3: 경로별 학습 곡선. 출처: arXiv 2608.31100*

## 파라미터 트레이닝은 게임마다 방향이 갈린다

Qwen3-8B를 경험으로 파인튜닝하니 Trust Evolution은 <span style="background-color: #fff59d"><strong>0에서 30까지 올랐지만</strong></span>, PvZ은 23에서 6으로 떨어졌다. <span style="background-color: #fff59d"><strong>잘못 판정된 경험이 파라미터에 굳어버리면 원래 잘하던 행동까지 덮어쓴다</strong></span>는 경고다.

## 채점 정확도와 성적 향상은 상관이 없다

116,117개 트랜지션을 분석했더니, <span style="background-color: #fff59d"><strong>스텝 채점 정확도와 다음 평가 점수 상승의 상관이 ρ ≈ -0.01</strong></span>이다. Chess는 자기 판정 동의율이 <span style="background-color: #fff59d"><strong>동전 던지기 수준(0.496)</strong></span>이고 과잉신뢰율은 0.365로 최고다. <span style="background-color: #fff59d"><strong>성공을 알아채는 것과 그걸 실행 가능한 정책으로 바꾸는 것은 전혀 다른 능력</strong></span>이라는 게 이 벤치마크의 핵심 메시지다.

![개념도](/images/2026-09-11-s3gym-self-testing-self-judging-self-improvement/fig1-concept.png)
*Figure 1: 경험 기반 개선 개념도. 출처: arXiv 2608.31100*

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### S3Gym이 기존 벤치마크와 다른 점은?

모델을 고정된 정책으로 보지 않고, <span style="background-color: #fff59d"><strong>경험이 행동을 개선하는지를 측정하며, 자기 판정과 환경 점수를 분리 기록</strong></span>합니다.

### Summary Memory가 항상 낫나요?

아니요. 게임 구조에 따라 요약이 크게 뒤처리는 경우가 있고, 논문은 <span style="background-color: #fff59d"><strong>요약을 선택적 압축 기제로 봐야 한다</strong></span>고 결론짓습니다.

### 자기 채점은 믿을 만한가요?

게임별 동의율 <span style="background-color: #fff59d"><strong>0.496~0.881으로 편차가 크고, 채점 정확도와 실제 개선의 상관은 사실상 0</strong></span>입니다.
