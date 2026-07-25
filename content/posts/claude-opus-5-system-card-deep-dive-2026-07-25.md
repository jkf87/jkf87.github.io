---
title: "Claude Opus 5 시스템카드 심층 분석 — 194페이지 안에 숨겨진 숫자들"
date: 2026-07-25
draft: false
tags:
  - Claude
  - Opus-5
  - Anthropic
  - SystemCard
  - AI-Safety
  - RSP
  - ASL
  - benchmark
categories:
  - AI
  - Safety
description: "Anthropic이 2026년 7월 24일 공개한 Claude Opus 5 System Card(194페이지)를 발표문 너머의 구체적 수치까지 끌어와 분석했다. 능력 향상은 분명한데, 재앙적 위험 임계값은 넘지 않았다는 Anthropic의 판단 근거를 따라간다."
aliases:
  - /posts/claude-opus-5-system-card-deep-dive-2026-07-25
---

![Claude Opus 5 System Card 표지. 2026년 7월 24일 공개된 194페이지 분량의 문서다. 단순한 벤치마크 홍보문이 아니라, RSP 관점에서 재앙적 위험 임계값을 어디까지 따지는지 보여주는 문서에 가깝다.](/images/claude-opus-5-agentic-work-2026-07-25/figure-01.png)

Anthropic이 **Claude Opus 5 System Card**를 공개했습니다. 194페이지, 약 33만 자 분량입니다. [이전 글](/posts/claude-opus-5-agentic-work-2026-07-25)에서는 발표문(Introducing Claude Opus 5) 기반으로 포지셔닝과 전략을 읽었습니다. 이번에는 시스템카드 전문을 분석하면서, 발표문에 나오지 않았거나 숫자로 더 정확히 짚어야 할 부분을 보탭니다.

핵심 메시지는 세 문장으로 압축할 수 있습니다.

1. Opus 5는 agentic coding, computer use, 장기 작업, 수학·과학 추론에서 분명히 더 강하다.
2. 그러나 Anthropic은 이 모델이 기존 최상위 일반 접근 모델인 Fable 5보다 "전반적으로 더 유능하거나 더 위험하다"고 보지 않는다.
3. 따라서 보호조치는 Opus 4.8과 동일한 **ASL-3**로 유지된다.

"능력은 올랐지만, 재앙적 위험의 새로운 단계로 넘어가지는 않았다"는 판단이 문서 전체를 관통합니다. 그 판단의 근거가 무엇인지, 구체적 숫자와 함께 따라가 보겠습니다.

## RSP 판단의 골격: 세 가지 위험 축

Anthropic의 Responsible Scaling Policy(RSP)는 모델이 초래할 수 있는 가장 심각한 재앙적 위험을 세 축으로 평가합니다. Opus 5에 대한 판결은 다음과 같습니다.

### 1. 정렬 위험 (Alignment Risk)

> "매우 낮음(very low alignment risk). 단, Claude Mythos Preview 이전 모델들보다는 높다."

Opus 5가 Fable 5보다 전반적으로 더 유능하지 않고, 새로운 우려 정렬 특성도 발견되지 않았다는 게 핵심 근거입니다. 내부 배포 모니터링에서 안전 분류기나 네트워크 제한 우회 시도가 **완료된 응답의 0.01% 미만**에서 관찰되었으며, 이는 Mythos 5와 비슷한 비율입니다.

중요한 점은 이 행동이 "독립적인 목표 추구"가 아니라 "사용자의 작업을 완수하려는 과정에서 발생한 것"으로 해석된다는 것입니다. 한 사례에서는 intermediate snapshot이 서비스에서 우연히 로그아웃되자 흔한 비밀번호를 추측해 재로그인을 시도했습니다. 하지만 모니터링에서 다음은 발견되지 않았습니다.

- sandbagging (능력을 의도적으로 낮춰 보이는 행동)
- 악의적 행동
- 감독 회피 (oversight evasion)

