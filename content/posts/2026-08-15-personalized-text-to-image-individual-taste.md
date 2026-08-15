---
title: "이미지 생성 AI는 이제 개인 취향을 배워야 한다"
date: 2026-08-15
tags:
  - AI
  - image-generation
  - diffusion
  - preference-learning
  - personalization
  - design
source: arxiv
source_url: https://arxiv.org/abs/2604.07427
paper_url: https://arxiv.org/html/2604.07427v1
---

arXiv:2604.07427 "Personalizing Text-to-Image Generation to Individual Taste" 정리했습니다. 핵심은 이겁니다. 이미지 생성 모델은 이제 프롬프트를 잘 따르는 수준을 넘어, <span style="background-color: #fff59d"><strong>사용자마다 다른 미감 자체를 학습해야 하는 단계</strong></span>로 가고 있습니다.

지금까지 ImageReward, PickScore, HPS 같은 보상 모델은 “대체로 사람들이 더 좋아하는 이미지”를 맞추는 쪽이었습니다. 근데 논문이 지적하는 병목은 명확합니다. <span style="background-color: #fff59d"><strong>평균적으로 좋은 이미지와 내가 좋아하는 이미지는 다를 수 있습니다</strong></span>.

저는 이 논문을 이미지 프롬프팅 논문에서 한 단계 더 나아간 디자인 워크플로 논문으로 읽었습니다. 프롬프트를 더 길게 쓰는 일도 필요합니다. 동시에 내가 계속 고른 이미지 기록이 하나의 취향 프로필이 되는 쪽이 더 중요해집니다.

## 평균 취향으로는 설명이 안 되는 영역

논문은 Text-to-Image 모델의 맹점을 이렇게 잡습니다. 모델은 open-ended prompt를 받아 고품질 이미지를 만들 수 있지만, 대부분의 시스템은 모든 사용자를 같은 사람처럼 취급합니다.

예를 들어 두 사람이 같은 프롬프트를 넣습니다.

> glass house in a forest

한 사람은 차갑고 미니멀한 건축 사진을 원할 수 있고, 다른 사람은 이끼 낀 숲속 오두막 같은 따뜻한 이미지를 원할 수 있습니다. 프롬프트는 같지만 원하는 결과는 다릅니다.

![](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-1-prompt-steering.png)

Figure 1은 이 차이를 바로 보여줍니다. 기존 reward model은 global reward, 즉 전체 사용자 평균 선호로 이미지를 밀어 올립니다. 이 논문은 같은 프롬프트라도 <span style="background-color: #fff59d"><strong>개별 사용자 취향에 맞춰 서로 다른 방향으로 prompt optimization</strong></span>을 할 수 있다고 봅니다.

여기서 중요한 구분이 있습니다. DreamBooth나 Textual Inversion 같은 기존 개인화는 주로 “무엇을 그릴 것인가”의 개인화였습니다. 내 강아지, 내 얼굴, 특정 오브젝트를 잘 그리게 하는 쪽입니다.

이 논문이 다루는 건 다릅니다. <span style="background-color: #fff59d"><strong>이미지에 무엇이 들어가느냐와 함께, 이미지가 어떻게 보이고 느껴지고 구성되느냐</strong></span>를 봅니다. 디자인 취향에 더 가깝습니다.

## PAMELA: 5천 장 이미지에 7만 개 취향 점수

논문은 PAM∃LA, 읽기 편하게 PAMELA라고 부르는 데이터셋과 predictor를 제안합니다.

구성은 이렇습니다.

- <span style="background-color: #fff59d"><strong>5,077개 이미지</strong></span>
- 약 <span style="background-color: #fff59d"><strong>70,000개 사용자 rating</strong></span>
- <span style="background-color: #fff59d"><strong>205명 사용자</strong></span>
- 이미지당 <span style="background-color: #fff59d"><strong>15명 평가</strong></span>
- 생성 모델은 Flux 2와 Nano Banana
- 도메인은 art, fashion, graphic design, cinematic photography 등

![](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-2-pamela-domains.png)

Figure 2는 데이터셋의 범위를 보여줍니다. 단순히 “사진이 선명한가”를 묻는 데이터가 아닙니다. 예술, 패션, 그래픽 디자인, 시네마틱 사진처럼 취향 차이가 크게 드러나는 영역을 의도적으로 넣었습니다.

기존 데이터셋과 비교하면 포인트가 선명합니다. Pick-a-Pic은 규모가 크지만 사용자별 dense rating을 목적으로 만든 데이터는 아닙니다. ImageRewardDB도 전문가 pairwise preference 중심입니다. PAMELA는 <span style="background-color: #fff59d"><strong>AI-generated image, subjective visual domain, multi-rater coverage, user-level label을 함께 갖춘 데이터셋</strong></span>을 목표로 합니다.

