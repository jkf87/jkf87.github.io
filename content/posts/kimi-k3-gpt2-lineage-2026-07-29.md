---
title: "GPT-2에서 Kimi K3까지, 22,580배 커진 모델의 진짜 변화"
date: 2026-07-29
draft: false
tags:
  - LLM
  - Kimi-K3
  - linear-attention
  - MoE
  - architecture
categories:
  - AI
  - Model Architecture
description: "ali(@waterloo_intern)의 X Article ‘22580: From GPT2 to Kimi3, Explained’를 뉴스레터 스타일로 정리했다. 22,580배 커진 것은 파라미터만이 아니라, 기억을 저장하고 지우고 다시 읽는 방식이다."
aliases:
  - /posts/kimi-k3-gpt2-lineage-2026-07-29
---

![GPT-2에서 Kimi K3까지 이어지는 attention 계보도. 이 글의 핵심은 “그냥 커졌다”가 아니라, 기억을 다루는 방식이 단계적으로 바뀌었다는 점이다. 출처: ali, 22580: From GPT2 to Kimi3, Explained.](/images/kimi-k3-gpt2-lineage-2026-07-29/hero.jpg)

GPT-2와 Kimi K3 사이에는 숫자로 보면 거의 우스운 차이가 있다. GPT-2는 약 124M parameter 모델이었다. Kimi K3는 2.8T parameter 모델이다. 단순히 나누면 **Kimi K3 하나 안에 GPT-2가 약 22,580개 들어간다.**

