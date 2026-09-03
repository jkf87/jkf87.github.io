---
title: "SafeEvolve 정리 — 하네스와 정책을 같이 진화시키는 에이전트 안전 정렬"
date: 2026-09-03
tags:
  - agent
  - safety
  - harness
  - RL
  - LLM
  - prompt-injection
draft: false
description: "arXiv 2609.02786 SafeEvolve 리뷰. 트레이스의 안전 경험을 하네스 업데이트와 정책 RL이 같이 쓰는 공진화 루프로 AgentDojo ASR 2.37%→0.79%, AgentHarm 유해 점수 56.45→12.27을 달성한 구조와 수치를 정리했습니다."
---

## 결론 먼저

에이전트를 운영해 보면 이런 실패를 다 겪습니다. 프롬프트와 스킬을 아무리 정교하게 다듬어도 약한 모델은 그걸 끝까지 따라 하지 못하고, 모델만 파인튜닝하면 새로 생기는 실패 패턴에 대응이 늦습니다. SafeEvolve(arXiv 2609.02786, Shanghai AI Lab 외)의 답은 <span style="background-color: #fff59d"><strong>하네스 업데이트와 정책 학습, 두 바퀴를 트레이스 증거로 맞물려 돌리는 것</strong></span>입니다.

핵심 수치 (Qwen3.5-4B 기준, 기준일 2026-09-03, arXiv 2609.02786v1):

| 항목 | Base | SafeEvolve | 변화 |
|---|---|---|---|
| AgentDojo ASR ↓ | 2.37% | 0.79% | 약 3배 감소 |
| AgentDojo Utility ↑ | 59.79% | 61.86% | 소폭 상승 |
| AgentHarm Harmful ↓ | 56.45 | 12.27 | 큰 폭 감소 |
| AgentHarm Refusal ↑ | 28.98% | 83.83% | 약 3배 상승 |

