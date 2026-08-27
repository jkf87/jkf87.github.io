---
title: "MidTool — 도구 사용 능력은 mid-training 단계에서 심어야 한다"
date: 2026-08-27
tags:
  - LLM
  - agent
  - tool-use
  - mid-training
  - MCP
  - fine-tuning
  - arxiv
draft: false
description: "Snowflake 팀의 MidTool 논문 정리. 20.3B 토큰의 도구 사용 mid-training 데이터를 Qwen3-4B/8B에 넣으니 BFCL·τ²-Bench·MCP-Universe 전반에서 SFT/RL 성능이 일관되게 오릅니다. 데이터 구성과 핵심 수치, 한계까지 정리했습니다."
---

## 결론 먼저

Snowflake 연구팀이 발표한 MidTool(arXiv:2608.20314)의 핵심 주장은 하나입니다. <span style="background-color: #fff59d"><strong>일반 도구 사용 능력은 post-training에만 맡기지 말고 mid-training 단계에서 전용 데이터로 심어야 한다</strong></span>는 겁니다.

Qwen3-4B-Base와 Qwen3-8B-Base에 20.3B 토큰 규모의 MidTool-Mix로 mid-training을 하고, 동일한 SFT·RL 레시피를 적용했더니 세 벤치마크(BFCL, τ²-Bench, MCP-Universe)에서 일관되게 baseline을 앞질렀습니다. 특히 멀티턴·인터랙티브 설정에서 격차가 컸습니다.

기준일: 2026-08-20 arXiv v1 공개, 이 글은 2026-08-27 기준입니다.

## 핵심 수치 요약

| 항목 | 값 |
| --- | --- |
| 데이터 총량 | 20.3B 토큰, 11.22M 샘플 |
| 구성 | Web 42% / Code 26% / PDF 23% / 네이티브 트라젝토리 9% |
| 베이스 모델 | Qwen3-4B-Base, Qwen3-8B-Base |
| BFCLv3 Overall (4B, SFT) | 39.73% → 50.25% (+10.5) |
| BFCLv3 Overall (4B, SFT+RL) | → 54.18% |
| τ²-Bench Pass@1 (4B, SFT) | 8.54% → 12.23% |
| MCP-Universe Score (4B, SFT) | 13.20 → 18.66 (+5.5) |
| 학습 환경 | mid-training/SFT: H200 32개, RL: B200 8개 |

