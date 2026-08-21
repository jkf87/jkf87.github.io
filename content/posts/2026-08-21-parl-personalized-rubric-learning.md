---
title: "취향은 점수보다 루브릭으로 남겨야 한다"
date: 2026-08-21
tags:
  - personalization
  - LLM-as-Judge
  - preference-learning
  - rubric
  - AI-evaluation
  - agent-evaluation
---

개인화 평가를 하다 보면 이상한 장면이 자주 나옵니다. 모델은 “사용자 취향을 반영했다”고 말하는데, 막상 사람은 그냥 평범한 답변과 큰 차이를 못 느낍니다. <span style="background-color: #fff59d"><strong>취향을 하나의 점수로 줄이면, 무엇을 봐야 하는지부터 흐려집니다</strong></span>.

오늘 볼 논문은 이 지점을 꽤 직접적으로 찌릅니다. 제목은 Preference-Aware Rubric Learning for Personalized Evaluation입니다. arXiv 2605.31545, 2026년 5월 29일 공개 논문입니다.

요지는 단순합니다. 개인 취향을 평가하려면 “몇 점인가”를 먼저 묻기보다, <span style="background-color: #fff59d"><strong>그 사람이 반복해서 중요하게 보는 평가 기준을 루브릭으로 뽑아야 한다</strong></span>는 겁니다.

![Figure 1. PARL framework](/images/2026-08-21-parl-personalized-rubric-learning/figure-1-parl-framework.png)

*Figure 1. PARL은 사용자 과거 기록에서 후보 루브릭을 만들고, 일관성 검증과 RL 기반 판별 최적화를 거쳐 개인화 평가 기준으로 쓴다. (arXiv:2605.31545 Figure 1)*

## 왜 이 논문이 PersonaJudge 다음에 자연스럽냐

앞서 본 PersonaJudge는 “평균 평가자” 대신 특정 평가자를 시뮬레이션해야 한다고 봤습니다. PARL은 한 걸음 더 실무 쪽으로 갑니다. 특정 사용자의 과거 기록이 있을 때, 그 사람의 취향을 어떤 평가 기준으로 남길 수 있느냐를 묻습니다.

기존 개인화 평가에는 세 가지 방법이 많이 쓰입니다.

- ROUGE, BLEU, BERTScore 같은 자동 지표
- 사람이 직접 보는 human evaluation
- LLM-as-a-Judge 프롬프트

논문은 셋 다 개인화에는 빈틈이 크다고 봅니다. 자동 지표는 표면 유사도에 강하게 묶입니다. 외부 평가자는 사용자의 숨은 선호를 모릅니다. LLM Judge는 사용자 히스토리를 넣어도 대체로 정적인 프롬프트와 하나의 총점에 머무릅니다.

개인화의 어려움은 여기 있습니다. <span style="background-color: #fff59d"><strong>좋은 답변과 그 사람다운 답변은 같은 말이 아닙니다</strong></span>. 문장은 매끄러워도 사용자가 늘 쓰던 구조, 톤, 강조점, 생략 습관을 놓칠 수 있습니다.

## PARL이 요구한 세 조건

논문은 개인화 루브릭이 최소 세 조건을 만족해야 한다고 봅니다.

첫 번째는 Representativeness입니다. 사용자 히스토리에서 반복적으로 드러나는 선호를 충분히 담아야 합니다. 한두 샘플에서 우연히 나온 표현을 취향으로 착각하면 안 됩니다.

두 번째는 User-Consistency입니다. 루브릭이 여러 과거 문맥에서 계속 맞아야 합니다. <span style="background-color: #fff59d"><strong>특정 task 하나에만 맞는 기준은 개인 취향이 아니라 그 순간의 산물일 수 있습니다</strong></span>.

세 번째는 Discriminativeness입니다. 이게 제일 중요합니다. 루브릭은 사용자가 직접 쓴 응답과, 그럴듯하게 개인화된 모델 응답을 구분해야 합니다. 좋은 문장을 후하게 주는 기준이면 개인화 평가로는 약합니다.

