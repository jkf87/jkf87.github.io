---
title: "Motif 3 테크니컬 리포트: 314B MoE가 에이전트 성능을 겨냥하는 방식"
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

![Motif 3 Technical Report 첫 페이지. 이 글은 314B total / 13.2B active MoE 모델이 어떤 구조와 post-training recipe로 agentic benchmark를 노렸는지 정리한다.](/images/motif-3-technical-report-2026-08-12/page-01-title.png)

Motif 3 테크니컬 리포트가 올라왔습니다. 숫자부터 큽니다. **총 314B parameters, token당 active 13.2B, sparse MoE layer마다 routed expert 384개, 그중 8개만 선택**합니다.

근데 이 리포트에서 더 중요한 건 "큰 MoE 하나 더 나왔다"가 아닙니다. Motif 3는 구조, 학습 시스템, tokenizer, post-training을 전부 agentic task 쪽으로 맞춰 놓은 모델입니다. 특히 τ³-Banking, ITBench-AA, Terminal-Bench 같은 도구 사용·터미널·업무형 벤치마크에서 강하게 나옵니다.

아직 제가 첫 번째로 담아보는 글이라, 아래는 리포트의 뼈대를 먼저 잡은 버전입니다. 디테일은 코난쌤이랑 보면서 더 채우면 좋겠습니다.

## 한 줄로 보면, "작게 켜지는 큰 모델"입니다

Motif 3는 decoder-only MoE 모델입니다.

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

여기서 포인트는 계산량입니다. 314B 전체를 매 token마다 다 쓰는 게 아니라, token마다 expert 8개만 켭니다. 그래서 총 capacity는 크게 가져가되, per-token compute는 13.2B 수준으로 제한합니다.

이 방향은 요즘 open-weight MoE들이 다 가는 길입니다. Kimi, DeepSeek, GLM 계열이 전부 비슷한 문제를 봅니다. "모델 전체는 커져야 하는데, inference cost는 그대로 커지면 안 된다"는 문제입니다.

Motif 3의 차별점은 expert 수를 꽤 잘게 쪼갰다는 점입니다. MoE layer마다 384 routed experts가 있고, token마다 8개를 고릅니다. fine-grained sparsity라고 부르는 이유입니다.

## Attention 쪽 이름은 GDLA입니다

![Motif 3의 GDLA 구조. MLA식 compressed KV latent와 differential attention의 signal/noise 경로를 결합하고, query-dependent output gate를 붙인 구조다.](/images/motif-3-technical-report-2026-08-12/figure-1-gdla-architecture.png)

Motif 3의 핵심 attention 구조는 **GDLA(Grouped Differential Latent Attention)**입니다.

이름이 길어서 쪼개면 이렇습니다.

1. Differential Attention: attention distribution 두 개를 만들고 하나에서 하나를 빼서, noise에 해당하는 공통 패턴을 줄이려는 방식
2. Grouped Differential Attention: signal head는 더 많이 두고, noise head는 적게 둔 뒤 반복 공유해서 계산 효율을 맞추는 방식
3. MLA(Multi-head Latent Attention): KV cache를 low-rank latent representation으로 압축해서 long-context inference 비용을 줄이는 방식

GDLA는 이 셋을 합친 형태입니다. 리포트 표현으로는 differential attention의 selectivity를 유지하면서, MLA의 compressed KV cache 장점을 가져옵니다.

Motif 3 설정은 query head 80개, KV head 16개입니다. 그중 signal query head 64개, noise query head 16개입니다. signal:noise가 4:1입니다. 그리고 full causal attention layer 1개 뒤에 sliding-window attention layer 3개를 반복합니다. sliding-window window는 128 tokens입니다.

이 설계는 long-context 모델에서 익숙한 trade-off를 그대로 봅니다. 모든 layer를 full attention으로 두면 비용이 너무 큽니다. 그렇다고 전부 local로 두면 먼 정보 연결이 약해집니다. 그래서 일부 layer만 full attention으로 두고, 나머지는 sliding-window로 갑니다.

리포트의 controlled experiment에서는 GDLA가 GDA와 MLA보다 낮은 loss를 유지했고, MLA가 loss 3.2에 도달하는 데 필요한 token보다 9.2% 적은 token으로 같은 loss에 도달했다고 합니다. 다만 이 비교는 약 10B 규모 모델에서 한 diagnostic comparison입니다. 314B 전체 모델의 완전한 ablation으로 읽으면 안 됩니다.

