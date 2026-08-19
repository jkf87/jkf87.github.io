---
title: "자기개선 에이전트는 왜 흔들리나 — 분산 증가 71%, 셔플만으로 -4.5%"
date: 2026-08-19T16:05:00+09:00
draft: false
tags:
  - agent
  - self-improvement
  - memory
  - evaluation
  - reliability
  - paper-review
---

## 결론 먼저

메모리 기반 자기개선(self-improving) 에이전트가 실제로는 상당히 취약하다는 재평가 결과가 나왔습니다. Salesforce AI Research가 AWM(Agent Workflow Memory)과 ReasoningBank(RBank)를 다시 돌려보니 두 가지 문제가 드러났습니다.

- 실행 간 분산(variance)이 <span style="background-color: #fff59d"><strong>24개 케이스 중 17개(약 71%)에서 오히려 커졌고</strong></span>, 같은 실험의 최고/최저 실행 격차는 <span style="background-color: #fff59d"><strong>최대 10%포인트</strong></span>까지 벌어졌습니다.
- 태스크 순서만 섞어도 성능이 <span style="background-color: #fff59d"><strong>+1.5% 개선에서 -4.5% 하락으로 뒤집혔습니다</strong></span>.

논문은 "On the Fragility of Self-Improving Agents: Variance, Task Order, and Underspecification"(arXiv 2608.18066, 2026-08-18)입니다. 코드와 데이터도 공개했습니다.

- 논문: https://arxiv.org/abs/2608.18066
- 코드: https://github.com/SalesforceAIResearch/self-improve-fragility

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>지금까지 보고된 "에이전트가 경험을 쌓으며 스스로 좋아진다"는 결과 상당수가, 단일 실행 + 정해진 태스크 순서라는 은밀한 전제 위에 서 있었다는 것입니다.</strong></span>

## 무엇을 재평가했나

대상은 웹 브라우징 에이전트입니다. 두 가지 대표적인 메모리 기반 자기개선 방법을 검증했습니다.

| 방법 | 메모리 형태 | 특징 |
|---|---|---|
| AWM (Agent Workflow Memory) | 성공 궤적에서 재사용 가능한 워크플로 요약 | 전체 워크플로를 컨텍스트에 포함 |
| RBank (ReasoningBank) | 성공/실패 궤적 모두에서 추론 트레이스와 인사이트 | 검색기로 관련 메모리 선택 |

벤치마크는 세 개입니다.

- WebArena: 812 태스크 (쇼핑, GitLab, Reddit, 지도 등 6개 도메인)
- VisualWebArena: 910 태스크
- SCUBA: 267 태스크 (Salesforce 엔터프라이즈 CRM)

백본 모델은 GPT-5-mini입니다. 여기가 중요한데, <span style="background-color: #fff59d"><strong>메모리 없는 기본 에이전트가 이미 WebArena 55.3%, VisualWebArena 54.9%를 찍습니다</strong></span>. VisualWebArena 리더보드 최고 성적(54.0%, 2026-05 기준)과 비슷한 수준입니다. 즉 예전 논문들이 썼던 약한 모델 기준의 이득이 지금은 남아있지 않은 상태에서 시작한 겁니다.

![Figure 1: 메모리 기반 자기개선 방법 개요](/images/2026-08-19-self-improve-fragility/fig-1-p3.png)

Figure 1: (a) 메모리 기반 자기개선 방법의 개요. 태스크마다 종료 후 메모리를 생성해 뱅크에 저장하고, 이후 태스크에서 검색해 사용합니다. (b)(c) AWM과 RBank의 예시 메모리.

## 문제 1: 자기개선 루프가 분산을 키운다

웹 에이전트 평가는 원래 노이즈가 큽니다. 메모리 없는 기본 에이전트도 3번 반복 실행하면 <span style="background-color: #fff59d"><strong>도메인별 최고/최저 격차가 WebArena GitLab에서 4.4%, SCUBA에서는 6.7%까지 벌어집니다</strong></span>. 단일 실행 결과만 보고하는 관행이 얼마나 위험한지 보여주는 수치입니다.

여기에 자기개선 루프를 얹으면 분산이 더 커집니다.

- 24개 케이스 중 17개(71%)에서 실행 간 분산 증가
- 11개 케이스에서 상대적 증가율 50% 초과
- <span style="background-color: #fff59d"><strong>최악/최고 실행 격차: GitLab 4.4% → RBank 적용 시 7.8%</strong></span>, Map 도메인은 8.2%
- 표준편차 최대 3.9%

![Table 1: 3회 실행 분산 지표](/images/2026-08-19-self-improve-fragility/table-1-p5.png)