ali(@waterloo_intern)의 X Article [22580: From GPT2 to Kimi3, Explained](https://x.com/i/article/2077616768491585536)는 이 숫자를 출발점으로 삼는다. 그런데 글의 좋은 점은 “와, 엄청 커졌다”에서 멈추지 않는다는 데 있다. 저자는 GPT-2, Linear Attention, DeltaNet, Gated DeltaNet, Kimi Linear, Kimi K3를 한 줄로 놓고 묻는다. **지난 7년 동안 바뀐 것은 정말 scale뿐이었나?**

저는 이 글을 읽으면서 답이 꽤 분명하다고 느꼈다. 파라미터는 커졌다. 맞다. 그런데 더 중요한 변화는 따로 있다. **모델이 긴 문맥을 기억하는 방식, 그 기억을 덮어쓰는 방식, 필요 없는 기억을 지우는 방식, 그리고 깊은 layer 사이에서 이전 표현을 다시 꺼내는 방식이 바뀌었다.**

## 이번 글이 답하는 질문

이 뉴스레터는 ali의 원문을 따라가되, 실무 관점에서 네 가지 질문으로 다시 묶었습니다.

1. GPT-2식 decoder-only Transformer의 병목은 어디였나?
2. Linear Attention은 왜 매력적이었고, 왜 부족했나?
3. DeltaNet과 Gated DeltaNet은 “기억” 문제를 어떻게 바꿨나?
4. Kimi K3는 왜 단순한 2.8T 모델이 아니라, length·depth·width를 같이 재설계한 모델인가?

![attention 계열의 흐름을 한 장에 압축한 도식. GPT-2 이후의 변화는 “attention을 없애자”가 아니라, softmax attention이 비싼 곳과 꼭 필요한 곳을 나눠 쓰는 방향으로 갔다. 출처: ali.](/images/kimi-k3-gpt2-lineage-2026-07-29/fig21.jpg)

## GPT-2의 기본 문제는 “마지막 토큰만 필요한데 전부 계산한다”는 데 있었다

GPT-2는 decoder-only Transformer다. 입력 token에 token embedding과 positional embedding을 더하고, 여러 Transformer block을 통과시킨 뒤, 마지막 hidden state를 vocabulary logit으로 바꿔 다음 token을 고른다.

여기서 직관적인 비효율이 하나 생긴다. autoregressive decoding에서는 매 step마다 다음 token 하나만 고르면 된다. 실제로 필요한 것은 **마지막 위치의 logit**이다. 그런데 모델은 입력의 모든 위치에 대한 representation을 만든다. 다음 token을 붙이면 또 거의 같은 history를 다시 보게 된다.

그래서 KV cache가 나온다. 이전 token들의 key와 value vector를 저장해두면, 새 token을 만들 때 과거 전체를 다시 projection하지 않아도 된다. 이건 매우 실용적인 최적화다. 하지만 동시에 새로운 병목도 만든다. context가 길어질수록 KV cache는 선형으로 커지고, inference는 memory bandwidth와 VRAM 압박을 받는다.

> GPT-2 이후의 큰 질문은 “더 큰 모델을 만들자”만이 아니었다. “긴 history를 매번 들고 다니지 않으면서도, 필요한 정보는 어떻게 다시 찾을 것인가?”였다.

이 질문이 Linear Attention 계열로 이어진다.

## Linear Attention은 attention을 고정 크기 상태로 접으려는 시도였다

Softmax attention은 query와 key의 곱을 만든 뒤 softmax를 적용한다. 이 구조는 모든 query가 모든 key와 연결된다. 품질은 좋지만, sequence length가 길어질수록 비용과 저장 공간이 커진다.

Linear Attention의 아이디어는 다르다. softmax 대신 ELU+1 같은 feature map을 query와 key에 따로 적용한다. 그러면 연산 순서를 바꿀 수 있다. 커져가는 K, V 목록을 계속 들고 있는 대신, 이를 **고정된 D×D state** 안에 접어 넣을 수 있다.

![Normal Attention과 Linear Attention의 차이를 보여주는 도식. Linear Attention의 핵심은 모든 token의 KV를 들고 다니는 대신, history를 고정 크기 state로 접는 데 있다. 출처: ali.](/images/kimi-k3-gpt2-lineage-2026-07-29/fig04.jpg)

이 방식은 길이가 길어질수록 매력적이다. KV cache가 token 수에 따라 계속 커지는 대신, recurrent state처럼 고정된 크기의 memory를 업데이트하면 되기 때문이다.

하지만 여기서 바로 trade-off가 생긴다. softmax attention은 매우 표현력이 높은 선택 메커니즘이다. Linear Attention은 이를 더 싸게 만들기 위해 근사한다. 그리고 모든 과거 정보를 고정 크기 state에 더해 넣다 보면, 결국 서로 간섭한다.

쉽게 말하면 이렇다. 책장을 무한히 늘릴 수 없으니, 노트를 한 장에 계속 덧쓴다. 처음에는 잘 보인다. 하지만 어느 순간부터 글씨가 겹친다. **Linear Attention의 문제는 기억장이 고정되어 있다는 것 자체가 아니라, 그 안에서 무엇을 남기고 무엇을 지울지 정책이 약하다는 데 있다.**

## DeltaNet은 “그냥 더하기” 대신 “덮어쓰기”를 배운다

DeltaNet이 등장하는 지점이 여기다. 순수 additive linear attention에서는 새 key-value association이 state에 계속 더해진다. 효율은 좋지만, 이미 같은 key 방향에 저장된 정보가 있을 때 이를 정교하게 바꾸기 어렵다.

DeltaNet은 먼저 현재 key가 cache에서 무엇을 꺼내는지 본다. 그 다음, 우리가 새로 저장하고 싶은 value와 기존에 꺼낸 value의 차이를 계산한다. 그리고 그 차이만큼 state를 업데이트한다.

즉, “무조건 더한다”에서 “기존 내용을 확인하고 필요한 만큼 고친다”로 바뀐다. 이 작은 차이가 중요하다. finite memory에서는 추가보다 갱신이 더 중요해지는 순간이 온다.

원문에서 인용한 Fast Weight Programmers의 문장이 이 대목을 잘 잡는다. sequence length가 storage capacity를 넘으면 overcapacity regime에 들어가고, 모델은 어떤 key-value association을 유지하고 삭제할지 동적으로 결정해야 한다. 끝없이 더하기만 하는 instruction은 언젠가 한계에 닿는다.

![Gated DeltaNet Transformer 구조. fixed-size recurrent state를 쓰되, 정보 간섭과 갱신 문제를 architectural rule로 다루려는 시도다. 출처: ali.](/images/kimi-k3-gpt2-lineage-2026-07-29/fig13.jpg)

여기서 또 다른 현실 문제가 나온다. Delta rule을 token마다 순차적으로 적용하면 training prefill을 병렬화하기 어렵다. 원문이 좋은 이유가 이 부분이다. 저자는 수식만 말하지 않고, chunk 단위로 어떻게 matrix multiplication에 얹는지 설명한다. C=1이면 가장 싼 linear recurrence에 가깝고, C=N이면 full attention에 가까워진다. 중간 chunk size는 FLOPs와 GPU utilization 사이의 타협점이다.

이건 논문 수식이라기보다 시스템 엔지니어링의 냄새가 난다. **좋은 attention 아이디어도 GPU가 잘 먹는 모양으로 접히지 않으면, 실제 모델에서는 이기기 어렵다.**

## Gated DeltaNet은 기억에 “감쇠”를 넣는다

DeltaNet은 특정 association을 더 잘 갱신하게 해준다. 하지만 여전히 문제가 남는다. 특정 key에 새 값을 쓸 수는 있지만, context switch가 일어났을 때 여러 정보를 한꺼번에 희미하게 만들거나, 오래된 내용을 자연스럽게 decay시키는 능력은 부족하다.

Mamba 계열이 주는 직관은 여기서 유용하다. 이전 state를 일정 비율로 decay한 뒤 새 state를 더하면, memory가 무한정 커지거나 포화되는 문제를 줄일 수 있다.

다만 모든 정보를 같은 비율로 잊는 것도 거칠다. 어떤 정보는 오래 남아야 하고, 어떤 정보는 빨리 지워져야 한다. Delta rule은 특정 사실을 고치는 데 강하고, gated recurrence는 전체 memory를 조절하는 데 강하다. Gated DeltaNet은 이 둘을 합친다.

원문 식으로 말하면 alpha가 1이면 Delta rule에 가깝고, 0이면 memory를 지운다. token이 지나가면서 누적 decay가 곱해진다. 결국 memory update는 “쓰기”만이 아니라 “얼마나 남길 것인가”의 문제가 된다.

> 긴 context 모델의 핵심은 모든 것을 기억하는 능력이 아니다. 무엇을 빨리 잊고, 무엇을 오래 붙잡을지 배우는 능력이다.

## Kimi Linear는 per-channel decay로 memory control을 더 잘게 쪼갠다

Kimi Linear가 흥미로운 이유는 이 흐름 위에 있기 때문이다. Moonshot AI의 Kimi Linear 논문은 Kimi Delta Attention(KDA)을 중심에 놓고, full attention 대비 KV cache를 최대 75% 줄이고, 1M context decoding에서 최대 6× throughput을 얻었다고 주장한다. 논문 기준으로는 48B total, 3B activated parameter 모델을 같은 training recipe로 비교했을 때 full MLA baseline보다 좋은 결과를 보였다고 한다.

핵심은 KDA가 Gated DeltaNet을 더 세밀하게 만든다는 점이다. Gated DeltaNet이 하나의 scalar decay로 state를 조절했다면, KDA는 channel-wise gating을 쓴다. 즉 state의 각 차원마다 다른 속도로 잊고 남길 수 있다.

이건 단순한 기교가 아니다. fixed-size associative memory가 가진 본질적 문제에 더 가까이 간다. memory의 모든 차원이 같은 의미를 담고 있지 않다면, 모든 차원을 같은 비율로 잊는 것도 당연히 비효율적이다. KDA는 “어느 부분을 얼마나 남길 것인가”를 더 세밀하게 만든다.

동시에 Kimi Linear는 hybrid 구조를 쓴다. KDA layer만 쌓지 않고, 일정 비율로 Multi-head Latent Attention(MLA)을 섞는다. 선형 attention은 효율적이지만 고정 크기 state의 한계를 가진다. full attention 계열은 비싸지만 token context에서 직접 global retrieval을 할 수 있다. 그래서 둘을 같이 쓴다.

## Kimi K3는 length, depth, width를 동시에 건드린다

Kimi K3는 이 계보의 최신 형태에 가깝다. 공개 정보 기준으로 Kimi K3는 2.8T total parameter, 104B activated parameter, 93 layer, 1M token context window를 가진 MoE 모델이다. attention layer 구성은 **69 KDA + 24 Gated MLA**다. 전문가(expert)는 896개이고, token마다 16개 routed expert와 2개 shared expert가 관여한다.

공식 설명과 OpenLM 정리에 따르면 Kimi K3의 핵심은 세 축으로 볼 수 있다.

첫째, length다. 긴 sequence는 KDA가 대부분 담당한다. 고정 크기 recurrent state로 history를 압축하고, periodic Gated MLA가 full global interaction을 보강한다. 즉 모든 layer에서 비싼 attention을 쓰지 않는다.

둘째, depth다. Kimi K3는 Attention Residuals(AttnRes)를 쓴다. 일반 Transformer residual은 이전 출력들을 사실상 계속 더해간다. 깊이가 깊어지면 초기 feature가 희석되고, hidden-state magnitude를 다루기 어려워질 수 있다. AttnRes는 residual pathway 자체에 attention을 넣는다. layer가 무조건 직전 state만 받는 대신, 이전 depth representation 중 무엇이 유용한지 선택적으로 가져온다.

셋째, width다. Stable LatentMoE로 capacity를 크게 늘리되, 모든 parameter를 매 token마다 쓰지 않는다. 896개 expert 중 16개만 선택한다. 이 정도 sparsity에서는 routing 안정성이 곧 모델 품질과 throughput이 된다. 그래서 Quantile Balancing, latent-space expert, SiTU-GLU, Per-head Muon 같은 장치가 같이 등장한다.

![Kimi K3 쪽으로 오면 attention 문제는 sequence length만의 문제가 아니다. KDA는 길이를, AttnRes는 깊이를, LatentMoE는 폭을 다룬다. 출처: ali.](/images/kimi-k3-gpt2-lineage-2026-07-29/fig18.jpg)

이 대목에서 원문의 결론이 좋다. Kimi K3는 capacity를 그냥 많이 넣은 모델이 아니다. **추가 capacity가 어디에 필요한지, 어떤 기능을 해야 하는지에 맞춰 배치한 모델**이다. KDA는 constant-state recurrent memory를 맡고, MLA는 token context에서 full retrieval을 맡고, MoE는 sparse expert capacity를 제공하고, AttnRes는 depth-wise representation retrieval을 맡는다.

## 결국 문제는 eviction policy다

저는 이 글의 마지막 문장이 거의 핵심이라고 봤다. fixed-capacity associative memory에는 eviction policy가 필요하다. 고정된 크기의 memory에 계속 정보를 넣으면 언젠가 간섭이 생긴다. 그러면 모델은 배워야 한다. 무엇을 남길지. 무엇을 지울지. 무엇을 다시 읽을지.

LLM architecture 논의는 종종 이름 싸움처럼 보인다. MHA, MLA, GQA, Mamba, DeltaNet, KDA, MoE, AttnRes. 그런데 이 계보를 한 줄로 보면 질문은 비교적 단순해진다.

- token 방향으로는 무엇을 기억할 것인가?
- 오래된 token 정보는 어떻게 압축할 것인가?
- 압축된 state에서 무엇을 지울 것인가?
- full attention은 어디에만 쓸 것인가?
- depth 방향으로는 어떤 layer의 representation을 다시 꺼낼 것인가?
- width 방향으로는 어떤 expert만 활성화할 것인가?

GPT-2에서 Kimi K3까지의 변화는 “parameter가 22,580배 커졌다”는 말로는 너무 작게 설명된다. 더 정확히는 이렇다. **모델은 더 커졌고, 동시에 더 선택적으로 변했다.** 모든 token을 다 보고, 모든 layer를 똑같이 더하고, 모든 expert를 다 쓰는 방식으로는 1M context와 3T-class scale을 감당하기 어렵다.

앞으로의 open model 경쟁도 이 방향으로 갈 가능성이 크다. 단순히 “몇 T parameter인가”보다, 그 parameter가 어떤 선택 메커니즘을 갖고 있는지가 중요해진다. attention은 사라지는 것이 아니라, 더 비싼 곳에서는 아껴 쓰고, 꼭 필요한 곳에서는 더 정교하게 쓰는 쪽으로 재배치되고 있다.

그래서 이 글은 Kimi K3 해설이면서, 동시에 요즘 LLM architecture를 읽는 좋은 렌즈다. **scale은 여전히 중요하다. 하지만 scale만으로는 부족하다. 큰 모델일수록 더 좋은 기억 관리 정책이 필요하다.**

---

참고 자료

- ali, [22580: From GPT2 to Kimi3, Explained](https://x.com/i/article/2077616768491585536)
- Moonshot AI / OpenLM, [Kimi K3](https://openlm.ai/kimi-k3/)
- Moonshot AI, [Kimi Linear: An Expressive, Efficient Attention Architecture](https://arxiv.org/pdf/2510.26692)

에이전트와 long-context 모델을 직접 실험해보고 싶은 분들께는 제가 쓴 책과 강의도 참고 자료로 남깁니다. 책은 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902), 강의는 [AI 에이전트 실전 강의 — 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)입니다. 이 글에서 말한 “기억을 어디에 두고, 언제 다시 읽게 할 것인가”는 모델 내부뿐 아니라 에이전트 하네스 설계에서도 그대로 반복되는 문제입니다.
