---
title: "Agent Lightning v1.0 — 하네스 그대로 두고 RL 학습시키는 프레임워크 정리"
date: 2026-08-23
source: https://arxiv.org/abs/2608.17528
tags: [agent, rl, harness, training]
---

MS 리서치가 8월 18일자로 Agent Lightning v1.0 기술 보고서를 냈습니다. 핵심은 한 줄입니다. <span style="background-color: #fff59d"><strong>배포할 때 쓰는 에이전트 하네스를 그대로 RL 포스트트레이닝에 넣는 프레임워크</strong></span>구요, 약 3,500줄짜리 가벼운 구현입니다.

- 논문: https://arxiv.org/abs/2608.17528
- 코드: https://github.com/microsoft/agent-lightning

## 결론부터

- Qwen3.5-9B 코딩 에이전트가 <span style="background-color: #fff59d"><strong>학습 예제 6천 건 + 적당한 컴퓨트만으로 SWE-bench Verified 41.8% → 56.4%</strong></span>를 찍었습니다. 절대 게인 14.6%p예요.
- 검색 에이전트(Llama-3.2-3B, HotpotQA)는 <span style="background-color: #fff59d"><strong>검증 보상 25.1% → 41.7%</strong></span>.
- 인스트럭션 팔로잉(Qwen3-4B)은 <span style="background-color: #fff59d"><strong>51.9% → 70.2%</strong></span>.

여기까지가 원문 수치구요, 아래부터는 왜 이게 되는지 정리했습니다.

## 하네스드 에이전틱 RL이 뭔지

기존 에이전틱 RL은 학습 엔진(verl, AReaL 등)이 환경 루프를 직접 돌립니다. 매 턴마다 LLM을 호출하는 방식이에요.

하네스드 방식은 반대입니다.

- 학습 엔진이 외부 프로세스(하네스)를 띄우고, 하네스가 LLM API를 여러 번 호출합니다.
- <span style="background-color: #fff59d"><strong>학습 엔진은 연속된 트라젝토리를 못 보고, request-response 쌍만 프록시로 관측</strong></span>해요.

원 논문(2025년 Agent Lightning)이 이 구조를 처음 제안했고, verl Uni-Agent, AReaL 2.0, slime, Polar가 같은 방향을 따라왔습니다. 이 패러다임에 <span style="background-color: #fff59d"><strong>harnessed agentic RL</strong></span>이라는 이름을 붙인 게 이번 보고서입니다.

![Figure 1](/images/agent-lightning-v1-harnessed-agentic-rl-2026-08-23/fig-1-p1.png)
*그림 1. 전체 아키텍처. 학습 클러스터와 에이전트 실행 환경을 API Gateway로 분리 (출처: 논문 Figure 1)*

## 구조 3개

1. <span style="background-color: #fff59d"><strong>API Gateway</strong></span> — 상태를 갖는 서비스. 롤아웃 라이프사이클 추적, 모델 등록, 모든 request-response 로깅. 일반 LLM 엔드포인트처럼 행동해서 기존 하네스가 코드 수정 거의 없이 붙습니다.
2. <span style="background-color: #fff59d"><strong>Rollout Controller</strong></span> — 에이전트 태스크 실행 관리. Kubernetes Job으로 스케줄링해요. 코딩 에이전트는 격리된 샌드박스가 필요해서 이게 필수입니다.
3. <span style="background-color: #fff59d"><strong>Customized Trainer</strong></span> — verl 위에 구축. Sample Adapter가 롤아웃 레벨 어드밴티지·로스 정규화를 처리합니다.

![Figure 2](/images/agent-lightning-v1-harnessed-agentic-rl-2026-08-23/fig-2-p3.png)
*그림 2. Rollout Controller가 API Gateway를 폴링하며 태스크 관리 (출처: 논문 Figure 2)*

## 기존 RL이 깨지는 지점 3곳

하네스가 루프를 소유하면 표준 RL 로직이 실패하는 지점이 있다고 논문은 짚습니다.

### 1. 리토큰화와 샘플 병합

하네스는 다음 스텝 프롬프트를 만들 때 이전 응답에 도구 출력이나 시스템 메시지를 붙이고, 챗 템플릿을 다시 적용합니다. 그래서 다음 request의 토큰 prefix가 이전 턴 토큰과 정확히 안 맞을 수 있어요.

GPU 효율을 위해 연속 request를 하나의 시퀀스로 병합(sample merging)하는 게 기본인데, <span style="background-color: #fff59d"><strong>토큰이 안 맞는데 억지로 병합하면 오프폴리시 오염</strong></span>이 생깁니다. 실제로 본 게 아니라 다른 데이터로 학습하는 셈이에요.

Agent Lightning은 <span style="background-color: #fff59d"><strong>엄격한 토큰 prefix 매치가 유지될 때만 best-effort 병합</strong></span>을 합니다.

