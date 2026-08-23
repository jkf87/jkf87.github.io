---
title: "당신의 에이전트는 정체됐는데, 환경은 이미 배울 걸 다 준 상태일 수 있다 — EnvHarness 정리"
date: 2026-08-24
tags: [agent, LLM, RL, environment, harness, skill-learning]
draft: false
---

에이전트를 학습시키다 보면 이상한 지점에 도달합니다. 모델은 분석도 하고 계획도 잘 세우는데 성능 곡선이 평평해지는 시점이 오죠. Google Cloud AI Research 팀이 8월 20일에 올린 [EnvHarness 논문](https://arxiv.org/abs/2608.19880)은 그 벽의 원인을 모델이 아니라 <span style="background-color: #fff59d"><strong>환경이 정적이라는 데서 찾고, 환경을 새로 만들지 말고 감싸서 재구성하자</strong></span>는 제안을 합니다.

## 정적 환경의 딜레마

LLM 에이전트는 환경과 상호작용하며 배웁니다. 웹, 코드베이스, 로봇 플랫폼 어디서든 환경이 태스크를 내고, 상태를 바꾸고, 성공을 평가하죠.

문제는 이 환경이 <span style="background-color: #fff59d"><strong>인간이 하드코딩해서 만든 정적 존재</strong></span>라는 겁니다. 어떤 에이전트가 약한지 모르고, 에이전트가 성장하면 가르칠 게 바닥납니다.

환경을 자동 생성하려는 시도도 있었지만 <span style="background-color: #fff59d"><strong>도메인별 파이프라인이 필요하고, LLM이 만든 검증기는 비싸거나 불안정</strong></span>했습니다. 그러면 어떻게 할까요?

## 환경에도 하네스를 씌운다

EnvHarness의 발상은 깔끔합니다. 우리는 이미 언어 모델에 하네스를 씌워왔잖아요? 스킬, 메모리, 도구를 플러그인으로 얹어서 얼어 있는 모델을 유능한 에이전트로 만들었죠. EnvHarness는 그 하네스 개념을 <span style="background-color: #fff59d"><strong>상호작용의 반대편, 환경에 적용</strong></span>합니다. 원본 환경 로직은 건드리지 않는 플러그인 계층이에요.

- Stage: 에피소드의 시작점을 바꾼다
- Contract: 허용 행동과 관측을 제어한다
- Chain: 여러 환경을 연결해 긴 에피소드를 만든다

그래서 도메인 불문 적용되고, <span style="background-color: #fff59d"><strong>새 환경이 원본의 인간 제작 검증기를 그대로 상속</strong></span>받아요. LLM 검증기의 불안정성 문제를 구조적으로 피해갑니다.

자동화는 EnvRigger가 담당합니다. 정책을 블랙박스로 보고 성공/실패 트라젝토리에서 취약점을 진단하고, 컴포넌트를 합성하고, 새 롤아웃으로 검증하는 루프죠. <span style="background-color: #fff59d"><strong>검증을 통과해야만 커밋</strong></span>됩니다.

## 숫자로 보는 성과

5개 벤치마크(ALFWorld, WebArena, SWE-bench Verified, OfficeQA, SpreadsheetBench), 4개 도메인에서 확인했습니다.

![Figure 1. 전체 성능](/images/2026-08-24-envharness-envrigger/fig-1-p1.png)
*Figure 1. EnvHarness 환경으로 학습한 에이전트가 원본 환경 학습을 일관되게 앞선다. 동일 환경 예산에서 EnvHarness는 계속 개선되고 실제/생성 환경은 평탄해진다. (원문 Figure 1)*

- ALFWorld OOD <span style="background-color: #fff59d"><strong>+9.0포인트 (61.4 → 70.4)</strong></span>, 원본 환경 대비
- SWE-bench Verified SR 49.8 → 52.5 (+2.70), 동시에 <span style="background-color: #fff59d"><strong>평균 스텝 55.0 → 49.6으로 단축. no-skill 대비 9.8% 감소</strong></span>
- 전용 생성기 SWE-smith 대비 SR +2.46, 스텝 −5.11 우위
- GRPO 온라인 RL에서도 ALFWorld In-Dist <span style="background-color: #fff59d"><strong>81.4 → 87.9 (+6.5)</strong></span>, WebShop 스코어 75.6 → 79.2
- OfficeQA EM +1.80, SpreadsheetBench Pass@1 +3.27

![Table 2](/images/2026-08-24-envharness-envrigger/table-2-p9.png)
*Table 2. ALFWorld와 WebArena 결과. 3회 독립 실행 평균. (원문 Table 2)*

![Table 3](/images/2026-08-24-envharness-envrigger/table-3-p9.png)
*Table 3. SWE-bench Verified, OfficeQA, SpreadsheetBench 결과. (원문 Table 3)*

인상적인 건 원본 환경에서 스킬을 뽑으면 오히려 성능이 떨어지는 케이스가 있었다는 점입니다. SpreadsheetBench에서 no-skill보다 낮아지기도 했어요. <span style="background-color: #fff59d"><strong>이미 하는 행동만 반복 연습시키는 환경에서 나오는 스킬은 중복이거나 열등</strong></span>라는 해석이 가능하죠. Chain 컴포넌트 결합 시에는 SR 54.3과 평균 43.1 스텝을 기록했습니다 (Table 5).

## 어디에 쓸 수 있나

환경 구축 비용 때문에 에이전트 학습이 막혀 있다면, <span style="background-color: #fff59d"><strong>검증된 기존 환경을 감싸서 난이도와 범위를 조정하는 게 훨씬 저렴한 대안</strong></span>입니다. 정책-환경 공진화 루프도 현실적인 운영 방향이 되고요.

물론 컴포넌트 검증에 롤아웃 비용이 들고 도메인별 프롬프트 템플릿은 여전히 필요합니다. 완전한 제로 도메인 지식은 아니에요.

코드는 공개돼 있습니다: [github.com/google-research/envharness](https://github.com/google-research/envharness)

원문: [arXiv:2608.19880](https://arxiv.org/abs/2608.19880)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
