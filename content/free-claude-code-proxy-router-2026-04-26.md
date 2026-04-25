---
title: "Claude Code를 무료로 굴리는 프록시가 GitHub 트렌딩 1위 찍음 — free-claude-code"
date: 2026-04-26
tags:
  - ClaudeCode
  - LLM
  - 프록시
  - 오픈소스
  - GitHub트렌딩
  - 로컬LLM
  - NVIDIA
description: localhost:8082 프록시로 Claude Code의 Anthropic API 호출을 가로채 NVIDIA NIM 무료 티어, OpenRouter, DeepSeek, LM Studio, llama.cpp로 우회시킴. 하루 +3,975 스타.
---

1. 어제부터 GitHub 트렌딩 1위로 free-claude-code가 올라옴. 누적 10,999스타. 하루에만 +3,975. 한국 시간 2026년 4월 26일 기준임.

2. 뭐 하는 레포냐. localhost:8082에 프록시 서버를 띄워놓고, Claude Code가 보내는 Anthropic API 요청을 가로챔. 그 요청을 다른 LLM 백엔드로 우회시킴. Claude Code 자체는 그대로 씀.

3. 사용법은 단순함. `ANTHROPIC_BASE_URL`을 `http://localhost:8082`로 바꾸기만 하면 됨. Claude Code가 보내는 요청이 전부 프록시 거쳐서 다른 모델로 흘러감.

4. 백엔드는 5종 지원함. NVIDIA NIM, OpenRouter, DeepSeek, LM Studio, llama.cpp. 이 중 NVIDIA NIM이 **무료 티어로 분당 40 요청까지** 됨. 이게 트렌딩 1위 만든 핵심 포인트임.

5. 근데 단순 프록시만 있는 게 아님. 쿼터 절약 최적화가 들어가 있음. quota probe, 타이틀 생성, 프리픽스 감지, 제안, 파일경로 추출 같은 자잘한 호출 5종은 로컬에서 즉시 처리해서 API 콜 자체를 안 쓰게 막아둠.

6. 그리고 또 하나. `<think>` 태그나 `reasoning_content`를 Claude의 native thinking 블록으로 자동 변환해줌. proactive throttling에 reactive backoff까지 들어가 있어서 rate limit 회피도 알아서 함.

7. Opus, Sonnet, Haiku 모델별로 다른 백엔드를 매핑할 수도 있음. 가벼운 작업은 무료 NIM으로, 복잡한 추론은 OpenRouter 유료 모델로 분배 가능함.

8. 부가 기능도 많음. Discord 봇은 트리 기반 스레딩, 세션 영속화, 음성 트랜스크립션, `/stop` `/clear` `/stats` 명령까지 지원. Telegram 봇도 환경변수 `MESSAGING_PLATFORM=telegram` + 봇 토큰만 넣으면 됨.

9. VSCode/IntelliJ 익스텐션 연동도 됨. `claude-pick`이라는 fzf 인터랙티브 모델 선택기까지 같이 들어 있음.

10. 설치는 짧음.

```bash
git clone https://github.com/Alishahryar1/free-claude-code
cp .env.example .env  # API 키 설정
uv run uvicorn server:app --host 0.0.0.0 --port 8082
ANTHROPIC_BASE_URL="http://localhost:8082" claude
```

11. 요구사항은 Python 3.14, uv, Claude Code CLI. 그리고 백엔드 API 키 1개 이상. 로컬 LLM 백엔드(LM Studio, llama.cpp) 쓰면 키도 필요 없음.

12. 짚어야 할 지점 세 개 있음. **첫째, Anthropic 약관상 회색지대임.** Claude Code는 Anthropic 모델 쓰라고 만든 도구인데 외부 LLM으로 우회시키는 거라 정책 리스크 있음.

13. **둘째, NVIDIA NIM 무료 40 req/min은 실사용 가능한 수준이긴 함.** 근데 프로젝트 규모 커지면 금방 한계 닥침. 무료 의도로 들어가도 결국 OpenRouter나 DeepSeek 같은 저가 유료로 넘어가게 되는 구조임.

14. **셋째가 중요함.** LM Studio나 llama.cpp 같은 로컬 백엔드로 쓰면 회색지대 자체를 피할 수 있음. API 키도 필요 없고, 오프라인에서도 굴러감. 보안 민감한 환경에서 코딩 에이전트 굴릴 때 이 조합이 합법적이고 안전함.

15. Discord 봇 쓸 거면 채널 ID 화이트리스트 필수임. 안 그러면 누가 와서 쿼터 다 태울 수 있음. 이건 실수하기 쉬운 지점.

16. 결국 이 레포가 트렌딩 1위 찍은 이유는 단순함. **"무료" + "Claude Code"** 키워드 조합이 폭발력 있음. Claude Code 비용 부담 느끼는 개발자가 많고, 로컬 LLM 폴백 옵션이 진입장벽을 낮춰줌.

17. 활용 결정은 각자 알아서 해야 함. 회사 코드에 쓰면 약관 리스크. 개인 프로젝트에 LM Studio 백엔드로 쓰면 합법. 그 사이 어디에 자기 라인을 그을지가 포인트임.

18. 한국 개발자 입장에서 가장 깔끔한 그림은 **로컬 LLM + 오픈소스 모델 조합**. Qwen2.5-Coder나 DeepSeek-Coder를 LM Studio에 올려놓고, Claude Code 인터페이스로 굴리면 됨. 약관 깔끔, 비용 0원, 오프라인 가능.

19. NVIDIA NIM 무료 티어를 잠깐 찍먹할 거면 회사 비밀 코드 말고 개인 사이드 프로젝트로만 굴리는 게 안전함. 트래픽 패턴이 외부 서버에 남는 점 잊지 말 것.

20. 트렌딩 1위 레포 하나가 던지는 메시지는 분명함. **"Claude Code 인터페이스는 좋은데 비용·정책 부담은 부담"**이라는 시장 신호임. 이 신호를 Anthropic이 어떻게 받을지가 다음 포인트.

---

**출처**

- [Alishahryar1/free-claude-code — GitHub](https://github.com/Alishahryar1/free-claude-code)
- [GitHub Trending — 2026-04-26](https://github.com/trending)
- [NVIDIA NIM 무료 티어 안내](https://build.nvidia.com)
