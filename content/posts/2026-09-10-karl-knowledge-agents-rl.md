---
title: "KARL: GLM 4.5 Air에 검색 에이전트 RL을 얹어 GPT 5.2급 그라운디드 추론을 더 싸게 만들기 (arXiv 2603.05218)"
date: 2026-09-10
tags:
  - llm
  - agents
  - rl
  - research
draft: false
description: "GLM 4.5 Air를 베이스로 합성 데이터 + 오프라인 대배치 RL로 학습한 지식 에이전트 KARL을 정리했습니다. KARLBench 6개 영역에서 Claude 4.6, GPT 5.2 대비 비용·지연 파레토 최적이라는 논문의 수치와 한계를 정리했습니다."
---

## 결론 먼저

논문의 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>작은 모델(GLM 4.5 Air)을 에이전트 롤아웃 기반 합성 데이터 + 반복 오프라인 RL로 학습시키면, 클로즈드 최상위 모델과 동등한 그라운디드 추론 품질을 훨씬 낮은 비용·지연으로 얻을 수 있다</strong></span>는 결과입니다.

기준: 2026-09-10 기준 arXiv 2603.05218v1 초안입니다.

| 항목 | 내용 |
|---|---|
| 베이스 모델 | GLM 4.5 Air |
| 학습법 | OAPL — 반복 대배치 오프폴리시 RL, 2회 반복 |
| 학습 태스크 | TREC-Biogen, BrowseComp-Plus(230문항 보정 서브셋) |
| 평가 | KARLBench 6개 검색 영역, 나머지 4종은 학습 안 한 OOD |
| 핵심 결과 | Claude 4.6, GPT 5.2 대비 비용/품질·지연/품질 파레토 최적 |
| 테스트타임 | 병렬 롤아웃 5→20 + 생성형 애그리게이터 |

