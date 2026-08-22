---
title: "롱호라이즌 에이전트 파인튜닝, RL 대신 진화 전략 — Agentic ESOpt"
date: 2026-08-22
tags: [agent, LLM, RL, evolution-strategies, fine-tuning, long-horizon]
draft: false
---

에이전트 RL 파인튜닝은 잘 돌아가는 것 같으면서도 두 가지 벽에 부딪힙니다. 역전파 트레이닝 스택 때문에 큰 모델을 풀파라미터로 못 돌린다는 것, 그리고 롱호라이즌 트레이토리에서 크레딧 어사인먼트가 터무니없이 어렵다는 것. NUS와 SUSTech, 옥스포드 팀이 낸 Agentic ESOpt(arXiv:2608.17310)는 이 지점에서 RL 대신 진화 전략(ES)을 쓰자는 논문입니다.

## 핵심 결론

<span style="background-color: #fff59d"><strong>풀파라미터 ES 파인튜닝은 추론 수준의 GPU 메모리(8.41GB)로 가능하고, 호라이즌이 길어질수록 RL 대비 우위가 커진다</strong></span>는 것이 논문의 주장입니다.

## 롱호라이즌에서 에이전트 RL이 만나는 두 개의 벽

에이전트 RL(PPO, GRPO)은 트레이토리 전체를 저장해 두고 역전파를 합니다. 활성값, 옵티마이저 상태까지 들고 있어야 하니 4B 모델 기준 GRPO가 58.88GB를 씁니다.

문제는 메모리만이 아닙니다. 터미널 리워드 하나를 수십 턴에 걸쳐 개별 액션에 다시 배분하는 크레딧 어사인먼트가 길어질수록 어려워집니다. 논문의 스케일링 분석에 따르면 정책그래디언트 추정량의 분산은 호라이즌 H에 대해 거의 선형적으로 증가합니다. 길어진 트레이토리에서는 같은 스칼라 결과값이 턴 수만큼 쌓인 스코어 항을 구분해야 하니, 신호가 묻히게 됩니다.

![](/images/2026-08-22-agentic-esopt-long-horizon-evolution/fig-1-p1.png)
*Figure 1. 롱호라이즌 에이전트 추론의 난제와 에이전트 RL의 병목, 그리고 Agentic ESOpt의 대응. (arXiv:2608.17310 Figure 1)*

## Agentic ESOpt는 이렇게 돌아갑니다

방식 자체는 단순합니다.

1. 현재 파라미터 θ 주변에 가우시안 퍼터베이션 G개를 샘플링합니다.
2. 퍼터베이션을 입은 에이전트들을 환경에 굴려 스칼라 리워드를 받습니다.
3. 리워드를 집단 내 z-스코어로 정규화해 가중 파라미터 업데이트를 합니다.

역전파가 없으니 노이즈 시드만 저장해서 in-place 덧셈뺄셈으로 처리하면 됩니다. <span style="background-color: #fff59d"><strong>메모리 요구량이 추론과 동일한 수준</strong></span>이라는 게 핵심입니다. 여기에 <span style="background-color: #fff59d"><strong>퍼터베이션 스케일 σ의 코사인 감쇠</strong></span>를 얹습니다. 초반에는 큰 σ로 넓게 탐색하고(날카로운 로컬 옵티마를 피하는 정규화 효과), 후반에는 작은 σ로 정밀하게 수렴시킵니다. 실험에서 σ 감쇠를 빼면 성능이 떨어지고, 종단 σ를 0으로 두면 오히려 과적합됩니다.

![](/images/2026-08-22-agentic-esopt-long-horizon-evolution/fig-2-p4.png)
*Figure 2. 퍼터베이션 샘플링부터 리워드 가중 업데이트까지의 상세 워크플로우와 프롬프트-파라미터 공진화 구조. (arXiv:2608.17310 Figure 2)*

가장 흥미로운 부분은 유연성입니다. ES의 블랙박스 피드백 인터페이스는 같은 트레이토리 데이터를 프롬프트 스페이스 최적화(스킬 증류, 테스트타임 컴퓨트)와 공유할 수 있습니다. <span style="background-color: #fff59d"><strong>파라미터 업데이트와 프롬프트 업데이트를 같은 루프 안에서 교대로 돌리는 프롬프트-파라미터 공진화</strong></span>가 가능해집니다.

## 실험 숫자

### 컨트롤드 롱호라이즌: 스도쿠

최소 성공 호라이즌 H*를 5, 10, 15로 통제한 멀티턴 스도쿠 환경입니다.