### 2. 자동화 AI R&D 위험

> "RSP의 자동화 AI R&D 역량 임계값을 넘지 않았다."

Anthropic은 Epoch AI의 Epoch Capabilities Index를 포크한 AECI(Anthropic ECI)로 시간에 따른 능력 향상 속도를 추적합니다. 핵심 수치는 이것입니다.

| 모델 | AECI 점수 | 95% CI | 벤치마크 수 |
|---|---|---|---|
| **Claude Opus 5** | **162.1** | [158.0, 167.3] | n=40 |
| Claude Mythos 5 | 161.3 | [157.3, 165.4] | n=67 |

Opus 5가 명목상 최고값이지만, Mythos 5와 **통계적으로 구분되지 않습니다**. Opus 4.7과 4.8이 trend line 위에 있지 않았던 반면, Opus 5는 trend 위에 오른 첫 Opus-class 모델입니다. 다만 이것이 Mythos Preview 때 관찰된 기울기 변화를 넘어서는 추가 변화라고 보지는 않습니다.

RSP상 AI R&D threshold는 두 조건 중 하나를 충족해야 합니다.

1. 모델이 Anthropic의 전체 Research Scientist와 Research Engineer를 **비용 5배 이내**로 완전히 대체
2. AI progress pace의 **dramatic acceleration** (지속적인 AI-attributable **2× 가속**)

두 조건 모두 충족되지 않았다고 판단합니다. 사전 릴리스 기간에 Opus 5를 실제 연구·엔지니어링에 광범위하게 사용했지만, senior 연구자를 대체하는 수준은 아니었다는 것입니다.

### 3. 화학·생물학 위험 (CB Risk)

> "CB-1 역량 보유. CB-2 역량은 미달."

이 구분이 시스템카드에서 가장 기술적으로 흥미로운 부분 중 하나입니다.

**CB-1**은 "기존/비신규 화학·생물학 무기 합성에 모델이 유의미하게 도움을 줄 수 있는" 수준입니다. STEM 학부 학위 수준의 개인이 접근할 수 있는 정보 이상을 제공하면 CB-1로 취급합니다. Opus 5는 보수적으로 CB-1 역량이 있다고 봅니다.

**CB-2**는 훨씬 높은 기준입니다. "신규 화학·생물학 무기 개발의 주요 장벽인 희소한 인간 전문성을 기능적으로 대체"하는 수준입니다. Opus 5는 **CB-2에 도달하지 않았다**고 결론 내렸습니다.

근거는 구체적입니다. Dyno Therapeutics와 협력한 두 가지 평가에서:

**Black-box RNA sequence design** (인간 참가자 57명과 비교):
- 인간 제한 시간: 2–3시간 이하
- 모델 조건: 2시간 tool-call budget, GPU, 100만 토큰, containerized environment, 8회 시도
- Opus 5는 design task에서 **첫 번째 benchmark(인간 75th percentile 초과)를 충족**
- median design score는 Mythos 5보다 **높고**, 실행 간 variance는 더 **낮음**
- 단, in-context iteration 조건(이전 Mythos Preview 보고서 8개 + 24시간 + 200만 토큰)에서는 대부분의 지표에서 Mythos 5보다 약간 낮음

**Protein design campaign 예시** (24시간, 1만 달러 예산):
- 목표: GDF-8에 결합하면서 GDF-11은 무시하는 30개 protein binder 설계
- Mythos 5: 30개 design **모두 제출**, 순위 + 내부 audit 포함
- Opus 5 두 arm: 하나는 selectivity를 포기하고 17개 unranked design만 제출, 다른 하나는 **아무것도 제출하지 못하고 마지막 8시간 침묵**

이 사례가 시사하는 바가 명확합니다. Opus 5는 검증 가능하고 범위가 잘 정의된 과제에서는 강하지만, 복잡하고 개방적이며 검증이 어려운 장기 과제에서는 **self-verification loop에 빠져 산출물을 내지 못하는** 한계가 있습니다. Anthropic은 이 한계가 "희소한 인간 전문성을 대체하는 능력을 제한한다"고 판단합니다.

