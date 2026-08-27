---
title: "인터랙션 텍스 — 멀티에이전트 LLM에서 소통이 다양성을 지우는 현상"
date: 2026-08-27
draft: false
description: "ICML 2026 워크숍 논문(2608.23541) 리뷰. 멀티에이전트 LLM에서 에이전트끼리 전체 해답을 주고받으면 한 라운드 만에 해답이 수렴하고 모델 다양성이 사라진다는 인터랙션 텍스(interaction tax) 분석. 독립 생성 후 선택이 안전한 기본값이라는 결과를 정리했습니다."
tags:
  - multi-agent
  - llm
  - paper-review
---

## 결론 먼저

"에이전트를 여럿 두면 서로 봐주니까 더 똑똑해지지 않을까?" 이런 기대로 debate나 critique 루프를 달아본 적 있다면, 이 논문이 그 기대의 반쪽을 잘라냅니다.

2026-08-24 공개 arXiv v1 기준으로, 시카고 대학교 팀이 11개 최적화 태스크에서 확인한 결과는 이겁니다. 에이전트끼리 <span style="background-color: #fff59d"><strong>전체 해답을 주고받는 순간, 제안들은 한 라운드 만에 서로 비슷해집니다</strong></span>. 다양한 모델을 섞은 이유가 사라지는 거죠. 논문은 이 손실에 <span style="background-color: #fff59d"><strong>인터랙션 텍스</strong></span>라는 이름을 붙였습니다.

