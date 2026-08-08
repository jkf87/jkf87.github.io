---
title: "OSReward: 컴퓨터 사용 에이전트의 보상 신호를 누가 판정하는가"
date: 2026-08-08
tags:
  - agent
  - computer-use
  - reward-model
  - VLM-judge
  - benchmark
  - RL
  - LLM
  - harness
---

컴퓨터를 대신 쓰는 AI 에이전트(CUA)가 늘고 있습니다. 문제는 이 에이전트가 임무를 완수했는지 판정하는 일입니다. 인간이 일일이 확인할 수 없으니 VLM(비전-언어 모델)에게 판사 역할을 맡기는데, 이 판사가 믿을 만한지 처음으로 체계적으로 검증한 벤치마크가 나왔습니다.

## 핵심 결과

OSReward는 4개 플랫폼(Windows, macOS, Linux, Web)에서 다양한 에이전트 백본이 실행한 궤적을 수집하고, 다단계 인간 주석으로 정답 라벨을 만들었습니다. 총 1,019개의 human-gold 궤적, 약 800인시가 투입되었습니다.

VLM 판사들을 평가한 결과입니다:

| 측정 항목 | 결과 |
|---|---|
| 최고 성능 VLM 판사 | 정확도 70%대 초반 |
| 일반적인 오픈 모델 | 정확도 50%대 (거의 찍기 수준) |
| 주요 실패 모드 | 실패한 궤적을 성공으로 잘못 판정 (leneincy bias) |
| OSReward-Hard(진짜 어려운 케이스) | 최고 모델도 chance level 근처 |

VLM 판사들이 일관되게 보인 패턴은 **실패를 성공으로 받아들이는 관대함 편향**입니다. 판사가 에이전트의 텍스트 행동 기록을 화면 상태보다 더 많이 참고하기 때문입니다.

## OS-Shepherd: 오픈 보상 모델

신뢰할 수 있는 판사는 비용이 너무 비싸고, 저렴한 모델은 신뢰할 수 없습니다. 이 간극을 메우기 위해 OS-Shepherd를 만들었습니다.

| 구성 요소 | 규모 |
|---|---|
| OS-Shepherd-100K | 10만 개 추론 주석 궤적 판정 |
| OS-Shepherd-9B | 9B 오픈 보상 모델 |
| OS-Shepherd-35B-A3B | 35B MoE 오픈 보상 모델 |
| 비용 | 프론티어 대비 30~60배 저렴 |

학습 데이터는 다양한 강력 VLM 판사들이 독립적으로 같은 판정에 도달한 궤적만 보존해서 라벨 신뢰성을 확보했습니다. RL 단계에서는 false-success 모드를 직접 타겟팅해서 관대함 편향을 교정합니다.

## 왜 중요한가

CUA 평가· 데이터 큐레이션· RL의 보상 신호가 모두 VLM 판사에 의존합니다. 근데 그 판사들이 실제로는 실패를 성공으로 분류하는 일이 많았다는 것입니다.

이건 에이전트 RL에 직접적인 영향을 줍니다. 보상 모델이 잘못된 보상을 주면 에이전트가 잘못된 행동을 강화받습니다. OS-Shepherd는 이 문제에 대한 오픈소스 대안입니다.

## 벤치마크 구성

OSReward는 세 가지 서브셋으로 구성됩니다:

- **OSReward (전체)**: 4개 플랫폼, 다양한 에이전트 백본, human-gold 라벨
- **OSReward-Hard**: 진짜 판정하기 어려운 케이스만 집중
- **OSReward-Multi**: 효율성과 정렬 점수를 세밀하게 평가

궤적은 에이전트 백본(다양한 오픈/상용 에이전트), 플랫폼(Windows/macOS/Linux/Web), 태스크 유형으로 다양하게 구성되어 있습니다.

## 데이터 및 코드

전체 코드, 벤치마크, 데이터셋, 모델 체크포인트가 공개되어 있습니다:

- 프로젝트 페이지: https://os-copilot.github.io/OSReward-Home/
- 논문: https://arxiv.org/abs/2607.28609

![Figure 1: VLM 판사들의 CUA 궤적 판정 성능과 관대함 편향](/images/2026-08-08-osreward-cua-reward-benchmark/fig-1-p1.png)

![Figure 2: OSReward-Hard에서 비용 대비 정확도 — 신뢰할 수 있는 판사는 비싸다](/images/2026-08-08-osreward-cua-reward-benchmark/fig-2-p3.png)

![Table 1: 주요 판사 모델과 OS-Shepherd의 OSReward 성능 비교](/images/2026-08-08-osreward-cua-reward-benchmark/table-1-p11.png)

![Figure 7: 판사별 오류 구성 — 관대함 편향이 주요 실패 모드다](/images/2026-08-08-osreward-cua-reward-benchmark/fig-7-p12.png)

## 더 실습해보고 싶은 분들께

에이전트 보상 모델링과 RL 파이프라인에 관심 있다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 요약

VLM 판사가 CUA 궤적을 판정할 때 체계적인 관대함 편향이 있습니다. OSReward는 이를 처음으로 측정한 벤치마크이고, OS-Shepherd는 이 문제를 해결하는 오픈 보상 모델입니다. 에이전트 RL을 하려는 분이라면 보상 신호의 신뢰성을 먼저 확인해야 합니다.
