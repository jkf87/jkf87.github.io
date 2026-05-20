---
title: 구글이 Vertex AI를 갈아엎음 — Gemini Enterprise Agent Platform이 진짜로 노린 것
date: 2026-04-26
tags:
  - AI
  - Google Cloud
  - Gemini
  - AI Agent
  - Vertex AI
  - AWS Bedrock
  - AgentCore
  - 에이전트
description: 구글의 Gemini Enterprise Agent Platform과 AWS의 Bedrock AgentCore를 나란히 놓고 비교. 모델 시대에서 에이전트 운영 시대로 넘어가는 두 가지 답안.
---

1\. 2026년 4월 23일, 구글 클라우드가 새 플랫폼을 냈음. 이름은 **Gemini Enterprise Agent Platform**임.

2\. 첫 인상은 단순 리브랜딩. 근데 그게 아니었음. 6년차 Vertex AI를 통째로 재편한 발표임.

3\. 이유는 단순함. 모델 자체로는 돈 벌기 어려워졌음. 진짜 돈 되는 곳은 에이전트 운영 인프라임.

4\. 배경지식부터 정리함. Vertex AI는 원래 모델 학습/배포 중심이었음. 모델 가져오고, 파인튜닝하고, 엔드포인트 띄우는 거.

5\. 근데 작년부터 분위기가 바뀌었음. 모델 자체는 이미 충분히 좋아짐. 진짜 어려운 건 그걸 24/7 안정적으로 돌리는 거임.

6\. 문제는 세 가지였음. 에이전트 ID가 없어서 누가 뭘 했는지 추적 불가. 메모리는 세션 단위라 며칠짜리 작업 못함. 보안은 모델/도구/사람 사이에서 누가 책임지는지 모름.

7\. 그래서 구글이 내놓은 답이 4영역 통합임. **Build / Scale / Govern / Optimize**.

8\. Build는 개발 진입장벽 낮추기. **Agent Studio**라는 노코드 툴이 있고, **ADK**로 풀코드 전환도 됨. 시각적으로 만들어보고, 그대로 그래프 기반 코드로 내보내는 흐름.

9\. 근데 Build만 잘된다고 끝이 아님. 실제 운영에서 가장 골치 아픈 건 Scale 쪽임.

10\. Scale의 핵심은 두 가지. **서브초 콜드 스타트**, 그리고 **며칠 단위 멀티데이 워크플로우**.

11\. 서브초 콜드 스타트는 사용자 입장에서 "에이전트가 어디 갔다가 늦게 깨는" 문제 해결.

12\. 멀티데이 워크플로우가 더 흥미로움. 며칠짜리 작업을 에이전트 혼자 끌고 가야 한다는 거임. 보고서 자동화, 장기 마케팅 캠페인 트래킹 같은 거.

13\. 그러려면 메모리가 필요함. 그래서 **Memory Bank**를 만든 거임. 대화 기반 장기 메모리 자동 생성, Memory Profiles로 저지연 컨텍스트 회수.

14\. 여기서 또 문제가 생김. 에이전트가 길어지고 똑똑해지면 보안이 더 위험해짐.

15\. Govern 영역이 들어오는 부분. 핵심은 세 개. **Agent Identity, Agent Registry, Agent Gateway**.

16\. Agent Identity는 모든 에이전트에 암호화 ID 부여. 작업 단위 감사 추적이 됨.

17\. Agent Registry는 사내 승인된 에이전트/도구만 라이브러리화. 어떤 부서 직원이 외부 에이전트를 함부로 갖다 붙이는 사고 방지.

18\. Agent Gateway는 트래픽 통제. **Model Armor**가 붙어있는데 프롬프트 인젝션, 데이터 유출 방어 담당.

19\. 근데 통제가 강해지면 운영자가 또 문제. 어디가 잘못 작동하는지 안 보임.

20\. 그래서 Optimize. **Agent Simulation, Evaluation, Observability, Optimizer** 네 가지.

21\. Simulation은 합성 사용자가 가짜로 에이전트랑 대화하면서 작업 성공률을 자동 채점.

22\. Evaluation은 실제 운영 트래픽 기반 채점. 멀티턴 자동 평가자가 단일 응답이 아니라 전체 대화 논리를 봄.

23\. Optimizer는 실패 케이스 자동 클러스터링 후 시스템 명령 최적화 제안. 사람이 일일이 디버깅 안 해도 됨.

24\. 이게 다 좋아 보이지만, 진짜 의미는 도입 사례에서 드러남.

25\. **Comcast**는 기존 스크립팅 자동화를 ADK 기반 다중 에이전트 아키텍처로 갈아엎음. 결과는 디지털 해결율 증가.

26\. **Payhawk**는 Memory Bank를 써서 사용자 습관을 자동 회수. 경비 제출 시간이 **50% 줄었음**.

27\. **L'Oréal**은 결정론적 워크플로우에서 자율 에이전트 오케스트레이션으로 전환. ADK + MCP로 자체 데이터 플랫폼 연결.

