---
title: "ReOPD: 에이전트 훈련을 오프라인으로 바꾸는prefix replay — 멀티턴 증류의 'prefix trap'"
date: 2026-07-26T16:10:00+09:00
draft: false
tags:
  - agent
  - distillation
  - on-policy
  - LLM
  - tool-use
  - harness
  - RL
  - automation
  - loop
  - Microsoft
categories:
  - AI Research
summary: "Microsoft Research의 ReOPD는 멀티턴 에이전트 온폴리시 증류를 오프라인으로 바꾼다. prefix trap이라는 개념으로 학생-교사 분포 정렬 문제를 정의하고, step-decay 샘플링으로 해결한다. 환경과의 상호작용 없이도 OPD 수준의 정확도를 유지하면서 4배 이상 빠르다."
source_url: "https://arxiv.org/abs/2607.04763"
authors:
  - conanssam
---

## 핵심 요약

강화학습(RL)은 LLM 에이전트에게 강력한 추론과 도구 사용 능력을 부여하지만, 희소한 스칼라 보상만으로는 샘플 효율이 떨어진다. 반면 지식 증류(knowledge distillation)는 교사 모델의 밀집한 per-token 감독 신호를 제공하지만, 교사의 궤적에만 의존하면 학생이 자신의 실수에서 회복하는 법을 배우지 못한다.

**On-Policy Distillation(OPD)**는 이 둘의 장점을 결합한다: 학생이 자신의 prefix에서 롤인하고, 교사가 각 스텝의 개선 타겟을 제공한다. 하지만 멀티턴 에이전트 설정에서 OPD는 **매 업데이트마다 학생을 환경에 굴리고 교사를 쿼리**해야 하는 엄청난 비용을 치른다.

Microsoft Research의 **ReOPD(Replayed-Prefix On-Policy Distillation)**는 이 문제를 우아하게 해결한다. 교사가 RL 훈련 중에 이미 수집한 궤적을 **재사용 가능한 prefix pool**로 활용하여, 학생 훈련 시 환경과의 상호작용을 **완전히 제거**한다.

![ReOPD가 온폴리시 증류의 이점을 유지하면서 환경 상호작용을 제거하는 개념도](/images/2026-07-26-reopd-multi-turn-on-policy-distillation/fig-1-p1.png)

> ReOPD는 OPD 수준의 정확도를 유지하거나 향상시키면서, 롤아웃당 **4배 이상 빠르고** 학생 훈련 중 **도구 호출을 zero**로 만든다.

## prefix trap: 멀티턴 증류의 숨겨진 함정

논문의 가장 중요한 이론적 기여는 **prefix trap** 개념이다. 단일 턴 증류에서는 단순히 "학생의 prefix에서 교사 타겟을 제공하면 된다"는 직관이 작동한다. 하지만 멀티턴 설정에서는 이야기가 다르다.

![OPD와 ReOPD의 비교: 위는 온라인 환경, 아래는 오프라인 환경](/images/2026-07-26-reopd-multi-turn-on-policy-distillation/fig-2-p2.png)

prefix를 학생의 것에 가까워지게 만들수록 두 가지 효과가 동시에 발생한다:

1. **학생 relevance는 증가** — 학생이 실제로 방문하는 상태와 일치
2. **교사 reliability는 감소** — 학생이 만든 "틀린" 히스토리에서 교사의 타겟이 불안정해짐

이것이 **양측 분포 이동(two-sided distribution shift)**이다. 학생의 occupancy와 교사의 reliability 사이의 균형이 깨지면, 증류 효과가 오히려 해가 될 수 있다.

논문은 이를 수학적으로 분해한다: 목표 갭(gap)은 정확히 두 항 — 학생 occupancy mismatch와 교사 reliability — 으로 분해된다. 따라서 "완전히 on-policy하게 만들면 좋다"는 직관이 항상 옳은 것은 아니다.

## ReOPD: 신뢰도 인식 prefix 설계

ReOPD의 해법은 놀랍도록 단순하다: **step-decay 샘플링 스케줄**.

- **초기 스텝의 prefix**는 학생과 교사 모두에게 안정적 → 높은 가중치
- **후기 스텝의 prefix**는 분포 이동이 큼 → 낮은 가중치

이는 기하학적 브리지(geometric bridge)로 해석할 수 있다. 학생과 교사의 occupancy 사이를 보간(interpolation)하되, 신뢰도가 높은 영역을 우선시하는 것이다.

![여러 이기종 환경에서 하나의 학생을 훈련시키는 구조](/images/2026-07-26-reopd-multi-turn-on-policy-distillation/fig-3-p3.png)

