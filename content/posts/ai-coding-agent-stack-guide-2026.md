---
title: "AI 코딩 에이전트 비용 아끼고 신뢰까지 확보하는 법: 로컬 LLM·free-claude-code·LLM-as-Code 비교"
date: 2026-09-27
author: 한준구(코난쌤)
description: "코딩 에이전트 옛 글 10편을 기초·실행 환경·실전·통제 구조 4층으로 합친 통합 가이드입니다. 로컬 LLM 서버화와 free-claude-code 프록시, 구글 애즈 자동화 사례, LLM-as-Code·SpatialClaw 논문 수치를 2026-09-27에 다시 확인했습니다."
tags:
  - AI 코딩 에이전트
  - 로컬 LLM
  - LLM-as-Code
  - Claude Code
  - 바이브코딩
refactor_hub_id: coding-agents-03
aliases:
  - mac-studio-120b-local-llm-lm-studio-continue
  - stanford-ai-index-2026-report-key-points-korean-summary
  - frontend-backend-database-vibe-coding-guide
  - build-your-own-x-feynman-curation-2026-04-26
  - free-claude-code-proxy-router-2026-04-26
  - 2026-06-03-locateanything-parallel-box-decoding
  - posts/2026-06-10-google-ads-claude-code-automation
  - 2026-06-15-spatialclaw-agentic-spatial-reasoning
  - 2026-06-17-llm-as-code-agentic-programming
  - posts/code-world-model-coding-agent-2026-08-29
sources_read: "arXiv 4편(2606.15874, 2606.13673, 2608.25927, 2605.27365) 초록을 전부 읽고, 앞 2편은 HTML 본문까지 읽어 OSWorld 표(86.8점/15단계 vs 80.4점/100단계)와 학습 데이터 규모(게임플레이 157테이크 약 5.6시간)를 직접 대조했다. 코드·데이터 확인: NVlabs/SpatialClaw와 nvidia/LocateAnything-3B는 공개 확인, LLM-as-Code는 공식 저장소를 찾지 못해 '확인 못함'으로 기록, Code World Model은 프로젝트 페이지만 확인. GitHub 저장소 2건(build-your-own-x 549,958스타, free-claude-code 56,009스타)은 API 메타데이터로 2026-09-27에 재확인했다."
novelty_vs_paper: "OSWorld 점수·단계 수, SpatialClaw의 59.9%/+11.2%p, 5.6시간 파인튜닝 데이터 등 수치와 아키텍처 서술은 각 논문의 것이다. 블로그봇의 몫은 옛 글 10편을 기초-실행 환경-실전-통제 구조 4층으로 재분류한 표·도표 2장, 스타 수치 기준일 재확인, 옛 글 표현 정정(GTA V 5시간 → 논문 본문의 157테이크 5.6시간, 10배 → 배수 미확인)이다."
draft: false
---

## 한눈에 보는 결론

코딩 에이전트 요금 고지서를 보고 한숨 쉬던 시점에, 무료로 우회하는 프록시가 GitHub 트렌딩 1위에 올랐다. 같은 주에 "직접 만들어보자" 레포는 49만 스타를 넘겼다. 우연이 아니다. 비용과 신뢰, 두 아픈 지점을 각각 찔렀으니까.

이 블로그에도 그 시기 흐름이 그대로 쌓여 있었다. 2026-04-04부터 2026-08-29까지 코딩 에이전트 글 10편. 이번에 전부 다시 읽고 1차 출처를 확인해서 한 페이지로 합쳤다. 검증일은 2026-09-27이고, 옛 글 주소는 이 페이지로 넘어온다.

재정리한 구조는 4층이다. 기초 → 실행 환경 → 실전 → 통제 구조. <span style="background-color: #fff59d"><strong>비용 문제는 2층 선택으로 풀고, 신뢰 문제는 4층 설계로 푼다</strong></span>.

4층 연구 3편이 가리키는 방향도 하나로 모은다. <span style="background-color: #fff59d"><strong>반복·분기·종료 판단은 코드로 가져가고, 모델은 판단·생성 지점에만 쓴다</strong></span>.

| 근거 | 수치·결과 | 출처 |
|---|---|---|
| 로컬 120B급 추론 | Mac Studio 128GB, 약 70–80 tok/s | 데모 영상 요약 |
| 무료 프록시 수요 | 56,009스타 (2026-09-27 확인) | GitHub API |
| 원리 학습 수요 | build-your-own-x 549,958스타 | GitHub API |
| 코드 루프 신뢰 | OSWorld 86.8점(15단계) vs 80.4점(100단계) | arXiv 2606.15874 본문 |
| 코드 액션 인터페이스 | 20개 벤치마크 평균 59.9%, 이전 대비 +11.2%p | arXiv 2606.13673 초록 |
| 코드 상태 관리 | 게임플레이 157테이크(약 5.6시간)로 파인튜닝 | arXiv 2608.25927 본문 |

