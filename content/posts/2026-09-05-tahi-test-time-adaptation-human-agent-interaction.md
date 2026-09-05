---
title: "TAHI — 사람-AI 상호작용으로 에이전트를 개인 전문가 수준으로 적응시키기 (arXiv 2609.04141)"
date: 2026-09-05
draft: false
tags:
  - agent
  - personalization
  - human-in-the-loop
  - test-time-adaptation
  - evaluation
description: "사람이 에이전트 결과를 고치는 반복 상호작용 데이터만으로 에이전트를 개인별 기준에 맞춰 적응시키는 TAHI 방법을 정리했습니다. 30명 대상 작업 600건, 성공률 4.5-20.9%p 개선과 루브릭이 16.0-22.3%p 더 많은 실패를 잡아내는 결과까지."
---

## 결론 먼저

TAHI(Test-time adaptation through Human-agent Interaction, arXiv 2609.04141)는 <span style="background-color: #fff59d"><strong>사람이 에이전트 산출물을 고치는 세션 간 상호작용 기록을 에이전트 컨텍스트와 가중치에 넣어, 개인 전문가의 기준으로 에이전트를 적응</strong></span>시키는 방법입니다. 사전에 다 적을 수 없는 개인별 평가 기준을 상호작션 중에 러브릭(rubric) 모듈로 굳혀서 재사용한다는 게 핵심이에요.

- 글쓰기·데이터 시각화 두 도메인, 30명, 총 600 태스크
- <span style="background-color: #fff59d"><strong>수십 개 태스크만으로 솔로 성공률 4.5-20.9%p 개선</strong></span>
- 진화하는 루브릭이 <span style="background-color: #fff59d"><strong>LLM 단독·인간 단독 루브릭보다 실패를 16.0-22.3%p 더 많이 포착</strong></span>
- 개인화된 에이전트가 다른 사용자에게도 <span style="background-color: #fff59d"><strong>최대 8.8%p 일반화 개선</strong></span>

기준일: 2026-09-05 기준, arXiv v1(2026-09-03 제출) 리뷰입니다.

## 핵심 요약 표

| 항목 | 값 |
|---|---|
| 논문 | TAHI: Efficient Test-Time Adaptation through Human-AI Interaction (arXiv 2609.04141) |
| 문제 | 인구 수준 데이터로 학습된 에이전트가 개인 전문가 기준을 못 맞춤 |
| 방법 | 세션 간 상호작용 데이터를 컨텍스트+가중치로 주입, 진화형 루브릭 모듈 |
| 규모 | 30명, 2개 도메인(글쓰기/시각화), 600 태스크 |
| 결과 | 솔로 성공률 +4.5~20.9%p (수십 태스크 내) |
| 루브릭 효과 | LM/인간 단독 대비 실패 포착 +16.0~22.3%p |
| 일반화 | 타 사용자 성공률 최대 +8.8%p |
| 링크 | https://arxiv.org/abs/2609.04141 |

## 왜 개인화가 어려운가

에이전트는 인구 수준 데이터로 넓은 능력을 갖춥니다. 근데 현실의 열린 과제는 성공 기준이 사용자마다 다르고, 그 기준조차 문서로 다 정리돼 있지 않아요. 논문의 표현을 빌리면, 개인 전문성은 평균에서 <span style="background-color: #fff59d"><strong>얼마나 벗어나고 끌어올리는지(elevation and departure from the average)</strong></span>에 드러납니다.

그래서 프롬프트에 "이렇게 해줘"를 다 못 박는 상황이 흔합니다. 기준은 반복해서 적용되는데 사용자 본인도 앞서 다 못 적는 거죠.

## TAHI가 보는 신호: 세션 간 상호작용

핵심 관찰은 이겁니다.

- 사용자는 에이전트 결과를 보고 그때그때 고친다(거부, 수정, 코멘트).
- 이 고침 기록이 사용자의 암묵적 평가 기준을 드러낸다.
- 이 기록이 세션을 넘어 반복되는 패턴을 이룬다.

TAHI는 cross-session interaction 데이터를 <span style="background-color: #fff59d"><strong>부족하게 활용되던 적응 재료로 쓴다</strong></span>는 점이 핵심이에요. 계속 쌓이는 고침 이력 자체를 학습 소스로 보는 관점이구요.

## 동작 구조

![사람-에이전트 상호작용 인터페이스 예시](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-1-p2.png)
*Figure 1. 인터페이스를 통한 사람-에이전트 상호작용 과정 (원문 Fig. 1)*

![테스트 타임 에이전트 적응 패러다임](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-2-p7.png)
*Figure 2. 테스트 타임 적응 패러다임과 예시 (원문 Fig. 2)*

구성은 크게 두 갈래예요.

1. 컨텍스트 적응: 상호작용에서 나온 피드백을 다음 태스크의 컨텍스트에 반영.
2. 가중치 적응: 같은 신호로 파라미터를 갱신.
3. 진화형 루브릭: 각 사용자의 평가 기준을 태스크를 거치며 갱신되는 모듈로 굳힘.

