---
title: "UniVR: 텍스트 없이 시각 공간에서 직접 추론하는 AI - Visual Reasoning GRPO의 등장"
slug: 2026-07-18-univr-visual-space-reasoning
publish: true
date: 2026-07-18T07:00:00+09:00
tags:
  - AI
  - visual-reasoning
  - reinforcement-learning
  - GRPO
  - world-model
  - agent
cover: /images/2026-07-18-univr-visual-space-reasoning/fig1_univr_overview.png
---

## 텍스트를 넘어: AI가 "보는 것"으로 생각하다

현재 LLM과 멀티모달 AI의 추론은 근본적으로 **텍스트 공간**에서 이루어진다. Gemini, GPT, Qwen 같은 최신 모델들은 시각 정보를 입력받아도, 이를 텍스트로 변환한 뒤 텍스트 기반 사고(chain-of-thought)로 추론한다. 시각적 결과물이 필요하면 다시 생성 모델로 렌더링하는 우회 경로를 쓴다.

문제는 이 **"보고 → 텍스트로 생각하고 → 다시 그리기"** 경로가 물리적 일관성과 공간적 정합성을 자주 잃어버린다는 것이다. 매듭을 묶거나 옷을 개는 것 같은 장기 과제에서, 텍스트 추론만으로는 중간 과정의 미세한 물리 역학을 정확히 포착할 수 없다.

> 인간은 언어 없이도 머릿속에서 장면을 시뮬레이션하며 추론한다. UniVR은 바로 이 능력 — **시각 공간에서의 직접 추론** — 을 AI에 부여한다.

![UniVR 개요: 시각 공간 추론 vs 텍스트 공간 추론](/images/2026-07-18-univr-visual-space-reasoning/fig1_univr_overview.png)
*Figure 1: UniVR은 텍스트 공간에서 추론하는 기존 LMM과 달리, 시각 공간에서 직접 추론하고 계획한다.*

## UniVR의 핵심 설계

UniVR은 베이징 교통대학교와 ByteDance가 공동 개발한 프레임워크로, **Emu3.5**라는 통합 생성 모델을 기반으로 한다. 핵심은 두 가지다.

### 1. 시각 공간에서의 통합 추론

텍스트-이미지 쌍 없이, **순수 시각 궤적(visual trajectory)**만으로 학습한다. 이미지 시퀀스 $x_{1:t}$와 명령어가 주어지면, 다음 프레임 분포 $p(x_{t+1} | x_{1:t})$를 직접 모델링한다. 텍스트 추론 체인을 거치지 않고, 시각적 상태 전환과 정책 역학을 직접 학습하는 것이다.

![UniVR 아키텍처](/images/2026-07-18-univr-visual-space-reasoning/fig2_architecture.png)
*Figure 2: 통합 next-token prediction 목표로 UniVR은 명령어와 이미지 쿼리를 처리하여 직접 시각 추론 궤적을 생성한다.*

이 접근의 장점은 물리적 역학, 공간 관계, 인과 진화를 텍스트라는 손실이 많은 중간 표현 없이 직접 포착한다는 점이다.

### 2. VR-GRPO: 시각 추론용 강화학습

UniVR의 진짜 혁신은 **Visual Reasoning GRPO(VR-GRPO)**에 있다. 기존 RL 방법론이 주로 시각적 충실도나 텍스트-이미지 정렬에 집중한 반면, VR-GRPO는 **다단계 시각 추론의 논리적 일관성**을 직접 최적화한다.

두 가지 보상 설계가 핵심이다:

- **글로벌 보상(Global Reward)**: 전체 궤적의 품질, 과제 완성도, 시각적 충실도를 평가
- **스텝-포컬 보상(Step-Focal Reward)**: 궤적 중 가장 오류가 발생하기 쉬운 구간을 자동 식별하여 미세한 물리적 오류를 포착

![VR-GRPO 방법론](/images/2026-07-18-univr-visual-space-reasoning/fig3_vr_grpo_method.png)
*Figure 3: VR-GRPO는 글로벌 보상과 스텝-포컬 보상을 결합하여 과제 완성도와 물리적 일관성을 동시에 보장한다.*

#### 스텝-포컬 보상의 작동 원리

