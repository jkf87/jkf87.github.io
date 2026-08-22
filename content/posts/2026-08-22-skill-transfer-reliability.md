---
title: 태스크 단위로 뽑은 스킬은 독이다 — 서브태스크 단위 스킬 이전 연구 정리
date: 2026-08-22
tags:
  - LLM
  - agent
  - skill
  - memory
  - evaluation
draft: false
---

## 결론 먼저

LLM 에이전트가 지난 태스크에서 "스킬"을 뽑아 재사용할 때, 태스크 전체를 요약해서 만든 스킬은 성능을 오히려 떨어뜨리고, <span style="background-color: #fff59d"><strong>서브태스크 단위로 쪼개서 만든 스킬은 성능을 올립니다</strong></span>. 그리고 <span style="background-color: #fff59d"><strong>텍스트 노트 형태가 코드 형태보다 이전이 잘 됩니다</strong></span>.

논문: "Break It Down, Pass It On: Cross-Task Skill Transfer in LLM Agents" (Stony Brook University, arXiv:2608.20274, 2026-08-20)

## 무엇을 비교했나

연구진은 기존 스킬 유도 방법들이 서로 다르게 만드는 두 축을 분리해서 테스트했습니다.

| 축 | 값 |
|---|---|
| 유도 단위 | 태스크 전체 vs 서브태스크 |
| 스킬 형식 | 텍스트 노트 vs 파이썬 코드 |

여기에 스킬 없는 기본 에이전트를 포함해 총 6개 조건(Task, Task+Text, Task+Code, Subtask, Subtask+Text, Subtask+Code)을 비교했습니다. 유도 프롬프트는 조건 간에 동일하게 맞춰서, <span style="background-color: #fff59d"><strong>각 축의 효과만 분리</strong></span>됩니다.

실험 환경은 이렇습니다.

- 벤치마크 3개: <span style="background-color: #fff59d"><strong>AppWorld, OfficeBench, KramaBench</strong></span> (장기 과제 벤치마크)
- 모델 11개: <span style="background-color: #fff59d"><strong>Qwen3 4B~235B, Gemma-3 4B~27B, GPT-OSS-120B, Nemotron-Super-120B, Gemini-3.1-Pro</strong></span>
- 에이전트는 태스크 스트림을 순서대로 풀면서, 각 태스크(또는 서브태스크) 뒤에 스킬을 쓰고 다음 태스크 앞에 검색해 읽습니다

![](/images/2026-08-22-skill-transfer-reliability/fig-1-p1.png)
*Figure 1. 서로 다른 태스크도 서브태스크(로그인, 장바구니 확인 등)는 공유한다. 태스크 단위 스킬은 원본 태스크에 묶여 공유되지 않고, 서브태스크 단위 스킬은 공유 서브태스크에서 서로 이전된다.*

## 핵심 수치

태스크 단위 스킬은 기본(스킬 없음) 대비 평균 성공률을 떨어뜨립니다.

- 텍스트 스킬: <span style="background-color: #fff59d"><strong>-1.2 포인트</strong></span>
- 코드 스킬: <span style="background-color: #fff59d"><strong>-4.1 포인트</strong></span> (벤치마크별로는 <span style="background-color: #fff59d"><strong>최대 -7.4 포인트</strong></span>)

같은 유도 프롬프트를 서브태스크 단위에 적용하면 방향이 뒤집힙니다.

- 텍스트 스킬: <span style="background-color: #fff59d"><strong>+1.9 포인트</strong></span>
- 코드 스킬: +0.5 포인트

Subtask+Text 조건은 <span style="background-color: #fff59d"><strong>3개 벤치마크 전부에서 이득</strong></span>이 나왔습니다. Subtask+Code는 3개 중 2개에서 이득, KramaBench에서는 -1.4 포인트였습니다.

모델별 편차는 있습니다. 예를 들어 AppWorld에서 Qwen3-235B는 스킬 없이 7.4%인데 Task+Text가 <span style="background-color: #fff59d"><strong>18.0%까지 오르는 반면, GPT-OSS-120B는 27.3%에서 17.0%로 떨어집니다</strong></span>. 그래서 평균 효과와 개별 모델 효과는 구분해서 봐야 합니다.

전체 조건을 태스크 난이도별로 나눠도 같은 패턴이 유지됩니다.

![](/images/2026-08-22-skill-transfer-reliability/fig-4-p7.png)
*Figure 4. 6개 조건의 태스크 성공률을 난이도별로 나눈 그림. 모델을 pooling한 결과.*

## 왜 서브태스크가 나은가: 스킬 유틸리티 점수

논문은 각 스킬의 두 속성을 측정합니다.

- specificity: 스킬이 실제 태스크들과 얼마나 가까운가
- abstractness: 스킬의 관련도가 여러 태스크에 얼마나 고르게 퍼지는가

두 속성 각각은 따로 보면 성공률을 예측하지 못합니다. specificity만 높거나 abstractness만 높은 스킬은 나머지를 잃어버려서 성공률이 오르내립니다. 대신 <span style="background-color: #fff59d"><strong>두 속성의 곱(specificity × abstractness)은 일관되게 성공률과 상관</strong></span>합니다. 저자들은 이 곱을 "<span style="background-color: #fff59d"><strong>skill utility score</strong></span>"라고 부릅니다.