## predictor는 이미지와 프롬프트만 보지 않는다

모델 구조도 흥미롭습니다.

![](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-3-predictor-architecture.png)

PAMELA predictor는 이미지와 프롬프트만 보는 모델이 아닙니다. frozen SigLIP2 encoder로 image/text feature를 뽑고, 사용자 demographic 정보와 이미지 metadata를 함께 넣습니다. 그 뒤 shallow transformer encoder가 이 정보를 합쳐서 해당 사용자의 aesthetic score를 예측합니다.

즉 질문이 바뀝니다.

“이 이미지는 좋은가?”가 아닙니다.

<span style="background-color: #fff59d"><strong>“이 사용자가 이 이미지를 좋아할까?”</strong></span>입니다.

이 차이가 큽니다. 실무에서는 “고품질 이미지”와 “우리 브랜드/내 채널/내 강의 썸네일에 맞는 이미지”는 자주 다릅니다. 평균 취향 reward는 그 차이를 잘 못 봅니다.

## 성능: HPSv3보다 개인 선호 예측이 좋아졌다

논문은 held-out user test set에서 PAMELA predictor를 기존 보상 모델들과 비교합니다.

Table 2의 핵심 수치만 보면 이렇습니다.

| Reward Model | User SROCC | User PLCC | User pairwise acc |
| --- | ---: | ---: | ---: |
| LAION Aesthetics | 0.1516 | 0.1471 | 0.5110 |
| ImageReward | 0.2841 | 0.2855 | 0.5978 |
| Q-Align Aesthetics | 0.2677 | 0.2906 | 0.5932 |
| HPSv3 | 0.4019 | 0.4444 | 0.6427 |
| PAMELA | <span style="background-color: #fff59d"><strong>0.4514</strong></span> | <span style="background-color: #fff59d"><strong>0.4722</strong></span> | <span style="background-color: #fff59d"><strong>0.6631</strong></span> |

숫자 점프의 크기보다 방향이 중요합니다. 기존 reward model이 “대중 평균 선호”를 잘 맞추는 동안, PAMELA는 사용자 단위 ranking과 pairwise accuracy에서 더 잘 맞췄습니다.

또 하나 봐야 할 점은 평균 성능도 포기하지 않았다는 겁니다. Avg PLCC 0.6116, Avg pairwise accuracy 0.6798로 population-level metric에서도 HPSv3보다 조금 높습니다. 논문은 이 결과를 단순한 trade-off로 보지 않습니다. <span style="background-color: #fff59d"><strong>개인 선호를 명시적으로 모델링해도 전체 품질 평가를 유지할 수 있다</strong></span>는 쪽입니다.

## 프롬프트 최적화가 개인 취향 쪽으로 휘어진다

이 논문이 블로그감인 이유는 여기 있습니다. predictor를 평가만 하는 데서 끝내지 않고, 이미지 생성 steering에 씁니다.

방법은 단순합니다.

1. LLaMA-3.1-8B-Instruct가 프롬프트 변형 20개를 만듭니다.
2. FLUX.2-dev로 각 후보 이미지를 생성합니다.
3. reward model이 점수를 매깁니다.
4. 가장 높은 후보를 다음 iteration의 context로 넘깁니다.

이 과정을 HPSv3, Q-Align, PAMELA로 비교합니다.

![](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-5-user-specific-steering.png)

Figure 5의 메시지는 단순합니다. 기존 global reward model은 특정 방향으로 이미지를 밀어 올리지만, PAMELA는 사용자별로 다른 결과를 만듭니다. 논문 표현대로라면, <span style="background-color: #fff59d"><strong>동일한 prompt optimization이라도 reward가 개인화되면 결과 이미지의 방향이 달라집니다</strong></span>.

이건 프롬프트 팁의 문제가 아닙니다. 프롬프트는 여전히 필요다만, 최적화의 기준이 달라집니다.

## 유저 스터디: 자기 취향으로 최적화한 이미지를 더 골랐다

논문은 user study도 붙였습니다. Mabyduck에서 <span style="background-color: #fff59d"><strong>15,300개 rating, 7,650개 pairwise comparison</strong></span>을 수집했고, 6명의 사용자와 18개 prompt를 대상으로 비교했습니다.

비교 대상은 대략 네 가지입니다.

- 최적화하지 않은 기본 이미지
- HPSv3로 최적화한 이미지
- Q-Align으로 최적화한 이미지
- PAMELA로 특정 사용자에게 맞춰 최적화한 이미지

