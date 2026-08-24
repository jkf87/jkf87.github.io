---
title: "API 에러 하나에 8B 에이전트는 왜 무너지는가 — Fission-GRPO 읽기"
date: 2026-08-24
tags: [agent, LLM, tool-use, reinforcement-learning, GRPO, error-recovery]
draft: false
---

작은 툴 에이전트는 대개 성공하는 순간을 잘 다룹니다. 문제는 실패한 순간이죠. API가 에러를 반환하는 순간, Qwen3-8B 같은 모델은 <span style="background-color: #fff59d"><strong>같은 잘못된 호출을 되풀이하는 환각 재시도 루프</strong></span>에 빠지고, 대화는 그대로 끝납니다.

![](/images/2026-08-24-fission-grpo-error-recovery-tool-use/fig-1-p1.png)

측정으로 보면 BFCL v4 Multi-Turn 기준 오류 복구율(최소 1회 오류 후 최종 성공 확률)은 Claude Sonnet 4가 50% 초과, Qwen3-8B는 <span style="background-color: #fff59d"><strong>약 20%</strong></span> 수준입니다. 이 격차가 Fission-GRPO(arXiv 2601.15625, ACL 2026)의 출발점입니다.

## 실패를 그냥 벌점으로 쓰면 안 되는 이유

기존 RL(GRPO 계열)은 오류를 그룹 내 음의 보상으로 처리합니다. "틀렸다"는 신호는 가는데 <span style="background-color: #fff59d"><strong>"어떻게 고치는지"는 없습니다</strong></span>. 설상가상으로 샘플 그룹 전체가 실패하면 보상 분산이 0이 되어 <span style="background-color: #fff59d"><strong>그래디언트가 사라지고 학습이 멈춥니다</strong></span>(DAPO, NGRPO가 지적한 한계).

미리 모아둔 오류-교정 데이터셋(ToolACE, LoopTool류)도 답이 아닙니다. 정책이 좋아지면 오류 분포가 달라지는데, 오프라인 데이터는 그대로라 <span style="background-color: #fff59d"><strong>시간이 지날수록 실제 오류와 어긋납니다</strong></span>.

## 핵분열이라는 이름의 데이터 증폭

Fission-GRPO의 루프는 세 단계입니다.

![](/images/2026-08-24-fission-grpo-error-recovery-tool-use/fig-2-p3.png)

1. 표준 GRPO 탐색 — 여러 롤아웃을 뽑고 그룹 상대 advantage로 업데이트. 보상은 형식 준수(감쇠 가중), 기능 정확도(증가 가중), 길이 규제의 3항 합성으로 문법에서 의미로 초점을 옮겨갑니다.
2. 오류 식별 & 진단 합성 — 실패 궤적을 걸러내고, Qwen3-32B를 SFT한 Error Simulator가 <span style="background-color: #fff59d"><strong>"parameter status expects value OPEN" 스타일의 비누출 런타임 에러 메시지</strong></span>를 생성합니다. 사람 평가로 비누출 96%, 일치도 Cohen's κ=0.71.
3. Fission 업데이트 — [대화; 실패한 호출; 진단] 문맥에서 G'개 복구 롤아웃을 다시 샘플링. <span style="background-color: #fff59d"><strong>하나의 실패가 연쇄적으로 훈련 신호 여러 개로 늘어난다</strong></span>고 해서 핵분열(fission)에서 이름을 땄습니다. LIFO 버퍼로 최근 오류를 우선 학습합니다.

## 숫자로 보는 성과

BFCL v4 Multi-Turn:

| 모델 | Fission-GRPO 정확도 |
|---|---|
| Qwen3-1.7B | 20.38% (GRPO 대비 +12.58%p) |
| Qwen3-4B | 40.87% |
| Qwen3-8B | 46.75% (오류 복구율 +5.7%p) |

- 8B 기준 전체 정확도 <span style="background-color: #fff59d"><strong>42.75% → 46.75%</strong></span>
- ToolACE-2-8B 대비 +9.75p, BitAgent-8B 대비 +9.00p
- TAU-Bench/TAU2-Bench에서도 대부분 설정 최고, <span style="background-color: #fff59d"><strong>TAU1 Retail +17.4%p</strong></span>까지
- 어블레이션: 제너릭 오류 프롬프트 대비 시뮬레이터 진단이 명확히 우위
- 동일 업데이트 스텝의 <span style="background-color: #fff59d"><strong>컴퓨트 매치 비교에서도 GRPO 상회</strong></span> — 오류 쪼개기는 낭비가 아니라 효율이라는 뜻입니다

카테고리 분해와 어블레이션 표는 아래 두 그림으로 확인할 수 있습니다.

![](/images/2026-08-24-fission-grpo-error-recovery-tool-use/fig-3-p8.png)

![](/images/2026-08-24-fission-grpo-error-recovery-tool-use/table-2-p8.png)

## 읽고 나서

가장 흥미로운 지점은 데이터 관점입니다. <span style="background-color: #fff59d"><strong>실패 궤적 + 진단 피드백 = 새 훈련 인스턴스</strong></span>라는 변환을 루프 안에 넣으면서, 오류 분포가 바뀌어도 데이터가 따라갑니다. 프롬프트에 오류 처리 로직을 박는 대신 오류 경험 자체를 학습 신호로 순환시키는 구조라는 게 이 논문의 메시지죠.

한계도 있습니다. 평가가 툴 호출 에이전트에 한정되고, 복구 증폭(G')만큼 롤아웃 비용이 늘며, Error Simulator 학습에 정답 툴콜이 필요합니다. 저자들은 코드 디버깅·수학 추론으로의 확장을 후속 과제로 제시합니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 참고

- Robust Tool Use via Fission-GRPO: Learning to Recover from Execution Errors (Zhang et al., ACL 2026) — https://arxiv.org/abs/2601.15625
- 코드: https://github.com/zxzadm/Fission-GRPO
- 벤치마크: BFCL v4 Multi-Turn, TAU-Bench, TAU2-Bench
