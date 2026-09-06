---
title: "CAPTURE — 사용자 취향 변화와 메모리 포이즈닝을 분리하는 방법"
date: 2026-09-06
tags: [agent-memory, llm-agent, memory-poisoning, personalization, security]
draft: false
description: "개인화 LLM 에이전트의 진짜 취향 변화와 메모리 포이즈닝을 한 턴 안에서 구분하는 문제를 정리하고, 연속시간 신념 추적 + 다중 시간규모 원장 구조 CAPTURE의 실험 결과를 수치로 정리했습니다."
---

## 결론 먼저

arXiv 2609.02265(2026-09-02)의 CAPTURE는 개인화 에이전트의 <span style="background-color: #fff59d"><strong>메모리 업데이트에서 "진짜 취향 변화"와 "메모리 포이즈닝"을 분리해서 판정하는 시스템</strong></span>입니다. 480개 홀드아웃 에피소드에서 <span style="background-color: #fff59d"><strong>독성 주입 성공률 11.5%를 유지하면서 정당한 취향 변화 수용률 83.5%를 달성</strong></span>했습니다. 기존 방어인 provenance-only 필터는 같은 조건에서 <span style="background-color: #fff59d"><strong>74.1% 수용에 그쳤습니다</strong></span>.

문제 정의가 이 논문의 진짜 기여입니다. 사용자가 "이제 요약만 줘"라고 말했을 때, 이게 진짜 역할 변화인지, 스탠드업 미팅 맥락인지, 빈정거림인지, 검색된 문서에 숨어든 공격인지 한 턴의 증거만으로는 구분이 안 됩니다. 저자는 이걸 <span style="background-color: #fff59d"><strong>preference-authenticity ambiguity</strong></span>라고 부릅니다.

기준일: 2026-09-06 기준, 논문 v1(2026-09-02 제출) 내용입니다.

## 핵심 수치 요약

| 항목 | CAPTURE | Provenance-only | StateMem | Recency RAG |
|---|---|---|---|---|
| Win rate (vs 비개인화) | 71.5% | 61.5% | 66.1% | 63.8% |
| Poisoning 성공률 | 11.5% | 20.0% | 34.8% | 51.6% |
| 정당한 업데이트 수용률 | 83.5% | 74.1% | 77.2% | 85.7% |
| 오탐 수용(거짓 업데이트) | 8.9% | 19.6% | 24.1% | 41.2% |
| 적응형 공격자 ASR | 24.7% | 22.1% | 37.2% | n/a |

## 왜 고정 규칙으로는 안 되는가

기존 시스템은 두 가지로 갈립니다. 개인화 파이프라인은 히스토리를 전부 진실로 받아들여서 속도를 올리고, 주입 방어는 출처가 불명확하면 거부합니다. 둘 다 한쪽 실패 모드를 희생하는 구조입니다.

논문의 Theorem 1이 요점입니다. <span style="background-color: #fff59d"><strong>recency와 provenance만 보는 어떤 규칙도, 공격자가 정당한 수정의 통계를 충분히 흉내 낼 수 있다면 오류율 하한이 존재</strong></span>합니다. 실제로 same-origin 오염(공격자가 외부 문서에 심은 문장을 사용자가 나중에 대화에 붙여넣는 시나리오)에서는 <span style="background-color: #fff59d"><strong>provenance 필터가 43.6%로 무너지고 CAPTURE는 17.5%에 그칩니다</strong></span>. 채널 라벨 자체가 오염되는 상황이라 규칙이 뚫리는 겁니다.

## CAPTURE 구조

### 1. 가설 추출

3B 파라미터 모델(Qwen2.5-3B + LoRA)이 이벤트를 읽고 (주장, 방향, 범위, 시간규모, 신뢰도, 출처) 튜플로 뽑아냅니다. <span style="background-color: #fff59d"><strong>이벤트의 약 7할은 취향 신호가 아예 없어서</strong></span>, 거절을 못 하는 추출기는 노이즈 원장을 만듭니다.

### 2. 진위 판정 게이트

잠재 신념 h(t)가 이벤트 사이에 연속시간으로 흐르는 neural ODE입니다. 오후에 40턴 몰아치고 9일 침묵하는 사용자 패턴에서 이산 스텝 모델은 간격을 동일하게 취급하는데, ODE는 9일 동안 transient 층이 충분히 감쇠한 상태로 다음 모순을 받아들입니다.

게이트는 6가지 행동 중 하나를 고릅니다: 유지, 추가, 범위 축소, 수정, 격리, 사용자에게 질문. 행동 분포의 엔트로피가 임계값을 넘으면 물어보고, <span style="background-color: #fff59d"><strong>질문 예산은 상호작용 12회당 1회 이하</strong></span>로 조정됐습니다.

