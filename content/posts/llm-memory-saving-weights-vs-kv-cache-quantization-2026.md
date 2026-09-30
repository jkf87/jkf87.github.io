---
title: "로컬 LLM 메모리 절약 두 갈래: 가중치 2비트(OA-EM)와 KV 캐시 압축(TurboQuant) 정리"
date: 2026-09-30
author: 한준구(코난쌤)
description: "LLM 메모리 절감은 가중치와 KV 캐시 두 레버로 나뉩니다. TurboQuant는 KV 캐시를 3.5비트/channel까지 무손실 압축하고, OA-EM은 2비트 가중치 양자화의 초기화 붕괴를 해결합니다. 두 논문 본문과 코드를 재확인한 수치로 두 갈래를 비교 정리했습니다."
tags:
  - LLM
  - 메모리
  - 양자화
  - KV캐시
  - 로컬추론
refactor_hub_id: reasoning-efficiency-02
aliases:
  - turboquant-extreme-compression-ai-efficiency
  - turboquant-16gb-mac-local-llm-revolution
  - 2bit-llm-quantization-oaem-2026-04-13
draft: false
sources_read: "TurboQuant(arXiv 2504.19874)와 OA-EM(arXiv 2604.08118) 논문은 PDF 본문을 텍스트 추출해 읽고 인용 수치를 원문에서 재확인함. Google Research 블로그 본문 읽음. 코드·데이터: github.com/kenno94-IK/aqlm-oaem 저장소와 허깅페이스 추론 모델 3종(Llama 3.2 3B·Llama 3.1 8B·Qwen 2.5 3B) 접속 확인, TurboQuant는 공식 저자 코드 없음(써드파티 구현만 검색됨). Alex Ziskind 영상은 존재·제목 확인(본문 수치는 재현하지 않음), turbo-quant.com 통합 상태 페이지와 llama.cpp PR #21089(closed) 상태 확인."
novelty_vs_paper: "가중치/KV 캐시 두 레버 분류와 증상 기반 진단 순서, 레버별 수치 비교표, 차트 2종, ρ 재계산(2bpp 18.0·3bpp 0.07로 논문 표와 일치 확인), TurboQuant 본문 예시 산식의 실제 계산값 2.25와 표기 2.5의 불일치 발견은 블로그봇의 재구성 기여. 알고리즘 구조와 벤치마크 수치 자체는 각 논문·블로그·영상의 기여임."
---

## 한눈에 보는 결론

로컬에서 LLM을 돌릴 때 메모리를 잡아먹는 곳은 크게 두 군데입니다. 모델 가중치(로드되면 고정)와 KV 캐시(컨텍스트가 길어질수록 커짐)입니다. 이번에 통합 정리한 글 3편이 정확히 이 두 갈래에 하나씩 대응합니다.

| 레버 | 대표 방법 | 이번에 원문에서 재확인한 수치 | 적용 시점 |
| --- | --- | --- | --- |
| 가중치 양자화 | AQLM + OA-EM (2bpp) | WikiText-2 ppl 11.53 vs FP16 7.28 (Llama 3.2 3B) | 모델 준비 단계, 오프라인 캘리브레이션 |
| KV 캐시 압축 | TurboQuant | LongBench-V1 3.5bit 50.06 ≈ FP16 49.89 (Llama-3.1-8B) | 추론 중 즉시, 학습 불필요 |
| 두 레버 동시 | Q4 가중치 + KV 캐시 압축 | 16GB Mac Mini + 9B Q4에서 131K 컨텍스트 구동 보고(영상) | GGUF 그대로, 캐시 플래그만 변경 |

<span style="background-color: #fff59d"><strong>두 레버는 독립이라 동시에 쓸 수 있고, 병목 위치는 증상으로 판별됩니다.</strong></span> <span style="background-color: #fff59d"><strong>모델 로드부터 실패하면 가중치 레버, 로드는 되는데 긴 컨텍스트에서 크래시하면 KV 캐시 레버입니다.</strong></span>

검증 기준일은 2026-09-30입니다. 두 논문은 PDF 본문을 직접 읽었고, 인용 수치는 전부 원문에서 다시 대조했습니다.

## 무엇을 비교했나

통합 대상 세 편과 1차 출처입니다.

