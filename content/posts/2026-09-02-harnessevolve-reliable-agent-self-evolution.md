---
title: "HarnessEvolve — 자기진화 에이전트가 스스로를 망가뜨리는 세 가지 이유와 그걸 막는 이중 게이트"
date: 2026-09-02
tags:
  - agent
  - self-evolution
  - harness
  - llm
draft: false
description: "Huawei 연구팀의 HarnessEvolve 논문 정리. 자기진화 에이전트의 크레딧 할당 실패·숏컷 학습·치명적 망각을 레퍼런스 트랙토리 비교와 품질·성능 이중 게이트로 해결한 구조를 수치와 함께 정리했습니다."
---

## 결론 먼저

에이전트가 자기 하네스를 스스로 고치는 '자기진화' — 성능은 오르는 것 같은데 실제로는 답을 하드코딩하거나 이전 능력을 잃어버리는 경우가 많았습니다. Huawei가 2026년 9월 1일에 올린 HarnessEvolve가 이 고장을 게이트 두 개로 잡았다는 논문이라 정리했습니다. <span style="background-color: #fff59d"><strong>레퍼런스 트랙토리 비교로 첫 분기점을 찾아 진짜 원인만 고치고, 업데이트는 품질 게이트와 성능 게이트를 둘 다 통과해야 반영한다</strong></span>는 구조입니다.

숫자가 웬만한 설명을 대신하니 표부터 보시면 됩니다. 기준일: 2026-09-02, 논문 v1 기준.

| 항목 | 값 | 비고 |
|---|---|---|
| CloudCoreNetwork-QA (Qwen3.6-27B) | 43.4% → 86.9% | Base 대비 +43.5pp, GEPA(65.3%) 대비 +21.6pp |
| SpreadsheetBench (DeepSeek-V4-Flash) | 44.3% → 76.4% | 5개 벤치마크 중 최대 개선폭 |
| SearchQA | 86.5% → 92.9% | |
| 레퍼런스 트랙토리 제거 시 | 86.9% → 57.8% | ablation 기여도 1위 |
| 사용 모델 | Qwen3.6-27B, DeepSeek-V4-Flash | 두 프레임워크 평가 |

