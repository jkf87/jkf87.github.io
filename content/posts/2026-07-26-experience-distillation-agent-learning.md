---
title: "에이전트가 경험에서 배운다 — Experience Distillation: 환경 샘플 9.6배 적게 쓰면서 ICL 효과를 가중치에 묻어내는 법"
date: 2026-07-26
tags:
  - agent
  - in-context-learning
  - context-distillation
  - reinforcement-learning
  - LLM
  - sample-efficiency
  - harness
  - automation
draft: false
summary: "컨텍스트에서 배운 것을 모델 가중치로 증류하는 Experience Distillation. 추가 환경 상호작용 없이 ICL 이득의 64.8%를 유지하고, GRPO 대비 9.6배 적은 샘플로 동일 성능에 도달한다."
authors:
  - jkf87
---

## 핵심 요약

- **문제**: 에이전트가 in-context learning(ICL)으로 경험에서 배우지만, 컨텍스트가 사라지면 이득도 사라진다. 추가 환경 상호작용 없이 이를 가중치에 내재화할 수 있는가?
- **해결책**: **Experience Distillation** — 수집된 경험만으로 context distillation을 수행. 환경 추가 샘플 불필요.
- **결과**: 749개 소프트웨어 엔지니어링 태스크 + 6개 텍스트 어드벤처 게임에서 ICL 이득의 **≥64.8%** 유지. 직접 SFT는 3.8%만 회복. GRPO 대비 **≥9.6배** 환경 샘플 효율.

---

## 배경: ICL의 달콤한 함정

LLM 에이전트에게 in-context learning은 마법 같다. 과거 시도(trial-and-error)를 컨텍스트에 넣어주면, 모델이 이전 실수를 피하고 더 나은 행동을 한다. 환경과의 상호작용 횟수를 극적으로 줄일 수 있다.

문제는 **컨텍스트가 사라지면 모든 것이 사라진다**는 점이다.

실제 서비스에서 매번 과거 경험을 수천 토큰 컨텍스트에 넣는 것은 비현실적이다. 토큰 비용이 늘어나고, 지연이 커지며, 컨텍스트 윈도우 한계에 부딪힌다.

그래서 자연스러운 질문은: **"추가 환경 상호작용 없이, 컨텍스트에서 배운 것을 가중치에 묻어낼 수 없는가?"**

이 논문은 이 문제를 **Experience Distillation**이라는 이름으로 정의하고, 실현 가능한 구현을 제시한다.

![Figure 1: 환경 샘플 효율성 비교 — ICL + Experience Distillation이 GRPO와 동등하면서 9.6배 적은 샘플 사용](/images/2026-07-26-experience-distillation-agent-learning/fig-1-p6.png)
*Figure 1: ICL + Experience Distillation (ICL+EPD)이 GRPO 대비 환경 샘플을 9.6배 이상 적게 사용하면서 동등한 성능에 도달한다. 가로축은 환경 상호작용 횟수(로그 스케일).*

---

## Experience Distillation: 방법론

### 핵심 아이디어

경험 조건부 교사(experience-conditioned teacher)가 컨텍스트에서 정답 행동을 생성할 수 있다면, 이 교사의 지식을 컨텍스트 없이도再现할 수 있도록 학생 모델을 훈련하자.

구체적 방법은 **branched rollout + single-step distillation**이다:

1. **수집된 경험**에서 임의의 중간 시점을 샘플링
2. 교사 모델(경험 있음)이 다음 행동을 생성
3. 학생 모델(경험 없음)이 교사의 행동 분포를 모방하도록 훈련
4. 이때 환경과의 **추가 상호작용은 전혀 필요 없음** — 수집된 궤적만으로 훈련 완료

### 왜 단순 SFT는 실패하는가

경험을 포함한 궤적 전체를 그대로 다음 토큰 예측(NTP)으로 학습하면 — 즉 직접 SFT — **이득의 3.8%만 회복**된다.

이유는 경험 궤적에 실패한 시도, 잘못된 행동, 비효율적 탐색이 모두 포함되어 있기 때문이다. 이를 무분별하게 모방하면 모델이 실수까지 학습해버린다.

반면 Experience Distillation은 교사가 **경험을 보고 정정한 행동**만 증류하므로, 실패를 반복하지 않는다.

### 순방향 KL의 선택

이 논문은 역방향 KL(RKL)이 아닌 **순방향 KL(FKL)**을 사용한다. FKL이 mode-covering 성질 때문에 교사의 다양한 정답 행동을 더 잘 포함한다. 샘플링된 토큰에 대한 NTP보다, 교사의 완전 분포에 대한 KL이 더 안정적인 결과를 낸다.

![Table 6: 샘플링 토큰 NTP vs 전체 분포 KL 비교](/images/2026-07-26-experience-distillation-agent-learning/table-6-p9.png)
*Table 6: 전체 분포 KL이 샘플링 토큰 NTP보다 일관되게 더 높은 성능을 보인다. 특히 소규모 데이터에서 차이가 크다.*

---

## 실험 결과

### 1. 소프트웨어 엔지니어링 (749 SWE 태스크)

749개의 큐레이션된 SWE 태스크에서 Experience Distillation은 ICL 이득의 **64.8% 이상**을 유지한다. 직접 SFT(3.8%)와 비교하면 압도적 차이.

![Table 4: 다중 태스크 Experience Distillation의 일반화 결과](/images/2026-07-26-experience-distillation-agent-learning/table-4-p8.png)
*Table 4: 다중 태스크 Experience Distillation(EPD)이 교차 리포지토리(cross-repo) 및 리포지토리 내(within-repo) 일반화에서 모두 유의미한 개선을 보인다.*

