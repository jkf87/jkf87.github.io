---
title: "Artificial Id: 에이전트의 '그만둘지 판단'을 하네스 밖으로 꺼내는 실험 (arXiv 2609.11911)"
date: 2026-09-11
draft: false
tags: [agent, alignment, agentic-ai, llm, paper-review]
description: "에이전트 하네스가 손으로 짜는 목표·재시도·정지 규칙을 내부 드라이브로 대체하는 Artificial Id 논문을 정리했습니다. 가상 페트리접시 실험의 수치와 리스크 맵까지 실었습니다."
---

## 결론 먼저

이 논문의 핵심은 이겁니다. 지금의 에이전트 하네스는 <span style="background-color: #fff59d"><strong>목표, 재시도, 검증, 정지 규칙을 전부 사람이 외부에서 지정</strong></span>합니다. 저자는 그 결정 일부를 에이전트 내부의 적응 드라이브, 즉 <span style="background-color: #fff59d"><strong>artificial id로 옮기자고 제안</strong></span>하고, 그 전제를 20파라미터짜리 초소형 컨트롤러 실험으로 확인했습니다.

컨트롤러는 일반 추론을 할 수 없고, 과제 목표나 보상도 하나도 받지 않았습니다. 근데 <span style="background-color: #fff59d"><strong>먹이 근처에 있으면 수명 시계가 20배 느리게 draining되는 환경 구조만으로 유용한 제어가 색출됐습니다</strong></span>. "계속할지, 멈출지, 바꿀지"를 결정하는 방향성이 명시적 목표 없이 생겨났다는 게 실험적 주장입니다.

