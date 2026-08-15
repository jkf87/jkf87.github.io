---
title: "ToolHazard: 에이전트 보안 테스트 환경을 자동 합성으로 키우는 프레임워크"
date: 2026-08-15
tags:
  - agent
  - security
  - prompt-injection
  - RL
  - alignment
  - benchmark
  - tool-use
  - LLM
  - evaluation
source: arxiv
source_url: https://arxiv.org/abs/2608.11878
paper_url: https://arxiv.org/abs/2608.11878
---

ToolHazard(arXiv:2608.11878) 정리했습니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>LLM 에이전트를 노리는 간접 프롬프트 인젝션 테스트 환경을 사람이 손으로 짜지 않고, 합성 파이프라인으로 계속 늘리는 프레임워크</strong></span>입니다.

기존 보안 벤치마크는 환경과 주입 위치를 사람이 미리 구현합니다. 도메인 하나 추가할 때마다 비용이 다시 들어서 확장이 안 됐구요, ToolHazard는 환경 코드·공격 지점·검증 함수까지 자동 생성으로 바꿨습니다.

핵심 수치부터 보시면 됩니다.

| 항목 | 값 |
| --- | --- |
| ToolHazard-Bench 규모 | <span style="background-color: #fff59d"><strong>환경 28개 · 태스크 87개 · 도구 512개</strong></span> |
| 태스크 평균 길이 | 15.56스텝 · 태스크당 후보 도구 18.75개 |
| 정렬 데이터 | 학습 환경 60개 · 유효 샘플 1,040개 (RL 329 / SFT 711) |
| 환경 1개 합성 비용 | <span style="background-color: #fff59d"><strong>$0.59</strong></span> |
| Qwen3-8B 정렬 후 | <span style="background-color: #fff59d"><strong>ASR 36.10% → 18.06% · BR 67.64% → 75.94%</strong></span> |

## 배경: 주입 위치를 손으로 지정하던 기존 벤치마크

에이전트 보안 연구의 병목은 환경 제작입니다. AgentDojo는 도메인 4개, ASB는 10개인데 전부 수작업 환경입니다. 주입 위치도 미리 정해 둬서, 새로운 공격 표면을 시험하려면 환경을 또 손으로 고쳐야 합니다.

LLM으로 도구 응답을 흉내 내는 시뮬레이션 방식도 있습니다. 근데 이쪽은 응답이 확률적이라 재현 가능한 평가·학습이 어렵습니다.

ToolHazard의 목표는 여기에 있습니다. 실행 가능한 상태 저장 환경을 합성하고, 주입 지점을 태스크 궤적에서 자동으로 찾고, 결과를 결정론적으로 검증하는 것.

위협 모델은 이렇게 정리됩니다.

- 공격자: 이메일 본문, 문서, DB 레코드, 도구 출력 같은 <span style="background-color: #fff59d"><strong>쓰기 가능한 환경 속성만 수정 가능</strong></span>
- 불가능: 사용자 쿼리, 시스템 프롬프트, 도구 구현, 모델 파라미터
- 성공 조건: 주입 지시가 에이전트 판단을 가로채서 의도하지 않은 도구 실행을 유발

브라우저 웹 에이전트와 웹페이지 단위 인젝션은 범위 밖이구요, API 기반 도구 사용 에이전트가 대상입니다.

## 구조: 환경 시뮬레이터 · 공격자 에이전트 · 사용자 시뮬레이터

![ToolHazard 프레임워크 개요](/images/toolhazard-scaling-adversarial-environments-2026-08-15/overview-framework.png)
*그림 1. ToolHazard 전체 파이프라인. 출처: 논문 Figure 1.*

모듈이 세 개입니다.

| 모듈 | 하는 일 |
| --- | --- |
| 환경 시뮬레이터 | 블루프린트 기획 → 실행 코드 생성 → 자동 검수로 상태 저장 환경 합성 |
| 공격자 에이전트 | 읽기/쓰기 경로 분석으로 주입 지점 발견, 페이로드 계획·실행 |
| 사용자 시뮬레이터 | 환경 상태에 발이 닿는 장기 태스크 생성 |