이 세 조건을 묶어서 논문은 Personalized Evaluation as Learning이라는 표현을 씁니다. 평가를 고정된 판단으로 두지 않고, 사용자 히스토리에서 배워야 하는 대상으로 둡니다.

## 방법은 두 단계입니다

PARL은 크게 두 모듈로 움직입니다.

먼저 Preference Induction & Consistency Validation입니다. 사용자 과거 기록에서 후보 루브릭을 만듭니다. 예를 들면 “제품 리뷰에서 구체적 사용 장면을 먼저 설명한다”, “Reddit 글에서 개인 경험을 짧게 넣는다”, “뉴스 헤드라인에서 수치보다 사건의 행위자를 앞세운다” 같은 식입니다.

그다음 이 후보 루브릭이 다른 사용자 기록에도 일관되게 맞는지 검증합니다. 통과한 기준만 남깁니다. 이 과정은 잡음을 줄이는 필터입니다.

두 번째는 Discriminative Optimization via RL입니다. 여기서 PARL은 진짜 사용자 응답을 positive로 두고, 여러 개인화 생성 모델의 응답을 negative sample로 둡니다. 그리고 루브릭이 진짜 사용자 응답에 더 높은 점수를 주도록 margin을 키웁니다.

논문은 두 변형을 둡니다.

| 변형 | 보상 설계 | 의미 |
|---|---|---|
| PARL-A | GT 만족도 × 판별 margin | 실제 사용자 응답에 잘 맞고, 대안 응답과도 잘 구분하는 루브릭 |
| PARL-B | 판별 margin 중심 | 미묘한 사용자 고유 신호를 더 강하게 찾는 루브릭 |

여기서 눈에 들어오는 건 “평가자를 학습한다”는 점입니다. <span style="background-color: #fff59d"><strong>PARL은 답변 생성 모델을 더 잘 만들기보다, 답변을 볼 기준을 먼저 학습합니다</strong></span>.

## 실험은 세 가지 개인화 생성 task에서 했습니다

논문은 세 데이터셋을 씁니다.

| Task | 사용자 수 | 내용 |
|---|---:|---|
| Amazon Review Generation | 2,242명 | 사용자의 과거 리뷰를 보고 새 리뷰 생성 |
| Reddit Topic Writing | 2,452명 | 작성자 과거 글을 보고 Reddit 본문 생성 |
| News Headline Generation | 827명 | 기자/작성자 과거 헤드라인을 보고 새 헤드라인 생성 |

평가 방식도 흥미롭습니다. 루브릭이 진짜 사용자 응답, 일반 생성, RAG, SFT, GRPO, SFT+GRPO 같은 여러 출력에 대해 얼마나 통과 판정을 주는지 봅니다.

여기서 GT는 사용자가 실제로 쓴 응답입니다. Max-Diff는 GT 점수와 가장 강한 non-GT 대안 사이의 차이입니다. 이 값이 커야 루브릭이 “그 사람다운 응답”을 구분한다고 볼 수 있습니다.

## 결과: 그냥 루브릭 생성은 너무 관대합니다

Table 1에서 제일 먼저 보이는 건 PARL-0입니다. PARL-0은 GT에 거의 1.0에 가까운 높은 점수를 줍니다. 얼핏 좋아 보입니다.

근데 함정이 있습니다. PARL-0은 non-GT, RAG, SFT, GRPO에도 높은 점수를 자주 줍니다. <span style="background-color: #fff59d"><strong>모두를 통과시키는 루브릭은 친절해 보여도 평가 도구로는 약합니다</strong></span>.

예를 들어 Amazon Review에서 PARL-0은 GT가 `1.000`인데 Non도 `1.000`, RAG도 `0.998`, SFT도 `1.000`입니다. Max-Diff는 사실상 `-0.000`입니다. 즉 진짜 사용자 응답과 모델 응답을 나누지 못합니다.

