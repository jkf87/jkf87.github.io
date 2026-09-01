---
title: "Diff Mining — 파인튜닝 로짓 차이만으로 숨은 학습 목적을 잡아내는 방법"
date: 2026-09-01
draft: false
tags: [interpretability, finetuning, llm, auditing]
description: "파인튜닝 모델과 베이스 모델의 로짓 차이를 모아 토큰 세트를 뽑아 숨은 파인튜닝 목적과 편향을 감지하는 Diff Mining 논문(arXiv:2608.26462)을 정리했습니다."
---

## 결론 먼저

Diff Mining(arXiv:2608.26462, ICLR 2026 Workshop "Principled Design for Trustworthy AI")은 파인튜닝 모델과 베이스 모델의 <span style="background-color: #fff59d"><strong>출력 로짓 차이를 집계</strong></span>해, 해당 파인튜닝이 무엇을 학습했는지 나타내는 토큰 세트를 구성하는 프레임워크입니다. <span style="background-color: #fff59d"><strong>모델 내부 접근이 필요 없으며 출력 로짓만으로 동작</strong></span>하여 대형 모델에 적용할 수 있습니다.

보고된 주요 결과는 다음과 같습니다.

- 파인튜닝 데이터에 사전학습 데이터를 희석해 섞는 비율(ft:pt 1:0 ~ 1:2) <span style="background-color: #fff59d"><strong>전 구간에서 Top-K Diff Mining이 기존 방법인 ADL보다 많은 관련 토큰을 발견</strong></span>했고, 해당 토큰 세트를 사용한 인터프리터빌리티 에이전트 성능도 전 구간에서 우위였습니다.
- 적대적 후속학습으로 편향을 숨긴 Llama 3.3 70B Instruct(Sheshadri et al. 2025 오픈소스 재현)에서, 타겟 프로빙 없이 단일 비지도 패스로 <span style="background-color: #fff59d"><strong>52개 숨은 편향 중 약 3분의 1</strong></span>에서 의미적으로 관련된 토큰을 식별했습니다.
- 여러 도메인을 섞어 파인튜닝한 경우 <span style="background-color: #fff59d"><strong>NMF 집계가 각 목적을 별도 토큰 클러스터로 분리</strong></span>했습니다.

기준일: 2026-09-01, 논문 v1 기준. 코드는 github.com/science-of-finetuning/diffing-toolkit에 공개되어 있습니다.

## 핵심 정보 표

| 항목 | 내용 |
| --- | --- |
| 프레임워크 | Diff Mining (2단계: 로짓 차이 추출 → 집계) |
| 요구 접근 수준 | <span style="background-color: #fff59d"><strong>출력 로짓 (내부 가중치·활성화 불필요)</strong></span> |
| 집계 방법 | Top-K 빈도, NMF |
| 비교 대상 | ADL (Minder et al. 2026 벤치마크) |
| 편향 탐지 결과 | <span style="background-color: #fff59d"><strong>Llama 3.3 70B, 52개 중 약 1/3</strong></span> |
| 스케일링 실험 기본값 | N=1000 문서, T=30 토큰 위치, Top-K=100, Qwen3 1.7B |
| 평가 프로토콜 | 관련 토큰 5시드 × 3순열=15회 평균, gpt-5-mini 1–5 루브릭 채점 |
| 공개 저장소 | science-of-finetuning/diffing-toolkit |

## 방법

### 1단계: 로짓 차이 추출

참조 코퍼스에서 무작위로 문서를 표본 추출해 베이스 모델과 파인튜닝 모델에 각각 통과시키고, 동일 문맥에서의 per-context 로짓 차이를 수집합니다. <span style="background-color: #fff59d"><strong>파인튜닝 도메인과 무관한 코퍼스를 사용해도 학습된 토큰의 로짓 상승이 관찰</strong></span>됩니다. 스케일링 실험의 기본 설정은 <span style="background-color: #fff59d"><strong>문서 1,000개, 각 문서 앞 30 토큰 위치</strong></span>입니다.

### 2단계: 집계

- Top-K 빈도: 가장 자주 로짓이 상승한 토큰 K개로 토큰 세트 V를 구성합니다(<span style="background-color: #fff59d"><strong>기본 K=100</strong></span>).
- NMF: 로짓 차이 행렬을 비음수 행렬분해하여 여러 파인튜닝 목적을 별개 토큰 클러스터로 분리합니다.

![Figure 1: 희석 비율에 따른 Top-K Diff Mining과 ADL 비교](/images/diffmining-logit-differences-2026-09-01/fig-1-p6.png)

