---
title: "UCP (Universal Commerce Protocol): AI 시대의 오픈 커머스 표준"
date: 2026-05-27
tags:
  - ucp
  - commerce
  - ai
  - agentic-commerce
  - google
  - shopify
  - open-source
description: "Google, Shopify, Etsy 등이 공동 개발한 UCP(Universal Commerce Protocol)는 AI 에이전트가 상품을 검색하고, 장바구니에 담고, 결제까지 완료하는 에이전트 커머스의 공통 언어입니다. 작동 원리, 핵심 개념, 생태계를 정리합니다."
image: images/ucp-universal-commerce-protocol/ucp-hero.png
---

## UCP가 뭔가요?

**Universal Commerce Protocol(UCP)**은 AI 에이전트·앱·비즈니스·결제사 사이에서 커머스 거래를 표준화하는 **오픈 프로토콜**입니다.

쉽게 말하면: 지금까지는 각 쇼핑몰마다 API를 따로 붙여야 했는데, UCP 하나만 연동하면 **어떤 쇼핑몰이든** AI가 상품을 찾고 바로 살 수 있게 만드는 공통 규격입니다.

Google이 Shopify, Etsy, Wayfair, Target, Walmart 등 20개 이상의 글로벌 파트너와 함께 개발했으며, 2026년 4월 공식 공개됐습니다.

> UCP = 커머스계의 **HTTP** 같은 존재

## 왜 필요한가?

기존 커머스 생태계의 문제:

- **N×N 복잡도**: AI 플랫폼 10개 × 쇼핑몰 1000개 = 10,000개 커스텀 연동
- **카트 포기율 증가**: AI에서 상품을 찾아도 결제까지 이어지지 않음
- **프래그먼테이션**: 각 플랫폼마다 다른 체크아웃 방식, 다른 결제 API

UCP는 이걸 **1:N** 구조로 단순화합니다.

## 어떻게 작동하나요?

UCP는 **프로필 기반 디스커버리** 모델을 사용합니다.

### 1단계: 프로필 발견

각 비즈니스는 `/.well-known/ucp` 경로에 자신의 기능과 결제 수단을 선언하는 프로필을 게시합니다.

```
POST /checkout-sessions HTTP/1.1
UCP-Agent: profile="https://example.com/.well-known/ucp"
```

### 2단계: 기능 교집합 (Capability Intersection)

플랫폼과 비즈니스가 서로의 프로필을 비교해서 **공통으로 지원하는 기능**만 활성화합니다. 양쪽 모두 동의한 기능만 사용되므로 사전 등록 없이도 안전하게 연동됩니다.

### 3단계: 거래 실행

합의된 기능으로 카탈로그 검색 → 장바구니 → 체크아웃 → 주문 관리까지 전체 커머스 라이프사이클을 처리합니다.

## 핵심 아키텍처

### 프로필 (Profile)

모든 참여자가 자신의 능력을 선언하는 명세서:
- 지원하는 서비스와 기능(catalog, cart, checkout, orders 등)
- 결제 수단 핸들러
- 서명 키 (보안 인증용)

### 기능 (Capabilities)

`dev.ucp.shopping.checkout`, `dev.ucp.shopping.catalog` 같은 **리버스 도메인 네이밍**으로 정의됩니다:

| 기능 | 설명 |
|------|------|
| Catalog Search | 상품 검색 및 조회 |
| Cart | 장바구니 구성 |
| Checkout | 결제 세션 관리 |
| Identity Linking | 계정 연동 (OAuth 2.0) |
| Order Management | 주문 조회 및 관리 |

### 결제 아키텍처

UCP의 결제는 3단계로 분리됩니다:

1. **Negotiation**: 비즈니스가 지원하는 결제 수단을 프로필에 선언
2. **Acquisition**: 플랫폼이 핸들러를 실행해 결제 수단(토큰) 획득
3. **Completion**: 비즈니스가 PSP를 통해 실제 결제 처리

소비자의 결제 수단과 결제 처리사가 분리되어 있어, **어떤 결제사든** 유연하게 연동 가능합니다.

### 전송 계층 (Transport)

