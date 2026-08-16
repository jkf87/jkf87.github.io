---
title: "SkillSentry: Claude Code와 Codex의 스킬 실행을 런타임 훅으로 감시하니 성공률이 24.1% 올랐다"
date: 2026-08-16
tags:
  - agent
  - LLM-agent
  - tool-use
  - harness
  - loop
  - runtime-assurance
  - skills
  - Claude-Code
  - Codex
source: arxiv
source_url: https://arxiv.org/abs/2608.09253
authors:
  - conanssam
draft: false
---

![SkillSentry 접근 개요](/images/2026-08-16-skillsentry-skill-runtime-assurance/fig3-overview.png)
그림 출처: arXiv:2608.09253 Fig. 3

arXiv:2608.09253 (2026-08-10, Fudan University) 정리했습니다. 핵심은 이겁니다. 에이전트에 스킬 문서를 넣어줘도 실행이 흔들리는 문제를, <span style="background-color: #fff59d"><strong>모델도 에이전트도 수정하지 않고 런타임 훅으로 감시하고 보정</strong></span>하는 쪽에서 풀었다는 것.

평가는 SkillsBench 기반 15개 스킬, Claude Code(Haiku-4.5, Opus-4.6)와 Codex(GPT-5.2, GPT-5.4) 네 조합에서 했습니다. <span style="background-color: #fff59d"><strong>평균 과제 성공률이 24.1% 올랐고</strong></span> 반복 실행 편차도 줄었습니다.

## 스킬이 있어도 실행은 흔들립니다

스킬 문서는 재사용 가능한 절차 지식을 줍니다. 근데 같은 스킬로 비슷한 과제를 반복 실행해도 결과가 계속 흔들립니다. 논문이 잡은 실패 원인은 두 가지입니다.

- <span style="background-color: #fff59d"><strong>절차 이탈</strong></span>: 스킬이 정한 스텝을 건너뛰거나 순서를 바꿔서 실행
- <span style="background-color: #fff59d"><strong>스텝 오류</strong></span>: 개별 스텝을 틀리게 수행하는 경우 (잘못된 인자, 잘못된 도구 호출)

![스킬 실행 실패 사례](/images/2026-08-16-skillsentry-skill-runtime-assurance/fig2-failures.png)
그림 출처: arXiv:2608.09253 Fig. 2

Table II를 보면 macroeconomic-timeseries-detrending 스킬 하나도 설정별로 0.613에서 0.833까지 갈립니다. 같은 스킬 문서를 쓰는데도 실행 환경에 따라 성공이 왔다 갔다 하는 겁니다.

## 런타임 가이던스는 문서와 트레이스를 합쳐서 만듭니다

SkillSentry는 스킬 문서를 그대로 컨텍스트에 안 넣습니다. <span style="background-color: #fff59d"><strong>스킬 문서에서 명세를 뽑고, 과거 성공/실패 트레이스에서 실행 경험을 캐서 합칩니다</strong></span>. 이걸 런타임 가이던스라고 부르고 전용 DSL로 표현합니다.

| 가이던스 필드 | 역할 |
|---|---|
| skill | 스킬 이름과 목표 |
| steps | 스텝별 논리적 액션 패턴 |
| on_enter | 스텝 진입 시 제안과 경고 |
| failure_patterns | 실패와 연관된 액션 패턴 |
| termination | 정상 종료 조건 |

![런타임 가이던스 예시](/images/2026-08-16-skillsentry-skill-runtime-assurance/fig5-guidance.png)
그림 출처: arXiv:2608.09253 Fig. 5

on_enter에는 "이 스텝에서는 이런 액션을 권장, 이런 액션은 경고"가 스텝 단위로 들어갑니다. failure_patterns는 과거 실패 트레이스에서 나온 위험 패턴 모음이구요. 둘 다 자동으로 채워집니다.

## 실행 루프를 훅으로 감싸서 검사합니다

Claude Code와 Codex는 실행 루프의 라이프사이클 훅을 제공합니다. SkillSentry는 이 훅에 붙어서 에이전트가 계획한 액션을 실행 전에 검사합니다. <span style="background-color: #fff59d"><strong>에이전트 구현 자체는 한 줄도 수정하지 않습니다</strong></span>.

- procedure checker: 액션이 현재 스텝의 논리 패턴과 맞는지 FSM으로 추적합니다. 이탈이나 failure_patterns 매치가 보이면 재계획 힌트를 줍니다.
- termination checker: termination 조건이 채워지기 전에 조기 종료하려 들면 경고를 줍니다.

![런타임 보증 사례](/images/2026-08-16-skillsentry-skill-runtime-assurance/fig6-assurance.png)
그림 출처: arXiv:2608.09253 Fig. 6

