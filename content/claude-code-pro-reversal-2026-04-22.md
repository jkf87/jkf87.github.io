---
title: "Anthropic, Claude Code Pro 제외했다가 되돌렸나"
date: 2026-04-22
tags:
  - Claude
  - Claude Code
  - Anthropic
  - pricing
  - subscription
  - SaaS
  - 개발도구
  - AI
description: "Claude 가격표에서 Pro의 Claude Code가 빠졌다가 다시 돌아온 것처럼 보였습니다. 단순 실수인지, 정책 흔들림인지, 그리고 그 뒤에 있는 Anthropic의 인프라 압박까지 같이 봐야 하는 이유를 정리했습니다."
---

- **가격 페이지**: [claude.com/pricing](https://claude.com/pricing)
- **Anthropic 공식 1**: [Anthropic and Amazon expand collaboration for up to 5 gigawatts of new compute](https://www.anthropic.com/news/anthropic-amazon-compute)
- **Anthropic 공식 2**: [Powering the next generation of AI development with AWS](https://www.anthropic.com/news/anthropic-amazon-trainium)
- **Anthropic 공식 3**: [Expanding our use of Google Cloud TPUs and Services](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- **도움말**: [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- **직전 글**: [Claude Pro에서 Claude Code 빠지나, Anthropic 가격 페이지에 뜬 이상 신호](./claude-code-pro-pricing-confusion-2026-04-22)

Anthropic 가격표가 하루 동안 두 번 말을 바꾼 것처럼 보였음.

처음엔 Pro 플랜의 Claude Code가 **X**로 보였음.
그래서 다들 이렇게 읽었음.

- 이제 Pro에서는 Claude Code 못 씀
- Max로 올리라는 뜻임
- 개발자 요금제가 사실상 다시 짜이는 중임

근데 몇 시간 뒤 다시 보니 체크로 돌아와 있었음.

즉 지금 질문은 하나임.
**실수였나, 철회였나, 아니면 내부 검토 흔적이 잠깐 밖으로 튄 건가.**

먼저 논란을 키운 장면은 이거였음.

![Claude 가격 페이지에서 Pro 플랜의 Claude Code가 X로 보이는 화면](./images/claude-code-pro-reversal-2026-04-22/claude-pricing-pro-code-x.jpg)
*이전 캡처. Claude Code 행의 Pro 칸이 X로 표시되어 있었음.*

그리고 지금은 이렇게 다시 보임.

![Claude 가격 페이지에서 Pro 플랜의 Claude Code가 다시 체크로 보이는 화면](./images/claude-code-pro-reversal-2026-04-22/claude-pricing-pro-code-restored.jpg)
*현재 캡처. Claude Code 행의 Pro 칸이 다시 체크로 보임.*

## 1. 이건 가격표 한 칸 문제가 아니었음

Claude Code는 부가 기능이 아님.
많은 사람한테는 Claude 구독의 핵심임.

그래서 Pro에서 이게 빠지면 해석이 바로 달라짐.

- Pro는 일반 채팅용
- Claude Code는 Max 이상용
- 개발자는 더 비싼 플랜으로 올려야 함

문제는 여기서 끝이 아니었음.
공식 도움말은 계속 **Pro 또는 Max**라고 적고 있었음.

그러니까 사용자는 당연히 헷갈릴 수밖에 없음.

- 가격표는 빼는 것처럼 보임
- 도움말은 여전히 된다고 함
- 몇 시간 뒤엔 다시 체크가 돌아옴

이건 그냥 디자인 실수가 아니라, **상품 메시지가 흔들린 사건**이었음.

## 2. 근데 이번 일은 배경까지 같이 봐야 함

여기서 중요한 게 하나 더 있음.
이번 혼선은 단순 오표기일 수도 있음.
근데 Anthropic이 최근 직접 밝힌 내용들을 보면, 왜 이런 민감한 흔들림이 나왔는지 배경이 보임.

Anthropic은 공식 글에서 이렇게 말했음.

- 2026년에 Claude 수요가 급증했음
- free, Pro, Max, Team 전반에서 소비자 사용이 크게 늘었음
- 이 성장 속도가 인프라에 **inevitable strain**, 즉 피할 수 없는 부담을 줬음
- 특히 피크 시간대에는 reliability와 performance에도 영향이 갔다고 설명했음

이건 꽤 중요함.

즉 지금 Anthropic은 그냥 마케팅 문구를 다듬는 단계가 아니라,
**실제로 수요가 너무 빨리 늘어서 계산 자원과 서비스 안정성을 같이 맞춰야 하는 국면**에 들어가 있다는 뜻임.

## 3. 정확히는 GPU 쇼티지라기보다, compute 쇼티지에 가까움

여기서 표현은 조금 정확하게 잡는 게 좋음.

사용자 입장에서는 보통 이걸 **GPU 쇼티지**라고 부름.
그 말이 완전히 틀린 건 아님.

근데 Anthropic 공식 문구 기준으로는 더 넓음.
이 회사는 지금 GPU 하나만 보는 게 아니라, **전체 compute capacity**를 문제로 보고 있음.

Anthropic은 공식적으로 이렇게 적었음.

- Google TPU를 최대 100만 개까지 확대하겠다고 했음
- AWS Trainium을 주요 훈련 인프라로 더 깊게 묶고 있음
- 자사 compute 전략을 **Google TPU + Amazon Trainium + NVIDIA GPU**의 다변화 구조라고 설명했음

이 말은 곧 이런 뜻임.

**“GPU가 부족해서 힘들다” 수준이 아니라, Claude를 계속 키우려면 칩, 클라우드, 전력, 데이터센터를 다 묶어서 더 크게 깔아야 하는 단계라는 것.**

## 4. AWS 확대는 그냥 제휴 뉴스가 아니었음

이 부분이 이번 글에서 제일 중요함.

Anthropic은 AWS 관련 공식 발표에서 두 가지를 분명히 말했음.

첫째,
AWS를 **primary cloud and training partner**로 두고 더 깊게 묶고 있음.

둘째,
Amazon과 새 계약을 맺고 **최대 5GW 규모의 compute capacity**를 확보하겠다고 했음.

여기서 숫자가 무거움.
Anthropic은 이 계약이:

- 앞으로 10년 동안 AWS 기술에 1,000억 달러 이상 커밋하는 구조이고
- 2026년 안에 의미 있는 신규 capacity가 빠르게 들어오며
- 올해 말까지 거의 1GW 규모가 순차적으로 붙는다고 설명했음

한마디로 이거임.

**Anthropic은 지금 Claude 수요를 감당하려고 AWS 쪽 인프라를 크게 늘리고 있음.**

그냥 “협력 강화” 수준이 아님.
**실사용 폭증을 버티기 위한 인프라 증설** 성격이 더 강함.

## 5. 그래서 Pro 가격표 흔들림이 더 의미심장해짐

이제 다시 가격표 얘기로 돌아오면 그림이 보임.

배경지식은 이거였음.

- Claude 수요가 급증했음
- Anthropic은 공식적으로 인프라 부담을 인정했음
- AWS와 Google 양쪽으로 compute를 더 크게 당기고 있음
- 칩 전략도 TPU, Trainium, NVIDIA GPU로 분산 중임

근데 이런 상황이면 당연히 다음 고민이 생김.

**누구에게 어느 정도 용량을 열어줄 건가.**

특히 Claude Code는 일반 채팅보다 무거운 사용 패턴이 많음.

- 세션이 김
- 저장소를 통째로 넣음
- 반복 호출이 많음
- 에이전트성 작업이 많음
- 토큰 사용량이 큼

그러니까 Anthropic 입장에선 이걸 모든 Pro 사용자에게 지금처럼 유지할지,
아니면 Max 중심으로 재분류할지,
계속 내부적으로 고민할 가능성이 높음.

그래서 이번 가격표 흔들림은 더 묘함.

그냥 디자이너 실수일 수도 있음.
근데 **인프라 압박이 실제로 있는 회사에서, 하필 가장 민감한 기능 칸이 흔들렸다는 것** 자체가 의미가 있음.

## 6. 지금 가능한 해석은 세 개임

### 1) 진짜 단순 실수였음

이게 제일 무난함.
가격표 한 칸이 잘못 들어갔다가 다시 수정됐다는 해석임.

### 2) 내부 검토 흔적이 잠깐 노출됐음

이쪽도 충분히 가능함.
특히 compute 압박이 있는 상황이면,
Pro와 Max 사이의 경계를 다시 만지는 시도가 내부적으로 아예 없다고 보기 어려움.

### 3) 실험군, 캐시, 롤아웃 차이였음

이것도 SaaS에서는 흔함.
페이지 실험, 지역별 노출, 로그인 상태 차이, 캐시 반영 문제로 서로 다른 화면이 잠깐 섞일 수 있음.

## 7. 지금 제일 팩트에 가까운 문장

지금 이렇게 말하면 됨.

**Anthropic이 Claude Code를 Pro에서 완전히 뺐다고 확정하긴 이르다. 근데 가격표는 실제로 흔들렸고, 그 흔들림은 수요 폭증과 compute 압박 속에서 나온 장면이라 더 가볍게 보기 어렵다.**

핵심은 이거임.

- 처음엔 X였음
- 지금은 체크임
- 도움말은 여전히 Pro 지원임
- Anthropic은 동시에 인프라 부담과 capacity 확장을 공식적으로 말하고 있음

그러면 남는 질문은 결국 하나임.

**이건 단순 실수였나, 아니면 아직 발표 안 된 상품 조정의 그림자가 먼저 보인 건가.**

## 8. 당장 뭘 보면 되냐면

### 첫째, pricing 페이지가 다시 또 흔들리는지

이건 며칠 더 보면 됨.
한 번 흔들린 페이지는 다시 흔들릴 수도 있음.

### 둘째, 도움말 문구가 바뀌는지

정책이 진짜 바뀌면 결국 여기가 따라옴.

### 셋째, Claude Code 제한 체감이 달라지는지

이게 제일 현실적임.
사용자들이 실제로 Pro에서 더 빨리 막히는지, Max 쪽으로 더 강하게 유도되는지 보면 됨.

## 출처

- Anthropic, [Anthropic and Amazon expand collaboration for up to 5 gigawatts of new compute](https://www.anthropic.com/news/anthropic-amazon-compute)
- Anthropic, [Powering the next generation of AI development with AWS](https://www.anthropic.com/news/anthropic-amazon-trainium)
- Anthropic, [Expanding our use of Google Cloud TPUs and Services](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- Anthropic Help, [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- Claude Help, [Usage limit best practices](https://support.claude.com/en/articles/9797557-usage-limit-best-practices)
