---
title: "CANOPY: 결과 보상만으로 장기 에이전트를 훈련한 알리바바의 실험"
date: 2026-09-06
tags:
  - AI
  - RL
  - agent
  - LLM
  - post-training
draft: false
description: "Qwen3-14B를 AppWorld 리더보드 정상까지 올린 CANOPY 프로토콜의 두 가지 진단(신호 고갈, 정책 드리프트)과 해법을 결과 수치와 절제 실험 중심으로 정리한다."
---

## 결론 먼저

"소형 오픈 모델은 아웃컴 온리 RL로 오래 못 간다"는 통념이 있다. 알리바바 리서치의 CANOPY 논문(arXiv 2609.01245)은 이 통념을 뒤집는 결과를 냈다. Qwen3-14B를 환경 상호작용만으로 훈련해 <span style="background-color: #fff59d"><strong>AppWorld 공식 리더보드 정상(2026년 2월 기준, Test-Normal TGC 86.9)</strong></span>에 올렸다. SFT 사전학습, 스킬 라이브러리, 다중 에이전트 오케스트레이션 없이다.

논문의 진단은 단순하다. 통념이 한계로 보던 현상의 원인은 <span style="background-color: #fff59d"><strong>탐색 규모를 작게 잡은 운영 문제</strong></span>라는 것.

| 항목 | 내용 |
| --- | --- |
| 논문 | Explore More, Drift Less (arXiv 2609.01245) |
| 방법 | CANOPY (Coverage-ANchored On-PolicY RL) |
| 베이스 | Qwen3-14B / Qwen3.5-9B |
| 핵심 수치 | AppWorld Test-Normal TGC 86.9, Test-Challenge 67.6 |
| 추가 수치 | SWE-bench Verified +16.6포인트 |
| 코드 | github.com/AlibabaResearch/SignalCoverageRL (공개 예정) |

두 가지 실패 원인을 짚고 각각 대응한다.

## 실패 1: 신호 고갈

GRPO 계열은 그룹 내 성공과 실패가 섞여야 그래디언트가 살아난다. 전부 실패하면 어드밴티지가 0이라 그 태스크는 그 스텝에서 학습에 기여하지 못한다.

성공 확률 0.05인 하드 태스크에서 정보가 있는 그룹이 나올 확률은 <span style="background-color: #fff59d"><strong>n=8이면 34%, n=32면 81%</strong></span>다. 작은 그룹은 하드 태스크를 침묵시킨다.

기존 연구들이 하드 태스크를 "해롭다"고 보고한 건, 논문 해석으로는 <span style="background-color: #fff59d"><strong>탐색 부족을 보상 밀도로 보정한 결과</strong></span>다. 커버리지를 복원하면 같은 하드 태스크가 가장 값진 학습 데이터가 된다.

![Figure 1](/images/2026-09-06-canopy-outcome-only-rl/fig-1-p1.png)
*Figure 1: AppWorld Test-Normal TGC를 메서드 계열별로 정리. 훈련된 정책 중 CANOPY가 가장 작은 축에 속하는 백본으로 선두다. 출처: arXiv 2609.01245 Figure 1.*

![Figure 2](/images/2026-09-06-canopy-outcome-only-rl/fig-2-p3.png)
*Figure 2: 희소 보상에서의 신호 커버리지. 그룹 크기와 성공률에 따른 유의미 그룹 확률. 출처: arXiv 2609.01245 Figure 2.*

## 실패 2: 정책 드리프트

검증 가능한 태스크 풀이 작은 환경에서는 재방문이 불가피하다. 앵커 없는 반복 최적화는 엔트로피를 떨어뜨린다. <span style="background-color: #fff59d"><strong>포화로 정보가 있는 그룹이 귀해지는 시점에 정확히 탐색이 죽는다</strong></span>. 증상은 후반부 훈련 불안정이다.

## 프로토콜

1. 탐색 확대: 같은 태스크 그룹을 <span style="background-color: #fff59d"><strong>n=32(스텝당 2,880 롤아웃)</strong></span>, 턴당 생성 무제한, 하드 티어 유지.
2. 드리프트 억제: <span style="background-color: #fff59d"><strong>가벼운 KL 앵커(기준은 베이스 모델 고정), 완전 온폴리시 1패스 업데이트</strong></span>, 액션 토큰에만 손실.
3. 테스트 예산 확장: 훈련 50턴/32k → 테스트 100턴/61k. 탐색이나 다중 롤아웃 선택 없이.

환경 토큰은 마스크로 걷어내고 정책이 직접 뽑은 액션 토큰에만 그래디언트가 흐른다. 워커 OOM 같은 외인성 결함은 채점 전에 격리해 그룹을 줄이는 방식으로 처리하고, 턴 한도 도달 같은 에이전트 기인 종료는 0점 그대로 둔다.

## 결과와 절제 실험

