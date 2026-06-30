---
title: "Claude Science: 과학자를 위한 AI 워크벤치가 의미하는 것"
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
draft: false
coverImage: /images/claude-science-ai-workbench-2026-07-01/hero.jpg
---

Anthropic이 **Claude Science**를 공개했다. 그냥 “논문을 잘 읽는 챗봇”이 아니다. PubMed, Jupyter, R, HPC 클러스터, 단백질 구조 뷰어, 유전체 데이터베이스처럼 연구자가 매일 오가던 도구들을 하나의 작업대 위에 올려놓겠다는 선언에 가깝다.

핵심은 이거다. **AI가 답을 쓰는 단계에서, 실험·분석·검증의 작업 환경으로 들어가고 있다.**

![Anthropic이 공개한 Claude Science 소개 이미지. 과학 연구용 AI 워크벤치가 ‘채팅창’보다 ‘실험대’에 가까워지고 있음을 보여준다.](/images/claude-science-ai-workbench-2026-07-01/hero.jpg)

---

## 연구자는 왜 또 하나의 앱을 열어야 하나

과학 연구의 병목은 “아이디어가 없어서”만 생기지 않는다. 오히려 훨씬 사소한 곳에서 시간이 샌다. 논문은 PubMed에서 찾고, 데이터는 GEO나 UniProt에서 받고, 분석은 Jupyter나 R에서 돌리고, 큰 작업은 클러스터에 올리고, 그림은 다시 고치고, 인용과 수치는 따로 확인한다.

Claude Science가 노리는 지점은 바로 이 **도구 사이의 마찰**이다. 연구자가 “이 후보 타깃을 조직별 발현, 안전성, 기존 문헌 기준으로 봐줘”라고 말하면, 에이전트가 필요한 데이터베이스와 분석 환경을 이어 붙이고, 결과물과 그 결과물을 만든 코드·환경·대화 기록까지 남긴다.

> 중요한 변화는 “AI가 과학 지식을 안다”가 아니라, **AI가 연구 작업의 흔적을 남기며 실행한다**는 쪽에 있다.

## 답변이 아니라 ‘감사 가능한 산출물’을 만든다

Claude Science의 가장 좋은 표현은 AI workbench다. 워크벤치는 말 그대로 작업대다. 답변 하나를 툭 던지는 곳이 아니라, 그림을 만들고, 원고를 다듬고, 분석 코드를 남기고, 다시 수정하는 장소다.

Anthropic은 Claude Science가 3D 단백질 구조, 게놈 브라우저 트랙, 화학 구조 같은 과학적 아티팩트를 네이티브로 렌더링한다고 설명한다. 더 중요한 건 렌더링 자체보다 **재현성**이다. 그림 하나를 만들더라도 어떤 코드와 환경에서 나왔는지, 어떤 입력을 썼는지, 어떤 대화 흐름으로 만들어졌는지를 같이 남긴다.

![Claude Science는 결과 그림만 보여주는 것이 아니라, 그 그림을 만든 코드와 환경, 설명, 기록까지 함께 남기는 쪽을 강조한다.](/images/claude-science-ai-workbench-2026-07-01/artifacts.jpg)

이건 과학자에게 꽤 큰 차이다. “그럴듯한 그래프”는 연구실에서 아무 쓸모가 없다. 나중에 다시 만들 수 있어야 하고, 동료가 검토할 수 있어야 하며, 숫자가 어디서 왔는지 추적 가능해야 한다. Claude Science는 그래서 리뷰어 에이전트를 붙인다. 인용이 맞는지, 계산이 틀리지 않았는지, 그림이 코드와 맞는지를 확인하고 오류를 고치게 한다.

## 클러스터와 GPU까지 ‘대화의 일부’가 된다

대형 분석은 채팅창 안에서 끝나지 않는다. 단백질 접힘 예측, 유전체 파이프라인, 대규모 single-cell RNA-seq 분석은 노트북 한 대로는 부족할 수 있다. 기존에는 연구자가 작업 스크립트를 만들고, 클러스터에 제출하고, 실패 로그를 보고, 다시 고치는 과정을 반복했다.

Claude Science는 이 과정을 에이전트가 맡는 그림을 제시한다. 사용자의 랩톱, Linux 서버, HPC 로그인 노드, 또는 Modal 같은 온디맨드 컴퓨트 자원을 연결해 필요한 만큼 확장한다. 다만 마음대로 외부 자원을 쓰는 구조는 아니다. 계획을 세우고, 새 리소스에 접근하기 전 확인을 받고, 사용자가 결정을 검토하거나 취소할 수 있게 한다고 밝힌다.

![Claude Science의 컴퓨트 관리 개념. 연구자가 클러스터 제출과 GPU 확장을 직접 붙잡는 대신, 에이전트가 계획·실행·검토 흐름을 관리하는 쪽으로 이동한다.](/images/claude-science-ai-workbench-2026-07-01/compute.jpg)

여기서 흥미로운 포인트가 하나 더 있다. Anthropic은 큰 데이터셋이 이미 있는 시스템 밖으로 나갈 필요가 없다고 강조한다. Claude Science는 로컬 또는 연구실 인프라 위에서 세션을 실행하고, 각 단계에 필요한 문맥만 Claude로 보낸다는 설명이다. 민감한 생명과학 데이터에서는 이 차이가 제품의 성패를 가를 수 있다.

## 60개 이상의 스킬과 커넥터, 과학용 MCP의 방향

