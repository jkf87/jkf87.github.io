---
title: "Solar Open 2를 쉽게 읽기: 국산 AI가 ‘현장 모델’로 바뀌는 순간"
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
description: "Upstage Solar Open 2 250B-A15B를 쉽게 풀어 읽었다. 핵심은 한국어 성능 하나가 아니라, 긴 문맥·도구 사용·오피스 산출물·온프레미스 서빙까지 이어지는 현장형 agent model recipe다."
aliases:
  - /posts/solar-open2-agentic-open-weight-2026-07-22
---

![Solar Open 2를 에이전트용 command center로 재구성한 이미지. 250B MoE 모델이 여러 전문가 모듈, 긴 컨텍스트 타임라인, 문서·코드·도구 호출 흐름을 하나로 묶는다는 점을 시각화했다.](/images/solar-open2-agentic-open-weight-2026-07-22/hero.jpg)

국산 AI 모델 이야기에서 오래 반복된 질문이 있다. “그래서 ChatGPT보다 좋아요?” 저는 이 질문이 이제 조금 낡았다고 봅니다.

Upstage가 공개한 **Solar Open 2**는 그 질문에 정면으로 답하려는 모델이 아니다. 더 중요한 질문을 던진다. **한국어로 된 실제 업무를, 외부 API에 보내지 않고, 우리 조직 안에서 돌릴 수 있는가?** 법률 문서, 엑셀, 보고서, 프레젠테이션, 내부 지식, 도구 호출이 얽힌 일을 모델이 끝까지 처리할 수 있는가?

이 관점으로 보면 Solar Open 2의 핵심은 “250B짜리 한국어 모델”이 아니다. **현장에서 굴릴 수 있는 agent model**을 만들겠다는 선언에 가깝다.

이 배경에는 정부의 **독자 AI 파운데이션 모델**, 줄여서 독파모 사업도 있다. 최근 흐름을 보면 1차 경쟁이 “언어 모델을 제대로 만들 수 있느냐”였다면, 2차 경쟁은 “그 모델이 실제 업무를 끝낼 수 있느냐”로 옮겨가고 있다. 외부 검색, 데이터베이스, 코드 실행, 문서 생성 같은 도구 호출 능력이 핵심 평가축으로 올라온 것이다. Solar Open 2는 이 판에서 Upstage가 내놓은 답안지다.

