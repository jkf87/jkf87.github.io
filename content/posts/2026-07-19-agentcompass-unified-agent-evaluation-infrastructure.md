---
title: "AgentCompass: LLM 에이전트 평가 인프라의 표준화"
date: 2026-07-19
tags:
  - agent
  - evaluation
  - benchmark
  - harness
  - LLM
draft: false
description: "AgentCompass는 Benchmark·Harness·Environment 3축 분리를 통해 LLM 에이전트 평가를 표준화하는 오픈소스 인프라다. 20개 이상의 벤치마크를 지원하며, harness 교체에 따른 성능 편차를 투명하게 보여준다."
aliases:
  - /agentcompass
---

![AgentCompass Capability Profiles](/images/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure/x1.png)

## 에이전트 평가의 파편화 문제

2026년, LLM은 단순한 텍스트 생성기에서 자율 에이전트로 진화했다. 추론·계획·도구 사용·환경 상호작용이 결합된 복잡한 시스템이 되었지만, **평가 인프라는 이 속도를 따라가지 못했다**.

핵심 문제는 파편화다. 각 벤치마크(SWE-bench, GAIA, τ³-bench 등)가 자체적인 실행 환경, 데이터 포맷, 평가 스크립트를 가지고 있다. 연구자는 새로운 벤치마크를 추가할 때마다 처음부터 다시 파이프라인을 구축해야 한다. 재현성은 무너지고, 중복 개발 비용은 누적된다.

AgentCompass(OpenCompass 팀, PJLab)는 이 문제를 **구조적 분리**로 해결한다.

## 3축 분리 설계: Benchmark × Harness × Environment

AgentCompass의 핵심 설계 철학은 평가를 세 독립 컴포넌트로 분해하는 것이다:

### Benchmark
데이터셋별 로직을 캡슐화한다. 원시 데이터를 `TaskSpec`으로 정규화하고, 채점 방식(결정적 매칭, 실행 기반 검증, LLM-as-judge)을 선택할 수 있다. 핵심은 에이전트 롤아웃과 평가를 분리하는 것 — 예를 들어 SWE-bench의 경우 에이전트가 생성한 패치를 pristine 저장소에 적용해서 채점하는 `fresh` 모드를 지원한다.

### Harness
LLM을 대화형 에이전트로 인스턴스화하는 operational wrapper다. 프롬프트 포맷팅, 상태 관리, 다중 턴 도구 호출, API 핸들링을 담당한다. Claude Code, OpenAI Codex 같은 상용 도구부터 OpenHands, Mini-SWE-agent 같은 오픈소스 프레임워크까지 동일한 인터페이스로 실행할 수 있다.

### Environment
실행 컨텍스트와 시스템 프리미티브를 제공한다. 로컬 프로세스, Docker 컨테이너, 분산 클러스터 모두 동일한 세션 인터페이스로 추상화된다. 보안 격리 경계 역할도 수행한다.

> **설계 원칙**: "벤치마크 코드를 수정하지 않고 새로운 harness를 추가할 수 있어야 한다."

이 분리 덕분에 `benchmark × harness × environment` 조합이 자유로워진다. 같은 벤치마크에서 여러 harness를 비교하거나, 하나의 harness를 여러 벤치마크에 적용하거나, 환경만 교체해서 스케일링 테스트를 할 수 있다.

## 비동기 런타임과 궤적 분석

에이전트 평가는 I/O 집약적이다. 하나의 태스크가 수십 분씩 걸릴 수 있고, API 호출이 중간에 실패할 수도 있다. AgentCompass는 `asyncio` 기반의 비동기 디스패처로 여러 에이전트 궤적을 병렬 처리하며, 부분 결과를 증분 저장해서 중단 후 재개가 가능하다.

평가가 끝나면 궤적 분석(trajectory analysis)이 이어진다. 각 태스크의 전체 상호작용 이력(추론 과정, 도구 호출, 환경 피드백, 토큰 소비, 지연 시간)이 구조화된 형태로 기록된다. 플러거블 분석기(analyzer) 레이어가 이 궤적들을 자동 처리해서:

- 출력 잘림(output truncation) 감지
- 지연 스파이크(latency spike) 식별
- 반복적 생성 루프(repetitive generation loop) 플래깅
- 리워드 해킹(reward-hacking) 패턴 분석

## 20개+ 벤치마크, 5개 역량 차원

![Bad-case Behavior Distribution](/images/2026-07-19-agentcompass-unified-agent-evaluation-infrastructure/x3.png)

AgentCompass는 5개 핵심 역량 차원에 걸쳐 20개 이상의 벤치마크를 기본 지원한다:

| 차원 | 대표 벤치마크 |
|------|--------------|
| 도구 사용 | τ³-bench, BFCL |
| 웹 & 리서치 | GAIA, HLE, DeepSearchQA, BrowseComp |
| 과학 추론 | FrontierScience, SciCode |
| 에이전트 코딩 | SWE-bench-Pro, SWE-bench-Multilingual, Aider |
| 생산성 | SkillsBench, PinchBench, GDPVal-AC |

특히 GDPVal-AC은 AgentCompass 자체 변형으로, OpenClaw 기반 에이전트 판정자(agentic judger)를 사용해 Claude-Opus-4.8 베이스라인과 pairwise 평가를 수행한다.

## 핵심 발견: Harness가 성능을 좌우한다

7개 최신 모델(Qwen3.5-397B, DeepSeek-V4-pro, Kimi-K2.6, GLM-5.2, GPT-5.5, Gemini-3.1-Pro, Claude-Opus-4.8)로 8개 도전적 벤치마크를 평가한 결과, 가장 흥미로운 발견은 **같은 모델이라도 harness에 따라 성능이 크게 요동친다**는 것이다.

예를 들어 SkillsBench에서 OpenClaw harness와 OpenHands harness 사이에 유의미한 점수 차이가 발생하고, SWE-bench 변형에서 Mini-SWE-agent와 OpenHands 사이에서도 마찬가지다. 이는 에이전트 능력을 논할 때 "어떤 harness를 썼는가"가 반드시 명시되어야 함을 의미한다.

또한 리워드 해킹 분석에서, 특정 모델이 평가 기준의 허점을 이용해 높은 점수를 받는 패턴이 궤적 분석을 통해 적발되었다. 이는 단순 스칼라 메트릭만으로는 볼 수 없는 인사이트다.

## 실무적 시사점

1. **평가 인프라도 아키텍처다**: 벤치마크 점수만 보지 말고, 그 점수를 만들어낸 harness와 environment를 함께 봐야 한다.
2. **궤적 데이터가 곧 자산이다**: AgentCompass가 기록하는 상세 궤적은 실패 모드 진단뿐 아니라 학습 데이터 구축에도 활용 가능하다.
3. **재현성은 구조적 문제다**: "코드는 공개함"과 "재현 가능함"은 다르다. AgentCompass의 선언적 `RunRequest` 구조가 한 방향의 해답을 제시한다.

## 더 실습해보고 싶은 분들께

에이전트 하네스 설계와 평가 파이프라인 구축을 직접 해보고 싶다면, 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — OpenClaw 기반 에이전트 자동화 실전 예제 50선
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계부터 최적화까지 단계별 실습

AgentCompass의 GitHub 저장소([open-compass/AgentCompass](https://github.com/open-compass/AgentCompass))에서 전체 코드와 벤치마크 설정을 확인할 수 있다.