여기서 루브릭이 재미있는 부분입니다. 적응 보조를 넘어서 <span style="background-color: #fff59d"><strong>확장 가능한 주석 도구로 쓸 수 있어서, 평가 루브릭을 대량 생산</strong></span>할 수 있어요.

## 수치로 보는 결과

![작업 유형별 인간 액션 분포](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-3-p10.png)
*Figure 3. 상호작용 중 관측된 인간 액션 분포 (원문 Fig. 3)*

![에이전트 적응 방식 비교](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/table-2-p10.png)
*Table 2. 에이전트 적응 방식 비교 (원문 Table 2)*

- 개선 폭: 솔로 태스크 성공률이 수십 개 태스크만에 4.5-20.9%p 오릅니다. 도메인과 개인 차이는 있지만, <span style="background-color: #fff59d"><strong>"수백 건"이 아니라 "수십 건"이라는 게 실용적 포인트</strong></span>예요.
- 루브릭 품질: 진화형 루브릭이 LM 단독·인간 단독보다 <span style="background-color: #fff59d"><strong>16.0-22.3%p 더 많은 실패 사례를 잡아냅니다</strong></span>.
- 일반화: 개인 A에게 맞춘 에이전트가 사용자 B에게도 최대 8.8%p 개선. <span style="background-color: #fff59d"><strong>개인별 기준이 완전히 따로 노는 건 아니다</strong></span>는 뜻이죠.

## 전문성이 흡수되는 지점

![컨텍스트와 가중치로 흡수되는 전문성](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-5-p12.png)
*Figure 5. 적응 중 컨텍스트/가중치로 흡수되는 전문성 (원문 Fig. 5)*

논문은 전문성이 어디에 쌓이는지도 분해해서 봅니다. 컨텍스트로 들어가는 부분과 가중치로 들어가는 부분이 다르다는 얘기고, 이건 "프롬프트에 다 넣으면 되는 거 아냐?"라는 질문에 대한 실증적 답에 가까워요.

## 평가 도구로서의 루브릭

![LLM 단독 루브릭의 실패](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-6-p13.png)
*Figure 6. LLM 단독 루브릭이 저품질 해법을 구분하지 못하는 사례 (원문 Fig. 6)*

![공유 루브릭 vs 개인 루브릭](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-7-p14.png)
*Figure 7. 공유 루브릭과 개인 루브릭 비교 (원문 Fig. 7)*

![진화형 루브릭의 측정 효과](/images/2026-09-05-tahi-test-time-adaptation-human-agent-interaction/fig-8-p28.png)
*Figure 8. 진화형 루브릭이 태스크 성공 측정에서 보이는 효과 (원문 Fig. 8)*

LLM-only 루브릭은 저품질 에이전트 산출물을 구분하지 못하는 경우가 있어요. 사람 고침 기록을 흡수한 진화형 루브릭은 그 간극을 메꿉니다. 평가 자동화에 관심 있는 분이라면 이 부분만 읽어도 됩니다.

## 내 해석: 어디에 쓸 수 있나

원문 근거와 제 해석을 나눠서 정리했습니다.

- 원문 주장: cross-session 상호작용 데이터로 개인 적응과 평가 루브릭 생성이 가능하다.
- 내 해석 1: 지금 흔한 "AI 결과물에 대해 써주는 피드백"이 사실 적응용 학습 데이터라는 관점. 피드백 UI를 데이터 수집 설계로 보면 제품 기획이 바뀝니다.
- 내 해석 2: 개인화와 일반화가 어느 정도 같이 간다는 결과(+8.8%p)는, 사용자별 루브릭을 모아서 공유 평가기준을 만드는 방향도 열려있다는 뜻이에요.
- 주의점: <span style="background-color: #fff59d"><strong>글쓰기·시각화 두 도메인, 30명 기준</strong></span>입니다. 코딩처럼 검증 가능한 도메인에서는 기준 자체가 다르게 굴러갈 수 있어요.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### TAHI는 파인튜닝인가요?
컨텍스트 적응과 가중치 적응을 함께 씁니다. 테스트 타임에 사람 상호작용 신호로 이둘을 갱신하는 구조예요.

### 얼마나 빨리 효과가 나타나나요?
수십 개 태스크 수준에서 솔로 성공률이 4.5-20.9%p 개선됐다고 보고합니다(2026-09-05 기준, 원문 v1).

### 루브릭은 사람이 직접 만들어야 하나요?
아니요. 사람-에이전트 상호작용에서 자동으로 진화하며, LM·인간 단독보다 실패 포착이 16.0-22.3%p 높습니다.

### 개인화 에이전트가 다른 사람에게도 도움이 되나요?
네, 최대 8.8%p 성공률 개선이 다른 사용자에게도 일반화됐습니다.

### 어떤 도메인에서 실험했나요?
논문 초록 쓰기(abstract writing)과 데이터 시각화, 30명/600 태스크입니다.

## 출처

- arXiv: https://arxiv.org/abs/2609.04141
- PDF: https://arxiv.org/pdf/2609.04141
- DOI: https://doi.org/10.48550/arXiv.2609.04141
- 제출: 2026-09-03 (v1), 리뷰 기준일 2026-09-05
