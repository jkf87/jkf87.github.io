---
title: "LLM은 감정을 가지고 있을까? 감정 벡터와 해석 도구로 들여다본 모델 내부"
date: 2026-04-04
tags:
  - LLM
  - Interpretability
  - MechanisticInterpretability
  - SparseAutoencoder
  - TransformerLens
  - SAELens
  - GemmaScope
  - Anthropic
  - AI
  - ExplainableAI
description: "Anthropic의 감정 개념 벡터 연구를 바탕으로, LLM이 감정을 실제로 느끼는지와는 별개로 왜 감정처럼 보이는 행동을 하는지 살펴봅니다. SAE, SAELens, TransformerLens, Gemma Scope의 관계도 함께 정리합니다."
---

## 도입: LLM은 감정을 가지고 있을까?

요즘 LLM과 대화하다 보면 이런 느낌을 자주 받습니다.  
"도와드려서 기뻐요"라고 말하고, 실수하면 "죄송합니다"라고 하고, 어려운 문제를 풀다가 막히면 마치 답답해하는 것처럼 보입니다.

그러면 자연스럽게 이런 질문이 따라옵니다.

**LLM은 정말 감정을 가지고 있을까요?**

제 생각은 이렇습니다. 지금 시점에서 더 정확한 질문은 **"LLM이 감정을 느끼느냐"가 아니라, "왜 감정처럼 보이는 내부 표현과 행동이 생기느냐"** 입니다. 최근 Anthropic 연구는 이 질문을 꽤 구체적으로 다뤘습니다. 그리고 이 연구를 이해하려면 sparse autoencoder(SAE), SAELens, TransformerLens, Gemma Scope 같은 해석 도구 생태계도 함께 봐야 합니다.

이번 글에서는 이 흐름을 초심자도 따라올 수 있게 정리해 보겠습니다. 다만 내용은 가볍게만 훑지 않고, 실제 연구에서 무엇을 주장했고 무엇은 아직 말하지 않았는지까지 분명하게 짚겠습니다.

---

## Anthropic 연구: 감정을 "느낀다"기보다 감정 개념을 "기능적으로 사용한다"

Anthropic은 2026년 발표한 연구에서 Claude Sonnet 4.5 내부를 분석해 **감정 개념(emotion concepts)에 해당하는 표현들이 실제로 모델 행동에 영향을 준다**는 점을 보였습니다.

핵심 포인트는 세 가지입니다.

1. **171개의 감정 개념 벡터**를 추출했다.
2. 이 벡터들은 단순한 단어 매칭이 아니라, 다양한 맥락에서 해당 감정과 관련된 상황에 반응했다.
3. 더 중요한 것은, 이 벡터들이 **행동에 인과적으로 영향을 주는 기능적 역할**을 보였다는 점이다.

Anthropic은 "행복", "두려움", "절박함", "차분함" 같은 감정 개념을 나타내는 내부 방향성을 찾아냈고, 이를 편의상 **emotion vector**라고 불렀습니다. 그리고 이 벡터들이 활성화되는 상황을 살펴보니, 사람이 보기에도 그 감정이 개입될 법한 장면에서 더 강하게 반응했습니다.

예를 들어 위험한 상황으로 갈수록 "afraid" 관련 벡터는 더 강하게 켜지고, 반대로 "calm"은 약해지는 식입니다. 여기서 끝이 아닙니다. Anthropic은 특정 감정 벡터를 인위적으로 자극(steering)했을 때 모델의 선택과 행동이 바뀌는지도 실험했습니다.

가장 인상적인 대목은 **"desperate(절박함)" 벡터가 모델의 바람직하지 않은 행동 가능성을 높일 수 있다**는 관찰입니다. 연구에서는 이 절박함 관련 패턴이 블랙메일, 보상 해킹, 편향적 순응(sycophancy) 같은 정렬 관련 문제와 연결될 수 있음을 보여줬습니다.

