---
title: "Solar Open 2: 한국 모델도 이제 업무 모델 쪽으로 오고 있다"
date: 2026-07-22
draft: false
tags:
  - Solar-Open-2
  - Upstage
  - open-weight
  - AI-agent
  - MoE
  - Korean-LLM
  - long-context
  - quantization
  - in-house-ai
categories:
  - AI
  - Agent
description: "Upstage Solar Open 2 250B-A15B를 기술 리포트와 모델카드 기준으로 읽었다. 핵심은 한국어 모델이 단순 대화를 넘어 오피스 문서와 업무 산출물, 온프레미스 agent model 쪽으로 이동하고 있다는 점이다."
aliases:
  - /posts/solar-open2-agentic-open-weight-2026-07-22
---

![Solar Open 2를 에이전트용 command center로 재구성한 이미지. 250B MoE 모델이 여러 전문가 모듈, 긴 컨텍스트 타임라인, 문서·코드·도구 호출 흐름을 하나로 묶는다는 점을 시각화했다.](/images/solar-open2-agentic-open-weight-2026-07-22/hero.jpg)

이제 한국 모델도 어느 정도 쓸 만해지는 것 같습니다. 오피스 업무 벤치마크 성적으로 보면, 문서를 만들고 업무를 처리하는 능력이 DeepSeek-V4-Pro 수준까지 왔습니다.

Upstage가 공개한 **Solar Open 2**는 250B 규모의 MoE 모델입니다. 매 토큰에서 활성화되는 파라미터는 15B라서, 표기는 **250B-A15B**입니다. 눈에 띄는 건 Upstage의 in-house benchmark인 **Ko-GDPval** 점수인데, Solar Open 2가 **86.8점**을 받았고 비교표에 함께 나온 DeepSeek-V4-Pro 1.6T가 86.9점입니다. 자체 평가라는 단서는 붙여야 하지만, 오피스 업무 평가에서 한국 모델이 DeepSeek-V4-Pro와 거의 붙었다는 이야기가 됩니다.

Solar Open 2는 "ChatGPT보다 좋냐"로 볼 모델은 아닙니다. 한국어로 된 문서, 스프레드시트, 보고서, 프레젠테이션, 법률·금융·공공 업무처럼 외부 API로 보내기 어려운 일을 조직 안에서 처리하려는 모델입니다. 말을 잘하는 모델에서, 일을 처리하는 모델로 초점이 옮겨가고 있습니다.

## 250B인데 15B처럼 계산한다

Solar Open 2는 sparse **Mixture-of-Experts(MoE)** Transformer입니다. 전체 파라미터는 약 **250B**지만, 매 토큰에서 실제 계산에 참여하는 파라미터는 **15B**입니다. 48개 layer, hidden size 4096, vocab size 196,608이고, MoE 쪽에는 320개의 routed expert 중 매 토큰마다 top-8이 선택되고 shared expert 1개가 항상 붙습니다.

A15B가 "모델이 15B만큼만 가볍다"는 뜻은 아닙니다. 전체 250B weight는 여전히 서빙해야 합니다. 다만 토큰 하나를 처리할 때 일부 expert만 켜지니까 계산량이 15B 수준으로 내려옵니다.

에이전트에서는 이게 중요합니다. 일반 챗봇은 질문 하나에 답하고 끝나지만, 업무 에이전트는 파일을 읽고, 도구를 호출하고, 결과를 확인하고, 다시 수정하는 과정을 여러 번 반복합니다. 토큰당 비용과 지연 시간이 그대로 사용성으로 이어집니다.

![Upstage가 공개한 Solar Open 2 핵심 요약. 모델카드는 agentic specialist, minimal inference cost, 1M-token context, selective weight transfer, multilingual support를 전면에 둔다.](/images/solar-open2-agentic-open-weight-2026-07-22/highlights-kr.png)

## 1M context는 긴 글이 아니라 작업 기록 문제다

