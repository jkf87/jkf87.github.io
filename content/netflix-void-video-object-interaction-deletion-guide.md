---
title: "Netflix VOID란 무엇인가: 영상에서 물체뿐 아니라 상호작용까지 지우는 비디오 편집 모델"
date: 2026-04-07
tags:
  - netflix
  - void
  - video editing
  - video inpainting
  - ai video
  - computer vision
  - huggingface
  - diffusion
description: "Netflix가 공개한 VOID 모델은 영상 속 물체만 지우는 것이 아니라, 그 물체가 장면에 남긴 상호작용까지 함께 제거하는 비디오 편집 모델이다. 무엇이 새로운지, 어떻게 동작하는지, 실제 실행 조건은 어떤지 정리했다."
---

# Netflix VOID란 무엇인가: 영상에서 물체뿐 아니라 상호작용까지 지우는 비디오 편집 모델

Netflix가 Hugging Face에 공개한 **VOID(Video Object and Interaction Deletion)** 는 이름 그대로 영상에서 특정 객체를 지우는 모델이다. 그런데 여기서 중요한 건 단순한 **object removal**이 아니라는 점이다.

이 모델이 노리는 건 훨씬 더 어렵다.

> **장면 속 물체를 지우는 것뿐 아니라, 그 물체가 주변 장면에 만든 상호작용까지 함께 지우는 것**

예를 들면 이런 상황이다.

- 사람을 영상에서 지운다
- 그런데 그 사람이 가려서 생긴 그림자만 지우는 게 아니다
- 사람이 건드려서 떨어진 물체, 밀린 물건, 주변 변화까지 같이 복원하려고 한다

즉, VOID는 “영상에서 물체 하나를 지운다”가 아니라,
**“그 물체가 존재하지 않았던 세계선을 다시 만들어낸다”**에 더 가깝다.

## 뭐가 새롭나

일반적인 영상 object removal이나 inpainting는 보통 두 단계에서 한계가 드러난다.

1. **보이는 대상은 지웠다**
2. 그런데 **장면의 물리적 흔적은 그대로 남는다**

예를 들어,
- 테이블 위 컵을 지웠는데 컵이 남긴 가림 정보가 어색하거나
- 사람을 지웠는데 주변 물체의 움직임은 그대로 남거나
- 반사, 그림자, 위치 변화가 이상하게 남는 경우가 많다

VOID는 여기서 한 단계 더 간다.

모델 카드에 따르면 VOID는
- secondary effects, 즉 **그림자와 반사**뿐 아니라
- **physical interactions**, 즉 사람이 사라졌을 때 같이 떨어져야 하는 물체나 움직임 변화까지
같이 처리하는 걸 목표로 한다.

이 포인트가 중요하다.

> 기존 모델이 “픽셀을 메운다”에 가깝다면,
> VOID는 “장면의 인과를 다시 맞춘다”에 가깝다.

## 어떻게 동작하나

모델 카드 기준으로 VOID는 다음 구조를 사용한다.

- 기반 모델: **CogVideoX-Fun-V1.5-5b-InP**
- 방식: 비디오 inpainting 특화 파인튜닝
- 핵심 입력: **quadmask conditioning**

여기서 quadmask가 핵심이다.

### quadmask가 뭔가
일반적인 마스크가 “여기를 지워라” 정도라면,
VOID는 4가지 영역을 나눠서 본다.

- **remove**: 직접 제거할 객체
- **overlap**: 객체와 겹치는 영역
- **affected**: 객체 제거로 인해 영향을 받는 영역
- **keep**: 유지할 배경

모델 카드 설명대로라면 이 값은 보통 이렇게 인코딩된다.

- `0` = remove
- `63` = overlap
- `127` = affected
- `255` = keep

이 설계가 중요한 이유는,
모델이 단순히 “사람을 지워라”만 받는 게 아니라,
**“사람이 없어졌을 때 어디까지 같이 바뀌어야 하는지”**를 더 구조적으로 전달받기 때문이다.

## 입력 형식은 어떻게 되나

기본 입력은 폴더 하나에 파일 3개다.

```text
my-video/
  input_video.mp4
  quadmask_0.mp4
  prompt.json
```

각각 의미는 다음과 같다.

- `input_video.mp4`: 원본 영상
- `quadmask_0.mp4`: 4값 마스크 영상
- `prompt.json`: 제거 후 장면을 설명하는 텍스트

즉, 이 모델은 완전 자동 편집 도구라기보다,
**장면 설명 + 구조화된 마스크 + 원본 영상**을 함께 받는 연구형/실전형 모델에 가깝다.

## 실제로 실행하려면 어떤가

여기서부터가 중요하다. 이 모델은 “재밌는 데모” 수준으로 보이면 안 된다. **요구사항이 높다.**

모델 카드 기준 빠른 시작은 두 가지다.

### 1. 노트북 방식
- 제공된 `notebook.ipynb` 실행
- 샘플 영상으로 추론 가능

