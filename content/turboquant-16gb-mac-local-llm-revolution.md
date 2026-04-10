---
title: "TurboQuant: 16GB Mac에서 대형 LLM을 돌리는 새로운 방법"
date: 2026-04-10
tags:
  - ai
  - llm
  - mac
  - local-ai
  - turboquant
  - quantization
description: "Google이 발표한 TurboQuant는 KV 캐시를 압축해 16GB 맥에서도 131K 컨텍스트를 사용할 수 있게 한다. Alex Ziskind의 실험 결과를 정리한다."
---

> "Same model, same machine. Turbo gives you two times more usable context." — Alex Ziskind

Alex Ziskind가 TurboQuant를 16GB Mac Mini에서 직접 테스트한 [영상](https://www.youtube.com/watch?v=XLlQDfhyBjc)이 22만 뷰를 넘겼다. 로컬 LLM을 돌리는 사람이라면 반드시 알아야 할 내용이라 정리한다.

## TurboQuant가 뭔가

LLM을 로컬에서 돌릴 때 메모리를 잡아먹는 건 두 가지다:

1. **모델 가중치(weights)** — 모델 자체의 크기
2. **KV 캐시** — 추론 중 생성되는 "단기 기억"

기존 양자화(quantization)는 모델 가중치를 압축한다. BF16(19.3GB) → Q8(10GB) → Q4(6GB)로 줄이는 식이다. 하지만 **KV 캐시는 건드리지 못했다.** 컨텍스트가 길어질수록 KV 캐시가 폭발적으로 커지면서 메모리를 잡아먹는다.

TurboQuant는 Google 리서치에서 발표한 기술로, **KV 캐시 자체를 압축**한다. 모델 가중치 양자화와 별도로 작동하므로, 기존 양자화와 함께 쓸 수 있다.

## 실험 환경

Alex는 두 대의 맥에서 테스트했다:

| 장비 | 메모리 | 역할 |
|------|--------|------|
| Mac Mini M4 | 16GB | 저사양 테스트 |
| MacBook Pro M5 Max | 128GB | 고사양 비교 |

테스트 모델: Qwen 3.5 9B (Q4 양자화, 약 6GB)

## 핵심 발견 1: 메모리 절약

16GB Mac Mini에서의 결과가 극적이다:

- **Q8 KV 캐시 + 131K 컨텍스트** → 크래시 (메모리 부족)
- **Turbo 3 KV 캐시 + 131K 컨텍스트** → 정상 구동, 3.6GB 여유

같은 모델, 같은 기기에서 **TurboQuant가 사용 가능한 컨텍스트를 2배로** 늘렸다. 32K, 65K, 131K 각 단계에서 모두 KV 캐시 크기가 큰 폭으로 줄었다.

## 핵심 발견 2: 비대칭이 답이다

TurboQuant에는 세 가지 변형이 있다:

| 변형 | 압축률 |
|------|--------|
| Turbo 2 | 4배 (가장 공격적) |
| Turbo 3 | 2.5배 |
| Turbo 4 | 1.9배 |

처음에 Alex는 K와 V에 동일한 Turbo를 적용하는 **대칭(symmetric)** 방식으로 테스트했다. 결과는 참담했다. Needle-in-a-haystack 테스트에서 Turbo 2, 3 모두 큰 컨텍스트에서 0점을 기록했다.

하지만 Tom(Turbo Quant Plus 개발자)의 제안대로 **비대칭(asymmetric)** 방식을 적용하자 완전히 달라졌다:

- **K: Q8 유지 + V: Turbo 3 또는 Turbo 4 적용**
- Needle-in-a-haystack: 모든 컨텍스트 길이에서 **3/3 만점**

품질 저하 없이 메모리만 줄인 것이다.

## 핵심 발견 3: 속도까지 빨라진다 (M5 Max)

M5 Max에서 놀라운 결과가 나왔다:

- **Q8 기준**: 컨텍스트 깊이 0 → 8K로 가면 54 tok/s → 37 tok/s로 하락
- **Turbo Quant**: 컨텍스트 깊이와 무관하게 **속도가 거의 일정**

KV 캐시가 작아지니 메모리 읽기 병목이 사라진 것이다. 다만 M4 Mac Mini에서는 compute-bound(연산 병목)이라 이 효과가 크지 않았다. Alex는 M5 Mac Mini가 나오면 16GB에서도 이 속도 이점이 나타날 것으로 예측했다.

## 지금 사용하려면

TurboQuant는 아직 llama.cpp 공식에 통합되지 않았다. 커뮤니티 포크를 사용해야 한다:

1. GitHub에서 **TurboQuant Plus** (Tom의 llama.cpp 포크) 클론
2. 빌드 후 비대칭 설정으로 실행:
   - K 캐시: Q8
   - V 캐시: Turbo 3 (권장) 또는 Turbo 4

```bash
# 비대칭 TurboQuant 실행 예시 개념
# K=Q8, V=Turbo3 설정으로 llama-server 실행
./llama-server -m model.gguf --cache-type-k q8_0 --cache-type-v turbo3
```

## 정리

| 항목 | 기존 양자화 | TurboQuant |
|------|------------|-----------|
| 압축 대상 | 모델 가중치 | KV 캐시 |
| 메모리 절약 | 모델 크기 축소 | 컨텍스트 메모리 축소 |
| 품질 영향 | Q4 이하에서 저하 | 비대칭 적용 시 무손실 |
| 속도 영향 | 없음 | 고사양에서 오히려 향상 |
| 최대 효과 | 모델 로딩 | 긴 컨텍스트 추론 |

16GB 맥을 가지고 있다면 TurboQuant는 게임체인저다. 모델을 바꾸지 않아도, 하드웨어를 업그레이드하지 않아도, 압축 방식 하나로 사용 가능한 컨텍스트가 2배가 된다. llama.cpp 공식 통합이 되면 더 넓은 사용자에게 퍼질 것이다.

- **영상 원본:** [After This, 16GB Feels Different — Alex Ziskind](https://www.youtube.com/watch?v=XLlQDfhyBjc)
- **Google 리서치 페이퍼:** [TurboQuant 논문](https://arxiv.org/abs/2504.03475)
