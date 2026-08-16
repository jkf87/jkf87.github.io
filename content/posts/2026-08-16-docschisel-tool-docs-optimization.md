---
title: "DocsChisel: 에이전트 도구 문서를 실패 트레이스로 다듬으면 과제 성공률이 95.89% 오릅니다"
date: 2026-08-16
tags:
  - agent
  - tool-use
  - LLM-agent
  - documentation
  - WorkBench
  - API-Bank
  - harness
  - loop
  - context-engineering
source: arxiv
source_url: https://arxiv.org/abs/2608.10037
authors:
  - conanssam
draft: false
---

![DocsChisel 접근 개요](/images/2026-08-16-docschisel-tool-docs-optimization/fig2-approach-overview.png)

arXiv:2608.10037 (2026-08-10, DocsChisel) 정리했습니다. 핵심은 이겁니다. 도구를 더 잘 쓰게 모델을 바꾸는 대신, <span style="background-color: #fff59d"><strong>도구 문서(tool documentation) 자체를 최적화 대상으로 보고 실패 트레이스로 다듬었다</strong></span>는 것.

원본 문서 대비 과제 성공률(TS)이 <span style="background-color: #fff59d"><strong>95.89% 상승</strong></span>, 기존 최고 기법 대비 평균 <span style="background-color: #fff59d"><strong>75.15% 상승</strong></span>입니다.

## 도구 문서가 에이전트 성능을 좌우합니다

LLM 에이전트는 브라우저, 코드 인터프리터, 파일 시스템 같은 외부 도구를 씁니다. 이때 도구 선택과 호출 규격은 컨텍스트에 들어간 문서에서 나옵니다. 문서에 애매하거나 빠진 정보가 있으면 잘못된 호출이 나오고, 뒤에 오는 스텝까지 전부 실패합니다.

근데 기존 연구는 대부분 도구 만들기, 검색, 호출, 평가에만 신경 썼고 문서는 "고정 입력"으로 뒀어요. EasyTool은 문서를 템플릿으로 압축하고, DRAFT는 도구 실행 피드백으로 다듬는데, 둘 다 기존 필드 안에서의 수정이라 필드 구성 자체는 그대로예요.

이 논문은 질문을 바꿨습니다. 도구 문서에 어떤 정보 필드가 있고, 그 필드들이 에이전트 설정마다 어떤 효과를 내는지 먼저 측정했습니다.

## 14개 데이터셋, 24,955개 도구 문서 조사

WorkBench, API-Bank, ToolLLM, SWE-bench, τ-bench 등 14개 도구 사용 데이터셋에서 문서를 모아서 17개 정보 필드로 정리했습니다.

| 항목 | 수치 |
|---|---|
| 조사 데이터셋 | 14개 |
| 수집 도구 | 24,955개 |
| 식별된 정보 필드 | 17개 |
| 전 데이터셋 공통 필드 | 도구 이름, 기능 설명 2개뿐 |
| 사용 안내(UG)·호출 제약(IC) 제공 | 2/14 데이터셋만 |

실험 백본은 GPT-4o, GLM-5, Claude Haiku 4.5 세 개, 에이전트 패러다임은 ReAct(LangChain)과 Multi-Agent(AutoGen) 두 개입니다.

## 필드 효과는 도메인·모델·패러다임마다 다릅니다

RQ2에서 필드를 하나씩 넣거나 빼면서 WorkBench 5개 도메인에서 측정했습니다.

- 필드 하나를 넣거나 빼면 TS가 평균 <span style="background-color: #fff59d"><strong>6.34%p</strong></span>씩 움직입니다.
- 17개 필드 중 <span style="background-color: #fff59d"><strong>방향이 일관된 건 6개뿐</strong></span>입니다. 도구 이름(TN), 과제 도메인(TD), 반환 타입(RPT), 응답 템플릿(RT), 선택 인자 표시(POF)를 빼면 TS 하락, 호출 제약(IC)을 넣으면 TS 상승(0.75~11.25%p).
- TD를 빼면 <span style="background-color: #fff59d"><strong>3.75~13.75%p 하락</strong></span>.
- 백본마다 효과가 갈립니다. POF 제거는 GPT-4o·GLM-5에선 손해인데 Claude Haiku 4.5에선 오히려 7.5%p 이득이에요.
- ReAct → Multi-Agent로 바꾸면 기능 설명(FD), 인자 설명(IPD), 필수 인자 표시(PRF), RT처럼 효과가 뒤집히는 필드가 나옵니다.

