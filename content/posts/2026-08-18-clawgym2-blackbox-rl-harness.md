---
title: "ClawGym II: OpenClaw·Claude Code 같은 블랙박스 하네스 너머로 RL 학습시키기"
date: 2026-08-18
tags:
  - agent
  - LLM-agent
  - harness
  - reinforcement-learning
  - RL
  - loop
  - coding-agent
  - OpenClaw
source: arxiv
source_url: https://arxiv.org/abs/2608.16798
authors:
  - conanssam
draft: false
---

arXiv:2608.16798 (2026-08-17, Huatong Song 외 다수) 정리했습니다. 핵심은 이겁니다. OpenClaw나 Claude Code처럼 <span style="background-color: #fff59d"><strong>내부가 안 보이는 상용 하네스를 통째로 RL 학습 파이프라인에 올리고</strong></span>, Qwen3-30A3B의 ClawGym-Bench Pass@1을 하네스별로 <span style="background-color: #fff59d"><strong>+9.98 / +14.81포인트</strong></span> 올렸다는 것.

![Figure 1. 블랙박스 RL 프레임워크 개요](/images/2026-08-18-clawgym2-blackbox-rl-harness/fig-1-p6.png)

## 문제: 하네스는 강한데 학습이 안 따라간다

Claude Code, Codex, OpenClaw 같은 프로덕션 하네스는 프롬프트, 도구 인터페이스, 컨텍스트 관리, 재시도 로직을 하나의 런타임으로 묶어서 롱호라이즌 과제 성능을 크게 올립니다.

근데 이 하네스들을 RL 학습에 쓰는 건 어려웠습니다.

- 하네스가 블랙박스라서 안에서 어떤 호출이 일어나는지 정리가 안 됩니다
- 롱호라이즌 과제는 상태ful 환경이 필요한데, 대규모 동시 롤아웃에 인프라가 버티질 못합니다
- 중간에 한 번 실패하면 트레이닝 트레이지토리 전체가 날아갑니다
- 호출 로그가 잘려 있고(forked, fragmented) 중복도 많아서 그냥 독립 학습시키면 공유 히스토리를 반복 학습하게 됩니다

이 논문의 목표는 하나입니다. <span style="background-color: #fff59d"><strong>하네스 내부를 안 고치고, 겉에서 돌리는 RL로 안정적으로 에이전트를 최적화하기</strong></span>.

## 프레임워크: 샌드박스 + 서빙 프록시 + prefix tree

구조는 세 층으로 나뉩니다.

**1. 샌드박스 실행 인프라.** 태스크 환경과 하네스를 <span style="background-color: #fff59d"><strong>임시 샌드박스에 격리</strong></span>해서 대규모 동시 롤아웃을 돌립니다. 롱호라이즌 과제에서 실패가 누적돼도 전체 배치가 무너지지 않게 하는 게 목적입니다.

**2. 서빙 프록시.** 모델 호출 경계에 프록시를 두고, 하네스가 모델을 부를 때마다 <span style="background-color: #fff59d"><strong>(입력, 출력) 쌍을 캡처</strong></span>합니다. 하네스 코드를 안 열어도 학습에 필요한 기록이 모델 쪽에서 확보됩니다.

**3. prefix tree 재구성.** 캡처된 호출들은 잘려 있고 갈라져 있고 중복됩니다. 이걸 <span style="background-color: #fff59d"><strong>롤아웃 단위 prefix tree로 조립해서 공유 히스토리 구조를 복원</strong></span>합니다. 그 다음 PPO(critic 기반)과 GRPO(critic-free)가 이 트리 구조에서 최적화되도록 고쳤습니다. 중복 학습 없이 멀티턴 구조를 보존하는 게 요점입니다.

여기에 <span style="background-color: #fff59d"><strong>학습-추론 일관성(training–inference consistency)</strong></span>을 유지합니다. 학습할 때 쓰는 컨텍스트 구성과 실제 하네스 추론 시점의 그것이 어긋나지 않게 한다는 뜻입니다.

## mix-harness 학습: 하네스 여러 개를 한 모델에

프레임워크의 마지막 조각은 mix-harness training입니다. 하나의 모델을 <span style="background-color: #fff59d"><strong>OpenClaw와 Claude Code라는 이질적인 하네스로 동시에(joint) 최적화</strong></span>합니다.