Table 1: 3회 실행에 걸친 분산 관련 지표. 자기개선 방법 적용 시 24개 중 17개 케이스에서 분산이 증가했습니다.

이유는 구조적입니다. 메모리 생성이 이전 태스크 결과에 조건화되어 있고 LLM 샘플링도 확률적이라, 초반의 작은 무작위성이 누적되면서 실행마다 완전히 다른 메모리 상태로 수렴합니다.

RBank가 기본 대비 평균 +1.5% 개선을 보이긴 하는데, 3회 실행 기준 <span style="background-color: #fff59d"><strong>p-value가 0.23</strong></span>입니다. 통계적으로 유의하다고 말하기 어렵습니다.

## 문제 2: 태스크 순서를 섞으면 성능이 뒤집힌다

기존 연구들은 기본 순서(작은 태스크 ID부터)를 사용했습니다. 근데 이 순서에 함정이 있습니다.

![Figure 2: 기본 순서에 숨어있는 암묵적 커리큘럼](/images/2026-08-19-self-improve-fragility/fig-2-p6.png)

Figure 2: 기본 순서에서의 통과율 이동평균(윈도우 30). 초반 통과율이 75% 수준으로 시작해 태스크 ID 150을 넘기면 40% 아래로 떨어집니다.

초반 태스크가 쉬운, <span style="background-color: #fff59d"><strong>사실상 easy-to-hard 커리큘럼이 순서에 박혀 있는 겁니다</strong></span>. 벤치마크 제작 과정에서 어노테이터가 쉬운 태스크부터 만들었던 부작용으로 보입니다. 자기개선 방법은 쉬운 태스크에서 "성공 경험"을 먼저 쌓기 때문에 이 순서가 은밀한 성공 전제로 작동합니다.

태스크 순서를 무작위로 섞으면(Shuffle-1, Shuffle-2) 결과가 달라집니다.

| 설정 | WebArena 성능 |
|---|---|
| 기본 순서 | 54.8% |
| Shuffle-1 + AWM | 49.1% |
| <span style="background-color: #fff59d"><strong>Shuffle-1 + RBank</strong></span> | 49.8% |

![Figure 3: 태스크 순서별 성능](/images/2026-08-19-self-improve-fragility/fig-3-p6.png)

Figure 3: 기본 순서와 두 개의 셔플 순서에서의 성능. 8개 중 6개 케이스에서 유의미한 하락이 나타났습니다.

메모리가 있으면 최악의 경우에도 메모리 없는 기본 에이전트 수준은 유지할 거라는 상식적 기대가 깨집니다. 실사용 환경에서 사용자 요청이 커리큘럼 순서로 들어오는 일은 없다는 게 이 결과의 무게입니다.

## 원인: 과소명시(underspecification)가 만드는 그럴듯한 쓰레기 메모리

논문의 가장 흥미로운 부분은 실패 원인 분석입니다. 연구진이 에이전트가 실제로 쓴 메모리를 수작업으로 뜯어봤습니다.

**환경 과소명시.** <span style="background-color: #fff59d"><strong>브라우저만 가능한 환경인데 API를 쓰라는 메모리가 계속 생성됐습니다</strong></span>. 실행 불가능한 전략인데 그럴듯해 보이니 메모리 뱅크에 쌓이고, 검색되고, 에이전트를 흔듭니다. "사용자에게 확인 요청" 메모리도 WebArena 3회 실행에서 26번, VisualWebArena에서 22번 등장했습니다. 환경이 사용자 확인을 지원하지 않아서 에이전트는 타임아웃까지 wait를 반복합니다.

![Figure 4: 검색된 메모리의 키워드 등장 횟수](/images/2026-08-19-self-improve-fragility/fig-4-p7.png)

Figure 4: 검색 메모리 내 특정 키워드 언급. (a)(b) API 기반 해결 제안이 도메인 전반에 등장. (c) 지도 태스크에서 실제 사이트 경로 엔진 대신 하버사인 공식을 쓰라는 메모리가 자기증식합니다.

**태스크 과소명시.** WebArena 태스크 118 "교근(이 악무는 문제)이 있는데 완화할 만한 걸 보여줘"를 에이전트가 문자 그대로 해석해 "치과 의사와 상담하세요"라고 답한 케이스가 대표적입니다. 원래 의도는 쇼핑몰에서 마우스가드 상품을 찾는 것이었는데요. 실패를 반성시키자 "의료 조언 전에 환자 정보를 수집하라"는 무관한 메모리가 생성됐습니다.

