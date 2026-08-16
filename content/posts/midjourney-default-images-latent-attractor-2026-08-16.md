---
title: "Midjourney는 모르는 프롬프트를 어디로 보내나: default image와 latent attractor"
date: 2026-08-16
tags:
  - image-generation
  - Midjourney
  - prompt-engineering
  - latent-space
  - CLIP
  - evaluation
  - creativity
source: arxiv
source_url: https://arxiv.org/abs/2505.09166
paper_url: https://arxiv.org/abs/2505.09166
---

이미지 모델은 모르는 단어를 만나도 멈추지 않습니다. 에러를 내지도 않습니다. 이미지를 내는 경우가 많습니다. 문제는 그 다음입니다. 모델이 프롬프트를 잘 모를 때, 어디로 가는가.

**An Exploration of Default Images in Text-to-Image Generation**(arXiv:2505.09166)은 이 질문을 Midjourney에서 봅니다. 논문의 표현을 빌리면 default image는 <span style="background-color: #fff59d"><strong>서로 관련 없는 여러 프롬프트에서 반복적으로 나타나는 시각적으로 비슷한 이미지</strong></span>입니다.

코난쌤이 말한 “모델마다 VAE나 latent space가 달라서 결과 분포가 다를 것 같다”는 질문과 꽤 잘 맞습니다. 이 논문은 내부 latent를 직접 본 논문은 아닙니다. 다만 Midjourney를 black-box로 두고, <span style="background-color: #fff59d"><strong>모호하거나 낯선 프롬프트가 어떤 시각적 attractor로 빨려 들어가는지</strong></span>를 관찰합니다.

![Midjourney default images teaser](/images/midjourney-default-images-latent-attractor-2026-08-16/teaser-default-images.png)
*그림 1. 관련 없는 프롬프트들이 비슷한 이미지로 수렴하는 default image 현상. 출처: 논문 Figure 1.*

## 모르는 단어는 빈칸이 아니라 기본 이미지로 처리됩니다

사용자는 프롬프트를 명령문처럼 생각합니다. “이 단어를 넣으면 이 개념이 들어가겠지”라고 기대합니다. 그런데 모델 입장에서는 단어가 항상 명확한 시각 개념으로 연결되는 게 아닙니다.

논문은 이런 경우 default image가 나온다고 정의합니다.

- 입력 단어가 학습 데이터에 거의 없거나
- 단어가 강한 시각 이미지를 호출하지 못하거나
- 프롬프트가 너무 추상적이거나
- 모델이 아는 개념으로 안정적으로 접지하지 못할 때

그 결과 서로 다른 프롬프트가 비슷한 이미지로 나옵니다. 논문은 이를 mode collapse와도 연결합니다. 여기서는 <span style="background-color: #fff59d"><strong>black-box TTI 모델의 inference 단계에서 관찰되는 반복 출력</strong></span>이라는 쪽에 초점을 맞춰 읽었습니다.

여기서 흥미로운 점은 default image가 항상 “못생긴 실패작”으로 보이지 않는다는 겁니다. Midjourney답게 꽤 예쁜 경우도 있습니다. 그래서 사용자가 “내 프롬프트가 잘 반영됐다”고 착각할 수도 있습니다. 예쁜 이미지는 설명 가능성의 적이 되기도 합니다.

## 연구자는 일부러 Midjourney를 헷갈리게 했습니다

논문은 먼저 130개 프롬프트를 수동으로 만들었습니다. 목표는 실제 사용자가 쓸 법하면서도 모델에게 낯선 입력을 만드는 것입니다.

| 범주 | 예시 성격 |
| --- | --- |
| A1 | 희귀하거나 가상의 이름 |
| A2 | 일부러 오염시킨 단어 |
| A3 | 웹 주소 |
| A4 | 저자원 언어 단어, 예: Finnish, Tagalog |
| A5 | glitch token |
| A6 | 음절·약어 |

