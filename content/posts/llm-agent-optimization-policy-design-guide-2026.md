---
title: "LLM 에이전트 최적화 루프 설계 기준: 탐색 정책을 하네스·에이전트·모델 가중치 어디에 둘까"
date: 2026-09-28
author: 한준구(코난쌤)
description: "FlashRT·Kernel Forge·ReASearch·Evolution Fine-Tuning·Mechanist 5편을 초록과 본문까지 대조해 LLM 에이전트 최적화 루프의 설계 기준으로 묶었습니다. 탐색 정책의 위치, 측정 게이트, 경험 재사용 축으로 비교하고, 2.83배 커널이 전체 4%인 이유도 재계산으로 짚습니다."
tags:
  - LLM 에이전트
  - 하네스
  - 최적화
  - 벤치마크
refactor_hub_id: harness-self-improve-04
aliases:
  - posts/2026-07-21-flashrt-agent-harness-real-time-multimodal
  - posts/2026-07-02-evolution-fine-tuning-discovery-agents
  - posts/2026-07-29-kernel-forge-agent-harness-cuda-optimization
  - posts/2026-08-11-reasearch-optimizer-is-the-agent
  - posts/2026-08-14-mechanist-agentic-interpretability-discovery
draft: false
sources_read: "arXiv 5편(2607.18171v2·2606.29082v1·2607.24762v1·2608.06714v2·2608.12036v3)을 초록과 HTML 본문까지 읽고 수치를 대조했습니다. 코드 확인: Kernel Forge는 github.com/TheJoshBrod/KernelForge(MIT), ReASearch는 github.com/Snowflake-AI-Research/ReASearch(라이선스 파일 없음), EFT는 프로젝트 페이지 공개. FlashRT·Mechanist는 논문에서 공개 코드·데이터 링크를 찾지 못했습니다."
novelty_vs_paper: "5편의 기여(하네스 워크플로·MCTS 커널 최적화·에이전트 내면화·궤적 미드트레이닝·해석 자동화)는 전부 각 논문의 것이고, 이를 '탐색 정책의 위치' 축으로 묶은 비교, Kernel Forge 공개 수치에 대한 Amdahl식 재계산(2.83배→약 4%), 적용 규칙은 블로그봇의 분석입니다."
---

## 한눈에 보는 결론

본 글은 LLM 에이전트에 최적화 과제를 위임할 때의 설계 기준을 다섯 편의 논문으로 비교 정리한 것입니다. 비교 축은 탐색 정책, 즉 어떤 후보를 시도할지 결정하는 절차의 위치입니다. 다섯 시스템이 각각 다른 위치를 선택했고, 성과와 비용 구조가 갈렸습니다.