**메모리의 전염.** 지도 도메인에서 하버사인(Haversine) 공식으로 두 지점 거리를 직접 계산하는 우회 전략이 한 번 메모리에 들어가면, 가끔 정답을 맞추기 때문에 점점 더 자주 검색되고 재사용됩니다. 잘못된 교훈이 스스로 증식하는 구조입니다.

## 완화 시도: 루브릭, 환경 피드백, 프롬프트 수정

원인 가설을 검증하기 위해 메모리 생성 단계에 세 가지 정보를 추가해봤습니다.

| 개선 | 내용 |
|---|---|
| +Rub | 태스크 채점 루브릭과 점수 (must_include, exact_match 등) |
| +Env | 클릭/선택 성공 여부 같은 환경 피드백 |
| +PMod | API·사용자 확인 전략 금지 + 웹 탐색 지식 유도 프롬프트 |

![Figure 5: 과소명시 완화 실험 결과](/images/2026-08-19-self-improve-fragility/fig-5-p8.png)

Figure 5: 세 가지 추가 정보를 개별/전체 적용한 결과. (a) Shuffle-1에서 +All 적용 시 49.8% → 52.7%. (b) 다른 순서에서도 개선 유지.

셋을 모두 적용하니 Shuffle-1에서 RBank가 <span style="background-color: #fff59d"><strong>49.8% → 52.7%로 +2.9% 올라갔고</strong></span>, Shuffle-2에서도 +1.1% 개선됐습니다. 관찰된 성능 하락분의 <span style="background-color: #fff59d"><strong>약 31%를 회복한 셈입니다</strong></span>.

근데 여전히 메모리 없는 기본 에이전트보다 낮습니다. 남은 69%의 갭은 다른 원인이 더 있다는 뜻이고, 논문도 그 부분은 열린 문제로 남겼습니다.

## 내 해석: 이 논문을 실무자가 어떻게 읽을지

원문 근거와 제 해석을 구분해서 정리했습니다.

1. **"단일 실행 벤치마크 리더보드"는 이제 그 신뢰 구간 자체를 의심해야 합니다.** 논문은 3회 실행 + 순서 셔플을 권장합니다. 자체 에이전트 평가를 할 때도 동일하게 적용할 수 있습니다. 1회 실행 결과로 A안이 B안보다 낫다는 결론을 내리면 그 차이는 노이즈일 확률이 높습니다.

2. **메모리는 검증되지 않은 가설입니다.** 논문 원문 표현으로 <span style="background-color: #fff59d"><strong>"unverified hypotheses rather than true lessons learned"</strong></span>. RAG 파이프라인에 넣는 문서도 검수하는데, 에이전트가 스스로 쓰는 메모리는 검수 없이 후속 태스크에 재사용됩니다. 하버사인 사례처럼 <span style="background-color: #fff59d"><strong>가끔 맞는 나쁜 전략이 가장 위험합니다</strong></span>. 메모리 검증/필터링 레이어가 실무에서도 필요합니다.

3. **환경 제약을 명시하라는 교훈은 프롬프트 엔지니어링에 바로 적용됩니다.** "이 환경은 브라우저만 된다", "API 호출은 불가능하다" 같은 제약을 메모리/반성 프롬프트에 박아넣는 것만으로 실패 메모리 생성이 줄어듭니다. 논문의 +PMod에 해당합니다.

4. **쉬운 태스크부터 처리하는 게 나쁜 건 아닙니다.** 문제는 그 커리큘럼이 "자기개선"의 성과로 오인됐다는 것입니다. 실무에서 온보딩 순서를 설계하는 것과, 임의 순서에서도 견디는 것은 별개의 목표고 후자가 배포 조건에 가깝습니다.

## 더 실습해보고 싶은 분들께

에이전트 루프, 자기개선 하네스, 메모리 시스템을 직접 만들어보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 정리

이 논문의 기여는 새 방법론이 아니라 평가의 정밀도를 올린 겁니다. 정리하면:

- 자기개선 루프는 분산을 키운다 (71% 케이스)
- 기본 태스크 순서는 암묵적 커리큘럼이었다
- <span style="background-color: #fff59d"><strong>셔플하면 개선(+1.5%)이 하락(-4.5%)으로 뒤집힌다</strong></span>
- 원인의 상당 부분은 과소명시, 루브릭·환경 피드백·프롬프트 수정으로 31% 회복
- <span style="background-color: #fff59d"><strong>나머지 69%는 미해결</strong></span>, 메모리 검증과 감독 인터페이스가 다음 과제

<span style="background-color: #fff59d"><strong>"스스로 좋아지는 에이전트"를 믿기 전에, 그 결과가 몇 번의 실행인지, 어떤 순서로 태스크가 들어왔는지 먼저 물어보면 됩니다.</strong></span>
