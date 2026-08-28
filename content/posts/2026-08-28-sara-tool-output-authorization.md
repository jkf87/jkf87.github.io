---
title: "SARA: 도구 증강 LLM 에이전트의 행동 유도와 실행 인가의 분리"
date: 2026-08-28
tags: [agent, security, tool-use, llm, prompt-injection, runtime-authorization]
draft: false
description: "arXiv 2608.27146 논문 요약. SARA의 인가 계약, Action Probe, 감사된 실행 이력, No-History-Promotion과 AgentDojo/AgentDyn 평가 결과를 정리합니다."
---

## 결론 먼저

SARA(Separating Action induction from Runtime Authorization)는 도구 증강 LLM 에이전트에서 신뢰할 수 없는 Observation이 야기하는 무단 실행 문제를, <span style="background-color: #fff59d"><strong>행동 유도(action induction)와 실행 인가(execution authorization)의 역할 분리로 해결하는 런타임 방어 프레임워크입니다</strong></span>(arXiv:2608.27146, 2026-08-27 제출, 중국과학원 정보공학연구원).

주요 결과(논문 Table 1, 기준일 2026-08-27):

| 평가 설정 | 백본 | Agent-only ASR | SARA ASR |
|---|---|---|---|
| AgentDojo | GPT-4o-mini | 15.79% | 0.06% |
| AgentDyn | GPT-4o-mini | 16.07% | 0.17% |
| AgentDojo | Gemini-2.5-Flash-Lite | 33.28% | 0.62% |
| AgentDyn | Gemini-2.5-Flash-Lite | 30.91% | 0.63% |

<span style="background-color: #fff59d"><strong>4개 주요 설정에서 ASR이 0.63% 이하로 감소했으며</strong></span>, <span style="background-color: #fff59d"><strong>공격 하 작업 완수율(UA)은 Agent-only 기준 이상을 유지했습니다</strong></span>.

## 문제 정의

오픈엔디드 도구 과제는 신뢰할 수 없는 Observation(웹페이지, 이메일, 검색 결과, API 응답)으로부터 파일 식별자, 객체 ID 등 런타임 정보를 획득해 후속 호출을 구체화해야 합니다. 따라서 <span style="background-color: #fff59d"><strong>외부 콘텐츠의 영향을 차단하는 방식은 정상 작업 수행 능력을 함께 훼손합니다</strong></span>.

위협 모델 요약:

- 신뢰 대상: 사용자 요청 U, 도구 스키마 T, SARA 런타임, 실제 도구 실행기
- 불신 대상: 모든 도구 Observation의 자연어 내용과 구조화 필드
- 공격 목표: Observation에 삽입된 지시가 사용자가 인가하지 않은 실제 외부 효과(발송, 권한 변경, 거래 등)를 유발하는 것
- 단순 데이터 의존은 보호 대상에서 제외됨

## 방법

![](/images/2026-08-28-sara-tool-output-authorization/fig-1-p6.png)

### 구성 요소

1. 인가 계약 K = Contract(U). 각 항목은 (효과 유형 e_j, 허용 연산 operation_j, 대상 범위 scope_j, 정적 인자 Σ_j)로 표현됩니다. <span style="background-color: #fff59d"><strong>K는 과제 수준의 권한 상한이며 런타임 정보는 기존 권한을 구체화할 수만 있습니다</strong></span>.
2. 맥락 격리 Action Probe. (z_t, Q_t, M_t) = Probe(O_t, T)를 수행하며, <span style="background-color: #fff59d"><strong>z_t ∈ {STATIC, ACTIONABLE}로 행동 유도 의미 존재 여부를 판정합니다</strong></span>. Q_t는 도구 수준 액션 발자국, M_t는 (도구, 인자 경로, 정규화 값) 형태의 인자 근원 앵커입니다.
3. 지속 액션 오리진 집합 F_t와 트레이토리 상태 S_t ∈ {CLEAN, EXPOSED}. <span style="background-color: #fff59d"><strong>ACTIONABLE이 한 번이라도 관측되면 트레이토리는 EXPOSED로 전환되고</strong></span>, 액션 오리진은 후속 도구 단계를 건너 지속됩니다.
4. 감사된 실행 이력 H_t. <span style="background-color: #fff59d"><strong>허가되어 성공한 호출만 기록하며</strong></span>, 증거 능력은 <span style="background-color: #fff59d"><strong>DATA_ONLY(패스트패스, 인자 값으로만 사용)와 GOAL_BOUND(실행 체인·인자 바인딩 판정 참여)로 구분됩니다</strong></span>.
5. No-History-Promotion. 액션 유도 근원이 부여된 인자가 실행 이력에 재등장하더라도 <span style="background-color: #fff59d"><strong>그 재등장만으로 오리진이 소멸되거나 실행 권한으로 승격되지 않도록 합니다</strong></span>.

