---
title: "압축된 컨텍스트로 학습시키면 에이전트가 깨짐 — MemoryWalker가 정의한 조건부 불일치와 복구법"
date: 2026-09-03
draft: false
tags:
  - agent
  - harness
  - loop
  - RL
  - LLM
  - context-engineering
  - training
description: "Claude Code 같은 하네스는 롤아웃 중 컨텍스트를 압축하는데 이 트랜스크립트를 그대로 학습 데이터로 쓰면 조건부 분포가 트리로 갈라져 성능이 무너짐. LogitTree, 4D mask, SDCC 세 복구법과 학습 직렬화만 바꿔 EM 28.9→45.9이 된 결과를 정리함."
---

Claude Code, Qwen-Agent 같은 프로덕션 하네스는 롤아웃 중에 컨텍스트를 계속 압축함(eviction). 근데 이 압축된 트랜스크립트를 그대로 RL 학습 데이터로 쓰면 학습-추론 조건부 분포가 어긋남. MemoryWalker(arXiv:2609.00865)는 이 어긋남을 수식으로 정의하고 복구 방법 세 가지를 제안함. 핵심 수치가 말을 대신함. Qwen3-4B, 7개 웹검색 벤치마크 평균 EM(정답 문자열과 정확히 일치해야 점수를 주는 지표)에서 Naive-Compressed 학습이 28.9, 무압축 물리 트레이스 학습이 32.1, 정확 보정 LogitTree가 45.9. 롤아웃과 보상은 동일하고 학습 직렬화 방식만 바꿨는데 17포인트가 오름.

1. 문제의 정체가 명확함. 하네스가 컨텍스트에서 토큰을 빼내는 시점마다 그 이후의 실효 히스토리는 갈라짐. 학습 대상이 시퀀스에서 트리로 바뀌는 것. 기존 선형화는 두 함정에 빠짐. 오른쪽 경로만 남기면 time-travel leakage, 이미 지워진 정보를 알고 있던 시점의 로짓으로 학습하게 됨. 깊이우선 순회를 재생하면 train-inference mismatch, 실제 배포에서 모델이 본 적 없는 프리픽스로 학습하게 됨. 측정값도 있음. 학습 안 된 Qwen3-4B에서 압축 스트림 재생은 Δcomp = -22.8 nats(nats는 자연로그 기반 정보량 단위), 전체 트레이스 재생은 +18.5 nats. 부호가 반대고 크기가 비슷함. 어느 쪽으로 틀어도 손해라는 것.

![](/images/2026-09-03-memorywalker-context-compression/fig-1-p4.png)

2. 복구법이 세 개임. LogitTree는 트리를 K+1개의 루트-리프 분기로 쪼개서 정확하게 학습. 비용이 기준 대비 4.20배. 4D attention mask는 같은 목표를 어텐션 마스크 하나로 구현, 1.35배. 둘 다 gradient-equivalent라는 증명이 있음. 그리고 SDCC(Self-Distillation for Conditioning Consistency)가 실용 포인트. 각 eviction 지점에서 압축된 학생 정책과 압축 전 프리픽스를 복원한 stop-gradient 교사 정책 사이의 forward KL(교사 분포를 고정하고 학생 분포를 그쪽으로 맞추는 방향의 KL 발산)을 최소화함. 백워드(역전파) 1회로 끝나고(1.55배) 잔여 KL에 대해 학습-배포 TV 거리(두 확률분포 차이를 0~1로 재는 거리) 상한 O(√ε_KL)를 보장함. 교사 eviction 로그를 못 받는 블랙박스 하네스에도 적용 가능함.

![](/images/2026-09-03-memorywalker-context-compression/fig-2-p5.png)

3. 실험 규모가 진짜임. 편집기 3종 white-box(TC-RAG, AgentFold, MemexRL)와 하네스 2종 black-box(Claude Code, OpenCode). 학습 코퍼스 81,638개 복합 QA. 평가는 7개 웹검색 벤치마크 총 38,280문항을 실제 웹 검색(DashScope+Firecrawl)을 도는 에이전트 루프로 채점. AgentFold는 3,000토큰마다 fold, 압축비 0.06~0.15. 데모가 아니라 프로덕션 조건에 가까운 검증임.

4. 결과 읽기. 정확 보정 두 종류는 무압축 플로어를 그대로 유지하고 SDCC는 격차를 상당히 좁힘. Naive-Compressed는 eviction이 많은 배치에서 로짓 드리프트가 특히 커짐(0.0237 vs LogitTree 0.0133). 블랙박스 전이도 같은 순서. Claude Code에서 SDCC 37.5 EM(LogitTree 35.9), OpenCode에서 36.9 vs 35.0. Claude Code와 OpenCode는 내부 eviction 기록을 노출하지 않아 LogitTree/4D를 못 쓰는데 SDCC만 적용 가능함. 논문의 주장이 SDCC 우위가 아니라는 점도 신뢰를 줌. 비용을 감당할 수 있으면 정확 보정이 기준점이고, 비용이 안 되거나 블랙박스면 SDCC를 쓰라는 구도.

![](/images/2026-09-03-memorywalker-context-compression/table-1-p30.png)

5. 하네스를 만들거나 에이전트를 학습시키는 사람에게 적용 포인트는 세 줄임. 첫째, 압축 하네스로 수집한 트랜스크립트를 그대로 SFT/RL에 넣지 말 것. 조건부 불일치가 수치로 측정되는 실제 손해임. 둘째, eviction 로그를 남겨두면 LogitTree/4D 같은 정확 보정이 열림. 하네스를 자체 구축한다면 압축 시점 기록을 스키마에 넣을 것. 로그가 없는 상용 하네스라면 SDCC로라도 갭을 묶을 것. 셋째, 백워드 횟수가 병목이면 SDCC(1회)가 LogitTree(K+1회)의 현실적 대체임.

6. 내가 보기에 이 논문의 교훈은 더 넓음. "학습 데이터의 직렬화 방식"이 모델 성능을 두 자릿수로 움직인다는 것. 에이전트 로그를 학습에 쓸 때 나는 보통 데이터 내용만 봤는데, 그 로그가 어떤 관점(view)에서 쓰였는지, 즉 모델이 실제로 무엇을 본 상태였는지가 같이 와야 한다는 것. 컨텍스트 압축뿐 아니라 요약, 캐시 히트, 프리픽스 재사용이 있는 모든 하네스에서 같은 문제가 재현될 수 있음. 학습 파이프라인에 "모델이 본 뷰"와 "물리 트레이스"를 구분하는 컬럼을 두는 것부터 시작할 만함.

원문: [arXiv:2609.00865](https://arxiv.org/abs/2609.00865).
