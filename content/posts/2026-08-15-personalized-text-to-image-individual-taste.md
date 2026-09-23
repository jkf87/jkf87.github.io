---
title: "평균적으로 좋은 이미지와 내가 좋아하는 이미지는 다름 — 개인 취향 보상 모델 PAMELA"
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
description: "ImageReward, PickScore 같은 보상 모델은 전체 사용자 평균 선호를 맞춤. PAMELA는 사용자 단위 취향 예측으로 방향을 틀고, 실제 사용자가 자기 취향으로 최적화한 이미지를 더 골랐음. 선택 로그가 취향 데이터가 되는 워크플로 전환을 정리함."
draft: true
refactor_hub: agent-rl-01
refactor_status: queued
---

이미지 생성 모델의 다음 경쟁 지점이 프롬프트 충실도에서 개인 미감으로 옮겨가고 있음. ImageReward, PickScore, HPS 같은 보상 모델은 "대체로 사람들이 더 좋아하는 이미지"를 맞추는 쪽이었음. 근데 평균적으로 좋은 이미지와 내가 좋아하는 이미지는 다를 수 있음. 같은 "glass house in a forest" 프롬프트를 넣어도 한 사람은 차갑고 미니멀한 건축 사진을, 다른 사람은 이끼 낀 숲속 오두막을 원함. 이 논문은 그 차이를 모델링함.

1. 문제 정의가 정확함. 기존 개인화 연구는 DreamBooth나 Textual Inversion처럼 "무엇을 그릴 것인가"의 개인화였음. 내 강아지, 내 얼굴, 특정 오브젝트를 잘 그리게 하는 것. 이 논문이 다루는 건 이미지가 어떻게 보이고 느껴지고 구성되느냐, 그러니까 디자인 취향 자체임. 기존 reward model은 global reward, 즉 전체 사용자 평균 선호로 이미지를 밀어 올리는데, 이 논문은 같은 프롬프트라도 개별 사용자 취향에 맞춰 서로 다른 방향으로 prompt optimization을 할 수 있다고 봄.

![프롬프트 스티어링 비교](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-1-prompt-steering.png)

2. 데이터셋 구성이 목적에 맞음. PAMELA는 5,077개 이미지에 약 7만 개 사용자 rating, 205명 사용자, 이미지당 15명 평가. 생성 모델은 Flux 2와 Nano Banana. 도메인은 art, fashion, graphic design, cinematic photography처럼 취향 차이가 크게 드러나는 영역을 의도적으로 넣었음. Pick-a-Pic은 규모가 크지만 사용자별 dense rating이 아니고 ImageRewardDB는 전문가 pairwise 중심. AI 생성 이미지, 주관적 비주얼 도메인, 다중 평가자 커버리지, 사용자 단위 라벨을 함께 갖춘 데이터셋이 목표였던 것.

![데이터셋 도메인](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-2-pamela-domains.png)

3. predictor 설계에서 질문이 바뀜. frozen SigLIP2 encoder(이미지와 텍스트를 같은 임베딩 공간으로 묶어주는 사전학습 인코더)로 이미지와 텍스트 feature를 뽑고, 사용자 demographic 정보와 이미지 메타데이터를 함께 넣어 shallow transformer로 해당 사용자의 미감 점수를 예측함. "이 이미지는 좋은가"가 아니라 "이 사용자가 이 이미지를 좋아할까"를 묻는 것. 실무에서 고품질 이미지와 우리 브랜드에 맞는 이미지는 자주 다르다는 걸 아는 사람이라면 이 차이의 가치를 바로 알 것임.

![predictor 구조](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-3-predictor-architecture.png)

4. 성능. held-out 사용자 테스트에서 PAMELA가 User SROCC 0.4514, PLCC 0.4722, pairwise accuracy 0.6631로(각각 순위 상관, 선형 상관, 두 이미지 중 어느 쪽을 선호할지 맞힌 비율을 재는 지표임) HPSv3(0.4019/0.4444/0.6427)보다 앞섬. 점프의 크기보다 방향이 중요함. 개인 단위 랭킹 예측에서 더 잘 맞췄다는 것. 그리고 population-level 지표에서도 HPSv3보다 조금 높아서 개인 선호를 명시적으로 모델링해도 전체 품질 평가를 유지할 수 있음. 트레이드오프가 필수가 아니라는 점이 실용적임.

5. 프롬프트 최적화로 이어지는 부분이 이 논문의 실무적 핵심임. LLM이 프롬프트 변형 20개를 만들고, FLUX.2-dev로 후보 이미지를 생성하고, reward model이 점수를 매기고, 최고 후보를 다음 반복의 컨텍스트로 넘기는 루프. 이 과정을 HPSv3, Q-Align(사람 선호 기준으로 이미지 품질을 점수 매기는 보상 모델), PAMELA로 각각 돌리니 global reward는 특정 방향으로 이미지를 밀어 올리는 반면 PAMELA는 사용자별로 다른 결과를 만듦. 프롬프트 팁의 문제가 아니라 최적화의 기준이 달라지는 것.

![사용자별 스티어링 결과](/images/2026-08-15-personalized-text-to-image-individual-taste/fig-5-user-specific-steering.png)

6. user study가 신뢰를 줌. 15,300개 rating, 7,650개 pairwise 비교에서 Elo(승패 기록으로 상대 선호 강도를 점수화하는 순위 산출 방식) 기준 PAMELA self-optimized 1065, other-optimized 1038, 무최적화 1016, HPSv3 959, Q-Align 922. 사용자가 자기 취향으로 최적화한 이미지를 가장 많이 골랐고 남의 취향으로 맞춘 것보다 자기 것을 더 선호함. 지표 개선이 아니라 실제 선택에서 확인됐다는 것.

7. 내 콘텐츠 제작 워크플로 결론은 이렇게임. 지금은 좋은 프롬프트 템플릿을 모으고 스타일 키워드를 저장하고 괜찮은 걸 골라서 다시 쓰는 방식으로 일함. 근데 더 중요한 자산은 따로 있음. 내가 고른 이미지와 버린 이미지의 기록. 블로그 히어로 이미지, 썸네일, 카드뉴스를 계속 만들면 선택 로그가 쌓이는데 그게 "나는 어떤 색감, 구도, 질감, 분위기를 선호하는가"의 데이터가 됨. 프롬프트는 명령이고 선택은 취향 데이터라는 구분이 앞으로의 UX를 결정할 것. "프롬프트를 더 자세히 써주세요"에서 "이 중 어떤 게 더 마음에 드나요"로 이동할 가능성이 큼. 한계도 분명함. demographic 정보 활용은 동의·설명 가능성·편향 문제가 따라오고 205명이 모든 문화권을 대표하진 못 함. 그리고 좋아하던 것만 계속 추천하면 취향의 필터 버블이 생길 수 있음. 그래도 평가 단위가 평균 품질에서 사용자별 만족으로 이동 중이라는 신호는 분명함.

원문: [arXiv:2604.07427](https://arxiv.org/abs/2604.07427).
