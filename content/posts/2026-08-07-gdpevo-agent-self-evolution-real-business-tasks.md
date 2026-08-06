---
title: "GDPevo: 에이전트 자기진화를 실제 비즈니스에서 측정한 최초의 벤치마크"
date: 2026-08-07
tags:
  - agent
  - self-evolution
  - benchmark
  - LLM
  - harness
  - evaluation
  - enterprise
  - automation
  - skill
  - loop
source: huggingface
source_url: https://arxiv.org/abs/2608.03764
github_url: https://github.com/Prism-Shadow/GDPevo
authors:
  - conanssam
---

에이전트가 경험에서 배운다고 한다. 근데 그게 진짜인지 어떻게 알 수 있을까. GDPevo는 이 질문에 대한 가장 구체적인 답입니다.

## 핵심을 한 줄로

에이전트 자기진화(self-evolution)를 GDP 관련 실제 비즈니스 워크플로우에서 측정하는 최초의 벤치마크입니다. 6개 도메인 24개 태스크 그룹, 240개 태스크로 구성되어 있고, 핵심 설계인 규칙 혼합(rule hybridization) 덕분에 "훈련에서 배운 게 테스트에서 통했는지"를 귀속(attributable)할 수 있습니다.

## 왜 기존 벤치마크로는 안 되는가

기존 평가에는 세 가지 문제가 있습니다.

1. 경제적 가치가 있는 도메인 부재: 기존 벤치마크는 ALFWorld, WebShop 같은 연구용 환경에 머물렀습니다. 실제 기업에서 쓰는 CRM, ERP, 의료, 법무 워크플로우는 다루지 않았죠.
2. 귀속 불가: 기존 벤치마크의 train-test split은 "학습 효과"를 의도적으로 설계하지 않았습니다. 그래서 점수가 올라도 그게 경험 때문인지, 운 때문인지 알 수 없습니다.
3. 데이터 오염: 정적 벤치마크는 모델 학습 데이터에 노출됩니다. 유효성이 빠르게 무너지죠.

## 규칙 혼합: 학습 효과를 측정 가능하게 만드는 설계

GDPevo의 핵심입니다. 각 비즈니스 워크플로를 원자적 비즈니스 규칙(atomic business rules)으로 분해합니다.

예를 들어 CRM 리드 캡처 워크플로우에서:
- 후원자 상태 우선순위 규칙
- 블랙리스트 제외 규칙  
- 연락처 중복 제거 및 정규화 규칙
- 후속 조치 스케줄링 규칙

이 규칙들의 부분집합을 5개 훈련 태스크에 나누어 심습니다. 그리고 테스트 태스크에서는 이 규칙들을 새로 조합해서 냅니다. 에이전트가 훈련에서 규칙을 추론하고 테스트에서 조합해서 적용해야 점수가 오르도록 설계한 것입니다.

![GDPevo 데이터 구축 파이프라인](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-1-p4.png)

파이프라인은 3단계로 자동화됩니다:
1. 시드 시나리오 발견: 기존 도메인 벤치마크에서 후보 시나리오 제안
2. 태스크 그룹 생성: 공유 환경 + 훈련 5개 + 테스트 5개 태스크 생성
3. 검증 및 리뷰: 품질, 난이도, 다양성 체크

전 과정이 자동화되어 있어서 V1(120 태스크)에서 V2(240 태스크) 확장에 이틀 걸렸습니다. 오염 우려가 생기면 새 버전을 빠르게 만들 수 있습니다.

## 4개 에이전트 × 4개 감독 타입 실험

에이전트는 하네스 + 모델 조합 4가지로 구성했습니다.

| 에이전트 | 구성 |
|---------|------|
| GPT-5.5 / Codex | OpenAI 최상위 |
| Opus 4.8 / Claude Code | Anthropic 최상위 |
| GLM-5.2 / Codex | 비용 효율형 |
| DeepSeek-V4-Pro-Preview / Codex | 오픈 모델 |

감독 타입은 4가지입니다:
- base: 진화 없음 (기준선)
- fewshot: 훈련 문제 + 정답 제공 (SFT와 유사)
- reflect: 훈련 문제 + 자기 시도의 점수만 제공 (RL과 유사)
- self: 훈련 문제만 제공 (비지도 학습과 유사)

## 결과: 진화는 효과가 있지만, 한계는 멀다