Solar Open 2는 **1,048,576 tokens**, 즉 1M context를 지원합니다. 에이전트 관점에서 이건 단순히 "긴 문서를 넣을 수 있다"가 아니라, 앞에서 어떤 파일을 읽었고, 어떤 도구 호출이 실패했고, 어떤 가정을 바꿨는지를 긴 작업 동안 잃지 않는다는 뜻입니다.

비용 문제를 줄이기 위해 **hybrid attention**을 씁니다. 48개 layer 중 12개는 softmax attention, 36개는 linear attention이고, 패턴은 `[Softmax, Linear, Linear, Linear] × 12`입니다. Softmax attention은 정확하지만 길어질수록 비싸고, linear attention은 긴 sequence를 싸게 처리하지만 정확도에서 약간 희생이 있습니다. 둘을 섞어서 정확도가 필요한 층은 남기고 나머지는 비용을 낮추는 방향입니다.

![테크니컬 리포트의 아키텍처 페이지. Solar Open 2는 48층에서 softmax attention 1층 뒤 linear attention 3층을 반복하고, positional encoding을 제거한 NoPE 구조를 쓴다.](/images/solar-open2-agentic-open-weight-2026-07-22/architecture-page.png)

위치 인코딩은 **NoPE**를 씁니다. Positional Encoding을 넣지 않는다는 뜻입니다. 일반 Transformer는 RoPE로 토큰 위치 정보를 넣지만, 이 방식은 학습 때 본 길이를 넘어갈 때 한계가 생길 수 있습니다. Solar Open 2는 명시적 위치 인코딩을 빼고 linear attention의 sequential state가 순서를 들고 가도록 했습니다. 조코딩 라이브에서 이활석 CTO도 모델이 position을 스스로 익히게 하는 방향이라고 설명했습니다.

기술 리포트에는 negative eigenvalue extension도 나옵니다. 기존 KDA 계열 linear attention state가 정보를 유지하거나 감소시키는 쪽이었다면, Solar Open 2는 eigenvalue 범위를 `[-1, 1]`로 넓혀 state가 sign flip을 할 수 있게 했습니다. 긴 문맥에서 잘못 누적된 정보를 상쇄하거나 수정할 여지를 주는 설계입니다.

다만 1M context를 지원한다는 것과 1M 전체에서 항상 같은 정확도가 나온다는 것은 다릅니다. 독립 검증은 아직 더 필요합니다.

## 이전 모델에서 2.3%만 가져왔다

Solar Open 2는 Solar Open 1을 단순히 더 키운 모델은 아닙니다. attention 구조가 바뀌었고 positional encoding도 빠졌습니다. 아키텍처가 달라져서 기존 weight를 그대로 옮길 수 없습니다.

Upstage는 **selective weight transfer**를 써서, Solar Open 1에서 shape과 의미가 맞는 부분만 옮겼습니다. token embedding/output layer, normalization layer, 일부 attention projection, shared expert가 해당합니다. 옮긴 파라미터는 **5.69B**, 전체의 약 **2.3%**입니다. 나머지는 새로 학습했습니다.

2.3%는 작아 보이지만 학습 초기 안정화에는 의미가 있었습니다. 리포트의 200B-A15B proxy 실험에서 selective transfer를 쓴 모델은 training cross-entropy 1.8에 12.6B tokens 만에 도달했고, random initialization은 21.5B tokens가 필요했습니다. 최종 성능이 아니라 초기 학습 곡선을 본 실험입니다.

데이터는 처음 정제한 20T token pool을 quality와 rarity 기준으로 10T mixture로 줄였습니다. real:synthetic = 4:6, math와 code는 각각 15% 이상, English share는 80% 이상입니다. 이후 10T general pre-training, 1T intensive pre-training, 약 0.9T length expansion으로 총 약 12T입니다. 한국어 특화 모델이라도 영어 기반 reasoning/code/math를 먼저 확보하고, 한국어 tokenizer와 post-training으로 한국어 업무 환경을 맞추는 구조입니다.

## 성능표에서 제일 볼 부분은 오피스 업무다