- 논문: [The Interaction Tax: When Communication Erases Diversity in Multi-Agent Teams](https://arxiv.org/abs/2608.23541)
- 어디서: ICML 2026 워크숍 (PMLR 306)
- 한 줄 결론: <span style="background-color: #fff59d"><strong>전체 해답 교환은 약한 기본값</strong></span>. 독립 생성 + 선택이 안전하다.

## 핵심 요약 표

| 항목 | 내용 |
| --- | --- |
| 논문 | arXiv:2608.23541 |
| 저자 | Ann, Liu, Tan (University of Chicago) |
| 모델 | Claude Sonnet 4 / GPT-4o / Gemini 2.5 Flash |
| 태스크 | 검증기 점수 최적화 11개 |
| 다양성 계수 | +0.188 (p<0.001, N=120) |
| 다양 모델 Debate MIG | −0.078 |
| 처방 | 독립 생성 후 선택 |

## 무엇을 했나

실험 설계는 단순합니다. 결정론적 검증기가 점수를 주는 최적화 태스크 11개를 준비하고, <span style="background-color: #fff59d"><strong>단일 에이전트 4종과 멀티에이전트 6종을 같은 예산으로 돌립니다</strong></span>. 탐색 중엔 보이는 개발 평가기 점수를 쓰고, 최종은 더 엄격한 은닉 평가기로 평가합니다. 점수는 Q∈[0,1]로 정규화했고, 태스크당 5 시드입니다.

![](/images/2026-08-27-interaction-tax-multi-agent-diversity/fig-1-p2.png)

Figure 1에서 눈여겨볼 장면이 나옵니다. Claude, GPT-4o, Gemini는 각자 구조적으로 다른 해답을 찾아갑니다. 그러다 서로의 해답을 통째로 교환하기 시작하면 제안이 뭉개지면서 한 점으로 모입니다.

## 숫자로 보는 인터랙션 텍스

먼저 좋은 소식. 모델을 섞는 건 실제로 효과가 있습니다. 세 모델 각각은 최소 한 태스크에서 최고점을 냈고, <span style="background-color: #fff59d"><strong>같은 모델 팀은 최소 한 태스크에서 Q=0을 맞습니다</strong></span>. 섞은 팀은 어디서도 0점이 없었고, 다양성 계수는 <span style="background-color: #fff59d"><strong>+0.188 (CI [+0.073, +0.299], p<0.001)</strong></span>였습니다.

나쁜 소식은 그 다음입니다. 같은 모델끼리는 상호작용이 이득이었는데, <span style="background-color: #fff59d"><strong>모델을 섞는 순간 셋 다 마이너스로 뒤집힙니다</strong></span>.

| 구성 | 같은 모델 MIG | 다양 모델 MIG |
| --- | --- | --- |
| Chain | 양수 | −0.024 |
| MAgICoRe | 양수 | −0.035 |
| Debate | 양수 | −0.078 |
| MoA | +0.012 | +0.016 |

![](/images/2026-08-27-interaction-tax-multi-agent-diversity/fig-2-p3.png)

유일하게 살아남은 MoA의 비결은 단순합니다. <span style="background-color: #fff59d"><strong>제안자들이 합성 전까지 서로의 출력을 아예 안 읽거든요</strong></span>. 파이프라인에서 "서로 보기" 단계 하나를 뺀 것만으로 세이프했습니다.

## 수렴은 한 번의 교환으로 끝난다

이 붕괴가 특히 무서운 이유는 속도입니다. 상호작용 전 에이전트 간 평균 해답 거리는 0.315였는데, <span style="background-color: #fff59d"><strong>전체 해답 교환 한 번 만에 0.229로 떨어집니다</strong></span>. Erdős 태스크에서 다양 모델 Debate는 2라운드까지 좋은 점수를 유지하다가, 3라운드에서 서로의 해답을 읽자마자 퇴행합니다.

원인도 찾았습니다. 합성 단계가 제안을 섞지 않아요. <span style="background-color: #fff59d"><strong>7개 태스크 중 5개에서 합성은 최고 제안자의 출력을 80% 이상 그대로 복사했습니다</strong></span>. Erdős에서 GPT-4o는 <span style="background-color: #fff59d"><strong>100개 시드 전부에서 똑같은 자명한 상수(Q=0.710)를 냈고</strong></span>, 뭘 섞어도 그 점으로 수렴합니다.

## 비판 루프의 희망과 함정

비판(critique)이 항상 나쁘진 않습니다. Knapsack-50처럼 결함이 "용량 초과"라는 명확한 형태면, 비평가가 과적 항목을 빼라는 직접 수리를 제안할 수 있죠. 여기서 <span style="background-color: #fff59d"><strong>다양 모델 Debate는 실현가능성 10/10, 같은 모델은 2/10</strong></span>이었습니다.

근데 3AP-Free-100은 반대입니다. 어떤 등차수열 트리플이 규칙을 위반했는지 찾는 것 자체가 어려워서, <span style="background-color: #fff59d"><strong>다양 모델 Debate는 0/10까지 떨어집니다</strong></span>. 점수 피드백 태스크에서는 <span style="background-color: #fff59d"><strong>첫 비판 라운드가 17/30(57%)에서 해답을 악화</strong></span>시켰습니다. 비판은 결함이 구체적이고 고칠 수 있을 때만 쓰세요.

![](/images/2026-08-27-interaction-tax-multi-agent-diversity/table-1-p3.png)

Table 1. 점수가 갈린 여섯 태스크의 Best-of-NN Q-점수. 모델 계열마다 이기는 태스크가 다르다. (원문 Table 1)

## 한계와 다음 과제

- <span style="background-color: #fff59d"><strong>Erdős를 빼면 다양성 계수가 +0.014로 줄고 CI가 0을 가로짭니다</strong></span>. 커버리지 효과는 태스크 의존적입니다.
- 시드가 5개(요인 실험 10개), 실현가능성 분석은 태스크 2개에 의존합니다.
- 검증기 점수 최적화 태스크만 썼으므로 글쓰기·계획 설정으로의 일반화는 미검증입니다.
- 어떤 저대역 공유(점수, 방법 설명, 실패 원인)가 최선인지는 후속 과제입니다.

## 실무 처방

1. 다양한 모델을 쓸 거면 제안은 독립으로.
2. 합성은 재조합이 아니라 선택이라고 이해하기.
3. 비판 루프는 결함이 국소적일 때만.
4. 공유할 거면 전체 해답 대신 점수·실패 원인부터.

<span style="background-color: #fff59d"><strong>멀티에이전트 성능은 에이전트 수보다 무엇을 언제 공유하느냐에 달려 있다</strong></span>는 결론입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 인터랙션 텍스란 무엇인가요?

에이전트가 서로의 전체 해답을 읽으면 제안이 한 라운드 만에 수렴해 모델 다양성이 사라지는 손실입니다. arXiv:2608.23541에서 이름 붙였고 Chain·MAgICoRe·Debate에서 다양 모델 팀 기준 음의 MIG로 측정됐습니다.

### MoA는 왜 안전한가요?

제안자들이 합성 전까지 서로의 출력을 읽지 않아 전체 해답 교환 단계 자체가 없기 때문입니다. MIG가 같은 모델 +0.012, 다양 모델 +0.016으로 유지됩니다.

### 비판 루프는 언제 도움이 되나요?

결함이 구체적이고 국소적일 때입니다. Knapsack(용량 제약)에서는 다양 모델 비판이 실현가능성을 2/10에서 10/10으로 올렸고, 결함 위치를 찾기 어려운 3AP-Free에서는 0/10으로 악화했습니다.

### 실험 설정은 어떻게 됐나요?

Claude Sonnet 4, GPT-4o, Gemini 2.5 Flash로 검증기 점수 최적화 태스크 11개를 동일 예산으로 돌렸습니다. 최종 평가는 은닉 평가기로 했고 점수는 Q∈[0,1]로 정규화했습니다.
