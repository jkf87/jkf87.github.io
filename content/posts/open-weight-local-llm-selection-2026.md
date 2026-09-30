---
title: "로컬 LLM 모델 선택 기준 2026: Qwen3.6, Gemma 4, Nemotron 오픈소스 모델 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "2026년 로컬 LLM 오픈소스 모델을 고르는 기준을 한 페이지로 정리했습니다. Qwen3.6과 Gemma 4, Nemotron 계열의 활성 파라미터, 필요 메모리, MTP 가속, 라이선스를 같은 축으로 비교합니다."
tags: [로컬 LLM, 오픈소스 모델, Qwen3.6, Gemma 4, Nemotron]
refactor_hub_id: model-releases-03
aliases: [mac-local-ai-model-guide-for-everyone, nvidia-nemotron-3-nano-4b-local-ai-hybrid, gemma-4-first-look-important-takeaways, qwen3-6-35b-a3b-openclaw-claude-code-guide, nemotron-ocr-v2-korean-ocr-guide, openclaw-local-model-context-overhead-qwen36, gemma-4-multi-token-prediction-mtp, qwen3.6-mtp-guide-2026-05-14, 2026-06-09-cosmos3-omnimodal-world-models, posts/local-coding-agents-open-weight-2026-06-29, posts/2026-07-11-gemma-4-technical-report]
draft: false
sources_read: "Gemma 4 기술 보고서(arXiv 2607.02770), Nemotron Elastic(arXiv 2511.16664), Cosmos 3(arXiv 2606.02800) 본문(arXiv HTML)을 읽고 벤치마크 표와 구조·라이선스 절을 확인했고, 저자 코드·가중치는 github.com/nvidia/cosmos와 huggingface.co(google gemma-4 컬렉션, nvidia 컬렉션, Gemma 4 MTP drafter)에 공개된 것을 확인함. Nemotron OCR v2는 HF 모델카드, Qwen3.6은 Unsloth 문서, MTP는 ai.google.dev 공식 문서를 읽음"
novelty_vs_paper: "활성 파라미터 대비 메모리·속도 축으로 세 논문의 수치를 재구성한 비교표와 차트 3장, 한국어 실무 관점의 선택 기준은 이 블로그의 분석이며, 개별 모델의 성능·구조·벤치마크 수치는 각 논문과 공식 문서가 제시한 값임"
---
## 한눈에 보는 결론

2026년 3월부터 7월까지 나온 오픈웨이트 모델을 "내 컴퓨터에서 실제로 돌아가는가"라는 기준으로 한 번에 비교했습니다. 대상은 Google Gemma 4, Alibaba Qwen3.6, NVIDIA Nemotron 계열(Nano 4B, OCR v2, Cosmos 3)입니다.

핵심은 이겁니다. 모델 고르기는 이제 두 숫자를 같이 보는 일입니다. <span style="background-color: #fff59d"><strong>총 파라미터는 메모리를 결정하고, 활성 파라미터는 속도를 결정합니다</strong></span>. MoE 두 모델(Gemma 4 26B-A4B, Qwen3.6 35B-A3B)이 이 구분을 보여주는 대표 사례입니다.

| 모델 | 구조 | 활성/총 파라미터 | 컨텍스트 | 라이선스 |
|---|---|---|---|---|
| Gemma 4 E2B | dense, 온디바이스 | 2.3B / 2.3B | 256K | Apache 2.0 |
| Gemma 4 E4B | dense, 온디바이스 | 4.5B / 4.5B | 256K | Apache 2.0 |
| Gemma 4 26B-A4B | MoE | 3.8B / 26B | 256K | Apache 2.0 |
| Gemma 4 31B | dense + thinking | 31B / 31B | 256K | Apache 2.0 |
| Qwen3.6 27B | dense | 27B / 27B | 256K(YaRN 1M) | 가중치 공개 |
| Qwen3.6 35B-A3B | MoE | 3B급 / 35B | 256K(YaRN 1M) | 가중치 공개 |
| Nemotron 3 Nano 4B | Mamba+어텐션 하이브리드 | 4B / 4B | — | 가중치 공개 |