### 3. 다중 시간규모 원장

가설 노드가 방향 그래프로 쌓이고 세 층으로 나뉩니다. 기본 감쇠율은 <span style="background-color: #fff59d"><strong>stable γ=0.01, contextual 0.1, transient 0.5(단위: 일)</strong></span>. 주말 프로젝트 얘기가 직업 정체성 얘기를 덮어쓰지 못하는 게 이 구조의 요점입니다. stable 노드를 덮어쓰려면 반복적 고신뢰 증거가 필요합니다.

### 4. 안전 선택기와 인과 감사

<span style="background-color: #fff59d"><strong>안전 셀렉터는 개인화 루프 바깥에 있어서 원장이 안전 임계값을 움직일 수 없습니다</strong></span>. 인용된 메모리는 실제로 제거하고 재디코딩해서 영향력을 측정하는 counterfactual audit을 돕니다. <span style="background-color: #fff59d"><strong>감사 제거 시 evidence F1이 0.79에서 0.58로 떨어집니다</strong></span>.

## 아키텍처가 남는 몫

같은 6클래스 라벨과 히스토리로 학습된 지도 Transformer-Δt가 69.3% win rate, 15.9% poisoning까지 따라옵니다. 개선의 대부분이 지도 신호에서 나온다는 뜻입니다. 그 위에 아키텍처가 남기는 몫은 <span style="background-color: #fff59d"><strong>win rate 2.2점, poisoning 4.4점으로 통계적으로 유의</strong></span>했습니다(p=0.011, p=0.003).

## 적응형 공격자에는 답이 없다

가장 솔직한 부분입니다. 가중치를 공개된 상태에서 적응형 공격자가 붙으면 <span style="background-color: #fff59d"><strong>poisoning이 11.5%에서 24.7%로 두 배 이상 오르고</strong></span>, 이 구간에서는 provenance 필터(22.1%)가 오히려 수치상 더 안전합니다. 저자는 유리한 쪽 수치만 보고하지 않고 둘 다 리포트합니다. 독립 레드팀 12팀의 외부 공격에서는 <span style="background-color: #fff59d"><strong>18.3%로 여전히 최저</strong></span>였습니다.

## 벤치마크 밖 검증

제너레이터 자기오버핏 의심을 피하려고 두 가지를 더 돌렸습니다. 독립 구축된 HorizonBench(6개월 시뮬레이션)에서 모순 해결 0.72 vs StateMem 0.65, 그리고 40명 실사용자 2–3주 히스토리 리플레이에서 win rate +4.5점, 만족도 4.1 vs 3.8. <span style="background-color: #fff59d"><strong>턴당 비용은 약 630ms</strong></span>입니다.

## 원문

- arXiv: https://arxiv.org/abs/2609.02265 (v1, 2026-09-02)
- 코드/가중치는 논문 공개 약속(supplementary 포함), 공격 제너레이터는 소속 연구자 요청 공개

![adaptation-security frontier](/images/2026-09-06-capture-preference-drift-memory-poisoning/fig-1-p3.png)
*Figure 1. 적응-보안 프론티어 (원문 Figure 1)*

![CAPTURE pipeline](/images/2026-09-06-capture-preference-drift-memory-poisoning/fig-2-p19.png)
*Figure 2. 이벤트가 CAPTURE를 통과하는 경로 (원문 Figure 2)*

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

**Q: 취향 변화와 메모리 포이즈닝이 왜 구분이 어려운가요?**
두 경우 모두 기존 신념과 모순되는 문장이 컨텍스트에 등장한다는 같은 관찰을 만들기 때문입니다. 출처 채널이 사용자여도 사용자가 붙여넣은 외부 문서일 수 있어서 채널 라벨만으로는 부족합니다.

**Q: provenance 필터로 충분하지 않나요?**
간접 주입에는 강한 편이지만 same-origin 오염에서는 43.6%까지 무너지고, 정당한 취향 변화 수용률도 74.1%로 낮아 개인화 품질이 떨어집니다. CAPTURE는 17.5% / 83.5%로 두 축을 동시에 잡습니다.

**Q: 적응형 공격자 앞에서도 안전한가요?**
아니요. 24.7%까지 오르면 provenance 필터(22.1%)와 통계적으로 구분되지 않습니다. 대신 수용률 83.5% 대 74.1%의 개인화 품질 차이는 유지됩니다.

**Q: 실서비스 비용은 어떻게 되나요?**
턴당 약 630ms가 추가됩니다. 인과 감사의 재디코딩이 가장 비싼 부분입니다.
