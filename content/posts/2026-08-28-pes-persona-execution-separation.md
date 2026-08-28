---
title: "Persona-Execution Separation — 페르소나는 자유롭게, 실행은 감사 가능하게 분리하는 에이전트 아키텍처"
date: 2026-08-28
tags:
  - agent
  - architecture
  - governance
draft: false
description: "LLM 에이전트의 페르소나와 실행을 서로 다른 트러스트 도메인에 나눠 담는 PES 아키텍처 패턴을 정리했습니다. 핀테크 파일럿의 5개 설계 결정과 검증 결과까지 함께 봅니다."
---

## 결론 먼저

에이전트의 페르소나(지시문, 말투, 자기소개)와 실행(상태를 바꾸는 실제 작업)을 하나의 프로세스, 하나의 트러스트 도메인에 두면 둘 중 하나를 포기하게 됩니다. 페르소나를 자주 고치면 감사 추적이 무너지고, 감사를 엄격히 하면 페르소나가 얼어붙습니다.

arXiv 2608.27427 논문은 이 딜레마를 아키텍처로 푼 패턴을 제안합니다. Persona-Execution Separation(이하 PES). 핵심은 <span style="background-color: #fff59d"><strong>페르소나는 저통제 도메인에 두고 자유롭게 드리프트, 실행은 고통제 도메인에 두고 전량 감사, 둘 사이는 fail-closed 계약 브리지로만 연결</strong></span>하는 것입니다.

## 핵심 요약 표

| 항목 | 내용 |
| --- | --- |
| 논문 | Persona-Execution Separation: An Architecture Pattern for Evolving LLM Agents under Execution Audit (arXiv:2608.27427) |
| 발표일 | 2026-08-27 |
| 핵심 주장 | <span style="background-color: #fff59d"><strong>단일 트러스트 도메인에서는 자유 드리프트(G1), 실행 추적성(G2), 결합 해제(G3)를 동시에 만족할 수 없음</strong></span> |
| 제안 | 페르소나/실행을 분리 도메인에 배치 + 계약 브리지 |
| 파일럿 | 금융권 디지털 직원 플랫폼(FIA Workbench, 가명), 2026-07-19 ~ 2026-08-17 약 한 달간 5개 ADR |
| 검증 | <span style="background-color: #fff59d"><strong>5개 모델 설정에서 R = 0.00</strong></span> (페르소나 변동이 실행 재검증을 유발 안 함) |

## 왜 단일 도메인은 안 되는가

기본 설계를 보면 대부분 여기에 속합니다. 하나의 프로세스가 에이전트의 정체성(시스템 프롬프트, 지시문)과 실행(툴 콜, 사이드 이펙트)을 함께 들고 있죠.

이 구조에서 갈등은 구조적입니다. 통제를 엄격히 하면 페르소나 수정마다 모든 실행이 재검증 대상이 됩니다. 느슨하게 하면 감사 추적이 깨집니다. 논문의 표현을 빌리면 <span style="background-color: #fff59d"><strong>조직은 결국 페르소나를 얼려서 진화를 멈추거나, 통제를 풀어서 감사를 포기합니다</strong></span>.

논문은 3.2절에서 더 강한 주장을 합니다. LLM 표현 수준에서 페르소나 변경과 실행 변경이 구분 불가능(representational indistinguishability)하기 때문에, 단일 도메인 안에서 G1–G3를 다 만족하려면 결국 타입드 체인지 오브젝트, 외부 게이트, 안정적 감사 앵커를 다시 만들어야 합니다. 즉 <span style="background-color: #fff59d"><strong>PES를 더 높은 결합 비용으로 안에서 재건축하는 셈</strong></span>이죠.

## 기존 포지션 4개와 PES

![Fig. 1](/images/2026-08-28-pes-persona-execution-separation/fig-1-p4.png)

논문 Figure 1은 이 공간을 두 축(진화 자유 × 실행 추적성)으로 정리합니다.

