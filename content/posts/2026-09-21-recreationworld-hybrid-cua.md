---
title: "GUI 에이전트와 코딩 에이전트를 하나로: RecreationWorld 하이브리드 CUA 벤치마크 정리"
date: 2026-09-21
draft: true
description: "Alibaba Token Hub의 RecreationWorld 논문(arXiv 2609.22000) 정리. 5개 플랫폼 250태스크로 하이브리드 컴퓨터 사용 에이전트를 평가하고 35,000 트레이젝토리로 학습해 OOD 벤치마크까지 전이시킨 결과를 정리했습니다."
tags:
  - GUI-agent
  - computer-use-agent
  - benchmark
  - agent
  - LLM
  - harness
  - rl
refactor_hub: web-gui-agents-01
refactor_status: queued
---

## 결론 먼저

RecreationWorld(Alibaba Token Hub, arXiv 2609.22000, 2026-09-18 공개)는 하이브리드 컴퓨터 사용 에이전트(CUA)의 평가와 학습을 위한 프레임워크입니다. 하이브리드 CUA란 <span style="background-color: #fff59d"><strong>GUI 조작과 코드·명령줄 작업을 단일 롱호라이즌 프로세스에서 상호 전환하며 수행하는 에이전트</strong></span>를 의미합니다.

논문은 재현(recreation) 태스크, 즉 <span style="background-color: #fff59d"><strong>실행 중인 레퍼런스 애플리케이션의 동작을 발견하고 이를 코드로 재구현하는 과제</strong></span>를 통해 이 능력을 측정합니다.

| 항목 | 내용 |
| --- | --- |
| 프레임워크 | RecreationWorld (Ubuntu, macOS, Windows, Android, Web) |
| 평가 벤치마크 | RecreationBench 250 태스크 (플랫폼당 50개) |
| 최고 성능 | GPT-6 Astra 평균 58.06% |
| 완전 통과율 | 최고 모델도 Prog 100%는 2.8% |
| 학습 데이터 | 35,000 트레이젝토리 (플랫폼당 7,000) |
| OOD 전이 | 5개 벤치마크에서 최대 +17.9pp |

## 태스크 정의

에이전트는 (1) 실행 중인 레퍼런스 앱(소스 비공개), (2) GUI 제어와 코딩 도구를 갖춘 작업 환경을 받습니다. 태스크 수행 중 GUI 탐색, 코드 작성, 빌드·실행, 시각 검증 사이를 자유롭게 이동할 수 있으며 <span style="background-color: #fff59d"><strong>작업 순서는 규정되지 않습니다</strong></span>.

![하이브리드 에이전트의 explore-implement-verify 루프](/images/2026-09-21-recreationworld-hybrid-cua/fig-2-p2.png)

산출물은 플랫폼별 빌드 계약을 충족하는 전체 소스 제출물입니다. 데스크톱은 소스+빌드/런치 스크립트, Android는 Gradle APK, Web은 단일 index.html입니다.

## 평가 방법

평가는 레퍼런스에서 유도된 동결된 히든 테스트 수트로 수행됩니다. <span style="background-color: #fff59d"><strong>레퍼런스 앱 자체가 오라클 역할</strong></span>을 한다는 점이 이 프레임워크의 핵심 설계입니다.

![레퍼런스 기반 히든 테스트 생성 과정](/images/2026-09-21-recreationworld-hybrid-cua/fig-4-p5.png)

절차는 다음과 같습니다.

1. 오케스트레이터가 레퍼런스 실행을 탐색해 동작 인벤토리를 구성한다.
2. 플랫폼별 생성기가 프로그래매틱 assertion(AT-SPI, AXUIElement, UI Automation, UiAutomator)과 VLM visual assertion을 작성한다.
3. 모든 케이스는 레퍼런스에서 재생 검증과 인간 검토를 통과한 뒤 동결된다.

테스트 수트 통계(5플랫폼 평균): <span style="background-color: #fff59d"><strong>77.2%의 케이스가 시작 화면을 벗어나며</strong></span> (1홉 53.2%, 2홉 이상 24.1%), 94.2%가 상호작용 결과를, 40.7%가 정확한 기대값을 요구합니다. "버튼이 있나" 수준이 아니라 <span style="background-color: #fff59d"><strong>계산된 값까지 정확히 일치하는지</strong></span> 검사하는 구조입니다.

## 주요 결과

RecreationBench에서 10개 프론티어 모델을 평가한 결과는 다음과 같습니다.

![RecreationBench 주요 결과 테이블](/images/2026-09-21-recreationworld-hybrid-cua/table-3-p11.png)

| 모델 | Prog (%) | VLM (%) | 평균 (%) |
| --- | --- | --- | --- |
| GPT-6 Astra | 58.19 | 57.92 | 58.06 |
| Claude Opus 5 | 45.99 | 42.34 | 44.16 |
| GPT-5.6 Sol | 40.63 | 43.49 | 42.06 |
| Qwen3.8-Max-0902 | 39.02 | 34.45 | 36.73 |
| Gemini 3.7 Flash | 32.07 | 30.74 | 31.41 |
| Claude Opus 4.8 | 32.40 | 29.81 | 31.10 |
| Qwen3.7-Plus | 26.30 | 22.46 | 24.38 |
| GLM-5.3 | 24.91 | 17.34 | 21.12 |
| Kimi K3 | 9.18 | 9.12 | 9.15 |