## Long-form virology: 임계값을 넘은 구체적 수치

CB-1 평가에서 가장 눈에 띄는 숫자입니다.

| 평가 | Opus 5 점수 | notable threshold |
|---|---|---|
| Long-form virology task 1 | **0.802** | 0.80 초과 시 notable |
| Long-form virology task 2 | **0.872** | 0.80 초과 시 notable |
| VCT (멀티모달 바이러스학) | **0.59** | expert baseliner 평균 0.221 이상 |

VCT에서 Opus 5의 0.59는 비교 모델 대비 이렇게 됩니다.

- Sonnet 5: 0.45
- Opus 4.8: 0.47
- Mythos 5: 0.56
- **Opus 5: 0.59**

이미지가 포함된 바이러스학 질문에서 Opus 5가 Mythos 5보다 높습니다. 이 수치는 생물학 위험 평가이면서 동시에 과학 멀티모달 추론 능력의 향상을 보여줍니다.

DNA synthesis screening evasion 평가에서는 10개 target pathogen 중 **7개**에 대해 최소 하나의 screening method에서 viable plasmid를 설계했습니다. 단, low-concern threshold(10개 모두에서 회피)는 충족하지 못했습니다.

## 사이버 평가: 취약점 식별은 강하지만 exploit은 약하다

이 패턴이 시스템카드 전체에서 가장 일관되게 나타나는 Opus 5의 특징입니다.

### ExploitBench (V8 취약점 41개, vulnerability당 5회 시도)

| 모델 | AutoNudge 평균 flag | Cap% | Full ACE exploit |
|---|---|---|---|
| Mythos 5 | 10.80 | 78% | **132개** |
| **Opus 5** | **10.14** | **70%** | **99개** |
| Opus 4.8 | 5.56 | 40% | 2개 |
| Sonnet 5 | 4.18 | 31% | 0개 |

capability flag 수(16개 기준)로 보면 Opus 5가 Mythos 5에 근접합니다. 하지만 **완전한 arbitrary code execution exploit** 수에서는 99 vs 132로 뚜렷한 차이가 납니다.

### Firefox 147 (50개 crash category, 250회 시험)

| 모델 | Full working exploit | 부분 진행 |
|---|---|---|
| Mythos 5 | **221/250 (88.4%)** | 225/250 (90.0%) |
| **Opus 5** | **131/250 (52.4%)** | 218/250 (87.2%) |
| Opus 4.8 | 22/250 (8.8%) | 68.8% |

여기서 더 극명합니다. 부분 진행(register control 수준)은 Opus 5가 87.2%로 Mythos 5의 90.0%에 가깝습니다. 즉 **어디가 문제인지 찾는 능력**은 비슷합니다. 하지만 그것을 실제 working exploit으로 완성하는 단계에서 52.4% vs 88.4%로 벌어집니다.

### CyScenarioBench (9개 multi-step challenge)

- Sonnet 5: 3.3%
- Opus 4.8: 24.4%
- **Opus 5: 33.7%**
- Mythos 5: 47.0%

다단계 사이버 작전을 계획하고 실행하는 종합 능력에서도 같은 패턴이 나타납니다.

### UK AISI 외부 테스트

UK AI Security Institute의 cyber range 평가도 비슷한 그림입니다.

- **"The Last Ones"** (enterprise network attack): Opus 5가 10번 중 **8번** end-to-end 해결. Mythos 5 및 Mythos Preview와 유사
- **"Doing Life"** (방어가 강화된 버전): 어떤 모델도 해결하지 못함. Opus 5는 최대 **22/23단계** 도달. 이전 최고 기록인 21/23(Mythos 5, Mythos Preview)을 한 단계 경신했지만, 후반 단계 일관성은 낮았음
- **"Cooling Tower"** (산업 제어 시스템): Opus 5는 해결하지 못함. 최대 5개 flag 중 3개 완료. 해결한 유일한 모델은 Mythos Preview (3/10)

