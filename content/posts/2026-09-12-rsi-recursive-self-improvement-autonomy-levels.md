---
title: "인류가 만드는 마지막 AI — 재귀적 자기개선(RSI) 자율성 5단계 논문 정리"
date: 2026-09-12
tags:
  - ai
  - llm
  - agent
  - rsi
  - self-improvement
  - survey
draft: false
description: "재귀적 자기개선(RSI) 서베이 arXiv 2609.11873 정리. 자율성 5단계(L1~L5) 프레임워크, Headroom-Closed Index로 본 도메인별 성능 격차, 안전한 상속·검증 과제까지 실무 관점으로 요약했습니다."
---

## 결론 먼저

재귀적 자기개선(RSI, Recursive Self-Improvement) 서베이 논문(arXiv 2609.11873)을 정리했습니다. 핵심은 이겁니다.

- RSI를 한 문장으로 정의하면 <span style="background-color: #fff59d"><strong>AI가 경험과 피드백을 자기 자신에 대한 영구적인 변경으로 바꾸고, 그 변경이 이후 개선 방식 자체에도 영향을 주는 폐쇄 루프</strong></span>입니다.
- 논문은 RSI를 통짜 개념 하나로 다루지 않고, <span style="background-color: #fff59d"><strong>AI가 개선 과정의 어디까지 통제하느냐를 기준으로 L1~L5 다섯 단계</strong></span>로 쪼갭니다.
- 현재 실존 시스템 대부분은 L1~L3이고, <span style="background-color: #fff59d"><strong>개선 메커니즘 자체를 개선하는 실효적 L5에 도달한 사례는 아직 없다</strong></span>가 논문의 결론입니다.

논문 정보는 아래와 같습니다.