![](/images/2026-08-22-agentic-esopt-long-horizon-evolution/fig-3-p6.png)
*Figure 3. H*별 최종 성공률과 평가 곡선. (arXiv:2608.17310 Figure 3)*

| H* | PPO | GRPO-B | Agentic ESOpt |
|---|---|---|---|
| 5 | 90.63 | 85.42 | 89.58 |
| 10 | 56.25 | 67.71 | 62.50 |
| 15 | 0.00 | 40.63 | 53.13 |

<span style="background-color: #fff59d"><strong>H*=15에서 PPO는 0%로 붕괴하고, Agentic ESOpt는 GRPO 대비 +12.5점으로 역전</strong></span>합니다. H*=5에서는 PPO가, H*=10에서는 GRPO가 이기는데, 이 순서 역전이 단순한 전체 승리보다 정보량이 많습니다. 최적화 전반의 우열이 아니라 <span style="background-color: #fff59d"><strong>호라이즌 길이에 따른 우위 체제 변화</strong></span>라는 해석이 가능합니다.

메모리 비교도 극적입니다. Qwen3.5-4B 기준 PPO가 89.40GB, GRPO가 58.88GB를 쓰는 자리에서 Agentic ESOpt는 <span style="background-color: #fff59d"><strong>8.41GB</strong></span>만 씁니다.

![](/images/2026-08-22-agentic-esopt-long-horizon-evolution/table-1-p6.png)
*Table 1. H*별 성공률과 GPU 메모리 요구량. (arXiv:2608.17310 Table 1)*

### 컴퓨트와 시간

G=32로 GRPO 8롤아웃보다 많이 평가하는데도, 레퍼런스 모델 평가와 역전파를 생략한 덕에 모델 FLOPs는 비슷하고 실측 월클록도 더 짧습니다. H*=15에서 GRPO 19.0시간 vs ESOpt 9.4시간.

![](/images/2026-08-22-agentic-esopt-long-horizon-evolution/table-2-p7.png)
*Table 2. 스도쿠 훈련 컴퓨트와 월클록 타임 비교. (arXiv:2608.17310 Table 2)*

### ReAct 도구 사용: Math / DocVQA

Qwen3.5-4B로 ReAct 스타일 파인튜닝을 하면 DAPO Mean@4 +13.8점, AIME 2026 Mean@4 +15.0점, DocVQA 정확도 +12.3점. 세 메트릭 평균으로 <span style="background-color: #fff59d"><strong>베이스 대비 +13.7점, Agentic GRPO 대비 +8.3점</strong></span>입니다. 모든 Pass@4 메트릭에서 매치드 GRPO를 이겼고, Trace2Skill과 조합하면 4B 모델이 27B 노스킬 베이스라인을 넘는 지점도 나옵니다.

### 웹 에이전트: WebArena-Lite

Qwen3.5-27B 풀파라미터 최적화로 <span style="background-color: #fff59d"><strong>29.47%에서 36.16%로 +6.69점</strong></span>. Trace2Skill과 조합하면 33.94%에서 36.36%로 +2.42점 추가 개선입니다.

### 테스트타임 휴리스틱 디자인

테스트타임 세팅 36개 비교에서 <span style="background-color: #fff59d"><strong>28개에서 매치드 베이스라인 개선</strong></span>을 달성했습니다. 온라인 프롬프트-파라미터 공진화가 실제로 작동한다는 증거입니다.

## 내 해석

ES가 단순히 '싼 대안'이라는 프레임은 이제 부정확합니다. <span style="background-color: #fff59d"><strong>호라이즌이 길어지는 에이전트 세팅에서는 ES가 구조적으로 유리한 체제</strong></span>라는 게 이 논문의 실험적 메시지입니다. 터미널 리워드를 턴 단위로 쪼개지 않고 파라미터 변형 하나에 통으로 귀속시키니, H가 길어져도 분산이 선형으로 자라지 않습니다.

실무적으로 눈에 띄는 건 메모리 숫자입니다. 8.41GB면 소비자급 GPU로도 4B 에이전트 풀파라미터 파인튜닝이 열린다는 뜻입니다. 다만 ES는 환경 평가 횟수가 많아진다는 트레이드오프가 있고, 시뮬레이션이 비싼 환경에서는 이득이 줄어들 수 있습니다. 논문도 이 비교를 별도 축으로 해석하라고 명시합니다.

## 한 줄 정리

<span style="background-color: #fff59d"><strong>롱호라이즌 에이전트 파인튜닝에서 RL의 역전파와 크레딧 어사인먼트가 병목이라면, 파라미터 스페이스 ES를 먼저 검토할 단계다</strong></span>.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
