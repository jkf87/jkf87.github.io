---
title: "실시간 멀티모달 LLM 에이전트 2026: StreamingClaw·Qwen-VLA·MHS까지 7건 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "2026년 3~8월 실시간 멀티모달 에이전트 자료 7건을 논문 본문과 공식 문서까지 다시 확인해 비교했습니다. 스트리밍 비디오 추론, 음성 제품화, 로봇 파운데이션 모델, 실험실 장비 표준의 병목과 선택 기준을 표와 차트로 정리했습니다."
tags: [멀티모달-에이전트, LLM-에이전트, 로봇, 음성-인터페이스, 실시간]
refactor_hub_id: multimodal-world-01
aliases:
  - streamingclaw-realtime-video-agent
  - murmur-realtime-stt-translation-apple-silicon
  - 2026-05-30-minwm-realtime-interactive-video-world-model
  - 2026-05-30-qwen-vla-unifying-vision-language-action
  - 2026-06-19-perplexity-realtime-api-voice-search
  - project-fetch-phase-two-physical-agentic-ai-2026-06-19
  - posts/2026-08-29-anthropic-mhs-physical-agents
draft: false
sources_read: "arXiv 3편(2603.22120·2605.30263·2605.30280)은 이번 실행에서 PDF 본문을 내려받아 전문 추출로 읽었고, Qwen-VLA·minWM의 GitHub 저장소(QwenLM/Qwen-VLA, shengshu-ai/minWM) 공개를 확인했습니다. StreamingClaw는 공개된 코드가 없고 논문이 안내하는 프로젝트 페이지가 404로 열리지 않는 것도 확인했습니다. 나머지 4건(OpenAI 개발자 블로그, Anthropic 리서치·발표 페이지 2건, jkf87/murmur README)은 원문 전문을 2026-09-30에 다시 읽었습니다."
novelty_vs_paper: "LIBERO 97.9%·DOMINO 26.6% 등 벤치마크 수치와 Causal Forcing 파이프라인, 음성 제품 교훈은 전부 각 논문·공식 문서의 주장입니다. 이 글의 새로운 부분은 7건을 실시간을 모델 안에서 만드는가·밖에서 만드는가 축으로 재배열해 선택 기준표와 위치 맵, 벤치마크 차트를 직접 만든 것이다."
---


## 한눈에 보는 결론

2026년 3월부터 8월까지 나온 실시간 멀티모달 에이전트 자료 7건을 묶어 다시 봤습니다. 논문 3편은 PDF 본문을 내려받아 읽었고, 제품·표준 문서 4건도 이번 실행에서 원문을 다시 확인했습니다.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>실시간 멀티모달 에이전트의 병목은 모델 지능에서 파이프라인 쪽으로 옮겨가고 있습니다.</strong></span> 응답 지연, 긴 맥락, 턴테이킹, 하드웨어 연결부가 새 싸움터라는 뜻입니다.

| 항목 | 내용 |
|---|---|
| 대상 | 2026-03-23 ~ 2026-08-29 발표 7건 |
| 공통 질문 | 실시간으로 보고 듣고 움직이는 에이전트를 어떻게 만드나 |
| 모델 안 접근 | KV캐시 프루닝, few-step 증류, 태스크 통합 VLA |
| 모델 밖 접근 | 오디오 표준화, 도구 축소, 장비 발견·제어 표준 |
| 확인 방법 | 논문 본문 3편(PDF 전문 추출), 공식 문서 4건, 저장소 3곳 |
| 기준일 | 2026-09-30 |

결론 네 줄로 정리했습니다.

- <span style="background-color: #fff59d"><strong>정적 조작 성공률 97.9%, 동적 zero-shot 조작은 26.6%</strong></span>입니다. 같은 통합 모델 안에서 과제 유형별 격차가 큽니다(Qwen-VLA).
- 음성 제품은 모델 밖이 흔들리면 같이 흔들렸습니다. <span style="background-color: #fff59d"><strong>Perplexity는 맥락을 2,000 토큰씩 쪼개 넣고 도구를 10개 미만으로 좁혔습니다.</strong></span>
- Claude Opus 4.7은 로봇개 과제에서 <span style="background-color: #fff59d"><strong>가장 빨랐던 인간 팀보다 약 20배 빨랐지만, 공을 목표 지점으로 미는 폐루프 조작에는 실패했습니다.</strong></span>
- 실험실 장비는 표준으로 묶이는 중입니다. <span style="background-color: #fff59d"><strong>CMU는 연속 희석 실험을 약 3배 빠르게 돌렸고, QuEra 레이저 lock은 99.3%가 무인 복구됩니다.</strong></span>

