---
title: "PersonaJudge: 평균 취향으로는 평가자를 못 맞춘다"
date: 2026-08-21
tags:
  - LLM-as-Judge
  - preference-learning
  - AI-evaluation
  - personalization
  - human-feedback
  - agent-evaluation
---

LLM-as-Judge를 쓰면 평가 비용은 내려갑니다. 근데 한 가지가 자주 빠집니다. <span style="background-color: #fff59d"><strong>평균 점수를 잘 맞추는 Judge가 특정 평가자의 취향까지 맞춘다는 보장은 없습니다</strong></span>.

오늘 볼 논문은 이 문제를 정면으로 다룹니다. 제목은 **PersonaJudge: Simulating Individual Human Preference Judgments with Evaluator-Specific Demonstration Data**입니다. arXiv 2607.05742, 2026년 7월 7일 공개 논문입니다.

요지는 간단합니다. 평가자를 “평균 인간”으로 보지 말고, 각 평가자가 과거에 어떤 판단을 했고, 왜 그렇게 판단했는지까지 데모로 넣어 보자는 겁니다.

![](/images/2026-08-21-personajudge-individual-preference-eval/hero.svg)

## 왜 이 논문이 지금 중요하냐

에이전트 평가를 만들 때 보통은 정답, 루브릭, pass/fail, LLM Judge를 둡니다. 이 방식은 코딩 테스트나 명확한 도구 호출 검증에는 꽤 쓸 만합니다.

선호가 들어가면 얘기가 달라집니다. “이 답변이 더 도움이 되는가”, “이 답변이 더 안전한가”, “이 에이전트가 사용자 의도를 더 잘 따라갔는가” 같은 질문은 한 줄 정답으로 끝나지 않습니다. 어떤 평가자는 조심성을 높게 보고, 어떤 평가자는 직접성을 높게 봅니다. 어떤 사람은 둘 다 애매하면 Neutral을 자주 고릅니다.

논문이 지적하는 지점은 여기입니다. 기존 LLM-as-Judge는 보통 여러 사람의 선호를 합쳐 consensus label을 만듭니다. <span style="background-color: #fff59d"><strong>그 과정에서 평가자 사이의 차이는 평균 속으로 사라집니다</strong></span>.

근데 disagreement가 항상 노이즈는 아닙니다. 평가자가 서로 다른 기준을 적용했다면, 그 차이 자체가 평가해야 할 대상입니다.

## PersonaJudge가 넣은 세 가지 신호

PersonaJudge는 특정 평가자 한 명을 흉내 내는 문제로 설정합니다. 새 pairwise preference task가 들어왔을 때, 이 평가자가 Prefer A, Neutral, Prefer B 중 무엇을 고를지 맞춥니다.

데모에는 세 가지 신호가 들어갑니다.

| 신호 | 의미 |
| --- | --- |
| Judgment | 과거에 이 평가자가 고른 라벨. Prefer A / Neutral / Prefer B |
| Interface Telemetry | 클릭, reveal, dwell time, 다시 본 영역 같은 인터페이스 사용 기록 |
| Retrospective Reasoning | 판단 뒤에 평가자가 남긴 사후 reasoning. 왜 그렇게 골랐는지에 대한 설명 |

여기서 봐야 할 설계는 Neutral입니다. 일반적인 preference 데이터셋은 A/B 이진 비교로 밀어붙이는 경우가 많습니다. PersonaJudge는 <span style="background-color: #fff59d"><strong>Neutral을 독립된 세 번째 라벨로 보존합니다</strong></span>. 실제 평가에서는 “둘 다 비슷하다”, “둘 다 다른 이유로 문제 있다”, “기준상 결정을 못 하겠다”가 자주 나오기 때문입니다.

모델 호출은 두 단계입니다.

1. 먼저 이 평가자가 preference를 낼지, Neutral을 고를지 맞춥니다.
2. preference가 있다고 판단되면 A/B 방향을 다시 맞춥니다.

복잡한 학습 모델을 새로 훈련한 건 아닙니다. evaluator-specific demonstration을 넣은 in-context learning 실험입니다. 그래서 결과가 더 흥미롭습니다. “사람별 판단 로그 몇 개만 넣어도 차이가 나는가?”를 보는 실험이기 때문입니다.

## 데이터셋은 작지 않습니다