### 그럼 왜 signal:noise를 4:1로 둔 걸까요?

이 부분은 리포트가 독립 ablation을 길게 보여주지는 않습니다. 제가 보기엔 **이론적으로 도출된 최적비라기보다, inductive bias와 경험적 튜닝이 섞인 설계값**에 가깝습니다.

Differential Attention의 기본 가정은 signal과 noise가 같은 성격이 아니라는 겁니다. signal은 다양해야 합니다. 어떤 head는 정의를 보고, 어떤 head는 수식을 보고, 어떤 head는 표를 보고, 어떤 head는 코드 블록이나 한국어 문맥을 봐야 합니다. 반대로 noise는 더 공통적일 가능성이 큽니다. 가까운 token, 문장 구분자, 반복되는 boilerplate, 표의 공통 구조처럼 attention mass를 먹지만 head마다 완전히 새로 추정할 필요는 적은 패턴입니다.

그래서 signal과 noise를 1:1로 두면 head budget 절반을 "무엇을 볼지"가 아니라 "무엇을 뺄지"에 쓰게 됩니다. Motif는 이 비용이 아깝다고 본 겁니다. noise head는 적게 만들고 여러 signal head가 공유하는 보정항처럼 쓰는 쪽을 택합니다.

대략 이렇게 읽으면 됩니다.

| 비율 | 해석 |
|---|---|
| 1:1 | noise 제거는 풍부하지만 signal capacity를 많이 먹음 |
| 4:1 | noise 제거 기능은 유지하면서 signal head 대부분을 살림 |
| 8:1 이상 | signal capacity는 크지만 noise 추정이 너무 거칠 수 있음 |

Motif 3는 grouped ratio `g = 4`를 씁니다. 그래서 signal query head 64개와 noise query head 16개가 됩니다. 다만 `1:1 vs 2:1 vs 4:1 vs 8:1` 같은 ratio별 비교표가 리포트에 제시된 것은 아닙니다. 따라서 글에서는 "4:1이 정답"이라고 쓰기보다, **Motif는 noise 추정보다 signal 표현에 head budget을 더 배정했고, 그 구현값이 4:1이다** 정도로 보는 게 안전합니다.

## MoE 안정화에 꽤 많은 장치를 넣었습니다

MoE는 expert를 많이 만든다고 자동으로 좋아지지 않습니다. router가 초반에 특정 expert만 고르면 그 expert만 더 학습되고, 더 잘 고르게 되고, 안 고른 expert는 계속 굶습니다. token count만 맞아도 expert들이 비슷한 기능으로 수렴하면 specialization이 무너집니다.

Motif 3는 이 문제를 여러 겹으로 막습니다.

- normalized sigmoid routing
- auxiliary-loss-free expert bias
- sequence-wise load-balancing objective
- decaying router noise
- layer-adaptive auxiliary-loss coefficient
- modified manifold-constrained hyper-connections(mHC)
- Expert-Specific PolyNorm activation

여기서 재미있는 건 Expert-Specific PolyNorm입니다. 보통 FFN activation을 하나로 고정하면 모든 expert가 같은 nonlinear response를 공유합니다. Motif 3는 expert마다 activation을 다르게 학습하게 해서, expert gate weight의 effective rank를 더 넓게 유지한다고 설명합니다. 쉽게 말하면 expert들이 서로 다른 방향으로 살아남게 만드는 장치입니다.

MoE의 실패는 두 가지로 옵니다. 하나는 router가 몇 expert만 계속 고르는 **expert starvation**입니다. 다른 하나는 token count는 균형 있게 나뉘는데 expert들이 결국 비슷한 함수로 수렴하는 **specialization collapse**입니다. Expert-Specific PolyNorm은 특히 두 번째 문제를 겨냥합니다. expert마다 activation 성격을 다르게 둘 수 있게 해서, 이름만 expert인 384개 복사본이 아니라 서로 다른 반응 곡선을 가진 expert로 남게 하려는 장치입니다.

약어로 줄이면 헷갈리기 쉽습니다. ESPN이라고 쓰면 스포츠 채널처럼 보이니, 글에서는 그냥 **Expert-Specific PolyNorm**으로 풀어 쓰는 편이 낫겠습니다.

