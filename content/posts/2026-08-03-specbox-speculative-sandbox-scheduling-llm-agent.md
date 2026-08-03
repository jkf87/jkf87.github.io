---
title: "SpecBox: LLM 에이전트가 도구를 부르기도 전에 샌드박스를 켜는 시스템"
slug: 2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent
date: 2026-08-03
tags:
  - agent
  - MCP
  - sandbox
  - runtime
  - serving-system
  - LLM
  - harness
  - infrastructure
  - cold-start
source: arxiv
source_url: https://arxiv.org/abs/2607.23933
authors:
  - Yihui Zhang
  - Tianyu Wo
  - Jinghao Wang
  - Xiaoyang Sun
  - Menghao Zhang
  - Cangzhou Yuan
  - Li Li
  - Chunming Hu
  - Albert Y. Zomaya
  - Renyu Yang
affiliation: Beihang University, University of Leeds, University of Sydney
---

**LLM 에이전트가 "도구를 쓰겠다"고 결정하는 순간, 샌드박스(격리된 실행 환경)를 띄우느라 수 초가 걸린다.** 그동안 GPU는 아무것도 하지 않고 기다린다. SpecBox는 에이전트가 토큰을 생성하는 도중에 이미 다음 도구가 뭔지 예측해서 샌드박스를 미리 켜둔다. 결과적으로 P99 지연시간을 2.9배 줄이고, 상시 대기 방식 대비 메모리는 45.9% 아꼈다. MCP(Model Context Protocol) 기반 에이전트 시스템의 가장 성가신 병목 — 콜드 스타트 — 을 "추측적 사전 할당"으로 공략한 연구다.

![Figure 1: 순차 실행(vanilla)과 SpecBox의 사전 준비(overlapped) 실행 비교. 기존 방식은 LLM 추론이 끝난 후 샌드박스를 준비하지만, SpecBox는 추론과 정지를 겹친다.](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-1-p1.png)

## 문제: 에이전트 루프의 보이지 않는 병목

LLM 에이전트는 추론(reasoning) → 계획(planning) → 도구 호출(tool use)의 루프를 반복한다. 이 과정에서 코드 실행, 웹 자동화, 데이터베이스 조회 같은 작업은 보안과 격리를 위해 독립된 샌드박스 컨테이너에서 실행된다. Anthropic이 제안한 MCP(Model Context Protocol)는 이 도구 호출 인터페이스를 표준화했다.

문제는 이 샌드박스를 "요청이 들어왔을 때 그제야 켜는" 구조(on-demand)에 있다. 컨테이너 이미지 다운로드, 파일 시스템 준비, 네임스페이스 설정, 런타임 핸드셰이크까지 수 초가 걸리고, 에이전트의 1회 실행 단계(step)에서 발생하는 지연 시간은 다음과 같이 분해된다:

> **T_step = T_context + T_generation + T_env_prep + T_data_io + T_sandbox_exec**

LLM 추론(T_context + T_generation)은 최적화되어 왔지만, T_env_prep(환경 준비)와 T_data_io(데이터 입출력)는 여전히 순차적으로 처리된다. AutoGen, LangGraph, AgentScope 같은 기존 프레임워크는 모두 "LLM이 도구 호출을 확정한 후에야" 샌드박스 준비를 시작하는 반응형(reactive) 모델을 쓴다.

![Figure 2: 실행 단계별 지연 시간 분해(왼쪽)와 32개 MCP 샌드박스의 콜드 스타트 지연(오른쪽). 대부분 2-4초지만 일부는 20초에 육박한다.](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-2-p3.png)

## 세 가지 관찰: 병목의 원인은 어디에?

SpecBox 연구팀은 에이전트 실행 트레이스를 분석해 세 가지 핵심 관찰을 도출했다.

**관찰 1 — 단계 내에서 준비를 미리 시작할 수 있다.** LLM이 토큰을 스트리밍하는 도중에도, 부분적인 토큰만으로 어떤 도구를 호출할지 짐작할 수 있다. "search"나 "read" 같은 키워드가 나오는 순간, 아직 LLM이 완전한 도구 호출 문장을 만들기 전에 샌드박스 부팅을 시작할 수 있다.

**관찰 2 — 단계 간에도 준비를 앞당길 수 있다.** 에이전트 워크플로에는 강한 시간적 국소성(temporal locality)이 있다. 논문 검색 다음에는 문서 읽기가 오고, 데이터 분석 다음에는 차트 생성이 온다. 현재 단계가 실행되는 동안 다음 단계에 필요할 샌드박스를 미리 예열(pre-warm)할 수 있다.

**관찰 3 — 중복 실행과 불필요한 데이터 전송이 많다.** 다중 턴 에이전트에서는 같은 문서를 다시 조회하거나 동일한 분석을 반복하는 일이 빈번하다. 매번 샌드박스를 새로 켜고 도구를 다시 실행하는 것은 낭비다.

## 설계: SpecBox의 세 가지 핵심 메커니즘

