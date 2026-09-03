---
title: PGPO 정리 — 실패한 롤아웃 안에서도 크레딧을 나눠주는 잠재력 기반 어드밴티지
date: 2026-09-03
tags:
  - agentic-rl
  - credit-assignment
  - paper-notes
draft: false
description: PGPO(arXiv:2609.02236) 정리. 앵커 상태 그룹 통계로 상태 잠재력을 추정하고, 인접 상태 간 잠재력 차이로 스텝 어드밴티지를 만들어 실패 트랙토리 내 크레딧을 구분하는 방법과 ALFWorld·WebShop 수치를 정리했습니다.
---

## 결론 먼저

PGPO(Potential-Guided Policy Optimization)는 희소 보상 멀티턴 에이전트 RL에서 <span style="background-color: #fff59d"><strong>실패한 트랙토리 안의 좋은 행동과 나쁜 행동을 다른 크레딧으로 구분</strong></span>해주는 방법입니다. 핵심 장치는 두 개구요.

- 같은 앵커 상태를 방문한 모든 롤아웃의 리턴을 모아 <span style="background-color: #fff59d"><strong>상태 잠재력 Φ(s̃)을 경험적으로 추정</strong></span>
- 현재 상태 → 다음 상태 잠재력 차이로 <span style="background-color: #fff59d"><strong>전이 자체를 평가하는 어드밴티지 A^φ를 추가</strong></span>

크리틱 추가 학습, 추가 추론, 추가 롤아웃 없이 GiGPO 스텝 신호에 곱해서 씁니다. Qwen2.5-1.5B 기준 ALFWorld Unseen 84.76% → <span style="background-color: #fff59d"><strong>88.73%</strong></span>, WebShop 성공률 66.53% → <span style="background-color: #fff59d"><strong>75.00%</strong></span> (기준일 2026-09-03, Table 1).

## 핵심 요약 표

| 항목 | 값 |
|---|---|
| 논문 | PGPO: Potential-Guided Policy Optimization for Multi-Turn Agentic Tasks |
| 번호 | arXiv:2609.02236 (2026-09-02) |
| 소속 | Fudan University · Zuoyebang · BEDI Cloud |
| 문제 | 실패 트랙토리 내부 크레딧 미분화 (failure-side credit degeneracy) |
| 방법 | 앵커 상태 그룹 리턴 평균으로 Φ(s̃) 추정 → 잠재력 차이 어드밴티지 A^φ |
| 백본 | Qwen2.5-1.5B / 7B Instruct |
| 벤치마크 | ALFWorld, WebShop |
| 최고 성적 | 1.5B WebShop 성공률 75.00%, 7B ALFWorld Seen 96.48% |
| 추가 비용 | 크리틱·추가 추론·추가 롤아웃 0 |

## 문제 상황: 실패한 트랙토리는 크레딧이 다 똑같습니다

ALFWorld/WebShop 같은 환경은 보상이 마지막에만 나옵니다. GRPO류 그룹 RL은 트랙토리 리턴을 그룹 내 표준화해서 씁니다. 그러면 <span style="background-color: #fff59d"><strong>실패 트랙토리의 모든 스텝이 같은 불리한 크레딧을 상속</strong></span>합니다.

GiGPO가 앵커 상태 그룹으로 스텝 레벨 신호를 만들어도, 그 신호는 결국 각 트랙토리의 최종 결과에서 나옵니다. 논문 식 (4)가 이걸 정리해서 보여줍니다.

논문의 ALFWorld 예시가 직관적이구요. "mug를 데워서 cabinet 1에 넣기" 과제에서 `open cabinet 1`은 목표에 가까워지는 좋은 행동입니다. 그런데 트랙토리가 나중에 countertop로 새면 이 행동도 실패 크레딧을 같이 받습니다. Figure 1 참고하세요.

![](/images/2026-09-03-pgpo-potential-guided-policy-optimization/fig-1-p1.png)

## 방법: 상태 잠재력을 롤아웃 통계로 뽑기

PGPO는 앵커 상태 그룹을 그대로 쓰면서 크레딧 계산만 바꿉니다.