정리하면 고정된 문서 규격은 모든 에이전트 설정에 안 통합니다. 그래서 문서를 설정에 맞게 적응적으로 최적화해야 한다는 동기가 나옵니다.

## DocsChisel 동작 방식: 진단 → 계획 → 생성 루프

![실패 트레이스 진단 프롬프트 템플릿](/images/2026-08-16-docschisel-tool-docs-optimization/fig4-diagnosis-prompt.png)

도메인별로 도구와 쿼리를 묶은 뒤, 도구마다 최대 5회 반복 루프를 돕습니다.

1. 실패 트레이스 진단: 원본 문서로 최적화 세트를 실행하고, 실패 트레이스에서 "문서 때문에 실패한 케이스"를 뽑습니다. 증거(e_f)와 행동 불일치(b_f), 의심 필드(H_f)를 기록해요.
2. 필드 조작 계획: 진단 기록을 Add/Remove/Refine 필드 연산으로 매핑합니다. 호출 조건이 없으면 IC 추가, 예시·코드가 오히려 방해면 UE/CI 제거, 비슷한 도구끼리 혼동이면 FD 정제.
3. 문서 생성: 원본 문서를 시맨틱 앵커로 두고 계획만 적용해서 새 문서를 만듭니다. 반복 재작성으로 원 의미가 드리프트하는 걸 막으려는 장치예요.
4. 회귀 인지 평가: 검증 세트에서 TS를 재측정하고, 원래 성공하던 쿼리가 새 문서로 깨지는 회귀 세트를 잡아냅니다. <span style="background-color: #fff59d"><strong>TS가 원본 이상일 때만 후보에 넣고</strong></span>, 최종은 검증 TS 최고(동률이면 가장 짧은 문서)를 선택합니다.

각 단계에는 진단·계획·생성 메모리가 도메인 단위로 쌓여서, 같은 도메인의 다른 도구 최적화에 재사용됩니다.

## 결과: 9개 도메인에서 최상위

![도메인·백본·패러다임별 효과성 비교](/images/2026-08-16-docschisel-tool-docs-optimization/fig8-effectiveness.png)

WorkBench + API-Bank에서 9개 도메인, 74개 도구, 2,072개 쿼리로 평가했습니다. 쿼리 분할은 최적화:검증:테스트 = 5:1:4 (1,036/207/829), 최적화 모델은 Claude Haiku 4.5, 반복 5회, 설정당 3×5=15회 반복 측정이에요.

- 원본 문서 대비 평균 <span style="background-color: #fff59d"><strong>TC +34.69%, TS +95.89%</strong></span>.
- 기법 대비 평균 <span style="background-color: #fff59d"><strong>TC +30.83%, TS +75.15%</strong></span>. 각 설정 최강 기법 대비로도 TC +26.23%, TS +46.11%.
- 9개 도메인 전체로는 원본 대비 <span style="background-color: #fff59d"><strong>TC +46.27%, TS +194.22%</strong></span>.
- 이메일, CRM, 건강관리, 스마트홈 도메인에서 특히 크게 올랐습니다.
- 반복 분포(IQR)도 EasyTool 대비 TC 41.56%, DRAFT 대비 52.93% 줄어서 안정적이에요.

EasyTool은 같은 템플릿을 전 설정에 적용해서 특정 에이전트에 필요한 필드를 지우거나 못 넣는 한계가 있고, DRAFT는 고립된 도구 실행 피드백이라 에이전트 전체 실행 실패는 못 고칩니다. DocsChisel은 에이전트 실패 트레이스에서 출발해서 필드 단위로 고치니까 이 차이가 난다는 설명입니다.

