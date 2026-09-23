---
title: "Claude Science — 답을 쓰는 AI가 아니라 감사 가능한 작업대가 과학용 AI의 기준임"
date: 2026-07-01
tags:
  - Anthropic
  - Claude
  - AI-agents
  - scientific-discovery
  - research-agent
  - bioinformatics
  - MCP
  - Skills
coverImage: /images/claude-science-ai-workbench-2026-07-01/hero.jpg
description: "Anthropic이 공개한 과학용 AI 워크벤치 Claude Science를 업무자동화 관점으로 정리. 도구 간 마찰 제거, 감사 가능한 산출물, 리스크 게이팅된 컴퓨트 관리가 핵심이다."
draft: true
refactor_hub: research-agents-01
refactor_status: queued
---

Anthropic이 과학자용 AI 워크벤치 Claude Science를 베타로 공개함. 논문 잘 읽는 챗봇이 아니라 PubMed, Jupyter, HPC 클러스터, 단백질 뷰어, 유전체 DB를 하나의 작업대에 올리겠다는 선언에 가까워서 정리함. 원문은 [Anthropic 발표](https://www.anthropic.com/news/claude-science-ai-workbench).

1. 노리는 지점이 정확함. 과학 연구의 병목은 아이디어 부족이 아니라 도구 사이 마찰임. 논문은 PubMed(생물의학 논문 검색 데이터베이스)에서, 데이터는 GEO·UniProt에서, 분석은 Jupyter·R에서, 큰 작업은 클러스터에, 그림은 다시 고치고 인용은 따로 확인함. "이 후보 타깃을 조직별 발현·안전성·문헌 기준으로 봐줘"라는 말 하나가 실제로는 여러 시스템을 건너는 작업임. 이 마찰을 에이전트가 이어 붙이는 것임.

![](/images/claude-science-ai-workbench-2026-07-01/gifs/scientist-microscope.gif)

2. 중요한 변화는 지식이 아니라 실행의 흔적임. AI가 과학 지식을 아느냐가 아니라 연구 작업의 흔적을 남기며 실행하느냐가 차이를 만듦. 그림 하나를 만들어도 어떤 코드·환경·입력·대화 흐름에서 나왔는지를 같이 남김. "그럴듯한 그래프"는 연구실에서 쓸모가 없고 재현·검토·추적이 가능해야 한다는 요구를 제품 구조로 넣은 것임.

![](/images/claude-science-ai-workbench-2026-07-01/gifs/stack-of-documents.gif)

![데이터베이스 연동 구조](/images/claude-science-ai-workbench-2026-07-01/databases.jpg)

3. 렌더링보다 재현성이 본체임. 3D 단백질 구조, 게놈 브라우저 트랙, 화학 구조를 네이티브로 렌더링한다는 얘기보다 중요한 건 리뷰어 에이전트를 붙였다는 것. 인용이 맞는지, 계산이 틀리지 않았는지, 그림이 코드와 맞는지 확인하고 오류를 고치게 함. 생성-검증 분리가 제품 레벨에서 구현돼 있다는 점이 하네스 설계 원칙과 같은 방향임.

4. 컴퓨트 관리 방식이 안전 설계의 표본임. 에이전트가 마음대로 외부 자원을 쓰는 게 아니라 계획을 세우고 새 리소스 접근 전 확인을 받고 사용자가 검토·취소할 수 있음. 그리고 큰 데이터셋이 이미 있는 시스템 밖으로 나가지 않고 필요한 문맥만 Claude로 보냄 — 민감한 생명과학 데이터에서는 이 차이가 제품 성패를 가른다는 판단이 맞음.

![컴퓨트 관리 화면](/images/claude-science-ai-workbench-2026-07-01/compute.jpg)

5. 60개 이상의 큐레이티드 스킬과 커넥터가 연결 층임. UniProt, PDB, Ensembl, ClinVar, ChEMBL 같은 DB가 각각 다른 스키마를 가진 상태에서 범용 모델 하나가 전부 외우는 대신 도메인별 스킬과 검증 가능한 실행 환경을 붙이는 구조임. BioNeMo(생명과학용 AI 프레임워크)로 Evo 2, Boltz-2 같은 생명과학 모델까지 닿고 연구실 내부 파이프라인도 커넥터로 붙일 수 있음.

![아티팩트 재현성](/images/claude-science-ai-workbench-2026-07-01/artifacts.jpg)

6. 베타 사례 세 개가 방향을 보여줌. Manifold Bio가 표적 치료제 후보를 내부 독점 데이터 기준까지 반영해 순위화한 것. Allen Institute가 커스텀 스킬 20개로 수천 편 논문에서 주장·정량 결과를 뽑아 evidence database를 만들고, 한 에이전트가 쓰고 다른 리뷰어 에이전트가 인용과 정확성을 비판하는 actor-critic(생성 담당과 비평 담당을 분리해 서로 검증하게 하는 구조)를 쓴 것. UCSF가 germline workup을 이전의 10분의 1 시간에 수행하고 연구팀이 독립 검증한 것.

7. 필자 관점에서 관전 포인트는 속도가 아니라 검증 구조임. 속도가 빨라질수록 검증 구조도 같이 빨라졌는지가 문제고, 에이전트가 너무 매끄럽게 결과를 만들면 연구자가 검증을 덜 하게 되는 위험이 있음. 내부 데이터·외부 모델·HPC·인용이 한 세션에 묶일수록 권한 관리와 감사 로그가 중요해지고 "AI가 알아서 했다"는 연구에서 면책 사유가 될 수 없음.

8. 이 전환이 성공하면 과학용 AI 제품의 기준이 모델 점수에서 실용 질문으로 바뀜. 누가 재현할 수 있는가, 6개 뒤에도 같은 그림을 다시 만들 수 있는가, 틀린 인용과 계산을 누가 잡는가, 연구자가 진짜 질문에 더 오래 머물게 되었는가. 필자의 자동화 파이프라인도 같은 질문을 받아야 함 — 스킬이 아니라 게이트와 감사 로그가 제품의 품질을 정의한다는 것.

9. 남는 판단. 지금 단계의 Claude Science는 과학자의 대체재가 아니라 연구실의 작업 기억과 잡무 실행력을 증폭하는 도구임. 채팅형 AI에서 검증 가능한 에이전트 작업실로 이동하느냐가 다음 관전 지점이고, 그 원칙 — 감사 가능한 산출물, 생성-검증 분리, 리스크 게이팅 — 은 과학 밖의 에이전트 제품에도 그대로 적용된다는 게 이 발표가 주는 실무 교훈임.

![Claude Science 워크벤치](/images/claude-science-ai-workbench-2026-07-01/hero.jpg)