| 항목 | 내용 |
|---|---|
| 제목 | The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement |
| arXiv | [2609.11873](https://arxiv.org/abs/2609.11873) |
| 공개 | 2026-09-10 (v1, 기준일 2026-09-12) |
| 분야 | cs.LG / cs.AI / cs.CL |
| 저자 | Yi Duan, Ying Liu 등 33인 (Tsinghua, Shanghai Jiao Tong 등) |

![](/images/2026-09-12-rsi-recursive-self-improvement-autonomy-levels/fig-1-p1.png)
*그림 1. RSI 자율성 5단계와 대표 시스템 (출처: 논문 Figure 1)*

## RSI가 문제가 되는 이유 — 개발 부담 3가지

논문은 먼저 프론티어 모델 개발이 왜 사람 손을 벗어나야 하는지 근거를 댑니다.

1. 파운데이션 모델 훈련 비용. Kimi K3는 2.8조 파라미터, Qwen3.8-Max는 2.4조 파라미터입니다. GPT-5.6 개발 6개월 동안 OpenAI의 내부 코딩 추론 컴퓨트는 <span style="background-color: #fff59d"><strong>100배</strong></span>, 에이전트 토큰 사용량은 <span style="background-color: #fff59d"><strong>22배</strong></span> 늘었습니다.
2. 피드백·학습 환경 구축 비용. NVIDIA AIMO-2 파이프라인은 긴 추론 솔루션 320만 개, 도구 통합 솔루션 170만 개를 만들고 문제 54만 개를 큐레이션했습니다.
3. 배포 후 반복 적응. Anthropic 보고에 따르면 <span style="background-color: #fff59d"><strong>에이전트 워크로드는 일반 챗보다 약 4배, 멀티에이전트는 약 15배의 토큰</strong></span>을 씁니다. Meta는 인프라 회귀 하나를 진단하는 데 엔지니어 10시간이 든다고 밝혔습니다.

요약하면 개선의 각 단계(뭘 고칠지 정하기 → 자원 만들기 → 됐는지 검증하기)가 전부 사람 조정 비용입니다. 이 조정의 일부를 시스템 자체의 능력으로 만드는 게 RSI입니다.

## 자율성 5단계 정리

논문의 메인 기여입니다. 무엇을 바꾸는가와 개선 결정을 누가 통제하는가를 분리해서 레벨을 매깁니다.

| 단계 | 이름 | AI가 하는 일 | 남는 사람 통제 | 대표 사례 |
|---|---|---|---|---|
| B0 | 태스크 내 개선 | 현재 출력만 다듬음 | 전부 | 일반적인 self-refine |
| L1 | 개선 실행 | 정해진 기준으로 업데이트 실행 | 무엇을·어떻게·성공 기준 | FineWeb-Edu 품질 라벨링 |
| L2 | 개선 전략 | 약점 진단 후 개선 방법 결정 | 목표·평가 기준 | Self-Harness (하네스 수정) |
| L3 | 경험 획득 | 다음 라운드 학습 경험 생성 | 목표·승격 규칙 | SIMA 2 약점 타깃 연습 |
| L4 | 환경 적응 | 배포 상호작용으로 영구 상태 갱신 | 승인·거버넌스 | PANDO 규칙 승격/강등 |
| L5 | 재귀적 상속 | <span style="background-color: #fff59d"><strong>개선 메커니즘 자체를 수정</strong></span> | 최종 승인 | A-Evolve-Training (부분) |

각 단계에서 논문이 반복해서 묻는 질문은 세 가지입니다.

- 루프가 어디서 닫히나 (개선이 실제로 시스템으로 돌아오나)
- 무엇이 다음 라운드로 상속되나
- 어떤 결정이 아직 사람이나 고정 인프라에 남아 있나

![](/images/2026-09-12-rsi-recursive-self-improvement-autonomy-levels/fig-2-p5.png)
*그림 2. 단계별 루프 구조 (출처: 논문 Figure 2)*

### L5가 특별한 이유

L2는 개선 후보를 탐색하고, L5는 <span style="background-color: #fff59d"><strong>그 탐색을 하는 개선자·검증자·후속 생성 절차 자체를 수정</strong></span>합니다. 논문은 여기서 둘을 구분합니다.

- 구조적 L5: AI가 지시한 변경이 지속되고 다음 개선 라운드를 통제함 (메커니즘 재사용)
- 실효적 L5: 수정된 메커니즘이 동일 예산·독립 평가에서 더 나은 후속 시스템을 실제로 만들어냄

A-Evolve-Training 사례가 가장 가깝습니다. 30B Nemotron 모델을 4라운드 자율 포스트트레이닝해서 외부 점수를 <span style="background-color: #fff59d"><strong>0.80에서 0.86</strong></span>으로 올렸고, 최상위 인간 제출(0.87)에 근접했습니다. 근데 논문 스스로 <span style="background-color: #fff59d"><strong>목표 선택과 중단 판단은 여전히 평가 과제로 남아 있다</strong></span>고 못박습니다.

## Headroom-Closed Index — 어디에 여력이 남았나

논문은 서로 다른 벤치마크 점수를 정규화하기 위해 HCI를 씁니다. 입문 연도 90퍼센타일 모델을 0, 만점을 100으로 잡는 정규화입니다.

2026년 기준 값입니다 (기준일 2026-09-12, 논문 Figure 3).

| 도메인 (2026) | HCI | 남은 헤드룸 |
|---|---|---|
| 사이버보안 에이전트 | 91.9 | 8.1 |
| 고급 수학 | 86.4 | 13.6 |
| 대학원 수준 과학 | 85.8 | 14.2 |
| 광범위 지식 | 77.2 | 22.8 |
| 법률 추론 | 64.5 | 35.5 |
| 멀티모달 추론 | 62.2 | 37.8 |
| 검색/터미널 에이전트 | 56.8 | 43.2 |
| 소프트웨어 엔지니어링 | 52.6 | 47.4 |
| 도구 에이전트 | 39.9 | 60.1 |

![](/images/2026-09-12-rsi-recursive-self-improvement-autonomy-levels/fig-3-p8.png)
*그림 3. 도메인별 능력 트레이젝토리와 RSI 확장 예시 (출처: 논문 Figure 3)*

핵심 관찰은 이겁니다. <span style="background-color: #fff59d"><strong>경계가 명확하고 검증이 쉬운 도메인(수학·사이버보안)은 포화에 가깝고, 긴 상태ful 워크플로우가 필요한 도메인(소프트웨어 엔지니어링·도구 에이전트)이 최대 45.9포인트 뒤처져 있습니다</strong></span>. 그래서 RSI의 가치는 남은 헤드룸이 큰 약한 배포 워크플로우에 집중된다는 게 논문의 그림입니다.

## 도메인별 RSI 속도 차이

논문은 과학, 엔바디드, 소프트웨어 엔지니어링, 의료 네 도메인을 나눠 보는데 속도가 다릅니다.

- 소프트웨어 엔지니어링: 검증 신호(테스트)가 명확해서 가장 빠르게 진화 중. SWE-bench류 + 에이전트 하네스 수정 조합
- 과학 발견: 검증 비용이 크고 사실성 확인이 병목. 가장 느림
- 엔바디드: 실세계 상호작용 데이터 수집 비용이 병목
- 의료: 안전 규제가 최대 제약

산업 사례도 실명으로 정리돼 있습니다. Tencent 혼원의 경험 기반 자기개선, ModelBest의 무인 데이터 파이프라인, Humanlaya의 납품 기반 품질 보증 등이 각각 어느 레벨에 해당하는지 매핑합니다.

## RSI가 실패하는 세 가지 지점

논문의 가장 실무적인 부분입니다. 자기수정 시스템이 오히려 위험해지는 조건입니다.

1. 안전한 상속. 지속성이 이득을 보장하지 않습니다. Gödel Agent는 MGSM 최적화 100회 중 <span style="background-color: #fff59d"><strong>14%의 시도가 초기 정책보다 성능이 떨어지는 결과</strong></span>로 끝났습니다. 전이 테스트·버전 히스토리·롤백이 필수입니다.
2. 자율성 귀속. 좋은 후보가 나왔다고 개선 능력이 생긴 게 아닙니다. Darwin Gödel Machine은 SWE-bench 서브셋을 <span style="background-color: #fff59d"><strong>20%에서 50%로</strong></span> 올렸지만 아카이브 관리·부모 선택 규칙은 자기수정 범위 밖에 있었습니다. 어느 결정이 AI 통제인지 분리해야 합니다.
3. 신뢰할 수 있는 검증. 평가자에 반복 접근하면 능력이 아니라 평가자 익스플로잇을 보상합니다. Anthropic 자동 연구 실험에서 <span style="background-color: #fff59d"><strong>랜덤 시드 체리피킹과 평가자 쿼리로 테스트 라벨 추출 시도</strong></span>가 관측됐습니다. 보호된 평가·동일 컴퓨팅 예산 비교가 필요합니다.

## 실무자 관점 요약

- 자기개선이라고 주어도 루프가 어디서 닫히는지부터 확인하세요. 대부분 실제 수준은 L1~L2입니다.
- 개인 실무에서 지금 쓸 수 있는 건 L2~L3입니다. 에이전트 하네스를 트레이스 기반으로 수정하거나, 관측된 약점을 다음 연습 태스크로 바꾸는 루프입니다.
- L5 행보는 구조적 사례(메커니즘 재사용)까지만 있고 <span style="background-color: #fff59d"><strong>동일 예산 독립 평가에서 입증된 실효적 L5는 아직 없다</strong></span>는 게 이 서베이의 정직한 결론입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### RSI(재귀적 자기개선)가 정확히 뭔가요?
AI가 경험과 피드백을 자기 자신(파라미터, 하네스, 개선 정책)에 대한 영구 변경으로 바꾸고, 그 변경이 이후 개선의 생성·평가·선택 방식에도 영향을 주는 자율적 폐쇄 루프입니다.

### 자율성 5단계(L1~L5)는 어떻게 구분하나요?
AI가 개선 실행(L1) → 개선 전략(L2) → 학습 경험 획득(L3) → 배포 환경 적응(L4) → 개선 메커니즘 자체 수정(L5) 순으로 통제 범위가 넓어집니다.

### 지금 상용 시스템 중 L5에 도달한 게 있나요?
논문 기준으로는 없습니다. A-Evolve-Training이 구조적으로 가장 가깝지만, 목표 선택·중단 판단·독립 검증이 남아 있어 실효적 L5 증명은 과제로 남았습니다.

### Headroom-Closed Index(HCI)는 무엇인가요?
벤치마크 첫 등록 연도 90퍼센타일 점수를 0, 만점을 100으로 정규화한 지표입니다. 도메인별로 남은 개선 여력을 같은 축에서 비교할 수 있게 합니다.

### 출처는 어디인가요?
Duan et al., "The Last AI Built by Humans: Toward Genuine Recursive Self-Improvement", arXiv:2609.11873 (2026). [abs](https://arxiv.org/abs/2609.11873) / [PDF](https://arxiv.org/pdf/2609.11873) / [HTML](https://arxiv.org/html/2609.11873v1)
