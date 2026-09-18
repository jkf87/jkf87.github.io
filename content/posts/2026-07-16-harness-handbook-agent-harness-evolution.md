---
title: "에이전트 하네스를 파일이 아니라 행동 지도로 읽는 법 — Harness Handbook 실무 정리"
date: 2026-07-18T01:20:00+09:00
draft: false
summary: "하네스 수정 요청은 행동 언어로 들어오는데 저장소는 파일·함수로 짜여 있음. 이 간극을 행동 중심 지도로 메우는 Harness Handbook 논문을 하네스 운영 관점에서 정리함."
tags: ["AI Agent", "Agent Harness", "Behavior Localization", "Code Understanding", "Tencent Hunyuan", "Loop Engineering"]
categories: ["AI Agent", "Software Engineering"]
source_url: "https://arxiv.org/abs/2607.13285"
project_url: "https://ruhan-wang.github.io/Harness-Handbook/"
authors: ["Ruhan Wang", "Yucheng Shi", "Zongxia Li", "Haitao Mi", "Dongruo Zhou"]
affiliations: ["Tencent HY LLM Frontier", "Indiana University", "University of Maryland", "University of Georgia", "National University of Singapore"]
---

하네스를 고쳐본 사람은 앎. 어려운 건 코드를 못 짜는 게 아니라 어디를 고쳐야 하는지 찾는 것임. "파일 삭제 전에 확인을 넣어줘" 하나가 프롬프트 생성, 도구 래퍼, 권한 정책, 상태 관리에 흩어져 있으니까. Harness Handbook은 이걸 행동 중심 지도로 푸는 접근임.

1. 문제 정의부터. 수정 요청은 "무엇을 해야 하는가"로 들어오는데 저장소는 파일·함수 단위로 조직돼 있음. 이 매핑은 자동으로 주어지지 않음. 논문은 이걸 behavior localization, 즉 수정하려는 행동이 구현된 모든 코드 위치를 찾는 문제로 명명함.

2. 왜 이게 병목인가. 모델 API가 바뀌고 실행 환경이 바뀌고 요구사항이 바뀔 때마다 하네스를 고쳐야 하는데, 코드 검색과 긴 컨텍스트로는 행동-구현 연결을 결국 사람이나 코딩 에이전트가 직접 복원해야 함. 하네스가 커질수록 이 탐색 비용이 선형으로 늘어남.

3. Handbook의 표현은 3층임. L1은 전체 아키텍처·실행 모델·데이터 흐름의 시스템 개요. L2는 컴포넌트·실행 단계별 책임과 입출력. L3는 실제 소스 위치와 연결된 세부 정보. 필요한 만큼만 L1→L2→L3로 내려가는 progressive disclosure 구조임.

![Harness Handbook 표현 구조](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-1-p4.png)

4. 자동 생성 파이프라인도 3단계임. 정적 분석으로 함수·호출 edge·소스 위치를 결정론적으로 뽑고(확인 안 된 호출은 unresolved로 남김), 실행 단계 골격에 소스를 배치하고, L1-L3 문서와 소스 위치를 연결해서 패키징함. 수동 문서가 아니라 재생성 가능한 자산임.

5. 코딩 에이전트가 쓰는 방식은 Behavior-Guided Progressive Disclosure임. 요청이 오면 L1에서 관련 행동 영역 찾고, L2에서 컴포넌트 좁히고, L3에서 소스 위치 확인하고, 현재 저장소에 위치가 존재하는지 검증한 다음 편집 계획을 세움. diff가 나오면 Handbook도 다시 동기화함.

6. 검증 환경은 Codex와 Terminus-2 두 오픈소스 하네스에 행동 기반 수정 요청 30개씩임. 요청은 목표 위치를 안 알려주는 Query, 여러 파일을 가로지르는 Cross-file, 키워드 검색으로 안 잡히는 Search-Hostile 세 유형으로 나눴음.

7. 결과. 계획 품질 win rate가 Codex에서 38.3% vs 28.3%, Terminus-2에서 45.6% vs 26.7%. Planner 토큰 사용량은 Codex에서 12.7%, Terminus-2에서 8.6% 감소함. Localization F1(정답 위치와 예측 위치의 겹침을 정밀도·재현율로 계산한 점수)은 24개 비교 전부에서 개선, 폭은 5.0~18.8포인트였음.

![계획 품질 및 토큰 비교](/images/2026-07-16-harness-handbook-agent-harness-evolution/fig-3-p8.png)

8. 흥미로운 건 complete miss 감소임. reference plan과 겹치는 게 0인 Wrong 케이스가 늘지 않았고 최대 25.9포인트까지 줄었음. 이미 맞는 걸 조금 더 잘 맞춘 게 아니라 엉뚱한 곳으로 가는 실패 자체를 줄였다는 뜻임.

9. 개선 폭은 요청 유형에 따라 달랐음. Codex에선 Query, Terminus-2에선 Search-Hostile에서 가장 컸고 폭은 16.3~33.3포인트임. 키워드 검색으로 쉽게 잡히는 수정엔 기존 도구로 충분하고, 행동이 여러 모듈에 흩어져 있을수록 이 접근의 이득이 커진다는 해석임.

10. 조심할 점 셋. 평가는 end-to-end 수정 성공률이 아니라 localization과 edit planning 품질 기준임. Judge에 LLM을 썼으니 수치는 그 평가 설계 안에서 봐야 함. 대상도 하네스 두 개뿐이라 일반화에는 갭이 있음.

11. 그래도 방향은 공감함. "컨텍스트를 더 길게"가 아니라 "행동과 구현 사이의 지도를 만들자"는 문제의식. 자동화 시스템의 수정 요청은 늘 "승인 없이 부르지 마라", "이 상태에선 물어봐라" 같은 행동 언어로 들어옴. 지도가 없으면 그걸 매번 다시 복원하는 비용을 계속 지불함.

12. 당장 채택할 수 있는 축소판. 자주 고치는 에이전트 행동 5개를 적고, 각 행동이 걸치는 파일·함수·상태·도구 호출을 표로 정리하고, 수정 뒤 표가 유효한지 확인하는 것부터임. 코딩 에이전트에 맡길 때도 파일명이 아니라 행동명으로 접근시키는 습관부터 바꾸면 됨.

하네스와 루프 설계를 직접 실습해보고 싶다면 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』를 참고할 것.

원문: [arXiv:2607.13285](https://arxiv.org/abs/2607.13285)
