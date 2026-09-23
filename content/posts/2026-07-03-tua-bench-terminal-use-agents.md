---
title: "터미널 에이전트 어디까지 믿을 수 있나 — TUA-Bench가 밝힌 65.8%의 벽"
date: 2026-07-03T07:00:00+09:00
tags:
  - LLM
  - AI Agent
  - Benchmark
  - Terminal
  - CLI
  - Meta AI
categories:
  - AI 연구
  - Agent
description: 터미널 범용 과제 120개로 에이전트를 평가한 TUA-Bench 결과, 최강 조합도 65.8%에 그침. 에이전트 도입 판단의 현실적 기준치로 쓸 만한 숫자를 정리함.
source_url: "https://arxiv.org/abs/2606.28480"
draft: true
refactor_hub: dev-tools-01
refactor_status: queued
---

터미널 에이전트를 업무에 실제로 쓰는 입장에서 가장 궁금한 건 성능이 아니라 "어디까지 위임할 수 있는가"임. Meta AI·Duke·Stanford가 만든 TUA-Bench(터미널에서 벌어지는 문서·메일·미디어·시스템 관리 같은 범용 과제 120개로 에이전트 성공률을 재는 벤치마크)가 그 질문에 숫자로 답함. 최고 성능 조합의 성공률은 65.8%.

1. 배경. LLM이 컴퓨터를 다루는 방식은 GUI 클릭 방식과 터미널 CLI 방식으로 나뉨. 터미널이 텍스트 네이티브라 LLM의 강점과 잘 맞음. 근데 기존 터미널 벤치마크는 SWE-bench(실제 GitHub 저장소의 버그를 고치는지 채점하는 코딩 벤치마크)처럼 코딩에 편중돼 있었음. 현실 터미널 작업은 문서 편집, 메일 정리, 데이터 수집까지 훨씬 넓음. 이 간극을 메운 게 TUA-Bench임. 원문은 [arXiv:2606.28480](https://arxiv.org/abs/2606.28480).

![TUA-Bench 개요](/images/2026-07-03-tua-bench-terminal-use-agents/fig-p1.jpeg)

2. 구성. 초안 394개 과제를 큐레이션해 120개만 남김. Office(문서·메일), Web & Info(실시간 검색·API 수집), Multimedia(FFmpeg, 즉 명령어로 영상·음성 파일을 변환·편집하는 오픈소스 도구로 편집·리사이즈), System & SW(패키지·서비스 설정), Science & Eng(생물정보학 파이프라인·물리 시뮬레이션) 5개 도메인임. Science 트랙은 박사 연구자들과 공동 설계해서 단순 코딩이 아닌 도메인 지식이 필요한 과제임.

![TUA-Bench 과제 구성](/images/2026-07-03-tua-bench-terminal-use-agents/fig-p2.png)

3. 채점은 전부 실행 기반임. 컨테이너 샌드박스(외부 영향 없이 격리해 에이전트를 안전하게 돌리는 가상 환경)에서 실제로 돌리고 결과를 검증함. 모델 자기 보고를 안 믿는다는 점이 신뢰 포인트임. 나도 에이전트 결과 검증할 때 "했다고 함"이 아니라 산출물 확인으로 게이트를 짜는데, 그 설계와 같은 방향임.

4. 결과. 1위 Claude Code + Opus 4.8(max)이 65.8%, 2위 Codex + GPT-5.5(xhigh)가 64.7%, OpenHands + Opus 4.8이 63.4%임. 오픈웨이트는 GLM-5.1 48.1%, DeepSeek-V4 Pro 46.2%로 아직 격차가 큼.

![리더보드 결과](/images/2026-07-03-tua-bench-terminal-use-agents/fig-p6.png)

![](/images/2026-07-03-tua-bench-terminal-use-agents/gifs/robot-working-terminal.gif)

5. 카테고리별로 보면 패턴이 보임. System & SW가 가장 쉽고 Office와 Multimedia가 가장 어려움. Opus는 Web & Info에서 압도적이고 나머지는 중위권, GPT-5.5 xhigh가 전 카테고리 고른 편임. 그래서 "어떤 모델을 쓸까"보다 "어떤 종류 과제를 맡길까"가 먼저임.

6. 실패 패턴이 실무적으로 제일 유용함. 장기 계획에서 길을 잃음, CLI 도구 옵션 오해, 중간 결과 확인 없이 진행, 실패 후 원인 파악 없이 재시도 반복. 똑똑해진다고 저절로 해결되는 게 아니라 하네스(에이전트를 실제로 돌리는 실행 틀 — 프롬프트·도구·검증 장치 세팅 전체) 설계·피드백 루프 문제임.

![](/images/2026-07-03-tua-bench-terminal-use-agents/gifs/agent-fail-facepalm.gif)

7. 그래서 내 조치. 터미널 에이전트에 위임할 때 시스템 설정·스크립트류는 적극적으로, 멀티스텝 문서·미디어 처리는 중간 결과 체크포인트를 강제로 넣음. 그리고 실패 시 무작정 재시도하지 않게 실패 원인을 먼저 보고하게 프롬프트를 고정함. 34.2%의 실패율을 전제로 설계해야 함.

8. 문제제기 하나. 65.8%라는 숫자가 낮아 보이지만, 과제가 샌드박스에서 한 번에 돌아가는 엄격한 조건임. 실무는 검색도 하고 문서도 열어보는 여유가 있어서 체감 성공률은 벤치보다 높게 나옴. 근데 그 여유가 검증 게이트를 대체하진 않음. 기준치로는 65%를 전제하는 게 안전함.

9. 결론. 터미널은 LLM에게 가장 자연스러운 인터페이스임. 근데 자연스럽다는 것과 완벽하다는 건 다른 문제고, 그 차이를 숫자로 보여준 게 이 벤치의 가치임.
