---
title: "에이전트 훈련 환경은 개수가 아니라 깊이임 — Echoverse가 증명한 것"
date: 2026-08-01
tags:
  - agent
  - computer-use
  - RL
  - harness
  - synthetic-environment
  - LLM
draft: false
summary: "컴퓨터 사용 에이전트 훈련의 병목은 환경 개수가 아니라 깊이였음. 얕은 환경은 훈련 안 한 것보다 나쁘고, 깊은 환경은 9B 모델을 36.5%에서 67.1%로 올림. 환경 설계 원칙을 실무 관점으로 정리함."
source_url: "https://arxiv.org/abs/2607.28074"
authors: ["Yash Pandya", "Sahil Gupta", "Sarthak Harne", "Archana Yadav", "Kavyansh Chourasia", "Hussein Mozannar", "Vibhav Vineet", "Sara Abdali", "Corby Rosset", "Yash Lara", "Ahmed Awadallah", "Ece Kamar", "Akshay Nambi"]
institution: "Microsoft Research"
---

컴퓨터 사용 에이전트를 훈련하려면 합성 환경을 많이 만들면 된다고 믿기 쉬움. Microsoft Research의 Echoverse가 그 가설을 깨고 "깊이"가 진짜 병목임을 증명했음. 원문은 [arXiv:2607.28074](https://arxiv.org/abs/2607.28074).

1. 배경. 진짜 업무(예약 결제, 메일 발송, 뱅킹 이체)는 전부 로그인 뒤에 있음. 이 작업은 상태를 바꾸고, 여러 화면·사용자에 걸쳐 의존성을 갖고, 성공을 화면이 아니라 DB로 판단해야 함. 실제 웹사이트는 리셋도 안 되고 그라운드 트루스도 안 보여줘서 훈련에 못 씀. 그래서 합성 환경인데, 기존 파이프라인은 "몇 개를 만드는가"에만 집중했음.

![](/images/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents/gifs/training-simulation.gif)

2. Echoverse의 깊이 정의는 다섯 가지임. 제어·권한·오류의 충실도(예약 인원을 바꾸면 가격이 바뀌어야 함), 교차 행위자 상태(한 사용자의 메시지가 다른 사용자 받은 편지함에 나타남), 워크플로우 의존성(항공편 없이 좌석 선택 불가), 그라운드 가능한 검증(픽셀이 아니라 SQL diff로 판정), 능력 타겟팅(에이전트가 실제로 실패하는 인터랙션에 맞춤). 그리고 이걸 기계 검증 가능한 클레임으로 변환해서 95% 이상 통과할 때까지 수리함.

![Echoverse 환경 설계](/images/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents/fig-1-p2.png)

![](/images/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents/gifs/booking-flight-computer.gif)

3. 가장 파괴적인 발견. 얕은 환경에서 훈련하면 훈련 안 한 것보다 나쁨. Allrecipes 도메인에서 베이스 80.0이 얕은 환경 학습 후 75.0으로 퇴행함. 깊은 환경은 85.0으로 오름. 얕은 환경은 "외형적으로 옳아 보이는 클릭"만 반복하게 만들어서 작동하지 않는 행동을 성공으로 학습하게 한다는 것임. 합성 환경 양산 파이프라인이 벤치마크 숫자는 올리면서 실제 성능을 깎아먹는 함정이라는 경고임.

![얕은 환경 vs 깊은 환경 성능](/images/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents/fig-2-p7.png)

4. 규모와 성과. 메일·캘린더·뱅킹·헬스케어·숙박 등 10개 풀 도메인과 데이트피커·중첩 필터 2개 능력 환경을 만듦. 21,009개 검증 궤적으로 SFT해서 Qwen3.5-9B가 36.5%에서 67.1%로 오름. GPT-5.4(81.1%)와의 격차를 14점으로 좁혔고 EchoMail·EchoBank에선 동등하거나 능가함.

5. 능력 월드 개념이 실무적으로 재밌음. 에이전트가 데이트피커에서만 실패하면 예약 사이트 전체를 하나 더 만들 필요 없이 그 컨트롤만 떼서 100개 렌더링으로 양산함. "3월의 마지막 목요일" 같은 추론형 태스크 포함. 그리고 이 훈련은 서로를 강화함. 데이트피커만 훈련해도 홀드아웃 필터가 62.8→82.1로 오르고 필터만 훈련해도 데이트피커가 34.0→50.7로 오름. 에이전트가 레이아웃이 아니라 규칙을 배운다는 증거임.

![도메인별 성능 향상](/images/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents/fig-5-p12.png)

6. 스케일링 축 실험도 결론이 명확함. 고정 환경에서 궤적 수를 늘리면(6,400→20,000) 합성 평균은 오르지만 실제 웹 전이는 포화됨(WebVoyager 54.8→55.6 정체). 환경 수를 늘리면 둘 다 오름. 일반화의 레버는 궤적 볼륨이 아니라 환경 다양성임.

7. 공동 진화가 복리를 만듦. EchoStay의 guest-count 컨트롤이 조용히 망가져 있어서 올바른 예약이 등록이 안 됐음. 같은 롤아웃을 모델 훈련 데이터이자 환경 결함 진단으로 이중 사용해서 수리하자 예약 가능 태스크가 48%→78%로, 모델 성능이 16.2%→38.5%로 두 배 이상 오름. 모델만 고치는 선형 구조와 달리 이 루프는 계속 새로운 능력 갭을 노출함.

![스케일링 축 실험 결과](/images/2026-08-01-echoverse-deep-evolving-environments-computer-use-agents/fig-8-p15.png)

8. RL도 돌림. 핵심은 상태 공간을 픽셀이 아니라 DB로 정의해서 리셋은 DB 복사 한 장, 보상은 SQL diff로 해결한 것임. GRPO에 궤적 보상(최종 DB 판정)과 밀집 단계 보상(반복·no-op은 0점)을 결합하되, 궤적 판정이 틀리면 마지막 단계 밀집 보상을 0으로 강제해서 과정 보상이 결과를 대체하지 못하게 함. 5개 환경에서 홀드아웃 점수 58.8%→68.0%.

9. 내 에이전트 평가 환경 설계에 반영할 것. 첫째, 성공 판정을 화면 캡처 비교가 아니라 데이터 상태 비교로 만드는 것. 이거 하나로 리셋·검증·보상이 전부 단순해짐. 둘째, 합성 테스트 시나리오를 빨리 많이 만들기보다 의존성 있는 시나리오 소수를 깊게 만드는 것. 셋째, 에이전트 실패 로그를 모델 문제와 환경(테스트) 결함으로 분리해서 환경 쪽을 먼저 고치는 것. 실패의 상당수가 환경 버그였다는 게 이 논문의 경험임.

10. 문제제기. SFT가 GPT-5.4 교사에 의존하고, 10개 도메인은 실제 웹 다양성보다 좁고, RL은 5개 환경만, 실제 웹 전이 개선은 있지만 크지 않음. 근데 "환경 품질 > 환경 수량"이라는 측정된 결론은 그대로 가져갈 가치가 있음.

11. 결론. 환경이 곧 보상임. DB 기반 상태 정의 하나로 훈련·검증·RL 전제조건이 풀리고, 공동 진화 루프가 복리를 만듦. 코드는 [aka.ms/echoverse](https://aka.ms/echoverse)에 공개돼 있음.

에이전트 실패를 학습 신호로 바꾸는 루프 설계는 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』에서 실습해볼 수 있음.
