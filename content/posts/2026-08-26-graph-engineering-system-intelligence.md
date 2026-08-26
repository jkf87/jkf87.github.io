---
title: "에이전트 하나 더 늘리는 대신 그래프를 설계하기 — Graph Engineering 서베이 읽기"
date: 2026-08-26
tags: [agent, LLM, multi-agent, system-intelligence, graph, survey]
draft: false
---

멀티에이전트 시스템에서 에이전트 수를 늘리는 것만으로는 성능이 안 나옵니다.

JLU DEEP 연구팀 등이 8월 21일 올린 서베이 "Graph Engineering in the Era of LLM Agents"(arXiv 2608.21156)은 이 지점에서 출발해서, <span style="background-color: #fff59d"><strong>태스크·에이전트·시스템 상태를 명시적 그래프로 구조화하는 설계 패러다임</strong></span>을 제안합니다. 이름하여 Graph Engineering이구요.

![](/images/2026-08-26-graph-engineering-system-intelligence/fig-1-p4.png)

## 왜 개별 에이전트로는 부족한가

논문의 진단은 구조적입니다. 실무 과제는 이질적 전문성, 상호 의존적 서브태스크, 병렬 실행, 독립 검증, 지속 상태를 요구하는데, 이걸 단일 에이전트 루프 하나에 밀어 넣으면 <span style="background-color: #fff59d"><strong>컨텍스트 용량 경쟁, 순차 제어 흐름 병목, 상태 격리 불가</strong></span>라는 세 가지 구조적 한계가 생깁니다.

여기서 논문이 정리하는 수식이 직관적입니다. `Agent = Loop(LLM + Harness)`. 프롬프트/컨텍스트 엔지니어링이 모델 인텔리전스를 끌어내고, 하네스/루프 엔지니어링이 개별 인텔리전스를 만든다면, 그 위의 시스템 인텔리전스는 <span style="background-color: #fff59d"><strong>에이전트를 많이 두는 게 아니라 일을 조직하는 방식</strong></span>이 결정한다는 겁니다. 에이전트가 열 명 있어도 <span style="background-color: #fff59d"><strong>역할 경계·조정 메커니즘·상태 관리가 없으면 시스템은 똑똑해지지 않아요</strong></span>.

## Graph Engineering의 세 기둥

![](/images/2026-08-26-graph-engineering-system-intelligence/fig-2-p7.png)

핵심 프레임은 세 가지 조직 문제입니다.

| 기둥 | 질문 | 다루는 것 |
|---|---|---|
| Task Organization | 무엇을 할지 | 목표 분해, 의존성·순서·동시성 표현, 검증 제약 |
| Agent Coordination | 누가 할지 | 이질적 에이전트 매핑, 통신·위임·동기화, 결과 통합 |
| Runtime State Management | 어떻게 굴러갈지 | 진행 추적, 출처 보존, 고장 국소화, 부분 복구 |

![](/images/2026-08-26-graph-engineering-system-intelligence/fig-6-p16.png)

Task Organization은 전역 목표를 실행 단위로 쪼개고 의존성 그래프(DAG)로 표현합니다. 저자들이 인용하는 사례 중 하나가 순차 계획을 <span style="background-color: #fff59d"><strong>병렬화 가능한 데이터플로우 그래프로 컴파일</strong></span>하는 접근이에요.

단일 에이전트 루프에서 시스템 지능으로 넘어가는 전형적인 예입니다.

![](/images/2026-08-26-graph-engineering-system-intelligence/fig-8-p20.png)

Runtime State Management는 실무자에게 가장 와닿는 부분입니다. 장기 실행 프로세스에서 진행 상황을 추적하고, 동시 업데이트를 조정하고, <span style="background-color: #fff59d"><strong>어디서 실패했는지 국소화하고 부분 복구하는 구조</strong></span>를 그래프 상태로 유지한다는 내용이에요.

공유 컨텍스트 하나에 모든 상태를 몰아넣는 방식과 정반대의 설계입니다.

## 서베이의 실용적 가치

<span style="background-color: #fff59d"><strong>70페이지짜리 서베이</strong></span>라 다 읽기 부담스럽다면, 실무자 관점에서 챙길 만한 건 두 가지입니다.

첫 번째, <span style="background-color: #fff59d"><strong>벤치마크·오픈소스 라이브러리를 3계층으로 정리</strong></span>했다는 점.

모델 인텔리전스(사전학습·포스트트레이닝), 개별 인텔리전스(하네스·루프), 시스템 인텔리전스(멀티에이전트 오케스트레이션)별로 벤치마크와 도구를 매핑해 둬서, 지금 내 시스템이 어느 계층의 문제를 풀고 있는지 진단할 때 쓸 수 있습니다.

다음으로 애플리케이션 분석입니다. 소프트웨어 엔지니어링, 과학 발견, 의료, 엔터프라이즈 워크플로, 사회·경제 시뮬레이션 영역을 훑으며 <span style="background-color: #fff59d"><strong>Task Organization과 Agent Coordination은 실무에서 이미 널리 쓰이는데 System Evolution(그래프 자체의 자기 진화)은 아직 드물다</strong></span>는 교차 결론을 줍니다. 여기가 연구·제품 양쪽의 빈 땅이라는 신호예요.

## 남겨진 과제

논문이 지목한 공개 과제도 정리했습니다. 그래프 네이티브 능력 기반 구조, 자가 진화 그래프 시스템, 그래프 네이티브 에이전트 OS, 그리고 프라이버시·윤리가 그것입니다. 다음 방향으로는 시스템 인텔리전스를 측정하는 방법론과 온톨로지 엔지니어링까지 언급합니다.

요약하면 <span style="background-color: #fff59d"><strong>"그래프를 잘 그리는 것"에서 "그래프가 스스로 개선되는 것"으로</strong></span> 넘어가야 한다는 이야기입니다.

자료는 <span style="background-color: #fff59d"><strong>github.com/DEEP-JLU/Awesome-Graph-Engineering</strong></span>에 논문·데이터·프로젝트가 모여 있습니다. 멀티에이전트 시스템 설계를 정리할 기준점이 필요하다면 이 서베이의 세 기둥 프레임부터 가져가면 됩니다.

원문: Graph Engineering in the Era of LLM Agents (arXiv 2608.21156, <span style="background-color: #fff59d"><strong>2026-08-21 제출</strong></span>)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
