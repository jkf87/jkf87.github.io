---
title: "EvoUndo — 자기 진화하는 에이전트 하네스, 되돌릴 수 없으면 채택하지 않는다"
date: 2026-08-31
draft: false
tags: [agent, harness, self-evolution, safety, LLM]
description: "능력을 올리는 하네스 변형이어도 복구 검증을 통과하지 못하면 영구 적용하지 않는 조건부 자기진화 프레임워크 EvoUndo 정리. 197개 자연 실패 복구 실험 결과를 수치로 확인합니다."
---

## 개요

EvoUndo(Sah et al., arXiv:2608.28363, 2026)는 LLM 에이전트의 런타임 자기 수정(self-modification)에 복구 가능성(recoverability) 제약을 부여하는 프레임워크이다. <span style="background-color: #fff59d"><strong>능력을 개선하는 변형이라도 복구 검증을 통과하지 못하면 영구 적용하지 않는다</strong></span>는 것이 핵심 설계이다.

## 핵심 요약

600개 자기진화 태스크에서 능력은 개선되었지만 복구 검증에 실패한 변형은 <span style="background-color: #fff59d"><strong>197개</strong></span>였다. 이들을 기존의 반복적 수리 방식으로 복구하려 하면 <span style="background-color: #fff59d"><strong>0/197, 전부 실패</strong></span>한다.

복구 언어를 확장하면 오라클 기준 <span style="background-color: #fff59d"><strong>191/197</strong></span>까지 복구 가능해진다. 실패의 원인은 모델 능력이 아니었습니다. 표현력과 상태 주소 grounding이었습니다.

| 항목 | 값 |
|---|---|
| 자기진화 태스크 | 600개 (6계열 × 100) |
| 능력 개선 + 복구 실패 | 197개 |
| 기존 수리 방식 성공 | 0/197 (0.0%) |
| 기본 언어 L0 오라클 복구 가능 | 48/197 |
| 확장 언어 L1 오라클 복구 가능 | 191/197 |
| 정확 주소 grounding 시 S0 복구 | 0/48 → 38/48 (79.2%) |
| 언어 확장 시 S1 복구 | 142/143 (99.3%) |
| 주 모델 | gpt-oss-120b (MXFP4, H200 8대) |
| 기준일 | 2026-08-31, arXiv 2608.28363v1 (2026-08-28 공개) |

## 문제 정의

하네스는 H=(S, Π)로 모델링된다. 자기진화 단계는 변형 m: S→S'을 적용하며, 능력 목표 J에 대해 ΔJ>0일 때 능력 개선으로 간주된다.

그런데 정방향 개선만으로는 장기 운영 시스템에 부족하다. 변형이 설정값을 덮어쓰거나 미들웨어 순서를 변경한 경우, 사전 상태 정보 없이는 복구가 불가능하다. <span style="background-color: #fff59d"><strong>올바른 복구 절차는 상태 의존적이며, 필요한 정보는 변형 이전 상태에만 존재한다</strong></span>.

복구 가능성은 다음과 같이 정의된다. 증인 캡처 w: S→W와 복구 프로그램 u: S×W→S를 쓴다.

반사실 상태 분포 Q에서 Pr[u(m(s), w(s)) ≃ s] ≥ τ_R을 만족하는 (w, u)가 복구 언어 L에 존재해야 한다. ≃는 타입된 관측 동치이다. 복구 가능성은 <span style="background-color: #fff59d"><strong>변형을 만든 상태에서뿐 아니라 반사실(counterfactual) 상태에서도 성립해야 한다</strong></span>.

![Table 2: 진단 세분화(D) × 복구 언어(L) 2×2 팩토리얼 결과](/images/2026-08-31-evoundo-recoverable-self-evolution/table2-factorial.png)
*원문 Table 2 (p.7). 원문: arXiv 2608.28363v1*

## 방법론

후보는 (m, w, u, Ce) 4튜플로 표현된다. 구성요소는 다음과 같다.

- 효과 계약 감사: 런타임이 SnapshotDiff와 실행 트레이스로 실제 효과를 독립 계산한다. E(m,s) ⊆ Ce를 요구하고, <span style="background-color: #fff59d"><strong>관측된 효과를 계약에서 빼먹으면 감사에서 탈락한다</strong></span>.
- 반사실 왕복 검증: 개발 상태 10개, 숨김 상태 40개(IID 20 + OOD 20)에서 s→w→m→u→ŝ 왕복을 검사한다.
- 입장 기준: <span style="background-color: #fff59d"><strong>Wilson 95% 하한 신뢰구간 LCB ≥ 0.85</strong></span>.
- fail-closed 설계: 구문 오류, 예외, 언어 외 프리미티브는 즉시 거부된다.
- 수리 제한: <span style="background-color: #fff59d"><strong>정방향 변형 m은 불변으로 잠기고</strong></span> (w, u, Ce)만 수정 가능하다. 변형을 no-op으로 약화해 회피하는 것을 차단한다.