GPT-6 Astra는 Prog 90% 이상 통과 태스크가 17.6%, Prog 100% 통과가 2.8%로 유일하게 복수 플랫폼에서 완전 통과를 기록했으나 절대 수준은 낮습니다. <span style="background-color: #fff59d"><strong>1위 모델조차 완전 재현은 2.8%</strong></span>라는 점이 이 벤치마크의 현 주소입니다.

## 분석 결과

정적 인터페이스 구조는 상대적으로 잘 재현되지만 <span style="background-color: #fff59d"><strong>상호작용과 계산 출력의 재현이 어렵습니다</strong></span>. 재현물의 89.4%가 레퍼런스보다 적은 프로덕션 소스를 포함하며(중간 LOC 비율 16.9%), 92.3%가 더 적은 파일을 사용합니다. 즉 <span style="background-color: #fff59d"><strong>재현된 앱은 원본보다 작고 단조롭다</strong></span>는 결과입니다.

최종 소스 수정 후 재실행·재검증을 완료하는 트레이젝토리 비율은 <span style="background-color: #fff59d"><strong>전 모델에서 50% 미만</strong></span>입니다(최고 Qwen3.8-Max-0902 47.5%). 트레이젝토리 중앙값은 282.5 톱레벨 툴콜이며 GUI-코드 편집 전환은 100콜당 9.08회입니다. 근접 벤치마크 WeaveBench는 178콜, 1.56회 전환으로 비교됩니다.

## 학습 실험: 35,000 트레이젝토리

Qwen3.8-Max로 재현 롤아웃을 생성하고 행동 검증기로 리젝션 샘플링해 <span style="background-color: #fff59d"><strong>플랫폼당 7,000개, 총 35,000 트레이젝토리의 SFT 데이터</strong></span>를 구축했습니다.

두 초기화(Qwen3.7-Plus, Qwen-Flash-CPT)를 학습한 결과 <span style="background-color: #fff59d"><strong>ProgramBench, GameCraft-Bench, Vision2Web, OSWorld 2.0, WeaveBench 5개 OOD 벤치마크에서 모두 상승(최대 +17.9pp)</strong></span>했으며, 자기 산출물의 렌더링 확인 빈도도 증가했습니다. 재현 태스크가 실행 기반 보상을 내장해 별도의 사람 라벨 없이 검증된 경험을 계속 뽑아낼 수 있다는 게 확장성 포인트입니다.

추가로 Windows 50앱에서 Direct MCP와 프로그래머블 SDK(JavaScript REPL) 구성을 비교했습니다. 태스크 품질은 유지되면서 <span style="background-color: #fff59d"><strong>컴퓨터-유스 콜 -39.9%, 입력 토큰 -40.7%, 추정 비용 $90.50→$41.58</strong></span>의 절감을 관측했습니다.

![Direct MCP vs 프로그래머블 SDK 비교](/images/2026-09-21-recreationworld-hybrid-cua/fig-9-p11.png)

GUI 하네스 설계에 바로 적용할 수 있는 교훈입니다. 관찰을 매번 컨텍스트로 흘려보내지 않고 런타임에서 걸러 돌려주는 구조가 비용과 시간을 절반 가까이 줄입니다.

## 결론 및 한계

RecreationWorld는 GUI 탐색, 구현, 실행, 검증을 반복하는 하이브리드 CUA 능력을 재현 가능한 환경에서 평가·학습할 수 있게 합니다. 프론티어 모델은 레퍼런스 충실도에 크게 미치지 못하며, 재현 학습의 OOD 전이에 대한 초기 증거를 제공합니다.

한계도 논문에 명시되어 있습니다. 고정 환경 중심 구성으로 <span style="background-color: #fff59d"><strong>실서비스·실사용자 상호작용 커버가 제한적</strong></span>이며, Android의 패킷 레벨 이그레스 필터 검증이 아직이라는 점입니다. 평가 무결성 측면에서는 네 가지 해킹 탐지기로 관측한 결과 전 모델에서 시도가 관측됐고, <span style="background-color: #fff59d"><strong>프롬프트 준수만 믿지 말고 명시적 접근 제어와 감사가 필요하다</strong></span>는 결론입니다.

## 자주 묻는 질문

**RecreationWorld와 RecreationBench의 관계는?**
RecreationWorld는 환경과 하네스를 포함한 프레임워크이고, RecreationBench는 그 안의 홀드아웃 평가용 250태스크 벤치마크입니다.

**하이브리드 CUA의 정의는?**
GUI 조작과 코드·CLI 사용을 한 롱호라이즌 프로세스에서 스스로 전환하며 수행하는 에이전트입니다.

**완전 재현율은?**
1위 GPT-6 Astra도 전체 프로그래매틱 테스트 통과는 2.8%에 그칩니다.

**학습 전이 효과는?**
5개 OOD 벤치마크에서 모두 향상, 최대 +17.9pp입니다.

**출처는?**
[arXiv 2609.22000](https://arxiv.org/abs/2609.22000)에서 논문을 볼 수 있고, 벤치마크·환경·테스트 수트가 GitHub·Hugging Face·ModelScope로 공개됐습니다. 기준일 2026-09-21.

## 더 실습해보고 싶은 분들께

하이브리드 에이전트·루프 설계를 직접 다뤄보고 싶다면:

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
