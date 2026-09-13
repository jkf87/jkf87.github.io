---
title: "멀티모달 LLM 에이전트가 공간 추론을 계획으로 못 옮기는 이유: MindTopo 벤치마크 정리"
date: 2026-09-13
tags:
  - llm
  - agent
  - benchmark
  - spatial-reasoning
  - multimodal
  - arxiv
draft: false
description: "연속변형에 불변하는 위상 관계를 13개 과제로 측정한 MindTopo(arXiv 2609.11900) 벤치마크를 정리했습니다. 최고 모델 53.5% vs 인간 97.4%."
---

로프를 구부리고 늘여도 매듭은 그대로 남습니다. 이런 성질을 위상(topology)이라고 부릅니다. Northwestern·Microsoft Research·Stanford 팀이 이 위상 감각으로 멀티모달 LLM을 측정한 벤치마크를 공개했습니다. 결과는 1차원적입니다. 모델은 정적 장면에서 위상 관계를 알아보는데, 행동 연속으로 옮기는 순간 무너집니다.

## 결론 먼저

MindTopo은 <span style="background-color: #fff59d"><strong>위상 성질 5가지를 추론(reasoning)과 계획(planning) 두 수준으로 나눠 측정하는 벤치마크</strong></span>입니다. 13개 과제, 11,030 인스턴스로 14개 MLLM을 평가했고, 전 모델이 추론보다 계획에서 크게 떨어졌습니다. 최고 모델 전체 평균 53.5%, 인간은 97.4%였습니다.

| 항목 | 내용 |
| --- | --- |
| 벤치마크 | MindTopo (Northwestern·MSR·Stanford) |
| 측정 대상 | 연속변형에 불변하는 위상 관계 5종 |
| 구성 | 13개 과제 / 11,030 인스턴스 (추론 8,030 + 계획 3,000) |
| 평가 모델 | MLLM 14종 + 영상생성 3종 |
| 최고 성적 | Gemini 3.1 Pro 전체 53.5% (추론 60.0 / 계획 43.2) |
| 인간 | 전체 97.4% |
| 학습 실험 | Qwen3-VL-2B SFT+RL: 추론 14.2→51.5%, 계획 0.2→6.3% |
| 소스 | arXiv 2609.11900 (2026-09-10) |

기준일: 2026-09-13, 논문 v1 기준입니다.

## 위상을 왜 따로 측정하나

기존 공간 추론 벤치마크는 거리·각도·모양 같은 계량(metric) 속성에 치중해 있었습니다. 인지과학 쪽 근거는 다릅니다. 아동이 공간을 이해할 때 <span style="background-color: #fff59d"><strong>위상 관계가 계량 기하보다 먼저 발달한다</strong></span>는 피아제의 견해가 유명하고, 성인 시각 연구에서도 시각 시스템은 유클리드 특징보다 위상 불변량을 먼저 뽑아낸다는 결과가 있습니다.

MindTopo은 이 근거를 그대로 설계에 옮겼습니다. 다섯 가지 위상 성질을 정의하고, 각각 추론 과제와 계획 과제를 매칭했습니다.

| 위상 성질 | 추론 과제 | 계획 과제 |
| --- | --- | --- |
| 연속성 (continuity) | 2D/3D 미로 도달 | Pipe (파이프 연결) |
| 분리 (separation) | IKEA 부분조립 | One Stroke (한붓그리기 분할) |
| 순서 (order) | Bead, Origami Point | Swap (슬라이딩 퍼즐) |
| 둘러쌈 (enclosure) | Sheep, Hole | Chat Noir (고양이 포위) |
| 매듭 (knots) | Knots | Untangle (로프 풀기) |

![MindTopo 개요](/images/2026-09-13-mindtopo-topological-reasoning-benchmark/fig-1-p1.png)

Figure 1. MindTopo 개요. 출처: arXiv 2609.11900 Figure 1.

과제는 전부 절차적으로 생성됩니다. 씬 상태에서 렌더링하고, 정답도 프로그램이 계산합니다. 사람 주석이 없으니 <span style="background-color: #fff59d"><strong>난이도를 파라미터로 조절하면서 데이터를 무한히 확장</strong></span>할 수 있는 구조입니다.

