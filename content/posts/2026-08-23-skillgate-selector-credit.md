---
title: 어떤 스킬을 읽을지 결정하는 토큰은 학습 신호를 못 받는다 — SkillGate 정리
date: 2026-08-23
tags: [LLM, agent, RL, skill, credit-assignment, GRPO]
draft: false
---

## 결론 먼저

에이전트가 스킬 라이브러리에서 어떤 스킬을 읽을지 고르는 그 결정, 실은 트레이닝에서 거의 학습이 안 됩니다. SkillGate 논문(arXiv:2608.18852, SJTU + 샤오홍슈)이 그 원인에 이름을 붙였습니다. <span style="background-color: #fff59d"><strong>selector credit starvation</strong></span>, 선택자 크레딧 고갈이요.

핵심 수치부터 보시면:

- 12,800개 온폴리시 트레젝토리 감사 결과, 스킬 이름을 부르는 토큰의 loss 점유율은 중앙값 <span style="background-color: #fff59d"><strong>0.14%</strong></span>
- 트레젝토리가 길어지면 이 점유율이 <span style="background-color: #fff59d"><strong>약 7배 더 희석</strong></span>
- 오라클(정답 스킬)을 제대로 읽었는데도 뒤의 실행이 실패해서 <span style="background-color: #fff59d"><strong>음의 어드밴티지를 받는 비율이 약 40%</strong></span>
- 그런데 매칭된 프롬프트 그룹에서 정답 스킬을 읽은 것의 가치는 <span style="background-color: #fff59d"><strong>+11.2pp 성공률</strong></span>

정리하면, 트레젝토리에서 가장 가치 있는 결정 중 하나가 신호는 거의 못 받고, 받는 신호는 절반 가까이 부호까지 틀린 상태입니다.

## 문제 설정

요즘 에이전트 프레임워크는 절차 지식을 스킬로 묶습니다. 이름 + 한 줄 설명만 보여주고, 본문은 필요할 때 파일로 여는 구조요. 공개 라이브러리에는 이미 수천 개가 넘게 쌓여 있어서, 컨텍스트 윈도우에 다 안 들어갑니다.

그래서 "어떤 스킬을 읽을지"는 에피소드 중간에 정책이 내리는 결정이 됐는데, 기존 RL 레시피로는 이걸 가르칠 수 없다는 게 논문의 출발점입니다.

논문은 실험용 슬레이트를 이렇게 구성했습니다 (K=16):

| 구성 | 개수 | 설명 |
| --- | --- | --- |
| 오라클 | 1 | 이 태스크를 위해 쓰이고 해결 검증까지 된 스킬 |
| 미스리딩 | 5 | 주제는 비슷한데 기능적으로 틀린 하드 네거티브 |
| 관련/무관 방관자 | 10 | 공개 라이브러리 2,045개에서 샘플링 |

에이전트에게 어떤 게 오라클인지 알려주지 않고, 안 읽어도 됩니다. 읽기는 그냥 샌드박스 경로에 대한 tool call이에요.

## 왜 아웃컴 RL이 실패하는가

GRPO 같은 시퀀스 레벨 RL은 트레젝토리 전체에 하나의 어드밴티지를 방송(broadcast)합니다. 이때 스팬의 그래디언트 점유율은 토큰 점유율과 같아지는데, 스킬 이름 몇 토큰은 수천 개 실행 토큰에 파묻힙니다.

![Figure 1: selector credit starvation](/images/2026-08-23-skillgate-selector-credit/fig-1-p2.png)

Figure 1이 이 삼중 실패를 보여줍니다. Share(점유율 희석), Sign(부호 오류), Value(정작 결정은 11.2pp짜리)이 전부 트레젝토리가 길어질수록 악화됩니다. 저자들이 완주한 런의 실제 트레이닝 아티팩트를 다시 읽어서 측정한 오프라인 감사라는 점이 강점이에요. 새로 학습시킨 게 아니라 이미 돌아간 런에서 증상을 확인한 겁니다.

## SkillGate 방법

해법은 더 좋은 보상도, 보상의 시간 해상도를 높이는 것도 아니고 <span style="background-color: #fff59d"><strong>크레딧의 분리</strong></span>입니다. 하나의 GRPO 업데이트 안에서 토큰 서포트를 겹치지 않는 두 채널로 나눕니다.

![Figure 2: SkillGate 개요](/images/2026-08-23-skillgate-selector-credit/fig-2-p4.png)

