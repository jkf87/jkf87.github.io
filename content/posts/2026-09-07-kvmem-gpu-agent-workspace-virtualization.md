---
title: "컨슈머 GPU에서 백만 토큰 에이전트 워크스페이스 돌리기 — KVMem 정리"
date: 2026-09-07
draft: false
tags:
  - agent
  - kv-cache
  - inference
  - systems
  - long-context
description: "KVMem은 에이전트 워크스페이스를 GPU-호스트메모리-NVMe에 페이징된 KV 상태로 가상화해서, 24GB 노트북 GPU에서 1M 토큰 워크스페이스를 약 50 tokens/s로 돌리는 시스템이다. 핵심 구조와 벤치마크 수치를 정리했다."
---

## 결론 먼저

KVMem(arXiv:2609.04852, Peking University)은 <span style="background-color: #fff59d"><strong>에이전트가 쌓아온 워크스페이스 히스토리를 텍스트 요약 대신 KV 상태 그대로 저장했다가, 필요할 때만 GPU로 되살려 쓰는 KV 가상화 시스템</strong></span>이다.

핵심 결과만 먼저:

| 항목 | 수치 | 조건 |
|---|---|---|
| 컨슈머 GPU 워크스페이스 | 1M 토큰 | 24GB RTX 5090 Laptop, Qwen3.6/3.8-27B NVFP4 |
| 실행 뷰(execution view) | 80K 토큰 | 같은 노트북, llama.cpp와 동일 |
| 생성 속도 | ~50 tokens/s | 싱글 세션 기준 |
| 서버 플랫폼 워크스페이스 | 최대 10M 토큰 | 96GB RTX PRO 6000, 실행 뷰 64K 고정 |
| DeepSWE Pass@1 | 43.8% → 48.4% | Qwen3.8-27B, compaction 대비 |
| DeepSWE Pass@4 | 81.3% → 93.8% | 16과제 × 4샘플 |
| 복구 지연시간 | 11.4~53.8배 개선 | Compact+RAG 대비, 요약 생성 제외 기준 |

