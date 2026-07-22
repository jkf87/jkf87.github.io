---
title: "Solar Open 2: 한국어 오픈웨이트 모델이 에이전트 시장을 정조준했다"
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
categories:
  - AI
  - Agent
description: "Upstage가 공개한 Solar Open 2 250B-A15B를 모델카드, 공식 블로그, 테크니컬 리포트 기준으로 읽었다. 이 모델의 핵심은 한국어 성능만이 아니라 1M context, hybrid attention, officework agent, MOPD로 이어지는 agentic model recipe다."
aliases:
  - /posts/solar-open2-agentic-open-weight-2026-07-22
---

![Solar Open 2를 에이전트용 command center로 재구성한 이미지. 250B MoE 모델이 여러 전문가 모듈, 긴 컨텍스트 타임라인, 문서·코드·도구 호출 흐름을 하나로 묶는다는 점을 시각화했다.](/images/solar-open2-agentic-open-weight-2026-07-22/hero.jpg)

Upstage가 **Solar Open 2**를 공개했다. 250B 파라미터 모델인데, 매 토큰에서 실제로 켜지는 것은 15B다. 그래서 이름 뒤에 붙은 표기가 **250B-A15B**다.

그런데 이 모델을 “한국어 잘하는 오픈웨이트 LLM” 정도로 읽으면 핵심을 놓친다. Upstage가 이번에 밀고 있는 단어는 chat이 아니라 **agent**다. 긴 문서를 읽고, 도구를 호출하고, 코드를 고치고, 엑셀·문서·프레젠테이션 같은 deliverable을 만들어내는 모델. Solar Open 2는 그 방향으로 설계된 한국어권 sovereign foundation model이다.

공식 모델카드, Upstage 블로그, 그리고 34쪽짜리 [Solar Open 2 Technical Report](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/Solar_Open_2_Tech_Report.pdf)를 같이 읽으면 그림이 꽤 선명해진다. 이 모델의 재미있는 지점은 벤치마크 숫자 하나가 아니다. **아키텍처, 데이터, post-training, agent scenario가 모두 “긴 작업을 끝까지 수행하는 모델” 쪽으로 정렬되어 있다.**

## 왜 250B인데 15B만 켜는가

Solar Open 2는 sparse **Mixture-of-Experts(MoE)** Transformer다. 전체 파라미터는 250,287,794,944개, 대략 250B다. 하지만 토큰 하나를 처리할 때는 320개의 routed expert 중 top-8과 shared expert 1개만 활성화한다. 그래서 active parameter는 15B다.

이 설계의 의도는 명확하다. 에이전트는 단답형 chat보다 훨씬 많은 토큰을 쓴다. 계획하고, 도구를 부르고, 결과를 읽고, 다시 수정하고, 파일을 열고, 검증한다. 모델 호출이 한 번으로 끝나지 않는다. 그러니 기업이 자체 인프라에 올려서 agent를 돌리려면 “큰 모델의 능력”과 “작은 모델에 가까운 추론 비용”을 동시에 노려야 한다.

Upstage 블로그는 quantization 사용 시 H200 2장에서도 구동 가능하다고 설명한다. Hugging Face 모델카드는 quickstart 기준으로 H200 4장을 minimum, H200 8장을 recommended로 적고 있다. 실제 운영 요구량은 context length와 serving 설정에 따라 달라진다. 그래도 메시지는 같다. **250B라는 숫자보다 중요한 것은 A15B라는 비용 구조다.**

![Upstage가 공개한 Solar Open 2 핵심 요약. 모델카드는 agentic specialist, minimal inference cost, 1M-token context, selective weight transfer, multilingual support를 전면에 둔다.](/images/solar-open2-agentic-open-weight-2026-07-22/highlights-kr.png)

## 1M context는 그냥 길이가 아니라 agent memory 문제다

Solar Open 2의 context length는 **1,048,576 tokens**, 즉 1M이다. 여기서 중요한 질문은 “와, 긴 문서 넣을 수 있네”가 아니다. 왜 agent 모델에서 1M context가 필요한가다.

테크니컬 리포트의 출발점은 이렇다. long-horizon agent는 한 번에 답하는 모델이 아니다. 여러 단계의 reasoning과 tool call을 반복한다. 작업 기록이 쌓이고, 파일과 문서가 흩어져 있고, 이전에 무엇을 했는지 기억해야 한다. 중간 한 단계의 오류가 뒤쪽 전체 작업을 망칠 수 있다.

이때 softmax attention만으로 1M context를 감당하면 KV cache와 계산량이 병목이 된다. Solar Open 2는 그래서 hybrid attention stack을 쓴다. 48 layers 중 12개는 softmax attention, 36개는 linear attention이다. 패턴은 `[Softmax, Linear, Linear, Linear] × 12`다.