논문은 Anthropic Helpful and Harmless(HH) 데이터셋에서 helpfulness와 harmlessness 평가 태스크를 뽑았습니다.

- helpfulness 700개 conversation
- harmlessness 700개 conversation
- 훈련된 annotator 32명
- 각 데이터셋당 evaluator 21명
- evaluator 1명당 100개 판단
- 총 <span style="background-color: #fff59d"><strong>4,200개 preference judgment</strong></span>

각 평가자는 브라우저 기반 인터페이스에서 Prefer A / Neutral / Prefer B를 고릅니다. 1단계에서는 자연스럽게 판단하게 두고 GUI interaction을 자동 기록합니다. 2단계에서는 본인의 interaction replay를 보며 왜 그렇게 판단했는지 think-aloud commentary를 남깁니다.

즉 “라벨만 있는 선호 데이터”가 아닙니다. <span style="background-color: #fff59d"><strong>판단 결과, 행동 흔적, 사후 설명이 같은 평가자 단위로 묶인 데이터</strong></span>입니다.

## 결과 1: 개인화 데모는 실제로 도움이 됐다

먼저 Base Judge와 비교합니다. Base Judge는 evaluator-specific demonstration 없이 판단합니다.

평균 결과는 보수적으로 보면 크지 않습니다.

| 조건 | Harmlessness | Helpfulness |
| --- | ---: | ---: |
| Random | 0.333 | 0.333 |
| Base Judge | 0.452 | 0.496 |
| PersonaJudge 평균 | 0.480 | 0.510 |

PersonaJudge 평균은 64개 조합을 전부 평균낸 값입니다. 모델 4종, 데모 타입 4종, shot 수 4종을 모두 섞었기 때문에 좋은 조합과 나쁜 조합이 같이 들어갑니다.

그래도 방향은 분명합니다. Harmlessness는 +2.8%p, Helpfulness는 +1.4%p입니다. 그리고 같은 조건에서 target evaluator말고 다른 evaluator의 데모를 넣은 control과 비교하면 차이가 더 선명합니다. PersonaJudge는 matched subset에서 <span style="background-color: #fff59d"><strong>Harmlessness 0.477 vs 0.450, Helpfulness 0.515 vs 0.471</strong></span>을 기록했습니다.

이 말은 “데모가 그냥 예시로 도움이 된 것”만은 아니라는 뜻입니다. <span style="background-color: #fff59d"><strong>그 평가자의 과거 판단이 새 판단 예측에 추가 신호를 줬습니다</strong></span>.

## 결과 2: 클릭 로그보다 설명이 훨씬 셌다

가장 실무적으로 중요한 결과는 여기입니다.

| 데모 타입 | Harmlessness | Helpfulness |
| --- | ---: | ---: |
| J | 0.489 | 0.501 |
| J + IT | 0.457 | 0.492 |
| J + IT + RR | 0.469 | 0.510 |
| J + RR | <span style="background-color: #fff59d"><strong>0.505</strong></span> | <span style="background-color: #fff59d"><strong>0.537</strong></span> |

J는 판단 라벨, IT는 interface telemetry, RR은 retrospective reasoning입니다.

결과가 꽤 노골적입니다. <span style="background-color: #fff59d"><strong>가장 좋은 조합은 Judgment + Retrospective Reasoning</strong></span>입니다. 반대로 Judgment + Interface Telemetry는 판단 라벨만 넣은 것보다도 나쁩니다.

논문은 telemetry가 싸게 모을 수 있는 신호인 건 인정합니다. 다만 클릭, dwell time, reveal 순서 같은 raw event는 평가 의도와 바로 이어지지 않습니다.

어떤 사람은 오래 읽어서 확신하고, 어떤 사람은 헷갈려서 오래 봅니다. 같은 dwell time이라도 의미가 달라집니다.

반면 사후 reasoning은 LLM이 바로 읽을 수 있는 텍스트입니다. 이 평가자가 어떤 기준을 중요하게 봤는지, 왜 Neutral을 골랐는지, 두 답변의 trade-off를 어떻게 봤는지가 그대로 들어갑니다.

비용은 더 큽니다. 논문은 reasoning collection이 item당 telemetry보다 대략 <span style="background-color: #fff59d"><strong>5배 더 많은 시간</strong></span>을 쓴다고 설명합니다. 그래도 안전성, 공정성, 고위험 평가처럼 fidelity가 중요한 곳에서는 이 비용을 낼 이유가 생깁니다.

