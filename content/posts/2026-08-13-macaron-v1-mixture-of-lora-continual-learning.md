---
title: "기반 모델 얼려두고 LoRA만 갈아끼우는 법 — Macaron-V1의 지속 학습 설계"
date: 2026-08-13
tags:
  - agent
  - LLM
  - continual-learning
  - self-improvement
  - harness
  - LoRA
  - model-harness-co-design
  - recursive-self-improvement
  - RL
  - open-source
authors:
  - конанссам
draft: true
refactor_hub: harness-self-improve-24
refactor_status: queued
---

744B 기반 모델을 동결하고 LoRA(LoRA는 기반 가중치를 얼려두고 저랭크 행렬만 추가로 학습해 붙이는 경량 파인튜닝 기법) 어댑터만 갈아끼우면서 지속 학습과 자기개선을 하겠다는 실험이 나옴. 배포 후 모델을 어떻게 관리할지 고민하는 사람에게 구조 참고가 돼서 정리함.

1. 배경. 에이전트 모델의 지속 학습은 딜레마임 — 배우면 좋은데 기반을 건드리면 재현성이 무너짐. Mind Lab의 Macaron-V1은 744B GLM-5.2를 동결하고 4개 LoRA 전문가 어댑터(chat, agent, coding, GenUI)를 올리는 Mixture-of-LoRA 구조로 이 딜레마를 회피함.

2. 설계 원칙이 명확함. "체인 사고 패턴이 유사한 작업을 하나의 LoRA로 묶고, 패턴이 크게 다른 작업은 별도 LoRA로 분리한다." MoE는 기반을 확장하고, 스킬은 고정 모델 주변 비계를 확장하고, MoL은 기반을 동결하고 어댑터를 조합함 — 세 번째 길이라는 것.

3. 라우팅이 가벼움. 별도 라우터 모델 없이 L0(chat) 어댑터가 24토큰 예산으로 라벨을 냄. Route 0.54초 + Answer + Summary 0.97초. 라우팅+요약 오버헤드가 3-hop 총 시간의 약 30-32%. 턴마다 지불하는 세금이지만 라우팅 정확도가 99%대라는 것.

4. Per-Adapter Conversation View가 절묘함. 각 어댑터는 자기 발화는 전문 그대로, 다른 어댑터 발화는 192토큰 요약으로 압축해서 봄. append-only 타임라인에서 결정론적으로 재구성되니 같은 어댑터에 재진입하면 byte-identical prefix가 만들어지고 KV prefix cache가 적중함. 컨텍스트 관리와 캐싱을 한 번에 해결하는 설계.

5. 모델-하네스 공동 설계 축 두 개. UI4A는 HTML 표현력과 스키마 검증성 사이의 절충 — 런타임 경계 안에서 프론트엔드 코드를 쓰게 해서 평균 1,224토큰을 672토큰으로 45% 절감. REPL 하네스는 도구 호출을 discrete JSON이 아니라 persistent Python namespace에서 처리해서 중간 관찰이 모델을 재통과하지 않게 함.

6. save_tool → 검증 → promote_tool 순서도 베낄 만함. 에이전트가 만든 헬퍼는 검증을 통과해야 이후 세션에서 호출 가능. 도구 자동 생성의 위험을 승격 절차로 통제하는 구조.

7. 재귀적 자기개선 루프가 3단계임. Discovery(현재 모델이 못 푸는 작업 변안 제안, 검증 가능한 답 포함) → Expansion(동결된 모델로 HCP 설정만 바꿔가며 통과 탐색) → Update(선택 궤적으로 GRPO(같은 문제에서 뽑은 여러 응답을 상대 비교로 학습 신호를 만드는 RL 알고리즘) 기반 LoRA 업데이트). 가중치 말고 설정을 먼저 탐색하는 순서가 중요함.

8. Expansion 결과가 인상적임. 동결 모델이 전부 실패한 TerminalBench(터미널 명령으로 실무 과제를 완수하는 능력을 재는 벤치마크) 122개 작업에서 단일 설정 스윕은 3.3~9.0%만 통과. 적응적 설정 탐색은 작업당 3.69회 시도로 122/122 달성. per-attempt 효율이 13배. "모델이 못 푼다"가 아니라 "설정 커버리지가 부족했다"였을 수 있다는 것.

9. 이걸 내 무기고로 번역하면 이거임. 모델 업그레이드나 파인튜닝을 고민하기 전에 하네스 설정 탐색을 먼저 돌릴 것. 프롬프트, 스킬, 도구 노출, 훅의 조합 공간이 의외로 크고, 실패 작업의 상당수가 설정 하나로 열림. 가중치를 건드리는 건 설정 공간이 소진된 뒤에 하는 것.

10. 배포 효율도 실무적임. 기반 1개만 상주하고 어댑터를 얹으니 복제 배치 대비 74.0% 절감. H20 한 대로 56K 토큰 16동시. 도메인별 어댑터 운영이 인프라 비용에서도 성립한다는 것.

11. 여기서 문제제기. 보고서가 한계를 스스로 명시함 — 라우팅 정확도 99%가 학습 데이터 트레이스라 일반화 추정치가 아님. KV 재사용 비교는 동등성이 확립 안 됨. 세대 간 누적 개선도 미측정. 그리고 단일 LoRA 예산 매치 비교가 없어서 어댑터 분리의 실제 이득(간섭 제거)이 정량화 안 됨. 홍보성 수치와 검증된 수치를 구분해서 읽어야 함.

12. 결론. "기반 동결 + 어댑터 조합 + 설정 우선 탐색"이라는 운영 원칙이 이 시스템의 알맹이임. 근데 자기개선 루프가 LoRA 업데이트까지 가기 전에 설정 탐색만으로 풀리는 케이스가 대부분이었다는 것 — 순서를 지키는 게 총비용을 줄인다는 교훈까지가 수확임.

![Macaron-V1-Venti 메인 결과](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-1-p1.png)

![MoE, Skills, MoL 비교](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-2-p4.png)

![GenUI 접근 방식 비교](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-3-p13.png)

![UI4A-Bench 갤러리](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-4-p14.png)

![함수 호출 vs REPL](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-5-p15.png)

![3개 루프가 하나의 하네스를 공유](/images/2026-08-13-macaron-v1-mixture-of-lora-continual-learning/fig-6-p17.png)
