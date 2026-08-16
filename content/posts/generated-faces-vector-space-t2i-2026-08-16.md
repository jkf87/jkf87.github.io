---
title: "이미지 모델의 차이는 어디에 남을까: 얼굴 분포로 본 Stable Diffusion, Midjourney, DALL·E 2"
date: 2026-08-16
tags:
  - image-generation
  - diffusion
  - latent-space
  - evaluation
  - FID
  - Midjourney
  - DALL-E
  - Stable-Diffusion
source: arxiv
source_url: https://arxiv.org/abs/2210.00586
paper_url: https://arxiv.org/abs/2210.00586
---

같은 프롬프트를 넣었는데 왜 모델마다 그림이 다르게 나올까요. 흔한 답은 이겁니다. Midjourney는 예쁘고, DALL·E는 말을 잘 듣고, Stable Diffusion은 조절이 쉽다. 틀린 말은 아닌데, 조금 표면적입니다.

조금 더 안쪽으로 들어가면 질문이 바뀝니다. <span style="background-color: #fff59d"><strong>모델마다 생성 이미지가 떨어지는 ‘분포’ 자체가 다른 것 아닐까</strong></span>. 내부 VAE나 latent space를 직접 볼 수 있으면 제일 좋겠지만, 상용 모델은 대부분 닫혀 있습니다. 그래서 연구자들은 우회합니다. 생성된 이미지를 다시 공통 벡터공간에 올리고, 그 분포를 비교합니다.

Ali Borji의 2022년 논문 **Generated Faces in the Wild: Quantitative Comparison of Stable Diffusion, Midjourney and DALL-E 2**는 이 방향의 초기 사례로 볼 수 있습니다. 논문 자체는 얼굴 품질 비교입니다. 읽는 관점을 조금 바꾸면, 이건 <span style="background-color: #fff59d"><strong>상용 이미지 모델을 black-box로 두고 결과물의 벡터 분포를 비교한 실험</strong></span>입니다.

## 질문을 “어디에 분포하나”로 바꿔봅니다

논문은 Stable Diffusion, Midjourney, DALL·E 2가 만든 얼굴을 비교합니다. 여기서 중요한 점은 “초상화 생성 모델” 전용 비교와 다르다는 대목입니다. 연구자는 복잡한 장면을 생성하게 한 뒤, 그 안에 들어 있는 얼굴만 잘라냅니다.

방식은 이렇습니다.

1. COCO caption 중 사람 관련 단어가 들어간 프롬프트를 고름
2. Stable Diffusion, Midjourney, DALL·E 2로 이미지를 생성함
3. MediaPipe face detector로 이미지 안의 얼굴을 탐지함
4. 탐지된 얼굴을 100×100 크기로 정규화함
5. 실제 얼굴 분포와 생성 얼굴 분포 사이의 FID를 계산함

여기서 FID, Fréchet Inception Distance는 이미지 품질 점수처럼 자주 쓰이지만, 실제로는 <span style="background-color: #fff59d"><strong>Inception 네트워크의 feature space에서 두 이미지 집합의 평균과 공분산이 얼마나 다른지 보는 지표</strong></span>입니다. 픽셀을 직접 비교하는 게 아닙니다. 이미지를 신경망이 읽은 벡터로 바꾼 뒤, 그 벡터들의 분포를 비교합니다.

그래서 이 논문은 코난쌤이 말한 질문과 닿아 있습니다. “모델마다 VAE 같은 게 달라서 결과 분포가 다르지 않을까?” 내부 latent는 못 보지만, 출력 이미지를 공통 feature space에 다시 올려서 분포 차이를 보는 겁니다.

![Stable Diffusion, Midjourney, DALL·E 2 얼굴 FID 비교](/images/generated-faces-vector-space-t2i-2026-08-16/fid-results.png)
*그림 1. 모델별 생성 얼굴의 FID 비교. 낮을수록 실제 얼굴 분포에 가깝다. 출처: 논문 Figure 1.*

## 데이터는 15,076개의 생성 얼굴입니다

논문이 만든 데이터셋 이름은 GFW, Generated Faces in the Wild입니다. 규모는 다음과 같습니다.

| 구분 | 수량 |
| --- | ---: |
| 전체 생성 얼굴 | <span style="background-color: #fff59d"><strong>15,076개</strong></span> |
| Stable Diffusion | 8,050개 |
| Midjourney | 6,350개 |
| DALL·E 2 | 676개 |
| 실제 얼굴 비교군 | 30,000개 |

