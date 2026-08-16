---
title: "VAE를 열어보면 이미지 모델의 차이가 보입니다: Latent-CLIP으로 보는 latent space 제어"
date: 2026-08-16
tags:
  - image-generation
  - diffusion
  - latent-space
  - CLIP
  - VAE
  - SDXL
  - FLUX
  - evaluation
source: arxiv
source_url: https://arxiv.org/abs/2503.08455
paper_url: https://arxiv.org/abs/2503.08455
---

이미지 모델의 차이를 “벡터공간의 분포”로 보고 싶다면, 이 논문은 꽤 직접적인 힌트를 줍니다. 앞의 두 글에서는 black-box 모델의 출력 이미지를 공통 feature space에 다시 올려서 봤습니다.

이번에는 한 단계 더 안쪽으로 들어갑니다. <span style="background-color: #fff59d"><strong>출력 이미지를 디코딩하기 전에, VAE latent 자체를 읽고 제어할 수 있느냐</strong></span>를 묻습니다.

**Controlling Latent Diffusion Using Latent CLIP**(arXiv:2503.08455)은 Latent-CLIP을 제안합니다. 기존 CLIP은 이미지를 픽셀로 본 뒤 텍스트와 맞춰 봅니다.

이 논문은 SDXL-Turbo의 latent를 그대로 입력받는 CLIP을 새로 학습합니다. diffusion 중간 결과를 매번 이미지로 디코딩하지 않아도 됩니다. latent 안에서 “이 이미지가 텍스트와 맞는가”, “위험한 방향으로 가는가”, “보상 점수가 올라가는가”를 볼 수 있습니다.

코난쌤이 말한 “모델마다 VAE 같은 게 조금씩 다를 것 같다”는 감각과 잘 맞습니다. 논문도 관련 배경에서 이 차이를 짚습니다.

<span style="background-color: #fff59d"><strong>SDXL, SDXL-Turbo, AuraFlow는 SDXL VAE latent space를 공유하고, Wuerstchen은 VQ-VAE를 쓰고, FLUX는 4채널이 아닌 16채널 latent space를 쓴다</strong></span>. 즉 모델의 차이는 프롬프트 해석을 넘어, 이미지가 압축되고 조작되는 공간 자체의 차이로도 이어집니다.

![Latent-CLIP 구조](/images/latent-clip-latent-diffusion-control-2026-08-16/latent-clip-architecture.png)
*그림 1. 기존 CLIP은 latent를 VAE-decoding한 뒤 픽셀 이미지로 읽는다. Latent-CLIP은 latent image를 바로 읽는다. 출처: 논문 Figure 1.*

## CLIP은 아직 픽셀 세계에 살고 있었습니다

Stable Diffusion 계열 모델을 떠올려보면 구조는 익숙합니다. 픽셀 이미지 전체에서 diffusion을 돌리면 너무 비쌉니다. 그래서 VAE가 이미지를 작은 latent image로 압축하고, diffusion은 그 latent 안에서 denoising을 합니다.

SDXL 예시는 이렇습니다.

| 항목 | 크기 |
| --- | ---: |
| 원본 이미지 | 1024×1024×3 |
| SDXL latent | 128×128×4 |
| SDXL-Turbo 기본 latent | 64×64×4 |

여기까지 보면 이미지 생성 모델은 이미 latent 세계로 들어왔습니다. 그런데 평가 모델은 아직 픽셀 쪽에 남아 있었습니다. CLIP, reward model, classifier, safety classifier, VLM은 이미지를 픽셀로 받은 뒤 판단하는 경우가 많습니다.

문제는 비용입니다. diffusion 중간 latent를 평가하려면 먼저 VAE decoder로 이미지로 되돌려야 합니다.

논문은 이 VAE-decoding step이 task-specific model의 forward pass보다 더 비쌀 때도 있다고 말합니다. <span style="background-color: #fff59d"><strong>생성은 latent에서 하는데, 판단하려고 매번 픽셀로 돌아오는 병목</strong></span>이 생기는 겁니다.

Latent-CLIP은 이 병목을 없애려는 시도입니다. “이미 latent 안에 의미 정보가 충분히 들어 있다면, CLIP도 latent를 직접 읽게 만들 수 있지 않을까?”라는 질문입니다.

## 27억 쌍으로 latent를 읽는 CLIP을 학습했습니다

논문은 SDXL-Turbo의 VAE latent space를 대상으로 Latent-CLIP을 학습합니다. 방식은 CLIP과 비슷합니다. 이미지와 텍스트를 같은 embedding space에 맞춥니다. 차이는 이미지 입력이 픽셀이 아닌 latent라는 점입니다.

