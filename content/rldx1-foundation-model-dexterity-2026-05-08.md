---
title: "한국 스타트업 RLWRLD, 5센서 로봇 손 전용 파운데이션 모델 RLDX-1 공개"
date: 2026-05-08
tags:
  - robotics
  - AI
  - foundation-model
  - korea-startup
  - dexterity
draft: false
---

**2026년 5월 7일**, 한국 로보틱스 스타트업 RLWRLD(리얼월드)가 로봇 손을 위한 파운데이션 모델 **RLDX-1**을 발표했다. 기존 VLA(Vision-Language-Action) 모델들이 시각과 언어만 처리하던 것과 달리, RLDX-1은 **토크, 촉각, 작업 메모리까지 하나의 모델에서 처리**하는 것이 핵심 차별점이다.

## 왜 "Dexterity-First"인가

LLM의 성공 공식 — 모델을 키우고 데이터를 많이 넣으면 새 능력이 나타난다 — 을 로보틱스에 그대로 적용하려는 시도가 많았다. 하지만 RLWRLD가 실제 고객 과제(커피 따르기, 손안에서 물체 회전, 반응형 잡기)에 기존 VLA를 배포해보니 일관되게 실패했다. 원인은 지능 부족이 아니라 **모델이 애초에 받지 않은 모달리티**(고자유도 손-물체 기하학, 접촉력, 시간 역학)에 있었다.

> "Scale cannot recover a modality the model was never given in the first place."

이 문제 인식에서 출발해 RLDX-1은 "손 재주(Dexterity)"를 최우선으로 설계됐다.

## 5가지 정밀도 영역과 DexBench

RLWRLD는 고객이 실제 겪는 로봇 실패를 **DexBench**라는 벤치마크로 정리하고, 각 실패 유형이 모델의 특정 모듈을 형성하도록 설계했다.

| 영역 | 문제 | RLDX-1의 해법 |
|------|------|---------------|
| **Grasp Diversity** | 5손가락 손 전제 | 합성 로봇 데이터 + 인간 손 데이터 |
| **Spatial Precision** | 접촉 전 기하학적 추론 | 로봇 특화 VLM (Qwen3-VL 8B 파인튜닝) |
| **Temporal Precision** | 움직이는 물체 대응 | Motion Module (시공간 시각 특징) |
| **Contact Precision** | 접촉/무게 감지 | Physics Module (토크 + 촉각 스트림) |
| **Context Awareness** | 다단계 작업 기억 | Memory Module + DAgger + Progress-Aware RL |

## 아키텍처: MSAT (Multi-Stream Action Transformer)

핵심은 **MSAT** 구조다. 기존 VLA들이 단일 트랜스포머 스트림에서 모든 모달리티를 융합하면, gradient를 지배하는 모달리티가 용량을 독차지한다. MSAT는 각 모달리티에 **독립 스트림**을 부여하고, 후반 블록에서 joint self-attention으로 융합한다.

주요 모듈:

- **Robot-Specialized VLM**: Qwen3-VL 8B를 로봇 궤적 VQA로 파인튜닝. 공간 추론·작업 이해·액션 그라운딩 강화. RoboCasa에서 +3.42%p
- **Motion Module**: 다프레임 관측을 motion token으로 압축. 컨베이어 벨트 pick-and-place에서 GR00T N1.6, π₀.₅ 대비 +37.5%p
- **Physics Module**: 토크·촉각을 전용 스트림으로 처리. 센서 없으면 자동 비활성화(우아한 성능 저하)
- **Cognition Interface**: 64개 학습 가능한 cognition token으로 VLM 출력 압축. 추론 속도 35% 향상 (16.3→22.1 Hz). 동일 토큰이 장기 메모리의 단위로 재사용됨

## 데이터: 합성 + 인간

실제 텔레오퍼레이션만으로는 5손가락 손이 커버해야 할 공간을 채울 수 없다.

**합성 로봇 데이터**: Cosmos-Predict2 같은 비디오 생성 모델로 소규모 실제 데모를 ~5배 증강. 역동역학 모델로 액션 라벨 자동 생성 후 품질 필터링. GR-1 Tabletop에서 9.2% 성능 향상.

**인간 데이터**: 맨손 그대로 촬영하고 소프트웨어에서 운동학적 차이를 보정하는 접근. 시간당 200+ 데모 생산. 파이프라인: 손 추적 → 3D Gaussian Splatting으로 워크스페이스 재구성 → 로봇 손으로 리타겟 → 시뮬레이션에서 롤아웃.

## 성능

RLDX-1은 8개 오픈 벤치마크에서 기존 최고 모델들을 능가했다:

- **RoboCasa Kitchen**: 70.6점 — VLA 모델 최초 70점 돌파
- **GR-1 Tabletop**: 58.7점 — GR00T N1.6 대비 +10.7%p
- **LIBERO-Plus**: 86.7% (조명·카메라 각도 등 7가지 변수)
- **ALLEX 휴머노이드 실물**: 커피 따르기 70.8% 성공률 — 타 모델들(약 30%대)의 ~2배

## 3단계 학습 파이프라인

1. **Pre-Training**: 단일 팔, 양 팔, 휴머노이드 등 다양한 embodiment 걸쳐 일반 조작 지식 학습
2. **Mid-Training**: Memory/Physics Module 추가, embodiment 특화 정밀 데이터로 미세조정
3. **Post-Training**: DAgger(실배포 실패 → 학습 데이터) + Progress-Aware RL(VLM 기반 진행도 추정으로 밀집 보상)

## 공개 및 향후 계획

- 모델: 8.1B 파라미터, 3버전(PT, MT-ALLEX, MT-DROID)
- 가중치·코드·기술문서: GitHub 및 Hugging Face에 공개
- 지원 하드웨어: WIRobotics ALLEX, Franka Research 3, OpenArm
- NVIDIA 인프라(Isaac GR00T, Lab, Sim, H100/A100, Jetson AGX Thor, TensorRT) 활용
- SKT, LG전자, CJ대한통운, 롯데, KDDI, ANA홀딩스, 미쓰이화학, 시마즈 등과 투자 및 개념검증 진행
- 샌프란시스코에서 5월 13일 "Dexterity Night" 런치 이벤트 예정
- 향후 접촉·토크·로봇 상태를 시간에 따라 시뮬레이션하는 **4D+ World Model** 개발 계획

---

**참고 자료:**
- [RLDX-1 소개 페이지](https://www.rlwrld.ai/ko/rldx-1)
- [기술 보고서 (arXiv)](https://arxiv.org/abs/2605.03269)
- [GitHub](https://github.com/RLWRLD/RLDX-1)
- [Hugging Face](https://huggingface.co/collections/RLWRLD/rldx-1)
- [DexBench](https://dexbench.org/)
