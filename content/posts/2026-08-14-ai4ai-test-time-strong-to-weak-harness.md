---
title: "AI4AI at Test-Time: 강한 모델이 약한 모델용 하네스를 컴파일해주는 실험"
date: 2026-08-14
tags:
  - agent
  - harness
  - LLM
  - scaffolding
  - test-time
  - strong-to-weak
  - builder
  - ToM
  - Salesforce
  - evaluation
---

<span style="background-color: #fff59d"><strong>GPT-5.4-mini의 정확도가 0.488에서 0.912로 올라갔다.</strong></span> 가중치는 그대로 두고, 강한 모델이 짜준 하네스만 얹었을 때 결과다. Salesforce AI Research와 UIUC이 공개한 "AI4AI at Test-Time: Strong-to-Weak Capability Transfer via Harnesses"의 핵심 수치다.

핵심은 이겁니다. 강한 모델이 과제 구조를 하네스로 컴파일해주면, 약한 모델도 최상위권에 근접한다. <span style="background-color: #fff59d"><strong>상향폭 +0.423, 상대율 86.7%</strong></span>. GPT-5.4 정식 모델의 기본 점수(0.619)도 넘고, <span style="background-color: #fff59d"><strong>동일 백본에 인간이 설계한 하네스 참고치(0.939)에 근접한다</strong></span>.

## 실험 설계

![AI4AI 프레임워크 개요](/images/2026-08-14-ai4ai-test-time-strong-to-weak-harness/fig-1-p4.png)

역할을 둘로 나눈다.

- **빌더**: GPT-5.5, Opus-4.7, Gemini-3.5-flash, Sonnet-4.6, Codex-5.3
- **타깃**: GPT-5.4-mini (타깃 의존성 실험은 Gemini-3.5-flash)

빌더는 Cursor, Claude Code, GPT Codex 세 코딩 에이전트 플랫폼 위에서 작업한다. <span style="background-color: #fff59d"><strong>검증 세트 195문항(전체의 5%)만 보고</strong></span> 스캐폴드를 반복 개선한다. 최종 평가는 <span style="background-color: #fff59d"><strong>숨겨진 3,900문항 히든 테스트</strong></span>에서 진행한다.

평가 과제는 이론심리(ToM) 4종: BigToM, Hi-ToM, MMToM-QA, MuMA-ToM. 관찰·믿음·의도 추적을 요구하는 벤치마크 묶음이다.

## 메인 결과

<span style="background-color: #fff59d"><strong>총 72개 실행(빌더×플랫폼×반복) 전부 기본 성능을 넘었다.</strong></span> 한 건의 실패도 없다.

| 지표 | 값 |
|---|---|
| GPT-5.4-mini 기본 | 0.488 |
| 스캐폴드 전체 평균 | 0.763 (+0.275) |
| 최고 실행 (GPT-5.5 / GPT Codex) | 0.912 (+0.423) |
| 기본 미만 실행 | 0% |
| 인간 설계 하네스 참고치 | 0.939 |

![메인 결과](/images/2026-08-14-ai4ai-test-time-strong-to-weak-harness/fig-2-p5.png)

빌더별 평균은 이렇다.

| 빌더 | 평균 정확도 |
|---|---|
| GPT-5.5 | 0.875 |
| Opus-4.7 (x-high) | 0.856 |
| Gemini-3.5-flash | 0.813 |
| Sonnet-4.6 | 0.810 |
| Opus-4.7 (high) | 0.807 |

## 빌더가 플랫폼보다 크다

변동의 주원인은 빌더 모델이었다. 같은 빌더 안에서 플랫폼 차이는 2차 효과에 그친다. <span style="background-color: #fff59d"><strong>빌더 간 격차가 플랫폼 간 격차보다 훨씬 크게 벌어진다</strong></span>.

## 추론 노력은 단조 증가

빌더의 추론 노력을 low에서 extra-high로 올리면 <span style="background-color: #fff59d"><strong>결과가 단조 증가했다 (Spearman ρ=0.77)</strong></span>.

| 플랫폼 | low | medium | high | extra-high |
|---|---|---|---|---|
| Cursor | 0.728 | 0.770 | 0.788 | 0.840 |
| Claude Code | 0.694 | 0.816 | 0.826 | 0.872 |

풀링하면 0.711 → 0.793 → 0.807 → 0.856. extra-high와 high 사이도 유의미했다 (순열검정 p=0.013). 과잉 엔지니어링 징후는 없었다.

스캐폴드 코드 크기도 함께 커진다. low에서 약 510~650줄, extra-high에서 1,000~1,300줄. 더 깊이 고민할수록 더 많은 과제 로직이 하네스로 컴파일된다.

## 헤드룸 법칙