PARL-A와 PARL-B는 달랐습니다. Amazon Review에서 PARL-A는 GT `0.931`, 가장 강한 대안보다 `+0.026` 높았습니다. PARL-B는 GT `0.930`, Max-Diff `+0.003`입니다.

Reddit Topic에서는 PARL-B가 더 강했습니다. GT `0.860`, Max-Diff `+0.036`입니다. News Headline에서도 PARL-B가 GT `0.804`, Max-Diff `+0.054`를 기록했습니다.

정리하면 이렇습니다. <span style="background-color: #fff59d"><strong>개인화 루브릭은 사용자를 잘 맞추는 것만으로 부족하고, 그럴듯한 모방을 밀어낼 수 있어야 합니다</strong></span>.

## user coverage도 차이가 큽니다

실무에서는 루브릭 품질만큼 coverage가 중요합니다. 특정 사용자에게 루브릭을 못 만들면 자동 평가 파이프라인에 넣기 어렵습니다.

Table 1에서 LM-8B의 user coverage는 Amazon `49.1%`, Reddit `75.0%`, News `66.9%`입니다. LM-235B는 각각 `84.6%`, `81.5%`, `87.1%`입니다.

PARL 계열은 거의 꽉 찹니다. PARL-A는 Amazon `99.3%`, Reddit `99.9%`, News `99.0%`입니다. PARL-B는 Amazon `99.5%`, Reddit `99.4%`, News `100.0%`입니다.

이 차이는 꽤 큽니다. 큰 모델에게 “사용자 루브릭 만들어줘”라고 시키는 것과, 루브릭 생성 자체를 학습시키는 것은 다른 문제라는 뜻입니다.

## ablation이 말해주는 것

Table 2도 실무적으로 중요합니다. Amazon Review에서 PARL-A를 기준으로 구성요소를 하나씩 뺐습니다.

| 설정 | GT | Max-Diff | User Coverage |
|---|---:|---:|---:|
| w/o PI | 0.953 | -0.018 | 81.1% |
| w/o CV | 0.916 | 0.011 | 90.5% |
| w/o RL | 0.931 | 0.001 | 49.1% |
| PARL-A | 0.931 | 0.026 | 99.3% |

PI를 빼면 GT 점수는 높지만 Max-Diff가 음수입니다. 사용자를 대표하는 기준이 약해져서 strong alternative를 밀어내지 못합니다.

CV를 빼면 coverage와 margin이 같이 내려갑니다. 불안정한 기준이 섞였다는 뜻입니다.

RL을 빼면 GT는 유지되지만 Max-Diff가 `0.001`로 거의 사라지고 coverage도 `49.1%`까지 내려갑니다. <span style="background-color: #fff59d"><strong>판별 margin을 학습하지 않으면 개인화 루브릭은 쉽게 일반 품질 평가로 미끄러집니다</strong></span>.

## LLM-as-a-Judge와도 직접 비교합니다

논문은 별도로 표준 LLM-as-a-Judge 방식도 봅니다. 같은 사용자 히스토리를 넣고, Qwen3-235B-A22B-Instruct가 1~5점으로 점수를 내게 했습니다.

결과는 일관적이지 않았습니다. Amazon Review에서는 어느 정도 작동했지만, Reddit Topic과 News Headline에서는 구분력이 크게 흔들렸습니다. 논문은 News Headline에서 평가 패턴이 뚜렷하지 않았다고 설명합니다.

이 대목이 중요합니다. 사용자 히스토리를 프롬프트에 넣는다고 자동으로 개인화 평가가 되는 건 아닙니다. Judge에게 히스토리를 보여주는 것과, Judge가 쓸 기준을 학습시키는 것은 다릅니다.

## 이걸 에이전트 평가에 붙이면 어떻게 되나