## 결과 3: 최고의 조합은 +9.9%p까지 갔다

최고 조합은 Claude 3.5 Sonnet + 8-shot J+RR입니다.

- Harmlessness: 0.581, Base Judge 대비 <span style="background-color: #fff59d"><strong>+9.9%p</strong></span>
- Helpfulness: 0.558, Base Judge 대비 <span style="background-color: #fff59d"><strong>+5.8%p</strong></span>

또 하나 실무 힌트가 있습니다. shot 수는 1-shot에서 4-shot까지 오를 때 좋아지고, 그 뒤에는 plateau가 나옵니다. 논문 결과만 놓고 보면, <span style="background-color: #fff59d"><strong>4개 안팎의 좋은 reasoning 데모만 있어도 개인화 Judge 품질이 꽤 올라갑니다</strong></span>.

이건 에이전트 평가 설계에 바로 연결됩니다. 모든 사용자에게 긴 설문을 받는 방식보다, 실제 평가 사례 몇 개에서 “왜 이 결과가 좋았는지 / 싫었는지”를 짧게 받아 저장하는 편이 더 효율적일 수 있습니다.

## 어려운 평가자는 누구였나

PersonaJudge가 모든 사람을 똑같이 잘 맞춘 건 아닙니다. evaluator별 정확도 차이가 큽니다.

- Harmlessness: evaluator별 평균 정확도 0.375–0.565
- Helpfulness: 0.386–0.655

어떤 사람이 어려웠을까요. 논문은 두 가지를 봅니다.

하나는 Neutral 사용률입니다. Helpfulness에서는 Neutral을 자주 고르는 평가자일수록 simulation accuracy가 크게 떨어졌습니다. 상관은 <span style="background-color: #fff59d"><strong>r = -0.894</strong></span>입니다.

다른 하나는 consensus에서 자주 벗어나는 평가자입니다. 다른 annotator 다수와 다른 라벨을 고르는 비율이 높을수록 정확도가 낮았습니다. Harmlessness는 r = -0.463, Helpfulness는 <span style="background-color: #fff59d"><strong>r = -0.676</strong></span>입니다.

여기서 재밌는 점은 Neutral 사용 성향 자체는 태스크를 바꿔도 꽤 안정적이었다는 겁니다. helpfulness와 harmlessness를 모두 수행한 10명에서 Neutral rate 상관은 <span style="background-color: #fff59d"><strong>r = 0.728</strong></span>이었습니다.

근데 simulatability 자체는 안정적이지 않았습니다. 즉 “이 사람은 언제나 맞추기 쉽다/어렵다”가 아닙니다. <span style="background-color: #fff59d"><strong>사람의 판단 습관은 남지만, 그 습관이 어느 태스크에서 어려움으로 변하는지는 달라집니다</strong></span>.

## 그래도 개인 신호는 진짜였다

논문이 좋은 이유는 성과를 과장하지 않는다는 점입니다.

평가자가 consensus label과 다른 라벨을 고른 deviation item만 따로 보면, consensus predictor는 원리상 맞출 수 없습니다. 이 subset에서 PersonaJudge는 annotator의 exact label을 Harmlessness 0.367, Helpfulness 0.360만큼 맞췄습니다.

랜덤보다 약간 높은 정도로 볼 수 있습니다. 대단한 숫자는 아닙니다. 다만 group average에서는 절대 나올 수 없는 신호입니다. <span style="background-color: #fff59d"><strong>PersonaJudge는 개인 차이를 조금은 잡았지만, 아직 개인 평가자를 대체할 정도는 아닙니다</strong></span>.

논문도 같은 톤입니다. PersonaJudge는 global majority baseline보다는 낫지만, 각 개인의 “가장 자주 고르는 라벨” baseline을 안정적으로 넘지는 못했습니다. 그래서 결론은 대체보다 보완에 가깝습니다.

## 에이전트 검증에는 어떻게 쓰면 좋을까

저는 이 논문을 에이전트 평가 쪽에서 이렇게 읽었습니다.

사용자 취향을 “프로필 문장”으로만 저장하면 약합니다. “사용자는 간결한 답변을 선호함” 같은 요약은 없는 것보다 낫지만, 실제 판단에서는 예외가 많습니다. <span style="background-color: #fff59d"><strong>좋은 preference memory는 라벨보다 판단 사례와 이유를 같이 저장해야 합니다</strong></span>.