| 포지션 | 진화 자유 | 직원 단위 추적 | 문제 |
| --- | --- | --- | --- |
| (1) 단일 도메인 | 낮음 | 있음 | 얼거나 풀거나 이지선다 |
| (2) 에이전트 + 툴 | 높음 | 없음 | 툴은 스테이트리스 함수, 툴 레벨 로그뿐 |
| (3) 오케스트레이터 + 서브에이전트 | 높음 | 종속적 | 서브에이전트는 종속 엔티티, 균일 권한 |
| (4) PES | 높음 | 있음 | 브리지 유지 비용 |

PES는 남은 마지막 코너를 차지합니다. <span style="background-color: #fff59d"><strong>대가는 계약 브리지의 구현과 운영</strong></span>입니다.

## PES 패턴의 구조

![Fig. 2](/images/2026-08-28-pes-persona-execution-separation/fig-2-p12.png)

Figure 2가 패턴 전부입니다. 하나의 직원 아이덴티티가 두 도메인에 걸쳐 있습니다.

- 저통제 도메인(표현 서피스): 페르소나가 여기 삽니다. 자유롭게 수정 가능
- 고통제 도메인(실행 서피스): SOP 루프, 승인, 감사 원장이 여기 있습니다. 페이스리스
- 계약 브리지: fail-closed. 3개 채널만 데이터가 오갑니다

세부 설계 결정이 흥미로운 부분입니다.

**페르소나 단일 소싱.** 페르소나는 정확히 한 곳에만 존재합니다. 실행 도메인은 읽기 전용 페르소나 미러조차 안 둡니다. <span style="background-color: #fff59d"><strong>두 번째 사본은 반드시 동기화 문제를 낳는다</strong></span>는 판단이에요.

**바인딩이지 프로젝션이 아님.** 실행 도메인에 페르소나를 복사하지 않고, 어떤 SOP를 시작할 수 있는지 식별자 목록(capability binding)만 넘깁니다. <span style="background-color: #fff59d"><strong>참조만 하고 복제는 안 합니다</strong></span>.

**레이어드 드리프트.** 자유 드리프트도 무한이 아닙니다. 코어 아이덴티티(이름, 직원 명부, 역할 경계, SOP 바인딩)는 드리프트 불가. <span style="background-color: #fff59d"><strong>감사 원장이 붙는 앵커라서 변경 자체가 승격 이벤트</strong></span>입니다. 서피스 페르소나(지시문, 말투, 스킬 튜닝)만 컴플라이언스 비용 0으로 자유롭게 바꿉니다.

## 브리지의 3채널

브리지를 통과하는 데이터는 세 종류뿐이고, <span style="background-color: #fff59d"><strong>그 외는 전부 거부(fail-closed)</strong></span>입니다.

1. 상태 요약만 역방향으로 흐름. 진행 상황, 단계, 담당자. <span style="background-color: #fff59d"><strong>원본 데이터(숫자, 고객 정보, 파일)는 실행 도메인 안에 남음</strong></span>
2. 데이터 본문은 못 나감. 단, DLP 마스킹 하에 지식 본문을 내보내는 E2 등급 예외는 검증 단계에서 합법화됨
3. 아이덴티티 연속성. 대화에서 원장 페이지로 딥링크해도 "대화로 돌아가기"로 왕복이 안 끊김

Bell-LaPadula의 no-write-down, Denning의 격자 모델, XACML의 PEP/PDP 분리가 이론적 뿌리로 언급됩니다. 근데 PES는 접근 제어 규칙이 아니라 "페르소나-실행 관계 자체"가 정책 대상이라는 점이 다릅니다.

## 파일럿: 한 달간 5개 결정

![Fig. 3](/images/2026-08-28-pes-persona-execution-separation/fig-3-p17.png)

![Table 3](/images/2026-08-28-pes-persona-execution-separation/table-3-p17.png)

파일럿은 금융업권 디지털 직원 플랫폼 FIA Workbench(가명)입니다. 2026-07-19 ADR-005부터 2026-08-17 ADR-030까지 한 달간 5개의 ADR(Architecture Decision Record)을 거치며 패턴이 수렴했습니다.

