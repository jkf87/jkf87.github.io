---
title: "하루 종일 도는 에이전트 하네스 — 분해·메모리·검증 통합으로 상용 에이전트 앞선 OneDayAgent"
date: 2026-08-06
tags:
  - agent
  - harness
  - long-horizon
  - LLM
  - loop
  - automation
  - task-decomposition
  - verification
  - memory
  - MCP
  - tool-use
source: arxiv
source_url: https://arxiv.org/abs/2608.05013
description: "롱호라이즌 일상 작업용 하네스 OneDayAgent를 AgentIF-OneDay 벤치마크 결과와 함께 정리. 검증 단계 추가만으로 +3.3점, 통합 구성 0.821로 상용 에이전트를 앞선 설계를 분석했다."
---

하루 걸리는 작업을 맡기면 목표 이탈, 상태 유실, 컨텍스트 오버플로우로 무너지는 문제를 하나의 하네스로 풀은 논문이 나옴.

![](/images/2026-08-06-onedayagent-long-horizon-harness/gifs/marathon-crawling-finish.gif) 상용 에이전트들보다 높은 점수를 냈다는 게 눈에 띄어서 정리함. 원문은 [arXiv:2608.05013](https://arxiv.org/abs/2608.05013).

1. 문제 정의가 실무 감각과 맞음. 롱호라이즌 일상 작업은 목표와 제약을 여러 단계에 걸쳐 보존해야 하고, 웹-로컬 파일-코드 실행 등 이기종 환경을 넘나들고, 멀티모달 입력이 섞임. 그래서 목표 이탈, 상태 유실, 컨텍스트 오버플로우 세 실패가 복합으로 터지는데 기존 연구는 개별 실패만 다뤘음.

2. 구조는 5단계임. Planner가 요청을 순차 서브태스크로 분해하고, Executor가 각각을 ReAct 루프로 실행하고, Synthesizer가 결과를 합성하고, Verifier가 원 요청·서브태스크 답변과 대조 검증하고, 실패 시 Repair가 문제 부분만 국소 수정함. 웹·학술·연산·파일·멀티모달 도구를 단일 액션 스페이스로 통합한 점도 실용적임.

![OneDayAgent 5단계 파이프라인](/images/2026-08-06-onedayagent-long-horizon-harness/fig-2-p3.png)

![](/images/2026-08-06-onedayagent-long-horizon-harness/gifs/robot-factory-assembly-line.gif)

3. 실행 메모리가 세 겹임. 관측값을 bounded evidence로 압축하는 요약 절단, 서브태스크 경계에서 low-level trace를 버리고 compact checkpoint만 넘기는 상태 전달, 그리고 컨텍스트가 90% 도달하면 LLM 요약으로 압축하고 하드 리밋엔 비상 프루닝. 35개 태스크가 압축을 트리거했는데 최대 350K 토큰까지 누적됐고, 압축 횟수와 점수의 상관은 거의 0 — 압축이 성능을 갉아먹지 않는다는 게 중요한 검증 결과임.

![3겹 실행 메모리 구조](/images/2026-08-06-onedayagent-long-horizon-harness/fig-3-p8.png)

4. 성적은 AgentIF-OneDay에서 GLM-5.2 백엔드로 0.821. Manus 0.645, Codex 0.664, ChatGPT-Agent 0.626 같은 상용 에이전트를 크게 앞섬. 모든 슬라이스에서 1위. 대신 지연 3,217초로 느림. 하루짜리 작업 기준으론 감수 가능한 트레이드오프임.

![AgentIF-OneDay 성적](/images/2026-08-06-onedayagent-long-horizon-harness/fig-4-p9.png)

5. 근데 제일 값진 건 에블레이션임. 검증만 추가하면 +3.3점에 지연 2분 증가. 분해만 추가하면 같은 점수에 10분 추가. 즉 비용 효율 최적점은 verification-only라는 결론임. 필자 관점에서도 검증기 다는 게 제일 저렴하고 확실한 개선이었음. 이 순서 — 검증 먼저, 분해는 필요할 때 — 는 그대로 배포 플레이북이 됨.

![실패 모드 분석](/images/2026-08-06-onedayagent-long-horizon-harness/table-2-p6.png)

6. 백엔드 분석도 참고할 만함. 파라미터 스케일과 점수는 약한 상관만 보이고 단조적이지 않음. 9B가 27B보다 높고, 백엔드마다 툴콜 수와 컨텍스트 축적 스타일이 다름. 하네스가 같아도 모델의 실행 스타일이 다르게 나온다는 건 백엔드 교체 시 재튜닝이 필요하다는 뜻임.

7. 케이스 스터디의 수리 흐름이 설계를 잘 보여줌. PPT 수정 중 파일 에러 → 합성 단계에서 실패 보고 → 검증기가 누락 식별 → 수리 단계가 프레젠테이션 재생성 → 2차 검증 통과. 실패를 삼키지 않고 검증기가 잡아내 국소 복구하는 루프가 실제로 작동한 것임.

8. 문제제기. 단일 벤치마크 평가라 일반화 확인이 부족함. 워크스페이스 격리가 없어서 보안 관점에서는 그대로 못 씀 — 하루 종일 파일과 웹을 다루는 에이전트에겐 격리가 필수라 이건 제법 큰 구멍임. 그리고 53분 평균 실행 비용이 들어도 되는 작업에만 적용 가능함.

9. 남는 결론. 롱호라이즌 성능은 화려한 기술보다 분해-압축-검증-수리의 정직한 조립에서 나옴. 도입 순서는 검증부터, 그다음 상태 압축, 분해는 작업이 진짜 복잡할 때만. 상용 에이전트를 사는 것보다 이 구조를 자기 워크로드에 맞게 따서 쓰는 게 나은 경우가 많다는 게 이 논문의 실무적 메시지임.
