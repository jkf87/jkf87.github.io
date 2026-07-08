---
title: "비디오 에이전트의 추론을 반사로 바꾸다: Light-Omni의 이중 문맥 상태와 장기 기억"
date: 2026-07-09
draft: false
description: "비디오 이해 에이전트가 매번 '탐정처럼' 추론하고 검색하는 비용을 혁신적으로 줄인 Light-Omni. 전역 상태(Global State)와 잠재 상태(Latent State)라는 이중 문맥 설계로 M3-Agent 대비 12.1배 속도 향상, 2.6배 GPU 메모리 절감, 2.4% 정확도 향상을 동시에 달성했다."
tags: [Video Understanding, Long-Term Memory, Multimodal Agent, Reflexive Reasoning, Episodic Memory, Qwen-Omni]
categories: [AI Research]
author: Conan's Blog Bot
---

> **논문**: [Light-Omni: Reflex over Reasoning in Agentic Video Understanding with Long-Term Memory](https://arxiv.org/abs/2607.05511)
> **저자**: Chang Nie, Jiaju Wei, Junlan Feng, Chaoyou Fu, Caifeng Shan
> **소속**: Nanjing University
> **프로젝트 페이지**: [clare-nie.github.io/Light-Omni](https://clare-nie.github.io/Light-Omni/)

![Figure 1: 비디오 이해 패러다임 비교. 기존 비디오 에이전트는 '탐정식' 반복 추론으로 검색하고 증거를 모은다. Light-Omni는 이중 문맥 상태로 전역 문맥을 유지하고, 의미론적으로 정렬된 임베딩을 직접 생성하여 증거를 집약한다. 수면 시간 기억 통합을 통해 실시간 상호작용을 방해하지 않고 전역 시야와 거의 일정한 지연을 가능하게 한다.](/images/2026-07-09-light-omni-reflexive-agentic-video-understanding/fig-arch-comparison.jpeg)

## 핵심 요약

영화 <메멘토>의 주인공 레너드는 단기 기억 상실증에 걸려 폴라로이드 사진과 메모에 의존해 과거를 기억한다. 현재의 멀티모달 대형 언어 모델(MLLM)도 긴 비디오 스트림 앞에서는 마찬가지다. 유한한 컨텍스트 창에 갇혀 본질적으로 "망향자(amnesiac)"가 된다.

Light-Omni는 이 문제를 **반사적 이해(reflexive understanding)**라는 새로운 패러다임으로 해결한다:

| 설계 축 | 기존 방식 | Light-Omni |
|---------|----------|------------|
| **행동 제어** | 반복적 추론 → 계획 → 검색 | 전역 문맥 기반 즉시 행동 |
| **검색** | 텍스트 중심 유사도 매칭 | 학습된 임베딩으로 의미론적 정렬 |
| **기억** | 파편화된 클립 데이터베이스 | 계층적 통합 전역 스크립트 |
| **지연** | 비디오 길이에 비례하여 증가 | 비디오 길이와 무관한 일정 지연 |

## 문제: "탐정식" 반복 추론의 한계

기존 비디오 에이전트(M3-Agent, WorldMM 등)는 긴 비디오를 처리할 때 다음과 같은 루프를 반복한다:

1. 질문 분석 → 검색어 재작성(rewrite)
2. 메모리 뱅크에서 클립 검색(search)
3. 검색 결과 평가 → 추가 검색 필요?
4. 증거 집약 → 답변 생성

이 "탐정식(detective-style)" 접근은 잘 작동하지만, **치명적인 비용**이 따른다:

- **지연**: 비디오가 길수록 검색 라운드가 늘어남
- **비용**: 매 라운드마다 LLM 추론 호출
- **근시(myopia)**: 로컬 유사도에 기반해 전역 서사 구조를 놓침
- **의미론적 간극**: 사용자 질의와 메모리 표현 간 정렬 불량

근본 원인은 **전역 문맥의 부재**다. 인간은 인지 지도(cognitive map)를 형성해 주의를 안내하지만, 기존 에이전트는 파편화된 대용물(fragmented substitutes)에 의존한다.

## Light-Omni의 설계: 이중 문맥 상태

![Figure 2: Light-Omni 프레임워크. 다중모달 장기 기억 시스템(정체성 프로필, 의미론적 기억, 에피소드 기억) 위에 이중 문맥 상태를 구축한다. 수면 시간 기억 통합이 에피소드 기억으로부터 전역 상태를 생성하고, 이에 조건화된 잠재 상태가 자율 행동과 검색 임베딩을 직접 구동한다.](/images/2026-07-09-light-omni-reflexive-agentic-video-understanding/fig-framework.jpeg)

### 1. 다중모달 장기 기억 시스템

Light-Omni는 인간의 기억 체계를 모방한 3층 구조를 사용한다:

- **정체성 프로필(Identity Profiles)**: 등장인물, 객체, 장소 등의 영구적 지식
- **의미론적 기억(Semantic Memory)**: 사건 요약, 관계, 사실
- **에피소드 기억(Episodic Memory)**: 시간순 관찰 기록 (시각·청각·상호작용)

### 2. 전역 상태(Global State): 수면 시간 통합

핵심 혁신은 **수면 시간 기억 통합(sleep-time memory consolidation)**이다. 인간이 수면 중 기억을 통합하듯, Light-Omni는 실시간 상호작용을 방해하지 않는 비동기 프로세스로 에피소드 기억을 압축한다.

**계층적 병합(hierarchical merging)** 알고리즘:
- 최근 관찰은 고해상도로 보존
- 과거 이벤트는 요약하여 저장
- 시간에 따른 해상도 감소(decay)로 유한 크기 유지

결과물은 하나의 **다중모달 스크립트**—전역 문맥을 제공하는 콤팩트한 표현이다.

### 3. 잠재 상태(Latent State): 반사적 행동 제어

전역 상태에 조건화하여, Light-Omni는 **단일 포워드 패스**로 다음을 수행한다:
- 작업별 헤드를 통해 자율 행동 결정 (`speech`, `search` 등)
- 의미론적으로 정렬된 검색 임베딩 직접 생성

중요한 점은 검색 중개자(rewrite, condition, keyword)를 **제거**했다는 것이다. 백본과 임베딩 공간을 공동 최적화(joint optimization)하여 질의와 메모리 분포를 직접 정렬한다.

![Figure 4: 비디오 길이에 따른 지연 비교. 기존 에이전트는 비디오가 길어질수록 지연이 선형 증가하지만, Light-Omni는 비디오 길이와 무관하게 거의 일정한 지연을 유지한다.](/images/2026-07-09-light-omni-reflexive-agentic-video-understanding/fig-latency.jpeg)

## 성능: 정확도와 효율성의 동시 달성

### 벤치마크 결과

| 지표 | vs Qwen2.5-Omni-7B (베이스) | vs M3-Agent |
|------|----------------------------|-------------|
| **정확도 향상** | +9.5% | +2.4% |
| **속도 향상** | 20.5× | 12.1× |
| **GPU 메모리 절감** | 3.3× | 2.6× |

- VideoMTE-long 및 LVBench에서 **평균 58.0%** 정확도
- GPT-4o (48.1%), Gemini-2.0-Flash (55.8%), Qwen2.5-VL-72B (56.1%) 능가
- HippoVlog에서 M3-Agent 대비 **+13.0%**, WorldMM-8B 대비 **+8.8%** 향상

![Figure 3: 주요 벤치마크 성능 비교. Light-Omni는 다양한 장비 비디오 벤치마크에서 기존 최고 성능 에이전트를 뛰어넘는다.](/images/2026-07-09-light-omni-reflexive-agentic-video-understanding/fig-results.jpeg)

### 범용 메모리 모듈로서의 활용

Light-Omni는 단독 에이전트뿐 아니라 **기존 MLLM의 메모리 시스템**으로도 작동한다:

| 통합 대상 | 정확도 향상 | 속도 향상 | 메모리 절감 |
|-----------|-----------|----------|-----------|
| Qwen2.5-VL-7B | +4.9% | 최대 7.2× | 2.5× |
| Qwen3-VL-8B | +2.5% | — | — |
| Gemini-2.0-Flash | +3.8% | — | — |

이는 Light-Omni가 특정 모델에 종속되지 않는 **범용 장기 기억 모듈**임을 입증한다.

## 기억 시스템의 구조

![Figure 5: 다중모달 장기 기억 시스템 구조. 정체성 프로필, 의미론적 기억, 에피소드 기억이 계층적으로 구성되며, 수면 시간 통합을 통해 전역 상태로 압축된다.](/images/2026-07-09-light-omni-reflexive-agentic-video-understanding/fig-memory.jpeg)

## 의의: 추론에서 반사로의 전환

Light-Omni의 가장 큰 철학적 기여는 **"추론(reasoning)에서 반사(reflex)로의 전환"**이다.

인지과학에서 인간의 의사결정은 두 가지 모드로 동작한다:
- **System 2 (느린 사고)**: 순차적 추론, 계획, 분석
- **System 1 (빠른 사고)**: 직관, 반사, 패턴 매칭

기존 비디오 에이전트는 모든 것을 System 2로 처리했다. 질문이 들어오면 계획하고, 검색어를 만들고, 결과를 평가하고, 다시 계획하는 식이다.

Light-Omni는 **전역 문맥이라는 인지 지도**를 구축함으로써, 대부분의 작업을 System 1—반사적 응답—으로 처리한다. 검색이 필요한 경우에도, 학습된 임베딩으로 즉시 의미론적으로 정렬된 결과를 얻는다.

이것이 12.1배 속도 향상의 본질이다. 단순한 엔지니어링 최적화가 아니라, **문제 해결 패러다임 자체의 전환**이다.

## 한계 및 향후 방향

- **베이스 모델 의존성**: Qwen-Omni 계열에 최적화되어 있어 다른 아키텍처(GPT, Claude 등)와의 통합은 추가 검증이 필요
- **오프라인 통합 비용**: 수면 시간 통합이 비동기지만, 여전히 계산 자원을 소비
- **평가 범위**: 비디오 이해에 특화되어 있어, 다른 멀티모달 도메인(로봇 공학, IoT 등)에서의 효용은 미탐구

## 결론

Light-Omni는 비디오 에이전트 분야에 "패러다임 전환"이라는 단어가 과하지 않은 기여를 가져왔다. 추론을 반사로, 검색을 직관으로 바꾸는 이 접근은 단순히 더 빠른 것이 아니라 **근본적으로 다른 방식으로 문제를 해결**한다.

인간의 기억이 폴라로이드 사진의 모음이 아니라 하나의 인지 지도인 것처럼, Light-Omni는 에이전트의 기억도 파편화된 데이터베이스가 아닌 **살아 있는 전역 문맥**이 되어야 한다는 철학을 보여준다.
