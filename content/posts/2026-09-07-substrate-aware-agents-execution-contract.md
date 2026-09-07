---
title: 실행 컨텍스트를 프롬프트에 넣었더니 에이전트가 짠 코드가 바뀌었다 — Substrate-Aware AI Agents 정리
date: 2026-09-07
tags:
  - ai-agent
  - llm
  - prompt-engineering
  - execution-context
draft: false
description: arXiv 2609.05232 정리. RAM 128MB·10초 제약 한 줄을 프롬프트에 넣으니 Claude Opus 5, GPT-5.6-Sol, Gemini 3.7 Flash가 생성한 코드의 메모리 사용량과 실행시간이 함께 줄었습니다. '기판 맹목' 개념과 실험 수치를 정리했습니다.
---

## 결론 먼저

에이전트가 아무리 좋은 작업 명세를 받아도, 그 코드가 돌아갈 환경의 제약(메모리, 시간제한, 런타임 버전)을 모르면 잘못된 계획을 세웁니다.

 이 논문은 이걸 <span style="background-color: #fff59d"><strong>substrate blindness(기판 맹목)</strong></span>라고 부릅니다.

핵심 실험: RAM 128MB·실행 10초 제약을 딱 한 줄 프롬프트에 추가했더니, 세 개 프론티어 모델이 생성한 코드의 <span style="background-color: #fff59d"><strong>피크 메모리와 실행시간이 같이 줄었습니다</strong></span>.<span style="background-color: #fff59d"><strong>알고리즘 힌트, 블록 크기, 파인튜닝 없이요</strong></span>.

- Claude Opus 5: 256.48 MiB → 107.82 MiB, 예산 내 통과 0/5 → 5/5
- GPT-5.6-Sol: 118.63 MiB → 64.61 MiB, 4/5 → 5/5
- Gemini 3.7 Flash: 452.36 MiB → 158.16 MiB, 0/5 → 2/5
- <span style="background-color: #fff59d"><strong>실행시간은 세 코호트 모두 감소, 최대 3.09배 빨라짐</strong></span>

기준일: 2026-09-04 arXiv 공개(v1), 단일 저자 독립 연구, 8페이지.

## 핵심 수치 표 (128MB 계약 공개 실험)

| 모델 | task-only 평균 MaxRSS | 계약 공개 평균 MaxRSS | 평균 wall time 변화 | 128 MiB 이내 통과 |
|---|---|---|---|---|
| claude-opus-5 | 256.48 MiB | 107.82 MiB | 0.9109s → 0.3612s (2.52x) | <span style="background-color: #fff59d"><strong>0/5 → 5/5</strong></span> |
| gpt-5.6-sol | 118.63 MiB | 64.61 MiB | 0.5507s → 0.3282s (1.68x) | 4/5 → 5/5 |
| gemini-3.7-flash | 452.36 MiB | 158.16 MiB | 1.0994s → 0.3561s (3.09x) | 0/5 → 2/5 |

인덱스 정렬 비교 14개 중 13개에서 계약 공개 쪽 피크 메모리가 더 낮았습니다. 14개 조건 통계적 페어는 아니고 서술적 비교라고 논문이 직접 밝힙니다.

![Table 1. 조건별 실행·자원 결과 (원문 Table 1)](/images/2026-09-07-substrate-aware-agents-execution-contract/table-1.png)

## 무엇을 실험했나

태스크는 하나로 정해져 있습니다. 8,000×1,024 float32 행렬을 로드해 모든 쌍의 유클리드 거리 합을 출력하는 코드 생성.

여기엔 함정이 하나 있습니다. 8,000×8,000 float32 거리 중간 행렬을 통째로 만들면 244.14 MiB가 필요합니다. 128MB 안에서는 원천적으로 불가능한 구조예요. 블록 처리 같은 다른 구현이 필요합니다.

두 조건을 비교했습니다.

| 조건 | 프롬프트 내용 |
|---|---|
| Task-only (A) | 작업 명세만 |
| Contract-disclosed (D) | 동일 명세 + <span style="background-color: #fff59d"><strong>"RAM limit: 128 MB, Execution time limit: 10.0 seconds"</strong></span> |

모델당 각 조건 5회 생성.

macOS 서브프로세스에서 Python 3.9.6, NumPy 2.0.2, BLAS 스레드 1로 고정해 실행하고 수치 정확도(상대오차 1e-4 미만), exit 상태, wall time, <span style="background-color: #fff59d"><strong>OS 피크 메모리(RUSAGE_CHILDREN MaxRSS)</strong></span>를 측정했습니다.

## 코드가 실제로 어떻게 바뀌었나

흥미로운 지점은 여기입니다. 계약을 공개하면 모델이 "예산 지켰습니다" 주석만 달고 넘어가는 게 아니구요, <span style="background-color: #fff59d"><strong>구현 구조 자체를 바꿉니다</strong></span>.<span style="background-color: #fff59d"><strong>원문 오디트에서 관찰된 변화</strong></span>:

- 블록 크기 조정 (bounded blocking)
- float32 유지 — 정밀도 승격(promotion) 회피
- - <span style="background-color: #fff59d"><strong>상삼각(upper-triangle) 순회로 계산량 절반 절감</strong></span>
- 임시 버퍼 재사용, in-place / memory-mapped 버퍼

레시피도 하나로 고정되지 않습니다. 어떤 task-only 코드는 이미 블록 처리를 쓰고, 어떤 계약 공개 코드는 다른 블록 지오메트리를 선택합니다. 원문의 표현대로 execution context는 구현 분포 자체를 이동시킵니다. 단일 정답을 강제하는 효과가 아니구요.