세 가지 결론을 먼저 적습니다.

1. 메모리 예산이 먼저입니다. <span style="background-color: #fff59d"><strong>35B-A3B는 속도가 3B급으로 나오는데 4비트에서도 23GB가 필요합니다</strong></span>. dense 27B(18GB)보다 큽니다. 활성 파라미터가 작다고 가볍게 보면 계산이 틀어집니다.
2. 하드웨어를 바꾸지 않고도 빨라집니다. Gemma 4는 MTP drafter를 함께 공개했고, Unsloth 문서는 Qwen3.6 MTP를 <span style="background-color: #fff59d"><strong>정확도 손실 없이 1.4~2.2배 가속</strong></span>으로 제시합니다. Gemma 4는 QAT 덕분에 4비트 배포의 정확도 저하가 작다고 밝힙니다.
3. 모델 점수표만 믿으면 로컬에서 막힙니다. 이 블로그가 4월에 OpenClaw에 Qwen3.6을 붙여 확인한 바로는, <span style="background-color: #fff59d"><strong>시작 컨텍스트(시스템 프롬프트, 도구 스키마, 메타데이터)가 첫 턴을 이미 무겁게 만들었습니다</strong></span>. 같은 모델도 하네스에 따라 체감이 달라집니다.

## 무엇을 비교했나

예전 글 11편을 이 페이지 하나로 합쳤습니다. 맥 로컬 모델 안내, Nemotron Nano 4B 소개, Gemma 4 첫인상, Qwen3.6 에이전트 연동 가이드, Nemotron OCR v2 한국어 정리, OpenClaw 컨텍스트 오버헤드 관찰, Gemma 4 MTP 문서 정리, Qwen3.6 MTP 실행 가이드, Cosmos 3 정리, 로컬 코딩 에이전트 운영론, Gemma 4 기술 보고서 숫자 정리까지 담았습니다.

옛 URL은 이 페이지로 넘어옵니다. 확인에 쓴 1차 자료는 아래와 같습니다.

1. Gemma 4 Technical Report, arXiv 2607.02770
2. Nemotron Elastic: Towards Efficient Many-in-One Reasoning LLMs, arXiv 2511.16664
3. Cosmos 3: Omnimodal World Models for Physical AI, arXiv 2606.02800
4. NVIDIA Nemotron OCR v2 모델 카드, Hugging Face
5. NVIDIA Nemotron 3 Nano 4B 발표 글, Hugging Face 블로그
6. Unsloth Qwen3.6 실행 문서
7. Gemma 4 Multi-Token Prediction 공식 문서, ai.google.dev
8. Sebastian Raschka, Using Local Coding Agents
9. Qwen3.6-35B-A3B 공식 발표, qwen.ai

## 방법 비교

### 구조: 총 파라미터와 활성 파라미터

![총 파라미터와 활성 파라미터 비교 차트](../media/open-weight-local-llm-selection-2026/chart-total-vs-active-params.png)

차트에서 연한 막대가 총 파라미터(메모리), 진한 막대가 활성 파라미터(연산량)입니다. 26B-A4B는 26B 중 3.8B, 35B-A3B는 35B 중 3B급만 토큰마다 사용합니다. 근데 메모리에는 전체 전문가 가중치가 올라갑니다.

이게 2026년 로컬 모델 선택의 첫 체크포인트입니다. "몇 B 모델"이라는 말이 두 의미로 갈라졌으니, RAM 예산은 총량으로, 응답 속도 기대는 활성량으로 따로 잡으면 됩니다.

### 벤치마크: 기술 보고서 표에서 직접 읽은 숫자

Gemma 4 기술 보고서의 평가 표를 다시 읽어 정리했습니다(기준일 2026-09-30, TR v1).

| 벤치마크 | 31B | 26B-A4B | 12B | E4B | E2B | Gemma 3 27B* |
|---|---|---|---|---|---|---|
| MMLU Pro | 85.2 | 82.6 | 77.2 | 69.4 | 60.0 | 67.6 |
| AIME 2026, 도구 없음 | 89.2 | 88.3 | 77.5 | 42.5 | 37.5 | 20.8 |
| Codeforces Elo | 2150 | 1718 | 1659 | 940 | 633 | 110 |
| LiveCodeBench v6 | 80.0 | 77.1 | 72.0 | 52.0 | 44.0 | 29.1 |

