---
title: "Agentic ESOpt — 그래디언트 버리고 에이전트를 진화시키기"
date: 2026-08-30
draft: false
description: "역전파 없이 파라미터 노이즈만으로 롱호라이즌 LLM 에이전트를 풀파라미터 파인튜닝하는 Agentic ESOpt를 정리했습니다. 학습 메모리 8.41GB, 15턴 과제에서 GRPO 대비 +12.5%p, WebArena-Lite 27B 웹 에이전트 실증까지."
tags: [agent, es, evolution-strategies, fine-tuning, rl, llm]
---

## 결론 먼저

에이전트 학습에서 조용한 쿠데타가 하나 일어났습니다. NUS 연구팀의 Agentic ESOpt는 RL 대신 <span style="background-color: #fff59d"><strong>진화 전략(Evolution Strategies)로 긴 호라이즌 LLM 에이전트를 튜닝</strong></span>하는데, 결과가 예상보다 좋습니다. 학습 GPU 메모리 <span style="background-color: #fff59d"><strong>8.41GB, GRPO의 7분의 1</strong></span>입니다. 성능은 15턴 과제에서 <span style="background-color: #fff59d"><strong>GRPO 대비 +12.50%p</strong></span> 앞섭니다.

| 항목 | 수치 | 비교 |
|---|---|---|
| 학습 GPU 메모리 | 8.41GB | GRPO 58.88GB (-85.7%) |
| 15턴 스도쿠 성공률 | 53.13% | GRPO 40.63% |
| H*=15 학습 시간 | 9.4h | GRPO 19.0h |
| DAPO / AIME 2026 | +13.8 / +15.0%p | 베이스 대비 |
| WebArena-Lite 27B | 29.47→36.16% | No Skill 대비 |
| 테스트타임 AHD | 28/36 개선 | 매칭 베이스 대비 |

기준일 2026-08-30, [arXiv:2608.17310](https://arxiv.org/abs/2608.17310) v2 기준.

## 왜 이런 실험을 했는가

최근 에이전트는 턴이 길어지는 방향으로 진화합니다. 근데 <span style="background-color: #fff59d"><strong>RL은 터미널 리워드를 턴마다 나눠주는 구조</strong></span>라, 턴이 15개만 넘어가도 크레딧 어사인먼트가 무너집니다. 논문은 이걸 수식으로 보이고(부록 C.3), 실험으로 확인합니다.

| 최소 성공 호라이즌 H* | 승자 | 성공률 |
|---|---|---|
| 5 | Agentic PPO | 90.63% |
| 10 | Agentic GRPO | 67.71% |
| 15 | Agentic ESOpt | 53.13% |

짧으면 PPO, 중간이면 GRPO, 길면 ES. <span style="background-color: #fff59d"><strong>이 순위 뒤집힘이 논문의 핵심 증거</strong></span>입니다. 전면승리가 아니라 체제 전환이라는 해석입니다.

![Figure 3](/images/2026-08-30-agentic-esopt-long-horizon-es-finetuning/fig-3-p6.png)

## 어떻게 돌아가나

![Figure 2](/images/2026-08-30-agentic-esopt-long-horizon-es-finetuning/fig-2-p4.png)

파라미터 공간에서 A/B 테스트를 수천 번 돌리는 셈입니다. 노이즈 G개를 뽑고, 각각으로 에이전트를 풀어놓고, 잘한 놈 쪽으로 평균을 밀어붙입니다.

업데이트식은 한 줄: <span style="background-color: #fff59d"><strong>θ ← θ + (α/G)Σ R̂ᵢεᵢ</strong></span>.

메모리가 싼 이유가 재밌습니다. <span style="background-color: #fff59d"><strong>노이즈는 시드만 저장</strong></span>하고, 더했다 뺐다 하니까 옵티마이저 상태가 아예 없습니다. σ는 코사인 감쇠로 초반엔 넓은 탐색, 후반엔 정밀 수렴을 만듭니다. σ를 상수로 두면 60스텝 39.58%에서 멈추고, 감쇠를 넣으면 100스텝 53.13%까지 갑니다.

![Table 1](/images/2026-08-30-agentic-esopt-long-horizon-es-finetuning/table-1-p7.png)

## 실무자가 챙길 것 세 가지

27B 웹 에이전트가 H100 4장에서 풀파라미터로 돌아갑니다.
WebArena-Lite에서 29.47% → 36.16%.

<span style="background-color: #fff59d"><strong>4B를 ES로 튜닝하면 27B 기본 모델과 비슷해집니다.</strong></span> DocVQA ANLS 0.3875 → 0.5043, 27B No Skill이 0.5036. 이건 그냥 돈 문제로 귀결됩니다.

프롬프트 탐색과 같은 루프를 돌 수 있습니다. 스킬 최적화(Trace2Skill), 테스트타임 휴리스틱 탐색(EoH)에 붙여도 <span style="background-color: #fff59d"><strong>36설정 중 28개 개선</strong></span>. frozen 모델 탐색의 한계를 파라미터 적응으로 뚫는다는 게 차별점입니다.

![Table 2](/images/2026-08-30-agentic-esopt-long-horizon-es-finetuning/table-2-p7.png)

![Table 3](/images/2026-08-30-agentic-esopt-long-horizon-es-finetuning/table-3-p8.png)

## 비판도 읽어야 한다

<span style="background-color: #fff59d"><strong>환경 평가가 비싼 도메인에선 롤아웃 많은 ES가 손해</strong></span>일 수 있습니다. σ 튜닝도 새 하이퍼파라미터 부담이고, 지속 학습은 미검증. Qwen3.5 백본 중심이라 일반화도 확인 필요합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**ES가 RL을 완전 대체하나요?**
아닙니다. 짧은 호라이즌(5~10턴)에선 PPO/GRPO가 이깁니다. 긴 호라이즌 체제에서만 ES가 유리합니다.

**LoRA랑 뭐가 다른가요?**
어댑터 방식과 달리 <span style="background-color: #fff59d"><strong>풀파라미터 업데이트인데 메모리는 추론 수준</strong></span>이라는 점이 다릅니다.

**바로 도입 가능한가요?**
σ 튜닝과 환경 비용 검토가 먼저입니다. 27B 웹 에이전트 실증은 이미 있습니다.

**왜 메모리가 추론 수준인가요?**
그래디언트·레퍼런스 모델·옵티마이저 상태가 없고, 노이즈는 시드로 저장합니다.

## 원문 근거와 내 해석 구분

원문 주장(초록, 섹션 4-6): ES의 세 이점 — 모델 확장성, 유연성, 긴 호라이즌 확장성 — 과 스도쿠/수학/DocVQA/WebArena/AHD 실험 근거. 내 해석: <span style="background-color: #fff59d"><strong>4B ES ≈ 27B 기본 구간이 실무적으로 가장 의미 있는 대목</strong></span>이고, 체제 전환 해석은 단일 벤치마크 우위보다 신뢰할 만합니다. 근데 백본이 Qwen3.5 중심이라 일반화는 직접 확인해볼 여지로 남습니다.