실제로 검증 결과:

- 태스크를 검색된 스킬의 평균 유틸리티로 나누면, 낮은 구간에서 높은 구간으로 갈수록 성공률이 단조 증가합니다. 태스크 단위 에이전트는 <span style="background-color: #fff59d"><strong>14.0% → 24.5%</strong></span>, 서브태스크 단위는 <span style="background-color: #fff59d"><strong>22.8% → 31.0%</strong></span>
- 스킬 라이브러리를 유틸리티 중앙값으로 반으로 나눠 각각 따로 실행하면, 고유틸리티 절반이 두 라이브러리 모두에서 더 높은 성공률을 냅니다 (태스크 단위 44.0% vs 42.9%, 서브태스크 단위 48.4% vs 47.0%)

이 점수의 실용적 장점은 <span style="background-color: #fff59d"><strong>계산에 태스크 실행이 필요 없다</strong></span>는 겁니다. 스킬 텍스트와 태스크 설명만 있으면 되니까, <span style="background-color: #fff59d"><strong>새 태스크를 돌리기 전에 스킬 메모리를 진단</strong></span>하는 용도로 쓸 수 있습니다.

![](/images/2026-08-22-skill-transfer-reliability/fig-5-p8.png)
*Figure 5. (a) 검색 스킬 평균 유틸리티로 태스크를 나누면 성공률이 단조 상승. (c)–(e) 서브태스크·텍스트 스킬의 유틸리티가 높다.*

## 실제 재사용도 확인

스킬이 정말 태스크 간에 이전되는지도 확인했습니다. 태스크 스트림을 50개 구간으로 나누고, 앞 구간에서 만든 스킬이 뒤 구간에서 검색되는 쌍의 비율(transfer density)을 측정한 결과, 서브태스크 단위 에이전트가 3개 벤치마크 모두에서 밀도가 높았습니다.

- AppWorld: <span style="background-color: #fff59d"><strong>31% vs 20%</strong></span>
- OfficeBench: 40% vs 28%
- KramaBench: 17% vs 6%

## 예산 관점에서는 반전 구간이 있다

계산 예산(컨텍스트에 드는 연산량)과 지연시간 기준으로 보면, 가장 작은 예산 구간에서는 태스크 단위 에이전트가 앞섭니다. 계획 단계가 없으니 저렴하기 때문입니다. <span style="background-color: #fff59d"><strong>예산이 커지면 서브태스크 단위 에이전트가 같은 비용으로 더 많은 태스크를 풉니다</strong></span>.

![](/images/2026-08-22-skill-transfer-reliability/fig-3-p5.png)
*Figure 3. 태스크당 예산 대비 성공률. 가장 작은 예산에서만 태스크 단위가 앞서고, 중간 이상 예산에서는 서브태스크+스킬이 같은 비용으로 더 많이 푼다.*

## 내 해석

지금 많은 에이전트 프레임워크가 "태스크 끝나고 회고를 저장해서 다음에 재사용한다"는 패턴을 기본으로 깔고 있습니다. 이 논문 결과는 <span style="background-color: #fff59d"><strong>그 저장 단위가 성능 방향을 가른다</strong></span>는 걸 보여줍니다. <span style="background-color: #fff59d"><strong>회고를 통째로 한 문서로 남기면 대부분의 모델에서 해가 되고</strong></span>, 서브태스크 단위로 쪼개면 도움이 됩니다.

코드로 저장하는 게 더 견고할 것 같은 직관도 여기서는 안 맞았습니다. 텍스트 노트가 코드보다 이전이 잘 됐습니다. 저자들은 코드 스킬이 인스턴스별 값들을 파라미터로 일반화하면서 오히려 검색·적용이 어려워진다고 분석합니다.

한계도 적어둡니다. 이 연구는 고정된 유도·검색·중복제거 규칙을 쓰고, 스킬을 에이전트가 스스로 수정하는 방식(최근 메모리 시스템들의 기능)은 다루지 않습니다. 평가도 최종 상태 기반이라 중간 단계 품질은 별도 판단이 필요합니다.

## 실무 적용 체크리스트

- 회고·스킬 저장은 <span style="background-color: #fff59d"><strong>태스크 전체 요약이 아니라 서브태스크 단위로 쪼개서 저장</strong></span>
- 형식은 <span style="background-color: #fff59d"><strong>텍스트 절차 노트로 작성</strong></span> (코드 스킬은 이전이 덜 됨)
- 스킬 라이브러리가 쌓이면 specificity × abstractness 곱으로 스킬별 점수를 매기고, 낮은 스킬은 정리
- 최소 예산 환경이라면 계획 단계 자체가 비용이니 이 트레이드오프를 감안

코드와 데이터는 github.com/Zesearch/skill-transfer-llm-agents에 공개되어 있습니다.

원문: [arXiv:2608.20274](https://arxiv.org/abs/2608.20274)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
