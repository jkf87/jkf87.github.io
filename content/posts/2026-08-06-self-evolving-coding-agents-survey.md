---
title: 코딩 에이전트가 스스로 진화한다 — 5가지 진화 통로와 실행 가능한 피드백
date: 2026-08-06
tags:
  - agent
  - coding-agent
  - self-evolution
  - LLM
  - harness
  - survey
  - software-engineering
  - memory
  - skill
  - tool-use
source: arxiv
source_url: https://arxiv.org/abs/2608.03392
github_url: https://github.com/zhouhao1024/Awesome-Self-Evolving-Coding-Agents
---

SWE-bench에서 30%를 맞는 코딩 에이전트가 있습니다. 다음 날 같은 에이전트가 비슷한 이슈에서 같은 파일을 잘못 고칩니다. 정적 에이전트의 한계입니다. Nanjing University of Science and Technology의 2026년 8월 설문은 이 문제를 "자기 진화하는 코딩 에이전트(Self-Evolving Coding Agents)"라는 프레임으로 정리했습니다.

## 왜 코딩 에이전트인가

소프트웨어 엔지니어링은 자기 진화가 가장 잘 작동하는 환경입니다. 일반 에이전트 환경과 달리 피드백이 실행 가능합니다. 테스트, 컴파일러, 런타임, CI 로그가 "맞다/틀리다"를 확정해 줍니다. 이 피드백을 다음 태스크의 개선 신호로 쓸 수 있습니다.

## 객체 중심 분류법 — 무엇이 진화하는가

논문의 핵심 기여는 진화 대상을 5가지로 나눈 것입니다.

### 1. 프레임워크 진화

에이전트 하네스 코드 자체를 수정합니다. Self-SWE-Agent는 자신의 구현을 수정하고 검증하고, CodingAgentEvo는 코딩 에이전트 변형을 유지하며 진화시킵니다. 프레임워크가 모든 후속 행동에 영향을 주기 때문에 위험도가 가장 높습니다.

### 2. 메모리 진화

SWE-Exp는 이슈 해결 궤적(성공/실패 모두)을 경험 은행에 저장합니다. 리포지토리 메모리는 커밋 히스토리와 함수 변경 이력을 축적합니다. EvoRepair는 취약점 수리 경험을 도메인 특화 메모리로 관리합니다.

### 3. 스킬/도구 진화

CODESKILL은 코딩 궤적에서 태스크 수준 스킬과 이벤트 구동 스킬을 추출합니다. gskill은 리포지토리별 아키텍처, 관례, 테스트 절차를 설명하는 스킬 문서를 자동 학습합니다. Socratic-SWE는 해결 궤적에서 Agent Skill Registry를 증류하고, 이것이 다음 태스크 커리큘럼을 만드는 닫힌 루프를 형성합니다.

### 4. 모델 진화

Self-Play SWE-RL은 실제 리포지토리에 버그를 만들고 수리하면서 솔버를 개선합니다. Agent-RLVR은 궤적과 환경 보상으로 정책을 업데이트합니다. CURE와 ZeroCoder는 코더와 테스터를 함께 훈련합니다. 일반 포스트트레이닝과의 경계는 학습 신호가 에이전트 자신의 코딩 시도에서 닫혀 있느냐입니다.

### 5. 워크플로우/토폴로지 진화

SEMAG는 태스크 난이도에 따라 계획·코딩·디버깅 구조를 바꿉니다. EvoMAC은 멀티에이전트 네트워크의 연결을 업데이트합니다.

![](/images/2026-08-06-self-evolving-coding-agents-survey/fig-1-p2.png)

그림 1. 자기 진화하는 코딩 에이전트의 전체 구조. 출처: Zhou et al., 2026.

## 진화의 시점과 증거

세 가지 시점이 있습니다. 태스크 수행 중(online), 태스크 완료 후(post-task), 스테이지별(stage-wise). 증거는 결과(테스트 통과), 환경(컴파일러/런타임), 궤적 파생(액션 패턴) 세 출처입니다.

![](/images/2026-08-06-self-evolving-coding-agents-survey/fig-2-p6.png)

그림 2. 진화 객체별 분류 체계. 출처: Zhou et al., 2026.

## 과제

피드백 신뢰성(통과하는 테스트가 정답을 보장하지 않음), 벤치마크 오버핏, 안전, 비용, 유지보수성이 미해결 문제입니다.

![](/images/2026-08-06-self-evolving-coding-agents-survey/table-2-p6.png)

표 2. 대표 시스템의 분류 매핑. 출처: Zhou et al., 2026.

## 결론

코딩 에이전트 자기진화는 소프트웨어 엔지니어링의 실행 가능한 피드백을 영구적인 개선 신호로 바꾸는 연구 방향입니다. 5가지 통로(프레임워크, 메모리, 스킬, 모델, 워크플로우)가 각각 발전하고 있고, 각각의 실패 모드가 있습니다. 논문의 GitHub 논문 목록은 이 방향의 연구를 시작할 때 유용한 출발점입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