하지만 조건이 붙는다.

> **GPU 40GB+ VRAM 필요 (예: A100)**

즉, 이건 현재 기준으로
- 맥북에서 가볍게 돌려보는 로컬 장난감 모델은 아니고
- **연구용 또는 고사양 GPU 환경용 모델**이다.

### 2. CLI 방식
모델 카드에 나온 예시는 대략 이런 흐름이다.

```bash
pip install -r requirements.txt

huggingface-cli download alibaba-pai/CogVideoX-Fun-V1.5-5b-InP \
  --local-dir ./CogVideoX-Fun-V1.5-5b-InP

huggingface-cli download netflix/void-model \
  --local-dir .

python inference/cogvideox_fun/predict_v2v.py \
  --config config/quadmask_cogvideox.py \
  --config.data.data_rootdir="./sample" \
  --config.experiment.run_seqs="lime" \
  --config.experiment.save_path="./outputs" \
  --config.video_model.transformer_path="./void_pass1.safetensors"
```

즉, 실제로는
- 베이스 모델 다운로드
- VOID 체크포인트 다운로드
- 샘플 비디오 데이터 구조 맞추기
- 추론 스크립트 실행
순서다.

## 체크포인트는 두 개다
모델 카드에는 체크포인트가 두 종류로 나온다.

### `void_pass1.safetensors`
- 기본 inpainting 모델
- 대부분의 영상에서 필수

### `void_pass2.safetensors`
- warped-noise refinement
- 긴 영상에서 temporal consistency 개선용
- 선택적

즉,
- **Pass 1만으로도 대부분 실행 가능**
- **Pass 2는 시간축 일관성을 더 보강하는 추가 단계**
로 이해하면 된다.

## 어떤 데이터로 학습했나
학습 데이터도 흥미롭다.

모델 카드 기준으로 VOID는 paired counterfactual video를 사용했다.
주요 출처는 두 가지다.

- **HUMOTO**: 사람-객체 상호작용을 Blender 물리 시뮬레이션으로 렌더링
- **Kubric**: 객체 중심 상호작용 데이터

이 조합은 모델의 성격을 잘 보여준다.

이 모델은 단순 배경 메우기가 아니라,
**“객체 제거 후 장면이 어떻게 바뀌어야 자연스러운가”**를 학습한 쪽이다.

## 이 모델이 주는 시사점
이 모델이 흥미로운 이유는 단지 Netflix가 공개해서가 아니다.

핵심은 AI 영상 편집이 이제
- 컷 편집,
- 스타일 변환,
- 단순 inpainting
단계를 넘어,

**장면의 원인과 결과까지 복원하려는 방향**으로 가고 있다는 점이다.

예전에는 “지운다”가 목표였다면,
지금은 “없었던 것처럼 만든다”가 목표가 된다.

이 차이는 꽤 크다.

왜냐하면 실제 영상 편집에서 사람을 속이는 건 픽셀 자체보다,
**장면의 물리적 일관성**이기 때문이다.

## 실무 관점에서 보면
현실적으로 지금 당장 모든 크리에이터가 쓸 수 있는 모델은 아니다.

이유:
- 40GB+ VRAM 요구
- 마스크 생성 파이프라인 필요
- 연구형 입력 구조
- 일반 사용자용 앱보다는 엔지니어링 성격이 강함

그래도 이 모델이 의미 있는 건,
곧바로 상용 워크플로우에 들어가서라기보다
**앞으로의 AI 비디오 편집이 어디로 가는지 보여주는 샘플**이기 때문이다.

특히 이런 분야에 관심 있는 사람은 꼭 볼 만하다.

- 비디오 인페인팅
- 객체 제거
- 생성형 영상 편집
- 멀티모달 비전 모델
- 물리 상호작용 기반 장면 편집

## 한 줄 정리

> **VOID는 “영상에서 물체를 지우는 모델”이 아니라, 그 물체가 장면에 남긴 상호작용까지 함께 지워서 더 자연스러운 세계를 복원하려는 모델이다.**

이게 이 모델의 본질이다.

## 지금 확인해볼 링크

- 모델 카드: <https://huggingface.co/netflix/void-model>
- 프로젝트 페이지: <https://void-model.github.io/>
- 논문: <https://arxiv.org/pdf/2604.02296>
- GitHub: <https://github.com/netflix/void-model>
- 데모: <https://huggingface.co/spaces/sam-motamed/VOID>

## 마무리

요즘 생성형 AI 영상 모델은 점점 더 “그럴듯한 프레임 생성”에서 벗어나,
**장면의 구조와 인과를 이해하는 쪽**으로 가고 있다.

VOID는 그 변화가 꽤 선명하게 보이는 사례다.

당장 가볍게 돌리기엔 무겁지만,
“앞으로 영상 편집 모델이 어디까지 갈 수 있는가”를 보고 싶다면 한 번쯤 꼭 읽어볼 만한 공개다.