- 같은 베이스, 같은 예산에서 <span style="background-color: #fff59d"><strong>훈련이 TGC 50포인트 이상을 추가</strong></span>했다.
- 다음 최고 훈련 정책(ESAT) 대비 Test-Normal 약 12 TGC, Test-Challenge 약 9 TGC 앞선다.
- 추론 시에는 프롬프트 하나에 체크포인트 하나. 오케스트레이션, 스킬 라이브러리, 검색 메모리가 전혀 없다.
- 예산 확장(50턴→100턴)은 훈련 정책에 79.5→83.2(mean@4), 베이스에는 22.8→32.4. 베이스도 오르지만 <span style="background-color: #fff59d"><strong>예산 자체가 능력을 사는 건 아니라는 게 드러난다</strong></span>.
- 단일 실행 86.9가 베이스의 best@4(58.9)를 28포인트 넘는다. Test-Challenge에서도 67.6 vs 37.7. <span style="background-color: #fff59d"><strong>RL이 리샘플링으로 도달 못 하는 능력을 더한다</strong></span>는 근거다.

![Figure 3](/images/2026-09-06-canopy-outcome-only-rl/fig-3-p6.png)
*Figure 3: 롤아웃 로그 기반 훈련 다이내믹스(n=32, 90 스텝). 난이도 L3가 다른 티어가 침묵한 뒤에도 오래 정보를 유지한다. 출처: arXiv 2609.01245 Figure 3.*

![Figure 4](/images/2026-09-06-canopy-outcome-only-rl/fig-4-p6.png)
*Figure 4: KL 앵커가 후반 붕괴를 막는다. 앵커 없는 실행은 스텝 70 이후 엔트로피 0.038로 붕괴하고 Dev가 81.6에서 멈춘다. 앵커 실행은 0.217을 유지하며 87.3까지 올라간다. 출처: arXiv 2609.01245 Figure 4.*

절제 실험(한 설정만 바꿔 90 스텝 재훈련):

| 절제 | Test-Normal TGC(mean@4) 변화 |
| --- | --- |
| 그룹 크기 32→8 | -16.4 |
| 온폴리시 위반(미니배치 2분할) | -17.4 |
| KL 앵커 제거 | -7.0 |
| 토큰 레벨 손실→시퀀스 정규화 | -5.4 |
| 하드 태스크 티어 제거 | -6.0 |
| 희소 보상→밀집(부분 점수) 보상 | -1.8 |

가장 큰 비용 두 개가 커버리지와 드리프트 양쪽에 하나씩 있다. <span style="background-color: #fff59d"><strong>보상 밀집화는 거의 차이가 없다(-1.8)</strong></span>. 부분 점수 보상은 탐색을 키우면 없어도 되는 보정이었다는 뜻이다.

![Metric map](/images/2026-09-06-canopy-outcome-only-rl/table-3-p6.png)
*Table 3: 훈련 예산과 확장 예산에서의 지표 매핑(스텝 90 체크포인트 기준). 출처: arXiv 2609.01245 Table 3.*

## SWE-bench Verified 이전

같은 설계 원리를 실제 저장소 수리로 옮긴다. Qwen3.5-9B + mini-swe-agent, bash만 쓰는 하네스로 SWE-rebench에서 훈련하고 SWE-bench Verified로 평가했다. 오염 방지를 위해 <span style="background-color: #fff59d"><strong>Verified에 등장하는 저장소의 태스크는 전부 제외</strong></span>했다. 결과는 같은 예산 매칭에서 +16.6포인트.

하이퍼파라미터는 그대로 옮기지 않고 n=16, KL 계수 1e-2, 패치 없는 종료 상태 -0.2로 재조정했다. 원리 이전이지 설정 복사가 아니다.

## 내 해석

논문 근거와 내 판단을 나눠서 적는다.

- "작은 그룹(n≤8)으로 하드 태스크를 돌리면 신호가 죽는다"는 인과는 계산과 절제 실험으로 뒷받침된다.
- 여기서 "하네스 엔지니어링의 시대가 끝났다"까지는 건너뛸 수 없다. 이 훈련은 <span style="background-color: #fff59d"><strong>검증 가능한 결과가 있는 도메인에서만 통한다</strong></span>. 검증자가 없는 영역에서는 여전히 하네스와 추론 시 시스템이 필요하다.
- AppWorld 훈련 풀이 90 태스크라는 건 명시적 한계다. 저자도 환경 스케일링을 다음 과제로 꼽는다.
- 그래도 방향성은 실용적이다. 스텝당 2,880 롤아웃은 비싸지만 <span style="background-color: #fff59d"><strong>스킬 라이브러리나 오케스트레이션을 유지보수하는 비용과 비교하면 단순한 투자</strong></span>다.

남는 결론: <span style="background-color: #fff59d"><strong>보상 설계를 손대기 전에 탐색 규모를 먼저 올려볼 것. 하드 태스크는 신호가 부족했을 가능성이 크다.</strong></span>

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**CANOPY는 새 RL 알고리즘인가요?**
아니다. 옵티마이저를 바꾸지 않고 그룹 크기 확대, KL 앵커, 완전 온폴리시 업데이트, 액션 토큰 마스크라는 기존 재료의 조합이다.

**왜 그룹 크기 32인가요?**
파일럿 패스로 가장 어려운 티어의 성공률을 추정하고, 목표 신호 커버리지를 만드는 그룹 크기를 데이터에서 정한다. 32는 그 계산의 결과다.

**SWE-bench에서도 하이퍼파라미터가 같나요?**
아니, 원리만 이전한다. n=16, KL 계수 1e-2, 빈 패치 터미널 -0.2로 재조정했다.

**기준일은 언제인가요?**
리더보드 순위는 2026년 2월 제출 기준, 체크포인트는 스텝 90 고정, 논문은 arXiv 2609.01245 (2026-09-01) 기준이다.