1. 잠재력 추정. 관찰 문자열이 정확히 같은 방문을 모아 앵커 상태 그룹 G_s̃을 만들고, 그 안의 스텝 리턴 평균으로 Φ(s̃)을 정의합니다 (식 6). 학습된 가치 네트워크 없이 몬테카를로 방식으로 가치를 추정한 셈입니다.
2. 전이 평가. 각 행동에 대해 δt = γΦ(s̃_next) − Φ(s̃_cur)을 계산합니다 (γ=1 기본). <span style="background-color: #fff59d"><strong>양수면 더 높은 잠재력 상태로 이동한 것</strong></span>, 음수면 낮은 곳으로 샜다는 뜻입니다. 마지막 스텝은 Φ 대신 실제 최종 보상을 대입합니다.
3. 그룹 내 표준화. δt를 현재 앵커 그룹 안에서 표준화해서 A^φ를 만듭니다.
4. 가중합. 최종 어드밴티지는 A = A^S + w(x)·A^φ. w(x) = β(1−p_succ)^α이고 <span style="background-color: #fff59d"><strong>성공률 낮은 과제일수록 A^φ 가중치가 커집니다</strong></span> (α=2.0, β=1.0).

PBRS(potential-based reward shaping)에서 착안했는데, 보상 변형이 아니라 어드밴티지 신호로 쓴다는 점이 다릅니다. 전체 파이프라인은 Figure 2입니다.

![](/images/2026-09-03-pgpo-potential-guided-policy-optimization/fig-2-p5.png)

핵심은 <span style="background-color: #fff59d"><strong>교차 트랙토리 크레딧 전파</strong></span>입니다. 실패한 트랙토리의 어떤 스텝이, 성공한 트랙토리가 지나간 상태로 이동했다면 그 전이 자체가 양의 신호를 받습니다. 자기 트랙토리 결과에만 매이던 기존 방식의 한계를 이렇게 우회합니다.

## 성능: Table 1 수치

기본 설정은 Qwen2.5-1.5B/7B Instruct, 시드 3회 평균, α=2.0, β=1.0입니다.

| 모델 | 방법 | ALFWorld Seen | ALFWorld Unseen | WebShop 성공률 | WebShop 점수 |
|---|---|---|---|---|---|
| 1.5B | GRPO | 72.8 | 70.1 | 56.8 | 75.8 |
| 1.5B | GiGPO | 90.16 | 84.76 | 66.53 | 84.95 |
| 1.5B | HGPO | 92.77 | 90.16 | 71.54 | 85.56 |
| 1.5B | PGPO | 93.03 | 88.73 | 75.00 | 87.99 |
| 7B | GiGPO | 93.29 | 92.18 | 77.60 | 88.93 |
| 7B | HGPO | 95.44 | 92.05 | 78.51 | 88.96 |
| 7B | PGPO | 96.48 | 90.82 | 79.10 | 91.73 |

![](/images/2026-09-03-pgpo-potential-guided-policy-optimization/table-1-p7.png)

정리하면 이렇습니다.

- 1.5B: ALFWorld Seen 최고, WebShop은 성공률·점수 모두 최고. Unseen은 HGPO(90.16)보다 1.43점 낮음
- 7B: ALFWorld Seen 최고(96.48), WebShop 최고. Unseen은 GiGPO(92.18)가 위
- 저자도 <span style="background-color: #fff59d"><strong>균등한 OOD 우위를 주장하지 않고 "보완적 로컬 크레딧 신호"로 positioning</strong></span>합니다

근데 WebShop 격차가 큽니다. 1.5B에서 GiGPO 대비 <span style="background-color: #fff59d"><strong>성공률 +8.47%p</strong></span>인데, WebShop은 과제별 성공률 편차가 커서 성공률 적응 가중치 w(x)가 들어맞았을 가능성이 높습니다.

## 절제 실험: w(x) 결과

Table 2 (ALFWorld, 1.5B) 핵심만 뽑으면:

