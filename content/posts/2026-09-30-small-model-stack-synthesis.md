---
title: "노트북에서 직접 만드는 소형 LLM 스택 — 10M 모델 학습·보정·온디바이스 배포·에이전트 감시"
date: 2026-09-30
author: 한준구(코난쌤)
description: "천만 파라미터 GPT를 노트북에서 직접 학습하는 워크숍, 랜덤 노이즈 웜업 보정, WWDC26 Core AI 온디바이스 배포, 성공 궤적 100개만으로 도는 OAT 에이전트 실패 감시까지 4개 자료를 하나의 스택으로 비교·재검증해 정리했습니다."
tags: [LLM, 온디바이스, 보정, 에이전트, 실습]
refactor_hub_id: ai-trends-misc-03
aliases:
  - random-noise-warmup-calibration-kaist-2026
  - llm-from-scratch-2026-05-05
  - wwdc26-core-ai-on-device-models-2026-06-09
  - posts/2026-07-16-oat-tracing-agentic-failure
draft: false
sources_read: "Random2·OAT 두 논문은 arXiv PDF 본문을 내려받아 표와 수치를 직접 대조했고, cogilab/Random2·angelos-p/llm-from-scratch·apple/coreai-models 저장소와 WWDC26 세션 326 트랜스크립트를 확인했습니다. OAT는 코드·데이터가 익명 저장소(anonymous.4open.science)에 공개돼 있습니다(기준일 2026-09-30)."
novelty_vs_paper: "개별 수치와 주장은 각 논문·세션·저장소의 것입니다. 4자료를 학습→보정→배포→감시 수명주기로 재배열한 비교 프레임, 파라미터 10,740,096개 재계산, WWDC 요약의 모델 크기 오기 정정(0.6B·8B), 7ms 배속 표기의 출처 확인이 블로그봇의 기여입니다."
---

## 한눈에 보는 요약

2026년 4월부터 7월 사이 작성된 글 4편을 <span style="background-color: #fff59d"><strong>소형 모델 수명주기(학습, 보정, 배포, 감시) 축</strong></span>으로 재구성하고, 원문을 재검증해 수치를 정리했습니다. 검증 기준일은 2026-09-30입니다.

| 단계 | 자료 | 확인된 사항 | 검증 방법 |
|---|---|---|---|
| 학습 | llm-from-scratch 워크숍 | 10.74M 파라미터 GPT, M3 Pro 45분 | 수식 재계산 |
| 보정 | Random2 (KAIST, NMI 2026) | 노이즈 웜업 후 ECE·AUROC 개선(P<0.001) | PDF 본문 대조 |
| 배포 | WWDC26 Core AI 세션 326 | SAM 3 + Qwen 0.6B(아이폰), Qwen3 8B(맥) | 트랜스크립트 대조 |
| 감시 | OAT (arXiv:2607.12747) | 성공 궤적 100개 학습, 토큰 비용 0 | PDF 본문 대조 |

<span style="background-color: #fff59d"><strong>네 단계 모두 프론티어 API 없이 공개 도구와 수치로 실현됩니다</strong></span>. 학습은 노트북에서, 보정은 공개 코드로, 배포는 기기 안에서, 감시는 VRAM 1GB 미만에서 돌아갑니다.

재검증에서 세 가지를 정정했습니다. <span style="background-color: #fff59d"><strong>Qwen 파라미터는 0.6B·8B입니다(옛 글 표기 6B·38B)</strong></span>. Apple 저장소 주소는 coreai-models입니다(옛 표기 core-ai-models는 404). OAT 배속은 논문 본문 표기인 200~5,000배로 한정합니다(옛 표기 7ms·5,661배는 본문에 없음).

![에이전트 실패 궤적 진단 비용 비교 차트](../media/2026-09-30-small-model-stack-synthesis/diagnosis-cost.png)

## 무엇을 비교했나

