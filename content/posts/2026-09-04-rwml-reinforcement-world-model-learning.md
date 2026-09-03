---
title: "RL로 월드 모델을 먼저 학습하면 에이전트 성능이 무료로 오릅니다 — RWML 정리"
date: 2026-09-04
tags:
  - LLM-agent
  - world-model
  - reinforcement-learning
  - GRPO
  - self-supervised
draft: false
description: "RWML 논문 정리. 태스크 성공 리워드 없이 다음 상태 예측만으로 GRPO 학습하면 ALFWorld +19.6pt, 정책 RL과 결합 시 +6.9pt 오르는 self-supervised 월드 모델 학습법을 다룹니다."
---

## 결론 먼저

Microsoft Research와 Dartmouth, Columbia 팀이 낸 RWML(Reinforcement World Model Learning)은 <span style="background-color: #fff59d"><strong>전문가 데이터도, 더 강한 LLM도, 태스크 성공 리워드도 없이</strong></span> 에이전트의 월드 모델을 RL로 학습하는 방법입니다. 핵심은 하나입니다. <span style="background-color: #fff59d"><strong>환경에서 관측한 (상태, 행동, 다음 상태) 트리플릿으로 다음 상태를 예측하게 하고, 임베딩 유사도 기반 이진 리워드로 GRPO 학습</strong></span>하는 거구요.

결과 수치(기준일 2026-09-04, arXiv:2602.05842v2):

| 항목 | ALFWorld (Qwen2.5-7B) | τ² Bench (Qwen3-8B) |
|---|---|---|
| Base (ReACT) | 13.0 | 31.9 |
| RWML 단독 (self-supervised) | 32.6 (+19.6) | 38.8 (+7.9) |
| Policy RL 단독 | 81.0 | 38.0 |
| <span style="background-color: #fff59d"><strong>RWML + Policy RL</strong></span> | <span style="background-color: #fff59d"><strong>87.9 (+6.9)</strong></span> | <span style="background-color: #fff59d"><strong>43.7 (+5.7)</strong></span> |

요약하면:

- <span style="background-color: #fff59d"><strong>성공 리워드 없이도 ALFWorld +19.6pt</strong></span> 상승. 신호는 "다음 상태를 맞췄는가"뿐입니다.
- 정책 RL 앞에 월드 모델 학습을 끼워 넣으면 <span style="background-color: #fff59d"><strong>전문가 데이터 학습과 동등하거나 그 이상</strong></span>의 성과.
- SFT 방식 월드 모델 학습(WM SFT)은 ALFWorld에서 2.8로 붕괴하는데, RWML은 그렇지 않습니다.