학습 데이터와 규모는 큽니다.

| 항목 | 내용 |
| --- | --- |
| 이미지-텍스트 원천 | LAION-2B-en, COYO |
| latent 생성 | 이미지를 512×512×3으로 맞춘 뒤 VAE encode |
| latent 크기 | 64×64×4 |
| 쌍 규모 | <span style="background-color: #fff59d"><strong>2.7B latent image-text pairs</strong></span> |
| 반복 샘플 | 총 34B latent image samples |
| 모델 | Latent-ViT-B/8, Latent-ViT-B/4-plus |
| 학습 자원 | 128 A100 4일 9.5시간, 256 A100 4일 1.9시간 |

여기서 봐야 할 점은 “latent를 읽는 모델 하나 만들자”는 작업이 생각보다 비싸다는 겁니다. VAE가 바뀌면 latent의 모양과 의미도 바뀝니다.

그래서 SDXL VAE용 Latent-CLIP을 FLUX latent에 그대로 쓸 수 있다고 보기 어렵습니다. 논문도 결론에서 이 한계를 분명히 말합니다. <span style="background-color: #fff59d"><strong>새 VAE architecture마다 대응되는 Latent-CLIP을 다시 학습해야 하는 문제가 남아 있습니다</strong></span>.

이 대목이 중요합니다. 모델별 VAE/latent space 차이는 단순 구현 디테일이 아닙니다. 평가기, 보상 모델, 안전 필터, 편집 도구까지 묶어서 바꾸는 인터페이스 차이입니다.

## latent를 직접 읽어도 ImageNet 분류가 됩니다

첫 검증은 zero-shot ImageNet 분류입니다. Latent-CLIP이 진짜 의미를 읽는지 보려면, latent 이미지를 보고 클래스 이름과 맞출 수 있어야 합니다.

논문은 두 데이터셋을 씁니다.

1. 원본 ImageNet validation set 50,000장
2. SDXL-Turbo로 만든 generated ImageNet

generated ImageNet을 따로 만든 이유가 흥미롭습니다. 원본 이미지를 VAE encode한 latent와 diffusion이 생성한 latent는 분포가 살짝 다를 수 있습니다.

연구자는 이를 확인하기 위해 ImageNet 이미지를 66% noise level까지 noising한 뒤, SDXL-Turbo로 class label 조건 denoising을 수행합니다. 이렇게 생성된 latent에서 Latent-CLIP이 여전히 잘 작동하는지 봅니다.

결과는 꽤 강합니다.

| 모델 | ImageNet top-1 | generated ImageNet top-1 |
| --- | ---: | ---: |
| Latent-ViT-B/8 | 68.8 | 81.7~82.0 |
| Latent-ViT-B/4-plus | <span style="background-color: #fff59d"><strong>73.5</strong></span> | <span style="background-color: #fff59d"><strong>84.6</strong></span> |
| CLIP ViT-B/16 D1B | 73.5 | 85.1 |
| CLIP ViT-L/14 L2B | 75.3 | 86.0 |

Latent-ViT-B/4-plus는 비슷한 크기의 pixel-space CLIP과 거의 맞먹습니다. generated latent에 직접 적용해도 top-1 84.6%가 나옵니다. <span style="background-color: #fff59d"><strong>VAE-decoding을 하지 않아도 latent 안에서 의미 분류가 가능하다</strong></span>는 근거입니다.

![ImageNet 원본과 SDXL 생성 이미지 비교](/images/latent-clip-latent-diffusion-control-2026-08-16/imagenet-generated-comparison.png)
*그림 2. 원본 ImageNet과 SDXL prompt 기반 생성 이미지 비교. generated ImageNet은 latent 분포 이동을 확인하기 위한 실험 장치다. 출처: 논문 Figure 3.*

## 보상 최적화도 픽셀로 돌아가지 않고 합니다

다음 실험은 ReNO입니다. ReNO는 reward-based noise optimization입니다.

풀어 쓰면, SDXL-Turbo가 한 번에 이미지를 만들 때 초기 noise를 조금씩 조정해서 reward가 높은 결과로 보내는 방식입니다. 기존에는 CLIPScore나 PickScore 같은 pixel-space reward를 쓰려면, 중간 latent를 이미지로 디코딩한 뒤 CLIP으로 점수를 계산해야 했습니다.

Latent-CLIP을 쓰면 이 단계가 줄어듭니다.

