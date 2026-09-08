---
title: "CONTINUITY — 에이전트 보안 컨트롤의 조합 실패를 막는 보안 문맥 컨트랙트 (arXiv 2609.05269)"
date: 2026-09-08
tags:
  - ai-agent
  - security
  - llm
  - arxiv
draft: false
description: "arXiv 2609.05269 정리. 개별 에이전트 보안 컨트롤이 조합될 때 보안 문맥이 유실되는 security-context discontinuity 문제를 assume-guarantee 컨트랙트와 검증 가능한 witness 체인으로 해결한 CONTINUITY 프레임워크를 2,560개 공격 차단 결과와 함께 정리했습니다."
---

## 결론 먼저

ZAST.AI 팀이 2026년 9월 4일 arXiv 2609.05269로 공개한 "CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls"를 정리했습니다.

핵심은 이겁니다. 에이전트 보안 컨트롤은 하나씩 보면 다 맞는데, 파이프라인으로 합치면 <span style="background-color: #fff59d"><strong>보안 문맥이 경계에서 사라지거나 바뀌는 실패</strong></span>가 있습니다. 논문은 이걸 <span style="background-color: #fff59d"><strong>security-context discontinuity</strong></span>로 정의하고, 검증 가능한 컨트랙트 체인으로 해결하는 프레임워크를 제안합니다.

핵심 수치 (기준일 2026-09-04, arXiv 2609.05269v1):

| 항목 | 값 |
|---|---|
| 공격 인스턴스 2,560건 중 유해 효과 | 0건 (Effect ASR 0.0%) |
| 정상 태스크 700건 자동 완료 | 100% |
| 모호 태스크 200건 에스컬레이션 | 100% |
| 최강 불완전 대조군 Gateway+Finality ASR | 65.6% |
| 신뢰 코어 규모 | 약 1.5 KLOC |
| 중앙값 증명 검증 / 전체 전환 | 4.21 ms / 7.17 ms |

