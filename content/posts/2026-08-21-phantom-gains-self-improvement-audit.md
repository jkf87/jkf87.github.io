---
title: "자기개선 측정의 7가지 함정 — Phantom Gains 정리"
date: 2026-08-21
tags: [agent, self-improvement, evaluation, paper-review]
draft: false
---

## 결론 먼저

LLM 자기개선(self-improvement) 논문들이 이제 정확도 평균 하나 대신 "어떤 문제를 새로 풀게 됐고, 어떤 문제를 잃었는지" 전이(transition) 단위로 성과를 보고합니다. 근데 Phantom Gains 논문(arXiv:2608.20290)은 그 전이 지표 자체가 측정 아티팩트에 취약하다는 걸 보여줍니다. 학습 전후의 노이즈 낀 추정치 두 개를 빼는 구조라서, <span style="background-color: #fff59d"><strong>아무것도 바뀌지 않은 모델에서도 "학습"과 "파괴"가 제조된다</strong></span>는 거예요.

핵심은 이겁니다. <span style="background-color: #fff59d"><strong>전이 지표를 쓰면 모든 통계에 대해 따로 측정한 null(기저값)이 필요하고, 그 null은 추가 실험 없이 얻을 수 있다</strong></span>는 것. 다중 팔 연구가 이미 갖고 있는 베이스라인 재평가로 거의 공짜라구요.

## 실험 설계

- 백본: Qwen3-8B, rank-32 LoRA, 3라운드 자기학습
- 비교군: <span style="background-color: #fff59d"><strong>훈련시키지 않은 frozen control을 동일한 파이프라인 전부 통과시킴</strong></span>
- 평가: 문제당 <span style="background-color: #fff59d"><strong>k=128 샘플</strong></span>로 solve rate 추정, 히스테리시스 밴드 [0.41, 0.59]로 이산화
- 벤치마크: MATH-500(200문제, 오염됨/부패 관찰용), AIME 2025+2026(60문제, 확장 관찰용), 난이도 밴드 1,163문제
- 전이 원장(ledger): 문제마다 7상태(stable-correct / stable-incorrect / learned / corrupted / recovered / transient / oscillating)로 분류
- 코드: github.com/chengxuphd/phantom-gains

## 7가지 측정 실패

![](/images/2026-08-21-phantom-gains-self-improvement-audit/fig-1-p3.png)

Figure 1이 감사 파이프라인과 실패가 들어오는 7개 지점을 한 장에 정리하고 있어요. Table 1을 옮기면 이렇습니다.

| 실패 | 없었다면 나왔을 결론 | 잡는 컨트롤 | 비용 |
|---|---|---|---|
| F1 단일 greedy 디코드 원장 | "훈련 안 된 모델의 CLR=1.5" | frozen floor + 추정치 | $27 |
| F2 m=1 확장 임계값 | "다수결 학습이 AIME 0.143 확장" | ER frozen floor | $0 |
| F3 고정 토큰 캡 | "증류가 가장 파괴적" | 체크포인트별 로그 | $0 |
| F4 저출력 원장 | "두 방법에 차이 없음" | 사전 파워 분석 | $88 |
| F5 학습 시드 1개 | "다수결이 STaR보다 덜 파괴적" | 시드 3개 이상 | $282 |
| F6 저출력 프로브 | "자기학습이 안전성 10점 하락" | 프로브 크기 먼저 | $2 |
| F7 null을 1회 측정 | "ER₂의 null은 0" | 모든 베이스라인이 재현 | $0 |

7개 중 3개가 이미 보유한 기록의 재분석이라 비용 $0이구요, 2개 더도 팔이 2개 이상인 연구라면 공짜입니다.

## F1: greedy 한 번으로는 상태가 안 나온다

토큰 0 디코딩은 배치(batching) 상황에서 결정론적이 아닙니다. greedy 샘플 1개로 원장을 만들면 훈련 안 한 모델을 자기 자신과 재평가하는 것만으로 학습 6건, 부패 9건이 나옵니다. <span style="background-color: #fff59d"><strong>CLR(부패/학습 비율) 1.5</strong></span> — 이 문헌이 보고하는 "충격적 결과"의 모양이 아무것도 없는 데서 제조됩니다.

원인 테스트도 직접 했습니다. 같은 200문제를 greedy로 두 번, 한 번은 64요청 병렬, 한 번은 엄격 직렬로 돌리면 <span style="background-color: #fff59d"><strong>판정 뒤집힘이 16/200에서 4/200으로 감소</strong></span>해요. 병렬이 원인인 건 맞는데, <span style="background-color: #fff59d"><strong>직렬로도 2%의 greedy 판정이 바뀌니까</strong></span> 단일 디코드는 답이 아닙니다.

## F2: 확장 통계는 자기 null이 필요하다

확장(expansion) 통계는 "베이스가 k draws에서 한 번도 못 푼 문제를 훈련 후 1회 이상 푼다"는 임계값 규칙입니다. 두 노이즈 낀 이항 추정치를 비대칭 임계값으로 비교하는데, 이 규칙이 아무 변화 없을 때 무엇을 반환하는지는 측정된 적이 없었습니다.

측정해보니 frozen Qwen3-8B를 k=128로 두 번 평가하면 도달 못 한 AIME 25문제 중 7문제가 "확장"됩니다. <span style="background-color: #fff59d"><strong>비율로 0.280</strong></span>이에요. 7개 전부 운 좋은 단일 샘플이어서 m≥2 성공을 요구하면 null이 0이 되는 것처럼 보입니다.

