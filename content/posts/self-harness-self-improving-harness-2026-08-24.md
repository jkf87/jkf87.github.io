---
title: "Self-Harness: 하네스가 스스로를 고치는 루프 — 상하이AI랩의 에이전트 자가개선 실험"
date: 2026-08-24
tags:
  - agent
  - harness
  - LLM
  - self-improvement
  - coding-agent
  - automation
  - loop
draft: false
---

## 개요

Shanghai AI Laboratory가 2026년 8월 20일 arXiv:2606.09498v3 "Self-Harness: Harnesses That Improve Themselves"를 발표했습니다. 이 논문은 <span style="background-color: #fff59d"><strong>모델 가중치를 고정한 채, 에이전트가 자기 실행 데이터를 근거로 자기 하네스를 반복 개선하는 루프</strong></span>를 제안합니다.

핵심 결과부터 정리하면 다음과 같습니다.

- 벤치마크 3개(Terminal-Bench-2.0, SWE-bench Verified, AppWorld) × 모델 3종(MiniMax M2.5, Qwen3.5-35B-A3B, GLM-5) = <span style="background-color: #fff59d"><strong>9개 조합 전부에서 held-in/held-out 패스율 동시 상승</strong></span>
- 전체 상대 개선 최대 <span style="background-color: #fff59d"><strong>+132%</strong></span> (Qwen3.5, AppWorld: 22.5% → 52.2%)
- Terminal-Bench-2.0에서 Qwen3.5는 18.0% → 36.7%로 <span style="background-color: #fff59d"><strong>2배 이상(+104%)</strong></span> 개선

## 문제 정의

LLM 에이전트 성능은 베이스 모델과 하네스(시스템 프롬프트, 도구, 메모리 정책, 오류 복구 절차 등)가 함께 결정합니다. 논문의 문제 제기는 세 가지입니다.

1. 모델마다 실패 패턴이 달라서 <span style="background-color: #fff59d"><strong>효과적인 하네스 설계는 본질적으로 모델별 최적화 문제</strong></span>다.
2. 지금 하네스는 거의 다 사람 전문가가 손으로 만들어서 새 모델 등장 속도를 못 따라간다.
3. 강한 외부 모델에게 하네스를 고치게 하는 접근은 비용이 크고, 프론티어 모델에는 쓸 선생 모델이 없다.

Self-Harness는 여기에 대한 답으로 <span style="background-color: #fff59d"><strong>개선 대상 모델 자신이 제안자 역할까지 맡는 내부 개선 루프</strong></span>를 제시합니다.

![Figure 1: 세 가지 하네스 개선 패러다임 비교](/images/self-harness-self-improving-harness-2026-08-24/fig-1-p2.png)
*Figure 1. 사람의 하네스 엔지니어링, 외부 모델 기반 메타-하네싱, Self-Harness 비교. 출처: 논문 Figure 1.*

## 방법론: 3단계 루프

![Figure 2: Self-Harness 최적화 루프 개요](/images/self-harness-self-improving-harness-2026-08-24/fig-2-p5.png)
*Figure 2. 한 번의 Self-Harness 루프 전체. 출처: 논문 Figure 2.*

### 1. Weakness Mining (약점 채굴)

고정 모델 M을 현재 하네스 h_t 하에서 held-in 분할 태스크에 실행하고 실행 트레이스를 수집합니다. 실패 기록은 실패 서명 φ(r) = (c, q, m)에 따라 클러스터링됩니다.

- c: 검증자 수준의 최종 실패 원인
- q: 관련 에이전트 행동의 인과적 지위
- m: 트레이스에서 노출된 추상적 메커니즘

<span style="background-color: #fff59d"><strong>세 성분이 정확히 일치할 때만 같은 클러스터로 묶습니다.</strong></span> 타임아웃끼리 묶는 식의 겉핥기 분류를 피하고, 같은 하네스 개입으로 해결 가능한 실패만 모은다는 설계입니다. 각 클러스터로부터 클러스터 크기, 대표 태스크, 공통 증상, 검증자 증거를 담은 증거 번들 B_t가 만들어지고, 이 번들은 구체적 수정 처방을 포함하지 않습니다. 평가자와 제안자를 분리하는 장치입니다.

### 2. Harness Proposal (수정 제안)

동일한 고정 모델 M이 제안자(proposer) 역할로 호출됩니다. 제안자는 다음을 포함하는 유계 컨텍스트를 받습니다.

- 현재 하네스의 편집 가능 표면
- 1단계에서 나온 검증자 근거 실패 패턴
- 유지해야 할 기존 통과 행동 기록
- 이전에 시도한 수정 이력

제안자는 <span style="background-color: #fff59d"><strong>K개의 상호 배타적인 최소(minimal) 수정 후보</strong></span>를 병렬로 생성합니다. 각 제안은 특정 실패 메커니즘에 근거하고 구체적 편집 표면을 지목해야 하며, 감사 기록 a_j(대상 실패 패턴, 편집 표면, 기대 효과, 회귀 위험)를 동반합니다.

### 3. Proposal Validation (수정 검증)

각 후보 하네스는 held-in 및 held-out 분할에서 재평가됩니다. 승격 규칙은 다음과 같습니다.

<span style="background-color: #fff59d"><strong>Δ held-in ≥ 0, Δ held-out ≥ 0, 그리고 max(Δ held-in, Δ held-out) > 0</strong></span>

어느 한쪽이라도 떨어지면 거절이고, 통과한 수정만 병합됩니다. <span style="background-color: #fff59d"><strong>모델 가중치와 평가자는 전 과정에서 고정</strong></span>되며 바뀌는 것은 하네스뿐입니다.

