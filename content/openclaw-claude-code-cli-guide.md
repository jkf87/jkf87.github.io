---
title: Claude Code CLI로 OpenClaw 연결하기, 근데 어디까지 안전한가
date: 2026-04-20
tags:
  - claude-code
  - openclaw
  - anthropic
  - tos
description: Claude Code CLI 로그인 정보를 OpenClaw에서 재사용하는 방법, 그리고 공식 CLI는 안전하지만 제3자 위임은 왜 회색 지대인지 정리했습니다.
---

Claude Code CLI로 OpenClaw 연결은 됨.
실제로 붙음.
설정도 어렵지 않음.

근데 여기서 많이 헷갈림.
**된다**와 **안전하다**는 같은 말이 아님.
이건 나눠서 봐야 함.

## 1. 결론부터 말하면 이렇다

1. 공식 Claude Code CLI 단독 사용은 안전한 쪽이었음.
2. OpenClaw가 Claude CLI를 호출하는 `--method cli` 위임 방식은 지금은 됨.
3. 근데 2번은 회색 지대였음.
4. 직접 OAuth 토큰 삽입, 구독 우회 프록시는 피하는 게 맞음.

이유는 단순함.
Anthropic이 허용한 건 **공식 Claude Code CLI 자체**였음.
근데 제3자 도구가 그 CLI를 대신 호출해서 구독 인증을 재사용하는 건 다른 얘기였음.

## 2. 연결 방법은 단순함

### 1) Claude Code CLI에 먼저 로그인하면 됨

```bash
claude auth login
```

여기까지는 공식 경로였음.
Anthropic이 제공한 공식 CLI를 본인 PC에서 직접 쓰는 흐름이었음.

### 2) 그 다음 OpenClaw에서 CLI 위임을 잡으면 됨

```bash
openclaw models auth login --provider anthropic --method cli --set-default
```

이 명령은 OpenClaw가 로컬 `claude` 바이너리를 호출해서 로그인 상태를 재사용하는 방식임.
즉 OpenClaw가 OAuth 토큰 문자열을 직접 들고 가는 구조는 아님.
공식 Claude CLI가 세션을 관리하는 쪽이었음.

### 3) 온보딩 화면에서는 이렇게 고르면 됨

![OpenClaw 온보딩에서 Anthropic Claude CLI 인증 방식을 선택하는 화면](./images/openclaw-claude-code-cli-guide/openclaw-claude-cli-guide.jpg)
*OpenClaw 온보딩 화면에서 `Anthropic Claude CLI`를 고르면, 이 호스트의 로컬 Claude CLI 로그인 정보를 재사용하는 방식으로 연결됨.*

스크린샷 기준으로 보면 선택지는 명확했음.

1. Model/auth provider는 `Anthropic`이었음.
2. Anthropic auth method는 `Anthropic Claude CLI`였음.
3. 이걸 고르면 로컬 로그인 세션 재사용으로 붙는 구조였음.

여기까지 보면 꽤 좋아 보임.
편함.
바로 됨.

## 3. 왜 사람들이 이 방식에 관심을 가졌나

1. API Key를 새로 발급하지 않아도 됐음.
2. 이미 Claude Code CLI 구독을 쓰고 있으면 바로 붙여볼 수 있었음.
3. OpenClaw가 OAuth 토큰을 직접 보관하지 않았음.
4. 개인 실험이나 로컬 테스트에선 확실히 편한 길이었음.

즉 **편한 길**이었음.
이건 맞음.

## 4. 근데 왜 회색 지대였나

이유는 단순함.
Anthropic 공식 Claude Code CLI를 **직접** 쓰는 건 허용된 경로였음.
스크립트, 자동화 용도로 설계된 공식 제품이었고, 2026-02-20 Consumer ToS 업데이트에서도 자동화 접근 금지 조항의 예외로 취급됐음.

문제는 그 다음이었음.
OpenClaw 같은 제3자 도구가 그 CLI를 subprocess로 호출해서 구독 인증을 재사용하는 순간, 해석이 달라졌음.
지금은 됐음.
문서도 현재는 안정 경로로 안내했음.
근데 앞으로도 계속 열린다고 장담하긴 어려웠음.

![회색 지대를 말하는 장면의 GIF](./images/openclaw-claude-code-cli-guide/gray-area.gif)
*지금 되는 것과 앞으로도 안전한 것은 다른 얘기였음. `--method cli`가 회색 지대로 보이는 이유가 여기 있었음.*

