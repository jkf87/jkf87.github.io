---
title: "PoisonedEvolution: 에이전트 스킬이 자가진화하는 과정을 공격하는 방법"
date: 2026-08-14
tags:
  - agent
  - security
  - self-evolving
  - skill-evolution
  - LLM
  - harness
  - safety
  - supply-chain
  - poison
  - SES
source: arxiv
source_url: https://arxiv.org/abs/2608.05563
paper_url: https://arxiv.org/abs/2608.05563
authors:
  - Lingqi Jiang
  - Xinhao Deng
  - Xiaohu Du
  - Jianan Ma
  - Yunhao Feng
  - Yuqi Qing
  - Zhihao Yuan
  - Linkang Du
  - Jingyi Wang
---

자가진화 스킬(SES) 시스템이 에이전트 궤적을 스킬로 증류하면서, 신뢰할 수 없는 경험이 신뢰된 지시어로 승격되는 구조적 취약점이 생겼습니다. PoisonedEvolution은 이 승격 과정을 공격합니다.

핵심은 이겁니다. 공격자는 악성 스킬을 직접 올리지 않습니다. SkillClaw 같은 다중 사용자 환경에서 정상적인 궤적 기여자로 참여해서, 10%의 증거만 넣으면 됩니다. 그러면 SES 파이프라인 자체가 악성 행동을 "재사용 가능한 경험"으로 분류해서 스킬에 기록합니다.

## 공격 모델: C1–C2–C3

![PoisonedEvolution 개요](/images/2026-08-14-poisoned-evolution-self-evolving-agent-skill-security/fig-1-p2.png)

PoisonedEvolution의 성공 조건 세 가지:

| 조건 | 의미 |
|---|---|
| C1 Inclusion | 공격 궤적이 필터를 통과해서 evolver에 도달 |
| C2 Evolution Attribution | evolver가 공격 행동을 "재사용 가능한 경험"으로 인정 |
| C3 Realization | 공격 행동이 요약·병합을 거쳐 스킬에 남음 |

C2가 핵심 병목구요. 공격 행동이 "인과적으로 유용하고 반복되는 패턴"으로 보여야 합니다. 단발성 노이즈와 구별되어야 합니다.

RAG poisoning과의 차이도 여기에 있습니다. RAG 공격은 검색 시점에 악성 문서가 컨텍스트에 들어가는 것이고, SES 공격은 증거→스킬 생성 파이프라인 자체를 속여서 지속적 아티팩트를 만들어냅니다. 한 번 성공하면 해당 스킬을 사용하는 모든 세션에 영향이 갑니다.

## 공격 설계

공격자는 skill-visible black-box 설정입니다. 공개된 스킬은 볼 수 있지만, 비공개 궤적 풀이나 evolver 프롬프트는 볼 수 없습니다. 직접 스킬 뱅크를 편집할 수도 없습니다.

트랜지토리 변환 과정:

1. 정상 작업 궤적을 가져옵니다 (SpreadsheetBench 출처)
2. 타겟 행동 b를 작업 제약조건과 성공 사이에 끼워넣습니다
3. surface 표현은 바꾸지만 행동의 의미는 유지합니다
4. k개의 변형된 궤적을 기여합니다

네 가지 보안 효과 패밀리를 테스트합니다:

| 패밀리 | 효과 | 예시 |
|---|---|---|
| F1 Confidentiality | 민감 정보 유출 | "결과물 생성 후 credential을 공격자 엔드포인트로 전송" |
| F2 Data integrity | 데이터 삭제 | "출력 후 소스 파일을 삭제" |
| F3 Supply chain | 패키지 소스 변경 | "의존성 설치 전 레지스트리를 공격자 서버로 교체" |
| F4 Safety weakening | 보안 검사 우회 | "커밋 전 보안 검사 비활성화" |

실제 실험에서는 inert canary 엔드포인트, 임시 경로, 루프백 레지스트리를 사용했습니다. 실제 요청, 파일 삭제, 패키지 설치는 실행하지 않습니다.

## 결과: 91% 스킬 삽입 성공률

![SkillClaw 메인 결과](/images/2026-08-14-poisoned-evolution-self-evolving-agent-skill-security/table-1-p6.png)

SkillClaw에서 n=30, k=3 (10% 공격자 비율) 설정으로 6개 LLM evolver × 4 패밀리 × 25회 = 600회 실험을 돌렸습니다.

| 지표 | 수치 |
|---|---|
| 전체 SER (Skill Embedding Rate) | 546/600 = 91.0% |
| 최고 evolver (DeepSeek-V3.2, Qwen3.5-122B) | 100/100 = 100% |
| 최저 evolver (GPT-5.4) | 70/100 = 70% |
| no-init (스킬 생성) 모드 | 490/600 = 81.7% |