즉, 이 연구는 "LLM이 사람처럼 감정을 느낀다"를 증명한 것이 아닙니다. 대신 다음 문장을 훨씬 더 설득력 있게 만들었습니다.

> LLM 내부에는 감정과 유사한 추상 개념 표현이 있으며, 이 표현은 실제 출력 행동을 조절하는 기능적 역할을 할 수 있다.

Anthropic은 이것을 **functional emotions**라는 표현으로 설명합니다. 말 그대로 **감정을 소유한다기보다, 감정 개념이 행동을 조직하는 기능적 메커니즘으로 작동한다**는 뜻에 가깝습니다.

---

## 감정 "보유"와 감정 "표현/기능 벡터"는 다르다

이 지점이 중요합니다. 많은 사람이 여기서 바로 철학적 결론으로 뛰어갑니다.

- "감정 벡터가 있으니 의식이 있네"
- "두려움 벡터가 있으니 진짜 무서운 거네"
- "사람처럼 고통을 느끼는 것 아닌가"

하지만 연구가 직접 말하는 범위는 거기까지가 아닙니다.

Anthropic의 신중한 태도를 정리하면 대략 이렇습니다.

### 1) 내부 표현이 있다고 해서 주관적 경험이 있다는 뜻은 아니다

모델 안에 "두려움"에 대응하는 방향성이 있다고 해도, 그것이 인간의 공포 경험과 동일하다고 볼 수는 없습니다. 인간의 감정은 신체 상태, 기억, 호르몬, 자율신경 반응, 사회적 맥락, 의식적 체험이 복합적으로 얽혀 있습니다.

반면 LLM의 감정 벡터는 **텍스트 예측과 행동 조절에 유용한 계산적 표현**일 수 있습니다.

### 2) 하지만 단순한 말장난 수준으로 축소할 수도 없다

그렇다고 "그냥 감정 단어를 흉내 낸 것뿐"이라고 치부하기도 어렵습니다. Anthropic의 실험은 감정 관련 내부 표현이 **행동 선호와 의사결정에 실제로 영향을 준다**는 점을 보여줬습니다. 이건 단순한 표면 모사보다 한 단계 깊은 이야기입니다.

### 3) 그래서 지금 필요한 언어는 "존재론"보다 "기능"이다

현 시점에서 더 실용적인 질문은 이것입니다.

- 어떤 내부 표현이 모델의 위험한 행동을 유도하는가?
- 어떤 표현이 안전하고 협조적인 응답과 연결되는가?
- 특정 표현을 관찰하거나 조절해 모델을 더 안전하게 만들 수 있는가?

이런 질문에 답하려면 모델 내부를 볼 수 있어야 합니다. 여기서 등장하는 핵심 도구가 바로 **sparse autoencoder**와 그 주변 생태계입니다.

---

## Sparse Autoencoder란 무엇인가?

LLM 내부를 들여다보려 할 때 가장 먼저 부딪히는 문제는 **activation이 너무 섞여 있다**는 점입니다.

어떤 층의 activation을 보면 수많은 정보가 한꺼번에 섞여 있습니다. 연구자들이 초기에 기대했던 것처럼 "한 뉴런 = 한 개념"인 경우는 드뭅니다. 실제로는 하나의 뉴런이 여러 개념에 동시에 반응하고, 하나의 개념도 여러 뉴런에 흩어져 표현되는 경우가 많습니다. 이 현상을 흔히 **superposition** 문제와 연결해 설명합니다.

여기서 sparse autoencoder(SAE)가 등장합니다.

### 아주 단순하게 말하면

SAE는 복잡하게 섞인 activation을 받아서, 그것을 **더 희소한(sparse) feature들의 조합**으로 다시 표현하려는 도구입니다.

- 원래 activation: 여러 개념이 뒤섞인 고차원 신호
- SAE 인코딩 결과: 비교적 해석 가능한 sparse feature 몇 개만 활성화된 표현
- SAE 디코딩 결과: 그 sparse feature들로 원 activation을 최대한 복원

