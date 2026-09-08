---
title: "컴퓨터 사용 에이전트에 CLI를 다리면 9B 모델도 성공률 23→40% — CUA-Universe 정리 (arXiv 2609.05374)"
description: "실제 데스크톱 앱 16종을 GUI+CLI 하이브리드 환경으로 바꿔 4,923개 검증 궤적으로 Qwen3.5-9B를 학습시킨 CUA-Universe(arXiv 2609.05374) 정리. CUA-Verse 스코어 3배, OSWorld +16.8pp, 토큰 60% 절감. 기준일 2026-09-08."
date: 2026-09-08
draft: false
tags:
  - agent
  - computer-use
  - gui
  - cli
  - fine-tuning
  - llm
---

## 결론 먼저

본 문서는 CUA-Universe(arXiv 2609.05374v1, 2026-09-04 게시, Shanghai Jiao Tong University 및 Zhejiang University)의 요약입니다. 컴퓨터 사용 에이전트(CUA)를 위한 GUI+CLI 하이브리드 환경 구축 파이프라인과, 이 환경에서 생성한 데이터로 학습한 9B 모델의 성능을 정리했습니다. 기준일은 2026-09-08입니다.

주요 결과:

- Qwen3.5-9B LoRA 파인튜닝 후 CUA-Verse 스코어 <span style="background-color: #fff59d"><strong>0.189 → 0.582 (약 3배)</strong></span>
- OSWorld 244태스크: 성공률 23.4% → 40.2% (+16.8pp), 스텝 −57%, 토큰 −44%
- OSWorld-MCP: <span style="background-color: #fff59d"><strong>SR 20.90% → 28.69%</strong></span> (미학습 MCP 인터페이스)

## 문제 정의

OSWorld·AndroidWorld 등의 벤치마크에서 컴퓨터 사용 에이전트는 대부분 GUI 동작(화면 좌표 클릭)만 사용합니다. 이로 인해 명령어 한 줄로 처리 가능한 작업을 다수의 클릭으로 수행하며 궤적이 길어지고, 장기 워크플로에서 취약해집니다. 반면 CLI 특화 에이전트는 시각 상태·레이아웃 정보에 접근하지 못하여 인터페이스 상태 의존 태스크에서 취약합니다.

논문이 정의하는 본질적 과제는 오케스트레이션입니다. 동일한 애플리케이션 상태를 공유하면서 <span style="background-color: #fff59d"><strong>GUI와 CLI 사이의 전환 시점을 결정하는 능력</strong></span>이며, 이를 학습시킬 수 있는 확장 가능한 환경이 부족했다고 지적합니다.

## 제안 방법: 3단계 파이프라인

![CUA-Universe 전체 구조](/images/2026-09-08-cua-universe-hybrid-gui-cli/fig-1-p2.png)

Figure 1 출처: arXiv 2609.05374v1, https://arxiv.org/abs/2609.05374

| 단계 | 기능 | 규모 |
| --- | --- | --- |
| App-Forge | 데스크톱 앱을 재현 가능한 VM으로 변환, CLI 서피스를 발견/래핑/생성 | <span style="background-color: #fff59d"><strong>16개 실제 앱</strong></span> (Blender, GIMP, Zotero, OBS, Audacity 등) |
| Task-Weave | 시드 파일 기반 재사용 가능 연산 조합으로 하이브리드 태스크 합성, 난이도 조절 | 앱당 연속 태스크 소스 |
| Path-Steer | 효율적 하이브리드 경로로 롤아웃 스티어링, 검증 궤적 수확 | <span style="background-color: #fff59d"><strong>4,923 에피소드 / 약 235K 스텝 레코드</strong></span> |

App-Forge의 앱 설치·CLI 도구 구축은 <span style="background-color: #fff59d"><strong>Codex 코딩 에이전트(GPT-5.6)가 수행</strong></span>하고, Task-Weave의 연산 추상화·태스크 합성은 Kimi K2.5가 수행합니다. 태스크 성공 판정은 VLM 저지(GPT-5.4)가 담당하며 <span style="background-color: #fff59d"><strong>스코어 0.75 이상만 통과</strong></span>합니다.

## 학습 설정

- 데이터 생성: Kimi K2.5 백본, Path-Steer 적용 롤아웃, 저지 0.75 통과 궤적만 수집
- 학습: Qwen3.5-9B + LoRA, 스텝 레벨 레코드, 3 에포크
- 환경: ms-swift 프레임워크, 8× A100 GPU, 약 2일

학습 방식은 RL이 아닌 <span style="background-color: #fff59d"><strong>검증 궤적 기반 증류(SFT)</strong></span>이며, 논문은 STaR/ReST 계열 효과(교사의 성공 궤적 상단 학습으로 학생이 교사 평균 초과)로 설명합니다.

## 결과 1: CUA-Verse (160 태스크)

| 모델 | 인터페이스 | Score | 스텝 | 토큰(K/에피소드) |
| --- | --- | --- | --- | --- |
| GPT-5.5 (상용) | GUI+CLI | 0.768 | 23.1 | 193 |
| Seed2.1 Pro (상용) | GUI+CLI | 0.599 | 40.1 | 449 |
| Kimi K2.5 (상용) | GUI+CLI | 0.522 | 21.1 | 275 |
| Ours (Qwen3.5-9B LoRA) | GUI+CLI | 0.582 | 35.2 | 255 |
| EvoCUA-8B (오픈) | GUI+CLI | 0.330 | 41.7 | 377 |
| Qwen3.5-9B (베이스) | GUI+CLI | 0.189 | 56.2 | 643 |