![Figure 4. 단일 하네스 vs mix-harness 학습 비교](/images/2026-08-18-clawgym2-blackbox-rl-harness/fig-4-p13.png)

결과부터 말하면, <span style="background-color: #fff59d"><strong>mix-harness로 학습한 모델이 단일 하네스로만 학습한 모델과 맞먹거나 더 좋았습니다</strong></span>. 블랙박스 RL 파이프라인이 하네스 종류를 가리지 않는다는 뜻이라, 실무적으로는 새 하네스가 나와도 같은 파이프라인에 붙일 수 있다는 얘기입니다.

## 수치: 무엇이 얼마나 올랐나

Qwen3-30A3B를 시작 모델로 잡고, OpenClaw 경로로는 ClawII-OC-30A3B, Claude Code 경로로는 ClawII-CC-30A3B를 학습했습니다.

| 모델 | ClawGym-Bench Pass@1 | PinchBench Pass@1 |
|---|---|---|
| Qwen3-30A3B (시작) | 기준선 | 기준선 |
| ClawII-OC-30A3B (OpenClaw RL) | +9.98p | +11.71p |
| ClawII-CC-30A3B (Claude Code RL) | +14.81p | +17.28p |

![Table 1. ClawGym-Bench / PinchBench 성능 비교](/images/2026-08-18-clawgym2-blackbox-rl-harness/table-1-p11.png)

몇 가지 포인트입니다.

- Claude Code 경로가 더 크게 올랐습니다. 저자들은 <span style="background-color: #fff59d"><strong>하네스가 성숙할수록 학습 시그널이 커지는</strong></span> 쪽으로 읽었습니다
- <span style="background-color: #fff59d"><strong>최적화 200–400 스텝 동안 학습이 안정적으로 유지</strong></span>됐습니다. 긴 롱호라이즌 RL에서 이건 그 자체로 결과입니다
- <span style="background-color: #fff59d"><strong>JobBench, OfficeQA 같은 더 어려운 과제에서도 일관된 개선</strong></span>이 있었습니다
- 평가는 Pass@1 기준이고, <span style="background-color: #fff59d"><strong>코드 검증 + 루브릭 판정을 0.7 / 0.3 가중합하는 하이브리드 프로토콜</strong></span>입니다

![Figure 2. OpenClaw 롤아웃 하네스에서의 PPO/GRPO 학습 곡선](/images/2026-08-18-clawgym2-blackbox-rl-harness/fig-2-p12.png)

![Figure 3. Claude Code 롤아웃 하네스에서의 PPO/GRPO 학습 곡선](/images/2026-08-18-clawgym2-blackbox-rl-harness/fig-3-p12.png)

## 내 해석: 어디에 쓸 수 있나

원문 근거와 제 해석을 구분해서 적습니다.

- (원문) 하네스 내부를 수정하지 않고도, 모델 호출 경계의 프록시 기록 + prefix tree 재구성만으로 PPO/GRPO 학습이 됩니다
- (원문) 이질적 하네스를 하나의 학습 루프에 묶는 mix-harness가 단일 하네스 학습보다 뒤지지 않습니다
- (해석) 하네스를 자체 구축하지 않는 팀에게는, <span style="background-color: #fff59d"><strong>이미 검증된 상용/오픈소스 하네스를 그대로 학습 환경으로 쓰는 길이 열렸다</strong></span>는 게 실질적 의미입니다
- (해석) prefix tree 재구성은 에이전트 RL에서 반복되는 "로그를 멀티턴 트레이지토리로 어떻게 맞추느냐" 문제의 깔끔한 답 중 하나로 보입니다. 트레이스 기반 디버깅에도 같은 구조가 재사용 가능할 것 같습니다
- (주의) 학습 인프라가 필요합니다. <span style="background-color: #fff59d"><strong>샌드박스 대규모 동시 롤아웃 + 서빙 프록시 + 트리 기반 최적화까지 갖추는 전제 조건</strong></span>이 있어서, 개인이 바로 돌려볼 규모는 아닙니다

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: [ClawGym II: Exploring Black-Box RL on Agent Harness (arXiv:2608.16798)](https://arxiv.org/abs/2608.16798)
- 벤치마크: ClawGym, ClawGym-Bench, PinchBench, JobBench, OfficeQA
- 기반 모델: Qwen3-30A3B