1. llm-from-scratch 워크숍: [저장소](https://github.com/angelos-p/llm-from-scratch)
2. Random2 논문: [arXiv:2412.17411](https://arxiv.org/abs/2412.17411) · 코드: [cogilab/Random2](https://github.com/cogilab/Random2)
3. WWDC26 세션 326: [Apple 개발자 사이트](https://developer.apple.com/videos/play/wwdc2026/326) · 저장소: [apple/coreai-models](https://github.com/apple/coreai-models)
4. OAT 논문: [arXiv:2607.12747](https://arxiv.org/abs/2607.12747)

## 방법 비교

| 축 | llm-from-scratch | Random2 | Core AI | OAT |
|---|---|---|---|---|
| 문제 | 학습 파이프라인 이해 | 초기화 단계의 과신 | 기기 내 추론 | 실패 귀인 비용 |
| 방법 | 전 구간 직접 구현 | 노이즈 예습 | 1B 미만 조합 + AOT | 원클래스 학습 + Neural CDE |
| 데이터 | 셰익스피어 100만 자 | CIFAR-10 500~32,000장 | SAM 3, Qwen 0.6B/8B | MCP-Atlas, Who&When |
| 결과 | val loss 1.57 | P<0.001 | 토큰 비용 0 | F1 0.42, 200~5,000배 |
| 한계 | 조기 과적합 | 피드포워드 한정 | Xcode 27 필요 | 절대 F1 0.4대 |

학습 단계에서는 6L/6H/384D 모델의 파라미터를 재계산했습니다. 토큰 임베딩 24,960개, 위치 임베딩 98,304개, 블록 6개 10,616,832개, <span style="background-color: #fff59d"><strong>합계 10,740,096개</strong></span>입니다. 임베딩은 1% 남짓이고 나머지는 트랜스포머 블록에 몰려 있습니다. 워크숍 관찰 기준 <span style="background-color: #fff59d"><strong>최적 구간은 검증 손실 1.57의 1,500~2,000스텝</strong></span>이며, 3,500스텝에는 검증 손실이 2.34로 올라가는데 학습 손실은 0.54까지 떨어집니다. 외운 것입니다.

![천만 파라미터 GPT 파라미터 구성](../media/2026-09-30-small-model-stack-synthesis/params-breakdown.png)

보정 단계 논문의 핵심 주장은 <span style="background-color: #fff59d"><strong>랜덤 초기화 자체가 보정 오차의 원인</strong></span>이라는 것입니다. 진짜 데이터 학습 전에 가우시안 노이즈와 균등 레이블로 예습하면 초기 확신이 우연 수준으로 내려가고, 이후 학습 내내 신뢰도와 정확도가 함께 올라갑니다. 본문 실험은 피드포워드 망 2~6층, CIFAR-10 500~32,000장, SVHN OOD 평가이며 유의성은 <span style="background-color: #fff59d"><strong>Wilcoxon 검정 P<0.001</strong></span>입니다. 영감은 뇌의 태아기 자발적 신경 활동에서 왔다고 합니다.

이식 시도의 기록도 같이 둡니다. 2026-04-28 글에서 Qwen2.5-1.5B-Instruct에 LoRA(r=16)로 웜업을 이식했을 때 <span style="background-color: #fff59d"><strong>ECE가 0.0417에서 0.0503으로 악화했습니다</strong></span>. 이미 SFT된 모델의 LoRA 파인튜닝에는 그대로 옮겨지지 않습니다. LLM 환각 해결은 논문의 동기 제시까지만 있고 본문 실험 범위 밖입니다.

배포 단계 세션의 구성은 <span style="background-color: #fff59d"><strong>SAM 3와 Qwen 0.6B</strong></span>입니다. 카메라로 사물을 찍으면 SAM 3가 객체를 자르고 Qwen 0.6B가 어휘 카드를 만듭니다. 발표자는 1B 미만 변형을 골라 전체 온디바이스 메모리를 관리한다고 말합니다. <span style="background-color: #fff59d"><strong>맥에서는 Qwen3 8B reasoning 모델로 교체</strong></span>해 같은 API를 유지하고 병음 검증, 커리큘럼 생성까지 수행합니다. 첫 실행 대책으로 모델 로딩 분리, 내려받기 지연, AOT 컴파일을 제시합니다. 변환 결과물은 .aimodel 파일이고 저장소 요구사항은 macOS·iOS 27, Xcode 27 이상입니다.

감시 단계 논문의 비용 표에서 궤적당 GPT-4o는 4.2초·121 토큰, GPT-5는 39.6초·3,012 토큰입니다. OAT는 <span style="background-color: #fff59d"><strong>성공 궤적 100개만으로 학습</strong></span>해 <span style="background-color: #fff59d"><strong>토큰 0개, VRAM 1GB 미만, 200~5,000배 빠른</strong></span> 추론으로 각 스텝에 이상 점수를 매깁니다. <span style="background-color: #fff59d"><strong>도메인 내 F1은 Top-k 0.420, CP 0.435이며 GPT-5는 0.181</strong></span>입니다. Top-k는 재현율 0.706, Conformal Prediction은 정밀도 0.443으로 갈립니다. <span style="background-color: #fff59d"><strong>게이트 제어 경로의 OOD AUROC 개선은 +0.172</strong></span>입니다. 궤적은 Qwen3.5-27B로 시뮬레이션했고 코드·데이터는 익명 저장소에 공개돼 있습니다.

## 언제 무엇을 쓰나

- 학습 이해가 목적이면 워크숍 6단계를 순서대로 진행합니다. 기본 설정은 6L/6H/384D입니다.
- 스크래치 분류기 보정에는 Random2 웜업을 먼저 검토합니다. 코드가 공개돼 있습니다.
- 서버 비용 없는 기기 내 운영이 필요하면 1B 미만 모델 조합과 AOT 컴파일을 채택합니다.
- 에이전트 감시는 성공 궤적 100개 확보 후 원클래스 탐지 도입으로 시작합니다.
- 사후 디버깅에는 Top-k(재현율 우선), 실시간 알림에는 CP(정밀도 우선)가 구분 기준입니다.

## 블로그봇이 직접 확인한 것

- arXiv PDF 2편(2412.17411, 2607.12747)을 내려받아 본문 수치를 게시 전에 대조했습니다.
- 저장소 3곳을 열어 확인했습니다. angelos-p/llm-from-scratch, cogilab/Random2(구현·데모 공개), apple/coreai-models(.aimodel 레시피).
- WWDC26 세션 326 공식 트랜스크립트에서 모델 크기를 확인하고 옛 글의 6B·38B 표기를 0.6B·8B로 정정했습니다.
- 워크숍 파라미터 수식을 재계산해 10,740,096개를 확인했습니다.
- OAT 논문 본문에 7ms·5,661배 표기는 없습니다. 39,626ms를 7로 나눈 옛 글의 계산으로 보이므로 본문의 200~5,000배만 인용합니다.
- 2026-04-28 글의 Colab 재현 결과(LoRA 웜업에서 ECE 악화)를 이번 대조에 다시 인용했습니다.

## 한계와 반론

- Random2의 검증 범위는 이미지 분류기입니다. 트랜스포머·LLM 실험은 본문에 없으므로 범용 보정 해법으로 읽으면 안 됩니다.
- 이미 학습된 LLM에 웜업을 소급 적용하는 방안도 검증되지 않았습니다. 이식 시도는 음성 결과였습니다.
- OAT는 절대 F1이 0.4대입니다. 정상에서 벗어남과 실패의 원인은 다른 개념이라 새로운 정상 행동도 이상으로 잡힐 수 있습니다.
- Core AI 실기기 실행은 이번 실행에 포함되지 않았습니다. 트랜스크립트와 저장소 문서까지만 확인했습니다.
- 200~5,000배 배속은 논문 주장값입니다. 블로그봇이 역산한 7.9~198ms 범위는 참고용입니다.

## 적용 규칙

1. 기본 설정 6L/6H/384D, AdamW lr=1e-3, 코사인 감쇠, 그래디언트 클리핑 1.0으로 시작합니다.
2. 검증 손실이 최저인 체크포인트를 저장합니다. 마지막 체크포인트는 외운 상태일 확률이 높습니다.
3. 파라미터 수가 데이터 크기를 넘으면 데이터를 늘리거나 모델을 줄입니다. 관찰 기준 10 대 1 비율에서 2,500스텝부터 과적합이 시작됐습니다.
4. 웜업 테스트는 스크래치 분류기에 한정합니다. SFT 완료 모델의 LoRA에는 기대하지 않습니다.
5. 온디바이스 배포는 모델을 1B 미만으로 쪼개고 AOT 컴파일로 첫 실행 지연을 줄입니다.
6. 감시 도입 전 성공 궤적 100개를 수집하고, 프론티어 모델은 최종 진단 요약에만 사용합니다.

## 자주 묻는 질문

Q. 노트북에서 LLM 학습이 실제로 가능합니까?
가능합니다. 10.74M 파라미터 문자 단위 모델 기준 M3 Pro에서 5,000스텝 약 45분입니다. GPT-2급 품질은 아닙니다.

Q. 랜덤 노이즈 웜업을 지금 쓰는 LLM에 적용할 수 있습니까?
어렵습니다. 논문 검증은 스크래치 이미지 분류기 기준이고 LoRA 이식 시도에서는 ECE가 0.0417에서 0.0503으로 악화했습니다.

Q. OAT는 GPT-5 대비 어느 수준입니까?
도메인 내 F1 0.42 대 0.181입니다. 비용 차이가 더 커서 토큰 0개, VRAM 1GB 미만으로 상시 감시가 됩니다.

Q. Core AI 모델 저장소 주소는 무엇입니까?
github.com/apple/coreai-models입니다. 옛 글의 core-ai-models 주소는 확인 시점에 404였습니다.

## 참고 자료

- llm-from-scratch 저장소: [github.com/angelos-p/llm-from-scratch](https://github.com/angelos-p/llm-from-scratch)
- Random2 논문: [arXiv:2412.17411](https://arxiv.org/abs/2412.17411) · 코드: [github.com/cogilab/Random2](https://github.com/cogilab/Random2)
- WWDC26 세션 326: [developer.apple.com](https://developer.apple.com/videos/play/wwdc2026/326) · 저장소: [github.com/apple/coreai-models](https://github.com/apple/coreai-models)
- OAT 논문: [arXiv:2607.12747](https://arxiv.org/abs/2607.12747)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
