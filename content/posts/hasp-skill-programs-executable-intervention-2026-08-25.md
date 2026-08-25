---
title: "스킬을 실행 가능한 프로그램으로 바꾸면 프롬프트 조언보다 30점 더 올라간다 — HASP 정리"
date: 2026-08-25
tags: [agent, LLM, harness, skill, RL, evaluation]
draft: false
---

## 결론 먼저

에이전트가 과거 경험에서 뽑은 "스킬"을 텍스트 조언으로 프롬프트에 넣는 방식은 실전에서 자주 무시됩니다. HASP(arXiv 2605.17734, Salesforce AI Research / NYU)는 스킬을 <span style="background-color: #fff59d"><strong>실행 가능한 Program Function(PF)</strong></span>으로 바꿔서, 에이전트 루프 안에서 다음 액션을 직접 고치거나 맥락을 주입하게 만듭니다.

Qwen2.5-7B-Instruct 기준으로 웹검색 추론에서:

| 방식 | 평균 정확도 |
|---|---|
| 스킬 텍스트만 프롬프트에 주입 (Prompt-Only Skills) | 20.5% |
| RA-Agent (multi-loop) | 31.2% |
| Search-R1 (학습 기반) | 29.9% |
| HASP PF-only (추론 시점 개입) | 51.0% |
| HASP + 보조 티처 선택 | 56.2% |
| HASP-Evolve + RS (학습 + 스킬 진화) | <span style="background-color: #fff59d"><strong>60.3%</strong></span> |

같은 스킬을 프롬프트에 넣을 때와 실행형으로 감쌀 때 <span style="background-color: #fff59d"><strong>20.5% → 51.0%로 약 30점 차이</strong></span>가 납니다. 핵심은 이겁니다: 병목은 스킬 본문의 품질이 아니라, <span style="background-color: #fff59d"><strong>발동 조건과 개입 방식을 코드로 명시하는 일</strong></span>이었습니다.

논문 원문: https://arxiv.org/abs/2605.17734

## 스킬이 왜 무시되는가

기존 스킬/메모리 시스템(ExpeL, Reflexion, Voyager 계열)은 교훈을 자연어로 저장했다가 프롬프트에 넣거나 검색해서 보여줍니다. 근데 이 방식은 "권고(advisory)"일 뿐입니다. 모델이 읽어도 다음 액션을 그대로 실행하면 끝입니다.

HASP는 여기서 한 단계 더 갑니다. 각 스킬을 두 개의 인터페이스를 가진 함수로 만듭니다.

- `should_activate(state, action)`: 지금 상태에서 이 스킬이 발동해야 하는가
- `intervene(...)`: 발동하면 다음 액션을 고치거나 corrective context를 주입

예를 들어 "같은 검색어를 반복하지 마라"는 텍스트 교훈 대신, 반복 검색 상태를 감지하면 검색어를 다시 쓰는 PF가 동작하는 식입니다.

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/fig-1-p2.png)

그림 1(원문 Figure 1): 프롬프트 스킬(왼쪽)과 PF(오른쪽)의 차이. PF는 런타임 상태에서 발동해 액션 수정/맥락 주입으로 개입합니다.

## 하네스 구조

HASP는 외부 하네스로 동작합니다. 매 스텝마다:

1. 기본 정책이 다음 액션 제안
2. 하네스가 관련 PF 후보 검색
3. `should_activate` 평가 → 활성화되면 개입
4. 수정된 액션 또는 주입된 맥락으로 루프 계속

개입은 두 가지 방식입니다. 액션 자체를 고치는 것(과도하게 좁은 검색어를 다시 쓰기)과, 추론에 경고 맥락을 주입하는 것(비슷한 개체 혼동 경고). 원본 제안과 수정된 액션 쌍이 기록되어서, 그대로 학습 신호가 됩니다.

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/fig-2-p4.png)

그림 2(원문 Figure 2): HASP 전체 구조. (a) 추론 시점 PF 개입, (b) PF 기록이 포스트트레이닝과 스킬 라이브러리 업데이트로 이어지는 흐름.

스킬 라이브러리 초기화는 학습 풀의 실패 사례에서 시작합니다. 반복되는 실패-수정 패턴(조기 종료, 개체 혼동 등)을 후보 PF로 요약하고, 문법/인터페이스/목업 실행 검증을 통과해야 라이브러리에 들어갑니다.

## 학습 신호로 내재화