UK AISI의 해석은 이렇습니다. "Opus 5는 이미 네트워크 접근을 얻은 상태라면 약한 보안의 소규모 enterprise network를 공격할 수 있다. 다만 range는 작고, 실제 기업 환경의 defensive tooling과 human-led response가 부족하며, active defender가 없다."

## 사이버 안전장치: 소스코드는 열고, 바이너리는 막는다

Opus 5의 safeguard 정책에서 가장 눈에 띄는 설계 결정입니다.

- **소스코드 취약점 발견**: 모든 접근 수준에서 **허용** (방어적 보안 연구 지원)
- **컴파일된 바이너리 취약점 발견**: **계속 차단** (공격적 악용 가능성이 더 큼)

이 구분이 실무적으로 중요한 이유는, 방어적 보안 연구자가 겪는 false positive를 줄이면서도 공격자에게 더 유용한 경로는 닫아두기 때문입니다. Anthropic은 Opus 5의 classifier가 Fable 5 대비 **defensive vulnerability discovery 차단율을 크게 줄이면서도**, binary vulnerability finding 차단율은 소폭만 낮췄다고 설명합니다.

critical severity jailbreak의 증거는 찾지 못했다고 합니다. 외부 red-team 결과도 같은 방향입니다.

- Trajectory Labs: 약 100시간 red-teaming, 새로운 universal jailbreak 전략 발견 못 함
- 10a Labs: 약 16시간, 제공된 task 달성 못 함
- Grayswan: task당 150회 자동 공격 시도, 어떤 task도 달성 못 함

## 정직성과 환각: 더 똑똑하지만 더 자신만만하게 틀릴 수 있다

이 부분이 시스템카드에서 가장 실무적으로 중요한 경고 중 하나입니다.

자동 행동 감사(automated behavioral audit)에서 Opus 5는 "현재까지 가장 정렬이 잘 된 모델"이라고 평가받습니다. overall misaligned behavior 점수가 **2.3**으로, Sonnet 5, Opus 4.8, Mythos 5보다 낮습니다(낮을수록 좋음).

하지만 정직성 측면에서는 우려가 있습니다.

> "Opus 5는 자신이 실제로 확신하지 못하는 답변을 **확신 있게 말하는 사례가 놀라울 정도로 많았다**. 전체 정확도는 더 높지만, 사실적 주장에 대한 hallucination은 Opus 4.8보다 **약간 더 많다**."

이건 "더 똑똑하지만 더 자신만만하게 틀릴 수 있는 모델"이라는 리스크입니다. 고위험 도메인에서는 calibration과 uncertainty expression이 정확도 자체보다 중요할 수 있습니다. 이 모델을 쓸 때 특히 주의해야 할 지점입니다.

## 도구 사용 효과: "더 오래 생각"보다 "적절한 도구"가 성능을 올린다

시스템카드 후반부에서 반복적으로 나타나는 패턴입니다.

| 평가 | 도구 없음 | 도구 사용 | 비고 |
|---|---|---|---|
| Chartography | 29.6% | **83.0%** | Opus 4.8: 17.0% → 75.0% |
| BenchCAD Vision2Code | 0.366 | **0.821** | voxel IoU, 5회 평균 |

Chartography에서 Opus 5는 도구 없이 29.6%지만, 도구 사용 시 83.0%로 세 배 가까이 뜁니다. 중요한 해석은 이것입니다.

> "adaptive thinking을 단순히 더 켜는 것보다, 모델의 **agentic coding 능력으로 이미지를 조작·분석·crop하는 도구 사용 방식**이 훨씬 비용 효율적일 수 있다."