DALL·E 2 수량이 적은 이유는 당시 대량 생성 API 접근이 어려웠기 때문입니다. 연구자는 포털에 프롬프트를 직접 입력하고 결과를 저장했습니다. 그래서 공정성을 위해 세 모델 모두 676개 얼굴로 맞춘 비교도 따로 합니다.

이 부분은 중요합니다. FID는 샘플 수에 민감합니다. 생성 이미지가 적으면 분포 추정이 흔들립니다. 논문도 이 한계를 인정합니다. 그래도 같은 샘플 수로 맞춘 비교에서도 Stable Diffusion이 가장 낮은 FID를 보였습니다.

<span style="background-color: #fff59d"><strong>결과만 놓고 보면 Stable Diffusion의 얼굴 분포가 실제 얼굴 분포에 가장 가까웠고, Midjourney와 DALL·E 2는 더 멀었습니다</strong></span>. 논문은 Midjourney의 낮은 점수 일부를 “surrealistic and anime” 경향 때문으로 봅니다. 지금 기준으로 보면 오래된 모델 비교지만, 분포 관점에서는 꽤 흥미로운 단서입니다.

![세 모델이 생성한 장면 예시](/images/generated-faces-vector-space-t2i-2026-08-16/sample-scenes.png)
*그림 2. 같은 계열의 사람 포함 장면에서도 모델마다 질감과 스타일의 기본값이 다르게 나타난다. 출처: 논문 Figure 2.*

## 얼굴만 보면 모델의 기본 미감이 더 또렷해집니다

전체 이미지를 보면 배경, 구도, 색감, 조명, 스타일이 섞입니다. Midjourney가 “더 멋져 보인다”거나 DALL·E가 “더 설명적으로 보인다”는 인상이 여기서 나옵니다. 그런데 얼굴만 잘라서 보면 이야기가 조금 달라집니다.

얼굴은 사람이 매우 민감하게 보는 대상입니다. 눈동자, 안경, 비대칭, 옆얼굴, 가려진 얼굴, 표정 같은 작은 오류가 바로 드러납니다. 논문도 세 모델 모두 다음 요소에서 자주 실패한다고 말합니다.

- eyeglasses
- eyeballs
- occluded faces
- profile faces
- symmetry

이 대목은 렌더링 문제만으로 보기 어렵습니다. 모델이 학습한 얼굴 manifold가 얼마나 촘촘한지, 복잡한 장면 안에서도 얼굴을 얼마나 안정적으로 복원하는지의 문제입니다. <span style="background-color: #fff59d"><strong>이미지 모델의 “표현력”은 예쁜 샘플 몇 장보다, 이런 실패 사례의 분포에서 더 잘 보일 때가 있습니다</strong></span>.

![생성 장면에서 검출된 얼굴 예시](/images/generated-faces-vector-space-t2i-2026-08-16/detected-faces.png)
*그림 3. 장면 전체 대신 검출된 얼굴만 잘라 비교한다. 이렇게 보면 모델별 얼굴 분포의 차이가 더 선명해진다. 출처: 논문 Figure 3.*

## 왜 DALL·E 2는 불리했을까

논문은 DALL·E 2가 Stable Diffusion보다 낮게 나온 이유를 몇 가지로 추정합니다.

첫 번째 이유는 OpenAI가 deepfake 방지를 위해 학습 과정에 얼굴 관련 safeguard를 넣었을 가능성입니다. 실제 인물 얼굴을 외워서 재현하는 위험을 줄이면, 얼굴 분포가 실제 얼굴과 조금 멀어질 수 있습니다.

두 번째 이유는 DALL·E 2가 단일 초점의 이미지, 특히 imaginary portrait에는 강하지만, 복잡한 장면 안의 작은 얼굴에는 불리할 수 있다는 설명입니다. 즉 “인물 초상화 하나”와 “사람이 여러 명 섞인 장면에서 검출된 작은 얼굴”은 다른 문제입니다.

세 번째는 앞서 말한 샘플 수 문제입니다. DALL·E 2는 676개뿐이라 FID 추정이 불안정할 수 있습니다. 연구자는 이 문제를 줄이기 위해 동일 샘플 수 비교를 했지만, 더 큰 데이터가 필요하다고 분명히 적습니다.

여기서 얻을 수 있는 교훈은 간단합니다. <span style="background-color: #fff59d"><strong>상용 모델 비교는 모델 능력과 함께 접근성, 안전장치, 샘플링 조건까지 같이 비교하게 됩니다</strong></span>. black-box 모델 평가가 어려운 이유입니다.

## 내부 latent를 못 보면 출력 분포를 본다