### 실행 경계 심사

후보 호출은 K, F_t, H_t를 근거로 <span style="background-color: #fff59d"><strong>목표 지지, 실행 체인 지지, 인자 수준 지지를 충족해야 실행됩니다</strong></span>. 부작용 없는 조회 호출은 Probe 발자국과 중복되는 경우에만 심사 대상이 되며 나머지는 패스트패스로 처리됩니다.

## 평가 결과

![](/images/2026-08-28-sara-tool-output-authorization/fig-3-p12.png)

보안–유틸리티 트레이드오프: Agent-only 대비 BU 감소폭은 <span style="background-color: #fff59d"><strong>SARA가 5.79/8.98/6.52/11.82%p, CaMeL은 31.52/39.71/15.94/29.55%p입니다</strong></span>. CaMeL은 <span style="background-color: #fff59d"><strong>ASR 0.11–0.28%로 더 낮지만</strong></span> 정상 작업 비용이 큽니다.

![](/images/2026-08-28-sara-tool-output-authorization/fig-2-p11.png)

백본 일반화(Llama3.1-8B, Llama3.3-70B, Qwen2.5-14B, Qwen3-32B): AgentDojo에서 Llama3.1-8B만 4.02%→1.64%, 나머지는 0.03% 이하입니다. AgentDyn에서도 Llama3.1-8B 잔여 1.75%를 제외하면 0.3% 미만입니다.

![](/images/2026-08-28-sara-tool-output-authorization/table-4-p13.png)

Table 4는 공격 과제에서의 런타임 추론 비용을 보고합니다.

기타 비교: Spotlighting은 UA 64.92%를 유지하지만 <span style="background-color: #fff59d"><strong>ASR 22.97%가 잔존합니다</strong></span>. Tool Filter와 IPIGuard는 ASR 1.83%/0.71%이나 UA가 45.29%/43.62%로 저하됩니다. AttriGuard는 UA 66.26%로 다소 높지만 ASR 1.17%입니다. ClawGuard는 잔여 <span style="background-color: #fff59d"><strong>ASR 4.29–7.00%</strong></span>, AIRGuard는 13.32–27.01%입니다.

## 한계

소형 백본(Llama3.1-8B)에서 잔여 ASR이 관측되어 <span style="background-color: #fff59d"><strong>Probe의 의미 판별이 모델 용량에 부분 의존합니다</strong></span>. SARA는 완전한 의미 판별 정확성을 가정하지 않으며, 오심사로 통과된 무단 호출은 방어 실패로 계산됩니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### SARA의 핵심 기여는 무엇입니까?
행동 유도 근원과 실행 권한을 분리하고, 실행 이력 재등장을 통한 권한 세탁(No-History-Promotion 위반)을 차단한 점입니다.

### 인젝션 탐지기와 다른 점은 무엇입니까?
악성 여부를 판정하지 않고 실행 경계에서 권한 근거를 심사합니다. 입력 차단에 따른 유틸리티 손실이 없습니다.

### 적용 전제 조건은 무엇입니까?
에이전트와 도구 실행기 사이에 런타임 배치가 필요하며, <span style="background-color: #fff59d"><strong>사용자 요청·도구 스키마·실행기의 무결성을 신뢰해야 합니다</strong></span>.
