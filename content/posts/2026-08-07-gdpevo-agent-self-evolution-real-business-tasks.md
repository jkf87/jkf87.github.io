---
title: "에이전트 자기진화를 실제 비즈니스에서 측정한 첫 벤치마크 — GDPevo 결과 해석"
date: 2026-08-07
tags:
  - agent
  - self-evolution
  - benchmark
  - LLM
  - harness
  - evaluation
  - enterprise
  - automation
  - skill
  - loop
source: huggingface
source_url: https://arxiv.org/abs/2608.03764
github_url: https://github.com/Prism-Shadow/GDPevo
authors:
  - conanssam
description: "자기진화가 실제 기업 워크플로우에서 효과가 있는지 귀속 가능하게 측정함. fewshot이 최대 +16.44pp, 근데 오라클 상한 91.6%엔 한참 못 미침. 진화 방법보다 모델 지능이 더 중요하다는 발견까지 정리함."
---

"에이전트가 경험에서 배운다"는 말의 검증 방법이 없었음. GDPevo가 실제 비즈니스 워크플로우에서 자기진화를 귀속 가능하게 측정하는 첫 벤치마크를 만들었음. 원문은 [arXiv:2608.03764](https://arxiv.org/abs/2608.03764).

1. 기존 평가의 문제 세 가지. 첫째, ALFWorld·WebShop(각각 텍스트 가상 세계의 집안일 과제, 모의 온라인 쇼핑 구매 과제를 다루는 연구용 에이전트 벤치마크) 같은 연구용 환경에 머물러서 CRM·ERP·의료·법무 같은 실제 기업 워크플로우를 다룬 벤치마크가 없었음. 둘째, train-test split이 학습 효과를 의도적으로 설계하지 않아서 점수가 올라도 경험 때문인지 운 때문인지 알 수 없었음. 셋째, 정적 벤치마크는 학습 데이터 오염으로 유효성이 무너짐.

2. 핵심 설계는 규칙 혼합(rule hybridization)임. 각 비즈니스 워크플로우를 원자적 비즈니스 규칙으로 분해함. CRM 리드 캡처라면 후원자 상태 우선순위, 블랙리스트 제외, 연락처 중복 제거, 후속 조치 스케줄링 같은 규칙들임. 이 규칙 부분집합을 훈련 태스크 5개에 나눠 심고 테스트 태스크에서는 새로 조합해서 냄. 훈련에서 규칙을 추론하고 테스트에서 조합 적용해야 점수가 오르는 구조라 학습 효과가 귀속 가능함.

![GDPevo 자기 진화 프레임워크](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-1-p4.png)

3. 규모와 운영. 6개 도메인 24개 태스크 그룹 240개 태스크임. 파이프라인(시드 발견 → 태스크 그룹 생성 → 검증 리뷰)이 자동화돼 있어서 V1에서 V2 확장에 이틀 걸렸음. 오염 우려가 생기면 새 버전을 빨리 찍을 수 있음. 정적 벤치마크의 약점을 운영으로 우회하는 접근임.

4. 실험 설계. 에이전트는 GPT-5.5/Codex, Opus 4.8/Claude Code, GLM-5.2/Codex, DeepSeek-V4-Pro-Preview/Codex 4종임. 감독 타입은 base(진화 없음), fewshot(훈련 문제+정답, SFT 유사), reflect(훈련 문제+자기 시도 점수만, RL 유사), self(훈련 문제만, 비지도 유사) 4가지임.

![실험 설계](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-2-p8.png)

5. 결과 1. fewshot이 모든 에이전트에서 최고였고 base 대비 +2.59~+16.44pp 향상이었음. 진화는 모델 훈련을 대체할 수 있음. GLM-5.2 fewshot이 GPT-5.5 base를 10.72pp 차이로 앞섰는데 비용은 절반 수준, DeepSeek fewshot은 GPT-5.5 base와 비슷한 정확도에 비용 1/28이었음. 진화가 비용도 줄임. GPT-5.5 fewshot은 정확도를 15.14pp 올리면서 테스트 비용을 20.88% 줄였음.

![](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/gifs/pokemon-evolving-glow.gif)

![feature 관점 결과](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-3-p9.png)

6. 결과 2, 그리고 반직관적인 부분. 출발점이 낮다고 더 많이 배우지 않음. base가 가장 낮았던 DeepSeek(43.58%)의 진화 효과도 가장 작았고(+5.21pp), base가 가장 높았던 Opus 4.8(50.63%)의 진화 효과가 가장 컸음(+16.44pp). 강한 모델일수록 경험에서 더 뽑아낸다는 것임.

7. 결과 3. 크로스 도메인 전이에서는 정반대임. fewshot은 같은 도메인에선 강한데 다른 도메인으로 넘어가면 해로운 경우가 많았음. SFT와 비슷한 과적합 패턴임. reflect는 크로스 도메인에서 더 안정적이어서 최악이 -1.0pp에 그쳤고 ERP → Finance로 +6.5pp 전이도 관찰됐음. RL이 더 일반적인 스킬을 만든다는 해석임. 내 운영 원칙으로 정리하면, 같은 업무 반복엔 정답 포함 경험을, 이웃 업무로 확장할 땐 피드백만 주는 게 맞다는 것임.

![상한 분석](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/fig-4-p16.png)

8. 결과 4가 내겐 제일 중요함. 스킬 생성기 비교에서 가장 단순한 Naive 생성기가 가장 성능이 좋았음(65.12%, +15.46pp). Codex, Claude Code, DeepAgents 같은 정교한 하네스가 전부 Naive보다 아래였음. 진화 방법보다 모델 자체 지능이 진화 효과를 결정한다는 뜻임. 하네스를 과도하게 엔지니어링하면 오히려 역효과가 났다는, 나 같은 하네스 만드는 사람에게는 약간 아픈 결과임. 근데 내 체감과도 맞음. 스킬 추출 파이프라인을 정교하게 만들수록 본질 아닌 데 토큰을 쓰는 경우가 있었음.

![](/images/2026-08-07-gdpevo-agent-self-evolution-real-business-tasks/gifs/this-meeting-is-over.gif)

9. 상한 분석. 모든 규칙을 미리 알려준 oracle 설정이 91.6%인데 최고 진화 에이전트는 65%대임. 자기진화 능력이 아직 갈 길이 멀다는 정직한 측정임. 채점도 LLM judge가 아니라 결정론적 규칙 그레이더라 각 실패를 특정 규칙 위반으로 추적 가능함. 비용을 토큰·턴·달러로 정확도와 함께 보고하는 것도 운영 관점에서 올바름.

10. 문제제기. 240 태스크는 여전히 작고, 규칙 혼합 설계가 "규칙 기반 업무"에 최적화돼서 판단이 주가 되는 업무에는 그대로 안 옮겨짐. 그리고 6개 도메인이 전체 기업 워크플로우를 대표한다고 보기도 어려움.

11. 결론. 자기진화는 효과가 있고(최대 +16.44pp) 비용도 줄지만 오라클 상한엔 한참 못 미침. fewshot이 안정적이고 도메인 간엔 reflect가 낫고, 진화 방법보다 모델 지능이 중요함. 코드는 [GitHub](https://github.com/Prism-Shadow/GDPevo)에 공개돼 있어서 내 자동화의 "경험 반영" 효과를 같은 귀속 구조로 측정해볼 수 있음.

자기진화 루프 실습은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 시작해볼 수 있음.
