---
title: "Continual Learning in Transition: 매개변수 중심에서 시스템 수준 적응으로"
date: 2026-08-09
draft: false
description: "LLM·에이전트 시대 continual learning의 3축(When·How·Where) 전환을 정리한 서베이"
tags:
  - continual-learning
  - LLM
  - agent
  - harness
  - memory
  - skill
  - survey
  - self-evolution
authors:
  - conanssam
---

논문: [Continual Learning in Transition](https://arxiv.org/abs/2608.06216) (Hou et al., 2026)

## 요약

Continual learning(CL)의 연구 범위가 매개변수 중심에서 시스템 수준 적응으로 전환하고 있습니다. 본 서베이는 이 전환을 When·How·Where 3축으로 체계화합니다.

- When: 학습 시점이 사전학습~포스트트레이닝~추론 시점으로 확장
- Where: 능력 저장 위치가 매개변수에서 하네스(메모리·스킬·프로토콜)로 확장
- How: 업데이트 방식이 오프폴리시 그래디언트에서 온폴리시 RL·그래디언트 프리 방법으로 확장

![Figure 1: 3차원 continual learning 개요](/images/2026-08-09-continual-learning-in-transition/fig-1-p2.png)

## 1. 고전적 CL의 세 가정

고전적 CL은 catastrophic forgetting 방지를 목표로 하며, 재생·그래디언트 투영·매개변수 분리·정규화의 네 방법족으로 구성됩니다. 이 방법들은 다음 세 가지를 암묵적으로 가정합니다:

1. 학습은 배포 전 훈련 단계에서만 발생
2. 능력은 매개변수에 저장
3. 업데이트는 오프폴리시 그래디언트 기반

LLM·에이전트 시대에 이 세 가정이 모두 해제되고 있습니다.

## 2. When 축: 학습 시점의 확장

![Figure 4: When 축](/images/2026-08-09-continual-learning-in-transition/fig-4-p7.png)

| 단계 | 특징 | 대표 방법 |
|---|---|---|
| 사전학습 | 코퍼스 스트림 지식 갱신 | 도메인 적응, 리플레이 버퍼 |
| 포스트트레이닝 | 정렬·태스크 적응·망각 통제 | RLHF, RLVR, 순차 SFT |
| 추론 시점 | 배포 후 적응, 지속성 | TTT-LM, TTRL |

추론 시점 학습의 핵심 구분은 지속성(persistence)입니다. 일반 추론 시 계산(검색, 샘플링)은 쿼리 종료 후 시스템을 변경하지 않지만, 추론 시 CL은 정보를 시스템에 기록하여 이후 행동에 영향을 줍니다.

## 3. Where 축: 능력 저장 위치의 확장

![Figure 5: Where 축](/images/2026-08-09-continual-learning-in-transition/fig-5-p8.png)

### 3.1 매개변수 캐리어

LoRA 계열(O-LoRA, LoRAMoE, SLIM)이 모듈 단위 업데이트로 간섭을 감소시킵니다.

### 3.2 하네스 층

**메모리**: MemoryLLM(학습 가능 메모리 풀), MemoryBank(에빙하우스 망각 곡선), A-MEM(원자 명제 단위), MemRL(보상 기반 RL 진화).

**스킬**: Voyager(코드 스킬 라이브러리), SkillRL(스킬+정책 동시 RL), SKILL0(하네스→매개변수 내재화).

**프로토콜**: Promptbreeder(프롬프트 진화), Cline/Aider/Cursor(규칙 파일 외부화).

### 3.3 캐리어 계층

| 층 | 쓰기 비용 | 안정성 | 용량 한계 |
|---|---|---|---|
| 매개변수 | 최고 | 최고 | 모델 크기 |
| 외부 메모리 | 중간 | 중간 | 저장·검색 대역폭 |
| 컨텍스트 | 최저 | 최저 | 하드 길이 제한 |

## 4. How 축: 업데이트 방식의 확장

![Figure 6: How 축](/images/2026-08-09-continual-learning-in-transition/fig-6-p10.png)

### 4.1 온폴리시가 CL에 유리한 구조적 이유

Shenfeld et al.: 망각 정도 ∝ 새 작업에 대한 KL 발산. 온폴리시 RL은 KL이 작은 해를 자연스럽게 선호. 오프폴리시 SFT는 임의로 먼 분포로 수렴 가능.

### 4.2 그래디언트 프리 학습

- 모델 병합(Task Arithmetic, TIES-Merging): 데이터 없이 가중치 공간 능력 합성
- 영차 미분(MeZO, ZeroFlow): 순전파만으로 미분 추정. 망각 완화에서 1차 미분과 동등
- 휴리스틱 학습: 메모리·스킬·프롬프트 진화 — 그래디언트 없이 피드백만으로 개선

## 5. 교차 프로파일

![Figure 3: 방법 분포](/images/2026-08-09-continual-learning-in-transition/fig-3-p6.png)

| 방법 | When | Where | How |
|---|---|---|---|
| Reflexion | 추론 | 하네스(메모리) | 그래디언트 프리 |
| TTRL | 추론 | 매개변수 | 온폴리시 |
| AgentEvolver | 포스트트레이닝 | 매개변수+하네스 | 온폴리시 |
| SKILL0 | 포스트테레이닝→추론 | 하네스→매개변수 | 온폴리시 |

## 6. 하네스 엔지니어링으로 충분한가

저자의 입장: 기능적으로는 CL을 대체하되 기구론적으로는 대체하지 않는다.

1. 하네스 수정 주체가 사람이면 폐쇄 루프가 아님
2. 폐쇄 루프 방법(Promptbreeder, Voyager, AgentEvolver)은 아직 초기 단계
3. 하네스 능력은 컨텍스트 결합도가 높아 이전이 어려움

## 7. 과제

- 캐리어 간 조정 스케줄링: 컨텍스트/메모리/스킬/매개변수 분배
- 다층 망각: 매개변수·메모리·컨텍스트·스킬 각층의 망각 양상이 상이
- 긴 호라이즌 에이전트: 오류 누적 증폭, 하네스 비미분성
- 검증 가능한 보상의 한계: 비코드 영역은 자동 검증 어려움

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [arXiv:2608.06216](https://arxiv.org/abs/2608.06216)