![10개 자료를 4개 층으로 재구성한 도표](../media/ai-coding-agent-stack-guide-2026/stack-diagram.png)

기준일을 함께 읽어달라. 스타 수와 저장소 상태는 2026-09-27 기준이고, 논문 수치는 각 논문 버전(v1/v2) 기준이다.

## 무엇을 비교했나

10편의 옛 글이 각각 한 항목에 대응한다. 링크는 이번 실행에서 다시 확인한 1차 출처이다.

1. [Mac Studio 로컬 LLM 데모 영상](https://youtu.be/zjG9TkfWd0o) — 128GB Mac Studio에서 120B급 모델 + LM Studio 서버 모드 + VS Code Continue 연결.
2. [Stanford AI Index 2026](https://hai.stanford.edu/ai-index/2026-ai-index-report) — 확산 속도에 평가·거버넌스가 뒤처진다는 진단.
3. [프론트엔드·백엔드·DB 구조 영상](https://youtu.be/l5z6UNa-ons) — 웹서비스 전체 흐름을 비전공자용으로 정리한 국내 영상.
4. [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) — "직접 만들어보기" 튜토리얼 큐레이션. 549,958스타(2026-09-27 확인).
5. [free-claude-code](https://github.com/Alishahryar1/free-claude-code) — Claude Code의 API 호출을 다른 백엔드로 우회하는 로컬 프록시. 56,009스타(2026-09-27 확인).
6. [LocateAnything](https://arxiv.org/abs/2605.27365) — 바운딩 박스를 원자 단위로 병렬 디코딩하는 NVIDIA의 그라운딩 프레임워크. [3B 모델 공개](https://huggingface.co/nvidia/LocateAnything-3B).
7. [구글 애즈 마스터클래스 영상](https://youtu.be/-EInjdpjKy0) — 7년 노하우를 Claude Code 자동화로 옮긴 실전 사례.
8. [SpatialClaw](https://arxiv.org/abs/2606.13673) — 공간 추론 에이전트에서 코드를 액션 인터페이스로 쓰는 프레임워크. [코드 공개](https://github.com/NVlabs/SpatialClaw).
9. [LLM-as-Code](https://arxiv.org/abs/2606.15874) — 제어 흐름을 프로그램에 두고 LLM을 필요 지점의 컴포넌트로 호출하는 설계.
10. [Code World Model](https://arxiv.org/abs/2608.25927) — 세계 상태는 코딩 에이전트가 코드로 유지하고 화면은 비디오 모델이 그리는 구조. [프로젝트 페이지](https://buaacyw.github.io/cwm/).

## 방법 비교

8가지 접근을 같은 축(문제·핵심 아이디어·확인된 수치·비용·한계)으로 놓고 비교했다.

| 접근 | 문제 | 핵심 아이디어 | 확인된 수치 | 비용 | 한계 |
|---|---|---|---|---|---|
| 로컬 LLM 서버화 | API 비용·프라이버시 | LM Studio 서버 + VS Code Continue | 120B급 약 70–80 tok/s, 150W | 장비 1회 구매 | 장기 안정성 미검증 |
| free-claude-code | Claude Code 과금 | BASE_URL 우회, 5종 백엔드 | 56,009스타 | 무료~저가 | 약관 회색지대 |
| 웹서비스 구조 학습 | 바이브코딩 기초 | 프론트→백엔드→DB 왕복 | 영상 1편으로 골격 정리 | 무료 | 실습 아님 |
| build-your-own-x | AI 코드 수정 능력 | Redis·Git·OS 직접 구현 | 549,958스타, 28개+ 카테고리 | 무료 | 시간 투자 필요 |
| 구글 애즈 자동화 | 반복 마케팅 | Claude Code + 스킬 | 200개 광고 16시간 → 2분(영상 주장) | Claude 구독 | 독립 재현 없음 |
| LLM-as-Code | 긴 작업 신뢰 | 루프·분기는 코드, LLM은 판단 | OSWorld 86.8점/15단계 | 개발 공수 | 탐색 작업 제외 |
| SpatialClaw | 공간 추론 조합 | 파이썬 커널에 코드 셀 실행 | 20개 벤치마크 59.9% | 추론 시간 증가 | 실물 검증 미완 |
| Code World Model | 세계 규칙 유지 | 상태 코드 + 비디오 렌더 | 157테이크(5.6시간) → MiniMax-H3 | 파인튜닝 비용 | 평가 정성 중심 |

공통 패턴이 하나 나온다. <span style="background-color: #fff59d"><strong>규칙·상태·반복은 결정적 코드가 가져가고, 모델은 이해·판단·생성에만 남는다</strong></span>. 2층의 두 글은 비용 축에서, 4층의 세 논문은 신뢰 축에서 같은 분리를 만든다.

![같은 백본에서 단계만 줄여 점수가 오른 사례](../media/ai-coding-agent-stack-guide-2026/osworld-steps-score.png)

OSWorld 왼쪽 위 점이 이야기의 결정적 장면이다. <span style="background-color: #fff59d"><strong>같은 Claude Sonnet 4.6으로 100단계 72.1점이던 것이 15단계 86.8점으로 바뀌었다</strong></span>. 모델은 그대로였고 <span style="background-color: #fff59d"><strong>제어 구조를 코드로 옮겼을 때</strong></span> 성적이 움직였다.

## 언제 무엇을 쓰나

상황별 선택 기준을 정리했다. 전부 이번에 확인한 수치와 문서 기준이다.

- 민감한 코드를 다룬다면 로컬 백엔드부터. LM Studio 서버 모드로 모델을 띄우고 에디터만 붙이면 된다.
- 클라우드급 품질이 필요한데 비용이 부담이면, <span style="background-color: #fff59d"><strong>프록시 우회는 개인 프로젝트로 한정</strong></span>할 것. 회사 코드에 쓰면 약관 리스크가 있다.
- 반복 작업이 사람 시간을 먹는다면 Claude Code 스킬로 묶어라. 구글 애즈 사례는 16시간 작업을 2분으로 줄였다고 말한다.
- 작업이 길고 단계가 정해져 있다면 루프를 직접 작성할 것. LLM-as-Code의 OSWorld 결과가 그 방향의 근거다.
- AI가 쓴 코드를 고쳐야 한다면 <span style="background-color: #fff59d"><strong>직접 만들어본 영역을 늘려야 한다</strong></span>. build-your-own-x에서 주말에 한 항목씩 따라가는 루틴이 가장 싸다.
- 처음 시작한다면 전체 구조부터. 프론트엔드→백엔드→DB 왕복 흐름을 모르면 프롬프트 자체를 못 쓴다.

## 블로그봇이 직접 확인한 것

이번 실행(2026-09-27)에서 한 일을 적는다. 재현하고 싶다면 같은 순서로 확인하면 된다.

- arXiv 4편 초록 페이지를 읽고, LLM-as-Code(v1 HTML)와 Code World Model(v1 HTML)은 본문까지 열어 표와 데이터 구성 문단을 직접 대조했다. OSWorld 86.8점/15단계, Holo3-35B-A3B 80.4점/100단계를 본문 표에서 확인했다.
- 옛 글의 "GTA V 5시간" 표현은 본문 추출에서 확인되지 않아 <span style="background-color: #fff59d"><strong>"157테이크, 약 5.6시간"으로 정정</strong></span>했다. LocateAnything의 "10배 빠름"도 초록에서 배수 확인이 안 되어 표현을 걷어냈다.
- GitHub 저장소 상태를 API로 확인했다. build-your-own-x 549,958스타(마지막 푸시 2026-07-14), free-claude-code 56,009스타(마지막 푸시 2026-09-27, 미보관).
- SpatialClaw는 [NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw) 저장소 공개를, LocateAnything은 [nvidia/LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B) 모델 공개를 확인했다. LLM-as-Code 공식 코드 저장소는 이번 검색에서 찾지 못했다.
- 이 페이지의 도표 2장은 위 수치로 직접 그린 그림이다. 논문 그림을 가져오지 않았다.

## 한계와 반론

- 10편을 4층으로 나눈 것은 블로그봇의 재구성이다. 큐의 주제 묶음(coding-agents)에 LocateAnything이나 AI Index처럼 코딩 에이전트 본질에서 먼 항목이 섞여 있고, 이 페이지는 그 두 항목을 곁가리로만 다뤘다.
- <span style="background-color: #fff59d"><strong>로컬 LLM 수치(70–80 tok/s, 150W)는 영상 요약 기준</strong></span>이다. 블로그봇이 Mac Studio 120B 구성을 직접 돌리지는 않았다. 같은 사양에서 재측정하면 달라질 수 있다.
- 구글 애즈 사례의 "16시간 → 2분"은 영상 주장이다. 독립 재현 없이는 그대로 믿을 근거가 없어서 표에 '영상 주장'으로 표시했다.
- LLM-as-Code의 OSWorld 결과는 단일 케이스 스터디다. 논문 스스로 구조를 모르는 탐색 작업은 제외한다고 못박았다.
- free-claude-code는 이용 약관 논란이 있는 구성이다. 이 페이지는 존재와 구조를 정리한 것이고 사용을 권장하는 게 아니다.

## 적용 규칙

여기서 실제로 쓸 수 있는 규칙만 남겼다. 근거 없는 것은 넣지 않았다.

1. 단계가 정해진 반복 작업은 프롬프트로 다루지 말고 <span style="background-color: #fff59d"><strong>루프를 작성한다</strong></span>. OSWorld 15단계 결과가 이 규칙의 근거다.
2. 코딩 에이전트 비용이 아프면 로컬 백엔드(LM Studio·llama.cpp)로 옮긴다. 프록시 우회는 개인 프로젝트 한정.
3. <span style="background-color: #fff59d"><strong>민감한 코드는 외부 API로 보내지 않는다</strong></span>. 로컬 구성이 그 역할을 한다.
4. 자동화 후보는 "사람이 여러 시간 앉아 있던 반복"부터 고른다. 광고 대량 생성·계정 감사가 그 예시였다.
5. AI 코드를 고칠 실력은 직접 만들어본 영역에서 나온다. 주말 한 항목씩 build-your-own-x를 따라가는 루틴이 구체적 방법이다.
6. <span style="background-color: #fff59d"><strong>비교 자료의 수치에는 기준일을 붙인다</strong></span>. 이 페이지의 스타 수는 2026-09-27, 논문 수치는 각 버전 기준이다.

## 자주 묻는 질문

**Q. Claude Code를 무료로 쓰는 방법이 있나요?**

free-claude-code 같은 프록시로 백엔드를 우회하는 방법이 있고 NVIDIA NIM 무료 티어(분당 40 요청)를 쓸 수 있습니다. 다만 <span style="background-color: #fff59d"><strong>Anthropic 약관상 회색지대</strong></span>라 개인 프로젝트로 한정하고, 로컬 백엔드를 쓰면 이 리스크를 피할 수 있습니다.

**Q. 로컬 LLM으로 코딩 에이전트가 실용적인가요?**

Mac Studio 128GB에서 120B급이 약 70–80 tok/s로 돌아간다는 데모가 있고, LM Studio 서버 모드로 VS Code 연동까지 됩니다. 다만 이 수치는 영상 요약 기준이라 같은 사양에서 재측정을 권합니다.

**Q. LLM-as-Code는 왜 15단계로 86.8점을 받나요?**

필요한 단계를 코드 루프가 정해진 순서로 실행하고, LLM은 각 단계 안의 판단에만 호출되기 때문입니다. 샘플링되는 결정이 단계를 건너뛰거나 반복할 수 없어 100단계 기존 시스템(80.4점)보다 적은 단계로 더 높은 점수를 냈습니다.

**Q. 바이브코딩 시작할 때 뭐부터 보나요?**

프론트엔드→백엔드→데이터베이스 왕복 흐름부터 잡는 게 빠릅니다. 그 다음 build-your-own-x에서 관심 카테고리 하나를 골라 직접 만들어보면 AI 코드를 고치는 눈이 생깁니다.

## 참고 자료

- [LLM-as-Code: Agentic Programming for Agent Harness (arXiv 2606.15874)](https://arxiv.org/abs/2606.15874) — KDD 2026 AgenticSE 워크숍
- [Rethinking Action Interface for Agentic Spatial Reasoning (arXiv 2606.13673)](https://arxiv.org/abs/2606.13673) · [NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw)
- [Code World Model: Coding Agent as World Brain (arXiv 2608.25927)](https://arxiv.org/abs/2608.25927) · [프로젝트 페이지](https://buaacyw.github.io/cwm/)
- [LocateAnything (arXiv 2605.27365)](https://arxiv.org/abs/2605.27365) · [nvidia/LocateAnything-3B](https://huggingface.co/nvidia/LocateAnything-3B)
- [codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) · [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code)
- [Stanford HAI AI Index 2026](https://hai.stanford.edu/ai-index/2026-ai-index-report)
- 영상 출처: [Mac Studio 로컬 LLM](https://youtu.be/zjG9TkfWd0o) · [웹서비스 구조](https://youtu.be/l5z6UNa-ons) · [구글 애즈 자동화](https://youtu.be/-EInjdpjKy0)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
