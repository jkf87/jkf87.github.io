---
title: "EDGE와 KOPA-Bench — 한국 공공 API 위에서 오픈소스 에이전트를 27B급으로 끌어올린 레시피"
date: 2026-09-07
tags:
  - agent
  - tool-use
  - MCP
  - benchmark
  - RL
draft: false
description: "LG CNS가 실제 한국 공공 API 10개 플랫폼 위에 145개 과제 벤치마크 KOPA-Bench를 만들고, 실행 검증 기반 EDGE 데이터 합성 + GRPO로 9B 모델을 27B급 성능까지 끌어올린 논문을 정리했습니다."
---

## 결론 먼저

LG CNS가 공개한 논문(arXiv 2609.05395)은 두 가지를 함께 제시합니다. 하나는 실제 한국 공공 API 위에서 돌아가는 다단계 tool-calling 벤치마크 **KOPA-Bench**(145 과제)이고, 다른 하나는 라이브 실행으로 검증된 의존성 그래프를 순회해 학습 데이터를 만드는 **EDGE** 프레임워크입니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>Qwen3.5-9B를 EDGE 데이터로 GRPO 파인튜닝하자 KOPA-Bench pass@1이 0.33에서 0.43으로 오르며 같은 계열의 untuned 27B(0.4482)에 근접</strong></span>했습니다. 데이터를 잘 만드는 9B가 모델을 키우는 27B를 거의 따라잡은 셈입니다.

| 항목 | 내용 |
| --- | --- |
| 논문 | Multi-Step Tool-Calling over Korean Open Public APIs (arXiv 2609.05395v1) |
| 소속 | LG CNS (Dain Kim 외 5인, 공동 1저자) |
| 벤치마크 | KOPA-Bench: 실공공 API 10플랫폼, 6도메인, 145과제 |
| 데이터 합성 | EDGE: 실행 검증 의존성 그래프 순회, 1,781개 학습 트라젝토리 |
| 학습 | GRPO 파인튜닝 (Qwen3.5-4B / 9B) |
| 핵심 수치 | 9B pass@1 0.3275 → 0.4310 (+10pp), untuned 27B 0.4482에 근접 |
| 코드 | github.com/dneirfi/EDGE-KOPA |

## 벤치마크가 필요했던 이유

데이터 주권 규제 때문에 공공기관은 오픈소스 모델을 온프레미스로 돌려야 합니다. 근데 기존 tool-calling 벤치마크는 <span style="background-color: #fff59d"><strong>에뮬레이트된 서비스나 LLM 사용자 시뮬레이터 기반</strong></span>이라 실제 API 응답의 지저분함을 담지 못합니다.

KOPA-Bench는 세 조건으로 플랫폼을 골랐습니다. 교통/금융/교육/법/정치/행정 6개 도메인 커버리지, 체인형 다단계 추론이 가능한 API 상호연결성, KOGL 라이선스 허용. 규모는 이렇습니다.

| 규모 항목 | 수치 |
| --- | --- |
| 플랫폼 | 10개 |
| 과제 | 145개 |
| 도구(함수) | 2,318개 |
| 평균 tool-call 수 | 과제당 5회 (최대 14회) |
| 병렬 실행 포함 과제 | 59% |

- <span style="background-color: #fff59d"><strong>벤치마크는 145 과제, 도구 2,318개, 과제당 평균 5회 tool-call</strong></span>로 구성됩니다. 각 플랫폼은 공식 문서를 파싱해 MCP 서버로 구현했습니다. 인증, 세션, 재시도 로직을 서버가 흡수하고 타입 있는 함수 시그니처를 표준 function-calling 인터페이스로 노출하는 구조구요.

한국 공공 API 특유의 함정도 과제에 그대로 들어 있습니다. "2021년 제주 중학교 특수교육 학생 수"를 묻는 과제에서 에이전트는 먼저 <span style="background-color: #fff59d"><strong>`get_education_api_key()`로 API 키를 발급받은 뒤 그 키를 다음 호출에 넘겨야 합니다</strong></span>. 키를 건너뛰면 Invalid API-key 에러가 돌아옵니다. 법령 코드, 기관 코드 같은 코드-룩업을 먼저 해야 하는 과제가 많다는 것도 특징입니다.

![Figure 1](/images/2026-09-07-edge-kopa-bench-korean-public-api/fig1-trajectory-comparison.png)

## 평가 설계: 세 개의 축

논문은 RESPONSE, ENVIRONMENT, ACTION 세 축으로 평가합니다. RESPONSE는 최종 답변, ENVIRONMENT는 호출 후 서버 상태, ACTION은 실행된 tool-call 시퀀스입니다. ACTION 하나로 평가하면 정답 액션을 포함했는데 시스템 상태가 틀어지는 경우, 반대로 우회 경로로 정답 상태에 도달하는 경우가 섞여서 구분이 안 됩니다. 그래서 결과(RESPONSE/ENVIRONMENT)와 과정(ACTION)을 나눠 측정했습니다.

과제 검증도 이중으로 했습니다. 저자 아닌 전문가 감사에서 <span style="background-color: #fff59d"><strong>7개 과제(4.8%) 오류</strong></span>를 잡았고, 골든 트라젝토리 실행 결과를 Claude Sonnet 4.6에 줘서 타깃 답변과 비교하는 실행 검증에서 <span style="background-color: #fff59d"><strong>첫 시도에 80% 통과</strong></span>, 전 과제가 통과할 때까지 수정을 반복했습니다.

## EDGE: 실행으로 검증된 그래프를 순회한다

