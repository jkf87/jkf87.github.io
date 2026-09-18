---
title: "에이전트 메모리를 모델 파라미터 안에 넣는다 — 메모리 파운데이션 모델 Metis 첫 검증"
date: 2026-07-31T22:00:00+09:00
draft: false
tags:
  - agent
  - memory
  - foundation-model
  - LLM
  - harness
  - native-memory
  - architecture
  - mid-training
  - automation
  - loop
  - tool-use
description: "외부 RAG 메모리의 최적화 단절·비용 문제를 지적하고 기억을 순방향 패스로 갱신하는 메모리 파운데이션 모델 Metis를 정리했다. remember·forget·update·reflect 4연산 학습 설계와 실무적 시사점."
---

에이전트 메모리가 전부 외부 RAG로 구현되어 있는데, 이걸 모델 안으로 밀어넣은 첫 사례가 나옴. 기억을 컨텍스트가 아니라 파라미터에 넣는 방향성이라 정리해둘 가치가 큼. 원문은 [arXiv:2607.26760](https://arxiv.org/abs/2607.26760).

1. 문제의식은 공감됨. MemGPT·Mem0 같은 외부 메모리는 저장과 검색이 이산적 연산이라 그레이디언트가 흐르지 않음. "뭘 저장하면 미래 추론에 도움이 될지"를 end-to-end로 최적화할 수 없음. 게다가 검색-재정렬-컨텍스트 결합-다시 prefill 비용이 매 추론마다 발생하고 대화가 길수록 선형으로 늘어남.

![](/images/2026-07-31-metis-memory-foundation-model/gifs/filing-cabinet-retrieval.gif)

![메모리 파운데이션 모델 개요](/images/2026-07-31-metis-memory-foundation-model/fig-1-p2.png)

2. 그래서 정의한 게 메모리 파운데이션 모델임. 파라미터 자체가 θt로 시간에 따라 변하는 모델. 기억·망각·갱신이 외부 룰이 아니라 모델의 순방향 계산 자체에서 수행됨. CoT가 추론을 모델 안에 넣었듯 기억을 내장하는 것이라는 프레임이 직관적임.

![](/images/2026-07-31-metis-memory-foundation-model/gifs/elephant-never-forgets.gif)

3. 구현이 영리함. 트랜스포머 층마다 메모리 블록을 추가하는데, 그레이디언트 없이 순방향 패스 한 번으로 메모리를 갱신함. 중요도 점수로 상위 토큰만 남기고, 할인 인자를 곱해 이전 정보를 점진 감쇠시키며 새 정보를 덮어쓰는 방식. 게이트 기반이라 순방향 계산만으로 끝남.

![Metis 아키텍처](/images/2026-07-31-metis-memory-foundation-model/fig-2-p7.png)

4. 훈련 데이터 설계가 제일 배울 점임. 대화 데이터를 그냥 모은 게 아니라 메모리 연산을 명시적으로 가르치는 구조를 합성함. Remember(A 말함→A 질의), Update(A₁ 후 A₂→최신 값 질의), Forget(취소 후 질의), Reflect(여러 사실에서 다중 홉 추론) 네 연산에 명시성·노이즈 차원을 직교시켜 약 100만 샘플을 만듦. 이 네 연산 분해는 외부 메모리 시스템을 설계할 때도 그대로 쓰이는 체크리스트임 — 메모리 시스템이 이 네 가지를 각각 처리하는지 따져보면 설계 구멍이 보임.

![훈련 데이터 구성](/images/2026-07-31-metis-memory-foundation-model/fig-3-p23.png)

5. 결과는 4B 규모에서 full-context baseline과 경쟁력 있는 성능, OOD 벤치마크(LoCoMo, LongMemEval)에서도 RAG와 견줄 만함. 특히 update와 reflect에서 외부 메모리 대비 우위. 지연시간은 고정 크기 상태라 대화가 길어도 선형 증가하지 않음.

![full-context baseline 대비 결과](/images/2026-07-31-metis-memory-foundation-model/fig-4-p25.png)

6. 필자 실무 관점. 당장은 도입할 수 없는 기술임 — 4B 프로토타입이고 상용 모델 통합 검증이 남았음. 그래도 두 가지가 지금 쓸모 있음. 첫째, 외부 메모리의 약점 진단 기준. 현재 파이프라인의 메모리가 "뭘 저장할지"를 휴리스틱으로 정하는데, 그 휴리스틱이 네 연산을 전부 커버하는지 점검하면 개선 지점이 나옴. 특히 forget과 update가 빠진 외부 메모리가 많음. 둘째, 방향성 예측. 메모리가 모델 안으로 흡수되면 하네스는 메모리 관리 대신 검증·권한·루프 제어에 집중하게 됨. 하네스 투자 방향을 그쪽으로 잡는 게 맞음.

![규모별 스케일링](/images/2026-07-31-metis-memory-foundation-model/fig-5-p26.png)

7. 문제제기. 고정 크기 파라미터에 무한 컨텍스트를 못 담는 근본 트레이드오프가 있고, 매우 긴 시퀀스에서 정보 손실과 잠재 공간의 정보 혼란이 관찰됨. 백본 교체 시 전이 검증도 초기 수준임. 상용 규모에서 RAG를 이길지는 미지수임.

8. 남는 결론. 추론의 내장화(CoT) 다음은 기억의 내장화라는 논문의 로드맵에 동의함. 완전 실현 전까지는 외부 메모리가 현실이니, 외부 시스템을 네 연산 기준으로 점검하고, 모델 쪽 흡수가 진행되면 하네스의 책임 범위를 옮겨가는 게 순서임.
