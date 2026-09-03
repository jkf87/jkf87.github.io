---
title: 웹 에이전트 월드 모델, 다음 상태를 구별하도록 학습하면 성공률 28%까지 오릅니다
date: 2026-09-03
tags:
  - web-agent
  - world-model
  - PRM
  - benchmark
  - WebArena
draft: false
description: 웹 에이전트 월드 모델을 다음 상태 재현 대신 행동 결과 구별 목표로 학습한 predicted-state matching 논문을 정리했습니다. WebArena-Lite 성공률 13.94%에서 28.48%로 오른 실험까지 함께 봅니다.
---

## 결론 먼저

Berkeley와 MIT-IBM 팀이 웹 에이전트용 월드 모델의 학습 목표를 바꿨습니다. 기존 방식은 다음 상태를 HTML·AXTree·요약문 같은 고정 형식으로 재생하는 supervised next-state prediction이었어요. 이 논문은 대신, <span style="background-color: #fff59d"><strong>예측 표현이 같은 분기점의 다른 행동 결과와 구별되도록 훈련하는 predicted-state matching을 제안했구요</strong></span>. WebArena-Lite에서 GPT-4o 정책 기준 <span style="background-color: #fff59d"><strong>태스크 성공률이 13.94%에서 28.48%로 올랐습니다</strong></span>.

## 핵심 요약 표

| 항목 | 값 |
|---|---|
| 논문 | Discriminative World Models for Web Agents (arXiv:2609.02885) |
| 소속 | UC Berkeley, MIT-IBM Watson AI Lab, Cal Poly, Xero |
| 제안 | predicted-state matching 학습 목표 |
| 모델 | Qwen3-8B 파인튜닝, 판정 Qwen3-32B |
| 데이터 | Go-Browse 기반 7,730개 분기 결정점, 30,920쌍 |
| WebArena-Lite 성공률 | ReAct 13.94% / Bo5 21.82% / Bo5+state matching 28.48% |
| 기준일 | 2026-09-02 arXiv v1 |

## 배경과 문제

웹 에이전트는 대부분 현재 관찰과 이력으로 다음 행동 하나를 바로 고르는 반응형 구조입니다. 근데 최근에는 후보 행동을 여러 개 뽑고, 월드 모델이 각 행동의 다음 상태를 예측하고, PRM(프로세스 보상 모델)이 순위를 매겨 고르는 test-time action selection 방식이 늘고 있어요.

종래 월드 모델은 supervised next-state prediction으로 학습합니다. 다음 상태를 미리 정해둔 형식의 문자열로 재현하도록 감독하는 거죠.

논문은 <span style="background-color: #fff59d"><strong>이 목표가 하류 순위 결정과 어긋난다고 지적합니다</strong></span>. 두 가지 사례가 그 증거예요.

- 텍스트 요약 방식(WebDreamer): 압축된 요약이 구별에 필요한 변경을 빠뜨릴 수 있음
- 전체 구조 방식(WebWorld): <span style="background-color: #fff59d"><strong>AXTree 전체를 뱉으면 바뀐 부분이 그대로 있는 부분에 묻힘</strong></span>

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>행동 선택에 쓰이는 예측 상태는 경쟁 행동 결과와 잘 구별될 때 가치가 있습니다</strong></span>.

## 방법 구조

![](/images/2026-09-03-dwm-discriminative-world-models-web-agents/fig-3-p5.png)

출처: 논문 Figure 3. Go-Browse 선형 궤적을 상태-행동 그래프로 합쳐 분기 결정점을 만드는 과정.

현재 상태와 질의 행동이 주어지면 월드 모델이 다음 상태 표현을 생성합니다. 그 표현을 고정 판정자(judge)에게 주고, 진짜 결과 상태와 다른 행동의 결과 상태 중 무엇에 대응하는지 맞히게 하게 하는 방식이 구요. <span style="background-color: #fff59d"><strong>문자열 일치 대신 구별력 기준으로 학습하고 평가합니다</strong></span>.

데이터 구축은 3단계로 정리됩니다.