핵심 아이디어는 **불확실성이 가장 높은 구간을 자동으로 찾아 집중 평가**하는 것이다. 구체적으로:

1. $K$개의 롤아웃 궤적을 생성
2. CLIP 인코더로 각 프레임의 임베딩 추출
3. 시간 단계별 궤적 간 분산 $\sigma(t)$ 계산
4. 분산이 최대인 지점 $t^*$ 주변의 구간을 추출
5. VLM(Qwen3-VL-30B)이 해당 구간을 집중 평가

이 설계는 글로벌 보상만으로는 놓치는 **중간 단계의 물리적 모순**(예: 옷걸이가 옷을 관통하거나, 액체 붓기 역학이 잘못되거나, 종이 타올 전환이 떨리는 현상)을 잡아낸다.

![보상 분석](/images/2026-07-18-univr-visual-space-reasoning/fig6_reward_analysis.png)
*Figure 6: 글로벌 보상만 사용하면 장기 과제의 단계별 오류를 놓친다. 스텝-포컬 보상이 이를 해결한다.*

## VR-X 벤치마크: 시각 추론의 종합 시험장

UniVR을 훈련하고 평가하기 위해 **VR-X** 벤치마크를 구축했다. 16개의 다양한 소스에서 수집된 대규모 데이터셋으로, 두 가지 주요 과제 카테고리를 다룬다:

![VR-X 벤치마크](/images/2026-07-18-univr-visual-space-reasoning/fig4_vrx_benchmark.png)
*Figure 4: VR-X 벤치마크 개요.*

- **장기 복합 계획(Long-horizon planning)**: 매듭 묶기, 옷 개기, 요리, 공예, 로봇 제어, 내비게이션 등 분당 단위의 과제
- **일반 시각 추론(General reasoning)**: 시각 탐색, 퍼즐, 공간 지각, 편집 등 기본 인지 기술

모델이 언어 없이 순수 시각적으로 추론하고 과제를 수행해야 하는, 기존에 없던 평가 패러다임이다.

## 결과: Gemini와의 직접 비교

UniVR은 VR-X에서 기존 방법론들을 크게 앞지르며, **최대 25% 성능 향상**을 달성했다. 더 흥미로운 것은 34B 파라미터 모델이 Gemini 3 Pro + Nano Banana 2 파이프라인에 근접하고, 장기 과제에서는 Gemini 3를 능가한다는 점이다.

![Gemini 비교](/images/2026-07-18-univr-visual-space-reasoning/fig7_gemini_comparison.png)
*Figure 7: Gemini 3 Pro + Nano Banana 2, Emu3.5, UniVR의 비교. 각 그룹의 첫 번째, 두 번째, 세 번째 행이 각각에 해당한다.*

### 에이전트 관점에서의 의미

UniVR의 결과는 **에이전트 연구**에 직접적인 시사점을 던진다:

1. **텍스트 없는 정책 학습**: 로봇 공학과 임베디드 AI에서 텍스트 주석이 없는 대량의 시각 데이터를 활용할 수 있는 길이 열렸다
2. **물리적 일관성**: 다단계 과제에서 중간 단계의 물리적 타당성을 유지하는 것은 실제 에이전트 배포의 핵심 과제
3. **확장 가능한 RL 보상 설계**: 작업별 휴리스틱 없이도 복잡한 시각 궤적의 품질을 자동 평가하는 메커니즘

## 한계와 향후 방향

논문도 솔직하게 인정하는 한계가 있다:

- **기반 모델 의존성**: Emu3.5의 생성 품질이 상한선을 정한다
- **평가자 한계**: VLM 기반 보상 모델(Qwen3-VL-30B)의 시각 세계 지식이 여전히 제한적
- **계산 비용**: 분당 단위의 비디오 생성과 RL 훈련은 상당한 컴퓨팅을 요구

그럼에도 UniVR은 **"AI가 텍스트를 거치지 않고 직접 시각적으로 사고한다"**는 패러다임의 실현 가능성을 처음으로 강력하게 입증한 연구다. 언어 중심 AI에서 진정한 멀티모달 지능으로 나아가는 중요한 이정표다.

---

**원문**: [arXiv:2607.12800](https://arxiv.org/abs/2607.12800)  
**프로젝트 페이지**: [UniVR GitHub](https://maverickren.github.io/UniVR.github.io/)
