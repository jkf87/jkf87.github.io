---
title: "재귀적 자기개선(RSI) 서베이 — 1,250편을 관통하는 검증 계층"
date: 2026-08-20
tags:
  - agent
  - self-improvement
  - evaluation
  - paper-review
draft: false
---

## 결론 먼저

UCR·IIT 연구진이 arXiv 2024–2026년 <span style="background-color: #fff59d"><strong>1,250편의 자기개선 논문을 두 축으로 정리한 서베이</strong></span>(arXiv:2607.07663)를 읽었습니다. 핵심은 이겁니다.

- "self-refine, self-reward, self-evolve" 같은 용어는 전부 다른 야망을 가리키는 말이라 분류가 필요하다.
- <span style="background-color: #fff59d"><strong>거의 모든 실용 시스템은 "사람이 루프 위에 있는(human-on-the-loop)" 상태, 즉 자동 검증 신호를 사람이 감사하는 구간에 몰려 있다</strong></span>.
- <span style="background-color: #fff59d"><strong>성공·실패를 가르는 변수는 하나 — 검증 신호의 강도</strong></span>. <span style="background-color: #fff59d"><strong>형식 검증기가 최강, 모델 자기평가가 최약</strong></span>이고, 입증된 자기개선 성과는 이 계층을 그대로 따라간다.

