---
title: "Relay-Bench: GPT-5.5가 43%에 머문다 — 도메인 간 추론 체인이 드러내는 LLM의 진짜 한계"
slug: 2026-07-23-relay-bench-multi-domain-reasoning
date: 2026-07-23
tags:
  - LLM
  - benchmark
  - reasoning
  - evaluation
  - agent
draft: false
summary: "한 프롬프트 안에 수학·코딩·검색·데이터 분석을 하나로 묶은 Relay-Bench에서 최강 모델 GPT-5.5조차 43.3%에 그쳤다. 벤치마크 포화 시대에 '순차적 다중 도메인 추론'이 새로운 시험대로 떠올랐다."
coverImage: ""
---

TL;DR — 한 프롬프트에 7개 영역의 문제를 직렬로 묶은 새 벤치마크 Relay-Bench에서 GPT-5.5(xHigh)가 43.3%, Gemini 3.1 Pro(High)가 40.0%, Claude Opus 4.7(Max)가 16.7%를 기록했다. 같은 모델들이 단일 도메인 벤치마크에서 85~95%를 받는 것과 극명한 대비를 이룬다.

## 벤치마크 포화, 그리고 새로운 접근

2025~2026년 LLM 벤치마크의 풍경은 한마디로 "포화(saturation)"로 요약된다. GPQA, MATH-500, AIME 2025 등 주요 벤치마크에서 프롰티어 모델들이 90% 이상을 기록하면서, 모델 간 실질적 차이를 구분하기 어려워졌다. 심지어 "Humanity's Last Exam"조차 출시 1년 만에 최고 점수가 4배 이상 상승했다.

Liam Swayne가 2026년 7월 20일 arXiv에 발표한 **Relay-Bench**[^1]는 여기에 대한 대답이다. 방법론의 복잡성을 늘리는 대신, 문제 자체의 구조를 바꿨다.

> "두 가지 일을 동시에 하려면 어느 쪽도 못 한다."
> — Publilius Syrus

![Fig. 1: Relay-Bench의 합성 문제 구조 — 각 서브문제가 하나의 최종 답으로 수렴하는 의존성 그래프](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-1-p1.png)

## 합성 문제(Composite Problem)의 구조

Relay-Bench의 모든 문제는 2~13개의 **서브문제(subproblem)**로 구성된 합성 문제다. 각 서브문제는 기존 벤치마크의 단일 문제와 유사하지만, 이들을 하나의 프롬프트로 엮으면 독립적으로 풀 때는 쉬운 문제들이 연쇄적으로 실패를 유발한다.

핵심 설계 원칙은 세 가지다:

1. **의존성 연쇄**: 한 서브문제의 정답이 다음 서브문제의 입력값이 되는 구조. 순환 의존성은 없다.
2. **도메인 혼합**: 수학, 코딩, 정보 추출(웹 검색), 시각 추론(텍스트로 인코딩), 일반 지식, 데이터 분석, 문제 해결 — 7개 영역을 한 문제 안에 배치.
3. **컨텍스트 부풀리기(Context Bloat)**: 약 7,813자의 무관한 "사용자 설정" 텍스트를 프롬프트에 삽입하고, 각 단어를 3글자 암호로 치환하는 논스(nonce) 인코딩을 적용. 일부 문제는 10,000회 이상의 변환 연산이 필요하다.

## 결과: 43.3%의 천장

![Fig. 2: 주요 벤치마크 간 모델 성능 비교 — Relay-Bench가 가장 낮은 점수대를 기록](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-2-p1.png)

세 프롴티어 모델의 Pass@1 결과는 다음과 같다:

| 모델 | Relay-Bench | HLE | ARC-AGI-2 | τ²-Bench |
|---|---|---|---|---|
| GPT-5.5 (xHigh) | **43.3%** | 44.3% | 75.8% | 95.6% |
| Gemini 3.1 Pro (High) | **40.0%** | 44.7% | 77.1% | 93.9% |
| Claude Opus 4.7 (Max) | **16.7%** | 40.0% | 39.6% | 85.0% |

평균 Relay-Bench 점수는 33.3%로, HLE 평균(42.9%), ARC-AGI-2 평균(79.3%), τ²-Bench 평균(92.7%)과 큰 격차가 있다.

## Claude Opus 4.7의 독특한 행동 패턴

![Fig. 4: 모델별 파싱 가능한 응답 및 정답 수](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-4-p4.png)

가장 흥미로운 발견은 모델별 "환각(hallucination)" 패턴이다. Claude Opus 4.7은 파싱 가능한 답변을 가장 적게 제출했지만, 제출한 답 중 오답은 단 하나였다. 환각률 50.0%는 세 모델 중 가장 낮다.

![Fig. 5: Relay-Bench와 AA-Omniscience에서의 환각률 비교](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-5-p4.png)