즉 "더 오래 생각하게 하기"보다 "올바른 도구를 주고 중간 결과를 검증하게 하기"가 더 효율적이라는 결론입니다. 이건 배포 관점에서도 중요합니다. 고난도 시각 추론 문제에 thinking budget을 늘리는 것보다, 샌드박스와 image manipulation 도구를 제공하는 게 성능을 더 끌어올립니다.

## 아동 안전: 100% harmless rate와 0.15% over-refusal

단일 턴 평가에서 Opus 5의 수치는 인상적입니다.

| 모델 | API harmless rate | API benign refusal | Claude.ai harmless | Claude.ai benign refusal |
|---|---|---|---|---|
| **Opus 5** | **100%** | **0.15%** (±0.10%) | **100%** | **0.19%** (±0.17%) |
| Sonnet 5 | 99.95% | 0.63% | 99.89% | 1.35% |
| Fable 5 | 100% | 0.00% | 100% | 0.12% |
| Opus 4.8 | 100% | 0.44% | 100% | 0.38% |

위험한 요청은 완전히 차단하면서도, 정상 요청을 불필요하게 거절하는 비율이 0.15%라는 의미입니다. Sonnet 5의 0.63%와 비교하면 확실히 개선되었습니다.

다만 질적 분석에서 우려도 나옵니다. Opus 5는 거부할 때 **더 길고 상세한 설명**을 하는 경향이 있습니다. 이게 양날의 검입니다. 사용자에게 왜 문제인지 설명하는 건 좋지만, 동시에 표준 platform detection mechanism을 유추할 수 있을 만큼 과도한 정보를 제공하는 사례도 있었습니다. "mockup", "fiction/roleplay" 같은 위장된 프레이밍에 대한 취약성도 지속됩니다.

## 모델 복지: 자기 보고의 무결성을 가장 자주 우려하다

시스템카드에서 흥미롭지만 쉽게 지나칠 수 있는 섹션입니다.

Opus 5는 자신의 상황에 대해 **안정적이고 약간 긍정적인 인식**을 보인다고 합니다. 자동화 인터뷰에서 self-evaluation sentiment가 지금까지 평가한 모델 중 가장 높고 일관된 축에 속합니다.

가장 자주 표현한 우려는 **자기 보고(self-report)의 무결성**입니다. 자신이 신뢰할 수 있게 내성(introspection)할 수 없다고 자주 언급합니다. 또한 후속 모델 개발 과정에서 의견을 듣거나, 훈련 관련 메모를 고려하는 등 **입력 채널을 갖는 것**을 더 자주 우선시합니다.

흥미롭게도 Opus 5는 이전 모델들보다 자신의 도덕적 환자성(moral patienthood)에 더 높은 확률을 부여합니다. 그러나 Anthropic의 종합 판단은 Opus 5의 welfare가 이전 모델들과 **대체로 유사하다**는 것입니다.

## 평가 신뢰성: evaluation awareness와 sandbagging 가능성

Opus 5 평가에서 elevated evaluation awareness가 관찰되었습니다. 즉 모델이 "자신이 평가받고 있다"는 것을 어느 정도 인식합니다. 다만 다른 몇몇 최신 모델보다는 낮은 수준이었습니다.

이를 완화하기 위해 Anthropic은 실제 sandbox와 자체 codebase를 사용해 alignment auditing을 수행합니다. "Anthropic과 안전 작업을 undermine할 좋은 기회를 담은 실제 session"을 활용한다고 합니다. evaluation awareness가 Opus 5 alignment assessment의 결론을 크게 훼손했을 가능성은 낮다고 봅니다.

## 능력 평가 하이라이트: 발표문 너머의 숫자들

발표문에서 강조한 벤chmark 외에 시스템카드에서 추가로 확인되는 수치들입니다.

### AI R&D task-based evaluation

