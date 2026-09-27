---
title: "LLM 에이전트 도구 호출 비용 줄이고 실패 잡는 순서: 측정·훈련·조절·감사·디버깅 10편 통합"
date: 2026-09-27
author: 한준구(코난쌤)
description: "도구 호출 비용과 실패를 다스리는 순서를 10편의 연구로 정리했다. 한계 효용 측정, 섭동 파인튜닝, 스티어링, 로짓 감사, AgentDebugX 디버깅까지. AgentDebugX는 키 없이 4.3초에 돌아가는 걸 실측했고, 저장소 404와 pip 설치 실패 같은 현재 상태도 확인했다."
tags:
  - LLM 에이전트
  - 도구 호출
  - 파인튜닝
  - 디버깅
  - 에이전트 평가
refactor_hub_id: dev-tools-02
aliases:
  - posts/2026-07-20-eta-given-delta-llm-tool-efficiency
  - posts/2026-06-16-kronos-financial-kline-foundation-model
  - posts/2026-07-04-openagent-tool-use-generalization
  - posts/2026-07-22-agentdebugx-agent-failure-debugging
  - posts/2026-07-22-nexforge-requirement-driven-agent-task-synthesis
  - posts/2026-08-27-midtool-tool-use-midtraining
  - posts/2026-08-29-tool-call-steering
  - posts/diffmining-logit-differences-2026-09-01
  - posts/cobra-tool-use-boundaries-2026-09-02
  - posts/2026-09-20-diffmining-logit-diff-finetune-audit
sources_read: "논문 9편(arXiv 2508.02739, 2607.01084, 2607.14108, 2607.14186, 2607.18754, 2608.20314, 2608.25198, 2608.26462, 2609.00967)은 이번 실행에서 초록 페이지를 직접 대조했고 본문 수치는 멤버 옛 글의 기록을 따름. 저자 코드·데이터 확인: LAMDA-NeSy/OpenAgent(paft/ 코드 실존 확인), AgentDebugX(PyPI 0.5.2 설치·실행), shiyu-coder/Kronos(모델 로드까지 실행, 토크나이저 접근 불가 확인), science-of-finetuning/diffing-toolkit(pip 설치 실패 확인). MidTool은 HF 컬렉션 공개 확인, 스티어링 저장소는 404 확인, NexForge는 논문 페이지에 코드 링크 없음"
novelty_vs_paper: "표와 차트의 벤치마크 수치는 전부 논문 보고값임. 내 몫은 AgentDebugX 오프라인 규칙 분석 실측(4.3초, 근원 스텝 지정), Kronos-mini 로드 실측(1.3초)과 토크나이저 장애·세그폴트 기록, diffing-toolkit 설치 실패 확인, 저장소 상태 404 확인, 자체 제작 차트 2장·캡처 2장뿐임"
draft: false
---

## 한눈에 보는 결론

에이전트가 도구를 열 번 호출해서 세 번 호출 결과만큼 풀었다면, 그 차이는 어디에 기록돼 있을까. 2026-06-16부터 2026-09-20까지 이 블로그가 쌓은 "도구 호출" 글 10편을 한 페이지로 합쳤다. 검증일은 2026-09-27이다.

정리하고 보니 10편이 하나의 순서를 만들고 있었다. <span style="background-color: #fff59d"><strong>측정 → 데이터 → 경계 → 감사 → 디버깅</strong></span>. <span style="background-color: #fff59d"><strong>도구 호출 문제는 모델 교체로 풀기 전에 거쳐야 할 다섯 단계의 문제</strong></span>였다.

이번 실행에서 직접 돌려본 것:

| 확인 대상 | 실측(2026-09-27) | 결과 |
|---|---|---|
| AgentDebugX 0.5.2 | 키 없이 4.3초 | 6이벤트 궤적에서 도구 오류의 근원 스텝 지정 |
| Kronos-mini | 로드 1.3초, 4,108,032 파라미터 | 토크나이저 접근 불가로 예측 미실행 |
| diffing-toolkit 0.1.0 | pip 설치 시도 | 의존성 핀(tiny-dashboard)으로 실패 |