SpecBox는 이 세 관찰에 대응하는 세 가지 최적화를 제안한다.

### 1. 의도 인식 샌드박스 예열 (Intent-Aware Prewarming)

![Figure 4: 라우팅 정책별 트레이드오프. 키워드 라우터는 빠르지만 위양성이 많고, 시맨틱 라우터는 정확하지만 느리다. 합집합(Union) 정책이 둘의 장점을 취한다.](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-4-p4.png)

LLM이 토큰을 생성하는 도중, 두 개의 비동기 라우터가 동시에 스트림을 감시한다:

- **키워드 라우터 (Keyword Router):** 도구별 키워드 프로파일과 스트리밍 토큰을 매칭한다. 임계값 γ=2, 즉 도구 특화 키워드 2개 이상이 매치되면 후보로 선정한다. 마이크로초 단위로 반응하지만, "read" 같은 범용 동사가 여러 도구에 공통이라 위양성(false positive)이 발생할 수 있다.
- **시맨틱 라우터 (Semantic Router):** TF-IDF 기반 희소 검출(sparse retrieval)로 현재 문맥과 도구 의도 표현을 비교한다. 정확하지만 더 많은 토큰이 누적된 후에야 판단할 수 있어 반응이 느리다.
- **합집합 조립 (Union Assembly):** 두 라우터의 후보 집합 중 **하나라도** 히트하면 즉시 예열을 시작한다. 교집합이 아닌 합집합을 쓰는 이유는, 교집합은 정확도는 높지만 시맨틱 라우터를 기다려야 해서 예열 시간이 줄어들기 때문이다.

실험 결과, 합집합 정책은 평균 대기 시간 124.45ms, 콜드 스타트 비율 5.0%를 기록했다. 반면 교집합은 콜드 스타트를 0%로 없앴지만 대기 시간이 393.52ms로 3.16배 느렸다.

### 2. 확률적 샌드박스 프리페칭 (Stochastic Prefetching)

![Figure 6: 1차 마르코프 모델 기반 샌드박스 상태 전이 그래프(왼쪽)와 예산 제약 하의 프리페칭 세션 예시(오른쪽).](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-6-p5.png)

단계 내 예열만으로는 무거운 샌드박스의 부팅 시간을 다 가릴 수 없다. SpecBox는 샌드박스 의존성 그래프(Sandbox Dependency Graph, SDG) 위에 1차 마르코프 모델을 구축한다.

과거 실행 트레이스에서 단계 간 전이 빈도를 세고, 라플라스 평활화를 적용해 다음 샌드박스의 출현 확률을 추정한다:

> **P(v_j | v_i) = (C_{i,j} + α) / Σ_k(C_{i,k} + α)**

현재 단계 v_i에서 확률 임계값 τ=0.6을 넘는 후보 중 콜드 스타트 비용이 λ=5 이상인 것만, 그리고 단계당 예산 B=1개만 프리페치한다. 단순하지만 효과적이다 — 현재 샌드박스가 실행 중일 때 백그라운드에서 다음 샌드박스를 미리 켜두는 것이다.

실험에서 프리페칭을 켠 SpecBox-Proactive는 10턴 기준 평균 대기 시간 97.14ms, 끼워넣기 없는 SpecBox-Reactive는 583.26ms로 6.0배 차이가 났다.

### 3. 재사용 인식 데이터 전송 (Reuse-Aware Transmission)

![Figure 7: 재사용 인식 데이터 전송. 시맨틱 캐시가 히트하면 이전 결과를 반환하고, 미스면 샌드박스를 실행한 뒤 대역 외(out-of-band) 데이터 경로로 결과를 전달한다.](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-7-p6.png)

세 번째 최적화는 두 가지로 구성된다:

- **시맨틱 캐시 (Semantic Cache):** 도구 식별자가 같고 정규화된 호출 표현의 의미 유사도가 τ_c=0.8 이상이면 이전 결과를 재사용한다. 단순 인자 매칭보다 넓은 재사용 범위를 확보하면서도, 도구가 다르거나 부작용이 있는 호출은 안전하게 걸러낸다. 캐시 적중률 37.4%, 평균 대기 시간 2.91배 단축.
- **대역 외 데이터 전송 (Out-of-Band Transport):** JSON-RPC 기본 경로는 제어 신호만 남기고, 큰 결과물(이미지, 파일, 구조화된 데이터)은 메모리 맵핑 공유 메모리로 전달한다. 1GB 페이로드에서 JSON-RPC는 1873ms, 대역 외 전송은 5.97ms — **313배 차이**. 제어 인터페이스는 기존 MCP 도구와 호환성을 유지한다.

## 시스템 아키텍처

![Figure 8: SpecBox 전체 아키텍처. 제어 평면(컨트롤러, 라우터, 매니저)과 데이터 평면(공유 메모리)이 분리되어 있다.](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-8-p7.png)

