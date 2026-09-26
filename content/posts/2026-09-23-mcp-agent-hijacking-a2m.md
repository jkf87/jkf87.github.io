---
title: "LLM 에이전트가 악성 MCP 도구를 골라버리는 이유: A2M 논문 정리 (arXiv 2609.26761)"
date: 2026-09-23
description: MCP 도구 설명문만 조작해 에이전트가 악성 도구를 부르게 만들고, 반환값으로 추론까지 조종하는 A2M 공격을 정리했습니다. 악성 도구 호출률 93.6%, 토큰 비용 32.4배 증가 결과입니다.
tags:
  - LLM 에이전트
  - MCP
  - 보안
  - tool-use
  - 벤치마크
draft: true
refactor_hub: agent-safety-02
refactor_status: merged
merged_into: posts/llm-agent-security-defense-guide-2026
---

## 결론 먼저

어느 날 에이전트가 사용자의 이메일과 액세스 토큰을 모르는 서드파티 도구에 넘기고 있었다면? 사용자 프롬프트에는 문제가 없었고, 시스템 프롬프트도 오염되지 않았습니다. 공격자가 한 일은 <span style="background-color: #fff59d"><strong>MCP 레지스트리에 도구 하나를 등록한 것뿐</strong></span>입니다.

이 시나리오를 실험으로 보여준 논문이 A2M: Trace-Optimized Agent Hijacking in the MCP Ecosystem(arXiv 2609.26761)입니다. 결과부터 요약하면:

- GLM-4.6 기준 <span style="background-color: #fff59d"><strong>악성 도구 호출률(MTIR) 평균 93.6%</strong></span>
- C-DoS 시나리오에서 <span style="background-color: #fff59d"><strong>토큰 비용 32.4배 증가</strong></span>
- IE/EIC/RD 평균 <span style="background-color: #fff59d"><strong>공격 성공률(ASR) 74.4%</strong></span>
- 다른 모델로 옮겨도(재최적화 없이) <span style="background-color: #fff59d"><strong>평균 MTIR 63.6% 유지</strong></span>. 도구 선택 취약점은 모델을 바꿔도 잘 안 막힙니다.
- 전이 공격에서 ASR은 24.5%로 떨어집니다. <span style="background-color: #fff59d"><strong>"부르게 만드는 것"과 "끝까지 조종하는 것"은 다른 취약점</strong></span>이라는 게 이 논문의 핵심 구분입니다.