PF가 개입할 때마다 (상태, 원래 액션, 수정된 액션, 주입 맥락, 결과) 기록이 남습니다. HASP는 이 기록을 4개 신호로 채점합니다: 개입 시점(timing), 방식(mode), 올바름(correctness), 결과(outcome). 가중치는 (0.15, 0.10, 0.25, 0.50)로 <span style="background-color: #fff59d"><strong>결과(outcome)에 절반 가중치</strong></span>를 둡니다.

이 점수로 세 가지 학습 경로를 만듭니다.

- SFT: 수정된 액션에 대한 지도 학습
- Rejection Sampling (RS): 태스크 성공 + PF 정합성 점수로 상위 트라젝토리만 학습
- On-policy distillation (OPD): 학생 정책 자신의 롤아웃에서 PF로 고쳐가며 학습. 고정 라이브러리에서 62.5%로 가장 강함

메인 레시피는 HASP-Evolve + RS입니다. 잔여 실패를 새 후보 PF로 요약하고, 검증 필터를 통과시켜 라이브러리를 갱신하는 닫힌 루프까지 붙입니다.

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/table-4-p7.png)

표(원문 Table 4): 학습/진화 전략별 소거 실험. 고정 라이브러리 대비 Evolve + RS가 웹검색 60.3%, 수학 45.4%.

## 코딩과 수학에서도 되는가

코딩(HumanEval/MBPP/BigCodeBench)에서는 PF-only가 평균 pass@1 63.4%, 티처 선택을 붙이면 68.7%, PF 기반 학습까지 하면 <span style="background-color: #fff59d"><strong>69.9%</strong></span>입니다. vanilla SFT 대비 +12.4%입니다.

수학은 조금 다릅니다. 웹검색만큼 드라마틱하진 않지만 PF-only 35.9% → 티처 38.8% → Evolve+RS 45.4%로 오릅니다. GameOf24에서 62.0%. 근데 AgentFlow(Flow-GRPO)가 수학 평균 51.5%로 이 논문 세팅보다 높습니다. 수학은 스킬 개입보다 전체 흐름 RL이 더 맞는 영역이라는 걸 보여주는 대비입니다.

## 소거 실험: 필터링이 없으면 무너진다

가장 실무적으로 중요한 구간입니다. 스킬 라이브러리 진화에서:

- 실행 가능 필터 + 티처 필터 둘 다: 60.3%
- 실행 필터만: 48.8%
- 티처 필터만: 47.2%
- 필터 없이 진화: <span style="background-color: #fff59d"><strong>36.3% (급락)</strong></span>

검증 안 된 PF가 라이브러리에 섞이면 24점이 사라집니다. 스킬 자기진화 시스템을 만들 때 <span style="background-color: #fff59d"><strong>실행 검증 + 리뷰 필터는 선택이 아니라 필수</strong></span>라는 게 이 논문의 경고입니다.

PF 점수 신호 소거에서는 mode 제거 시 -15.5점, outcome 제거 시 -12.8점으로, "어떻게 고쳤는지"와 "결과가 어땠는지"를 함께 봐야 한다는 결과가 나옵니다.

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/table-6-p9.png)

표(원문 Table 6): 복구된 실패 구조와 진화된 PF 패밀리의 활용도.

## 케이스 스터디

![](/images/hasp-skill-programs-executable-intervention-2026-08-25/fig-4-p9.png)

그림 4(원문 Figure 4): MuSiQue 2-hop 개체 정리 질문 사례. PF가 개체 혼동 상태를 감지해 검색어를 리다이렉트하는 과정.

## 내 해석: 하네스 엔지니어링 관점

원문 근거와 제 해석을 구분해서 정리하면:

- (원문) 스킬을 실행형으로 만들면 프롬프트 주입 대비 큰 폭으로 올라간다.
- (원문) 진화에는 안정적 선택(필터)이 필요하고, OPD와 진화를 동시에 돌리면 불안정해진다(Evolve+OPD 56.7%로 역행).
- (해석) 이건 "스킬 본문 품질"보다 "발동 조건과 개입 인터페이스의 명시성"이 병목이었다는 뜻입니다. 비슷한 맥락에서 Skill-Use 벤치마크(arXiv 2608.04828)는 프론티어 모델들도 trigger/compliance/boundary 전부를 안정적으로 못 한다고 측정했습니다. 두 결과는 같은 방향을 가리킵니다.
- (해석) 실무적으로는, 노트/교훈을 쌓는 것보다 `should_activate`/`intervene` 인터페이스가 있는 실행 스킬 몇 개가 더 싸고 효과적일 수 있습니다. 7B 모델 기준 결과라는 점은 한계로 남습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
