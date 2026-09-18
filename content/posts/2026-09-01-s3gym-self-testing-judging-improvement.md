---
title: "자기테스트·자기판단이 성능 개선로 이어지는지 실제로 측정함 — S3Gym 결과"
date: 2026-09-01
tags: [agent, LLM, self-improvement, benchmark, memory, RL]
draft: false
description: "경험은 도움이 될 때가 있지만 자동 개선을 보장하지 않음. 판단 품질과 다음 성능 향상의 상관이 거의 0이었다는 결과와 과제 구조별 최적 반영 방식을 정리함."
---

에이전트가 스스로 테스트하고 스스로 점수를 매기고 그 경험을 다음 행동에 쓰면 정말 좋아지는가. S3Gym이 이 질문을 따로 재는 벤치마크를 만들었음. 원문은 [arXiv 2608.31100](https://arxiv.org/abs/2608.31100).

1. 구성은 3단임. Self-Testing(relaxed 설정에서 여러 에피소드를 돌며 행동과 관찰을 모음), Self-Judging(각 transition에 스스로 점수를 매기고 판단), Self-Improvement(그 경험을 History ICL, Summary Memory, Parameter Training 중 하나로 반영하고 strict held-out 설정에서 재평가)임. 환경은 Chess, Minesweeper, Tetris, Snake, Plants-vs-Zombies, Trust Evolution 등 7개 텍스트 게임임.

2. 중요한 장치가 둘임. 탐색 seed와 평가 seed가 분리되고 평가 trajectory는 경험에 다시 들어가지 않음. 외운 행동이 아니라 경험에서 뽑은 규칙이나 정책이 옮겨가는지를 보는 것임. 내 자동화 평가에도 이 분리 원칙이 그대로 필요해서 바로 챙겼음.

3. 결과의 첫 줄은 "경험은 도움이 될 때가 있지만 자동 개선을 보장하지 않음"임. Summary Memory는 규칙으로 압축되는 게임(Nullify, Tetris, Trust)에서 좋았음. GPT-5.5/Trust에서는 요약이 opponent-conditioned policy로 바뀌며 +66.89를 만들었음. 근데 현재 상태 디테일이 중요한 게임(Minesweeper, PvZ, Snake)은 raw history가 더 좋았음. "무조건 요약해서 메모리에 넣자"가 답이 아니라 과제 구조에 따라 갈린다는 것임.

4. Parameter Training은 강하고 불안정함. Qwen3-8B를 20개 체크포인트로 본 결과 Trust Evolution은 0점에서 최대 30점까지 올라갔는데 PvZ는 초기 23점에서 업데이트된 모든 체크포인트가 6점을 받고 회복하지 못했음. 같은 훈련 경로가 환경에 따라 정반대 결과를 냄. 논문은 원인을 단정하지 않고 exploration overfitting, 설정 mismatch, 잘못된 자기판단 굳화 가능성만 조심스럽게 제시함.

5. 제일 중요한 발견은 자기판단과 개선의 단절임. 7개 모델·7개 게임, 98런, 116,117개 transition을 비교했을 때 판단 agreement와 다음 strict 점수 게인의 상관이 ρ=-0.010, calibration 오차 반대값과 게인의 상관도 ρ=-0.018로 거의 신호가 없었음. 좋은 행동을 알아보는 단계와 그 판단을 다음 정책으로 바꾸는 단계가 분리되어 있다는 뜻임.

6. 판단 자체도 부분적임. Minesweeper, Nullify, PvZ, Snake, Tetris에서 event agreement가 0.82-0.881까지 나오지만 이건 zero-reward transition이 많은 영향도 있음. PvZ는 agreement가 높아도 NMAE가 0.882로 큼. 좋아 보이는 행동인지 정도는 알아도 가치 크기를 잘 맞춘다는 뜻은 아님.

7. 내 업무에 적용한 프레임. "지난 실행에서 배웠다"는 말을 하려면 최소 세 개를 나눠봐야 함. 테스트를 잘했는가(실패가 드러나는 케이스를 스스로 만들었는가), 판단을 잘했는가(로그의 성공/실패 원인을 환경 신호와 맞게 봤는가), 반영을 잘했는가(다음 실행에 쓸 규칙·메모리·스킬·코드 변경으로 바꿨는가)임. 그리고 내 자동화 로그 관리에도 이 원칙을 붙였음. 상태 디테일이 중요한 작업(디버깅, 데이터 처리)은 raw 로그를 남기고, 규칙이 잘 압축되는 작업(운영 절차, 반복 검사)은 요약 메모리를 남김.

8. 문제제기. 텍스트 게임 벤치마크라 실무 시스템의 API, 권한, 비동기 상태, 사람 피드백을 그대로 안 담음. Parameter Training 결과는 Qwen3-8B 중심 별도 실험이라 컨텍스트 방식과 완전히 같은 조건 비교가 아님. PvZ 부정 전이의 원인도 확정이 아님.

9. 결론. 자기판단이 정확해도 자기개선이 되는 게 아님. 로컬 보상을 맞히는 능력과 피드백을 상태 추상화·의사결정 규칙·탐색 전략으로 바꾸는 능력은 별개이고, 후자가 별도로 설계돼야 한다는 게 이 벤치마크의 메시지임. 프로젝트 페이지는 [self-developing-agents.github.io](https://self-developing-agents.github.io/)에 공개돼 있음.
