---
title: "QCR: 에이전트 트레이토리 메모리에서 재사용 단계가 별도 병목이다"
date: 2026-08-15
tags:
  - LLM
  - agent
  - memory
  - trajectory-reuse
  - retrieval
  - WebArena
  - AppWorld
  - harness
source: arxiv
source_url: https://arxiv.org/abs/2608.12847
paper_url: https://arxiv.org/html/2608.12847v1
---

arXiv:2608.12847 "Beyond Retrieval: Query-Conditioned Reuse of Long-Horizon Agent Trajectories"(2026-08-14, Yifei Li 외 8인) 정리했습니다. 핵심은 이겁니다. <span style="background-color: #fff59d"><strong>에이전트 메모리에서 검색기가 과거 트레이토리를 잘 찾아와도, 그걸 지금 쿼리에 맞게 다시 쓰는 단계가 따로 있고 병목은 거기에 있습니다</strong></span>.

이 논문은 그 재사용 단계만 분리해서 측정하는 프레임워크를 만들었구요, 테스트용 최소 구현인 QCR 노트로 <span style="background-color: #fff59d"><strong>평균 62.3% Success, Full Trajectory 대비 +10.7pt, 온라인 토큰 48.9% 감소</strong></span>를 냈습니다.

평가는 WebArena · WorkArena · AppWorld의 <span style="background-color: #fff59d"><strong>2,391개 타깃 인스턴스</strong></span>로 했습니다.

## 개요

기여는 세 가지입니다.

1. 후보 검색, 타깃 상태, 모델, 디코딩, 도구 예산을 고정하고 에이전트에 전달되는 지원물(support)만 변경하는 통제 평가 프레임워크
2. 테스트용 최소 구현인 QCR(Query-Conditioned Reuse) 노트: 워크플로 불변식, 재획득 바인딩, 적용 조건, 검증 가드레일의 4필드
3. 메모리 표현 비교와 트레이토리 길이·바인딩 시프트 분석

## 문제 정의와 평가 프레임워크

![](/images/2026-08-15-qcr-query-conditioned-reuse-agent-trajectories/fig-1-p1.png)

Figure 1은 설계 가설을 담고 있습니다. 메모리가 쌓이면 저장과 검색은 잘 되는데, 찾아온 기록을 변경된 타깃에서 쓰는 일이 새 병목이 된다는 관찰입니다. 사용자가 바뀌고, 엔티티 ID가 바뀌고, 환경 상태가 바뀐 타깃에서 과거 기록은 그대로 쓸 수 없습니다.

![](/images/2026-08-15-qcr-query-conditioned-reuse-agent-trajectories/fig-2-p4.png)

평가 파이프라인은 Figure 2 한 장으로 정리됩니다.

- 오프라인 — 검증된 과거 트레이토리를 통합 뱅크에 저장
- 온라인 — 검색기가 타깃 쿼리로 상위 5개 후보를 반환
- 공통 랭커 — 후보 설명만 보고 소스 기록 1개를 선택. 모든 메모리 조건에서 동일
- 메모리 조건 — 같은 기록을 어떻게 변환해서 넘길지만 변경
- 실행 — 타깃 Success, Milestone, API 호출 수, 온라인 토큰 측정

벤치마크도 이 목적에 맞춰 만들었습니다. 검증된 소스 트레이토리 하나에서 최대 4개의 타깃 변형을 생성하되, 워크플로는 유지하고 엔티티 · 사용자 · 레코드 ID · 파일 경로 · 날짜 같은 바인딩 값을 다른 발산 수준으로 교체합니다. 소스당 평균 3.84개 변형이 나왔구요, 절차는 같고 값이 다른 상황에서 메모리가 실제로 도움이 되는지를 측정할 수 있습니다.

## QCR 노트의 4개 필드

QCR은 검색 뒤에 딱 하나의 연산을 끼워넣습니다. 선택된 소스 트레이토리를 타깃 쿼리와 초기 관찰에 조건지어 짧은 노트로 재작성하는 겁니다. 필드는 네 개입니다.

1. 워크플로 불변식(workflow invariant) — 소스와 타깃이 공유하는 절차. 예: "검사 → 검증 → 수정 → 재확인"
2. 재획득 바인딩(bindings to re-obtain) — 타깃에서 반드시 새로 확인해야 하는 값
3. 적용 조건(applicability conditions) — 재사용 가능 조건과 거절 조건
4. 검증 가드레일(verification guardrail) — 제출 전 확인 항목

작성 규칙이 엄격합니다. <span style="background-color: #fff59d"><strong>과거 식별자 · 경로 · 사용자 · 날짜 · 도구 출력은 전부 소스 쪽 증거로만 취급하고, 과거 바인딩을 타깃에 복사하는 걸 금지</strong></span>합니다.

타깃 정답 추론과 도구 호출도 금지구요, 노트는 검색 집합보다 확실히 짧아야 하고 타깃 정답을 누설하면 안 됩니다.

## 종단 성능 (Table 1)

Table 1, 2,391개 타깃 평균 Success(%)입니다.

| 메모리 조건 | WebArena | WorkArena | AppWorld | API 호출 | 온라인 토큰 |
| --- | --- | --- | --- | --- | --- |
| 메모리 없음 | 31.5 | 36.6 | 47.1 | 24.6 | 15.2k |
| Generic Summary | 40.2 | 45.9 | 57.6 | 20.8 | 8.1k |
| Full Trajectory | 43.8 | 49.6 | 61.4 | 21.9 | 18.4k |
| QCR 노트 | 54.7 | 60.4 | 71.8 | 16.7 | 9.4k |

읽을 포인트 세 개입니다.

