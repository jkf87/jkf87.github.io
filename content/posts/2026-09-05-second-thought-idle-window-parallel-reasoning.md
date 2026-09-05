---
title: "Second Thought: LLM 에이전트의 행동-관찰 구간에서의 병렬 추론 (arXiv 2608.13667)"
date: 2026-09-05
tags:
  - agent
  - LLM
  - inference
  - parallel-reasoning
  - latency
draft: false
description: "ReAct 에이전트의 Action-Observation 윈도에서 네 개의 보조 추론 브랜치를 병렬 실행하는 Second Thought 프레임워크의 정리. 턴 수 9개 조합 전부 감소, 메인 스레드 디코딩 최대 43% 감소, 과제당 중간 지연시간 10.9% 감소를 보고한다."
---

## 핵심 요약

ReAct 루프의 LLM 에이전트에서 추론은 Thought 단계에서만 발생하고, Action 직렬화와 Observation 대기 동안에는 추론이 정지한다. arXiv 2608.13667(v1, 2026-08-13 공개, Singapore Management University)은 이 구간을 reasoning idle window로 정의하고, 여기에 미래 턴을 위한 보조 추론을 병렬로 실행하는 Second Thought를 제안한다.

주요 결과(논문 v1 기준, 기준일 2026-09-05):

| 항목 | 결과 |
| --- | --- |
| 학습 필요 여부 | 불필요 (training-free) |
| 벤치마크 | SWE-Bench Pro, Terminal-Bench 2.1, τ³-bench (banking, 97 tasks) |
| 모델 | DeepSeek-V4-Flash, Qwen3.6-Plus, MiniMax-M3 |
| 평균 턴 수 | 9개 모델-벤치마크 조합 전부 감소 |
| 메인 스레드 디코딩 | 6개 조합 감소, 최대 43% (36.5k → 20.8k 토큰) |
| Pass@1 | 7개 조합 유의차 없음, 2개 조합 +12.4 / +10.2점 |
| 페어 재생 지연시간 | 과제당 중간값 256.9초 → 229.0초 (−10.9%) |
| 컴퓨트 매칭 대조군(s1) 대비 | 적용 4개 설정 전부 높은 Pass@1, 순차 디코딩 1.3배~3.2배 적음 |

<span style="background-color: #fff59d"><strong>요약하면, 정확도를 유지하면서 추가 추론을 임계경로 밖으로 이동시켜 턴 수와 지연시간을 줄이는 학습 불필요 프레임워크다.</strong></span>

## 배경: 추론이 멈추는 구간

테스트타임 스케일링은 추론 토큰을 늘려 정확도를 끌어올리지만, 모든 토큰이 순차 디코딩 경로 위에 놓이므로 지연시간이 비례해서 늘어난다. <span style="background-color: #fff59d"><strong>ReAct 에이전트에서 실질 추론은 Thought 단계에만 존재하며, Action-Observation 구간 동안에는 어떠한 추론도 생성되지 않는다.</strong></span> 논문은 이 반복 구간을 윈도로 formalize하고 "여기에 미래 턴을 위한 병렬 추론을 넣을 수 있는가"를 질문한다.

기존 병렬 추론(셀프컨시스턴시, Tree-of-Thought, 분기 생성 계열)은 Thought 내부에서 경쟁 후보를 수평으로 샘플링하므로 병합 시 투표·정렬이 필요하다. 반면 이 윈도의 보조 추론은 이미 결정된 행동을 바꿀 수 없어 트라젝토리에 조건화되어야 하고, Observation 도착이라는 외부 데드라인 때문에 중단에 강해야 한다. 이 두 제약이 설계를 결정한다.

## 방법: Thought 종료 시점의 네 브랜치 fork

구조는 다음과 같다. Thought가 끝나는 순간 같은 모델이 트라젝토리 스냅샷을 그대로 이어받아 네 개의 보조 브랜치를 fork하고, Observation이 도착하면 브랜치를 전부 종료한 뒤 생성된 생각을 다음 턴 컨텍스트 끝에 병합한다.

![Second Thought 전체 워크플로우](/images/2026-09-05-second-thought-idle-window-parallel-reasoning/fig-2-p3.png)
*Figure 2: Second Thought 워크플로우 (원문 3페이지)*

네 브랜치의 역할은 다음과 같다.

- Check: 현재 계획의 전제 검증
- Recall: 트라젝토리 초반의 제약 및 맥락 재소환
- Rehearse: 다음 단계의 예행
- Alternative: 현재 계획 실패 시의 대안 초안

두 가지 설계 포인트가 중요하다.

원자적 사고(atomic thoughts). 윈도 길이는 Observation 도착 시점에 따라 결정되어 예측 불가능하다. 각 브랜치는 `<thought>...</thought>` 태그로 감싼, 서로 의존하지 않는 원자적 사고 단위로 출력한다. <span style="background-color: #fff59d"><strong>임의 시점에서 중단되어도 진행 중인 단 하나만 버리고 완료된 사고는 그대로 사용할 수 있다.</strong></span>

네 브랜치는 경쟁 후보와 달리 같은 트라젝토리를 보는 보조 관점이다. 그래서 결과를 이어 붙이는 것으로 병합이 끝난다. 프리픽스 KV 캐시가 메인 스레드와 공유되어 비용 효율도 확보된다.

![버그 수정 태스크 비교](/images/2026-09-05-second-thought-idle-window-parallel-reasoning/fig-1-p2.png)
*Figure 1: vanilla ReAct와 Second Thought의 버그 수정 태스크 비교 (원문 2페이지)*

