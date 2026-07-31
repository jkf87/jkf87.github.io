---
title: "SkillRise: 에이전트가 경험에서 스킬을 뽑아 다음 태스크에 쓴다 — 단일 정책으로 cross-task 스킬 진화"
slug: skillrise-agentic-rl-cross-task-skill-evolution-2026-07-31
date: 2026-07-31
tags: [agent, reinforcement-learning, skill-learning, LLM, agentic-RL, cross-task]
source: huggingface
source_url: https://huggingface.co/papers/2607.26784
paper_url: https://arxiv.org/abs/2607.26784
github_url: https://github.com/Within-yao/SkillRise
authors:
  - Zhiyuan Yao
  - Yuxin Chen
  - Zhengxi Lu
  - Zishan Xu
  - Yueqing Sun
  - Yifu Guo
  - Yuquan Lu
  - Zhengzhou Cai
  - Kangning Zhang
  - Zhuowen Han
  - Zi-Han Wang
  - Ziang Ye
  - Qi Gu
  - Xunliang Cai
  - Weiwen Liu
  - Yongliang Shen
affiliations:
  - Zhejiang University
  - National University of Singapore
  - Shanghai Jiao Tong University
  - Meituan
description: "LLM 에이전트가 태스크를 풀면서 스킬 문서를 스스로 큐레이팅하고, 다음 관련 태스크에 재사용하는 통합 RL 프레임워크 SkillRise를 분석한다. 단일 정책으로 task solving과 skill curation을 번갈아 수행하며, decoupled credit assignment로 각 역할을 분리해서 학습한다."
---