실험 조건도 고정했습니다. Midjourney model 6.1, square aspect ratio, stylize 0, chaos 0, weird 0, seed 123456. <span style="background-color: #fff59d"><strong>130개 프롬프트 × 4장, 총 520장</strong></span>을 만들고, 저자들이 affinity diagramming으로 비슷한 이미지를 묶었습니다.

그 결과 수동 실험에서 10개의 canonical default image를 찾았습니다.

![수동 실험에서 찾은 10개 default image](/images/midjourney-default-images-latent-attractor-2026-08-16/manual-default-images.jpg)
*그림 2. 수동 실험에서 식별한 10개의 default image. 출처: 논문 Figure 4.*

논문에서 특히 자주 나오는 예시는 Lady-Birdhead입니다. 서로 다른 프롬프트를 넣었는데, 흰 드레스를 입은 여성이 왼쪽을 보고 있고, 머리 위에 새가 있는 식의 이미지가 반복됩니다. 세부는 바뀌지만 motif는 남습니다.

![Lady-Birdhead default image variations](/images/midjourney-default-images-latent-attractor-2026-08-16/lady-birdhead.jpg)
*그림 3. Lady-Birdhead default image의 변형들. 출처: 논문 Figure 5.*

이 장면이 중요한 이유는 단순합니다. <span style="background-color: #fff59d"><strong>프롬프트가 달라도 모델 내부의 시각적 기본 경로가 반복될 수 있다</strong></span>는 뜻입니다. 사용자는 단어를 바꿨다고 생각합니다. 그래도 모델은 비슷한 시각 후보군으로 돌아갑니다.

## CLIP embedding으로 75만 장을 다시 묶었습니다

수동 실험만으로는 “특수하게 만든 프롬프트라 그런 것 아니냐”는 반론이 가능합니다. 논문은 그래서 실제 Midjourney Discord 데이터로 확장합니다.

데이터 규모는 꽤 큽니다.

| 항목 | 값 |
| --- | ---: |
| 수집 원천 | Midjourney Discord 채널 |
| 기간 | 2022-07-09 ~ 2025-03-17 |
| 필터링 후 prompt | <span style="background-color: #fff59d"><strong>189,431개</strong></span> |
| 이미지 후보 | <span style="background-color: #fff59d"><strong>757,724장</strong></span> |
| 포함 버전 | Midjourney v1.0 ~ v6.1 |

분석 방식은 이렇습니다.

1. Midjourney 이미지 패널을 4개 이미지로 분리
2. 각 이미지를 CLIP ViT-L/14 embedding으로 변환
3. 같은 major version 안에서 pairwise cosine similarity 계산
4. hierarchical clustering으로 시각적으로 비슷한 이미지 묶기
5. prompt가 단어 수준으로 너무 비슷한 cluster 제거
6. sentence-transformer로 prompt semantic similarity가 높은 cluster 제거

즉 이미지가 비슷해도 프롬프트가 비슷하면 default image 후보에서 뺍니다. 연구자가 보고 싶은 대상은 “dog”와 “labrador”가 비슷한 이미지를 만든 사례와 다릅니다. <span style="background-color: #fff59d"><strong>프롬프트는 서로 다른데 이미지가 같은 곳으로 수렴하는 사례</strong></span>입니다.

이 부분이 이번 주제와 가장 직접적으로 맞습니다. 내부 VAE는 못 보지만, 출력 이미지를 CLIP 벡터공간으로 올린 뒤 cluster를 찾습니다. 그리고 prompt embedding까지 써서 “시각적으로는 가깝지만 의미적으로는 먼” 묶음만 남깁니다.

## 결과: 4,715개 cluster, 36,243장 이미지

대규모 분석 결과는 이렇습니다.

| 항목 | 값 |
| --- | ---: |
| potential default image cluster | <span style="background-color: #fff59d"><strong>4,715개</strong></span> |
| cluster에 포함된 이미지 | 36,243장 |
| 필터링 데이터셋 내 비율 | 4.84% |
| cluster 평균 크기 | 7.69장 |
| cluster 크기 범위 | 3 ~ 100장 |

