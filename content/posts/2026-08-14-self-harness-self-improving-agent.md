---
title: "Self-Harness: 에이전트가 자기 하네스를 직접 고치는 루프"
date: 2026-08-14
tags:
  - agent
  - harness
  - LLM
  - self-improvement
  - regression-testing
  - Terminal-Bench
  - SWE-bench
  - AppWorld
  - automation
  - loop
---

결론부터. 상하이 AI랩(Shanghai AI Laboratory)이 공개한 Self-Harness에서 에이전트가 자기 하네스를 스스로 고치는 루프를 제안했고, <span style="background-color: #fff59d"><strong>모델 3종 × 벤치마크 3종 = 9개 조합 전부에서 통과율이 올라갔다</strong></span>. 최대 상승폭은 <span style="background-color: #fff59d"><strong>+40.6%p (GLM-5, AppWorld 44.4→85.0)</strong></span>. 최대 상대율은 <span style="background-color: #fff59d"><strong>+132% (Qwen3.5-35B-A3B, AppWorld 22.5→52.2)</strong></span>.

사람 엔지니어도, 더 강한 외부 모델도 안 씁니다. <span style="background-color: #fff59d"><strong>고치는 주체와 고쳐지는 대상이 같은 모델입니다</strong></span>.

논문: Self-Harness: Harnesses That Improve Themselves (arXiv 2606.09498, v2 2026-08-12)

## 루프 구성

![하네스 개선의 세 가지 패러다임 비교](/images/2026-08-14-self-harness-self-improving-agent/fig-1-p2.png)

기존엔 두 방식이 있었다구요. 사람이 하네스를 손으로 다듬거나, 강한 외부 에이전트가 약한 쪽 하네스를 고쳐주거나. Self-Harness는 세 번째 방식입니다. 당사자가 자기 하네스를 고친다.

한 바퀴는 3단계.

- 약점 채굴(Weakness Mining): 현재 하네스로 과제를 돌리고, 실패한 실행 궤적을 클러스터링해서 반복 실패 패턴을 뽑는다
- 하네스 제안(Harness Proposal): 패턴마다 걸리는 최소 수정안을 여러 개 만든다
- 수정 검증(Proposal Validation): 회귀 테스트를 돌리고 조건을 통과해야 승인

핵심은 이겁니다. 승인 규칙. <span style="background-color: #fff59d"><strong>Δ(held-in) ≥ 0, Δ(held-out) ≥ 0, 둘 중 하나는 &gt; 0</strong></span>. 이 조건을 못 넘기면 수정은 버려지고 하네스는 그대로 유지됩니다.

![Self-Harness 최적화 루프 개요](/images/2026-08-14-self-harness-self-improving-agent/fig-2-p5.png)

## 실험 설정

- 모델: MiniMax M2.5, Qwen3.5-35B-A3B, GLM-5
- 벤치마크: Terminal-Bench-2.0 (고정 64과제), SWE-bench Verified (100건, 67 held-in / 33 held-out), AppWorld (180건, 90 / 90)
- 시작점: DeepAgent 기반 최소 하네스

<span style="background-color: #fff59d"><strong>가중치는 고정입니다. 바뀌는 건 하네스만.</strong></span>

## 결과 수치

![초기/최종 하네스의 held-in·held-out·전체 통과율](/images/2026-08-14-self-harness-self-improving-agent/table-1-p11.png)

Terminal-Bench-2.0:

| 모델 | held-in | held-out |
|---|---|---|
| MiniMax M2.5 | 43.0 → 50.0 | <span style="background-color: #fff59d"><strong>40.5 → 61.9</strong></span> |
| Qwen3.5-35B-A3B | 15.1 → 36.0 | 23.8 → 38.1 |
| GLM-5 | 47.7 → 57.0 | 42.9 → 57.1 |

SWE-bench Verified 전체: 46.0→52.5 / <span style="background-color: #fff59d"><strong>19.5→41.5</strong></span> / 52.0→55.5

AppWorld 전체: 48.6→58.9 / 22.5→52.2 / <span style="background-color: #fff59d"><strong>44.4→85.0</strong></span>

<span style="background-color: #fff59d"><strong>9개 조합 전부 held-in·held-out 동반 상승입니다</strong></span>. 트레이스를 제안자에게 안 보여준 held-out에서 <span style="background-color: #fff59d"><strong>상대 상승폭이 더 큰 조합도 4개 있어요</strong></span>. 본 적 없는 과제에도 수정이 이전됩니다.

## 모델별로 다르게 고쳐진 지점

<span style="background-color: #fff59d"><strong>같은 루프를 돌렸는데 수정 지점이 모델마다 다르게 나옵니다</strong></span>. 이게 논문에서 가장 흥미로운 관찰이다.

- MiniMax M2.5: <span style="background-color: #fff59d"><strong>필요한 출력 파일을 일찍 만들기</strong></span>, 구조화 도구 출력 꼼꼼히 다루기, 막힌 도구 루프 끊기
- Qwen3.5-35B-A3B: 의존성 미리 점검, 실패한 명령 반복 금지, 무한 탐색 사이클 끊기, 도구 에러 후에도 산출물 남기기
- GLM-5: <span style="background-color: #fff59d"><strong>셸 명령 사이 환경 설정 유지</strong></span>, 탐색에서 구현·테스트로 빨리 전환

국소 수정만 나온 건 아니다. SWE-bench에선 <span style="background-color: #fff59d"><strong>diff 점검 서브에이전트와 패치 검증 서브에이전트</strong></span>가, AppWorld에선 상태 감사 서브에이전트와 페이지네이션 가드가 하네스에 추가됐습니다.

![모델별 대표 진화 궤적](/images/2026-08-14-self-harness-self-improving-agent/fig-4-p12.png)

## 내 해석과 주의점

- 하네스가 모델마다 다르게 수렴한다는 건 <span style="background-color: #fff59d"><strong>정답 하네스가 없다는 증거</strong></span>다. 모델·과제 조합마다 다시 맞춰야 합니다
- 승인 규칙(회귀 게이트)이 루프의 안전장치인데, <span style="background-color: #fff59d"><strong>이 게이트를 돌리는 것도 같은 시스템이라 평가 게이밍 여지는 남는다</strong></span>. 논문이 이 리스크를 명시적으로 다루지는 않습니다 (여기서부터 내 판단)
- 루프 계산 비용, 여러 라운드 수정이 안전하게 쌓이는지에 대한 분석은 이번 버전에 없다
- <span style="background-color: #fff59d"><strong>터미널·코딩·앱 조작처럼 검증기가 있는 과제에 한정된 결과다</strong></span>

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
