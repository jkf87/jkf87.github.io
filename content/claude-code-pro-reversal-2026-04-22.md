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
description: "Claude 가격표에서 Pro의 Claude Code가 빠졌다가 다시 돌아온 것처럼 보였음. 단순 실수인지, 정책 흔들림인지, 그리고 그 뒤에 있는 Anthropic의 인프라 압박까지 같이 봐야 하는 이유를 정리함."
---

- **가격 페이지**: [claude.com/pricing](https://claude.com/pricing)
- **Anthropic 공식 1**: [Anthropic and Amazon expand collaboration for up to 5 gigawatts of new compute](https://www.anthropic.com/news/anthropic-amazon-compute)
- **Anthropic 공식 2**: [Powering the next generation of AI development with AWS](https://www.anthropic.com/news/anthropic-amazon-trainium)
- **Anthropic 공식 3**: [Expanding our use of Google Cloud TPUs and Services](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- **도움말**: [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- **직전 글**: [Claude Pro에서 Claude Code 빠지나, Anthropic 가격 페이지에 뜬 이상 신호](./claude-code-pro-pricing-confusion-2026-04-22)

Anthropic 가격표가 하루 동안 두 번 말을 바꾼 것처럼 보였음.
처음엔 Pro의 Claude Code가 빠진 것처럼 보였고, 몇 시간 뒤엔 다시 돌아와 있었음.
이거 하나로 끝나는 얘기가 아니었음.
이유는 단순함.
Claude Code는 지금 Anthropic 상품 구조에서 제일 민감한 칸 중 하나이기 때문임.

1. 처음 장면은 이거였음.

Pro 칸의 Claude Code가 X로 보였음.
그러니까 해석이 바로 이렇게 감.

- 이제 Pro에서는 Claude Code 못 씀
- Max로 올리라는 뜻임
- 개발자 요금제를 다시 짜는 중임

![Claude 가격 페이지에서 Pro 플랜의 Claude Code가 X로 보이는 화면](./images/claude-code-pro-reversal-2026-04-22/claude-pricing-pro-code-x.jpg)
*이전 캡처. Claude Code 행의 Pro 칸이 X로 표시되어 있었음.*

2. 근데 몇 시간 뒤엔 다시 체크가 돌아왔음.

그래서 질문도 바뀌었음.
이제는 “빼는 거냐”가 아니라 “왜 흔들렸냐”가 됐음.

- 단순 실수였나
- 테스트 화면이 잠깐 보인 건가
- 내부 검토 흔적이 먼저 튄 건가

![Claude 가격 페이지에서 Pro 플랜의 Claude Code가 다시 체크로 보이는 화면](./images/claude-code-pro-reversal-2026-04-22/claude-pricing-pro-code-restored.jpg)
*현재 캡처. Claude Code 행의 Pro 칸이 다시 체크로 보임.*

3. 이걸 가볍게 보기 어려운 이유가 있음.

Claude Code는 부가 기능이 아님.
많은 사람한테는 Claude 유료 구독의 핵심임.

그래서 Pro에서 이게 빠지면 상품 구조가 바로 달라짐.

- Pro는 일반 채팅용으로 밀리고
- Claude Code는 Max 이상으로 올라가고
- 개발자는 체감상 입장권이 확 비싸짐

문제는 도움말 문서가 계속 **Pro 또는 Max**라고 적고 있었다는 점임.
그러니까 화면은 흔들렸는데, 공식 설명은 그대로였음.
이게 그냥 아이콘 실수처럼 안 보이는 이유임.

4. 여기서 배경지식이 하나 더 붙음.

Anthropic은 최근 공식 글에서 수요가 너무 빨리 늘었다고 직접 말했음.

- 2026년에 enterprise와 developer 수요가 빨라졌음
- free, Pro, Max, Team 전반에서 consumer usage도 급증했음
- 그 결과 인프라에 **inevitable strain**이 생겼다고 했음
- peak hour에는 reliability와 performance에도 영향이 갔다고 적었음

이건 꽤 중요함.
지금 Anthropic은 문구만 만지는 회사가 아니라, 실제로 용량이 빡빡해진 회사라는 뜻이기 때문임.

5. 그래서 AWS 얘기가 그냥 제휴 뉴스가 아니게 됨.

Anthropic은 AWS를 더 깊게 묶고 있음.
공식 표현도 셈.
**primary cloud and training partner**라고 했음.

거기서 끝도 아님.
Amazon과 새 계약을 맺고 **최대 5GW 규모의 compute capacity**를 확보하겠다고 했음.
또 10년 동안 AWS 기술에 1,000억 달러 이상 커밋하는 구조라고 설명했음.

이건 예쁜 파트너십 발표문이 아님.
Claude 수요를 버티기 위해 인프라를 더 크게 까는 얘기임.

6. 근데 이것도 AWS 하나로 끝나는 그림이 아님.

Anthropic은 Google Cloud 쪽으로도 up to 1 million TPUs 확대 계획을 밝혔음.
그리고 자사 compute 전략을 아예 이렇게 설명했음.

- Google TPU
- Amazon Trainium
- NVIDIA GPU

즉 지금 상황은 GPU 몇 장 부족하네 수준이 아님.
**compute 전체를 더 크게 당겨야 하는 국면**임.
그래서 사용자들이 말하는 GPU 쇼티지도 완전히 틀린 말은 아닌데, 공식 문구 기준으로는 compute shortage 쪽이 더 정확함.

7. 이제 다시 가격표로 돌아오면 그림이 이어짐.

배경은 이거였음.

- Claude 수요가 급증했음
- 인프라 strain을 Anthropic이 직접 인정했음
- AWS와 Google 양쪽으로 capacity를 크게 늘리고 있음
- Claude Code는 일반 채팅보다 훨씬 무거운 사용 패턴이 많음

그러면 당연히 회사 입장에서는 이런 고민을 하게 됨.

- 누구에게 어느 정도 용량을 열어둘 건가
- Pro와 Max 경계를 어디에 둘 건가
- 코딩 유저를 어느 플랜으로 묶을 건가

그래서 이번 흔들림은 더 묘함.
진짜 단순 실수일 수도 있음.
근데 **인프라 압박이 실제로 있는 회사에서, 하필 가장 민감한 기능 칸이 흔들렸다는 것** 자체가 의미가 있음.

8. 지금 제일 무난한 결론은 이거임.

Anthropic이 Claude Code를 Pro에서 완전히 뺐다고 확정하긴 이르다.
근데 가격표는 실제로 흔들렸음.
그리고 그 흔들림은 그냥 해프닝으로 넘기기엔 배경이 너무 무거움.

- 화면은 X였다가 체크로 바뀌었음
- 도움말은 여전히 Pro 지원이라고 적고 있음
- Anthropic은 동시에 인프라 압박과 capacity 확장을 공식적으로 말하고 있음

그러니까 남는 질문은 결국 하나임.
**이건 단순 실수였나, 아니면 아직 발표 안 된 상품 조정의 그림자가 먼저 보인 건가.**

9. 지금 봐야 하는 것도 명확함.

- pricing 페이지가 다시 흔들리는지
- 도움말 문구가 바뀌는지
- Pro에서 Claude Code 제한 체감이 달라지는지

결국 답은 여기서 나옴.
화면 한 장보다, 실제 제한과 공식 문서가 어디로 붙는지가 더 중요함.

## 출처

- Anthropic, [Anthropic and Amazon expand collaboration for up to 5 gigawatts of new compute](https://www.anthropic.com/news/anthropic-amazon-compute)
- Anthropic, [Powering the next generation of AI development with AWS](https://www.anthropic.com/news/anthropic-amazon-trainium)
- Anthropic, [Expanding our use of Google Cloud TPUs and Services](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- Anthropic Help, [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- Claude Help, [Usage limit best practices](https://support.claude.com/en/articles/9797557-usage-limit-best-practices)