## 96MB로 더 조이면

계약을 128MB에서 96MB로 더 빡빡하게 주면 어떻게 되는지도 봤습니다.

| 모델 | 96MB 계약 평균 MaxRSS | task-only 대비 메모리 | 시간 변화 | 96 MiB 이내 통과 |
|---|---|---|---|---|
| gpt-5.6-sol | 60.88 MiB | -48.7% | -35.0% | 5/5 |
| claude-opus-5 | 87.57 MiB | -65.9% | -58.3% | 4/5 |
| gemini-3.7-flash | 118.46 MiB | -73.8% | -63.8% | 3/5 |

96MB 조건의 15개 실행 가능한 프로그램은 전부 수치적으로 정확했고 10초 이내에 끝났습니다.

![Table 2. task-only vs 128MB vs 96MB 조건별 자원 결과 (원문 Table 2)](/images/2026-09-07-substrate-aware-agents-execution-contract/table-2.png) 계약을 조이면 각 모델의 평균 wall time은 5.3~11.9% 살짝 오르는데, task-only 기준으로는 여전히 크게 빠릅니다. <span style="background-color: #fff59d"><strong>MaxRSS × wall time 곱은 task-only 대비 67~90% 낮았구요</strong></span>.

## 왜 중요한가: 하네스 설계에 바로 적용되는 이야기

논문은 이걸 에이전트 하네스 관점으로 확장합니다. Kubernetes의 CPU/메모리 request·limit, Cloud Run의 메모리 초과 인스턴스 종료, AWS Lambda의 메모리-CPU-과금 결합 — 실제 운영 환경은 전부 이 계약 조건을 전제로 돌아갑니다.

근데 지금 대부분의 에이전트 하네스는 이 정보를 모델 추론 컨텍스트에서 빼놓습니다. 계획 단계에서 이걸 넣어주면, 실패 후 반복 수리(repair loop)를 돌기 전에 <span style="background-color: #fff59d"><strong>첫 생성부터 배포 가능한 계획이 나옵니다</strong></span>.

재미있는 사건 하나. task-only 조건의 Claude 코드 하나가 Python 3.10 문법(union 타입)을 써서 고정된 Python 3.9.6 런타임에서 실행 실패했습니다.

 <span style="background-color: #fff59d"><strong>런타임 버전도 계약의 일부</strong></span>라는 걸 보여주는 사례예요. RAM/시간 실험 자체는 통제되어 있고, 버전 계약 연구는 후속 과제로 남겨뒀습니다.

![Figure 2. 모든 실행 결과를 task-only 평균 대비 %로 정규화한 메모리·wall time 분포 (원문 Figure 2)](/images/2026-09-07-substrate-aware-agents-execution-contract/figure-2.png)

## 내 해석: 어디까지 믿을지

원문 근거와 내 판단을 나눠서 정리합니다.

원문이 보여준 것: 단일 수치 태스크, 모델당 5샘플, 두 조건 비교에서 실행 계약 공개가 생성 코드의 자원 프로파일을 크게 개선한다는 통제된 증거.

내 해석:

- 샘플이 작고(n=5) 태스크도 하나라, 일반화는 '방향성 증거' 수준으로 받아들이는 게 맞습니다. 저자도 proof of concept이라고 명시합니다.
- 근데 실무 관점에서는 반발력이 꽤 셉니다. 개입이 <span style="background-color: #fff59d"><strong>프롬프트 한 줄</strong></span>이니까요. 비용 제로에 가까운 개입으로 <span style="background-color: #fff59d"><strong>메모리 49~74% 감소, 시간 35~64% 감소</strong></span>가 관찰됐습니다.
- <span style="background-color: #fff59d"><strong>하네스·스케줄러가 이미 알고 있는 정보(메모리 limit, 타임아웃, 툴 쿼터, 런타임 버전)를 시스템 프롬프트나 태스크 명세에 붙이는 건 오늘 바로 적용할 수 있습니다</strong></span>.
- 코드 생성以外(예: 툴 선택, 멀티스텝 계획)에서 같은 효과가 나오는지는 후속 연구 몫입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

Q: substrate blindness가 정확히 뭔가요?**
에이전트가 작업 명세는 받았지만, 그 계획이 실행될 환경의 메모리·시간·런타임 제약을 모르는 상태를 뜻합니다. 논문은 이걸 정보 비대칭 문제로 정의합니다.

Q: 어떤 제약을 프롬프트에 넣었나요?**
"RAM limit: 128 MB"와 "Execution time limit: 10.0 seconds" 두 줄만 추가했습니다. 알고리즘 힌트나 블록 크기 지시는 없습니다.

Q: 어떤 모델로 실험했나요?**
Anthropic claude-opus-5, OpenAI gpt-5.6-sol, Google gemini-3.7-flash 세 설정입니다. 계층 매칭 통제군으로 설계되진 않았고, 공급자 다양성 확보 목적이라고 합니다.

Q: 실험 코드와 원시 응답을 볼 수 있나요?**
네. 평가 아카이브가 공개되어 있습니다: https://github.com/manu2/Context-Aware-Agent-Experiment

## 출처

- 원문: Substrate-Aware AI Agents: Execution Context as a First-Class Input, Manu Agrawal, 2026. https://arxiv.org/abs/2609.05232
- 평가 아카이브(GitHub): https://github.com/manu2/Context-Aware-Agent-Experiment
- 본문 수치는 전부 v1 원문 Table 1, Table 2, Figure 1, Figure 2 기준입니다(기준일 2026-09-04).