패턴에 안 맞는 액션을 무조건 막지는 않습니다. 유효한 탐색일 수 있어서 실행은 허용하고 FSM 진행만 안 시킵니다. <span style="background-color: #fff59d"><strong>영구 차단을 피한 설계</strong></span>라는 게 저자들의 강조점입니다.

## 결과: 평균 성공률 24.1% 상승

네 조합의 평균 성공률(Table IV 기준)입니다.

| 구성 | Base Agent | SkillSentry |
|---|---|---|
| Claude Code + Haiku-4.5 | 0.572 | 0.741 |
| Claude Code + Opus-4.6 | 0.661 | 0.811 |
| Codex + GPT-5.2 | 0.604 | 0.752 |
| Codex + GPT-5.4 | 0.668 | 0.805 |

개별 스킬 단위로 보면 격차가 더 큽니다. excitation-signal-design은 Haiku 기준 <span style="background-color: #fff59d"><strong>0.120에서 0.373으로 세 배 가까이</strong></span> 올랐습니다.

## 실행 비용은 턴 7.8% 토큰 8.7% 증가입니다

| 항목 | Base | SkillSentry |
|---|---|---|
| 추론 턴 (Haiku-4.5) | 20.2 | 22.2 |
| 토큰 비용 (Haiku-4.5) | 796K | 886K |
| 추론 턴 (GPT-5.4) | 27.8 | 30.4 |
| 토큰 비용 (GPT-5.4) | 757K | 804K |

증가 원인은 스텝 가이던스 전달과 이탈 감지 시 재계획 요청입니다. <span style="background-color: #fff59d"><strong>성공률 개선 대비 비용 증가가 10% 미만</strong></span>이라는 게 실무적으로 쓸 만한 지점입니다.

## 트레이스가 쌓일수록 스스로 좋아집니다

가이던스는 고정이 아닙니다. 새 트레이스가 쌓일 때마다 갱신하는데, macro detrending 스킬을 10회 반복 진화하면 <span style="background-color: #fff59d"><strong>테스트 성공률이 약 58.2% 상대 상승</strong></span>합니다. 개선은 초반에 크고 후반에 수렴하며, 반복 실행 다섯 번의 표준편차도 줄어듭니다.

## 절제된 해석: 어디까지가 효과인가

어블레이션 결과를 보면 효과의 출처가 보입니다.

| 변형 | 평균 성공률 변화 |
|---|---|
| on_enter 제거 | -19.0% |
| failure_patterns 제거 | -13.6% |
| 가이던스를 시스템 프롬프트에 통째로 | -5.8% |

<span style="background-color: #fff59d"><strong>같은 정보라도 실행 시점에 해당 스텝만 전달하는 게 효과의 상당 부분</strong></span>이라는 뜻입니다. 크로스 모델 일반화도 확인했습니다. <span style="background-color: #fff59d"><strong>다른 모델에서 진화한 가이던스를 가져다 써도 base 대비 +17.2%</strong></span>, 자체 진화 대비 94.2% 효율을 유지합니다.

내 해석을 붙이면 이 연구의 실체는 이렇습니다. <span style="background-color: #fff59d"><strong>스킬을 정적 문서에서 실행 통계가 축적되는 산 물체로 바꾼 구조</strong></span>라는 것. 도큐먼트 최적화(DocsChisel 류)가 쓰기 전에 문서를 고친다면, SkillSentry는 실행 중에 감시하고 실행 뒤에 가이던스를 갱신합니다. 방향이 다르고 서로 충돌하지도 않습니다.

한계도 적습니다. SkillsBench 유래 15개 스킬, 두 에이전트, 30분 실행 제한이라는 설정이라는 점. 절차형 스킬에 특화된 평가라 자유 탐색형 과제에서는 FSM 추적이 어떻게 동작할지 확인이 필요합니다.

## 실무에서 바로 쓸 수 있는 부분

- Claude Code/Codex 훅 인터페이스로 외부 감시 레이어를 붙이는 패턴 자체가 참고가 됩니다. 에이전트 코드 수정이 0입니다.
- 스킬 문서를 계속 다시 쓰는 것보다, 성공/실패 트레이스에서 on_enter와 failure_patterns를 축적하는 편이 쌓이는 자산이 됩니다.
- 재현 실험을 반복 돌릴 때 성공률 편차를 잡는 용도로도 쓸 수 있습니다.

시작은 간단합니다. Claude Code나 Codex를 그대로 두고 <span style="background-color: #fff59d"><strong>훅부터 붙이는 걸로 시작하면 됩니다</strong></span>.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 루프 설계를 더 다뤄보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

원문: https://arxiv.org/abs/2608.09253