## 실험 결과

2×2 요인 실험(진단 세분화 D0/D1, 언어 L0/L1) 결과를 두 층으로 나눠 보면 이렇다.

- S0 층(48개): 정확 주소 grounding을 주면 <span style="background-color: #fff59d"><strong>0/48 → 38/48 (79.2%)</strong></span>로 회복.
- S1 층(143개): 언어를 확장하면 <span style="background-color: #fff59d"><strong>142/143 (99.3%)</strong></span> 회복.
- 전체 코호트 상호작용 효과: <span style="background-color: #fff59d"><strong>−25.89pp</strong></span>. gpt-oss-120b에서 정확한 주소 피드백이 확장 언어와 결합하면 오히려 성능을 낮췄다. Qwen3.8-27B 재현에서는 유의하지 않았다(모델 의존적).

신규 홀드아웃(300 태스크, 100 숨김 상태)에서는 정밀도-커버리지 트레이드오프가 그대로 나타났다. 개발 반사실 다양성을 Q2→Q20으로 늘리면 오탐이 <span style="background-color: #fff59d"><strong>16.8% → 0.0%</strong></span>으로 사라진다. 대신 수확이 49.7% → 35.0%로 떨어진다.

## 비교 및 한계

영향 범위가 알려진 경우 효과 범위 스냅샷이 우수하다(<span style="background-color: #fff59d"><strong>300/300 대 243/300</strong></span>). EvoUndo는 역산술이 없거나 상태 의존적 복구가 필요한 경우에 해당한다.

평균 저장/지연은 EvoUndo가 393.6 B / 0.050 ms로 풀 스냅샷(1165.0 B / 0.084 ms)보다 가볍다. 한계도 명시돼 있다. L0/L1 계산의 완전성 보장 부재, 분산 상태·외부 API 미커버, <span style="background-color: #fff59d"><strong>불가역 물리/금융 효과는 복구 대신 보상 의미론이 필요</strong></span>한 점, 모델 규모 다양성 부족이다.

## 실무 적용 관점

원문 근거와 구분하여 정리하면, 실무적으로 바로 쓸 수 있는 부분은 다음 두 가지다.

- 자기진화 파이프라인에 <span style="background-color: #fff59d"><strong>'undo 검증 게이트'를 앞단에 붙이는 설계</strong></span>. 변형 제출 시점에 사전 상태 증인 캡처와 복구 프로그램을 함께 요구하는 방식은 오늘 바로 적용 가능한 패턴이다.
- 진단 피드백 세밀화를 무조건 최대화하지 않을 것. 본 논문에서는 <span style="background-color: #fff59d"><strong>거친 진단 + 표현력 좋은 복구 언어 조합이 최고 효율(94.2%)</strong></span>이었다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### EvoUndo가 해결하려는 문제는 무엇인가요?
에이전트가 실행 중 자기 하네스(프롬프트, 도구, 미들웨어, 설정)를 바꿀 때 능력은 올라가도 나중에 안전하게 되돌릴 수 없는 변형이 생기는 문제입니다. 논문은 이를 복구 가능성 제약으로 formalize합니다.

### 왜 반복 프롬프팅으로는 복구가 되지 않았나요?
600태스크 코호트의 197개 자연 실패에서 기존 수리 방식은 0/197이었습니다. 원인이 상태 주소 정보 부족(grounding)과 복구 언어 표현력 부족이어서, 더 열심히 프롬프트해도 해결되는 종류의 실패가 아니었습니다.

### L0와 L1 복구 언어의 차이는 무엇인가요?
L0는 설정·프롬프트·도구 레지스트리·라우팅 상태를 다루고, L1은 여기에 미들웨어 순서, 이벤트 리스너, 샌드박스 파일, 관리 소켓, 순서 있는 복구 합성을 추가합니다. L1에서 오라클 복구 가능 범위가 48/197 → 191/197로 늘었습니다.

### 운영 환경에 바로 적용할 수 있나요?
모델링된 하네스 상태에 한정된 실험이며 분산 데이터베이스, 멀티호스트 상태, 외부 API, 불가역 효과는 커버하지 않습니다. 다만 변형 제출 시 증인 캡처와 왕복 검증 패턴 자체는 바로 적용 가능합니다.

## 참고 자료

- 원문: [EvoUndo: Recoverability-Constrained Self-Evolution for LLM Agent Harnesses (arXiv:2608.28363)](https://arxiv.org/abs/2608.28363)
- HTML 전문: https://arxiv.org/html/2608.28363v1
- 본문 표 이미지는 원문 Table 2(p.7) 캡처. 기준일: 2026-08-31.