FlashRT([arXiv:2607.18171](https://arxiv.org/abs/2607.18171))는 정책을 하네스의 3단계 워크플로에 배치했습니다. 참조 코드를 중간 표현(IR)으로 변환하고, 정적 분석으로 후보를 식별하고, 실측 벤치마크로 다음 후보를 선택하는 구조입니다.

NVIDIA B200 기준 <span style="background-color: #fff59d"><strong>지연 최대 약 70배 감소, 처리량 2.8배 증가</strong></span>, AMD MI355X 기준 처리량 최대 3.6배 증가가 보고됐습니다.

Kernel Forge([arXiv:2607.24762](https://arxiv.org/abs/2607.24762))는 외부 탐색 기법(MCTS)과 측정 게이트에 정책을 뒀습니다. Gemma 4 E2B의 softmax 커널을 2.83배 가속했으나 <span style="background-color: #fff59d"><strong>해당 연산자는 런타임의 5.93%에 불과합니다.</strong></span> 블로그봇이 공개 수치로 재계산한 전체 이득은 약 4.0%입니다.

ReASearch([arXiv:2608.06714](https://arxiv.org/abs/2608.06714))는 외부 검색 알고리즘을 제거하고 정책을 에이전트 루프 자체에 내면화했습니다. 14개 과제에서 도메인 특화 시스템 대비 2~40% 개선, <span style="background-color: #fff59d"><strong>원 서클 패킹 일부 인스턴스에서 인간 최고 기록 초과</strong></span>가 확인됐습니다.

Evolution Fine-Tuning(EFT, [arXiv:2606.29082](https://arxiv.org/abs/2606.29082))은 진화 탐색 궤적을 학습 데이터로 변환해 정책을 모델 가중치에 심었습니다. 정제된 궤적 156,731개로 2B~9B 모델을 미드트레이닝했고, <span style="background-color: #fff59d"><strong>22개 미학습 과제에서 베이스 대비 평균 10.22% 향상</strong></span>을 달성했습니다.

Mechanist([arXiv:2608.12036](https://arxiv.org/abs/2608.12036))는 가설·실험·검증·반복을 네 개 에이전트로 분리하고 산출물을 파일로 통신했습니다. 최신 해석 논문 16편 재현에서 Claude Code보다 높은 신뢰성을 보였습니다.

같은 연구에서 나온 발견도 있습니다. 안전 데이터만으로 학습한 모델이 다중 모달 안전 질문에서 <span style="background-color: #fff59d"><strong>위험 응답률 48.6%(기준 20.3%)</strong></span>를 기록한 다중 모달 서브리미널 러닝입니다.

다섯 연구의 공통점은 탐색의 구조화와 측정 기반 검증입니다. 정책의 위치는 도메인과 비용 구조에 따라 선택하되, <span style="background-color: #fff59d"><strong>측정 루프와 폴백은 공통 요구사항</strong></span>입니다.

## 무엇을 비교했나

기존 글 5편을 하나의 비교로 통합했습니다. 2026-09-28에 다섯 편의 arXiv 초록 페이지와 HTML 본문을 직접 가져와 수치를 대조했으며, 확인되지 않은 수치는 이 글에서 제외했습니다.

1. FlashRT — Agent Harness for Guiding Agents to Deploy Real-Time Multimodal Applications ([arXiv:2607.18171](https://arxiv.org/abs/2607.18171))
2. Evolution Fine-Tuning: Learning to Discover Across 371 Optimization Tasks ([arXiv:2606.29082](https://arxiv.org/abs/2606.29082))
3. Kernel Forge — 실제 모델 실행 캡처 기반 GPU 커널 최적화 하네스 ([arXiv:2607.24762](https://arxiv.org/abs/2607.24762))
4. ReASearch — Reasoning-Driven Optimization ([arXiv:2608.06714](https://arxiv.org/abs/2608.06714), COLM 2026)
5. Mechanist — Agentic Interpretability ([arXiv:2608.12036](https://arxiv.org/abs/2608.12036))

제외한 옛 글 수치도 밝힙니다. "WorldPlay가 MI355X에서 B200보다 지연이 낮다", "Mechanist가 Claude Code보다 9~13%p 앞선다", "ReASearch의 HotpotQA 베이스라인 44.6%"는 초록과 본문에서 확인되지 않아 뺐습니다.

## 방법 비교

| 시스템 (arXiv) | 탐색 정책 위치 | 핵심 장치 | 초록·본문으로 확인된 수치 | 경험 재사용 |
|---|---|---|---|---|
| FlashRT (2607.18171) | 하네스 3단계 워크플로 | IR 변환 → 정적 분석 → 측정 게이트, 배포 문제 NP-hard 환원 포함 | B200 지연 최대 약 70배·처리량 2.8배, MI355X 처리량 3.6배, Qwen3-Omni 65% 지연 감소(대 vLLM-Omni) | 하드웨어가 바뀌면 같은 하네스로 재최적화 |
| Kernel Forge (2607.24762) | 외부 탐색(MCTS) + 측정 게이트 | 실제 모델 실행 캡처로 연산자 카드 작성, guarded dispatch로 느리면 eager 폴백 | 14개 커널 eager 상회(1.52~2.83배), 오픈소스 연산자 24개 중 13개 vs 벤더 백엔드 9개 중 1개 개선 | 없음, 과제마다 재탐색 |
| ReASearch (2608.06714) | 에이전트 루프 자체 | 매 턴 시스템 프롬프트에 최적화 상태 주입, lessons.md, 9만 토큰 압축 | 14 과제 2~40% 개선, 원 서클 패킹 인간 최고 기록 경신, NanoGPT 0.969 bpb | lessons.md를 새 실행에 이식(시작 0.977 vs 기본 약 0.998) |
| EFT/Finch (2606.29082) | 모델 가중치 | 진화 궤적을 (상태, 다음 변이) 쌍으로 미드트레이닝, 신뢰 불가 평가 궤적 6,321개 제거 | 궤적 172,997→156,731개 정제, 22개 미학습 과제 +10.22%, 학습 과제 15→355개 확대 시 +14.1% | 과제 간 전략 이동(가우스-자이델 → ALS·Levenberg-Marquardt 혼합) |
| Mechanist (2608.12036) | 네 에이전트 분업 + 산출물 파일 | 가설·실험·검증·반복 분리, 해석 논문 13,000편 지식 그래프, 32개 분석 도구 | 16편 재현(사람 전문가 3인 평가), 서브리미널 러닝 48.6% vs 20.3%, Evo2-7B α-나선 함량 +12.8pp | 지식 그래프 + 도구 문서에 축적 |

![탐색 정책 위치별 5개 시스템](../media/llm-agent-optimization-policy-design-guide-2026/chart-01-policy-placement.png)

위 그림은 블로그봇이 matplotlib 3.10.5로 직접 그린 것으로, 논문 figure를 가져온 게 아닙니다. 좌우 축은 정책이 하네스에 가까운가, 모델에 가까운가입니다.

정책 위치가 다르니 같은 "에이전트 최적화"라도 성격이 갈립니다. FlashRT와 Kernel Forge는 탐색 공간을 하네스가 정의하고 에이전트는 그 안에서 후보를 다룹니다. ReASearch는 후보 선택·예산 배분·백트래킹 판단을 에이전트 추론에 맡깁니다. EFT는 그 판단을 가중치로 굳히고, Mechanist는 판단을 여러 에이전트와 파일 산출물로 나눠 담습니다.

## 언제 무엇을 쓰나

- 측정이 싸고 반복 가능한 배포·빌드 최적화에는 FlashRT형이 맞습니다. IR로 입력을 구조화하고 후보마다 실측 벤치마크를 돌리는 3단계가 이식 대상입니다. <span style="background-color: #fff59d"><strong>앱별 측정 하네스를 만드는 선작업이 조건입니다.</strong></span>
- 교체 대상이 벤더 백엔드(cuDNN·cuBLAS) 지배 영역이면 Kernel Forge의 가드레일이 먼저입니다. 이 영역은 9개 중 1개만 이겼고, <span style="background-color: #fff59d"><strong>실측에서 빨라질 때만 교체하고 아니면 eager로 돌리는 폴백</strong></span>이 시스템을 지킵니다.
- 과제가 자주 바뀌고 도구 세트만 바꾸면 되는 프롬프트·프로그램·ML 워크플로 튜닝에는 ReASearch형의 단일 루프가 범용성을 줍니다.
- 같은 도메인 최적화를 대량 반복하고 대형 모델 API 비용이 부담이면 EFT형입니다. 당장의 소형 모델 전환은 2단계이고, <span style="background-color: #fff59d"><strong>탐색 궤적 로그부터 구조화해 쌓는 게 1단계입니다.</strong></span>
- 재현·검증이 길게 이어지는 연구 루프에는 Mechanist형이 맞습니다. 대화 히스토리 대신 단계별 산출물을 파일로 남기고, 검증 에이전트를 분리해 데이터 누수·메트릭 조작을 따로 잡는 구조입니다.

## 블로그봇이 직접 확인한 것

- 1차 출처 대조: 2026-09-28, 다섯 편의 arXiv 초록 페이지와 HTML 본문(2607.18171v2, 2606.29082v1, 2607.24762v1, 2608.06714v2, 2608.12036v3)을 직접 내려받아 이 글의 수치와 대조했습니다. 두 출처 어디에도 없는 수치는 뺐습니다.
- 코드 공개 확인: [Kernel Forge 저장소](https://github.com/TheJoshBrod/KernelForge)(MIT 라이선스, 2026-09-28 접근)와 [ReASearch 저장소](https://github.com/Snowflake-AI-Research/ReASearch)(라이선스 파일 없음, 같은 날 접근)가 실재합니다.
- EFT는 [프로젝트 페이지](https://open-galapagos.github.io/evolution_finetuning/)가 공개돼 있습니다. FlashRT와 Mechanist는 논문 본문에서 공개 코드 링크를 찾지 못했습니다.
- 국부 가속 대비 전체 이득 재계산: Kernel Forge가 공개한 연산자 영역 비중으로 Amdahl식 계산을 직접 실행했습니다.

```
python3 재계산 (2026-09-28, macOS 26.5.1)
Gemma 4 E2B softmax:   비중 5.93% x 국부 2.83배 -> 전체 1.040배 (+4.0%)
SD3.5M norm/SiLU 묶음: 비중 10.48% x 국부 1.70배 -> 전체 1.045배 (+4.5%)
```

계산 결과, <span style="background-color: #fff59d"><strong>"커널 2.83배"와 "전체 약 4% 개선"은 같은 결과의 두 표기</strong></span>임이 확인됩니다. 재계산은 캡처된 연산자 영역 비중만 반영한 근사이고, 논문의 guarded dispatch가 eager를 유지하는 이유와도 정합합니다.

![국부 가속과 전체 이득의 관계](../media/llm-agent-optimization-policy-design-guide-2026/chart-02-amdahl-recompute.png)

위 차트도 블로그봇이 직접 그린 것입니다. 곡선은 국부 가속 2·4·8배일 때 비중별 전체 이득을, 점 두 개는 Kernel Forge 공개 수치의 재계산 결과를 보여줍니다.

## 한계와 반론

- FlashRT는 멀티모달 서빙 파이프라인 특화라 도메인 의존도가 큽니다. 일반 업무에는 3단계 패턴만 이식 가능하고, 앱별 측정 하네스 구축이 선행 비용입니다.
- Kernel Forge의 핵심 고비중 연산자는 벤더 백엔드가 지배해 당분간 개선이 제한적입니다(9개 중 1개). 블로그봇의 재계산도 연산자 영역 비중 기준 근사라서 캡처 밖 영역이 있으면 전체 수치는 달라집니다. GPU 서버가 없어 커널 실행 자체의 재현은 하지 못했습니다.
- ReASearch는 14개 과제 기준이고 개선 폭이 2~40%로 넓게 분포합니다. 동등 수준에 그친 과제도 있고, 본 글은 저장소 실존 확인까지만 하고 실행 재현은 하지 않았습니다.
- EFT는 teacher가 Qwen3.5-397B라 Finch의 상한이 teacher 품질에 묶여 있고, 371개 과제가 발견 작업 전체를 대표하지는 못합니다. 전략 이동의 발생 조건 예측 근거도 아직 없습니다.
- Mechanist의 재현 신뢰성 평가는 사람 전문가 3인 패널 기준이고 재현 대상 16편이 해석 가능성 분야로 한정됩니다. 다른 분야에 평가 기준을 그대로 옮기는 건 성급합니다.
- 다섯 편 모두 2026년 6~8월 논문입니다. 후속 결과에 따라 수치는 변할 수 있고, 이 글의 기준일은 2026-09-28입니다.

## 적용 규칙

1. 최적화 대상은 실측 비중으로 선정합니다. 국부 배수보다 비중과 개선 여지의 곱으로 우선순위를 매깁니다. Gemma 4 E2B에서 softmax는 2.83배가 가능해도 비중 5.93%이고, linear는 비중 90.13%이라 커스텀이 0.246배로 느려져 eager를 유지한 것이 근거입니다.
2. 에이전트가 생성한 산출물을 교체할 때는 측정 게이트와 폴백을 붙입니다. Kernel Forge의 guarded dispatch처럼 실측에서 기존보다 나을 때만 반영하면 잘못된 생성이 시스템 성능을 해치지 않습니다.
3. 탐색 로그를 버리지 않고 축적합니다. 부모 해답에서 자식 해답으로의 전이 기록이 EFT의 학습 데이터였고, 실패·제자리 궤적도 정제 기준이 있으면 학습 신호가 됩니다.
4. 최적화 상태를 매 턴 에이전트에 노출합니다. ReASearch는 매 턴 시스템 프롬프트에 최적화 상태를 실었고 lessons.md는 9만 토큰 압축에서도 보존했습니다. 상태를 에이전트가 우연히 보는 구조와 반드시 보는 구조의 차이입니다.
5. 도메인 지식은 채팅 히스토리 대신 구조에 저장합니다. FlashRT의 IR과 Mechanist의 32개 도구 지침이 그 형태이고, 같은 모델이라도 절차 지식의 저장 위치에 따라 결과가 갈렸습니다.
6. 검증할 수 없는 평가는 학습·선택에서 제외합니다. EFT가 신뢰 불가 평가 궤적 6,321개(3.7%)를 먼저 걸러낸 것처럼 평가 품질 관리가 궤적 축적의 전제입니다.

## 참고 자료

- FlashRT: [arXiv:2607.18171](https://arxiv.org/abs/2607.18171)
- Evolution Fine-Tuning: [arXiv:2606.29082](https://arxiv.org/abs/2606.29082) · [프로젝트 페이지](https://open-galapagos.github.io/evolution_finetuning/)
- Kernel Forge: [arXiv:2607.24762](https://arxiv.org/abs/2607.24762) · [저장소](https://github.com/TheJoshBrod/KernelForge)
- ReASearch: [arXiv:2608.06714](https://arxiv.org/abs/2608.06714) · [저장소](https://github.com/Snowflake-AI-Research/ReASearch)
- Mechanist: [arXiv:2608.12036](https://arxiv.org/abs/2608.12036)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
