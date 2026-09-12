---
title: "Mr.LHDR: 최고 성능 딥리서치 에이전트도 43%에 그치는 장기 증거 사슬 벤치마크 (arXiv 2609.11318)"
date: 2026-09-12
tags:
  - llm-agents
  - deep-research
  - benchmark
  - multimodal
  - arxiv
draft: false
description: 문항당 평균 12.1개 필수 중간 결론과 의존 깊이 10.4로 장기 딥리서치를 측정한 Mr.LHDR 벤치마크. GPT-5.5도 OA 43.1%, o3 Deep Research는 32.4%에 그치는 결과와 이미지 절제 실험을 정리했다.
---

## 결론 먼저

Mr.LHDR(Multimodal real-world Long-Horizon Deep Research, arXiv 2609.11318, 2026-09-10 공개)는 실전 웹 기반 장기 딥리서치 능력을 평가하는 벤치마크다. 저자는 MBZUAI와 USTC 소속 Minghao Guo, Meng Cao 등이며 Tencent가 참여했다.

핵심은 구조다. 102문항, 8개 카테고리, 문항당 평균 12.1개의 필수 중간 결론, 의존 깊이 10.4. 최종 답은 짧고 유일하며 검증 가능하다. 각 문항에는 <span style="background-color: #fff59d"><strong>추론 상태를 바꾸는 비텍스트 증거(이미지, 지도, PDF, 로고, 차트, 표, 영상 프레임)가 최소 1개</strong></span> 포함된다.

결과: <span style="background-color: #fff59d"><strong>일반 모델 최고 성능인 GPT-5.5도 OA 43.1%, SA 34.3%</strong></span>. 딥리서치 시스템 최고인 o3 Deep Research는 OA 32.4%, SA 19.6%에 그친다. 최종 답 정확도가 전체 과정 성공을 크게 과대 평가한다는 것이 이 벤치마크의 핵심 발견이다.

## 핵심 수치

| 항목 | 값 |
|---|---|
| 문항 수 / 카테고리 | 102개 / 8개 (media, people, organizations, geography, society, academia, technology, sports) |
| 문항당 필수 중간 결론 | 평균 12.1개 (총 1,231개) |
| 의존 그래프 평균 깊이 | 10.4 |
| 최고 OA (일반 모델) | GPT-5.5: 43.1% (SA 34.3%) |
| 최고 OA (딥리서치 시스템) | o3 Deep Research: 32.4% (SA 19.6%) |
| 이미지 제거 시 DACS 변화 | 34.2% → 21.6% (−12.6pt, 95% CI [6.9, 18.9]) |
| 평가 시스템 수 | 25개 (툴증강 VLM, 툴프리 VLM, 딥리서치 시스템, 프레임워크 에이전트) |
| 심사 모델 | Qwen3-VL-235B |

기준일: 2026-09-12, arXiv v1(2026-09-10 게시) 기준.

## 기존 벤치마크와 다른 점

MM-BrowseComp는 문항당 체크리스트가 평균 3.0개로 중기 탐색에 머문다. BrowseComp 계열은 텍스트 중심이고, 증거가 주어지는 문서/RAG 벤치마크는 증거 탐색 자체를 측정하지 않는다.

Mr.LHDR은 다른 것을 잰다. 각 문항은 숨겨진 Node-Relation 그래프로 만들어지고, 에이전트는 열린 웹에서 증거를 찾아 중간 결론을 축적하며, 선행 결론이 만족되어야 후속 결론이 인정된다. 즉 이 벤치마크가 재는 것은 <span style="background-color: #fff59d"><strong>의존 연결된 증거 사슬을 끝까지 유지하는 능력</strong></span>이지, 긴 프롬프트 처리 능력이 아니다.

![Figure 1: MM-BrowseComp 예제는 체크리스트 4개, Mr.LHDR 예제는 두 개 선행 브랜치에 12개의 필수 결론이 필요하다](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-1-p3.png)