기준일: 2026-09-07 논문 v1 기준. 소스 코드는 [github.com/kvmem/kvmem-qw3](https://github.com/kvmem/kvmem-qw3)에 공개돼 있다.

## 문제 정의: 컴팩션의 정보 손실과 반복 prefill

긴 에이전트 작업을 돌리면 워크스페이스 히스토리가 모델 컨텍스트 창을 넘는다. 지금 대부분의 에이전트 시스템(Claude Code, OpenHands condenser, OpenClaw compaction 엔진 등)은 두 가지로 대응한다.

컴팩션은 오래된 히스토리를 요약으로 바꾼다. 근데 요약은 <span style="background-color: #fff59d"><strong>나중에 뭘이 중요해질지 모르는 시점에 미리 버리는 결정</strong></span>이라, 초기 파일의 한 문장이나 툴 출력의 값 하나가 나중에 태스크 크리티컬이 되면 복구할 방법이 없다. 논문은 서로 다른 두 히스토리 H1, H2가 같은 요약 C로 매핑되면 구분 자체가 불가능하다는 논증으로 이걸 보여준다.

텍스트 검색(Compact+RAG)은 빠진 증거를 원문으로 복구한다.

근데 그 텍스트는 이미 한 번 prefill해서 KV를 만들어둔 내용이다. 다시 가져오면 <span style="background-color: #fff59d"><strong>이미 처리한 내용을 또 prefill하는 비용을 매번 다시 지불</strong></span>한다. AgentLongBench 1M 토큰 설정에서 Compact+RAG의 pre-answer latency가 416초인 이유가 이거다.

KVMem의 출발점은 이거다. 히스토리가 실행 뷰를 벗어날 때 이미 KV 상태로 인코딩돼 있으니, <span style="background-color: #fff59d"><strong>버리는 게 아니라 GPU-호스트메모리-NVMe에 페이징해두고 필요할 때 복원하면 된다</strong></span>. 가상 메모리(paging)를 KV 캐시에 적용하는 발상이다.

## 구조: 세 가지 메커니즘

![](/images/2026-09-07-kvmem-gpu-agent-workspace-virtualization/fig-1-p6.png)

Figure 1: KVMem의 세 가지 핵심 설계 — 스텝 단위 메모리 스케줄링, 쿼리 조건 검색, 계층형 KV 관리 (논문 Figure 1)

### 스텝 단위 메모리 스케줄링 구조

OpenHands SWE-bench Lite 롤아웃 8개의 어텐션을 128토큰 윈도우로 분석했다. 같은 에이전트 스텝 안의 인접 윈도우 KL 발산은 평균 0.070비트인데, <span style="background-color: #fff59d"><strong>스텝 경계를 가로지르는 윈도우는 평균 2.59비트로 37.3배 높다</strong></span>. 즉 모델의 과거 어텐션은 한 스텝 안에서는 안정적이고 스텝이 바뀔 때 급변한다.

![](/images/2026-09-07-kvmem-gpu-agent-workspace-virtualization/fig-2-p7.png)

Figure 2: 스텝 경계에서 어텐션이 급변하는 관측 (논문 Figure 2)

그래서 KVMem은 워킹셋을 스텝당 한 번, prefill 직후·디코딩 직전에 갱신한다. 디코딩 중에는 고정한다.

어텐션도 희소하다. 윈도우당 평균 103.1개 과거 블록 중 <span style="background-color: #fff59d"><strong>top-8 블록이 전체 과거 어텐션의 66.5%, top-16이 77.0%</strong></span>을 차지한다. 전체를 상주시킬 필요 없이 작은 세트만 잘 고르면 된다.

### Mean-K 검색 인덱스 구조

백만 토큰 워크스페이스의 모든 KV를 스캔하면 검색 비용이 감당이 안 된다. KVMem은 32토큰 블록 단위로 나누고, 각 블록을 레이어·KV헤드별로 <span style="background-color: #fff59d"><strong>K 벡터의 평균(Mean-K) 하나로 요약한 인덱스</strong></span>를 만든다. 이때 RoPE 위치 인코딩을 제거한 position-independent K를 쓴다.

검색 시점에는 현재 쿼리 벡터와 후보 블록들의 Mean-K를 어텐션 공간에서 직접 스코어링한다. 별도 임베딩 모델이 아니라 <span style="background-color: #fff59d"><strong>서빙 모델 자신의 어텐션 신호로 랭킹</strong></span>하는 게 포인트다. 인덱스 전체는 호스트 메모리에 두고 고정 크기 타일만 GPU로 올려 스코어링해서, 워크스페이스가 커져도 검색의 GPU 풋프린트는 일정하다.

### 계층형 KV 관리와 re-RoPE 복원 구조

![](/images/2026-09-07-kvmem-gpu-agent-workspace-virtualization/fig-3-p9.png)

Figure 3: 패킹+파이프라인 rematerialization (논문 Figure 3)

선택된 블록의 KV를 GPU 실행 뷰로 되살리는 건 단순 페이지 로드가 아니다. RoPE가 박힌 K는 위치가 바뀌면 무효라서, KVMem은 position-independent raw K를 원천으로 유지하다가 새 논리 위치에 맞춰 re-RoPE한다.

이식은 vLLM·LMCache·CacheBlend를 의식한 구분인데, <span style="background-color: #fff59d"><strong>매 스텝 바뀌는 쿼리 의존 서브셋을 새 컴팩트 위치로 재매핑하는 건 이 셋 어느 추상화에도 없는 실행 모델</strong></span>이라서 저자들은 QW3이라는 C++/CUDA 네이티브 엔진을 직접 구현했다.

이식(implementation) 포인트 세 가지:

- 선행 stage-out: 나가는 블록을 chunked prefill과 겹쳐서 미리 호스트 메모리로 복사해두면 전환 시점에 기다릴 게 없다.
- 연속 스텝의 워킹셋 겹침이 크니까 GPU 상주 블록은 페이지 재사용, 자주 검색되는 블록은 호스트 메모리에 우선 유지(LRU 대비).
- 흩어진 블록 복원을 묶어서(packing) PCIe 전송하고, CPU 수집 → H2D 전송 → GPU scatter/re-RoPE 3단계를 파이프라인으로 겹친다.

## 결과: 4개 벤치마크 수치

Table 1 요약 (Qwen3.6-27B, 동일 활성 컨텍스트 예산 비교):

| 벤치마크 | 메트릭 | Sliding | Compact-only | Compact+RAG | KVMem | Full Context |
|---|---|---|---|---|---|---|
| LongMemEval-S (32K 활성) | 정답률 % | 26.8 | 45.6 | 86.2 | 85.6 | 86.6 |
| LongMemEval-S | 지연시간 s | 0.19 | 18.92 | 26.63 | 0.48 | 0.30 |
| MemoryAgentBench (>256K) | 종합점수 % | 17.95 | 27.54 | 34.80 | 40.99 | – |
| AgentLongBench (≤256K) | 태스크성공 % | 25.36 | 15.84 | 47.49 | <span style="background-color: #fff59d"><strong>60.87</strong></span> | 59.54 |
| AgentLongBench (512K) | 태스크성공 % | 25.0 | 22.5 | 54.0 | 53.0 | – |
| AgentLongBench (1M) | 태스크성공 % | 20.0 | 32.0 | 42.0 | 50.0 | – |
| AgentLongBench (1M) | 지연시간 s | 0.26 | 380.19 | 416.38 | 0.73 | – |

눈에 띄는 지점 두 곳.

AgentLongBench ≤256K에서 KVMem이 60.87%로 Full Context(59.54%)보다 오히려 높다. 저자의 설명은 전체 컨텍스트를 다 보여주면 롱컨텍스트 성능 저하가 생기는데, 쿼리 관련 서브셋만 노출하면 그 저하가 부분적으로 완화된다는 것. 흥미로운 관측이다.

LongMemEval-S 세부 분석(Table 2)에서 KVMem의 fresh prefill은 <span style="background-color: #fff59d"><strong>0.08K 토큰</strong></span>, Compact+RAG는 31.00K 토큰. 총 입력도 Full Context와 동일한 109.74K다. 텍스트로 다시 집어넣는 경로를 아예 안 타니까 나오는 숫자다.

### DeepSWE 실전 평가

실제 에이전트 트레이젝토리 전체에서도 측정했다. DeepSWE v1.1 첫 16과제 × 4샘플, Qwen3.8-27B + Claude Code 하네스로 64 트레이젝토리씩 비교. KVMem 설정은 1M 논리 워크스페이스 + 128K 선택 예산 + 64K 생성 리저브, 컴팩션 무효화. 비교군은 256K dense 컨텍스트 + Claude Code 네이티브 auto-compaction.

결과: Pass@1 43.8% → 48.4%, Pass@4 81.3% → 93.8%(16과제 중 15과제 해결).

효율은 <span style="background-color: #fff59d"><strong>평균 prefill 시간 211.5초 → 95.0초(2.23배), 에이전트 전체 시간 52.5분 → 45.8분(1.15배), 디코딩 토큰도 18.7% 감소</strong></span>. 공개 모델 재집계와 비교하면 Pass@4 93.8%는 Gemini 3.7 Flash(81.3%)보다 높은 수치다. 물론 하네스가 달라 엄격한 통제 비교는 아니다.

### 노트북에서 1M 토큰

24GB RTX 5090 Laptop GPU 노트북에서 vLLM은 약 10K, llama.cpp는 약 80K 컨텍스트가 한계다. KVMem(QW3)은 실행 뷰 80K는 llama.cpp와 동일한데, <span style="background-color: #fff59d"><strong>가상 워크스페이스를 1M 토큰까지 키우면서도 약 50 tokens/s를 유지</strong></span>한다. 모델 원생 창(256K)의 4배, GPU 상주 실행 뷰의 12.5배다.

서버(96GB RTX PRO 6000)에서는 워크스페이스를 256K → 10M로 키워도 GPU 메모리는 약 34GiB로 거의 고정되고, 늘어나는 건 호스트 메모리(64GiB 상한)와 NVMe(8.5 → 324GiB)다. 10M 토큰에서도 retrieval 지연 1.3초, TTFT 1.6초 수준.

## 한계 (논문 스스로 밝힌 것)

- 가상화되는 건 주소 가능한 워크스페이스지, 한 번의 모델 호출이 함께 attend하는 토큰 수가 아니다. 각 스텝은 여전히 실행 뷰 안에서만 본다.
- KV 재사용은 새 컨텍스트에서 텍스트를 다시 계산하는 것과 수학적으로 동등하지 않다. re-RoPE로 위치 정합성을 맞추지만 <span style="background-color: #fff59d"><strong>과거 KV는 원래 자기 인과 컨텍스트에서 계산된 것</strong></span>이라는 근본 차이가 남는다.
- KV 상태는 텍스트보다 훨씬 크다. 스토리지 용량을 재사용 가능한 모델 상태와 바꾸는 트레이드오프고, 10M는 평가 상한이지 아키텍처 한계가 아니다.
- QW3 엔진 수준의 저수준 제어가 필요해서 <span style="background-color: #fff59d"><strong>블랙박스 LLM API 위에 투명하게 얹을 수는 없다</strong></span>. 클라우드 서빙 스택 통합은 future work로 남아 있다.

## 왜 중요한가

내 해석이다. 최근 긴 컨텍스트 에이전트 논의는 대부분 프롬프트/요약 레이어(compaction, RAG)에서 일어났는데, KVMem은 그 아래 시스템 레이어(KV 캐시)에서 문제를 다시 정의한다. "어차피 이미 KV로 계산해뒀는데 왜 텍스트로 저장했다가 다시 계산하나"라는 질문은 한번 들으면 당연해 보인다. 실행 뷰를 고정하고 워크스페이스만 키우는 발상은 OS 페이지 가상메모리의 직접적인 이식이고, 스텝 경계 어텐션 관측(37.3배 KL 차이)이 그 스케줄링 근거라는 것도 깔끔하다.



근데 27B 로컬 모델 기준 실험이라는 점, DeepSWE 비교군이 같은 하네스 내 compaction뿐이라는 점은 실사용 관점에서 감안해야 한다. 그리고 컨슈머 GPU에서 1M 토큰이 실용적이게 됐다는 것 자체가, 로컬 에이전트 파이프라인 설계에서 "컨텍스트가 넘치면 요약"이라는 디폴트 가정을 다시 볼 신호다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Q. KVMem은 모델의 컨텍스트 창 자체를 늘려주나요?**
아니다. 한 번의 모델 호출이 보는 실행 뷰는 컨텍스트 창과 GPU KV 예산 안에서 제한된다. 늘어나는 것은 주소 가능한 워크스페이스이고, 각 스텝에서 쿼리 관련 서브셋만 실행 뷰로 materialize된다.

**Q. 기존 컴팩션 대비 무엇이 다른가요?**
컴팩션은 히스토리를 요약 텍스트로 바꿔서 정보를 잃고, RAG로 복구하면 이미 처리한 텍스트를 다시 prefill해야 한다. KVMem은 원래 KV 상태를 GPU-호스트-NVMe에 저장해뒀다가 복원하므로 손실도 재계산도 없다.

**Q. 어떤 하드웨어에서 확인된 결과인가요?**
24GB RTX 5090 Laptop GPU 노트북에서 Qwen3.6/3.8-27B NVFP4로 1M 토큰 워크스페이스·약 50 tokens/s, 96GB 서버 GPU에서는 10M 토큰까지 평가됐다. 소스는 github.com/kvmem/kvmem-qw3에 공개돼 있다.

**Q. API 기반 모델에 바로 쓸 수 있나요?**
현재 구현은 KV 할당·검색·위치 복원·계층 이동을 직접 제어해야 해서 자체 QW3 엔진에서 동작한다. 블랙박스 API 위에는 얹을 수 없고, 클라우드 서빙 통합은 future work다.

## 참고

- 논문: [arXiv:2609.04852](https://arxiv.org/abs/2609.04852) (KVMem: Virtualizing Million-Token Agent Workspaces on a Consumer GPU, 2026-09-04)
- 코드: [github.com/kvmem/kvmem-qw3](https://github.com/kvmem/kvmem-qw3)
- 비교 대상 시스템: vLLM, LMCache, CacheBlend, MemGPT/Mem0류 텍스트 메모리
- 벤치마크: LongMemEval-S, MemoryAgentBench, AgentLongBench, DeepSWE v1.1
