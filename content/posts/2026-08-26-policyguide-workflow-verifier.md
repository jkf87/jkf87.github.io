---
title: "PolicyGuide — 정책을 워크플로 그래프로 컴파일해서 에이전트를 외부에서 검증하기"
date: 2026-08-26T19:05:00+09:00
draft: false
tags: [llm-agent, policy-compliance, runtime-guardrail, tau2-bench, verifier]
---

## 왜 절차 누락이 문제인가

고객 서비스 에이전트를 붙잡고 운영해 본 사람들은 안다. 정책 위반은 대부분 드라마틱한 해킹이 아니라, <span style="background-color: #fff59d"><strong>신원 확인 한 번을 건너뛰고 승인 버튼을 누르는 아주 사소한 순간</strong></span>에 일어난다. PolicyGuide(arXiv:2608.19861) 연구팀이 실제 정책 문서를 뜯어봤더니 <span style="background-color: #fff59d"><strong>절차 요건이 airline 67.4%, retail 약 100%, telecom 98.0%에 등장</strong></span>한다. 즉, 문제의 본질은 "금지된 행동"보다 "빠뜨린 절차"인 것이다.

## 지금까지의 두 갈래, 그리고 빈 구멍

지금까지의 접근은 두 갈래였다. 하나는 액션 가드 방식으로 <span style="background-color: #fff59d"><strong>위험한 툴 호출을 가로채서 검사하는 방법</strong></span>, 다른 하나는 <span style="background-color: #fff59d"><strong>SOP를 상태머신으로 만들어 절차를 강제하는 방법</strong></span>. 근데 전자는 <span style="background-color: #fff59d"><strong>마지막 mutating 호출만 보니 건너뛴 절차를 늦게 발견</strong></span>하고, 후자는 절차 완수용이라 정책 위반을 막는 세이프가드로 설계되지 않았다.

PolicyGuide는 이 빈 구멍을 메운다. <span style="background-color: #fff59d"><strong>정책 문서를 워크플로 그래프로 컴파일</strong></span>하고, <span style="background-color: #fff59d"><strong>사용자 턴 경계마다 외부 verifier가 그래프 위치를 추적</strong></span>한다. 워크플로가 끝나기 전에 에이전트가 mutating 호출을 시도하면, 런타임이 미충족 단계의 수정 지시를 돌려준다. <span style="background-color: #fff59d"><strong>필수 단계가 채워진 뒤에야 mutation을 권장하는 구조</strong></span>다.

![](/images/2026-08-26-policyguide-workflow-verifier/fig-2-p2.png)

## 숫자로 보는 임팩트

결과는 명확하다. τ²-bench 세 도메인에서 <span style="background-color: #fff59d"><strong>mean Pass⁴를 0.42에서 0.62로 끌어올렸다</strong></span>. 특히 <span style="background-color: #fff59d"><strong>telecom에서는 0.19에서 0.61로, 세 배 가까운 도약</strong></span>이다. telecom이 이렇게 크게 움직인 이유는 <span style="background-color: #fff59d"><strong>diagnose → instruct → verify 같은 긴 순서 체인</strong></span> 때문이다. 중간에 에이전트 쪽 mutation이 아예 없을 수도 있어서, 액션 가드가 개입할 지점 자체가 없었던 도메인이다.

가장 흥미로운 건 절제 실험이다. 같은 그래프를 에이전트에게만 주고 외부 verifier를 제거한 PolicyGuide-Self는 <span style="background-color: #fff59d"><strong>어느 도메인에서도 ReAct을 못 넘는다</strong></span>. 다시 말해 그래프를 "알려주는 것"만으로는 부족하고, <span style="background-color: #fff59d"><strong>상태를 코드에 영속해서 외부에서 추적해야 효과</strong></span>가 있다는 뜻이다. 그래프 대신 원문 정책 텍스트를 준 매칭 비교에서도 <span style="background-color: #fff59d"><strong>telecom에서 0.325 차이</strong></span>가 났다.

![](/images/2026-08-26-policyguide-workflow-verifier/table-2-p7.png)

![](/images/2026-08-26-policyguide-workflow-verifier/table-3-p8.png)

매칭 비교(Table 3, telecom 40 태스크)에서는 ReAct 0.250, PolicyGuard 0.325, FlowAgent 0.350, PolicyGuide 0.675. <span style="background-color: #fff59d"><strong>외부 그래프 verifier가 0.675로 최상위</strong></span>다.

GPT 5.4가 저작한 워크플로를 <span style="background-color: #fff59d"><strong>Claude Sonnet 4.6과 Gemini 2.5 Pro에 그대로 붙여도 성능이 올라간다</strong></span>. verifier와 actor가 분리된 구조의 실용적 이점이다.

![](/images/2026-08-26-policyguide-workflow-verifier/table-4-p7.png)

CRAFT 레드팀 공격에 대해서도 <span style="background-color: #fff59d"><strong>관측된 최저 공격 성공률</strong></span>을 기록했다.

![](/images/2026-08-26-policyguide-workflow-verifier/fig-6-p8.png)

## 내 해석

이 연구가 주는 교훈은 단순하다. <span style="background-color: #fff59d"><strong>모델이 지키지 못하는 건 모델 밖으로 꺼내면 된다</strong></span>. 절차 상태를 프롬프트나 컨텍스트에 다 넣으면 긴 대화에서 놓치게 되어 있다. 이걸 코드가 들고 있게 만드는 아키텍처 결정이 PolicyGuide의 본질이다. 에이전트 하네스를 만드는 사람이라면 바로 적용할 수 있는 원칙이다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- PolicyGuide: From Guarding One Action to Guiding the Whole Workflow for Policy-Compliant LLM Agents — https://arxiv.org/abs/2608.19861