특히 강력한 점은 **다중 환경 시나리오**에서 빛난다. 수학 추론 환경(Python)과 검색 환경(search)을 동시에 학습시킬 때, OPD는 모든 환경을 동시에 배포해야 하지만 ReOPD는 각 환경의 교사 궤적을 따로 수집해서 하나의 통합 pool로 합치면 끝이다.

## 실험 결과: 정확도 유지 + 비용 대폭 절감

### 수학 추론 환경 (Python tool)

Qwen3-4B-Instruct-2507 학생 / Qwen3-8B 교사 설정에서:

- ReOPD는 OPD와 **동등하거나 더 높은 정확도** 달성
- 교사-학생 격차가 클 때 특히 ReOPD가 유리 (신뢰도 문제가 더 크기 때문)
- 학생 훈련 중 **도구 호출 zero**, 롤아웃당 **4배 이상 빠름**

### 검색 환경 (Search tool)

교사가 학생의 히스토리에서도 비교적 신뢰할 수 있는 설정에서는 ReOPD가 OPD와 거의 동일한 성능을 보인다. 이는 이론적 예측과 정확히 일치한다 — 교사 reliability가 높으면 prefix trap의 영향이 줄어든다.

### 다중 환경 통합 훈련

![step-decay 샘플링이 증류를 개선하는 효과](/images/2026-07-26-reopd-multi-turn-on-policy-distillation/fig-5-p17.png)

하나의 Qwen3-4B 학생을 수학 + 검색 두 환경에서 동시 훈련할 때, ReOPD는 각 환경을 별도로 배포할 필요 없이 통합 pool로 훈련한다. 복잡도가 환경 수에 선형이 아닌 상수로 유지된다.

![다중 환경 통합 훈련에서 ReOPD의 자원 효율성과 성능](/images/2026-07-26-reopd-multi-turn-on-policy-distillation/table-6-p16.png)

## 왜 중요한가

ReOPD의 의미는 단순한 효율성 개선을 넘는다:

1. **에이전트 훈련의 산업화**: 환경 배포가 병목이던 에이전트 증류를 정적 데이터셋 문제로 변환했다. 이는 ML 인프라 설계를 근본적으로 바꾼다.

2. **prefix 분포 설계라는 새로운 문제 정의**: "on-policy vs off-policy"의 이분법을 넘어, prefix 분포를 어떻게 설계하느냐가 핵심 축이 된다.

3. **교사-학생 비대칭의 정형화**: "더 똑똑한 교사가 항상 더 좋은 교사는 아니다"라는 직관을 양측 분포 이동이라는 정밀한 프레임으로 제공한다.

4. **RL 증류 파이프라인 통합**: 교사의 RL 훈련에서 자연스럽게 수집되는 on-policy 롤아웃을 재활용하므로, 추가 데이터 수집 비용이 없다.

![step index가 likelihood-ratio 가중치의 강력한 프록시임을 보여주는 분석](/images/2026-07-26-reopd-multi-turn-on-policy-distillation/fig-4-p10.png)

## 한계와 향후 방향

논문이 인정하는 한계:

- **prefix pool 의존성**: 교사의 RL 훈련에서 수집된 궤적의 품질과 다양성에 의존
- **멀티모달 환경 미검증**: 텍스트 기반 도구 환경(Python, Search)에서만 검증되었으며, 시각적/물리적 환경에서의 효과는 미지수
- **step-decay의 일반성**: 단순한 step-decay 스케줄이 효과적이었지만, 더 복잡한 환경에서는 다른 스케줄이 필요할 수 있음
- **교사 reliability 추정**: 현재는 step index를 프록시로 사용하지만, 직접적인 reliability 추정이 더 정밀할 수 있음

## 더 실습해보고 싶은 분들께

에이전트 증류, 하네스 설계, 루프 엔지니어링에 관심이 있다면 다음 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 직접 다뤄보는 실습 가이드
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 루프 설계와 컨텍스트 엔지니어링의 원리부터 적용까지

ReOPD는 "환경과의 상호작용 없이도 on-policy 증류가 가능하다"는 것을 보였다. 이것이 의미하는 바는 명확하다 — 에이전트 훈련의 병목은 이제 연산이지, 환경 배포가 아니다.

---

**Paper**: [arxiv.org/abs/2607.04763](https://arxiv.org/abs/2607.04763)
**Code**: [github.com/baohaoliao/ReOPD](https://github.com/baohaoliao/ReOPD)
**Project Page**: [baohaoliao.github.io/ReOPD](https://baohaoliao.github.io/ReOPD/)
**Models & Data**: [huggingface.co/baohao/reopd](https://huggingface.co/collections/baohao/reopd)
