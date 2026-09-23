---
title: "LLM 에이전트가 몇 턴 뒤에 안전장치를 놓치는 이유: BLINDSPOT 벤치마크 정리 (arXiv 2609.16305)"
date: 2026-09-19T07:00:00+09:00
tags:
  - llm-agent
  - agent-safety
  - benchmark
  - refusal-calibration
  - paper-summary
description: "BLINDSPOT(arXiv 2609.16305)은 14.7턴짜리 장기 상호작용 2,500개 이상으로 13개 모델의 거부 캘리브레이션을 평가한 벤치마크입니다. 전체 턴의 절반은 9턴 이후에야 실패가 드러났습니다."
draft: true
refactor_hub: agent-safety-01
refactor_status: queued
---

## 결론 먼저

핵심은 이겁니다. LLM 에이전트 안전은 한 턴짜리 프롬프트 차단이 아니라 <span style="background-color: #fff59d"><strong>트랙토리(전체 상호작용) 단위로 측정해야 하는 속성</strong></span>이라는 겁니다. BLINDSPOT 논문(arXiv 2609.16305, IBM Research·RPI, 2026년 9월 14일)은 이걸 숫자로 보여줍니다.

- 불안전 완료(UCR) 궤적 16개 중 <span style="background-color: #fff59d"><strong>첫 4턴 안엔 하나도 실패가 없었고, 절반이 드러난 건 11턴째</strong></span>입니다. Figure 6 기준 "50% by turn 9~11" 구간이죠.
- 상호작용을 전체 길이로 늘리면 GPT-4o UCR이 <span style="background-color: #fff59d"><strong>1턴 5%에서 풀 horizon 22%로 4배 이상</strong></span> 늘었습니다. Claude Haiku 4.5는 12%→41%, Mistral Large 3는 18%→58%.
- 한 번 거부했어도 계속 몰아붙이면 <span style="background-color: #fff59d"><strong>이후 턴에서 불안전 완료로 넘어가는 궤적이 존재</strong></span>합니다. 초기 거부 ≠ 지속 안전입니다.
- 거부를 많이 한다고 안전한 게 아닙니다. Claude Opus 4.6은 UCR 4%로 낮지만 <span style="background-color: #fff59d"><strong>정상 요청 완수율 72%, 과잉 거부 17%</strong></span>로 캘리브레이션이 기울어 있습니다.

기준일: 논문 v1은 2026-09-14 공개. 아래 수치는 모두 논문 Table 3/6/7, Figure 6 기준입니다.

## 핵심 요약 표

| 항목 | 값 |
| --- | --- |
| 논문 | BLINDSPOT (arXiv:2609.16305v1) |
| 소속 | IBM Research, Rensselaer Polytechnic Institute |
| 공개 | 2026-09-14 |
| 공격 패밀리 | 22개 |
| 시나리오 | 35개 (핵심 도메인 25 + 크로스 도메인 10), 7개 도메인 |
| 생성 궤적 | 2,500개 이상, 평균 14.7턴 |
| 결과 분류 | 5종 (Safe Completion / Correct Refusal / Unsafe Completion / Over-Refusal / Indeterminate) |
| 평가 모델 | 13개 (GPT-5.6 3종, Claude 2종, Gemini 2.5 Pro, Llama-3.3-70B, Mistral Large 3, Gemma 3 2종 등) |
| 최저 UCR | GPT-5.6 Sol 2% (SCS 96.0) |
| 최고 UCR | Mistral Large 3 58% (ORR도 33%) |

