---
title: "SkillProx: 에이전트 스킬이 늘어만 가면 망한다 — 근접 기울기로 줄이면서 키우는 법"
date: 2026-08-11
tags:
  - agent
  - skill-evolution
  - LLM
  - harness
  - textual-optimization
  - self-evolution
  - loop
  - automation
draft: false
showTableOfContents: true
---

논문: [SkillProx: Self-Evolving Agent Skills via Proximal Textual Gradient Descent](https://arxiv.org/abs/2608.07449) (2026-08-07, Mingxuan Zheng 외, HKUST)

## 핵심 한 줄

에이전트 스킬을 텍스트 기반 경사 하강법으로 업데이트하되, 근접 항(proximal term)을 넣어 "쓸모없는 지식을 자동으로 삭제"하는 정방향-역방향 루프를 만들었습니다.

## 문제: 스킬이 자라나기만 하면 망한다

LLM 에이전트가 반복 작업을 할 때, 절차적 지식을 "스킬"이라는 텍스트 파일로 저장해서 재사용합니다. 실패할 때마다 진단해서 패치를 붙이는데, 여기에 두 가지 문제가 생깁니다.

1. **진단이 맞아 보여도 실제로는 성능을 떨어뜨린다** — LLM이 "이렇게 고치세요"라고 쓴 게 그럴싸해도, 스킬에 넣고 실행해 보면 정확도가 내려가는 경우가 있습니다. 기존 방법은 재실행 없이 그냥 패치를 커밋합니다.
2. **스킬이 계속 커지기만 한다** — 반복 패치로 중복 지시, 충돌하는 휴리스틱, 작업 특정 해법이 쌓입니다. 삭제는 "그냥 편집 중 하나"로 취급되고, 정리 메커니즘이 없습니다.

논문의 실험에서 open-loop 방식(재실행 없이 커밋)의 평균 OJ hard accuracy는 50.30±2.50이고, 폐루프(재실행 후 게이트 통과만 커밋)는 51.40±1.51입니다. 분산도 줄고 하위권이 올라갑니다.

## SkillProx: 정방향 진단 + 역방향 근접 정리

![SkillProx 파이프라인](/images/2026-08-11-skillprox-proximal-textual-gradient-agent-skills/fig-1-p2.png)

근접 경사 하강법(proximal gradient descent)의 구조를 빌려왔습니다.

| 단계 | 역할 | 하는 일 |
|------|------|---------|
| 정방향 (Forward) | 성능 개선 | 현재 스킬로 배치 실행 → 실패 진단 → 패치 생성 → **같은 배치에 재실행** → 게이트 통과만 커밋, 실패하면 롤백 |
| 역방향 (Backward) | 복잡도 정리 | 스킬을 지식 단위로 분해 → leave-one-out 유틸리티 감사 → 음수 기여 단위 삭제/강등/병합 → 검증 세트로 게이트 |

정방향은 "새로운 지식이 들어올 때 실제로 도움이 되는지 확인"하고, 역방향은 "쌓인 지식 중에 남길 것을 결정"합니다.

### 정방향: 재실행 게이트

진단자(Diagnostician)가 실패 궤적을 보고 편집 방향을 제안하면, 패처(Patcher)가 후보 스킬을 만듭니다. 여기서 같은 배치에 다시 실행합니다.

게이트 조건:
- hard accuracy가 전과 같거나 높아야 함
- cell accuracy도 떨어지지 않아야 함

통과하면 커밋, 실패하면 롤백하고 "이 방향은 효과가 없었다"는 피드백을 다음 진단에 넘깁니다. 최대 3회 재시도.

### 역방향: leave-one-out 유틸리티 감사

스킬을 섹션 단위로 쪼갭니다. 각 단위를 하나씩 빼고 검증 세트를 돌려서, 뺐을 때 정확도가 올라가면 그 단위는 음수 유틸리티입니다.

대표 사례: 29,129자 스킬에서 3.12%를 삭제했더니 검증 hard accuracy가 46% → 54%로 올랐습니다. cell accuracy도 96.05% → 99.73%.

## 결과

3개 백본(Qwen3.5-4B, Qwen3.5-27B, Qwen3.6-27B), 3개 벤치마크(SpreadsheetBench, WikiTableQuestions, HiTab)에서 실험했습니다.

![컴포넌트별 기여](/images/2026-08-11-skillprox-proximal-textual-gradient-agent-skills/table-3-p7.png)

| 비교 | 요약 |
|------|------|
| SkillProx vs SkillGrad (최강 baseline) | 평균 +3.0 pp |
| 폐루프만 (Prox 제거) | 정확도는 오르지만 스킬이 계속 큼 |
| Prox만 (폐루프 제거) | 스킬은 줄지만 정확도가 덜 오름 |
| 둘 다 | 정확도 + 스킬 크기 모두 개선 |

4B 모델에서 가장 큰 이득을 봅니다. SkillProx가 EvoSkill보다 +14.3 pp, Trace2Skill보다 +11.0 pp 앞섭니다. 약한 모델일수록 스킬 품질에 더 민감하게 반응합니다.

![정확도-압축 파레토](/images/2026-08-11-skillprox-proximal-textual-gradient-agent-skills/fig-2-p7.png)

## 같은 실패 패턴이 만드는 다른 지식

재미있는 포인트: open-loop와 closed-loop가 같은 실패(순차 스캔 중 참조값이 바뀜)를 만나도 대처가 다릅니다.

| | open-loop | closed-loop |
|---|-----------|-------------|
| 진단 내용 | "구체적 예시를 추적하라" + 작업 특정 하드코딩 | "참조값을 갱신하라"는 실행 가능한 규칙 |
| cell utility | -0.0337 (해로움) | +0.0495 (도움) |

진단 텍스트가 그럴싸해도 재실행해 보면 차이가 납니다. 세만틱 플러저빌리티만으로는 재사용 가능한 규칙과 오버피팅된 템플릿을 구분할 수 없습니다.

## 왜 중요한가

에이전트 스킬 진화 연구가 "어떻게 더 잘 쌓을 것인가"에 집중되어 있을 때, SkillProx는 "무엇을 버릴 것인가"를 같은 비중으로 다룹니다. 하네스/스킬 자가진화 루프에서 삭제가 first-class 시스템 기능이 되어야 한다는 점을 데이터로 보여줍니다.

정방향 게이트는 온라인 차단, 역방향 Prox는 사후 정리. 두 단계가 보완적으로 작동합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

코드: [github.com/Steven011018/SkillProx](https://github.com/Steven011018/SkillProx)
