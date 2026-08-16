---
title: "Evoke: 세 걸음으로 두 시간을 생성하는 인터랙티브 월드 모델 — Alaya-EVOKE 논문 정리"
date: 2026-08-16
tags:
  - world-model
  - interactive-video
  - video-generation
  - LLM
  - efficiency
  - distillation
  - external-memory
source: huggingface
source_url: https://huggingface.co/papers/2608.13546
paper_url: https://arxiv.org/html/2608.13546v1
---

arXiv:2608.13546 "Alaya-EVOKE: From Linear-Scaling Supervision to Endless World"(2026-08-13, USTC·Alaya Lab, Yin 외 6인) 논문 정리입니다. 인터랙티브 월드 모델은 <span style="background-color: #fff59d"><strong>영구 기억, 즉각 반응, 장시간 생성</strong></span>을 동시에 만족해야 하는데, 이 세 요구는 서로 충돌합니다. 이 논문은 그 충돌을 <span style="background-color: #fff59d"><strong>외부 지오메트리 메모리 + 롱호라이즌 교사 증류</strong></span>로 푼 사례입니다.

## 문제 구조

기존 인터랙티브 월드 모델은 크게 두 방식으로 세션을 유지합니다.

- 컨텍스트나 KV 캐시에 과거 프레임을 쌓는 방식: 세션이 길어지면 비용이 계속 늘어납니다.
- 컨텍스트를 짧게 자르는 방식: 비용은 싸지만 장면 일관성이 무너집니다.

즉 세션 길이와 기억 유지가 트레이드오프로 묶여 있었습니다. 저자들은 이걸 모델 크기 키우기로 풀지 않고, 상태를 어디 두는지라는 시스템 설계 문제로 바꿨습니다.

## 방법 1: 외부 지오메트리 월드 상태

Evoke는 장면 지오메트리를 <span style="background-color: #fff59d"><strong>카메라 포즈로 인덱싱된 외부 월드 상태 뱅크</strong></span>에 보관합니다. 디노이저 컨텍스트에는 짧은 관측만 남기고, 현재 뷰에 필요한 정보만 뱅크에서 검색해 씁니다.

결과는 이겁니다.

- 디노이저 컨텍스트 크기가 <span style="background-color: #fff59d"><strong>세션 길이와 무관하게 일정</strong></span>
- 유지 비용은 90초 관측 고정 예산 안에서만 발생

포즈 기반 리콜 검증도 했습니다. 같은 포즈로 돌아오는 궤적에서 재방문 PSNR을 측정했는데, <span style="background-color: #fff59d"><strong>리텐션 윈도우가 떠나 있던 시간을 덮으면 2.3–3.2dB 향상</strong></span>, 21개 비교 중 20개가 이 전이를 따랐습니다. 다만 도달하는 플래토는 <span style="background-color: #fff59d"><strong>15.4–17.8dB 수준</strong></span>입니다. 픽셀 단위 재현까지는 안 되고, '알아볼 수 있는 수준'의 복원입니다.

![](/images/2026-08-16-alaya-evoke-long-horizon-world-model/fig-7-p10.png)

Figure 7은 카메라가 돌아왔을 때 월드 상태 뱅크가 해당 영역을 복원하는 과정입니다.

## 방법 2: 롱호라이즌 교사 설계

저지연 상호작용에는 3-스텝 소수 생성이 쓰이는데, 이런 학생의 상한은 결국 교사가 정합니다. 기존 방식은 고품질 생성기를 그대로 교사로 쓰는데, Evoke는 교사 자체를 롱호라이즌용으로 다시 설계했습니다.

- 스파스 어텐션: 청크별 그룹화 + 원거리 프레임 검색 + 선형 어텐션 전역 상태 → <span style="background-color: #fff59d"><strong>활성화 메모리와 계산이 시간에 대해 선형 증가</strong></span>
- 청크별 컨디셔닝으로 시퀀스 중간에도 프롬프트 변경·이벤트 제어 가능
- <span style="background-color: #fff59d"><strong>30초 롱호라이즌 분포 매칭 목적함수</strong></span>를 self-forced rollout 하에 적용, 3-스텝·CFG 없는 학생으로 전이

여기서 노린 핵심은 이겁니다. 짧은 윈도우에서는 그럴듯해 보이는 <span style="background-color: #fff59d"><strong>콘텐츠 드리프트가 긴 감독 구간에서는 드러납니다</strong></span>. 그 감독이 학생의 드리프트 저항으로 이어집니다.