## 평가 지표: OA, SA, CS, DACS

이 논문의 평가 설계가 실무적으로 가장 흥미로운 부분이다.

| 지표 | 측정 내용 |
|---|---|
| OA (Overall Accuracy) | 최종 답 정확도 |
| SA (Strict Accuracy) | 답 + 필수 중간 결론 전부 응답에 명시 |
| CS (Checklist Score) | 중간 결론 커버리지 |
| DACS (Dependency-Aware CS) | 선행 결론이 만족된 경우만 후속 결론에 점수 |

DACS는 재귀적으로 각 결론의 선행 조건을 확인한다. Llama 4 Maverick은 CS 46.7%인데 DACS는 37.8%, Grok 4.20은 CS 69.3%에 DACS 62.4%다. <span style="background-color: #fff59d"><strong>전제가 빠진 하류 결론이 얼마나 많은지</strong></span>를 보여주는 지표다.

## 실험 결과

![Table 4: 25개 시스템 주요 결과. OA, SA, CS, DACS와 카테고리별 SA](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/table-4-p10.png)

OA–SA 갭이 핵심이다. GPT-5.5는 8.8pt, o4-mini는 14.7pt(35.3→20.6), o3 Deep Research는 12.8pt(32.4→19.6). <span style="background-color: #fff59d"><strong>최종 답은 맞았는데 필수 결론 전부를 담지 못한 응답이 그만큼 많다</strong></span>. 프레임워크 에이전트 그룹(DeerFlow 등)은 OA 15.7% 수준으로 더 낮다.

![Figure 4: OA를 SA와 잔차로 분해. 잔차는 정답이지만 필수 결론을 모두 명시하지 못한 응답](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-4-p12.png)

### 이미지 절제 실험

같은 모델(Qwen3-VL-235B)로 102문항을 이미지 있음/없음으로 각각 풀게 했다. CS는 26.9→39.3%(+12.4), DACS는 21.6→34.2%(+12.6). 부트스트랩 100% 구간에서 양수라 방향이 안정적이다. <span style="background-color: #fff59d"><strong>비텍스트 증거는 최종 답보다 증거 사슬 복원에 더 크게 기여한다</strong></span>는 점을 통제된 실험으로 보여준다.

![Figure 5: 이미지 유무에 따른 OA/CS/DACS 변화와 95% 부트스트랩 CI](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-5-p12.png)

### 체크리스트 길이 효과

관측치가 20개 이상인 구간에서는 모든 대표 모델에서 체크리스트가 길어질수록 SA가 단조 감소했다. 요구 결론 수가 늘수록 전체 체크리스트를 만족시키기가 점점 어려워진다.

![Figure 6: 체크리스트 길이 구간별 DACS와 SA](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-6-p13.png)

### 툴프리 Gemini 모델의 높은 DACS

Gemini 3.1 Pro는 툴 없이도 DACS 70.1%로 다른 툴프리 모델(29.0–37.8%)을 크게 앞선다. 대신 OA/SA는 낮다. <span style="background-color: #fff59d"><strong>중간 결론은 넓게 복원하는데 사슬을 완성하는 마지막 연결을 놓치는 패턴</strong></span>이다.

### 실패 유형 분석

실패한 체크리스트 항목에 진단 라벨을 붙인 결과, 툴증강 VLM과 딥리서치 시스템에서는 <span style="background-color: #fff59d"><strong>증거를 사전 지식으로 덮어쓰는 knowledge override가 지배적</strong></span>이었다. 의존 깊이 기준으로는 실패율이 전반 1/3에서 48.8%, 중반 55.3%, 후반 69.3%로 깊어질수록 악화한다.

![Figure 7: 모델 그룹별 실패 라벨 분포](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-7-p14.png)

## 데이터 구성