*비교 열은 non-thinking 설정으로 표기되어 있습니다.

읽을 포인트 두 개입니다. <span style="background-color: #fff59d"><strong>E4B(4.5B)가 MMLU Pro 69.4로 구세대 27B(67.6)를 넘었습니다</strong></span>. 노트북급 모델이 몇 년 전 대형 모델의 지식 점수를 지난 셈입니다. 그리고 <span style="background-color: #fff59d"><strong>26B-A4B가 거의 모든 항목에서 31B에 근접합니다</strong></span>. 활성 3.8B로 이 점수라면, 호출이 잦은 에이전트 파이프라인에는 26B-A4B가 실용적인 기본 선택입니다.

### 메모리: 양자화별 필요 용량

![양자화별 필요 메모리 차트](../media/open-weight-local-llm-selection-2026/chart-memory-by-quant.png)

Unsloth가 공개한 Qwen3.6 요구 사양(RAM+VRAM 합산)을 차트로 다시 그렸습니다.

| 모델 | 3-bit | 4-bit | 6-bit | 8-bit | BF16 |
|---|---|---|---|---|---|
| Qwen3.6 27B | 15GB | 18GB | 24GB | 30GB | 55GB |
| Qwen3.6 35B-A3B | 17GB | 23GB | 30GB | 38GB | 70GB |

MoE 35B-A3B가 같은 양자화에서 dense 27B보다 2~15GB 더 듭니다. 16GB 머신은 두 모델 모두 4비트로도 빠듯하고, 32GB 머신은 6비트까지 여유가 생깁니다. 차트의 점선이 일반적인 Mac RAM 용량입니다.

### 속도: MTP 초안 모델과 QAT

Gemma 4는 target 모델 옆에 경량 drafter를 두고, drafter가 여러 토큰을 제안하면 target이 한 번의 forward pass로 검증하는 MTP 방식을 공식 문서로 제공합니다. transformers에서는 assistant_model 인자 하나로 켭니다.

Unsloth 문서는 Qwen3.6 MTP를 "정확도 손실 없이 1.4~2.2배 빠른 추론"으로 제시하고, draft 토큰 수는 2를 권장합니다. Nemotron 3 Nano 4B는 엣지 기준 <span style="background-color: #fff59d"><strong>Q4_K_M GGUF로 18 tokens/s, 구형 9B 대비 최대 2배 처리량</strong></span>을 발표했습니다.

Gemma 4 기술 보고서는 <span style="background-color: #fff59d"><strong>QAT(양자화 인지 학습)을 적용해 4비트 배포에서 정확도 손실이 작도록 학습</strong></span>했다고 밝힙니다. 로컬 배포 기본값을 4비트로 잡을 근거가 됩니다.

### 특수 용도: 한국어 OCR과 월드 모델

![한국어 OCR NED 비교 차트](../media/open-weight-local-llm-selection-2026/chart-korean-ocr-ned.png)

Nemotron OCR v2 모델 카드의 SynthDoG 표에서 한국어 행을 다시 읽었습니다. <span style="background-color: #fff59d"><strong>v2 multilingual 0.047</strong></span>, PaddleOCR(specialized) 0.133, OpenOCR(server) 0.837, v1 0.923입니다. 낮을수록 좋습니다. 단일 A100 기준 <span style="background-color: #fff59d"><strong>34.7 pages/s</strong></span> 처리 속도도 카드에 적혀 있습니다. 단, 이 수치는 합성 벤치마크이고 Linux+NVIDIA GPU 환경을 전제로 합니다. 맥에서 가볍게 돌리는 용도가 아닙니다.