Linear attention layer는 긴 sequence를 recurrent state에 누적한다. KV cache가 sequence length에 비례해 계속 커지는 softmax attention과 다르게, 긴 작업 기록을 더 싸게 들고 가려는 장치다. softmax layer는 25%만 남겨 exact global recall을 보존한다. 리포트는 이 구조가 같은 규모의 all-softmax stack 대비 대략 **1/4 수준의 memory and computation**으로 1M context를 노린다고 설명한다.

![테크니컬 리포트의 아키텍처 페이지. Solar Open 2는 48층에서 softmax attention 1층 뒤 linear attention 3층을 반복하고, positional encoding을 제거한 NoPE 구조를 쓴다.](/images/solar-open2-agentic-open-weight-2026-07-22/architecture-page.png)

## RoPE를 버리고 NoPE로 간 이유

Solar Open 2에서 꽤 과감한 선택은 **NoPE**, 즉 positional encoding을 아예 쓰지 않는다는 점이다. 일반적인 Transformer에서는 RoPE 같은 positional encoding이 query/key에 위치 정보를 넣는다. 문제는 이 방식이 학습 때 본 길이 분포에 묶이기 쉽다는 것이다. 길이를 바깥으로 extrapolate할 때 한계가 생긴다.

Solar Open 2는 softmax layer에 명시적 position signal을 넣지 않는다. 대신 token order와 long-range information을 linear attention의 sequential state가 들고 가게 한다. 리포트 표현으로는 RoPE extrapolation limit과 softmax position-learning bottleneck을 함께 피하려는 설계다.

여기에 두 가지가 더 붙는다. 하나는 softmax attention 출력에 elementwise sigmoid gate를 넣어 attention sink를 줄이고 long-context extrapolation을 돕는 것. 다른 하나는 KDA(Kimi Delta Attention)에 **negative eigenvalue extension**을 넣는 것이다. 표준 linear attention state는 보통 decay하거나 persist할 수 있지만, sign flip이나 적극적 erase가 어렵다. Solar Open 2는 eigenvalue 범위를 `[-1, 1]`로 넓혀 state가 잘못 쓴 정보를 지우고 뒤집을 수 있게 만든다.

이건 논문적인 디테일처럼 보이지만, agent 관점에서는 꽤 현실적이다. 긴 작업을 하다 보면 초반 state에 잘못 들어간 정보가 계속 누적된다. Linear-heavy 구조에서 state가 “잊고 고치는 능력”을 가져야 한다는 문제의식이다.

## Solar Open 1에서 2.3%만 가져왔다

또 하나 재미있는 부분은 initialization이다. Solar Open 2는 Solar Open 1에서 출발했지만, 전체를 그대로 키운 모델이 아니다. 아키텍처가 크게 바뀌었기 때문에 호환되는 뼈대만 가져왔다.

리포트는 이것을 **selective weight transfer**라고 부른다. Solar Open 1에서 Solar Open 2로 옮긴 파라미터는 5.69B, 전체 250B의 약 **2.3%**다. token embedding/output layer, normalization layer, 일부 softmax attention projection, linear attention의 query/output projection, shared expert처럼 shape과 의미가 맞는 부분만 전이했다. 나머지 대부분, 특히 320 routed experts는 random initialization이다.

이게 작은 디테일이 아닌 이유가 있다. 200B-A15B proxy 실험에서 transfer를 쓴 모델은 training cross-entropy 1.8에 도달하는 데 12.6B tokens가 필요했고, random initialization은 21.5B tokens가 필요했다. 약 1.7배 차이다. 대형 모델 학습에서 이 정도는 돈과 시간의 차이다.

데이터도 마찬가지다. 처음 정제한 20T token pool을 quality와 rarity 기준으로 10T mixture로 줄였다. real-to-synthetic 비율은 4:6, math와 code는 각각 최소 15%, English share는 80% 이상으로 맞췄다고 한다. 이후 10T general pre-training, 1T intensive pre-training, 약 0.9T length expansion으로 이어진다. 총 pre-training token은 약 12T다.

여기서 한 가지 흥미로운 고백도 있다. Length expansion 단계에서는 데이터 분포 변화 때문에 전체 성능이 약간 떨어졌고, Upstage는 네 개 중간 checkpoint를 merge해 최종 pre-trained model을 만들었다. 1M context를 붙이는 일은 단순히 길이를 늘리는 문제가 아니라, 기존 능력과 긴 문맥 능력 사이의 trade-off를 다루는 작업이었다는 뜻이다.

## Post-training의 주인공은 12명의 specialist다

Solar Open 2의 post-training은 네 단계다. SFT, multi-domain RL, specialist, 그리고 **MOPD(Multi-teacher On-policy Distillation)**다.