논문은 4.84%를 Midjourney 전체 default image 발생률로 해석하면 안 된다고 주의합니다. 짧은 프롬프트, 특정 필터, 특정 threshold로 만든 분석 결과입니다. 그래도 “현상이 실제 사용자 데이터에서도 나온다”는 근거로는 충분합니다.

관찰도 흥미롭습니다.

- 실제 사용자도 짧고 낯선 프롬프트를 사용함
- fantasy names, domain names, oxymorons, abstract noun phrasing, poetic paradoxes, typo 등이 default image 후보를 만들 수 있음
- default image에는 portrait, intricate cityscape, dream-like imagery가 반복됨
- Midjourney major version마다 default image 집합이 다름
- 오래된 버전은 더 단순하거나 추상적이고, 최근 버전은 더 복잡하고 정교함

이건 모델 버전의 미감 차이를 보는 좋은 렌즈입니다. 같은 회사의 같은 제품이라도 버전이 바뀌면 attractor가 바뀝니다. 표현력은 올라가지만, fallback이 사라지는 건 아닙니다. <span style="background-color: #fff59d"><strong>default image는 모델이 모르는 영역에서 드러나는 시각적 습관</strong></span>입니다.

## seed, style, 버전이 바뀌어도 motif는 남습니다

논문은 ablation도 합니다. seed를 바꾸고, style modifier를 붙이고, 더 긴 프롬프트 안에 default-triggering term을 넣고, 모델 버전도 바꿉니다.

![Default image ablation studies](/images/midjourney-default-images-latent-attractor-2026-08-16/ablation-studies.jpg)
*그림 4. seed, style modifier, larger prompt, model version 변화에 따른 default image 변화. 출처: 논문 Figure 7.*

결과를 짧게 정리하면 이렇습니다.

| 조작 | 관찰 |
| --- | --- |
| seed 변경 | default image가 달라질 수 있지만 일부 motif를 공유함 |
| style modifier 추가 | cubism, oil on canvas 같은 스타일이 적용되지만 기본 motif가 남음 |
| 긴 프롬프트에 삽입 | 모델이 아는 단어가 많아지면 default image에서 벗어남 |
| 여러 default prompt 결합 | 여전히 default image가 나오지만 종류가 줄어드는 경향 |
| 버전 변경 | v6.0과 v6.1은 유사, v5.1/v5.2는 더 surreal/abstract |

여기서 실무적으로 중요한 건 긴 프롬프트입니다. 모르는 단어 하나만 던지면 모델은 기본 경로로 갑니다. 그런데 주변에 강한 시각 단서를 많이 주면 아는 단어들이 출력을 끌고 갑니다. prompt engineering은 그래서 “예쁜 단어 추가”보다 <span style="background-color: #fff59d"><strong>모델이 접지할 수 있는 attractor를 충분히 제공하는 작업</strong></span>에 가깝습니다.

## 사용자는 default image를 항상 알아차리지 못합니다

논문은 Prolific에서 48명을 대상으로 사용자 연구도 했습니다. 참가자는 prompt와 이미지를 보고 만족도를 1~7점으로 평가했습니다.

핵심 결과는 다음과 같습니다.

| 조건 | 평균 만족도 |
| --- | ---: |
| Q1: 단어 대체가 미묘하게만 드러남 | 4.9 |
| Q2: prompt-image mismatch가 눈에 띔 | 2.6 |
| Q3: prompt와 이미지가 잘 맞음 | 4.6 |
| Q4: default image | <span style="background-color: #fff59d"><strong>2.4</strong></span> |

Q3와 Q4 차이는 통계적으로 유의했습니다. OR=16.2, p<0.05입니다. default image가 사용자 만족도를 낮출 수 있다는 뜻입니다.

다만 Q1처럼 변화가 미묘하면 사용자는 꽤 만족했습니다. 이게 더 중요한 대목입니다. <span style="background-color: #fff59d"><strong>default image는 실패인데도 미감이 좋으면 성공처럼 받아들여질 수 있습니다</strong></span>. 이미지 모델 평가에서 “예쁜가”와 “프롬프트를 이해했는가”를 분리해야 하는 이유입니다.