코난쌤이 말한 “모델마다 VAE 같은 게 조금씩 다를 것”이라는 감각은 맞는 방향입니다. Stable Diffusion 계열은 VAE로 픽셀 이미지를 압축한 latent에서 diffusion을 돌립니다. DALL·E 2는 CLIP latent를 거치는 구조로 설명됩니다. Midjourney는 세부 구조가 공개되어 있지 않습니다. Firefly, GPT-image 계열도 마찬가지로 내부 구조를 완전히 알기 어렵습니다.

그래서 직접 비교는 어렵습니다. 서로 다른 모델의 내부 latent 좌표는 같은 공간이 아닙니다. 어떤 모델의 z 좌표와 다른 모델의 z 좌표를 그대로 비교할 수 없습니다.

대신 가능한 실험은 이겁니다.

| 보고 싶은 것 | 가능한 우회 측정 |
| --- | --- |
| 내부 latent 분포 | 생성 이미지를 공통 encoder로 재임베딩 |
| 시각적 realism | Inception feature 기반 FID/KID |
| 프롬프트-이미지 정렬 | CLIP score, VQA 기반 평가 |
| 스타일 attractor | CLIP/DINO embedding의 centroid와 covariance |
| 다양성 | 같은 프롬프트 반복 생성의 intra-prompt variance |
| 모델 간 거리 | Wasserstein distance, MMD, cluster overlap |

이 논문은 그중 FID를 택했습니다. 얼굴 이미지를 Inception feature space에 올리고, 실제 얼굴 분포와 얼마나 다른지 봤습니다. 지금 다시 한다면 DINOv2, CLIP, ArcFace 같은 feature extractor를 같이 쓰는 게 더 낫습니다. 특히 얼굴은 Inception보다 ArcFace 계열이 더 직접적일 수 있습니다. 논문도 “ImageNet으로 학습된 embedding은 얼굴 평가에 한계가 있고, 얼굴 전용 분류 모델이 더 나을 수 있다”고 적습니다.

## 프롬프트는 명령문이 아니라 분포를 건드리는 좌표값입니다

이 논문은 오래됐습니다. DALL·E 2, 초기 Midjourney, 초기 Stable Diffusion 비교입니다. 지금의 GPT-image, Imagen, Midjourney v7, FLUX, SD3.5와는 다릅니다. 그래도 중요한 관점은 남습니다.

우리는 이미지 모델을 볼 때 결과 한 장을 봅니다. 그런데 모델은 한 장만 만드는 장치로만 보기 어렵습니다. 실제로는 <span style="background-color: #fff59d"><strong>특정 조건에서 이미지 분포를 샘플링하는 시스템</strong></span>입니다. 같은 “a person in a room”이라는 프롬프트도 어떤 모델은 사진 쪽으로, 어떤 모델은 일러스트 쪽으로, 어떤 모델은 광고 이미지 쪽으로 끌고 갑니다.

이 차이는 단순 취향이 아닙니다. 학습 데이터, text encoder, latent representation, decoder, safety layer, sampling policy가 합쳐진 결과입니다. 내부를 못 보더라도 출력 분포는 남습니다. 그 출력 분포를 공통 벡터공간에서 보면, 모델의 “기본 세계관”이 조금씩 드러납니다.

그래서 이 논문의 진짜 쓸모는 순위표가 아닙니다. Stable Diffusion이 이겼다는 순위표보다도, <span style="background-color: #fff59d"><strong>이미지 생성 모델을 비교할 때 샘플 몇 장의 인상이 아니라 분포를 봐야 한다는 태도</strong></span>가 더 중요합니다.

다음에 이 주제를 확장한다면 실험은 이렇게 짤 수 있습니다.

- 같은 프롬프트 100개를 여러 모델에 입력
- 모델당 프롬프트별 4~8장 생성
- 결과 이미지를 CLIP, DINOv2, Inception, aesthetic encoder로 임베딩
- 프롬프트별 centroid shift와 covariance를 비교
- “말을 잘 듣는 모델”과 “자기 스타일로 끌고 가는 모델”을 분리

이렇게 보면 프롬프트 엔지니어링도 조금 다르게 보입니다. 프롬프트는 모델에게 내리는 고정 명령문으로만 보기 어렵습니다. <span style="background-color: #fff59d"><strong>각 모델의 latent attractor를 어느 방향으로 건드릴지 정하는 조향값</strong></span>처럼 작동합니다.

---

## 더 실습해보고 싶은 분들께

에이전트와 자동화 루프를 직접 다뤄보고 싶다면 코난쌤의 책 **[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)**와 **[AIFrenz 빌드캠프 · 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)**를 같이 보셔도 좋습니다. 이런 논문을 읽고, 실험 루프를 만들고, 글로 정리하는 흐름 자체가 요즘 에이전트 작업의 좋은 연습문제입니다.