논문: [arXiv:2609.00829](https://arxiv.org/abs/2609.00829)

## 자기진화가 자꾸 실패하는 세 가지 이유

자기 하네스(프롬프트·스킬·도구·실행 로직)를 고치는 게 왜 위험한가. 논문이 짚는 고장은 세 개입니다.

1. <span style="background-color: #fff59d"><strong>크레딧 할당 실패</strong></span> — 태스크 끝에 성공/실패 신호 하나만 받으면 어떤 액션이 원인이었는지 모릅니다. 뒤의 오류는 앞 실수의 파급이라서 전체 반성은 원인을 잘못 짚습니다.
2. <span style="background-color: #fff59d"><strong>숏컷 학습</strong></span> — 답을 하네스에 박아넣거나 인컨텍스트 예시를 과하게 주입해서 정확도만 부풀립니다. 데이터 누수 + 프롬프트 비만이죠.
3. <span style="background-color: #fff59d"><strong>치명적 망각</strong></span> — 업데이트마다 일부 트랙토리만 보니까 이전 능력이 반복적으로 깎입니다.

근데 이건 알고리즘 하나 바꿔서 되는 게 아니라 시스템 구조 문제라고 저자들은 봅니다. 실행과 최적화가 한 루프에 섞여 있으면 최적화 판단을 실행 에이전트가 조작할 수 있어서요.

## 구조: 실행과 진화를 분리한 4에이전트 파이프라인

HarnessEvolve는 실행 에이전트와 진화 파이프라인을 분리했습니다. 각 단계가 독립 모듈이라서 결정이 감사 가능합니다.

![HarnessEvolve 프레임워크 개요](/images/2026-09-02-harnessevolve-reliable-agent-self-evolution/fig-1-p4.png)

- 실행 에이전트: 하네스를 들고 태스크 수행. 최적화 대상.
- 평가 에이전트: 정확도 채점 + 레퍼런스 트랙토리 신뢰성 검증.
- 최적화 에이전트: 첫 분기점 탐색 + 오류 클러스터링.
- 게이트 에이전트: 데이터 누수·프롬프트 비만 검사.

### 레퍼런스 트랙토리: 첫 분기점만 본다

여기가 제일 흥미로운 장치입니다. <span style="background-color: #fff59d"><strong>정답을 준 상태에서 실행한 경로(τ⁺)와 실패 경로(τ⁻)를 비교해서 가장 먼저 갈린 액션을 루트 원인으로 지정</strong></span>합니다. 그 뒤 분기는 파급 효과로 무시하구요.

오류 신호는 원인 기준으로 클러스터링되는데, <span style="background-color: #fff59d"><strong>멤버 1개짜리 클러스터를 보존해서 드물지만 치명적인 패턴이 묻히지 않게</strong></span> 했습니다. KMeans처럼 강제 배분하지 않는 점이 차이점입니다.

### 이중 게이트

품질 게이트는 데이터 누수(LLM-as-judge, η_leak=0.8 초과 거부)와 프롬프트 비만(인컨텍스트 예시 η_blo=5개 초과 거부)을 검사합니다. 거부 사유를 돌려주고 3회 재시도 후 폐기합니다.

성능 게이트는 <span style="background-color: #fff59d"><strong>현재 배치 개선 + 최근 배치에서 2.5pp 이상 악화 없음</strong></span>을 둘 다 요구합니다. 통과 후보는 스냅샷 풀에 쌓이고 에포크 끝에 검증 세트 최고 성능을 최종 선택합니다.

![자기진화 곡선](/images/2026-09-02-harnessevolve-reliable-agent-self-evolution/fig-2-p9.png)

## 결과: 5개 벤치마크 전체 1위

내부 데이터셋 2종 + 오픈소스 3종에서 GEPA, ACE, SkillOpt와 비교했습니다.

| 데이터셋 | Base | 최강 baseline | HarnessEvolve |
|---|---|---|---|
| CloudCoreNetwork-QA (Qwen) | 43.4 | 65.3 (GEPA) | 86.9 |
| Wireless-QA (DeepSeek) | 85.9 | 90.1 (ACE) | 92.8 |
| SearchQA | 86.5 | 90.0 (ACE) | 92.9 |
| OfficeQA | 62.8 | 68.9 (ACE) | 70.9 |
| SpreadsheetBench | 44.3 | 74.6 (SkillOpt) | 76.4 |

재미있는 건 오픈소스 데이터셋에서 <span style="background-color: #fff59d"><strong>OpenClaw 하네스(skills, AGENTS.md, SOUL.md, tools)를 통째로 최적화 대상으로 삼았다</strong></span>는 점입니다. SkillOpt가 skill.md 하나만 고치는 것과 대비됩니다.

### 프레임워크 간 전이

OpenClaw에서 최적화한 스킬을 Hermes, OpenCode, LAMAgent, DeepSeek Harness에 그대로 옮겼는데 전 프레임워크에서 유지 또는 개선. SpreadsheetBench의 OpenCode에서는 57.5% → 87.9%까지 올랐습니다. 특정 프레임워크에 맞춘 학습이 아니라 일반 오류 패턴을 배웠다는 근거로 읽힙니다.

### Ablation

![Ablation 결과 표](/images/2026-09-02-harnessevolve-reliable-agent-self-evolution/table-4-p9.png)

- 레퍼런스 트랙토리 제거: 86.9% → 57.8%. <span style="background-color: #fff59d"><strong>가장 큰 붕괴. 이 프레임워크의 핵심</strong></span>입니다.
- 오류 클러스터링 제거: 68.6%. 개별 수정끼리 충돌.
- 품질 게이트 제거: 80.1%.

![하네스 최적화 전후 비교](/images/2026-09-02-harnessevolve-reliable-agent-self-evolution/fig-3-p14.png)

## 내 해석: 어디까지 믿을 수 있나

여기부터는 제 판단입니다.

레퍼런스 트랙토리는 정답 있는 학습 데이터가 필요합니다. 실서비스 온라인 태스크에는 τ⁺가 없어서 <span style="background-color: #fff59d"><strong>57.8%짜리 폴백으로 내려갑니다</strong></span>. 게이트 자체도 LLM-as-judge라서 <span style="background-color: #fff59d"><strong>감사자가 최적화자보다 강하다는 가정이 숨은 전제</strong></span>입니다. 평가 비용도 만만치 않아서 patience 조기종료가 붙어 있습니다.

그래도 <span style="background-color: #fff59d"><strong>실행·평가·최적화·게이트 분리 + 원인 클러스터링 + 이중 게이트 + 스냅샷 풀 선택</strong></span>이라는 레시피는 다른 하네스 최적화 작업에도 그대로 옮겨볼 수 있는 구조입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**HarnessEvolve가 최적화하는 대상은 정확히 뭔가요?**
하네스 전체입니다. OpenClaw에서는 skills 디렉토리, AGENTS.md, SOUL.md, 도구까지. LAMAgent에서는 프로젝트 코드 전부입니다.

**레퍼런스 트랙토리는 정답이 있어야만 만들 수 있나요?**
네. 정답을 함께 준 상태의 실행 경로가 τ⁺라서, 정답 없는 태스크는 폴백 진단으로 내려갑니다. 폴백 성능은 57.8%까지 떨어집니다.

**성능 게이트의 임계값은 어떻게 설정했나요?**
δ=0.0, ε=2.5pp, R=2, η_leak=0.8, η_blo=5. 배치 10회·에포크 5회 무개선 시 조기 종료합니다.

**최적화된 스킬을 다른 프레임워크에서도 쓸 수 있나요?**
가능합니다. 4개 프레임워크 전환 실험에서 전부 Base 대비 유지 또는 개선했습니다. OpenCode + SpreadsheetBench는 57.5% → 87.9%.