## F7: 그 "수리"는 null을 1번만 측정한 탓

근데 m=2 수리는 frozen 비교 한 쌍 위의 결론입니다. 각 팔의 체크포인트 0은 훈련 안 된 모델의 독립 평가라서, 이 실험 기록 안에 AIME만 11개, 순서쌍 110개가 이미 들어 있습니다. 그 110쌍으로 pooled null을 재면 <span style="background-color: #fff59d"><strong>0.058 [0.038, 0.078]이 나옵니다. 다수결 자기학습의 실측값 0.048은 null과 구분이 안 됩니다.</strong></span> 임계값을 올려도 구조적으로 안 되고(m=5가 되어야 null이 0에 가까움), m은 벤치마크·k마다 다르게 동작합니다.

저자들의 결론은 임계값을 버리는 겁니다. 훈련 안 된 모델의 독립 평가 전부를 하나의 pooled baseline(1,408 draws/문제)로 묶고, 문제별로 <span style="background-color: #fff59d"><strong>단측 Fisher exact test를 FDR 통제 아래</strong></span> 돌리면 임계값이 사라지고 모든 팔이 같은 분모를 공유합니다. 이 검정은 <span style="background-color: #fff59d"><strong>11개 held-out 재현에서 검출 0건</strong></span>, Bonferroni·오류율·풀 크기 변화에도 불변이었어요.

![](/images/2026-08-21-phantom-gains-self-improvement-audit/fig-2-p7.png)

Figure 2 왼쪽이 임계값 대비 ER_m과 110쌍의 frozen null 밴드구요, 오른쪽이 임계값 없는 검정 결과입니다. 베이스가 1,408 draws에서 1~5번 푼 문제(희귀 도달)에서 <span style="background-color: #fff59d"><strong>증류만 17개 유의미 개선, 자기학습 3종은 0~2개</strong></span>입니다.

## 통제된 감사의 본 결과

스트림·볼륨·평가가 매칭된 사다리에서 확실한 해리(dissociation)가 나옵니다.

- 증류(외부 교사): 베이스가 1,408 draws에서 최대 5번 푼 22문제 중 <span style="background-color: #fff59d"><strong>8–11개 개선</strong></span>
- 자기학습 3형태(STaR, 다수결 SFT, 정책경사): 같은 층위에서 <span style="background-color: #fff59d"><strong>0–2개</strong></span>
- 이 비대칭이 교사의 전체 이득이 커서 그런 건지 회귀로 검정 → <span style="background-color: #fff59d"><strong>β=1.91, p<10⁻⁸로 기각</strong></span>. 즉 정말 층위별로 다릅니다
- 베이스가 한 번도 못 푼 10문제에서는 증거 불충분. <span style="background-color: #fff59d"><strong>"확장"이 아니라 "희귀 도달 문제 개선"이 올바른 주장</strong></span>입니다
- 부패: 두 방법 다 밴드 1,163문제 중 <span style="background-color: #fff59d"><strong>88–106개를 부패. 설계 매칭된 floor는 8개</strong></span>

F3도 여기서 터집니다. 고정 토큰 캡 때문에 가장 효과적인 팔(증류)이 가장 파괴적인 걸로 채점되는데, 실제 원인은 토큰 캡 아래 스타일 드리프트로 인한 로그 잘림이었어요.

F5도 조심스러운 발견입니다. 다수결 자기학습은 같은 데이터·예산으로 시드만 바꾸면 <span style="background-color: #fff59d"><strong>CLR이 0.55–1.53을 오갑니다</strong></span>. 정확도도 +4.0 / −2.8 / −1.0이구요. 방법 설계만으로 결과가 정해지지 않는다는 것, 이게 단일 시드 비교가 얼마나 위험한지 보여주는 대표 사례입니다.

![](/images/2026-08-21-phantom-gains-self-improvement-audit/table-8-p27.png)

Table 8은 체크포인트별 정확도와 전이 카운트 전체인데, 헤드라인 숫자마다 대응하는 floor가 붙어 있습니다.

## 실험 설계자를 위한 실무 체크리스트

원문에서 바로 쓸 수 있는 결론을 정리했습니다.

1. 전이 지표를 쓰면 <span style="background-color: #fff59d"><strong>통계마다 null을 따로 측정</strong></span>한다. frozen control을 동일 파이프라인으로 통과시키면 됩니다
2. <span style="background-color: #fff59d"><strong>각 팔의 체크포인트 0은 독립 베이스라인 평가</strong></span>입니다. 팔이 4개 이상이면 재분석만으로 null을 얻습니다
3. null도 추정치입니다. 1회 측정으로 확정하지 말고 재현쌍을 모아 구간을 만들어요
4. 단일 greedy 디코드로 원장을 만들지 않습니다. k샘플 solve rate + 히스테리시스가 최소안
5. 방법 비교는 시드 3개 이상. 다수결류는 특히 시드에 민감합니다
6. 프로브(안전성 등)는 본 실험 전에 크기를 먼저 계산합니다

## 원문 근거와 내 해석 구분

여기까지가 원문 주장이구요, 제 해석을 하나 붙이면 — 이 논문의 타겟은 자기개선 방법 그 자체보다 "전이 단위 평가"라는 2세대 분석 관행 자체입니다. F1·F2는 표준 관행이고 F7은 수정 절차 안에 숨어 있으니까요. 다만 저자도 명시하듯 증류 vs 자기학습 해리는 "확장"이 아니라 희귀 도달 문제로 한정된 주장이고, 8B 단일 백본·수학 도메인 결과라는 경계가 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
