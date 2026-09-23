---
title: "30분짜리 작업의 중간에 길을 잃는 에이전트 — LongHorizon-Harness가 실행 구조를 바꾼 방식"
date: 2026-08-05
tags:
  - agent
  - harness
  - LLM
  - long-horizon
  - task-state
  - MEA-loop
  - automation
  - tool-use
  - computer-use
  - OpenClaw
draft: true
refactor_hub: harness-self-improve-06
refactor_status: queued
---

에이전트가 긴 작업을 시작하고 중간에 길을 잃는 경험은 흔함. METR 보고서가 작업 호라이즌이 7개월마다 두 배로 늘어난다고 하지만, 호라이즌이 길어진다고 끝까지 안정 실행되는 건 별개 문제임. Alibaba DreamX 팀의 진단은 기존 하네스가 task execution과 task state management를 같은 컨텍스트에서 처리한다는 것. 실행 히스토리가 길어지면 상태 추적이 무너지고 에이전트의 자기 완료 주장이 검증 없이 state로 받아들여짐.

1. 해법의 핵심은 Manage-Execute-Audit 루프로 역할을 분리하는 것임. 세 역할이 라운드별로 돌아감. 구조 자체는 단순한데 분리의 원칙이 전부임.

![MEA 루프](/images/2026-08-05-longhorizon-harness-mea-loop-long-horizon-agents/mea-overview.png)

2. Manager는 task state를 유지하며 다음 서브태스크를 정함. 환경에는 직접 손을 안 대고 audit report만 봄. Executor는 fresh context에서 서브태스크만 수행함. 이전 실행 히스토리는 받지 않고 목표와 수락 기준이라는 계약만 받음. Claude Code, Codex, OpenClaw 같은 기존 하네스를 AgentAdapter로 그대로 연결함.

3. Auditor가 이 설계의 이빨임. 실행이 끝난 환경을 읽기 전용으로 검사함. 실행기의 보고를 믿지 않고 파일, 메타데이터, 빌드 결과, 스크린샷으로 환경의 실제 상태를 검증함. 검증된 fact만 다음 라운드로 넘어가고 실행 히스토리는 버려짐.

4. 결과 숫자. WeaveBench(장기 실행 과제 종합 벤치마크)에서 Qwen 3.7-Plus가 51.8%→80.7%. Terminal-Bench 2.1(실제 터미널에서 시스템 과제를 수행시켜 채점하는 벤치마크)에서 69.7%→77.2%. OSWorld 2.0(실제 컴퓨터 화면에서 OS 과제를 수행시키는 벤치마크)에서 2.8%→8.3%로 binary completion이 3배 가까이 늘었음. Claude Opus 4.7을 쓰면 OSWorld 서브셋에서 20.6%→35.3%임. 약한 모델이든 강한 모델이든 하네스 개선이 일관되게 더해짐.

![벤치마크 결과](/images/2026-08-05-longhorizon-harness-mea-loop-long-horizon-agents/benchmark-figure.png)

5. 제일 극적인 건 시스템 관리 카테고리임. Terminal-Bench 2.1에서 0.593→0.889로 급등함. installation이나 service configuration 같은 상태ful 작업에서 audit이 "대충 끝낸 척"을 정확히 잡아냈다는 뜻임. 긴 작업 실패의 상당수가 실제로는 미완료인데 완료로 보고되는 케이스라는 것과 맞물림.

6. 비용 구조도 공개돼서 실무 계산이 가능함. Manager는 전체 토큰의 2~8%만 씀. 상태 관리 오버헤드가 거의 없다는 뜻임. Auditor가 19~38%를 차지해서 독립 검증이 주요 추가 비용임. 근데 모델이 강할수록 전체 토큰이 줄어듦. Opus 4.7은 OSWorld에서 16.5M→11.1M로 감소함. 강한 모델은 audit-replan 라운드가 적게 필요해서임.

7. 적용 범위의 경계도 명확함. 환경 상태가 파일, 바이너리, 메타데이터로 검증 가능하면 효과가 큼. 문서 편집, 빌드, 시스템 관리가 대표적임. 반면 숨겨진 성능 임계값이나 비디오 시각 정밀도가 핵심인 작업에선 한계가 있고 MTEB(텍스트 임베딩 모델 성능 벤치마크), data-science, video-processing 태그에선 오히려 하락이 있었음.

8. 하네스가 모델을 넘는 숫자 하나. Qwen 3.7-Plus + LH-Harness의 게임 태스크 점수 0.733이 Claude Opus 4.7 + 기본 Claude Code의 0.680보다 높음. 에이전트 능력이 모델만의 속성이 아니라 model-harness 시스템의 속성이라는 증거임.

9. 실무 채점. 이 구조는 우리 자동화 파이프라인에 바로 얹을 수 있음. 첫째, 실행 에이전트는 서브태스크 단위로 fresh context로 돌릴 것. 둘째, 완료 판정은 에이전트의 보고가 아니라 독립 검사(파일 존재, 빌드 결과, 상태 확인)로 할 것. 셋째, 검증된 사실만 상태로 남기고 실행 로그는 버릴 것. 이 세 원칙이 MEA의 축소판임.

10. 특히 audit 비용 19~38%는 예산 설계의 기준점으로 쓸 만함. 검증을 안 넣어서 실패한 작업을 재돌리는 비용과 검증을 넣는 비용을 비교하면, 긴 작업일수록 audit이 이득이라는 게 이 논문의 암시임.

11. 한계. 검증 가능한 환경 상태에 최적화돼서 주관적 품질 기준이 섞인 작업엔 그대로 못 옮김. 그리고 Auditor가 환경을 읽는 인터페이스가 도메인마다 필요해서 새 도메인 진입 비용이 있음.

12. 그래도 방향은 명확함. 긴 호라이즌의 문제는 모델 능력이 아니라 실행 구조에서 온다는 진단. 실행과 검증과 상태 관리를 한 컨텍스트에 뭉쳐둔 구조가 병목이었고, 분리하는 것만으로 같은 모델이 등급 하나씩 올라갔음.

원문: [arXiv:2608.01964](https://arxiv.org/abs/2608.01964)