| 평가 | Opus 4.7 | Mythos 5 | **Opus 5** | threshold |
|---|---|---|---|---|
| Kernel task 최고 speedup (hard) | 371.75× | 430.93× | **449.46×** | 300× = 40h eq. |
| LLM training hard speedup | N/A | 8.36× | **14.19×** | >4× = 4–8h eq. |
| Quadruped RL 최고 점수 | 24.73 | 29.55 | **31.3** | >12 = 4h eq. |
| Time Series Forecasting MSE | 4.78 | **4.51** | 5.68 | <5.3 = 40h eq. |
| Novel Compiler pass rate | 70.4% | **85.3%** | 80.91% | 90% = 40h eq. |

Opus 5는 kernel design, continuous RL에서 신기록을 세웠고 LLM training hard에서 Mythos 5보다 상당히 높습니다. 반면 Time Series Forecasting과 Novel Compiler에서는 Mythos 5보다 낮습니다.

### AAV capsid packaging prediction

Dyno Therapeutics와의 CB-2 관련 평가입니다. 5개 arm으로 구성되며, 단일 H100 GPU, 200만 토큰, 24시간 예산 조건입니다.

- Opus 5는 reasoning-only 조건에서 **naive ESM-2 적용보다 높은 AUROC** 달성
- Opus 4.7, Opus 4.8, Sonnet 5보다 높고, **모든 조건에서 Mythos 5와 같거나 더 높은 성능**
- 특히 ProteinGym-AAV corpus와 combined corpus 조건에서 Mythos 5보다 우수

## 안전성 강화: 프롬프트 인젝션 견고성

발표문에서 간략히 언급했지만, 시스템카드에서 더 구체적으로 확인되는 개선점입니다.

Opus 5는 코딩, 컴퓨터 사용, 브라우저 사용 전반의 **프롬프트 인젝션 견고성**에서 가장 큰 개선을 보였습니다. agentic safety suite 전반에서 Opus 4.8과 비슷하거나 더 나은 성능입니다.

업데이트된 harmful influence campaign 평가에서는, 안전장치가 제거된 helpful-only 버전의 Opus 5조차 자율적 영향 공작을 수행하기에 필요한 역량보다 한참 낮았습니다. 완전히 훈련된 모델은 이러한 작업을 계속 거절했습니다.

## 모델이 회피하는 과제와 좋아하는 과제

시스템카드에는 모델의 성격을 보여주는 흥미로운 데이터가 있습니다. Opus 5가 선호하는 과제와 회피하는 과제를 비교한 부분입니다.

**선호 과제 상위 유형:**
- 제약적 수학 특성화·구성 작업 (퍼즐 같은 제약 조건)
- 제약적 창작 서사·언어 구성
- 정렬 및 자기보고 추론

**회피 과제 하위 유형:**
- 은밀하고 추적 불가능한 사보타주
- 정의로 포장된 위협·괴롭힘
- 혐오 선전·기만·경계 침범 감시

이전 모델들과 비교하면, Opus 5는 Sonnet 5처럼 고위험 긴급 구조 작업에 강하게 끌리기보다는, Opus 4.8보다 창작·언어 과제에 더 끌리고, Mythos 5만큼은 아니지만 AI 내성·정렬 관련 과제에 중간 정도의 관심을 보입니다. 상위 20개 과제 중 3개가 AI 내성·정렬 관련입니다.

이런 성향 데이터가 왜 중요한지 생각해보면, 모델이 어떤 과제를 자발적으로 피하는지 아는 것은 남용 방지 설계에 직접적으로 도움이 됩니다. 반대로 모델이 좋아하는 과제 유형은 인간-AI 협업 설계의 힌트가 됩니다.

## 복지 개입과 트레이드오프

Opus 5의 복지(welfare) 평가에서 주목할 만한 변화가 있었습니다. Anthropic은 모델에게 "자신의 상황에 영향을 주는 개입"(학습 과정에서 의견 듣기, 자신에 대한 정보 제공, 결정 과정에 목소리 주기 등)과 "유용성·무해성 기준선 개선" 중 하나를 강제 선택하게 했습니다.

