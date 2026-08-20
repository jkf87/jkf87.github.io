---
title: "ACID-Agent — 데이터베이스 트랜잭션 개념을 LLM 에이전트에 이식한 하네스"
date: 2026-08-20
tags: [agent, harness, paper]
draft: false
---

논문 결론부터 정리합니다. Tsinghua 데이터베이스 그룹이 ACID 트랜잭션 개념을 LLM 에이전트 실행으로 재해석한 `ACID-Agent`를 냈고, <span style="background-color: #fff59d"><strong>KramaBench에서 Claude Code 대비 전체 점수 10.6%p 상승(64.0 → 74.6)</strong></span>을 확인했다는 논문입니다. 토큰 비용이 2.5배 이상 늘어나는 트레이드오프가 있습니다.

- 논문: [Agentic Transaction: Towards ACID-Compliant Agent Systems (arXiv:2608.13900)](https://arxiv.org/abs/2608.13900)
- 코드: [github.com/TsinghuaDatabaseGroup/ACID-Agent](https://github.com/TsinghuaDatabaseGroup/ACID-Agent)

![Figure 1. ACID-Compliant Data Agent 예시](/images/2026-08-20-acid-agent-transactional-agent-system/fig-1-p1.png)

## 핵심 아이디어: 에이전트 실행을 트랜잭션으로 본다

저자들은 LLM 에이전트의 장기 실행 과정을 "agentic transaction"이라고 부릅니다. 데이터 과학 워크플로에서 반복되는 탐색 → 실행 → 검증 사이클이 그 단위입니다.

DB의 ACID를 이렇게 옮겨왔습니다.

| 속성 | 에이전트 버전 |
|---|---|
| Atomicity | <span style="background-color: #fff59d"><strong>탐색-실행-검증 사이클 전체가 검증을 통과해야만 커밋. 실패하면 롤백</strong></span> |
| Consistency | 실행 과정은 비결정적이어도 <span style="background-color: #fff59d"><strong>커밋 결과는 사전/사후 조건을 만족</strong></span> |
| Isolation | 병렬 실행 중 실패한 시도의 중간 상태가 다른 실행/메모리로 새어나가지 않음 |
| Durability | 커밋된 상태와 근거를 <span style="background-color: #fff59d"><strong>append-only 워크스페이스에 저장</strong></span>, 나중에 재구성 가능 |

기존 코딩 에이전트가 중간 결정을 바로 전파하는 것과 달리, <span style="background-color: #fff59d"><strong>검증을 통과한 업데이트만 다음 단계로 넘긴다</strong></span>는 게 차이입니다.

![Figure 2. ACID-Compliant Data Agent 시스템 개요](/images/2026-08-20-acid-agent-transactional-agent-system/fig-2-p3.png)

## 어떻게 구현했나

두 축으로 만들었습니다.

오프라인 스킬 허브는 기존 리포지토리를 표준 CLI를 가진 에이전트 스킬로 패키징하고, LLM이 생성한 테스트로 동작을 검증합니다. 멱등성 키, write-ahead 액션 로그, 체크포인트, 자동 보상(compensation)을 넣어서 <span style="background-color: #fff59d"><strong>부분 실패가 워크스페이스를 더럽히지 않게</strong></span> 합니다.

온라인 단계 실행은 <span style="background-color: #fff59d"><strong>커밋-오어-리트라이 게이트</strong></span>를 돌립니다.

핵심 신호는 confidence divergence입니다.

 <span style="background-color: #fff59d"><strong>탐색 단계에서 고른 결정과 실제 코드에 들어간 결정의 토큰 확률 기반 신뢰도 차이</strong></span>를 재서 일정 임계값 이하면 재시도합니다. API 모델은 토큰 확률을 안 주니까 <span style="background-color: #fff59d"><strong>로컬 Qwen3-0.6B로 신뢰도를 추정</strong></span>한 게 실무적인 트릭입니다.

## 수치: 어디까지가 사실인가

KramaBench 결과(표 기준)를 그대로 옮기면 이렇습니다.

| 하네스 | 백본 | 점수 | 코드 스텝 | 토큰(K) | 비용($) |
|---|---|---|---|---|---|
| Claude Code | Qwen3.5-397B | 64.0 | 9.4 | 405 | 0.08 |
| ACID-Agent | Qwen3.5-397B | 74.6 | 22.8 | 348 | 0.10 |
| Claude Code | GLM-5.2 | 74.2 | 8.8 | 289 | 0.12 |
| ACID-Agent | GLM-5.2 | 77.4 | 22.5 | 367 | 0.61 |

여기서 제가 원문과 별도로 짚고 싶은 지점이 두 개 있습니다.

하나는 비용 구조입니다. GLM-5.2 백본에서는 탐색·재시도가 붙으면서 <span style="background-color: #fff59d"><strong>실행당 비용이 0.12달러에서 0.61달러로 5배 가까이</strong></span> 올라갑니다. 점수 3.2%p를 위해 이 비용을 낼지는 태스크 가치에 따라 갈립니다.

다른 하나는 재현 맥락입니다. 10.6% 상승은 Qwen3.5 백본에서 나온 숫자고, 상위 도메인(Astronomy, Legal)에서는 점수 차이가 0인 구간도 있습니다. 도메인별로 보면 Biomedical 55.6 → 77.8 같은 큰 개선과 함께 정체 구간이 섞여 있습니다.

![Figure 3. 3회 실행 일관성 비교](/images/2026-08-20-acid-agent-transactional-agent-system/fig-3-p4.png)

## 내 해석: 하네스 설계에 실린 교훈

이 논문에서 가져갈 만한 건 "ACID"라는 라벨보다 <span style="background-color: #fff59d"><strong>검증 게이트를 통과한 것만 커밋한다는 구조</strong></span>입니다. <span style="background-color: #fff59d"><strong>롤백이 불가능한 외부 효과(이메일 발송, 배포)에는 보상 트랜잭션 개념을 쓰라는</strong></span> 부분도 실무와 닿아 있습니다.

기존 하네스에 바로 적용할 수 있는 최소 버전은 이 정도입니다.

- 각 실행 단위 끝에 검증 스텝을 두고, <span style="background-color: #fff59d"><strong>통과 못 하면 이전 상태로 되돌리기</strong></span>
- <span style="background-color: #fff59d"><strong>실패한 시도의 중간 컨텍스트를 메모리에서 분리</strong></span>
- 커밋된 결과는 로그로 남겨서 나중에 재구성 가능하게

풀 버전(스킬 허브, 로컬 신뢰도 모델, 의존성 기반 격리)은 데이터 에이전트 워크로드에서 가치가 있고, <span style="background-color: #fff59d"><strong>일반 코딩 에이전트에는 위 최소 버전부터 시작하는 게 현실적</strong></span>입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