28\. **PayPal**은 더 흥미로움. **Agent Payment Protocol(AP2)** 을 깔아서 에이전트끼리 거래하는 기반을 만들고 있음.

29\. **Gurunavi**는 사용자 만족도 **30% 상승 예상**. Memory Bank 덕분에 수동 검색이 줄었음.

30\. **Color Health**는 유방암 선별 적격성 확인 → 임상의 연결 → 예약 자동화를 한 에이전트가 처리. 의료 영역까지 들어옴.

31\. 여기서 진짜 신호를 읽어야 함.

32\. 첫째, 구글은 자체 모델만 강요하지 않음. **200개 이상 모델 지원**, Claude Opus/Sonnet/Haiku도 들어감.

33\. 이유는 단순함. 모델 락인 게임에서 이미 진 거임. 그래서 "어떤 모델 쓰든 우리 운영 인프라 위에서 돌려라"로 전략 전환.

34\. 둘째, 공식 가격이 아직 없음. 종량제로 갈 가능성 큼. 모델 추론 + Agent Runtime + Memory Bank 별도 과금 구조 예상.

35\. 셋째, 한국 기업도 곧 이 흐름에 휩쓸림.

36\. 지금 한국에서 LLM 도입한 기업들 보면 대부분 RAG 챗봇 정도임. 근데 이게 다음 단계임. 멀티 에이전트, 며칠짜리 워크플로우, 거버넌스까지.

37\. 개인 입장에서도 같은 신호임. 더 이상 "모델 잘 다루는 사람"이 아니라 "에이전트 운영 잘 하는 사람"이 필요해짐.

38\. **ID, 메모리, 거버넌스, 평가**. 이 네 가지를 다룰 줄 모르면 결국 시연용 장난감만 만드는 거임.

39\. 근데 사실 **AWS는 이미 깃발 꽂은 상태**임. **Bedrock AgentCore**라는 답안이 먼저 나와있었음.

40\. AgentCore 구성을 보면 구글하고 거의 1:1 대응됨. **Runtime / Gateway / Identity / Memory / Tools / Observability / Evaluation / Policy**. 8개 프리미티브임.

41\. Google이 4영역(Build/Scale/Govern/Optimize)으로 묶어서 보여준 걸 AWS는 8개 독립 서비스로 쪼개놨음. 같은 문제, 다른 포장.

42\. 매핑하면 단순함. Runtime은 둘 다 동일. Memory도 동일. Gateway는 양쪽 다 API/Lambda를 MCP 도구로 바꿔주는 역할. Identity도 같은 그림.

43\. 근데 거버넌스에서 결이 다름. 구글은 **Model Armor**로 프롬프트 인젝션·데이터 유출을 LLM 런타임에서 막음. AWS는 **Cedar 정책**으로 IAM 스타일 세밀 권한 통제.

44\. 철학 차이임. 구글은 "AI가 이상한 짓 하기 전에 잡자". AWS는 "애초에 권한이 없으면 못 한다". 클라우드 출신 회사답게 AWS가 더 정적·선언적.

45\. 도구 전략도 다름. AWS는 **Code Interpreter, Browser Tool을 관리형 프리미티브**로 바로 줌. 구글은 ADK + MCP 위에서 직접 짜는 흐름. AWS가 "갖다 쓰면 됨" 쪽에 더 가까움.

46\. 프레임워크 호환성도 차이. Google은 자기네 ADK 중심에 외부 모델 200개 지원. AWS는 한 발 더 나가서 **Strands Agents, CrewAI, LangGraph** 등 어떤 프레임워크 코드든 수정 없이 올릴 수 있다고 광고함.

47\. 발표 순서도 보면 AWS가 먼저였음. AgentCore가 깔린 상태에서 구글이 통합 콘솔로 답한 격임.

48\. 패턴이 보임. AWS는 **레고 블록 전략**임. 프리미티브 8개 골라서 조립. 클라우드 엔지니어 친화.

49\. 구글은 **올인원 콘솔 전략**임. Build/Scale/Govern/Optimize 한 화면에서 다 보이게. 비개발자·PM도 끌어들이려는 의도.

50\. 그래서 누가 이기냐? 아직 모름. 근데 한국 기업 입장에서는 어느 쪽 택하든 똑같은 4가지를 운영해야 한다는 결론은 같음.

51\. **ID, 메모리, 거버넌스, 평가**. 이름만 다를 뿐 양쪽 다 이 네 개를 박아놨음. 못 다루면 결국 시연용 장난감만 만드는 거임.

52\. 모델 시대는 끝났음. 운영 시대로 넘어왔음.

---

**원문**: [Introducing Gemini Enterprise Agent Platform — Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/introducing-gemini-enterprise-agent-platform)
**비교 대상**: [Amazon Bedrock AgentCore Samples — GitHub](https://github.com/awslabs/agentcore-samples)
**소스**: [GeekNews 토픽](https://news.hada.io/topic?id=28882)