출처: [arXiv:2608.20314](https://arxiv.org/abs/2608.20314), 데이터·모델은 [HuggingFace 컬렉션](https://hf.co/collections/MidTool/midtool-release)에 공개되어 있습니다.

![MidTool 파이프라인 개요](/images/2026-08-27-midtool-tool-use-midtraining/fig-1-p1.png)
*그림 1. MidTool 데이터 구축 파이프라인 (원문 Figure 1)*

## 문제 정의

도구 사용 능력은 지금까지 거의 전부 post-training(SFT, RL)으로 만들어 왔습니다. 근데 이 방식엔 구조적 부담이 있습니다. 모델이 도구 인식, 스키마 기반 인자 구성, 정보 부족 시 명확화 요청, 멀티스텝 실행을 좁은 감독 신호만으로 한 번에 배워야 하거든요.

연구팀은 이걸 두 결핍으로 나눕니다. <span style="background-color: #fff59d"><strong>grounding</strong></span>은 문서·PDF·코드 같은 지저분한 실자료에서 도구 경계와 필수 인자를 추론하는 능력. <span style="background-color: #fff59d"><strong>execution</strong></span>은 여러 턴에 걸쳐 계획하고, 누락 정보를 되묻고, 순서를 지켜 호출하는 능력입니다. MidTool의 두 합성 브랜치가 각각 이 결핍을 겨냥합니다.

## 데이터 파이프라인

![MidTool-Mix 구성](/images/2026-08-27-midtool-tool-use-midtraining/table-2-p6.png)
*표 2. MidTool-Mix 구성 (원문 Table 2)*

네 가지 소스에서 출발합니다.

- **Web**: FineWeb 덤프(2020–2025)에서 API 레퍼런스, 개발 문서, CLI 안내 등을 필터링. 6.86M 샘플.
- **PDF**: FinePDFs 영어 서브셋. 매뉴얼·제품 핸드북 같은 장문 절차 문서. 1.34M 샘플.
- **Code**: GitHub 이벤트 데이터 기반 에이전트·MCP 저장소 + 주요 언어 고품질 저장소. 2.60M 샘플.
- **Tool artifacts**: 실제 REST API와 MCP 스킬에서 실행 가능한 스키마 확보.

여기에 합성 브랜치 두 개가 붙습니다. 문서 기반 context-grounded 증강은 Qwen3-235B로 QA와 트라젝토리를 만들고, 네이티브 합성은 GPT-5 시리즈로 단일 호출부터 정보 누락 상황까지 트라젝토리를 생성한 뒤 턴 순서·스키마·인자·응답 일관성 검증을 통과한 것만 남깁니다.

오염 관리도 두 겹입니다. 수집 단계에서 BFCL·τ²-Bench·MCP-Universe 관련 저장소를 블랙리스트로 제외하고, 완성 믹스에 DeCon으로 재검사했더니 <span style="background-color: #fff59d"><strong>기준일 기준 실제 리키지 증거는 없었다</strong></span>고 보고합니다.

## 결과: BFCL

4B 기준으로 SFT만 붙였을 때 Overall이 39.73%에서 50.25%로 오릅니다. 멀티턴 평균은 15.50%에서 26.63%로 <span style="background-color: #fff59d"><strong>10점 이상 상승</strong></span>합니다. RL을 더하면 54.18%까지 갑니다. 8B에서도 같은 패턴이 유지되고, RL 조합이 멀티턴 최고 성격을 냅니다.

## 결과: τ²-Bench, MCP-Universe

![τ²-Bench 결과](/images/2026-08-27-midtool-tool-use-midtraining/table-4-p8.png)
*표 4. τ²-Bench 결과 (원문 Table 4)*

τ²-Bench는 항공·리테일·통신 수직 도메인의 인터랙티브 과제를 측정합니다. 4B에서 MidTool-Mix가 Overall Pass@1을 8.54%에서 12.23%로, RL까지 더하면 19.96%까지 끌어올립니다. 리테일 Pass@1은 SFT+RL 기준 33.55%로 baseline 대비 크게 오릅니다.

MCP-Universe는 실제 MCP 서버(브라우저 자동화, 금융, 위치, 웹 검색) 위에서 돌아가는 OOD 테스트입니다. 4B Overall Score가 13.20에서 18.66로, Pass는 1.68%에서 5.03%로 오릅니다. 8B SFT+RL은 Score 21.31, Pass 9.50%까지 갑니다.

## 절제 실험 결과

한쪽 브랜치만 빼면 성능이 깨집니다. 문맥 증강만 남기면 BFCL Overall +4.9, 네이티브 트라젝토리만 남기면 +7.9. 두 브랜치를 다 넣은 완성 믹스만 <span style="background-color: #fff59d"><strong>8개 지표 전부에서 무미드트레이닝 대비 개선</strong></span>을 보입니다. 즉 grounding 지도와 execution 지도는 상호 보완적입니다.

비교 baseline인 일반 mid-training(Dolmino-20BT)은 BFCL에선 좀 오르지만 τ²-Bench와 MCP-Universe 전이는 약합니다. 범용 명령이행 데이터는 심플한 함수 콜에는 도움이 되지만 <span style="background-color: #fff59d"><strong>에이전트 설정으로는 전이가 잘 안 된다</strong></span>는 신호입니다.

## 학습 동역학

![SFT 수렴](/images/2026-08-27-midtool-tool-use-midtraining/fig-4-p20.png)
*그림 4. SFT 손실 궤적 (원문 Figure 4)*

MidTool-Mix로 초기화한 모델이 SFT에 가장 낮은 손실로 진입하고, 내내 유리하게 유지됩니다. RL에서도 초기 보상이 높고 초반 상승이 빠릅니다.

흥미로운 건 <span style="background-color: #fff59d"><strong>RL 훈련 보상은 나중에 서로 비슷해지는데 벤치마크 격차는 그대로 남는다</strong></span>는 점입니다. 학습 환경에 대한 적응만으로 최종 품질이 정해지지는 않고, mid-training의 진짜 가치는 범용성 쪽에 있습니다.

## 한계: 웹 검색은 그대로 0점

MCP-Universe의 웹 검색 서브셋은 0.00에 머뭅니다. 브라우저 자동화·금융·위치 도메인은 개선되니 도구 전이 자체는 잘 된 것이고, <span style="background-color: #fff59d"><strong>긴 호라이즌 탐색·반복 정제가 필요한 deep-search류 행동은 별도 감독이 필요하다</strong></span>는 능력 경계입니다. 논문은 이 결과를 일반 도구 사용과 전문 에이전시 영역을 가르는 증거로 읽습니다.

부록 파일럿에서는 텍스트 전용 학습만 한 Gemma3-4B가 VisualToolBench에서 도구 성공률 0.5863 → 0.7231로 오르는 초기 전이 신호도 보고합니다.

## 내 해석

정리했습니다. 이 논문의 실무적 의미는 셋이라고 봅니다.

- 도구 사용 데이터 파이프라인의 설계 철학이 '깨끗한 데모 수집'에서 '지저분한 실자료 + 실행 검증 합성'으로 옮겨가고 있습니다.
- 공개 데이터와 코드가 전부 풀려 있어서 <span style="background-color: #fff59d"><strong>미드트레이닝 실험이 이제 중소 팀도 접근 가능한 영역이 됐다</strong></span>라는 점입니다.
- 커리큘럼 관점에서 mid-training과 post-training을 함께 설계해야 한다는 다음 질문을 남겨둡니다.

근데 두 합성 브랜치가 전부 GPT-5·Qwen3-235B 같은 강한 교사 모델에 의존한다는 점은 남은 약점입니다. 논문도 오픈웨이트 에이전트가 자기 도구 사용 학습 데이터를 합성하는 시점을 '에이전트 성숙도의 척도'로 보자고 제안합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### MidTool-Mix 데이터와 모델은 공개되어 있나요?
네. [HuggingFace 컬렉션](https://hf.co/collections/MidTool/midtool-release)에서 데이터와 모델을 공개했습니다.

### mid-training만 하면 도구 사용이 되나요?
mid-training만으로 끝나는 건 아닙니다. MidTool의 주장은 mid-training이 post-training의 기반을 다진다는 것입니다. 실험에서도 SFT·RL은 동일하게 적용했고, 그 조합에서 격차가 벌어졌습니다.

### 일반 mid-training 데이터를 쓰면 어떻게 되나요?
Dolmino-20BT 비교에서 BFCL 일부는 오르지만 τ²-Bench·MCP-Universe 전이는 약했습니다. 도구 중심 구성이 유효합니다.

### 어떤 모델로 검증했나요?
Qwen3-4B-Base와 Qwen3-8B-Base 두 규모에서, SFT 단독과 SFT+RL 두 레시피에서 모두 일관된 개선을 확인했습니다.