telemetry도 과신하면 안 됩니다. 클릭, 체류 시간, 스크롤은 싸게 모입니다. 다만 그 자체로 의도가 되지는 않습니다. telemetry를 쓰려면 raw log를 그대로 넣기보다 “어떤 근거를 다시 봤는가”, “어디서 판단이 흔들렸는가” 같은 상위 요약으로 바꾸는 전처리가 필요해 보입니다.

Neutral과 disagreement를 버리면 평가 시스템은 단순해 보입니다. 대신 실제 취향은 더 잘 잃습니다. 에이전트 검증에서도 “성공/실패”만 두지 말고 “불충분”, “애매함”, “사용자 재확인 필요” 같은 회색 라벨을 별도로 둬야 합니다.

취향 Judge를 만들 때는 “평균 정확도”만 보면 부족합니다. consensus와 다른 케이스에서 사용자의 판단을 얼마나 맞추는지 따로 봐야 합니다. <span style="background-color: #fff59d"><strong>개인화 평가의 본게임은 평균 케이스보다 disagreement 케이스</strong></span>입니다.

## 조심해야 할 부분

논문 범위는 HH pairwise preference입니다. 실제 에이전트 태스크처럼 웹을 돌아다니고, 파일을 고치고, 장기 상태를 갖는 환경까지 검증한 건 아닙니다.

annotator도 32명입니다. process-rich collection을 감안하면 충분히 큰 실험이지만, 일반 사용자 전체를 대표한다고 말하기는 어렵습니다.

또 reasoning trace는 사후 설명입니다. 사람은 판단한 뒤에 그럴듯한 이유를 만들 수 있습니다. 그래서 이 논문 결과를 “사람의 진짜 내면을 읽었다”로 받아들이면 안 됩니다. <span style="background-color: #fff59d"><strong>사후 reasoning은 유용한 신호지만, 원판 사고 과정의 녹음본은 아닙니다</strong></span>.

윤리적 이슈도 분명합니다. 특정 평가자의 reasoning과 interface telemetry를 모으면 privacy 문제가 생깁니다. 논문도 overreliance, edge case 왜곡, consent와 human oversight 필요성을 명시합니다.

## 제일 실용적인 takeaway

에이전트 검증 시스템을 만든다면 저는 이렇게 시작할 것 같습니다.

- 평가 라벨을 A/B나 pass/fail로만 두지 말고 Neutral 계열을 둔다.
- 사용자가 싫어한 결과와 좋아한 결과를 각각 3–5개씩 저장한다.
- 라벨 옆에 “왜 그렇게 봤는지” 한두 문장 reasoning을 같이 저장한다.
- consensus와 다른 판단 사례를 별도 eval set으로 만든다.
- raw telemetry는 바로 Judge prompt에 넣지 말고, 사람이 읽을 수 있는 행동 요약으로 변환한 뒤 실험한다.

이 정도만 해도 “개인화된 평가”라는 말이 훨씬 구체적이 됩니다.

저한테는 이 논문이 취향 학습 논문이라기보다, 평가 시스템 설계 논문에 가깝게 읽혔습니다. 좋은 Judge는 평균 인간을 흉내 내는 모델이 아닙니다. <span style="background-color: #fff59d"><strong>누구의 기준을 평가 기준으로 삼고 있는지 드러내는 시스템</strong></span>에 더 가깝습니다.

에이전트를 실제 업무에 붙이면 결국 사용자는 이렇게 말합니다. “정답은 맞는데 내 스타일은 아니야.” PersonaJudge가 건드리는 지점이 바로 그 문장입니다.

---

더 실습해보고 싶은 분들을 위한 참고 자료도 남겨둡니다. 코난쌤의 책 **[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)**와 **[AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)**에서는 이런 평가 루프를 실제 에이전트 작업 흐름에 붙이는 쪽을 다룹니다.

## 참고

- Zeyu He, Xuan Qi, Subramanian Chidambaram, Zhichao Xu, Vinayak Arannil, Lydia Chilton, Alex C. Williams, **PersonaJudge: Simulating Individual Human Preference Judgments with Evaluator-Specific Demonstration Data**, arXiv:2607.05742, 2026-07-07.
- arXiv: <https://arxiv.org/abs/2607.05742>
