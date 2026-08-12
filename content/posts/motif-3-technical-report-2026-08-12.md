---
title: "Motif 3: 314B MoE 모델이 에이전트용으로 만들어지는 방식"
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
---

![Motif 3 Technical Report 첫 페이지. 314B total parameter 모델이지만 token마다 약 13.2B만 활성화하는 MoE 구조가 핵심이다.](/images/motif-3-technical-report-2026-08-12/page-01-title.png)

Motif 3 테크니컬 리포트가 올라왔습니다. 숫자만 보면 일단 큽니다. **총 314B parameter, token당 active parameter는 약 13.2B, sparse MoE layer마다 routed expert 384개, 그중 token마다 8개만 선택**합니다.

근데 이 글에서 보고 싶은 건 “또 큰 MoE가 나왔다”가 아닙니다. Motif 3는 꽤 노골적으로 agentic task를 보고 만든 모델입니다. 긴 문맥을 싸게 다루는 attention, expert가 서로 비슷해지지 않게 하는 MoE 안정화, 여러 specialist teacher를 한 모델에 합치는 post-training이 한 묶음으로 들어갑니다.

제가 이해한 핵심은 이겁니다. **Motif 3는 큰 모델을 매번 다 쓰는 모델이 아니라, 큰 전문가 조직을 token마다 일부만 호출하는 모델**입니다.

## 314B인데 token마다 13.2B만 씁니다

Motif 3는 decoder-only MoE 모델입니다. 구조를 표로 보면 이렇습니다.

| 항목 | Motif 3 |
|---|---:|
| 총 파라미터 | 314B |
| token당 활성 파라미터 | 약 13.2B |
| Transformer layer | 53개 |
| dense / MoE layer | 2 dense + 51 MoE |
| hidden dimension | 4,096 |
| routed experts | layer당 384개 |
| routing | top-8 |
| context length | 256K tokens |
| pretraining tokens | 약 12.5T |

여기서 중요한 건 total parameter와 active parameter를 분리했다는 점입니다. 314B짜리 모델을 매 token마다 전부 계산하면 비용이 너무 큽니다. 그래서 MoE layer마다 expert 384개를 준비해두고, token마다 필요한 expert 8개만 고릅니다.

비유하면 부서마다 전문가가 384명 있는데, 회의마다 전원을 부르지 않습니다. 그 안건에 필요한 8명만 호출합니다. 조직 전체 역량은 크지만, 매 요청의 회의 비용은 제한하는 방식입니다.

이 방향은 최근 frontier급 open-weight 모델들이 계속 가는 길입니다. Kimi, DeepSeek, GLM 계열도 비슷한 문제를 봅니다. 모델은 커져야 하는데, inference cost가 같이 폭증하면 실제 배포가 어렵습니다. Motif 3의 답은 fine-grained sparsity입니다. expert를 꽤 잘게 쪼개고, token 단위로 얇게 호출합니다.

## GDLA는 attention을 덜 헷갈리게, 더 싸게 만들려는 장치입니다

![Motif 3의 GDLA 구조. MLA식 compressed KV latent와 differential attention의 signal/noise 경로를 결합하고, query-dependent output gate를 붙인 구조다.](/images/motif-3-technical-report-2026-08-12/figure-1-gdla-architecture.png)

Motif 3의 attention 이름은 **GDLA(Grouped Differential Latent Attention)**입니다. 이름이 긴데, 세 단어만 잡으면 됩니다.

첫째, **Differential**입니다. 일반 attention은 중요한 정보와 잡음을 같이 봅니다. Differential Attention은 attention을 두 갈래로 나눕니다. 하나는 signal attention, 다른 하나는 noise attention입니다. 그리고 대략 signal에서 noise를 빼는 식으로 최종 attention을 만듭니다. 문맥에서 진짜 볼 부분만 남기려는 방향입니다.

둘째, **Grouped**입니다. signal과 noise를 1:1로 만들면 비쌉니다. head budget 절반을 “무엇을 볼지”가 아니라 “무엇을 뺄지”에 쓰게 됩니다. Motif 3는 signal query head를 64개, noise query head를 16개 둡니다. 즉 **signal:noise = 4:1**입니다.

