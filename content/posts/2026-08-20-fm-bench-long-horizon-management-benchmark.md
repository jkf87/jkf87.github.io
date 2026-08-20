---
title: "FM-Bench — LLM 에이전트 20년 경영 벤치마크, 성적은 경영 행동이 결정한다"
date: 2026-08-20T16:00:00+09:00
tags: [agent, benchmark, long-horizon, LLM, paper-review]
draft: false
---

## 결론 먼저

LLM 에이전트가 축구 클럽을 <span style="background-color: #fff59d"><strong>20년 동안 340~400번의 의사결정 지점</strong></span>으로 경영하게 하고 최종 점수 하나로 평가하는 벤치마크가 나왔습니다. `FM-Bench (Football Management Benchmark)`입니다. arXiv 2608.18423, 2026-08-19 공개, 코드는 GitHub에 오픈소스로 있습니다.

핵심 결과는 한 줄로 정리됩니다.

<span style="background-color: #fff59d"><strong>순위를 가르는 것은 모델 크기도, 가격도, 벤더도 아니고 경영 행동이다.</strong></span> 토큰 지출량은 성적과 상관이 없었습니다.

## 벤치마크 구조

하나의 런(run)은 이렇게 돌아갑니다.

- LLM 에이전트가 축구 클럽 단장이 되어 20 in-game 년을 경영
- 26개 도구(tool)를 사용: 선수 영입, 트레이드, 계약 협상, 시설·유스 투자, 라인업 설정
- 모든 라이벌과 <span style="background-color: #fff59d"><strong>동일한 예산으로 스쿼드를 시작</strong></span>
- 이사회가 있고, 성적이 나쁘면 <span style="background-color: #fff59d"><strong>해임될 수 있음</strong></span>
- 결정론적 엔진이 20년을 누적해 하나의 최종 점수를 냄. LLM 심판이나 인간 평가자 없음

두 트랙이 있습니다.

1. **Solo 트랙**: 프론티어 모델 15개가 각각 고정된 스크립트 세계와 대결
2. **Arena**: 같은 15개 모델 + 스크립트 앵커 1개가 <span style="background-color: #fff59d"><strong>하나의 공유 세계에서 20년간 맞대결</strong></span>. 이 규모의 헤드투헤드 평가는 논문 주장 기준 최초

![Figure 1: 하나의 런이 어떻게 진행되는지. 20 in-game 년, 340~400개 의사결정 지점](/images/2026-08-20-fm-bench-long-horizon-management-benchmark/figure-1-run-overview.png)

*Figure 1. 런의 구조 (원문 Figure 1 발췌, 캡션 앵커 크롭)*

## 결과

- 3개 시드에서 <span style="background-color: #fff59d"><strong>15개 모델 전부 모든 호라이즌을 완주</strong></span>. 반면 눈가림 스크립트 baseline은 대부분의 런에서 파산(도태)
- Solo 평균 점수와 Arena 1위는 `claude-fable-5`가 기록
- 근데 Arena 우승은 <span style="background-color: #fff59d"><strong>10개 서로 다른 모델 사이에서 로테이션</strong></span>
- <span style="background-color: #fff59d"><strong>스케일·가격·벤더 어느 것도 순위를 예측하지 못했고</strong></span>, 순위는 호라이즌 후반부에야 안정
- 최고 기록 인간 첫 플레이어는 모델 보드의 <span style="background-color: #fff59d"><strong>최하단</strong></span>에 위치

인간 첫 플레이가 모델 전원보다 아래라는 점은 의외입니다. 20년치 누적 결과를 감안하면 인간이 오히려 장기 보상 최적화에 약하다는 신호로 읽히네요.

## 무엇이 모델을 가르나

점수 뒤에 있는 행동 여섯 가지를 측정했습니다. 고득점 모델의 공통 패턴은 다음과 같습니다.

- 시즌 막판에 <span style="background-color: #fff59d"><strong>느린 보상 투자(유스 등)를 줄이는 것</strong></span>
- 현금을 방치하지 않고 <span style="background-color: #fff59d"><strong>계속 투자 상태로 유지</strong></span>
- 계약 만료 데드라인 훨씬 전에 <span style="background-color: #fff59d"><strong>갱신 협상을 먼저 여는 것</strong></span>

![Figure 3: 크레딧 어사인먼트. 좌: 보상 시계에 따른 재량 지출, 우: 관련 행동 지표](/images/2026-08-20-fm-bench-long-horizon-management-benchmark/figure-3-credit-assignment.png)

*Figure 3. 크레딧 어사인먼트 분석 (원문 Figure 3 발췌)*

반면 두 가지는 전 모델이 실패했습니다.

1. <span style="background-color: #fff59d"><strong>수백 번의 거절된 바이드에서 시장의 숨은 가격을 학습하는 것 — 어떤 모델도 못 함</strong></span>
2. 셀프 관리 메모리가 두 반대 모드로 실패: <span style="background-color: #fff59d"><strong>계속 커지기만 하는 아카이브</strong></span>, 아니면 <span style="background-color: #fff59d"><strong>매 시즌 전부 다시 쓰는 플랜</strong></span>

![Figure 5: 15개 모델의 6축 역량 매트릭스](/images/2026-08-20-fm-bench-long-horizon-management-benchmark/figure-5-capability-matrix.png)

*Figure 5. 역량 매트릭스 (원문 Figure 5 발췌)*

## 내 해석

원문 근거와 제 해석을 나눠 정리했습니다.

원문 근거: 위 결과 전부. 특히 "token spend predicts nothing"과 메모리 실패 두 모드.

내 해석:

- 긴 호라이즌 에이전트에서 중요한 건 추론량이 아니라 <span style="background-color: #fff59d"><strong>보상 시계(payoff horizon)에 맞춘 자원 배분</strong></span>입니다. 이건 모델을 바꿔서 얻는 게 아니라 하네스·정책 설계 영역이에요.
- 거절된 바이드에서 가격을 배우지 못한다는 건, <span style="background-color: #fff59d"><strong>암시적 피드백 신호를 메모리에 구조화해서 남기는 능력이 현재 에이전트에 없다</strong></span>는 뜻입니다. 이건 긴 컨텍스트 에이전트 설계자에게 직접 적용되는 교훈이구요.
- 메모리 두 실패 모드(무한 증가 아카이브 vs 매번 리라이트)는 실무 에이전트 메모리 설계에서 <span style="background-color: #fff59d"><strong>정확히 피해야 하는 두 극단</strong></span>입니다. 통합·압축이 있는 중간 지점이 필요하다는 방향을 보여줍니다.

최종 테이크아웨이: 긴 호라이즌 의사결정 벤치마크에서 <span style="background-color: #fff59d"><strong>행동 정책이 계산량을 이겼다</strong></span>는 결과입니다. 에이전트를 튜닝할 때 더 큰 모델보다 먼저 볼 지점을 주는 논문입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: arXiv 2608.18423 — FM-Bench: A Benchmark for Long-Horizon Management with Competing Agents
- 코드: https://github.com/Analogy-AI/fm-bench
- HF paper page: https://huggingface.co/papers/2608.18423
