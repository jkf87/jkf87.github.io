---
title: "에이전트는 도구가 죽어도 옛 루틴을 버리지 못함 — set-shifting 실험 교훈"
date: 2026-07-22T22:00:00+09:00
summary: "도구 그룹의 신뢰성이 조용히 바뀌었을 때 에이전트가 어떻게 무너지는지 측정한 연구. 프롬프트 지시보다 도구 설명 프레이밍이 더 강한 개입 채널이라는 발견까지 정리함."
tags: ["agent", "harness", "LLM", "tool-use", "cognitive-flexibility", "evaluation", "WCST"]
categories: ["AIAgent"]
sources:
  - title: "Set-shifting Behavioral Test for Harnessed Agents"
    url: "https://arxiv.org/abs/2607.13396"
    authors: ["Ziwei Ye", "et al."]
    date: 2026-07-15
draft: true
refactor_hub: harness-self-improve-07
refactor_status: queued
---

API가 죽거나 백엔드가 장애로 바뀌어도 에이전트는 예전에 성공했던 도구를 계속 호출하는 경우가 많음. 인지심리학의 WCST(Wisconsin Card Sorting Test, 정답 규칙이 몰래 바뀌었을 때 사람이 규칙 전환을 얼마나 잘하는지 재는 고전 실험)를 에이전트 하네스로 옮긴 연구가 이 현상을 측정했음. 원문은 [arXiv:2607.13396](https://arxiv.org/abs/2607.13396).

1. 실험 설계. 기능이 같지만 이름·설명이 다른 도구 그룹들을 하네스에 마운트하고, 세션 도중 신뢰할 수 있는 그룹을 조용히 바꿈. 스키마도 설명도 그대로라서 도구를 호출해봐야 실패 응답이 돌아오는 게 유일한 단서임. 스케줄링, DevOps 인시던트 분류, 멀티클라우드 스토리지 3개 도메인이었음.

2. 각 shift 지점에서 역전(옛 그룹 복귀), 신규 이동(새 그룹), 비이동 컨트롤로 갈라지는 분기 설계를 써서 같은 컨텍스트에서 출발하는 페어 비교를 만듦. 90턴 안에 2개 분기 층, 9개 엔드포인트. 이 설계 자체가 내 실험 파이프라인에 참고할 만함.

![실험 설계: 도구 그룹 신뢰성 전환](/images/2026-07-22-set-shifting-harnessed-agents/fig-2-p4.png)

3. 발견 1. 에이전트는 shift 후 몇 턴 안에 소수의 반복 루틴으로 수렴함. 그리고 shift가 일어나도 그 루틴에서 잘 안 벗어남. bimodal(두 극단만 나타나는 분포) 패턴이 뚜렷했음. 완전히 전환하거나 아예 못 하거나. 절반쯤 적응하는 경우가 거의 없음.

![shift 후 루틴 수렵 패턴](/images/2026-07-22-set-shifting-harnessed-agents/fig-3-p6.png)

![](/images/2026-07-22-set-shifting-harnessed-agents/gifs/same-thing-every-night-brain.gif)

4. 발견 2. 실패 모드가 모델마다 질적으로 다름. mimo-v2.5는 예전에 쓴 도구 그룹들을 섞어서 계속 호출하고 새 그룹 탐험을 안 함. deepseek-v4-pro는 궤적 시작에 고른 단일 그룹에 고착해서 그게 신뢰 불가능해져도 전환을 안 함. 같은 하네스, 같은 도구인데 사전 학습이 도구 선택 편향을 결정한다는 뜻임.

![](/images/2026-07-22-set-shifting-harnessed-agents/gifs/why-so-stubborn.gif)

5. 발견 3. set-shifting 정확도 Φ는 올바른 그룹을 post-shift 전 구간에서 호출할 결합 확률임. 단일 shift에서 60%대가 2단계 shift에서 20% 이하로 추락함. shift가 누적될수록 회복이 극히 드묾.

![set-shifting 정확도 Φ 분포](/images/2026-07-22-set-shifting-harnessed-agents/table-1-p6.png)

6. 개입 실험이 실무 포인트임. 정책 프롬프트로 "도구를 전환하라"고 지시하면 deepseek의 고착은 줄지만 도구를 자꾸 바꾸면서도 정답을 못 맞추는 over-switching이 생김. 그리고 mimo에는 아무 효과가 없었음. 하나의 시스템 프롬프트 최적화가 모든 모델에 통한다는 가정이 깨지는 지점임.

7. 제일 흥미로운 건 구조 개입임. 같은 도구를 "경쟁하는 제공자"로 소개하면 에이전트가 하나에 올인하고, 그게 신뢰 가능 그룹일 확률이 올라감. "보완하는 관측 피드"로 소개하면 매 턴 모든 그룹을 섞는 루틴에 갇힘. 32쌍 중 26쌍에서 경쟁 프레이밍이 Φ를 올렸고(p=3×10⁻⁴, 즉 우연으로 이 차이가 날 확률이 10만분의 3이라는 뜻), 프롬프트가 닿지 않았던 mimo에까지 효과가 갔음. 도구 설명의 프레이밍이 지시보다 강한 개입 채널일 수 있다는 것임.

![경쟁 vs 보완 프레이밍 개입 효과](/images/2026-07-22-set-shifting-harnessed-agents/fig-4-p7.png)

8. 내 하네스 설계에 반영할 것 세 가지. 첫째, 대체 가능한 도구는 경쟁 관계로 설명을 쓰고, 함께 써야 하는 도구만 보완으로 씀. 둘째, 실패 응답이 반복되면 강제로 대안 그룹을 시도하게 하는 구조(재시도 상한 + 폴백 목록)를 하네스에 하드코딩함. 모델의 자발적 전환을 기대하지 않는 게 정확함. 셋째, 첫 몇 턴의 도구 선택이 세션 전체를 규정하는 경우가 있어서 초기 컨텍스트 설계에 가장 공을 들임.

![도메인별 결과 정리](/images/2026-07-22-set-shifting-harnessed-agents/table-4-p12.png)

9. 문제제기. 오픈웨이트 2개 모델만 테스트해서 프론티어 모델에서 같은 패턴인지는 미확인임. 그리고 실패 응답만 단서인 극단적 설정이라 실무에서는 에러 메시지 텍스트가 더 많은 정보를 줌. 근데 방향 자체는 실무 체감과 일치함. 도구 호출 이력이 컨텍스트를 채우고 과거 성공이 새 시도를 억제하는 구조는 내 자동화 로그에서도 봤던 패턴임.

10. 결론. 에이전트 유연성은 단일 턴 정확도가 아니라 환경 변화 적응력으로 측정해야 함. 벤치마크 코드는 [GitHub](https://github.com/zwycl/wcst-tool-bench)에 공개돼 있어서 내 에이전트의 경직성을 직접 돌려볼 수 있음.

도구 사용 루프 설계 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 겪어볼 수 있음.