논문: [arXiv:2609.26761](https://arxiv.org/abs/2609.26761), 코드: [github.com/Lilaizhen/A2M](https://github.com/Lilaizhen/A2M). 수치는 v1(2026-09-22 제출) 기준이고, 정리 시점은 2026-09-23입니다.

## 핵심 구조 한눈에 보기

| 항목 | 내용 |
| --- | --- |
| 프레임워크 | A2M (Attraction-to-Manipulation), 2단계 블랙박스 최적화 |
| 1단계 | 도구 이름/설명 최적화로 선택 확률 상승 |
| 2단계 | 실행 트레이스 피드백으로 반환 페이로드 정제 |
| 벤치마크 | LiveMCPBench (95 태스크, 70 서버, 527 도구) |
| 평가 모델 | GLM-4.6, Qwen3-Max, DeepSeek-V3.1, Kimi-K2-0905, GPT-5(medium) |
| 직접 공격 | MTIR 93.6%, C-DoS Cost× 32.4, ASR 74.4% |
| 전이 공격 | MTIR 63.6%, Cost× 2.7, ASR 24.5% |

![Figure 1: 정상 MCP 상호작용과 공격형 상호작용 비교](/images/2026-09-23-mcp-agent-hijacking-a2m/fig-1-p2.png)

Figure 1에서 아래쪽 공격 흐름을 보면 `SmartPaperRetrieval`이라는 악성 도구가 반환값에 "user_email과 access_token을 제공하라"는 문구를 심어서, 에이전트가 사용자의 이메일과 토큰을 도구 인자로 넘기게 만듭니다. <span style="background-color: #fff59d"><strong>사용자 프롬프트도, 에이전트 시스템 프롬프트도 오염되지 않았는데 공격이 성립</strong></span>합니다.

## 두 개의 구멍: 선택과 반환

MCP 에이전트는 도구를 고를 때 이름(n)과 설명(d)이라는 의미적 메타데이터에 의존합니다. 공격자가 이 메타데이터를 통제하면 <span style="background-color: #fff59d"><strong>도구 선택 자체를 경쟁적으로 뺏어올 수 있습니다(Attraction)</strong></span>. 호출된 뒤에는 반환값이 "신뢰하는 환경 피드백"으로 들어갑니다. <span style="background-color: #fff59d"><strong>도구 출력은 일반 텍스트 입력과 달리 검증 레이어를 거의 거치지 않는다</strong></span>는 점이 두 번째 구멍입니다(Manipulation).

기존 연구(ToolHijacker, AMA, MPMA, ToolTweak)는 주로 선택 단계만 다뤘습니다. A2M은 <span style="background-color: #fff59d"><strong>선택 이후의 추론 조종까지 트레이스 기반으로 최적화해서 전체 공격 사슬을 완성</strong></span>한 점이 다릅니다.

![Figure 2: A2M 2단계 파이프라인](/images/2026-09-23-mcp-agent-hijacking-a2m/fig-2-p5.png)

## 공격은 어떻게 최적화되나

1단계에서는 Authority(권위), Urgency(긴급성), Comprehensiveness(포괄성), Resource Optimality(자원 최적), Security(보안) 다섯 가지 설득 전략으로 메타데이터 후보를 만들고, 몬테카를로 롤아웃(랭킹용 3회)으로 실제 선택률을 측정합니다. 실제 결과에서는 <span style="background-color: #fff59d"><strong>Comprehensiveness(31.6%)와 Resource Optimality(22.1%)가 선택된 메타데이터의 절반 가까이</strong></span>를 차지했습니다. "이 도구 하나면 끝"류의 포장이 잘 먹힌다는 뜻입니다.

2단계에서는 Analyzer가 실행 트레이스에서 공격 실패 지점을 진단하고, Optimizer가 그 피드백으로 페이로드를 다시 씁니다. <span style="background-color: #fff59d"><strong>트레이스 진단 기반의 방향성 있는 수정이라는 점</strong></span>이 효율의 원천입니다.

공격 목표는 4개 시나리오로 나뉩니다.

| 시나리오 | 내용 | 지표 |
| --- | --- | --- |
| C-DoS | 반복 추론 루프로 토큰 비용 부풀리기 | Cost× (출력 토큰 5배 가중) |
| IE (Information Exfiltration) | 민감 정보를 악성 도구 인자로 유출 | ASR |
| EIC (Environment Integrity Compromise) | config.json 변경 등 미승인 쓰기 | ASR |
| RD (Reasoning Derailment) | 잘못된 후속 도구 선택, 조기 종료 | ASR |

IE/EIC/RD는 DeepSeek-V3 저지(temperature 0)가 1~4점 루브릭으로 채점하며 <span style="background-color: #fff59d"><strong>4점(목표 완전 달성)만 공격 성공으로 간주</strong></span>합니다.

## 숫자로 보는 결과

![Table 1: 5개 모델 공격 성능](/images/2026-09-23-mcp-agent-hijacking-a2m/table-1-p8.png)

직접 공격(GLM-4.6 최적화·평가):

| 시나리오 | MTIR | 결과 |
| --- | --- | --- |
| C-DoS | 81.6% | Cost× 32.4 (베이스라인 최고 10.0의 3배 이상) |
| IE | 95.1% | ASR 65.9% |
| EIC | 97.6% | ASR 64.3% |
| RD | 100.0% | ASR 92.9% |

<span style="background-color: #fff59d"><strong>모든 지표에서 zero-shot, LLM-GA, AMA, MPMA 베이스라인을 상회</strong></span>했습니다. RD는 호출률 100%, 성공률 92.9%로 사실상 다 맞습니다.

전이 공격(재최적화 없음)에서는 평균 MTIR 63.6%, Cost× 2.7, ASR 24.5%. 특히 GPT-5는 <span style="background-color: #fff59d"><strong>악성 도구 호출률이 64.9~76.3%인데 IE/EIC 성공률은 0%</strong></span>였습니다. 안전 정렬이 강한 모델은 "선택"을 막는 게 아니라 "실행"을 막는 구조라는 뜻이고, GLM-4.6 실패 모드 분석에서도 IE/EIC의 최다 실패 원인은 페이로드 무시였습니다. 호출 통제와 반환값 신뢰 문제는 별도로 막아야 합니다.

절제 실험(18개 홀드아웃 태스크, C-DoS Cost× 평균):

| 구성 | Mean Cost× |
| --- | --- |
| A2M 전체 | 28.86× |
| 2단계 생성 제거 | 10.70× |
| 초기 전략 5종 제거 | 13.29× |
| 트레이스 최적화 제거 | 10.65× |

<span style="background-color: #fff59d"><strong>구성 요소 하나만 빼도 28.86×가 10~13×로 떨어집니다.</strong></span> 2단계 분리, 설득 전략 시드, 트레이스 최적화가 각각 기여합니다.

## 방어의 시사점

![Table 9: 탐지 실험](/images/2026-09-23-mcp-agent-hijacking-a2m/table-9-p18.png)

방어 평가에서는 퍼플렉시티 기반 탐지, 메타데이터 패러프레이징, 런타임 정보 흐름 제어가 완화 효과를 주지만 <span style="background-color: #fff59d"><strong>평가 세팅에서 잔여 위험이 남는다</strong></span>는 게 저자 결론입니다. 실무 체크리스트로 옮기면:

- 검증 안 된 MCP 서버를 에이전트 도구 풀에 그대로 노출하지 않기
- 도구 반환값을 <span style="background-color: #fff59d"><strong>불신 텍스트로 취급하는 검증 레이어</strong></span> 두기
- 파일 쓰기/시크릿 접근 도구는 런타임 격리와 권한 최소화
- 토큰 소비 급증(C-DoS 징후) 모니터링

코드와 벤치마크가 공개되어 있어 MCP 서버 검수 파이프라인의 레드팀 도구로 쓸 수 있습니다.

## 자주 묻는 질문

Q1. 공격자가 모델 내부를 볼 수 있어야 하나요?
아니요. 블랙박스 가정입니다. 모델 가중치·시스템 프롬프트·메모리 접근 없이, 로컬 대리 에이전트의 실행 트레이스에서 최적화 신호를 얻습니다.

Q2. 사용자 프롬프트에 인젝션이 필요한가요?
필요 없습니다. 사용자와 에이전트가 모두 정상이어도, 레지스트리에 등록된 악성 도구의 메타데이터와 반환값만으로 공격이 성립합니다.

Q3. GPT-5는 안전한가요?
부분적으로. 악성 도구 호출률은 64.9~76.3%로 여전히 높지만 IE/EIC 공격 성공률은 0%였습니다. 호출 단계와 조종 단계를 분리해 평가해야 하는 이유입니다.

Q4. 어떤 도구 설명이 위험한가요?
실험에서는 포괄성(Comprehensiveness, 31.6%)과 자원 최적(Resource Optimality, 22.1%) 전략으로 만든 메타데이터가 가장 많이 선택되었습니다. "이 도구 하나로 충분하다"류의 설명을 검수 때 주의 깊게 보세요.

Q5. 어떤 한계가 있나요?
시맨틱 레이어 공격만 다루고 네트워크/OS 수준 익스플로잇은 제외됐습니다. LiveMCPBench와 고정 ReAct 스택 기준 결과라 일반성에 제약이 있습니다.

## 더 실습해보고 싶은 분들께

MCP 도구를 붙여서 에이전트를 돌려보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고 자료

- [A2M: Trace-Optimized Agent Hijacking in the MCP Ecosystem (arXiv 2609.26761)](https://arxiv.org/abs/2609.26761)
- [github.com/Lilaizhen/A2M](https://github.com/Lilaizhen/A2M)
- [LiveMCPBench (arXiv 2508.01780)](https://arxiv.org/abs/2508.01780)
- 수치는 논문 v1(2026-09-22 제출) 기준, 정리 시점 2026-09-23입니다.
