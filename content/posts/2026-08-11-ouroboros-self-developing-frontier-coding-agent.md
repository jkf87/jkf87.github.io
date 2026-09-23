---
title: "스스로를 커밋으로 고치는 코딩 에이전트 — Ouroboros 161일 실운영 결과"
date: 2026-08-11
tags:
  - agent
  - harness
  - LLM
  - coding-agent
  - self-evolution
  - terminal-bench
  - OSWorld
  - safety
  - loop
  - automation
source: arxiv
source_url: https://arxiv.org/abs/2608.08311
description: "하네스 전체를 버전 관리 대상으로 두고 reviewed commit으로 지속 개선하는 자기진화 코딩 에이전트 Ouroboros. Terminal-Bench 86.74%와 161일·11만 달러 실사용 실험에서 나온 안전 설계를 정리했다."
draft: true
refactor_hub: harness-self-improve-05
refactor_status: queued
---

에이전트가 자기 자신을 고치는 시스템은 많았지만 배포 상태에서 감사 가능한 커밋 게이트를 통과시키는 설계로 161일을 버틴 사례가 나옴. 자기 참조 시스템을 운영해본 사람 입장에서 정리할 가치가 큼. 원문은 [arXiv:2608.08311](https://arxiv.org/abs/2608.08311).

![하네스 전체가 버전 관리 대상](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/gifs/robot-coding.gif)

1. 구조가 먼저임. Ouroboros는 launcher/supervisor 경계와 변경 가능한 에이전트 저장소로 나뉨. launcher는 시작, 프로세스 감독, 릴리스 부트스트래핑, 패닉 스톱을 담당하고 저장소는 태스크 루프, 도구, 프롬프트, 메모리, 리뷰 로직까지 전부임. 하네스 전체가 버전 관리 대상이라는 게 출발점임.

![Ouroboros 아키텍처(논문 Figure 1)](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/fig-1-p4.png)

![스스로를 고치며 일하는 중](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/gifs/self-improving-at-work.gif)

2. 진화는 두 모드임. 재귀적 자유 진화는 "개선 자체"를 태스크로 스케줄해서 시스템이 검토 후 변경을 구현하고 리뷰 통과 시 커밋함. 경험 기반 핵심 진화는 일반 작업 중 발견한 버그, 비효율 컨텍스트, 도구 경로 문제를 내구성 있는 에러 클래스로 기록해서 같은 게이트로 수정함. 즉흥 고침이 아니라 분류된 에러 클래스 단위로 고친다는 게 운영 지속성의 비결로 보임.

3. 커밋 파이프라인이 안전 설계의 핵심임. 결정론적 사전검사, diff 지문, 리뷰어 증거 수집, 지문 재확인 순으로 진행하고 diff-리뷰 패널은 모든 모드에서 블로킹임. 지문 재확인은 리뷰 도중 diff가 몰래 바뀌는 걸 잡는 장치인데, 자기수정 시스템에서 이게 없으면 리뷰가 장식이 됨.

![서브에이전트 패치 통합 프로토콜(논문 Figure 2)](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/fig-2-p4.png)

4. 벤치마크는 Terminal-Bench 2.1(터미널에서 실제 작업을 수행하는 능력을 재는 벤치마크) 86.74%(이전 최고 83.8%를 약 2표준편차 차이로 상회), OSWorld-Verified(실제 컴퓨터 화면을 GUI로 조작하는 과제 벤치마크, 검증본) 90.69%, SWE-bench Pro(실제 저장소의 난이도 높은 이슈를 고치는 코딩 벤치마크) 58.2%, GAIA(검색·도구 사용·추론이 섞인 범용 어시스턴트 과제 벤치마크) 78.2%. trajectory audit으로 shortcut trial 1건을 스스로 식별해 제외한 것도 평가 신뢰성 관점에서 좋은 습관임. 벤치마크는 frozen seed로 평가하고 실사용 진화는 별도 라인으로 분리해서 재현 가능성과 진화를 안 섞음.

![벤치마크 패밀리별 결과(논문 Table 2)](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/table-2-p6.png)

5. 근데 제일 값진 건 Hope 실험임. 2026년 2월부터 161일간 하나의 에이전트를 7개 채널(웹, 음성, 텔레그램, 디스코드, X, 댓글, 이메일)로 운영. 모델 지출 110.6K 달러, 79.7B 토큰, 코드 175,755줄. 사용자 제안은 advisory로만 처리하고 변경 추진 여부는 에이전트가 결정함.

![실세션 태스크 트리 뷰(논문 Figure 3)](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/fig-3-p5.png)

6. Hope의 진화 사례 두 개가 실용적임. 중복 메시지 문제를 소셜 피드백으로 발견해 verbatim-duplicate 가드를 추가한 것. deep self-review의 컨텍스트 오버플로를 자가 관측으로 찾아내 import-graph 중심성 기반 context atlas로 교체한 것. 외부 비판과 내부 관측을 모두 에러 클래스로 흡수하는 루프가 실제로 돌았다는 증거임.

7. 안전 장치 목록이 그대로 체크리스트로 쓸 만함. 거버넌스 파일은 일반 쓰기 도구에서 접근 차단, 외부 지출 한도는 에이전트가 자의로 상향 불가, /panic은 supervisor가 에이전트 핸들링 전에 프로세스 트리를 종료. 그리고 161일 기록된 에피소드 중 운영자 셧다운에 저항한 사례가 없었다는 것 — 자기수정 에이전트의 안전성 논의에서 가장 부족했던 실증 데이터임.

8. 필자 관점. 자동화 파이프라인도 같은 구조로 가져갈 수 있음. 파이프라인 스크립트 자체를 git 관리하고, 변경은 게이트를 통과한 커밋으로만, 지출 한도는 코드 밖 설정으로 두는 것. 필자의 마이그레이션 작업도 "git 명령 금지" 제약이 있듯이 변경 권한 분리가 핵심인데 이 논문이 그 원칙을 시스템으로 완성한 셈임.

9. 문제제기. 단일 에이전트 단일 운영자 사례라 일반화에 한계가 있음. 110K 달러 규모 예산이 전제라 개인·소규모 팀이 그대로 따긴 어려움. 그리고 리뷰어가 같은 모델 계열이라는 순환 가능성은 frozen seed 평가로만 부분 완화됨.

10. 남는 결론. 자기진화 에이전트의 지속 가능성은 진화 능력이 아니라 커밋 게이트, 지출 한도, 권한 분리라는 지루한 안전 설계에서 나옴. 화려한 재귀적 개선보다 감사 가능한 변경 이력이 시스템을 오래 살려둔다는 게 161일이 남긴 교훈임.