- QCR은 세 벤치마크 전부에서 최고입니다. <span style="background-color: #fff59d"><strong>WebArena 31.5 → 54.7, WorkArena 36.6 → 60.4, AppWorld 47.1 → 71.8</strong></span>
- Full Trajectory는 토큰을 가장 많이 쓰면서(18.4k) 성능은 QCR보다 낮습니다.
- QCR은 API 호출도 가장 적습니다(16.7). Milestone 완수율도 70.6 / 74.8 / 82.9로 전 구간 최고입니다.

## 선택 진단: 리랭커는 오라클과 1.8pt 차이

![](/images/2026-08-15-qcr-query-conditioned-reuse-agent-trajectories/fig-3-p7.png)

Figure 3이 왜 요약 리랭킹이 필요한지 보여줍니다. 상위 5개 후보의 쌍 커버리지는 95.6%, 재사용 커버리지는 97.8%로 충분한데, 검색기 top-1의 쌍 정확도는 78.9%에 그칩니다. 그래서 후보 설명을 다시 읽어 재사용 가능성을 판정하는 요약 리랭커를 넣었구요, <span style="background-color: #fff59d"><strong>최종 재사용 가능 메모리 정확도 94.8%</strong></span>를 냈습니다.

종단 Success는 검색기 top-1 그대로 56.1%, 무작위 44.8%, 리랭커 선택 62.3%, 오라클 재사용 선택 64.1%입니다. <span style="background-color: #fff59d"><strong>리랭커가 오라클과 1.8pt 차이</strong></span>까지 갑니다. 선택 문제는 거의 풀렸구요, 남는 격차는 사용 쪽에서 난다는 근거입니다.

## 트레이토리 길이에 따른 효용

Table 2입니다. 값은 같은 구간의 메모리 없음 대비 Success 변화(pt)입니다.

| 조건 | 짧은 트레이토리 | 아주 긴 트레이토리 | 짧을 때 대비 유지율 |
| --- | --- | --- | --- |
| Full Trajectory | +18.4 | +2.9 | 15.8% |
| Generic Summary | (낮은 출발) | (낮은 유지) | 32.4% |
| QCR 노트 | (높은 출발) | +13.2 | 60.3% |

Full Trajectory는 히스토리가 길어지면서 효용이 +18.4pt에서 +2.9pt로 떨어집니다. QCR도 길어지면 도움이 줄긴 하는데 아주 긴 구간에서도 +13.2pt를 유지합니다. 논문도 명시하길, 길이 그룹마다 메모리 없음 난이도가 달라서 이 표는 등록된 구성 하의 연관 관계지 길이만의 인과 추정은 아닙니다.

## 바인딩 시프트에 따른 효용

Table 3이 결정적인 결과입니다. 소스-타깃 간 바인딩 교체 규모에 따른 효용입니다.

| 조건 | 시프트 없음 | 대규모 시프트 | 유지율 |
| --- | --- | --- | --- |
| Full Trajectory | +26.9 | +2.2 | 8.2% |
| Generic Summary | — | +5.3 | — |
| QCR 노트 | +29.6 | +20.1 | 67.9% |

바인딩이 안 바뀌면 통째 주입도 +26.9pt로 쌉니다. 대규모 시프트에서는 +2.2pt로 거의 사라지구요, QCR은 +20.1pt를 유지합니다.

실패 유형도 측정했습니다. 대규모 시프트에서 stale-binding 에러(소스 값이 타깃 관찰과 충돌하는 상태로 반복)는 <span style="background-color: #fff59d"><strong>Full Trajectory 46.9% → QCR 10.9%</strong></span>로 낮아집니다.

올바른 재바인딩 비율은 <span style="background-color: #fff59d"><strong>31.7% → 77.8%</strong></span>로 올라갑니다. 원문 표현으로는, 방법이 바인딩 시프트를 없애는 게 아니라 낡은 소스 값이 현재 과제 증거를 밀어내는 속도를 줄이는 겁니다.

## 내 해석: 하네스에 적용할 포인트

여기부터는 제 해석입니다. 원문 근거와 구분해서 읽으시면 됩니다.

- Generic Summary는 대규모 시프트에서 +5.3pt에 그칩니다. <span style="background-color: #fff59d"><strong>요약이 아니라 쿼리 조건화(conditioning)가 효용의 본체</strong></span>라는 걸 숫자가 보여줍니다.
- 트레이토리/스킬 카드를 쌓는 시스템이라면 카드에 "이 값은 타깃에서 다시 얻어라" 필드와 거절 조건을 명시하는 것만으로 stale copy 실패를 크게 줄일 수 있습니다.
- 컨텍스트 예산이 빠듯한 로컬/온프레미스 에이전트에서는 토큰 48.9% 절감이 곧 비용 절감입니다. 성능과 비용이 같은 방향으로 움직이는 케이스라 흔치 않습니다.

## 한계

- QCR은 재사용 가설 검증용 최소 구현이며, <span style="background-color: #fff59d"><strong>보편적으로 최적인 메모리 스키마를 주장하는 게 아닙니다</strong></span>. 4필드 자체가 구현 선택입니다.
- 길이 분석은 등록된 구성에서의 측정이고, 길이만 분리한 인과 실험이 아닙니다.

## 더 실습해보고 싶은 분들께

에이전트 메모리 · 트레이토리 재사용 · 하네스 루프를 직접 굴려보고 싶다면 두 개 먼저 보시면 됩니다.

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- 원문: Beyond Retrieval: Query-Conditioned Reuse of Long-Horizon Agent Trajectories (arXiv:2608.12847, 2026-08-14)
- 본문 그대로 보기: https://arxiv.org/html/2608.12847v1
- Figure 1–3, Table 1–3은 원문에서 캡션 앵커로 잘라 썼습니다.