Figure 1의 예시에서 vanilla ReAct는 하위 호환 제약을 위반하여 되돌리기 비용을 지불한다. <span style="background-color: #fff59d"><strong>Second Thought는 대기 시간에 생성된 제약 회상(Recall)과 대안 준비(Alternative)가 이 실수를 사전에 차단한다.</strong></span>

## 결과: 턴 수는 9개 조합 전부 감소

<span style="background-color: #fff59d"><strong>SWE-Bench Pro + Qwen3.6-Plus 설정에서 메인 스레드 출력 토큰이 36,519개에서 20,792개로 43% 감소했다.</strong></span> 턴 수 감소는 9개 모델-벤치마크 조합 전부에서 확인되었고, 메인 스레드 디코딩 감소는 그중 6개에서 유의했다.

Pass@1은 9개 중 7개에서 유의한 변화가 없었다. 유의한 2개는 모두 Terminal-Bench 2.1에서 <span style="background-color: #fff59d"><strong>Qwen3.6-Plus +12.4점, DeepSeek-V4-Flash +10.2점 상승</strong></span>이다. 유일한 하락(52.0% → 51.3%)은 150개 중 1문제 차이로 통계적으로 유의하지 않다.

동일 계산 예산을 메인 스레드 추론에 배치하는 대조군(s1, budget forcing)과 비교하면, 적용 가능한 4개 설정 전부에서 Second Thought가 더 높은 Pass@1을 기록하면서 <span style="background-color: #fff59d"><strong>순차 디코딩은 1.3배에서 3.2배 적게 사용했다.</strong></span> 같은 예산이라면 메인 라인에 넣기보다 윈도에 분산하는 편이 낫다는 해석이 가능하다.

## 절제 실험: 네 브랜치의 역할 분해

![절제 실험](/images/2026-09-05-second-thought-idle-window-parallel-reasoning/fig-3-p6.png)
*Figure 3: 단일 브랜치(only-X) 및 제외(w/o-X) 변형 절제 실험 (원문 6페이지)*

SWE-Bench Pro + DeepSeek-V4-Flash 기준 결과는 다음과 같다.

| 변형 | Pass@1 | 메인 출력 토큰 |
| --- | --- | --- |
| 전체 구성 | 최고 수준 | 중간 |
| only-recall | 46.0% (하락) | 19.7k (최소) |
| w/o-recall | 48.0% (최대 하락) | — |
| w/o-rehearse | 52.0% (유지) | +10% 증가 |

검증 없는 맥락 회상만으로는 부족하고(only-recall), 과거 제약의 재소환이 같은 실수 반복을 방지하며(w/o-recall), Rehearse는 다음 단계 고민을 미리 끝내는 역할(w/o-rehearse)이라는 분해가 성립한다. <span style="background-color: #fff59d"><strong>전체 구성이 파레토 최적이다. 더 적은 토큰을 쓰는 변형은 정확도를 희생한다.</strong></span>

커버리지 측면에서, 수확(harvest) 턴은 전체의 28.7%인데 그 턴이 아이들 타임의 86.7%를 차지한다. <span style="background-color: #fff59d"><strong>96.5%의 태스크가 최소 1회 세컨드 사고를 수신한다.</strong></span>

## 지연시간 검증: 페어 재생

토큰 절약이 실제 시간으로 이어지는지 확인하기 위해 SWE-Bench Pro 50개 인스턴스를 동일 엔드포인트, 동시성 4, 3회 반복의 페어 프로토콜로 재생했다. 결과는 <span style="background-color: #fff59d"><strong>과제당 중간 지연시간 256.9초 → 229.0초(−10.9%)</strong></span>이며, 내역은 메인 디코딩 −13.4%, 도구 실행 −6.0%이다. 이는 임계경로 자체가 실제로 단축되었음을 보여준다.

## 비용 및 제약

네 개 보조 브랜치의 병렬 디코딩으로 API 토큰 비용과 동시성 사용량은 증가한다. 원문 Table 3에 2026-07-01 기준 제공자 단가로 계산한 과제당 비용이 정리되어 있다. 도구 응답 지연이 짧은 환경에서는 윈도 길이 자체가 짧아 효과가 제한될 수 있다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Second Thought는 모델 재학습이 필요한가요?**
아니요. training-free 프레임워크로, 같은 모델이 트라젝토리를 이어받아 보조 브랜치를 fork하는 구조입니다. 프롬프트와 오케스트레이션 수준으로 적용할 수 있습니다.

**정확도가 떨어지지 않나요?**
9개 모델-벤치마크 조합 중 7개에서 유의한 변화가 없었고, 2개(Terminal-Bench 2.1)에서 +12.4점, +10.2점 올랐습니다. 유일한 하락은 유의하지 않은 1문제 차이였습니다.

**지연시간은 얼마나 줄어드나요?**
SWE-Bench Pro 50개 인스턴스 페어 재생에서 과제당 중간값이 256.9초에서 229.0초로 10.9% 줄었습니다. 메인 스레드 출력 토큰 기준으로는 최대 43% 감소 설정도 있습니다.

**추가 비용은 없나요?**
보조 브랜치 4개가 윈도 동안 병렬 디코딩하므로 API 토큰 비용과 동시성은 늘어납니다. 원문 Table 3에 과제당 비용이 정리되어 있습니다.

## 출처

- 논문: Second Thought: Reasoning in Parallel as LLM Agents Act and Observe — https://arxiv.org/abs/2608.13667 (v1, 2026-08-13)
- 코드: https://anonymous.4open.science/r/2nd-thought
- DOI: https://doi.org/10.48550/arXiv.2608.13667
- 인용 수치는 논문 v1 기준이며 기준일은 2026-09-05이다.