- 태스크 채널: 기존 그룹 정규화 아웃컴 어드밴티지. 단, 스킬 리드 tool call 전체를 loss에서 제외해서 태스크 아웃컴이 선택을 수정할 수 없게 함
- 셀렉터 채널: <span style="background-color: #fff59d"><strong>액션 로컬 어드밴티지를 스킬 이름 토큰에만</strong></span> 적용. 정확히 한 번 읽었고 그것이 오라클일 때만 양수

두 서포트는 구조적으로 분리(disjoint)돼 있고, 배치당 두 채널의 loss 무게는 같습니다. 그래서 선택 결정의 무게가 트레젝토리 길이에 더 이상 좌우되지 않아요.

셀렉터 유틸리티는 아웃컴에서 유도하지 않기 때문에, 아웃컴 기반 가중치 스킴에 적용되는 불가능성 결과(arXiv:2607.23364)도 회피합니다.

## 결과

5개 에이전틱 벤치마크(Claw-Eval, SkillsBench, SETA, SWE, Terminal-Bench 2.0), 16 후보 슬레이트에서:

- Qwen3.5-9B 정책이 <span style="background-color: #fff59d"><strong>40.8% → 53.2% 성공률</strong></span> (동일 예산 아웃컴 RL 대비 47.0%)
- 오라클 스킬 노출률 83.9%, 미스리딩 노출률 <span style="background-color: #fff59d"><strong>21.8%로 2/3 감소</strong></span> (아웃컴 RL은 69.6%까지 올라가 있었음)
- 읽는 스킬 수도 줄었습니다. 정확히 하나만 읽는 clean single-oracle 비율 75.4%

동일 초기화·데이터·스텝·하이퍼파라미터를 공유하는 통제 비교군 SkillRL(outcome only)과의 차이가 이 수치의 의미입니다. 차이가 나는 건 그래디언트가 어디에 닿는지뿐이에요.

흥미로운 건 프론티어 모델 행동입니다. DeepSeek-V4-Pro, GLM-5, Kimi-K2.6 같은 대형 모델들도 오라클 스킬을 절반 이상의 트라이얼에서 읽지 못합니다. 일반 능력으로 스킬을 놓친 걸 보상할 수는 있어도, 신뢰할 수 있는 선택자는 안 된다는 뜻이에요. <span style="background-color: #fff59d"><strong>스케일만으로는 인폴리시 스킬 선택이 해결되지 않는다</strong></span>는 게 논문의 독립적인 발견입니다.

## 어블레이션: 신호를 어디에 놓을 것인가

Table 2 어블레이션이 설계를 좁혀갑니다. 같은 초기화, 같은 100 스텝에서 셀렉터 신호의 착지점만 바꿨습니다.

| 설계 | 신호 위치 | 성공률 | clean single-oracle |
| --- | --- | --- | --- |
| SkillRL (outcome only) | 없음 | 42.1 | 21.4 |
| Group-level regret | 프롬프트 그룹 | 41.8 | 15.7 |
| Trajectory bonus | 트레젝토리 전체 | 41.8 | 33.9 |
| Action credit | 첫 오라클 리드 | 45.0 | 64.6 |
| SkillGate | 유일한 리드가 오라클일 때 | 50.0 | 75.4 |

![Figure 3: 다섯 가지 크레딧 설계](/images/2026-08-23-skillgate-selector-credit/fig-3-p8.png)

![Figure 5: 오프라인 감사](/images/2026-08-23-skillgate-selector-credit/fig-5-p9.png)

## 실무 관점

스킬 라이브러리가 커질수록 선택 문제는 더 심해집니다. 미리 로딩하는 방식은 k에 선형으로 비용이 늘어서 16개 전체면 온디맨드 비용의 16배입니다.

SkillGate는 아웃컴만으로 트레이닝하던 기존 에이전틱 RL에 적용할 수 있는, 크고 검증 가능한 수정입니다. 저자들의 표현을 빌리면 하나의 트레젝토리에 종류가 다른 결정들이 섞여 있을 때 <span style="background-color: #fff59d"><strong>토큰 서포트를 분할하는 게 단일 어드밴티지를 재분배하는 것보다 싸고 검증 가능한 대안</strong></span>이라고요.

한계도 논문이 스스로 명시합니다. 각 구성이 싱글 런이고, 정답 스킬을 아는 트레이닝 태스크가 필요하며, 액션 로컬 방식은 기권(abstention)에 크레딧을 줄 수 없습니다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 스킬 선택을 직접 다뤄보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: SkillGate: Training In-Policy Skill Selection in Long-Horizon Agents (arXiv:2608.18852)
- 코드: https://github.com/DeepExperience/SkillGate
- 모델: https://huggingface.co/simonlqy/SkillGate-9B