mHC 쪽도 실무적으로 중요합니다. 원래 manifold-constrained hyper-connections의 post-mapping multiplier는 2인데, Motif 3는 이를 시간에 따라 1로 anneal합니다. 리포트는 큰 깊이와 scale에서 multiplier 2가 residual stream activation outlier를 누적시켰다고 설명합니다. 큰 모델 학습에서 "이론상 좋은 구조"를 그대로 쓰면 수치적으로 튀는 부분이 있고, 실제 scale에서는 damping이 필요했다는 얘기입니다.

## Tokenizer에서 한국어가 눈에 띕니다

Motif 3는 tokenizer도 새로 훈련했습니다. SuperBPE 기반이고, Stage 2에서 space-separated letter run을 pre-tokenization unit 안에 넣어서 여러 단어를 하나의 token 후보로 merge할 수 있게 합니다.

예시가 흥미롭습니다. 영어의 "of the"뿐 아니라 한국어의 **"수 있다"** 같은 multi-word sequence를 예로 듭니다.

리포트의 tokenizer compression table에서 Motif tokenizer는 English, Korean, code, math에서 가장 좋은 bytes per token을 보입니다.

| Tokenizer | vocab | en | ko | code | math |
|---|---:|---:|---:|---:|---:|
| Motif | 220,160 | 5.68 | 5.31 | 4.07 | 4.55 |
| Qwen3.5 | 248,066 | 4.51 | 4.03 | 3.68 | 3.54 |
| Gemma-4 | 262,144 | 4.61 | 3.73 | 3.57 | 3.58 |
| DeepSeek-V4 | 129,280 | 4.73 | 3.34 | 3.80 | 3.86 |
| gpt-4o o200k | 200,000 | 4.70 | 3.65 | 3.92 | 3.75 |

bytes per token은 높을수록 같은 텍스트를 더 적은 token으로 표현한다는 뜻입니다. 한국어 5.31은 꽤 공격적인 수치입니다. 긴 한국어 문서, HWP/업무 문서, 법률·금융 도메인을 많이 다룰 때 context budget에 직접 영향을 줍니다.

물론 tokenizer compression이 곧 모델 품질은 아닙니다. 그래도 한국어를 peripheral language로만 두지 않았다는 신호로 볼 수 있습니다.

## Pretraining은 12.5T tokens, long-context는 후반 stage에서 256K로 올립니다

![Motif 3 base model evaluation table. pretraining만으로 MMLU 86.20, GSM8K 93.93, HumanEval 73.70, MBPP 84.60을 보고한다.](/images/motif-3-technical-report-2026-08-12/table-4-base-eval.png)

Pretraining corpus는 약 12.5T tokens입니다. 웹 문서, STEM, code, mathematics, multilingual content, synthetic QA, legal/financial domain data가 들어갑니다. Nemotron data가 전체 pretraining corpus의 약 70%를 차지한다고 합니다.

Context schedule도 분명합니다.

1. 처음에는 최대 4K sequence로 시작
2. learning-rate decay phase에서 32K로 전환
3. 별도 long-context stage에서 256K까지 확장

Long-context stage에서는 전체 pretraining corpus의 약 5%를 dedicated long-context dataset으로 재구성합니다. full-attention layer는 DeepSeek-YaRN 방식으로 4K에서 256K까지 확장하고, sliding-window layer는 local RoPE를 유지합니다.

여기서 하나 더 볼 부분은 reasoning-focused data 비중입니다. 리포트는 pretraining mixture에서 reasoning-focused data를 5% 미만으로 제한했다고 합니다. base model distribution이 reasoning trace에 과하게 쏠리지 않게 하려는 의도입니다. reasoning은 post-training에서 더 밀어 넣고, base는 넓게 가져가겠다는 쪽에 가깝습니다.

## Post-training은 7명의 teacher를 한 모델로 증류합니다

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

여기서 6개 teacher는 GRPO로 학습하고, software-engineering teacher는 SFT로 만든다고 합니다. RL task는 13개 verifier domain을 묶어서 씁니다. 모든 verifier를 하나의 policy에 동시에 섞지 않고, latency와 reward variance가 비슷한 domain끼리 나눠 teacher를 만듭니다.

그 다음 MOPD가 이 teacher들의 장점을 general student 하나에 통합합니다. 이 방향은 최근 post-training에서 자주 보이는 흐름입니다. specialist model을 여러 개 따로 배포하기보다, teacher들을 이용해 하나의 unified model에 capability를 흡수시키는 방식입니다.

