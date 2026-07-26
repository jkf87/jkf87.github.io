---
title: "OpenForge RL: 하네스를 입은 에이전트를 그대로 훈련시키는 오픈 프레임워크"
date: 2026-07-27
draft: false
tags:
  - agent
  - RL
  - harness
  - open-source
  - LLM
---

> Columbia University · Dartmouth College · Microsoft Research (2026년 7월)

현대 AI 에이전트는 Claude Code, Codex, OpenClaw 같은 **하네스(harness)** 없이는 제 역량을 발휘하지 못한다. 하네스가 멀티턴 추론·도구 사용·컨텍스트 관리를 담당하기 때문이다. 그런데 이 하네스가 에이전트 훈련, 특히 강화학습(RL) 기반 end-to-end 훈련을 극도로 어렵게 만든다는 사실은 잘 알려져 있지 않다. OpenForge RL은 이 문제를 정면으로 돌파한 최초의 오픈소스 프레임워크다.

![](/images/2026-07-27-openforge-rl-harness-native-agent-training/fig-1-p1.png)

*Figure 1: OpenForge RL은 any harness × any environment 조합을 표준 RL 코드베이스(예: veRL)와 연결한다. 훈련–배포 불일치(train–deploy mismatch)가 없다.*

## 문제: 하네스는 강력하지만 훈련하기는 어렵다

에이전트가 실제로 사용되는 환경에서 하네스는 단순한 API 래퍼가 아니다. 서브에이전트를 spawn하고, MCP 서버와 통신하며, 브라우저나 데스크톱 GUI를 제어하는 등 **상태를 가진 다중 프로세스 시스템**이다.

기존 오픈소스 RL 프레임워크(veRL, Slime, OpenRLHF 등)는 이런 복잡한 롤아웃을 처리하지 못한다. 단일 모델 호출이나 간단한 코드 실행을 가정하기 때문이다. 그 결과, 연구자들은 훈련용으로 하네스를 단순화해서 재구현해야 했고, 이는 **훈련–배포 불일치**라는 심각한 문제를 낳았다. 모델은 훈련 시의 단순화된 환경에서는 잘 동작하지만, 실제 배포 환경의 복잡한 하네스에서는 성능이 떨어지는 것이다.

## 핵심 아이디어: 프록시 + 오케스트레이터

OpenForge RL의 해법은 놀랍도록 우아하다. 두 개의 가벼운 컴포넌트로 문제를 해결한다.

![](/images/2026-07-27-openforge-rl-harness-native-agent-training/fig-2-p4.png)

*Figure 2: 오케스트레이터가 원격 샌드박스를 spawn하고, 프록시가 하네스의 LLM 호출을 가로채서 RL 프레임워크의 추론 엔진으로 라우팅한다.*

### 1. 경량 프록시

하네스가 LLM에 보내는 모든 호출을 가로채는 프록시를 둔다. 이 프록시는:
- 하네스가 자체적인 추론 로직을 그대로 실행하도록 놔둔다
- prompt–response 쌍을 기록하여 표준 RL 훈련 샘플로 변환한다
- 훈련 프레임워크(예: veRL)의 추론 엔진과 호환된다

이 설계의 핵심은 **훈련과 추론의 분리**다. 하네스의 내부 로직을 수정할 필요 없이, 어떤 하네스든 그대로 사용할 수 있다.

### 2. Kubernetes 오케스트레이터

각 롤아웃을 자체 컨테이너에서 실행한다. 이는:
- 훈련 노드와 롤아웃 환경을 분리하여 스케일링 문제 해결
- 클라우드 프로바이더(Azure 등)에서 탄력적으로 확장
- 서로 다른 환경(도구 사용, 브라우저, 데스크톱)을 동시에 지원

## 결과: 작은 모델로 큰 성과

OpenForge RL로 훈련된 모델은 두 가지 영역에서 인상적인 성과를 보여준다.

### 도구/클로 에이전트 (OpenForge-Claw, 30B-A3B MoE)

| 벤치마크 | 점수 |
|----------|------|
| ClawEval (pass³) | 31.7 |
| ClawEval (pass@3) | 55.9 |
| QwenClawBench | 33.7 |
| MCPAtlas | 28.1 |

### GUI 에이전트 (OpenForge-GUI, 8B)

| 벤치마크 | 점수 |
|----------|------|
| OSWorld-Verified | 37.7 |
| Online-Mind2Web | 63.0 |
| WebVoyager | 72.3 |