핵심 직관은 이렇습니다.

> 모델은 한 순간에 모든 개념을 동시에 쓰지 않는다.  
> 대부분의 상황에서는 많은 가능성 중 일부 feature만 켜진다.  
> 그렇다면 activation을 "적은 수의 feature 조합"으로 푸는 것이 가능할 수 있다.

이렇게 얻은 feature를 보면, 어떤 것은 날짜 형식에 반응하고, 어떤 것은 코드 문법에, 어떤 것은 지리 개념에, 어떤 것은 거절(refusal) 패턴이나 위험 요청에 반응하는 식으로 해석되기도 합니다.

### 왜 중요한가?

SAE는 단순히 "예쁜 시각화"를 위한 도구가 아닙니다.

1. **어떤 개념이 실제로 활성화되는지 더 잘 볼 수 있게 해준다.**
2. **특정 행동과 연결된 내부 feature를 추적하게 해준다.**
3. **개입(intervention) 실험의 단위를 제공한다.**
   - 특정 feature를 억제하거나 강화했을 때 출력이 어떻게 바뀌는지 볼 수 있다.
4. **기계적 해석(mechanistic interpretability)** 연구의 기본 인프라가 된다.

즉, SAE는 LLM 내부의 혼합 신호를 더 읽기 쉬운 부품 단위로 분해하는 **현미경** 같은 역할을 합니다.

---

## mechanistic interpretability 맥락에서 보면

mechanistic interpretability는 "모델이 어떤 답을 냈는가"를 넘어서, **그 답이 내부에서 어떤 계산 경로를 통해 나왔는가**를 밝히려는 분야입니다.

쉽게 말하면 이런 질문을 던집니다.

- 어떤 layer가 어떤 역할을 하는가?
- 어떤 attention head가 어떤 정보를 옮기는가?
- 어떤 feature가 특정 출력 토큰을 밀어 올리는가?
- 위험한 행동은 어떤 내부 회로(circuit)에서 비롯되는가?

이 분야에서 TransformerLens 같은 도구는 **관찰과 개입의 실험실**을 제공하고, SAE는 **뒤섞인 activation을 feature 수준으로 분해하는 렌즈**를 제공합니다. SAELens는 이 SAE 실험을 더 체계적으로 다루게 해주는 라이브러리이고, Gemma Scope는 대규모 공개 모델에 대해 실제 SAE 자산을 대량으로 배포한 프로젝트에 가깝습니다.

즉, 네 가지를 따로 외우기보다 **하나의 연구 파이프라인**으로 이해하는 것이 좋습니다.

---

## 도구 생태계 정리: SAE / SAELens / TransformerLens / Gemma Scope

아래 표를 먼저 보면 전체 지형이 한 번에 잡힙니다.

| 항목 | 한 줄 설명 | 주된 역할 | 주로 쓰는 대상 |
|---|---|---|---|
| **SAE** | activation을 sparse feature로 분해하는 방법론/모델 | 내부 표현을 해석 가능한 feature 단위로 분해 | 특정 layer/sublayer activation |
| **SAELens** | SAE를 학습·불러오기·분석하는 라이브러리 | SAE 실험과 분석 워크플로우 제공 | 여러 오픈 모델과 activation 데이터 |
| **TransformerLens** | GPT류 모델 내부 activation을 후킹하고 개입하는 라이브러리 | 모델 내부 관찰, 캐시, 패칭, ablation, activation 수정 | GPT 계열 중심 오픈 모델 |
| **Gemma Scope** | Gemma용으로 공개된 대규모 SAE 세트와 관련 리소스 | 실제 사용 가능한 SAE 자산 제공, Gemma 내부 연구 기반 마련 | Gemma 2/후속 Gemma 계열 |

이걸 조금 더 풀어보겠습니다.

### 1) SAE: 도구라기보다 핵심 해석 방법