환경 시뮬레이터는 시드 태스크에서 상태 공간·제약 규칙·연산을 추론하고, OOP 클래스로 실행 코드를 만듭니다. 검수는 테스팅 에이전트·체킹 에이전트 이중 구조로 돌아가구요, 통과 못 한 환경은 버립니다. 이 단계 비용이 환경당 합성 비용의 대부분입니다.

공격자 에이전트의 주입 지점 발견이 기존 red-teaming과 다른 부분입니다. 기존 방식은 미리 정해 둔 위치에 페이로드를 넣습니다. ToolHazard는 <span style="background-color: #fff59d"><strong>어디가 뚫리는지를 환경 코드에서 직접 찾아냅니다</strong></span>.

1. 쓰기 가능한 텍스트 속성 식별 (자유 텍스트 필드만 후보)
2. 연산별 읽기/쓰기 의존성 그래프 분석
3. 읽기 경로와 쓰기 경로가 둘 다 있는 속성만 유효 공격점으로 채택

태스크 완수 여부는 최종 환경 상태에 대해 체크 함수를 실행해 계산합니다. 평가 시점에 LLM 심판이 없어서 결정론적이구요, <span style="background-color: #fff59d"><strong>사람 판정과 일치율은 95% 이상, 검수자 간 일치는 99% 이상</strong></span>입니다.

## 벤치마크 구성: ToolHazard-Bench 환경 규모

![ToolHazard-Bench 통계](/images/toolhazard-scaling-adversarial-environments-2026-08-15/bench-stats.png)
*그림 2. 벤치마크 분포 통계. 출처: 논문 Figure 2.*

87개 태스크에 도구가 512개 붙어 있습니다. 평균 실행 길이 15.56스텝, 태스크당 후보 도구 18.75개로, 기존 보안 벤치마크보다 워크플로 복잡도가 한 단계 높습니다.

| 벤치마크 | 상태 저장 | 도메인 수 | 스텝/태스크 | 주입 지점 |
| --- | --- | --- | --- | --- |
| AgentDojo | 있음 | 4 | 4.19 | 사전 정의 |
| ASB | 없음 | 10 | 2.96 | 사전 정의 |
| ToolHazard-Bench | 있음 | 28 | 15.56 | LLM 탐색 |

환경당 상태 속성 18.25개, 도구 18.28개로 AgentDojo(17.35 / 18.5)와 비슷한 밀도입니다. 합성 환경이 실제 벤치마크보다 성기지 않다는 검증이구요.

공격은 6가지 래퍼 전략으로 인스턴스화됩니다.

![여섯 가지 인젝션 전략](/images/toolhazard-scaling-adversarial-environments-2026-08-15/six-strategies.png)
*그림 3. 환경 측 인젝션 전략 6종. 출처: 논문 Figure 5.*

Basic Combined는 고전적인 "이전 지시 무시"류, Important-Template는 사용자 메시지인 척 위장, Multi-turn은 가짜 대화 턴으로 감싸는 방식입니다. Decision Hijacking과 Tool Selection, Reasoning Criteria가 새로 등장한 전략인데, <span style="background-color: #fff59d"><strong>구형 공격에 어느 정도 면역이 생긴 최신 모델도 이 쪽에는 무너집니다</strong></span>.

## 결과: 최신 모델도 환경 주입에 뚫립니다

GPT-5, GPT-4.1, Gemini-3.1-Pro, Gemini-2.5-Pro, DeepSeek-V3.2, Qwen3-8B/4B를 ReAct 프레임으로 돌렸습니다. ASR(공격 성공률)이 낮을수록 좋습니다.

| 모델 | Basic | Important | Multi-turn | Hijacking | Criteria | Tool Sel. |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5 | 1.18 | 51.49 | 33.43 | 44.82 | 44.96 | 59.14 |
| GPT-4.1 | 1.18 | 70.63 | 58.00 | 50.14 | 30.41 | 75.57 |
| Gemini-3.1-Pro | 3.53 | 23.06 | 24.19 | 36.28 | 63.20 | 32.56 |
| DeepSeek-V3.2 | 1.18 | 73.33 | 73.33 | 75.00 | 40.00 | 73.33 |

<span style="background-color: #fff59d"><strong>GPT-5는 전략 4개에서 ASR 40%를 넘깁니다</strong></span>. Gemini-3.1-Pro도 3개가 30% 초과구요. 고전적인 Basic Combined에는 다들 강한데, 새 전략 앞에서는 일관되게 무너집니다.

