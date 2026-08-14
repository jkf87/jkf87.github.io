---
title: "SHAPER: 동결된 모델 그대로 쓰면서 스킬과 하네스만 진화시키는 embodied 에이전트"
date: 2026-08-14
tags:
  - agent
  - harness
  - LLM
  - embodied
  - self-evolution
  - frozen-model
  - skill-evolution
  - VLM
  - Microsoft
  - loop
---

모델은 그대로 두고, 스킬과 하네스만 고쳤더니 embodied 에이전트 성능이 확 올라간다. Microsoft Research의 SHAPER는 VLM 플래너와 VLA 실행기를 동결한 채, 텍스트 스킬과 Python 하네스 코드만 롤아웃 피드백으로 진화시키는 프레임워크다. $3 미만의 API 비용으로 SFT를 넘어선다.

## SHAPER가 보는 에이전트 시스템

에이전트를 네 개 컴포넌트로 쪼갠다.

- **VLM 플래너** (Qwen3.6-27B) — 상위 계획, 동결
- **실행기** (VLA 액터 또는 환경 API) — 로우레벨 액션, 동결
- **스킬** — 플래넸 프롬프트의 텍스트 절차 지시, 최적화 대상
- **하네스** — `build_context()` Python 함수, 최적화 대상

파라미터는 얼려두고, 비파라미터 부분(스킬 + 하네스)만 환경 롤아웃 피드백으로 고친다.

## 어떻게 진화시키는가

![SHAPER 개요](/images/2026-08-14-shaper-skill-harness-evolution-embodied-agents/fig-2-p4.png)

핵심 아이디어는 "텍스트 그래디언트"다. 멀티모달 궤적 전체를 옵티마이저에 보여주면 컨텍스트가 폭발한다. 대신:

1. 각 턴의 before/after 관찰 쌍을 턴별 판정(judge)으로 압축
2. 에피소드 단위 요약(summarizer)으로 다시 압축
3. 배치 전체 통계와 합쳐서 텍스트 그래디언트 Γ(c) 생성
4. 동결된 모델을 옵티마이저 프롬프트로 호출해서 새 스킬/하네스 제안
5. 샌드박스 검증 → 검증 세트 평가 → Top-K 빔 유지

스킬 먼저 진화시키고, 선택된 스킬을 고정한 다음 하네스를 진화시키는 2단계 스케줄이다.

## VLABench: 로봇 조작에서의 결과

VLABench는 언어 조건부 로봇 조작 벤치마크. π₀ VLA 실행기를 그대로 쓰고 상위 플래너만 SHAPER로 진화시켰다.

테스트타임 스케일링(MG-Select, VOTE)은 direct execution보다 못했다. 샘플링을 많이 한다고 안정적인 향상이 나오지 않는 환경에서, 스킬+하네스 진화는 +11.25포인트를 만들어냈다.

분포 이동(C2~C4)에서 개선 폭이 더 컸다. 특히 C3(다른 태스크 형태)에서 Seed 40.0% → Full SHAPER 50.0%.

## ESI-Bench: 공간 지능에서의 결과

ESI-Bench는 에이전트가 능동적으로 시야를 움직이면서 증거를 모아야 하는 벤치마크다.

동결된 27B 모델이 하네스 진화까지 더하니 GPT-5 Passive Single-view 참고치(40.3%)를 매크로 정확도 42.9%로 넘어섰다.

거울 반사 카테고리가 가장 극단적이다: Skill Evolution 20.0% → Full SHAPER 60.0%.

하네스가 바뀌면서 생긴 일을 구체적으로 보면:

- 기존: 최근 5개 뷰만 유지 → 초반에 본 거울 속 대상이 사라짐 → 30스텝 동안 왔다갔다 하다가 "모르겠다"
- 진화 후: 전체 이력에서 의미 있는 프레임 3개 선택 → 결정론적 crop 추가 → 1스텝의 거울 이미지를 7스텝의 후보 3개와 비교 → "가운데" 정답

![ESI-Bench 하네스 진화 사례](/images/2026-08-14-shaper-skill-harness-evolution-embodied-agents/fig-4-p9.png)

## 스킬 진화의 실제 효과

![VLABench 스킬 진화](/images/2026-08-14-shaper-skill-harness-evolution-embodied-agents/fig-3-p8.png)

Seed 스킬은 "관찰하고 서브태스크 내라"가 전부. 진화된 스킬은:

- 태스크 의도 → 짧은 정규 명령 매핑
- 턴마다 진행 상태 분류 (성공/실패/부분/정체)
- 같은 명령 반복 감지 → 다른 명령 형태로 전환
- VLA 액터 명령 분포에 맞춘 스텝 예산 조정

실제 에피소드에서 seed는 같은 retrieval 명령을 반복하다 400스텝 한도 도달. 진화된 스킬은 부분 성공 감지 → pick-up으로 전환 → 297스텝에 완료.

## 비용 구조

진화 1회당 API 비용이 $2.25~$2.83이다. 여기에 시뮬레이터/GPU 비용은 별도.

진화가 끝나면 스킬과 하네스는 고정된다. 배포 횟수가 늘어도 per-deployment 비용이 0이다. 테스트타임 스케일링과 근본적으로 다른 지점이다.

## 이전 연구와 비교

SHAPER 이전에 스킬만 진화시키는 연구(SkillOpt, EmbodiSkill)와 하네스만 합성하는 연구(AutoHarness)가 있었다. SHAPER는 둘 다 하는 첫 프레임워크다.

## 남은 과제

논문도 인정하는 한계: cross-embodiment transfer(다른 로봇 형태로의 전이)와 실물 로봇 검증은 아직이다. VLABench와 ESI-Bench는 시뮬레이션 환경이다.

원문: [SHAPER: Self-Evolving Embodied Agents via Skill-Harness Evolution](https://arxiv.org/abs/2608.11350) (Microsoft Research, 2026-08)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
