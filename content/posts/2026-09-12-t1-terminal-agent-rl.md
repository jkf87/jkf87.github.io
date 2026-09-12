---
title: "T1: 터미널 에이전트를 순수 RL로 64%까지 끌어올린 레시피 (arXiv 2609.11042)"
date: 2026-09-12
tags: [ai, llm, agent, rl, terminal, arxiv, moe]
draft: false
description: "arXiv 2609.11042 T1 논문 정리. Qwen3.5-122B MoE를 터미널 태스크 순수 강화학습으로 Terminal-Bench 2.1 49.4%에서 64.0%까지 올린 TITO·R3·dense test-count reward 레시피와 실패 기록을 정리했습니다."
---

## 결론 먼저

Tencent Hy 팀이 Qwen3.5-122B-A10B를 터미널 태스크 강화학습만으로 후트레이닝해서 Terminal-Bench 2.1에서 <span style="background-color: #fff59d"><strong>49.4% → 64.0% resolved</strong></span>까지 올렸다.

122B 중 활성 파라미터 10B짜리 모델이 같은 하네스에서 GPT-5.4(54.8%), DeepSeek-V4-Flash(56.9%)를 넘고 Claude Opus 4.6(63.8%)과 0.2점 차이라는 게 핵심 결과다.

논문: [arXiv 2609.11042](https://arxiv.org/abs/2609.11042) · Project Page/HuggingFace는 논문 첫 페이지 링크 참조

여기서 숫자보다 레시피가 더 중요하다. 이 팀은 <span style="background-color: #fff59d"><strong>MoE RL의 훈련-추론 불일치를 TITO와 R3로, 희소 보상을 test-count dense reward로</strong></span> 각각 따로 잡았고, 둘 중 하나라도 빠지면 학습이 무너지는 걸 직접 측정해서 보여준다.

핵심 숫자 (기준일 2026-09-12, 논문 Table 1·Figure 9):

| 항목 | 값 |
| --- | --- |
| 베이스 모델 | Qwen3.5-122B-A10B (활성 10B) |
| Terminal-Bench 2.1 (base → SFT → T1) | <span style="background-color: #fff59d"><strong>43.8 → 49.4 → 64.0%</strong></span> |
| SFT 기여 vs RL 기여 | +5.6pt vs <span style="background-color: #fff59d"><strong>+14.6pt (전체 상승분의 약 3/4이 RL)</strong></span> |
| Long-Horizon Terminal Bench | 27.9 (GPT-5.4 27.2, Gemini-3.1-Pro 27.9와 동급) |
| 훈련-추론 logprob 격차 | TITO+R3 적용 시 <span style="background-color: #fff59d"><strong>0.021 → 0.013</strong></span>, loss 영역 토큰 드리프트 0 |
| 태스크당 롤아웃 | <span style="background-color: #fff59d"><strong>최대 300+ 턴</strong></span>, 실제 셸 명령 실행 |

## 학습 데이터와 태스크 구성

터미널 태스크다. 자기 완결형 태스크 하나는 instruction, 도커 환경, 검증기(verifier), 참조 솔루션을 갖는다.

에이전트는 클라우드 샌드박스에서 진짜 셸을 돌리며 최대 300턴 이상 작업하고, 보상은 태스크 자체의 검증기를 실행해서 얻는다. 프레퍼런스 모델이나 사람 점수는 쓰지 않고 <span style="background-color: #fff59d"><strong>실행 결과만으로 보상을 매긴다</strong></span>.

데이터 풀은 세 개다.

- TMax-15k: 공개 코퍼스 변환 14,601태스크. 검증기가 이진 결과만 냄
- RST-38k: 시드 솔루션을 재귀적으로 확장해 합성한 37,484태스크
- T1-15k: 감사를 통과한 15,000태스크. <span style="background-color: #fff59d"><strong>검증기가 assertion 단위로 통과/실패를 기록</strong></span> (샘플 태스크 93%에서 사전 확인)

카테고리 분포를 보면 스크립팅·자동화 17.9%, 소프트웨어 개발 16.5%, 시스템 어드민 13.8% 순으로 커맨드라인 엔지니어링에 몰려 있다.

상위 5개 카테고리가 67.9%다. 이 논문의 성격상 어드민/디버깅 이점이 크게 나온 게 이 분포와 맞닿아 있다.

![T1-15k 카테고리 구성](/images/2026-09-12-t1-terminal-agent-rl/fig-3-p7.png)

전체 훈련 파이프라인은 아래 그림 하나로 요약된다. 좌측 태스크, 중앙 비동기 PPO 훈련, 우측 샌드박스 실행으로 구성되고 rollout과 training이 파이프라인으로 겹쳐 돈다.

![T1 훈련 파이프라인](/images/2026-09-12-t1-terminal-agent-rl/fig-2-p5.png)

## MoE 모델의 훈련 추론 불일치 해결: TITO와 R3

이 논문에서 가장 실무적인 부분이다. 121.4B 중 116B가 전문가 가중치라 <span style="background-color: #fff59d"><strong>모든 토큰이 256개 전문가 중 8개만 쓴다.</strong></span>

추론과 훈련의 미세한 수치 차이가 라우터 선택을 뒤집으면, 그 행동을 만들지 않은 파라미터로 그래디언트가 흐르는 일이 생긴다. 문장 하나에서 전문가 선택이 수백 번 바뀔 수 있다는 뜻이다.

해법을 두 축으로 나눴다.

- TITO (Token-In-Token-Out): 롤아웃에서 실제 샘플링된 <span style="background-color: #fff59d"><strong>정확한 토큰 ID 그대로 훈련</strong></span>하고, 턴 경계에서 생기는 토크나이저 재정렬 드리프트는 스티칭으로 수리한다
- R3 (Rollout Routing Replay): 샘플러가 MoE 모든 레이어에서 토큰별로 고른 전문가를 기록해두고 <span style="background-color: #fff59d"><strong>훈련 때 그 선택을 그대로 리플레이</strong></span>한다

둘을 합치면 훈련-추론 logprob 격차가 0.021 → 0.013으로 줄고, loss가 계산되는 영역의 토큰 드리프트는 정확히 0이 된다. 이 격차가 정책 이동인지 회계 오류인지를 가르는 문제라는 게 저자들의 설명이다.

크리틱 쪽도 같은 문제가 있다. 웜스타트된 크리틱을 액터 학습률의 30배로 훈련하는데, <span style="background-color: #fff59d"><strong>122B 액터-크리틱 페어를 며칠씩 공존시키는 인프라</strong></span>가 필요했다고 한다.

## dense reward 설계: assertion 통과 개수로 매긴다

롤아웃 배치 하나에 샌드박스 수백 시간이 드는데 이진 보상이면 트레젝토리당 정보가 1비트다. 저자들은 <span style="background-color: #fff59d"><strong>이진 보상 캠페인이 SFT 베이스라인을 한 번도 넘지 못했다</strong></span>고 적고 있다.

그래서 검증기의 assertion 통과 개수를 전역 고정 스케일(S=20)로 나눠 dense reward로 쓴다.

여기서 설계 디테일이 세 가지 있다.

- 분모를 배치 최댓값이 아니라 <span style="background-color: #fff59d"><strong>전역 고정값 S=20</strong></span>으로 둬서, 한 샘플이 배치 전체의 보상 스케일을 왜곡할 경로를 막는다
- T1-15k는 품질 순으로 정렬돼 있어서 <span style="background-color: #fff59d"><strong>에포크마다 셔플이 필수</strong></span>다. 안 하면 크리틱이 보는 보상 분포가 에포크 따라 단조 드리프트한다
- assertion 개수 보상은 턴을 늘려 테스트만 늘리는 파밍을 유도할 수 있는데, 27B 실험에선 실제 관찰됐고 122B에선 모니터링으로 억제됐다

![test-count reward 학습 곡선](/images/2026-09-12-t1-terminal-agent-rl/fig-8-p15.png)

리워드 해킹 방어는 데이터 쪽이 1차 방어선이다. T1-15k 선정 시 DeepSeek-V4-Pro 감사를 통과시키며 숨은 요구사항, 테스트 누출, 솔루션 지름길, 약한 검증기 4가지는 하드 리젝트했다.

## 결과: 10B 활성 파라미터로 4위

같은 Terminus-2 하네스에서 T1은 64.0%로 전체 4위, Claude Opus 4.7(66.1%), GPT-5.5(66.0%), Muse Spark(62.2%)… 대역에 들어간다. 카테고리별로는 <span style="background-color: #fff59d"><strong>디버깅 100.0, 시스템 어드민 88.9</strong></span>로 더 큰 범용 모델을 앞선다.

![Terminal-Bench 2.1 순위](/images/2026-09-12-t1-terminal-agent-rl/fig-9-p17.png)

주의할 점도 논문이 직접 적는다. 하네스 선택이 점수를 크게 움직인다(Claude Opus 4.6이 Claude Code에선 70.1, Terminus-2에선 63.8).

그리고 <span style="background-color: #fff59d"><strong>T1은 이 하네스에 맞춰 RL 훈련됐고 비교 모델은 아니다.</strong></span> 하위 블록의 Codex CLI 79.1% 같은 숫자는 다른 하네스라 직접 비교가 아니다.

롱호라이즌(LHTB)에선 27.9로 Gemini-3.1-Pro와 동급, GLM-5.2(31.6)·DeepSeek-V4-Pro(30.7)엔 못 미친다. Terminal-Bench 2.1 순위를 LHTB로 추정하면 안 된다는 걸 Sonnet 4.6(2.1에선 51.5인데 LHTB에선 37.3)이 보여준다.

## 실패한 경로와 남긴 기록

이 논문의 미덕은 안 된 것도 공개한 것이다. 성공한 경로는 아래 최종 레시피 하나뿐이고, 나머지는 왜 안 되는지가 기록돼 있다.

- 이진 보상 학습: 43.8 → 47.2에서 정체, SFT 체크포인트(49.4)에 못 미침. 남은 건 웜업된 크리틱
- 필터 없는 RST-38k dense reward: 59.9%까지 가긴 가지만 품질 필터링된 T1-15k보다 낮음
- 길이 셰이핑 변형 2종: 효과 없음

<span style="background-color: #fff59d"><strong>성공한 최종 레시피는 "T1-15k + PPO + warm-start 크리틱 + TITO + R3" 3에포크</strong></span> 하나다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」

## 자주 묻는 질문

T1은 어떤 모델을 어떻게 학습한 건가요?
Qwen3.5-122B-A10B(활성 10B MoE)를 RST-38k로 SFT한 체크포인트(49.4%)에서 출발해, T1-15k 태스크에 PPO 3에포크를 돌려 64.0%에 도달했다.

왜 이진 성공/실패 보상 대신 assertion 개수를 쓰나요?
롤아웃 비용이 트레젝토리당 샌드박스 수십 분~수 시간인데 이진 보상은 정보 1비트라 학습이 안 됐다. 검증기 assertion 통과 수를 고정 스케일로 나눈 dense reward가 실제로 베이스라인을 넘겼다.

TITO와 R3는 각각 뭘 고치나요?
TITO는 토큰 축(샘플링된 토큰 ID 그대로 훈련 + 턴 경계 재토큰화 수리), R3는 전문가 축(롤아웃 때의 MoE 라우팅 선택을 훈련에 리플레이)의 불일치를 따로 잡는다.

Terminal-Bench 2.1 64.0%가 최고 점수인가요?
아니다. 같은 하네스 기준 Claude Opus 4.7이 66.1%로 더 높고, 다른 하네스(Codex CLI)의 GPT-5.3-Codex는 79.1%다. 하네스가 다르면 직접 비교할 수 없다.

학습 코드와 모델이 공개됐나요?
논문 첫 페이지에 Project Page와 HuggingFace 링크가 있다. 훈련은 slime v0.3.0 + Megatron-Core, 롤아웃은 SGLang, 평가는 Harbor/Terminus-2 + Daytona 샌드박스 스택으로 돌아갔다.