Figure 1은 희석 비율 변화에 따른 비교 결과입니다. 왼쪽이 관련 토큰 비율, 오른쪽이 인터프리터빌리티 에이전트 점수이며 <span style="background-color: #fff59d"><strong>두 지표 모두 전 구간에서 ADL 대비 우위</strong></span>를 보입니다.

## 평가 설정

평가는 Minder et al. 2026의 벤치마크와 인터프리터빌리티 에이전트, 가설 채점기(gpt-5-mini, 1–5 루브릭)를 사용합니다. 에이전트는 베이스/파인튜닝 모델에 쿼리할 수 있으며, 토큰 세트 V의 노출 여부만을 실험 변수로 둡니다. 관련 토큰 점수는 데이터 샘플링 5시드 × 토큰 순서 3순열, 총 15회 측정의 평균입니다.

![Figure 2: 스케일링 법칙](/images/diffmining-logit-differences-2026-09-01/fig-2-p14.png)

Figure 2는 문서 수, 토큰 위치 수, K 등 파라미터별 스케일링 법칙을 보여줍니다.

## 실제 파인튜닝 사례 연구

여러 도메인이 혼합된 실제 파인튜닝에서도 토큰 세트가 각 도메인의 특성을 반영했습니다. Figure 3은 SDF, Cat Loving Supervised 등 실제 파인튜닝에서 선택된 토큰 세트 예시입니다.

![Figure 3: 실제 파인튜닝에서 선택된 토큰 세트](/images/diffmining-logit-differences-2026-09-01/fig-3-p16.png)

편향 탐지 사례에서는 보상 모델에 대한 거짓 믿음 52개가 주입되고 적대적 후속학습으로 은폐된 Llama 3.3 70B Instruct 대상으로, Top-K Diff Mining이 숨은 목적과 강하게 연결된 토큰을 <span style="background-color: #fff59d"><strong>최소 3분의 1 이상의 편향에서 식별</strong></span>했습니다.

![Figure 7: 토큰별 로짓 차이 분포](/images/diffmining-logit-differences-2026-09-01/fig-7-p26.png)

Figure 7은 단일 토큰 수준의 로짓 차이 분포로, <span style="background-color: #fff59d"><strong>학습된 토큰('cake')과 무관 토큰의 분포가 명확히 구분</strong></span>됨을 보여줍니다.

## 해석

이하는 원문 결과가 아닌 작성자 해석입니다.

- 감사 도구로의 실용성: <span style="background-color: #fff59d"><strong>로짓 접근만으로 오픈 웨이트 모델의 숨은 목적 1차 스크리닝이 가능</strong></span>하다는 점에서 감사 파이프라인의 문턱이 낮아집니다.
- 비용 구조: 수십만 토큰 수준의 forward로 동작하므로 대형 모델에도 적용 가능한 계산 예산입니다.
- 한계: <span style="background-color: #fff59d"><strong>탐지율 약 1/3은 과반 편향을 놓친다는 의미</strong></span>이며, 적대자가 이 방법 자체를 회피하도록 학습하는 시나리오는 별도 검증이 필요합니다. 논문도 완결된 탐지기가 아닌 <span style="background-color: #fff59d"><strong>감사 도구 개발 방향</strong></span>으로 위치시키고 있습니다.

## 자주 묻는 질문

**Q. 모델 가중치 접근이 필요한가요?**
아니요. <span style="background-color: #fff59d"><strong>베이스 모델과 파인튜닝 모델의 출력 로짓 접근만 필요</strong></span>합니다.

**Q. 참조 코퍼스는 파인튜닝 도메인과 관련 있어야 하나요?**
아니요. 무관한 코퍼스에서도 학습된 토큰의 로짓 상승이 관찰됩니다.

**Q. 숨긴 편향을 모두 탐지하나요?**
아니요. 적대적으로 은폐된 설정에서 약 3분의 1 수준의 관련 토큰 식별이 보고되었습니다.

**Q. 기본 실험 설정은 어떻게 되나요?**
문서 1,000개, 토큰 위치 30개, Top-K=100이며 Qwen3 1.7B 모델 유기체로 검증되었습니다.

## 더 실습해보고 싶은 분들께

모델 디핑·인터프리터빌리티 실험도 결국 에이전트 파이프라인 위에서 돌아갑니다. 에이전트 자동화를 더 파보고 싶다면 두 자료를 추천합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 논문: https://arxiv.org/abs/2608.26462
- 코드: https://github.com/science-of-finetuning/diffing-toolkit
- Minder et al. 2026 (벤치마크 및 인터프리터빌리티 에이전트)
- Sheshadri et al. 2025 (편향 주입 모델 오픈소스 재현)
