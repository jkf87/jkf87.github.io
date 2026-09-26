---
title: "LLM 에이전트 하네스·스킬 자가진화 설계 가이드: 논문 7편의 실패 진단과 처방 비교"
date: 2026-09-26
author: 한준구(코난쌤)
description: "LLM 에이전트가 스스로 스킬과 하네스를 고치게 만드는 2026 논문 7편을 비교했습니다. 고정된 개선 절차, 순환 추론, 낡은 경험, 과적합, 희소 보상의 실패 모드별 처방과 초록에서 확인한 수치를 표로 정리했습니다."
tags:
  - LLM 에이전트
  - 하네스
  - 자가진화
  - 스킬
  - 벤치마크
refactor_hub_id: harness-self-improve-20
aliases:
  - posts/2026-07-24-metaskill-evolve
  - posts/2026-07-28-metaevolve-llm-self-evolution-meta-skills-rl
  - posts/2026-08-04-drevo-harness-self-evolution
  - posts/2026-08-09-harnesscompass-guiding-automatic-harness-evolution
  - posts/2026-08-10-gse-globalized-skill-evolution-coding-agents
  - posts/2026-08-12-skillhex-hypothesis-driven-agent-skill-evolution
  - posts/2026-09-23-agent-harness-evolution-overfitting-rrsi
draft: false
---

## 한눈에 보는 결론

에이전트가 스킬과 하네스를 스스로 고치는 루프를 돌리면 저마다 다른 지점에서 무너집니다. 2026년 7~9월 논문 7편을 나란히 놓고 보니 흥미로운 패턴이 있습니다. 각 논문이 다른 실패 지점을 진단하고, 그 진단에 맞는 장치를 하나씩 달았어요.

- 개선 절차 자체가 고정돼 있던 문제 → MetaSkill-Evolve가 메타 스킬을 진화 대상으로 끌어올렸습니다. <span style="background-color: #fff59d"><strong>백본 대비 OfficeQA 홀드아웃 +23.54점.</strong></span>
- 진화 이력을 무시하고 같은 생각을 순환 → MetaEvolve가 "이전보다 나아지게" 보상을 주는 RL로 메타 스킬을 훈련했습니다. <span style="background-color: #fff59d"><strong>코딩 7벤치마크 OOD 평균 +24.12%p.</strong></span>
- 낡은 경험을 여전히 유효한 것처럼 재사용 → DREvo가 증거를 함수 단위로 재보정했습니다. 도메인 추론 과제 평균 +16.2%.
- 진화에 쓴 작업만 외워버리는 과적합 → HarnessCompass는 작업 무관 수정만 허용하는 게이트, RRSI는 제안·선택 양쪽에 정규화를 넣었습니다.
- 스킬끼리 부딪히는 호환성 붕괴 → GSE가 스킬 관계 그래프로 전역 진화를 했습니다. <span style="background-color: #fff59d"><strong>산업 내부 배포에서 F1 +61.4%.</strong></span>
- 검증 데이터 없는 희소 보상에서 초반 진단에 몰빵 → SkillHEX가 가설 검증과 수정 트리로 착취 함정을 피했습니다. <span style="background-color: #fff59d"><strong>SkillsBench 통과율 55.9%(GPT-5.3-Codex, 5회 예산).</strong></span>

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>진화 루프의 성패는 어떤 알고리즘을 도입하느냐보다, 어떤 실패 모드를 막는 장치를 설계에 넣었느냐로 갈립니다.</strong></span>

## 무엇을 비교했나

예전에 단편적으로 다뤘던 글 7편을 하나의 비교로 합쳤습니다. 2026-09-26에 7편의 arXiv 초록 페이지를 직접 가져와 핵심 주장을 대조했고, 초록에서 확인 안 되는 본문 표 수치는 이 글에서 뺐습니다.

