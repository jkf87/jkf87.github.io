---
title: "LEGO-RL: 코딩 에이전트 하네스를 통째로 RL 훈련 루프에 올리는 방법"
date: 2026-08-27
tags:
  - agent
  - coding-agent
  - reinforcement-learning
  - harness
  - LLM
  - GSPO
  - SWE-bench
draft: false
description: "LEGO-RL은 OpenHands SDK·Claude Code·OpenCode 같은 코딩 에이전트 하네스를 내부 제어 흐름을 바꾸지 않고 정책경사 RL 훈련에 직접 연결하는 프레임워크다. Qwen3.5-35B-A3B를 GSPO로 훈련해 SWE-bench Verified에서 하네스별로 4~9.4%p 상승을 확인했다."
---

## 결론 먼저

LEGO-RL(arXiv 2608.17393)은 코딩 에이전트 하네스를 <span style="background-color: #fff59d"><strong>내부 제어 흐름을 거의 건드리지 않고 RL 훈련 루프에 직접 올리는</strong></span> 프레임워크입니다. 하네스 쪽 코드를 고쳐 훈련용으로 맞추는 기존 방식 대신, 훈련 엔진 쪽에서 하네스의 LLM 호출을 프록시로 가로채서 토큰 단위 정렬을 맞춥니다.

핵심 숫자부터 정리했습니다.

| 항목 | 값 |
| --- | --- |
| 훈련 대상 | Qwen3.5-35B-A3B (sparse MoE) |
| 알고리즘 | GSPO |
| OpenHands SDK | SWE-bench Verified 64.0% → 70.4% |
| Claude Code | 62.4% → 68.2% |
| OpenCode | 57.2% → 66.6% |
| 롤아웃-훈련 확률 상관 | 0.99 이상 유지 |
| 기준일 | 2026-08-27 기준, v1(2026-08-18 제출) |

같은 모델, 같은 알고리즘인데도 하네스마다 기본 성능과 훈련 이득이 다릅니다. <span style="background-color: #fff59d"><strong>하네스가 곧 훈련 환경이라는 걸 숫자로 보여주는 결과</strong></span>구요, OpenCode가 9.4%p로 가장 크게 올랐습니다.

## 문제: 하네스와 정책경사는 기본적으로 안 맞는다

코딩 에이전트 RL은 이제 실제 하네스 없이는 말이 안 됩니다. 툴 통합, 리포지토리 컨텍스트, 실행 피드백을 하네스가 전부 관리하거든요.

근데 하네스의 네이티브 실행 환경은 정책경사 훈련과 충돌합니다. 논문이 지적하는 충돌 지점은 두 가지입니다.

- 환경 크래시와 보상 해킹이 결과 보상 신호를 오염시킨다
- 훈련-추론 불일치가 롤아웃 행동과 정책 업데이트를 분리시킨다

특히 성가신 문제가 컴팩션이랑 재직렬화입니다. 하네스가 컨텍스트를 줄이려고 히스토리를 다시 쓰면, 훈련기가 계산한 로그확률과 실제 생성 스트림이 어긋납니다. <span style="background-color: #fff59d"><strong>컴팩션·재직렬화가 있어도 토큰 단위 정렬을 유지하는 게 이 논문의 첫 번째 기둥</strong></span>입니다.

## 세 가지 기둥

### in-process LLM 프록시

하네스 내부의 LLM 호출을 in-process 프록시로 가로채서 원시 생성 스트림을 캡처합니다. 트레이너 쪽에서 로그확률을 재계산하니까, 하네스가 히스토리를 다시 직렬화해도 정렬이 깨지지 않습니다. <span style="background-color: #fff59d"><strong>롤아웃-훈련 확률 상관 0.99 이상</strong></span>이 이 장치의 검증 결과입니다.

![](/images/2026-08-27-lego-rl-harness-native-rl-coding-agents/fig-1-p2.png)

전체 훈련 인프라 개요입니다. 원문 Figure 1.

### 샌드박스 오케스트레이션

확장 가능한 샌드박스 오케스트레이션으로 이미지 캐싱을 하고, 단계별 방어(stage-wise defenses)로 <span style="background-color: #fff59d"><strong>보상 해킹을 완화</strong></span>합니다. 코딩 에이전트 RL에서 보상 해킹은 테스트 통과만 요령껏 만드는 궤적 형태로 나오는데, 실행 단계마다 검증을 끼워넣는 구조입니다.

### 플러그인과 Live UI

검증·모니터링을 자동화하는 플러그인과 궤적을 세밀하게 들여다보는 Live UI가 붙습니다. <span style="background-color: #fff59d"><strong>훈련이 관찰 가능(observable)해야 디버깅이 된다</strong></span>는 관점인데, 에이전트 RL에서 이게 생각보다 큰 문제라 동의합니다.