| 변형 | Seen | Unseen |
|---|---|---|
| A^E만 (GRPO) | 72.8 | 70.1 |
| A^φ만 | 80.33 | 74.41 |
| A^S만 | 89.71 | 83.65 |
| A^S + A^φ (가중 없이) | 87.57 | 84.64 |
| A^S + w(x)A^φ (PGPO) | 93.03 | 88.73 |
| + A^E 추가 | 87.30 | 83.60 |

A^φ 단독은 A^S보다 약합니다. 그래서 <span style="background-color: #fff59d"><strong>잠재력 신호는 스텝 신호를 대체하는 게 아니라 보완하는 것</strong></span>이 맞습니다. 가중 w(x) 없이 그냥 더하면 오히려 89.71 → 87.57로 떨어지고, 거기에 에피소드 신호 A^E까지 얹으면 87.30으로 더 떨어집니다. 조절이 중요합니다.

## 메커니즘 분석: 실패 스텝 분산

논문은 FTD(실패 트랙토리 내 분산), FGD(실패 앵커 그룹 내 분산) 두 지표로 확인합니다. A^E는 둘 다 거의 없고, A^S는 FTD만 있고 FGD가 0입니다. A^φ와 최종 A는 <span style="background-color: #fff59d"><strong>FGD가 0이 아니라 같은 앵커 상태에서 갈린 행동들이 다른 크레딧을 받는다는 직접 증거</strong></span>가 나옵니다 (Figure 3).

![](/images/2026-09-03-pgpo-potential-guided-policy-optimization/fig-3-p8-2.png)

액션 레벨 정답이 없으니, 성공 트랙토리에도 관측된 실패 행동을 "보수적 프록시"로 삼아 방향성을 검증했다고 저자는 씁니다.

## 한계와 실무 포인트

- 앵커 키가 <span style="background-color: #fff59d"><strong>관찰 문자열 정확 매칭</strong></span>이라 템플릿 환경에서 잘 돌아가지만, 부분 관측·패러프레이즈에 취약합니다. 텍스트 유사도 완화 실험에서도 GiGPO보다 강하게 유지된다고는 하나 완전한 검증은 아니라고 스스로 밝힙니다
- 잠재력이 동일 배치 롤아웃 통계라 <span style="background-color: #fff59d"><strong>앵커 그룹이 작거나 성공이 드물면 노이즈</strong></span>가 커집니다. 편향-분산 보장이 없습니다
- 평가가 ALFWorld/WebShop 두 환경뿐이라 열린 웹·툴유즈·임바디드 확장 검증은 남은 과제입니다

실무에서 가져갈 부분은 이겁니다. 희소 보상 멀티턴 에이전트를 RL로 돌린다면, 실패 롤아웃을 통째로 버리지 말고 <span style="background-color: #fff59d"><strong>상태 단위로 재활용해 전이 품질 신호를 뽑는 게 거의 공짜로 +3~8%p를 만든다</strong></span>는 결과입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

PGPO에서 잠재력 Φ(s̃)은 어떻게 계산하나요?
같은 관찰 문자열을 가진 앵커 상태 그룹 내 모든 스텝 리턴의 평균입니다(식 6). 학습된 가치 네트워크가 없습니다.

GiGPO와 PGPO의 차이는 뭔가요?
GiGPO는 각 트랙토리의 최종 결과에서 유도된 스텝 리턴을 표준화하고, PGPO는 앵커 상태 간 잠재력 차이라는 별도 전이 신호 A^φ를 더해 교차 트랙토리 크레딧 전파를 만듭니다.

PGPO는 추가 비용이 드나요?
크리틱 학습, 추가 모델 추론, 추가 환경 롤아웃이 전부 없습니다. 롤아웃 그룹 통계 계산만 추가됩니다.

ALFWorld Unseen에서는 PGPO가 최고인가요?
아니요. 1.5B/7B 모두 HGPO·GiGPO가 Unseen에서 더 높습니다(예: 7B GiGPO 92.18% vs PGPO 90.82%). 저자도 보완적 신호로 positioning합니다.

원문은 어디서 보나요?
arXiv:2609.02236, https://arxiv.org/abs/2609.02236 (2026-09-02 공개)입니다.