처음 두 단계는 generalist base를 만든다. 그 다음이 중요하다. Upstage는 12개 domain specialist를 따로 키웠다. reasoning 계열(math, STEM, code), agents & tools 계열(coding, general tool use, single-workspace, multi-workspace, search), preference & alignment 계열(instruction following, human preference, safety, abstention)로 나뉜다.

문제는 specialist를 따로 잘 키우는 것과 하나의 모델로 합치는 것이 다르다는 점이다. 그냥 teacher가 만든 trace로 SFT하면 student가 자기 실수로 흘러간 state에서 어떻게 복구해야 하는지 배우기 어렵다. 그래서 MOPD는 student가 직접 rollout한 trajectory 위에서, 해당 prompt에 routing된 specialist teacher의 full-vocabulary distribution을 따라가게 한다. 쉽게 말하면, **학생이 자기가 실제로 헤매는 길 위에서 선생님의 다음 선택 분포를 배운다.**

![테크니컬 리포트의 post-training 개요. SFT와 multi-domain RL 이후 12개 specialist teacher를 만들고, MOPD로 하나의 deployable model에 통합한다.](/images/solar-open2-agentic-open-weight-2026-07-22/posttraining-page.png)

이 방식이 agent 모델에서 중요한 이유는 분명하다. Agent는 정답 문장 하나를 생성하는 것이 아니라 상태가 계속 바뀌는 환경에서 움직인다. coding agent는 repo를 수정하고 테스트를 돌린다. officework agent는 xlsx/docx/pptx/pdf를 만들고, 숫자와 출처가 일치해야 한다. tool-use agent는 MCP 환경에서 state를 바꾼다. 이런 작업은 결과만 보고 학습하기 어렵고, trajectory 품질과 self-checking이 중요하다.

리포트의 fully asynchronous RL 설명도 이 맥락이다. Agent rollout은 길이가 들쭉날쭉하다. 동기식으로 처리하면 제일 느린 rollout을 기다리느라 GPU가 놀게 된다. Upstage는 actor와 trainer를 분리하고, stale token을 관리하며, 긴 trajectory를 버리지 않고 salvage하는 방식으로 agentic RL의 throughput 문제를 다뤘다. 이 대목은 모델 논문이라기보다 agent harness 운영 보고서처럼 읽힌다.

## Korean officework agent라는 목표가 선명하다

Solar Open 2가 가장 세게 주장하는 영역은 한국어다. 하지만 단순한 Korean QA가 아니라 **Korean officework agent**다.

리포트에는 Ko-GDPval이라는 in-house benchmark가 나온다. GDPval의 “economically valuable real-world work” 패러다임을 한국 산업, 법, 업무 관행에 맞춘 벤치마크라고 설명한다. 11개 산업 domain, 58개 직업, 170개 한국어 task로 구성되어 있고, 변호사, CPA, 감염관리 전문가, project-finance underwriter 같은 직무의 실제 deliverable 중심 작업을 다룬다.

Solar Open 2의 Ko-GDPval 점수는 **86.8**이다. DeepSeek-V4-Pro 1.6T가 86.9라서 거의 붙어 있고, DeepSeek-V4-Flash 85.0, MiMo-V2.5-Pro 84.6보다 높다. Solar Open 1은 3.4였다. 이건 “조금 좋아졌다”가 아니라, 이전 세대에서는 사실상 못 하던 deliverable-producing officework가 이번 세대에서 생겼다는 주장에 가깝다.

한국어 benchmark 평균도 Solar Open 2가 85.4로 비교 모델 중 가장 높다. KMMLU-Pro 78.4, CLIcK 90.7, Ko-AIME’25 97.7, KBank-MMLU 80.8, KBL 75.5, KorMedMCQA 93.0 같은 숫자가 나온다. 물론 Ko-AIME, KBank-MMLU, Ko-GDPval은 in-house benchmark라 해석에 주의가 필요하다. 그래도 방향은 명확하다. Upstage는 한국어를 “번역된 언어”가 아니라 “업무가 실제로 벌어지는 환경”으로 모델링하려 한다.

## 영어 agent benchmark에서는 강하지만 빈틈도 있다

영어 쪽 결과도 꽤 공격적이다. Solar Open 2는 MMLU-Pro 86.2, GPQA-Diamond 86.3, LiveCodeBench v6 92.4, AIME2026 95.7을 기록했다. Agent benchmark에서는 SWE-Bench Verified 70.4, APEX-Agents 16.6, MCP-Atlas 58.2, GDPval-AA v2 ELO 1128이다.