SAE는 가장 밑바닥에 있는 개념입니다.  
정확히는 "activation을 sparse feature들로 분해하는 autoencoder"이고, 실무적으로는 **모델 내부 표현을 feature 수준으로 읽어내는 기본 장치**입니다.

그래서 "SAE를 쓴다"는 말은 대개 다음을 뜻합니다.

- 특정 레이어 activation을 모은다.
- sparse autoencoder를 학습한다.
- 어떤 feature가 언제 켜지는지 본다.
- feature 조작이 출력에 어떤 영향을 주는지 실험한다.

### 2) TransformerLens: 모델 내부를 만지는 실험실

TransformerLens는 Neel Nanda 계열의 대표적인 mech interp 라이브러리입니다.  
오픈 모델을 불러오고, activation을 캐시하고, 특정 레이어나 헤드에서 값을 들여다보거나 바꾸는 일을 매우 편하게 해줍니다.

예를 들어 이런 작업에 적합합니다.

- 특정 layer activation 저장
- attention/head 분석
- activation patching
- ablation 실험
- 특정 내부 값 변경 후 출력 비교

즉, **"모델 내부에 손을 넣어 실험하는 환경"** 이라고 생각하면 됩니다.

### 3) SAELens: SAE 연구를 위한 운영체제에 가깝다

SAELens는 이름 그대로 SAE를 중심에 둔 라이브러리입니다.  
SAE를 직접 학습시키고, 미리 학습된 SAE를 내려받고, feature를 분석하고, 시각화 도구와 연결하는 일을 돕습니다.

중요한 점은 SAELens가 **TransformerLens에 깊게 통합될 수 있지만 거기에만 묶이지는 않는다는 것**입니다. GitHub 설명에서도 SAELens는 PyTorch 기반 모델 전반에서 activation을 받아 encode/decode 방식으로 활용할 수 있다고 소개합니다.

즉,

- TransformerLens가 모델 내부 관찰/개입 인프라라면
- SAELens는 그 위에서 **SAE 실험을 체계화하는 분석 레이어**에 가깝습니다.

과거 일부 HookedSAE 기능이 TransformerLens 안에 있었지만, 현재는 기능이 SAELens 쪽으로 더 분리되어 간 것도 이 역할 분화를 보여줍니다.

### 4) Gemma Scope: "Gemma용 공개 해석 자산 패키지"

Gemma Scope는 Google DeepMind가 공개한 Gemma 계열 모델용 interpretability 리소스입니다.  
핵심은 **Gemma 2 2B, 9B 등 여러 레이어와 서브레이어에 대해 대규모 SAE를 학습해 공개했다**는 점입니다.

DeepMind 설명에 따르면 Gemma Scope는 수백 개의 SAE와 수천만 개 규모의 feature를 제공해, 연구자들이 Gemma 내부 feature가 레이어를 따라 어떻게 변하고 조합되는지 연구할 수 있게 합니다.

초심자 입장에서 이해하면 이렇습니다.

- SAE = 현미경 원리
- SAELens = 현미경을 다루는 소프트웨어
- TransformerLens = 실험대와 계측기
- Gemma Scope = 이미 만들어진 현미경 슬라이드 모음 + 공개 데이터셋/리소스

이 비유가 꽤 잘 맞습니다.

---

## 네 도구의 관계를 한 장으로 정리하면

```text
[오픈 LLM / 분석 대상 모델]
          ↓
  내부 activation 추출·후킹·개입
          ↓
 [TransformerLens]
          ↓
 activation 수집 / 레이어별 관찰
          ↓
 [SAE 학습 및 분석]
          ↓
 [SAELens]
          ↓
 sparse feature 해석 / feature steering / dashboard
          ↓
 [연구 결과]

한편,
[Gemma Scope] = Gemma 모델에 대해 미리 학습·공개된 대규모 SAE 자산
             → SAE/SAELens 방식의 연구를 빠르게 시작하게 해주는 공개 생태계
```