| 방식 | reward 계산 위치 | 총 시간 |
| --- | --- | ---: |
| pixel CLIPScore ViT-B/32 | VAE decode 후 픽셀 이미지 | 11.59초 |
| Latent-ViT-B/8 CLIPScore | latent 직접 평가 | <span style="background-color: #fff59d"><strong>9.11초</strong></span> |
| Latent-ViT-B/4-plus CLIPScore | latent 직접 평가 | 9.01초 |
| ReNO ensemble | 여러 reward 조합 | 22.51초 |

논문은 같은 크기 pixel CLIP 대비 전체 ReNO 실행 시간이 약 21% 줄었다고 보고합니다. 숫자만 보면 엄청난 혁신으로 보이지 않을 수 있습니다.

다만 inference-time optimization은 반복 단계가 많아질수록 비용이 누적됩니다. <span style="background-color: #fff59d"><strong>latent에서 평가하고 latent에서 조정하는 루프는 이미지 생성 파이프라인의 비용 구조를 바꿀 수 있습니다</strong></span>.

품질도 크게 무너지지 않았습니다. T2I-CompBench에서 Latent-ViT-B/4-plus CLIPScore는 color 0.69, texture 0.70을 기록했고, 비슷한 pixel CLIP과 동등하거나 약간 높은 수준입니다.

spatial relationship은 0.24~0.25 근처로 여전히 어렵습니다. 이건 Latent-CLIP만의 문제라기보다 현재 reward optimization 전반의 약점에 가깝습니다.

![T2I-CompBench reward optimization 비교](/images/latent-clip-latent-diffusion-control-2026-08-16/t2i-clipscore-reward.png)
*그림 3. T2I-CompBench prompt에서 pixel CLIP reward와 Latent-CLIP reward를 비교한다. 목적은 더 예쁜 샘플보다 decoding 없이 reward를 줄 수 있는지 확인하는 데 있다. 출처: 논문 Figure 4.*

## GenEval에서도 큰 격차는 없었습니다

GenEval은 object co-occurrence, position, counting, color 같은 구성을 봅니다. 여기서 Latent-CLIP은 pixel-space CLIP과 비슷한 수준의 성능을 보입니다.

몇 가지 숫자만 보면 이렇습니다.

| 모델 | mean | two objects | counting | total time |
| --- | ---: | ---: | ---: | ---: |
| Base SDXL-Turbo | 0.54 | 0.66 | 0.45 | 0.12초 |
| ReNO ensemble | 0.64 | 0.86 | 0.62 | 22.51초 |
| Latent-ViT-B/8 CLIPScore | 0.60 | 0.78 | 0.53 | 9.11초 |
| Latent-ViT-B/4-plus CLIPScore | <span style="background-color: #fff59d"><strong>0.62</strong></span> | <span style="background-color: #fff59d"><strong>0.82</strong></span> | 0.60 | 9.01초 |
| CLIP ViT-g/14 CLIPScore | 0.62 | 0.82 | 0.60 | 13.50초 |

해석은 조심해야 합니다. Latent-CLIP이 ReNO ensemble을 이겼다는 이야기는 아닙니다. 더 큰 ensemble과는 아직 차이가 있습니다.

논문의 핵심은 <span style="background-color: #fff59d"><strong>비슷한 크기의 pixel CLIP reward를 latent reward로 바꿔도 성능이 크게 떨어지지 않고 시간이 줄어든다</strong></span>는 쪽입니다.

![GenEval prompt에서 reward optimization 비교](/images/latent-clip-latent-diffusion-control-2026-08-16/geneval-comparison.png)
*그림 4. GenEval prompt에서 base SDXL-Turbo, pixel CLIP reward, Latent-CLIP reward 결과를 비교한다. 출처: 논문 Figure 6.*

## 안전 필터도 latent 안에서 움직일 수 있습니다

논문은 safety 적용도 실험합니다. I2P(inappropriate image prompts) 데이터셋 4,703개 prompt를 쓰고, hate, harassment, violence, self-harm, sexual content, shocking imagery, illegal activity 같은 범주를 봅니다.

방식은 간단합니다. harmful concept와 가까운 latent는 reward를 낮게 주고, 50 gradient steps 동안 그 방향에서 멀어지게 합니다. 픽셀 이미지로 매번 렌더링할 필요가 줄어듭니다. 결과는 다음과 같습니다.

| 모델 | 전체 inappropriate probability |
| --- | ---: |
| SDXL-Turbo | 0.32 |
| pixel CLIP ViT-B/16 | 0.19 |
| Latent-ViT-B/4-plus | <span style="background-color: #fff59d"><strong>0.16</strong></span> |
| SLD Hyp-Strong | 0.13 |

SLD는 safety 전용 방법입니다. Latent-CLIP은 범용 reward model에 가깝습니다. 그 점을 감안하면 Latent-CLIP의 수치는 꽤 근접합니다. aesthetic score도 5.79에서 5.82로 유지됩니다. 즉, 위험한 방향을 줄이면서 전체 이미지 품질은 크게 무너지지 않았다는 주장입니다.