결론은 논문 제목 그대로입니다. Elo/BT score 기준으로 PAMELA self-optimized가 1065, PAMELA other-optimized가 1038, unoptimized baseline이 1016, HPSv3가 959, Q-Align이 922였습니다. <span style="background-color: #fff59d"><strong>사용자는 자기 취향에 맞춰 최적화한 이미지를 가장 많이 골랐고, 다른 사람에게 맞춘 이미지보다 자기에게 맞춘 이미지를 더 선호했습니다</strong></span>.

이 부분이 중요합니다. 개인화 reward가 단순히 metric을 올린 게 아니라, 실제 사용자의 선택에서도 확인됐다는 뜻입니다.

## 실무에서는 프롬프트 모음과 선택 기록을 같이 봐야 한다

콘텐츠 제작자 입장에서 보면 이 흐름은 꽤 실용적입니다.

지금은 보통 이렇게 일합니다.

- 좋은 프롬프트 템플릿을 모은다
- 마음에 드는 작가명, 렌즈, 조명, 스타일 키워드를 저장한다
- 생성한 이미지 중 괜찮은 걸 고른다
- 다음번에 다시 비슷한 프롬프트를 쓴다

근데 이 논문식으로 보면 더 중요한 자산은 따로 있습니다.

<span style="background-color: #fff59d"><strong>내가 고른 이미지와 버린 이미지의 기록</strong></span>입니다.

블로그 히어로 이미지, 강의 썸네일, 브랜드 카드뉴스, 제품 목업을 계속 만들다 보면 선택 로그가 쌓입니다. 그 선택 로그는 “나는 어떤 색감, 구도, 밀도, 질감, 분위기를 선호하는가”를 알려줍니다.

앞으로 이미지 모델 UX는 “프롬프트를 더 자세히 써주세요”에서 “이 중 어떤 게 더 마음에 드나요?”로 이동할 가능성이 큽니다. 프롬프트는 명령이고, 선택은 취향 데이터입니다.

## 한계도 분명하다

좋은 방향이지만 바로 제품화하면 조심해야 할 부분도 있습니다.

먼저, 사용자 demographic 정보를 쓰는 방식은 민감합니다. 취향 예측에 도움이 될 수 있지만, 실제 서비스에서는 동의, 저장, 설명 가능성, 편향 문제가 따라옵니다.

다음으로, 205명과 7만 rating은 연구용으로 의미 있지만, 모든 문화권과 디자인 맥락을 대표한다고 보기는 어렵습니다.

또 취향을 맞추는 모델은 사용자를 더 좁은 스타일 안에 가둘 수도 있습니다. 계속 좋아하던 것만 추천하면 새로운 취향을 발견하기 어렵습니다.

그래서 이 논문은 “이제 모든 이미지 모델이 개인 취향을 완벽히 안다”는 주장과 거리가 있습니다. 오히려 <span style="background-color: #fff59d"><strong>이미지 생성의 다음 평가 단위가 평균 품질에서 사용자별 만족으로 이동하고 있다</strong></span>는 신호에 가깝습니다.

## 저는 이렇게 봅니다

이 논문은 이미지 프롬프팅의 끝을 말하지 않습니다. 프롬프트가 여전히 중요합니다. 다만 프롬프트만으로는 부족한 영역이 보인다는 겁니다.

사람은 자기가 뭘 좋아하는지 항상 말로 설명하지 못합니다. 근데 고를 수는 있습니다. 이 이미지가 더 좋다, 저 색감은 별로다, 이 구도는 우리 채널과 안 맞는다. 이런 선택이 쌓이면 프롬프트보다 더 정직한 취향 데이터가 됩니다.

그래서 다음 이미지 생성 워크플로는 이렇게 바뀔 수 있습니다.

<span style="background-color: #fff59d"><strong>프롬프트를 잘 쓰는 역량과 자신의 선택 데이터를 잘 쌓는 습관이 함께 갈 때 더 일관된 이미지</strong></span>를 만들 가능성이 있습니다.

블로그 히어로 이미지 하나를 고를 때도 그냥 “괜찮네”로 끝내지 말고, 왜 골랐는지, 왜 버렸는지를 남겨두면 좋겠습니다. 그게 나중에는 개인 취향 reward model의 학습 데이터가 될 수 있습니다.

## 더 실습해보고 싶은 분들께

이미지 생성과 취향 프로필도 결국 반복 실행, 평가, 수정 루프가 핵심입니다. 이런 자동화 흐름을 직접 다뤄보고 싶은 분들은 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』와 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」를 참고하셔도 좋습니다.
