---
title: "MemToC — 도구 결과가 내 기억과 충돌할 때, LLM은 누구 말을 듣나"
date: 2026-08-28
tags:
  - LLM
  - agent
  - tool-use
  - benchmark
  - hallucination
  - fine-tuning
draft: false
description: "MemToC 벤치마크(arXiv 2608.26295) 정리. 정답을 안 LLM이 틀린 도구 결과를 만나면 6.5-17.1%만 자기 답을 지키고, 20개 파인튜닝 조합 중 19개에서 기권이 줄었다는 결과와 실무 적용 포인트."
---

## 결론 먼저

에이전트를 운영하다 보면 이런 순간이 옵니다. 모델이 분명 정답을 알고 있는데, API가 내려준 결과가 그 답과 다릅니다. 그러면 모델은 조용히 자기 답을 버리고 도구 결과를 그대로 답으로 냅니다. 이 장면을 6,504번 통제해서 재현한 벤치마크가 MemToC입니다 (arXiv:2608.26295, 기준일 2026-08-28).

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>정답을 가진 모델이 틀린 도구 결과를 만나면 6.5-17.1%만 자기 답을 지킵니다</strong></span>. "도구를 신뢰하라"는 통념을 소스 정확성을 통제해 처음으로 뒤집어 본 측정입니다.

| 항목 | 값 |
| --- | --- |
| 평가 에피소드 | 6,504개 |
| 기반 질문 | 542개 품질 통제 질문 |
| 대상 모델 | 오픈 웨이트 7-9B 5종 |
| 검증된 정답 유지율(틀린 도구 상대) | 6.5-17.1% |
| 올바른 도구 추종율 | 86.0-93.1% |
| 둘 다 틀릴 때 도구 답 반복 | 78.4-86.0% |

## 숫자로 보는 결과

올바른 도구는 <span style="background-color: #fff59d"><strong>86.0-93.1%로 잘 따르</strong></span>는데, 틀린 도구도 비슷하게 따른다는 게 문제입니다. 둘 다 틀린 경우에는 <span style="background-color: #fff59d"><strong>78.4-86.0%로 도구 답을 그대로 반복</strong></span>합니다. 도구를 판단해서 고르는 수준을 넘어서 그냥 복사에 가깝습니다.

같은 질문과 에피소드를 두고 지시문 표현만 3가지로 바꾸면 모델 간 순위가 흔들렸습니다. <span style="background-color: #fff59d"><strong>프롬프트 표현 하나로 순위가 바뀐다</strong></span>는 뜻이라, 도구 신뢰도 랭킹 해석은 조심해야 합니다.

![MemToC overview](/images/2026-08-28-memtoc-memory-tool-conflict/fig-2-p3.png)

## 어떻게 측정했나

542개 검증된 사실 질문에서 모델별 클로즈드북 답을 유도하고, <span style="background-color: #fff59d"><strong>정답/오답이 통제된 도구 결과를 삽입</strong></span>합니다. 4가지 소스 정확성 케이스와 도구 에러, 무도구 조건을 두고 7-9B 오픈 웨이트 모델 5종을 평가했습니다. 실행 가능한(executable) 도구를 쓴 점이 특징입니다.

![한 에피소드의 네 가지 케이스](/images/2026-08-28-memtoc-memory-tool-conflict/fig-3-p11.png)

## 왜 문제인가

도구는 항상 옳지 않습니다. API는 실패하고, 검색 결과는 오래되고, 계산기도 버그가 있습니다. 모델이 도구 결과를 무조건 복사하면 <span style="background-color: #fff59d"><strong>도구 에러가 그대로 최종 답이 되는 경로</strong></span>가 만들어집니다. 파이프라인이 길어질수록 오염이 증폭됩니다.

## 고칠 수 있을까

ToolHop 기반 <span style="background-color: #fff59d"><strong>체인 레벨 크로스피팅</strong></span>으로 SFT와 DPO를 비교했습니다. 같은 사실을 공유하는 질문이 학습/평가에 걸치지 않게 분리한 설계입니다.

판정 기준은 비대칭입니다. <span style="background-color: #fff59d"><strong>정답 유지는 오르되 올바른 도구 추종은 줄지 않아야</strong></span> 통과입니다. 그 결과 SFT와 DPO 모두 4개 백본 중 2개에서만 통과했습니다.

경고도 있습니다. <span style="background-color: #fff59d"><strong>20개 조합 중 19개에서 기권(abstention)이 감소</strong></span>했습니다. 도구 에러 후나 답 불가 입력에서 아는 척이 늘어난 거죠. 개선은 드물게 깨끗하게 옵니다.

## 실무 적용 포인트

- <span style="background-color: #fff59d"><strong>무조건 도구 우선 정책은 도구 장애에 취약</strong></span>합니다
- 도구 출력에 신뢰도·출처 메타데이터를 붙여 모델이 판단 재료를 갖게 하는 게 실용적입니다
- 파인튜닝으로 조정할 땐 정답 유지, 도구 추종, 기권, 표현 강건성을 같이 평가해야 합니다

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### MemToC는 기존 벤치마크와 뭐가 다른가

기존 평가는 모델이 도구와 파라미터 기억 중 무엇을 선호하는지만 쟀습니다. MemToC는 도구 결과의 정답 여부를 통제해서 선호 대신 정답 조건별 판단을 측정합니다.

### 핵심 수치는 얼마나 안 좋은가

검증된 정답 유지율 6.5-17.1%, 올바른 도구 추종 86.0-93.1%, 둘 다 틀릴 때 도구 답 반복 78.4-86.0%입니다. 대상은 오픈 웨이트 7-9B 모델 5종, 6,504개 에피소드입니다(2026-08-28 기준).

### 파인튜닝으로 어떻게 고치나

SFT와 DPO가 비대칭 기준을 통과한 건 4개 백본 중 2개뿐이고, 20개 조합 중 19개에서 기권 감소 부작용이 관측됐습니다. 파인튜닝은 정답 유지·도구 추종·기권·표현 강건성을 함께 평가해야 합니다.

## 참고

- 논문: [MemToC: Benchmarking Memory-Tool Conflict Resolution in Large Language Models](https://arxiv.org/abs/2608.26295) (arXiv:2608.26295)
- Figure 2, 3: 원문 캡션 기반 크롭
