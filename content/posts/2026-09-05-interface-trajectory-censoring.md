---
title: 툴 호출 0개는 모델 탓이 아니라 인터페이스 탓일 수 있다
date: 2026-09-05
tags:
  - agent
  - evaluation
  - serving
  - tool-use
  - RL
  - benchmark
draft: false
description: 에이전트 벤치마크의 tool-call rate가 0이어도 모델이 정상 호출을 내보내고 있을 수 있습니다. 서빙 인터페이스의 템플릿-파서 계약 불일치로 호출이 사라지는 interface-induced trajectory censoring 현상을 arXiv 2609.03966 논문으로 정리했습니다.
---

## 결론 먼저

에이전트 벤치마크에서 <span style="background-color: #fff59d"><strong>tool-call rate가 0으로 나와도 모델이 도구를 못 쓰는 게 아닐 수 있습니다</strong></span>. 모델이 잘 포장된(well-formed) 툴 호출을 내보내고 있어도, 서빙 인터페이스의 채팅 템플릿과 파서 계약이 안 맞으면 그 호출은 실행 직전에 사라집니다.

<span style="background-color: #fff59d"><strong>서버는 HTTP 200과 빈 `tool_calls` 배열을 돌려줍니다</strong></span>. 겉에서 보면 "도구를 안 쓰는 모델"과 구분이 안 됩니다.

이 논문은 arXiv 2609.03966(2026-09-03 공개)입니다. 홍콩시립대학교 Wenbo Wang의 1인 연구이고, 이 현상에 이름을 붙였습니다. <span style="background-color: #fff59d"><strong>interface-induced trajectory censoring</strong></span>. 핵심 주장은 한 줄입니다. <span style="background-color: #fff59d"><strong>관측된 tool-call rate는 모델만의 속성이 아니라, 그것을 측정하는 model × interface 스택 전체의 속성이라는 것</strong></span>.

## 핵심 수치 요약

| 항목 | 수치 | 조건 |
|---|---|---|
| BFCL v4 점수 변화 | <span style="background-color: #fff59d"><strong>0.00 → 0.96 / 0.19</strong></span> | 가중치·케이스·시드 고정, 서빙 어댑터만 교체 |
| τ-bench 파싱된 호출 | <span style="background-color: #fff59d"><strong>0 → 636</strong></span> | 소매 115개 과업, 동일 교체 |
| τ-bench 실행 도달 과업 | 0 → 103 | 위와 동일 |
| Qwen2.5-Coder 서버 파싱 | <span style="background-color: #fff59d"><strong>0/100 (전체 스케일)</strong></span> | 21× 크기 범위에서 일관 |
| 32B에서 실제 방출된 정상 호출 | <span style="background-color: #fff59d"><strong>80/100 (~72 보정)</strong></span> | 서버는 여전히 0으로 기록 |
| 매칭 인벨로프 silent fraction | 0–2 | 실행 전 커밋된 사전등록 예측 |
| Llama-3.1-8B 잘못된 툴 지목 | <span style="background-color: #fff59d"><strong>23% → 0%</strong></span> | `strict: true` 플래그 하나 |
| verl AgentLoop 7B | <span style="background-color: #fff59d"><strong>45/115 생성물에 호출, 실행 0</strong></span> | RL 학습 루프 내부 |

기준일: 2026-09-03 arXiv v1 기준. 코드·데이터·사전등록은 GitHub `nebula-1999/Interface-Induced-Trajectory-Censoring`에 공개돼 있습니다.

## 연구의 시작점이 된 이상한 학습 커브

저자는 Qwen2.5-Coder-1.5B로 150 GRPO 스텝을 돌렸는데, 점수가 오르더라도 오른 게 전부 첫 턴에서 나왔다고 합니다. <span style="background-color: #fff59d"><strong>턴 2 이후의 복구는 스텝 0부터 150까지 6–9개로 평평했습니다</strong></span>. "1.5B는 멀티턴 복구를 못 배운다"가 자연스러운 해석이었죠.

<span style="background-color: #fff59d"><strong>실제로는 툴 호출이 한 번도 성공한 적이 없었습니다</strong></span>. 서버는 매번 HTTP 200을 돌려줬고, `tool_calls`는 빈 배열이었고, 학습 루프는 멀쩡한 싱글턴 트레젝토리를 기록하고 있었습니다. 아무도 알려주지 않았을 뿐입니다.

## 무슨 일이 벌어지나

에이전트 평가는 모델 하나를 재는 게 아니라 `모델 × 프로토콜 × 직렬화 × 파서 × 실행 스택`의 합성을 잽니다. 이 스택의 대부분 단계가 실패할 때 출력이 똑같다는 게 문제입니다. 파서가 모델이 내보낸 포맷을 인식 못 하면 서빙 계층은 툴 호출 0개를 보고합니다. 도구를 거부하는 모델이 내는 결과와 정확히 같습니다.

![Figure 1: 5단계 투명 퍼널](/images/2026-09-05-interface-trajectory-censoring/fig-1-p2.png)

Figure 1이 이 논문의 측정 단위입니다. 저자는 의도 / 방출 포맷 / 서버 파싱 / 실제 실행 / 멀티턴 복구 다섯 단계를 독립적으로 측정했고, 업계 관행은 그중 세 번째(서버 파싱)만 보고한다고 지적합니다.

## BFCL에서 0.00과 0.96이 같은 모델에서

