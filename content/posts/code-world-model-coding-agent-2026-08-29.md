---
title: "코드 월드 모델 — 코딩 에이전트를 월드 브레인으로 쓰는 방식"
date: 2026-08-29
tags: [paper-review, world-model, coding-agent, video-model]
draft: false
description: "웨스트레이크 AGI Lab과 NTU의 Code World Model(arXiv 2608.25927) 정리. 코딩 에이전트가 코드로 월드 상태를 갱신하고, 프록시 비디오를 통해 MiniMax-H3가 시각을 렌더링하는 구조를 다룹니다."
---

세상에 상호작용하는 게임 월드를 통째로 생성하는 모델들이 요즘 쏟아지고 있는데, 다들 비슷한 벽에 부딪힙니다. 화면은 그럴듯한데, 세계의 규칙이 안 지켜진다는 거죠. 이번에 볼 논문은 이 문제에 꽤 색다른 답을 내놨습니다.

## 결론 먼저

Code World Model(arXiv 2608.25927)의 핵심 아이디어는 단순합니다. <span style="background-color: #fff59d"><strong>세계의 진화는 코딩 에이전트가 코드로 관리하고, 화면 구현은 비디오 모델이 맡는</strong></span> 거예요. 이 논문은 이 코딩 에이전트를 "월드 브레인"이라고 부릅니다.

왜 이런 구조가 나왐을까요? 비디오 월드 모델은 화면만 보고 배우니까 <span style="background-color: #fff59d"><strong>결과는 알지만 규칙을 모릅니다</strong></span>. 예를 들어 플레이어가 도시 통치자를 암살하면, 질서와 파벌 동맹과 NPC 행동이 모두 바뀌어야 하는데 이런 건 화면 데이터에 제대로 남지 않아요. 심지어 <span style="background-color: #fff59d"><strong>플레이어가 없는 화면 밖에서 벌어지는 일은 시각 기록 자체가 없죠</strong></span>.

## 핵심 구조 요약

| 항목 | 내용 |
|---|---|
| 논문 | Code World Model: Coding Agent as World Brain (arXiv 2608.25927) |
| 소속 | 웨스트레이크대 AGI Lab, NTU |
| 저자 | Yiwen Chen, Guosheng Lin, Chi Zhang (3인) |
| 핵심 제안 | 코딩 에이전트 = 월드 브레인, 프록시 비디오 = 상태-화면 인터페이스 |
| 비디오 모델 | MiniMax-H3 파인튜닝 |
| 학습 데이터 | GTA V 게임플레이 <span style="background-color: #fff59d"><strong>5시간</strong></span> + 실영상 3D 재구성 기반 쌍 데이터 |
| 프로젝트 페이지 | https://buaacyw.github.io/cwm/ |

## 파이프라인

![파이프라인](/images/code-world-model-coding-agent-2026-08-29/fig2-pipeline.png)

Fig. 2 출처: arXiv 2608.25927

흐름을 보면 이해가 빠릅니다. 사용자 입력 → 코딩 에이전트의 추론과 코드 실행 → 월드 상태 갱신 → 프록시 컴파일 → 비디오 모델이 화면 생성 → 다시 피드백.

재미있는 건 역할 분리예요. 코딩 에이전트는 "드물지만 복잡한" 결정만 합니다. 새 사건 해석, 장기 결과 추론, 세계 작동 방식 수정 같은 것들이요. 반복적인 실행(위치, 속성, 쿨다운, 충돌)은 코드에 맡깁니다. 그리고 비디오 모델은 오직 외관과 미세 동작만 책임집니다.

## 프록시라는 똑똑한 인터페이스

그럼 갱신된 상태를 어떻게 비디오 모델에 전달할까요? 텍스트로 하면 안 되더라고요. <span style="background-color: #fff59d"><strong>아무리 긴 텍스트와 전용 카메라 조건을 줘도 카메라 궤적과 개체 움직임이 정밀하게 제어되지 않았습니다</strong></span>.

그래서 나온 게 프록시입니다. <span style="background-color: #fff59d"><strong>프레임 단위 공간·시간 제약을 아예 이미지 좌표로 직접 표현하는 조건</strong></span>이에요. 논문의 표현을 빌리면 "텍스트 프롬프트의 시각적 대응물"입니다. 해상도는 <span style="background-color: #fff59d"><strong>타깃의 1/4이라 토큰 부담도 1/16 수준</strong></span>입니다.

## 데이터는 어떻게 만들었나

![쌍 데이터 구성](/images/code-world-model-coding-agent-2026-08-29/fig3-paired-data.png)

Fig. 3 출처: arXiv 2608.25927

게임 데이터는 런타임 주석을 코드가 읽어서 <span style="background-color: #fff59d"><strong>픽셀 단위 프록시 주석을 자동 생성</strong></span>합니다. 실영상은 <span style="background-color: #fff59d"><strong>캘리브레이션된 3D 재구성으로 오프라인 컴파일</strong></span>하는데, <span style="background-color: #fff59d"><strong>액션 라벨이 필요 없어요</strong></span>. 주석 비용이 확 줄어드는 지점입니다.

## 결과

![시각 품질 결과](/images/code-world-model-coding-agent-2026-08-29/fig4-visual-quality.png)

Fig. 4 출처: arXiv 2608.25927

놀라운 건 <span style="background-color: #fff59d"><strong>GTA V 게임플레이 5시간만으로 파인튜닝했다는 점</strong></span>입니다. 그런데도 <span style="background-color: #fff59d"><strong>전혀 다른 캐릭터, 환경, 모션, 카메라 궤적으로 강하게 일반화</strong></span>됩니다. <span style="background-color: #fff59d"><strong>60초마다 스타일이 바뀌는 장기 생성 데모</strong></span>도 세계 상태가 코드로 유지되니 가능해집니다.

## 내 해석

명시적 3D 월드 생성 루트의 고질적 문제가 에셋 커버리지의 천장이었다는 걸 생각하면, 이 접근은 방향이 다릅니다. 비디오 모델의 사전지식이 커질수록 같이 스케일업되는 구조라서요.

다만 <span style="background-color: #fff59d"><strong>평가가 정성 중심이라는 건 기억해야 합니다</strong></span>. 코딩 에이전트가 임의의 복잡한 세계를 처음부터 구축하는 건 논문 스스로 "기대"라고 쓴 부분이고요. <span style="background-color: #fff59d"><strong>오픈엔디드 세계는 아직 데모 단계</strong></span>입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 코드 월드 모델에서 코딩 에이전트의 역할은 뭔가요?

월드 브레인 역할입니다. 사건을 추론하고 실행 가능한 코드로 월드 상태를 갱신합니다.

### 프록시 비디오는 왜 필요한가요?

텍스트 조건만으로 카메라 궤적과 개체 위치의 정밀 제어가 안 되기 때문입니다. 프록시는 프레임 단위 제약을 이미지 좌표로 직접 전달합니다.

### 학습 데이터가 정말 5시간인가요?

GTA V 게임플레이 약 5시간으로 MiniMax-H3를 파인튜닝했고 다양한 도메인으로 일반화됐다고 보고했습니다.

### 비디오 월드 모델 대비 장점은 뭔가요?

화면 데이터는 결과만 보여주지만 코드는 규칙과 지식을 직접 다룹니다. 화면 밖 상태와 장기 결과 전파를 커버합니다.