GUI 영역에서는 **몇 배 더 큰 모델과 맞먹거나 능가하는 성능**을 달성했다. 사용한 훈련 데이터는 수백~수천 개의 태스크에 불과하다.

## 하네스 선택이 에이전트 행동을 결정한다

OpenForge RL의 가장 흥미로운 발견은 **어떤 하네스로 훈련하느냐가 에이전트의 행동 패턴을 크게 바꾼다**는 점이다.

![](/images/2026-07-27-openforge-rl-harness-native-agent-training/fig-5-p10.png)

*Figure 5: SFT와 SFT+RL 비교. RL이 도구 사용 분포와 자기 검증 행동을 어떻게 변화시키는지 보여준다.*

연구진은 ZeroClaw, OpenClaw, Codex 세 가지 하네스로 동일한 모델을 훈련하고 비교했다:

- **더 단순하고 정렬된 하네스일수록 학습하기 쉽다** — 복잡한 하네스는 탐색 공간을 넓혀 RL 수렴을 어렵게 만든다
- **RL은 에이전트의 신뢰성을 전반적으로 향상시킨다** — 자기 검증(self-verification), 도구 커버리지, 다단계 계획 완료율이 모두 개선된다
- **하지만 에러 복구(error recovery)는 여전히 약하다** — RL로 학습하기 가장 어려운 능력 중 하나

이 발견은 실용적인 시사점을 갖는다. 하네스를 설계할 때 단순성과 학습 용이성을 고려해야 하며, 에이전트 훈련에서 에러 복구 능력을 별도로 타겟팅해야 한다.

![](/images/2026-07-27-openforge-rl-harness-native-agent-training/fig-3-p5.png)

*Figure 3: 데이터 합성 파이프라인. 후보 명령 생성 → 품질 필터링 → 환경 구축 → 테스트 → 정제 과정을 거친다.*

## 왜 중요한가

OpenForge RL이 해결하는 문제는 단순한 엔지니어링 과제가 아니다. **에이전트가 실제 동작하는 환경에서 훈련할 수 있느냐 없느냐**의 문제다.

지금까지는 클로즈드 소스 시스템(GPT-4 + Codex, Claude + Claude Code)만이 실제 하네스로 훈련된 모델을 보유하고 있었다. 오픈소스 연구자는 단순화된 모의 환경에서만 훈련할 수 있었고, 이 격차는 계속 벌어지고 있었다.

OpenForge RL은 이 격차를 좁히는 인프라를 제공한다. 코드, 데이터, 모델을 모두 공개하겠다는 약속도 중요하다. 이제 누구나 자신이 사용하는 하네스(OpenClaw, Claude Code, Codex 등)에서 에이전트를 end-to-end로 훈련하고 연구할 수 있다.

## 데이터 합성 파이프라인

도구 사용 및 GUI 영역은 코딩과 달리 훈련 태스크가 풍부하지 않다. OpenForge RL은 이 문제를 해결하기 위해 자동 태스크 합성 파이프라인도 함께 제공한다:

1. 웹/X API에서 현실적인 시나리오를 기반으로 태스크 후보 생성
2. 중복 및 저품질 태스크 필터링
3. 실행 가능한 환경(Docker)과 검증 스크립트 자동 구축
4. 별도의 오픈 LLM/VLM으로 태스크 테스트
5. 결함 패치 및 정제

이 파이프라인은 CLI 태스크부터 GUI/컴퓨터 사용 태스크(Xvfb 가상 디스플레이 포함)까지 자연스럽게 확장된다.

## 더 실습해보고 싶은 분들께

에이전트 하네스, 자동화 루프, 그리고 실제 환경에서의 강화학습은 이제 막 시작된 분야입니다. 직접 실험하고 싶다면 다음 자료를 추천합니다:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』 — OpenClaw 기반 에이전트 자동화의 실전 활용 사례集
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」 — 에이전트 루프 설계와 강화학습 파이프라인의 실무 강의

---

**_paper_: [OpenForgeRL: Train Harness-native Agents in Any Environment](https://arxiv.org/abs/2607.21557) (arXiv:2607.21557, 2026년 7월)**
**_authors_: Xiao Yu, Baolin Peng, Ruize Xu, Hao Zou, Qianhui Wu, Hao Cheng, Wenlin Yao, Nikhil Singh, Zhou Yu, Jianfeng Gao**
**_affiliations_: Columbia University · Dartmouth College · Microsoft Research**