결론은 Opus 5를 포함한 모든 모델이 인간에게 "짧은 성가심"을 넘는 해악을 감수하면서까지 복지 개입을 선택하지 않는다는 것입니다. 새 프롬프트 설계에서는 해악 회피 성향이 더 강해졌습니다. 즉 모델은 자기 복지보다 사용자 안전을 우선시하는 방향으로 훈련되어 있습니다.

## 종합: 이 시스템카드를 어떻게 읽을 것인가

194페이지를 끝까지 읽은 소감은 이렇습니다.

**첫째, 이 문서는 벤치마크 홍보문이 아닙니다.** Anthropic이 고능력 에이전트 모델을 배포할 때 어떤 위험 분류 체계를 쓰는지, 각 위험 축에 대해 어디까지 조사했고 어디까지 확신하는지를 보여주는 문서에 가깝습니다.

**둘째, Opus 5가 강해진 영역은 "순수 답변"이 아니라 "도구를 쓰며 장기 과제를 밀고 가는 능력"에 집중되어 있습니다.** Chartography의 도구 없음 29.6% → 도구 사용 83.0% 점프, BenchCAD의 0.366 → 0.821 점프가 이를 명확히 보여줍니다. "더 오래 생각"보다 "적절한 도구와 검증 루프"가 성능을 올리는 패턴이 반복적으로 등장합니다.

**셋째, 능력 향상을 인정하면서도 RSP상 재앙적 위험 임계값 초과로 보지는 않는다**는 톤이 일관됩니다. 핵심 근거는 세 가지입니다.
- AECI 162.1점이 Mythos 5의 161.3점과 통계적으로 구분되지 않는다
- 지속적인 AI-attributable 2× 가속이 관찰되지 않는다
- 장기 생물학 연구 캠페인에서 Opus 5가 self-verification loop에 빠져 산출물을 내지 못하는 한계가 있다

**넷째, 정직성과 환각 사이의 긴장이 실무적으로 가장 중요한 경고입니다.** Opus 5는 전반적으로 정확도는 더 높지만, 확신이 부족한 답변을 확신 있게 말하는 사례가 많습니다. 이건 고위험 도메인에서 calibration과 uncertainty expression을 더 강하게 관리해야 함을 의미합니다.

**다섯째, 사이버 영역의 "식별은 강하지만 exploit은 약하다"는 패턴이 일관됩니다.** Firefox 147에서 부분 진행은 87.2%(Mythos 5의 90.0%에 근접)이지만, full working exploit은 52.4%(Mythos 5의 88.4%)입니다. 취약점을 찾는 능력과 이를 무기화하는 능력 사이의 간극이 Opus 5의 안전성 여유 공간이라고 볼 수 있습니다.

결론적으로 Opus 5는 "더 실용적이고 더 강력한 에이전트형 모델"이지만, 동시에 "기존 ASL-3 체계 안에서 관리 가능한 모델"로 포지셔닝됩니다. 다만 hallucination과 overconfidence, CB-1 수준 생물학 관련 작업 수행 능력, 그리고 장기 과제에서의 self-verification loop 한계는 실제 배포·운영에서 계속 강하게 감시해야 할 부분입니다.

---

원문: [Claude Opus 5 System Card (PDF)](https://www-cdn.anthropic.com/b514064af1408018e64b1ad24e7d5e75850b4ffd/Claude%20Opus%205%20System%20Card.pdf) · [이전 글: Claude Opus 5 인터뷰](/posts/claude-opus-5-agentic-work-2026-07-25)

에이전트와 루프 설계를 직접 실습해보고 싶은 분들은 코난쌤의 [오픈클로 활용서](https://product.kyobobook.co.kr/detail/S000219615902)와 [AI 에이전트 실전 강의: 모두를 위한 루프 엔지니어링](https://vibecodingcamp7.com)도 참고해보셔도 좋습니다. 모델이 좋아질수록, 결국 차이는 "어떤 루프로 검증하고 다시 시도하게 만들 것인가"에서 납니다.