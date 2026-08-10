---
title: "EvoHarness-RL: 에이전트가 하네스를 언제 읽을지 직접 배우는 방법"
date: 2026-08-10
tags:
  - agent
  - harness
  - LLM
  - reinforcement-learning
  - GRPO
  - self-evolution
  - long-horizon
  - loop
source: https://arxiv.org/abs/2608.05446
venue: LLA@COLM 2026
authors:
  - Xuying Ning
  - Dongqi Fu
  - Tianxin Wei
  - Hanqing Zeng
  - Yuanchen Bei
  - Bingxuan Li
  - Zihao Li
  - Qifan Wang
  - Xiang Shen
  - Yifan Wu
  - Jiayi Liu
  - Hong Li
  - Yinglong Xia
  - Xiangjun Fan
  - Hanghang Tong
  - Jingrui He
affiliation: UIUC, Meta AI
---

LLM 에이전트가 긴 작업을 하려면 외부 하네스가 필요하다는 건 이제 상식입니다. 메모리, 도구, 상태 추적기, 진행 로그 — 이런 것들이 모여서 하네스를 구성하죠. 그런데 한 가지 질문이 남아 있습니다. 에이전트는 이 하네스를 도대체 언제 읽어야 할까요?

EvoHarness-RL(UIUC + Meta AI, LLA@COLM 2026)은 이 질문에 대한 답을 제시합니다. 하네스 사용 정책 자체를 모델이 학습하게 만드는 거죠.

## 발상의 전환: 하네스 사용 정책을 학습 대상으로

기존 에이전트 시스템에서 하네스 사용 규칙은 사람이 프롬프트로 정합니다. "매 스텝마다 상태를 기록하라", "이전 경험에서 관련 지식을 찾아라" 같은 식이죠. 이런 규칙은 직관적이지만 비용을 무시합니다. 하네스를 한 번 읽을 때마다 한 스텝을 소모하니까요.

EvoHarness-RL은 하네스 액션을 환경 액션과 동일한 선택지로 놓습니다. track, commit, recall, note라는 네 가지 메타 액션이 환경 액션과 경쟁하게 만드는 거죠. 같은 스텝 예산을 쓰니까, 모델은 "지금 하네스를 읽는 게 이득인가?"를 자연스럽게 학습합니다.

## BPE: 세 가지 하네스 역할

EvoHarness-RL은 외부 하네스를 세 가지 역할로 추상화합니다:

- Belief (B): 환경에 대한 믿음 — 물건 위치, 객체 상태, 공간 관계. `track` 액션으로 조회
- Progress (P): 실행 상태 — 완료한 하위목표, 남은 작업, 막힌 지점. `commit` 액션으로 갱신
- Experience (E): 에피소드 간 재사용 지식 — 일반 스킬, 작업별 팁, 흔한 실수, 탐색 우선순위. `recall`로 검색, `note`로 기록

이 추상화가 좋은 이유는 도메인을 바꿔도 같은 인터페이스를 쓸 수 있기 때문입니다. ALFWorld에서는 Belief가 객체 상태 추적기지만, 웹 환경에서는 DOM 상태 요약이 될 수 있고, 코딩 환경에서는 파일 시스템 상태가 될 수 있습니다.

## 2단계 학습: SFT로 부트스트랩, GRPO로 최적화

![학습 파이프라인](/images/2026-08-10-evoharness-rl-self-evolving-runtime-harness/fig-2-p4.png)

1단계에서는 Claude Opus로 성공 궤적을 수집해서 Qwen3-8B를 SFT합니다. 87개 궤적, 1,153개 액션 쌍이 나왔고, 하네스 호출이 약 18%를 차지했습니다.

2단계에서는 cost-aware GRPO로 정책을 최적화합니다. 보상 설계가 이 연구의 핵심입니다:

- 성공 보상(10점)이 게이트키퍼
- 효율 보너스는 성공한 궤적에만 지급 — 짧을수록 좋습니다
- 다양성 보너스는 코사인 어닐링으로 초기 탐색 장려, 후반 특화
- 스팸/포맷 패널티로 반복 행동과 잘못된 액션 억제

## 96.9%: 8B 모델이 프론티어 모델에 필적하는 성공률

![메인 결과](/images/2026-08-10-evoharness-rl-self-evolving-runtime-harness/table-1-p6.png)

ALFWorld 140-task seen split 기준 주요 결과:

| 모델 | ALFWorld 성공률 |
|---|---|
| Qwen3-8B ReAct | 47.9% |
| GPT-4.1 (표준) | ~48% |
| Claude Opus 4.5 (표준) | ~84% |
| SkillRL (이전 학습 기반 SOTA) | 89.9% |
| EvoHarness-RL (Qwen3-8B) | 96.9% |
| Claude Opus 4.5 + BPE | 98.5% |

프롬프트에 BPE만 추가해도(학습 없이) 모든 모델이 크게 오릅니다. GPT-4.1은 +22.1, GPT-5는 +25.7. Claude Opus 4.5는 98.5%까지. 외부 상태 추상화가 범용적으로 효과가 있다는 증거입니다.

unseen split에서도 86.6%를 기록해서, 단순 암기가 아님을 보여줍니다.

## 하네스 어닐링: 자꾸 보다가 점점 안 보게 된다

![하네스 사용량 변화](/images/2026-08-10-evoharness-rl-self-evolving-runtime-harness/fig-3-p8.png)

GRPO가 진행되면서 하네스 호출 빈도가 에피소드당 5~6회에서 약 1회로 떨어집니다. 모델이 반복되는 하네스 사용 패턴을 가중치 안으로 흡수하는 거죠. 논문은 이를 "하네스 어닐링"이라고 부릅니다.

액션별로 차이가 있습니다. recall(경험 검색)은 끝까지 유지됩니다 — 과거 경험이 계속 도움이 되니까요. 반면 commit(진행 상태 기록)과 note(새 인사이트 작성)는 빠르게 감소합니다. 루틴이 내재화되면 외부에 적을 필요가 없어지니까요.

한편 Experience 저장소도 진화합니다. 초반에 빠르게 확장되다가 중복 병합, LFU 삭제로 압축됩니다. 정책이 "언제 쓸지"를 학습하는 동안 하네스는 "무엇을 제공할지"를 진화시키는 거죠.

## 한계: ALFWorld는 작은 세계다

이 연구의 제약도 분명합니다. ALFWorld는 텍스트 기반 가정 환경이라 상태 공간이 작고 구조화되어 있습니다. 6개 작업 유형, 140개 과제. 웹 네비게이션이나 소프트웨어 엔지니어링 같은 더 넓은 환경에서도 하네스 정책 학습이 유효할지는 다음 단계입니다.

그래도 핵심 통찰은 선명합니다. "더 좋은 하네스를 만드는 것"과 "하네스를 언제 쓸지 모델이 배우는 것"은 다른 문제이고, 후자가 적어도 ALFWorld에서는 엄청난 차이를 만듭니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [EvoHarness-RL: Learning Self-Evolving Runtime Harness for Long-Horizon LLM Agents](https://arxiv.org/abs/2608.05446) (LLA@COLM 2026)