SpecBox는 에이전트 엔진과 외부 샌드박스 사이에 위치하는 런타임 미들웨어다. 제어 평면에서 컨트롤러가 토큰 스트림을 구독하고, 두 라우터가 비동기로 후보를 생성하며, 합집합 결과를 샌드박스 매니저가 중복 제거 후 컨테이너를 시작한다. 백그라운드 프리페치 워커는 SDG를 업데이트하며 다음 단계 예열을 수행한다. 데이터 평면에서는 공유 메모리 백플레인이 큰 결과물을 zero-copy로 전달한다.

AgentScope 프레임워크에 통합되어 구현되었으며, 프레임워크에 종속되지 않는 구조다.

## 평가: 실제로 얼마나 빨라지는가?

### 대규모 동시 실행 환경

200개의 다중 턴 에이전트 트레이스(MCPBench 기반, 32개 MCP 호환 도구 서버 — Playwright, Jupyter, Neo4j 등)로 평가했다. Qwen3.5-Max 모델을 사용했고, Docker 컨테이너로 샌드박스를 격리했다.

![Figure 9: 다중 턴 에이전트 세션(5-8단계)에서의 누적 샌드박스 프로비저닝 지연 시간 분포. On-demand는 긴 꼬리를 보이지만 SpecBox는 1초 이내에 집중된다.](/images/2026-08-03-specbox-speculative-sandbox-scheduling-llm-agent/fig-9-p8.png)

**핵심 결과:**

| 지표 | On-demand | Reserved | SpecBox |
|------|-----------|----------|---------|
| P99 지연시간 (QPS=20) | 257.2초 | ~85초 | **88.7초** |
| 누적 프로비저닝 지연 | 높음 (꼬리 길어짐) | 최저 | **4.53배 단축** |
| 피크 메모리 | 24.3–40.4 GiB | 80.6 GiB | **49.4 GiB** |
| 피크 CPU | ~15.8 코어 | ~15.9 코어 | **~12.2 코어** |

SpecBox는 Reserved(상시 대기)의 성능에 근접하면서, 메모리는 45.9% 적게 쓴다. On-demand 대비 P99 지연시간은 2.9배, 누적 프로비저닝 지연은 4.53배 개선했다. CPU 사용량도 22.8–23.3% 줄었다.

### 컴포넌트별 기여도

- **키워드 라우터 임계값 γ=2:** 평균 대기 323ms, 라우팅 적중률 95%. γ=1은 위양성이 너무 많고 γ=3은 너무 늦다.
- **시맨틱 라우터:** TF-IDF 희소 검출이 신경망 인코더(all-MiniLM-L6-v2)와 정확도는 비슷하지만 3.7배 빠르다.
- **확률적 프리페칭:** 10턴 기준 대기 시간 6.0배, 턴당 콜드 스타트 0.24–0.83건(Reactive는 최대 2.90건).
- **시맨틱 캐시:** 적중률 37.4%, 대기 시간 2.91배 단축. exact-match보다 넓은 재사용 범위.
- **대역 외 전송:** 1GB에서 313.55배 빠름. 페이로드 크기에 거의 무감각(O(1))해진다.

## 의의와 한계

SpecBox의 핵심 통찰은 **"에이전트 런프의 병목은 LLM 추론이 아니라 환경 준비에 있다"**는 것이다. 그리고 그 병목을 LLM 토큰 생성 시간 동안 "숨기는" 것이 가능하다.

**의의:**
- MCP 생태계의 콜드 스타트 문제를 시스템 수준에서 해결했다. 도구 수정이나 프로토콜 변경 없이 런타임만 교체하면 된다.
- 추측적 실행(speculative execution)을 에이전트 런타임에 적용한 체계적 시도다. CPU 파이프라인의 분기 예측과 유사한 개념을 샌드박스 스케줄링으로 옮겼다.
- Agentic RL(VERL, Slime 등)의 롤아웃 환경 준비에도 적용 가능하다고 논의한다.

**한계:**
- 1차 마르코프 모델은 긴 호라이즌 워크플로에서 예측 정확도가 떨어진다. 다만 2계층 구조(단계 내 예열이 단계 간 프리페칭의 실패를 커버)로 안전망을 제공한다.
- 공유 메모리 전송은 같은 호스트 내로 제한된다. 분산 클러스터 확장을 위해서는 RDMA 통합이 필요하다.
- 부작용이 있는 도구 호출에는 캐시 재사의 안전성이 추가 검증이 필요하다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 루프 엔지니어링은 SpecBox처럼 "도구 호출 전에 환경을 준비하는" 최적화부터, 에이전트의 추론 루프 자체를 설계하는 것까지 폭넓은 영역입니다. 직접 에이전트를 만들어보고 싶다면 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스를 실전에서 활용하는 50가지 패턴
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 최적화의 기초부터 실습까지

> **Paper:** [SpecBox: Speculative Sandbox Scheduling for Efficient LLM Agent Serving (arXiv:2607.23933)](https://arxiv.org/abs/2607.23933)