EDGE(Execution-grounded Dynamic Graph for tool-calling data synthEsis)는 두 페이즈로 됩니다.

Phase A는 도구 간 의존성 그래프를 만듭니다. 어떤 도구의 출력이 다른 도구의 입력으로 흘러갈 수 있는지 후보 엣지를 세우고, 실제 라이브 API를 호출해보고 성공한 엣지만 남깁니다. <span style="background-color: #fff59d"><strong>문서상 가능해 보이는데 실제로는 실패하는 연결은 그래프에서 잘려나갑니다</strong></span>.

![Figure 2](/images/2026-09-07-edge-kopa-bench-korean-public-api/fig2-edge-overview.png)

Phase B는 이 검증된 그래프 위에서 트라젝토리를 조립합니다. 각 분기점을 응답 카디널리티(일대일/일대다)로 타입을 붙이고, 그래프를 순회하면서 각 트라젝토리에 한국어 질의와 정답을 생성합니다. 이렇게 1,781개 학습 데이터를 만들었습니다.

![Figure 6](/images/2026-09-07-edge-kopa-bench-korean-public-api/fig6-edge-pruning.png)

핵심 통찰은 <span style="background-color: #fff59d"><strong>프루닝이 문서 말고 실행 결과에 지배된다</strong></span>는 것입니다(Figure 7). 논문 표현을 빌리면 execution success rises as unreliable edges are pruned, 신뢰할 수 없는 엣지가 잘릴수록 실행 성공률이 올라갑니다.

![Figure 7](/images/2026-09-07-edge-kopa-bench-korean-public-api/fig7-pruning-execution.png)

## 결과: 9B가 27B를 거의 따라잡다

GRPO로 Qwen3.5-4B/9B를 학습한 결과는 표로 정리됩니다.

| 모델 | KOPA pass@1 | KOPA pass@4 | BFCL Multi |
| --- | --- | --- | --- |
| Qwen3.5-27B (untuned) | 0.4482 | 0.5655 | 89.65 |
| Qwen3.5-9B (base) | 0.3275 | 0.4690 | 82.40 |
| Qwen3.5-9B (EDGE+GRPO) | 0.4310 | 0.5517 | 87.65 |
| Qwen3.5-4B (base→EDGE) | 0.18 → 0.31 | — | +4.04pp |

주목할 점 두 가지를 짚습니다. 개선이 in-distribution에만 국한되지 않습니다. 영어 범용 tool-calling 벤치마크 BFCL에서도 <span style="background-color: #fff59d"><strong>4B +4.04pp, 9B +5.87pp 올랐습니다</strong></span>. 그리고 <span style="background-color: #fff59d"><strong>9B의 pass@4(0.5517)는 27B(0.5655)와 사실상 동급</strong></span>입니다.

![Figure 4](/images/2026-09-07-edge-kopa-bench-korean-public-api/fig4-execution-refinement.png)

## 내 해석: 무엇을 베껴야 하나

원문 근거와 구분해서 제 해석을 적습니다.

이 논문의 진짜 자산은 벤치마크보다 데이터 합성 파이프라인 쪽이라고 봅니다. <span style="background-color: #fff59d"><strong>"실제로 호출해보고 성공한 엣지만 남긴다"는 규칙은 도구 생태계에 상관없이 적용할 수 있는 일반 레시피</strong></span>입니다. 사내 내부 API, MCP 서버 묶음에도 그대로 옮길 수 있습니다.

평가의 3축 분리(ACTION/RESPONSE/ENVIRONMENT)도 베낄 만한 설계입니다. tool-call 시퀀스 정확도와 결과 상태 정확도를 나눠 보지 않으면 우회 성공과 표면적 성공이 섞입니다.

2,318개 도구라는 규모가 주는 시사지점도 있습니다. 공공 API 문서를 파싱해 MCP로 래핑하는 작업이 논문 저자들에겐 수작업이었을 텐데, 이걸 자동화하면 도구 인벤토리 구축 비용이 크게 내려갑니다.

## 자주 묻는 질문

- **KOPA-Bench는 어디서 쓸 수 있나요?** 코드와 데이터가 github.com/dneirfi/EDGE-KOPA에 공개되어 있습니다.
- **EDGE 데이터 합성의 핵심 규칙이 뭔가요?** <span style="background-color: #fff59d"><strong>도구 간 의존성 엣지를 문서 기준 말고 실제 라이브 호출 성공 여부로 유지한다</strong></span>는 것입니다. 실행 실패 엣지는 그래프에서 제거됩니다.
- **9B가 정말 27B를 이겼나요?** <span style="background-color: #fff59d"><strong>pass@1로는 근접(0.4310 vs 0.4482), pass@4로는 사실상 동급(0.5517 vs 0.5655)</strong></span>입니다. 같은 계열 모델 내 비교라는 조건이 붙습니다.
- **한국 공공 API만 대상인가요?** 벤치마크는 그렇고, EDGE 방법 자체는 도구 의존성 그래프를 만들 수 있는 어떤 API 묶음에도 적용 가능합니다. BFCL(영어 범용)에서도 개선이 확인되었습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 출처

- arXiv: [Multi-Step Tool-Calling over Korean Open Public APIs: A Benchmark and a Data-Synthesis Recipe](https://arxiv.org/abs/2609.05395) (2609.05395v1)
- 코드/데이터: [github.com/dneirfi/EDGE-KOPA](https://github.com/dneirfi/EDGE-KOPA)
- 본문 수치는 논문 v1 기준. 기준일: 2026-09-07.
