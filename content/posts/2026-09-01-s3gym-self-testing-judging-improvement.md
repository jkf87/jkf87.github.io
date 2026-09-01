---
title: "S3Gym — 자기테스트와 자기판단이 성능 개선으로 이어지는지 보는 벤치마크"
date: 2026-09-01
tags: [agent, LLM, self-improvement, benchmark, memory, RL]
draft: false
description: "S3Gym은 LLM 에이전트가 자기테스트와 자기판단으로 얻은 경험을 세 가지 방식에 넣었을 때 실제 성능이 좋아지는지 검증한 벤치마크입니다."
---

## 결론 먼저

S3Gym 논문을 정리했습니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>에이전트가 스스로 테스트하고, 스스로 점수를 매기고, 그 경험을 다음 행동에 쓰면 정말 좋아지는가</strong></span>를 따로 재는 벤치마크입니다.

결과는 선명합니다. <span style="background-color: #fff59d"><strong>경험은 도움이 될 때가 있습니다. 근데 자동 개선을 보장하지 않습니다</strong></span>. Summary Memory는 규칙으로 압축되는 게임에서 좋았고, raw history는 현재 상태 디테일이 중요한 게임에서 더 나았습니다. 파라미터 Training은 Trust Evolution에서는 크게 좋아졌지만  <span style="background-color: #fff59d"><strong>Plants-vs-Zombies에서는 23점에서 6점으로 떨어진 뒤 그대로였습니다</strong></span>.

자기판단도 충분하지 않았습니다. 116,117개 transition을 비교했을 때, <span style="background-color: #fff59d"><strong>판단 품질과 다음 성능 향상의 상관이 거의 0에 가까웠습니다</strong></span>. 좋은 행동을 알아보는 단계와 그 판단을 다음 정책으로 바꾸는 단계가 분리된다는 뜻입니다.

## 핵심 요약 표 (기준일 2026-09-01, arXiv 2608.31100v1)

| 항목 | 값 |
| --- | --- |
| 논문 | S3Gym: Can LLMs Turn Self-Testing and Self-Judging into Self-Improvement? |
| 공개 | arXiv v1, 2026-08-31 UTC / 논문 표기 Date 2026-09-01 |
| 주제 | LLM agent self-improvement benchmark |
| 환경 | Chess, Minesweeper, Nullify, Tetris, Snake, Plants-vs-Zombies, Trust Evolution |
| 루프 | Self-Testing → Self-Judging → Self-Improvement |
| 경험 반영 방식 | History ICL, Summary Memory, parameter Training |
| 평가 | 탐색은 relaxed configuration, 평가는 held-out strict configuration |
| 주요 수치 | Self-Judging 분석 <span style="background-color: #fff59d"><strong>98 runs, 116,117 transitions</strong></span> |
| 소스 | https://arxiv.org/abs/2608.31100 / https://self-developing-agents.github.io/ |

## 선정 이유

최근 자기개선 에이전트 논문이 계속 나오고 있습니다. memory를 붙인다, skill을 쌓는다, harness를 고친다, RL로 훈련한다는 말은 많습니다. 근데 실제로는 한 가지 질문이 계속 남습니다.

경험을 많이 모은 뒤 다음 행동이 실제로 좋아지는지 확인해야 합니다.

S3Gym은 이 질문을 게임 환경으로 줄였습니다. 환경은 작게 만들고, 검증은 실행 가능하게 만들고, 탐색과 평가는 분리합니다. 에이전트는 탐색 중에 실제 verifier 점수를 보지 못합니다. 대신 자기 점수와 자기 요약을 만들고, 그걸 다음 행동에 써야 합니다.

![](/images/2026-09-01-s3gym-self-testing-judging-improvement/fig-1-p3.png)

Figure 1. 논문이 보는 자기개선 루프입니다. 사람도 테스트하고 판단하고 기억하거나 학습합니다. LLM 에이전트도 같은 구조로 Self-Testing, Self-Judging, Self-Improvement를 분리해서 봅니다.

## S3Gym이 재는 것

S3Gym은 단순 게임 성능 평가를 넘어서 봅니다. 이미 평가되는 고정 정책의 성능보다, 경험을 얻은 뒤 정책이 바뀌는지를 봅니다.

구성은 3단입니다.

1. Self-Testing: 에이전트가 relaxed 설정에서 여러 episode를 돌며 행동과 관찰을 모읍니다.
2. Self-Judging: 각 transition에 대해 스스로 점수를 매기고, 왜 좋았는지 나빴는지 판단합니다.
3. Self-Improvement: 그 경험을 History ICL, Summary Memory, Training 중 하나로 반영하고 strict held-out 설정에서 다시 평가합니다.