## 비용: 도구당 12.65분

| 기법 | 문서 길이(토큰) | 최적화 토큰 비용 | 시간(분/도구) |
|---|---|---|---|
| 원본 | 152.58 | – | – |
| EasyTool | 82.68 | 237.81 | 0.23 |
| DRAFT | 189.56 | 4,784.39 | 2.26 |
| DocsChisel | 189.23 | 4,480.81 | 12.65 |

문서 길이는 원본보다 24.02% 길어지지만 DRAFT와 비슷해서 컨텍스트 부담은 유의미하게 크지 않고, 최적화 토큰은 DRAFT보다 6.35% 적게 써요. 시간은 도구당 12.65분으로 제일 길지만, <span style="background-color: #fff59d"><strong>한 번 해두면 재사용하는 오프라인 비용</strong></span>입니다.

## 최적화 모델과 메모리의 영향

![반복 횟수 민감도](/images/2026-08-16-docschisel-tool-docs-optimization/fig9-iterations.png)

최적화 모델을 바꿔서 재면(GPT-4o ReAct 에이전트 고정):

| 최적화 모델 | TC | TS |
|---|---|---|
| GPT-4o | 47.50% | 21.25% |
| GLM-5 | 73.75% | 35.63% |
| Claude Haiku 4.5 | 93.75% | 56.25% |

문서 최적화 품질은 <span style="background-color: #fff59d"><strong>최적화 모델의 지시 추종·추론 능력에 크게 좌우됩니다</strong></span>. 반복은 <span style="background-color: #fff59d"><strong>5회까지가 효율 고점</strong></span>이고(1회 대비 TS +80.00%), 그 뒤로는 수렴합니다.

메모리 절제 실험(NoMem)에서는 5회째에 TC -13.64%, <span style="background-color: #fff59d"><strong>TS -76.47%</strong></span>. 메모리 없으면 2회 차부터 성능이 정체돼요. 반복이 쌓일수록 도메인 경험이 재사용되는 구조라 메모리가 실질 엔진입니다.

## 내 해석: MCP 도구 설명 관리에 바로 적용됩니다

원문 근거와 제 해석을 나눠서 적으면 이렇습니다.

- MCP 서버나 에이전트 하네스에서 <span style="background-color: #fff59d"><strong>도구 설명(description)은 사실상 프롬프트</strong></span>예요. 이 논문 결과는 설명 필드 구성이 성공률을 수십 %p 단위로 움직인다는 측정인데, 그러면 도구가 많은 하네스에서 문서 최적화는 모델 교체와 별개로 남는 투자입니다.
- "필드 효과가 백본마다 다르다"는 결과가 실무적으로 제일 아픕니다. GPT-4o용으로 다듬은 설명을 GLM-5나 Haiku에 그대로 쓰면 최적이 아니에요. 도구 설명에 <span style="background-color: #fff59d"><strong>버전을 붙이고 백본별로 관리</strong></span>하는 게 정당해집니다.
- <span style="background-color: #fff59d"><strong>호출 제약(IC) 추가가 일관된 이득</strong></span>이었다는 점은 바로 챙길 만합니다. 제 도구 설명들에 "언제 쓰면 안 되는지" 한 줄씩 추가하는 것부터 시작할 수 있어요.
- 통계 처리도 단단합니다. Mann-Whitney U + Holm 보정으로 p_adj<0.05, 필드 분류 작업자 간 일치도 Cohen's κ=0.862.
- 한계도 명시돼 있어요. 과제 분해 오류, 확률적 추론, 불완전한 쿼리 같은 문서 밖 요인은 못 고칩니다. 그리고 도구당 12.65분의 오프라인 비용이 있으니 도구 수가 수천 개인 대형 레지스트리에는 우선순위가 필요합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 원문

- arXiv:2608.10037 — DocsChisel: Adaptive Tool Documentation Optimization Framework for LLM Agents
- 코드/자료: 익명 저장소 공개(논문 참조), 베이스라인 EasyTool·DRAFT 공식 아티팩트 사용