공식 모델카드, Upstage 블로그, 34쪽짜리 [Solar Open 2 Technical Report](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/Solar_Open_2_Tech_Report.pdf), 조코딩 채널의 [Solar Open Weight Day 라이브](https://www.youtube.com/live/6XX-yR3qomM), Nota AI의 [INT4 global-pruned 모델카드](https://huggingface.co/nota-ai/Solar-Open2-250B-Nota-INT4-GlobalPruned), 그리고 독파모 2차 평가 관련 보도를 함께 읽으면 그림이 더 또렷해진다. Solar Open 2는 벤치마크 숫자 하나로 설명되는 모델이 아니다. 아키텍처, 학습 데이터, 강화학습 환경, 양자화 버전까지 모두 **“기업·기관 안에서 돌아가는 한국어 업무 에이전트”** 쪽으로 맞물려 있다.

## 이 모델은 챗봇보다 ‘직원’ 쪽을 보고 있다

Solar Open 2는 sparse **Mixture-of-Experts(MoE)** Transformer다. 전체 파라미터는 약 **250B**다. 그런데 매 토큰에서 실제로 활성화되는 파라미터는 **15B**다. 그래서 표기가 **250B-A15B**다.

숫자만 보면 헷갈릴 수 있다. 250B면 매우 큰 모델인데, A15B면 상대적으로 작은 모델처럼 돈다. MoE는 여기서 중요해진다. 모든 전문가를 매번 다 부르는 것이 아니라, 토큰마다 필요한 expert 일부만 켠다. Solar Open 2는 320개의 routed expert 중 top-8과 shared expert 1개를 사용한다. 전체 지식 저장고는 크게 두되, 실제 계산은 선택적으로 한다.

왜 이렇게 만들었을까. 에이전트는 일반 채팅보다 훨씬 많은 토큰을 쓴다. 질문에 답하고 끝나는 것이 아니라, 계획을 세우고, 파일을 읽고, 도구를 호출하고, 결과를 확인하고, 다시 수정한다. 코딩 에이전트라면 repo를 열고 테스트를 돌린다. 오피스 에이전트라면 xlsx, docx, pptx, pdf 같은 산출물을 만들어야 한다. 한 번의 답변이 아니라 하나의 작업 루프다.

이때 비용은 제품의 기능이 된다. 모델이 한 번 답하고 끝나는 서비스라면 조금 비싸도 버틸 수 있다. 하지만 에이전트가 수십 번 호출되며 일을 끝내는 구조라면, 토큰당 비용과 지연 시간이 곧 사용성이다. 그래서 Solar Open 2의 설계 목표는 “제일 큰 모델”이 아니다. **큰 모델의 능력을 가져오되, 실제 조직이 감당할 수 있는 비용 구조로 낮추는 것**이다. 이게 250B보다 A15B가 중요한 이유다.

![Upstage가 공개한 Solar Open 2 핵심 요약. 모델카드는 agentic specialist, minimal inference cost, 1M-token context, selective weight transfer, multilingual support를 전면에 둔다.](/images/solar-open2-agentic-open-weight-2026-07-22/highlights-kr.png)

## 100만 토큰은 ‘긴 글 읽기’가 아니라 작업 기억 문제다

Solar Open 2는 **1,048,576 tokens**, 즉 1M context를 내세운다. 여기서 흔한 해석은 “책 몇 권을 한 번에 넣을 수 있겠네”다. 맞는 말이지만 충분하지 않다.

에이전트 관점에서 긴 context는 문서 길이 문제가 아니라 **작업 기억** 문제다. 모델이 앞에서 어떤 파일을 읽었는지, 어떤 도구를 불렀는지, 어떤 가정을 했는지, 어디서 실패했는지 기억해야 한다. 긴 업무에서는 초반의 작은 오류가 뒤쪽 전체 작업을 망칠 수 있다. 문서 몇 개를 넣는 것보다, 작업의 흔적을 오래 붙잡는 능력이 더 중요하다.

문제는 비용이다. 일반적인 softmax attention은 문맥이 길어질수록 KV cache와 연산 부담이 커진다. Solar Open 2는 그래서 **hybrid attention**을 쓴다. 48 layers 중 12개는 softmax attention, 36개는 linear attention이다. 패턴은 `[Softmax, Linear, Linear, Linear] × 12`다.

Softmax attention은 정확한 recall에 강하다. 대신 길어질수록 비싸다. Linear attention은 긴 sequence를 더 싸게 처리한다. 대신 모든 것을 softmax처럼 정확히 기억한다고 말하기는 어렵다. Solar Open 2는 둘 중 하나를 고르지 않고 섞었다. 정확한 global recall이 필요한 층은 남기고, 나머지는 긴 문맥을 싸게 버티는 구조로 간다.

이활석 CTO는 라이브에서 이 선택을 더 직설적으로 설명했다. Solar Open 1은 all-softmax attention이었다. Solar Open 2는 softmax attention과 linear attention을 섞었다. 이 조합으로 같은 규모의 all-softmax stack 대비 메모리와 computation을 대략 **1/4 수준**까지 줄이는 것이 목표다. 1M context는 “그냥 길게 받는다”가 아니라, 긴 작업을 버틸 비용 구조를 같이 만든 결과다.

![테크니컬 리포트의 아키텍처 페이지. Solar Open 2는 48층에서 softmax attention 1층 뒤 linear attention 3층을 반복하고, positional encoding을 제거한 NoPE 구조를 쓴다.](/images/solar-open2-agentic-open-weight-2026-07-22/architecture-page.png)

## RoPE를 빼고, 모델에게 순서를 배우게 했다

Solar Open 2에서 또 하나 과감한 선택은 **NoPE**다. Positional Encoding을 쓰지 않는다는 뜻이다. 일반적인 Transformer는 RoPE 같은 방식으로 token 위치 정보를 넣는다. 그런데 이 방식은 학습 때 본 길이 분포에 묶이기 쉽다. 짧은 context에서 배운 위치 감각을 아주 긴 context로 늘릴 때 문제가 생긴다.

Solar Open 2는 softmax layer에 명시적 position signal을 넣지 않는다. 대신 token order와 long-range information을 linear attention의 sequential state가 들고 가게 한다. 이활석 CTO는 라이브에서 “모델 스스로가 positioning을 익히게끔” 만들었다고 설명했다. 사람이 위치 정보를 박아 넣기보다, 긴 sequence를 처리하는 state 안에서 순서를 익히게 한 셈이다.

여기에 **negative eigenvalue extension**도 들어간다. 말은 어렵지만 직관은 단순하다. 긴 작업에서는 모델의 내부 state에 잘못된 정보가 들어갈 수 있다. Linear-heavy 구조라면 그 정보가 계속 누적될 위험이 있다. 그래서 state가 단순히 기억만 하는 것이 아니라, 잘못 쓴 것을 지우고 뒤집을 수 있어야 한다.

CTO 설명에서 이 대목이 좋았다. 그는 negative eigenvalue를 둔 이유를 “이전에 쓴 것을 지우거나, 원래는 안 됐던 상황까지 학습되게 만들고 싶었다”는 취지로 설명했다. 긴 context를 거대한 창고로만 보지 않은 것이다. **오래 기억하되, 틀린 기억은 고칠 수 있어야 한다.** 에이전트에게 필요한 기억은 저장소가 아니라 작업 상태다.

물론 1M context가 만능이라는 뜻은 아니다. 라이브에서도 실제 성능과 GPU 비용은 별도 문제라고 선을 그었다. 1M을 물리적으로 받을 수 있는 것과, 1M에서 항상 같은 정확도를 유지하는 것은 다르다. Solar Open 2의 중요한 점은 그 어려움을 숨기지 않고, 아키텍처 차원에서 비용과 기억의 균형을 잡으려 했다는 데 있다.

## 이전 모델을 2.3%만 가져왔는데, 그 2.3%가 중요했다

Solar Open 2는 Solar Open 1의 후속이다. 하지만 Solar Open 1을 그대로 키운 모델은 아니다. attention 구조가 바뀌었고, RoPE도 빠졌다. 아키텍처가 달라졌으니 기존 weight를 통째로 옮길 수 없다.

Upstage는 여기서 **selective weight transfer**를 썼다. Solar Open 1에서 Solar Open 2로 옮긴 파라미터는 **5.69B**, 전체 250B의 약 **2.3%**다. token embedding/output layer, normalization layer, 일부 attention projection, shared expert처럼 shape과 의미가 맞는 부분만 전이했다. 나머지 대부분, 특히 320 routed experts는 random initialization이다.

2.3%면 별것 아닌 것처럼 보인다. 그런데 대형 모델 학습에서는 초기 몇 퍼센트가 돈과 시간을 크게 바꾼다. 리포트의 200B-A15B proxy 실험에서 transfer를 쓴 모델은 training cross-entropy 1.8에 도달하는 데 12.6B tokens가 필요했다. random initialization은 21.5B tokens가 필요했다. 약 1.7배 차이다.

라이브 설명도 현실적이었다. Solar Open 1 결과를 “그냥 다 버리는 게 아니라” 최대한 활용하고 싶었지만, 구조가 바뀌어 direct mapping은 어려웠다. 그래서 이식 가능한 weight와 remapping 가능한 weight를 실험으로 찾아냈고, 결과적으로 약 5.7B만 가져왔다. 모델 재사용은 단순히 “이전 모델을 더 학습시킨다”가 아니다. **아키텍처가 바뀐 상태에서 무엇을 옮길 수 있는지 찾는 engineering problem**이다.

데이터 쪽도 비슷하다. Upstage는 처음 정제한 20T token pool을 quality와 rarity 기준으로 10T mixture로 줄였다. real-to-synthetic 비율은 4:6, math와 code는 각각 최소 15%, English share는 80% 이상이다. 이후 10T general pre-training, 1T intensive pre-training, 약 0.9T length expansion으로 이어진다. 총 pre-training token은 약 12T다.

여기서도 trade-off가 나온다. 1M context 데이터를 넣으면 긴 문맥 능력은 올라가지만, 짧은 context 성능은 흔들릴 수 있다. Upstage는 length expansion 이후 네 개 중간 checkpoint를 merge해 최종 pre-trained model을 만들었다. 1M context는 단순 확장이 아니라, 기존 능력과 긴 문맥 능력 사이의 균형을 다시 맞추는 작업이었다.

## Solar Open 2의 진짜 무대는 한국어 오피스 업무다

Solar Open 2가 가장 강하게 주장하는 영역은 한국어다. 그런데 단순한 한국어 질의응답이 아니다. 핵심은 **Korean officework agent**다.

리포트에는 **Ko-GDPval**이라는 in-house benchmark가 나온다. GDPval의 “economically valuable real-world work” 패러다임을 한국 산업, 법, 업무 관행에 맞춘 벤치마크라고 설명한다. 11개 산업 domain, 58개 직업, 170개 한국어 task로 구성되어 있다. 변호사, CPA, 감염관리 전문가, project-finance underwriter 같은 직무의 실제 deliverable 중심 작업을 다룬다.

Solar Open 2의 Ko-GDPval 점수는 **86.8**이다. DeepSeek-V4-Pro 1.6T가 86.9다. 사실상 붙었다. DeepSeek-V4-Flash 85.0, MiMo-V2.5-Pro 84.6보다 높다. Solar Open 1은 3.4였다. 이건 “조금 좋아졌다”가 아니라, 이전 세대에서는 사실상 못 하던 deliverable-producing officework가 이번 세대에서 생겼다는 주장에 가깝다.

한국어 benchmark 평균도 Solar Open 2가 85.4로 비교 모델 중 가장 높다. KMMLU-Pro 78.4, CLIcK 90.7, Ko-AIME’25 97.7, KBank-MMLU 80.8, KBL 75.5, KorMedMCQA 93.0 같은 숫자가 나온다. 다만 Ko-AIME, KBank-MMLU, Ko-GDPval은 in-house benchmark다. 독립 검증이 더 쌓여야 한다. 이 점은 분명히 봐야 한다.

그럼에도 방향은 중요하다. Upstage는 한국어를 “번역된 언어”로 보지 않는다. **업무가 실제로 벌어지는 환경**으로 본다. 한국 회사의 문서 양식, 엑셀, 프레젠테이션, 법률·금융 표현, HWP 같은 포맷, 내부망 제약까지 들어와야 한국어 업무 모델이 된다.

이 지점에서 온프레미스가 중요해진다. 행정, 법률, 금융, 의료, 공공 업무는 데이터가 조직 밖으로 나가기 어렵다. 외부 API가 편해도 사건 기록, 계약서, 고객 정보, 내부 의사결정 문서를 그대로 보낼 수 없다. Upstage의 on-premises 안내도 같은 문제를 정면으로 말한다. 데이터와 인프라, compliance를 조직 안에서 통제하는 것이 enterprise AI의 핵심이라는 것이다. Solar Open 2가 “현장 모델”로 읽히는 이유도 여기에 있다.

이활석 CTO 설명에서도 이 대목이 분명했다. 그는 RL에서 가장 큰 관문으로 **verifiable한 데이터를 다양하고 대량으로 뽑아내는 데이터 생성 파이프라인**을 꼽았다. 코딩 agent라면 코드를 고치고 테스트로 검증하는 환경이 필요하다. officework agent라면 문서나 스프레드시트, 발표자료가 제대로 만들어졌는지 확인하는 verifier가 필요하다. 그래서 GPU만 있으면 되는 일이 아니다. CPU, 실행 환경, verifier, 데이터 공장까지 함께 필요하다.

특히 officework 쪽은 **OfficeVerse**라는 내부 파이프라인과 이어진다. 문서 업무 타입을 늘리고, HWP 같은 한국 업무 포맷까지 추가하는 식으로 환경을 고도화하고 있다는 언급도 있었다. 이 지점이 한국어 LLM의 진짜 난이도다. 한국어를 자연스럽게 말하는 것과 한국 회사의 파일·숫자·보고 체계를 맞추는 것은 다른 문제다.

## 12명의 specialist를 하나의 모델에 합쳤다

Solar Open 2의 post-training은 네 단계다. SFT, multi-domain RL, specialist, 그리고 **MOPD(Multi-teacher On-policy Distillation)**다.

처음 두 단계는 generalist base를 만든다. 그 다음 Upstage는 12개 domain specialist를 따로 키웠다. reasoning 계열(math, STEM, code), agents & tools 계열(coding, general tool use, single-workspace, multi-workspace, search), preference & alignment 계열(instruction following, human preference, safety, abstention)로 나뉜다.

여기서 어려운 점은 specialist를 따로 잘 키우는 것과 하나의 deployable model로 합치는 것이 다르다는 데 있다. teacher가 만든 정답 trace만 SFT하면 student가 자기 실수로 흘러간 상황에서 어떻게 복구해야 하는지 배우기 어렵다. 실제 에이전트는 늘 깨끗한 정답 경로만 걷지 않는다. 도구 호출이 실패하고, 파일을 잘못 읽고, 중간 가정이 틀릴 수 있다.

그래서 MOPD는 student가 직접 rollout한 trajectory 위에서, 해당 prompt에 routing된 specialist teacher의 full-vocabulary distribution을 따라가게 한다. 쉽게 말하면, **학생이 자기가 실제로 헤매는 길 위에서 선생님의 다음 선택 분포를 배운다.**

![테크니컬 리포트의 post-training 개요. SFT와 multi-domain RL 이후 12개 specialist teacher를 만들고, MOPD로 하나의 deployable model에 통합한다.](/images/solar-open2-agentic-open-weight-2026-07-22/posttraining-page.png)

Fully asynchronous RL도 같은 맥락이다. Agent rollout은 길이가 들쭉날쭉하다. 동기식으로 처리하면 가장 느린 rollout을 기다리느라 GPU가 놀게 된다. 라이브에서 이활석 CTO는 처음 synchronously 학습을 돌렸을 때 GPU utilization이 약 20% 수준이었다고 말했다. 나머지 80%가 노는 구조라면 대규모 RL에서는 답이 없다.

그래서 actor와 trainer를 분리하고, stale token을 관리하고, 긴 trajectory를 버리지 않고 salvage하는 방식이 필요해진다. Solar Open 2의 post-training은 알고리즘 하나로 끝나는 일이 아니다. GPU, CPU, 가상환경, verifier, batching을 함께 맞춘 시스템 작업이다. 이 대목은 모델 논문보다 agent harness 운영 보고서처럼 읽힌다.

## 양자화 버전이 나오면서 ‘우리 조직 안에서 돌린다’가 가까워졌다

처음 Solar Open 2만 보면 여전히 부담스럽다. Hugging Face 모델카드는 quickstart 기준 H200 4장을 minimum, H200 8장을 recommended로 적는다. Upstage 블로그는 quantization 사용 시 H200 2장에서도 구동 가능하다고 설명한다. 그래도 개인이 집에서 돌리는 모델은 아니다.

그런데 Nota AI가 공개한 [Solar-Open2-250B-Nota-INT4-GlobalPruned](https://huggingface.co/nota-ai/Solar-Open2-250B-Nota-INT4-GlobalPruned)가 이 그림을 바꾼다. 이 모델은 Solar Open 2를 **W4A16 weight-only INT4**로 양자화하고, MoE expert를 전역 중요도 기준으로 pruning한 버전이다.

여기서 중요한 건 pruning 방식이다. 모든 layer에서 expert를 똑같이 자르는 uniform pruning이 아니다. Nota AI는 네트워크 전체에서 expert 중요도를 추정하고, layer마다 필요한 expert 수를 다르게 남긴다. 즉 덜 중요한 expert를 기계적으로 자르는 것이 아니라, 전체 모델 안에서 중요한 expert를 더 보존한다.

결과 숫자가 꽤 크다. Nota 모델카드 기준 weight footprint는 **117.8GB**까지 줄었다. unpruned INT4 모델은 2장에 올리기 어려워 4×H100으로 넘어가야 하지만, global-pruned 모델은 **2×H100**에 올라간다. 예시 서빙 명령도 vLLM 기준 `--tensor-parallel-size 2`, `--max-model-len 131072`로 제시되어 있다.

물론 조건은 있다. upstream vLLM이 per-layer variable expert count를 아직 직접 지원하지 않기 때문에 repository의 `patch/solar_open2.py`를 vLLM 모델 정의에 덮어써야 한다. 1M context 전체를 항상 2장으로 여유 있게 돌린다는 뜻도 아니다. 예시는 131K context다. context를 더 길게 잡으면 KV cache와 throughput 문제가 다시 따라온다.

그래도 의미는 분명하다. 모델카드는 세 개 고난도 reasoning benchmark 평균에서 unpruned INT4가 83.99, Nota global-pruned INT4가 **83.39**, 같은 비율의 uniform pruning이 78.79라고 적는다. 성능을 크게 잃지 않고 2×H100 서빙선까지 내린 것이다.

정확히 말하면 “아무 PC에서 250B를 돌린다”가 아니다. 하지만 **회사·학교·랩의 in-house GPU 서버에서 한국어 agent model을 직접 서빙해볼 수 있는 선**까지 내려왔다. 이게 오픈웨이트의 현실적인 의미다. API로만 쓰는 모델이 아니라, 조직 안의 데이터·문서·업무 시스템 곁에 붙일 수 있는 모델이 된다.

이 차이는 작지 않다. API 모델은 빠르게 붙일 수 있지만, 데이터가 밖으로 나가고 모델 업데이트와 정책 변경을 외부에 맡겨야 한다. In-house 모델은 운영이 어렵지만, 내부 문서와 업무 시스템 가까이에 둘 수 있다. 한국어 업무 에이전트에서는 후자가 특히 중요하다. 모델이 똑똑한 것만으로는 부족하고, 조직의 파일, 도구, 권한, 감사 체계 안에 들어와야 하기 때문이다.

## 강한 숫자만 보면 안 된다

영어 쪽 결과도 공격적이다. Solar Open 2는 MMLU-Pro 86.2, GPQA-Diamond 86.3, LiveCodeBench v6 92.4, AIME2026 95.7을 기록했다. Agent benchmark에서는 SWE-Bench Verified 70.4, APEX-Agents 16.6, MCP-Atlas 58.2, GDPval-AA v2 ELO 1128이다.

하지만 빈틈도 있다. repository-level, terminal-level software engineering에서는 MiMo-V2.5와 DeepSeek-V4-Flash가 앞선다. SWE-Bench Verified는 Solar Open 2가 70.4, MiMo-V2.5가 73.0, DeepSeek-V4-Flash가 73.8이다. Terminal Bench Hard는 Solar Open 2가 28.3, MiMo-V2.5가 41.7이다.

이 대목은 오히려 신뢰도를 올린다. “모든 것을 이긴다”가 아니라, 어디서 강하고 어디에 과제가 남았는지 드러난다. Upstage도 conclusion에서 남은 gap을 repository/terminal-level software engineering, officework deliverable의 fine-grained numerical precision으로 적었다. 둘 다 더 강한 verification과 self-checking behavior가 필요한 영역이다.

또 하나는 라이선스다. Solar Open 2는 Hugging Face에 weights가 공개되어 있고, Upstage 블로그는 commercially usable license라고 쓴다. 다만 라이선스 이름은 **Upstage Solar License**다. Apache 2.0 같은 익숙한 permissive license로 단정하면 안 된다. 실제 제품에 넣으려면 [LICENSE](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/LICENSE)를 따로 확인해야 한다.

## 이 모델의 진짜 메시지는 ‘한국어 agent stack’이다

저는 Solar Open 2의 핵심을 모델 하나보다 **recipe**로 봅니다. 한국어 tokenizer 효율을 유지하고, Solar Open 1에서 호환되는 2.3%의 뼈대만 가져오고, 20T pool을 10T high-value mixture로 줄이고, 1M context를 위해 hybrid attention과 NoPE를 택하고, 12개 specialist를 MOPD로 합친다. 여기에 Nota AI의 INT4 global pruning까지 붙으면서 in-house serving 가능성이 더 가까워졌다.

이 흐름은 “큰 모델을 만들었다”보다 구체적이다. 한국어권의 sovereign model이 agent 시대에 무엇을 파야 하는지 보여준다. native-language tokenizer, 실제 업무 데이터, 도구 호출 환경, deliverable 검증, 긴 trajectory 학습, 그리고 온프레미스 서빙. 이 여섯 가지가 함께 가야 한다.

그래서 Solar Open 2는 한국어 LLM 뉴스이면서 동시에 agent engineering 뉴스다. 모델 경쟁은 “대답을 얼마나 잘하나”에서 “일을 얼마나 끝까지, 검증 가능하게 수행하나”로 이동하고 있다. 독파모 2차 평가가 에이전트 활용성과 현장성을 더 강하게 보는 흐름과도 맞물린다. Upstage는 이번 릴리스에서 그 방향을 꽤 노골적으로 선언했다.

저는 이 지점이 제일 반갑다. 한국어 모델이 한국어 문장을 잘 쓰는 수준을 넘어, 한국어로 된 업무 환경에서 파일을 읽고, 숫자를 맞추고, 문서를 만들어내는 쪽으로 가고 있다. 아직 라이선스, serving 비용, 독립 검증이라는 숙제는 남아 있다. 하지만 질문은 바뀌었다. “한국어 모델도 쓸만한가?”가 아니라, **“한국어권 agent stack을 어디까지 우리 손으로 만들 수 있는가?”** 쪽으로.

---

### 참고 자료

- Upstage Hugging Face Model Card: [upstage/Solar-Open2-250B](https://huggingface.co/upstage/Solar-Open2-250B)
- Upstage Blog: [Korea's Sovereign Foundation Model, Built for Agentic Use](https://www.upstage.ai/blog/en/solar-open-2)
- Technical Report: [Solar Open 2 Technical Report](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/Solar_Open_2_Tech_Report.pdf)
- Nota AI Quantized Model: [Solar-Open2-250B-Nota-INT4-GlobalPruned](https://huggingface.co/nota-ai/Solar-Open2-250B-Nota-INT4-GlobalPruned)
- 조코딩 라이브: [Solar Open Weight Day](https://www.youtube.com/live/6XX-yR3qomM) — 특히 6:23 이후 이활석 CTO 기술 설명
- 디지털투데이: [8월 2차 평가 앞둔 독파모 4사, 에이전틱AI로 승부](https://www.digitaltoday.co.kr/news/articleView.html?idxno=677596)
- Upstage On-premises: [Private AI, on your terms](https://www.upstage.ai/pricing/on-premises)

에이전트와 자동화 워크플로우를 직접 실습해보고 싶은 분들은 제가 정리한 오픈클로 책과 루프 엔지니어링 강의도 참고하셔도 좋습니다. 책은 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902), 강의는 [AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)입니다. 모델을 “답변기”가 아니라 실제 작업 루프 안에 넣어보는 쪽에 초점을 둡니다.