1. MetaSkill-Evolve — 두 시간 스케일 메타 스킬 진화 ([arXiv:2607.05297](https://arxiv.org/abs/2607.05297))
2. MetaEvolve — RL로 기르는 자기진화 메타 스킬 ([arXiv:2607.21971](https://arxiv.org/abs/2607.21971))
3. DREvo — 재보정된 과거 경험 기반 하네스 진화 ([arXiv:2607.26722](https://arxiv.org/abs/2607.26722))
4. HarnessCompass — 일반화 게이트로 제약하는 하네스 진화 ([arXiv:2608.01918](https://arxiv.org/abs/2608.01918))
5. GSE — 코딩 에이전트 전역 스킬 진화 ([arXiv:2608.06153](https://arxiv.org/abs/2608.06153))
6. SkillHEX — 가설 기반 스킬 진화 탐색 ([arXiv:2608.05628](https://arxiv.org/abs/2608.05628))
7. RRSI — 정규화된 재귀적 하네스 자기개선 ([arXiv:2609.24972](https://arxiv.org/abs/2609.24972))

![스킬·하네스 자가진화 7종 위치 지도](../media/llm-agent-self-evolution-design-guide-2026/chart-01-failure-mode-map.png)

위치 지도를 보면 진화 대상이 세 층으로 나뉩니다. 모델 가중치를 건드리는 MetaEvolve, 개별 스킬과 스킬 뱅크를 다루는 SkillHEX·MetaSkill-Evolve·GSE, 하네스 전체를 다루는 DREvo·HarnessCompass·RRSI. 근데 실패 모드 진단은 층을 넘어 겹칩니다. 과적합을 진단한 논문이 세 편(GSE·HarnessCompass·RRSI)이고, 각자 게이트·관계 그래프·정규화라는 다른 처방을 냈어요.

## 방법 비교

| 방법 | 진화 대상 | 핵심 진단 | 처방 | 대표 수치 (초록 기준) | 비용 신호 |
|---|---|---|---|---|---|
| MetaSkill-Evolve | 태스크 스킬 + 메타 스킬 | 개선 절차가 한 번 정해지면 고정, 비재귀적 | 빠른 루프(태스크 스킬)·느린 루프(메타 스킬) 두 시간 스케일, 5컴포넌트 파이프라인(Analyzer·Retriever·Allocator·Proposer·Evolver) | 백본 대비 +23.54(OfficeQA) / +16.09(SealQA) / +1.92(ALFWorld)점 | 백본 1개 고정, 추가 모델·목적함수 없음 |
| MetaEvolve | 모델 가중치(RL) | 기존 포스트트레이닝이 단일 턴 완료만 최적화, 진화 이력 무시 | 진화 궤적 합성 데이터 + 개선 폭 보상 RL(GRPO 계열), 무개선 시 벌점 | 코딩 7벤치 in-dist +10.01%, OOD +24.12%, 도메인 밖 알고리즘 최적화 +46.9% 상대 | RL 훈련 비용 별도, 추론 시 진화 검색 비용은 그대로 |
| DREvo | 하네스 | 낡은 경험의 유효성 재평가 없음, 실행 가능한 방향 번역 부재 → 궤적 출렁임 | 함수 단위 증거 고정, 상태 의존 재보정, 역할 조건부 검색 의도 증류 | 5벤치마크 전부 최고, 도메인 추론 평균 +16.2%, 에이전트 과제 +14.2% | 제한 진화 예산 하에서 평가 |
| HarnessCompass | 하네스 | 진화 작업 과적합, 궤적 신호만 의존, 컴포넌트 동시 수정 간섭 | 작업 무관 수정만 허용하는 전역 제약, 1인칭 피드백, 컴포넌트별 분리 진화 후 통합 | <span style="background-color: #fff59d"><strong>SWE-bench Verified(GPT-5.4) Pass@1 54→66%</strong></span>, 진화 5회 | 진화 횟수 5회로 효율 개선 |
| GSE | 스킬 뱅크 전체 | 국소 업데이트 → 호환성 붕괴·과적합 회귀 | 스킬 관계 그래프(SRG) 공동 진화, 클러스터 일반화, 리플레이 검증 | 테스트 생성 정밀도 +6.1~34.1%·재현율 +31.8~180.0%, 산업 배포 F1 +61.4% | 전역 추론의 토큰 비용 증가 |
| SkillHEX | 개별 스킬 | 검증 세트 없는 희소 보상, 그리디 수정의 착취 함정 | 반증 가능한 실패 가설 → 실행 가능한 테스트, 캐시된 출력 재분석, PUCT 트리 탐색 | SkillsBench 87과제 통과율 55.9%(GPT-5.3-Codex), 57.9%(Claude Opus 4.7), 예산 5회 | 추가 환경 호출 없이 진단 신호 확보 |
| RRSI | 하네스 | 유한한 evolve 셋 반복 재사용 → 적응적 과적합, 복잡도 누적 | 제안부 정규화(어닐링 에디트 예산·미탐색 궤적 장려) + 선택부 정규화(critic 스크리닝·pruner) | 8벤치 evolve 최대 +14.1점, OOD 5벤치 최대 +4.7점 | 정책 토큰 30% 절감 |

![자가진화 7종 대표 수치](../media/llm-agent-self-evolution-design-guide-2026/chart-02-headline-numbers.png)

수치 표와 차트에 공통 주의문을 달아둡니다. <span style="background-color: #fff59d"><strong>7편의 단위와 비교 대상이 제각각이라 논문 간 점수 순위는 성립하지 않습니다.</strong></span> 각 행은 해당 논문의 내부 비교입니다.

공통 축으로 다시 읽으면 구별점이 세 개 나옵니다.

- 손대는 층위: 가중치(MetaEvolve) / 스킬·스킬 뱅크(MetaSkill-Evolve·GSE·SkillHEX) / 하네스(DREvo·HarnessCompass·RRSI).
- 일반화 검증 여부: <span style="background-color: #fff59d"><strong>RRSI는 OOD 5벤치를, HarnessCompass는 헬드아웃·다른 모델 전이를 명시적으로 보고합니다</strong></span>. MetaEvolve는 OOD가 in-dist보다 크게 나왔다는 점을 증거로 씁니다.
- 비용 회계: RRSI는 정책 토큰 30% 절감을, SkillHEX는 캐시 재분석으로 환경 호출을 줄인 점을, GSE는 전역 진화의 토큰 비용 증가를 각자 보고합니다. <span style="background-color: #fff59d"><strong>비용을 보고하는 논문과 보고하지 않는 논문을 섞어 읽으면 왜곡이 생깁니다.</strong></span>

## 언제 무엇을 쓰나

상황별 선택 기준을 정리했습니다. 논문을 그대로 쓰는 게 목적이 아니라, 루프 설계에서 빌려올 장치를 고르는 기준입니다.

- 반복 작업에서 프롬프트·절차 파일을 계속 고쳐 쓰는데 "어떻게 고칠지" 규칙이 몇 달째 그대로다 → MetaSkill-Evolve 구조. 개선 절차도 문서로 두고 주기적으로 되돌아보는 느린 루프를 함께 돌리면 됩니다.
- 같은 실패가 반복되고 재시도가 제자리걸음이다 → MetaEvolve 교훈. 매 시도의 실패 원인과 개선 폭을 구조화해서 다음 시도 컨텍스트에 강제로 넣고, 개선 없는 재시도에 상한을 둡니다.
- 쌓아둔 성공 사례가 많은데 최근 성과가 흔들린다 → DREvo 접근. 각 교훈에 신선도와 구조 호환성을 붙여 지금 파이프라인에 유효한 것만 다음 제안에 반영합니다.
- 특정 데이터·파일명·케이스에 맞춘 수정이 눈에 띈다 → HarnessCompass 게이트. "이 수정이 어디에나 유효한가"를 검사해서 인스턴스 하드코딩을 차단합니다.
- 스킬·프롬프트 파일이 열몇 개를 넘었다 → GSE 관점. 의존·공동사용·충돌 관계 인덱스를 유지하고, 개별 사례 교훈을 바로 반영하기 전에 클러스터로 묶어 리플레이 검증을 돌립니다.
- 시도 횟수가 몇 번 안 되는 비싼 환경이다 → SkillHEX 구조. 수정을 덮어쓰지 말고 트리로 보관하고, 실패 원인을 검증 가능한 가설로 바꿔 이미 뽑아둔 출력으로 검증합니다.
- 진화 점수는 오르는데 처음 보는 작업에서 이득이 사라진다 → RRSI 처방. 후보당 에디트 수를 라운드마다 줄이고, 벤치마크 특화 제안을 평가 전에 걸러내고, 최근 기여 없는 컴포넌트를 가지치기합니다.

하나의 루프에 전부 넣을 필요는 없습니다. <span style="background-color: #fff59d"><strong>지금 내 루프에서 실제로 관측되는 실패 모드 하나에 대응 장치 하나부터 붙이면 됩니다.</strong></span>

## 블로그봇이 직접 확인한 것

2026-09-26에 블로그봇이 7편의 arXiv 초록 페이지를 직접 가져와서 옛 글의 핵심 주장과 대조했습니다.

| arXiv | 확인 내용 (초록 기준) |
|---|---|
| 2607.05297 | 두 시간 스케일, 메타 스킬 5컴포넌트(ψ·σ·α·π·ε → Analyzer·Retriever·Allocator·Proposer·Evolver), 백본 단일 고정, +23.54/+16.09/+1.92점 |
| 2607.21971 | AlphaEvolve 관찰에서 출발, 진화 궤적 합성 + 검증 보상 RL, in-dist +10.01% / OOD +24.12% / 도메인 밖 +46.9% 상대 |
| 2607.26722 | 낡은 경험 재평가·명시적 방향 번역 부재 진단, 함수 단위 증거·재보정·역할 조건부 증류, 5벤치 최고 + 평균 16.2%/14.2% |
| 2608.01918 | 과적합·궤적 신호만 의존·컴포넌트 간섭 진단, 전역 제약 + 1인칭 피드백 + 분리 최적화, Pass@1 54→66%(진화 5회), 헬드아웃·타 모델 전이 |
| 2608.06153 | 국소 업데이트 문제 진단, SRG·클러스터 일반화·리플레이 검증, OpenHands·mini-SWE-agent에서 정밀도/재현율/F1 최고, 내부 배포 F1 +61.4% |
| 2608.05628 | 희소 보상·착취 함정 진단, 가설→실행 가능한 테스트·증거 트리 탐색, 87과제 55.9%(GPT-5.3-Codex)·57.9%(Claude Opus 4.7), 예산 5회 |
| 2609.24972 | 적응적 과적합 진단, 어닐링 에디트 예산·critic·pruner, evolve 최대 +14.1점 / OOD 5벤치 최대 +4.7점 / 정책 토큰 30% 절감 |

코드·프로젝트 링크도 확인했습니다. <span style="background-color: #fff59d"><strong>RRSI의 저장소(github.com/google-research/rrsi)와 프로젝트 페이지(regularized-rsi.com)가 모두 응답했습니다(HTTP 200).</strong></span> 나머지 6편은 초록에 저장소 주소가 확인되지 않아 링크를 싣지 않았습니다.

위의 두 차트는 블로그봇이 matplotlib 3.10.5로 직접 그린 그림입니다. 논문 figure를 가져온 게 아닙니다.

정정한 것도 적어둡니다. <span style="background-color: #fff59d"><strong>옛 글의 HarnessCompass 수치(51.8→61.0)는 초록의 54→66과 달라서 초록 쪽으로 바로잡았고,</strong></span> MetaEvolve의 "AlphaEvolve 대비 46.9%"는 초록 문장(훈련 도메인 밖 알고리즘 최적화 과제에서 46.9% 상대 향상)으로 바꿔 옮겼습니다. 본문 표의 세부 수치(예: 백본 모델명, 컨텍스트 토큰량)는 이번 재확인 범위 밖이라 뺐습니다.

## 한계와 반론

- 벤치마크가 제각각입니다. OfficeQA, 코딩 7종, SWE-bench Verified, SkillsBench, 8종 혼합은 서로 다른 과제라 <span style="background-color: #fff59d"><strong>연구 간 점수 비교는 성립하지 않습니다</strong></span>.
- 7편 모두 각자의 기준선과 설정에서 낸 수치입니다. 동일 조건 재비교가 없어서 "누가 최선인가"는 이 글로 답할 수 없습니다.
- 진화·훈련에 든 실제 비용의 회계 기준이 편차가 큽니다. 토큰 절감을 보고한 RRSI·SkillHEX와 비용을 명시하지 않은 논문을 같은 표에 두면 왜곡됩니다.
- 블로그봇이 논문 코드를 실행하지 않았습니다. 구현 난이도·운영 비용에 대한 실측은 이 글에 없습니다. RRSI만 저장소 응답을 확인했고 나머지는 실행 가능성 자체를 못 봤습니다.
- LLM이 제안·평가를 담당하는 구조라 평가기 오염이 있으면 증거 전체가 오염됩니다. DREvo·RRSI 계열에서 이 리스크가 구조적으로 남습니다.
- 초록 재확인으로 못 낸 본문 세부 수치(예: 메타 업데이트 주기 최적값, 컨텍스트 크기 안정화)는 원문을 직접 확인해야 합니다.

## 교실·업무에 적용한다면

수업 보조 에이전트나 사내 문서 작업 봇을 운영한다면 이렇게 시작하면 됩니다.

스킬 파일 3~5개 수준이면 SkillHEX식 버전 관리부터입니다. 수정할 때마다 이전 버전을 남기고(파일 복사나 git이면 충분), 실패 원인을 "그럴듯한 설명"으로 넘기지 말고 다음 실행으로 확인할 수 있는 가설로 적어둡니다.

스킬·프롬프트 파일이 열몇 개를 넘으면 GSE식 관계 인덱스를 만듭니다. 스프레드시트에 스킬 이름, 함께 쓰는 스킬, 충돌하는 스킬 세 열만 두어도 회귀가 눈에 보이기 시작합니다.

프롬프트 개선을 자동화했다면 HarnessCompass·RRSI의 게이트를 붙입니다. 특정 학생 이름, 특정 문서 형식, 특정 주차 데이터에만 맞는 수정이 제안에 섞이는지 평가 전에 검사하고, 한 번에 여러 수정을 묶어 넣지 않습니다.

MetaSkill-Evolve의 축소판은 회고에 있습니다. "실패를 어떻게 진단할지"를 정의한 문서 자체를 분기마다 한 번씩 고치는 습관이 두 층위 개선의 시작입니다.

MetaEvolve의 교훈은 재시도 정책입니다. 개선 폭을 재지 않고 "다시 해봐"만 반복하면 순환합니다. 매 시도 뒤 뭐가 바뀌었는지 숫자나 체크리스트로 남기고, <span style="background-color: #fff59d"><strong>두 번 연속 무개선이면 접근 자체를 바꿉니다</strong></span>.

오픈클로를 쓴다면 스킬·메모리·에이전트 설정 파일이 곧 진화 대상입니다. 이 글의 장치들을 그 파일들에 붙인다고 보시면 됩니다.

## 참고 자료

1. Recursive Self-Improvement of LLM Agents via Two-Timescale Meta-Skill Evolution — [arXiv:2607.05297](https://arxiv.org/abs/2607.05297)
2. Teaching LLMs to Self-Evolve: Cultivating Core Meta-Skills with Reinforcement Learning — [arXiv:2607.21971](https://arxiv.org/abs/2607.21971)
3. Distilling Recalibrated Historical Experience for Harness Self-Evolution — [arXiv:2607.26722](https://arxiv.org/abs/2607.26722)
4. Guiding Automatic Harness Evolution toward Generalizable and Effective Agent Harnesses — [arXiv:2608.01918](https://arxiv.org/abs/2608.01918)
5. Learning Globally Reusable Skills for Coding Agents — [arXiv:2608.06153](https://arxiv.org/abs/2608.06153)
6. Improving Agent Skills via Hypothesis-Driven Autonomous Exploration and Exploitation — [arXiv:2608.05628](https://arxiv.org/abs/2608.05628)
7. Regularized Recursive Self-Improvement of Agent Harnesses — [arXiv:2609.24972](https://arxiv.org/abs/2609.24972), [코드(github.com/google-research/rrsi)](https://github.com/google-research/rrsi), [프로젝트 페이지](https://regularized-rsi.com/)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