동일 레시피에서 교사만 짧게/길게 바꿔 비교한 통제 실험에서, 롱호라이즌 교사 학생이 <span style="background-color: #fff59d"><strong>광도 안정성(photometric stability)에서 확실히 강</strong></span>했습니다. 콘텐츠 디스크립터는 유의미한 차이가 없어서, 저자들은 효과를 광도 안정성으로 한정해 해석합니다. 윈도우 길이만 늘려서 설명되는 효과인지도 확인했는데, <span style="background-color: #fff59d"><strong>짧은 호라이즌 이상에서는 감지력이 더 오르지 않아</strong></span> 교사 전체 설계의 효과로 봅니다.

![](/images/2026-08-16-alaya-evoke-long-horizon-world-model/fig-5-p8.png)

Figure 5는 청크별 스파스 어텐션 구조로 긴 감독을 가능하게 만드는 구조입니다.

## 결과: 성능과 비용

WBench 네비게이션 스플릿(158 케이스)에서 Evoke는 평가된 소수(few-step) 시스템 중 <span style="background-color: #fff59d"><strong>Video Quality 82.79, Setting 83.76, Physical 72.06으로 그룹 평균 1위</strong></span>입니다. Scene(74.68)과 Causal Fidelity(82.44)에서 가장 큰 격차가 났고, Consistency는 최고 결과와 동등했습니다. 약한 부분은 명시적입니다. <span style="background-color: #fff59d"><strong>Navigation(78.63)과 Perspective(69.74)는 최상위보다 낮습니다.</strong></span>

일반 화질 벤치마크에서도 확인했습니다.

| 벤치마크 | Evoke | 순위 | 비고 |
|---|---|---|---|
| VBench-2.0 | 66.77 | <span style="background-color: #fff59d"><strong>10팀 중 1위</strong></span> | 리더 Veo 3 66.72 |
| VBench-Long | 85.11 | 7/10 | 1위 IPOW 88.26 |

이 점수는 <span style="background-color: #fff59d"><strong>3-스텝, CFG 없이</strong></span> 낸 값이고 비교군은 기본 다중 스텝 샘플러라, 스텝 매칭 비교는 아니라는 단서가 붙습니다.

## 세션 안정성과 경계 비용

8개의 <span style="background-color: #fff59d"><strong>65.5분(2,619청크) 롤아웃</strong></span>으로 정량 평가했습니다. 광도 통계는 초기 과도기 후 안정되고, 콘텐츠 디스크립터는 초반에 빠르게 변하다가 이후 느려지는데 그 감속 폭이 실제 영상 대조군과 비슷합니다. 저자들의 해석은 '달아나는 품질 붕괴는 없다' 정도로 한정됩니다. 장면 정체성이 영구히 보존된다는 주장까지는 하지 않습니다.

계산 쪽은 이렇게 정리됩니다. 리텐션 예산이 차면 활성 지오메트리 풀은 더 늘지 않고, <span style="background-color: #fff59d"><strong>세션이 길어도 한 스텝 비용은 그대로</strong></span>입니다. 단가는 H200 한 장, 384×640 해상도에서 <span style="background-color: #fff59d"><strong>1.5초 청크를 2.11초에 생성</strong></span>합니다. 2시간 연속 생성 데모도 Figure 1로 제시했습니다.

![](/images/2026-08-16-alaya-evoke-long-horizon-world-model/fig-1-p2.png)

Figure 1은 연속 카메라 제어 하에 2시간 롤아웃을 뽑은 사례입니다.

![](/images/2026-08-16-alaya-evoke-long-horizon-world-model/fig-4-p6.png)

Figure 4는 한 시간 세션에서 단계별 비용이 늘지 않고 유지되는 그래프입니다.

## 텍스트 제어의 경계

청크별 컨디셔닝으로 세션 중간에 텍스트 지시를 바꿀 수 있는데, 여기에 명확한 경계가 있습니다. 통제 평가에서 세션 중간에 삽입된 절(clause)은 <span style="background-color: #fff59d"><strong>미고정 콘텐츠 대상이면 67% 실현, 이미 지오메트리로 고정된 콘텐츠면 4%</strong></span>였습니다.

즉 <span style="background-color: #fff59d"><strong>텍스트는 자유로운 콘텐츠를 다루고, 고정된 지오메트리는 이미 관측된 장면의 덮어쓰기를 막습니다.</strong></span> 이것도 설계된 동작이라는 게 이 논문의 설명입니다.

## 남은 한계

- 재방문 복원이 픽셀 충실 수준은 아닙니다(15.4–17.8dB 플래토).
- Navigation/Perspective 등 카메라 제어 경로는 최상위보다 약합니다.
- VBench 비교는 스텝 매칭이 아니라 해석에 주의가 필요합니다.
- 롱호라이즌 교사 효과는 광도 안정성으로 한정해서 해석하는 게 정확합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

코드는 github.com/SII-YuanyangYin/Evoke, 프로젝트 페이지는 evoke-world.github.io/Evoke 입니다.