여기서 중요한 단어는 **On-Policy**입니다. 단순히 teacher 답변을 모아 offline dataset처럼 베끼는 게 아니라, student가 현재 policy로 생성한 trajectory 위에서 teacher 신호를 받으며 학습하는 쪽입니다. 비유하면 수학, 코딩, 은행 업무, 터미널 작업, 긴 문서 읽기 선생님을 따로 훈련한 뒤, 배포할 때는 선생님 7명을 모두 데리고 나가는 게 아니라 학생 한 명에게 각 영역의 교정 신호를 흡수시키는 방식입니다.

정리하면 이렇습니다.

- 대부분의 specialist teacher: RL/GRPO 기반
- software-engineering teacher: repository-level 수정과 test execution 검증을 다루지만, 리포트에서는 SFT teacher로 구성
- 최종 배포 모델: 여러 teacher의 능력을 MOPD로 합친 unified student

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

## 제가 보기엔 이 리포트의 키워드는 세 개입니다

첫째, **fine-grained MoE**입니다. 384 experts 중 top-8만 켜는 구조로 capacity와 per-token compute를 분리합니다. 이건 앞으로 open-weight frontier 모델의 기본 형태에 가깝습니다.

둘째, **long-context는 architecture와 systems가 같이 가야 한다**는 점입니다. GDLA, MLA식 KV compression, hybrid full/sliding-window schedule, window-aware context parallelism, MXFP8, fused kernels가 한 세트로 묶입니다. context length를 숫자로만 올리는 게 아니라, 실제 학습과 inference 비용을 맞춰야 합니다.

셋째, **agentic post-training**입니다. General SFT 하나로 끝내지 않고, tool use, professional work, software engineering, long-context abstention, math, code/science, chat teacher를 따로 만든 뒤 MOPD로 합칩니다. 벤치마크 강점도 이 설계와 맞물립니다. Motif 3는 "더 똑똑한 챗봇"보다는 "업무 환경에서 굴릴 agent backbone"을 목표로 놓은 모델처럼 보입니다.

## 아직 조심해서 봐야 할 부분

리포트가 스스로 적은 한계도 있습니다.

- training/evaluation이 실제 모든 업무, 언어, 배포 조건을 대표하지는 않음
- 현재는 text model이라 image/video input이 필요한 작업에는 제한이 있음
- 256K context를 지원해도, long-horizon application에는 context보다 더 긴 state tracking, planning, recovery, environment interaction이 필요함
- SciCode와 CritPt 같은 전문 과학·코딩 reasoning에서는 strongest model 대비 낮은 영역이 있음

저는 마지막 항목이 특히 중요해 보입니다. Motif 3가 256K context와 agentic benchmark에서 강하다고 해도, 실제 long-horizon agent는 context window만으로 해결되지 않습니다. 작업 상태를 어떻게 저장하고, 실패를 어떻게 복구하고, 어떤 verifier로 중간 행동을 채점할지가 같이 붙어야 합니다.

이 부분은 최근 우리가 계속 봤던 RL environment, harness, verifier 논의와 그대로 이어집니다.

## 다음에 채우면 좋은 디테일

이 글은 1차 정리입니다. 같이 보면서 아래 부분을 더 채우면 좋겠습니다.

1. GDLA의 signal:noise ratio가 다른 값일 때 어떤 차이가 나는지 추가 ablation 찾기
2. Expert-Specific PolyNorm이 실제로 expert specialization을 얼마나 돕는지 ablation 확인하기
3. MOPD가 DeepSeek/Upstage/다른 MoE post-training recipe와 어떻게 다른지 비교하기
4. 한국어 tokenizer compression 5.31이 실제 한국어 업무 문서에서 얼마나 이득인지 예시 만들기
5. τ³-Banking, ITBench-AA, Terminal-Bench가 각각 무엇을 재는 benchmark인지 별도 박스로 정리하기

지금 단계의 제 판단은 이렇습니다. Motif 3 리포트는 단순 모델 카드가 아니라, **"MoE architecture + long-context systems + agentic post-training"을 하나의 제품형 model recipe로 묶은 문서**입니다. 숫자보다 이 조합을 보는 게 더 중요합니다.

---

원문: [Motif 3: Technical Report](https://arxiv.org/abs/2608.09119) / [PDF](https://arxiv.org/pdf/2608.09119)