원문: [Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops](https://arxiv.org/abs/2607.07663) (Mingguang Chen 외, 2026-07-08)

## 두 축 택소노미

서베이는 각 논문을 두 질문 위에 배치합니다.

축 1 — 무엇을 개선하는가:

| 카테고리 | 논문 수 | 2026년 비중 |
|---|---|---|
| 배포 시점 자기진화 (출력 정제, 테스트타임 학습, 하네스/스킬 진화) | 393 | 74% |
| 학습 시점 자기반복 (self-reward RL, CoT 자기학습, self-play) | 340 | 69% |
| 자기평가 (judge, PRM, verifier, rubric, 메타평가) | 318 | 82% |
| 자동 연구 (AI scientist, 진화적 프로그램 발견) | 139 | 76% |
| 이론·한계·안전 | 60 | 57% |

축 2 — 루프 폐쇄 정도: 사람이 매 변경을 검토(human-in-the-loop) → 자동 신호를 사람이 감사(human-on-the-loop) → 시스템이 스스로 생성·검증·적용(closed loop).

![Figure 1: 두 축 택소노미](/images/2026-08-20-rsi-taxonomy-survey/fig-1-p5.png)

그리드에서 눈에 띄는 건 두 가지구요. 밀도는 중간 행(human-on-the-loop)에 집중돼 있고, 폐쇄 루프 행은 어디나 성기며, 그중 가장 중요한 칸은 <span style="background-color: #fff59d"><strong>자기평가 × 폐쇄 루프 — 시스템이 자기 기준("더 나음")을 스스로 다시 쓰는 지점</strong></span>입니다. 유계 자기정제가 열린 RSI로 넘어가는 경계가 정확히 여깁니다.

## 검증 계층이 전부를 결정한다

서베이의 독특한 선택은 자기평가를 부록이 아니라 독립 카테고리로 다룬 겁니다. 논리는 이렇습니다. <span style="background-color: #fff59d"><strong>모든 개선 루프는 "어떤 신호가 인간 판단을 대체할 수 있다"는 주장</strong></span>이고, 그래서 평가자 설계가 나머지 세 카테고리를 떠받치는 기둥이라는 거예요.

검증 신호를 강한 것부터 세우면:

1. 형식 검증기 (proof checker, 실행 피드백)
2. 학습된 리워드/프로세스 보상 모델
3. LLM judge, 루브릭
4. 내재적 자기평가 (최약)

관찰된 규칙은 두 가지입니다.

- <span style="background-color: #fff59d"><strong>입증된 자기개선 강도가 이 계층 순서를 그대로 따른다</strong></span>. 코드·수학처럼 답이 검사 가능한 영역에서 자기학습이 작동하고, 그렇지 않은 곳에서는 성능이 저하된다.
- 대표 실패 모드 — <span style="background-color: #fff59d"><strong>자기확인 루프(self-confirming loop), 모델 붕괴, 다양성 붕괴</strong></span> — 는 전부 이 계층을 어겼을 때 나타난다.

![Figure 5: 검증 계층](/images/2026-08-20-rsi-taxonomy-survey/fig-5-p18.png)

## 부정 결과의 계보

이 서베이에서 가장 가치 있는 부분은 진단 논문들입니다.

- Huang et al.의 유명한 부정 결과: <span style="background-color: #fff59d"><strong>외부 피드백 없이는 LLM이 추론을 자기교정하지 못하고, 순진한 자기교정은 오히려 답을 악화시킨다</strong></span>.
- 문서 번역 9개 모델·7개 언어쌍 연구: 정제 이득은 유창성·스타일·용어에서 오고, 적절성(adequacy) 개선은 제한적이며 일관성이 없다. <span style="background-color: #fff59d"><strong>정제는 초고의 실제 오류를 고치기보다 정제자 자기 분포 쪽으로 출력을 끌어당긴다</strong></span>.
- SkillsBench: <span style="background-color: #fff59d"><strong>사람이 쓴 스킬은 통과율을 16.2점 올리는데, LLM이 쓴 스킬은 측정 가능한 이득이 없다</strong></span>.

2026년 문헌은 이 결과를 내면화했구요. 새 시스템 거의 전부가 비판을 외부 신호(실행, 검색, 탐지기, 솔버)에 기반하고, "내재적 자기교정" 논문은 드물어졌습니다. 택소노미로 말하면 폐쇄 루프 자기비판에서 검증 기반 정제로 조용히 후퇴했고, 그게 신뢰성을 높였다는 것. 자율성을 줄여서 신뢰성을 산 셈이에요.

## 하네스·스킬 진화와 비용

"에이전트가 자기를 다시 쓰는" 구간의 실상도 정리돼 있습니다.

- 실제로 진화하는 건 거의 항상 <span style="background-color: #fff59d"><strong>샌드박스된 한 컴포넌트뿐, 나머지는 고정</strong></span>이고 고정 벤치마크로 검증한다.
- 34개 설정 비교에서 self-consistency·정제·토론·MoA를 아우른 결과, <span style="background-color: #fff59d"><strong>피크 이득 +7.1점이 약 20배 컴퓨트에서야 나온다</strong></span>. 셀프컨시스턴시는 일찍 포화되고 멀티에이전트 이득은 오래 간다. 이득 상당수는 재귀보다 더 나은 엔지니어링에서 나온다.
- 스킬 라이브러리는 지속·실행 가능해서 가장 날카로운 안전 표면이다. 추론 시점 실수는 증발하고 잘못된 가중치 업데이트는 롤백되지만, <span style="background-color: #fff59d"><strong>공유 라이브러리의 오염된 스킬은 전파된다</strong></span>.

![Figure 3: 지속성 순으로 본 배포 시점 자기진화](/images/2026-08-20-rsi-taxonomy-survey/fig-3-p7.png)

## 현장 신호와 남은 질문

Anthropic 에세이 프레임(2026-05 기준 Claude가 병합 코드의 80% 이상을 작성)은 동기 부여용 인용일 뿐 증거로 쓰이지 않습니다. 서베이의 판단은 이렇습니다. 실행 쪽은 스펙트럼 멀리 왔는데 <span style="background-color: #fff59d"><strong>"어떤 문제가 중요한가"를 정하는 리서치 방향 설정이 마지막 병목</strong></span>이고, 그게 검증 계층의 최상단에 앉는다.

가장 큰 빈틈으로 꼽은 건 <span style="background-color: #fff59d"><strong>거버넌스급 자기개선 측정</strong></span> — 실무에 들어가 있는 자기개선을 제대로 잴 도구가 없다는 겁니다.

## 내 해석

원문 주장과 제 해석을 구분해 정리하면:

- 서베이 근거: 자기개선 성공 여부는 검증 신호 강도와 정확히 궤를 같이한다.
- 내 해석: 그래서 실무에서 할 일은 "자기개선 도입"이 아니라 <span style="background-color: #fff59d"><strong>내 도메인의 검증기를 먼저 세우는 것</strong></span>입니다. 실행 가능한 피드백(테스트, 컴파일, 실행 로그)이 있는 곳에만 루프를 달면 됩니다.
- 서베이 근거: 스킬 지속성은 리스크 계산을 바꾼다. 오염은 전파된다.
- 내 해석: 스킬/메모리를 에이전트에 달 거면 감사 가능한 단위(루브릭, diff, 롤백)로 제한하는 게 SHARP 패턴의 교훈입니다.

원문 근거는 전부 서베이 본문이고, "내 해석" 표시 없는 문장은 원문 정리입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

![Figure 6: 코퍼스 분기 성장](/images/2026-08-20-rsi-taxonomy-survey/fig-6-p26.png)

참고: 2026년 7월 8일자 v1 기준 정리이고, <span style="background-color: #fff59d"><strong>코퍼스의 74%가 2026년 게시라 인용 수는 사실상 0입니다</strong></span> — 저 숫자는 활동 지도이지 영향력 측정이 아닙니다.