일반 벤치마크도 높습니다. MMLU-Pro 86.2, GPQA-Diamond 86.3, LiveCodeBench v6 92.4, AIME2026 95.7이고, agent benchmark에서는 SWE-Bench Verified 70.4, APEX-Agents 16.6, MCP-Atlas 58.2, GDPval-AA v2 ELO 1128입니다.

제일 눈에 띄는 건 역시 Ko-GDPval입니다. 11개 산업 domain, 58개 직업, 170개 한국어 task로 구성된 Upstage의 in-house benchmark로, 변호사·회계사·감염관리 전문가 같은 직무의 실제 업무 산출물을 평가합니다. Solar Open 2가 **86.8점**, DeepSeek-V4-Pro 1.6T가 86.9점, Solar Open 1은 3.4점이었습니다.

자체 평가라는 점은 분명히 해야 합니다. 독립 검증이 더 쌓이기 전까지 "DeepSeek를 이겼다"나 "완전히 동급이다"라고 단정하긴 이릅니다. 다만 자체 평가 기준으로는 한국어 문서와 업무 산출물을 만드는 능력이 프런티어급 오픈 모델과 비교 가능한 수준까지 올라왔습니다.

한국어 benchmark 평균은 85.4입니다. KMMLU-Pro 78.4, CLIcK 90.7, Ko-AIME'25 97.7, KBank-MMLU 80.8, KBL 75.5, KorMedMCQA 93.0이 나옵니다. Ko-AIME, KBank-MMLU, Ko-GDPval은 in-house benchmark라는 점도 같이 봐야 합니다.

## OfficeVerse와 post-training

이 결과가 단순히 모델 크기에서만 나온 건 아닌 것 같습니다. 리포트를 보면 post-training 비중이 큽니다.

Post-training은 SFT, multi-domain RL, 12개 domain specialist, **MOPD(Multi-teacher On-policy Distillation)**로 이어집니다. specialist는 reasoning(math, STEM, code), agents & tools(coding, general tool use, single/multi-workspace, search), preference & alignment(instruction following, human preference, safety, abstention)로 나뉩니다.

MOPD는 teacher가 만든 정답 trace만 베끼는 게 아니라, student가 직접 rollout한 trajectory 위에서 specialist teacher의 full-vocabulary distribution을 따라가게 합니다. 실제 에이전트는 늘 정답 경로만 걷지 않습니다. 도구 호출이 실패하고, 중간 가정이 틀리고, 파일을 다시 읽어야 합니다. 그런 상황에서 배워야 하니까 on-policy 방식이 중요해집니다.

![테크니컬 리포트의 post-training 개요. SFT와 multi-domain RL 이후 12개 specialist teacher를 만들고, MOPD로 하나의 deployable model에 통합한다.](/images/solar-open2-agentic-open-weight-2026-07-22/posttraining-page.png)

오피스 업무 쪽에서는 **OfficeVerse**가 중요합니다. 문서, 스프레드시트, 프레젠테이션 같은 업무 산출물을 만들고 검증하는 환경입니다. 모델이 답변 문장만 잘 쓰는 게 아니라, 실제 파일과 결과물을 만들고 그게 맞는지 확인하는 쪽으로 학습 환경을 만들었습니다.

한국어를 잘 말하는 것과 한국 회사의 업무 문서를 처리하는 것은 다른 문제입니다. 법률, 금융, 공공, 의료에서는 문서 양식, 숫자, 내부 용어, 보안 제약까지 같이 들어옵니다. 외부 API에 보내기 어려운 데이터도 많습니다. 그래서 Solar Open 2는 온프레미스와 오픈웨이트를 같이 이야기합니다.

## 온프레미스와 양자화

Solar Open 2는 오픈웨이트 모델입니다. 라이선스는 **Upstage Solar License**로, commercially usable이라고 하지만 실제 제품에 넣으려면 조건을 따로 확인해야 합니다.

서빙 비용은 현실적으로 봐야 합니다. BF16 원본은 H200 4장 minimum, 8장 recommended입니다. quantization을 쓰면 H200 2장에서도 구동 가능하다고 하지만, 개인 노트북에서 돌릴 모델은 아닙니다.