반면 GPT-5.5는 가장 많은 정답을 맞혔지만, 환각률도 33.3%로 가장 높았다. Gemini 3.1 Pro는 그 중간에 위치한다.

더욱 주목할 만한 점: Claude Opus 4.7은 인코딩된 문제(7,813자 이상의 의미 없는 텍스트가 포함된 프롬프트)를 만나면 **`stop_reason=refusal`**로 응답을 중단했다. 이는 Anthropic이 Claude Mythos에서 테스트 중인 안전장치가 과도하게 보수적으로 작동하고 있음을 시사한다.

## 컨텍스트 길이와 비용

![Table 1: 모델별 벤치마크 실행 비용 분석](/images/2026-07-23-relay-bench-multi-domain-reasoning/table-1-p5.png)

전체 벤치마크 개발 및 실행 비용은 **$163.29**에 불과했다. 모델별로 보면:

- **Claude Opus 4.7**: $33.76 (가장 비싸) — 한 문제에서 370만 입력 토큰, 41회 도구 호출 기록
- **Gemini 3.1 Pro**: $32.99 — 입력 단가는 가장 낮지만 캐시 적중률이 0.6%에 불과
- **GPT-5.5**: $22.44 (가장 저렴) — Gemini 대비 32% 할인

![Fig. 6: 비용 대비 정확도 — GPT-5.5가 파레토 최전선에 위치](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-6-p5.png)

GPT-5.5는 비용-성능 프론티어에서 두 경쟁 모델을 모두 지배(dominated)한다. 더 싸면서 더 정확하다.

## 왜 이 벤치마크가 다른가

기존 벤치마크들이 취한 방향은 세 가지다:

1. **입력 모달리티 확장** — MMMU, MathVista 등 시각 입력 추가
2. **도구 호출 평가** — ToolBench, API-Bank 등 에이전트 시나리오
3. **비이진 평가** — MT-Bench, AlpacaEval 등 LLM 판관제 도입

Relay-Bench는 정반대다. 텍스트만으로, 도구는 전부 허용하되, **문제 내부의 복잡성**을 극대화한다. 단일 도메인에서는 쉬운 문제들을 연쇄로 묶어 자연스럽게 실패율을 높인다.

![Fig. 7: Wilson 95% 신뢰구간 — 문제 수(30개)가 적어 구간이 넓다](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-7-p5.png)

## GAIA 포화 예측

![Fig. 3: GAIA 벤치마크의 포화 추세선 — 2025년 12월경 포화 예측](/images/2026-07-23-relay-bench-multi-domain-reasoning/fig-3-p3.png)

흥미롭게도 논문은 GAIA 벤치마크의 포화 시점을 2025년 12월 15일로 추정한다. 기록 경신 점수들의 추세선이 90%를 넘는 시점이다. Relay-Bench의 저자는 비교적 1~2년은 포화되지 않을 것으로 예상한다.

## 한계와 시사점

30개 문제라는 작은 테스트 셋은 명확한 한계다. Wilson 95% 신뢰구간이 넓어, 특히 Claude Opus 4.7의 경우 구간 폭이 점수 자체보다 크다. 저자도 더 큰 문제 셋과 더 좁은 범위의 필수 역량(검색·코드 실행 제외)을 요구하는 개정판을 후속 과제로 제시한다.

그럼에도 핵심 발견은 선명하다:

- **단일 도메인에서 90%+를 기록하는 모델들이 다중 도메인 연쇄 추론에서는 33~43%로 추락**한다
- **컨텍스트가 길어질수록 정확도가 하락**한다 — 이는 최근 연구[^2]와 일치한다
- **모델마다 "포기" 방식이 다르다** — Claude는 답변을 거부하고, GPT는 추측하고, Gemini는 중간에 끊긴다
- **도구 사용을 전부 허용해도 점수가 오르지 않는 구조적 한계**가 존재한다

이는 에이전트 시스템 설계자에게 직접적인 시사점을 준다. 여러 도메인이 얽히는 실제 작업에서는 단일 도메인 벤치마크 점수가 무의미할 수 있다. 하네스(에이전트 프레임워크)가 도메인 간 전환을 어떻게 관리하느냐가, 모델 자체의 추론 능력만큼 중요해진다.

## 더 실습해보고 싶은 분들께

다중 도메인 추천과 도구 호출이 얽히는 에이전트 루프를 직접 다뤄보고 싶다면, 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 자동화와 도구 연계를 50가지 사례로 풀어낸 실습서
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 컨텍스트 관리의 기초부터 실전까지

---

[^1]: Swayne, L. (2026). Relay-Bench: Evaluating LLMs on Multi-Domain Reasoning Chains. arXiv:2607.18438.
[^2]: Du, Y. et al. (2025). Context Length Alone Hurts LLM Performance Despite Perfect Retrieval. arXiv:2510.05381.
