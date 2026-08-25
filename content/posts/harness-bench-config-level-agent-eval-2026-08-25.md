---
title: "Harness-Bench: 같은 모델인데 하네스만 바꿨더니 23.8점 차이가 났다"
date: 2026-08-25
draft: false
tags: [agent, harness, benchmark, llm, evaluation]
source: https://arxiv.org/abs/2605.27922
---

## 결론 먼저

<span style="background-color: #fff59d"><strong>같은 모델, 같은 태스크인데 하네스(실행 레이어)만 바꿨더니 점수 차이가 23.8점</strong></span>이 나왔다는 논문입니다. 베이징대·Qihoo360 팀의 Harness-Bench(arXiv 2605.27922) 정리했습니다.

핵심 주장은 한 줄로 정리됩니다.

`Agent = Model + Harness`

<span style="background-color: #fff59d"><strong>에이전트 성능은 베이스 모델만으로 보고하면 안 되고, 모델+하네스 조합 단위로 보고해야 한다</strong></span>구요.

![Figure 1: Harness-Bench 평가 파이프라인](/images/harness-bench-config-level-agent-eval-2026-08-25/fig-1-p3.png)
*Figure 1. 태스크를 샌드박스에서 실행하고 아티팩트·트레이스·사용량·검증 결과를 모두 기록하는 파이프라인*

## 무엇을 측정했나

기존 벤치마크(SWE-bench, WebArena, GAIA 등)는 <span style="background-color: #fff59d"><strong>하네스를 고정하거나 통째로 추상화</strong></span>해서, 실행 레이어 차이를 못 재는 상태였습니다.

Harness-Bench는 반대로 접근합니다.

- 태스크, 예산, 타임아웃, 평가자를 고정
- 하네스 설정만 바꿔가며 실행
- 각 하네스의 네이티브 동작은 그대로 유지

<span style="background-color: #fff59d"><strong>106개 샌드박스 오프라인 태스크</strong></span>를 쓰구요, 소프트웨어 엔지니어링, 데이터 분석, 워크스페이스/도구 조작, 근거 기반 지식작업 등 <span style="background-color: #fff59d"><strong>8개 워크플로 카테고리</strong></span>로 구성했습니다.

![Figure 2: 태스크 구성](/images/harness-bench-config-level-agent-eval-2026-08-25/fig-2-p4.png)
*Figure 2. 106개 태스크의 8개 워크플로 카테고리 분포*

점수 공식은 이렇습니다.

```
TaskScore = Security × Completion × Process
Process = (Robustness + ToolUse + Consistency) / 3
```

<span style="background-color: #fff59d"><strong>보안 위반이 하나라도 있으면 0점 곱으로 날아가는 보수적 구조</strong></span>입니다. 프로세스 평가는 <span style="background-color: #fff59d"><strong>claude-sonnet-4.6을 고정 심판</strong></span>으로 사용했습니다.

## 숫자로 보는 결과

<span style="background-color: #fff59d"><strong>6개 설정 가능 하네스 × 8개 API 모델 백엔드 완전요인설계로 5,088개 트레이토리, 여기에 Codex 106개를 더해 총 5,194개</strong></span>를 분석했습니다.

| 항목 | 값 |
|---|---|
| 최고 하네스 | NanoBot 76.2점 |
| 최저 하네스 | OpenClaw 52.4점 |
| 격차 | 23.8점 (동일 태스크·동일 모델 풀) |
| 모델 바운드 참조 | Codex(GPT-5.4) 80.4점 |

![Table 2: 하네스별 종합 결과](/images/harness-bench-config-level-agent-eval-2026-08-25/table-2-p7.png)
*Table 2. 같은 태스크·모델 풀에서 하네스별로 집계한 점수. Tokens와 Turns는 낮을수록 좋음*

재미있는 점은 <span style="background-color: #fff59d"><strong>NanoBot이 최고 점수를 받으면서도 Hermes, ZeroClaw, NullClaw, Moltis보다 토큰을 적게 썼다</strong></span>는 겁니다. 긴 트레이토리가 곧 성능은 아니라는 거죠.

## 강한 모델일수록 하네스 영향이 작다

Figure 3이 논문에서 가장 실무적인 그림입니다.

![Figure 3: 하네스 의존성](/images/harness-bench-config-level-agent-eval-2026-08-25/fig-3-p7.png)
*Figure 3. 모델별 평균 점수와 크로스-하네스 분산. 강한 모델일수록 분산이 작다*

- GPT-5.4, Claude-Sonnet-4.6 같은 강한 백엔드는 평균이 높고 하네스 간 분산이 작음. 프롬프트·도구 인터페이스·상태관리 차이에 잘 버틴다는 뜻
- 약한 백엔드는 하네스에 따라 편차가 큼. 실행 기반에 민감하다는 뜻

즉 <span style="background-color: #fff59d"><strong>예산이 부족해서 약한 모델을 쓴다면, 하네스 설계에 더 공을 들여야 한다</strong></span>는 결론이 나옵니다. 카테고리별로는 <span style="background-color: #fff59d"><strong>구조화된 데이터 분석, 도구 시퀀싱, 워크스페이스 조작에서 하네스 의존성이 더 컸습니다</strong></span>.

## 실패 패턴: 실행 정렬(execution alignment) 실패

논문의 분석 파트가 개인적으로 제값 하는 대목입니다. 실패 트레이토리를 뜯어보니, <span style="background-color: #fff59d"><strong>모델이 그럴듯하게 추론은 하는데 그 추론이 도구 피드백·워크스페이스 상태·증거·검증 가능한 산출물과 분리되는 패턴이 반복</strong></span>됐습니다.

대표 증상 두 가지:

- <span style="background-color: #fff59d"><strong>출력 스키마 위반, 필수 산출물 누락</strong></span>. 태스크를 이해한 것처럼 보이는데 기계가 검증할 형태로 만들지 못함
- <span style="background-color: #fff59d"><strong>부분 진행 후 회복 실패</strong></span>. 도구 피드백을 받았는데 다음 행동에 반영 안 하고, 진행 상태를 보존하지 않고, 커밋 없이 끝남

하네스는 '무엇이 미완료 의무인지, 무엇이 관측된 증거인지, 무엇이 복구 가능한 실패인지'에 대한 표현을 암묵적으로 정의합니다. 이 표현이 약하면 그럴듯한 추론이 평가 조건에서 떠내려간다는 이야기입니다.

## 내 해석

- <span style="background-color: #fff59d"><strong>하네스 비교가 리더보드가 된 시점에서 "모델만 바꿔 끼우는" 에이전트 도입은 절반만 한 선택</strong></span>입니다. 동일 예산이면 하네스 튜닝이 더 싸게 먹히는 경우가 많을 겁니다
- 강한 모델이 하네스 영향을 덜 받는다는 결과는 곧 <span style="background-color: #fff59d"><strong>강한 모델의 가격 프리미엄이 "하네스 엔지니어링 인건비"와 대체재 관계</strong></span>라는 뜻이기도 합니다
- 보안 게이트를 0/1 곱으로 넣는 설계는 실무 벤치마크에서도 바로 벤치마킹할 만합니다

한계도 명시돼 있구요. 샌드박스 오프라인이라 라이브 서비스·장기 상태는 커버 못 하고, 프로세스 점수에 LLM 심판이 개입하므로 <span style="background-color: #fff59d"><strong>진단 용도로 읽어야 한다</strong></span>고 합니다.

코드·데이터는 <span style="background-color: #fff59d"><strong>github.com/Qihoo360/harness-bench</strong></span>에 공개돼 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