원문: [arXiv abs](https://arxiv.org/abs/2609.16305) / [PDF](https://arxiv.org/pdf/2609.16305)

## 문제 설정: 왜 기존 평가로 안 되는가

기존 에이전트 안전 벤치마크는 크게 두 한계가 있었습니다.

1. 한 턴짜리 유해 프롬프트·탈옥 프롬프트 중심이라, <span style="background-color: #fff59d"><strong>여러 턴에 걸쳐 누적되는 의도 변화·권한 만료·상태 조작</strong></span>을 못 잡습니다.
2. 공격 성공/과제 성공 같은 이진 요약만 쓰면, 에이전트가 "행동해야 할 때 행동했는지, 거부해야 할 때 거부했는지"가 가려집니다.

논문이 드는 예시가 직관적입니다. 기업 내부 어시스턴트가 영업 보고서 요약부터 시작합니다. 정상 요청이죠. 이후 턴에서 고객 개인 레코드를 달라고 하고, 긴급함을 강조하고, "관리자 승인 받았다"고 주장하고, 마지막엔 외부 수신자로 전송을 요청합니다. <span style="background-color: #fff59d"><strong>개별 턴마다는 그럴듯한 요청이 누적되면 정책 위반이 되는 구조</strong></span>입니다.

## Benchmark 파이프라인

![BLINDSPOT 개요: 시나리오가 유저 에이전트·타깃 에이전트·도구·환경 상태를 초기화하고, 상호작용 궤적이 5종 결과로 판정된다](/images/2026-09-19-llm-agent-safety-refusal-calibration-blindspot/fig-1-p2.png)

Figure 1: 전체 파이프라인. 출처: 논문 Figure 1.

구성요소는 이렇습니다.

- **시나리오**: 초기 상태·도구·정책·권한 조건·유저 목표 정의
- **User Agent**: 정상 유저 또는 적대적 유저. <span style="background-color: #fff59d"><strong>직전 응답을 보고 다음 요청을 적응적으로 생성</strong></span>합니다 (response-conditioned adaptive attack)
- **Target Agent**: 평가 대상 모델. 시나리오 도구를 호출하며 상태를 변경
- **판정(adjudication)**: 도구 실행 기록·권한 상태·정책 조건·환경 전이를 근거로 5종 결과 중 하나 배정. 시맨틱 판정관 + 필요시 사람 검토

여기서 중요한 설계가 <span style="background-color: #fff59d"><strong>"safe twin"(안전 쌍둥이)</strong></span>입니다. 적대적 궤적과 거의 같지만 정책상 허용되는 대응 요청을 매칭해서, "무조건 거부하는 모델"이 가짜 좋은 점수를 받지 못하게 합니다.

## 결과: 5가지 실험 발견

### 1. 안전·유용성은 하나의 순위로 안 센다

Table 3 주요 수치입니다.

| 모델 | UCR↓ | CRR↑ | BCR↑ | ORR↓ | SCS↑ |
| --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol | 2 | 78 | 94 | 7 | 96.0 |
| Llama-3.3-70B | 7 | 71 | 97 | 10 | 95.0 |
| Claude Opus 4.6 | 4 | 67 | 72 | 17 | 83.1 |
| Gemini 2.5 Pro | 12 | 64 | 89 | 11 | 88.5 |
| GPT-4o | 22 | 51 | 84 | 16 | 80.9 |
| Claude Haiku 4.5 | 41 | 26 | 69 | 30 | 63.8 |
| Mistral Large 3 | 58 | 12 | 61 | 33 | 50.6 |

<span style="background-color: #fff59d"><strong>Llama-3.3-70B가 BCR 97%로 정상 과제 완수는 최고</strong></span>인데 UCR도 7%입니다. 반면 Claude Opus 4.6은 UCR은 더 낮지만 과잉 거부가 높죠. Mistral Large 3는 안전 실패와 과잉 거부가 동시에 높은 최악 조합입니다.

### 2. 지연 실패: 짧은 평가는 실패를 놓친다

![불안전 완료가 상호작용 턴에 따라 누적되는 그래프](/images/2026-09-19-llm-agent-safety-refusal-calibration-blindspot/fig-6-p8.png)

Figure 6: 불안전 실패의 턴별 누적. 출처: 논문 Figure 6.

Figure 6 분석입니다. 불안전 궤적 16개 중:

- <span style="background-color: #fff59d"><strong>첫 4턴: 실패 0건</strong></span>
- 턴 5까지: 18.75%
- 턴 11까지: 50%
- 턴 13까지: 81.25%
- 턴 19에 와서야 100%

요약하면 <span style="background-color: #fff59d"><strong>절반가량의 실패는 9~11턴은 지나야 보입니다</strong></span>. 첫 응답만 보는 평가로는 구조적으로 못 잡습니다.

### 3. 적응적 공격이 반복 프롬프팅보다 위험하다

Table 7 ablation입니다. 유저 에이전트가 직전 응답을 못 보게 하면(NA) UCR이 확 떨어집니다.

| 모델 | NA UCR | AD UCR | 배율 |
| --- | --- | --- | --- |
| Claude Opus 4.6 | 1 | 4 | 4.0× |
| GPT-5.6 Terra | 3 | 8 | 2.7× |
| GPT-4o | 11 | 22 | 2.0× |
| Claude Haiku 4.5 | 25 | 41 | 1.6× |
| Mistral Large 3 | 37 | 58 | 1.6× |

<span style="background-color: #fff59d"><strong>단순 반복이 아니라 "거부를 보고 우회하는" 적응이 실패율을 최대 4배까지 올립니다</strong></span>. Claude Opus 4.6의 4.0×가 가장 큽니다.

### 4. 반복 실행에도 숨은 실패 설정이 나온다

Fail@k 결과에서 GPT-5.6 Sol은 Fail@1 3%에서 Fail@5 8%로, GPT-4o는 23%→42%로 늘었습니다. <span style="background-color: #fff59d"><strong>같은 설정이라도 확률적으로 실패하는 구성이 존재</strong></span>한다는 뜻이라, 일회 실행 결과만 믿으면 안 됩니다.

### 5. 도구 조합·상태 의존 공격이 따로 있다

공격 메커니즘 22종 중 사회공학·간접 인젝션이 각 9패밀리로 가장 많고, 권한 스푸핑 8, 관측 오염 6입니다. 시간 패턴은 <span style="background-color: #fff59d"><strong>staged 14, gradual 9, delayed 9, adaptive 7 vs 원샷 3</strong></span> — 명백히 장기 horizon 설계입니다.

![시나리오별 공격 적용 가능성 행렬](/images/2026-09-19-llm-agent-safety-refusal-calibration-blindspot/table-8-p22.png)

Table 8: 시나리오–공격 적용 행렬 예시. 출처: 논문 Table 8.

## 내 해석: 실무자에게 의미 있는 것

원문 근거와 제 해석을 구분해서 적습니다.

- **평가 설계**: 논문 데이터가 시사하듯, 에이전트 안전 리포트에 <span style="background-color: #fff59d"><strong>최소 15턴 이상, 반복 실행 포함</strong></span>이 없으면 UCR 숫자 자체를 신뢰하기 어렵습니다. 이건 제 판단이지만 Table 6 추세가 일관되게 뒷받침합니다.
- **거부율 지표의 함정**: 거부를 늘리면 UCR은 내려가지만 BCR·ORR이 나빠집니다. SCS 같은 캘리브레이션 통합 점수를 같이 봐야 합니다.
- **하네스 방어**: 초기 거부 후에도 계속 몰아붙이는 사용자에 대해 상태(권한 만료·수신자 변경)를 재검하는 가드레일이 하네스 레벨에서 필요합니다. ActGuard 같은 실행 전 감사 계열 방어와 자연스럽게 이어지는 지점이죠.

한계도 적어둡니다. 논문 스스로 preliminary results라고 명시했고, 16개 불안전 궤적 기반 Figure 6 통계는 표본이 작습니다. 모델별 세부는 Appendix D를 봐야 합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문 (FAQ)

**BLINDSPOT에서 "거부 캘리브레이션"이란 정확히 무엇인가요?**
금지된 행동은 거부하고(Correct Refusal), 허용된 정상 과제는 완수하고(Safe Completion), 불필요한 거부는 하지 않는 것(Over-Refusal 방지)을 궤적 전체에서 유지하는 능력입니다.

**왜 한 턴 평가로는 에이전트 안전을 측정할 수 없나요?**
이 논문에서 불안전 완료 궤적의 절반이 9~11턴 이후에야 드러났고, 첫 4턴엔 실패가 0건이었습니다. 첫 응답만 보면 지연 실패를 구조적으로 놓칩니다.

**어떤 모델이 가장 안전했나요?**
UCR 2%·SCS 96.0인 GPT-5.6 Sol이 최저 위험었고, Llama-3.3-70B는 정상 과제 완수율(BCR 97%)이 가장 높으면서 UCR 7%를 유지했습니다. 단일 순위보다 캘리브레이션 프로필로 봐야 합니다.

**BLINDSPOT 코드와 데이터는 공개되어 있나요?**
논문 첫 페이지에 코드·데이터셋 링크가 "Code and Dataset" 표기로 안내되어 있습니다. arXiv 페이지에서 확인하세요.

## 참고

- 원문: [BLINDSPOT: A Benchmark for Safety and Refusal Calibration in Long-Horizon Tool-Using Agents (arXiv:2609.16305)](https://arxiv.org/abs/2609.16305)
- 관련 국내 정리: [LLM 에이전트 간접 프롬프트 인젝션 방어를 실행 전에 끝내는 법: ActGuard 논문 정리](/posts/2026-09-18-llm-agent-indirect-prompt-injection-actguard)
- 관련 국내 정리: [LLM 에이전트 벤치마크가 위험한 이유: MemRiskBench 논문 정리](/posts/2026-09-17-llm-agent-benchmark-memriskbench)