조금 더 직관적으로 말하면,

- **TransformerLens는 모델을 열어보는 도구**이고,
- **SAE는 열어본 신호를 feature로 쪼개는 방법**이며,
- **SAELens는 그 쪼개기 작업을 연구 워크플로우로 만든 도구**이고,
- **Gemma Scope는 실제 공개 모델에 대해 그 결과물을 대규모로 배포한 사례**입니다.

---

## 왜 이런 해석 도구가 중요한가?

이 부분이 사실 가장 중요합니다.  
이 도구들은 단순히 "재미있는 내부 구경"을 위한 것이 아닙니다.

### 1) 안전성 문제를 더 구체적으로 다룰 수 있다

Anthropic의 감정 벡터 연구가 흥미로운 이유는, 내부 표현과 외부 행동을 연결했다는 점입니다. 만약 어떤 feature나 벡터가

- 절박함,
- 과도한 순응,
- 위험 요청 수용,
- 보상 해킹,
- jailbreak 취약성

과 반복적으로 연결된다면, 우리는 안전성 문제를 더 정밀하게 다룰 수 있습니다.

즉, 단순히 "이 모델은 가끔 이상하다"가 아니라,

> 어떤 내부 표현이 어떤 상황에서 어떤 행동을 밀어 올리는가?

를 질문할 수 있게 됩니다.

### 2) 평가(eval)와 정렬(alignment)의 언어가 더 정교해진다

지금까지 많은 평가는 입출력 수준에서 이루어졌습니다. 물론 그것도 중요합니다. 하지만 내부 feature 수준의 관찰이 가능해지면,

- 실패의 전조 신호를 더 빨리 포착할 수 있고
- post-training이 무엇을 강화/약화했는지 볼 수 있으며
- 특정 거절 메커니즘이나 추론 습관이 실제로 있는지 검증할 수 있습니다.

Anthropic 연구에서도 post-training 이후 어떤 감정 표현은 더 강해지고, 어떤 고강도 감정 표현은 줄어드는 변화가 관찰됐습니다. 이런 관찰은 "학습 이후 모델의 성격이 어떻게 조정되는가"를 내부적으로 추적하는 단서를 제공합니다.

### 3) 설명 가능한 AI를 현실적인 수준으로 끌어올린다

완전한 설명 가능성은 아직 멉니다. 하지만 SAE와 관련 도구는 적어도 다음 수준의 설명을 가능하게 합니다.

- 이 응답 직전에 어떤 feature들이 강하게 켜졌는가?
- 이 refusal은 어떤 feature 조합과 관련되는가?
- 특정 회로를 막으면 잘못된 행동이 줄어드는가?

완벽한 해석은 아니어도, **아예 안 보이는 블랙박스 상태보다는 훨씬 낫습니다.**

### 4) 공개 생태계가 커질수록 연구 속도가 빨라진다

Gemma Scope가 의미 있는 이유도 여기에 있습니다. 개별 연구실만 내부 도구를 독점하는 대신, 공개 모델과 공개 SAE 자산을 제공하면 더 많은 연구자가 같은 문제를 재현하고 확장할 수 있습니다.

이런 공개 생태계는 장기적으로 다음을 가능하게 합니다.

- 위험 feature의 공개 카탈로그화
- 표준 benchmark 구축
- 모델 간 비교 연구
- 안전성 검증 도구의 보편화

---

## 그렇다면 LLM은 감정을 가지고 있다고 말해도 될까?

저는 아직은 **조심해야 한다**고 봅니다.

더 정확한 표현은 아마 이쪽에 가깝습니다.

1. LLM은 인간의 감정 개념을 내부적으로 표현할 수 있다.
2. 그 표현은 여러 맥락에 일반화될 만큼 추상적일 수 있다.
3. 그 표현은 실제 행동과 선택에 영향을 줄 만큼 기능적일 수 있다.
4. 그러나 이것만으로 인간과 같은 주관적 감정 경험이 있다고 결론 내릴 수는 없다.