중요한 장치가 있습니다. <span style="background-color: #fff59d"><strong>탐색 seed와 평가 seed가 분리됩니다</strong></span>. <span style="background-color: #fff59d"><strong>평가 trajectory는 경험에 다시 들어가지 않습니다</strong></span>. 그래서 외운 행동이 아니라, 경험에서 뽑은 규칙이나 정책이 옮겨가는지를 봅니다.

![](/images/2026-09-01-s3gym-self-testing-judging-improvement/fig-2-p7.png)

Figure 2. S3Gym 전체 파이프라인입니다. 7개 text game에서 탐색 trajectory를 만들고, 자기판단을 붙인 뒤 History ICL, Summary Memory, Training으로 반영합니다. 업데이트된 에이전트는 더 엄격한 설정에서 평가됩니다.

## 경험을 넣는 3가지 방식

S3Gym은 경험을 반영하는 길을 3개로 나눕니다.

| 방식 | 의미 | 장점 | 약점 |
| --- | --- | --- | --- |
| History ICL | raw trajectory와 score를 context에 그대로 넣음 | 상태 디테일 보존 | context가 길고 노이즈가 남음 |
| Summary Memory | 점수 조건이 붙은 요약/전략을 memory로 보관 | 규칙 압축 가능 | 디테일이 필요한 과제에서 정보 손실 |
| Parameter Training | 선택·수정된 trajectory로 모델 가중치 업데이트 | 추론 때 history 없이 지속 | 잘못된 경험이 굳거나 negative transfer 발생 |

여기서 중요한 점은 방식별 승자가 하나로 고정되지 않는다는 점입니다. <span style="background-color: #fff59d"><strong>Summary Memory는 Nullify, Tetris, Trust에서 평균 NABA가 더 좋았습니다</strong></span>. 반대로 <span style="background-color: #fff59d"><strong>Minesweeper, PvZ, Snake는 direct history가 더 좋았습니다</strong></span>. Chess는 거의 갈렸습니다.

이 차이는 직관적입니다. Trust처럼 “상대가 이런 보상 구조면 defect하라”는 규칙으로 압축되는 과제는 summary가 좋습니다. Minesweeper나 Snake처럼 현재 board, hazard, 위치가 중요한 과제는 raw history의 디테일이 살아 있어야 합니다.

![](/images/2026-09-01-s3gym-self-testing-judging-improvement/table-7-p18.png)

Table 7. Summary Memory와 direct-history ICL 비교입니다. <span style="background-color: #fff59d"><strong>GPT-5.5 / Trust에서는 Summary direction이 opponent-conditioned policy로 바뀌며 ΔNABA +66.89</strong></span>를 만들었고, o3-mini / Tetris에서는 look-ahead 규칙으로 ΔNABA +14.42를 만들었습니다.

## Training은 강하고 불안정합니다

파라미터 Training은 경험을 모델 안에 넣는 방식입니다. 잘 되면 추론 때 별도 history나 memory가 없어도 좋아집니다. 근데 실패하면 나쁜 경험도 같이 굳습니다.

Qwen3-8B를 20개 checkpoint로 본 결과가 그렇습니다. <span style="background-color: #fff59d"><strong>Trust Evolution은 0점에서 최대 30점까지 올라갔고</strong></span>, 업데이트된 19개 checkpoint 중 18개가 초기 baseline보다 높았습니다. <span style="background-color: #fff59d"><strong>post-training average는 8.684, AUC+는 163.5</strong></span>였습니다.

근데 PvZ는 반대였습니다. 초기 점수는 23점인데, 업데이트된 모든 checkpoint가 6점을 받았습니다. 논문은 원인을 단정하지 않습니다. exploration trajectory overfitting, relaxed/strict 설정 mismatch, 잘못된 self-judgment consolidation 가능성을 조심스럽게 말합니다.

![](/images/2026-09-01-s3gym-self-testing-judging-improvement/fig-7-p15.png)

Figure 7. Qwen3-8B parameter training 결과입니다. Trust는 큰 폭으로 오르지만  <span style="background-color: #fff59d"><strong>PvZ는 23에서 6으로 떨어진 뒤 회복하지 못합니다</strong></span>. 같은 training pathway도 환경에 따라 정반대 결과가 납니다.

## 자기판단은 로컬 신호일 뿐입니다

S3Gym이 좋은 지점은 Self-Judging을 따로 뜯어본다는 겁니다. 에이전트가 “이 행동이 좋았다”고 말하는 게 실제 environment reward와 맞는지 본 겁니다.

