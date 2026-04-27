---
title: "TradingAgents 사용법 — LLM 9명이 주식 분석·매매 결정하는 멀티에이전트 오픈소스"
date: 2026-04-28
slug: tradingagents-multi-agent-trading-llm-2026-04-28
tags:
  - TradingAgents
  - 멀티에이전트
  - LLM
  - 주식
  - 투자
  - LangGraph
  - 백테스트
  - 재테크
  - 깃허브트렌딩
description: "TradingAgents는 LLM 9명이 주식을 토론해 매수·매도를 결정하는 멀티에이전트 오픈소스. GitHub 별 53k, LangGraph 기반. 펀더멘털·뉴스·심리·기술 분석부터 리스크 검토까지, 설치법·구조·한계 한국어 정리."
aliases:
  - tradingagents-multi-agent-trading-llm-2026-04-28/index
---

요즘 LLM에 종목 물어보면 답이 너무 매끈해서 오히려 못 믿게 됨. 모르는 게 없다는 듯 말하는데 막상 따라가 보면 단편적임. 근데 이런 LLM 한 명이 아니라 9명한테 역할 분담해서 토론까지 시키면 어떻게 될까. 이걸 그대로 만든 오픈소스가 있음.

![TradingAgents 전체 구조도 - 분석가 4명, 연구원 2명, 트레이더, 리스크팀, 포트폴리오 매니저로 이어지는 의사결정 플로우](./images/tradingagents-multi-agent-trading-llm-2026-04-28/schema.png)

1. 이름은 TradingAgents임. TauricResearch 팀이 만든 멀티에이전트 LLM 금융 트레이딩 프레임워크임. 깃허브 별이 5만 3천을 넘고, arXiv 논문도 같이 공개돼 있음(2412.20138). 자기 네이밍을 "research framework"로 못 박아서 "투자 자문 아니다"는 점은 README 첫 페이지부터 강조함.

2. 핵심 아이디어는 단순함. 진짜 트레이딩 회사처럼 역할을 쪼개서 LLM 에이전트한테 따로 시키는 거임. 회사에 분석가 따로, 트레이더 따로, 리스크 매니저 따로 있는 것처럼.

3. 1단계 분석가 팀이 4명임. 펀더멘털 분석가는 재무제표를 보고 본질가치를 따짐. 심리 분석가는 SNS와 여론을 점수화함. 뉴스 분석가는 글로벌 뉴스와 매크로 지표를 해석함. 기술 분석가는 MACD나 RSI 같은 차트 지표를 봄. 사람 한 명이 다 보던 걸 4명한테 나눠 줌.

![분석가 4명 역할 분담 - 펀더멘털·심리·뉴스·기술 분석가가 각자 데이터 소스로 종목을 평가](./images/tradingagents-multi-agent-trading-llm-2026-04-28/analyst.png)

4. 2단계는 연구원 팀임. 두 명임. 강세파(Bullish) 연구원과 약세파(Bearish) 연구원. 분석가 4명의 결과를 받아서 서로 정해진 라운드 수만큼 토론함. 한쪽은 살 이유, 다른 쪽은 팔 이유를 만들어내며 충돌시킴. 사람이 자기 포지션과 다른 의견 일부러 안 듣는 편향을 구조로 막아둔 거임.

5. 3단계 트레이더가 토론 결과를 정리해서 매수·매도와 사이즈를 결정함. 4단계는 리스크 매니지먼트 팀이 변동성·유동성 등 리스크를 보고 전략을 조정함. 마지막에 포트폴리오 매니저가 거래를 승인하거나 거절함. 통과되면 시뮬레이션 거래소로 주문이 나감.

6. 흥미로운 건 같은 종목을 다시 돌릴 때임. v0.2.4부터 결정 로그가 기본 켜져 있음. 매번 매수·매도 결정이 `~/.tradingagents/memory/trading_memory.md`에 기록됨. 다음에 같은 종목을 분석할 때 그 결정의 실제 수익률(SPY 대비 알파 포함)과 한 문단짜리 회고가 포트폴리오 매니저 프롬프트에 다시 들어감. "이 종목은 지난번 우리가 어떻게 봤고 결과가 어땠는지"를 매번 학습 자료로 활용하는 구조임.

7. 코드 입장에선 단순함. LangGraph로 만들어졌고 한 줄로 돌림.
   ```python
   from tradingagents.graph.trading_graph import TradingAgentsGraph
   from tradingagents.default_config import DEFAULT_CONFIG

   ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
   _, decision = ta.propagate("NVDA", "2026-01-15")
   print(decision)
   ```
   propagate에 종목 티커와 날짜 넣으면 위 9명이 차례로 굴러서 의사결정이 나옴. CLI도 있어서 `tradingagents` 한 줄로 인터랙티브하게 돌릴 수 있음.