블로그 작업이나 에이전트 평가로 가져오면 그림이 꽤 선명합니다.

지금 우리가 만드는 자동 블로그 루프도 사실 개인화 평가 문제입니다. “좋은 글인가”만 보면 안 됩니다. 코난쌤 문체에 맞는지, 과한 AI 냄새가 없는지, 원문 수치를 보존했는지, 이미지가 원문 Figure인지, Threads로 옮겼을 때 자연스러운지까지 봐야 합니다.

이 기준들은 하나의 점수보다 루브릭에 가깝습니다. 그리고 실제로 지금도 voice gate, image gate, promo gate, Threads gate가 따로 존재합니다.

PARL식으로 보면 다음 단계가 보입니다.

- 승인된 글과 거절된 글을 나눠 저장한다
- 사용자가 좋아한 표현과 싫어한 표현을 루브릭 후보로 만든다
- 여러 글에서 반복되는 기준만 남긴다
- 좋은 일반 글과 “코난쌤다운 글”을 구분하는 margin을 키운다
- 최종 평가는 총점보다 루브릭별 pass/fail과 근거 문장으로 남긴다

취향은 기억해야 하고, 기억은 평가 가능한 기준으로 내려와야 합니다. 이 논문이 주는 실무 힌트는 여기에 가깝습니다.

## 한계도 있습니다

이 논문은 좋은 방향을 보여줍니다. 곧바로 모든 개인화 평가를 해결했다고 보기는 어렵습니다.

우선 task가 텍스트 생성에 묶여 있습니다. Amazon Review, Reddit Topic, News Headline은 모두 쓰기 스타일이 강하게 드러나는 과제입니다. 도구 호출형 에이전트나 장기 작업 에이전트에는 trajectory, side effect, policy compliance 같은 축이 추가됩니다.

또한 negative sample을 어떤 모델에서 뽑느냐가 중요합니다. 약한 negative만 있으면 루브릭이 쉽게 이깁니다. 너무 강한 negative를 쓰면 사용자 고유 신호와 일반 품질 신호를 분리하기 어려워질 수 있습니다.

그리고 사용자 히스토리 자체가 편향되어 있거나 오래된 취향을 담고 있으면, 루브릭도 그쪽으로 굳을 수 있습니다. 개인화 평가에는 업데이트와 폐기 정책이 같이 필요합니다.

## 저는 이렇게 읽었습니다

PersonaJudge가 “평균 평가자로는 특정 사람을 못 맞춘다”고 말한다면, PARL은 “특정 사람을 맞추려면 평가 기준 자체를 학습해야 한다”고 말합니다.

이건 LLM 개인화보다 넓은 이야기입니다. 에이전트, 블로그 자동화, 코드 리뷰, 교육 피드백, 추천 시스템 모두 비슷합니다. 평균 점수는 운영에 편해도, 반복되는 취향은 평균 안에서 사라집니다.

그래서 이 논문의 메시지는 꽤 실무적입니다. 개인화 시스템을 만들고 싶다면 생성기보다 평가기부터 개인화해야 합니다.

좋은 자동화는 “무엇을 만들까”만 배우지 않습니다. 무엇을 통과시킬지, 무엇을 보류할지, 무엇을 사용자다운 결과로 볼지까지 배웁니다.

## 더 실습해보고 싶은 분들께

더 실습해보고 싶은 분들을 위한 참고 자료도 남겨둡니다. 코난쌤의 책 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)와 [모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)에서는 이런 평가 루프를 실제 에이전트 작업 흐름에 붙이는 쪽을 다룹니다.

## 참고

- Yilun Qiu et al., Preference-Aware Rubric Learning for Personalized Evaluation, arXiv:2605.31545, 2026.
- Code: <https://github.com/SnowCharmQ/PARL>
- PersonaJudge 후속 맥락: 개인별 평가자 시뮬레이션에서 개인별 루브릭 학습으로 이어지는 흐름.
