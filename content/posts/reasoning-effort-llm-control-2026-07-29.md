---
title: "언제 비싸게 생각하게 할 것인가 — reasoning effort는 정확도 옵션이 아니라 원가 옵션임"
date: 2026-07-29
tags:
  - LLM
  - reasoning-models
  - inference-scaling
  - RLVR
  - agents
categories:
  - AI
  - Agent
description: "Sebastian Raschka의 Controlling Reasoning Effort in LLMs를 실무 관점으로 정리. reasoning effort는 단순 UI 옵션이 아니라 post-training과 inference-time compute가 만나는 조절 노브다."
aliases:
  - /posts/reasoning-effort-llm-control-2026-07-29
draft: true
refactor_hub: agent-rl-04
refactor_status: queued
---

"Reasoning effort: low, medium, high"라는 메뉴가 이제 이상하지 않음. 모델을 고르던 시대에서 같은 모델 안에서 얼마나 오래 생각하게 할지 고르는 시대가 됨. Sebastian Raschka의 [Controlling Reasoning Effort in LLMs](https://magazine.sebastianraschka.com/p/controlling-reasoning-effort-in-llms)를 읽고 정리함 — 핵심은 reasoning effort가 prompt trick이 아니라 비용과 정확도 사이를 움직이도록 학습된 조절 노브라는 것.

1. 정의부터. reasoning model은 인간처럼 사유하는 모델이 아니라 최종 답만 내는 대신 중간 reasoning trace(중간 풀이 과정 텍스트)를 만들어가며 문제를 푸는 모델임. RLVR(검증 가능한 보상 RL, 정답을 프로그램으로 확인할 수 있는 과제에서 보상을 주는 강화학습)로 수학·코딩에서 정답 보상을 주면 풀이·되돌아가기·자기수정 행동이 저절로 학습됨 — DeepSeek-R1의 "Aha moment". 긴 생각을 쓰라고 가르친 게 아니라 맞는 답을 찾는 과정에서 긴 생각이 유용해지도록 만든 것.

2. `<think>` 태그 오해부터 풀어야 함. 이 태그는 reasoning 능력을 만드는 장치가 아니라 trace의 시작과 끝을 표시하는 경계선임. UI가 중간 풀이를 감추고 최종 답만 보여줄 수 있는 것도 이 분리 덕분. format reward가 붙어서 모델이 태그 안에 trace를 넣는 법을 배우는 것 — 중요한 건 태그가 아니라 그 형식을 따르게 만든 post-training과 보상 구조임.

3. thinking on/off의 내부. Qwen3의 enable_thinking=False는 대체로 assistant 응답 앞에 빈 `<think></think>` 블록을 prefill하는 방식 — "생각은 이미 끝났으니 바로 답하라"는 상태에서 생성을 시작하는 것. Thinking Mode Fusion 같은 SFT(정답 예시로 가르치는 지도학습)로 /think와 /no_think 예시를 섞어 학습함. 모드 전환은 프롬프트 지시가 아니라 그 지시를 따라본 데이터와 훈련 흔적이 있어야 작동한다는 것 — 임의 모델에 "think less"라고 쓴다고 스위치가 생기지 않음.

4. reasoning effort의 본질. 모델 선택은 다른 scale의 모델을 고르는 일이고 effort 조절은 같은 모델이 추론 시점에 더 많은 토큰과 컴퓨트를 쓰게 허용하는 일. effort를 올리면 성능도 오르지만 높은 구간에서 수익 체감이 옴 — 돈 두 배 쓰고 점수 조금 오르는 구간이 생긴다는 것.

5. 그래서 이 메뉴의 정체는 unit economics 옵션임. 최고 성능만 보면 항상 max를 고르고 싶지만 서비스는 latency, API 비용, 사용자 체감, 재시도 비용을 같이 봄. "이 모델이 제일 똑똑한가"보다 "이 작업에 얼마만큼의 생각을 사는 게 맞는가"가 질문이 되는 것.

6. effort level은 학습 때 만들어짐. system prompt에 effort label을 넣고, SFT에서 low엔 짧은 target high엔 긴 target을 붙이고, RLVR에서 토큰 페널티 λ(e)(생성 길이에 부과되는 비용 계수, effort 등급마다 다르게 설정)를 effort마다 다르게 주는 방식. Inkling은 effort를 0~1 연속값으로 다루는데 — UI에선 슬라이더, 하네스에선 router가 세밀하게 조절할 수 있는 숫자임.

7. 공개 모델 비교에서 세 가지 공통 패턴. chat template과 SFT로 모드의 문법을 만들고(DeepSeek V4, GLM-5), RL에서 길이와 비용을 조정하고(Inkling, Nemotron), hard budget에 견디는 훈련을 넣음(Nemotron은 trace를 무작위 예산에서 자른 예시, Kimi는 budgeted/unconstrained phase). 비슷한 UI 라벨 뒤에 완전히 다른 훈련 레시피가 숨어 있다는 것 — 어떤 모델의 "medium"과 다른 모델의 "medium"은 같은 의미가 아님.

8. 벤치마크를 볼 때도 "무슨 모델인가"만으론 부족함. 어떤 effort였는지, 예산은 얼마였는지, trace를 강제로 잘랐는지, tool-use 작업에서 같은 설정이었는지까지 봐야 함. 이건 하네스 효과 연구들과 같은 결론 — 보고된 점수의 조건을 안 보면 비교가 성립하지 않는다는 것.

9. 여기서 내 에이전트 운영에 적용할 것. 한 작업 안에서도 단계별로 필요한 생각 깊이가 다름 — 파일 목록 훑기는 low, 실패 원인 좁히기는 medium 이상, 패치 전략과 회귀 리스크는 high, 검증된 명령 실행은 다시 low. 전부 max로 돌리면 비용이 터지고 전부 low면 어려운 순간에 무너짐. effort router를 만드는 것이 하네스 설계의 다음 영역이라는 것.

10. 사용자 override도 남겨둘 것. 자동 선택이 기본이 되더라도 "이번 건 high로 가자"는 사람의 의사결정은 필요함 — 빨리 대충 보고 싶을 때와 비용 들여서 끝까지 물고 늘어져야 할 때가 있으니까.

11. 결론. reasoning effort는 "모델이 생각한다"는 낭만을 걷어내고 토큰·지연·보상·예산이라는 공학 단위로 바꿔줌. 좋은 에이전트 하네스의 조건에 "생각 예산을 언제 올리고 내리는가"가 포함되는 것. 근데 모델마다 effort의 의미가 다르니 결국 내 워크로드에서 effort별 비용-성능 곡선을 직접 측정하는 수밖에 없다는 결론임.

![Reasoning effort 대시보드](/images/reasoning-effort-llm-control-2026-07-29/hero.svg)

![GPT-5.6 Sol의 effort별 benchmark 점수](/images/reasoning-effort-llm-control-2026-07-29/fig01-gpt56-effort.png)

![training scaling vs inference scaling](/images/reasoning-effort-llm-control-2026-07-29/fig04-training-vs-inference-scaling.png)

![Qwen3 thinking 토글](/images/reasoning-effort-llm-control-2026-07-29/fig14-qwen3-thinking-toggle.png)

![비용-성능 effort 곡선](/images/reasoning-effort-llm-control-2026-07-29/fig19-cost-performance-effort.png)

![effort-conditioned training](/images/reasoning-effort-llm-control-2026-07-29/fig21-effort-conditioned-training.png)

![두 스케일링 축](/images/reasoning-effort-llm-control-2026-07-29/fig23-two-scaling-axes.png)

![공개 모델 비교](/images/reasoning-effort-llm-control-2026-07-29/fig32-open-weight-comparison.png)