논문: [arXiv:2602.05842](https://arxiv.org/abs/2602.05842) (2026-02-05 v1, 2026-02-09 v2). 저자: Baolin Peng 외, Microsoft Research / Dartmouth / Columbia.

## 문제 설정

LLM 에이전트는 언어 과제는 잘하는데, <span style="background-color: #fff59d"><strong>"내가 이 행동을 하면 환경이 어떻게 바뀌는가"를 예측하는 능력</strong></span>이 약합니다. 사전학습 목표(정적 텍스트 next-token prediction)와 에이전트 환경의 요구가 어긋나서 그렇습니다.

기존 해법 두 가지와 각각의 문제:

| 방식 | 필요 것 | 문제 |
|---|---|---|
| 전문가 궤적 SFT | 전문가 데이터 또는 강한 LLM 생성 데이터 | 확장성, 비용 |
| 태스크 성공 리워드 RL | 정확한 성공/실패 신호 | 희소(sparse), 설계 난이도 |

SFT로 다음 상태를 맞추는 WM SFT 접근도 있는데, <span style="background-color: #fff59d"><strong>토큰 수준 충실도가 우선되다 보니 의미적 동치를 놓치고 모델 붕괴로 이어질 수 있다</strong></span>는 게 논문의 진단입니다.

## RWML 방법

학습 데이터는 자기 자신으로 만듭니다. 대상 모델 π_θ로 환경에 N번 롤아웃(ALFWorld N=3, τ² Bench N=6, temperature 1.0)해서 얻은 궤적을 전부 ⟨s≤t, a_t, s_{t+1}⟩ 트리플릿으로 쪼갭니다.

![](/images/2026-09-04-rwml-reinforcement-world-model-learning/fig-2-p3.png)

Figure 2. RWML 개요. 롤아웃 → 트리플릿 변환 → "too easy" 샘플 서브샘플링 → GRPO 학습. 출처: arXiv:2602.05842v2.

리워드 함수는 이진(binary)입니다:

```
r_WM(ŝ, s) = 1.0  if d(ŝ, s) < τ_d
             0.0  otherwise
d(ŝ, s) = 1 - cos(E(ŝ), E(s))
```

E(·)는 기존 임베딩 모델을 그대로 씁니다. <span style="background-color: #fff59d"><strong>예측 다음 상태와 실제 다음 상태의 임베딩 코사인 거리가 임계값 이하면 1점</strong></span>. 이게 리워드 전부입니다.

여기에 두 가지 디테일이 붙습니다.

- **too-easy 필터링**: 별도 SFT 모델(전체의 10%로 학습)이 10회 시도해서 계속 맞추는 샘플은 p=0.1 확률로만 남깁니다. 두 벤치마크 모두 약 30%가 easy로 걸러졌고, 이걸 빼면 성능이 떨어집니다(abl. Table 4).
- **이진 리워드**: 연속값 LLM-as-a-judge보다 <span style="background-color: #fff59d"><strong>해킹(reward hacking)에 더 강함</strong></span>이 실증됐습니다. 논문 부록 D에 판정 모델을 속여 통과하는 사례가 나옵니다.

최적화는 표준 GRPO. 온라인 RL이라서 그런지, 아래 다시 나오지만 forgetting도 적습니다.

## 결과

Table 1 (3회 평균, max step 30):

![](/images/2026-09-04-rwml-reinforcement-world-model-learning/table-1-p5.png)

Table 1. ALFWorld·τ² Bench 성능. 출처: arXiv:2602.05842v2.

읽을 포인트:

- WM SFT 단독은 ALFWorld 2.8로 base(13.0)보다 못합니다. <span style="background-color: #fff59d"><strong>RL 신호와 SFT 신호의 격차가 이만큼 큽니다</strong></span>.
- RWML + Policy RL은 87.9. GPT-5 ReACT(49.3)와도 비교되는 수준입니다.
- τ² Bench는 Retail/Telecom/Airline 세 도메인에서 각각 44.2/45.8/38.3.

Table 2에서는 전문가 데이터/강한 LLM 기반 방법들과 비교합니다:

![](/images/2026-09-04-rwml-reinforcement-world-model-learning/table-2-p5.png)

Table 2. 전문가 데이터 기반 학습법과의 비교. 출처: arXiv:2602.05842v2.

<span style="background-color: #fff59d"><strong>ALFWorld에서는 전문가 주석 방법보다 위, τ² Bench에서는 전체 2위</strong></span>. 외부 감독 없이 이 숫자면 충분히 의미가 있습니다.

## 왜 잘 되는가 — 세 가지 증거

### 1. Forgetting이 적다

Table 3에서 학습 후 MMLU-Redux, IFEval, MATH-500, GSM8k, GPQA-Diamond, LiveCodeBench를 다시 측정했습니다.

![](/images/2026-09-04-rwml-reinforcement-world-model-learning/table-3-p6.png)

Table 3. 학습 후 forgetting 측정. 출처: arXiv:2602.05842v2.

WM SFT 대비 <span style="background-color: #fff59d"><strong>거의 모든 벤치마크에서 성능 하락이 작습니다</strong></span>. 온라인 RL의 on-policy 성질 때문으로 보는 논문 해석이랑 제 판단이 일치합니다.

### 2. 파라미터 업데이트가 작다

레이어별 weight change ratio를 보면 RWML은 WM SFT보다 훨씬 적은 파라미터만 건드립니다. 그리고 <span style="background-color: #fff59d"><strong>이후 Policy RL을 얹을 때 간섭이 적어서 조합이 잘 된다</strong></span>는 게 Figure 3의 핵심입니다. SFT-then-RL이 아니라 RL-then-RL 구조라 안정적이라는 이야기입니다.

### 3. 무효 행동이 줄어든다

명시적으로 학습한 적 없는데 이런 변화가 나옵니다:

| 환경 | 무효/비효율 행동 비율 |
|---|---|
| ALFWorld (형식 오류, 불필요한 look/examine) | 59.30% → 39.45% |
| τ² Bench (없는 툴 이름, 잘못된 인자) | 24.90% → 8.84% |

<span style="background-color: #fff59d"><strong>τ² Bench에서 무효 툴콜이 24.90%에서 8.84%로 약 1/3</strong></span>로 줄었습니다. 환경을 이해하니 행동이 정확해지는 거죠.

## 한계

- <span style="background-color: #fff59d"><strong>약한 베이스 모델은 전이가 안 됩니다</strong></span>. τ² Bench에서 Qwen2.5-7B는 월드 모델 지식을 의사결정으로 옮기지 못했고, Qwen3-8B/30B-A3B는 큰 폭 상승(Figure 4). 최소 이상의 베이스 역량이 전제조건입니다.
- B200 GPU 환경 기준 학습 비용이 있고, τ² Bench 본셋팅(GPT-4.1 유저 시뮬레이터) 평가는 비용 때문에 일부만 했습니다.
- 텍스트 상태 환경 한정입니다. ALFWorld, τ² Bench 둘 다 텍스트 기반이라 시각/물리 환경으로의 확장은 미검증.

## 내 해석

이 논문의 포지션은 "mid-training"입니다. 사전학습과 태스크 RL 사이에 <span style="background-color: #fff59d"><strong>self-supervised로 환경 역학을 주입하는 단계</strong></span>를 하나 끼워 넣는 거고, 리워드 설계가 임베딩 코사인 + 이진화로 끝나서 확장 비용이 낮습니다.

실무적으로 눈에 띄는 지점 두 가지:

- 커스텀 환경에서 에이전트를 돌릴 때 성공 리워드를 정의하기 애매하면, <span style="background-color: #fff59d"><strong>"다음 관측 예측" 신호로 먼저 학습시키는 루트</strong></span>가 현실적인 대안이 됩니다.
- LLM-as-a-judge 리워드를 쓰는 파이프라인이라면 이진화 판정으로 바꾸는 것만으로 reward hacking 리스크를 줄일 수 있다는 증거로 쓸 만합니다.

원문 근거(arXiv:2602.05842v2)와 제 해석을 구분해두었습니다. 수치는 전부 논문 표에서 가져온 값입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**RWML은 어떤 리워드를 쓰나요?**
예측한 다음 상태와 실제 다음 상태를 임베딩 모델로 코사인 비교해서, 거리가 임계값 이하면 1.0, 아니면 0.0을 주는 이진 리워드입니다. 성공/실패 태스크 리워드는 쓰지 않습니다.

**RWML만으로 어느 정도까지 오르나요?**
ALFWorld에서 base 대비 +19.6pt(13.0 → 32.6), τ² Bench에서 +7.9pt(31.9 → 38.8)입니다. 여기에 Policy RL을 얹으면 각각 87.9, 43.7까지 올라갑니다.

**왜 SFT 대신 RL로 월드 모델을 학습하나요?**
SFT는 토큰 수준 충실도를 강요해서 의미적으로 같은 표현을 다르게 쓰면 틀린 것으로 학습되고, ALFWorld에서 성능이 2.8로 붕괴합니다. 임베딩 거리 리워드는 의미적 동치를 허용하고, forgetting과 파라미터 간섭도 적습니다.

**전문가 데이터가 꼭 필요한가요?**
아니요. RWML은 대상 모델 자신의 롤아웃에서 트리플릿을 만들어 self-supervised로 학습합니다. ALFWorld에서는 전문가 데이터 기반 방법보다 높은 성적을 냈습니다.

**어떤 모델에서 효과가 있나요?**
베이스 역량이 일정 이상이어야 합니다. τ² Bench에서 Qwen2.5-7B는 전이에 실패하고 Qwen3-8B, Qwen3-30B-A3B는 유의미한 상승을 보였습니다.