타깃을 Gemini-3.5-flash로 바꾸면 이야기가 달라진다. 약한 타깃(GPT-5.4-mini)은 평균 +0.262를 얻는데, 강한 타깃(Gemini-3.5-flash)은 +0.110에 그친다.

<span style="background-color: #fff59d"><strong>상향폭은 타깃이 남긴 헤드룸(1 − 기본 정확도)으로 예측된다 (Pearson r=0.75)</strong></span>. "타깃이 강해지면 효과가 줄어든다"는 표면 규칙의 정체다.

주의할 지점도 있다. 강한 타깃에서는 모든 빌더가 최소 한 벤치마크에서 성능이 떨어졌다 (20개 매칭 중 9건). <span style="background-color: #fff59d"><strong>이미 잘 푸는 과제에 얹는 추가 규칙은 방해가 될 수 있다</strong></span>.

## 메커니즘: 인지 부하 감소

메커니즘은 인지 부하 감소로 귀결된다. <span style="background-color: #fff59d"><strong>코드·규칙이 답을 내는 문항 비중(결정론 비율)이 높을수록 정확도가 올라간다 (r=0.72)</strong></span>. 타깃이 reasoning해야 할 분량을 빌더가 대신 구조화해주는 식이다.

과제별 컴파일 가능성은 크게 갈린다.

| 벤치마크 | 결정론 비율 평균 |
|---|---|
| BigToM | 0.94 |
| Hi-ToM | 0.51 |
| MMToM-QA | 0.44 |
| MuMA-ToM | 0.36 |

BigToM은 거의 코드로 변환이 되고, 자유 대화 추론이 필요한 MuMA-ToM은 규칙화가 어렵다. <span style="background-color: #fff59d"><strong>코드 줄수 자체는 정확도와 거의 무관했다 (r≈0.22). 무엇을 옮겼는지가 관건이다</strong></span>.

## 기법별 기여

상위권을 가르는 기법은 과제 구조를 하네스에 박아넣는 쪽이다.

| 기법 | 정확도 차이 |
|---|---|
| 극성/부정 논리 | +0.090 |
| 구조화된 추출 | +0.055 |
| few-shot 예시 | +0.042 |
| 하이브리드 폴백 | +0.040 |
| 자기일관성 투표 | +0.038 |

포맷 강제, 라우팅, greedy 디코딩은 거의 모든 실행이 쓰는 바닥층 기법이다 (57개 실행 중 56~57개). 이것만으로 상위권과 하위권이 갈리지는 않는다.

## 아이템 수준 검증

<span style="background-color: #fff59d"><strong>최고 스캐폴드는 기본에서 틀린 1,717문항을 고쳤고, 맞았던 걸 깨뜨린 건 105문항이다</strong></span> (McNemar χ²=1424.4, p<10⁻⁴). 노이즈 재분배로는 설명이 안 된다. 광범위한 개선이다.

상위 스캐폴드들은 서로 다른 오류도 고친다. <span style="background-color: #fff59d"><strong>상위 스캐폴드가 고친 오류의 합집합은 기본 오류의 97%를 커버한다</strong></span>. 하나의 설계로는 닿지 않는 영역을 서로 보완한다.

self-scaffolding 대조도 informative하다. GPT-5.4-mini가 자기 하네스를 직접 만들어도 +0.17~+0.22는 올린다. 강한 빌더는 +0.31까지 끌어올린다 (GPT Codex 기준).

## 남은 오류

잔여 오류는 컴파일이 안 되는 영역에 몰려 있다.

- Hi-ToM 재귀 깊이: order 0에서 0.999 → order 4에서 0.700
- 기만(deception) 포함 시 0.829 → 0.772
- MMToM-QA 베이지안 목표 추론 유형: qtype 2.1에서 0.680

<span style="background-color: #fff59d"><strong>상위 스캐폴드는 평균적으로 기본 오류의 83%를 고치고, 맞은 문항의 7%만 깨뜨린다</strong></span>. Pareto 개선에 가깝다.

## 실무 레시피

논문이 제안하는 배포 처방을 정리했습니다.

1. 가장 강한 빌더를 쓴다
2. 빌딩에 높은 추론 노력을 할당한다
3. 검증 평가는 소수(중앙값 5회)면 충분하다
4. 증명 가능한 서브태스크는 코드 오프로딩을 우선한다
5. 여러 독립 스캐폴드를 만들어 선택하거나 앙상블한다

검증을 많이 돌린다고 좋아지지 않는다. 반복 횟수와 최종 성적은 거의 무관했다 (r=0.17). <span style="background-color: #fff59d"><strong>검증 점수 최고치만 최종 성적을 잘 추적한다 (r=0.96)</strong></span>.

원문: [AI4AI at Test-Time: Strong-to-Weak Capability Transfer via Harnesses](https://arxiv.org/abs/2608.12307) (Salesforce AI Research + UIUC, 2026-08)

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
