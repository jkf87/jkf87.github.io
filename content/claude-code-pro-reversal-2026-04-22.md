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
description: "Claude 가격표에서 Pro의 Claude Code가 빠졌다가 다시 돌아온 것처럼 보였음. 단순 실수인지, 정책 조정 신호인지, 그리고 그 뒤에 있는 Anthropic의 인프라 압박까지 같이 정리함."
---

- **가격 페이지**: [claude.com/pricing](https://claude.com/pricing)
- **Anthropic 공식 1**: [Anthropic and Amazon expand collaboration for up to 5 gigawatts of new compute](https://www.anthropic.com/news/anthropic-amazon-compute)
- **Anthropic 공식 2**: [Powering the next generation of AI development with AWS](https://www.anthropic.com/news/anthropic-amazon-trainium)
- **Anthropic 공식 3**: [Expanding our use of Google Cloud TPUs and Services](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- **도움말**: [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- **직전 글**: [Claude Pro에서 Claude Code 빠지나, Anthropic 가격 페이지에 뜬 이상 신호](./claude-code-pro-pricing-confusion-2026-04-22)

Anthropic 가격표를 보면 하루 안에 화면이 두 번 다르게 보였음. 처음엔 Pro의 Claude Code가 빠진 것처럼 보였고, 몇 시간 뒤엔 다시 체크가 붙어 있었음. 이건 그냥 캡처 하나로 끝나는 얘기가 아니었음. 이유는 단순함. Claude Code는 지금 Anthropic 상품 구조에서 제일 민감한 기능 중 하나이기 때문임.

1. 처음 보인 장면은 Pro의 Claude Code가 X로 표시된 화면이었음. 그래서 해석도 바로 그쪽으로 갔음. 이제 Pro에서는 Claude Code를 못 쓰는 거냐, Max로 올리라는 뜻이냐, 개발자 요금제를 다시 짜는 중이냐 같은 얘기가 바로 붙었음.

![Claude 가격 페이지에서 Pro 플랜의 Claude Code가 X로 보이는 화면](./images/claude-code-pro-reversal-2026-04-22/claude-pricing-pro-code-x.jpg)
*이전 캡처. Claude Code 행의 Pro 칸이 X로 표시되어 있었음.*

2. 근데 몇 시간 뒤엔 같은 자리에서 다시 체크가 보였음. 그러면 질문도 자연히 바뀜. 진짜로 뺀 게 아니라면 왜 잠깐 X가 보였는지, 실수였는지, 테스트 화면이었는지, 아니면 내부 검토 흔적이 먼저 나온 건지가 더 중요해짐.

![Claude 가격 페이지에서 Pro 플랜의 Claude Code가 다시 체크로 보이는 화면](./images/claude-code-pro-reversal-2026-04-22/claude-pricing-pro-code-restored.jpg)
*현재 캡처. Claude Code 행의 Pro 칸이 다시 체크로 보임.*

3. 이걸 가볍게 보기 어려운 이유가 있음. Claude Code는 부가 기능이 아님. 많은 사람한테는 Claude 유료 구독의 핵심임. 그래서 Pro에서 이게 빠지면 상품 구조가 바로 달라짐. Pro는 일반 채팅용으로 밀리고, Claude Code는 Max 이상으로 올라가고, 개발자는 체감상 입장권이 확 비싸지게 됨.

4. 문제는 공식 도움말 문서가 계속 Pro 또는 Max라고 적고 있었다는 점임. 그러니까 가격표에선 빠진 것처럼 보였는데, 도움말은 여전히 된다고 적고 있었음. 이러면 사용자는 당연히 헷갈릴 수밖에 없음. 그래서 이번 일은 아이콘 하나 잘못 들어간 해프닝으로만 보기 어려워짐.

5. 여기서 배경지식이 하나 더 붙음. Anthropic은 최근 공식 글에서 2026년 들어 enterprise와 developer 수요가 빨라졌고, free, Pro, Max, Team 전반에서 consumer usage도 급증했다고 직접 말했음. 그리고 그 결과 인프라에 inevitable strain이 생겼고, peak hour에는 reliability와 performance에도 영향이 있었다고 설명했음. 이건 꽤 무거운 문장임. 지금 Anthropic은 문구만 만지는 회사가 아니라, 실제로 용량이 빡빡해진 회사라는 뜻이기 때문임.

6. 그래서 AWS 얘기가 그냥 제휴 뉴스가 아니게 됨. Anthropic은 AWS를 primary cloud and training partner라고 부르고 있음. 거기서 끝도 아님. Amazon과 새 계약을 맺고 최대 5GW 규모의 compute capacity를 확보하겠다고 했고, 앞으로 10년 동안 AWS 기술에 1,000억 달러 이상 커밋하는 구조라고도 설명했음. 이건 예쁜 파트너십 발표문이 아니라, Claude 수요를 버티기 위한 인프라 증설 얘기에 더 가까움.

7. 근데 이것도 AWS 하나로 끝나는 그림이 아님. Anthropic은 Google Cloud 쪽으로도 최대 100만 TPUs 확대 계획을 밝혔음. 그리고 자기들 compute 전략을 Google TPU, Amazon Trainium, NVIDIA GPU를 함께 쓰는 구조라고 설명했음. 그래서 시장에서 흔히 말하는 GPU 쇼티지라는 표현이 완전히 틀린 건 아닌데, 공식 문구 기준으로는 compute capacity 부족 쪽이 더 정확함.

8. 이제 다시 가격표 얘기로 돌아오면 그림이 이어짐. Claude 수요는 급증했고, 인프라 부담은 커졌고, AWS와 Google 양쪽으로 capacity를 크게 늘리는 중이고, Claude Code는 일반 채팅보다 훨씬 무거운 사용 패턴을 많이 만들고 있음. 그러면 회사 입장에선 결국 이런 고민을 하게 됨. 누구에게 어느 정도 용량을 열어둘 건가, Pro와 Max 경계를 어디에 둘 건가, 코딩 유저를 어느 플랜으로 묶을 건가 하는 문제임.

9. 그래서 이번 장면은 더 묘함. 진짜 단순 실수일 수도 있음. 근데 인프라 압박이 실제로 있는 회사에서, 하필 가장 민감한 기능 칸이 X였다가 체크로 다시 보였다는 점 자체가 의미가 있음. 적어도 지금 시점에서 제일 무난한 결론은 이거임. Anthropic이 Claude Code를 Pro에서 완전히 뺐다고 확정하긴 이르다. 근데 가격표에선 분명 다른 표시가 나타났고, 그 배경엔 실제 수요 폭증과 compute 압박이 있음. 그래서 남는 질문도 자연히 하나로 좁혀짐. 이건 단순 실수였나, 아니면 아직 발표 안 된 상품 조정의 그림자가 먼저 보인 건가.

## 출처

- Anthropic, [Anthropic and Amazon expand collaboration for up to 5 gigawatts of new compute](https://www.anthropic.com/news/anthropic-amazon-compute)
- Anthropic, [Powering the next generation of AI development with AWS](https://www.anthropic.com/news/anthropic-amazon-trainium)
- Anthropic, [Expanding our use of Google Cloud TPUs and Services](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- Anthropic Help, [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- Claude Help, [Usage limit best practices](https://support.claude.com/en/articles/9797557-usage-limit-best-practices)