UCP는 다중 전송 프로토콜을 지원합니다:

- **REST API** (핵심)
- **MCP (Model Context Protocol)** 바인딩
- **A2A (Agent-to-Agent)** 지원
- **AP2 (Agent Payments Protocol)** 호환

## 보안과 프라이버시

- **OAuth 2.0** 기반 계정 연동
- **AP2** 통한 안전한 에이전트 결제 (토큰화 + 검증 가능한 자격 증명)
- 비즈니스는 항상 **Merchant of Record** — 고객 관계와 데이터 소유권 유지
- `dev.ucp.` 네임스페이스는 UCP 기술 위원회 관할, 벤더는 자체 도메인에서 자유롭게 확장 가능

## 생태계

### 공동 개발사

| 카테고리 | 기업 |
|----------|------|
| **개발 주도** | Google, Shopify |
| **커머스** | Etsy, Wayfair, Target, Walmart, Best Buy, Macy's, The Home Depot |
| **결제** | Stripe, Adyen, Visa, Mastercard, American Express |
| **글로벌** | Flipkart, Zalando |

### 오픈소스 생태계

GitHub [universal-commerce-protocol/ucp](https://github.com/universal-commerce-protocol/ucp)에서 스펙과 문서가 공개되어 있고, 커뮤니티가 이미 활발하게 활동 중입니다:

- **UCP PHP Spec** — PHP용 스펙 생성기
- **UCP Go SDK** — Go 클라이언트 라이브러리
- **Omnix Gateway** — Magento, Shopware, Shopify 연동 게이트웨이
- **UCP Client** — TypeScript용 능력 인식 클라이언트
- **Magento 2 UCP Module** — Adobe Commerce용 구현체

## 누구를 위한 건가요?

### 개발자

- 오픈 표준 위에 커머스의 미래를 구축
- SDK와 레퍼런스 구현체로 빠른 통합
- GitHub에서 기여 가능

### 비즈니스 (쇼핑몰 운영자)

- AI 어시스턴트, 챗봇, 임베디드 경험 — 어디서든 고객 응대 가능
- 각 플랫폼마다 체크아웃을 새로 만들 필요 없음
- 비즈니스 로직과 고객 관계는 그대로 유지

### AI 플랫폼

- 단일 프로토콜로 수백만 비즈니스와 연동
- Google AI Mode, Gemini, ChatGPT 등에서 직접 구매 가능

## 실제 사용 사례

Google은 이미 **Google AI Mode**와 **Gemini** 앱에서 UCP를 적용하고 있습니다:

1. 사용자가 "런던 여행용 가방 추천해줘"라고 질문
2. Gemini가 UCP로 여러 쇼핑몰의 카탈로그를 검색
3. 마음에 드는 가방을 발견하면 바로 장바구니에 추가
4. UCP 체크아웃으로 Gemini 내에서 결제 완료
5. 비즈니스의 기존 PSP로 결제 처리 — Google이 대행하지 않음

## 시작하려면?

1. **[ucp.dev](https://ucp.dev/)** 에서 문서 읽기
2. **[GitHub 저장소](https://github.com/universal-commerce-protocol/ucp)** 에서 스펙 확인
3. **[Google 구현 가이드](https://developers.google.com/merchant/ucp)** 로 Merchant Center 연동
4. SDK로 프로토타입 구축 후 테스트

## 요약

| 항목 | 내용 |
|------|------|
| **정체** | 에이전트 커머스용 오픈 표준 프로토콜 |
| **개발** | Google 주도, Shopify 등 20+ 파트너 공동 개발 |
| **핵심 기능** | 카탈로그 검색, 장바구니, 체크아웃, 주문 관리 |
| **전송** | REST, MCP, A2A, AP2 |
| **보안** | OAuth 2.0, AP2, 토큰화 결제 |
| **오픈소스** | GitHub에서 스펙·문서·SDK 공개 |
| **사이트** | [ucp.dev](https://ucp.dev/) |

UCP는 "AI가 대신 사준다"는 미래를 현실로 만드는 인프라입니다. 커머스의 HTTP가 될 수 있을지, 커뮤니티의 선택이 기대됩니다.