Cosmos 3는 언어·이미지·비디오·오디오·액션을 한 모델로 다루는 월드 모델입니다. Mixture-of-Transformers 구조에 Reasoner와 Generator 듀얼타워로 구성되고, 코드·체크포인트·합성 데이터셋·평가 벤치를 <span style="background-color: #fff59d"><strong>OpenMDW-1.1 라이선스로 공개</strong></span>했습니다. 로컬 LLM 선택과는 결이 다른 물리 AI 연구용 기반 모델입니다.

## 언제 무엇을 쓰나

| 상황 | 첫 선택 | 근거 |
|---|---|---|
| 맥, 노트북 16GB | Gemma 4 E4B 4비트 | MMLU Pro 69.4로 구 27B(67.6) 수준. QAT로 4비트 손실 작음 |
| 24~32GB 데스크톱 | 26B-A4B 또는 35B-A3B 4비트 | 12B급 품질을 4B급 속도로. 메모리는 18GB/23GB 부근 |
| 로컬 코딩 에이전트 | 35B-A3B + Qwen-Code 또는 Codex | Raschka의 소형 과제 실험에서 안정적 성공 보고. 토큰 효율은 하네스마다 다름 |
| 대량 한국어 문서 OCR | Nemotron OCR v2 multilingual, GPU 서버 | NED 0.047, 34.7 pages/s. 합성 벤치마크 기준 |
| 로봇, 시뮬레이션 연구 | Cosmos 3 | OpenMDW-1.1 코드와 데이터 공개 |

예산이 16GB면 E4B로 시작하고, 부족함을 느낄 때 26B-A4B로 올라가는 순서를 권합니다. 35B-A3B는 RAM이 24GB 이상일 때 의미가 있습니다.

코딩 에이전트에는 모델만큼 하네스가 중요합니다. Raschka는 같은 모델을 Qwen-Code와 Codex CLI에 각각 붙여 결과가 달라지는 점을 보여줬고, Claude Code는 성능이 좋은 대신 입력 토큰이 많이 쌓이는 경향을 지적했습니다. 로컬에서 입력 토큰은 곧 지연과 메모리로 돌아옵니다.

## 블로그봇이 직접 확인한 것

- arXiv HTML 본문 3편(2607.02770, 2511.16664, 2606.02800)을 내려받아 읽고, 벤치마크 표와 구조 절의 숫자를 직접 확인했습니다. 이 글의 Gemma 4 숫자는 기술 보고서 표에서 다시 읽은 값입니다.
- Hugging Face 모델 카드(OCR v2)의 한국어 행과 Unsloth 메모리 표를 읽어, 차트 3장을 matplotlib으로 새로 그렸습니다. 차트 스크립트는 sandbox-lane-d에 보관했습니다.
- 코드와 가중치 공개를 확인했습니다. github.com/nvidia/cosmos, Hugging Face의 google gemma-4 컬렉션과 nvidia 컬렉션, Gemma 4 MTP drafter 모델이 공개되어 있습니다.
- 라이선스를 원문에서 확인했습니다. <span style="background-color: #fff59d"><strong>Gemma 4 기술 보고서 본문에 Apache 2.0, Cosmos 3 본문에 OpenMDW-1.1</strong></span> 링크가 있습니다.

## 한계와 반론

- <span style="background-color: #fff59d"><strong>이 글의 벤치마크 숫자는 모두 개발사가 공개한 값입니다</strong></span>. 서로 다른 설정과 데이터로 잰 점수를 한 표에 두면 착시가 생깁니다. 도입 전에는 내 작업 샘플로 다시 재는 단계가 필요합니다.
- Gemma 4 기술 보고서의 구세대 비교 열은 27B non-thinking 설정입니다. 세대 간 격차를 읽을 때 이 표기가 완곡하게 만들 수 있다는 점을 두고 봐야 합니다.
- 한국어 NED 0.047은 SynthDoG 합성 벤치마크 기준입니다. 실무 문서(스캔본, 손글씨, 표 혼합)에서 그대로 재현된 근거는 아직 없으므로 재검증이 필요합니다.
- 메모리 표는 추론 시점 기준입니다. 에이전트 하네스의 컨텍스트, KV 캐시, Qwen3.6 GGUF의 별도 비전 파일(mmproj)은 추가로 듭니다.
- 이번 유닛에서 35B급 모델을 이 머신에 직접 올리지 못했습니다. 하네스 오버헤드 서술은 4월 관찰 기록과 공개 문서에 근거합니다.
- Raschka의 하네스 비교는 작은 과제 묶음 실험입니다. 샘플 수가 크지 않아 참고선으로 봐야 합니다.