분석 대상은 7개 모델과 7개 게임, direct-history와 summary-memory 조건을 합친 98 runs, 116,117 transitions입니다.

결과는 부분적입니다. Minesweeper, Nullify, PvZ, Snake, Tetris는 event agreement가 0.82~0.881까지 나옵니다. 근데 이건 zero-reward transition이 많은 영향도 있습니다. calibration을 보면 PvZ는 agreement가 높아도 NMAE가 0.882로 큽니다. 좋아 보이는 행동인지 정도는 알아도, 가치 크기를 잘 맞춘다는 뜻은 아닙니다.

더 중요한 건 다음 성능과의 연결입니다. 판단 agreement와 다음 strict score gain의 상관은 전체에서 <span style="background-color: #fff59d"><strong>ρ(A,g) = -0.010</strong></span>입니다. calibration error 반대값과 gain의 상관도 <span style="background-color: #fff59d"><strong>ρ(-E,g) = -0.018</strong></span>입니다. 거의 신호가 없습니다.

그래서 이 논문의 메시지는 명확합니다. local reward를 맞히는 능력만으로는 자기개선이 안 됩니다. <span style="background-color: #fff59d"><strong>agent가 feedback을 state abstraction, decision rule, exploration strategy로 바꾸는 단계</strong></span>가 따로 필요합니다.

## 적용하면 어디에 쓸 수 있나

이 논문은 블로그 자동화나 코딩 에이전트에도 바로 닿습니다. “지난 실행에서 배웠다”는 말을 하려면 최소한 3개를 나눠봐야 합니다.

- 테스트를 잘했는가: 실패가 드러나는 case를 스스로 만들었는가
- 판단을 잘했는가: 로그의 성공/실패 원인을 환경 신호와 맞게 봤는가
- 반영을 잘했는가: 다음 실행에서 쓸 수 있는 규칙, memory, skill, code change로 바꿨는가

Transcript를 길게 붙이는 것은 History ICL입니다. 요약 memory를 남기는 것은 Summary Memory입니다. 스킬이나 하네스를 수정하는 것은 더 오래 남는 update입니다. 각 방식은 장점이 다르고, 과제 구조에 따라 실패 방식도 다릅니다.

특히 agent harness 쪽에서는 “무조건 요약해서 memory에 넣자”가 답이 아닙니다. <span style="background-color: #fff59d"><strong>상태 디테일이 중요한 과제에서는 summary가 필요한 정보를 버릴 수 있습니다</strong></span>. 반대로 규칙이 잘 압축되는 과제에서는 raw history보다 summary가 낫습니다.

## 한계

S3Gym은 text-based game benchmark입니다. 실제 업무 시스템의 API, 권한, 비동기 상태, 사람 피드백, 장기 운영 비용을 그대로 담지는 않습니다.

또 parameter training 결과는 Qwen3-8B 중심의 별도 실험입니다. context-level 방식과 완전히 같은 조건의 matched comparison으로 읽으면 안 됩니다.

논문도 원인을 조심스럽게 말합니다. PvZ의 negative transfer가 왜 생겼는지는 가능성을 제시할 뿐, 확정된 인과로 말하지 않습니다.

그래도 장점은 큽니다. 자기개선을 체감 평가에 맡기지 않고, 탐색·판단·반영·held-out 평가로 쪼개서 볼 수 있게 해줍니다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 RL 루프를 직접 다뤄보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

- Q. S3Gym은 무엇을 평가하나요? — LLM 에이전트가 자기테스트와 자기판단으로 얻은 경험을 다음 행동 개선으로 바꾸는지 평가합니다.
- Q. Summary Memory가 항상 좋은가요? — 아닙니다. Nullify, Tetris, Trust처럼 규칙으로 압축되는 과제에서는 좋았고, Minesweeper, PvZ, Snake처럼 상태 디테일이 중요한 과제에서는 direct history가 더 나았습니다.
- Q. 자기판단이 정확하면 자기개선도 되나요? — 논문 결과만 보면 아닙니다. judgment-quality 지표와 다음 성능 향상의 상관이 거의 0에 가까웠습니다.
- Q. Training은 안전한가요? — 강할 수 있지만 불안정합니다. Trust는 개선됐지만 PvZ는 23점에서 6점으로 떨어진 뒤 모든 checkpoint에서 회복하지 못했습니다.

## 원문

Jiajun Shi et al. “S3Gym: Can LLMs Turn Self-Testing and Self-Judging into Self-Improvement?” arXiv:2608.31100v1 (2026). https://arxiv.org/abs/2608.31100

Project page: https://self-developing-agents.github.io/