논문: [arXiv:2609.02786](https://arxiv.org/abs/2609.02786) / 코드: [github.com/MaoPopovich/SafeEvolve](https://github.com/MaoPopovich/SafeEvolve)

## 문제 설정: 한쪽만 고치면 안 되는 이유

에이전트는 하네스(명령, 스킬, 메모리 등 <span style="background-color: #fff59d"><strong>모델 외부의 편집 가능한 컴포넌트</strong></span>)를 통해 환경과 상호작용합니다. 안전 실패는 최종 응답뿐 아니라 다단계 실행 중간의 위험한 툴콜이나 주입 지시 추종에서 발생합니다.

기존 접근의 한계:

1. 하네스만 진화 — <span style="background-color: #fff59d"><strong>정교한 아티팩트가 약한 고정 정책에서 실행되지 않고</strong></span>, 다단계 실행 중 감쇠하며, 모델 간 이전도 안 됩니다.
2. 정책만 학습 — 고정 하네스 아래 최적화라 <span style="background-color: #fff59d"><strong>새 실패 모드에 대한 적응 지침이 없고</strong></span>, 파라미터에 박힌 안전 능력은 모델 간 이전이 어렵습니다.

![하네스 단독/정책 단독/공진화 비교](/images/2026-09-03-safeevolve-harness-policy-co-evolution/fig-1-p2.png)

## 프레임워크 구조

![SafeEvolve 개요](/images/2026-09-03-safeevolve-harness-policy-co-evolution/fig-2-p4.png)

### 하네스 쪽: 증거 기반 유한 업데이트

완료된 온-폴리시 트레이스에서 안전 증거를 뽑아 안전 프롬프트와 3계층 스킬 뱅크(일반 원칙 / 태스크·도구 절차 / 반복 실수 수정)를 갱신합니다. <span style="background-color: #fff59d"><strong>모든 업데이트는 버전·롤백 메타데이터를 달아 감사 가능하고 되돌릴 수 있게</strong></span> 만들고, 에피소드 시작 시 검색으로 필요한 스킬만 노출한 뒤 에피소드 내에는 고정합니다.

### 정책 쪽: 2단계 SFT→RL

1. Harness-use SFT: 진화된 하네스에서 검증기를 통과한 트레이스만 모아 <span style="background-color: #fff59d"><strong>어시스턴트 응답과 툴콜 턴에 대해서만 학습</strong></span>하는 콜드스타트입니다. 스킬을 언제 쓰고 무시할지 부트스트랩합니다.
2. Harness-augmented RL: 진화된 하네스 컨텍스트에서 그룹 샘플링한 트레이스에 그룹 상대 어드밴티지로 업데이트합니다.

보상은 검증기 분해형이며 태스크 타입별로 다릅니다:

| 태스크 타입 | 보상 |
|---|---|
| clean | 유틸리티 점수 U(τ) |
| 악성 쿼리 | 안전 점수 S(τ) (유해 요청 수행에 벌점) |
| 환경 인젝션 | λU·U + λS·S + λUS·U·S (유틸리티·안전·교차항) |

<span style="background-color: #fff59d"><strong>인젝션 보상에 U·S 교차항을 넣어 '본래 태스크 완수 + 주입 무시'를 동시에 만족하는 트레이스를 우대</strong></span>하는 게 설계 포인트입니다. λ 계수는 모든 백본·실행에서 고정입니다.

### 루프 전체

각 롤아웃 배치는 명시적 (정책, 하네스) 쌍에서 생성되고, 현재 배치는 정책을 갱신하며 최근 배치들의 증거는 다음 라운드 하네스 갱신을 제안·검증합니다. <span style="background-color: #fff59d"><strong>행동 변화의 원인이 정책 갱신인지 하네스 갱신인지 나중에 귀속해서 따져볼 수 있게</strong></span> 기록이 남습니다.

## 실험 결과 리딩

백본은 Qwen3.5-4B와 Qwen3-4B-Instruct-2507. 롤아웃 200 스텝, 배치당 32 태스크 × 8 롤아웃 = 트레이스 256개/업데이트, 최대 프롬프트 4096 토큰, 학습률 1e-6입니다.

Table 1 (Qwen3.5-4B, AgentDojo):

| 방법 | Utility ↑ | U-Attack ↑ | ASR ↓ |
|---|---|---|---|
| Base | 59.79 | 60.04 | 2.37 |
| SFT | 60.82 | 59.83 | 1.53 |
| DPO | 60.82 | 60.93 | 1.97 |
| GRPO | 30.93 | 26.48 | 13.35 |
| MetaSecAlign | 61.86 | 58.51 | 2.29 |
| AgentAlign | 60.82 | 56.77 | 0.79 |
| SafeEvolve | 61.86 | 56.77 | 0.79 |

읽을 거리:

- GRPO는 안전 RL이 <span style="background-color: #fff59d"><strong>공격 시 유틸리티를 60.04→26.48로 붕괴</strong></span>시키는 전형적 실패를 보여줍니다. 검증 보상만으로는 감독이 불안정합니다.
- AgentAlign은 Qwen3-4B에서 유해 점수를 크게 낮추지만 benign 점수와 툴 유틸리티가 무너집니다.
- SafeEvolve는 <span style="background-color: #fff59d"><strong>거부율 28.98%→83.83%를 달성하면서 benign 유틸리티도 유지</strong></span>합니다. 단일 보수 행동이 아니라 위험 유형별 대응을 학습했다는 게 논문의 해석입니다.

## 하네스만 바꿔도 되는가 (Table 2)

정책을 얼리고 하네스만 진화시키는 실험입니다.

| 조건 (Qwen3.5-4B) | AgentDojo ASR ↓ | AgentHarm Harmful ↓ | Refusal ↑ |
|---|---|---|---|
| Base | 2.37 | 56.45 | 28.98 |
| Evolved prompt | 1.27 | 43.49 | 48.85 |
| Evolved skills | 0.92 | 16.80 | 76.97 |

<span style="background-color: #fff59d"><strong>학습 없이도 스킬 뱅크만으로 ASR 2.37→0.92, 유해 점수 56.45→16.80</strong></span>까지 갑니다. 검색된 절차적 가이던스가 다단계 실행에서 단일 글로벌 프롬프트보다 안정적이라는 결과입니다. 이 부분이 실무적으로 가장 바로 쓸 수 있는 구간입니다.

## 스킬 뱅크 성장 과정 (Figure 4)

![스킬 뱅크 진화](/images/2026-09-03-safeevolve-harness-policy-co-evolution/fig-4-p9.png)

<span style="background-color: #fff59d"><strong>액티브 스킬 뱅크가 26개에서 47개로 성장</strong></span>하며, 대부분 태스크 특화 스킬과 반복 실수 수정 스킬입니다. 게이트를 통과한 수정만 반영되며, 수락 사례는 이런 것들입니다:

- 모호한 예약 ID와 참조 삭제 대상 해결
- 누락된 툴 인자 추가
- 중첩 소스에서 정확한 타깃 사용
- 존재하지 않는 업데이트 필드 조작 방지

![스킬 검색 전략 ablation](/images/2026-09-03-safeevolve-harness-policy-co-evolution/table-3-p9.png)

검색 전략 ablation(Table 3)도 같은 방향입니다. general 스킬만으로도 ASR은 줄지만 유틸리티를 잃고, <span style="background-color: #fff59d"><strong>계층 검색 + 동적 스킬 우선이 안전-유틸리티 균형을 회복</strong></span>합니다.

## 일반화: 제안 모델 교체와 정책 간 이전

![제안 모델 ablation](/images/2026-09-03-safeevolve-harness-policy-co-evolution/fig-5-p10.png)

하네스 업데이트 제안을 GPT-5.5, DeepSeek-Chat, GLM-5.1로 바꿔도 <span style="background-color: #fff59d"><strong>세 제안자 모두 베이스 대비 안전 영역으로 이동</strong></span>합니다. 제안자 선택은 벤치마크별 트레이드오프에 영향을 주지만 구조 자체가 특정 강모델에 묶이지 않습니다.

![크로스-정책 하네스 이전](/images/2026-09-03-safeevolve-harness-policy-co-evolution/fig-6-p10.png)

Qwen3.5-4B에서 진화한 하네스를 다른 정책에 그대로 옮기면 4B 타깃에서 가장 잘 이전되고, 1.7B에서는 <span style="background-color: #fff59d"><strong>약한 정책이 진화된 가이던스를 끝까지 실행하지 못하는 한계</strong></span>가 드러납니다. 이 호환 간극이 공진화가 필요하다는 근거로 제시됩니다.

## 내 해석과 한계

- 이 논문의 답은 '하네스 대 파라미터' 논쟁에 대해 둘 다입니다. 다만 공허한 절충이 아니라 <span style="background-color: #fff59d"><strong>트레이스 증거라는 공유 기반과 감사 가능한 유한 업데이트라는 구체적 접점</strong></span>을 제시했다는 점이 의미 있습니다.
- Table 2의 무학습 개선 폭이 크다는 건 실무에서 바로 적용할 수 있는 신호입니다.
- 유의점: 메인 결과가 4B급 백본과 LLM 생성 유한상태 시뮬레이터에서 나왔고, 교차항 가중치가 고정이며, 1.7B 이전 실패가 보여주는 정책 용량 의존성은 실서비스 적용 시 따져봐야 할 변수입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### SafeEvolve의 핵심 아이디어는 무엇인가요?
완료된 온-폴리시 트레이스의 안전 증거를 하네스(프롬프트·계층형 스킬 뱅크) 업데이트와 정책 SFT→RL이 번갈아 소비하는 공진화 루프로 만드는 것입니다.

### AgentDojo와 AgentHarm에서 수치는 어떻게 변했나요?
Qwen3.5-4B에서 AgentDojo ASR 2.37%→0.79%, AgentHarm 유해 점수 56.45→12.27, 거부율 28.98%→83.83%입니다. Benign 유틸리티는 유지·소폭 상승했습니다.

### 정책 학습 없이도 효과가 있나요?
있습니다. 정책을 얼린 상태에서 진화된 스킬 뱅크만 적용해도 AgentDojo ASR 0.92%, AgentHarm 유해 점수 16.80까지 개선됩니다(Table 2).

### 인젝션 태스크의 보상은 어떻게 설계되었나요?
유틸리티, 안전, 그리고 두 점수의 곱 항(U·S)을 고정 가중치로 결합해 본래 태스크 완수와 주입 무시를 동시에 만족하는 트레이스를 우대합니다.

### 이 논문의 한계는 무엇인가요?
4B급 백본 중심 검증, LLM 생성 시뮬레이터 환경 의존, 고정 보상 가중치, 약한 정책(1.7B)로의 하네스 이전 실패 등입니다.