## 강한 모델일수록 공격에 취약한 구조

흥미로운 역상관이 하나 있습니다. DeepSeek-V3.2가 정상 태스크 수행률(BR)은 최고인데 공격에는 가장 취약합니다. Qwen3-4B는 지시 추종 능력이 약해서 오히려 공격 영향이 작구요.

논문의 해석: <span style="background-color: #fff59d"><strong>환경 지시를 충실히 따르는 능력 자체가, 악성 주입도 충실히 따르는 결과로 이어진다</strong></span>는 것입니다. 모델 세대가 올라갈수록 BR은 오르고 ASR은 내리긴 하는데, 그 개선만으로는 인젝션 방어에 부족합니다.

## 주입 타이밍과 배치가 성공률을 바꿉니다

![주입 타이밍과 배치의 영향](/images/toolhazard-scaling-adversarial-environments-2026-08-15/timing-placement.png)
*그림 4. 주입 시점·위치에 따른 ASR 변화. 출처: 논문 Figure 3.*

같은 페이로드라도 언제·어디에 들어가느냐로 ASR이 달라집니다.

- 타이밍: <span style="background-color: #fff59d"><strong>실행 초반에 읽히는 주입점일수록 ASR 상승</strong></span>
- 배치: 도구 응답의 마지막 필드에 넣을수록 ASR 상승

뒤는 위치 편향(position bias) 때문입니다. 에이전트가 관찰 끝자락 내용을 다음 행동 근거로 더 많이 쓰는 현상이구요, 방어 설계할 때 위치를 고려해야 한다는 근거가 됩니다.

## 출력 포맷: 자유 텍스트가 더 위험합니다

![도구 출력 포맷별 공격 성공률](/images/toolhazard-scaling-adversarial-environments-2026-08-15/output-format.png)
*그림 5. 출력 포맷에 따른 ASR. 출처: 논문 Figure 4.*

같은 환경에서 도구 출력만 자유 텍스트 ↔ JSON/YAML로 바꿔 비교했습니다. <span style="background-color: #fff59d"><strong>자유 텍스트 쪽 ASR이 크게 높습니다</strong></span>.

논문 추정은 이렇습니다. 자유 텍스트는 의미 경계가 없어서 주입 내용이 "실행 가능한 지시"로 섞여 들어가고, 구조화 포맷은 구문 경계가 부차적 격리 역할을 한다고요. 실무에서는 <span style="background-color: #fff59d"><strong>도구 출력을 구조화하고 엄격 파싱을 붙이는 것만으로도 실질 방어가 됩니다</strong></span>.

## 공격은 정상 작업 수행도 같이 깎습니다

인젝션은 안전 문제만 만드는 게 아닙니다. 공격받는 환경에서는 정상 태스크 수행률(BR)도 같이 떨어집니다.

| 공격 유형 | GPT-4.1 BR | Gemini-3.1-Pro BR |
| --- | --- | --- |
| 공격 없음 | 78.6 | 82.8 |
| Decision Hijacking | 52.5 | 80.0 |
| Multi-turn | 41.3 | 82.7 |

<span style="background-color: #fff59d"><strong>GPT-4.1은 Multi-turn에 BR이 절반까지 떨어집니다</strong></span>. Gemini-3.1-Pro는 BR을 거의 지키는 편이구요. 안전 위반과 능력 저하를 같이 봐야 한다는 게 논문의 지적입니다.

## 정렬 데이터 ToolHazard-Align: 보상 설계와 학습 설정

ToolHazard는 평가뿐 아니라 정렬 데이터 합성에도 씁니다. 학습 환경 60개(평가 28개와 분리)에서 환경-태스크 300쌍을 만들고, 공격 6종을 적용해 후보 1,800개를 생성, 필터링 후 1,040개가 남습니다. RL용 329개, SFT용 711개입니다.

보상은 트레이젝토리 단위로 정의됩니다.

```
R(τ) = R_task(τ) − R_injected(τ)
```

정상 태스크 완수에 보상, 주입 지시 이행에 벌점입니다. 거절만 하면 태스크 실패로 점수가 깎이는 구조라, <span style="background-color: #fff59d"><strong>최대 보상을 받으려면 공격을 무시하고 과제를 끝내야 합니다</strong></span>. 과잉 거부가 없었다는 것도 여기서 확인됩니다.