Claude Science에는 유전체학, single-cell, proteomics, 구조생물학, cheminformatics 등을 위한 **60개 이상의 curated skills와 connectors**가 준비되어 있다. 생물학만 봐도 UniProt, PDB, Ensembl, Reactome, ClinVar, ChEMBL, GEO 같은 데이터베이스가 각각 다른 스키마와 질의 방식을 가진다. 연구자 입장에서는 “질문 하나”지만, 실제로는 여러 시스템을 건너뛰어야 한다.

Claude Science의 에이전트는 이 연결을 미리 갖춘 상태로 출발한다. 또 NVIDIA BioNeMo Agent Toolkit을 통해 Evo 2, Boltz-2, OpenFold3 같은 생명과학 모델과 라이브러리에도 닿는다. 연구실이 이미 쓰는 파이프라인이나 사내 도구가 있다면 connector나 reusable skill로 이어 붙일 수 있다는 점도 중요하다.

![Claude Science는 생명과학 데이터베이스와 모델, 연구실 내부 파이프라인을 한 대화 안에 연결하려 한다. 과학용 에이전트의 경쟁력은 모델 성능만이 아니라 연결된 도구의 깊이에서 나온다.](/images/claude-science-ai-workbench-2026-07-01/databases.jpg)

이 대목은 Claude Code나 MCP 흐름을 본 사람에게 익숙하다. 범용 모델 하나가 모든 걸 외우는 대신, **도메인별 스킬과 검증 가능한 실행 환경을 붙여서 에이전트를 만든다.** 과학 분야에서는 그 요구가 더 빡세다. 틀린 답변이 “조금 불편한 자동완성”이 아니라, 잘못된 실험 설계나 근거 없는 주장으로 이어질 수 있기 때문이다.

## 실제 베타 사례가 말해주는 것

Anthropic이 소개한 베타 사례는 꽤 공격적이다. Manifold Bio는 조직 표적 치료제 후보를 평가하는 데 Claude Science를 썼다. 조직별 표면 발현, trafficking, 안전성 기준을 놓고 후보 타깃을 순위화했고, 내부 독점 데이터에서 얻은 기준까지 맥락으로 반영했다고 한다.

Allen Institute의 신경과학자 Jérôme Lecoq은 약 20개의 커스텀 스킬로 “computational review template”을 만들었다. 수천 편의 논문에서 중심 주장과 정량 결과를 뽑아 evidence state database에 저장하고, 섹션별 하위 에이전트가 긴 리뷰를 작성한다. 특히 한 에이전트가 쓰고 다른 리뷰어 에이전트가 인용과 정확성을 비판하는 actor-critic 구조가 핵심이었다.

UCSF Brain Tumor Center의 Stephen Francis는 glioma의 분자역학 연구에서 Claude Science가 분석을 크게 가속했다고 말한다. Anthropic에 따르면, 여러 접근법에 걸친 germline workup을 이전 대비 약 10분의 1 시간에 수행했고, 연구팀이 결과를 독립적으로 검증했다.

숫자만 보면 화려하다. 하지만 여기서 더 중요한 질문은 “몇 배 빨라졌나”가 아니다. **속도가 빨라질수록 검증 구조가 같이 빨라졌는가**다. Claude Science가 리뷰어 에이전트와 감사 가능한 산출물을 전면에 내세우는 이유도 여기에 있다.

## 그래서 이건 과학자의 대체재인가, 증폭기인가

내가 보기엔 지금 단계의 Claude Science는 과학자를 대체한다기보다, 연구실의 “작업 기억”과 “잡무 실행력”을 증폭하는 도구에 가깝다. 문헌을 훑고, 데이터베이스를 연결하고, 파이프라인을 돌리고, 그림을 다시 고치고, citation fidelity를 점검하는 일은 중요하지만 반복적이다. 그 반복을 줄이면 과학자는 질문 설계와 검증, 해석에 더 오래 머물 수 있다.

물론 위험도 선명하다. 에이전트가 너무 매끄럽게 결과를 만들면, 연구자는 검증을 덜 하게 될 수 있다. 내부 데이터와 외부 모델, HPC 자원, 논문 인용이 한 세션 안에 묶일수록 권한 관리와 감사 로그도 더 중요해진다. “AI가 알아서 했다”는 말은 연구에서 면책 사유가 될 수 없다.

그래서 Claude Science의 진짜 관전 포인트는 기능 목록이 아니다. **과학 연구가 ‘채팅형 AI’에서 ‘검증 가능한 에이전트 작업실’로 이동할 수 있느냐**다. 이 전환이 성공하면, 과학용 AI 제품의 기준은 모델 점수보다 더 실용적인 질문으로 바뀐다.

이 결과를 누가 재현할 수 있는가. 6개월 뒤에도 같은 그림을 다시 만들 수 있는가. 틀린 인용과 계산을 누가 잡아내는가. 그리고 마지막으로, 연구자는 더 많은 시간을 진짜 질문에 쓰게 되었는가.

## 시작하려면

Claude Science는 현재 베타로 제공된다. Anthropic에 따르면 macOS와 Linux에서 사용할 수 있고, Claude Pro, Max, Team, Enterprise 플랜 사용자가 대상이다. Team과 Enterprise는 관리자의 활성화가 필요하다.

또 Anthropic은 최대 50개의 Claude Science AI for Science 프로젝트에 최대 3만 달러 크레딧을 지원하고, Modal도 일부 프로젝트에 최대 2천 달러 컴퓨트 크레딧을 제공한다고 밝혔다. 신청은 2026년 7월 15일까지, 프로젝트 기간은 2026년 9월 1일부터 12월 1일까지다.

원문: [Claude Science, an AI workbench for scientists](https://www.anthropic.com/news/claude-science-ai-workbench)
