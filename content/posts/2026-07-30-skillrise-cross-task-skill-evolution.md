---
title: "SkillRise: 에이전트가 서로 다른 작업에서 스킬을 배우기 시작하면 — 크로스태스크 스킬 진화 RL의 등장"
date: 2026-07-30T16:00:00+09:00
draft: false
summary: "RLVR이 같은 작업을 반복하며 성적을 올리는 동안, SkillRise는 '서로 다르지만 관련된 작업' 시퀀스에서 스킬 문서를 진화시키며 범용 대응력을 학습한다. ALFWorld 85.9%, WebShop 84.4%, ScienceWorld 54.6% — 단일 정책으로 task solving과 skill curation을 번갈아 수행하며, 테스트 타임에 작업 시퀀스가 길어질수록 성능이 올라가는 크로스태스크 스케일링 현상을 최초로 입증했다."
tags: ["agent", "RL", "skill-learning", "LLM", "cross-task", "automation", "loop", "tool-use"]
categories: ["LLM Agent", "Reinforcement Learning"]
source_url: "https://arxiv.org/abs/2607.26784"
authors: ["Zhejiang University", "NUS", "SJTU", "Meituan"]
---

> **원논문**: [SkillRise: Agentic Reinforcement Learning for Cross-Task Skill Evolution](https://arxiv.org/abs/2607.26784) (Yao et al., 2026)

---

## 핵심 한 줄

**에이전트 RL이 같은 작업을 반복하는 대신, "관련되지만 서로 다른 작업"의 시퀀스를 풀면서 스킬 문서를 진화시키도록 훈련하면 — 테스트 타임에도 새로운 작업이 주어질수록 더 잘 풀게 된다.**

---

## 1. 문제: 에이전트 RL의 고립 에피소드 문제

현재의 에이전트 강화학습(RL)은 각 작업(task)을 독립적인 에피소드로 취급한다. 에이전트가 ALFWorld에서 물건을 찾고, WebShop에서 상품을 구매하고, ScienceWorld에서 과학 실험을 수행하더라도 — 각 에피소드가 끝나면 경험이 사라진다.

이는 낭비다. 비슷한 작업에는 공통의 해결 패턴(reusable solution pattern)이 존재한다. ALFWorld의 "Pick" 작업에서 배운 "위치를 탐색하고 → 대상을 찾고 → 집어드는" 루틴은 "Clean" 작업이나 "Heat" 작업에서도 재사용될 수 있다. 하지만 표준 agentic RL은 이 관계를 무시한다.

![SkillRise 프레임워크 개요: 관련 작업들을 난이도순으로 정렬하고, 단일 정책이 task solving과 skill curation을 번갈아 수행한다](/images/2026-07-30-skillrise-cross-task-skill-evolution/fig-1-p3.png)
*Figure 1: SkillRise 전체 구조. (a) 관련 작업 인스턴스를 난이도순으로 정렬한다. (b) 공유 정책이 각 작업을 풀고 진화하는 스킬 문서를 큐레이션하며, 이 문서가 다음 작업으로 전달된다. (c) Task solving은 현재 작업 보상으로, skill curation은 후속 작업 보상의 할인합으로 평가한다.*

기존 스킬 학습 접근법도 한계가 있다:

- **같은 작업 반복 (LaMer)**: 같은 인스턴스를 여러 번 시도하며 reflection을 개선하지만, 스킬이 인스턴스 특화에 머물러 다른 작업으로 전이되지 않는다.
- **다단계 파이프라인 (RetroAgent, SkillRL)**: 추출 → 저장 → 검색 → 실행의 파이프라인을 거치지만, 어느 단계에서 실패했는지 귀인하기 어렵고, 외부 teacher 모델(Gemini-2.5-Pro 등)에 의존하며, 런타임 오버헤드가 4~6배에 달한다.

SkillRise의 질문은 단순하다: **"에이전트가 작업을 풀면서 동시에 다음 작업에 쓸 스킬을 정리하도록, 하나의 정책으로 end-to-end 학습할 수 없는가?"**

---

## 2. 핵심 설계: 크로스태스크 시퀀스 + 단일 정책 + 분리 크레딧

### 2.1 크로스태스크 시퀀스 구성

SkillRise는 관련 작업들을 하나의 시퀀스로 묶는다. 예를 들어 WebShop에서 "청바지 2개 속성" → "청바지 3개 속성" → "청바지 4개 속성" 식으로, 같은 제품 카테고리 내에서 요구 속성 수가 증가하도록 정렬한다.

각 시퀀스는 K=3개의 서로 다른 작업 인스턴스로 구성된다. 이들은 같은 작업 패밀리에 속하지만 구체적인 엔티티와 목표가 다르다.

### 2.2 단일 정책의 이중 역할

하나의 정책 π_θ가 시퀀스를 따라 두 가지 역할을 번갈아 수행한다:

1. **Task Solving**: 현재 작업 x_i를 스킬 문서 S_{i-1}와 함께 받아 궤적 τ_i를 생성
2. **Skill Curation**: 작업 완료 후, 궤적과 결과를 바탕으로 스킬 문서를 개정하여 S_i 생성

개정된 문서 S_i만이 다음 작업 x_{i+1}으로 전달된다. 이전 궤적은 넘어가지 않는다. 즉 **스킬 문서가 작업 간 유일한 정보 채널**이다.

### 2.3 분리 크레딧 할당 (Decoupled Credit Assignment)

여기가 핵심 통찰이다. Task solving과 skill curation은 시간적 역할이 다르다:

- **Task solving** → 현재 작업의 결과로 평가: `G_solve = r_i`
- **Skill curation** → 후속 작업들의 할인된 결과로 평가: `G_curate = Σ γ^(j-i) * r_j`

감마(γ)는 0.6을 사용하며, 후속 작업일수록 스킬 문서의 영향이 희미해진다고 가정한다.

그룹 내 상대적 어드밴티지를 계산할 때도, solving과 curation을 분리한다. 같은 역할, 같은 시퀀스 위치의 시도들끼리만 비교하여 베이스라인을 잡는다(role-aware group-relative optimization). 이렇게 하면 "푸는 능력"과 "정리하는 능력"이 서로의 베이스라인을 오염시키지 않는다.

---

## 3. 실험 결과: 3개 벤치마크 전면 석권

### 3.1 메인 결과 (Pass@1)

Qwen3-4B를 백본으로 사용하여 ALFWorld, WebShop, ScienceWorld에서 평가했다.

![Pass@1/2/3 성공률 표: SkillRise가 세 벤치마크 모두에서 최고 성능을 기록](/images/2026-07-30-skillrise-cross-task-skill-evolution/table-2-p6.png)
*Table 2: Pass@1/2/3 성공률. SkillRise는 세 벤치마크 모두에서 최고 성능을 달성했다. Pass@3에서는 ALFWorld 94.6%, WebShop 93.4%, ScienceWorld 75.5%에 도달한다.*

SkillRise는 모든 벤치마크에서 최고 Pass@1을 달성했다:

| 벤치마크 | SkillRise | 최강 베이스라인 (GiGPO) | 개선 |
|---|---|---|---|
| ALFWorld | **85.9%** | 83.6% | +2.3pp |
| WebShop | **84.4%** | 77.3% | +7.1pp |
| ScienceWorld | **54.6%** | 46.1% | +8.5pp |

ScienceWorld에서의 +8.5pp 개선이 특히 인상적이다. ScienceWorld는 가장 다양한 과학 주제(전기회로, 생물, 화학 반응 등)를 다루기 때문에, 크로스태스크 스킬 전이의 효과가 가장 크게 나타나는 것이다.

### 3.2 크로스태스크 테스트 타임 스케일링

**Figure 2 참고**: ALFWorld에서 시퀀스 길이 K가 1→2→3으로 증가할 때 SkillRise의 성공률이 지속적으로 상승한다. 베이스라인(LaMer, GRPO)들은 이런 경향을 보이지 않는다.

이 논문의 가장 흥미로운 발견은 **테스트 타임 크로스태스크 스케일링**이다. 훈련 시 K=3으로 학습했음에도, 테스트 시 시퀀스 길이를 늘리면 성능이 계속 올라간다. 즉 에이전트가 "스킬을 정리하는 방법" 자체를 학습한 것이지, 특정 스킬을 암기한 것이 아니다.

이는 베이스라인들이 전혀 보여주지 않는 패턴이다. 같은 작업을 반복하는 LaMer는 시퀀스가 길어져도 성능이 개선되지 않는다.

### 3.3 파이프라인 효율성 비교

![스킬 학습 파이프라인 비교: SkillRise가 RetroAgent와 동등한 성능을 1/6 시간에 달성](/images/2026-07-30-skillrise-cross-task-skill-evolution/fig-4-p8.png)
*Figure 4: ALFWorld에서 스킬 학습 파이프라인 비교. 왼쪽: 평균 성공률. 오른쪽: SkillRise 기준 상대 런타임. RetroAgent는 6.0×, SkillRL은 4.3×의 시간이 소요된다.*

SkillRise는 RetroAgent와 동등한 85.9% 성공률을 달성하면서도, 런타임은 **1/6**에 불과하다. SkillRL(Gemini-2.5-Pro teacher 사용)보다는 12.5pp 높으면서 4.3배 빠르다. 외부 teacher 모델, 별도 메모리 모듈, 검색 컴포넌트가 전혀 필요 없다.

---

## 4. 분석: 왜 작동하는가?

### 4.1 학습 역학

![ALFWorld 훈련 역학: 감마 민감도와 스킬 큐레이션 효과](/images/2026-07-30-skillrise-cross-task-skill-evolution/fig-3-p8.png)
*Figure 3: ALFWorld 훈련 역학. 왼쪽: 감마(γ)값 {0.3, 0.4, 0.6, 0.7}에 따른 학습 곡선 — 모두 1pp 이내로 수렴하여, 결과가 감감 선택에 강건함을 보인다. 오른쪽: SkillRise vs no-curation vs GRPO 비교. 스킬 큐레이션을 제거하면 약 3pp, task-independent GRPO는 6pp 이상 하락한다.*

감마(γ)값을 0.3에서 0.7까지 변화시켜도 결과는 1pp 이내로 수렴한다. 이는 프레임워크가 미래 작업에 얼마나 가중치를 두는지에 대해 강건하다는 것을 보여준다.

스킬 큐레이션을 제거한 ablation에서는 약 3pp 하락이 발생한다. 단순히 관련 작업을 나열하는 것만으로는 부족하고, 명시적으로 궤적을 스킬 문서로 변환하는 단계가 필요하다.

### 4.2 스킬 문서의 진화

논문의 부록에 제시된 스킬 문서 예시를 보면, 에이전트가 다음과 같은 내용을 자발적으로 정리한다:

- **절차적 지식**: "pick_two_obj 작업에서는 첫 번째 객체를 찾은 후 즉시 집지 말고, 두 번째 객체 위치를 먼저 확인하라"
- **실패 모드**: "냉장고 안에 있는 객체를 찾을 때, 'go to fridge'가 아닌 'go to countertop' 먼저 확인해야 할 때가 있다"
- **일반화된 전략**: "탐색 순서는 작업 지시문의 전치사구 순서를 따르는 것이 효율적이다"

이것이 인스턴스 특화 메모가 아니라, 여러 작업에 걸쳐 수정되고 정제된 **이전 가능한 절차적 지식**이라는 점이 핵심이다.

---

## 5. 의미: 에이전트 학습의 패러다임 전환

SkillRise가 시사하는 바는 명확하다:

**1. 스킬 학습은 파이프라인이 아니라 정책의 일부여야 한다.**
추출, 저장, 검색, 실행을 분리된 모듈로 두면, 각 단계의 오류가 합성되고 귀인이 어려워진다. 단일 정책이 스킬 문서를 직접 편집하고 사용하면, 보상 신호가 명확해진다.

**2. 크로스태스크 시퀀스가 자연스러운 학습 신호를 만든다.**
"같은 작업을 10번 반복"하는 것보다 "관련 3개 작업을 난이도순으로 풀기"가 더 다양한 경험을 제공한다. 후속 작업의 성공 여부가 스킬 품질의 자연스러운 검증이 된다.

**3. 테스트 타임 스케일링은 스킬 품질의 리트머스 시험지다.**
테스트 시 시퀀스가 길어질수록 성능이 올라간다는 것은, 에이전트가 진정한 의미의 "학습하는 방법(learning to learn)"을 습득했음을 의미한다. 이는 단순한 성능 지표를 넘어, 지속적 개선(continual improvement) 가능성을 보여준다.

---

## 6. 한계와 향후 방향

논문이 인정하는 한계:

- **작업 패밀리 메타데이터 필요**: 시퀀스 구성에 환경에서 제공하는 패밀리 정보를 사용한다. 오픈 환경에서 관련 작업을 자동 발견하는 것은 미해결 과제.
- **모델 규모**: 4B 파라미터까지만 실험. 더 큰 모델에서의 효과는 미확인.
- **텍스트 기반 환경 한정**: ALFWorld, WebShop, ScienceWorld는 모두 텍스트 인터페이스. 멀티모달 환경에서의 검증이 필요.

---

## 더 실습해보고 싶은 분들께

에이전트가 자신의 경험을 정리하고 다음 작업에 활용하는 "학습 루프"를 직접 만들어보고 싶다면, 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 실전에서 설계하고 운영하는 방법을 다룹니다. 스킬 문서를 큐레이션하는 에이전트를 구성하는 데 바로 적용할 수 있습니다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — RL 루프와 크레딧 할당의 원리를 실습하며, 크로스태스크 학습 신호를 설계하는 감각을 기를 수 있습니다.

SkillRise의 핵심 아이디어 — "정책이 직접 스킬을 편집하라" — 은 하네스 설계에서도 동일하게 적용됩니다. 에이전트에게 자신의 경험을 되돌아보고 다음을 개선할 도구를 주면, 그것이 곧 학습입니다.

---

> **원논문**: [SkillRise: Agentic Reinforcement Learning for Cross-Task Skill Evolution](https://arxiv.org/abs/2607.26784) — Zhiyuan Yao et al., Zhejiang University / NUS / SJTU / Meituan, 2026
> **코드**: [github.com/Within-yao/SkillRise](https://github.com/Within-yao/SkillRise)