## 실험 설정

- 벤치마크: Terminal-Bench-2.0 (64 사례 고정 부분집합), SWE-bench Verified (100 사례, 67 held-in / 33 held-out), AppWorld (180 사례)
- 모델: MiniMax M2.5, Qwen3.5-35B-A3B, GLM-5
- 초기 하네스: DeepAgent SDK 기반 최소 구성 (짧은 시스템 프롬프트 + 기본 파일시스템/셸 도구)

## 주요 결과

![Table 1: 초기 하네스 vs Self-Harness 패스율](/images/self-harness-self-improving-harness-2026-08-24/table-1-p11.png)
*Table 1. 초기/최종 하네스의 held-in, held-out, 전체 패스율(%). 출처: 논문 Table 1.*

| 벤치마크 | 모델 | 초기 (전체) | Self-Harness (전체) | 상대 개선 |
|---|---|---|---|---|
| Terminal-Bench-2.0 | MiniMax M2.5 | 42.2% | 53.9% | +28% |
| Terminal-Bench-2.0 | Qwen3.5-35B-A3B | 18.0% | 36.7% | +104% |
| Terminal-Bench-2.0 | GLM-5 | 46.1% | 57.0% | +24% |
| SWE-bench Verified | MiniMax M2.5 | 46.0% | 52.5% | +14% |
| SWE-bench Verified | Qwen3.5-35B-A3B | 19.5% | 41.5% | +113% |
| SWE-bench Verified | GLM-5 | 52.0% | 55.5% | +7% |
| AppWorld | MiniMax M2.5 | 48.6% | 58.9% | +21% |
| AppWorld | Qwen3.5-35B-A3B | 22.5% | 52.2% | +132% |
| AppWorld | GLM-5 | 44.4% | 85.0% | +91% |

여기서 읽히는 패턴 두 가지:

- <span style="background-color: #fff59d"><strong>약한 모델일수록 개선 폭이 큽니다.</strong></span> Qwen3.5-35B-A3B는 세 벤치마크에서 +104~132%. 초기 하네스가 최소 구성이라 약한 모델이 하네스 없이 잃는 점수가 컸다는 해석입니다.
- held-out에서도 전 조합 상승. held-in 과적합만은 아니라는 신호입니다.

![Figure 4: 모델별 하네스 진화 궤적](/images/self-harness-self-improving-harness-2026-08-24/fig-4-p12.png)
*Figure 4. 모델/벤치마크별 진화 궤적. 초록 = 채택, 회색/빨강 = 거절. 출처: 논문 Figure 4.*

채택된 수정은 작고 감사 가능한 변경들이었습니다. 구체적으로:

- MiniMax M2.5 / Terminal-Bench: <span style="background-color: #fff59d"><strong>아티팩트 조기 생성, 도구 호출 50회 후 리다이렉트, 스키마 준수</strong></span> 3개 수정으로 42.2% → 53.9%
- Qwen3.5 / Terminal-Bench: 의존성 사전검사, 루프 브레이커, 툴 에러 트리거 미들웨어로 18.0% → 36.7%
- GLM-5 / Terminal-Bench: 셸 세션 간 변경사항 영속화, 탐색→구현 전환 규칙으로 46.1% → 57.0%
- GLM-5 / AppWorld: null 완료 의미론, 진척 확인 알림, 페이지네이션 소진 규칙으로 <span style="background-color: #fff59d"><strong>44.4% → 85.0%</strong></span>

트레이스 분석의 대표 사례 하나. 초기 하네스의 Qwen3.5는 extractor 스크립트를 만든 뒤 덮어쓰기/수정 실패를 반복하다가 결국 해당 파일을 지우고 종료해 검증에 실패합니다.

수정된 하네스에서는 툴 에러 발생 시 시스템 프롬프트가 개입해 아티팩트를 재생성하고, 파싱을 고치고, JSON을 검증하고, <span style="background-color: #fff59d"><strong>검증자가 요구하는 파일을 남겨둔 채 종료</strong></span>합니다. 모델은 그대로인데 행동이 바뀐 겁니다.

## 한계

논문이 스스로 명시하는 한계는 다음과 같습니다.

- 본 연구는 <span style="background-color: #fff59d"><strong>고정 벤치마크에서의 유계 하네스 수정 실험이지 열린 자기개선이 아닙니다.</strong></span>
- 채택된 수정은 벤치마크 특화 실패 패턴을 반영할 수 있습니다.
- 검증자 결과와 트레이스 기록 품질에 의존합니다.
- <span style="background-color: #fff59d"><strong>더 위험도가 높은 하네스 변경에는 패스율 비회귀를 넘어서는 승격 게이트가 필요하다</strong></span>고 저자들이 직접 적었습니다.

## 실무 관점 요약

하네스 개선을 자동화하려는 실무자에게 남기는 교훈은 이것입니다. <span style="background-color: #fff59d"><strong>'수정 제안 생성'이 아니라 '실패 서명 클러스터 → 최소 수정 → 회귀 게이트'라는 증거 파이프라인을 먼저 구축하는 것이 효과의 핵심</strong></span>입니다. 실행 트레이스에서 반복 실패를 뽑아 그것만 고치는 접근과, 그럴듯한 제안을 그대로 반영하는 접근은 결과가 다릅니다.

## 더 실습해보고 싶은 분들께

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

Zhang, Hangfan et al. "Self-Harness: Harnesses That Improve Themselves." arXiv:2606.09498v3, 2026-08-20. https://arxiv.org/abs/2606.09498
