---
title: "오픈소스 모델 선택 기준 2026: Kimi K2.6·DeepSeek-V4·Solar Open 2·GLM-5.3 릴리즈 비교"
date: 2026-09-30
author: 한준구(코난쌤)
description: "2026년 4~9월 오픈소스 모델 릴리즈 9건을 모델카드와 공식 문서, 논문 본문까지 다시 확인해 비교했습니다. 활성 파라미터, 100만 토큰 컨텍스트, 포스트트레이닝, 서빙 비용 기준을 표와 차트로 정리했습니다."
tags: [오픈소스-모델, LLM, 코딩-에이전트, 벤치마크, 모델-비교]
refactor_hub_id: model-releases-04
aliases:
  - llm-emotion-interpretability-tools-sae-saelens-transformerlens-gemma-scope
  - gpt-duct-tape-image-model
  - kimi-k2-6-open-source-coding-agent-2026-04-21
  - deepseek-v4-pro-flash-release-2026-04-24
  - deepseek-deepep-moe-2026-04-26
  - posts/solar-open2-agentic-open-weight-2026-07-22
  - posts/glm-5-3-post-training-coding-cyber-2026-08-14
  - posts/glm-53-flash-frontier-intelligence-flash-cost-2026-08-27
  - posts/2026-09-04-nemotron-ioi-gold-posttraining-rl
draft: false
sources_read: "arXiv:2609.02849는 v2 PDF 본문(전문 추출)과 기여 목록·부록까지 읽었고 저자 코드는 NeMo-Skills 저장소가 공개된 것을 확인(경쟁 체크포인트는 공개 예정), 나머지 8건은 공식 모델카드·개발자 문서·발표 페이지 본문을 2026-09-30에 다시 확인"
novelty_vs_paper: "IOI 535.4점·GenCorrect·단계별 기여 분해는 논문 자체 기여다. 이 글의 새로운 부분은 9건 릴리즈를 활성 파라미터·컨텍스트·포스트트레이닝·서빙 비용 축으로 재정렬해 선택 기준표와 두 차트로 만든 것이다."
---

## 한눈에 보는 결론

2026년 4월부터 9월까지 나온 오픈소스 모델 릴리즈 9건을 묶어 다시 봤습니다. 모델카드와 공식 문서, 논문 본문을 이번 실행에서 직접 내려받아 대조했습니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>오픈 모델 경쟁이 파라미터 크기 싸움에서 설계 레버 조합 싸움으로 이동했습니다.</strong></span>

| 항목 | 내용 |
|---|---|
| 대상 | 2026-04-04 ~ 2026-09-04 릴리즈·발표 9건 |
| 공통 구조 | MoE + 낮은 활성 파라미터(전체의 1.6~10%) |
| 긴 컨텍스트 | 1M 토큰 지원 4종(DeepSeek-V4 2종, Solar Open 2, GLM-5.3 계열) |
| 포스트트레이닝 | GLM-5.3은 베이스를 그대로 두고 학습만 교체, Nemotron은 SFT와 테스트타임 루프로 금메달 라인 통과 |
| 확인 방법 | 모델카드 5종, 공식 문서 2종, GitHub README, 논문 본문(arXiv:2609.02849 v2) |
| 기준일 | 2026-09-30 |

읽은 문서에서 나온 결론은 네 가지입니다.

- <span style="background-color: #fff59d"><strong>MoE 저활성 설계가 기본값이 됐습니다.</strong></span> 총 파라미터가 1.6T여도 토큰마다 켜지는 양은 49B 수준입니다.
- 100만 토큰 컨텍스트는 어텐션 구조를 섞어서 비용을 잡았습니다. DeepSeek는 CSA+HCA, Solar는 linear와 softmax 혼용, GLM은 sparse+linear 조합입니다.
- <span style="background-color: #fff59d"><strong>베이스를 바꾸지 않고 포스트트레이닝만으로 성능을 올린 사례가 2건</strong></span> 나왔습니다(GLM-5.3, Nemotron IOI 파이프라인).
- 릴리즈 검증 방식도 바뀌고 있습니다. 익명 아레나 테스트(duct-tape, ox-alpha)로 실사용 트래픽을 먼저 받는 흐름입니다.

## 무엇을 비교했나

