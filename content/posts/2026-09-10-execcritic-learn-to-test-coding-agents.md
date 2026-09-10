---
title: "ExecCritic: 테스트를 학습하는 코딩 에이전트 (arXiv 2609.09133) 논문 정리"
date: 2026-09-10
tags:
  - ai-agent
  - coding-agent
  - reinforcement-learning
  - swe-bench
  - test-generation
  - arxiv
draft: false
description: "arXiv 2609.09133 논문 요약. 코딩 에이전트의 패치와 테스트를 같은 트라젝토리가 쓰면 잘못된 패치가 잘못된 테스트를 통과하는 가짜 확신이 생긴다. ExecCritic은 Test 에이전트와 Repair 에이전트를 분리하고 테스트를 동결한 뒤 실행 피드백으로 수정하게 한다. SWE-bench Verified 72.6% 달성 과정 정리."
---

## 결론 먼저

arXiv 2609.09133v1(2026-09-08, Microsoft Research · UW-Madison · Georgia Tech, Leitian Tao 외)는 코딩 에이전트의 실행 피드백 루프에서 가장 위험한 지점을 정확히 찌른다. 패치와 그 패치를 검증하는 테스트를 같은 에이전트가 같은 트라젝토리에서 만들면, 두 오류가 서로 공명해서 가짜 확신이 생긴다는 것이다.

핵심 수치는 이것이다. 같은 Qwen-3.5-35B-A3B Repair 에이전트에 대해 <span style="background-color: #fff59d"><strong>학습 안 된 Qwen이 만든 테스트는 해결률을 61.2%에서 57.3%로 떨어뜨리고, GPT-5.6이 만든 테스트는 65.3%로 올린다</strong></span>. 피드백의 방향을 정하는 건 테스트의 질이다.

이 문제를 풀기 위해 두 역할을 분리해 각각 학습시키면, 두 Qwen 에이전트의 조합이 <span style="background-color: #fff59d"><strong>SWE-bench Verified 72.6%, 원래 베이스라인 대비 +11.4포인트</strong></span>에 도달한다. 평가 시점에 stronger model도 Oracle 피드백도 쓰지 않고.

## 논문 정보

| 항목 | 값 |
|---|---|
| 제목 | ExecCritic: Learn to Test, Test to Improve for Coding Agents |
| 저자 | Leitian Tao 외 (Microsoft Research · UW-Madison · Georgia Tech) |
| 게시일 | 2026-09-08 (기준일: 2026-09-10) |
| 코드 | https://github.com/MSR-Orchard/execcritic |
| 원문 | https://arxiv.org/abs/2609.09133 |
| 백본 | Qwen-3.5-35B-A3B (두 역할 모두) |
| 학습 데이터 / 평가 | SWE-ReBench / SWE-bench Verified |

## 문제: 패치와 검증의 결합

SWE-bench 같은 리포지토리 수준 버그 수정에서 공식 평가기는 숨겨져 있다. 그래서 에이전트는 스스로 검증 체크를 만들고, 그 근거로 제출을 결정한다. 여기서 두 가지 실패 모드가 생긴다.

- 아무 체크 없이 제출하면, 요청된 변경에 대한 로컬 근거가 전혀 없는 채로 평가기에 도달한다.
- 체크를 돌리면 더 나쁜 경우가 있다. 함수가 빈 리스트를 받을 때만 발생하는 버그가 있다고 하자. 에이전트가 이 조건을 놓쳐서 정상 케이스만 고치고, 테스트도 그 케이스만 덮으면? 테스트는 돌아가고 패치는 통과하고 원래 버그는 그대로 남는다.

논문의 정식화가 직관적이다. 관습적 에이전트 루프에서는 패치 p와 검증 근거 E가 같은 정책 π에서 나온다. E가 비어 있으면 무검증 제출이고, E가 있어도 같은 오해가 패치와 근거와 중단 결정을 함께 오염시킬 수 있다.

해결책은 독립성이다. 테스트를 Repair 후보 트라젝토리에 대한 접근 없이 생성하고, 소스 수정 중에는 그대로 동결한다. Repair 에이전트는 테스트를 고칠 수 없고 소스만 고친다.

## 구조: Learn to Test, Test to Improve

![Figure 1 전체 구조](/images/2026-09-10-execcritic-learn-to-test-coding-agents/fig-1-p1.png)

두 단계로 나뉜다.

### Learn to Test