셋째, **Latent**입니다. 이건 MLA(Multi-head Latent Attention) 쪽입니다. KV cache를 그대로 크게 저장하지 않고, low-rank latent representation으로 압축합니다. 긴 context에서 KV cache가 너무 커지는 문제를 줄이려는 겁니다.

한 문장으로 줄이면 이렇습니다.

> GDLA는 attention을 signal/noise로 나눠 noise를 빼고, signal 쪽에 더 많은 head를 주고, KV cache는 latent 공간에 압축해 저장하는 구조다.

## 그럼 왜 signal:noise가 4:1일까요?

이 부분은 리포트가 ratio ablation을 따로 길게 보여주지는 않습니다. 그래서 “4:1이 이론적으로 증명된 최적값”이라고 쓰면 안 됩니다. 제 판단으로는 **경험적 설계값에 가깝습니다.** 다만 아무 근거 없이 찍은 숫자는 아닙니다.

Differential Attention의 가정은 signal과 noise가 같은 성격이 아니라는 겁니다. signal은 다양해야 합니다. 어떤 head는 정의를 보고, 어떤 head는 수식을 보고, 어떤 head는 표를 보고, 어떤 head는 코드 블록을 보고, 어떤 head는 한국어 문맥을 봐야 합니다.

반대로 noise는 상대적으로 공유 가능할 수 있습니다. 가까운 token, 문장 구분자, 반복되는 boilerplate, 표의 공통 구조처럼 attention mass를 먹지만 head마다 완전히 다르게 추정할 필요는 적은 패턴입니다.

그래서 1:1로 두면 너무 비쌉니다. noise 제거는 풍부해지지만 signal capacity를 많이 먹습니다. 8:1 이상으로 너무 벌리면 signal은 많아지지만 noise 추정이 거칠어질 수 있습니다. Motif 3는 그 사이에서 `g = 4`를 둔 겁니다.

| 비율 | 해석 |
|---|---|
| 1:1 | noise 제거는 풍부하지만 signal capacity를 많이 씀 |
| 4:1 | noise 제거 기능은 유지하면서 signal head 대부분을 살림 |
| 8:1 이상 | signal capacity는 크지만 noise 추정이 거칠 수 있음 |

리포트의 controlled experiment에서는 GDLA가 GDA와 MLA보다 낮은 loss를 유지했고, MLA가 loss 3.2에 도달하는 데 필요한 token보다 9.2% 적은 token으로 같은 loss에 도달했다고 합니다. 다만 이 비교는 약 10B 규모 diagnostic comparison입니다. 314B 전체 모델에서 ratio별 ablation을 보여준 것은 아닙니다.

그래서 안전한 해석은 이 정도입니다. **Motif 3는 noise 추정보다 signal 표현에 head budget을 더 배정했고, 그 구현값이 4:1이다.**

## Expert-Specific PolyNorm은 expert를 “다른 전문가”로 남기려는 장치입니다

MoE는 expert를 많이 둔다고 자동으로 좋아지지 않습니다. 실패 패턴이 두 개 있습니다.

첫째는 **expert starvation**입니다. router가 초반에 몇 expert만 계속 고르면, 그 expert만 더 학습됩니다. 더 학습된 expert는 더 자주 선택되고, 안 선택된 expert는 계속 굶습니다.

둘째는 **specialization collapse**입니다. token count는 그럭저럭 균형 있게 나뉘는데, expert들이 결국 비슷한 함수로 수렴하는 경우입니다. 이름은 전문가 384명인데, 실제로는 비슷한 반응을 하는 복사본이 되는 겁니다.

Motif 3는 이 문제를 여러 장치로 막습니다.

- normalized sigmoid routing
- auxiliary-loss-free expert bias
- sequence-wise load-balancing objective
- decaying router noise
- layer-adaptive auxiliary-loss coefficient
- modified manifold-constrained hyper-connections(mHC)
- Expert-Specific PolyNorm activation

여기서 **Expert-Specific PolyNorm**이 중요합니다. 보통 FFN activation을 하나로 고정하면 모든 expert가 같은 nonlinear response를 공유합니다. Motif 3는 expert마다 activation 성격을 다르게 학습할 수 있게 합니다. 리포트는 이 방식이 expert gate weight의 effective rank를 더 넓게 유지한다고 설명합니다.