- Go-Browse 궤적 2,839개에서 같은 브라우저 상태를 만나는 궤적 병합
- 상태-행동 그래프로 변환 후, 같은 상태에서 나가는 여러 행동과 결과를 분기 결정점으로
- <span style="background-color: #fff59d"><strong>최종 7,730개 결정점, 30,920쌍의 매칭 예제 확보</strong></span>

## 실험 결과 리딩

세 단계 평가를 돌렸습니다.

홀드아웃 매칭 벤치마크에서 제안 모델이 GPT-4o, Qwen 계열, WebDreamer-7B, WebWorld-8B, <span style="background-color: #fff59d"><strong>같은 데이터로 학습한 supervised baseline을 모두 이겼습니다</strong></span>. <span style="background-color: #fff59d"><strong>판정자를 GPT-4o와 Llama-3.1-70B로 바꿔도 순위가 유지됐어요</strong></span>.

WebPRMBench 행동 순위 결정이 그 다음 수준입니다. 학습된 보상 모델이든 frozen ranker든, 예측 상태를 붙이면 성적이 오르고 <span style="background-color: #fff59d"><strong>WebWorld-8B 상태보다 제안 모델 상태가 일관되게 좋았습니다</strong></span>.

끝으로 WebArena-Lite 엔드투엔드에서 GPT-4o 정책으로 ReAct 13.94%, Best-of-5 21.82%, 여기에 <span style="background-color: #fff59d"><strong>state matching 예측을 얹으면 28.48%까지 올라갑니다</strong></span>.

![](/images/2026-09-03-dwm-discriminative-world-models-web-agents/fig-1-p2.png)

출처: 논문 Figure 1. 같은 결정점에서 WebDreamer는 다른 행동의 결과를 서술하고, WebWorld는 바뀌지 않은 페이지 구조까지 길게 반복합니다. <span style="background-color: #fff59d"><strong>제안 모델은 해당 행동이 만든 상태 변경을 특정해내요</strong></span>.

## 내 해석과 한계

원문 근거와 내 해석을 구분해서 정리했습니다.

- <span style="background-color: #fff59d"><strong>수치 비교는 전부 WebArena 계열 환경, GPT-4o 정책 기준입니다</strong></span>. 다른 환경·정책에서의 검증은 아직 열린 질문이에요. 논문 한계 절도 스스로 인정합니다.
- <span style="background-color: #fff59d"><strong>매칭 평가가 LLM 판정자에 의존합니다</strong></span>. 판정자를 3종 바꿔 확인하긴 했지만 모델 기반 프록시라는 한계는 남습니다.
- <span style="background-color: #fff59d"><strong>학습 목표 하나를 다운스트림 과제에 맞춰 바꿨더니 같은 데이터로도 성적이 올랐다는 점</strong></span>이 이 논문의 가장 깔끔한 기여입니다. 웹 에이전트 월드 모델을 만드는 분이라면 바로 참고할 만해요.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 기존 supervised 방식과 다른 점은 무엇인가요?

고정 형식 문자열 재현을 감독하는 대신, 생성 표현이 같은 결정점의 대안 행동 결과와 구별되는지를 기준으로 학습·평가합니다. 출력 형식에 제약을 두지 않는 목표예요.

### WebArena-Lite 성공률은 얼마나 변했나요?

GPT-4o 정책 기준 ReAct 13.94%, Best-of-5 21.82%, Bo5 + state matching 28.48%입니다. 기준일은 2026-09-02 arXiv v1이에요.

### 데이터는 어떻게 만들었나요?

WebArena의 Go-Browse 궤적 2,839개에서 같은 상태를 재방문하는 궤적을 병합해 상태-행동 그래프를 만들고, 분기 결정점 7,730개, 짝 예제 30,920개를 추출했습니다.

### 어떤 모델을 사용했나요?

<span style="background-color: #fff59d"><strong>월드 모델은 Qwen3-8B를 파인튜닝했고, 매칭 판정자는 학습에 Qwen3-32B</strong></span>, 검증에 GPT-4o와 Llama-3.1-70B-Instruct를 썼습니다.

### 소스는 어디서 확인하나요?

논문: https://arxiv.org/abs/2609.02885, 프로젝트 페이지: https://dhruvpendharkar.github.io/dwm/