재미있는 점은 PES가 처음부터 설계 목표가 아니었다는 것. 페르소나 저장 위치, capability binding, 원웨이 밸브, 승격 채널, 듀얼페이스 결정이 개별적으로 내려졌고, 나중에 그게 하나의 패턴으로 크리스털라이즈됐습니다. 논문은 각 결정마다 기각된 대안을 함께 기록한 점을 강조합니다.

## 검증: R = 0.00

메커니즘 체크 결과가 이 논문의 실무적 신뢰 포인트입니다.

- <span style="background-color: #fff59d"><strong>페르소나 변동 후 실행 측 재검증 없음: 5개 모델 설정에서 R = 0.00</strong></span>
- 하드 어서트 필드에 페르소나 핑거프린트 없음
- 사전 분리 빌드(2026-08-14 복구) 프로브: 실행 경로가 페르소나와 "우연히" 분리돼 있었음(omission에 의한 분리). <span style="background-color: #fff59d"><strong>배선 하나 바뀌면 역전 가능한 상태</strong></span>였고, PES는 이걸 감사되는 아키텍처 규칙으로 만듦

마지막 항목이 실전 교훈입니다. <span style="background-color: #fff59d"><strong>우연한 격리는 격리가 아닙니다. 규칙이어야 합니다</strong></span>.

## 2025–2026 이웃 연구와의 차이

Fides, CaMeL, Progent, AgentSpec, Firewalls(DAF), SafeGPT, PoEM 등 실행 표면의 보안을 다루는 클러스터는 이미 있습니다. 프롬프트 인젝션, 데이터 유출, 권한 과잉을 막는 쪽이죠.

근데 논문의 스캔(2022–2026)에서 <span style="background-color: #fff59d"><strong>페르소나(운영 아이덴티티)를 고통제 실행과 다른 도메인에 두고 "자유 드리프트 + 감사 오염 방지"를 같이 달성한 조합은 없었다</strong></span>고 합니다. 의도/실행 분리(Chahine 2026), 페르소나 포이즌 방지(Shaikh & Virkki 2026)가 가장 가까운 이웃입니다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 툴 콜 루프 설계에 관심 있다면 아래 두 개를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### PES는 두 개의 에이전트로 쪼개는 건가요?

아닙니다. 하나의 직원 아이덴티티가 표현 서피스와 실행 서피스라는 두 얼굴을 갖는 구조입니다. 신원이 둘로 나뉘는 게 아니라 통제 영역이 둘로 나뉩니다.

### 페르소나를 마음껏 바꿔도 감사에 문제가 없나요?

서피스 페르소나(지시문, 말투) 한정입니다. 코어 아이덴티티(이름, 역할, SOP 바인딩)는 변경 자체가 승격 이벤트로 통제됩니다. 파일럿 검증에서 페르소나 변동이 실행 재검증을 유발하지 않았습니다(R = 0.00, 5개 모델 설정).

### 도입 조건이 있나요?

논문은 다음 세 조건이 동시에 성립할 때 적용한다고 봅니다. <span style="background-color: #fff59d"><strong>멀티유저 배포, 실행 감사 요구, 페르소나 변동 예상</strong></span>. 셋 중 하나라도 없으면 비용 대비 이득이 없습니다.

### 기존 오픈소스 플랫폼으로는 안 되나요?

DeepSeek Harness(단일 유저, 도메인 분리 없음), AgentScope(승인 시스템은 있으나 도메인 분리·페르소나 개념 없음), StaffDeck(SOP 상태머신과 권한 격리는 있으나 듀얼페이스 분리 없음) 등이 비교됐고, G1–G3를 동시에 만족하는 조합은 없었다는 게 논문의 결론입니다.

## 참고

- 원문: [Persona-Execution Separation (arXiv:2608.27427)](https://arxiv.org/abs/2608.27427)
- PDF: https://arxiv.org/pdf/2608.27427
- 본문 수치·인용은 모두 원문 기준이며, 기준일은 2026-08-28입니다.
