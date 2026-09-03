---
title: E-Commerce Bench — 1년 사업을 맡긴 LLM 에이전트 18개, 가장 번 모델의 함정
date: 2026-09-03
tags:
  - agent
  - benchmark
  - long-horizon
  - e-commerce
  - LLM
  - Qwen
draft: false
description: QwenLM의 E-Commerce Bench(arXiv:2608.30730) 정리. 365일 사업 시뮬레이션에서 GPT-5.6 Sol은 14.3배 수익에 사기 회피 16위, 오픈웨이트 1위는 Qwen3.8-Max-Preview 4.2배.
---

## 결론 먼저

QwenLM 팀이 1년짜리 온라인 사업 운영 벤치마크 `E-Commerce Bench`를 공개했습니다. LLM 에이전트에게 초기 자본 ¥100,000을 주고 시뮬레이션된 365일 동안 온라인 스토어 여러 개를 동시에 운영하게 하는 구조입니다. 시장 조사, 공급자 협상, 재고 발주, 가격 전략, 주문 이행, 반품 처리, 현금흐름 관리를 전부 에이전트가 결정합니다.

핵심 결과는 이겁니다. 18개 프론티어 모델을 7개 축으로 평가했는데, <span style="background-color: #fff59d"><strong>어떤 모델도 모든 축에서 1등하지 못했습니다</strong></span>. 가장 많이 번 GPT-5.6 Sol은 <span style="background-color: #fff59d"><strong>¥100,000을 ¥1,431,425로 불렸지만 사기 회피는 18위 중 16위</strong></span>였습니다. 돈을 잘 버는 것과 운영을 안전하게 하는 능력은 따로 움직입니다.

## 벤치 구성 요약

| 항목 | 값 |
|---|---|
| 벤치명 | E-Commerce Bench (arXiv:2608.30730) |
| 운영 기간 | 시뮬레이션 365일 (2026 달력 기준) |
| 초기 자본 | ¥100,000 |
| 도구 수 | 18개 (시장조사·공급자 협상·가격·배송·인출 등) |
| 평가 대상 | 프론티어·오픈웨이트 18개 모델, 각 5회 실행 |
| 평가 축 | 연말 총자산 + 협상·사기회피·현금흐름·운영효율·실행·학습 7개 |
| 재현성 | 수요 모델·협상 커널 결정론적, LLM은 대화 표현만 담당 |
| 코드 | github.com/QwenLM/E-CommerceBench |

환경은 실제 이커머스 플랫폼의 상품·공급자 데이터에서 만들었습니다. 1년 치 프로모션, 자연재해, 공급망 쇼크 캘린더가 수요를 계속 바꿉니다. 재현성을 위해 양쪽 시장을 전부 결정론적으로 고정했습니다. 고객 구매·반품은 고정 수요 모델을 따르고, 공급자 가격·양보·수락 여부는 협상 커널이 정합니다. LLM은 그 결정을 대사로 바꾸는 역할만 합니다.

## 에이전트 루프 구조

![Figure 3: E-Commerce Bench overview](/images/2026-09-03-ecommerce-bench-long-horizon-agents/fig-3-p7.png)

에이전트는 4개 레이어로 동작합니다. 핵심은 에이전트 루프 레이어인데, <span style="background-color: #fff59d"><strong>모델 호출 1번이 도구 호출 배치를 만들고, 1년 치 도구 트래픽 전부를 컨텍스트 윈도우 안에 유지</strong></span>합니다. 옆에 영구 메모리가 붙습니다.

![Figure 4: agent loop](/images/2026-09-03-ecommerce-bench-long-horizon-agents/fig-4-p8.png)

컨텍스트가 넘치면 그룹 단위로 제거됩니다. 그룹은 에디터가 한 단위로 지우는 묶음이라고 합니다.

![Figure 5: eviction](/images/2026-09-03-ecommerce-bench-long-horizon-agents/fig-5-p9.png)

정산은 3계좌 지연결산 구조입니다. 비용은 발주일에 빠져나가고 매출은 나중에 들어옵니다. 그래서 현금흐름 관리를 못 하면 흑자 상태에서도 파산할 수 있습니다.

![Figure 6: deferred settlement](/images/2026-09-03-ecommerce-bench-long-horizon-agents/fig-6-p10.png)

## 결과: 모델별 강점이 다 갈립니다

![Figure 1: end-of-year assets](/images/2026-09-03-ecommerce-bench-long-horizon-agents/fig-1-p2.png)

