---
title: "ToFu: 에이전트 하네스를 박스 밖으로 꺼내다 — 토큰 효율·다국어·화이트박스 연구 도구"
date: 2026-07-18
draft: false
summary: "SWE-bench Verified에서 Claude Code보다 28.4% 적은 토큰으로 더 높은 성능을 내는 오픈소스 에이전트 하네스 ToFu의 구조와 시사점을 분석한다."
tags:
  - agent
  - harness
  - LLM
  - MCP
  - open-source
  - token-efficiency
categories:
  - AI Agent
  - LLM
source_url: "https://arxiv.org/abs/2607.11423"
---

> **논문**: [ToFu: A White-Box, Token-Efficient Agent Harness for Researchers](https://arxiv.org/abs/2607.11423)
> **저자**: Junhao Ruan, Yuan Ge, Bei Li, Yongjing Yin, Yuchun Fan, Xin Chen, Jingang Wang, Chenglong Wang, Jingbo Zhu, Tong Xiao (Northeastern University / LongCat RSI, Meituan / NiuTrans Research)
> **코드**: [github.com/NiuTrans/ToFu](https://github.com/NiuTrans/ToFu) (MIT License)

## 하네스가 에이전트의 성능을 결정한다

에이전트 시스템의 성능은 LLM 자체만큼이나 그 LLM을 둘러싼 **하네스(harness)**—오케스트레이션 코드, 컨텍스트 관리, 도구 호출 인터페이스—에 달려 있다. 이는 자동차의 엔진(LLM)과 섀시·변속기·조향장치(하네스)의 관계와 비슷하다. 아무리 좋은 엔진도 조잡한 섀시 위에서는 제 성능을 낼 수 없다.

ToFu는 Northeastern University와 Meituan LongCat RSI 팀이 발표한 **오픈소스 에이전트 하네스**로, 세 가지 문제의식에서 출발한다.

1. **토큰 비효율**: 단순한 "hello"에도 수천 토큰을 소모하고, 복잡한 작업에서는 비용이 폭발한다
2. **다국어 격차**: 영어 중심 LLM의 구조적 한계로 비영어권 사용자가 성능 페널티를 받는다
3. **블랙박스 문제**: 상용 하네스(Claude Code 등)는 서버 측에서 조용히 업데이트되어 연구 재현성이 떨어진다

![Figure 1: ToFu 하네스와 인간의 상호작용](/images/2026-07-18-tofu-white-box-agent-harness/fig-1-p1.png)
*Figure 1: ToFu 하네스의 인간-에이전트 상호작용 인터페이스*

## 6개 모듈 아키텍처

ToFu는 여섯 개의 핵심 모듈로 구성된다.

![Figure 2: ToFu 하네스 전체 구조도](/images/2026-07-18-tofu-white-box-agent-harness/fig-2-p3.png)
*Figure 2: ToFu 하네스의 아키텍처 개요. 6개 모듈이 유기적으로 연결된다*

| 모듈 | 역할 |
|------|------|
| **User Interface** | 웹 UI / 소셜 봇 인터페이스, 체크포인트 복원, 위험 작업 승인 |
| **Agent Orchestration Core** | 작업 분해, planner-worker-critic 추론, 도구 호출 관리, 폴백·중단·종료 제어 |
| **Model Abstraction Layer** | 이기종 LLM 프로바이더 통합 게이트웨이, 레이트리밋·재시도·폴백 라우팅 |
| **Capability Runtime** | 셸 실행, 웹 검색, 브라우저/데스크톱 제어, MCP 어댑터(Overleaf, GitHub, Notion 등) |
| **State & Knowledge** | 대화 상태, 실행 히스토리, 장기 메모리, 재사용 가능한 스킬 저장 |
| **Context Management** | 단기 컨텍스트 구성, 압축, 캐시 인식 레이아웃, 다국어 강화 |

특히 주목할 점은 **Agent Orchestration Core**가 planner-worker-critic 패턴을 사용한다는 것이다. 단순히 LLM에 "이것 좀 해줘"라고 던지는 게 아니라, 계획→실행→비판의 루프를 명시적으로 관리한다.

## 3계층 컨텍스트 압축: 토큰을 아끼는 기술

ToFu의 핵심 혁신은 **3계층 컨텍스트 압축(three-layer context compaction)**이다. 이것이 Claude Code 대비 28.4% 적은 토큰으로 더 높은 성능을 내는 비결이다.

### 제1계층: 도구 출력의 크기 인식 예산화
검색 결과, 명령어 실행 출력, 웹 페이지 캡처 등 **대용량 도구 결과를 외부화**하고 컴팩트한 미리보기로 대체한다. 단, 소스코드 파일 읽기는 보수적으로 처리한다—잘라내면 에이전트가 반복적으로 다시 읽어서 오히려 비용이 증가하기 때문이다.

### 제2계층: 캐시 인식 마이크로 압축
최근 도구 결과와 추론 궤적은 그대로 보존하되, 오래된 대용량 출력과 이미지 결과는 간결한 플레이스홀더로 교체한다. 결정론적 규칙 기반이라 추가 LLM 호출이 필요 없고, 프롬프트 캐시 재사용을 무효화하지 않도록 설계된다.

### 제3계층: 쿼리 인식 의미적 압축
대화가 컨텍스트 한계에 다다르면, 경량 모델(GPT-4o 등)이 오래된 대화를 현재 쿼리 기준으로 요약한다. 중요한 턴은 고해상도로, 유용한 턴은 압축, 무관한 턴은 제거한다. 현재 진행 중인 턴은 항상 그대로 보존한다.

이 3계층 구조는 "하나의 전역 잘라내기 규칙"이 아니라 **보수적→중간→적극적** 압축을 상황에 따라 단계적으로 적용하는 것이 핵심이다.

## SWE-bench Verified: 더 적은 토큰으로 더 높은 성능

ToFu는 Claude opus 4.6, GLM 5.1, DeepSeek-v4-pro 세 개의 백본 LLM에서 Claude Code 및 OpenCode와 비교 평가되었다.

![Figure 3: ToFu 다국어 강화 모드 성능](/images/2026-07-18-tofu-white-box-agent-harness/fig-3-p6.png)
*Figure 3: MAPS:SWE-bench에서 다국어 강화(M-Enh)의 효과. 10개 언어 중 7개에서 개선*

핵심 결과:

- **Pass@1**: 세 LLM 평균 ToFu가 Claude Code보다 +3.8%p, OpenCode보다 +8.7%p 높음
- **토큰 사용량**: Claude Code 대비 평균 28.4% 감소 (최대 43.6%)
- **비용**: 비슷하거나 약간 낮은 비용으로 더 높은 성능

가장 흥미로운 발견은 **"더 많은 계산이 더 나은 성능을 의미하지 않는다"**는 점이다. 테스트 타임 스케일링에서 토큰을 많이 쓴다고 무조건 좋은 결과가 나오지 않으며, 하네스 설계가 토큰 효율의 핵심이라는 것을 데이터가 보여준다.

![Figure 4: ToFu UI 및 논문 리더 데모](/images/2026-07-18-tofu-white-box-agent-harness/fig-4-p10.png)
*Figure 4: ToFu 데모 UI. 좌측은 에이전트 대화 인터페이스, 우측은 논문 리더 기능*

## 다국어 강화: translate-then-reason

ToFu의 다국어 전략은 단순하면서도 효과적이다. 비영어권 사용자 입력을 **영어로 번역→영어로 추론→원래 언어로 역번역**하는 파이프라인이다. 코드 블록이나 번역 불가 영역은 보호 마커로 감싸서 의미·포맷 손상을 방지한다.

MAPS:SWE-bench에서 한국어를 포함한 10개 언어를 테스트한 결과, 평균 2.5%p 향상을 보였다. 영어 중심 LLM의 구조적 강점을 활용하면서도 사용자는 자기 언어로 에이전트와 소통할 수 있다.

## MCP 생태계 통합: 에이전트가 진짜 일하게 만들기

ToFu는 Model Context Protocol(MCP)을 통해 Overleaf, GitHub, Slack, Notion 등의 외부 플랫폼과 직접 상호작용한다. 특히 **Overleaf MCP** 통합은 학술 논문 작성 워크플로우를 자동화한다:

- LaTeX 소스 읽기 및 섹션 분석
- 초록·방법론 섹션 수정
- 버전 히스토리 및 diff 검사
- 매뉴스크립트 컴파일 및 PDF 확인

ToFu 자체가 Claude Code를 **호출 가능한 도구**로 사용할 수도 있다. 이는 하네스 위에 또 다른 하네스를 얹는 메타 구조로, 에이전트 생태계의 composability를 보여준다.

## BM25 메모리: 가볍지만 효과적인 장기 기억

ToFu의 메모리 시스템은 구조화된 Markdown 레코드에 메타데이터(이름, 설명, 태그, 스코프)를 붙여 저장하고, **BM25 랭킹**으로 검색한다. Dense embedding 대신 경량 BM25를 선택한 이유는 기술 메모리(라이브러리 이름, 에러 메시지, API, 파일 패턴)에서는 정확한 용어 매칭이 더 효과적이기 때문이다.

메모리는 프로젝트별 메모리와 전역 메모리로 분리되어, 재사용 가능한 경험은 작업 간에 공유되면서도 프로젝트 로컬 규칙을 보존한다.

![Table 3: ToFu와 OpenCode 설계 비교](/images/2026-07-18-tofu-white-box-agent-harness/table-3-p10.png)
*Table 3: ToFu와 OpenCode의 소스 검증 설계 비교*

## 시사점: 하네스 연구의 새 기준

ToFu는 단순히 "또 다른 코딩 에이전트"가 아니다. 이 논문이 던지는 메시지는 세 가지다.

**1. 하네스 설계가 모델 선택만큼 중요하다.** 같은 LLM을 써도 하네스에 따라 성능과 비용이 극적으로 달라진다. ToFu는 이를 실증적으로 보여준다.

**2. 토큰 효율은 새로운 최적화 축이다.** 더 많이 생각한다고 더 잘하는 게 아니다. 컨텍스트 압축·캐시 인식 설계·의미적 요약의 적절한 조합이 핵심이다.

**3. 화이트박스 도구가 연구 생태계에 필요하다.** 블랙박스 상용 하네스로는 하네스 진화 패턴을 연구할 수 없다. MIT 라이선스의 오픈소스 하네스는 연구자에게 재현 가능한 실험 기반을 제공한다.

에이전트 하네스 연구가 활성화되면서, "어떤 LLM을 쓰느냐"만큼이나 "어떤 하네스로 감싸느냐"가 에이전트 시스템 설계의 핵심 질문이 되고 있다.

## 더 실습해보고 싶은 분들께

에이전트 하네스와 MCP 도구 사용, 긴 컨텍스트 에이전트 루프를 직접 다뤄보고 싶다면 다음 두 자료를 추천한다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

ToFu처럼 컨텍스트 압축과 도구 오케스트레이션을 직접 설계해보고, 에이전트 루프 안에서 어떤 일이 일어나는지 실험해볼 수 있다.