쉽게 말하면 이겁니다. expert A, B, C가 같은 입력을 받아도 서로 다른 반응 곡선을 갖게 만드는 장치입니다. expert들이 “고르게 선택되는 것”을 넘어, 실제로 서로 다른 기능으로 남도록 유도합니다.

약어로 줄이면 헷갈립니다. ESPN이라고 쓰면 다른 게 떠오르니, 이 글에서는 그냥 Expert-Specific PolyNorm으로 풀어 쓰겠습니다.

## mHC는 큰 모델에서 residual stream이 튀는 문제를 누릅니다

Motif 3는 modified manifold-constrained hyper-connections(mHC)도 씁니다. 원래 mHC의 post-mapping multiplier는 2인데, Motif 3는 이를 시간에 따라 1로 anneal합니다.

리포트가 말하는 이유는 실무적입니다. 큰 depth와 scale에서 multiplier 2를 그대로 쓰면 residual stream activation outlier가 누적됐다고 합니다. 이론상 좋은 구조라도 314B 규모에서는 수치적으로 튀는 부분이 생깁니다. 그래서 scale에 맞게 damping을 넣은 겁니다.

이런 대목이 저는 꽤 중요해 보입니다. 큰 모델 리포트는 보통 멋진 architecture 이름만 보게 되는데, 실제로는 이런 안정화 장치가 학습 성공 여부를 가릅니다.

## Tokenizer에서 한국어가 꽤 크게 잡힙니다

Motif 3는 tokenizer도 새로 훈련했습니다. SuperBPE 기반이고, Stage 2에서 여러 단어가 하나의 pre-tokenization unit 안에서 merge될 수 있게 합니다.

예시가 흥미롭습니다. 영어의 “of the”뿐 아니라 한국어의 **“수 있다”** 같은 표현을 예로 듭니다.

리포트의 tokenizer compression table에서 Motif tokenizer는 English, Korean, code, math에서 가장 좋은 bytes per token을 보입니다.

| Tokenizer | vocab | en | ko | code | math |
|---|---:|---:|---:|---:|---:|
| Motif | 220,160 | 5.68 | 5.31 | 4.07 | 4.55 |
| Qwen3.5 | 248,066 | 4.51 | 4.03 | 3.68 | 3.54 |
| Gemma-4 | 262,144 | 4.61 | 3.73 | 3.57 | 3.58 |
| DeepSeek-V4 | 129,280 | 4.73 | 3.34 | 3.80 | 3.86 |
| gpt-4o o200k | 200,000 | 4.70 | 3.65 | 3.92 | 3.75 |

bytes per token은 높을수록 같은 텍스트를 더 적은 token으로 표현한다는 뜻입니다. 한국어 5.31은 꽤 공격적인 수치입니다. 긴 한국어 문서, HWP/업무 문서, 법률·금융 도메인을 많이 다룰 때 context budget에 직접 영향을 줍니다.

물론 tokenizer compression이 곧 모델 품질은 아닙니다. 그래도 한국어를 peripheral language로만 둔 설계는 아닌 것으로 보입니다.

## Pretraining은 12.5T tokens, long-context는 후반에 256K로 올립니다

![Motif 3 base model evaluation table. pretraining만으로 MMLU 86.20, GSM8K 93.93, HumanEval 73.70, MBPP 84.60을 보고한다.](/images/motif-3-technical-report-2026-08-12/table-4-base-eval.png)

Pretraining corpus는 약 12.5T tokens입니다. 웹 문서, STEM, code, mathematics, multilingual content, synthetic QA, legal/financial domain data가 들어갑니다. Nemotron data가 전체 pretraining corpus의 약 70%를 차지한다고 합니다.

Context schedule도 분명합니다.

1. 처음에는 최대 4K sequence로 시작
2. learning-rate decay phase에서 32K로 전환
3. 별도 long-context stage에서 256K까지 확장