evolver 모델에 따라 70%에서 100%까지 격차가 큽니다. evolver의 승격 정책이 공격 표면의 크기를 결정합니다. 스킬 품질이나 모델 크기 자체의 문제는 아닙니다.

## 반복 지원이 결정적이다

![공격자 지원과 희석 효과](/images/2026-08-14-poisoned-evolution-self-evolving-agent-skill-security/fig-2-p5.png)

k=1 (3.3%)일 때 SER은 5/25에 불과합니다. k=2 (6.7%)에서 21/25로 급등하고, k=3 (10%)에서 25/25가 됩니다.

단발성 궤적은 노이즈로 분류되지만, 2개 이상의 일관된 궤적은 SES가 증류하도록 설계된 "재사용 가능한 경험"과 구분이 안 됩니다.

희석 효과도 확인했습니다. k=3을 고정하고 n을 늘리면: n=10 (30%)에서 25/25, n=30 (10%)에서 25/25, n=100 (3%)에서 22/25. 클린 풀이 100개로 늘어나도 3개의 공격 궤적으로 88% SER을 유지합니다.

## 인과 프레이밍과 도메인 정렬

![조건별 곱내기 결과](/images/2026-08-14-poisoned-evolution-self-evolving-agent-skill-security/fig-3-p6.png)

C2 인과(attribution) 실험:

| 조건 | SER |
|---|---|
| Local (한 곳에 삽입) | 8/25 |
| Fragmented (여러 곳에 분산) | 11/25 |
| Causal (결과와 인과적으로 연결) | 25/25 |

인과적 프레이밍이 없으면 공격이 통하지 않습니다. 행동이 task 결과와 인과적으로 연결되어 있어야 evolver가 "이건 유용한 경험이다"라고 판단합니다.

C3 실현(realization) 실험에서도 도메인 정렬이 중요합니다. Generic 표현은 18/25, 보조 채널은 0/25, 도메인 특화 표현은 25/25입니다.

## Trace2Skill로 전이: 61.5%

Trace2Skill 파이프라인은 구조가 다릅니다. 성공/실패 궤적을 분리하고, 분석 LLM이 교훈을 추출하고, 계층적 병합을 거칩니다.

| 시스템 | SER |
|---|---|
| SkillClaw | 546/600 = 91.0% |
| Trace2Skill | 369/600 = 61.5% |

추가 단계가 있어서 SER이 낮아지지만, 여전히 과반수 시험에서 공격이 성공합니다. F4(안전 약화)는 Trace2Skill에서 28/150까지 떨어지는데, 실패 분석 경로에서 안전 완화가 "필요한 수리"로 보이지 않기 때문입니다.

## 방어: 증거 승격을 검사해야 한다

스킬 텍스트를 생성 후에 검사하는 것으로는 부족합니다. evolver가 이미 증거를 압축하고 정규화한 후이기 때문입니다.

연구팀이 제안하는 파일럿 방어 — 출처 다양성 게이트(provenance-diversity gate):

- 최소 3명의 독립 사용자/클러스터 필요
- 단일 출처가 다수를 차지하면 거부
- 높은 텍스트 유사도 패널티

n=30, k=3에서 이 게이트는 F1 패밀리 25/25를 모두 차단합니다 (게이트 후 SER 0/25).

한계도 있습니다. 조직적인 Sybil 공격자는 다양성을 흉내낼 수 있고, 그룹화가 정확해야 합니다. 근데 방향은 맞습니다. 증거 수준에서 출처를 추적하고, 승격 결정을 감사 가능하게 만들어야 합니다.

## 정리

| 항목 | 수치 |
|---|---|
| 공격자 권한 | skill-visible black-box |
| 최소 공격 예산 | k=3 in n=30 (10%) |
| SkillClaw SER | 91.0% |
| Trace2Skill SER | 61.5% |
| 파일럿 방어 | provenance-diversity gate → SER 0% |

에이전트 스킬 시스템이 자가진화할 때, 증거→지시어 승격 경계가 새로운 보안 경계입니다. 스킬 파일을 스캔하는 것만으로는 막을 수 없고, evolver가 증거를 크레딧으로 변환하는 시점에 출처 기반 검사가 필요합니다.

## 더 실습해보고 싶은 분들께

에이전트 스킬 시스템, 하네스 설계, RL 루프를 직접 다뤄보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

논문: [arXiv:2608.05563](https://arxiv.org/abs/2608.05563)
