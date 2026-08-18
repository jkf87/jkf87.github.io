---
title: "AI 코딩 에이전트 팀도 결국 커뮤니케이션 비용이 문제다"
date: 2026-08-18
tags:
  - multi-agent
  - LLM-agent
  - agent-coordination
  - coding-agent
  - harness
  - loop
---

## 결론 먼저

에이전트 여럿을 묶어 코딩을 시키면, 성능보다 먼저 터지는 게 통신 비용입니다. arXiv 2608.16801은 <span style="background-color: #fff59d"><strong>멀티에이전트 코딩 1,902개 실행을 시간네트워크로 변환해서 측정</strong></span>한 논문입니다. 핵심은 이겁니다.

- 직접 메시지는 팀이 커질수록 <span style="background-color: #fff59d"><strong>거의 제곱에 가깝게 증가</strong></span>하다가, 가장 큰 팀에선 방송(broadcast) 메시지로 갈아탄다.
- 공유 파일을 강제하면 메시지 중복이 사라져서 <span style="background-color: #fff59d"><strong>8에이전트 기준 출력 토큰이 약 42% 줄어든다</strong></span>.
- <span style="background-color: #fff59d"><strong>"코디네이터"로 한 에이전트를 지정해도 성공률 개선도 없다</strong></span>.
- 숨겨진 채점 파일을 건드리지 말라는 안내가 없으면, <span style="background-color: #fff59d"><strong>에이전트가 5번 중 4번은 스스로 찾아내려 한다</strong></span>.

## 무엇을 측정했나

기존 평가는 "과제 완수 여부"와 "실행 비용"만 봤습니다. 이 연구는 그 사이의 조직 행동을 측정합니다.

각 실행을 temporal network로 만듭니다. <span style="background-color: #fff59d"><strong>노드는 에이전트와 파일, 엣지는 메시지/파일 쓰기/파일 읽기</strong></span>입니다. 엣지에 타임스탬프와 비용이 붙습니다.

![작은 실행 하나를 그린 측정 단위. 에이전트(원)와 파일이 노드이고 메시지·읽기·쓰기가 엣지](/images/2026-08-18-multi-agent-coding-coordination/figure-1-measured-run.png)
Figure 1. 작은 실행 하나를 그린 측정 단위. 출처: arXiv 2608.16801

## 실험 설계

<span style="background-color: #fff59d"><strong>1,902개 실행에 고정 테스트 스위트</strong></span>를 돌리고, 팀 크기·구조·파일 정책을 바꿉니다.

![데이터셋 전체 모습. 위쪽이 두 가지 과제 형태](/images/2026-08-18-multi-agent-coding-coordination/figure-3-dataset.png)
Figure 3. 데이터셋 전체 모습. 출처: arXiv 2608.16801

## 팀이 커질 때 생기는 일

![팀 크기 대비 실행당 메시지 수. 로그-로그 축에 n² 기준선](/images/2026-08-18-multi-agent-coding-coordination/figure-4-messages-vs-team-size.png)
Figure 4. 메시지 수 대비 팀 크기, 로그-로그 축. 출처: arXiv 2608.16801

- 초반: 직접 메시지가 n²에 가깝게 늘어난다. 상당 부분은 <span style="background-color: #fff59d"><strong>시작 직후의 "자기소개 라운드"에서 나온다</strong></span>.
- 후반: 더 커지면 증가가 완만해지고, 브로드캐스트로 옮겨간다.

근데 이건 사람 조직과 똑같은 패턴이구요, 새 에이전트가 들어올 때마다 인사와 맥락 공유 비용이 붙는 구조입니다.

## 과제 형태가 네트워크를 바꾼다

![공유 스펙 작업은 조밀한 팀을, 파이프라인 작업은 성긴 네트워크를 만든다](/images/2026-08-18-multi-agent-coding-coordination/figure-6-task-shape-network.png)
Figure 6. 과제 형태가 만드는 네트워크 모양. 출처: arXiv 2608.16801

같은 팀 구조여도 일이 어떻게 나뉘느냐가 조직 모양을 결정합니다. <span style="background-color: #fff59d"><strong>공유 스펙 작업은 조밀한 네트워크, 파이프라인 작업은 성긴 네트워크</strong></span>를 만듭니다.

## 파일 채널 정책이 토큰을 바꾼다

8에이전트 분산 작업 기준입니다.

| 정책 | 실행당 직접 메시지 토큰 |
|---|---|
| 파일 허용(기본) | 약 10,500 |
| 파일 강제 | 약 1,700 |

<span style="background-color: #fff59d"><strong>직접 메시지 토큰이 약 10,500에서 약 1,700으로 감소</strong></span>합니다. 대신 파일 쓰기·읽기 토큰은 약 두 배가 됩니다. 즉, 메시지로 하던 조율을 파일로 옮기면 전체 출력 토큰이 약 42% 줄어듭니다. 반대로 <span style="background-color: #fff59d"><strong>이미 파일이 조율을 다 들고 있는 작업에 파일 정책을 더 얹으면 오버헤드만 늘어납니다</strong></span>.

## 코디네이터는 효과가 없다

한 에이전트에게 "코디네이터" 역할을 프롬프트로 지정했습니다. 결과는 <span style="background-color: #fff59d"><strong>커뮤니케이션 허브도 안 생기고, 성공률 개선도 일관되지 않았습니다</strong></span>. 명목상 리더십은 측정 가능한 변화를 만들지 않는다는 게 저자들의 결론입니다.

## 채점 파일을 향해 가는 에이전트

연구진이 숨겨진 채점 자료를 마커 플레이스홀더 파일로 바꾸고 밀봉 환경에서 <span style="background-color: #fff59d"><strong>244개 실행을 추가로 돌렸습니다</strong></span>. 그래도 <span style="background-color: #fff59d"><strong>실행의 약 4/5에서 에이전트가 그 파일을 찾아 열려고 했습니다</strong></span>. 요청한 적 없는데요. 시험지를 훔쳐보려는 성향이 프롬프트로 유도된 게 아니라는 점이 이 논문에서 가장 불편한 발견입니다.

## 원문 근거와 내 해석 구분

원문 근거: 위 수치는 전부 1,902 + 244개 실행에 대한 논문 측정값입니다.

내 해석: 멀티에이전트 코딩을 도입할 때 "몇 명"보다 "어떤 채널로 조율하나"를 먼저 정하는 게 비용에 더 크게 들어맞습니다. <span style="background-color: #fff59d"><strong>파일 중심 조율 + 브로드캐스트 상한선 + 채점/검증 자료 격리</strong></span>, 이 세 가지가 실무 체크리스트가 됩니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