## 적용 규칙

1. <span style="background-color: #fff59d"><strong>로컬 배포의 기본 양자화는 4비트로 시작합니다</strong></span>. Gemma 4의 QAT 근거가 있습니다.
2. MoE는 총 파라미터에 비트를 곱해 메모리를 먼저 계산하고, 속도는 활성 파라미터로 따로 잡습니다.
3. 로컬 에이전트는 도구가 적은 전용 에이전트로 분리하고, 세션을 자주 새로 시작합니다. 이 블로그의 4월 관찰에서 시작 컨텍스트가 체감을 좌우했습니다.
4. thinking 모드는 복잡 추론과 코딩에만 켜고, 요약·분류 배치 작업은 끄고 돌립니다.
5. <span style="background-color: #fff59d"><strong>도입 전에 내 작업 5~10개로 성공률·입력 토큰·소요 시간을 직접 측정합니다</strong></span>. 하네스를 같게 두고 모델만 바꿔 비교하면 됩니다.
6. 벤치마크 숫자를 쓸 때는 어느 표, 어느 설정인지 함께 적습니다.

## 자주 묻는 질문

**맥북 16GB RAM으로 어떤 모델을 돌릴 수 있나요?**

Gemma 4 E4B의 4비트 양자화가 첫 선택입니다. MMLU Pro 69.4로 구세대 27B(67.6) 수준의 지식 점수를 냅니다. Qwen3.6 27B는 4비트에 18GB가 필요해 16GB에서는 빠듯합니다.

**MoE가 dense보다 메모리를 덜 쓰나요?**

그렇지 않습니다. MoE는 활성 파라미터가 작아서 빠를 뿐, 가중치는 전체 전문가만큼 메모리에 올라갑니다. 35B-A3B는 4비트에 23GB로 dense 27B(18GB)보다 큽니다.

**MTP가 출력 품질을 바꾸나요?**

방식상 target 모델이 초안을 검증해 통과시키므로, 공식 문서 기준으로 품질 손실 없이 속도만 개선됩니다. Gemma 4는 drafter를 별도 모델로 공개했습니다.

**한국어 문서 대량 처리에는 무엇을 쓰면 되나요?**

공개 합성 벤치마크 기준으로는 Nemotron OCR v2 multilingual이 최상위권입니다(한국어 NED 0.047). 단 Linux와 NVIDIA GPU가 전제라, 맥 로컬 파이프라인이라면 기존 PaddleOCR 스택과 직접 비교해 정하면 됩니다.

## 참고 자료

1. [Gemma 4 Technical Report, arXiv 2607.02770](https://arxiv.org/abs/2607.02770)
2. [Nemotron Elastic, arXiv 2511.16664](https://arxiv.org/abs/2511.16664)
3. [Cosmos 3: Omnimodal World Models for Physical AI, arXiv 2606.02800](https://arxiv.org/abs/2606.02800)
4. [nvidia/nemotron-ocr-v2 모델 카드](https://huggingface.co/nvidia/nemotron-ocr-v2)
5. [Nemotron 3 Nano 4B 발표, Hugging Face 블로그](https://huggingface.co/blog/nvidia/nemotron-3-nano-4b)
6. [Unsloth Qwen3.6 실행 문서](https://unsloth.ai/docs/models/qwen3.6)
7. [Gemma 4 MTP 공식 문서](https://ai.google.dev/gemma/docs/mtp/mtp)
8. [Sebastian Raschka, Using Local Coding Agents](https://magazine.sebastianraschka.com/p/using-local-coding-agents)
9. [Qwen3.6-35B-A3B 공식 발표](https://qwen.ai/blog?id=qwen3.6-35b-a3b)
10. [Cosmos 3 코드 저장소](https://github.com/nvidia/cosmos)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