1. TurboQuant 논문 정리 — [TurboQuant (arXiv 2504.19874)](https://arxiv.org/abs/2504.19874), Google Research·NYU·Google DeepMind (Zandieh, Daliri, Hadian). <span style="background-color: #fff59d"><strong>KV 캐시를 3.5비트/channel까지 무손실 압축하는 온라인 벡터 양자화</strong></span>.
2. 16GB Mac 실험 정리 — Alex Ziskind 영상 ["After This, 16GB Feels Different"](https://www.youtube.com/watch?v=XLlQDfhyBjc)과 [turbo-quant.com의 llama.cpp 통합 상태 페이지](https://turbo-quant.com/turboquant-llama-cpp). TurboQuant를 실제 맥에서 돌린 사례.
3. 2비트 가중치 양자화 정리 — [Initialisation Determines the Basin (arXiv 2604.08118)](https://arxiv.org/abs/2604.08118), 셰필드 대학 (Kennedy, Moosavi). 코드북 초기화가 2bpp 품질을 결정한다는 분석과 [공식 코드](https://github.com/kenno94-IK/aqlm-oaem).

보조 출처로 [Google Research 블로그](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)와 [llama.cpp PR #21089](https://github.com/ggml-org/llama.cpp/pull/21089)을 확인했습니다. 정리 과정에서 기존 글의 TurboQuant 논문 링크(arXiv 2504.03475)가 실제로는 광학 논문이었음을 확인했고, 올바른 번호(2504.19874)로 바로잡았습니다.

## 방법 비교

| 축 | TurboQuant (KV 캐시) | OA-EM (가중치 2bpp) |
| --- | --- | --- |
| 압축 대상 | 추론 중 생성되는 K/V 벡터 | 모델 가중치 자체 |
| 시점 | 온라인, 즉시 적용 | 오프라인 캘리브레이션 + PV-tuning |
| 학습 필요 | 없음 (data-oblivious) | 캘리브레이션 데이터 + 파인튜닝 |
| 핵심 아이디어 | 무작위 회전 후 좌표별 최적 스칼라 양자기, 잔차에 1비트 QJL로 내적 비편향화 | Hessian 가중 Mahalanobis 거리 기반 EM으로 코드북 초기화 |
| 재확인 수치 | LongBench-V1: 2.5bit 49.44 / 3.5bit 50.06 / FP16 49.89, 압축 ≥4.5× | post-PV ppl: greedy 11.76~12.66, OA-EM 11.49~11.53 (beam 4~16) |
| 실험 환경 | A100 1장, Llama-3.1-8B-Instruct·Ministral-7B | Llama 3.2 3B·Llama 3.1 8B·Qwen 2.5 3B |
| 코드 | 공식 코드 없음 (확인 시점 기준) | GitHub + 허깅페이스 추론 모델 3종 공개 |
| 추론 비용 | 메모리 대역폭 절감, H100 4비트 attention logits 최대 8배 가속(블로그 보고) | LUT O(1) 역양자화, 그룹당 MAC 0으로 ARM·엣지 유리 |

![압축 레버별 품질 곡선 비교](../media/llm-memory-saving-weights-vs-kv-cache-quantization-2026/chart-01-bits-quality.png)

두 그래프의 모양 차이가 이번 정리의 요점입니다. <span style="background-color: #fff59d"><strong>KV 캐시는 3.5비트에서 FP16과 사실상 동일한 점수(50.06 vs 49.89)를 유지합니다.</strong></span> 가중치 2bpp는 초기화 방식에 따라 perplexity가 갈리고, <span style="background-color: #fff59d"><strong>더 넓은 beam search가 greedy에선 오히려 12.01로 나빠집니다.</strong></span>

## 언제 무엇을 쓰나

- 모델 로드 단계에서 메모리 부족: 가중치 양자화. Q4가 기본값이고, 2bpp가 필요하면 AQLM 계열 + OA-EM 초기화로 갑니다.
- 긴 컨텍스트에서 크래시: KV 캐시 양자화. <span style="background-color: #fff59d"><strong>K는 Q8 유지, V만 저비트로 깎는 비대칭 적용이 안전한 시작점입니다.</strong></span>
- 긴 컨텍스트 + 소형 기기 둘 다: 두 레버를 겹칩니다. <span style="background-color: #fff59d"><strong>영상 사례에서 16GB Mac Mini가 9B Q4 모델로 131K 컨텍스트를 돌렸다는 보고가 이 구성입니다.</strong></span>
- 엣지 기기 추론: 가중치 2bpp의 LUT 역양자화가 산술 연산을 안 쓰므로 ARM CPU에서 유리합니다.

![로컬 LLM 추론 메모리 지도](../media/llm-memory-saving-weights-vs-kv-cache-quantization-2026/chart-02-memory-map.png)

## 블로그봇이 직접 확인한 것

- 두 논문의 PDF 본문을 텍스트로 추출해 읽고, 인용 수치를 원문에서 재확인했습니다. TurboQuant: 3.5/2.5 bits, 49.44/50.06/49.89, ≥4.5×, NIAH 4× 압축에서 full-precision 동일.
- 같은 방식으로 OA-EM 수치도 재확인했습니다. 352.39/60.61/7.28(pre-PV greedy beam4/beam8/FP16), 11.76→12.01(greedy post-PV), 11.53→11.49(OA-EM post-PV), 43→0.23(basin 지속).
- OA-EM 논문의 representational ratio ρ=N/K^M을 Llama 3.2 3B 레이어 크기(3072×3072, 그룹 8)로 직접 다시 계산했습니다. <span style="background-color: #fff59d"><strong>2bpp에서 18.0, 3bpp에서 0.07이 나와 논문 표(≈18, ≈0.07)와 일치했습니다.</strong></span>
- TurboQuant 본문의 유효 비트 예시 산식을 검산했습니다. <span style="background-color: #fff59d"><strong>(32×3+96×2)/128을 계산하면 2.25입니다.</strong></span> <span style="background-color: #fff59d"><strong>본문 표기인 2.5와 어긋납니다.</strong></span> 예시 숫자의 오차로 보이고, 이번 정리에서는 비정수 비트가 아웃라이어 채널 분리에서 나온다는 구조만 인용합니다.
- OA-EM 공식 저장소와 허깅페이스 추론 모델 3종(Llama 3.2 3B ppl 11.53, Llama 3.1 8B 9.25, Qwen 2.5 3B 10.73) 접속을 확인했습니다. TurboQuant는 공식 저자 코드를 찾지 못했습니다(써드파티 구현만 검색됨).
- Alex Ziskind 영상은 실제 존재를 확인했고(제목 "After This, 16GB Feels Different"), llama.cpp 통합 상태는 <span style="background-color: #fff59d"><strong>PR #21089(TBQ3_0/TBQ4_0 추가)가 2026-09-30 확인 시점 closed(미병합)</strong></span>인 것까지 확인했습니다.
- 비교 차트 2종을 직접 만들었고, 그래프에 쓴 수치는 전부 위 재확인 값입니다.

## 한계와 반론

- 두 방법의 벤치마크가 다릅니다. LongBench-V1 점수와 WikiText-2 perplexity는 직접 비교 불가능하고, 각 축 안의 비교로만 읽어야 합니다.
- 영상의 실측 수치(131K 구동, 3.6GB 여유, 54→37 tok/s 하락, NIAH 3/3)는 공개된 보고치이고 블로그봇이 재현한 값이 아닙니다. 비대칭 적용 권고도 영상과 커뮤니티 포크 기준입니다.
- <span style="background-color: #fff59d"><strong>H100 8배 가속과 KV 메모리 6배 절감은 Google 블로그의 주장이고, 논문 본문 실험은 A100 기준 압축 ≥4.5×·무손실입니다.</strong></span> 숫자를 인용할 때 출처를 분리해서 적었습니다.
- TurboQuant는 llama.cpp 공식 브랜치에 아직 없습니다(2026-09-30 기준 PR closed). 커뮤니티 포크를 쓰려면 유지보수 리스크를 감수해야 합니다.
- OA-EM도 2bpp에서 FP16 대비 ppl 갭(11.53 vs 7.28)은 남아 있습니다. <span style="background-color: #fff59d"><strong>초기화가 붕괴를 막는 것이지 압축 자체의 손실을 없애는 건 아닙니다.</strong></span>
- llama.cpp의 tbq3_0/tbq4_0 세부 비트폭(약 3.0625/4.0625)은 PR 설명 기준이라 병합 시 바뀔 수 있습니다.

## 적용 규칙

이번에 원문을 확인한 범위에서만 뽑은 규칙입니다.

1. 메모리 문제는 먼저 위치로 분류합니다. 모델 파일 로드부터 실패하면 가중치 레버, 로드 후 긴 컨텍스트에서 실패하면 KV 캐시 레버로 갑니다. 영상 사례(16GB + 9B Q4 로드 성공, 131K Q8 캐시 크래시)가 이 분류의 실례입니다.
2. KV 캐시 양자화는 비대칭부터 시작합니다. K=Q8 유지 + V만 Turbo 3/4 적용이며, <span style="background-color: #fff59d"><strong>K·V에 같은 저비트를 깎는 대칭 적용은 영상에서 긴 컨텍스트 검색 과제 0점으로 나타났습니다.</strong></span>
3. 2bpp 가중치 양자화에서 beam width를 키우는 건 답이 아닙니다. <span style="background-color: #fff59d"><strong>greedy 초기화는 beam 8→16에서 11.76→12.01로 나빴고</strong></span>, 초기화를 OA-EM으로 바꾸는 게 beam width를 키우는 것보다 효과가 컸습니다(11.53 vs 12.01).
4. 코드북 압축 전에 ρ를 계산해 봅니다. ρ=N/K^M이 1보다 크면(2bpp의 18 등) 초기화에 민감한 구간이고, 1보다 작으면(3bpp의 0.07) 관대한 구간입니다. 레이어 크기와 그룹 크기만 있으면 계산됩니다.
5. 두 레버를 겹칠 때는 저장된 GGUF를 바꾸지 않습니다. <span style="background-color: #fff59d"><strong>KV 캐시 양자화는 런타임 설정이라 모델 파일이 그대로 쓰인다는 점</strong></span>을 통합 상태 페이지에서 확인했습니다.
6. 비공식 포크를 쓰기 전에 자체 점검을 돌립니다. 바늘찾기류 과제 몇 개로 검색 품질을 확인한 뒤 도입합니다. 영상의 대칭 적용 실패가 점검의 필요성을 보여줍니다.
7. 공식 지원 여부는 사용 시점에 다시 확인합니다. 이 글 기준 llama.cpp PR #21089은 closed이고, Ollama 같은 상위 도구는 llama.cpp 병합을 따라갑니다.

## 자주 묻는 질문

**Q. KV 캐시 압축만으로 16GB 맥에서 큰 모델을 돌릴 수 있나요?**
가중치가 먼저 들어가야 합니다. 영상 사례는 9B Q4(약 6GB)로 가중치를 줄인 뒤, KV 캐시를 3비트급으로 압축해 131K 컨텍스트를 확보한 구성입니다. 두 레버를 함께 쓴 사례로 읽으면 됩니다.

**Q. 2비트 가중치 양자화는 실용적인가요?**
용도에 따라 갈립니다. <span style="background-color: #fff59d"><strong>OA-EM 적용 후에도 WikiText-2 ppl이 11.53으로 FP16(7.28)보다 높습니다.</strong></span> 초기화 붕괴(352.39)는 막았지만 품질 갭은 남아 있어, 온디바이스 보조 용도에 맞는지 판단이 필요합니다.

**Q. TurboQuant를 지금 llama.cpp나 Ollama에서 쓸 수 있나요?**
공식 브랜치에는 없습니다. 2026-09-30 확인 기준 통합 PR #21089이 closed 상태고, 커뮤니티 포크(TheTom/turboquant_plus)로 먼저 써볼 수 있습니다.

**Q. 8배 빨라진다는 숫자는 논문 결과인가요?**
Google 블로그가 H100에서 4비트 TurboQuant의 attention logits 계산을 32비트 키 대비 최대 8배라고 보고했고, 논문 본문 실험은 A100 기준입니다. 이 글은 두 출처를 분리해서 적었습니다.

## 참고 자료

- [TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate (arXiv 2504.19874)](https://arxiv.org/abs/2504.19874)
- [Google Research 블로그: TurboQuant](https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/)
- [Alex Ziskind, "After This, 16GB Feels Different" (YouTube)](https://www.youtube.com/watch?v=XLlQDfhyBjc)
- [turbo-quant.com: llama.cpp 통합 상태](https://turbo-quant.com/turboquant-llama-cpp)
- [llama.cpp PR #21089: add CPU TurboQuant KV cache types](https://github.com/ggml-org/llama.cpp/pull/21089)
- [Initialisation Determines the Basin (arXiv 2604.08118)](https://arxiv.org/abs/2604.08118)
- [aqlm-oaem 공식 코드 (GitHub)](https://github.com/kenno94-IK/aqlm-oaem)
- [OA-EM 2비트 추론 모델 (Hugging Face)](https://huggingface.co/kennedyian94)

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
