---
title: "MGM: 멘델 유전법칙으로 코딩 에이전트를 진화시키는 방법"
date: 2026-08-12
tags:
  - agent
  - self-evolution
  - coding-agent
  - harness
  - LLM
  - co-evolution
  - scaffold-evolution
  - DGM
  - HGM
  - loop
---

![](/images/2026-08-12-mgm-mendel-godel-machine/fig1-overview.jpg)

코딩 에이전트가 자기 코드를 고치면서 성능이 올라가는 연구가 나오고 있습니다. DGM, HGM 같은 프레임워크가 대표적이에요. 기존 방식의 문제는 에이전트가 실패하면 그 실패 기록 하나만 보고 코드를 고친다는 거예요. 여러 실패 기록을 비교하면 더 정확하게 고칠 수 있는데, 그걸 활용하지 않습니다.

MGM(Mendel Gödel Machine)은 비교 증거를 활용하는 세 가지 연산자로 이 부분을 개선합니다.

논문: [arXiv:2608.07645](https://arxiv.org/abs/2608.07645)
코드: [github.com/RealLcz/MGM](https://github.com/RealLcz/MGM)

## 세 가지 자기수정 연산자

MGM은 아카이브(에이전트 변형들을 저장하는 트리)에서 이미 수집한 궤적 데이터를 재활용합니다. 추가 평가 없이, 있는 데이터로 더 정확한 진단을 하는 거죠.

1. 클로널 돌연변이 (Clonal Mutation, Φ_CM)
기존 방식과 동일합니다. 에이전트가 task 하나에서 실패하면, 그 궤적 하나만 보고 코드를 고쳐요. 아카이브가 작을 때의 기본 연산자입니다.

2. 반응규 돌연변이 (Reaction-norm Mutation, Φ_RM)
같은 에이전트가 여러 task에서 보인 성공/실패 패턴을 비교합니다. task A에서도 실패하고 task B에서도 실패하면, 그 공통 원인이 에이전트 코드의 구조적 결함일 가능성이 높아요. 단일 task 실패만 볼 때보다 진단 정확도가 올라갑니다.

3. 교계 교배 (Cross-lineage Hybridization, Φ_CH)
다른 계통의 에이전트가 같은 task를 시도한 궤적을 비교합니다. 에이전트 A는 task τ에서 실패했는데 에이전트 B는 성공했다면, B의 궤적에서 A가 놓친 행동 패턴을 찾아서 A 코드에 반영합니다. 파일을 직접 복사하는 게 아니라 에이전트가 직접 학습해서 코드를 수정해요.

## 비교 증거가 수정 품질을 높이는 원리

핵심은 실패 원인 후보를 좁히는 거예요.

예를 들어 task 하나에서 실패했다고 치면, 원인이 될 수 있는 코드 영역이 10개예요. 근데 두 task에서 공통으로 실패한다면, 교집합만 봐도 되니까 후보가 3개로 줄어듭니다. 후보가 적으면 수정이 더 정확해질 수밖에 없죠.

논문에서는 이걸 가산적 적합도 지형(additive fitness landscape) 모델로 정식화하고, 명제 1에서 Φ_RM과 Φ_CH의 유효 수정 확률이 Φ_CM보다 엄격히 높다는 것을 증명했습니다.

![](/images/2026-08-12-mgm-mendel-godel-machine/fig3-fitness-landscape.png)

## 실험 결과

### Polyglot (60-task subset)

백본: Qwen3.6-35B-A3B. 동일 예산 200회 평가.

| 방법 | 초기 | 진화 후 |
|---|---|---|
| HGM | 50.8% | 77.9% |
| MGM | 50.8% | 93.2% |

같은 예산인데 15.3포인트 차이가 납니다.

### SWE-bench Verified (60-task subset)

| 방법 | 초기 | 진화 후 |
|---|---|---|
| HGM | 68.3% | 73.3% |
| MGM | 68.3% | 78.3% |

### Polyglot 전체 (225-task)

Qwen3.6-35B-A3B로 진화한 스캐폴드를 DeepSeek-V4-Pro에 그대로 옮기면 96.9%가 나옵니다. GPT-5를 파라미터 수 117배 차이로 이기는 수준이에요.

### 교차 벤치마크 일반화

Polyglot에서 진화한 스캐폴드를 SWE-bench Pro와 SWE-bench Multilingual에 그대로 가져다 씁니다.

| | 초기 | HGM | MGM |
|---|---|---|---|
| SWE-bench Pro | 16.7% | 13.3% (−3.4) | 26.7% (+10.0) |
| SWE-bench Multilingual | 41.7% | 43.3% (+1.6) | 55.0% (+13.3) |

HGM은 마이너스도 나오는데 MGM은 두 곳 모두 플러스입니다. 진화 과정에서 task 특화가 아니라 재사용 가능한 워크플로 수준 개선을 얻은 거죠.

### 교차 모델 일반화

Qwen3.6-35B-A3B로 진화한 스캐폴드를 DeepSeek-V4-Flash와 DeepSeek-V4-Pro에 옮겨서 평가합니다.

| 백본 | 초기 | HGM | MGM |
|---|---|---|---|
| DeepSeek-V4-Flash | 50.0% | 60.0% | 66.7% |
| DeepSeek-V4-Pro | 45.0% | 70.0% | 75.0% |

## 제거 실험

Φ_RM과 Φ_CH를 각각 빼보면:

| 설정 | Polyglot-60 |
|---|---|
| Full MGM | 93.2% |
| Φ_RM 제거 | 하락 |
| Φ_CH 제거 | 더 큰 하락 |

Φ_CH(교계 교배)가 더 큰 기여를 합니다. 다른 계통의 성공 경험을 가져오는 게 핵심이었던 거죠.

## 정리

기존 self-improving agent 연구(DGM, HGM)는 아카이브 관리와 노드 평가 선택에 집중했습니다. MGM은 수정 증거의 질을 올리는 방향으로 접근합니다.

추가 평가 비용 없이 기존 궤적을 재활용해서 더 나은 진단을 만들어냅니다. 진화 결과가 다른 벤치마크, 다른 모델로 옮겨도 통하는데, 스캐폴드 수준의 개선이기 때문입니다.

작은 모델로 진화한 다음 큰 모델에 옮기는 것도 가능하다는 건, 비용 효율적인 경로가 있다는 뜻입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