![Default images and user satisfaction](/images/midjourney-default-images-latent-attractor-2026-08-16/user-study.png)
*그림 5. default image가 사용자 만족도에 미치는 영향. 출처: 논문 Figure 8.*

## default image를 latent attractor로 읽어봅니다

논문은 default image의 특징을 8개 postulate로 정리합니다. 블로그 관점에서는 네 가지가 특히 중요합니다.

1. unknown input이 들어오면 default image가 생긴다.
2. default image는 모델·버전별로 다르다.
3. 창의적인 프롬프트일수록 default image를 만날 가능성이 있다.
4. 스타일과 구성 제약을 붙여도 기본 motif가 남을 수 있다.

이건 “상용 이미지 모델의 표현력 차이”를 보는 데 좋은 틀입니다. 모델이 잘 아는 개념에서는 차이가 잘 안 보일 수 있습니다. “a dog in a park”는 꽤 그럴듯하게 냅니다. 그런데 희귀 이름, 저자원 언어, 추상 명사, glitch token, 낯선 조합을 넣으면 모델의 기본값이 드러납니다.

그래서 default image는 실패 사례이면서 진단 도구입니다. <span style="background-color: #fff59d"><strong>모델의 시각 vocabulary가 어디까지 닿아 있고, 어디서 generic visual prior로 후퇴하는지 보여줍니다</strong></span>.

## 프롬프트 민감도는 “잘 듣는다”보다 넓은 문제입니다

이 논문은 Midjourney 한 모델만 봅니다. DALL·E, Stable Diffusion, Firefly, Imagen을 직접 비교하지는 않습니다. 그래도 방법론은 확장하기 좋습니다.

상용 이미지 모델들을 비교한다면 이렇게 설계할 수 있습니다.

| 비교 질문 | 측정 방식 |
| --- | --- |
| unknown prompt에서 어디로 수렴하나 | CLIP/DINO cluster의 centroid 비교 |
| 모델별 default motif가 있나 | dissimilar prompt → similar image cluster 탐색 |
| prompt sensitivity가 큰가 | 같은 prompt의 seed별 intra-cluster variance |
| style modifier가 얼마나 먹히나 | modifier 전후 embedding shift |
| 버전 업데이트가 뭘 바꾸나 | version별 default cluster drift |

이렇게 보면 “Midjourney는 예쁘다”보다 더 구체적인 말을 할 수 있습니다. Midjourney는 어떤 prompt dead zone에서 어떤 시각적 기본값으로 돌아가는가. DALL·E는 모르는 단어를 거절하거나 보정하는가, 아니면 비슷한 fallback을 만드는가. Stable Diffusion은 base checkpoint와 LoRA에 따라 attractor가 어떻게 달라지는가. Firefly는 상용 안전장치와 Adobe stock 기반 데이터 정책이 fallback에 어떤 흔적을 남기는가.

이번 논문은 이렇게 읽을 수 있습니다. 프롬프트가 모델을 완전히 조종한다고 보기는 어렵습니다. 프롬프트는 모델이 이미 가진 시각 분포 안에서 경로를 선택하게 합니다. 모르는 길로 밀어 넣으면, 모델은 자기에게 익숙한 길로 돌아옵니다.

그래서 이미지 모델의 표현력은 잘 나온 샘플보다 실패 상황에서 더 잘 보일 때가 있습니다. <span style="background-color: #fff59d"><strong>모델이 모르는 것을 만났을 때 어디로 후퇴하는가, 그 후퇴 지점이 모델의 기본 세계관을 보여줍니다</strong></span>.

## 더 실습해보고 싶은 분들께

에이전트와 자동화 루프를 직접 다뤄보고 싶다면 코난쌤의 책 **[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)**와 **[AIFrenz 빌드캠프 · 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)**를 같이 보셔도 좋습니다. 이런 논문을 읽고, 실험 루프를 만들고, 글로 정리하는 흐름 자체가 요즘 에이전트 작업의 좋은 연습문제입니다.