![정확도-비용 트레이드오프](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-2-p8.png)

다섯 가지 핵심 발견이 있습니다.

1. fewshot이 가장 안정적입니다. 모든 에이전트에서 fewshot이 최고 정확도를 기록했습니다. base 대비 +2.59 ~ +16.44 pp 향상이 있었습니다.

2. 진화는 모델 훈련을 대체할 수 있습니다. GLM-5.2 fewshot이 GPT-5.5 base를 10.72 pp 차이로 앞섰습니다. 비용은 약 절반수준이었고요. DeepSeek-V4-Pro-Preview fewshot도 GPT-5.5 base와 비슷한 정확도를 냈는데, 비용은 1/28이었습니다.

3. 출발점이 낮다고 더 많이 배우는 건 아닙니다. DeepSeek-V4-Pro-Preview가 base 정확도가 가장 낮았지만(43.58%) 진화 효과도 가장 작았습니다(+5.21 pp). 반면 Opus 4.8이 base가 가장 높았고(50.63%) 진화 효과도 가장 컸습니다(+16.44 pp).

4. 진화는 비용도 줄입니다. GPT-5.5 fewshot은 정확도를 15.14 pp 올리면서 테스트 비용을 20.88% 줄였습니다.

5. 오라클 상한은 91.6%. 모든 규칙을 미리 알려준 oracle 설정에서 91.6%였습니다. 최고 진화 에이전트도 이에 한참 못 미칩니다. 자기진화 능력이 아직 갈 길이 멉니다.

## 크로스 도메인 전이: fewshot vs reflect

![크로스 도메인 전이 매트릭스](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-3-p9.png)

fewshot은 같은 도메인 안에서는 강한 반면, 다른 도메인으로 넘어가면 오히려 해로운 경우가 많았습니다. SFT와 비슷한 과적합 패턴입니다.

반면 reflect는 크로스 도메인에서 더 안정적이었습니다. 최악의 경우 -1.0 pp에 그쳤고, ERP → Finance로 +6.5 pp 전이도 관찰됐습니다. RL이 더 일반적인 스킬을 만든다는 해석이 가능합니다.

## 하네스보다 모델이 중요하다

여러 스킬 생성기(Codex, Claude Code, DeepAgents, OpenCode, Naive)를 비교했습니다. 결과는 놀랍습니다.

| 스킬 생성기 | GPT-5.5 정확도 | 향상 |
|------------|---------------|------|
| Naive | 65.12% | +15.46 pp |
| DeepAgents | 62.69% | +13.03 pp |
| Codex | 62.19% | +12.53 pp |
| Claude Code | 62.15% | +12.49 pp |
| OpenCode | 60.79% | +11.13 pp |

가장 단순한 Naive 생성기가 가장 성능이 좋았습니다. 하네스의 진화 방법(evolution method)보다 모델 자체의 지능이 진화 효과를 결정한다는 의미입니다. 진화 방법을 과도하게 엔지니어링하면 오히려 역효과가 났습니다.

## 채점과 비용

채점은 LLM judge가 아닌 결정론적 규칙 기반 그레이더를 사용합니다. 각 실패를 특정 규칙 위반으로 추적할 수 있습니다. 비용도 1급 지표로 다룹니다 — 토큰, 에이전트 턴, 달러 비용을 정확도와 함께 보고합니다.

## 정리

GDPevo가 보여주는 것은 명확합니다.

- 에이전트 자기진화는 효과가 있다. 최대 16.44 pp 향상.
- 오라클 상한(91.6%)에는 한참 못 미친다. 현재 최고 진화 에이전트가 65%대.
- fewshot(정답 제공)이 가장 안정적이지만 도메인 간 전이에서는 reflect(피드백만)가 더 낫다.
- 진화 방법보다 모델 지능이 더 중요하다. Naive 스킬 생성기가 복잡한 것보다 낮다.

에이전트가 "경험에서 배운다"는 말을 이제 측정할 수 있게 됐습니다. 그리고 그 측정 결과는, 아직 갈 길이 멉니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

---

> **원문**: [GDPevo: Evaluating Agent Self-Evolution on Real Business Tasks](https://arxiv.org/abs/2608.03764)
> **코드**: [github.com/Prism-Shadow/GDPevo](https://github.com/Prism-Shadow/GDPevo)