> **Paper**: [SkillRise: Agentic Reinforcement Learning for Cross-Task Skill Evolution](https://arxiv.org/abs/2607.26784) (arXiv:2607.26784, 2026년 7월)
> **Code**: [github.com/Within-yao/SkillRise](https://github.com/Within-yao/SkillRise)
> **Authors**: Zhiyuan Yao, Yuxin Chen, Zhengxi Lu et al. (절강대학교, NUS, 상해교통대학, 메이퇀)

---

## 핵심 한 줄

**SkillRise는 단일 정책(하나의 LLM)으로 "태스크 풀기"와 "스킬 문서 수정하기"를 번갈아 수행하면서, 관련된 태스크들이 순서대로 주어질 때 점점 더 능력이 올라가는(end-to-end) 강화학습 프레임워크다.** ALFWorld·WebShop·ScienceWorld 세 벤치마크에서 일관되게 최고 성능을 기록했고, 테스트 시점에도 관련 태스크가 길어질수록 성능이 올라가는 cross-task test-time scaling 현상을 보였다.

---

## 왜 필요한가: 기존 agentic RL의 근본 한계

현재 LLM 에이전트 강화학습은 대부분 **각 태스크를 독립적인 에피소드**로 다룬다. 태스크 A를 풀고 얻은 경험이 태스크 B에 전달되지 않는다. 매번 0부터 탐색하는 셈이다.

스킬 학습(skill learning) 연구는 크게 두 방향이 있었다:

1. **같은 태스크 반복 시도**: Reflexion, LaMer처럼 하나의 태스크를 여러 번 풀면서 reflection을 축적. 하지만 여기서 얻은 지식은 해당 인스턴스에 국한되기 쉽고, 다른 태스크로의 전이가 보장되지 않는다.
2. **외부 스킬 뱅크 파이프라인**: 스킬을 추출하고 저장하고 검색하고 실행하는 다단계 파이프라인(ex. RetroAgent, SkillRL). 하지만 추출·검색·실행이 얽혀 있어서 "스킬 자체의 품질"을 평가하기 어렵고, 런타임 오버헤드도 크다.

SkillRise는 이 두 한계를 **하나의 정책으로 end-to-end** 해결한다.

![SkillRise 프레임워크 개요. (a) 관련 태스크를 난이도 순으로 정렬하고, (b) 단일 정책이 태스크 풀기와 스킬 문서 큐레이팅을 번갈아 수행하며, (c) 각 역할에 대해 분리된 크레딧을 할당한다.](/images/skillrise-agentic-rl-cross-task-skill-evolution-2026-07-31/fig-1-p3.png)

---

## 방법: SkillRise의 세 가지 설계 축

### 1. Cross-Task Sequence Construction (관련 태스크 순서 만들기)

SkillRise는 먼저 **같은 태스크 패밀리**에 속하는 서로 다른 인스턴스들을 모으고, 난이도 순으로 정렬한다.

예를 들어 WebShop에서는 같은 제품 카테고리(예: 전자제품) 안에서 서로 다른 구매 요청을 모으고, 요구되는 속성(attribute)과 옵션(option)의 개수가 적은 것부터 많은 것 순으로 배치한다. ALFWorld에서는 같은 태스크 유형(Pick, Clean, Heat 등) 안에서 다양한 인스턴스를 난이도순으로 정렬한다.

이렇게 하면 앞의 쉬운 태스크에서 얻은 경험이 뒤의 어려운 태스크에 도움이 된다. **태스크 패밀리 메타데이터가 필요하다는 점이 현재 버전의 제약사항**이다.

### 2. Cross-Task Rollout with Skill Evolution (스킬 문서를 매개로 한 순차 롤아웃)

핵심 아이디어: **하나의 텍스트 문서(Skill Document)가 태스크 사이의 유일한 정보 채널이다.**

i번째 태스크를 풀 때:
- 정책은 직전까지 축적된 스킬 문서 $S_{i-1}$를 컨텍스트에 넣고 태스크를 수행한다.
- 태스크가 끝나면, 같은 정책이 **역할 전환**하여 트라젝토리 $\tau_i$와 결과 $r_i$를 바탕으로 스킬 문서를 수정한다.
- 수정된 $S_i$만 다음 태스크로 전달된다. 이전 트라젝토리는 넘어가지 않는다.

이때 task solving 프롬프트와 skill curation 프롬프트는 다르지만, **정책 파라미터는 공유**된다. 같은 LLM이 두 역할을 모두 수행하는 것이다.

스킬 문서는 완전히 재작성된다 — 쓸모있는 스킬은 보존하고, 새 트라젝토리에서 드러난 성공 절차나 실패 패턴을 통합하며, 인스턴스 특정 디테일은 제거한다. 컨텍스트 윈도우를 아끼면서도 일반적인 스킬만 남기는 구조다.

### 3. Decoupled Credit Assignment (역할별 크레딋 분리)

가장 중요한 설계 결정 중 하나. task solving과 skill curation은 **시간적 역할이 다르다**:

- **Task solving**: 현재 태스크의 보상 $r_i$로 평가
- **Skill curation**: 이후 태스크들의 할인된 보상 합 $\sum_{j=i+1}^{K} \gamma^{j-i} r_j$로 평가

왜 분리해야 할까? curation 단계에서 만든 스킬 문서는 현재 태스크의 성공/실패에 영향을 주지 않는다 (이미 끝났으므로). 오직 **다음 태스크들에만** 영향을 미친다. 따라서 현재 태스크 보상으로 curation을 평가하면 잘못된 신호가 된다.

그룹 비교(group-relative advantage)도 같은 원칙을 따른다: 같은 시퀀스 위치(position $i$)와 같은 역할(solve/curate)을 가진 N개의 독립 트라이얼끼리만 비교한다. solve 단계의 성과를 curate 단계의 베이스라인으로 쓰지 않는다.

![학습 역학. ALFWorld에서 훈련 보상(%)의 변화를 보여준다. 얇은 선은 개별 시드, 굵은 선은 평균이다.](/images/skillrise-agentic-rl-cross-task-skill-evolution-2026-07-31/fig-3-p8.png)

---

## 실험 결과: 세 벤치마크에서 일관된 최고 성능

### Pass@1 (한 번 시도한 성공률)

| 벤치마크 | SkillRise | 최강 baseline (GiGPO) | 개선 |
|---|---|---|---|
| ALFWorld | **85.9%** | 83.6% | +2.3pp |
| WebShop | **84.4%** | 77.3% | +7.1pp |
| ScienceWorld | **54.6%** | 46.1% | +8.5pp |

ScienceWorld에서 가장 큰 개선(+8.5pp)이 인상적이다. ScienceWorld는 과학 실험을 통한 추론이 필요한 가장 어려운 벤치마크인데, 여기서 스킬 전이 효과가 가장 크게 나타난다.

모델은 Qwen3-4B를 사용했고, 8×NVIDIA H800 GPU로 훈련했다. 시퀀스당 3개 태스크, 8개 독립 트라이얼, 감가율 γ=0.6.

### Within-Task Generalization (같은 태스크 반복 적응)

SkillRise는 **서로 다른 태스크의 시퀀스**로 훈련했지만, 같은 태스크를 반복 시도할 때도 잘 작동한다. Pass@2, Pass@3에서도 모든 벤치마크에서 최고 성능을 기록했다.

![Pass@1/2/3 성공률. SkillRise는 세 벤치마크 모두에서 Pass@2와 Pass@3 최고 성능을 달성했다.](/images/skillrise-agentic-rl-cross-task-skill-evolution-2026-07-31/table-2-p6.png)

이건 중요한 발견이다 — cross-task로 배운 큐레이션 정책이 within-task 적응에도 일반화된다는 것은, 학습된 것이 특정 태스크의 요령이 아니라 **"경험에서 일반적 스킬을 추출하는 메타 능력"** 그 자체라는 증거다.

### Cross-Task Test-Time Scaling (테스트 시점 스케일링)

가장 흥미로운 결과. 테스트 시점에 관련 태스크의 시퀀스 길이가 길어질수록(더 많은 관련 태스크를 순서대로 풀수록) 성능이 올라간다. 각 태스크를 한 번씩만 시도해도 말이다.

경쟁 모델들은 이 추세를 보이지 않는다. 이건 SkillRise가 단순히 같은 태스크를 반복 샘플링해서 좋아지는 것이 아니라, **진짜로 이전 태스크에서 배운 스킬을 재사용**한다는 뜻이다.

태스크가 많아질수록 스킬 문서가 정제되고, 그 정제된 문서가 다음 태스크의 성공률을 높이는 선순환이 만들어지는 것이다.

### 효율성: 다단계 파이프라인 대비 압도적 런타임

![스킬 학습 파이프라인 비교. 왼쪽은 평균 성공률, 오른쪽은 실행 시간. SkillRise는 RetroAgent 및 SkillRL과 동등한 성능을 유지하면서 런타임을 크게 줄인다.](/images/skillrise-agentic-rl-cross-task-skill-evolution-2026-07-31/fig-4-p8.png)

ALFWorld에서 SkillRise의 평균 성공률은 85.9%로 RetroAgent와 동등하고, SkillRL보다 12.5pp 높다. 그런데 GPU 시간 기준으로:

- **RetroAgent**: SkillRise 대비 **6.0×** 실행 시간
- **SkillRL**: SkillRise 대비 **4.3×** 실행 시간

다단계 파이프라인(추출→저장→검색→실행)이 필요 없기 때문에 극적으로 효율적이다.

---

## 분석: 왜 작동하는가

SkillRise가 작동하는 이유를 세 가지 차원에서 분석할 수 있다.

**첫째, 스킬 문서가 "유일한 정보 채널"이라는 설계.** 이전 트라젝토리를 통째로 넘기지 않고, 정제된 문서만 넘긴다. 이건 컨텍스트 윈도우 절약뿐 아니라, 정책이 "뭘 넘길지" 자체를 학습하게 만든다. 쓸데없는 디테일을 버리고 일반적 패턴만 남기는 능력을 RL로 직접 최적화하는 셈이다.

**둘째, decoupled credit assignment의 역할 분리.** curation 단계를 현재 태스크 보상이 아닌 "미래 태스크들의 할인된 보상"으로 평가한다. 이건 정책에게 "지금 당장의 성공이 아니라, 다음 태스크에서 도움이 되는 스킬을 만들어라"라고 지시하는 것과 같다. 이 신호가 없으면 curation은 단순히 현재 트라젉토리를 요약하는 데 그칠 수 있다.

**셋째, 점진적 난이도의 효과.** 쉬운 태스크에서 어려운 태스크로 가는 커리큘럼 구조가 스킬 축적에 유리하다. 첫 태스크에서 기본 루틴을 익히고, 이후 태스크에서 변형을 다루는 식이다. 이건 curriculum learning의 고전적 통찰과 일치한다.

---

## 한계와 향후 방향

논문이 인정하는 한계:

1. **태스크 패밀리 메타데이터 필요**: 시퀀스를 만들기 위해 "이 태스크들은 관련이 있다"는 정보가 미리 있어야 한다. 실제 환경에서는 이 메타데이터가 항상 available하지 않다. 자동으로 관련성을 발견하는 것은 future work.
2. **모델 크기 제한**: 4B 파라미터까지만 실험. 더 큰 모델에서 어떻게 작동하는지 미확인.
3. **세 개의 텍스트 기반 벤치마크만**: ALFWorld, WebShop, ScienceWorld는 모두 텍스트 인터페이스 기반이다. 멀티모달 환경이나 보상 검증이 어려운 실무 태스크에서의 검증이 필요하다.

---

## 더 실습해보고 싶은 분들께

LLM 에이전트가 자기 경험에서 스킬을 추출하고, 그 스킬을 다음 태스크에 재사용하면서 점점 더 능력이 올라가는 것 — 이게 SkillRise의 핵심 아이디어다. 이런 "에이전트가 스스로 개선되는 루프"를 직접 만들어보고 싶다면, 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 자동화의 다양한 활용 패턴을 실습 중심으로 다룬다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 자기 개선 메커니즘을 체계적으로 배울 수 있다.

---

## 정리

SkillRise는 LLM 에이전트에게 "경험을 축적하고 재사용하는 능력"을 end-to-end RL로 가르치는 프레임워크다. 핵심 통찰은 세 가지다:

1. **단일 정책**으로 task solving과 skill curation을 번갈아 수행한다 — 외부 파이프라인 불필요.
2. **Decoupled credit assignment**로 curation은 "미래 태스크 성공"으로 평가한다 — 정확한 학습 신호.
3. 관련 태스크가 길어질수록 성능이 올라가는 **cross-task test-time scaling**이 자연스럽게 발생한다.

4B 모델로 ALFWorld 85.9%, WebShop 84.4%, ScienceWorld 54.6%를 달성하면서도 다단계 파이프라인 대비 4-6배 빠르다. "에이전트가 경험에서 배운다"는 목표를 향해 매우 실용적인 접근을 제시한 논문이다.
