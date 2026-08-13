---
title: "HSI: 동결된 LLM이 자기 하네스를 계속 고쳐서 성능을 올리는 방법"
date: 2026-08-13
tags:
  - agent
  - harness
  - LLM
  - self-evolution
  - self-improvement
  - frozen-model
  - BALROG
  - loop
  - automation
source: arxiv
source_url: https://arxiv.org/abs/2608.08466
authors:
  - conanssam
draft: false
---

![HSI 프레임워크 개요](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/fig-1-p5.png)

## 개요

Zhou et al.(2026)은 동결된 LLM으로 세 가지 역할을 동시에 수행하면서 자기 하네스를 진화시키는 프레임워크 HSI를 제안한다. 모델 가중치를 건드리지 않고, 하네스(프롬프트·도구·메모리·검증 로직)만 고쳐서 BALROG 벤치마크에서 유의미한 성능 향상을 얻었다.

핵심 구조는 세 개의 계층이다:

| 계층 | 역할 | 편집 가능? |
|---|---|---|
| Task Harness | 환경과 상호작용하며 태스크 수행 | 가능 |
| Evolver | 태스크 하네스를 평가 기반으로 재작성 | 가능 |
| Meta-Evolver | Evolver의 전략 코드 자체를 재작성 | 외부 실행 로직은 동결 |

동결된 외부 앵커가 최상단에 있어서 무제한 자기 참조를 막는다. 같은 모델이 태스크도 수행하고 하네스도 고치고, 전략까지도 수정한다.

## 실험 설정

- 백본: DeepSeek-V4-Flash-Preview (동결)
- 벤치마크: BALROG (장기 텍스트 게임 6종)
- 태스크 실행 시 추론(thinking)은 OFF, 하네스 수정 시에는 ON
- 반복 횟수: 5회 outer iteration, iteration당 최대 80 react() 스텝
- 평가 지표: % Progress (0–100)

thinking-on/off 설계가 핵심입니다. 태스크 수행 시 모델의 추론 능력을 고정시켜서, 성능 변화가 순수하게 하네스 개선에서 오는 것을 보장한다.

## 결과

| 환경 | Init Harness | HSI (meta-on) | 개선 폭 |
|---|---|---|---|
| BabyAI | 42.0 | 81.3 | +39.3 |
| Crafter | 11.6 | 44.6 | +33.0 |
| TextWorld | 40.0 | 65.0 | +25.0 |
| MiniHack | 0.8 | 15.8 | +15.0 |
| NLE | ~0 | 0.2 | ≈0 |

TextWorld 65.0% Progress는 Grok-4(62.9%), Claude-Opus-4.5-Thinking(59.0%)을 넘는 수치다. 같은 모델, 같은 추론 예산에서 하네스만 바꿔서 얻은 결과다.

메타 진화를 끄면 모든 환경에서 성능이 떨어진다. TextWorld는 65.0 → 46.0, MiniHack은 15.8 → 5.8. 진화 전략 자체를 진화시키는 것이 유효하다.

![Crafter 진화 궤적](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/fig-2-p11.png)

## 진화가 어떻게 진행되는가

Crafter 환경의 진화 궤적을 보면 패턴이 보인다.

1. 초기 반복에서는 누락된 추상화를 발견한다. 보상 신호를 명시적으로 노출하고, 인벤토리 상태를 구조화하고, 행동-상태 정렬을 개선한다.
2. 중기 반복에서는 구조화된 알고리즘 컴포넌트를 도입한다. 규칙 기반 제안, 안전 제약 등.
3. 후기 반복에서는 경쟁하는 설계를 다듬거나 가지치기한다.

메타 진화기의 역할은 이런 로컬 발견을 재사용 가능한 휴리스틱으로 코드화하는 것이다. "원시 관찰보다 구조화된 상태 표현을 우선하라" 같은 원칙을 Σ에 기록해서 이후 반복에 반영한다.

## 일반화 검증

BabaIsAI 서브-수트(20% held-out)에서 진화된 하네스가 본 적 없는 태스크로 얼마나 전달되는지 측정했다.

| 서브-수트 | Best Dev | Test (held-out) |
|---|---|---|
| BreakStop | 1.00 | 0.98 |
| GoTo | 1.00 | 1.00 |
| Make | 0.56 | 0.36 |

네비게이션 계열(BreakStop, GoTo)에서는 거의 완벽한 일반화를 보인다. 반면 Make(다단계 제작)에서는 한계가 명확하다. 모델 자체의 추론 능력이 부족하면 하네스 개선으로 커버할 수 없다.

![BabaIsAI-Make 진화 궤적](/images/2026-08-13-hsi-hierarchical-self-improvement-harness/fig-3-p12.png)

## 한계

두 가지 경계가 실험적으로 확인되었다.

1. **피드백 한계**: 보상 신호가 희소한 환경(NLE)에서는 진화가 작동하지 않는다. 유의미한 수정 방향을 찾기 어렵기 때문이다.
2. **백본 능력 한계**: 동결된 모델이 태스크에서 충분한 능력을 보이지 않으면 하네스 재설계로 한계를 넘을 수 없다.

하네스 진화는 기존 모델 능력을 체계적으로 끌어내는 메커니즘이지, 더 강한 모델을 대체하는 것이 아니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

코드는 [github.com/TailinZhou/hsi](https://github.com/TailinZhou/hsi)에서 확인할 수 있다.