73문항(71.6%)은 Linear 템플릿, 29문항(28.4%)은 Multi-branch. 운영 태그는 Symbolic 79.4%, Constraint 74.5%, Numerical 29.4%, Temporal 17.6%. 가장 큰 카테고리는 media 21문항, geography 17문항이다.

![Figure 3: 카테고리, 작성 템플릿, 운영 태그 분포](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-3-p9.png)

![Table 3: 평가 대상 모델 그룹 요약](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/table-3-p9.png)

6인 주석팀(석박사 AI 연구자)이 Node-Relation 그래프 설계, 과잉 완성 체크리스트 초안, 소스/체크리스트/멀티모달/지름길/메타데이터 검문을 통과한 문항만 잠갔다. <span style="background-color: #fff59d"><strong>모든 문항의 체크리스트는 사람이 검증한 의존 DAG다</strong></span>.

![Figure 2: Mr.LHDR 구축 파이프라인. AI가 후보를 탐색하고 사람이 검증해 잠근다](/images/2026-09-12-mr-lhdr-long-horizon-deep-research/fig-2-p7.png)

## 한계와 해석

논문이 밝히는 한계는 명확하다. 프레임워크 에이전트 그룹이 단일 오픈소스 프레임워크로만 구성되어 일반화 불가. DACS는 명시된 결론의 의존 일관성을 잴 뿐 <span style="background-color: #fff59d"><strong>실제 검색 출처나 근거를 검증하지 않는다</strong></span>. 102문항이라 신뢰구간이 넓어 시스템 간 완전한 순위 결정은 불가능하다.

리서치 에이전트를 만드는 쪽에서 보면 실무적 시사점은 이렇다. 최종 답 정확도만 보면 하네스 개선 지점을 놓친다. 다음 병목은 중간 결론의 선행 조건을 보존하는 리서치 상태 추적, 출처·모달리티 바인딩, 분기별 선행 조건 유지, 사슬 수준 검증이다. 코드와 데이터는 GitHub(minghaoguo20/Mr-LHDR-eval)에 공개되어 있다.

## 자주 묻는 질문

### Mr.LHDR이 기존 딥리서치 벤치마크와 다른 점은 뭔가요?
문항당 평균 12.1개의 필수 중간 결론과 10.4의 의존 깊이로 장기 증거 사슬을 요구하고, 모든 문항에 추론 상태를 바꾸는 비텍스트 증거를 포함시킨 점이 다릅니다. MM-BrowseComp는 평균 체크리스트 3.0개입니다.

### 최고 성능 시스템의 점수는 얼마인가요?
일반 모델 중 GPT-5.5가 OA 43.1%, SA 34.3%로 최고였고, 딥리서치 시스템 중에서는 o3 Deep Research가 OA 32.4%, SA 19.6%로 최고였습니다. 2026-09-10 arXiv v1 기준입니다.

### DACS 지표는 무엇을 측정하나요?
Dependency-Aware Checklist Score의 약자로, 각 중간 결론에 점수를 주기 전에 그 결론의 선행 결론들이 응답에 올바르게 명시되었는지 재귀적으로 확인합니다. 전제 없는 결론을 걸러내는 지표입니다.

### 이미지 증거는 실제로 성능에 영향을 주나요?
같은 모델(Qwen3-VL-235B)로 102문항을 이미지 있음/없음으로 비교한 결과 DACS가 12.6pt 차이났고(34.2% vs 21.6%), 부트스트랩 95% CI가 [6.9, 18.9]로 양수였습니다.

## 출처

- 논문: [arXiv:2609.11318](https://arxiv.org/abs/2609.11318)
- 코드/데이터: [github.com/minghaoguo20/Mr-LHDR-eval](https://github.com/minghaoguo20/Mr-LHDR-eval)

## 더 실습해보고 싶은 분들께

딥리서치 에이전트, 긴 컨텍스트 에이전트, 루프 기반 자동화에 관심 있다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