![Figure 3](/images/agent-lightning-v1-harnessed-agentic-rl-2026-08-23/fig-3-p4.png)
*그림 3. 리토큰화 예시 (출처: 논문 Figure 3)*

### 2. 어드밴티지 계산 단위

롤아웃 하나가 샘플 몇 개를 만들지는 제각각입니다. 검색 에이전트는 2스텝, 코딩 에이전트는 20스텝일 수 있어요.

샘플 단위로 어드밴티지를 계산하면 스텝 많은 태스크가 정책에 과도한 영향을 줍니다. 논문은 롤아웃 단위 어드밴티지를 주장합니다. <span style="background-color: #fff59d"><strong>최종 결과 보상을 그 롤아웃의 전체 스텝에 분배</strong></span>하는 거구요.

![Figure 4](/images/agent-lightning-v1-harnessed-agentic-rl-2026-08-23/fig-4-p7.png)
*그림 4. 전통적 RL에서 롤아웃 하나 = 학습 샘플 하나 (출처: 논문 Figure 4)*

### 3. 로스 정규화

샘플 단위 정규화는 긴 롤아웃 몇 개가 그래디언트를 지배하게 만듭니다. <span style="background-color: #fff59d"><strong>롤아웃 토큰 평균 로스</strong></span>를 쓰면 태스크당 기여가 균등해져요.

![Figure 5](/images/agent-lightning-v1-harnessed-agentic-rl-2026-08-23/fig-5-p8.png)
*그림 5. 샘플 수가 다른 3개 롤아웃 배치 예시 (출처: 논문 Figure 5)*

## 코딩 에이전트 학습 파이프라인

여기가 실무적으로 제일 유용한 부분입니다. <span style="background-color: #fff59d"><strong>전체 파이프라인을 재현 가능하게 공개</strong></span>했어요.

리워드 해킹 방어:

- <span style="background-color: #fff59d"><strong>.git 디렉토리 숨기고 git 커맨드 비활성화</strong></span> — 커밋 히스토리 조작으로 버그를 고친 척하는 걸 차단
- <span style="background-color: #fff59d"><strong>네트워크 격리</strong></span> — 화이트리스트만 허용, 인터넷에서 정답 검색 차단
- 난이도 필터링 — SWE-smith에서 너무 쉽거나 테스트가 깨진 태스크 제거

## 학습 결과

세 가지 설정을 비교했습니다.

| 설정 | 효과 |
|---|---|
| 샘플 단위 어드밴티지 | 전통적 RL. 불안정 |
| 롤아웃 단위 어드밴티지 | 개선 |
| <span style="background-color: #fff59d"><strong>롤아웃 단위 어드밴티지 + 정규화</strong></span> | <span style="background-color: #fff59d"><strong>최상. 검증 보상 38.2% 피크</strong></span> |

롤아웃 통계도 재밌습니다. <span style="background-color: #fff59d"><strong>평균 롤아웃당 학습 샘플 2.41개, 단일 시퀀스로 병합되는 롤아웃은 36%</strong></span>뿐이었어요. 다중 샘플 처리가 실제로 필요하다는 실증입니다.

효율도 개선됐습니다. 롤아웃 추론과 가중치 업데이트가 같은 GPU 풀을 공유하는 collocated async RL로, <span style="background-color: #fff59d"><strong>동기식 대비 2배 빠르고 GPU도 덜 씁니다</strong></span>.

![Figure 6](/images/agent-lightning-v1-harnessed-agentic-rl-2026-08-23/fig-6-p10.png)
*그림 6. 동기 RL / 비동기 RL / collocated async RL 비교 (출처: 논문 Figure 6)*

## 내 해석

- 이 보고서의 실체는 프레임워크 소개보다 <span style="background-color: #fff59d"><strong>"하네스드 RL에서 표준 RL이 어디서 깨지는가"에 대한 정리</strong></span> 쪽입니다. 리토큰화·롤아웃 어드밴티지·로스 정규화 3개는 직접 구현해보는 팀이라면 전부 부딪히는 문제예요.
- 3,500줄 구현이라는 점이 의도적입니다. 대형 프레임워크 말고 연구용 테스트베드 포지션이고, verl 기반이라 기존 스택에서 붙이기 쉽습니다.
- 코딩 에이전트 RL 하려는 팀은 <span style="background-color: #fff59d"><strong>데이터 클리닝 + 샌드박싱 스크립트</strong></span>만 봐도 값지구요, SWE-smith 필터링 로직이 공개되어 있습니다.

## 더 실습해보고 싶은 분들께

- 『[이게 되네? 오픈클로 미친 활용법 50제](https://product.kyobobook.co.kr/detail/S000219615902)』
- 「[모두를 위한 루프 엔지니어링](https://aifrenz.liveklass.com/classes/309184)」
