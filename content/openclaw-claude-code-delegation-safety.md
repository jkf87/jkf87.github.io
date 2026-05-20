---
title: OpenClaw에서 Claude Code CLI 위임 방식 — 안전한가?
date: 2026-04-20
tags: [claude-code, openclaw, anthropic, tos]
---

공식 Claude Code CLI 단독 사용은 안전합니다.  
Anthropic 문서에서 스크립트·자동화 용도로 명시 허용합니다.  
2026-02-20 Consumer ToS 업데이트에서도 자동화 접근 금지 조항에서 면제됩니다.  

OpenClaw가 설치된 claude 바이너리를 subprocess로 호출하는 `--method cli` 방식은 현재 작동합니다.  
Anthropic이 OAuth 토큰을 직접 다루지 않고 공식 바이너리가 세션을 관리하기 때문입니다.  
OpenClaw 공식 문서도 이를 "Officially sanctioned / Stable"로 분류합니다.  

하지만 Anthropic은 2026-04-04 이후 제3자 도구에서 Pro/Max OAuth 사용 금지를 강화 중입니다.  
이슈 #63316 본문에서는 CLI 위임도 추가 차단될 수 있다고 명시합니다.  

![회색 지대](./images/openclaw-claude-code-delegation-safety/gray-area.gif)  
![차단](./images/openclaw-claude-code-delegation-safety/blocked.gif)  

정책적으로 100% 안전한 길은 API Key 인증입니다.  
Console에서 발급받은 API Key를 모든 제3자 도구에서 사용하면 문제 없습니다.  

현재 OpenClaw에서 구독 활용 시 `--method cli` 위임을 사용할 수 있습니다.  
당분간 작동하지만 언제든 차단 가능성을 모니터링해야 합니다.  

직접 OAuth 토큰을 제3자 도구에 넣는 방식은 4월 4일부터 서버 차단 대상입니다.  
claude-max-api-proxy 같은 커뮤니티 프록시는 기술적으로 작동하지만  
Anthropic이 "technical compatibility only" 경고를 유지합니다.  

따라서 피해야 할 것은 직접 OAuth 토큰 삽입과 구독 우회 프록시입니다.  
출처: Legal and compliance - Claude Code Docs, The Register 기사들, GitHub Issue #63316.  

결론은 단순합니다.  
공식 CLI 단독 사용은 안전합니다.  
제3자 도구에서 CLI를 호출하는 위임 방식은 회색 지대입니다.  
그래서 나는 뭐 해야 되나?  
가능하다면 API Key 인증을 쓰고,  
현재 구독이라면 `--method cli` 사용을 잠시 허용하되 차단 가능성을 주시하라.  
직접 토큰 삽입이나 프록시는 피하라.  