![13개 과제 구성](/images/2026-09-13-mindtopo-topological-reasoning-benchmark/fig-2-p3.png)

Figure 2. 위상 성질×인지 수준별 13개 과제. 출처: arXiv 2609.11900 Figure 2.

## 숫자로 보는 격차

리더보드에서 눈에 띄는 대목을 뽑았습니다.

모든 모델이 <span style="background-color: #fff59d"><strong>추론보다 계획에서 크게 떨어집니다</strong></span>. Gemini 3.1 Pro는 추론 60.0%인데 계획은 43.2%, GPT-5.5는 57.7%에서 48.3%로 떨어집니다. Gemini 3.1 Flash Lite는 계획이 13.1%까지 내려갑니다.

인간과 격차도 큽니다. 인간 전체 97.4%, 계획 과제는 100%입니다. 최고 모델과 44%p 차이입니다.

오픈소스 대형 모델도 마찬가지입니다. Qwen3.5-VL-397B가 계획 19.9%, InternVL-3.5-241B는 4.3%입니다.

| 모델 | 전체 | 추론 | 계획 |
| --- | --- | --- | --- |
| Gemini 3.1 Pro | 53.5% | 60.0% | 43.2% |
| GPT-5.5 | 54.1% | 57.7% | 48.3% |
| Qwen3.5-VL-397B | 34.9% | 44.3% | 19.9% |
| Gemini 3.1 Flash Lite | 36.3% | 50.8% | 13.1% |
| InternVL-3.5-241B | 21.8% | 32.7% | 4.3% |
| 무작위 | 9.5% | 13.3% | 3.5% |
| 인간 | 97.4% | 95.8% | 100% |

## SFT와 RL로 좁혀지나

Qwen3-VL-2B-Instruct로 학습 실험을 했습니다. 답만 보는 SFT, GRPO, SFT+GRPO를 비교했습니다.

9개 과제 평균이 베이스 8.0%에서 SFT 28.8%, GRPO 단독 18.7%, <span style="background-color: #fff59d"><strong>SFT+RL 조합 31.4%</strong></span>까지 올라갑니다. SFT+GRPO는 추론 평균을 14.2%에서 51.5%로 끌어올렸습니다.

| 설정 | 추론 평균 | 계획 성공 | Pipe | One Stroke |
| --- | --- | --- | --- | --- |
| 베이스 | 14.2% | 0.2% | 0% | 0% |
| SFT | — | — | 0% | 0.8% |
| RL (GRPO) | — | — | 0% | 0% |
| SFT + RL | 51.5% | 6.3% | 0% | 0.5% |

핵심은 나머지 숫자입니다. 계획 성공률은 0.2%에서 6.3%로만 올라갔고, <span style="background-color: #fff59d"><strong>Pipe 과제는 모든 학습 조건에서 0%</strong></span>입니다. 추론에서 배운 위상 지식이 긴 행동 열 실행으로 옮겨가지 못하는 셈입니다.

전이 실험도 미묘합니다. 4개 추론 과제로 학습하고 남은 1개를 평가하는 leave-one-out에서 Bead는 9.3→26.5%, Knots는 11.2→15.5%로 오르는데, 2D Maze·Assembly·Sheep은 개선이 없었습니다. 전이는 선택적이라는 뜻입니다.

## 영상 생성 모델은 세계 모델이 되나

논문의 가장 흥미로운 대목입니다. 계획 실패가 동역학 문제라면, 다음 상태를 그려주는 영상 생성을 붙이면 어떨까 하는 가설을 테스트했습니다.

GPT-5.6-Luna를 플래너로 쓰고, 매 스텝 GPT-Image-2로 예상 상태를 렌더링하거나 Wan2.2-I2V-A14B·Seedance-2.0-Mini로 후보 계획을 롤아웃했습니다.

결론은 부정적입니다. Wan2.2-I2V-A14B는 Untangle 쉬움 난이도에서 54.3%까지 갔다가 어려움에서는 0%로 붕괴합니다. 감사(audit) 결과 <span style="background-color: #fff59d"><strong>119개 롤아웃 중 116개가 동역학을 위반</strong></span>했고, 위상 불변 위반이 93건, 정합성 오류가 90건이었습니다.