### 2. 텍스트 어드벤처 게임 (TaleSuite, 6 태스크)

6개의 TaleSuite 태스크에서도 동일한 패턴. ICL로 수집한 경험을 Experience Distillation에 통과시키자, 컨텍스트 없이도 ICL 효과의 대부분을 유지한다.

![Figure 2: TaleSuite 6 태스크에서 연속 Experience Distillation](/images/2026-07-26-experience-distillation-agent-learning/fig-2-p8.png)
*Figure 2: Continual Experience Distillation — 각 사이클마다 경험을 수집하고 증류를 반복할수록 성능이 개선된다.*

### 3. GRPO 대비 샘플 효율

GRPO(강화학습 베이스라인)와 비교했을 때, ICL → Experience Distillation 파이프라인은 **≥9.6배 적은 환경 샘플**로 동등한 성능에 도달한다.

이는 실제 환경 상호작용이 비싼 경우(예: 인간 피드백 필요, 장시간 실험) 결정적인 이점이다.

![Figure 3: 교사 생성 데이터 스케일링 곡선](/images/2026-07-26-experience-distillation-agent-learning/fig-3-p10.png)
*Figure 3: 교사가 생성하는 증류 데이터 양이 늘어날수록 성능이 향상되지만, 소규모 데이터에서도 이미 강력한 베이스라인을 능가한다.*

### 4. 하이퍼파라미터 민감도

학습률과 훈련 기간에 대한 민감도 분석에서, Experience Distillation은 비교적 넓은 범위에서 안정적이다. 극단적 학습률에서만 성능 저하가 관찰된다.

![Figure 4: 학습률과 훈련 기간에 따른 영향](/images/2026-07-26-experience-distillation-agent-learning/fig-4-p17.png)
*Figure 4: 학습률과 훈련 스텝 수에 따른 Experience Distillation 성능. 적절한 범위에서 안정적으로 작동한다.*

### 5. GRPO 학습 궤적

GRPO 베이스라인의 전체 학습 곡선을 통해, 강화학습이 수렴하는 데 필요한 막대한 환경 샘플 수를 시각적으로 확인할 수 있다.

![Figure 5: GRPO 학습 곡선](/images/2026-07-26-experience-distillation-agent-learning/fig-5-p23.png)
*Figure 5: 6개 TaleSuite 태스크에서 GRPO 학습 곡선. 수백만 환경 스텝이 필요하다.*

---

## 왜 중요한가

### 에이전트 훈련의 실용적 병목

실제 에이전트 시스템에서 환경 상호작용 비용은 무시할 수 없다. 소프트웨어 엔지니어링 에이전트라면 코드를 실행하고 테스트를 돌려야 한다. 로봇이라면 물리적 행동이 필요하다. 인간 피드백이 필요한 태스크라면 더욱 비싸다.

Experience Distillation은 **이미 수집된 경험**만으로 훈련을 수행하므로, 추가 환경 비용을 0으로 만든다. 이는 에이전트 자가개선 루프의 실용성을 크게 높인다.

### 하네스와의 관계

에이전트 하네스 관점에서 Experience Distillation은 흥미한 위치에 있다. 하네스가 ICL을 통해 에이전트 성능을 끌어올린 후, 그 이득을 모델 가중치로 영구 이전하는 메커니즘이기 때문이다.

이는 "하네스 개선 → 모델 개선"의 단방향 파이프라인을 만들 수 있음을 시사한다. 하네스에서 발견한 휴리스틱, 도구 사용 패턴, 탐색 전략을 경험으로 수집하고, 이를 증류하여 모델 자체를 개선하는 것.

### Context Distillation의 에이전트 확장

기존 context distillation 연구는 주로 지시사항(instruction)이나 프롬프트 엔지니어링 결과를 가중치로 옮기는 데 집중했다. Experience Distillation은 이를 **에이전트의 상호작환 경험**으로 확장한다. 궤적(trajectory)이라는 훨씬 더 길고 복잡한 시퀀스를 증류 대상으로 다루는 것이다.

---

## 한계와 과제

- **교사 모델 의존성**: 경험 조건부 교사가 정확해야 한다. 교사가 경험을 제대로 활용하지 못하면 증류 품질도 떨어진다.
- **태스크 일반화**: 다중 태스크 설정에서 일반화가 확인되었지만, 더 넓은 도메인에서의 검증이 필요하다.
- **지속적 학습**: Continual Experience Distillation(그림 2)이 가능함을 보였지만, catastrophic forgetting 리스크는 여전하다.
- **분포 시프트**: 수집 시점과 증류 시점 사이에 환경이 변하면, 경험의 유효성이 떨어질 수 있다.

---

## 더 실습해보고 싶은 분들께

에이전트 경험 증류, 컨텍스트 증류, 자가개선 루프를 직접 실험하고 싶다면 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 루프와 컨텍스트 엔지니어링을 실습하며 체감할 수 있다.
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 자가개선 루프의 설계와 운영을 체계적으로 배울 수 있다.

---

## 참고문헌

- Gou, C., Tu, H., Fang, Y., Cai, J., & Rezatofighi, H. (2026). Sample-Efficient Learning from Agent Experience. arXiv:2607.21051.
- Janner, M. et al. (2019). When to Trust Your Model: Model-Based Policy Optimization. NeurIPS.
- Hübotter, J. et al. (2026). Reinforcement Learning via Self-Distillation. arXiv:2601.20802.

*이 포스트는 arXiv:2607.21051의 내용을 기반으로 작성되었습니다. 논문의 그림과 표는 학술 목적으로 인용되었습니다.*
