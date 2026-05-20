---
title: "처음부터 만드는 LLM: 토크나이저부터 트랜스포머·학습·생성·경연까지 (전 6장 통합)"
date: 2026-05-05
tags:
  - ai
  - llm
  - transformer
  - pytorch
  - tutorial
  - llm-from-scratch
description: "PyTorch로 GPT를 처음부터 직접 짜보는 워크숍 — 토크나이저, 트랜스포머 블록(어텐션·MLP·잔차·LayerNorm), 학습 루프(AdamW·LR 스케줄·그래디언트 클리핑), 텍스트 생성(temperature·top-k), 실데이터 스케일링, 경연까지 6장을 한 글에 모았음."
aliases:
  - llm-from-scratch-2026-05-05/index
  - llm-from-scratch
---

이 글은 [angelos-p/llm-from-scratch](https://github.com/angelos-p/llm-from-scratch) 워크숍의 영문 docs 6편을 한국어로 옮겨 한 편으로 합친 것임. PyTorch로 GPT를 처음부터 직접 짜보는 핸즈온 워크숍이고, 셰익스피어 텍스트로 ~10M 파라미터 모델을 노트북에서 한 시간 안에 학습시키는 게 목표임. 코드/식별자/수식은 원문 그대로 두고 본문만 자연스러운 한국어로 옮김.

원본 디렉토리: [`docs/`](https://github.com/angelos-p/llm-from-scratch/tree/main/docs) · 라이선스/저작권은 원저자에게 있음.

## 목차

1. **토큰화(Tokenization)** — 텍스트를 정수로
2. **트랜스포머** — GPT 아키텍처를 PyTorch로
3. **학습 루프** — forward / loss / backprop / optimizer
4. **텍스트 생성** — 샘플링(temperature, top-k)
5. **모두 합쳐서 돌려보기** — 실데이터·손실 곡선·스케일링
6. **경연 — 최고의 AI 시인 만들기** — 데이터 찾고 모델 키우기


## Part 1: 토큰화(Tokenization)

LLM은 텍스트를 직접 보는 게 아니다. 정수(integer) 시퀀스를 본다. 토크나이저(tokenizer)는 이 둘 사이를 오가는 변환기다.

이 단계에서 따로 만들 파일은 없다. 토크나이저는 Part 3의 `train.py` 안에 곧바로 녹여 넣을 거라서, 여기서는 그게 어떻게 동작하는지 미리 짚어두고 가는 게 목적이다.

### 캐릭터 단위 토큰화(Character-Level Tokenization)

가장 단순한 토크나이저를 쓴다. 등장하는 문자(character) 하나하나에 ID를 하나씩 부여하는 방식이다.

```python
text = open("../data/shakespeare.txt").read()
chars = sorted(set(text))
vocab_size = len(chars)  # 65 for Shakespeare

stoi = {c: i for i, c in enumerate(chars)}  # string to int
itos = {i: c for c, i in stoi.items()}      # int to string

def encode(s):
    return [stoi[c] for c in s]

def decode(ids):
    return "".join([itos[i] for i in ids])
```

```python
encode("Hello")  # [20, 43, 50, 50, 53]
decode([20, 43, 50, 50, 53])  # "Hello"
```

이게 끝이다. 외부 라이브러리도, 사전학습 모델도 필요 없다. 셰익스피어 텍스트에는 알파벳, 숫자, 구두점, 줄바꿈을 합쳐 65개의 고유 문자가 들어있다. 문자 하나가 토큰 하나가 되는 것이다.

이 토크나이저는 데이터 로딩 코드에 그대로 박혀 들어가기 때문에 별도의 토크나이저 파일을 따로 작성할 필요가 없다.

### 왜 캐릭터 단위인가?

캐릭터 단위 토큰화는 셰익스피어 같은 작은 데이터셋(약 100만 글자)에서 잘 동작한다. 이유는 다음과 같다.

- **아주 작은 어휘 크기(vocabulary)** (65 토큰) — 모델의 임베딩(embedding) 테이블과 출력 레이어가 작아진다
- **빽빽한 통계** — 가능한 바이그램(bigram) 조합이 65² = 4,225개뿐이라 데이터 안에서 모든 바이그램이 충분히 여러 번 등장한다
- **외부 의존성 없음** — 별도 라이브러리가 필요 없다

이게 생각보다 훨씬 중요하다. GPT-2의 토크나이저(BPE, 50,257 토큰)로 셰익스피어를 토큰화하면 약 33만 8천 토큰이 나오고, 그중 고유 토큰 종류는 약 1만 1,700개에 이른다. 토큰 바이그램 대부분이 한두 번밖에 등장하지 않아서 — 데이터가 너무 희소(sparse)해서 모델이 시퀀스 패턴을 학습할 수가 없다. 실제로 테스트해봤다. 셰익스피어에 BPE를 쓰면 학습 손실(loss)이 약 6.3(유니그램 빈도 수준)에서 멈춰서 더 이상 떨어지지 않는다. 캐릭터 단위로 바꾸면 약 1.5까지 내려간다.

### 트레이드오프

캐릭터 단위 토큰화는 큰 데이터셋으로 가면 한계가 명확하다.

- **시퀀스 길이가 BPE 대비 약 3배 길다** (샘플당 연산량이 늘어난다)
- **모델이 철자(spelling)를 처음부터 배워야 한다** — "단어"라는 개념 자체가 없다
- **예측 가능한 패턴에 모델 용량을 낭비한다** — `t-h-e`는 거의 항상 함께 등장하지만, 모델은 이 세 글자를 한 글자씩 따로 예측해야 한다

데이터셋이 커지면(TinyStories, OpenWebText 같은 것들) **바이트 페어 인코딩(Byte-Pair Encoding, BPE)**으로 갈아타게 된다. BPE는 자주 등장하는 문자 시퀀스를 하나의 토큰으로 묶어주는 방식이다. GPT-2는 50,257개 토큰의 BPE 토크나이저를 쓴다. `tiktoken`으로 손쉽게 쓸 수 있다.

```python
import tiktoken
enc = tiktoken.get_encoding("gpt2")
tokens = enc.encode("Hello, world!")  # [15496, 11, 995, 0]
text = enc.decode(tokens)             # "Hello, world!"
```

하지만 셰익스피어를 다루는 이 워크숍에서는 캐릭터 단위가 정답이다.

### 모델과 어떻게 연결되는가

어휘 크기는 모델 아키텍처에서 두 가지를 직접적으로 결정한다.

1. **임베딩 테이블** — `nn.Embedding(vocab_size, n_embd)`은 각 토큰 ID를 학습 가능한 벡터로 매핑한다. vocab_size=65일 때는 아주 작다(65 × 384 = 24,960 파라미터). GPT-2의 어휘 크기인 50,257을 쓰면 50,257 × 384 = 1,930만 파라미터가 되어 — 모델 전체 파라미터의 거의 절반을 차지하게 된다.

2. **출력 레이어** — `nn.Linear(n_embd, vocab_size)`는 가능한 다음 토큰들에 대한 확률 분포를 출력한다. 토큰이 65개라면 모델은 65개 중에서 고른다. 50,257개라면 5만 개가 넘는 클래스에 예측 확률을 분산시켜야 한다.

### 핵심 정리

- 토큰화는 텍스트 ↔ 정수 시퀀스 간 변환이다
- 우리는 캐릭터 단위 방식을 쓴다. 고유 문자마다 ID를 하나씩 부여한다(`stoi`/`itos` 매핑)
- 어휘 크기는 데이터셋과 맞아야 한다 — 작은 데이터셋에 5만 어휘를 쓰면 대부분의 토큰 패턴이 너무 희소해서 학습이 안 된다
- 캐릭터 단위는 작은 실험에 적합하다. 큰 데이터셋에서는 BPE가 필요하다
- 어휘 크기는 모델 크기(임베딩 테이블)와 학습 난이도(출력 분포 폭)에 직접 영향을 준다

---

## Part 2: 트랜스포머

이 파트가 워크숍의 핵심임. 여기서는 PyTorch로 GPT 모델 아키텍처 전체를 처음부터 직접 작성하게 됨.

### 큰 그림

GPT는 **자기회귀 언어 모델(autoregressive language model)** 임. 토큰 시퀀스가 주어지면 다음 토큰을 예측하고, 이 예측을 루프로 반복하면 텍스트 생성이 됨.

아키텍처는 동일한 **트랜스포머 블록(transformer block)** 들을 쌓아 올린 구조이고, 각 블록은 다음 네 가지로 구성됨.

1. **멀티 헤드 셀프 어텐션(multi-head self-attention)** — 각 토큰이 이전 토큰들 전체를 볼 수 있게 해줌
2. **피드 포워드 네트워크(feed-forward network, MLP)** — 각 위치를 독립적으로 처리함
3. **잔차 연결(residual connection)** — 각 서브 레이어의 출력에 원래 입력을 다시 더해줌
4. **레이어 정규화(layer normalization)** — 학습을 안정화시킴

### 직접 작성하기: `model.py`

스크래치패드 안에 `model.py` 라는 새 파일을 만들자. 이 절을 읽어가면서 클래스를 하나씩 추가하면 됨. 다 끝나면 이 파일에는 `GPTConfig`, `CausalSelfAttention`, `MLP`, `Block`, `GPT` 가 들어 있게 됨.

#### 설정

```python
from dataclasses import dataclass

@dataclass
class GPTConfig:
    vocab_size: int = 65       # character-level: 65 unique chars in Shakespeare
    block_size: int = 256      # max sequence length (context window)
    n_layer: int = 6           # number of transformer blocks
    n_head: int = 6            # number of attention heads
    n_embd: int = 384          # embedding dimension
```

`vocab_size` 는 토크나이저에서 나옴(셰익스피어 데이터의 경우 65 글자). `block_size` 는 모델이 한 번에 볼 수 있는 토큰의 최대 개수임. `n_embd` 는 모델의 폭(width) 으로, 모든 은닉 상태(hidden state) 가 이 크기의 벡터가 됨.

#### 임베딩

```python
import torch
import torch.nn as nn

class GPT(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(config.vocab_size, config.n_embd),   # token embeddings
            wpe = nn.Embedding(config.block_size, config.n_embd),   # position embeddings
            h = nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
            ln_f = nn.LayerNorm(config.n_embd),
        ))
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
        # weight tying: the output projection shares weights with the token embeddings
        self.transformer.wte.weight = self.lm_head.weight
```

임베딩 테이블은 두 개임.

- **`wte`** (word token embedding): 각 토큰 ID를 학습 가능한 벡터로 매핑함. 크기: `[65, 384]`
- **`wpe`** (word position embedding): 각 위치(0부터 255까지) 를 학습 가능한 벡터로 매핑함. 크기: `[256, 384]`

**가중치 묶기(weight tying)**: 토큰 → 임베딩으로 매핑하는 행렬을 그대로 (전치한 형태로) 출력 단의 임베딩 → 로짓(logit) 매핑에도 재사용함. 파라미터를 줄여줄 뿐 아니라 학습에도 도움이 됨 — 모델의 입력 토큰 표현과 출력 토큰 표현이 일관되도록 강제하기 때문임. 어휘가 65개뿐인 우리 경우엔 절약 효과가 미미하지만, 어휘가 큰 모델에서는 큰 차이를 만드는 표준적인 기법임.

#### 순전파(forward pass)

```python
    def forward(self, idx, targets=None):
        B, T = idx.shape
        pos = torch.arange(0, T, device=idx.device)

        tok_emb = self.transformer.wte(idx)    # (B, T, n_embd)
        pos_emb = self.transformer.wpe(pos)    # (T, n_embd)
        x = tok_emb + pos_emb                  # (B, T, n_embd) — broadcasting adds position info

        for block in self.transformer.h:
            x = block(x)

        x = self.transformer.ln_f(x)
        logits = self.lm_head(x)               # (B, T, vocab_size)

        loss = None
        if targets is not None:
            loss = nn.functional.cross_entropy(
                logits.view(-1, logits.size(-1)),
                targets.view(-1)
            )
        return logits, loss
```

```
token IDs (B, T)
    │
    ▼
┌─────────┐     ┌─────────┐
│   wte   │     │   wpe   │
│ [65,384]│     │[256,384]│
└─────────┘     └─────────┘
    │               │
    ▼               ▼
  tok_emb    +   pos_emb      → x (B, T, 384)
                                  │
                                  ▼
                          ┌──────────────┐
                          │ Block × 6    │
                          └──────────────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │  LayerNorm   │
                          │   lm_head    │  Linear: 384 → 65
                          └──────────────┘
                                  │
                                  ▼
                          logits (B, T, 65)
```

위치 임베딩(position embedding) 을 토큰 임베딩에 더해주는 것 — 이것이 바로 모델이 단어 순서를 인식하게 되는 방식임. 위치 임베딩이 없다면 "the dog bit the man" 과 "the man bit the dog" 가 모델 입장에서는 똑같이 보임.

#### 셀프 어텐션

각 토큰이 시퀀스 내 모든 이전 토큰을 어텐드(attend, 주목)하게 해주는 메커니즘임.

```python
class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config.n_embd % config.n_head == 0
        self.c_attn = nn.Linear(config.n_embd, 3 * config.n_embd)  # Q, K, V projections
        self.c_proj = nn.Linear(config.n_embd, config.n_embd)       # output projection
        self.n_head = config.n_head
        self.n_embd = config.n_embd

    def forward(self, x):
        B, T, C = x.shape
        qkv = self.c_attn(x)
        q, k, v = qkv.split(self.n_embd, dim=2)

        # reshape for multi-head: (B, T, C) → (B, n_head, T, head_dim)
        head_dim = C // self.n_head
        q = q.view(B, T, self.n_head, head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, head_dim).transpose(1, 2)

        # attention with causal mask (each token can only attend to previous tokens)
        y = torch.nn.functional.scaled_dot_product_attention(
            q, k, v, is_causal=True
        )

        y = y.transpose(1, 2).contiguous().view(B, T, C)
        return self.c_proj(y)
```

```
x (B, T, 384)
    │
    ▼
┌─────────┐
│  c_attn │  one Linear → split into Q, K, V
└─────────┘
    │
    ▼
┌─────────────────────────────┐
│  split into 6 heads         │  each head: (B, T, 64)
│                             │
│  Q @ K^T / sqrt(64)         │  similarity scores
│  mask future positions      │  causal: can only look back
│  softmax → weights          │
│  weights @ V                │  weighted combination
│                             │
│  head1  head2  ...  head6   │
└─────────────────────────────┘
    │
    ▼  concatenate all heads
┌─────────┐
│  c_proj │  project back to 384 dims
└─────────┘
    │
    ▼
output (B, T, 384)
```

하나씩 뜯어보면 이렇다.

1. **Q, K, V 투영(projection)**: 단일 선형 레이어 하나가 입력을 세 개의 행렬 — Query, Key, Value — 로 투영함. 각각의 형상은 `(B, T, n_embd)`.

2. **멀티 헤드 리셰이프(reshape)**: 임베딩 차원을 `n_head` 개의 별개 헤드(head) 로 쪼갬. 각 헤드의 차원은 `head_dim = n_embd / n_head = 64` 가 됨. 이렇게 하면 모델이 입력의 서로 다른 측면들을 병렬로 어텐드할 수 있음.

3. **스케일드 닷 프로덕트 어텐션(scaled dot-product attention)**: 각 쿼리(query) 위치에 대해 모든 키(key) 위치와의 유사도 점수를 계산하고, 미래 위치는 마스킹(masking) 한 뒤(causal), 소프트맥스(softmax) 를 적용해 그 결과로 값(value) 들을 가중 평균함. 수식으로 쓰면 `softmax(QK^T / sqrt(head_dim)) @ V` 임.

4. **인과적 마스킹(causal masking)** (`is_causal=True`): 위치 `i` 는 위치 `0..i` 까지만 어텐드할 수 있음. 이렇게 해야 학습 중에 모델이 미래 토큰을 슬쩍 보고 "치팅" 하는 것을 막을 수 있음. 이 인과성 덕분에 GPT가 **자기회귀(autoregressive)** 모델이 됨.

5. **출력 투영(output projection)**: 모든 헤드를 이어붙이고 다시 `n_embd` 차원으로 투영함.

#### 왜 멀티 헤드인가?

384 차원 헤드 하나 대신 64 차원짜리 헤드 6개를 쓰면, 모델이 서로 다른 관계들을 동시에 추적할 수 있음. 한 헤드는 자음 뒤에 어떤 모음이 오는지를 보고, 다른 헤드는 줄바꿈 패턴을 보고, 또 다른 헤드는 직전 문맥에 집중하는 식으로 말이다.

#### MLP 블록

```python
class MLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.c_fc = nn.Linear(config.n_embd, 4 * config.n_embd)
        self.gelu = nn.GELU(approximate='tanh')
        self.c_proj = nn.Linear(4 * config.n_embd, config.n_embd)

    def forward(self, x):
        x = self.c_fc(x)       # project up: 384 → 1536
        x = self.gelu(x)       # non-linearity
        return self.c_proj(x)  # project back down: 1536 → 384
```

```
x (B, T, 384)
    │
    ▼
┌─────────┐
│  c_fc   │  Linear: 384 → 1536 (expand 4x)
└─────────┘
    │
    ▼
┌─────────┐
│  GELU   │  non-linearity
└─────────┘
    │
    ▼
┌─────────┐
│  c_proj │  Linear: 1536 → 384 (project back)
└─────────┘
    │
    ▼
output (B, T, 384)
```

MLP는 각 위치(position) 에 독립적으로 적용됨. 표현(representation) 을 임베딩 차원의 4배까지 늘렸다가, 비선형 함수(GELU) 를 통과시킨 뒤, 다시 원래 차원으로 줄여줌. 모델의 "사고" 가 대부분 일어나는 곳이 바로 이 MLP임 — 어텐션이 정보를 모아주면 MLP가 그것을 처리하는 구조임.

**왜 ReLU 대신 GELU 인가?** GELU(Gaussian Error Linear Unit) 는 ReLU보다 매끄러움. 0에서 딱 잘리는 하드 컷오프(hard cutoff) 가 없기 때문에 그래디언트(gradient) 흐름에 도움이 됨. GPT-2는 속도를 위해 `tanh` 근사를 사용함.

#### 트랜스포머 블록

```python
class Block(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.n_embd)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embd)
        self.mlp = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))   # attention with residual connection
        x = x + self.mlp(self.ln_2(x))    # MLP with residual connection
        return x
```

```
x (B, T, 384)
    │
    ├───────────────────┐
    ▼                   │
┌──────────┐            │
│ LayerNorm│            │
└──────────┘            │
    │                   │
    ▼                   │
┌──────────┐            │
│ Self-Attn│            │
└──────────┘            │
    │                   │
    ▼                   │
  + ◄───────────────────┘  residual connection
    │
    ├───────────────────┐
    ▼                   │
┌──────────┐            │
│ LayerNorm│            │
└──────────┘            │
    │                   │
    ▼                   │
┌──────────┐            │
│   MLP    │            │
└──────────┘            │
    │                   │
    ▼                   │
  + ◄───────────────────┘  residual connection
    │
    ▼
output (B, T, 384)
```

핵심 디자인 선택은 두 가지임.

1. **Pre-norm** (어텐션/MLP 뒤가 아니라 앞에서 LayerNorm): 각 서브 레이어로 들어가는 입력을 정규화함으로써 학습을 안정화시킴. 원조 트랜스포머 논문은 post-norm 방식을 썼지만, 지금은 pre-norm이 표준임.

2. **잔차 연결(residual connection)** (`x = x + sublayer(x)`): 입력을 출력에 다시 더해줌. 역전파(backpropagation) 때 그래디언트가 네트워크를 그대로 통과해 흐를 수 있게 해주기 때문에, 깊은 네트워크도 학습 가능해짐. 잔차 연결이 없다면 6층짜리 네트워크조차 훨씬 학습이 어려움.

#### 파라미터 개수

```python
config = GPTConfig()
model = GPT(config)
n_params = sum(p.numel() for p in model.parameters())
print(f"Parameters: {n_params / 1e6:.1f}M")  # ~10.8M
```

파라미터들은 어디에 모여 있을까?

- 토큰 임베딩: `65 × 384 = 25K` (글자 단위 어휘여서 매우 작음 — lm_head 와 공유됨)
- 위치 임베딩: `256 × 384 = 98K`
- 트랜스포머 블록 하나당: `~1.8M` (어텐션: 4 × 384² = 590K, MLP: 2 × 384 × 1536 = 1.2M, 정규화: 무시 가능한 수준)
- 6개 블록: `~10.6M`
- 합계: `~10.8M`

거의 모든 파라미터가 임베딩이 아니라 트랜스포머 블록에 모여 있다는 점에 주목하자. GPT-2의 5만 어휘 기준으로는 임베딩 테이블이 50,257 × 384 = 19.3M 이 되어 모델 전체 크기의 거의 두 배에 달함. 그래서 어휘 크기(vocab size) 가 중요한 것임.

### 핵심 정리

- GPT는 동일한 트랜스포머 블록을 쌓아 올린 스택임
- 각 블록 구성: LayerNorm → Self-Attention → Residual → LayerNorm → MLP → Residual
- 셀프 어텐션은 각 토큰이 이전 토큰들 전부를 보게 해줌(인과적 마스킹은 미래를 보지 못하게 막음)
- 멀티 헤드 어텐션은 여러 어텐션 패턴을 병렬로 돌림
- 잔차 연결과 레이어 정규화 덕분에 깊은 네트워크도 학습 가능해짐
- 입력 임베딩과 출력 투영 사이의 가중치 묶기로 파라미터를 줄일 수 있음

---

## Part 3: 학습 루프

이제 모델은 갖췄다. 다음은 이 모델에게 언어를 가르치는 일이다. 학습 루프는 모델이 실제로 배우는 곳이며, 여기서 내리는 모든 결정이 모델이 수렴할지 아니면 헛소리로 발산할지를 좌우한다.

### 학습 목표

GPT는 **다음 토큰 예측(next-token prediction)** 으로 학습한다. 토큰 시퀀스 `[t0, t1, ..., tn]` 가 주어졌을 때 `[t1, t2, ..., tn+1]` 을 예측하는 식이다. 손실 함수(loss function)는 모델이 예측한 확률 분포와 실제 다음 토큰 사이의 교차 엔트로피(cross-entropy)다.

이건 자기지도(self-supervised) 학습이다. 정답 라벨이 데이터 자체에서 나오기 때문이다. 모든 텍스트는 한 칸씩 밀린 채로 입력이자 동시에 타깃이 된다.

### 직접 작성하기: `train.py`

스크래치패드에 `train.py` 라는 새 파일을 만든다. 이 파일은 (Part 2에서 작성한) `model.py` 와 (Part 4에서 작성할) `generate.py` 에서 임포트한다. 샘플 생성 부분은 일단 건너뛰고, Part 4가 끝난 뒤에 다시 돌아와서 추가하면 된다.

이번 절을 읽으면서 아래 조각들을 하나씩 `train.py` 에 추가하자.

#### Step 1: 데이터 로딩 (문자 단위)

```python
import torch

def load_data(filepath, block_size, batch_size, device):
    with open(filepath, "r") as f:
        text = f.read()

    chars = sorted(set(text))
    vocab_size = len(chars)
    stoi = {c: i for i, c in enumerate(chars)}
    itos = {i: c for c, i in stoi.items()}

    tokens = torch.tensor([stoi[c] for c in text], dtype=torch.long)
    print(f"Dataset: {len(tokens):,} chars, vocab size: {vocab_size}")

    def get_batch(split_tokens):
        ix = torch.randint(len(split_tokens) - block_size - 1, (batch_size,))
        x = torch.stack([split_tokens[i:i + block_size] for i in ix]).to(device)
        y = torch.stack([split_tokens[i + 1:i + block_size + 1] for i in ix]).to(device)
        return x, y

    n = int(0.9 * len(tokens))
    get_train = lambda: get_batch(tokens[:n])
    get_val = lambda: get_batch(tokens[n:])
    return get_train, get_val, vocab_size, stoi, itos
```

각 배치는 다음과 같이 구성된다.
- `batch_size` 개의 시작 위치를 무작위로 뽑는다
- `x`: 위치 `i` 부터 `i + block_size` 까지의 문자 (입력)
- `y`: 위치 `i+1` 부터 `i + block_size + 1` 까지의 문자 (타깃, 한 칸 밀린 값)

함수는 배치 생성기와 함께 `stoi`/`itos` 매핑도 반환한다. 텍스트 생성 단계에서 필요하기 때문이다.

#### Step 2: 디바이스 설정

```python
def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")     # Apple Silicon GPU
    elif torch.cuda.is_available():
        return torch.device("cuda")    # NVIDIA GPU
    return torch.device("cpu")
```

Apple Silicon 맥북에서는 MPS가 CPU 대비 대략 2~3배 정도 빠르다.

#### Step 3: 학습률 스케줄

```python
import math

def get_lr(step, warmup_steps, max_steps, max_lr, min_lr):
    if step < warmup_steps:
        return max_lr * (step + 1) / warmup_steps
    if step >= max_steps:
        return min_lr
    progress = (step - warmup_steps) / (max_steps - warmup_steps)
    return min_lr + 0.5 * (max_lr - min_lr) * (1 + math.cos(math.pi * progress))
```

두 단계로 나뉜다.

1. **워밍업(warmup)** (처음 ~100 스텝): 학습률을 0에 가까운 값에서 `max_lr` 까지 점진적으로 끌어올린다. 옵티마이저(optimizer)가 큰 업데이트를 하기 전에 모멘트(moment) 추정값을 보정할 시간을 주는 단계다.

2. **코사인 감쇠(cosine decay)** (남은 스텝): 학습률을 부드럽게 줄여나간다. 초반에는 큰 폭으로 업데이트해 탐색하고, 후반에는 작은 폭으로 미세 조정한다.

#### Step 4: 옵티마이저

```python
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
```

셰익스피어 데이터로 문자 단위 학습을 할 때는 평범한 `AdamW` 에 `lr=1e-3`, 가벼운 가중치 감쇠(weight decay)만 줘도 충분히 잘 돌아간다. 풀 GPT-2 레시피(파라미터 그룹별 분리된 weight decay, betas=(0.9, 0.95), weight_decay=0.1)는 대규모 BPE 학습용이라 여기서는 오버킬이다.

#### Step 5: 전체 학습 루프

```python
import json
from tqdm import tqdm

def train(data_path, max_steps=5000, batch_size=64,
          n_layer=6, n_head=6, n_embd=384, block_size=256):
    device = get_device()
    print(f"Using device: {device}")

    get_train_batch, get_val_batch, vocab_size, stoi, itos = load_data(
        data_path, block_size, batch_size, device
    )

    config = GPTConfig(
        vocab_size=vocab_size,
        block_size=block_size,
        n_layer=n_layer,
        n_head=n_head,
        n_embd=n_embd,
    )
    model = GPT(config).to(device)
    print(f"Model: {n_layer}L/{n_head}H/{n_embd}D, "
          f"{sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params")

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)

    max_lr = 1e-3
    min_lr = max_lr * 0.1
    warmup_steps = 100

    loss_log = {"steps": [], "train": [], "val": []}

    pbar = tqdm(range(max_steps), desc="Training")
    for step in pbar:
        # --- validation loss ---
        if step % 100 == 0:
            model.eval()
            with torch.no_grad():
                val_losses = []
                for _ in range(20):
                    x, y = get_val_batch()
                    _, loss = model(x, y)
                    val_losses.append(loss.item())
                val_loss = sum(val_losses) / len(val_losses)
                tqdm.write(f"Step {step:5d} | val loss: {val_loss:.4f}")
            model.train()

        # --- update learning rate ---
        lr = get_lr(step, warmup_steps, max_steps, max_lr, min_lr)
        for param_group in optimizer.param_groups:
            param_group["lr"] = lr

        # --- training step ---
        x, y = get_train_batch()
        _, loss = model(x, y)
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        pbar.set_postfix(loss=f"{loss.item():.4f}", lr=f"{lr:.2e}")

        # --- log loss ---
        loss_log["steps"].append(step)
        loss_log["train"].append(loss.item())
        if step % 100 == 0:
            loss_log["val"].append(val_loss)

        # --- generate sample ---
        if step > 0 and step % 100 == 0:
            model.eval()
            sample = generate(model, "To be or not", stoi, itos,
                            max_new_tokens=100, temperature=0.8)
            tqdm.write(f"\n--- Step {step} sample ---\n{sample}\n---\n")
            model.train()

        # --- save checkpoint ---
        if step > 0 and step % 1000 == 0:
            torch.save({
                "step": step,
                "model_state_dict": model.state_dict(),
                "config": config,
                "stoi": stoi,
                "itos": itos,
            }, f"checkpoint_{step}.pt")

    # --- save final checkpoint and loss log ---
    torch.save({
        "step": max_steps,
        "model_state_dict": model.state_dict(),
        "config": config,
        "stoi": stoi,
        "itos": itos,
    }, "checkpoint_final.pt")

    with open("loss_log.json", "w") as f:
        json.dump(loss_log, f)

    return model, stoi, itos
```

#### Step 6: 진입점

터미널에서 바로 실행할 수 있도록 `train.py` 맨 아래에 다음을 추가한다.

```python
if __name__ == "__main__":
    train("../data/shakespeare.txt")
```

이렇게 하면 기본 설정(6L/6H/384D, 5000 스텝)과 함께 포함된 셰익스피어 데이터셋으로 학습 함수가 실행된다. 다른 인자를 넘겨서 모델을 바꿀 수도 있다.

```python
if __name__ == "__main__":
    import sys
    data_path = sys.argv[1] if len(sys.argv) > 1 else "../data/shakespeare.txt"
    train(data_path)
```

#### 각 부분이 하는 일

**검증 손실(validation loss)**: 100 스텝마다 홀드아웃(held-out) 데이터로 평가한다. 학습 손실은 떨어지는데 검증 손실이 올라간다면 과적합(overfitting)이 시작된 것이다.

**그래디언트 클리핑(gradient clipping)** (`clip_grad_norm_`): 그래디언트 전체 크기를 1.0으로 제한한다. 가끔 튀는 큰 그래디언트가 가중치를 폭주시키는 걸 막아준다.

**샘플 생성**: 100 스텝마다 텍스트를 생성해서 모델이 배우는 과정을 눈으로 확인한다. 무작위 문자 → 무작위 단어 → 셰익스피어풍 텍스트 순으로 변해가는 게 보인다.

**체크포인팅(checkpointing)**: 모델 상태를 주기적으로 저장한다. 체크포인트에는 `stoi`/`itos` 도 함께 저장되므로, 원본 데이터 없이도 저장된 모델만으로 텍스트를 생성할 수 있다. 학습이 끝나면 최종 체크포인트가 `checkpoint_final.pt` 로 저장된다.

**손실 로그**: 학습 손실과 검증 손실을 `loss_log.json` 에 저장해두면 학습이 끝난 뒤 손실 곡선을 그릴 수 있다 (Part 5 참고).

### 손실 값이 의미하는 것 (문자 단위, vocab=65)

- **~4.2**: 무작위 (학습 안 됨). `ln(65) ≈ 4.17`
- **~3.3**: 문자 빈도(어떤 글자가 자주 나오는지)를 학습한 단계
- **~2.5**: 흔한 바이그램("th", "he", "in")까지 학습한 단계
- **~1.5-2.0**: 알아볼 수 있는 단어와 셰익스피어풍 구조를 생성하는 단계
- **~1.0-1.2**: 좋은 품질 — 인물 이름, 줄바꿈이 있는 운문을 생성
- **<1.0**: 학습 데이터를 외우고 있을 가능성이 큼

### 모델이 학습하는 모습 지켜보기

실제 학습 한 번이 어떻게 굴러가는지 보자 (6L/6H/384D, batch_size=64, M3 Pro). 프롬프트는 항상 "To be or not"이다.

**Step 200** (val loss: ~3.5) — 무작위 문자, 단어 없음:
```
To be or notis p ce mei odorethleedetire'ilethed ye m arkesothir fnon b tigb'i.
```

**Step 800** (val loss: ~1.8) — 단어가 형성되고 인물 이름이 등장:
```
To be or not men, and my lord.

ROMEO:
Thou sir, do content the he, stray, there ir;
```

**Step 1000** (val loss: 1.64) — 일관된 어구, 셰익스피어 구조:
```
To be or nothing are good men,
The profent of little, our actory.

CORIOLANUS:
Is it now of your many death?
```

**Step 2400** (val loss: ~1.60) — 최고 품질. 그럴듯한 셰익스피어:
```
To be or not to be some of you shall know
That everlature by Romeo: what news,
Which you had knock'd my part to speak
```

**Step 3500** (val loss: 2.34) — 과적합. 여전히 유창하지만 창의성이 떨어짐:
```
To be or nothing, take me but most profane,
That offer them not amish. If I defeath
Is not a puggival and self,
```

### 과적합: 학습 손실 vs 검증 손실

파라미터 1,000만 개짜리 모델을 100만 자 정도밖에 안 되는 셰익스피어 데이터로 돌리면, 모델은 일반적인 패턴을 배우는 대신 학습 데이터를 그대로 외우는 **과적합** 에 빠진다. 이 현상은 다음처럼 명확하게 드러난다.

```
Step   500 | val loss: 2.14   ← 빠르게 떨어짐, 구조를 학습 중
Step  1000 | val loss: 1.64   ← 여전히 개선 중
Step  1500 | val loss: 1.57   ← 베스트 구간
Step  2000 | val loss: 1.59   ← 정체 시작
Step  2500 | val loss: 1.71   ← 검증 손실이 올라감 — 과적합
Step  3000 | val loss: 1.98   ← 점점 나빠짐
Step  3500 | val loss: 2.34   ← 완전히 외워버림 (학습 손실은 0.54)
```

**최고 모델** 은 5000 스텝이 아니라 1500~2000 스텝 근처(val loss ~1.57)에 있다. 그 이후로는 매 스텝마다 새로운 텍스트를 생성하는 능력이 *나빠진다*. 단지 학습 데이터를 더 잘 암송하게 될 뿐이다.

#### 과적합은 왜 생기나?

모델은 파라미터 **1,000만 개** 로 **약 100만 자** 짜리 데이터를 학습한다. 즉 데이터 대비 파라미터 비율이 10:1이다. 이 정도면 모델이 학습 셋의 모든 문자를 외우고도 남는 용량을 가진 셈이다. 해법은 항상 같다. **데이터를 더 많이 쓰거나** 아니면 **모델을 더 작게** 만드는 것.

#### 어떻게 대응할까

이 워크숍에서는 과적합이 의도된 현상이고 그대로 둬도 괜찮다. 중요한 개념을 직접 보여주기 때문이다. 실제 환경이라면 다음처럼 처리한다.

1. **데이터를 더 쓴다** — TinyStories(4억 7,600만 토큰) 정도 되면 1,000만 파라미터 모델이 훨씬 오래 학습할 수 있다
2. **더 작은 모델을 쓴다** — 2L/2H/128D (~50만 파라미터) 모델은 셰익스피어로도 훨씬 천천히 과적합된다
3. **드롭아웃(dropout)을 추가한다** — 학습 중 활성값을 무작위로 0으로 만들어 정규화(regularization) 효과를 낸다
4. **일찍 멈춘다(early stopping)** — 검증 손실이 가장 낮을 때의 체크포인트를 저장해두고 그것을 사용한다

### 맥북에서의 일반적인 학습 (문자 단위 셰익스피어)

| 모델 | 파라미터 | 배치 크기 | 스텝 | 시간 (M3 Pro) | 베스트 Val Loss | 과적합 시점 |
|-------|--------|-----------|-------|---------------|---------------|-------------|
| 6L/6H/384D | ~10M | 64 | 5,000 | ~45 min | ~1.7 (step 2500) | ~step 1500 |
| 4L/4H/256D | ~4M | 64 | 5,000 | ~20 min | ~1.6 (step 3000) | ~step 2000 |
| 2L/2H/128D | ~0.5M | 64 | 5,000 | ~5 min | ~1.8 (step 5000) | 거의 안 됨 |

6L 모델은 가장 빨리 좋은 샘플을 뽑지만 가장 빨리 과적합된다. 2L 모델은 학습이 빠르고 거의 과적합되지 않지만 출력 품질이 낮다. 이게 바로 근본적인 트레이드오프다. **모델 용량 vs 데이터 크기**.

처음에는 6L/6H/384D 설정으로 시작하자. M3 Pro에서 batch_size=64로 돌리면 초당 약 1.9 이터레이션이 나온다.

### 핵심 정리

- 목표는 교차 엔트로피 손실 기반의 다음 문자 예측이다
- 작은 데이터셋에서는 문자 단위 토크나이제이션이 가장 잘 통한다 — BPE 어휘는 너무 희소하다
- AdamW + lr=1e-3 + 코사인 감쇠 조합은 좋은 출발점이다
- 1.0 그래디언트 클리핑은 학습 불안정을 막아준다
- 학습 도중 샘플을 생성해보는 것이 진행 상황을 확인하는 가장 좋은 방법이다
- **학습 손실과 검증 손실의 격차를 주시하라** — 검증 손실이 올라가기 시작하면 과적합이다
- 최고 모델은 학습 손실이 가장 낮은 모델이 아니라, 검증 손실이 가장 낮은 모델이다

---

## Part 4: 텍스트 생성

모델은 이미 학습이 끝났다. 이제 글을 쓰게 만들 차례다. GPT 의 텍스트 생성은 **자기회귀(autoregressive)** 방식으로 동작한다. 토큰을 하나 만들어서 입력 끝에 붙이고, 다시 모델에 넣어 다음 토큰을 만드는 과정을 반복하는 것이다.

스크래치패드에 `generate.py` 라는 새 파일을 만들자. 다 작성한 뒤에는 `train.py` 로 돌아가서 맨 위에 `from generate import generate` 를 추가한다. 이렇게 하면 Part 3 에서 건너뛰었던, 학습 도중 샘플을 뽑아 보는 기능이 활성화된다.

### 가장 단순한 방법: 그리디 디코딩(Greedy Decoding)

매번 가장 확률이 높은 토큰만 고르는 방식이다.

```python
def generate_greedy(model, idx, max_new_tokens):
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -model.config.block_size:]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :]
        next_token = logits.argmax(dim=-1, keepdim=True)
        idx = torch.cat([idx, next_token], dim=1)
    return idx
```

결정론적(deterministic)이라서 같은 프롬프트를 넣으면 항상 같은 출력이 나온다. 가장 확률이 높은 다음 토큰이 다시 다음의 가장 확률 높은 토큰을 끌어내는 식으로 자기 강화가 일어나기 때문에, 결과물은 반복적이고 지루한 경향이 있다.

### 온도(Temperature)

소프트맥스(softmax) 를 적용하기 전에 로짓(logit) 을 스케일링하는 기법이다. 온도가 높을수록 더 무작위하게, 낮을수록 더 결정론적으로 동작한다.

```python
logits = logits / temperature
```

수식으로 보면, 소프트맥스는 `exp(logit_i) / sum(exp(logit_j))` 를 계산한다. 모든 로짓을 온도로 나누면 분포가 다음과 같이 바뀐다.
- **T = 1.0**: 원래 확률 그대로
- **T → 0**: 그리디(argmax) 에 가까워짐
- **T > 1.0**: 분포를 평탄하게 만들어 희귀한 토큰에 더 많은 기회를 줌
- **T = 0.7~0.9**: 일관성 있으면서도 다양성이 있는 텍스트를 위한 일반적인 스윗스폿

### Top-k 샘플링

확률 상위 k개의 토큰만 후보로 두고, 나머지는 전부 `-inf` 로 바꾸는 방법이다.

```python
if top_k > 0:
    values, _ = torch.topk(logits, top_k)
    logits[logits < values[:, -1:]] = float("-inf")
```

이렇게 하면 모델이 극도로 확률 낮은 토큰을 뽑아 버리는 사고를 막을 수 있다. 문자 단위 모델(어휘 크기 65) 기준으로는 `top_k=40` 정도가 합리적이다. 거의 모든 문자를 후보에 두면서도 정말 가능성 없는 것들만 걸러 내는 수준이다.

### 완성된 generate 함수

```python
@torch.no_grad()
def generate(model, prompt, stoi, itos, max_new_tokens=200, temperature=0.8, top_k=40):
    device = next(model.parameters()).device
    tokens = [stoi[c] for c in prompt if c in stoi]
    idx = torch.tensor([tokens], dtype=torch.long, device=device)

    model.eval()
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -model.config.block_size:]
        logits, _ = model(idx_cond)
        logits = logits[:, -1, :] / temperature

        if top_k > 0:
            values, _ = torch.topk(logits, top_k)
            logits[logits < values[:, -1:]] = float("-inf")

        probs = torch.softmax(logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        idx = torch.cat([idx, next_token], dim=1)

    return "".join([itos[i] for i in idx[0].tolist()])
```

토큰 하나를 만드는 파이프라인은 다음과 같다.
1. 현재 시퀀스를 모델에 넣어 다음 위치의 로짓을 받는다
2. 온도 스케일링을 적용한다
3. top-k 로 필터링한다 (확률이 너무 낮은 토큰 제거)
4. 소프트맥스로 확률 분포로 바꾼다
5. `multinomial` 로 분포에서 샘플링한다
6. 뽑힌 토큰을 시퀀스에 붙이고 반복한다

`@torch.no_grad()` 는 그래디언트(gradient) 계산을 끈다. 추론에는 필요 없고, 메모리도 아낄 수 있다.

이 함수는 학습 데이터에서 만든 `stoi`/`itos` 매핑을 인자로 받는다. 문자가 토큰 ID 로, 또 그 반대로 어떻게 변환되는지를 정의하는 사전들이다.

#### 커맨드라인 인터페이스

`generate.py` 맨 아래에 다음 코드를 추가하면 터미널에서 직접 실행할 수 있다.

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate text from a trained GPT checkpoint")
    parser.add_argument("checkpoint", help="Path to checkpoint file (e.g. checkpoint_final.pt)")
    parser.add_argument("--prompt", default="To be or not", help="Starting text for generation")
    parser.add_argument("--max_new_tokens", type=int, default=200, help="Number of tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.8, help="Sampling temperature (lower = more deterministic)")
    parser.add_argument("--top_k", type=int, default=40, help="Only sample from top-k most likely tokens")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        torch.manual_seed(args.seed)

    checkpoint = torch.load(args.checkpoint, weights_only=False)
    config = checkpoint["config"]
    stoi = checkpoint["stoi"]
    itos = checkpoint["itos"]

    model = GPT(config)
    model.load_state_dict(checkpoint["model_state_dict"])

    output = generate(model, args.prompt, stoi, itos,
                      max_new_tokens=args.max_new_tokens,
                      temperature=args.temperature,
                      top_k=args.top_k)
    print(output)
```

### 시드(seed) 로 재현 가능하게 만들기

생성 과정에는 `torch.multinomial` 로 무작위 샘플링이 들어가기 때문에, 같은 프롬프트라도 매번 다른 결과가 나온다. 같은 결과를 다시 얻고 싶다면 생성 전에 시드를 고정하면 된다.

```python
torch.manual_seed(42)
print(generate(model, "To be or not", stoi, itos, temperature=0.8))
## seed=42 인 동안에는 매번 같은 출력이 나옴
```

커맨드라인에서는 이렇게 쓴다.
```bash
python generate.py checkpoint_final.pt --prompt "To be or not" --seed 42
```

### 설정값을 바꿔 가며 실험해 보기

```python
checkpoint = torch.load("checkpoint_final.pt", weights_only=False)
config = checkpoint["config"]
stoi = checkpoint["stoi"]
itos = checkpoint["itos"]

model = GPT(config)
model.load_state_dict(checkpoint["model_state_dict"])

## deterministic, repetitive
print(generate(model, "To be or not to be", stoi, itos, temperature=0.1))

## balanced
print(generate(model, "To be or not to be", stoi, itos, temperature=0.8))

## creative, potentially incoherent
print(generate(model, "To be or not to be", stoi, itos, temperature=1.5))
```

### 어떤 결과가 나올까

셰익스피어 데이터셋 위에서 6L/6H/384D 구성으로 학습했을 때 실제로 나온 샘플들이다.

#### Step 200 (val loss ~3.5) — 무작위에 가까운 문자열
```
To be or notis p ce mei odorethleedetire'ilethed ye m arkesothir fnon b tigb'i.
```

#### Step 1000 (val loss 1.64) — 단어와 구조가 보이기 시작
```
To be or nothing are good men,
The profent of little, our actory.

CORIOLANUS:
Is it now of your many death?
```

#### Step 2400 (val loss ~1.60) — 품질의 정점, 그럴듯한 셰익스피어 풍
```
To be or not to be some of you shall know
That everlature by Romeo: what news,
Which you had knock'd my part to speak
```

참고로 가장 좋은 출력은 step 1500~2500 구간에서 나온다. 그 이후에는 모델이 과적합(overfit) 되어 학습 데이터를 그대로 토해 내기 시작한다 (자세한 내용은 Part 3 참고).

### 핵심 정리

- 자기회귀 생성: 토큰을 하나 예측 → 붙이기 → 반복
- 그리디 디코딩은 결정론적이고 반복적이다
- 온도는 무작위성을 조절한다 (보통 0.7~0.9 가 적절)
- top-k 는 극도로 가능성 낮은 토큰을 잘라낸다
- 문자 단위 모델에서는 학습 도중 샘플을 뽑아 보면서 모델이 학습되는 과정을 직접 관찰할 수 있다

---

## Part 5: 모두 합쳐서 돌려보기

이제 모든 조각을 연결해서 실제 데이터로 학습을 돌리고, 곧 시작될 경연을 준비할 시간임.

### 프로젝트 구조

지금쯤 다음과 같은 파일들이 준비돼 있어야 함.

```
scratchpad/
├── model.py           # GPT architecture (Part 2)
├── train.py           # Tokenization + data loading + training loop (Parts 1 & 3)
└── generate.py        # Text generation (Part 4)
```

셰익스피어 데이터셋은 레포의 `data/shakespeare.txt` 에 이미 들어있어서 따로 다운로드할 필요 없음.

#### Google Colab 사용 시

로컬 환경 대신 Colab을 쓰는 경우:

1. [colab.research.google.com](https://colab.research.google.com/) 에서 새 노트북을 연다
2. **Runtime → Change runtime type → GPU (T4)** 로 GPU를 활성화한다
3. 첫 번째 셀에서 의존성을 설치한다:
   ```python
   !pip install -q torch numpy tqdm tiktoken
   ```
4. 셰익스피어 데이터를 받는다:
   ```python
   import urllib.request, os
   os.makedirs("data", exist_ok=True)
   urllib.request.urlretrieve(
       "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
       "data/shakespeare.txt"
   )
   ```
5. 모델, 학습 루프, 생성 코드를 노트북 셀에 작성한다 (문서에서 붙여넣어도 되고 직접 써도 됨)
6. 데이터 경로는 `"../data/shakespeare.txt"` 가 아니라 `"data/shakespeare.txt"` 를 사용한다

바로 실행 가능한 노트북도 레포의 `colab.ipynb` 에 함께 들어있음.

### Step 1: 학습

```bash
cd scratchpad
python train.py
```

기본 설정은 6L/6H/384D 모델(약 10M 파라미터)을 셰익스피어 데이터에서 batch_size=64로 5000 스텝 학습함. M3 Pro에서 약 45분 정도 걸림. 다음 정보를 볼 수 있음:

- 100스텝마다 검증 손실(val loss)과 생성 샘플
- 1000스텝마다 체크포인트(checkpoint)
- 마지막에 최종 체크포인트와 손실 로그(loss log)

### Step 2: 생성

```bash
python generate.py checkpoint_final.pt
```

이 스크립트는 체크포인트를 불러와서 세 개의 프롬프트로부터 텍스트를 생성함. 어떤 체크포인트 파일이든 인자로 넘길 수 있음.

### Step 3: 실험

기본 파이프라인이 동작하기 시작하면, 경연 전에 다음 실험들을 통해 직관(intuition)을 키워보자.

#### 모델 크기 vs. 품질

같은 데이터로 세 가지 모델을 학습시킨 뒤 출력 품질을 비교한다:

| 설정 | 파라미터 | n_layer | n_head | n_embd | 예상 손실 |
|--------|--------|---------|--------|--------|---------------|
| Tiny | ~0.5M | 2 | 2 | 128 | ~2.0 |
| Small | ~4M | 4 | 4 | 256 | ~1.5 |
| Medium | ~10M | 6 | 6 | 384 | ~1.2 |

`train.py` 의 `train()` 호출을 다음처럼 바꿔주면 됨:

```python
## tiny — fast, good for testing ideas
model, stoi, itos = train(data_path, n_layer=2, n_head=2, n_embd=128)

## medium — default, good baseline
model, stoi, itos = train(data_path, n_layer=6, n_head=6, n_embd=384)

## large — needs more data to justify
model, stoi, itos = train(data_path, n_layer=12, n_head=12, n_embd=768)
```

#### 컨텍스트 길이(Context Length)

`block_size=128` 과 `block_size=512` 로 각각 학습해본다. 컨텍스트가 길어지면 모델이 연(stanza) 전체와 운율 구조(rhyme scheme)를 더 잘 잡아내지만, 메모리를 더 많이 쓰게 됨(대신 batch_size를 줄여서 보정).

#### 학습률(Learning Rate)

`3e-4` (보수적), `1e-3` (기본값), `3e-3` (공격적) 을 시도해본다. 적절한 학습률은 모델 크기와 데이터에 따라 달라짐.

### 학습 모니터링

학습 루프는 `loss_log.json` 을 저장함. 어떤 도구로든 시각화할 수 있음:

```python
## pip install matplotlib
import json, matplotlib.pyplot as plt

with open("loss_log.json") as f:
    log = json.load(f)

plt.figure(figsize=(10, 6))
plt.plot(log["steps"], log["train"], alpha=0.3, label="train")
plt.xlabel("Step")
plt.ylabel("Loss")
plt.legend()
plt.savefig("loss_curve.png")
plt.show()
```

#### 체크해야 할 패턴

- **학습 손실(train loss)이 줄지 않음**: 학습률이 너무 낮거나 버그가 있음
- **학습 손실은 줄지만 검증 손실이 올라감**: 과적합(overfitting) — 데이터를 늘리거나 모델을 줄여야 함
- **손실 스파이크(loss spike)**: 학습률을 낮추거나 그라디언트 클리핑(gradient clipping)을 점검할 것
- **손실이 평탄해짐(plateau)**: 모델이 배울 수 있는 만큼 다 배운 상태. 데이터를 더 넣거나 모델을 키워야 함

### 자, 이제: 경연

여기까지 오면 모델을 직접 학습시켜봤고, 과적합도 겪어봤고, 다양한 설정을 실험해본 셈임. 이제 그 모든 경험을 적용할 차례.

#### [Part 6 — 경연: 최고의 AI 시인 →](06-competition.md)

목표: 좋은 시(poetry) 데이터셋을 찾아서, 가능한 한 좋은 모델을 학습시키고, 모델이 생성한 가장 훌륭한 시 한 편을 제출하는 것. 데이터, 모델 크기, 토크나이저, 학습 전략 등 무엇이든 바꿔도 됨. 단 두 가지 규칙만 지키면 됨: 노트북에서 처음부터(from scratch) 직접 학습시킬 것, 그리고 시는 모델이 생성한 것이어야 함.

### 더 읽어볼 자료

- [Karpathy의 microgpt](http://karpathy.github.io/2026/02/12/microgpt/) — 순수 파이썬 200줄짜리 풀 GPT 구현
- [build-nanogpt 영상 강의](https://github.com/karpathy/build-nanogpt) — 빈 파일에서부터 GPT-2 를 만드는 4시간짜리 영상
- [nanochat](https://github.com/karpathy/nanochat) — 풀 ChatGPT 클론 학습 파이프라인
- [Attention Is All You Need (2017)](https://arxiv.org/abs/1706.03762) — 오리지널 트랜스포머 논문
- [GPT-2 논문 (2019)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) — 비지도 다중 과제 학습기로서의 언어모델
- [TinyStories 논문](https://arxiv.org/abs/2305.07759) — 정제된 데이터로 학습한 작은 모델
- [Chinchilla (2022)](https://arxiv.org/abs/2203.15556) — 데이터와 파라미터의 최적 스케일링(scaling)

---

## Part 6: 경연 — 최고의 AI 시인

셰익스피어로 GPT를 학습시켜봤다. 이제 배운 걸 실전에 써볼 차례다. 가장 좋은 시를 만들어내는 모델을 학습시키고, 가장 잘 나온 시 한 편을 제출해보자.

### 도전 과제

가장 잘 쓴 시를 생성하는 모델을 학습시킨다. 데이터셋, 모델 크기, 토크나이저, 학습 전략 — 무엇이든 자유롭게 고를 수 있다. 단, 다음 조건만 지키면 된다.

1. 모델은 직접 학습시킨 것이어야 한다 (사전학습 가중치 사용 금지, 남이 만든 모델을 파인튜닝하는 것도 금지)
2. 시는 모델이 생성한 것이어야 하며, 사람이 쓰거나 편집한 것이면 안 된다
3. 증명할 수 있어야 한다 — 체크포인트와 정확한 생성 명령어를 같이 제출한다

### 제출물

세 가지를 제출한다.

1. **시(poem)** — 모델이 뽑아낸 최고의 결과물
2. **체크포인트** — 우리가 재현할 수 있도록
3. **생성 명령어** — 정확한 프롬프트, temperature, top_k, seed 값까지

`--seed` 플래그를 써서 재현 가능하게 만들자. 같은 seed에 같은 체크포인트, 같은 인자를 주면 항상 동일한 출력이 나온다.

```bash
## example submission command
python generate.py checkpoint_best.pt --prompt "The morning sun" --temperature 0.7 --top_k 30 --seed 42
```

제출한 명령어를 그대로 체크포인트에 돌려서 결과를 검증할 거다.

### 어떻게 이길까

우승작은 다음 기준으로 평가한다.

- **응집성(Coherence)** — 시로서 말이 되는가?
- **창의성(Creativity)** — 흥미로운 이미지, 예상 밖의 표현이 있는가?
- **구조(Structure)** — 운율, 행 바꿈, 연(stanza)이 살아 있는가?
- **감정(Emotion)** — 무언가를 불러일으키는가?

GPT-2 수준을 기대하는 사람은 아무도 없다. 기준선은 "기계가 쓴 게 명백하지만, 그래도 노력한 흔적이 보인다" 정도다.

### 시도해볼 만한 방향

기본기는 익혔으니 이제 한계까지 밀어볼 차례다. 당겨볼 만한 레버들이다.

#### 더 좋은 데이터

셰익스피어는 잘 동작했지만 결국 한 가지 스타일일 뿐이다. 더 나은 시 데이터셋을 찾거나 직접 만들어보자.

- **Poetry Foundation** — 시대와 스타일을 아우르는 수천 편의 시
- **Project Gutenberg** — 퍼블릭 도메인 시집
- **여러 출처 결합** — 셰익스피어 + 소네트 + 현대 자유시
- **공격적인 큐레이션** — 별로거나 무관한 텍스트는 제거하고 진짜 시만 남긴다

데이터가 많을수록 좋지만, **양보다 질이 더 중요하다**. 정성껏 큐레이션한 1MB짜리 시 데이터가, 시가 군데군데 섞인 무작위 텍스트 10MB를 이긴다.

#### 더 큰 모델

데이터가 많아지면 즉시 과적합되지 않으면서 더 큰 모델을 정당화할 수 있다.

| 설정 | 파라미터 수 | n_layer | n_head | n_embd |
|--------|--------|---------|--------|--------|
| 워크숍 기본값 | ~10M | 6 | 6 | 384 |
| 좀 더 큰 버전 | ~25M | 8 | 8 | 512 |
| GPT-2 Small | ~85M | 12 | 12 | 768 |

과적합 교훈을 잊지 말자. 같은 데이터에 더 큰 모델을 얹으면 그저 더 빠르게 외워버릴 뿐이다. 데이터에 맞춰서 모델을 키워야 한다.

#### 더 좋은 토크나이저

문자 단위(character-level)는 셰익스피어처럼 데이터셋이 작을 때 잘 통했다. 시 데이터셋이 커지면 다음을 고려해보자.

- **tiktoken의 BPE** — GPT-2가 쓰는 토크나이저, 5MB 이상 데이터셋에 적합
- **직접 학습한 BPE** — 시 어휘에 맞춘 작은 어휘집(1k–5k 토큰)
- **단어 단위(word-level)** — 데이터셋이 충분히 크고, 모델이 단어 단위로 사고하길 원할 때

#### 학습 튜닝

- **더 긴 컨텍스트** (`block_size=512` 또는 `1024`) — 연 전체와 행을 가로지르는 운율 패턴을 모델이 포착할 수 있게 해준다
- **드롭아웃(Dropout)** — attention과 MLP 블록에 `nn.Dropout(0.1)` 을 추가해 과적합을 줄인다
- **얼리 스탑(Early stopping)** — 마지막 체크포인트가 아니라 검증 손실(val loss)이 가장 낮은 체크포인트를 저장한다
- **학습률(Learning rate)** — 자기 모델/데이터 조합에 맞게 `max_lr` 을 튜닝한다

#### 생성 트릭

같은 모델이라도 생성 설정에 따라 결과물이 완전히 달라진다.

- **Temperature** — 0.6에서 1.0 사이를 시도해보자. 낮을수록 더 집중된 출력이 나온다
- **Top-k** — 10에서 50 사이를 시도해보자. 낮을수록 더 가능성 높은 토큰들로 제한된다
- **프롬프트 엔지니어링** — 프롬프트가 중요하다. 제목, 첫 행, 또는 스타일 단서로 시작해보자
- **체리피킹(Cherry-pick)** — 시 20편을 뽑아서 그중 가장 잘 나온 한 편만 제출한다. 이건 정정당당한 방법이다.

### 제약 사항

- 모델은 이 워크숍 코드(또는 그 변형)를 사용해 처음부터 학습되어야 한다
- 사전학습 모델 금지, 파인튜닝 금지, 어디서도 가중치를 불러오면 안 된다
- 출력물의 수동 편집 금지 — 다듬기(trimming) 외에는 모델이 생성한 그대로를 제출한다
- 코드의 어떤 부분이든 수정 가능하다: 모델 구조, 학습 루프, 토크나이저, 생성 로직
- 학습은 본인 머신이나 Google Colab에서 돌려야 한다 (유료 클라우드 GPU 사용 금지)

---

> 원본: [angelos-p/llm-from-scratch](https://github.com/angelos-p/llm-from-scratch) · [docs/](https://github.com/angelos-p/llm-from-scratch/tree/main/docs)
> 한국어 번역 — 코드/식별자/수식은 원문 그대로, 본문은 자연스러운 한국어로 의역함.
