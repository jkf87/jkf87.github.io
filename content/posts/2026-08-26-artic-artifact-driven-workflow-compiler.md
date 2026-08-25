---
title: "논문 정리: Artic — 자연어 워크플로를 컴파일해서 에이전트 실행 성공률 28%p 올리기 (arXiv 2608.21341)"
date: 2026-08-26
tags:
  - agent
  - LLM
  - workflow
  - harness
  - compilation
  - reliability
draft: false
---

## 개요

- 논문: Natural-Language Workflows Are Not Software Yet: Artifact-Driven Compilation for Reliable Agent Execution
- 저자: Xiangzhe Xu, Hanxi Guo (공동 1저자), Guangyu Shen, Siyuan Cheng, Xiangyu Zhang (Purdue University)
- 게시: 2026-08-21, arXiv 2608.21341 (cs.SE)
- 링크: https://arxiv.org/abs/2608.21341

## 문제 정의

자연어 워크플로는 에이전트를 위한 소프트웨어 유사 인터페이스로 확산 중이다. <span style="background-color: #fff59d"><strong>도메인 전문가가 절차를 자연어로 작성하면 에이전트가 이를 실행한다</strong></span> 다만 소프트웨어가 기대하는 두 속성 — 환경 간 재사용 가능한 예측 가능성, 프로그램 지시에 대한 정확한 이행 — 이 자연어 워크플로에서는 성립하지 않는다.

논문이 지적하는 원인은 다음 두 가지다.

1. 암묵적 데이터 의존성: <span style="background-color: #fff59d"><strong>각 스텝이 과거 컨텍스트의 모든 중간 결과에 접근 가능하다</strong></span>. <span style="background-color: #fff59d"><strong>중간 결과를 전역 변수에 저장하는 프로그램에 비유된다</strong></span>. 실행 에이전트는 매 스텝 관련 결과를 식별해야 하며 노이즈가 있으면 오류가 발생한다.
2. 이행 부담의 증가: 컨트롤 플로우가 복잡하고 중간 결과가 많으면 <span style="background-color: #fff59d"><strong>스텝 누락, 잘못된 제어 이전, 컨텍스트 컴팩션 중 정보 유실이 발생한다</strong></span>.

![Fig. 1](/images/2026-08-26-artic-artifact-driven-workflow-compiler/fig-1-p3.png)

Fig. 1은 환자 리퍼럴 워크플로(χ-Bench 유래)의 실패 모드를 보여준다. Error A는 필요한 이용 이력 대신 의사의 만성질환 리퍼럴 메시지를 근거로 삼은 사례, <span style="background-color: #fff59d"><strong>Error B는 `high risk OR recent acute utilization` 조건을 AND로 해석한 사례다</strong></span>.

## 제안 방법: Artic

Artic(ARTIfact-driven workflow Compiler)은 자연어 워크플로를 아티팩트 중심 워크플로로 변환하는 컴파일러다. 아티팩트 중심 언어에서 각 스텝은 다음을 선언한다.

- 읽기/쓰기 아티팩트
- 산출 아티팩트에 대한 제약(constraints)
- 명시적 제어 이전 조건

스텝 내부의 로컬 동작은 자연어 지시로 유지되어 에이전트가 수행한다. 데이터 의존성과 제어 이전만 명시적·검사 가능해진다. 이 표현은 부담(burden) 신호를 분석 가능하게 만든다. 다수 아티팩트에 의존하는 스텝은 컨텍스트 압박 지표로, 중첩 분기는 제어 복잡도 지표로 식별된다.

![Fig. 3](/images/2026-08-26-artic-artifact-driven-workflow-compiler/fig-3-p4.png)

컴파일 파이프라인은 두 단계다.

1. 제약 최적화: LLM이 초안을 작성하고, 프로그램 분석이 문제 구간(과도한 제어 복잡도, 컴팩션 생존 어려운 라이브 아티팩트 등)을 보고한다.
2. 충실성 검증: 정적 검증, 귀납 검증(전역 충실성 주장을 지역 의무로 분해), 드라이런 시뮬레이션(원본/컴파일본 실행 트레이스 비교). <span style="background-color: #fff59d"><strong>실패 시 진단을 최적화 단계로 환류한다</strong></span>.

검증 없는 컴파일러 변형은 전체 시스템 대비 16%p 저하된다. 드라이런이 리퍼럴 출처 자격 검증 누락을 발견하는 사례가 Fig. 12에 제시된다.

## 실험 설정

- 데이터: <span style="background-color: #fff59d"><strong>SOP-Bench 기반 11개 실제 도메인 워크플로, 488개 문제 인스턴스</strong></span>
- 컴파일러 모델: GPT-5.4, Sonnet-4.6, GLM-5 (컴파일러 선택에 따른 성능 변동은 안정적)
- 실행기 모델: 3B 활성 ~ 700B+ 총 파라미터 6종 (GLM-4.7-Flash, GPT-OSS-120B, Qwen3-235B 등)
- 실행 환경: <span style="background-color: #fff59d"><strong>공통 Codex 기반 에이전트 하네스, MCP 툴 인터페이스</strong></span>
- 메트릭: 태스크 해결률(벤치마크 오라클 충족 비율)

## 결과 요약

### RQ1 해결률

- <span style="background-color: #fff59d"><strong>원문 텍스트 워크플로 대비 평균 28%p 향상</strong></span>
- 모든 실행기 모델에서 최고 평균: GLM-4.7-Flash 85%, GPT-OSS-120B 82%, Qwen3-235B 85%
- 베이스라인: Text 직접 실행, SkillCreator(텍스트 재작성), Code(Python 구현), MASFactory/Chat2Workflow(NL-to-workflow 파이프라인). 단순 도메인에서 Code가 근접하나 복잡 도메인에서 일반화 부족

### RQ2 일관성

- <span style="background-color: #fff59d"><strong>실행기 모델 교차 일관성 +32%p, 반복 실행 일관성 +56%p</strong></span>
- Medical 도메인 인스턴스 단위 일관성: 컴파일 워크플로 80% vs 텍스트 48%
- k=10 반복 실행: 텍스트 16%p 하락, 컴파일본 유지
- 환경 교란(일시 오류, 컨텍스트 컴팩션) 하 성능: 컴파일본 100% 유지 vs 텍스트 80%
- <span style="background-color: #fff59d"><strong>에이전트당 평균 입력 토큰 63%, 출력 토큰 50% 감소</strong></span>

### RQ3 비용

- <span style="background-color: #fff59d"><strong>컴파일은 워크플로당 1회 오프라인 비용</strong></span>. GLM-5 기준 중위 컴파일 시간 5분 미만, 평균 비용 $3 미만

### RQ4 어블레이션

- <span style="background-color: #fff59d"><strong>드라이런 피드백, 귀납 검증, 최적화 각각 8~32%p 기여</strong></span>. 최적화(부담 스텝 식별·분해) 기여가 최대

## 논의

- KYB 도메인의 오타/조작 판별처럼 <span style="background-color: #fff59d"><strong>모델 판단력에 의존하는 문제는 워크플로 강제로 해결되지 않는다</strong></span>. 논문은 이를 워크플로 강제와 직교하는 문제로 명시한다.
- 기여 요약: 워크플로 강제를 아티팩트 기반 실행 모델로 형식화, 컴파일러 구현, 검증 패러다임(지역 의무 분해 + 드라이런) 제안, 488 인스턴스 평가.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