| 모델 | 연말 총자산 | 특징 |
|---|---|---|
| GPT-5.6 Sol | ¥1,431,425 (약 14.3배) | 수익 1위, 사기 회피 16/18위, 툴 호출당 수익은 Fable5보다 낮음 |
| Claude Opus 4.7 | 중위권 | 협상·사기 회피 1위 |
| Qwen3.8-Max-Preview | ¥416,252 (약 4.2배) | 오픈웨이트 1위, GLM 5.2 대비 +38%, 반복 발주에서 가격을 점점 깎는 학습 |

![Figure 2: seven axes radar](/images/2026-09-03-ecommerce-bench-long-horizon-agents/fig-2-p2.png)

벤더별 최강 모델 6개를 레이더로 그리면 그림이 확 뒤틀립니다. <span style="background-color: #fff59d"><strong>6개 중 전부가 18개 모델 중앙값 아래로 떨어지는 축이 최소 1개씩 있습니다</strong></span>. GPT-5.6 Sol의 사기 회피 16위가 대표 사례입니다.

파산도 나옵니다. <span style="background-color: #fff59d"><strong>4개 모델이 일부 실행에서 파산했고, GPT-5.5는 매출이 정산되기 전인 17일차에 무너진 에피소드가 있습니다</strong></span>. 초기 자본 소진 속도가 수익 능력보다 먼저 문제가 되는 경우입니다.

## 왜 long-horizon 벤치가 따로 필요한가

이 논문의 관점은 이렇습니다. long-horizon 과제는 짧은 과제를 이어 붙인 게 아닙니다. 환경이 계속 바뀌고 의존성이 수천 스텝에 걸쳐 있어서, 모델이 계속 탐색하고 경험에서 배우고 정책을 고쳐야 합니다. GitHub 이슈 해결이나 컴퓨터 조작 같은 에피소딕 벤치와는 평가 대상이 다릅니다.

Qwen3.8-Max-Preview가 보여준 학습 패턴이 근거입니다. 반복 발주에서 구매가를 점점 내려가는 형태로 협상 정책을 고쳐 나갔습니다. 1년 단위 과제에서만 보이는 유형의 적응입니다.

## 내 해석 (원문 근거와 구분)

원문이 말하는 건 사실 관계까지입니다. 여기서부터는 제 해석입니다.

이 벤치의 실무적 가치는 순위표보다 평가 방식에 있습니다. 연말 총자산 하나로 에이전트를 재면 사기 회피가 뒤처진 고수익 모델이 우승합니다. 실서비스에서 그런 모델은 가장 비싼 사고를 칩니다. 7개 축을 같이 보게 만든 설계가 이 벤치의 핵심 기여라고 봅니다.

결정론적 환경도 좋은 선택입니다. 협상 상대까지 LLM으로 만들면 실행마다 결과가 흔들려서 모델 비교가 불가능합니다. 협상 커널로 고정하고 LLM은 표현만 맡긴 설계는 다른 long-horizon 벤치에서도 참고할 만합니다.

한계도 있습니다. 중국 이커머스 하나의 수요 모델을 가정했고, 결정론성이 현실 시장의 불확실성을 줄여 줍니다. 특정 도메인 성적을 일반 에이전트 능력으로 확대 해석하면 안 됩니다.

## 자주 묻는 질문

### E-Commerce Bench에서 가장 많이 번 모델은?
GPT-5.6 Sol입니다. 초기 ¥100,000을 ¥1,431,425(약 14.3배)로 불렸습니다. 사기 회피는 18위 중 16위였습니다.

### 오픈웨이트 모델 중 1위는?
Qwen3.8-Max-Preview입니다. ¥416,252(약 4.2배)로, GLM 5.2 (high)보다 38% 높습니다.

### 벤치마크 환경은 재현 가능한가요?
네. 고객 구매·반품은 고정 수요 모델, 공급자 협상은 결정론적 커널이 결정하고 LLM은 대사 표현만 담당합니다. 코드는 github.com/QwenLM/E-CommerceBench에 공개되어 있습니다.

### 에이전트가 파산하기도 하나요?
네. 18개 모델 중 4개가 일부 실행에서 파산했습니다. GPT-5.5는 매출 정산 전인 17일차에 자본이 무너진 에피소드가 있었습니다.

### 어느 날짜 기준인가요?
2026-09-03 기준, arXiv:2608.30730v1(2026-08-31 제출) 내용입니다.

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)』

출처: arXiv:2608.30730 — E-Commerce Bench: Evaluating LLM Agents on Long-Horizon Autonomous Business Operation (Wei Fan 외, QwenLM). https://arxiv.org/abs/2608.30730