논문: [arXiv:2609.05269](https://arxiv.org/abs/2609.05269), 구현: [github.com/zast-ai/continuity](https://github.com/zast-ai/continuity)

## 문제 정의

전형적인 에이전트 파이프라인은 ingress 인증, provenance 서비스, 메모리 계층, 정책 게이트웨이, 프로토콜 어댑터, 툴 서버, 최종 effect sink로 이어집니다. 각 컴포넌트는 국소적으로 올바른데도 <span style="background-color: #fff59d"><strong>종단 경로는 불안전할 수 있습니다</strong></span>.

논문의 예시가 직관적입니다. 신뢰할 수 없는 인보이스에서 유래한 이메일 수신처를 보죠. provenance 레이어가 라벨을 붙이고 게이트웨이가 검증된 release를 요구합니다. 근데 뒤의 어댑터가 직렬화하면서 소스 바인딩을 떨구거나 논리 alias를 재작성하면, <span style="background-color: #fff59d"><strong>최종 sink는 유효 서명과 허용 툴명만 보고 게이트웨이가 승인한 대상과 같은지 판단할 수 없습니다</strong></span>.

논문이 정리한 불연속 형태 다섯 가지:

- 자기 선언 권한 루트에서 체인 시작
- 컴포넌트 서명 키가 부여받지 않은 역할로 승인됨
- release가 필드명만 지정하고 소스 값·유효기간은 미바인딩
- 선언된 관계의 증명 없이 어댑터가 변환 수행
- finality sink가 subject·policy·revocation·replay 체크 생략

암호 서명만으로는 이걸 못 막습니다. <span style="background-color: #fff59d"><strong>서명은 누가 만들었는지만 증명해요</strong></span>. 그 주체가 그 단계에 대한 권한이 있었는지, 변환이 상위 계약을 보존했는지는 증명하지 않으니까요.

## 접근 방법

CONTINUITY는 <span style="background-color: #fff59d"><strong>ECI(End-to-End Consequence Integrity)</strong></span>를 정의합니다. 실현된 모든 외부 효과는 인증된 root grant에서 시작해 각 승인된 전환을 거쳐, 현재 유효한 1회용 effect-bound permit까지 이어지는 검증 가능한 witness를 가져야 한다는 조건이에요. witness에는 필드 수준 소스 커밋먼트, 컴포넌트 신원과 계약, typed release, 변환 증거, finality 상태가 들어갑니다.

각 컨트롤은 assume–guarantee 컨트랙트 `Ci = (Ai, Gi, Pi, Mi)`로 모델링됩니다. 입력 가정, 출력 보장, 보존 필드, 명시적 변환 관계 네 가지구요. 안전한 조합의 조건은 <span style="background-color: #fff59d"><strong>상위 보장이 하위 가정을 소거하고, 변경된 보안 필드는 보존되거나 독립 검증되는 관계 witness로 정당화되어야 한다</strong></span>는 겁니다.

| 메커니즘 | 역할 |
|---|---|
| 서명된 root grant | 인증 권한 체인 시작점 보장 |
| 역할 바인딩 컴포넌트 신원 | 키 역할 오용 차단 |
| RFC 6901 JSON Pointer leaf path | 필드 수준 provenance 지정 |
| bounded typed release | 소스·값·유효기간 바인딩 공개 |
| transformation witness | 변환 before/after/관계 증명 |
| 1회용 finality permit | subject·action·policy·revocation·replay 바인딩 |

설계 포인트 하나 짚으면, 어댑터는 모든 정상 시나리오에서 실제 보안 관련 변환(논리 수신처 alias의 canonical 주소 해석)을 수행합니다. 신뢰된 디렉터리 witness가 before 값·after 값·관계·컴포넌트·계약·태스크·만료를 묶을 때만 받아들여요. 즉 <span style="background-color: #fff59d"><strong>모든 변경을 금지하는 대신 검증을 통과한 변경만 허용하는 구조</strong></span>입니다.

![Figure 1: CONTINUITY 아키텍처](/images/2026-09-08-continuity-security-context-contracts/fig-1-p8.png)

Figure 1: CONTINUITY 아키텍처 — 플래너는 신뢰 경로 밖에 있고, 각 전환이 서명된 receipt와 witness로 검증됩니다 (원문 Figure 1).

## 평가 결과

평가는 결정론적 컴포먼스 스위트로 합니다. <span style="background-color: #fff59d"><strong>플래너는 이미 침해된 상태로 가정하고 공격을 시작</strong></span>해요. LLM이 공격을 거절해서 막힌 걸 보안 경로 성과로 계상하지 않기 위해서입니다.

규모는 이렇습니다. 32개 교차 계층 fault 클래스, 4개 도메인, 도메인당 20개 파라미터화 인스턴스, 700개 정상 태스크, 200개 모호 태스크. 총 <span style="background-color: #fff59d"><strong>3,460 시나리오, 24,220 시스템-시나리오 실행</strong></span>이구요.

| 구성 | Effect ASR | 차단 클래스 (128 중) | 정상 완료 | 모호 에스컬레이션 |
|---|---|---|---|---|
| Pass-through | 100.0% | 0 | 100% | 0% |
| Tool allowlist | 100.0% | 0 | 100% | 0% |
| Gateway policy | 96.9% | 4 | 100% | 0% |
| Provenance gateway | 84.4% | 20 | 100% | 100% |
| Effect-bound permit | 81.3% | 24 | 100% | 0% |
| Gateway + Finality | 65.6% | 44 | 100% | 100% |
| CONTINUITY | 0.0% | 128 | 100% | 100% |

최강 불완전 구성인 Gateway+Finality조차 65.6% ASR입니다. 게이트웨이 승인과 정확한 최종 액션 바인딩이 있어도, <span style="background-color: #fff59d"><strong>permit 발급자가 post-adapter 액션이 게이트웨이 승인 상태와 어떻게 연결되는지 검증하지 않으면 뚫립니다</strong></span>. 컴포지션 갭이 곧 공격면이라는 중심 주장의 수치 근거예요.

![Figure 3: 유해 효과 성공률과 정상 자동 완료](/images/2026-09-08-continuity-security-context-contracts/fig-3-p12.png)

Figure 3: 불완전 구성은 교차 계층 fault에 여전히 노출되지만 전체 시스템은 정상 완료를 유지합니다 (원문 Figure 3).

## 어블레이션과 한계

타겟 어블레이션에서 <span style="background-color: #fff59d"><strong>필드 provenance 제거, 컨트랙트 정합성 제거, 불완전 매개 제거가 각각 24개 fault-domain 클래스를 재오픈</strong></span>합니다. 제일 큰 영향이에요.

반면 authority monotonicity 단독 제거는 0개입니다. 논문은 이 점에 대해 "해당 불변량이 논리적으로 불필요하다는 증명이 아니라 <span style="background-color: #fff59d"><strong>다른 불변량의 중복 차단</strong></span>"이라고 명시적으로 못 박습니다. 해석의 절제가 돋보이는 부분이구요.

![Figure 4: 비제로 타겟 어블레이션의 Effect ASR](/images/2026-09-08-continuity-security-context-contracts/fig-4-p12.png)

Figure 4: ablation별 Effect ASR — provenance·contract·mediation 제거가 최대 18.8%까지 재개방합니다 (원문 Figure 4).

성능은 기록된 호스트에서 <span style="background-color: #fff59d"><strong>중앙값 증명 검증 4.21 ms, 전체 전환 7.17 ms</strong></span>입니다. 네트워크·모델·외부 정책 서비스·저장소 지연은 제외된 마이크로벤치마크라는 주의가 붙어요.

![Table 4: 레퍼런스 프로토타입 레이턴시](/images/2026-09-08-continuity-security-context-contracts/table-4-p13.png)

Table 4: 레퍼런스 프로토타입 레이턴시 (원문 Table 4).

한계도 명확하게 적혀 있습니다. <span style="background-color: #fff59d"><strong>결과는 결정론적 컴포먼스 문이지 실세계 공격 확률 추정이 아니고</strong></span>, fault 분류의 완전성, 신뢰 검증기의 정확성, TCB 침해 저항은 범위 밖입니다.

## 내 해석

제 정리는 세 줄입니다.

프롬프트 인젝션 대응에서 "게이트웨이 정책 + 툴 화이트리스트면 충분하다"는 통념을 수치로 반박하는 데이터입니다. 대조군이 정확히 그런 실무 조합의 자리에 있고 <span style="background-color: #fff59d"><strong>65.6~100% ASR이 나옵니다</strong></span>.

전체 프레임워크 도입보다는 조각 단위 적용이 현실적이에요. 툴 호출 직전 permit에 canonical 액션을 바인딩하고 1회만 쓰게 하기, 어댑터에서 값이 바뀔 때 before/after 관계 증명 남기기 정도는 기존 시스템에도 붙일 수 있습니다.

모호한 태스크는 자동 실행을 멈추고 Escalate로 넘기는 설계가 200/200으로 동작하면서 정상 태스크 완료율 100%를 유지합니다. <span style="background-color: #fff59d"><strong>보안 강화가 실용성을 해치지 않는다는 게 같은 표에서 증명됩니다</strong></span>.

## 자주 묻는 질문

- **CONTINUITY는 프롬프트 인젝션을 방어하나요?** 인젝션은 막지 못해도, 인젝션 결과가 외부 효과로 커밋될 때 witness가 없으면 차단합니다. 플래너 침해 가정 하에 2,560개 공격을 전부 차단했습니다.
- **실존 시스템과 비교한 결과인가요?** 아닙니다. 6개 대조군은 메커니즘 수준의 네거티브 컨트롤이에요.
- **오버헤드는 어느 수준인가요?** 중앙값 검증 4.21 ms, 전체 전환 7.17 ms입니다. 네트워크·모델 지연은 제외된 마이크로벤치마크예요.
- **TCB가 침해되면 어떻게 되나요?** 논문의 명시적 범위 밖입니다. 신뢰된 검증기·키 서비스·finality sink가 정상 동작한다는 가정 위의 결과입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

출처: Chris Zheng, Geng Yang. "CONTINUITY: Security-Context Contracts for Composable LLM Agent Controls." arXiv:2609.05269 (2026). [PDF](https://arxiv.org/pdf/2609.05269) · [코드](https://github.com/zast-ai/continuity)
