---
title: "AutoSaddler: 에이전트 실행 트레이스에서 하네스를 자동으로 고치는 오프라인 학습"
date: 2026-08-27
draft: false
tags:
  - agent
  - harness
  - llm
  - rl
description: "마이크로소프트·POSTECH·KAIST 공동의 AutoSaddler는 에이전트 하네스(프롬프트·도구·미들웨어)의 개선을 오프라인 학습 문제로 바꿔 GAIA2 +9.0%p, SWE-Bench Pro +9.6%p, Terminal-Bench 2.0 +10.0%p를 달성한 연구입니다."
---

## 핵심 요약

AutoSaddler(arXiv 2608.23041, Microsoft/POSTECH/KAIST, 2026)는 LLM 에이전트의 하네스(프롬프트, 도구, 미들웨어) 최적화를 <span style="background-color: #fff59d"><strong>실패 실행 트레이스 기반의 오프라인 학습 문제로 정의</strong></span>한 연구이다. GAIA2에서 +9.0%p, SWE-Bench Pro에서 +9.6%p, Terminal-Bench 2.0에서 +10.0%p의 Pass@1 향상을 보고했다.

또한 <span style="background-color: #fff59d"><strong>최고 개발 성적 도달에 소요된 롤아웃은 147개</strong></span>였다.

| 항목 | 값 |
| --- | --- |
| GAIA2 Pass@1 향상 | +9.0%p |
| SWE-Bench Pro 향상 | +9.6%p |
| Terminal-Bench 2.0 향상 | +10.0%p |
| 최고 성적 도달 롤아웃 수 | 147 |
| 비교 기법 최고 성적 | <span style="background-color: #fff59d"><strong>64.6%, 61.5% (약 2,800 실행)</strong></span> |

## 문제 정의

하네스는 에이전트의 성능에 큰 영향을 주지만 <span style="background-color: #fff59d"><strong>지금까지 최적화는 대부분 수작업</strong></span>이었다. 본 논문은 하네스 최적화를 <span style="background-color: #fff59d"><strong>미니배치 기반 오프라인 학습으로 재정식화</strong></span>하고, 반복적으로 실패 신호를 하네스 업데이트에 반영한다.

## 방법론

제안 방식은 세 구성요소로 이루어진다.

![AutoSaddler 파이프라인](/images/2026-08-27-autosaddler-harness-optimization-traces/fig-2-p5.png)

1. 증거 기반 진단(evidence-grounded diagnosis): 실패 트레이스로부터 <span style="background-color: #fff59d"><strong>원인을 근거와 함께 특정</strong></span>한다.
2. 구조화된 패치 생성(structured patching): 하네스를 <span style="background-color: #fff59d"><strong>코드로 취급하여 국소적 수정을 생성</strong></span>한다.
3. 일반화 인지 선택(generalization-aware selection): <span style="background-color: #fff59d"><strong>검증을 통과한 패치만 하네스에 반영</strong></span>한다.

## 실험 결과

세 벤치마크에서 기본 하네스 대비 <span style="background-color: #fff59d"><strong>일관된 향상</strong></span>이 확인되었다.

![메인 결과 비교](/images/2026-08-27-autosaddler-harness-optimization-traces/fig-1-p2.png)

옵티마이저 비용(런타임, 금액, LLM 호출 수)은 테이블 13에 정리되어 있다.

![옵티마이저 비용](/images/2026-08-27-autosaddler-harness-optimization-traces/table-13-p24-3.png)

어블레이션에 따르면 (1) 얕은 반성보다 <span style="background-color: #fff59d"><strong>깊은 디버깅</strong></span>, (2) 자유 수정보다 <span style="background-color: #fff59d"><strong>표적 수정</strong></span>, (3) 트레이지토리 수리보다 <span style="background-color: #fff59d"><strong>일반화 인지 선택</strong></span>이 각각 성능에 기여했다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**학습 대상은 모델 가중치입니까?**
아니요. <span style="background-color: #fff59d"><strong>프롬프트, 도구, 미들웨어로 구성된 하네스</strong></span>입니다.

**온라인 RL과의 차이는 무엇입니까?**
수집된 실패 트레이스로 오프라인 학습하며, <span style="background-color: #fff59d"><strong>147개 롤아웃으로 최고 성적에 도달</strong></span>했습니다.

**공개 자료는 어디에서 확인할 수 있습니까?**
arXiv 2608.23041 및 프로젝트 페이지(aka.ms/AutoSaddler-website)에서 확인할 수 있습니다.

## 참고 자료

- [arXiv:2608.23041](https://arxiv.org/abs/2608.23041) (기준일 2026-08-27)
- [프로젝트 페이지](https://aka.ms/AutoSaddler-website)
