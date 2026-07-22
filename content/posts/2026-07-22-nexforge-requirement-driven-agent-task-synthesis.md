---
title: "NexForge: 에이전트 훈련 데이터를 '요구사항'에서 자동 생성하는 파이프라인"
slug: 2026-07-22-nexforge-requirement-driven-agent-task-synthesis
publish: true
date: 2026-07-22T13:00:00+09:00
tags:
  - agent
  - data-synthesis
  - SFT
  - terminal-bench
  - automation
  - LLM
  - open-source
draft: false
---

> **논문**: [NexForge: Scaling Agent Capabilities through Requirement-Driven Task Synthesis for LLMs](https://arxiv.org/abs/2607.14186)
> **저자**: Jiarong Zhao, Zhikai Lei, Zhiheng Xi et al. (East China Normal University, Shanghai Qiji Zhifeng)
> **v3**: 2026-07-21

## 한 줄 요약

에이전트 훈련 데이터를 만드는 기존 방식은 "미리 정해둔 도구·저장소·스킬 그래프"에 매여 있었다. NexForge는 **사용자의 요구사항 한 줄**에서出发해, 실제 수요를 조사하고, 분포를 제어하며, 실행 가능한 작업 환경과 전문가 궤적을 자동 합성한다 — 도메인별 인프라 없이도.

## 문제: 기존 에이전트 데이터 합성의 한계

터미널 에이전트·오피스 에이전트를 훈련시키려면 "실행 가능한 환경(executable workspace) + 고품질 궤적(trajectory)"이 필요하다. 그런데 기존 방법들은 전부 **substrate-bound**였다:

- SkillSynth: 미리 정의된 스킬 그래프에서 태스크 생성
- Terminal-World: 에이전트 스킬 기반 환경 구축
- CLI-Universe: 사전 정의된 능력 분류 체계 사용
- R2E-Gym / SWE-smith: 특정 코드 저장소와 테스트에 의존

![Substrate-bound vs. NexForge](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/fig-2-p2.png)
*그림 2: 기존 방법(좌)은 각 도메인마다 별도 파이프라인이 필요하다. NexForge(우)는 요구사항 하나로 모든 도메인을 커버한다.*

이런 방식의 문제는 세 가지다:
1. **확장 한계**: 입력 substrate의 크기가 전체 데이터 크기의 상한이 된다
2. **도메인별 인프라**: 새 도메인마다 처음부터 파이프라인을 만들어야 한다
3. **분포 왜곡**: 실제 수요가 아닌 substrate의 편향이 태스크 분포를 결정한다

## NexForge: 요구사항 기반 파이프라인

NexForge의 핵심 통찰은 **"무엇을 연습할지"와 "어떻게 실행 가능하게 만들지"를 분리**하는 것이다.

![NexForge 파이프라인 개요](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/fig-3-p4.png)
*그림 3: NexForge 전체 파이프라인. 요구사항 → 수요 조사 → 분포 제어 컴파일 → 환경 구체화 → 궤적 수집*

### 1단계: 연구 기반 수요 발견 (Research-Based Demand Discovery)

사용자 요구사항 $I$가 들어오면, 웹 검색이 가능한 리서치 에이전트가 실제 전문가 워크플로, 기술 문서, 역할 기술서 등을 조사한다. 결과로 두 가지가 나온다:

- **태스크 수요 프로파일** $\Phi(I)$: 태스크 형태(task type), 산출물(deliverable), 소스 전략, 런타임, 언어, 난이도에 대한 가중 분포
- **시나리오 저수지**: 조직, 직무, 워크플로 등 구체적 맥락 정보

시나리오는 태스크 형태를 명시하지 않고 맥락만 기술하므로, 분포를 독립적으로 왜곡하지 않는다.

### 2단계: 분포 인식 컴파일 (Distribution-Aware Task Compilation)

각 시나리오에 대해 호환성 필터를 거쳐 태스크 형태를 샘플링한다. 핵심은 **순차적 호환성 검사**:

> 시나리오 → 태스크 타입 → 산출물 → 소스 전략 → 런타임 → 언어 → 난이도

각 단계에서 이전 선택과 시나리오에 호환되는 옵션만 남기고, 프로파일 가중치로 샘플링한다. 이렇게 생성된 **디렉티브(directive)**는 "어떤 작업을 할지"를 결정하지만, "어떤 저장소를 쓸지"는 아직 정해지지 않는다.

### 3단계: 환경 구체화 및 궤적 수집

디렉티브가 정해지면:
1. **자료 채굴**: 공개 저장소, 문서, 데이터셋을 검색
2. **블루프린트 설계**: 워크스페이스 구조 계획
3. **워크스페이스 생성 및 검증**: 실제 실행 가능한 환경 구축
4. **교사 모델 궤적 수집**: GPT-5.5로 에이전트 롤아웃 생성
5. **궤적 정제**: 오류 전용 출력, 중복, 구조적 문제 제거

## 성과: Terminal-Bench에서 무슨 일이 일어났나

![Nex-N2 성능](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/fig-1-p1.png)
*그림 1: NexForge 데이터 스케일링에 따른 Terminal-Bench 2.1 및 GDPval 성능.*

### Terminal-Bench 2.0 결과

| 모델 | 스캐폴드 | TB 2.0 |
|------|---------|--------|
| Gemini 3.1 Pro | TongAgents | 80.2 |
| Claude Opus 4.6 | Claude Code | 58.0 |
| **Qwen3.5-35B-A3B + Terminal-3.6K** | NexAU | **52.0** |
| **Qwen3.5-35B-A3B + Terminal-43.2K** | NexAU | **58.4** |
| Qwen3.5-35B-A3B Base | NexAU | 22.5 |

![Terminal-Bench 2.0 상세 비교](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/table-3-p8.png)
*표 3: Terminal-Bench 2.0 pass@1 정확도. 좌: 프론티어 모델, 우: 터미널 특화 32B 모델.*

Terminal-43.2K로 스케일링하면 58.4%에 도달하여 **Claude Opus 4.6 + Claude Code (58.0%)과 동급**이 된다. 같은 Qwen3-32B 베이스에서 기존 최고인 Terminal-World(31.5%)를 크게 앞지른다.

### 데이터 스케일링 곡선

![데이터 스케일링](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/fig-4-p8.png)
*그림 4: 데이터 규모에 따른 Terminal-Bench 2.0 정확도(좌)와 GDPval Elo(우). 점선은 참조 모델.*

2K → 3.6K → 43.2K로 갈수록 일관된 향상. 오피스 도메인에서도 813 → 1338 → 1384 Elo로 꾸준히 오른다.

### Nex-N2: 공개 모델의 SOTA

NexForge 데이터로 훈련된 **Nex-N2** 모델 패밀리:
- **Terminal-Bench 2.1**: Nex-N2-Pro 75.3% (GPT-5.5의 83.4%에 근접)
- **GDPval**: Nex-N2-Pro 1585 Elo (Claude Opus 4.7의 1753에 이어 Claude Sonnet 4.6 1633과 경쟁)
- 모델은 [nex.sii.edu.cn](https://nex.sii.edu.cn/)에서 공개

## 왜 잘 작동하는가: 불랙이션 분석

![분포 분석](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/fig-5-p10.png)
*그림 5: (a) 태스크 타입 빈도, (b) 소스 전략 구성, (c) 분포 형태, (d) 집중도 vs 정확도.*

### 태스크 형태 제어 + 시나리오 그라운딩의 시너지

| 변형 | 시나리오 | 태스크 형태 | TB 2.0 |
|------|---------|------------|--------|
| Terminal-2K (full) | 저수지 | 프로파일 | 43.8 |
| w/o profile | 저수지 | 없음 | 40.2 |
| w/o scenario | 중립 시드 | 프로파일 | 42.7 |

![불랙이션 상세](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/table-6-p10.png)
*표 6: 불랙이션 결과. Asst./Tool은 궤적당 평균 어시스턴트 메시지 및 도구 호출 수.*

프로파일을 제거하면 태스크 타입 다양성이 급격히 감소한다 (24개 → ~3개, top-1 시그니처 커버리지 20.6% → 78.5%). 시나리오를 제거하면 궤적이 짧아지고 도구 호출이 줄어든다. 두 신호가 **상호 보완적**이다.

### 호환성 필터의 효과

분포 인식 태스크 컴파일(DATC)을 적용하면 디렉티브-시나리오 호환률이 7% → 81%로 급등한다.

![디렉티브 호환성](/images/2026-07-22-nexforge-requirement-driven-agent-task-synthesis/table-5-p10.png)
*표 5: DATC 적용 여부에 따른 디렉티브-시나리오 호환률.*

## 크로스 도메인 적응력

同一个 파이프라인으로 터미널과 오피스 두 영역을 커버한다:

- **터미널**: 소프트웨어 엔지니어링 54%, 시스템 관리 12%, 데이터 처리 9% ... (24개 타입)
- **오피스**: 데이터 분석 21%, 문서 리뷰 17%, 정보 취합 14% ... (15개 타입)
- **그라운딩**: 터미널은 GitHub 저장소 45%, 오피스는 웹 파일 69%

요구사항 명세만 바꾸면 같은 코어 파이프라인이 자동으로 도메인에 맞춰진다.

## 의의와 한계

**의의**:
- 에이전트 훈련 데이터 합성을 substrate에서 해방
- "요구사항 → 수요 조사 → 분포 제어 → 환경 구축 → 궤적"이라는 완전 자동 파이프라인
- 43.2K 태스크로 Claude Opus 4.6 + Claude Code와 동급 성능 달성
- Nex-N2 모델 패밀리를 공개 — 오픈소스 SOTA

**한계**:
- 교사 모델로 GPT-5.5에 의존 (비용)
- 정답 검증자(success verifier) 없이 궤적을 필터링하므로 불완전한 궤적이 포함될 수 있음
- 향후 머신 체크 가능한 검증자를 도입하여 RL과 벤치마크 구축으로 확장 예정

## 더 실습해보고 싶은 분들께

에이전트 데이터 합성, 터미널 에이전트 훈련, 그리고 자동화된 에이전트 파이프라인 설계는 직접 손으로 만져봐야 체감이 옵니다. 다음 두 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — 에이전트 하네스와 자동화 루프를 처음부터 끝까지 조립하는 실습 가이드
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 훈련 데이터와 RL 루프를 다루는 실전 강의

NexForge가 보여주는 "요구사항에서 자동으로 에이전트 훈련 환경을 만드는" 세계는, 하네스와 루프 엔지니어링의 핵심 실습 주제이기도 합니다.
