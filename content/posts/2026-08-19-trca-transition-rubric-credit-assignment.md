---
title: "실패 트랙토리의 72%는 학습 신호임 — TRCA의 전환 단위 루브릭 크레딧 정리"
date: 2026-08-19
tags:
  - reinforcement-learning
  - LLM-agent
  - credit-assignment
  - rubric-reward
  - GRPO
  - long-horizon
  - agent-training
draft: true
refactor_hub: agent-rl-06
refactor_status: queued
---

긴 호라이즌 에이전트 학습에서 실패한 롤아웃은 대부분 버려짐. TRCA(arXiv 2608.16156)는 그 버린 실패 안에 이미 학습 신호가 들어 있다는 걸 보이고 루브릭 기반 전환 단위 보상으로 꺼내는 방법을 제안함. 학습된 평가기도 성공 앵커도 안 쓰는 게 차별점임.

1. 출발점이 진단임. Qwen2.5-1.5B-Instruct 롤아웃을 뽑아 보니 96.5%가 터미널 성공에 실패했고 태스크 조건별 트레이닝 그룹의 85.6%엔 성공 트랙토리가 하나도 없었음. GRPO 계열은 성공/실패 터미널 아웃컴만으로 크레딧을 나누니까 이 상황에선 스텝 단위 판별이 사실상 불가능함.

2. 근데 같은 데이터를 사람 어노테이션과 프론티어 LLM 판정으로 다시 보니 실패한 롤아웃의 액션 72.2%는 여전히 진단적으로 유용한 전환 신호를 갖고 있었음. 성공 앵커가 없어도 스텝 크레딧을 만들 수 있다는 근거가 여기서 나옴.

![동기](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-motivation.png)

3. 기존 접근의 비용 구조와 대비됨. 프로세스 리워드 모델은 중간 스텝마다 평가기를 돌려서 어노테이션 비용과 추가 추론 비용이 붙음. 성공 앵커 기반(GiGPO, HCAPO)은 성공 트랙토리가 확보될 때만 작동함. TRCA는 둘 다 안 쓰고 액션이 일으킨 상태 전환 자체를 규칙 기반 루브릭으로 평가함.

4. 루브릭은 세 개임. Evidence는 환경에서 태스크 관련 정보를 새로 획득했는가. Execution은 환경을 유의미하게 바꾸는 유효한 액션인가. Invalidity는 무효, 중복, 퇴행 행동인가. 이 판정에서 두 개의 보상을 만듦.

![TRCA 개요](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-overview.png)

5. Foundational Rubric Reward는 세 카테고리의 부호 있는 점수 합산인 로컬 전환 품질임. 이 스텝 자체를 제대로 했는가를 봄. Breakthrough Rubric Reward는 지금까지 커버 안 된 Evidence/Execution 조건을 새로 충족했는지 추적함. 태스크 진전을 새로 만들었는가를 봄. λ로 섞고 터미널 아웃컴까지 합쳐 completion-aware return을 만듦.

6. 스텝 상대 어드밴티지 계산을 위해 유사한 결정 컨텍스트끼리 그룹을 묶는데, 텍스트 정합이 아니라 페이지 타입, 상품 식별, 태스크 술어 같은 환경별 구조 정보로 함. 그룹핑 기준을 도메인 구조로 잡는 게 이식의 핵심 지점임.

7. 결과. ALFWorld(텍스트 가상 집안에서 그릇 옮기기·물건 찾기 같은 일상 과제를 시키는 에이전트 벤치마크)의 Qwen2.5-7B 설정에서 TRCA 94.5로 GRPO 83.3, GiGPO 90.8, GraphGPO 93.3을 앞섬. WebShop(가상 쇼핑몰에서 주문서대로 상품을 검색·구매하는 벤치마크)에서 83.8 vs GraphGPO 80.3. SearchQA(검색 기반 질의응답 모음) 평균(3B) 45.4%로 7개 개별 데이터셋 전부 1위였음.

![결과](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-results.png)

8. 샘플 효율이 실무적으로 중요함. Pick_two에서 트랙토리 1.92K만 뽑은 시점에 성공률이 11.5%→34.6%로 오르고 3.84K로 69.2%에 도달함. GRPO는 6.40K를 써도 46.7%임. 실패 신호를 살리니 적은 롤아웃으로도 학습이 굴러가는 것임.

![학습 곡선](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-learning-curves.png)

9. Ablation이 구조를 명확히 함. Breakthrough 보상을 빼면 세 벤치마크 전부 더 크게 하락함. 실질 엔진은 "새로 커버된 조건" 추적이고 Foundational은 넓은 바탕이라는 것임. λ=0.8에서 평균 92.0%인데 λ=1.0(Foundational 제거)에서 88.3%로 떨어짐. 돌파 크레딧만 남기면 로컬 품질 신호를 잃어서 전체가 흔들림. 두 보상이 상호보완이라는 근거임.

![λ 히트맵](/images/2026-08-19-trca-transition-rubric-credit-assignment/trca-lambda-heatmap.png)

10. 실무 채점. 루브릭이 코드로 강제된다는 게 강점임. 롤아웃마다 PRM을 돌리는 추론 비용도 없고 성공을 기다릴 필요도 없음. Appendix에 벤치마크별 관측 가능 신호와 연산자 라이브러리가 공개돼서 자기 환경에 맞춰 다시 바인딩하면 됨.

11. 근데 이식 조건이 분명함. Evidence/Execution 판정이 환경에서 관측 가능한 상태 변화에 의존하기 때문에 상태 노출이 빈약한 환경에선 루브릭 신호 자체를 정의하기 어려움. WebShop처럼 페이지/상품/옵션이 구조화된 환경이라 성능이 잘 나온 측면이 있음.

12. 그리고 흐름상 같이 볼 것. 성공 앵커 의존이 이 논문이 지적한 병목인데 같은 지점을 검증기로 접근하는 Verifier-Bounded Credit Assignment(arXiv 2608.13179)가 있음. "성공이 희소한 초기 학습에서 크레딧을 어디서 끌어오는가"라는 질문의 두 답을 나란히 보면 지도가 그려짐.

13. 한계. 루브릭 설계가 도메인별 수작업이라 완전 자동은 아니고, 평가 환경도 ALFWorld/WebShop/SearchQA로 제한적임. 그래도 "실패 로그를 버리지 말고 전환 단위로 채점하라"는 원칙은 에이전트 학습 인프라를 짜는 누구에게나 적용되는 교훈임.

원문: [arXiv:2608.16156](https://arxiv.org/abs/2608.16156)