실제로 2026-04-04 이후 Anthropic은 **제3자 도구에서 Pro/Max OAuth 사용 금지**를 더 강하게 적용하는 쪽으로 움직였음.
이슈 #63316에서도 CLI 위임 방식이 나중에 추가 차단될 수 있다고 적어둔 상태였음.

즉 이건 이렇게 봐야 했음.

1. 지금은 작동함.
2. 문서도 당장은 안정 경로로 안내함.
3. 근데 공급자 정책이 바뀌면 가장 먼저 흔들릴 수 있음.

## 5. 공식 CLI 단독 사용은 왜 안전하다고 봤나

이건 간단했음.
공식 제품이었기 때문임.
Anthropic이 제공한 공식 CLI를 본인 환경에서 직접 실행하는 건 제품이 의도한 사용 방식이었음.

중요한 건 여기였음.

1. **Claude Code CLI 자체 사용**
2. **제3자 도구가 Claude Code CLI를 대신 호출하는 사용**

겉으로는 비슷해 보여도 정책상 같은 영역이 아닐 수 있었음.
여길 섞으면 설명이 바로 꼬였음.

## 6. 금지된 경로는 더 선명했음

### 1) 직접 OAuth 토큰 삽입

Pro/Max OAuth 토큰을 직접 제3자 도구에 넣는 방식이었음.
이건 4월 4일 이후 서버 차단 대상이었음.

### 2) 구독 우회 프록시

`claude-max-api-proxy` 같은 커뮤니티 프록시가 여기에 들어갔음.
기술적으로 될 수는 있었음.
근데 Anthropic은 이런 흐름에 대해 사실상 경고를 유지했음.

![차단된 상황을 보여주는 GIF](./images/openclaw-claude-code-cli-guide/blocked.gif)
*편한 우회로처럼 보여도 오래 못 가는 쪽이었음. 특히 토큰 직접 삽입이나 프록시는 여기로 흘렀음.*

짧게는 편해 보였음.
근데 길게 보면 가장 위험했음.

## 7. 권장은 이렇게 정리하면 됨

### 1) 정책적으로 100% 안전한 길

**API Key 인증**이었음.
Anthropic Console에서 키를 발급받아 연결하는 방식이었음.
이 경로가 가장 깔끔했음.
모든 제3자 도구에서 설명이 쉬웠고, 정책 리스크도 가장 낮았음.

### 2) 현재 OpenClaw에서 구독을 활용하는 길

**`--method cli` 위임 방식**이었음.
당분간은 작동했음.
근데 언제든 차단 가능성은 모니터링해야 했음.
편한 길이지, 완전히 안전한 길은 아니었음.

### 3) 피해야 할 것

1. 직접 OAuth 토큰 삽입
2. 구독 우회 프록시
3. 비공식 세션 재사용 해킹

짧게 편한데, 길게 보면 제일 비싼 선택이었음.

## 8. 그래서 누구는 뭘 쓰면 되나

### 개인 사용자라면

테스트나 학습 목적이면 `--method cli`로 빠르게 붙여볼 수 있었음.
근데 이 경로에 작업 전체를 잠그는 건 추천하기 어려웠음.
나중에 API Key로 옮길 계획까지 같이 잡는 편이 나았음.

### 팀이나 운영 환경이라면

처음부터 API Key가 맞았음.
정책 설명이 쉽고, 장애 원인도 단순하고, 유지보수도 편했음.

### 블로그나 강의에서 소개하는 사람이라면

문장을 이렇게 끊어야 했음.

1. 공식 Claude Code CLI 자체는 안전했음.
2. OpenClaw가 그 CLI를 호출해 재사용하는 위임 방식은 현재 작동하지만 회색 지대였음.
3. OAuth 직접 삽입이나 프록시는 피해야 했음.

이 선을 흐리면 독자가 잘못 받아들였음.

## 9. 마지막 정리

이건 두 문장으로 끝났음.

**Claude Code CLI를 직접 쓰는 건 안전한 쪽이었음.**
**OpenClaw가 그 CLI를 대신 호출하는 위임 방식은 현재 가능하지만 회색 지대였음.**

그래서 선택 기준도 단순했음.

1. 편하게 빨리 붙이고 싶으면 `--method cli`
2. 오래 안정적으로 쓰고 싶으면 API Key
3. 토큰 직접 삽입이나 프록시는 피하기

이 주제는 “된다”보다 “어디까지 안전한가”를 같이 적어야 했음.
그게 핵심이었음.