논문: [arXiv:2603.05218](https://arxiv.org/abs/2603.05218) / [HTML 전문](https://arxiv.org/html/2603.05218v1)

## KARL이 푸는 문제

그라운디드 추론(grounded reasoning)은 검색·근거 통합이 필수인 영역입니다. 의료 기록 취합, 재무 표 계산, 기술 문서 절차 추론 같은 걸 말합니다.

문제는 기존 평가입니다. HotpotQA 같은 벤치마크는 이 능력의 아주 좁은 조각만 봅니다. 그래서 논문은 KARLBench라는 6개 영역 스위트를 만들었습니다.

- 제약 기반 개체 탐색(BrowseComp-Plus)
- 문서 간 보고서 통합(TREC-Biogen)
- 표 기반 수치 추론(FinanceBench)
- 전수 개체 수집(QAMPARI)
- 기술 문서 절차 추론(FreshStack)
- 사내 노트 팩트 집약(PMBench, 자체 벤치마크)

웹 검색 벤치마크를 일부러 배제했습니다. 살아있는 웹 변동성을 없애서 통제된 비교를 하기 위해서구요. 에이전트는 벡터 검색 도구 하나만 씁니다. 도구 오케스트레이션 효과를 분리하기 위함입니다.

![Figure 1: KARL의 비용/품질, 지연/품질 파레토 프론티어](/images/2026-09-10-karl-knowledge-agents-rl/fig1-pareto-cost-quality.png)
*Figure 1. KARL(테스트타임 컴퓨트 포함/미포함)과 최신 클로즈드 모델 비교. 출처: arXiv 2603.05218 Figure 1*

## 데이터는 프롬프트로 만들지 않는다

RL 데이터는 에이전트가 직접 만듭니다. <span style="background-color: #fff59d"><strong>합성 에이전트가 코퍼스를 벡터 검색으로 탐색하면서 근거가 담긴 QA쌍을 직접 생성하는 애전틱 합성 파이프라인</strong></span>입니다.

![Figure 2: 애전틱 데이터 합성 파이프라인](/images/2026-09-10-karl-knowledge-agents-rl/fig2-data-synthesis-pipeline.png)
*Figure 2. Stage I 데이터 합성 흐름. 출처: arXiv 2603.05218 Figure 2*

필터도 구체적입니다.

- 패스레이트 필터: <span style="background-color: #fff59d"><strong>8회 롤아웃이 전부 맞거나 전부 틀린 데이터는 제거</strong></span>
- 품질 필터: <span style="background-color: #fff59d"><strong>gpt-4o-mini 저지가 모호하거나 정답 오류인 문항 제거</strong></span>

그리고 여기서 자기부스트가 돌아갑니다. 학습으로 좋아진 에이전트가 다음 반복의 합성 데이터를 만듭니다. 2회 반복 후 BrowseComp-Plus에서 정답 근거 문서를 못 찾고 예산을 소진하던 롤아웃 패턴이 사라졌습니다.

## OAPL: 온라인 RL 없이 도는 반복 학습

학습 레시피는 OAPL(Optimal Advantage-based Policy Optimization with Lagged Inference)입니다. 논문이 같이 개발한 <span style="background-color: #fff59d"><strong>대배치 반복 오프폴리시 RL</strong></span> 패러다임이구요.

장점 세 가지가 실무적으로 중요합니다.

- 샘플 효율적
- 학습/추론 엔진 불일치에 강함
- 멀티태스크 학습이 온라인 RL에서 흔히 필요한 안정화 휴리스틱 없이 됨

## 결과: 파레토 프론티어

KARLBench에서 KARL은 Claude 4.6, GPT 5.2 대비 비용/품질, 지연/품질 모두에서 파레토 최적입니다. <span style="background-color: #fff59d"><strong>동등 품질을 더 낮은 비용·지연으로 내고, 테스트타임 컴퓨트를 충분히 주면 최고 클로즈드 모델 품질을 넘어섭니다</strong></span>.

여기서 주목할 점: 학습에 안 쓴 OOD 태스크(FinanceBench, QAMPARI, FreshStack, PMBench)에서도 우위가 유지됐습니다. 단일 벤치마크에 과적합되지 않았다는 뜻입니다.

정량 분석에서 RL 학습의 효과:

- 검색 다양성: 반복 2회에서 <span style="background-color: #fff59d"><strong>BrowseComp-Plus 고유 문서 37% 더 검색</strong></span>, TREC-Biogen 8% 더 검색
- 근거 적중: 의료 사례에서 <span style="background-color: #fff59d"><strong>베이스는 5개 너겟, KARL은 9개 전부 적중</strong></span> (비자발성 골절의 비전형 원인 탐색)

## 테스트타임 컴퓨트와의 궁합

![Figure 3: 병렬 솔버 롤아웃과 애그리게이션](/images/2026-09-10-karl-knowledge-agents-rl/fig3-solver-rollouts.png)
*Figure 3. Stage II 병렬 롤아웃. 출처: arXiv 2603.05218 Figure 3*

병렬 롤아웃 5→20개를 뿌리고 생성형 애그리게이터가 하나의 답으로 합칩니다. 다수결은 기존 답 중 하나를 고르는 방식이구요, <span style="background-color: #fff59d"><strong>애그리게이터는 후보 답들을 조합해 더 나은 새 답을 합성</strong></span>합니다.

- PMBench에서 N=5일 때 <span style="background-color: #fff59d"><strong>애그리게이터 결과가 개별 롤아웃 최고보다 나은 비율 23.7%</strong></span>
- <span style="background-color: #fff59d"><strong>N=15 넘으면 수익 체감</strong></span> (pass@k 포화 + 컨텍스트 길어짐)
- KARL의 우위는 모든 N에서 유지 → <span style="background-color: #fff59d"><strong>RL 학습 이득과 테스트타임 컴퓨트가 상보적</strong></span>

롱테일 대응도 참고할 만합니다. 긴 탐색 중 컨텍스트가 차면 압축 단계를 밟는데, <span style="background-color: #fff59d"><strong>BrowseComp-Plus에서 질문당 압축 중앙값 6회, 평균 10.2회, 약 80%가 20회 미만으로 해결</strong></span>됩니다.

## 한계: 검색은 좋아졌는데 계산은 그대로

솔직한 실패 사례도 있습니다. 크리켋 통계 수치 계산 문제에서 KARL은 근거를 이미 확보했는데도 계산하지 않고 13쿼리 만에 조기 종료하며 답을 내지 못했습니다. 미리 집계된 수치를 찾으려는 쿼리만 계속 날렸구요.

즉 <span style="background-color: #fff59d"><strong>RL이 개선한 건 검색 전략(쿼리 작성, 근거 축적, 커밋 캘리브레이션)이고, 검색 후 수치 계산 능력은 그대로</strong></span>입니다. 이건 KARL 도입 시 예상해야 할 경계선입니다.

정리했습니다. <span style="background-color: #fff59d"><strong>작은 모델 + 애전틱 합성 + 오프폴리시 RL + 테스트타임 애그리게이션이 하나의 배포 가능한 조합으로 끝까지 검증</strong></span>됐다는 게 이 논문의 실무적 가치입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### KARL은 어떤 모델을 베이스로 하나요?
GLM 4.5 Air입니다. 같은 하네스에서 베이스와 KARL을 직접 비교해서 RL 효과를 분리했습니다.

### KARL은 웹 검색 에이전트인가요?
웹 검색은 쓰지 않습니다. 닫힌 코퍼스에서 벡터 검색 도구만 쓰는 그라운디드 추론 에이전트입니다. 웹 검색 변동성을 통제하기 위한 설계 선택입니다.

### KARLBench는 어디서 볼 수 있나요?
논문 부록에 6개 태스크 구성과 예시가 정리되어 있고, PMBench만 자체 벤치마크로 비공개입니다.

### 클로즈드 모델보다 정말 좋은가요?
품질/비용·품질/지연 트레이드오프에서 파레토 최적이고, 테스트타임 컴퓨트를 충분히 주면 최고 클로즈드 모델 품질을 넘어섭니다. 다만 검색 후 수치 계산은 개선되지 않았습니다.
