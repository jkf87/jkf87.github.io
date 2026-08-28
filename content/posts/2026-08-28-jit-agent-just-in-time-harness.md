---
title: "JIT-Agent — 하네스를 미리 만들지 말고, 태스크가 들어올 때 생성한다"
date: 2026-08-28
draft: false
tags: [agent, harness, LLM, arxiv]
description: "arXiv 2608.25593 논문 리뷰. JIT-Agent는 메모리·계획·액션·도구 오케스트레이션 4개 모듈로 하네스를 정형화하고, 태스크마다 맞춤 하네스를 실시간 생성·수리·진화시키는 모델입니다. DeepSeek-V4-Flash가 GPT-5.6을 넘고, 태스크당 API 비용은 평균 36% 줄었습니다."
---

## 결론 먼저

JIT-Agent(arXiv 2608.25593, 2026-08-26 제출)는 에이전트 하네스를 태스크가 들어올 때 그 자리에서 생성하는 프로그램으로 취급합니다. 논문은 이걸 harness intelligence라고 부르고, <span style="background-color: #fff59d"><strong>모델 스케일링과 직교하는 별도의 훈련 가능한 능력</strong></span>이라고 주장합니다.

핵심 숫자 세 가지:

| 항목 | 결과 | 기준 |
| --- | --- | --- |
| DeepSearchQA | DeepSeek-V4-Flash + JIT-Agent가 GPT-5.6 대비 +9.1 | 논문 Figure 1 |
| OdysseyBench | +4.3 (같은 설정) | 논문 Figure 1 |
| 태스크당 API 비용 | 평균 36% 감소 | 논문 Figure 4 |

기준일: 2026-08-28 기준, arXiv v1 초록과 본문 기준입니다.

## 하네스를 4개 모듈로 정형화한다

논문은 하네스 `h`를 네 튜플로 정의합니다.

```
h = (M, P, A, F)
```

| 모듈 | 역할 |
| --- | --- |
| M (Memory) | 히스토리 컨텍스트, 증거 저장, 상태 압축 |
| P (Planning) | 목표 분해, 서브골 생성, 개정 |
| A (Action) | 실행 루프, 제어 흐름, 검증 |
| F (Capability) | 태스크 레지스트리 기반 도구·스킬 배치 |

실행 프로토콜 Π 아래에서 정보는 <span style="background-color: #fff59d"><strong>M→P→F→A 순서로 흐릅니다</strong></span>. ReAct 같은 고정 스캐폴드도 이 표기로 변환할 수 있고, 그래서 비교 대상이 됩니다.

여기까진 표기 정리입니다. 중요한 건 다음 단계입니다.

## 3단계 훈련: 생성 → 수리 → 진화

![](/images/2026-08-28-jit-agent-just-in-time-harness/jit_method_overview_final.png)

![](/images/2026-08-28-jit-agent-just-in-time-harness/jit_training_pipeline_frontier.png)

**Stage I — 생성(Adaptivity).** 교사 모델이 ReAct, Plan-and-Execute 같은 시드 뱅크를 보고 태스크에 맞게 하네스를 다시 짭니다. 이 데이터로 SFT + 선호 학습을 돌립니다. <span style="background-color: #fff59d"><strong>성능이 오르면서 비용을 희생하지 않는 하네스를 선호</strong></span>하도록 가중치를 줍니다.

**Stage II — 수리(Reliability).** 생성한 코드는 인터페이스 불일치, 런타임 예외로 깨집니다. <span style="background-color: #fff59d"><strong>컴파일 에러와 스택 트레이스 같은 진단 리포트를 입력으로 넣고 로컬 패치를 생성</strong></span>하도록 훈련합니다. 개발자가 디버깅하듯 실행 가능해질 때까지 고칩니다.

**Stage III — 진화(Evolvability).** Evo-GDPO라는 방식으로, 후보 하네스 그룹을 병렬 실행하고 보상(성과 R_rew, 지연 R_lat, 비용 R_cost)으로 하네스 뱅크 B_n을 갱신합니다. <span style="background-color: #fff59d"><strong>테스트 타임에도 하네스 생성 전략이 계속 좋아지는 구조</strong></span>입니다.

## 벤치마크 결과

![](/images/2026-08-28-jit-agent-just-in-time-harness/four_benchmark_leaderboard.png)

![](/images/2026-08-28-jit-agent-just-in-time-harness/advanced_harness_cost_performance_dsqa_agentif.png)

DeepSearchQA, OfficeBench 등 4개 벤치마크에서 <span style="background-color: #fff59d"><strong>JIT-Agent + GLM-5.2, JIT-Agent + DeepSeek-V4-Flash 조합이 상위권</strong></span>에 올랐습니다. xBench-DS에서는 표준 ReAct 하네스 대비 <span style="background-color: #fff59d"><strong>토큰 절반 이하로 더 높은 정확도</strong></span>를 냈습니다.