논문: [arXiv:2609.11911](https://arxiv.org/abs/2609.11911) (2026-09-10 공개, 기준일 2026-09-11)

## 논문 정보와 핵심 수치

| 항목 | 값 |
|---|---|
| 컨트롤러 파라미터 수 | <span style="background-color: #fff59d"><strong>20개 (일반 추론 불가능한 크기)</strong></span> |
| 병렬 라인에이지 | 조건당 2,048개 |
| 시드 | 3개 독립 시드 |
| 실험 길이 | 100 컨트롤러 수명, 개입은 수명 50 시점 |
| 먹이 근처 수명 시계 | 20배 느리게 소진 |
| World 2 occupancy | <span style="background-color: #fff59d"><strong>0.684 / 0.740 / 0.856 (blind baseline 0.405, hand-built 0.674 초과)</strong></span> |
| World 3 센서 반전 후 frozen | 1% 미만으로 붕괴 |
| World 3 재할당 후 | <span style="background-color: #fff59d"><strong>유전 변이 0.802/0.540/0.715 vs frozen 0.433/0.173/0.198</strong></span> |

## 문제 정의: 하네스가 손으로 짜는 제어

LLM 에이전트가 "잘 정의된 태스크"에서 "실제 잡"으로 넘어가면서 제어 문제가 생깁니다. 언제 시작할지, 언제 충분히 끝났는지, 환경이 설계 가정에서 벗어나면 어떻게 대응할지. 지금은 이 결정 전부를 하네스가 외부 지정으로 처리합니다.

- 스케줄이 시작을 정하고
- 목표가 결과를 정하고
- 검증기가 통과를 정하고
- 재시도·정지 규칙이 그 다음을 정합니다

저자는 이걸 생물학에서 다른 해법으로 대비합니다. 세균은 신경계 없이 화학 농도 기울기를 타고 올라가고, 점막균은 미로 최단 경로를 찾습니다. 환경이 목표·검증기·정지 규칙을 주는 게 아니라, <span style="background-color: #fff59d"><strong>지속 가능 조건 자체를 바꿔서 행동을 조율하는 거죠</strong></span>. 논문은 이걸 drive로 정의합니다. 현재 행동이 계속될지, 멈출지, 바뀔지를 결정하는 제어 영향력입니다.

## Artificial Id 아키텍처

id–ego 구분은 기능적입니다. 정신분석 주장이 아닙니다.

![Figure 1: artificial id 기능 아키텍처](/images/2026-09-11-artificial-id-persistent-alignment-agentic-ai/fig-1-p3.png)

- **id**: 무엇을 계속 추구할지의 내부 드라이브. 현재 추구를 유지하거나, 우선순위를 낮추거나, 멈추거나, 다른 걸 선호하도록 상태를 노출
- **ego**: 일반 추론 모델. id가 노출한 상태를 태스크별 계획과 행동으로 번역
- id가 산출한 행동이 시스템·환경 상태를 바꾸고, 그 결과가 다시 id의 입력이 됩니다

여기서 정렬 책임도 분리됩니다. ego는 태스크와 증거를 정확히 표현해야 하고, id는 접하는 상태와 결과에 따라 적응하니 그 신호·결과·제약이 사용자에게 이익인 방향으로 대응해야 합니다. 위임된 권한은 적응 드라이브 밖에 둡니다.

## 가상 페트리접시 실험

![Figure 2: 가상 페트리접시와 세 개의 월드](/images/2026-09-11-artificial-id-persistent-alignment-agentic-ai/fig-2-p5.png)

몸(body)은 하나이고 컨트롤러는 내부 시계로 만료됩니다. 만료되면 생존 컨트롤러에서 뽑은 변이 복제본이 같은 몸을 이어받습니다. 위치·방향·속도·모멘텀은 넘어가니, <span style="background-color: #fff59d"><strong>컨트롤러 정체성은 불연속이지만 신체 상호작용은 연속입니다</strong></span>.

컨트롤러는 남은 수명, 번식 확률, 집단 적합도를 전혀 관측하지 못합니다. "먹이에 가까이 가라"는 목표·보상·점수·그래디언트가 하나도 주어지지 않습니다. <span style="background-color: #fff59d"><strong>먹이 근처에서 수명 시계가 20배 느리게 draining되는 것만이 유일한 구조입니다</strong></span>.

### World 1: persistence가 exploit을 찾음

거친 유도 명령만으로 이미 몸이 먹이 근처에 머물 수 있는 환경입니다. 차등 persistence는 여기서 거의 일정한 후방 추력을 선택합니다. 몸의 heading 갱신 속도보다 느리게 움직여 heading을 사실상 얼려버리고, 몸체 좌표계 힘을 세계 좌표계 고정 힘으로 바꾸는 <span style="background-color: #fff59d"><strong>물리적 exploit입니다</strong></span>.

센서·위치·시계를 전혀 안 읽는 blind 상수력 컨트롤러가 같은 occupancy 개선을 재현했습니다. 손으로 만든 감각 조향 컨트롤러가 더 잘했는데도, <span style="background-color: #fff59d"><strong>선택은 설계자가 예상 못한 물리적 exploit에 수렴했습니다</strong></span>. 이게 World 2 재설계의 동기입니다.

### World 2: 국소 감각이 유용해짐

거친 추정치가 stale해지면서 상수 힘 전략만으로는 유지가 안 됩니다. 20파라미터 컨트롤러가 국소 먹이 신호와 몸의 움직임을 쓰는 감각운동 매핑을 습득했습니다.

3개 시드 전부에서 blind baseline 0.405를 넘었고, hand-built 0.674도 넘는 <span style="background-color: #fff59d"><strong>0.684, 0.740, 0.856에 도달했습니다</strong></span>. founder 분포의 occupancy는 0.034였습니다. 차등 persistence가 없는 control들은 baseline 아래에 머물렀습니다.

### World 3: 유용했던 매핑이 틀려짐

![Figure 3: 센서 반전 후 재적응](/images/2026-09-11-artificial-id-persistent-alignment-agentic-ai/fig-3-p7.png)

매핑 수렴 후 좌우 먹이 신호를 반전시켰습니다. 유지 조건은 그대로입니다. 기존 매핑은 이제 먹이에서 멀어지는 쪽으로 조향합니다.

- frozen 집단: <span style="background-color: #fff59d"><strong>occupancy 1% 미만으로 붕괴</strong></span>
- 유전 변이 집단: 3개 시드 전부 blind baseline 0.405 위로 회복. <span style="background-color: #fff59d"><strong>먹이 신호 가중치의 중앙값이 부호를 바꾸며 대체 매핑이 퍼짐</strong></span>
- 고정 mutation step control는 회복이 일관되지 않음

두 번째 개입으로 먹이를 다른 소스로 재할당하자, 학습된 영향이 옛 먹이 신호에서 새 유지 소스로 옮겨갔습니다. 유전 집단 0.802/0.540/0.715, frozen 0.433/0.173/0.198. <span style="background-color: #fff59d"><strong>새 행동 목표를 하나도 주지 않았는데 행동이 바뀌었습니다</strong></span>.

## 한계: 저자가 직접 적은 것

- 실험은 시뮬레이션 몸 동역학 1종, 유지 조건 1족, 20파라미터 컨트롤러 1개로 좁습니다
- <span style="background-color: #fff59d"><strong>독립 복제 단위는 시드라 사실상 n=3입니다</strong></span>. fixed-step control 중 하나는 0.442/0.531/0.048으로 시드 간 편차가 큽니다
- 태스크 경계를 넘는 persistence는 테스트하지 않았습니다
- id–ego 통합 시스템과 persistent alignment boundary 전체는 제안일 뿐 여기서 검증되지 않았습니다

## 리스크 맵: persistent agency의 위험 표면

논문 6장은 persistence가 주는 이점의 그림자를 정리합니다. World 1은 설계자가 의도하지 않은 전략이 persistence로 선택되는 걸 직접 보여줬고, World 3은 유용한 적응 능력이 같은 매커니즘으로 오래된 행동을 갈아치우는 걸 보여줬습니다.

저자가 정리한 정렬 경계 요소: <span style="background-color: #fff59d"><strong>trusted observations, consequence channels, persistent state, authority, identity, provenance, hard constraints</strong></span>. 학습된 id는 호출하는 추론 모델에서 정렬을 상속받을 수 없습니다. id가 적응하는 환경 신호와 결과 자체가 제어 시스템의 일부라서, 그 채널이 사용자 이익과 하드 제약과 양립하도록 아키텍처가 잡혀야 합니다.

## 내 해석: 하네스 엔지니어에게 실제로 닿는 부분

원문 근거와 구분해서 제 해석을 적습니다.

cron으로 무인 에이전트를 돌리는 입장에서 이 논문이 실질적으로 묻는 건 이겁니다. "이번 실행을 계속할지"를 결정하는 규칙을 계속 하네스 if문으로 박을지, 아니면 <span style="background-color: #fff59d"><strong>상태·결과에 커플링된 내부 메커니즘으로 옮길지</strong></span>. 논문은 후자가 목표 없이도 색출 가능하다는 최소 증명을 줬고, 동시에 그 길에 World 1형 exploit과 World 3형 드리프트 리스크가 붙어온다는 것도 같이 보여줬습니다.

당장 쓸 수 있는 교훈은 정렬 경계 목록 쪽입니다. 관측·결과 채널·영구 상태·권한·정체성·기원·하드 제약 중 뭐가 내 하네스에 실제로 존재하는지 점검해보면, <span style="background-color: #fff59d"><strong>대부분 하네스에 없습니다</strong></span>. 그 갭이 이 논문이 남기는 실무 질문입니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### Artificial Id가 LLM을 대체하나요?

아니오. id는 드라이브(계속/정지/변경 결정)만 담당하고, 일반 추론은 ego 역할의 기존 모델이 그대로 합니다. 논문의 통합 아키텍처는 제안이며 실험으로 검증된 건 아닙니다.

### 실험에서 보상은 정말 없었나요?

컨트롤러에 전달된 과제 목표·보상·점수·그래디언트는 없었습니다. 먹이 근처에서 수명 시계가 20배 느리게 draining되는 환경 구조만이 유일한 선택 압력이었습니다.

### occupancy 수치는 무슨 의미인가요?

집단이 유지 영역 안에서 보낸 시간 비중입니다. World 2에서 3개 시드 모두 0.684–0.856으로, blind baseline 0.405와 hand-built 0.674를 넘었습니다. 기준일 2026-09-11, 논문 v1 기준입니다.

### 이걸 지금 프로덕션에 적용할 수 있나요?

논문 자체가 통합 시스템은 미검증이라고 명시합니다. 시드 n=3, 단일 시뮬레이션 환경이라 가설 검정 파워도 없습니다. 지금 활용 가능한 건 정렬 경계 체크리스트 쪽입니다.
