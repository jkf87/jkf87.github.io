---
title: "314B인데 토큰마다 13B만 쓴다 — 에이전트 백본을 위해 설계된 MoE의 내부"
date: 2026-08-12
draft: false
tags:
  - LLM
  - MoE
  - agent
  - long-context
  - reinforcement-learning
  - post-training
  - technical-report
source: arxiv
paper_url: https://arxiv.org/abs/2608.09119
authors:
  - Motif Technologies
description: "Motif 3 테크니컬 리포트 분석. 총 314B에 토큰당 활성 13.2B, expert 384개 중 8개만 선택하는 구조와 에이전트용 post-training(MOPD)까지. 큰 전문가 조직을 토큰마다 일부만 호출하는 설계를 실무 관점으로 정리."
---

숫자만 보면 또 큰 MoE 모델임. 총 314B parameter, token당 active는 약 13.2B, expert 384개 중 8개만 선택. 근데 [Motif 3 리포트](https://arxiv.org/abs/2608.09119)에서 볼 건 크기가 아니라 방향임. 노골적으로 agentic task를 보고 만든 모델이라는 것. 긴 문맥을 싸게 다루는 attention, expert가 서로 비슷해지지 않게 하는 MoE 안정화, 여러 specialist teacher를 한 모델에 합치는 post-training이 한 묶음으로 들어가 있음. 큰 전문가 조직을 토큰마다 일부만 호출하는 모델이라는 게 내 이해의 핵심임.

1. 구조부터. 314B를 매 토큰 전부 계산하면 비용이 감당 안 되니 MoE layer마다 expert 384개를 준비해두고 토큰마다 필요한 8개만 고름. 부서마다 전문가가 384명 있는데 회의마다 그 안건에 필요한 8명만 호출하는 방식. 조직 전체 역량은 크지만 매 요청의 회의 비용은 제한하는 것. 53개 layer 중 51개가 MoE이고 context는 256K, pretraining은 약 12.5T 토큰. Kimi, DeepSeek, GLM 계열이 가는 길과 같은 방향인데 expert를 잘게 쪼개고 토큰 단위로 얇게 호출하는 fine-grained sparsity가 차이임.

![Motif 3 첫 페이지](/images/motif-3-technical-report-2026-08-12/page-01-title.png)

2. attention 이름이 GDLA(Grouped Differential Latent Attention)인데 세 단어만 잡으면 됨. Differential은 attention을 signal과 noise 두 갈래로 나눠서 noise를 빼는 것. Grouped는 head 배분으로, signal query head 64개에 noise query head 16개, 즉 signal:noise = 4:1. Latent는 MLA 쪽인데 KV cache를 low-rank latent로 압축해서 긴 context에서 캐시가 커지는 문제를 줄이는 것. 4:1인 이유는 리포트에 ratio ablation이 길게 나오지 않아서 경험적 설계값으로 읽는 게 안전한데, 논리는 이해됨. signal은 다양해야 하고(정의를 보는 head, 수식을 보는 head, 표를 보는 head) noise는 상대적으로 공유 가능하니 1:1은 낭비고 8:1은 noise 추정이 거칠어질 수 있음. 제어 실험에서는 GDLA가 MLA보다 9.2% 적은 토큰으로 같은 loss에 도달했다고 함.

![GDLA 구조](/images/motif-3-technical-report-2026-08-12/figure-1-gdla-architecture.png)

3. MoE 안정화가 리포트의 숨은 주인공임. MoE는 expert를 많이 두면 좋아지는 게 아닌데 실패 패턴이 둘임. router가 초반에 몇 expert만 골라서 그것만 학습되는 expert starvation, token count는 균형인데 expert들이 비슷한 함수로 수렴하는 specialization collapse. Motif 3는 normalized sigmoid routing, auxiliary-loss-free expert bias, load-balancing, router noise decay 같은 장치들과 함께 Expert-Specific PolyNorm activation을 씀. activation을 하나로 고정하면 모든 expert가 같은 비선형 반응을 공유하는데 expert마다 activation 성격을 다르게 학습하게 해서 서로 다른 기능으로 남도록 유도하는 것. 그리고 residual stream outlier를 막기 위해 hyper-connection multiplier를 시간에 따라 1로 anneal하는 mHC도 씀. 314B 규모에서는 이런 안정화 장치가 학습 성공 여부를 가린다는 대목이 멋진 아키텍처 이름보다 실무적임.

4. tokenizer에서 한국어가 크게 잡힘. SuperBPE 기반이고 "수 있다" 같은 한국어 표현이 merge 예시로 나옴. compression 표에서 한국어 bytes per token 5.31로 비교 대상(Qwen3.5 4.03, Gemma-4 3.73, DeepSeek-V4 3.34)보다 높음. 같은 한국어 텍스트를 더 적은 토큰으로 표현한다는 뜻이라 긴 한국어 문서를 다룰 때 context budget에 직접 영향을 줌. compression이 곧 품질은 아니지만 한국어를 peripheral로 둔 설계는 아닌 것으로 보임.

5. pretraining도 정리됨. 12.5T 토큰에 웹, STEM, 코드, 수학, 다국어, 합성 QA, 법률·금융이 들어가고 context는 4K로 시작해 32K를 거쳐 별도 stage에서 256K로 확장. reasoning-focused data를 5% 미만으로 제한해서 base가 reasoning trace에 쏠리지 않게 한 것도 의도가 분명함. reasoning은 post-training에서 밀어 넣고 base는 넓게 가져가는 것.

6. post-training의 MOPD(Multi-teacher On-Policy Distillation)가 에이전트 관점의 핵심임. teacher를 일곱 개 만듦. agentic tool use, professional work, software engineering, long-context reasoning & abstention, mathematics, code and science, chat. 대부분 RL/GRPO로 학습하는데 software-engineering teacher만 SFT로 구성함. repo 수정, test execution, 실패 로그처럼 데이터 구조가 다르기 때문. 그리고 MOPD에서 student가 현재 policy로 만든 trajectory 위에서 각 teacher가 자기 영역에서 교정함. 수학 선생, 코딩 선생, 터미널 선생을 따로 훈련하고 학생 하나를 세워서 각자 교정한 뒤 unified student로 배포하는 것. 앞서 정리한 MAD-OPD(토론 선생)와 같은 "좋은 선생을 여럿 만들어 한 학생에 합친다"는 흐름의 다른 구현임.

7. 결과는 agentic 쪽이 눈에 뜀. τ³-Banking 35.3, ITBench-AA 51.5는 비교군 중 최고 수준이고 SWE-bench Verified 76.2, Terminal-Bench 2.1 74.9. 반대로 SciCode 40.6이나 CritPt 6.6은 strongest model보다 낮아서 전문 과학 reasoning은 개선 여지가 있다고 리포트도 인정함. AA-Omniscience는 accuracy 30.1에 Non-Hallucination 71.6로, 많이 맞히는 쪽보다 근거 없는 답을 덜 하는 쪽에 강점이 있다는 읽기가 가능함. 모든 벤치마크가 같은 harness에서 재평가된 건 아니라서 순위표는 과하게 읽지 말 것.

![평가 테이블](/images/motif-3-technical-report-2026-08-12/table-6-eval.png)

8. 내가 가져갈 것 세 개. 첫째, capacity와 per-token compute를 분리하는 fine-grained MoE는 open-weight frontier의 기본 형태가 되어가니 추론 비용 계산 시 total parameter가 아니라 active parameter를 볼 것. 둘째, long-context는 숫자가 아니라 아키텍처(GDLA, KV 압축)와 시스템(커널, 양자화)이 한 세트로 가야 실비용이 맞춰진다는 것. 셋째, 256K context를 지원해도 실제 long-horizon agent는 context window로 해결이 안 되고 상태 저장, 실패 복구, verifier가 같이 붙어야 한다는 리포트의 자체 인정. 지금까지 정리한 하네스·검증 논의와 정확히 이어지는 부분임. 모델 카드가 아니라 MoE 아키텍처 + long-context 시스템 + agentic post-training을 하나의 제품형 recipe로 묶은 문서라서 숫자보다 조합을 볼 것.

원문: [arXiv:2608.09119](https://arxiv.org/abs/2608.09119)