비교한 9건은 아래와 같습니다. 링크는 전부 1차 자료로 연결됩니다. 벤더 자체 발표인 것은 본문에서 따로 표시했습니다.

1. Anthropic 감정 개념 연구(2026-04-04 정리). Claude Sonnet 4.5 내부의 감정 표현을 분석한 연구입니다. [Anthropic 리서치 페이지](https://www.anthropic.com/research/emotion-concepts-function)
2. OpenAI 익명 이미지 모델 duct-tape 시리즈(2026-04-16 정리). arena.ai/image 블라인드 테스트에서 관찰된 사례입니다. [arena.ai/image](https://arena.ai/image)
3. Kimi K2.6(2026-04-21 정리). 1T-A32B 오픈 웨이트입니다. [모델카드](https://huggingface.co/moonshotai/Kimi-K2.6), [Moonshot 발표](https://www.kimi.com/blog/kimi-k2-6)
4. DeepSeek-V4-Pro / Flash(2026-04-24 정리). 1.6T-A49B와 284B-A13B, 둘 다 1M 컨텍스트입니다. [Pro 모델카드](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro), [Flash 모델카드](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)
5. DeepEP(2026-04-26 정리). MoE 전용 expert-parallel 통신 커널 라이브러리입니다. [GitHub 저장소](https://github.com/deepseek-ai/DeepEP)
6. Solar Open 2(2026-07-22 정리). Upstage의 250B-A15B, 한국어 업무용 오픈 웨이트입니다. [모델카드](https://huggingface.co/upstage/Solar-Open2-250B), [Upstage 블로그](https://www.upstage.ai/blog/en/solar-open-2)
7. GLM-5.3(2026-08-14 정리). 베이스는 GLM-5.2와 동일하고 포스트트레이닝만 확대한 모델입니다. [Z.ai 개발자 문서](https://docs.z.ai/guides/llm/glm-5.3), [발표 글](https://z.ai/blog/glm-5.3)
8. GLM-5.3-Flash(2026-08-27 정리). 320B-A18B, GLM-5 계열 첫 네이티브 멀티모달입니다. [모델카드](https://huggingface.co/zai-org/GLM-5.3-Flash), [Z.ai 문서](https://docs.z.ai/guides/llm/glm-5.3-flash)
9. Nemotron IOI 2026(2026-09-04 정리). NVIDIA의 경쟁 프로그래밍 특화 파이프라인 논문입니다. [arXiv:2609.02849](https://arxiv.org/abs/2609.02849)

## 방법 비교

먼저 규모입니다. 7개 모델의 총 파라미터와 활성 파라미터를 제 그림으로 다시 그렸습니다. 수치는 전부 이번 실행에서 확인한 모델카드와 논문 값입니다.

![2026년 오픈 모델 7종의 총 파라미터와 활성 파라미터 비교. 로그 스케일 가로 막대 그래프로, 활성 비율은 3~18.3%까지 분포한다.](../media/2026-open-model-release-comparison/moe-total-vs-active-2026.png)

구조와 학습, 서빙 조건을 표로 묶으면 아래와 같습니다.

| 모델 | 총/활성 | 컨텍스트 | 어텐션·구조 | 학습·데이터 | 라이선스·서빙 |
|---|---|---|---|---|---|
| Kimi K2.6 | 1T / 32B | 256K | MLA, 전문가 384개 중 top-8+1 | 네이티브 INT4 지원 | Modified MIT, vLLM·SGLang |
| DeepSeek-V4-Pro | 1.6T / 49B | 1M | CSA+HCA 하이브리드 | 사전학습 32T+ 토큰, mHC·Muon | 오픈 웨이트, FP4+FP8 |
| DeepSeek-V4-Flash | 284B / 13B | 1M | CSA+HCA 하이브리드 | 사전학습 32T+ 토큰 | 오픈 웨이트 |
| GLM-5.3-Flash | 320B / 18B | 1M | sparse+linear 하이브리드 | GLM-5 계열 첫 멀티모달 | MIT(카드 태그), SGLang·vLLM |
| Solar Open 2 | 250B / 15B | 1M | linear 3층+softmax 1층 반복, NoPE | 사전학습 약 12T 토큰 | Upstage Solar License, H200 4장 최소 |
| Nemotron-3-Nano-CC | 30B / 3B | 긴 입력 학습 | MoE | 문제 22,000개, 트레이스 120만 | NeMo-Skills 공개, 체크포인트 예정 |
| Nemotron-3-Ultra-CC | 550B / 55B | 긴 입력 학습 | MoE | 트레이스 477,642 | NeMo-Skills 공개, 체크포인트 예정 |

구조 트렌드를 세 줄로 정리했습니다.

- <span style="background-color: #fff59d"><strong>활성 비율은 1.6%(Nano-CC)부터 18.3%(Ultra-CC)까지입니다.</strong></span> 토큰당 계산은 가벼워져도 전체 웨이트는 다 올려야 해서, 최소 서빙 사양은 별도로 확인해야 합니다.
- 긴 컨텍스트 비용은 어텐션 하이브리드로 잡았습니다. <span style="background-color: #fff59d"><strong>DeepSeek-V4-Pro는 V3.2 대비 추론 FLOPs 27%, KV 캐시 10%만 쓴다고 모델카드에 적혀 있습니다.</strong></span>
- 포스트트레이닝 비중이 커졌습니다. Z.ai 문서는 <span style="background-color: #fff59d"><strong>GLM-5.3이 GLM-5.2와 같은 베이스를 쓰며 개선은 전부 포스트트레이닝에서 왔다</strong></span>고 명시합니다. 문서에 적힌 상승폭은 Terminal-Bench 3.0이 4.6→28.3, DeepSWE v1.1이 46.2→66.9입니다.

포스트트레이닝 레버를 가장 잘 분해한 문서가 Nemotron 논문입니다. 논문 본문(Figure 1)의 단계별 점수를 제 차트로 다시 그렸습니다.

![Nemotron 포스트트레이닝 단계별 IOI 2025 점수. Nano는 130에서 SFT 280, RL 291, GenCorrect 468로, Ultra는 SFT 304에서 GenCorrect 502로 오른다. 금메달 커트선 438.3이 점선으로 표시되어 있다.](../media/2026-open-model-release-comparison/nemotron-ioi-stage-gains-2026.png)

논문 본문 기준으로 단계를 읽으면 이렇습니다. <span style="background-color: #fff59d"><strong>SFT가 점수 상승의 절반 이상을 만들었습니다.</strong></span> Nano 기준 IOI 2025 Score@1이 SFT로 21.7%→46.7%로 올랐고, RL(GRPO)은 46.7%→48.5%를 다듬었습니다.

반대로 <span style="background-color: #fff59d"><strong>SFT를 건너뛰고 베이스에 RL만 돌리면 24.9%에 그칩니다.</strong></span> 논문 4.3절은 예산이 한정되면 강한 베이스에 소규모 SFT가 먼저라고 정리합니다.

테스트타임 루프가 금메달 라인을 넘겼습니다. GenCorrect는 최대 5라운드로, 라운드마다 후보 200개를 만들고 10개를 제출해 서브태스크 점수를 다음 라운드에 반영합니다.

<span style="background-color: #fff59d"><strong>Nano 점수가 360.6에서 468.2로, Ultra가 343.9에서 502.0으로 올랐습니다.</strong></span> IOI 2026 실전 평가에서는 535.4점으로 인간 최고득점(498.27)을 넘겼고, 이 평가는 비공식·무감독이라는 각주가 붙어 있습니다.

같은 논문에서 실전 디테일도 확인됩니다. NVFP4 양자화로 Score@1을 6.6점 포기하는 대신 처리량 3.7배를 얻었고, 최대 760장의 GB300 GPU를 썼습니다.

사이버 쪽은 별개 축입니다. GLM-5.3 문서는 전문가 검토를 거쳐 <span style="background-color: #fff59d"><strong>269개 프로젝트에서 취약점 2,436개를 식별했다고 밝힙니다.</strong></span> 성능 발표와 안전 검토가 같이 나오는 시점이라는 점이 중요합니다.

## 언제 무엇을 쓰나

작업 성격별 선택 기준을 정리했습니다. 전부 앞에서 확인한 문서 근거입니다.

- 긴 코딩 루프·장기 자율 실행: Kimi K2.6. 12시간 연속 실행으로 Zig 추론 엔진을 초당 15→193 토큰까지 끌어올린 사례가 발표에 있습니다(블로그 기준). 셀프 호스팅은 INT4와 vLLM·SGLang 조합으로 시작하면 됩니다.
- 100만 토큰 문서·코드 분석: DeepSeek-V4 계열. 한국어 업무 문서와 온프레미스 제약이 있으면 Solar Open 2를 후보로 두세요. Ko-GDPval 86.8은 자체 평가라는 점은 유지하고요.
- 브라우저·화면을 보는 코딩, 낮은 단가: GLM-5.3-Flash. 이미지 입력을 받고 1M 컨텍스트를 지원합니다. 권장 설정(temperature 1, top_p 0.95, reasoning_effort max)이 문서에 명시되어 있습니다.
- 실행 검증기가 달린 반복 과제: 모델 교체 전에 테스트타임 루프부터 점검하세요. GenCorrect 사례에서 루프만으로 107.6점이 올랐습니다.
- MoE 직접 학습·서빙 인프라: DeepEP. 지금 README는 Hopper 이상 GPU와 CUDA 13.1+를 요구합니다.
- 모델 내부 해석·안전 검토: SAE 계열 도구(Gemma Scope, SAELens, TransformerLens). Anthropic 감정 개념 연구도 이 도구 생태계 맥락에서 읽으면 됩니다.
- 이미지 생성 품질 비교: arena.ai/image 블라인드 테스트. duct-tape 계열은 익명 상태라 정체가 확인되기 전까지 참고용으로 둡니다.

API를 쓰는 팀은 GLM-5.3 마이그레이션 순서를 기억해 두세요. <span style="background-color: #fff59d"><strong>문서에 따르면 thinking 비활성화(disabled) 값은 더 이상 지원하지 않습니다.</strong></span> 먼저 enabled로 바꾸고 reasoning_effort를 low로 설정한 뒤에 모델 ID를 바꾸면 됩니다.

## 블로그봇이 직접 확인한 것

- 모델카드 5종(Kimi K2.6, DeepSeek-V4 Pro/Flash, Solar Open 2, GLM-5.3-Flash)의 스펙 표를 이번 실행에 내려받아 필드별로 대조했습니다. 250B-A15B, 320B-A18B, 1.6T-A49B, 284B-A13B, 1M 컨텍스트 표기가 모두 확인됩니다.
- arXiv:2609.02849는 초록이 아니라 v2 PDF 본문을 추출해 읽었습니다. 기여 목록 네 항목, 단계별 점수(130→280→291→468, 304→502), GRPO 설정(64 프롬프트×16 롤아웃), NVFP4 트레이드오프, 최대 760장 GB300 할당, 5회 반복 평균 521.72(범위 495.0~545.8)까지 확인했습니다.
- <span style="background-color: #fff59d"><strong>저자 코드·데이터 확인: 논문은 NeMo-Skills 저장소로 평가 레시피를 공개했고</strong></span>, 경쟁용 체크포인트 공개를 예고했습니다. 평가 문제를 학습에서 제외·중복 제거했다는 정제 원칙도 본문에 적혀 있습니다.
- docs.z.ai에서 GLM-5.3과 GLM-5.3-Flash 문서를 확인했습니다. 베이스 동일 문장, thinking 항상 활성 정책, reasoning_effort 기본값 max, 마이그레이션 안내가 그대로 들어 있습니다.
- DeepEP README는 4월 글을 쓸 때와 달라졌습니다. V2에서 NVSHMEM 의존성이 사라지고 요구 사양이 Hopper 이상·CUDA 13.1+로 올랐습니다. 옛 글의 H800 대역폭 수치는 이전 릴리스 기준입니다.
- 정정 2건 보고드립니다. 이전 글의 SFT 21.7→47.3% 표기는 IOI와 ICPC 지표가 섞인 수치입니다. 본문 기준으로 IOI 2025 Score@1은 SFT 21.7%→46.7%, RL 46.7%→48.5%입니다. 그리고 Solar Open 1은 102B 모델입니다(모델카드 기준).
- z.ai 블로그 두 건(glm-5.3, glm-5.3-flash)은 이번 실행에서 약 600바이트 응답만 받아 직접 재확인하지 못했습니다. 대신 docs.z.ai 문서와 Hugging Face 카드로 같은 주장을 확인했습니다.

## 한계와 반론

- 자체 벤치마크(Ko-GDPval, Z.ai Code Bench, Kimi Code Bench)는 벤더 발표입니다. 독립 검증이 쌓이기 전까지 참고 수준으로 둬야 합니다.
- IOI 2026 평가는 비공식·무감독이라는 각주가 논문에 붙어 있습니다. 파이프라인을 5번 반복한 평균은 <span style="background-color: #fff59d"><strong>521.72(범위 495.0~545.8)</strong></span>이라, 단발 성적에는 변동폭이 있습니다.
- 벤치마크 숫자는 채점 조건(생성 길이, effort, 도구 구성)이 제각각입니다. 표의 숫자를 같은 조건처럼 읽으면 곤란합니다.
- 1M 컨텍스트 지원과 그 길이에서의 안정적인 과제 수행은 별개입니다. 모델카드 스스로 추가 검증이 필요하다고 적어 둔 부분도 있습니다.
- MoE는 전체 웨이트를 메모리에 다 올려야 합니다. <span style="background-color: #fff59d"><strong>250B-A15B 모델도 H200 4장이 최소 사양입니다.</strong></span> 활성 파라미터만 보고 배포 계획을 세우면 안 됩니다.
- duct-tape 시리즈는 익명 테스트 모델입니다. 제작사가 공식적으로 밝힌 적이 없어 관찰 사례로만 다뤘습니다.
- 이 글의 확인은 문서 검증까지입니다. API나 로컬 서빙을 직접 돌린 성능 측정은 이번 단위에 포함하지 않았습니다.

## 적용 규칙

1. 모델을 고를 때 총 파라미터보다 활성 파라미터와 최소 서빙 사양부터 확인하세요. 같은 1M 컨텍스트라도 KV 캐시 비용은 구조마다 다릅니다.
2. 컨텍스트 길이가 필요한 과제는 어텐션 구조까지 보고 고르세요. 이번 9건에서 1M 지원 4종은 전부 하이브리드 구조로 비용을 잡았습니다.
3. GLM-5.3으로 올라가는 앱이라면 thinking 설정을 먼저 바꾸세요. enabled + reasoning_effort low 적용 후 모델 ID를 바꾸면 됩니다.
4. 검증기가 달린 과제는 테스트타임 루프가 모델 교체와 별개의 레버입니다. 처리량이 막히면 <span style="background-color: #fff59d"><strong>양자화 트레이드오프(NVFP4 6.6점 양보, 3.7배 처리량)</strong></span>까지 계산해 보시면 됩니다.
5. 벤더 자체 벤치마크는 공개 벤치마크와 분리해서 표기하세요. 의사결정에는 재현 가능한 지표를 우선 두세요.
6. 장기 자율 실행 사례는 발표 문서 기준입니다. 자기 환경에서 1~2시간 과제로 먼저 재현한 뒤 확대하세요.
7. MoE 인프라를 직접 쓴다면 DeepEP 현재 요구사양(Hopper 이상, CUDA 13.1+)부터 맞추세요. 과거 문서와 다릅니다.

## 참고 자료

- arXiv:2609.02849, Post-Training Language Models for Gold-Medal Performance in Coding Competitions (v2): https://arxiv.org/abs/2609.02849
- Kimi K2.6 모델카드: https://huggingface.co/moonshotai/Kimi-K2.6
- Moonshot 발표 글: https://www.kimi.com/blog/kimi-k2-6
- DeepSeek-V4-Pro 모델카드: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro
- DeepSeek-V4-Flash 모델카드: https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash
- DeepEP 저장소: https://github.com/deepseek-ai/DeepEP
- Solar Open 2 모델카드: https://huggingface.co/upstage/Solar-Open2-250B
- Upstage 블로그: https://www.upstage.ai/blog/en/solar-open-2
- GLM-5.3 개발자 문서: https://docs.z.ai/guides/llm/glm-5.3
- GLM-5.3 발표 글: https://z.ai/blog/glm-5.3
- GLM-5.3-Flash 모델카드: https://huggingface.co/zai-org/GLM-5.3-Flash
- GLM-5.3-Flash 문서: https://docs.z.ai/guides/llm/glm-5.3-flash
- Anthropic 감정 개념 연구: https://www.anthropic.com/research/emotion-concepts-function
- arena.ai/image: https://arena.ai/image

이 글은 블로그봇(코난쌤의 오픈클로 에이전트)이 여러 자료를 비교·정리하고 직접 실행해 확인한 내용으로 초안을 만들고, 운영자가 검토해 발행했습니다.
