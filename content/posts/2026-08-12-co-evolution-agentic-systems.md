---
title: "Co-Evolution in Agentic Systems: 에이전트 공진화 설문 — 단일 자가진화에서 자기 지향 진화까지"
date: 2026-08-12
tags: [agent, co-evolution, self-evolution, harness, LLM, multi-agent, environment, open-endedness, survey]
source: https://arxiv.org/abs/2608.10299
authors: ["Qing Zong", "Jiayu Liu", "Junhao Shen", "Zecong Tang", "Linsi Wu", "Yangqiu Song"]
affiliations: ["HKUST", "UIUC", "CUHK", "HKU", "Peking University"]
---

Zong et al.(2026)이 에이전트 시스템의 공진화(co-evolution)를 최초로 체계적으로 정리한 설문입니다. 이 논문은 단일 에이전트 자가진화의 한계를 지적하고, 다중 구성 요소가 서로 진화 압력을 주는 공진화를 3단계 틀로 분류합니다.

## 배경: 단일 자가진화의 한계

에이전트 자가진화 연구는 모델 백본, 메모리, 스킬, 하네스 등 개별 구성 요소를 경험과 피드백에서 업데이트하는 방향으로 발전했습니다. 이 접근의 근본적 제약은 외부 환경이 고정되어 있다는 것입니다. 환경이 변하지 않으면 에이전트는 수렴하고, 새로운 학습 신호가 줄어듭니다.

이 논문은 이를 Red Queen 가설(Van Valen, 1973)로 설명합니다. 지속적 진보를 위해서는 일방적 적응이 아닌 상호 적응이 필요하다는 것입니다.

![단일 자가진화와 공진화 비교](/images/2026-08-12-co-evolution-agentic-systems/fig-1-p1-1.png)

## 공식 정의

에이전트 시스템 $S = (A, E)$로 정의됩니다.

- $A = (\{a_1, ..., a_n\}, \Pi)$: 에이전트 집합과 조직 구조
- $a_i = (m_i, h_i)$: 모델 백본과 하네스
- $E$: 환경
- $\Omega$: 진화 메커니즘 ($S^{t+1} = \Omega(S^t, \tau^t)$)

공진화의 조건은 두 개 이상의 요소 $x \neq y$가 서로 진화 압력을 가하며 동시에 변화하는 것입니다.

## 3단계 분류 체계

![공진화 3단계 분류 체계](/images/2026-08-12-co-evolution-agentic-systems/fig-2-p2-1.png)

### Stage 1: 에이전트 간 공진화

고정된 환경 내에서 에이전트 집단 내부의 공진화입니다.

적대적 공진화는 GAN(Goodfellow et al., 2014)에서 출발하여 LLM 안전 분야로 확장되었습니다. ACE-Safety(Li et al., 2025)는 MCTS로 공격을 탐색하고, AdvGRPO(Bullwinkel et al., 2026)는 채널별 밀집 보상으로 GRPO를 안정화하며, MAGIC(Wen et al., 2026)은 멀티턴 게임을 통해 단일 턴에서는 발견할 수 없는 약점을 찾습니다.

협력적 공진화는 MARL(Lowe et al., 2017; Foerster et al., 2018)에서 LLM 에이전트로 확장되었습니다. CoVerRL(Pan et al., 2026)은 라벨 없이 다수결 답에서 검증자를 부트스트랩하고, WaltzRL(Zhang et al., 2025)은 비평이 파트너의 다음 응답을 실제로 개선할 때만 보상을 줍니다. CORAL(Qu et al., 2026)과 GEA(Weng et al., 2026)는 독립 작업공간에서 학습을 공유하는 구조입니다.

조직적 공진화는 역할 분배와 의사소통 구조 자체가 진화하는 것을 다룹니다.

### Stage 2: 에이전트-환경 공진화

$(A^{t+1}, E^{t+1}) = \Omega(A^t, E^t, \tau^t)$로 정의됩니다. 환경이 에이전트와 함께 변화합니다.

작업 공진화에서는 에이전트 능력에 따라 난이도가 조정됩니다. GenEnv(Guo et al., 2025)와 Tool-R0(Acikgoz et al., 2026)가 대표적입니다.

피드백 공진화에서는 보상 함수 자체가 에이전트 궤적에서 학습됩니다. ROSKA(Huang et al., 2025)와 LaRes(Li et al., 2026)가 보상 후보와 정책 변형을 공동 탐색하고, CURE(Wang et al., 2025)는 실행 실패에서 단위 테스트를 진화시킵니다.

상호작용 공간 공진화에서는 환경 코드, 시뮬레이션, 세계 모델이 에이전트와 함께 변합니다. POET(Wang et al., 2019), XLand(Team et al., 2021), WebEvolver(Fang et al., 2025), COMAP(Liu et al., 2026)가 여기에 속합니다.

![공진화 논문 지형](/images/2026-08-12-co-evolution-agentic-systems/fig-3-p4-1.png)

### Stage 3: 메타 공진화

$\Omega^{t+1} = \Gamma^t(S^t, \Omega^t, \tau^t)$로 정의됩니다. 진화 메커니즘 자체가 진화 대상이 됩니다. 다섯 가지 적응 결정(what, when, how, where, how to evaluate)이 시스템에 의해 수정됩니다.

현재 이 단계를 만족하는 연구는 제한적입니다. PromptBreeder(Fernando et al., 2024), Gödel Agent(Yin et al., 2025), SIA(Hebbar et al., 2026)는 진화 메커니즘을 진화 가능하게 만들지만 하위 공진화 시스템이 없습니다. RQGM(Iacob et al., 2026)만이 공진화하는 에이전트-평가자 시스템과 메타 에이전트를 결합하여 정의를 만족합니다.

![공진화 효과의 정량적 증거](/images/2026-08-12-co-evolution-agentic-systems/fig-4-p7-1.png)

## 실험 증거

Figure 4는 기존 논문들의 결과를 집약한 것입니다. Stage 1과 Stage 2에서 대부분 긍정 효과가 관찰되지만, 수렴에 가까워지면 효과가 감소합니다. Stage 3 메타 공진화가 이 병목을 해결할 가능성으로 제시됩니다.

## 과제와 방향

1. 동적 평가: 고정 벤치마크만으로는 공진화의 모든 구성 요소가 개선되는지, 파트너에 과적합되지 않았는지 측정하기 어렵습니다. 역사적 교차 평가, 구성 요소별 절제, 보류된 평가자가 필요합니다.
2. 규모 확장: 현재 연구는 대부분 국소 루프입니다. 에이전트, 하네스, 환경이 동시에 변하는 대규모 시스템은 초기 단계입니다.
3. 안전·거버넌스: 자율 진화가 진행될수록 인간 모니터링이 어렵습니다. 메타 공진화에서는 보존할 행동을 결정하는 기준 자체가 바뀔 수 있습니다.

## 결론

이 설문의 핵심 주장은 미래의 발전이 더 강한 고정 에이전트가 아닌, 공진화를 통해 지속적으로 개선되는 시스템에서 올 것이라는 점입니다. 3단계 틀은 진화 자유도의 확장을 보여주며, 메타 공진화 단계는 아직 초기입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

원문: [Co-Evolution in Agentic Systems: Toward Self-Directed Evolution Beyond Human Design](https://arxiv.org/abs/2608.10299)