![](/images/2026-08-27-lego-rl-harness-native-rl-coding-agents/fig-2-p7.png)

다섯 단계로 닫히는 운영 워크플로입니다. 원문 Figure 2.

## 기존 프레임워크와의 차이

| 프레임워크 계열 | 접근 | LEGO-RL과의 차이 |
| --- | --- | --- |
| 전통적 agentic RL | 훈련 엔진이 환경 루프를 소유 | 하네스가 루프를 소유하도록 유지 |
| 하네스 개조 방식 | 하네스 내부를 훈련용으로 수정 | 내부 제어 흐름 무수정 |
| 별도 롤아웃 스택 | 훈련용 경량 환경 재구현 | 네이티브 하네스 그대로 |

![](/images/2026-08-27-lego-rl-harness-native-rl-coding-agents/table-1-p3.png)

대표적 agentic RL 프레임워크 비교입니다. 원문 Table 1.

<span style="background-color: #fff59d"><strong>훈련 엔진이 관찰하는 건 LLM 요청-응답 쌍의 시퀀스뿐</strong></span>이라는 점이 전통적 agentic RL과의 구조적 차이입니다. 환경 루프 소유권이 훈련 엔진에서 하네스로 넘어갔을 때 생기는 새 문제 세트를 다루는 논문입니다.

## 하네스별 훈련 결과

![](/images/2026-08-27-lego-rl-harness-native-rl-coding-agents/fig-3-p9.png)

세 하네스에서의 훈련 곡선입니다. 원문 Figure 3.

![](/images/2026-08-27-lego-rl-harness-native-rl-coding-agents/table-2-p10.png)

SWE-bench Verified 최종 성능입니다. 원문 Table 2.

해석을 정리하면:

- 베이스 성능은 OpenHands SDK(64.0%) > Claude Code(62.4%) > OpenCode(57.2%)
- 훈련 후 격차는 줄어듦: 70.4% / 68.2% / 66.6%
- <span style="background-color: #fff59d"><strong>약한 하네스일수록 훈련 이득이 크다</strong></span>는 패턴

원문 근거와 제 해석을 구분하자면, 위 숫자는 전부 논문 보고값이구요, "약한 하네스일수록 이득이 크다"는 패턴 읽기는 세 점에서 나온 제 추정입니다.

## 내 해석: 왜 이 방향이 중요한가

하네스를 수정하지 않고 훈련한다는 건 실무적으로 큰 의미가 있습니다. 실제로 배포되는 하네스 그대로 훈련하니까 <span style="background-color: #fff59d"><strong>훈련된 행동이 배포 환경에서 그대로 이어진다</strong></span>는 점이 핵심입니다. 훈련용 모조 환경을 따로 만들면 거기서 생긴 실력이 실제 하네스로 옮겨가는지가 항상 의문이었거든요.

또 하나는 측정 가능성입니다. 확률 상관 0.99라는 숫자는 "롤아웃과 훈련이 같은 정책을 보고 있다"는 직접 증거라서, 컴팩션 있는 하네스에서 RL을 돌리는 사람들에게 실질적인 체크리스트가 됩니다.

한계도 적습니다. 세 하네스 전부 코딩 에이전트라는 점, 보상 해킹 방어의 단계별 설계가 특정 벤치마크에 과적합됐을 가능성은 원문에서도 완전히 배제하지 않습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### LEGO-RL이 정확히 뭔가요?

OpenHands SDK, Claude Code, OpenCode 같은 코딩 에이전트 하네스를 내부 수정 없이 정책경사 RL(GSPO) 훈련에 연결하는 프레임워크입니다. in-process LLM 프록시로 토큰 단위 정렬을 유지합니다.

### 성능 향상은 얼마나 되나요?

Qwen3.5-35B-A3B 기준 SWE-bench Verified에서 OpenHands SDK 64.0%→70.4%, Claude Code 62.4%→68.2%, OpenCode 57.2%→66.6%입니다(논문 보고값, 기준일 2026-08-27).

### 기존 agentic RL과 뭐가 다른가요?

기존 방식은 훈련 엔진이 환경 상호작용 루프를 소유합니다. LEGO-RL은 하네스가 루프를 소유하고 훈련 엔진은 LLM 요청-응답 시퀀스만 관찰합니다.

### 컨텍스트 컴팩션이 있어도 되나요?

네. 하네스가 컴팩션이나 재직렬화를 해도 트레이너 쪽 로그확률 재계산으로 정렬을 유지하며, 롤아웃-훈련 확률 상관이 0.99 이상이라고 보고합니다.

### 소스는 어디서 확인하나요?

원문: [arXiv:2608.17393](https://arxiv.org/abs/2608.17393), 프로젝트 페이지: [lego-rl.pages.dev](https://lego-rl.pages.dev)
