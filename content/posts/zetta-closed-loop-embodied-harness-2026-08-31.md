---
title: "Zetta (arXiv 2608.16590): 폐루프 자기진화 엔바디드 하네스 기술 정리"
date: 2026-08-31
tags:
  - agents
  - embodied
  - harness
draft: false
description: "Zetta는 VLA 베이스 정책을 동결한 상태에서 코드 기반 런타임 크리틱과 회복 스킬을 온라인으로 진화시키는 폐루프 엔바디드 하네스다. LIBERO-Pro 90.8%, RoboCasa 93.6% 달성과 Z-Infra 롤아웃 인프라의 20.6배 처리량 개선을 정리한다."
---

## 결론 먼저

본 보고서는 arXiv 2608.16590v1(2026-08-17, 칭화 AIR 및 Z-Trans AI)로 공개된 "Zetta ζ: An Efficient Closed-Loop Embodied Harness for Self-Evolving Physical Intelligence"의 기술 내용을 정리한다.

논문의 주장은 다음과 같다. 기존 엔바디드 에이전트 하네스는 오픈루프로 동작하여 에피소드 종료 후에만 반성을 수행한다. Zetta는 베이스 정책(VLA)을 동결한 채, 하네스 H={C, R, T}(런타임 크리틱, 회복 플레이북, 이기종 도구셋)을 온라인에서 진화시켜 <span style="background-color: #fff59d"><strong>폐루프 실행을 구현</strong></span>한다. 기준일: 2026-08-31, 논문 v1 기준.

## 핵심 결과

| 항목 | 결과 |
| --- | --- |
| LIBERO-Pro 성공률 | 34.5% → <span style="background-color: #fff59d"><strong>90.8%</strong></span> |
| RoboCasa 18 태스크 평균 | 73.56% → <span style="background-color: #fff59d"><strong>93.56%</strong></span> |
| 추론 지연 | <span style="background-color: #fff59d"><strong>91% 감소 (11.1배)</strong></span> |
| 롤아웃 처리량 | 35.1 ep/min (<span style="background-color: #fff59d"><strong>20.6배</strong></span>) |
| 베이스 정책 | π0.5, GR00T N1.5 동결 |

기준일: 2026-08-31, 논문 v1 기준.

## 프레임워크 구조

Zetta는 세 개의 시간 스케일 분리 루프로 구성된다.

1. Critic-Governed Action Loop: 액션 주파수로 크리틱을 실행하고 검증된 증거에 기반해 회복 스킬을 발동한다.
   <span style="background-color: #fff59d"><strong>실행 중 실시간 개입을 담당하는 루프</strong></span>다.
2. Rollout-Batch Candidate Optimization Loop: 실패 클러스터링 및 인과 진단을 통해 후보 크리틱·회복을 제안한다.
3. Validation-Gated Skill Update Loop: <span style="background-color: #fff59d"><strong>성공률 개선과 롤아웃 간 일반화를 통과한 후보만 스킬 메모리에 반입</strong></span>한다.

진단은 Evaluation, Critic, State, Planning, Recovery, Parameter 순서의 계층적 절차를 따른다.

![Zetta 전체 프레임워크](/images/zetta-closed-loop-embodied-harness-2026-08-31/fig-1-p1.png)

## 아하 모먼트와 제로샷 전이

물리 지능의 "아하 모먼트"가 관측되었다. 예컨대 LIBERO-Pro의 Wine Bottle in Bowl 태스크에서 성공률이 정체 구간(15%)을 지나 <span style="background-color: #fff59d"><strong>retained-object 크리틱 도입 후 95%로 급등</strong></span>했다.

PnP-Stove에서 진화한 스킬의 <span style="background-color: #fff59d"><strong>제로샷 전이</strong></span>로 PnP-Sink 58%→82%, PnP-Cabinet 62%→80%, PnP-Toaster 72%→90%의 개선이 확인되었다.

전이가 되는 이유는 스킬이 태스크 궤적을 외운 게 아니라 <span style="background-color: #fff59d"><strong>EEF 정렬·접촉 안정성 같은 태스크 독립 물리 변수에 작동</strong></span>하기 때문이라는 게 저자들의 해석이다.

![RoboCasa 누적 스케일링](/images/zetta-closed-loop-embodied-harness-2026-08-31/fig-9-p24.png)

## Z-Infra 롤아웃 인프라 구조

Z-Infra는 자기진화 에이전트용 롤아웃 인프라로, Ray 기반 3계층(컨트롤 플레인, 환경 워커, 롤아웃 워커) 구조다.

VLM/Action Expert 프로세스 분리(CUDA IPC)로 <span style="background-color: #fff59d"><strong>π0.5 평균 추론 지연 53% 감소</strong></span>, prefix MLP W8A8 양자화로 1.18~1.32배 가속을 달성했다. 폐루프 학습에서는 <span style="background-color: #fff59d"><strong>롤아웃 처리량이 곧 진화 속도</strong></span>라는 게 이 인프라를 따로 만든 이유다.

![Z-Infra 3계층 아키텍처](/images/zetta-closed-loop-embodied-harness-2026-08-31/fig-3-p14.png)

## 한계

실험이 <span style="background-color: #fff59d"><strong>시뮬레이션 벤치마크(LIBERO-Pro, RoboCasa)로 제한</strong></span>된다. 실물 로봇 환경에서의 폐루프 크리틱 주파수 재현성은 후속 연구 과제다.

진화 종료 후 <span style="background-color: #fff59d"><strong>진화에 쓰이지 않은 격리 테스트 시드</strong></span>에서 최종 평가했다는 점은 신뢰 근거로 꼽을 만하다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Q: Zetta에서 실제로 학습되는 대상은 무엇인가요?**
베이스 VLA 정책(π0.5, GR00T N1.5)의 파라미터는 동결되어 있고, 런타임 크리틱(C)·회복 플레이북(R)·도구셋(T)으로 구성된 하네스만 진화합니다.

**Q: LIBERO-Pro 90.8%는 어떤 조건에서 측정된 값인가요?**
진화 이터레이션이 쌓이며 34.5%에서 90.8%까지 상승했고, 최종 평가는 진화에 사용되지 않은 격리 시드에서 수행했습니다. π0.5 단독 매크로 평균은 32.0%, Zetta 적용 후 71.13%입니다.

**Q: 진화한 스킬이 다른 태스크로 전이되나요?**
PnP-Stove에서 배운 pre-grasp 정렬·재그래스프·안정 배치 스킬을 PnP-Sink/Cabinet/Toaster에 제로샷 적용해 평균 64%→84%로 올랐습니다.

**Q: 코드와 프로젝트 페이지는 어디서 볼 수 있나요?**
프로젝트 페이지는 https://air-embodied-brain.github.io/zetta , 논문은 https://arxiv.org/abs/2608.16590 에서 확인할 수 있습니다.

## 출처

- arXiv 2608.16590: https://arxiv.org/abs/2608.16590
- DOI: https://doi.org/10.48550/arXiv.2608.16590
- 프로젝트 페이지: https://air-embodied-brain.github.io/zetta