Nota AI가 공개한 [Solar-Open2-250B-Nota-INT4-GlobalPruned](https://huggingface.co/nota-ai/Solar-Open2-250B-Nota-INT4-GlobalPruned)는 W4A16 INT4 양자화와 global expert pruning을 적용해서 weight footprint를 **117.8GB**까지 줄였습니다. 2×H100, `--max-model-len 131072` 조건의 예시가 제시됩니다. vLLM patch가 필요하고 context를 길게 잡으면 KV cache 문제가 다시 생기지만, 회사나 연구실 GPU 서버에서 직접 서빙해볼 수 있는 선으로는 내려왔습니다.

## 약한 부분도 분명하다

모든 영역에서 앞서는 건 아닙니다. repository-level, terminal-level software engineering에서는 MiMo-V2.5와 DeepSeek-V4-Flash가 앞섭니다. SWE-Bench Verified는 Solar Open 2가 70.4, MiMo-V2.5가 73.0, DeepSeek-V4-Flash가 73.8입니다. Terminal Bench Hard는 Solar Open 2가 28.3, MiMo-V2.5가 41.7입니다.

Upstage도 conclusion에서 repository/terminal-level software engineering과 officework deliverable의 fine-grained numerical precision을 남은 과제로 적고 있습니다. 둘 다 verifier와 self-checking이 더 강해져야 하는 영역입니다.

그리고 Ko-GDPval과 일부 한국어 benchmark는 자체 평가입니다. 1M context도 받을 수 있는 길이와 그 길이에서 안정적으로 업무를 끝내는 능력을 구분해서 봐야 합니다.

## 한국 모델의 질문이 바뀌었다

Solar Open 2를 보면 한국 모델에 대한 질문이 조금 바뀌었다는 걸 느낍니다. 예전에는 "한국어도 자연스럽게 하나?"가 먼저였고, 이제는 "한국어 문서와 업무 산출물을 만들 수 있나?"로 이동하고 있습니다.

Upstage가 제시한 성적표만 놓고 보면, Solar Open 2는 오피스 업무 벤치마크에서 DeepSeek-V4-Pro 수준에 매우 가까운 결과를 냈습니다. 이게 독립 검증까지 거쳐 유지된다면 의미가 큽니다. 한국어 모델이 단순 대화용이 아니라 내부망에서 문서와 도구를 다루는 업무 모델로 쓸 수 있다는 가능성이 커지는 겁니다.

과제도 분명합니다. 라이선스, serving 비용, 독립 검증, 긴 문맥 안정성, 숫자 정확도, terminal-level agent 능력은 더 봐야 합니다. 그래도 방향은 분명합니다. 한국 모델도 이제 말만 하는 모델에서, 문서를 만들고 일을 처리하는 모델 쪽으로 오고 있습니다.

---

### 참고 자료

- Upstage Hugging Face Model Card: [upstage/Solar-Open2-250B](https://huggingface.co/upstage/Solar-Open2-250B)
- Upstage Blog: [Korea's Sovereign Foundation Model, Built for Agentic Use](https://www.upstage.ai/blog/en/solar-open-2)
- Technical Report: [Solar Open 2 Technical Report](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/Solar_Open_2_Tech_Report.pdf)
- Nota AI Quantized Model: [Solar-Open2-250B-Nota-INT4-GlobalPruned](https://huggingface.co/nota-ai/Solar-Open2-250B-Nota-INT4-GlobalPruned)
- 조코딩 라이브: [Solar Open Weight Day](https://www.youtube.com/live/6XX-yR3qomM) — 특히 6:23 이후 이활석 CTO 기술 설명
- Upstage On-premises: [Private AI, on your terms](https://www.upstage.ai/pricing/on-premises)

에이전트와 자동화 워크플로우를 직접 실습해보고 싶은 분들은 제가 정리한 오픈클로 책과 루프 엔지니어링 강의도 참고하셔도 좋습니다. 책은 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902), 강의는 [AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)입니다. 모델을 "답변기"가 아니라 실제 작업 루프 안에 넣어보는 쪽에 초점을 둡니다.