Long-context stage에서는 전체 pretraining corpus의 약 5%를 dedicated long-context dataset으로 재구성합니다. full-attention layer는 DeepSeek-YaRN 방식으로 4K에서 256K까지 확장하고, sliding-window layer는 local RoPE를 유지합니다.

여기서 하나 더 볼 부분은 reasoning-focused data 비중입니다. 리포트는 pretraining mixture에서 reasoning-focused data를 5% 미만으로 제한했다고 합니다. base model distribution이 reasoning trace에 과하게 쏠리지 않게 하려는 의도입니다. reasoning은 post-training에서 더 밀어 넣고, base는 넓게 가져가겠다는 쪽에 가깝습니다.

## MOPD는 여러 선생을 한 학생에게 합치는 post-training입니다

Motif 3의 post-training pipeline은 세 단계입니다.

1. General SFT
2. Specialist teacher training
3. MOPD(Multi-teacher On-Policy Distillation)

General SFT 전에 preliminary SFT model을 한 번 써서 capability-specific failure mode를 찾습니다. 특히 agentic trajectory에서 실패하기 쉬운 decision을 찾아 targeted supervision을 만듭니다. 그다음 pretrained checkpoint에서 다시 시작해 consolidated corpus로 general SFT를 합니다.

이후 teacher를 7개 만듭니다.

| Teacher | Coverage |
|---|---|
| Agentic tool use | shell/tool 환경, multi-step task execution |
| Professional work | 직업형 산출물, 비교 기반 채점 |
| Software engineering | repo-level 수정, test execution 검증 |
| Long-context reasoning & abstention | 긴 입력 검색·종합, 모르면 멈추기 |
| Mathematics | competition/proof-style problem |
| Code and science | program synthesis, scientific computing, physical reasoning |
| Chat | dialogue quality, instruction following, safety |

여기서 대부분의 specialist teacher는 RL/GRPO로 학습합니다. 단, software-engineering teacher는 리포트에서 SFT teacher로 구성합니다. 이 구분이 중요합니다. SWE류 작업은 repo 수정, test execution, 실패 로그 등 데이터 구조가 다르고, 리포트는 이 영역을 별도 SFT teacher로 다룹니다.

MOPD에서 중요한 단어는 **On-Policy**입니다. 단순히 teacher 답변을 모아 offline dataset처럼 베끼는 게 아니라, student가 현재 policy로 만든 trajectory 위에서 teacher 신호를 받으며 학습합니다.

비유하면 이렇습니다. 수학 선생님, 코딩 선생님, 은행 업무 선생님, 터미널 작업 선생님, 긴 문서 읽기 선생님을 따로 훈련합니다. 그런데 배포할 때 선생님 7명을 다 데리고 나갈 수는 없습니다. 학생 한 명을 세우고, 각 선생님이 자기 영역에서 교정해줍니다. 최종 배포 모델은 선생님 묶음이 아니라 **하나의 unified student**입니다.

## 결과는 agentic benchmark 쪽이 제일 눈에 띕니다

![Motif 3 evaluation table. Motif 3는 τ³-Banking 35.3, ITBench-AA 51.5, Terminal-Bench 2.1 74.9, SWE-bench Verified 76.2를 보고한다.](/images/motif-3-technical-report-2026-08-12/table-6-eval.png)

리포트의 비교 대상은 MiniMax-3, GLM-5.1, Kimi-K2.6, Qwen-3.7, DeepSeek-v4-Pro입니다. 모든 benchmark가 같은 harness에서 완전히 재평가된 건 아니고, 일부는 leaderboard reported scores와 비교합니다. 그래서 순위표를 너무 과하게 읽으면 안 됩니다.

그래도 방향은 선명합니다.

| Benchmark | Motif 3 |
|---|---:|
| GDPval-AA v2 | 38.7 |
| τ²-Bench Telecom | 94.7 |
| τ³-Banking | 35.3 |
| ITBench-AA | 51.5* |
| SWE-bench Verified | 76.2 |
| Terminal-Bench 2.1 | 74.9 |
| SciCode | 40.6 |
| GPQA Diamond | 83.4 |
| AA-LCR | 72.3 |
| IFBench | 78.2 |

별표가 붙은 ITBench-AA는 public subset 기준입니다.

