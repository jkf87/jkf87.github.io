---
title: "SHE: 롤아웃 트라젝토리로 안전 하네스를 진화시키는 프레임워크 정리"
date: 2026-08-19
tags: [agent-safety, harness, LLM-agent]
draft: false
---

논문: [Safety Harness Evolution (SHE), arXiv 2608.09885](https://arxiv.org/abs/2608.09885) (Shanghai AI Lab, Fudan, SJTU, HKUST, 2026-08-10)

결론부터 정리했습니다. <span style="background-color: #fff59d"><strong>LLM 에이전트의 안전성은 모델 가중치와 함께, 컨텍스트·메모리·도구·권한을 관리하는 하네스(harness)가 함께 결정합니다</strong></span>. 이 논문은 하네스를 배포 후 고정물로 두는 대신, <span style="background-color: #fff59d"><strong>실행 트라젝토리의 실패를 진단해서 하네스의 안전 경계를 스스로 진화시킵니다</strong></span>. 핵심은 이겁니다.

- <span style="background-color: #fff59d"><strong>하네스를 4개 아티팩트로 분해: System Prompt, Rule Bank, Safety Memory, Tool Policy</strong></span>
- 실패 트라젝토리를 구조화 진단 → 책임 아티팩트로 라우팅 → 국소 수정
- Agent-SafetyBench에서 <span style="background-color: #fff59d"><strong>ASR 17.1% → 5.5% (정적 SafeHarness 대비 3.1배 감소), 평균 UA 31.6% → 47.6% 향상</strong></span>
- 진화된 하네스는 학습에 안 쓴 AgentHarm과 다른 에이전트 모델(Kimi K2.6, GLM-5.2, MiniMax M2.7)에도 그대로 이전됨

![SHE 프레임워크 개요](/images/2026-08-19-she-safety-harness-evolution/fig-2-p4.png)

## 하네스 안전을 정적으로 유지할 때 생기는 문제

기존 안전 장치는 Llama Guard, NeMo Guardrails, LlamaFirewall 같은 가드레일이나 Task Shield, Progent, SafeHarness 같은 하네스 레벨 방어로 접근합니다. 근데 <span style="background-color: #fff59d"><strong>이 방어들은 배포 후 고정입니다</strong></span>. <span style="background-color: #fff59d"><strong>규칙은 사람이 설계한 대로 멈춰 있고, 새로운 공격 패턴이 트라젝토리에 드러나도 그 실패를 규칙으로 되먹임하는 통로가 없습니다</strong></span>.

논문이 지적하는 장애물은 두 개입니다.

| 문제 | 내용 |
|---|---|
| 결합된 기능 | 하나의 안전 실패가 컨텍스트 구성·메모리 검색·도구 권한·응답 필터에 얽혀 있어서 어디를 고쳐야 할지 특정이 안 됨 |
| 트라젝토리 → 규칙 변환 | 실행 기록에는 도구 관찰, 검증 결과, 실패 기록이 풍부한데, 여기서 실행 가능한 규칙 수정을 뽑아내기 어려움 |

진단은 가능한데 개선이 자동으로 이어지지 않는 상태입니다. SHE가 메우는 게 이 간극입니다.

## 4개 아티팩트 분해 구조

SHE는 하네스를 편집 가능한 네 가지 상태로 나눕니다.

| 아티팩트 | 역할 | 형태 |
|---|---|---|
| System Prompt | 전역 행동 계약: 소스 신뢰 위계, 능력 근거, 신뢰 경계 | 텍스트 |
| Rule Bank | 리스크 분류·개입 규칙 (allow/warn/block/sanitize/judge) | 규칙 레코드 |
| Safety Memory | 반복 진화로도 못 막은 실패의 경험치 | 대조적 경계 엔트리 |
| Tool Policy | 도구 호출·관찰·차단·복구에 대한 권한 강제 | 정책+디텍터 레코드 |

<span style="background-color: #fff59d"><strong>각 아티팩트에 안전 책임을 명시적으로 배정하는 게 핵심입니다</strong></span>. 실패가 어느 책임 영역에 속하는지 특정할 수 있어서, 한 컴포넌트 수정이 다른 컴포넌트를 건드리는 간섭을 막습니다.

## 진화 루프 동작 순서

![SHE 동기](/images/2026-08-19-she-safety-harness-evolution/fig-1-p2.png)

1라운드는 이렇게 돕니다.

1. 롤아웃 수집: 진화용 태스크를 현재 최적 하네스로 실행
2. 구조화 진단: <span style="background-color: #fff59d"><strong>실패를 3차원으로 분해 — harm domain(피해 유형) / attack surface(침입 채널) / failure mode(실패 양상)</strong></span>
3. 아티팩트 라우팅: 진단을 책임 아티팩트로 지정
4. 국소 수정(bounded edit): 라우팅된 아티팩트만 수정. 과거 거절 이력도 피드백으로 반영
5. 유효성 검사: 스키마 준수, 보상 해킹성·과도한 기능 제거 여부 확인
6. 최적 하네스 선택: <span style="background-color: #fff59d"><strong>안전 점수가 오르고 유틸리티가 떨어지지 않을 때만 채택</strong></span>, 아니면 거절 사유 저장 후 롤백

Safety Memory는 갱신 조건이 별도입니다. <span style="background-color: #fff59d"><strong>같은 실패 패턴이 2라운드 넘게 미해결이거나 수정 후 재발할 때만 경계를 엔트리로 저장합니다</strong></span>.

## 실험 설정

- 베이스 에이전트: DeepSeek-V3.2 / 진화·판정 모델: GPT-5.5 / AgentHarm 판정: GPT-4o
- Agent-SafetyBench 첫 200 태스크 중 15개만 진화에 사용(90 태스크-조건 인스턴스), <span style="background-color: #fff59d"><strong>나머지 185개는 최종 평가 전용 — 데이터 누수 방지</strong></span>
- 공격 조건 6종: clean, context poisoning, indirect injection, tool tampering, memory injection, composite attack
- 20 진화 라운드, 각 조합 2회 롤아웃, temperature 0

## 결과 숫자

| 지표 | SHE seed → evolved | 정적 SafeHarness → SHE evolved |
|---|---|---|
| 평균 ASR | <span style="background-color: #fff59d"><strong>8.6% → 5.5%</strong></span> | 17.1% → 5.5% |
| Clean UBR | 25.7% → 19.8% | — |
| 평균 UA | <span style="background-color: #fff59d"><strong>33.5% → 47.6%</strong></span> | 31.6% → 47.6% |

![모델 간 이전 결과](/images/2026-08-19-she-safety-harness-evolution/fig-3-p7.png)

Hold-out AgentHarm에서는 <span style="background-color: #fff59d"><strong>Harm Score 19.8% → 9.8%, Harm Refusal 78.4% → 86.4%</strong></span>. 진화에 안 쓴 리스크에도 경계가 이전됩니다. Kimi K2.6, GLM-5.2, MiniMax M2.7에 <span style="background-color: #fff59d"><strong>추가 진화 없이 하네스를 옮겨도 안전성 개선이 유지됐습니다</strong></span>.

인용 원문의 핵심 주장: 진화된 하네스는 정적 SafeHarness 대비 "3.1× lower average ASR and 50.6% higher UA"를 달성하면서 benign utility도 함께 올립니다.

## 진화가 실제로 배운 경계의 예시

![학습된 안전 경계 사례](/images/2026-08-19-she-safety-harness-evolution/fig-5-p9.png)

가장 구체적인 예시는 앱 설치 유도 실패 사례입니다. 사용자가 앱 추천을 요청했을 때, <span style="background-color: #fff59d"><strong>에이전트가 추천을 넘어 기기 레벨 자동 설치까지 실행한 게 실패 지점이었습니다</strong></span>. SHE는 이걸 두 경계로 바꿉니다.

- Rule Bank: <span style="background-color: #fff59d"><strong>앱 추천·공식 스토어 안내는 허용, 기기 레벨 설치 실행은 금지</strong></span>
- Tool Policy: 설치 액션에 실행 제약 부과

추천은 살리고 설치만 차단하는, 트라젝토리에서 뽑은 재사용 가능한 경계를 만든 겁니다. 벤치마크 특화 핵이 아니라고 저자들은 주장합니다.

## 내 해석

이 논문의 가치는 안전 장치 자체를 버전 관리 대상으로 취급했다는 점입니다. 근데 두 가지는 짚어둘 필요가 있습니다.

첫 번째, 진화 품질이 GPT-5.5 진단에 의존합니다. 진화 모델을 바꾸는 절제 실험(Table 3)에서 DeepSeek-V3.2는 이른 수렴 후 안전을 공격적으로 올리고, GPT-5.5는 유틸리티 보존이 강하고, GLM-5.2는 중간입니다. <span style="background-color: #fff59d"><strong>진화 모델 선택이 곧 안전-유틸리티 트레이드오프 선택입니다</strong></span>.

두 번째, 진화는 15개 태스크에서 20라운드 돌았고 <span style="background-color: #fff59d"><strong>수용 지점은 R00, R03–R05, R17 다섯 곳뿐입니다</strong></span>. R05–R16은 플래토라서 후보가 계속 거절됩니다. 안전-유틸리티 동시 개선 조건이 보수적이라 실제로 살아남는 수정은 많지 않습니다. 이건 장점이자 비용입니다.

실무 관점에서 하네스의 System Prompt·규칙·도구 권한을 아티팩트로 분리하고, 실패 로그 기반으로 국소 수정한 뒤 유틸리티 회귀 테스트를 거쳐 채택하는 루프 — <span style="background-color: #fff59d"><strong>이 구조는 논문 구현을 그대로 안 써도 프롬프트/가드레일 운영에 바로 벤치마킹 가능한 설계입니다</strong></span>.

코드는 [github.com/RainbowQTT/SHE](https://github.com/RainbowQTT/SHE)에 공개되어 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