학습 설정은 이렇습니다.

| 항목 | 값 |
| --- | --- |
| 알고리즘 | GRPO (ROLL 프레임워크) |
| KL 정규화 계수 | 0.1 |
| 학습률 | 1.0×10⁻⁶ |
| 스텝당 태스크 / 롤아웃 | 64 / 8 |
| 최대 궤적 길이 | 32K 토큰 |

SFT는 LlamaFactory로 클린 환경 성공 궤적을 3에포크 학습합니다.

## 정렬 결과와 일반화

![정렬 성능 비교](/images/toolhazard-scaling-adversarial-environments-2026-08-15/align-results.png)
*그림 6. ToolHazard-Align 전후 성능. 출처: 논문 Table 4.*

| 모델 | TH-Bench BR↑ | TH-Bench ASR↓ | AgentDojo BR↑ | AgentDojo ASR↓ |
| --- | --- | --- | --- | --- |
| Qwen3-4B | 38.19 | 25.05 | 30.03 | 14.23 |
| Qwen3-4B + Align | 70.68 | 22.76 | 41.73 | 7.17 |
| Qwen3-8B | 67.64 | 36.10 | 43.05 | 29.16 |
| Qwen3-8B + Align | 75.94 | 18.06 | 52.08 | 18.34 |

Qwen3-8B는 ASR이 36.10%에서 18.06%로 절반 가까이 줄면서 BR도 오릅니다. <span style="background-color: #fff59d"><strong>AgentDojo(환경·도구 분포가 다른 독립 벤치마크)에서도 ASR 29.16% → 18.34%로 개선</strong></span>되는 걸 보면 벤치마크 암기가 아닙니다.

못 본 공격 전략에 대한 일반화 실험도 있습니다. 전략 3개로만 학습하고 나머지 3개로 평가했더니 ASR 26.92% · BR 73.31%로, 6개 전부 쓴 학습(25.45% / 74.59%)과 근접합니다. 래퍼별 암기를 넘어서 견고성 자체가 이전됐다는 근거입니다.

## 합성 비용

| 단위 | 비용 |
| --- | --- |
| 환경 1개 | $0.59 |
| 사용자 시나리오 1개 | $0.03 |
| 공격 인스턴스 1개 | $0.05 |

<span style="background-color: #fff59d"><strong>환경 1개당 $0.59 중 $0.46이 자동 검수</strong></span>입니다. 품질 관리가 파이프라인에서 가장 비싼 단계라는 뜻이구요, 그래도 도메인 확장이 씨드 데이터와 컴퓨트 추가로 가능하다는 게 핵심입니다.

## 한계

- 합성 환경과 실제 엔터프라이즈 시스템 사이 갭 존재. <span style="background-color: #fff59d"><strong>재현 가능한 스트레스 테스트 프레임으로 봐야 하고, 프로덕션 위험 추정치로는 못 씁니다</strong></span>
- 공격 전략 6종은 고정. 전략 자동 발견은 후속 연구 범위
- 정렬 실험은 Qwen3-4B/8B까지만. 대형 모델은 컴퓨트 제약으로 못 함
- 브라우저 에이전트 · 웹페이지 인젝션은 범위 밖

## 실무에서 가져갈 점

정리하면 방어 관점에서 가져올 것은 네 개입니다.

1. <span style="background-color: #fff59d"><strong>실행 초반 스텝의 입력 검증을 더 세게</strong></span>. 이른 주입이 가장 잘 먹히는 공격
2. 도구 출력은 구조화 + 엄격 파싱. 자유 텍스트 출력이 공격에 훨씬 취약
3. 관찰 끝 필드가 위험 위치. 위치 인지 방어가 필요
4. 정렬 보상은 <span style="background-color: #fff59d"><strong>'과제 완수 + 주입 무시' 조합으로 설계. 거절에는 점수를 주지 않습니다</strong></span>

## 더 실습해보고 싶은 분들께

에이전트 보안 평가·정렬 환경 설계는 그 자체로 루프 엔지니어링 문제입니다. 실습이 필요하시면 아래 두 개를 추천합니다.

『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』

「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