![TradingAgents CLI 화면 - 뉴스 분석 결과가 실시간으로 출력되는 모습](./images/tradingagents-multi-agent-trading-llm-2026-04-28/cli-news.png)

8. 모델 선택이 넓음. OpenAI(GPT 시리즈), Google(Gemini), Anthropic(Claude), xAI(Grok), DeepSeek, Qwen, GLM, OpenRouter, 그리고 Ollama로 로컬 모델까지 다 받음. v0.2.4부터는 깊은 사고용 모델과 빠른 작업용 모델을 다르게 지정 가능함(`deep_think_llm`, `quick_think_llm`). GPT-5.4로 깊게 보고 5.4-mini로 빠르게 처리하는 식.

9. 체크포인트 기능도 있음. `--checkpoint` 옵션 켜면 LangGraph가 노드마다 상태를 저장해서, 도중에 끊겨도 마지막 성공 지점부터 재개됨. API 호출 비용이 한 번 돌리는 데 적지 않으니까(에이전트 9명이 길게 토론하면 토큰이 많이 나감) 이런 기능이 있는 게 차이를 만듦.

10. 결과 품질에 대해 말하자면 한계도 분명함. 같은 종목·같은 날짜라도 모델·온도·데이터 출처에 따라 답이 달라짐. README도 "performance varies based on many factors"라고 정확하게 명시함. 즉 이 도구가 "맞춰주는 무기"가 아니라 "여러 시나리오를 빠르게 시뮬레이션해보는 사고 보조 도구"임을 인정하는 거임.

11. 한국 투자자 입장에서 인사이트는 두 가지임. 첫째, 종목 하나 결정에 LLM 한 명한테 의지하는 건 위험함. 같은 LLM이라도 역할을 나누면 답의 폭이 넓어짐. 둘째, 진짜 자산 운용사가 어떤 절차로 의사결정하는지를 코드로 들여다볼 수 있음. 펀더멘털·심리·뉴스·기술이라는 네 축, 강세·약세 토론, 리스크 검토, 포트폴리오 매니저 결재. 이 흐름 자체가 공부 자료가 됨.

12. 한 가지 강조할 부분은 백테스트 한계임. 멀티에이전트 시스템은 본질적으로 결정 과정에 LLM 추론이 끼어 있어서 같은 입력이어도 출력이 흔들림. 그래서 "백테스트 수익률 N%"식의 단정 결론을 이 도구로 만들기는 어려움. 대신 "왜 이런 의사결정이 나왔는지"의 추적은 매우 풍부함. 분석가 한 명 한 명의 리포트가 다 남기 때문임.

13. 더 큰 그림에서 보면, 한 명의 천재 LLM 모델보다 여러 LLM의 협업이 더 합리적인 답을 낼 수 있다는 가설을 금융이라는 어려운 도메인에서 실증해보는 시도임. 같은 팀이 후속작 Trading-R1 논문(arXiv: 2509.11420)도 따로 내고, 곧 별도 터미널 앱도 출시 예정이라고 함.

14. 정리하면, 종목 분석에 LLM을 진지하게 써보고 싶은 사람한테는 좋은 출발점임. 절대 매매 자문 도구로 쓰지 말고, "여러 시각의 분석 리포트를 짧은 시간에 받는 보고서 자동 생성기"로 쓰는 게 적절함. 깔아만 보고 NVDA나 AAPL 같은 친숙한 종목으로 한 번 돌려보면, LLM이 토론하면서 어떤 근거를 만드는지가 그대로 보여서 의외로 재밌음.

---

**참고 자료**

- GitHub: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) (★ 53,443)
- arXiv 원논문: [2412.20138](https://arxiv.org/abs/2412.20138)
- 후속작 Trading-R1: [arXiv 2509.11420](https://arxiv.org/abs/2509.11420)
- 데모 영상: [YouTube](https://www.youtube.com/watch?v=90gr5lwjIho)
- 디스코드 커뮤니티: [TradingResearch](https://discord.com/invite/hk9PGKShPK)

> 이 글은 정보 제공 목적이며, 매매 자문이 아님. 실제 투자 결정은 본인 책임임.

---

**같이 보면 좋은 글**
- [[mattpocock-skills-real-engineers-claude-2026-04-27|Claude Code Skills 22개 — mattpocock .claude 폴더 공개]]
- [[chatgpt-gpt5-5-40s-work-2026-04-24|ChatGPT GPT-5.5 — 40대 직장인이 당장 건질 게 뭔지 정리]]
- [[cmux-yc-s24-terminal-ai-agents-2026-04-26|cmux — AI 에이전트 100개 돌리는 터미널]]