실험 설계가 깔끔합니다. 가중치, 케이스, 디코딩, 시드를 전부 고정하고 서빙 어댑터 설정만 바꿨습니다. 결과는 BFCL v4에서 같은 모델이 0.00 또는 0.96 / 0.19를 기록했습니다.

2×2 요인 실험(채팅 템플릿 × 파서)으로 효과의 위치도 특정했습니다.

<span style="background-color: #fff59d"><strong>주효과(main effect) 둘 다 정확히 0이고, 전부 상호작용 항에 있었습니다</strong></span>. 어느 한쪽만 고쳐도 아무 소용이 없다는 뜻입니다. 체크포인트가 뭘 내보내도록 학습됐는지, 채팅 템플릿이 뭘 내보내라고 말하는지, 파서가 뭘 받아들이는지 — 세 당사자가 독립적으로 설정되는 계약이 실패 지점입니다.

파서를 버그로 보기엔 이르다는 점도 검증했습니다. 저자는 vLLM의 `hermes` 익스트랙터를 저장된 첫 턴 4,254개에 한 줄씩 리플레이했고, 서버 자신의 규칙이 받아들였을 호출을 <span style="background-color: #fff59d"><strong>놓친 사례는 0건이었습니다</strong></span>. Qwen2.5-Coder는 정상적인 bare JSON 호출을 내보내고 `<tool_call>` 인벨로프를 절대 안 쓰기 때문에, hermes가 이를 못 보는 건 올바른 동작입니다.

## 스케일이 커질수록 과소계수가 커진다

![Figure 4: 스케일별 과소계수](/images/2026-09-05-interface-trajectory-censoring/fig-4-p32.png)

Qwen2.5-Coder를 21× 스케일 범위로 걸쳐 프로브를 돌렸습니다. 서버는 모든 크기에서 0/100을 파싱했습니다. 근데 모델이 실제로 내보낸 정상 호출은 32B에서 80/100까지 올라갑니다. <span style="background-color: #fff59d"><strong>모델이 커질수록 검열되는 양이 늘어나고, 보고되는 격차는 벌어집니다</strong></span>.

저자는 사전등록된 대조 실험도 돌렸습니다. 매칭된 인벨로프(모델이 파서 포맷에 맞게 설정된 경우)에서는 silent fraction이 0–2에 머무는데, 이 예측은 실행 전에 리포지토리에 커밋해뒀다고 합니다.

Llama-3.1-8B 에피소드도 빼놓을 수 없습니다. 과업 함수 자체를 툴로 부르는 실패가 23%였는데, `strict: true` 플래그 하나로 0%가 됐습니다.

## RL 학습 루프 안까지 침투한다

![Figure 5: RL 학습 롤아웃](/images/2026-09-05-interface-trajectory-censoring/fig-5-p35.png)

verl의 AgentLoop, 7B 모델 기준입니다. 115개 생성물 중 45개가 완전한 툴 호출을 담고 있었는데, <span style="background-color: #fff59d"><strong>수용 0, 실행 0, 관찰 반환 0이었습니다</strong></span>.

RL 입장에서 이보다 나쁜 환경은 없습니다. 강화하고 싶은 행동이 경험 분포에 아예 없으니까요. 논문은 이를 마스킹(유효 호출 미인식)과 서프레션(무효 호출 차단) 두 방향의 검열로 정리합니다.

평가 시점에 어댑터를 고치면 메커니즘은 돌아오지만 성적 향상은 유의미하지 않았습니다. 파싱 0→84, 복구 0→9, <span style="background-color: #fff59d"><strong>패스율 53→62 (n.s.)입니다</strong></span>.

## 실무에서 할 일

저자는 <span style="background-color: #fff59d"><strong>98줄짜리 프리플라이트 체크</strong></span>를 공개했습니다. 이 논문이 보고한 모든 사일런트 실패를 잡아낸다고 합니다.

- 에이전트 평가를 돌리기 전에 서빙 스택의 템플릿·파서·체크포인트 계약을 먼저 확인합니다.
- tool-call rate 0이 나오면 모델 용량을 의심하기 전에 파싱 퍼널을 측정합니다.
- RL 학습에서 "모델이 도구를 안 쓴다"는 결론을 내리기 전에, 롤아웃 안에 실행된 호출이 실제로 존재하는지 확인합니다.

참고로 vLLM 이슈 #32926(2026-01-23)이 이미 Qwen2.5-Coder의 이 문제를 문서화했는데 `not planned`로 닫혔다고 합니다. 함정은 아직 살아 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

### 툴 호출이 0개로 기록될 때 우선 확인 방법
채팅 템플릿·파서·모델 체크포인트의 3자 계약이 맞는지 프리플라이트 체크로 확인합니다. 모델이 방출하는 원시 출력을 직접 덤프해서 정상 호출이 있는지 보는 게 첫 단계입니다.

### 파서 버그 여부를 가리는 방법과 이유
파서가 파서가 자기 규칙에 맞는 호출을 놓친 사례를 0건 발견했습니다. 실패는 세 당사자가 독립적으로 설정된 계약 전체의 문제입니다.

### RL 학습에 영향을 주는 이유
영향을 줍니다. 툴 호출이 파싱 단계에서 사라지면 실행도 관찰도 없으니, 강화할 툴 사용 경험 자체가 롤아웃에 존재하지 않게 됩니다.

### 원문과 코드를 확인하는 방법
arXiv 2609.03966, 코드·데이터·사전등록은 GitHub `nebula-1999/Interface-Induced-Trajectory-Censoring`에 공개돼 있습니다.