Table 1 출처: arXiv 2609.05374v1

오픈소스 최고점(0.582)이며 <span style="background-color: #fff59d"><strong>교사 Kimi K2.5(0.522)를 초과</strong></span>합니다. 동일 베이스 대비 스코어 약 3배, 스텝 −37%, <span style="background-color: #fff59d"><strong>토큰 −60%(643K→255K)</strong></span>입니다. 앱별로는 오디오/비디오(Audacity 0.815, OBS 0.605)가 강하고 3D/공간(Blender 0.398, Godot 0.460)이 약합니다.

## 결과 2: OSWorld 전이

244태스크 통제 프로토콜(os, multi-app 제외)에서 GUI-only와 GUI+CLI를 동일 조건 비교했습니다.

본 모델은 GUI-only 23.4% → GUI+CLI 40.2%로, CLI 추가 시 <span style="background-color: #fff59d"><strong>이전에 실패하던 41개 태스크를 해결</strong></span>했습니다. 반면 학습되지 않은 타 모델은 +3~+8개에 그쳤습니다. 공통 해결 태스크 기준 <span style="background-color: #fff59d"><strong>스텝 2.35배 절감</strong></span>, 태스크당 토큰 286.5K(비교군 최저)입니다.

![OSWorld 앱별 GUI vs GUI+CLI](/images/2026-09-08-cua-universe-hybrid-gui-cli/fig-4-p6.png)

Figure 4 출처: arXiv 2609.05374v1

## 결과 3: OSWorld-MCP 일반화

학습 시 앱 전용 CLI만 사용했음에도, 미학습 MCP 인터페이스(158개 도구)에서 다음 결과를 얻었습니다.

| 지표 | Qwen3.5-9B 베이스 | Ours | 변화 |
| --- | --- | --- | --- |
| SR | 20.90% | 28.69% | <span style="background-color: #fff59d"><strong>+7.79pp</strong></span> |
| TIR(도구 사용 정확도) | 10.66% | 23.36% | <span style="background-color: #fff59d"><strong>약 2.2배</strong></span> |
| ACS(평균 완료 스텝) | 37.22 | 27.25 | −27% |
| 토큰(M) | 125.68 | 87.95 | −30% |

Table 2 출처: arXiv 2609.05374v1

Score 기준 29.51%로 <span style="background-color: #fff59d"><strong>Seed2.1 Pro(27.03%)를 상회</strong></span>합니다.

## Path-Steer ablation

CLI 접근을 유지한 채 경로 안내만 제거한 320태스크 비교입니다.

| 백본 | 조건 | Accept(≥0.75) | 평균 스코어 | 태스크당 비용 |
| --- | --- | --- | --- | --- |
| Kimi K2.5 | w/ Path-Steer | 0.51 | 0.71 | $0.26 |
| Kimi K2.5 | w/o | 0.44 | 0.63 | $0.31 |
| Seed2.1 Pro | w/ Path-Steer | 0.54 | 0.75 | $0.29 |
| Seed2.1 Pro | w/o | 0.45 | 0.67 | $0.33 |

Table 3 출처: arXiv 2609.05374v1

백본 변경에도 동일 패턴이 관측되어, 수확량·품질 향상은 CLI 접근 자체가 아닌 <span style="background-color: #fff59d"><strong>모달리티 스티어링에 기인</strong></span>한다고 결론짓습니다.

## 한계

- 코드/데이터는 <span style="background-color: #fff59d"><strong>"release 예정" 상태로 게시 시점 미공개</strong></span>.
- CUA-Verse 8개 앱은 학습 도메인과 앱이 겹침(태스크만 분리).
- <span style="background-color: #fff59d"><strong>3D/공간 앱에서 성능 낮음</strong></span>, GPT-5.5(0.768)와 격차 존재.
- 채점이 GPT-5.4 VLM 저지에 의존.

## 더 실습해보고 싶은 분들께

하이브리드 인터페이스 에이전트, 환경-데이터 파이프라인 주제 실습에 아래 자료를 권합니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### CUA-Universe는 RL로 학습했나요?

아니요. 검증 궤적 4,923 에피소드로 Qwen3.5-9B에 LoRA SFT를 수행했습니다.

### CLI 접근만 주면 어떤 모델이든 성능이 오르나요?

아니요. 미학습 모델은 +3~+8태스크에 그쳤고, 학습된 9B만 +41태스크가 상승했습니다.

### CUA-Verse에서 9B 모델이 상용 모델을 이긴 건가요?

오픈소스 최고점(0.582)이며 교사 Kimi K2.5(0.522) 초과. Seed2.1 Pro(0.599), GPT-5.5(0.768)에는 미달입니다.

### 학습 데이터 비용은 얼마나 들었나요?

Path-Steer 적용 시 태스크당 약 $0.26, 미적용 시 $0.31(Kimi K2.5 기준). 8× A100 약 2일 학습.

## 출처

- 논문: CUA-Universe: A Scalable and Dynamic Environment for Hybrid GUI+CLI Agents, arXiv 2609.05374v1 (2026-09-04), https://arxiv.org/abs/2609.05374
- PDF: https://arxiv.org/pdf/2609.05374
- 소속: Shanghai Jiao Tong University, Zhejiang University
- 기준일 2026-09-08.