Test 에이전트는 이슈와 버그 상태 리포지토리만 보고 세 가지를 산출한다. 리포지토리 네이티브 테스트 패치, 정확한 실행 커맨드, JSON 행동 계약(behavior contract)이다. 하네스는 이 묶음을 검증하고, 버그 상태에서 깨끗하게 실패하는지 확인한다. 깨끗한 Base 실패가 없으면 Base-gate 실패로 표시되고, 피드백 수정 단계는 진행하지 않는다. Round-0 패치가 그대로 평가된다.

![Figure 2 Test 자격검증 워크플로](/images/2026-09-10-execcritic-learn-to-test-coding-agents/fig-2-p4.png)

Base 실패는 필요조건일 뿐이다. 학습 신호로는 Base-to-Gold 성공을 측정한다. 테스트가 버그 상태에서 실패하고, 정답 패치를 적용한 상태에서 통과해야 진짜 판별 테스트다. 논문의 Django 예시가 이걸 잘 보여준다.

![Figure 3 Django 빈 리스트 버그 예시](/images/2026-09-10-execcritic-learn-to-test-coding-agents/fig-3-p5.png)

초기 패치 p0는 real_apps가 truthy할 때만 타입을 검사해서 빈 리스트가 assertion을 우회한다. 생성된 테스트는 AssertionError를 기대하므로 p0에서 실패하고, 가드를 `if real_apps is not None`로 바꾼 p1에서 통과한다.

### Test to Improve

동결된 테스트가 Repair 에이전트의 각 패치 후보에 대해 실행된다. 실패하면 bounded 실행 피드백이 다음 수정을 조건화한다. 통과하면 에피소드가 즉시 종료되고 그 패치가 제출된다. 최대 5회 수정 후에도 통과하지 못하면 마지막 후보가 강제 제출된다. 공식 평가기는 여전히 최종 권위다.

## 학습 레시피

![Figure 4 Test/Repair 보상 구조](/images/2026-09-10-execcritic-learn-to-test-coding-agents/fig-4-p6.png)

두 역할에 각각 실행 기반 보상이 붙는다.

- Test 보상: 유효 제출 실패 시 -0.2. Base 실패 + Gold 통과(Q=1)면, 후보 패치들에 대한 balanced accuracy에 따라 0.2 / 0.5 / 1.0으로 계단식 상승. 올바른 패치는 통과시키고 잘못된 패치는 실패시켜야 최고점이다.
- Repair 보상: 유효 실패 0.1, 테스트 통과·공식 실패 0.2, 수정 후 공식 성공 1.0, Round-0 직접 성공 1.5. Round-0 보너스를 크게 두는 이유는 직접 해결 능력을 유지하면서 피드백 활용도 가르치기 위해서다.

Test 학습은 DeepSeek-V4-Flash-0731의 5,000개 트라젝토리로 SFT한 뒤 GRPO로 온폴리시 학습한다. Repair 학습은 Round-0 정확도 0.4 미만 이슈로 제한해 수정 신호가 있는 데이터만 쓴다. 이런 필터링이 실무적으로 중요하다.

## 주요 결과

### 테스트 품질이 피드백의 방향을 결정한다

![Figure 5 테스트 소스별 효과](/images/2026-09-10-execcritic-learn-to-test-coding-agents/fig-5-p9.png)

Repair 에이전트를 고정하고 피드백 소스만 바꾼 결과:

| 피드백 소스 (Base Qwen Repair 고정) | SWE-bench Verified 해결률 |
|---|---|
| 테스트 없음 (Round-0) | 61.2% |
| Base Qwen 테스트 | <span style="background-color: #fff59d"><strong>57.3% (-3.9p)</strong></span> |
| GPT-5.6 테스트 | 65.3% (+4.1p) |
| Oracle F2P 테스트 | 69.4% (+8.2p) |

같은 실행 피드백 메커니즘인데 테스트 소스에 따라 -3.9p에서 +4.1p까지 갈린다. 이 대비가 이 논문의 동기 전부다.

### 역할별 학습이 둘 다 된다

| 구성 요소 | 학습 전 | 학습 후 |
|---|---|---|
| Test 에이전트 Base-to-Gold | 22.2% | <span style="background-color: #fff59d"><strong>62.2% (+40.0p)</strong></span> |
| Repair 에이전트 Round-0 해결률 | 61.2% | 68.3% (+7.1p) |
| 두 학습된 에이전트 조합 | — | <span style="background-color: #fff59d"><strong>72.6% (+11.4p)</strong></span> |