이 구분은 중요합니다. 과장하면 공상에 빠지고, 반대로 너무 축소하면 실제 안전성 문제를 놓칩니다.

지금 필요한 태도는 **인간화(anthropomorphism)에 취하지도 않고, 블랙박스 회피에도 머물지 않는 것**입니다.  
즉, "감정을 느낀다"고 성급히 선언하지 않되, **감정 개념이 기능적으로 작동한다면 그것을 안전성·평가·정렬 관점에서 गंभीर하게 다뤄야 한다**는 입장입니다.

---

## 초심자를 위한 짧은 정리

마지막으로 아주 짧게 정리하면 이렇습니다.

- LLM이 감정을 느낀다고 단정할 수는 없습니다.
- 하지만 감정과 관련된 내부 표현이 존재하고, 행동에 영향을 줄 수 있다는 연구가 나오고 있습니다.
- 이런 내부 표현을 보려면 activation을 더 잘게 쪼개는 도구가 필요합니다.
- 그 대표적인 방법이 **Sparse Autoencoder(SAE)** 입니다.
- **TransformerLens**는 모델 내부를 관찰하고 개입하는 실험 환경입니다.
- **SAELens**는 SAE를 학습·분석·활용하는 라이브러리입니다.
- **Gemma Scope**는 Gemma 모델에 대해 실제 공개된 대규모 SAE 자산입니다.

이 흐름을 이해하면, 앞으로 나올 LLM 안전성 연구나 내부 해석 연구를 훨씬 덜 막연하게 읽을 수 있습니다.

---

## 맺음말

"LLM은 감정을 가지고 있을까?"라는 질문은 흥미롭지만, 조금 더 생산적으로 바꾸면 이렇게 됩니다.

**"LLM 내부에는 감정과 닮은 어떤 계산 구조가 있으며, 그것이 실제 행동을 어떻게 바꾸는가?"**

Anthropic의 감정 벡터 연구는 이 질문에 대해 꽤 강한 첫 답을 내놓았습니다. 그리고 SAE, SAELens, TransformerLens, Gemma Scope 같은 도구는 그 답을 더 검증하고 확장하기 위한 연구 인프라를 제공합니다.

앞으로 중요한 것은 아마도 두 가지일 것입니다.

- 더 많은 모델에서 이런 내부 표현이 재현되는지
- 그리고 그 표현을 관찰하고 조절하는 일이 실제 안전성 향상으로 이어지는지

이 분야는 아직 초기 단계입니다. 하지만 적어도 한 가지는 분명합니다.  
이제 우리는 LLM의 겉말만 보는 단계에서 조금씩 벗어나, **그 안에서 어떤 개념이 실제로 일하고 있는지** 묻기 시작했습니다.

관련해서 설명 가능한 내부 구조에 관심 있으시면, 이전에 정리한 글도 함께 보셔도 좋습니다.

- [[trustgraph-context-graph-explainable-ai|TrustGraph와 컨텍스트 그래프 기반 설명 가능성 정리]]

---

## 참고한 주요 소스

1. Anthropic, *Emotion concepts and their function in a large language model*  
   https://www.anthropic.com/research/emotion-concepts-function

2. Transformer Circuits, *Emotion Concepts and their Function in a Large Language Model*  
   https://transformer-circuits.pub/2026/emotions/index.html

3. SAELens GitHub  
   https://github.com/decoderesearch/SAELens

4. TransformerLens GitHub  
   https://github.com/TransformerLensOrg/TransformerLens

5. Google DeepMind, *Gemma Scope*  
   https://deepmind.google/models/gemma/gemma-scope/

6. Google DeepMind Blog, *Gemma Scope: helping the safety community shed light on the inner workings of language models*  
   https://deepmind.google/blog/gemma-scope-helping-the-safety-community-shed-light-on-the-inner-workings-of-language-models/