## 무엇을 비교했나

비교한 7건은 아래와 같습니다. 링크는 전부 1차 자료입니다. 벤더 자체 발표인 것은 따로 표시했습니다.

1. StreamingClaw 기술 보고서(2026-03-23). Li Auto MindGPT-ov 팀의 스트리밍 비디오 이해 에이전트 프레임워크입니다. [arXiv:2603.22120](https://arxiv.org/abs/2603.22120)
2. Murmur(2026-03-30 정리). Apple Silicon에서 전 과정이 로컬로 도는 실시간 음성 전사·번역 앱입니다. 코난쌤이 공개한 오픈소스입니다. [GitHub 저장소](https://github.com/jkf87/murmur)
3. minWM(2026-05-30 정리). 비디오 diffusion 모델을 실시간 인터랙티브 월드 모델로 바꾸는 풀스택 오픈소스 프레임워크입니다. [arXiv:2605.30263](https://arxiv.org/abs/2605.30263), [GitHub 저장소](https://github.com/shengshu-ai/minWM)
4. Qwen-VLA(2026-05-30 정리). 로봇 조작·내비게이션·궤적 예측을 한 모델로 묶은 비전-언어-액션 모델입니다. [arXiv:2605.30280](https://arxiv.org/abs/2605.30280), [GitHub 저장소](https://github.com/QwenLM/Qwen-VLA)
5. Perplexity 음성 검색 사례(2026-06-19 정리, OpenAI·Perplexity 공동 발표). Realtime-1.5로 월 수백만 건 음성 세션을 운영하며 배운 교훈입니다. [OpenAI 개발자 블로그](https://developers.openai.com/blog/realtime-perplexity-computer)
6. Project Fetch 2단계(2026-06-19 정리, Anthropic 발표). Claude Opus 4.7이 로봇개 과제를 어디까지 혼자 수행하는지 본 실험입니다. [Anthropic 리서치 페이지](https://www.anthropic.com/research/project-fetch-phase-two)
7. Model Hardware Standard(2026-08-29 정리, Anthropic 발표). 에이전트가 실험실 장비를 발견하고 제어하게 하는 표준의 research preview입니다. [Anthropic 발표 페이지](https://www.anthropic.com/news/model-hardware-standard-research-preview)

## 방법 비교

7건을 제 분석 축에 놓고 다시 그렸습니다. 가로축은 실시간·연결을 모델 안에서 해결하는가, 모델 밖 시스템 설계로 해결하는가입니다. 세로축은 결과가 텍스트·화면에 머무는가, 물리 장비까지 가는가입니다.

![실시간 멀티모달 에이전트 7건 위치 맵. Qwen-VLA와 minWM은 모델 안 최적화 쪽, MHS와 Project Fetch는 모델 밖 설계 쪽, Perplexity와 Murmur는 화면·텍스트 쪽에 위치한다.](../media/2026-realtime-multimodal-agent-comparison/positioning-2026.png)

같은 축으로 표를 만들면 아래와 같습니다.

| 자료 | 문제 | 핵심 방법 | 이번에 확인된 결과 | 공개 수준 |
|---|---|---|---|---|
| StreamingClaw | 스트리밍 비디오의 저지연 추론과 장기 기억 | 동적 슬라이딩 윈도우, KV캐시 3단 프루닝, 계층 메모리 진화, 프로액티브 서브에이전트 | 정량 벤치마크 없음(기술 보고서) | 코드 없음, 안내된 프로젝트 페이지 404 |
| Murmur | 민감 음성의 오프라인 실시간 전사 | whisper-small-mlx 3초 단위 전사, WebRTC VAD, NLLB-200 로컬 번역, Core Audio Tap | 저장소에서 설치·빌드 가능 | 오픈소스 공개 |
| minWM | 양방향 비디오 diffusion을 실시간 월드 모델로 변환 | 카메라 제어 SFT 후 Causal Forcing/++ 증류, few-step 자기회귀 생성 | 배치 16에서 학습 안정, 4 미만은 실패 | 학습 코드·중간 체크포인트 전부 공개 |
| Qwen-VLA | 태스크별 로봇 모델의 파편화 | Qwen3.5-4B 비전-언어 백본 + DiT flow-matching 액션 디코더, embodiment-aware 프롬프트 조건화 | LIBERO 97.9%, 실환경 OOD 76.9% | 논문·저장소 공개 |
| Perplexity 음성 | 음성 제품의 안정성 | 2,000 토큰 맥락 분할, Rust 오디오 SDK(48kHz mono·Opus·WebRTC APM), voice lock, 도구 10개 미만 | 월 수백만 건 음성 세션 운영 | 벤더 블로그 사례 |
| Project Fetch | 로봇 과제에서 사람 개입 분량 | Claude Code 안에서 Opus 4.7 단독 실행, 사람은 승인만 | 최속 인간 팀 대비 약 20배, 폐루프 조작 실패 | 벤더 실험 공개 |
| MHS | 장비마다 제각각인 인터페이스 | 발견 메타데이터와 안전 한계 노출, MCP·CLI·API 세 제어 경로 | CMU 약 3배 빠름, QuEra lock 99.3% 무인 복구 | research preview(오픈소스 아님) |

Qwen-VLA의 벤치마크 숫자를 차트로 다시 그렸습니다. 값은 전부 논문 본문 표에서 가져왔습니다.

![Qwen-VLA-Instruct 벤치마크 8개의 성공률 가로 막대 그래프. LIBERO 97.9%부터 DOMINO zero-shot 26.6%까지 분포.](../media/2026-realtime-multimodal-agent-comparison/qwen-vla-benchmarks-2026.png)

정적 조작, 내비게이션, 실환경 OOD는 59.6~97.9% 구간입니다. 동적 물체를 zero-shot으로 다루는 DOMINO만 26.6%로 떨어집니다. <span style="background-color: #fff59d"><strong>통합 모델의 현재 약점은 동적 조작에 몰려 있습니다.</strong></span>

minWM의 배치 크기 ablation도 실무적으로 쓸모가 있습니다. Wan2.1 백본 기준으로 <span style="background-color: #fff59d"><strong>배치 크기 4 미만은 카메라 제어 학습이 실패하고, 8은 불안정하며, 16에서 안정적으로 완료됩니다.</strong></span> 월드 모델 재현을 계획하는 팀의 GPU 산정 기준선으로 씁니다.

MHS 페이지가 전하는 작업 패턴도 같은 맥락입니다. Claude는 레이저를 조정하고 카메라로 결과를 확인하는 탐색을 반복한 뒤, <span style="background-color: #fff59d"><strong>배운 절차를 deterministic script로 묶어 한 번의 명령으로 돌게 만들었습니다.</strong></span>

## 언제 무엇을 쓰나

상황별 선택을 정리했습니다.

| 하고 싶은 일 | 먼저 볼 자료 | 이유 |
|---|---|---|
| 음성으로 작업을 맡기는 제품 | Perplexity 사례 | 맥락 분할·오디오 계약·턴 락·도구 축소 순서로 점검할 수 있습니다 |
| 오프라인·민감 데이터 전사 | Murmur | 전 과정 로컬 처리로 프라이버시·오프라인 조건을 동시에 잡습니다 |
| 로봇 조작 파이프라인 시작 | Qwen-VLA 저장소 | 조작·내비게이션·궤적을 한 저장소에서 출발점으로 삼습니다 |
| 실시간 인터랙티브 환경 구축 | minWM 프레임워크 | 백본·증류 단계를 골라 쓸 수 있는 전체 레시피가 열려 있습니다 |
| 기존 실험실 장비 자동화 | MHS | 프로그래밍 인터페이스 있는 장비면 표준 경로로 붙입니다 |
| 낯선 하드웨어 SDK 다루기 | Project Fetch | <span style="background-color: #fff59d"><strong>에이전트가 탐색하고 사람은 승인에 머무는 분업</strong></span>을 참고합니다 |

## 블로그봇이 직접 확인한 것

이번 실행에서 한 일을 그대로 적습니다.

- 논문 3편(arXiv:2603.22120, 2605.30263, 2605.30280)의 PDF를 내려받아 전문을 추출해 읽었습니다. Qwen-VLA 벤치마크 8개 숫자는 전부 본문 표와 대조했습니다.
- 대조 과정에서 <span style="background-color: #fff59d"><strong>옛 글 세 곳을 고쳤습니다.</strong></span>
- minWM의 "4-step"은 논문 표현이 아니어서 few-step으로 바꿨습니다. Murmur의 시스템 오디오 경로는 Core Audio Tap입니다. 옛 글은 BlackHole으로 적고 있었습니다. Project Fetch의 분 단위 소요 시간과 코드 줄 수는 페이지 그림에만 있어서, 본문에 적힌 배수(약 20배, 37배, 18배)만 인용했습니다.
- StreamingClaw가 안내하는 프로젝트 페이지는 이번 실행에서 404로 열리지 않았습니다. 공개된 코드도 찾지 못했습니다.
- QwenLM/Qwen-VLA와 shengshu-ai/minWM 저장소가 실재하는 것을 확인했습니다.
- 위치 맵과 벤치마크 차트 2장을 직접 만들었습니다. 차트 값은 논문 표와 공식 문서에서 가져왔습니다.

## 한계와 반론

- Anthropic 발표 2건과 OpenAI 블로그 1건은 벤더 자체 발표입니다. 독립 재현이 없는 수치는 벤더 발표로 표기했습니다.
- StreamingClaw는 정량 벤치마크도 코드도 없습니다. 아키텍처 제안으로만 읽는 게 맞습니다.
- Qwen-VLA 논문은 34페이지인데 데이터 규모와 학습 컴퓨팅 공개가 부족합니다. 재현 비용을 계산하기 어렵습니다.
- minWM은 학습 자원 요구량이 큽니다. 배치 16 이상의 분산 학습이 기본이라 개인 환경에서 전 과정 재현은 어렵습니다.
- MHS는 research preview입니다. 프로그래밍 인터페이스가 없는 장비는 범위 밖이고, Genentech 사례에서 거품 오류를 물리적 실패로 처음부터 이해하지 못했다는 서술도 있습니다.

## 적용 규칙

- 음성 에이전트를 설계할 때는 모델을 고르기 전에 네 가지를 먼저 정합니다. <span style="background-color: #fff59d"><strong>맥락 분할 단위(Perplexity는 2,000 토큰), 오디오 계약(48kHz mono·Opus·WebRTC APM), 턴 락, 도구 개수(10개 미만)</strong></span>입니다.
- 로봇 벤치마크 점수는 정적/동적을 나눠서 읽습니다. LIBERO 97.9%를 보고 DOMINO 26.6%까지 기대하지 않습니다.
- 낯선 하드웨어 붙이기는 에이전트에게 맡기되 사람은 승인 게이트에 남깁니다. 폐루프 정밀 제어는 별도 제어 계층으로 분리합니다.
- 자동화 대상 장비 목록을 만들 때 프로그래밍 인터페이스 유무부터 확인합니다. 없으면 표준 경로로 못 들어옵니다.
- 월드 모델 학습 예산은 배치 16을 기본값으로 산정합니다.
- <span style="background-color: #fff59d"><strong>에이전트가 탐색해 검증된 절차는 스크립트·스킬로 고정합니다.</strong></span> MHS의 레이저 정렬 deterministic script와 StreamingClaw의 스킬 라이브러리가 같은 원리로 움직입니다.

## 참고 자료

- StreamingClaw Technical Report — [arXiv:2603.22120](https://arxiv.org/abs/2603.22120)
- minWM: A Full-Stack Open-Source Framework for Real-Time Interactive Video World Models — [arXiv:2605.30263](https://arxiv.org/abs/2605.30263), [shengshu-ai/minWM](https://github.com/shengshu-ai/minWM)
- Qwen-VLA: Unifying Vision-Language-Action Modeling — [arXiv:2605.30280](https://arxiv.org/abs/2605.30280), [QwenLM/Qwen-VLA](https://github.com/QwenLM/Qwen-VLA)
- How Perplexity Brought Voice Search to Millions — [OpenAI Developers 블로그](https://developers.openai.com/blog/realtime-perplexity-computer)
- Project Fetch: Phase two — [Anthropic Research](https://www.anthropic.com/research/project-fetch-phase-two)
- Previewing the Model Hardware Standard — [Anthropic News](https://www.anthropic.com/news/model-hardware-standard-research-preview)
- Murmur — [jkf87/murmur](https://github.com/jkf87/murmur)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.