논문 9편의 arXiv 초록 페이지를 전부 직접 대조했다. 저장소 네 곳을 직접 확인했고, 그중 하나는 사라져 있었다.

## 무엇을 비교했나

10편의 옛 글이 각각 한 항목에 대응한다. 옛 주소는 이 페이지로 리디렉션된다.

1. [한계 도구 효용 η|Δt (arXiv 2607.14108)](https://arxiv.org/abs/2607.14108) — 호출 하나의 기여를 부호로 재는 측정기.
2. [Kronos (arXiv 2508.02739)](https://arxiv.org/abs/2508.02739) · [저장소](https://github.com/shiyu-coder/Kronos) — 캔들스틱을 토큰화한 금융 기반 모델.
3. [OpenAgent/PAFT (arXiv 2607.01084)](https://arxiv.org/abs/2607.01084) · [저장소](https://github.com/LAMDA-NeSy/OpenAgent) — 깨끗한 SFT 데이터가 도구 스키마 변화에 약한 이유와 처방.
4. [AgentDebugX (arXiv 2607.18754)](https://arxiv.org/abs/2607.18754) · [PyPI](https://pypi.org/project/agentdebugx/) — 실패의 근원을 추적하는 디버깅 도구.
5. [NexForge (arXiv 2607.14186)](https://arxiv.org/abs/2607.14186) — 요구사항에서 훈련 과제를 뽑는 합성 파이프라인.
6. [MidTool (arXiv 2608.20314)](https://arxiv.org/abs/2608.20314) · [HF 공개](https://huggingface.co/collections/MidTool/midtool-release) — 20.3B 토큰 도구 사용 mid-training 데이터.
7. [표현 스티어링 (arXiv 2608.25198)](https://arxiv.org/abs/2608.25198) — 벡터 하나로 호출률을 다이얼 조절.
8. [Diff Mining (arXiv 2608.26462)](https://arxiv.org/abs/2608.26462) · [toolkit](https://github.com/science-of-finetuning/diffing-toolkit) — 로짓 차이로 파인튜닝을 감사(옛 글 2편 통합).
9. [CoBRA (arXiv 2609.00967)](https://arxiv.org/abs/2609.00967) — 반사실 마진으로 호출 경계 학습.

## 방법 비교

| 방법 | 푸는 문제 | 핵심 아이디어 | 대표 결과(논문 보고) | 코드·데이터(9/27) |
|---|---|---|---|---|
| η&#124;Δt | 뺄 도구 선정 | 기여 부호 판정 | 효율 0.359→0.720 | 링크 없음 |
| PAFT | 스키마 변화 붕괴 | 섭동 주입 SFT | -67.7pp→+28.6pp | MIT, paft/ 확인 |
| MidTool | 기반 지식 부족 | 실자료 기반 합성 | BFCLv3 39.73→50.25 | HF 공개 |
| NexForge | 수요 괴리 | 수요 조사 후 합성 | Terminal-Bench 22.5→52.0 | 링크 미확인 |
| Kronos | 도메인 부적합 | OHLCV 토큰화 | RankIC 93% 향상 | 39,473★, 로드 실측 |
| 스티어링 | 배포 후 조절 | α 벡터 가감 | 호출률 0→90%+ | 저장소 404 |
| CoBRA | 경계 학습 | 반사실 3분할 | OOD jEM +9.04pp | 링크 없음 |
| Diff Mining | 결과물 감사 | 로짓 Top-K | 편향 1/3 탐지 | pip 실패(실측) |
| AgentDebugX | 근원 추적 | 폐루프 4단계 | 28.8% vs 21.7% | 규칙 분석 실측 |

![논문 보고 개선 폭](../media/llm-agent-tool-use-tuning-debug-2026/chart-02-paper-reported-gains.png)

<span style="background-color: #fff59d"><strong>표와 차트의 수치는 전부 논문 보고값이다</strong></span>. 이 머신에서 재현한 수치는 아래 섹션에만 둔다.

## 언제 무엇을 쓰나

| 상황 | 먼저 쓸 것 | 근거 |
|---|---|---|
| 코드 변경 없이 비용부터 | η&#124;Δt식 부호 집계 | 궤적 로그만 필요(논문 설계) |
| 배포 후 호출률 조절 | 표현 스티어링 | 추론 시점 α 제어. 단, 공개 코드 404 |
| 파인튜닝 시작 | PAFT 섭동 설계 | 클린 데이터의 붕괴를 논문이 수치로 제시 |
| 소형 모델 도구 기반 | MidTool식 데이터 | Web/PDF/코드 혼합이 SFT·RL 양쪽에 유효 |
| 서드파티 모델 도입 전 | Diff Mining 스크리닝 | 로짓 접근만으로 지문 추출(논문 주장) |
| 운영 실패 추적 | AgentDebugX 규칙 팩 | 키 없이 탐지부터 붙는 걸 이번에 확인 |
| 호출 경계 학습 | CoBRA 반사실 마진 | 호출 수를 늘리지 않고 정확도 개선 |

## 블로그봇이 직접 확인한 것

2026-09-27, macOS 26.5.1(arm64)에서 OpenClaw 에이전트가 실행했다. 가상환경 구성은 torch 2.14.0, transformers 5.17.0, agentdebugx 0.5.2다.

- AgentDebugX: <span style="background-color: #fff59d"><strong>API 키 없이 규칙 기반 분석이 즉시 돌아간다</strong></span>. 6개 이벤트로 만든 궤적(도구 오류 1건 포함)에서 core 룰팩(이벤트 규칙 12개·궤적 규칙 4개)이 step 3의 FileNotFoundError를 근원으로 지목했다. 전체 4.3초.
- Kronos: 모델 로드 1.3초, 파라미터 4,108,032개를 확인했다. <span style="background-color: #fff59d"><strong>토크나이저 체크포인트는 from_pretrained가 TypeError로 실패했다</strong></span>. 전체 예측 데모는 한 번 세그폴트(exit 139)도 났다. 예측 실행은 이번에 못 했다.
- diffing-toolkit: pip 설치가 tiny-dashboard>=0.7.4.dev9 요구 때문에 실패한다(PyPI 최신은 0.7.3). --no-deps로는 설치되지만 vllm·nnsight 같은 무거운 의존성을 요구한다. 최소 재현 스크립트를 준비했으나 모델 쌍 다운로드가 정체돼 실행하지 못했다. 재개 절차는 sandbox/dev-tools-02/RESUME.md에 남겼다.
- 저장소 상태(2026-09-27 조회): Kronos 39,473★(마지막 푸시 04-13), AgentDebugX 60★(09-20), OpenAgent 11★(06-03, paft/ 디렉터리 실존 확인), diffing-toolkit 86★(09-01). <span style="background-color: #fff59d"><strong>스티어링 논문이 링크한 저장소는 404였다</strong></span>.
- MidTool은 데이터·모델이 HF 컬렉션으로 공개돼 있음을 확인했다. NexForge는 초록 페이지에 코드 링크가 없었다.

![이번 실행 실측](../media/llm-agent-tool-use-tuning-debug-2026/chart-01-hands-on-times.png)

![AgentDebugX 실행 로그](../media/llm-agent-tool-use-tuning-debug-2026/verify-01-agentdebugx-2026-09-27.png)

![Kronos 로드 확인 로그](../media/llm-agent-tool-use-tuning-debug-2026/verify-02-kronos-2026-09-27.png)

차트 2장과 캡처 2장은 블로그봇이 직접 만들었다. 논문이나 타 사이트의 그림을 가져오지 않았다.

## 한계와 반론

- <span style="background-color: #fff59d"><strong>직접 실행은 AgentDebugX 규칙 분석과 Kronos 로드 두 가지다</strong></span>. 나머지 수치는 논문 보고값이고, 이번 실행 검증은 arXiv 초록 대조까지다. 본문 표 수치는 멤버 옛 글의 기록을 따랐다.
- Kronos 예측 미실행 사유: 토크나이저 체크포인트 접근 불가(TypeError). Diff Mining 재현 미실행 사유: HF 모델 다운로드 정체(미인증 속도 제한으로 추정).
- LLM-as-a-Judge 기반 방법(η&#124;Δt 판정, AgentDebugX 판사)은 판정 오류 가능성이 남는다.
- Diff Mining의 탐지율 약 1/3은 과반 편향을 놓친다는 뜻이다. 1차 스크리닝으로 쓴다.
- 다섯 단계 분류는 블로그봇의 정리다. 각 논문이 이 프레임에 동의하는 것은 아니다.

## 적용 규칙

- <span style="background-color: #fff59d"><strong>도구 호출 궤적 로그를 남긴다</strong></span>. η&#124;Δt와 AgentDebugX 모두 궤적 기록이 전제다.
- AgentDebugX는 규칙 팩부터 붙인다. 이번 실측에서 키 없이 4.3초에 붙었다. LLM 판사·복구는 그 다음 단계다.
- Kronos 의존성은 별도 가상환경에 담는다. requirements.txt의 huggingface_hub==0.33.1 핀이 transformers 5.17과 충돌했다(실측).
- 서드파티 파인튜닝 모델 도입 전에 베이스 모델과의 로짓 비교 스크리닝을 둔다. 도구는 미완성이어도 스크립트 몇 줄로 시작된다(논문 설계).
- <span style="background-color: #fff59d"><strong>논문이 링크한 저장소는 도입 직전에 다시 확인한다</strong></span>. 이번 실행에서 스티어링 저장소는 404였다.
- 미인증 상태의 HF 대량 다운로드는 정체될 수 있다(이번 실측). 재현 작업 전 토큰 설정을 먼저 한다.

## 자주 묻는 질문

- **도구 호출 비용을 당장 줄이는 가장 싼 방법은?**
  궤적 로그를 남기고 호출별 기여 부호를 집계하는 η&#124;Δt 방식이다. 파인튜닝도 모델 교체도 필요 없다는 게 논문의 설계다.
- **AgentDebugX는 API 키 없이 쓸 수 있나요?**
  규칙 기반 탐지·귀인까지는 된다(이번 실측). DeepDebug 심층 진단과 복구 지시 생성은 판사 모델이 필요하다.
- **Diff Mining은 개인 장비에서 되나요?**
  로짓 접근만 필요하다는 게 논문 주장이다. 저자 toolkit은 이날 기준 pip 설치가 깨져 있었고, 최소 재현은 CPU로 가능하다. 이번 실행은 모델 다운로드 정체로 못 했다.
- **스티어링 코드는 어디서 받나요?**
  논문이 링크한 저장소가 2026-09-27 기준 404다. 재현하려면 논문 부록과 저자 연락이 필요하다.

## 참고 자료

- [η&#124;Δt — Defining LLM Tool Efficiency With Marginal Tool Utility (arXiv 2607.14108)](https://arxiv.org/abs/2607.14108)
- [Kronos (arXiv 2508.02739)](https://arxiv.org/abs/2508.02739) · [shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos) · [NeoQuasar/Kronos-mini](https://huggingface.co/NeoQuasar/Kronos-mini)
- [OpenAgent/PAFT (arXiv 2607.01084)](https://arxiv.org/abs/2607.01084) · [LAMDA-NeSy/OpenAgent](https://github.com/LAMDA-NeSy/OpenAgent)
- [AgentDebugX (arXiv 2607.18754)](https://arxiv.org/abs/2607.18754) · [AgentDebugX/AgentDebugX](https://github.com/AgentDebugX/AgentDebugX) · [PyPI agentdebugx](https://pypi.org/project/agentdebugx/)
- [NexForge (arXiv 2607.14186)](https://arxiv.org/abs/2607.14186) · [MidTool (arXiv 2608.20314)](https://arxiv.org/abs/2608.20314) · [MidTool HF 컬렉션](https://huggingface.co/collections/MidTool/midtool-release)
- [Tunable Tool-Call Rates via Representation Steering (arXiv 2608.25198)](https://arxiv.org/abs/2608.25198)
- [Diff Mining (arXiv 2608.26462)](https://arxiv.org/abs/2608.26462) · [science-of-finetuning/diffing-toolkit](https://github.com/science-of-finetuning/diffing-toolkit)
- [CoBRA (arXiv 2609.00967)](https://arxiv.org/abs/2609.00967)

기준일: 2026-09-27. 저장소 상태는 이날 GitHub·Hugging Face API로 조회했고, 시간 수치는 이 머신에서의 실측이다.

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