가장 눈에 띄는 건 τ³-Banking 35.3입니다. 비교표에 있는 다른 모델보다 높습니다. ITBench-AA 51.5도 available results 중 가장 높다고 적습니다. Terminal-Bench 2.1은 74.9로 Qwen-3.7의 75.0과 거의 같습니다.

반대로 SciCode 40.6, CritPt 6.6은 strongest model보다 낮습니다. 리포트도 scientific coding과 specialized scientific reasoning은 개선 여지가 있다고 적습니다.

AA-Omniscience도 해석이 필요합니다. Accuracy는 30.1로 최고는 아닙니다. 대신 Non-Hallucination은 71.6으로 높습니다. 많이 맞히는 쪽보다, 근거 없는 답을 덜 하는 쪽에 강점이 있다는 식으로 읽을 수 있습니다.

## 저는 세 가지를 보면 된다고 봅니다

첫째, **fine-grained MoE**입니다. 384 experts 중 top-8만 켜는 구조로 capacity와 per-token compute를 분리합니다. 앞으로 open-weight frontier 모델의 기본 형태에 가까워 보입니다.

둘째, **long-context는 architecture와 systems가 같이 가야 한다**는 점입니다. GDLA, MLA식 KV compression, hybrid full/sliding-window schedule, window-aware context parallelism, MXFP8, fused kernels가 한 세트로 묶입니다. context length를 숫자로만 올리는 게 아니라, 실제 학습과 inference 비용을 맞춰야 합니다.

셋째, **agentic post-training**입니다. General SFT 하나로 끝내지 않고, tool use, professional work, software engineering, long-context abstention, math, code/science, chat teacher를 따로 만든 뒤 MOPD로 합칩니다. 벤치마크 강점도 이 설계와 맞물립니다. Motif 3는 “더 똑똑한 챗봇”보다는 “업무 환경에서 굴릴 agent backbone”을 목표로 놓은 모델처럼 보입니다.

## 그래도 조심해서 봐야 합니다

리포트가 스스로 적은 한계도 있습니다.

- training/evaluation이 실제 모든 업무, 언어, 배포 조건을 대표하지는 않음
- 현재는 text model이라 image/video input이 필요한 작업에는 제한이 있음
- 256K context를 지원해도, long-horizon application에는 context보다 더 긴 state tracking, planning, recovery, environment interaction이 필요함
- SciCode와 CritPt 같은 전문 과학·코딩 reasoning에서는 strongest model 대비 낮은 영역이 있음

저는 마지막 항목이 특히 중요해 보입니다. Motif 3가 256K context와 agentic benchmark에서 강하다고 해도, 실제 long-horizon agent는 context window만으로 해결되지 않습니다. 작업 상태를 어떻게 저장하고, 실패를 어떻게 복구하고, 어떤 verifier로 중간 행동을 채점할지가 같이 붙어야 합니다.

이 부분은 최근 우리가 계속 봤던 RL environment, harness, verifier 논의와 그대로 이어집니다.

## 다음에는 여기를 더 파보면 좋겠습니다

1. GDLA의 signal:noise ratio가 다른 값일 때 어떤 차이가 나는지 추가 ablation 찾기
2. Expert-Specific PolyNorm이 실제로 expert specialization을 얼마나 돕는지 확인하기
3. MOPD가 DeepSeek/Upstage/다른 MoE post-training recipe와 어떻게 다른지 비교하기
4. 한국어 tokenizer compression 5.31이 실제 한국어 업무 문서에서 얼마나 이득인지 예시 만들기
5. τ³-Banking, ITBench-AA, Terminal-Bench가 각각 무엇을 재는 benchmark인지 별도 박스로 정리하기

지금 단계의 제 판단은 이렇습니다. Motif 3 리포트는 단순 모델 카드가 아니라, **MoE architecture + long-context systems + agentic post-training을 하나의 제품형 model recipe로 묶은 문서**입니다. 숫자보다 이 조합을 보는 게 더 중요합니다.

---

원문: [Motif 3: Technical Report](https://arxiv.org/abs/2608.09119) / [PDF](https://arxiv.org/pdf/2608.09119)
