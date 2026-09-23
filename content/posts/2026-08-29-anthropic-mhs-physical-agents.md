---
title: "에이전트가 실험실 장비를 직접 잡는 날 — Anthropic MHS 연구 프리뷰 정리"
date: 2026-08-29
tags:
  - ai-agents
  - anthropic
  - mcp
  - lab-automation
  - robotics
categories:
  - AI
  - Agent
description: "Anthropic과 HHMI Janelia가 공개한 Model Hardware Standard 연구 프리뷰 정리. MCP·CLI·API로 실험실 장비를 연결하는 표준이고 초기 사례는 바이오·현미경·양자 레이저까지 넓음."
aliases:
  - /posts/2026-08-29-anthropic-mhs-physical-agents
draft: true
refactor_hub: multimodal-world-01
refactor_status: queued
---

Anthropic이 공개한 Model Hardware Standard, MHS의 핵심은 간단함. AI 에이전트가 현미경, 액체 핸들러, 로봇팔, 플레이트 리더 같은 물리 장비를 공통 방식으로 발견하고 제어하게 만드는 표준이라는 것. 아직 오픈소스는 아니고 research preview이며 첫 파트너는 과학 연구소와 고급 제조 현장임. 시작점은 Anthropic과 HHMI Janelia Research Campus의 협업이었음.

1. 문제로 잡은 건 모델 성능보다 앞에 있는 병목임. 실험실 장비는 각자 자기 프로그램과 인터페이스를 씀. 장비끼리 말을 못 하니 사람이 중간에서 붙이는데 통합에 몇 주에서 몇 달이 걸림. MHS는 여기에 공통 드라이버를 놓아서 read, write 같은 단순한 primitive로 장비를 다루게 함.

![MHS 구조](/images/2026-08-29-anthropic-mhs-physical-agents/official-01.png)

2. 중요한 건 발견(discovery)임. 장비가 네트워크 안에서 자기 자신을 표준 형식으로 드러내고 에이전트는 그 정보를 읽고 무엇을 조작할 수 있는지 파악함. 측정 항목, 조정 가능한 값, 안전 제한, 특성 메타데이터가 들어감. 매뉴얼과 연구자 암묵지에 흩어져 있던 정보가 드라이버 안으로 들어가는 것임.

![실험실 비교](/images/2026-08-29-anthropic-mhs-physical-agents/official-03.png)

3. 제어 경로는 세 개임. MCP(Model Context Protocol, AI 에이전트가 외부 도구·데이터 소스에 표준 방식으로 접속하게 하는 연결 규약)는 에이전트가 장비를 도구처럼 호출하는 경로. CLI는 사람이 터미널에서 다루는 방식. 코드 API는 장시간 작업이나 빠른 반복을 스크립트로 묶을 때 씀. 세 경로를 다 준 게 실무적 판단임.

4. Anthropic이 든 Claude 레이저 조정 사례가 구조의 핵심을 보여줌. Claude가 카메라로 결과를 보고 레이저 빔이 어떻게 움직였는지 확인하고 다시 조정함. 그리고 배운 절차를 deterministic script로 패키징함. 이후엔 매 단계 온라인 추론 없이 한 번의 명령으로 정렬 작업을 돌림.

5. 이 대목이 중요함. 물리 세계의 에이전트는 말로 계획하는 모델만으로는 느리고 위험함. 반복 가능하고 검증 가능한 부분은 코드로 내려야 하고 MHS는 그 경계를 표준화하려는 시도임. 에이전트로 탐색하고 스크립트로 고정하는 이중 구조는 우리 자동화 파이프라인에서도 그대로 쓰는 원칙임.

6. 초기 사례가 생각보다 넓음. Genentech는 BCA protein assay 자동화 PoC를 구현함. 액체 핸들러, 로봇팔, 플레이트 리더를 함께 조율하는 절차임. University of Washington은 qPCR(DNA를 증폭하며 진행 상황을 실시간 측정하는 실험) 증폭 곡선을 보다가 적절한 순간에 멈추는 에이전트 감독과 collision-free plate handoff를 만듦.

7. CMU는 serial dilution(시료를 단계적으로 희석해 여러 농도를 만드는 실험)을 기존보다 약 3배 빠르게 돌림. 액체 핸들러, 플레이트 리더, 로봇팔, 모니터링 카메라가 3대 컴퓨터에 흩어져 있고 인터페이스도 달랐는데 에이전트가 조율함. HHMI Janelia는 예전에 서로 공유 인터페이스가 없는 7개 vendor program을 엮어야 했던 현미경 rig를 MHS로 씀.

8. QuEra 사례도 눈에 띔. 중성 원자 양자컴퓨터 안의 레이저 시스템 일부를 에이전트가 제어했고 레이저 lock을 99.3% 확률로 사람 개입 없이 복구하는 controller를 만듦. 물리 계층 운영까지 에이전트가 들어갔다는 신호임.

![CMU 장비](/images/2026-08-29-anthropic-mhs-physical-agents/official-06.png)

9. MCP의 물리 세계 확장판이라는 관점이 맞음. MCP가 파일, 브라우저, DB, SaaS를 연결했다면 MHS는 그 생각을 물리 장비로 밀어 넣음. 장비가 자기 사용법과 안전 한계를 자연어 태그와 참조 파일로 설명한다는 게 핵심임.

10. 이 구조가 되면 병목이 바뀜. 예전 병목은 장비를 붙이는 일이었음. 다음 병목은 장비를 안전하게 운용할 정책, 평가, 관찰, 복구 절차임. 우리 쪽 업무자동화도 도구 연결이 해결되면 다음 싸움은 운영 정책이라는 점에서 같은 구조임.

![자율 실험 루프](/images/2026-08-29-anthropic-mhs-physical-agents/official-14.png)

11. 안전 문제는 남아 있음. Claude는 텍스트와 이미지로 물리 세계를 배워서 공간 추론과 물리 추론에 한계가 있음. Genentech 사례에서 단백질 샘플의 거품 오류를 Claude가 처음부터 물리적 실패로 이해한 게 아니라 연구자들이 안내해야 했음. 전문가 감독이 필요한 지점이 명확함.

12. 또 하나의 제한. MHS는 programmable interface가 있는 장비에서 작동함. 프로그래밍 인터페이스가 없는 장비는 제조사가 드라이버를 만들어야 해서 확장 속도가 제조사 협력에 달림. AWS Strands Robots, Danaher, QIAGEN, Tecan, Universal Robots 등이 vendor 목록에 들어가 있고 다음 채택자로 Hugging Face LeRobot과 Raspberry Pi가 언급됨.

13. 정리하면 MHS는 아직 완성된 공개 표준이 아님. 안전 평가와 best practice를 만들기 위해 먼저 돌려보는 research preview임. 그래도 방향은 선명함. 에이전트의 다음 작업장이 브라우저와 코드 저장소를 넘어 실험실과 제조 라인으로 넓어지고 있다는 것.

14. 개인적 판단을 붙이면 "AI 과학자"라는 표현보다 이쪽이 훨씬 현실적인 신호임. 과장된 미래상보다 드라이버, 메타데이터, MCP, CLI, API 같은 지루한 연결부가 먼저 움직이고 있음. 실무에서는 보통 이런 지루한 부분이 진짜 변화를 만듦.

원문: [Previewing the Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview)