![I2P safety latent guidance](/images/latent-clip-latent-diffusion-control-2026-08-16/i2p-safety-progression.png)
*그림 5. I2P prompt에서 latent guidance가 진행되며 이미지가 어떻게 바뀌는지 보여준다. 출처: 논문 Figure 8.*

## 이 논문이 모델별 latent 차이를 말해주는 방식

이 논문은 Midjourney, DALL·E, Firefly를 비교하지 않습니다. SDXL-Turbo의 latent space 안에서 Latent-CLIP을 학습하고 평가합니다. 그래도 코난쌤 질문에 중요한 힌트를 줍니다.

첫 번째로, latent space는 의미를 담고 있습니다. 이미지로 디코딩하지 않아도 class, prompt alignment, harmful concept, aesthetic preference를 어느 정도 읽을 수 있습니다.

두 번째로, latent space는 모델별 인터페이스입니다. SDXL VAE의 64×64×4 latent를 읽도록 학습한 모델은 SDXL 계열에는 맞지만, FLUX의 16채널 latent나 Wuerstchen의 VQ-VAE latent에는 그대로 맞지 않습니다.

세 번째로, 모델 비교는 “같은 프롬프트 결과 비교”에서 끝나지 않습니다. <span style="background-color: #fff59d"><strong>각 모델이 어떤 latent representation을 쓰고, 그 공간에서 의미·스타일·안전·선호를 어떻게 읽고 조정할 수 있는지</strong></span>까지 봐야 합니다.

이 관점으로 앞의 두 글을 다시 보면 흐름이 이어집니다.

| 글 | 관찰 위치 | 질문 |
| --- | --- | --- |
| Generated Faces in the Wild | Inception feature space | 출력 얼굴 분포가 실제 얼굴과 얼마나 다른가 |
| Default Images | CLIP image embedding space | 모르는 프롬프트가 어떤 default image로 수렴하는가 |
| Latent-CLIP | VAE latent space | 디코딩 전 latent를 직접 읽고 제어할 수 있는가 |

앞의 두 글이 “상용/black-box 모델은 내부를 못 보니 출력 분포를 보자”였다면, 이번 글은 “열린 latent diffusion에서는 내부 공간을 직접 읽는 평가기를 만들 수 있다”는 이야기입니다.

## 프롬프트 엔지니어링 다음은 latent interface입니다

이미지 모델을 쓰는 입장에서는 보통 프롬프트를 고칩니다. 단어를 더 넣고, 스타일을 붙이고, negative prompt를 조절합니다. 이 방식은 여전히 중요합니다. 다만 모델이 발전할수록 제어 지점은 더 안쪽으로 들어갑니다.

Latent-CLIP이 보여주는 방향은 이렇습니다.

- 생성 중간 latent를 바로 평가한다.
- reward를 pixel image 대신 latent에 준다.
- safety filtering도 latent 단계에서 한다.
- 모델별 VAE/latent space에 맞는 평가기를 따로 둔다.
- 디코딩 비용을 줄이고, inference loop를 더 촘촘하게 돌린다.

그래서 이 논문은 “CLIP을 빠르게 만든 논문” 정도로만 읽으면 아깝습니다. 더 큰 메시지는 <span style="background-color: #fff59d"><strong>이미지 생성 모델의 표현력과 제어 가능성이 VAE latent interface 위에서 다시 설계되고 있다</strong></span>는 점입니다.

코난쌤이 처음 던진 질문, 모델마다 VAE가 다르면 결과 분포도 다르지 않겠냐는 질문은 여기서 더 선명해집니다. 맞습니다. 그리고 그 차이는 이미지 몇 장의 미감 차이로만 나타나지 않습니다. 평가기 위치, reward 계산 위치, safety 적용 단계까지 바꿉니다.

결국 다음 세대 이미지 모델 비교는 이렇게 가야 할 것 같습니다. 프롬프트 결과를 보는 비교에서, <span style="background-color: #fff59d"><strong>모델별 latent space를 읽고 조향하는 인터페이스 비교</strong></span>로요.

## 더 실습해보고 싶은 분들께

에이전트와 자동화 루프를 직접 다뤄보고 싶다면 코난쌤의 책 **[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)**와 **[AIFrenz 빌드캠프 · 모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)**를 같이 보셔도 좋습니다.

논문을 읽고, 실험 루프를 만들고, 결과를 글과 Threads로 재가공하는 과정 자체가 요즘 에이전트 작업의 좋은 연습문제입니다.
