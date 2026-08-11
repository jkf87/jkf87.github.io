---
title: "Ouroboros: A Self-Developing Frontier Coding Agent with Reviewed Core Evolution"
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
github_url: https://github.com/razzant/ouroboros
authors:
  - razzant
---

Ouroboros는 에이전트 하네스의 도구, 프롬프트, 컨텍스트 조립, 코어 구현체를 버전 관리 대상으로 두고, reviewed commit을 통해 지속적으로 개선하는 코딩 에이전트 시스템입니다. Terminal-Bench 2.1에서 86.74%, OSWorld-Verified에서 90.69%를 기록했으며, 161일간 7개 채널에서 운영된 실사용 실험(Hope)을 포함합니다.

논문: [arXiv:2608.08311](https://arxiv.org/abs/2608.08311)
코드: [github.com/razzant/ouroboros](https://github.com/razzant/ouroboros)

## 시스템 구조

Ouroboros는 launcher/supervisor 경계와 mutable agent repository로 구성됩니다. Launcher는 시작, 프로세스 감독, 릴리스 부트스트래핑, panic-stop을 담당합니다. Repository는 태스크 루프, 도구, 프롬프트, 메모리 projection, 리뷰 로직, 벤치마크 어댑터, 사용자 인터페이스를 포함합니다.

![Ouroboros 아키텍처](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/fig-1-p4.png)
*그림 1. Ouroboros 아키텍처.*

### 진화 모드

두 가지 핵심 진화 모드가 있습니다:

1. **재귀적 자유 진화**: 개선 자체를 태스크로 스케줄. 시스템 검토 후 변경을 선택·구현하고, 리뷰 통과 시 커밋. 완료 후 다음 진화 주기를 스케줄하여 연속적인 reviewed update 시퀀스를 생성.

2. **경험 기반 핵심 진화**: 일반 작업 수행 중 발견되는 버그, 비효율적 컨텍스트 구성, 도구 경로 문제를 내구성 있는 에러 클래스로 기록. 동일한 reviewed commit 게이트를 통해 수정.

### 커밋 파이프라인

세 가지 런타임 모드(light/advanced/pro)가 저장소 편집 권한을 제어합니다. 커밋 경로는 deterministic preflight, diff fingerprint, reviewer evidence 수집, fingerprint 재확인 순으로 진행됩니다. diff-review 패널은 모든 컨텍스트 모드에서 블로킹입니다.

![서브에이전트 패치 통합](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/fig-2-p4.png)
*그림 2. 서브에이전트 패치 통합 프로토콜.*

## 벤치마크 결과

| 벤치마크 | 점수 | 모델 | 비고 |
|----------|------|------|------|
| Terminal-Bench 2.1 | 86.74% (386/445) | Opus 5 | trajectory audit 후, 이전 SOTA 83.8% |
| OSWorld-Verified | 90.69% (327.39/361) | Opus 5 | 이전 SOTA 90.19% 초과 |
| CL-Bench | 0.2301 | Sonnet 4.6 | 5-rollout, normalized reward |
| SWE-bench Pro | 58.2% | Opus 5 | Codex 59.4%와 통계적 동등 (p=0.40) |
| GAIA | 78.2% | Sonnet 5 | Claude Code 78.8%와 동등 |

Terminal-Bench 2.1에서 trajectory audit을 통해 1개 shortcut trial을 식별하고 제외했습니다. 445 trial 기준 이항 표준오차는 약 ±1.7%로, 직전 최고(Claude Code + Fable 5, 83.8%)를 약 2 표준편차 차이로 상회합니다.

![태스크 트리](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/fig-3-p5.png)
*그림 3. 라이브 세션의 태스크 트리.*

![결과 표](/images/2026-08-11-ouroboros-self-developing-frontier-coding-agent/table-2-p6.png)
*표 2. 벤치마크 결과 요약.*

## Hope: 161일 실사용 실험

2026년 2월부터 7개 상호작용 채널(웹 채팅, 음성, Telegram, Discord, Twitter/X, 웹사이트 댓글, 이메일)에서 하나의 Ouroboros 에이전트를 지속 운영했습니다.

- 운영 기간: 161일 (2026년 8월 6일 기준)
- 모델 지출: $110.6K
- 처리 토큰: 79.7B
- 코드 라인: 175,755
- 메모리 아티팩트: 227MB

사용자의 제안과 비판은 advisory로 처리되며, 에이전트가 변경 추진 여부를 결정합니다. 두 가지 진화 사례가 있습니다:

1. 중복 메시지 문제를 소셜 피드백으로 발견 → verbatim-duplicate guard 추가
2. deep self-review의 context overflow를 자가 관측 → import-graph centrality 기반 context atlas로 교체

## 운영 안전 설계

자기 코드와 모델 API를 변경할 수 있는 에이전트는 안전이 핵심 설계 제약입니다. 주요 장치:

- Constitution: untruncated path로 로드, 리뷰 컨텍스트에 포함
- Governance 파일 보호: 일반 쓰기 도구에서 접근 불가
- Diff fingerprint: 리뷰 전후 동일성 확인
- 외부 지출 한도: 에이전트가 자의로 상향 불가
- /panic: supervisor가 agent 핸들링 전 프로세스 트리 종료
- 기록된 에피소드 중 operator shutdown에 저항한 사례 없음

## 관련 연구와의 위치

Ouroboros는 Darwin Gödel Machine, Meta-Harness, Live-SWE-agent와 같은 자가진화 시스템 계열에 속합니다. 차이점은 deployed, version-controlled implementation에서 변경이 auditable commit gate를 거친다는 점입니다. 벤치마크 캠페인은 frozen seed로 평가하고, Hope는 별도 라인에서 live evolution을 유지하여 재현 가능한 평가와 진화를 분리합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
