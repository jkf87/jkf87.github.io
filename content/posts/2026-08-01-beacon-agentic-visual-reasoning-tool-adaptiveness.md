---
title: "도구를 쥐여주면 오히려 성능이 떨어짐 — Beacon이 짚은 도구 사용의 역설과 해법"
date: 2026-08-01
tags:
  - agent
  - tool-use
  - visual-reasoning
  - LLM
  - reinforcement-learning
  - RL
  - harness
  - MLLM
  - automation
  - GRPO
  - adaptive
  - evaluation
draft: false
---

에이전트에게 도구를 주면 똑똑해진다고 믿었는데 분석 결과가 반대였음. 도구 사용 RL 훈련을 거친 기존 모델들이 쉬운 문제에서 도구를 쓰다가 오히려 틀리는 패턴을 보였고 도구 이득이 거의 상쇄됐음. Beacon은 이 문제를 "언제 도구를 쓸지 아는 능력" 관점에서 정의하고 풀었음.

1. 배경. 시각 추론 에이전트는 이미지를 자르고 주석 달고 픽셀 연산 코드를 생성해서 문제를 풂. Thyme, Metis 같은 최근 모델이 다 이 패러다임임. 근데 베이징대·Kling 팀이 정밀 분석하니 도구를 쓸 때와 안 쓸 때의 정확도 차이가 거의 없었음. Metis는 -2.58%까지 기록함.

![도구 사용 역설](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-2-p2.png)

2. 원인은 둘임. 첫째, 무차별 도구 호출. 난이도와 무관하게 항상 도구를 쓰거나 항상 안 씀. 텍스트만으로 풀리는 문제에 도구를 부르는 비적응적 행동임. 둘째, 도구 사용 손해가 이득보다 크거나 비슷함. 어려운 문제를 풀어주는 Tool-Gain보다 쉬운 문제를 망치는 Tool-Harm가 같거나 큰 구조임.

3. 그래서 평가 프레임부터 다시 만듦. Mode Adaptiveness는 각 문제를 텍스트 전용으로 5번 추론해 text-easy(4번 이상 정답)와 text-hard(1번 이하)로 분류하고, easy에서 도구를 안 쓼을(easy) ratio와 hard에서 쓼을(hard) ratio를 측정함. 기존 모델들의 MA 평균은 50% 부근. 무작위 전략과 다르지 않았다는 뜻임.

4. Tool Effect는 실제 성능 영향을 정량화함. text-hard에서 도구로 맞춘 비율이 Tool-Gain, text-easy에서 도구 쓰다가 틀린 비율이 Tool-Harm임. 기존 모델들의 ΔTE는 거의 0이었음. 전체 정확도가 올라가 보였던 건 SFT 데이터 효과지 도구 사용 자체의 효과가 아니었다는 게 밝혀진 것임.

![MA와 TE 지표](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-3-p5.png)

5. 해법 첫 조각은 Necessity-Aware Adaptive Reward임. 기존 GRPO는 정답이면 1, 오답이면 0이라 "항상 도구 쓰기"가 안전해 보임. NAAR는 텍스트로 풀리는 문제에선 텍스트 정답에 1.0, 도구 사용 정답에 0.25를 줌. 텍스트로 못 푸는 문제에선 도구 정답에 1.0임.

6. 이 설계의 핵심은 도구를 써서 맞혀도 풀 점수를 안 준다는 것임. easy 문제에서 도구를 쓰면 75%가 깎임. 그러면 모델이 자연스럽게 "이 문제는 텍스트로 되는가"를 내부 판단하게 됨. 그리고 난이도 라벨링을 교사 모델이 아니라 현재 정책 성능 기준으로 온라인으로 해서 분포 불일치도 막음.

7. 두 번째 조각은 Hint-Guided Capability Expansion임. RLVR의 근본 한계는 정책이 처음부터 못 푸는 문제는 학습 신호가 없다는 것. 전 롤아웃이 틀리면 그룹 내 어드밴티지가 무의미함.

8. HCE는 이걸 힌트로 돌파함. 8번 롤아웃해도 전부 틀리면 Gemini 3.1 Pro가 정답 없는 힌트를 만들고, 힌트를 넣어 다시 8번 굴림. 그 궤적으로 학습하되 정책 업데이트 시에는 힌트를 뺀 원래 프롬프트로 importance sampling ratio를 계산함. 힌트 의존 없이 힌트가 도와준 경험만 흡수하는 구조임.

![Beacon RL 훈련](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-4-p7.png)

9. 결과. 13개 벤치마크에서 오픈소스 평균 1위. ChartQAPro +16.82, GameQA +10.60, HR-Bench 4K +6.17. 그리고 ΔTE가 +1.96~+5.51로 양수가 됨. 기존 모델들의 0과 대비되는, 도구 사용이 실제로 순수 성능을 올렸다는 증거임.

10. 훈련 중 패턴 변화도 확인함. 초반엔 거의 모든 문제에 도구를 쓰다가 점점 text-easy에서는 줄이고 text-hard에서는 유지하는 적응적 패턴으로 바뀜. NAAR가 의도한 대로 행동이 진화한 것임.

![도구 사용 패턴 변화](/images/2026-08-01-beacon-agentic-visual-reasoning-tool-adaptiveness/fig-6-p13.png)

11. 실무 채점. 이건 시각 추론만의 이야기가 아님. 터미널 에이전트, 웹 에이전트, 딥리서치 에이전트 전부 같은 문제를 안고 있음. 도구를 많이 두는 게 능사가 아니라 언제 쓸지 아는 게 능력임. 하네스 설계에서 도구 호출 비용을 차등 두는 게 그 역할을 대신할 수 있음.

12. 우리 파이프라인에 바로 적용할 것. 첫째, 태스크별로 "도구 없이 풀리는지"를 먼저 측정하고 easy/hard를 나눌 것. 둘째, easy 태스크의 도구 사용에 비용 페널티를 둘 것. 셋째, 성능 평가는 전체 정확도 말고 Tool-Gain과 Tool-Harm을 분리해 볼 것. 그래야 도구 인프라가 진짜 도움인지 알 수 있음.

13. 그리고 HCE 패턴은 범용임. 정책이 전부 실패하는 태스크에 힌트를 넣어 성공 궤적을 만들고 힌트 없이 학습하는 구조는 코딩 에이전트나 수학 추론 등 모든 RLVR 설정에서 재사용 가능함.

원문: [arXiv:2607.28595](https://arxiv.org/abs/2607.28595)