좋은 숫자만 보면 과하게 흥분하기 쉽다. 리포트는 빈틈도 적고 있다. repository-level, terminal-level software engineering에서는 MiMo-V2.5와 DeepSeek-V4-Flash가 앞선다. SWE-Bench Verified는 Solar Open 2가 70.4, MiMo-V2.5가 73.0, DeepSeek-V4-Flash가 73.8이다. Terminal Bench Hard는 Solar Open 2가 28.3, MiMo-V2.5가 41.7이다.

이건 오히려 신뢰도를 조금 올린다. “모든 것을 이긴다”가 아니라, 어디서 강하고 어디서 남은 과제가 있는지 드러난다. Upstage도 conclusion에서 남은 gap을 repository/terminal-level software engineering, officework deliverable의 fine-grained numerical precision으로 적었다. 둘 다 더 강한 verification과 self-checking behavior가 필요한 영역이다.

## 오픈웨이트지만 라이선스와 현실 비용은 확인해야 한다

Solar Open 2는 Hugging Face에 weights가 공개되어 있고, Upstage 블로그는 commercially usable license라고 쓴다. 다만 라이선스 이름은 **Upstage Solar License**다. Apache 2.0 같은 완전 익숙한 permissive license로 단정하면 안 된다. 실제 제품에 넣으려면 [LICENSE](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/LICENSE)를 따로 확인해야 한다.

운영 비용도 마찬가지다. A15B라고 해도 250B MoE다. 긴 context, high-throughput serving, tool-use agent까지 붙이면 GPU 메모리와 serving stack이 중요하다. Hugging Face 모델카드는 Transformers 실험용으로 Upstage의 별도 Transformers branch를 안내하고, production serving은 vLLM을 권장한다. 즉 이 모델은 노트북에서 “한번 돌려보자”보다 기업·기관의 자체 인프라 deployment에 가까운 물건이다.

그럼에도 의미가 있다. 한국어권에서 오픈웨이트 모델이 단순 챗봇 품질 경쟁을 넘어, agent workflow와 office deliverable까지 정면으로 잡기 시작했다는 신호이기 때문이다.

## 이 모델의 진짜 메시지는 recipe다

저는 Solar Open 2의 핵심을 모델 하나보다 **recipe**로 봅니다. 한국어 tokenizer 효율을 유지하고, Solar Open 1에서 호환되는 2.3%의 뼈대만 가져오고, 20T pool을 10T high-value mixture로 줄이고, 1M context를 위해 hybrid attention과 NoPE를 택하고, 12개 specialist를 MOPD로 합친다.

이 흐름은 “큰 모델을 만들었다”보다 조금 더 구체적이다. 특정 언어권의 sovereign model이 agent 시대에 어디를 파야 하는지 보여준다. native-language tokenizer, 실제 업무 데이터, 도구 호출 환경, deliverable 검증, 긴 trajectory 학습. 이 다섯 가지가 함께 가야 한다.

그래서 Solar Open 2는 한국어 LLM 뉴스이면서 동시에 agent engineering 뉴스다. 앞으로 모델 경쟁은 “대답을 얼마나 잘하나”에서 “일을 얼마나 끝까지, 검증 가능하게 수행하나”로 이동한다. Upstage는 이번 릴리스에서 그 방향을 꽤 노골적으로 선언했다.

저는 이 지점이 제일 반갑다. 한국어 모델이 한국어 문장을 잘 쓰는 수준을 넘어, 한국어로 된 업무 환경에서 파일을 읽고, 숫자를 맞추고, 문서를 만들어내는 쪽으로 가고 있다. 아직 라이선스, serving 비용, 독립 검증이라는 숙제는 남아 있다. 하지만 질문은 바뀌었다. “한국어 모델도 쓸만한가?”가 아니라, **“한국어권 agent stack을 어디까지 자체적으로 만들 수 있는가?”** 쪽으로.

---

### 참고 자료

- Upstage Hugging Face Model Card: [upstage/Solar-Open2-250B](https://huggingface.co/upstage/Solar-Open2-250B)
- Upstage Blog: [Korea's Sovereign Foundation Model, Built for Agentic Use](https://www.upstage.ai/blog/en/solar-open-2)
- Technical Report: [Solar Open 2 Technical Report](https://huggingface.co/upstage/Solar-Open2-250B/blob/main/Solar_Open_2_Tech_Report.pdf)

에이전트와 자동화 워크플로우를 직접 실습해보고 싶은 분들은 제가 정리한 오픈클로 책과 루프 엔지니어링 강의도 참고하셔도 좋습니다. 책은 [이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902), 강의는 [AIFrenz 빌드캠프 · AI 에이전트 실전 강의 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)입니다. 모델을 “답변기”가 아니라 실제 작업 루프 안에 넣어보는 쪽에 초점을 둡니다.