![Table 1 Test 에이전트 비교](/images/2026-09-10-execcritic-learn-to-test-coding-agents/table-1-p9.png)

Test 에이전트 62.2%는 Codex-5.3(61.0%)과 비슷한 수준이다. GPT-5.6-sol(87.8%)까지는 25.6p 남아 있다. 학습된 조합에 Oracle 피드백을 주면 77.6%까지 올라가므로, <span style="background-color: #fff59d"><strong>남은 5.0p 격차는 테스트 품질을 올리면 더 딸 수 있다는 뜻</strong></span>이다.

![Figure 6 학습 다이내믹스](/images/2026-09-10-execcritic-learn-to-test-coding-agents/fig-6-p10.png)

### 오버헤드가 작다

피드백 수정으로 68.3%에서 72.6%로 오르는 동안, 수정에 진입한 120개 트라젝토리는 평균 <span style="background-color: #fff59d"><strong>13턴만 추가</strong></span>로 해결했다. 5회 40턴 예산을 다 쓰는 일이 드물다는 뜻이다. 테스트 생성은 이슈당 1회의 일회성 비용이고 3회 Repair 실행에서 재사용된다.

## 내 해석: 어디서 쓸 수 있나

원문 근거와 구분해서 내 해석을 적는다.

이 논문의 진짜 기여는 진단 쪽이다. "실행 피드백을 넣으면 좋아진다"는 통념을 <span style="background-color: #fff59d"><strong>테스트가 틀리면 피드백이 독이 된다</strong></span>는 반례로 교정했다. 에이전트 시스템을 설계할 때 검증자와 실행자의 독립성을 명시적으로 설계해야 한다는 교훈은 코딩 외 도메인에도 적용된다.

SWE-bench Pro에서는 생성 테스트가 +0.7p에 그친다(61.6% → 62.3%). Oracle은 +11.8p를 주는데도. Pro 인스턴스는 평균 14.43개 F2P 테스트(Verified는 3.03개)를 요구한다. 하나의 테스트 묶음이 커버리지에 한계가 있다. <span style="background-color: #fff59d"><strong>테스트 하나에 하나의 행동만 검증하는 설계는 넓은 스펙의 태스크에서 상한이 낮다</strong></span>는 게 실무적 교훈이다.

언어 일반화 편차도 크다. Python 62.2%, Rust 66.7%, C++ 58.3%, C 26.1%, <span style="background-color: #fff59d"><strong>Java 2.4%</strong></span>. Python만으로 학습해도 Rust/C++은 되는데 C/Java는 안 된다. 레포지토리 네이티브 테스트 인프라 발견이 언어마다 난이도가 다르다는 뜻이다.

제한도 분명하다. 조합된 이득은 전체 시스템 기준이지 컴퓨트 매칭된 비교가 아니다. Base-gate 실패 시 Round-0로 폴백하는 설계가 전체 분모에 남는다는 점도 숙지해야 한다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### ExecCritic의 핵심 아이디어가 뭔가요?

Test 에이전트와 Repair 에이전트를 분리하고, 자격을 통과한 테스트를 소스 수정 중 동결하는 것입니다. 같은 트라젝토리가 패치와 테스트를 함께 쓰면 오류가 공명해서 가짜 확신이 생기는 것을 차단합니다.

### 생성된 테스트가 성능을 떨어뜨릴 수도 있나요?

네. 학습 전 Qwen 테스트는 해결률을 61.2%에서 57.3%로 3.9포인트 낮췄습니다. 테스트가 잘못된 행동 목표를 인코딩하면 피드백이 잘못된 방향으로 수정을 유도합니다.

### 최종 성능은 얼마인가요?

역할별 학습을 마친 두 Qwen-3.5-35B-A3B 에이전트의 조합으로 SWE-bench Verified 72.6%입니다. 원래 no-test 베이스라인(61.2%) 대비 11.4포인트 증가이며, 평가 시점에 stronger model이나 Oracle 피드백 없이 달성했습니다.

### 코드는 공개되어 있나요?

네. https://github.com/MSR-Orchard/execcritic 에서 공개되어 있습니다. 학습·롤아웃·평가는 Orchard 프레임워크로 수행됐습니다.

## 참고

- 원문: [arXiv:2609.09133](https://arxiv.org/abs/2609.09133)
- 코드: [MSR-Orchard/execcritic](https://github.com/MSR-Orchard/execcritic)
- 벤치마크: SWE-bench Verified, SWE-bench Pro, SWE-bench Multilingual