즉 생성 모델은 <span style="background-color: #fff59d"><strong>그럴듯한 최종 상태에는 도달하는데, 그 상태로 가는 유효한 경로는 보존하지 않습니다</strong></span>. LTX-2.5의 Pipe 클립 중 35.2%가 종료 상태 기준으로는 성공으로 파싱되는데, 전 구간 결함 없이 통과한 클립은 0개였습니다. 1,560개 롤아웃 전체에서 과정이 유효하면서 과제까지 성공한 영상은 하나도 없었습니다.

![오류 유형별 실패 사례](/images/2026-09-13-mindtopo-topological-reasoning-benchmark/fig-5-p9.png)

Figure 5. 오류 카테고리별 대표 실패 사례. 출처: arXiv 2609.11900 Figure 5.

## 내 해석

논문 근거와 제 해석을 나눠서 적습니다.

논문이 보여주는 것은 명확합니다. 정적 장면 해석(추론)과 폐쇄 루프 행동(계획) 사이에는 측정 가능한 격차가 있고, 파인튜닝으로도 잘 좁혀지지 않습니다.

여기서 제 해석을 하나 붙이면, 이 결과는 GUI 에이전트나 로봇 조작 에이전트를 만드는 팀에 직접적인 시사점을 줍니다. 화면을 읽는 능력과 상태를 유지하며 행동하는 능력은 별개의 축입니다.

<span style="background-color: #fff59d"><strong>후자가 병목이면 모델 교체보다 하네스에서 상태 추적을 설계하는 게 먼저</strong></span>입니다. 영상 생성을 세계 모델로 쓰는 접근도 엔드포인트 성공만 보고 판단하면 안 됩니다. 과정 감사가 필요합니다.

한계도 있습니다. 씬이 전부 절차적 렌더링이라 실사진 다양성이 없고, 영상 생성 평가는 3개 모델에 국한됩니다. 방향·고차 곡면 같은 위상 인접 개념도 범위 밖입니다.

## 자주 묻는 질문

### MindTopo이 기존 공간 추론 벤치마크와 다른 점은 뭔가요?

거리·각도 같은 계량 속성 대신 연속변형에 불변하는 위상 관계를 측정 대상으로 삼았고, 같은 성질을 추론과 계획 두 수준에서 나눠 평가한다는 점이 다릅니다.

### 최고 성적이 어느 정도인가요?

Gemini 3.1 Pro가 전체 평균 53.5%로 최상위권입니다. 인간 97.4%와 비교하면 44%p 격차입니다. 논문 리더보드에서 GPT-5.5가 54.1%로 근소하게 앞선 구간도 있어, 최고 모델은 53~54% 수준으로 보면 됩니다.

### 파인튜닝하면 계획 능력도 오르나요?

Qwen3-VL-2B 실험에서 추론은 14.2%에서 51.5%까지 올랐지만 계획은 0.2%에서 6.3%에 그쳤습니다. Pipe 과제는 모든 학습 조건에서 0%였습니다.

### 영상 생성 모델을 월드모델로 쓸 수 있나요?

이 논문의 감사 결과로는 불가합니다. 1,560개 롤아웃에서 과정이 유효하면서 과제에 성공한 사례가 없었습니다. 최종 상태만 놓고 보면 그럴듯한 결과가 나오는 경우가 있어서 엔드포인트 평가만으로는 판단하면 안 됩니다.

### 데이터와 코드는 공개됐나요?

네. 코드는 GitHub(mll-lab-nu/MindTopo), 데이터셋은 HuggingFace(MLL-Lab/MindTOPO)에 공개돼 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고 자료

- 논문: [MindTopo: Can Foundation Models Reason in Topological Space? (arXiv 2609.11900)](https://arxiv.org/abs/2609.11900)
- 프로젝트 페이지: [mind-topo.github.io](https://mind-topo.github.io/)
- 코드: [github.com/mll-lab-nu/MindTopo](https://github.com/mll-lab-nu/MindTopo)
- 데이터셋: [HuggingFace MLL-Lab/MindTOPO](https://huggingface.co/datasets/MLL-Lab/MindTOPO)