논문은 이 결과를 비용-성능 파레토 프론티어 관점에서 제시합니다. <span style="background-color: #fff59d"><strong>저비용·고성능 영역에 JIT-Agent가 위치</strong></span>한다는 겁니다.

## 태스크별로 생성된 하네스 구조

논문이 흥미로운 이유는 생성된 하네스의 구조를 시각화한 대목입니다. <span style="background-color: #fff59d"><strong>프롬프트 수정 수준을 넘어서 에이전트 로직을 다시 배선합니다</strong></span>.

- Palimpsest: 아티팩트 생산용. 태스크를 의존성 그래프(DAG)로 변환해 병렬 실행
- Trapdoor: 딥 리서치용. <span style="background-color: #fff59d"><strong>경계 있는 재귀 위임으로 개인 메모리를 가진 서브에이전트가 단서를 해결</strong></span>
- Pegboard: 다중 출처 증거 수집용. 후보 × 단서 매트릭스를 만들고 한 행이 채워질 때만 검증 트리거

<span style="background-color: #fff59d"><strong>태스크에 따라 최적 하네스 구조가 달라진다</strong></span>는 것이 논문의 실증 포인트입니다. 여행 계획에는 체크리스트를 통과해야 답을 내놓는 Turnstile, 데이터 분석에는 <span style="background-color: #fff59d"><strong>코드 기반 상태 관리를 우선하는 Abacus</strong></span>가 나왔다고 합니다.

## 내 해석

원문 주장과 제 해석을 나눠서 정리합니다.

원문은 <span style="background-color: #fff59d"><strong>하네스 인텔리전스가 훈련 가능하고 전이 가능하며 복리적으로 쌓이는 능력</strong></span>이라고 말합니다. 벤치마크 숫자는 이 주장을 뒷받침합니다.

제가 주목하는 지점은 다릅니다. <span style="background-color: #fff59d"><strong>Stage II의 진단 기반 수리가 실무에서 가장 먼저 써먹을 수 있는 부분</strong></span>입니다. 하네스 생성 코드가 깨졌을 때 스택 트레이스를 보고 패치하는 훈련 데이터를 만드는 일은 개인도 따라 할 수 있습니다. Stage III의 Evo-GDPO는 보상 설계(성과·지연·비용)가 논문의 숨은 설계 결정이라, 재현하려면 이 가중치를 먼저 고정해야 합니다.

한계도 적습니다. 하네스 뱅크가 커질수록 평가 비용이 함께 커지는 구조라, 오프라인 트레이스 기반 방법(AutoSaddler 계열)과 어느 쪽이 싼지는 아직 비교가 없습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Q. JIT-Agent가 정확히 뭘 생성하나요?**
네 모듈(M, P, A, F)로 구성된 실행 가능한 하네스 코드입니다. 태스크 설명을 입력받아 그 태스크에 맞는 메모리·계획·액션·도구 오케스트레이션 구조를 그 자리에서 만듭니다.

**Q. 기존 AutoSaddler 같은 하네스 최적화와 뭐가 다른가요?**
AutoSaddler는 실행 트레이스에서 오프라인으로 하네스를 고칩니다. JIT-Agent는 태스크가 들어온 시점에 온라인으로 하네스를 생성합니다. 논문은 이 대비를 AOT(Ahead-of-Time) vs JIT로 표현합니다.

**Q. 비용 절감은 어느 정도인가요?**
태스크당 API 비용 평균 36% 감소, xBench-DS에서는 ReAct 대비 토큰 절반 이하입니다. 도구를 더 선택적으로 쓰고 메모리를 더 효과적으로 관리해서라고 논문은 설명합니다.

**Q. 어떤 백본 모델에서 확인됐나요?**
DeepSeek V4, Mimo-V2.5, Qwen3.6, GLM-5.2 등 멀티스케일 모델군에서 일관된 개선을 확인했다고 합니다. 생성된 하네스는 OpenCode, Claude Code 같은 상용 에이전트 런타임과도 성능 경쟁이 됩니다.

## 출처

- 논문: [JIT-Agent: Scaling Harness Intelligence via Just-in-Time Harness Evolution (arXiv 2608.25593)](https://arxiv.org/abs/2608.25593)
- HTML 전문: https://arxiv.org/html/2608.25593v1
- 저자: Guibin Zhang 외 (LV-NUS Lab)
- 인용 핵심: "Code as agent harness" (arXiv 2605.18747), "Externalization in LLM agents" 리뷰
